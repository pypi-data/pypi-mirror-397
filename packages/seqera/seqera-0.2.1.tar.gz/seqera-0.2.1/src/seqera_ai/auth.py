"""Auth0 helpers for the Seqera AI CLI."""

from __future__ import annotations

import base64
import hashlib
import json
import os
import secrets
import threading
import time
import urllib.parse
import webbrowser
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Dict, Optional

import requests
from rich.console import Console
from rich.panel import Panel


class AuthError(Exception):
    """Raised when Auth0 operations fail."""


@dataclass
class AuthTokens:
    """Auth0 token payload returned by the token endpoint."""

    access_token: str
    refresh_token: str
    expires_in: int
    id_token: Optional[str] = None
    scope: Optional[str] = None


@dataclass
class Auth0Config:
    """Runtime configuration for Auth0 integration."""

    domain: str
    client_id: str
    audience: str
    scopes: tuple[str, ...] = ("openid", "profile", "email", "offline_access")
    redirect_host: str = "127.0.0.1"
    redirect_port: int = 53682
    redirect_path: str = "/callback"
    profile: str = "default"

    @property
    def authorize_url(self) -> str:
        return f"https://{self.domain}/authorize"

    @property
    def token_url(self) -> str:
        return f"https://{self.domain}/oauth/token"

    @property
    def device_code_url(self) -> str:
        return f"https://{self.domain}/oauth/device/code"

    @property
    def revoke_url(self) -> str:
        return f"https://{self.domain}/oauth/revoke"

    @property
    def userinfo_url(self) -> str:
        return f"https://{self.domain}/userinfo"

    def build_redirect_uri(self, port: int) -> str:
        return f"http://{self.redirect_host}:{port}{self.redirect_path}"

    @classmethod
    def from_env(cls) -> "Auth0Config":
        """Load configuration using CLI environment variables."""

        # Production defaults; override with env vars for local development
        domain = os.getenv("SEQERA_AUTH0_DOMAIN", "seqera.eu.auth0.com").strip()
        audience = os.getenv("SEQERA_AUTH0_AUDIENCE", "platform").strip()
        client_id = os.getenv(
            "SEQERA_AUTH0_CLI_CLIENT_ID", "FUWn9TEdfcgbrxfxo6QJ2MYLMlPZMTrN"
        ).strip()

        redirect_host = os.getenv("SEQERA_AUTH0_REDIRECT_HOST", "127.0.0.1").strip()
        redirect_path = os.getenv("SEQERA_AUTH0_REDIRECT_PATH", "/callback").strip()
        profile = os.getenv("SEQERA_AUTH0_PROFILE")

        redirect_port_env = os.getenv("SEQERA_AUTH0_REDIRECT_PORT")
        redirect_port = 53682
        if redirect_port_env:
            try:
                redirect_port = int(redirect_port_env)
            except ValueError as exc:
                raise AuthError(
                    "SEQERA_AUTH0_REDIRECT_PORT must be an integer"
                ) from exc

        if not profile:
            profile = f"{domain}:{audience}"

        return cls(
            domain=domain,
            client_id=client_id,
            audience=audience,
            redirect_host=redirect_host,
            redirect_port=redirect_port,
            redirect_path=redirect_path or "/callback",
            profile=profile,
        )


class LoopbackServer:
    """Small HTTP server to capture the OAuth callback."""

    def __init__(self, host: str, start_port: int, callback_path: str):
        self.host = host
        self.start_port = start_port
        self.callback_path = callback_path or "/callback"
        self._server: Optional[HTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._event = threading.Event()
        self._result: Optional[Dict[str, str]] = None
        self.port: Optional[int] = None

    def _handler(self):
        parent = self

        class _LoopbackHandler(BaseHTTPRequestHandler):
            def do_GET(self):  # type: ignore[override]
                parsed = urllib.parse.urlparse(self.path)
                params = urllib.parse.parse_qs(parsed.query)

                if parsed.path != parent.callback_path:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b"Not found")
                    return

                result = {k: v[0] for k, v in params.items() if v}
                parent._result = result
                parent._event.set()

                message = "You can close this tab and return to the Seqera AI CLI."
                if "error" in result:
                    status = 400
                    title = "Authentication failed"
                else:
                    status = 200
                    title = "Authentication complete"

                html = f"""
<html>
  <head><title>{title}</title></head>
  <body style="font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
    <h2>{title}</h2>
    <p>{message}</p>
  </body>
</html>
""".strip()
                self.send_response(status)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html.encode("utf-8"))))
                self.end_headers()
                self.wfile.write(html.encode("utf-8"))

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                return

        return _LoopbackHandler

    def start(self) -> int:
        for offset in range(10):
            candidate_port = self.start_port + offset
            try:
                server = HTTPServer((self.host, candidate_port), self._handler())
                self._server = server
                self.port = candidate_port
                break
            except OSError:
                continue

        if not self._server or self.port is None:
            raise AuthError(
                "Unable to start local callback server. Try adjusting SEQERA_AUTH0_REDIRECT_PORT."
            )

        thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        thread.start()
        self._thread = thread
        return self.port

    def wait_for_callback(self, timeout: int = 300) -> Dict[str, str]:
        if not self._event.wait(timeout):
            raise AuthError("Timed out waiting for the Auth0 callback.")

        if not self._result:
            raise AuthError("Auth0 callback did not include any parameters.")
        return self._result

    def close(self) -> None:
        if self._server:
            self._server.shutdown()
            self._server.server_close()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=0.2)


class TokenStorage:
    """Stores refresh tokens in the OS keychain and metadata on disk."""

    SERVICE_NAME = "seqera-ai-cli"

    def __init__(self, config: Auth0Config):
        self.config = config
        self._keyring = self._load_keyring()
        self.config_dir = self._resolve_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.state_path = self.config_dir / "auth-state.json"

    def _resolve_config_dir(self) -> Path:
        override = os.getenv("SEQERA_CLI_CONFIG_DIR")
        if override:
            return Path(override).expanduser()

        xdg = os.getenv("XDG_CONFIG_HOME")
        if xdg:
            return Path(xdg).expanduser() / "seqera-ai"
        return Path.home() / ".config" / "seqera-ai"

    def _load_keyring(self):
        try:
            import keyring  # type: ignore

            return keyring
        except ImportError:
            return None

    def _account_id(self, profile_id: Optional[str] = None) -> str:
        target = profile_id or self.config.profile
        return f"{target}"

    def _fallback_file(self, profile_id: Optional[str] = None) -> Path:
        safe = (profile_id or self.config.profile).replace(":", "_")
        return self.config_dir / f"refresh-token.{safe}"

    def _read_state(self) -> Dict[str, Any]:
        if not self.state_path.exists():
            return {"profiles": {}}
        try:
            return json.loads(self.state_path.read_text())
        except (json.JSONDecodeError, OSError):
            return {"profiles": {}}

    def _write_state(self, state: Dict[str, Any]) -> None:
        tmp_path = self.state_path.with_suffix(".tmp")
        tmp_path.write_text(json.dumps(state, indent=2))
        tmp_path.chmod(0o600)
        tmp_path.replace(self.state_path)

    def set_refresh_token(self, refresh_token: str) -> None:
        if self._keyring:
            try:
                self._keyring.set_password(
                    self.SERVICE_NAME, self._account_id(), refresh_token
                )
                return
            except Exception:
                pass

        fallback = self._fallback_file()
        fallback.write_text(refresh_token)
        fallback.chmod(0o600)

    def get_refresh_token(self) -> Optional[str]:
        if self._keyring:
            try:
                token = self._keyring.get_password(
                    self.SERVICE_NAME, self._account_id()
                )
                if token:
                    return token
            except Exception:
                pass

        fallback = self._fallback_file()
        if fallback.exists():
            return fallback.read_text().strip() or None
        return None

    def delete_refresh_token(self, profile_id: Optional[str] = None) -> None:
        account = self._account_id(profile_id)
        if self._keyring:
            try:
                self._keyring.delete_password(self.SERVICE_NAME, account)
            except Exception:
                pass

        fallback = self._fallback_file(profile_id or self.config.profile)
        if fallback.exists():
            try:
                fallback.unlink()
            except OSError:
                pass

    def clear_all_refresh_tokens(self) -> None:
        state = self._read_state()
        profiles = list(state.get("profiles", {}).keys())
        for profile_id in profiles:
            self.delete_refresh_token(profile_id)

    def get_metadata(self) -> Dict[str, Any]:
        state = self._read_state()
        return state.get("profiles", {}).get(self.config.profile, {})

    def set_metadata(self, metadata: Dict[str, Any]) -> None:
        state = self._read_state()
        state.setdefault("profiles", {})[self.config.profile] = metadata
        self._write_state(state)

    def clear_metadata(self) -> None:
        state = self._read_state()
        profiles = state.get("profiles", {})
        profile_data = profiles.pop(self.config.profile, None)
        if profile_data is None:
            return

        # Store logout flag before clearing, so we know user explicitly logged out
        profiles[self.config.profile] = {"explicitly_logged_out": True}

        if profiles:
            self._write_state(state)
        elif self.state_path.exists():
            try:
                self.state_path.unlink()
            except OSError:
                pass

    def clear_all_metadata(self) -> None:
        if self.state_path.exists():
            try:
                self.state_path.unlink()
            except OSError:
                pass


class AuthManager:
    """High-level helper that drives the Auth0 flows."""

    def __init__(self, config: Auth0Config, console: Optional[Console] = None):
        self.config = config
        self.console = console or Console()
        self.storage = TokenStorage(config)
        self._access_token: Optional[str] = None
        self._expires_at: float = 0.0
        # Check if user explicitly logged out (from persistent storage)
        metadata = self.storage.get_metadata()
        self._explicitly_logged_out = bool(metadata.get("explicitly_logged_out", False))

    def _ensure_client_configured(self) -> None:
        if not self.config.client_id:
            raise AuthError(
                "Auth0 client ID is not configured. "
                "Set SEQERA_AUTH0_CLI_CLIENT_ID environment variable."
            )

    def _pkce_pair(self) -> tuple[str, str]:
        verifier = base64.urlsafe_b64encode(os.urandom(32)).decode("utf-8").rstrip("=")
        challenge = (
            base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest())
            .decode("utf-8")
            .rstrip("=")
        )
        return verifier, challenge

    def _request(self, url: str, data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            response = requests.post(url, data=data, timeout=15)
        except requests.RequestException as exc:
            raise AuthError(f"Failed to contact Auth0: {exc}") from exc

        if response.status_code >= 400:
            try:
                payload = response.json()
                message = (
                    payload.get("error_description")
                    or payload.get("error")
                    or response.text
                )
            except ValueError:
                message = response.text
            raise AuthError(f"Auth0 request failed ({response.status_code}): {message}")

        # Handle empty responses (e.g., /oauth/revoke returns 200 with empty body)
        if not response.content:
            return {}

        try:
            return response.json()
        except ValueError as exc:
            raise AuthError("Auth0 response was not valid JSON.") from exc

    def _fetch_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                self.config.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10,
            )
            if response.status_code >= 400:
                return None
            return response.json()
        except requests.RequestException:
            return None

    def _handle_token_response(self, payload: Dict[str, Any]) -> AuthTokens:
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        expires_in = payload.get("expires_in")

        if not access_token or not refresh_token or not expires_in:
            raise AuthError("Auth0 did not return the expected tokens.")

        return AuthTokens(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(expires_in),
            id_token=payload.get("id_token"),
            scope=payload.get("scope"),
        )

    def _authorization_code_login(self) -> AuthTokens:
        verifier, challenge = self._pkce_pair()
        state = secrets.token_urlsafe(16)
        server = LoopbackServer(
            self.config.redirect_host,
            self.config.redirect_port,
            self.config.redirect_path,
        )

        port = server.start()
        redirect_uri = self.config.build_redirect_uri(port)

        authorize_params = {
            "client_id": self.config.client_id,
            "audience": self.config.audience,
            "scope": " ".join(self.config.scopes),
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
        authorize_url = (
            f"{self.config.authorize_url}?{urllib.parse.urlencode(authorize_params)}"
        )

        self.console.print(
            Panel.fit(
                f"\n[link={authorize_url}]Opening Seqera CLI login page[/link]\n\n"
                f"If your browser does not open, click or paste this URL:\n\n[link={authorize_url}]{authorize_url}[/link]",
                title="Seqera CLI Login",
            )
        )

        opened = webbrowser.open(authorize_url)
        if not opened:
            self.console.print(
                "[yellow]Unable to open browser automatically. Please open the URL manually.[/yellow]"
            )

        try:
            callback_params = server.wait_for_callback()
        finally:
            server.close()

        if "error" in callback_params:
            description = (
                callback_params.get("error_description") or callback_params["error"]
            )
            raise AuthError(f"Auth0 returned an error: {description}")

        returned_state = callback_params.get("state")
        if returned_state != state:
            raise AuthError(
                "Auth0 callback state mismatch. Please try logging in again."
            )

        code = callback_params.get("code")
        if not code:
            raise AuthError("Auth0 did not return an authorization code.")

        payload = self._request(
            self.config.token_url,
            data={
                "grant_type": "authorization_code",
                "client_id": self.config.client_id,
                "code": code,
                "code_verifier": verifier,
                "redirect_uri": redirect_uri,
            },
        )
        return self._handle_token_response(payload)

    def _device_code_login(self) -> AuthTokens:
        payload = {
            "client_id": self.config.client_id,
            "audience": self.config.audience,
            "scope": " ".join(self.config.scopes),
        }
        device_data = self._request(self.config.device_code_url, data=payload)

        verification_uri = device_data.get(
            "verification_uri_complete"
        ) or device_data.get("verification_uri")
        user_code = device_data.get("user_code")
        interval = int(device_data.get("interval", 5))
        device_code = device_data.get("device_code")
        expires_in = int(device_data.get("expires_in", 600))

        if not verification_uri or not user_code or not device_code:
            raise AuthError("Auth0 device authorization response was incomplete.")

        self.console.print(
            Panel.fit(
                f"1. Visit [link={verification_uri}]{verification_uri}[/link]\n"
                f"2. Enter the code [bold]{user_code}[/bold]\n"
                "3. Approve access for Seqera AI CLI.",
                title="Device Authorization",
            )
        )

        deadline = time.time() + expires_in
        poll_payload = {
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "device_code": device_code,
            "client_id": self.config.client_id,
        }

        while time.time() < deadline:
            time.sleep(interval)
            try:
                token_data = self._request(self.config.token_url, data=poll_payload)
                return self._handle_token_response(token_data)
            except AuthError as exc:
                message = str(exc)
                if "authorization_pending" in message:
                    continue
                if "slow_down" in message:
                    interval += 5
                    continue
                raise

        raise AuthError("Device authorization expired before approval.")

    def login(self, use_device_flow: bool = False) -> Dict[str, Any]:
        """Perform a fresh login using either the browser or device-code flow."""

        self._ensure_client_configured()

        # If we already have a refresh token, try to reuse it before prompting the user
        existing_refresh = self.storage.get_refresh_token()
        if existing_refresh:
            # Clear the explicit logout flag since we have valid tokens
            self._explicitly_logged_out = False
            try:
                tokens = self._refresh(existing_refresh)
                self._access_token = tokens.access_token
                self._expires_at = time.time() + max(60, tokens.expires_in - 60)

                metadata = self.storage.get_metadata() or {}
                if not metadata.get("user"):
                    metadata["user"] = self._fetch_user_info(tokens.access_token) or {}
                now_ts = int(time.time())
                metadata.setdefault("last_login", now_ts)
                metadata["last_refresh"] = now_ts
                metadata.setdefault("method", "refresh")
                metadata["explicitly_logged_out"] = False  # Clear logout flag
                metadata.update(
                    {
                        "domain": self.config.domain,
                        "audience": self.config.audience,
                        "client_id": self.config.client_id,
                    }
                )
                self.storage.set_metadata(metadata)
                metadata["status"] = "already_logged_in"
                return metadata
            except AuthError as exc:
                self.console.print(
                    f"[yellow]Existing login is invalid ({exc}). Starting a new Auth0 login...[/yellow]"
                )
                self.storage.delete_refresh_token()
                self.storage.clear_metadata()

        tokens = (
            self._device_code_login()
            if use_device_flow
            else self._authorization_code_login()
        )
        self._access_token = tokens.access_token
        self._expires_at = time.time() + max(60, tokens.expires_in - 60)
        # Clear the explicit logout flag since user is logging in
        self._explicitly_logged_out = False

        user = self._fetch_user_info(tokens.access_token) or {}
        metadata = {
            "user": user,
            "last_login": int(time.time()),
            "method": "device" if use_device_flow else "browser",
            "domain": self.config.domain,
            "audience": self.config.audience,
            "client_id": self.config.client_id,
            "status": "new_login",
            "explicitly_logged_out": False,  # Clear logout flag on login
        }
        self.storage.set_refresh_token(tokens.refresh_token)
        self.storage.set_metadata(metadata)
        return metadata

    def _refresh(self, refresh_token: str) -> AuthTokens:
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.config.client_id,
            "refresh_token": refresh_token,
        }
        response = self._request(self.config.token_url, data=payload)

        new_refresh = response.get("refresh_token")
        tokens = self._handle_token_response(
            {**response, "refresh_token": new_refresh or refresh_token}
        )
        if new_refresh:
            self.storage.set_refresh_token(new_refresh)
        return tokens

    def get_access_token(self, prompt_login: bool = True) -> str:
        """Return a valid access token, refreshing or logging in as needed."""

        if self._access_token and (self._expires_at - time.time()) > 300:
            return self._access_token

        refresh_token = self.storage.get_refresh_token()
        if refresh_token:
            # If we have a refresh token, clear the explicit logout flag
            # (user may have logged in again via another process or manually restored tokens)
            self._explicitly_logged_out = False
            try:
                tokens = self._refresh(refresh_token)
                self._access_token = tokens.access_token
                self._expires_at = time.time() + max(60, tokens.expires_in - 60)
                if tokens.refresh_token:
                    metadata = self.storage.get_metadata() or {}
                    metadata["last_refresh"] = int(time.time())
                    # Clear logout flag
                    metadata["explicitly_logged_out"] = False
                    self.storage.set_metadata(metadata)
                return self._access_token
            except AuthError as exc:
                self.console.print(
                    f"[yellow]Refreshing tokens failed: {exc}. Forcing a new login.[/yellow]"
                )
                self.storage.delete_refresh_token()
                self.storage.clear_metadata()

        # If user explicitly logged out, automatically log them back in if prompt_login is True
        if self._explicitly_logged_out:
            if not prompt_login:
                raise AuthError(
                    "You have logged out. Run `seqera login` to authenticate again."
                )
            # Automatically run login
            self.console.print(
                "[bold]You have logged out. Starting Auth0 login...[/bold]"
            )
            self.login(use_device_flow=False)
            if not self._access_token:
                raise AuthError("Auth0 login failed.")
            return self._access_token

        if not prompt_login:
            raise AuthError("No CLI login found. Run `seqera login` first.")

        self.console.print(
            "[bold]No cached credentials found. Starting Auth0 login...[/bold]"
        )
        self.login(use_device_flow=False)
        if not self._access_token:
            raise AuthError("Auth0 login failed.")
        return self._access_token

    def logout(self, clear_all: bool = False) -> None:
        """Revoke the refresh token and wipe credentials."""

        refresh_token = self.storage.get_refresh_token()
        if refresh_token:
            try:
                self._request(
                    self.config.revoke_url,
                    data={"client_id": self.config.client_id, "token": refresh_token},
                )
            except AuthError as exc:
                self.console.print(
                    f"[yellow]Failed to revoke token (already invalid?): {exc}[/yellow]"
                )

        self._access_token = None
        self._expires_at = 0.0
        self._explicitly_logged_out = True

        if clear_all:
            self.storage.clear_all_refresh_tokens()
            self.storage.clear_all_metadata()
            # When clearing all, we don't store logout state (clean slate)
        else:
            self.storage.delete_refresh_token()
            self.storage.clear_metadata()
            # Store logout state in metadata so it persists across CLI invocations
            # (clear_metadata already stores the logout flag, but we ensure it's set)
            state = self.storage._read_state()
            state.setdefault("profiles", {})[self.config.profile] = {
                "explicitly_logged_out": True
            }
            self.storage._write_state(state)

    def status(self) -> Dict[str, Any]:
        """Return metadata describing the current login state."""

        metadata = self.storage.get_metadata()
        refresh_token = self.storage.get_refresh_token()
        info: Dict[str, Any] = {
            "profile": self.config.profile,
            "domain": self.config.domain,
            "audience": self.config.audience,
            "client_id": self.config.client_id,
            "logged_in": bool(refresh_token),
            "metadata": metadata,
        }

        if not refresh_token:
            return info

        try:
            token = self.get_access_token(prompt_login=False)
            info["access_token_valid"] = True
            info["seconds_until_expiry"] = max(0, int(self._expires_at - time.time()))
            if not metadata.get("user"):
                user = self._fetch_user_info(token)
                if user:
                    metadata["user"] = user
                    self.storage.set_metadata(metadata)
        except AuthError:
            info["access_token_valid"] = False
        return info


_AUTH_MANAGER: Optional[AuthManager] = None


def get_auth_manager(console: Optional[Console] = None) -> AuthManager:
    """Return a cached AuthManager instance."""

    global _AUTH_MANAGER
    if _AUTH_MANAGER is None:
        config = Auth0Config.from_env()
        _AUTH_MANAGER = AuthManager(config, console=console)
    return _AUTH_MANAGER
