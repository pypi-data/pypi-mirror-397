# CLI Token Usage Tracking

This document explains how AI token counting works for the Seqera AI CLI, providing parity with the website's SeqeraAI2 token tracking system.

## Overview

The CLI uses the same thread-based token tracking model as the website. Each CLI session is treated as a persistent thread, allowing us to:

- Track token usage per user and organization
- Aggregate usage by day/week/month for quota management
- Maintain conversation history for context
- Provide consistent tracking across CLI and web interfaces

## Architecture

### Session-to-Thread Mapping

Unlike the website where users explicitly create threads, CLI sessions automatically create and reuse threads:

1. **Session Creation**: When a CLI session is created (via `get_or_create_session`), it initially has no thread
2. **Thread Creation**: On the first query, `_ensure_thread_for_session` creates a `Thread` row:
   - `mode`: `cli`
   - `version`: `2` (structured format)
   - `title`: First 100 characters of the first user message (or "CLI Session")
   - `user_id`: Extracted from authenticated user profile
3. **Thread Reuse**: Subsequent queries in the same session reuse the same thread ID
4. **Thread Persistence**: The `thread_id` is stored in the in-memory session dict and sent to the CLI client in the WebSocket `session` message

### Message Persistence

Each CLI query/response pair is persisted as two `Message` rows:

- **User Message**: Contains the user's query text, linked to the thread
- **Assistant Message**: Contains the assistant's response text, linked to the thread and LangSmith `run_id`

This is handled by `_save_cli_conversation`, which mirrors the website's `save_conversation` function.

### Token Usage Extraction

Token usage is extracted from Claude Agent SDK messages using best-effort parsing:

1. **Extraction**: `_extract_usage_from_message` checks multiple attributes:
   - `message.usage`
   - `message.response_metadata`
   - `message.metadata`
2. **Accumulation**: During streaming, token counts are accumulated across all messages using `_accumulate_usage`

3. **Recording**: After the assistant message is saved, `_record_token_usage_if_available` calls `record_token_usage` to persist usage to the `token_usage` table

### Token Usage Storage

Token usage is stored in the `token_usage` table with the following structure:

- `user_id`: User who made the request
- `org_id`: Organization ID (optional, for org-level quotas)
- `message_id`: UUID of the assistant message (links to `message` table)
- `run_id`: LangSmith run ID (for traceability)
- `input_tokens`: Number of input tokens
- `output_tokens`: Number of output tokens
- `total_tokens`: Total tokens used
- `usage_date`: Date for aggregation (daily/weekly/monthly queries)

## Implementation Details

### Key Functions

**`_ensure_thread_for_session`** (`services/api-assistant/routes/cli_agent.py:87`)

- Creates a thread for a session if one doesn't exist
- Reuses existing thread if session already has one
- Returns thread ID for message persistence

**`_save_cli_conversation`** (`services/api-assistant/routes/cli_agent.py:120`)

- Persists user and assistant messages to the database
- Links messages to thread and LangSmith run ID
- Returns the assistant message for token usage linking

**`_extract_usage_from_message`** (`services/api-assistant/routes/cli_agent.py:169`)

- Best-effort extraction of token counts from Claude Agent SDK messages
- Handles multiple possible attribute names and formats
- Returns `None` if no usage data found

**`_persist_cli_interaction`** (`services/api-assistant/routes/cli_agent.py:241`)

- Orchestrates the full persistence flow:
  1. Saves conversation (user + assistant messages)
  2. Records token usage if available
- Called after each query completes (both `/query` and `/ws/query` endpoints)

### Endpoints

Both CLI endpoints support token tracking:

- **`POST /cli-agent/query`**: Non-streaming query endpoint
- **`WebSocket /cli-agent/ws/query`**: Streaming query endpoint (primary CLI interface)

Both endpoints:

1. Create/retrieve thread for the session
2. Execute query and accumulate token usage
3. Persist messages and token usage after completion

## Viewing Token Usage

### Database Queries

Token usage data is stored in PostgreSQL. To view it:

**Top users by total tokens (all time):**

```bash
docker compose exec -T postgres psql -U postgres -d postgres \
  -c "select user_id, sum(total_tokens) as total from token_usage group by user_id order by total desc limit 5;"
```

**Daily aggregates by user:**

```bash
docker compose exec postgres psql -U postgres -d postgres \
  -c "SELECT user_id, usage_date, SUM(input_tokens) AS input, SUM(output_tokens) AS output, SUM(total_tokens) AS total FROM token_usage GROUP BY user_id, usage_date ORDER BY usage_date DESC LIMIT 20;"
```

**CLI-specific usage (by thread):**

```bash
docker compose exec postgres psql -U postgres -d postgres \
  -c "SELECT t.id AS thread_id, tu.usage_date, SUM(tu.input_tokens) AS input, SUM(tu.output_tokens) AS output, SUM(tu.total_tokens) AS total FROM token_usage tu JOIN message m ON tu.message_id = m.id JOIN thread t ON m.thread_id = t.id WHERE t.version = 2 GROUP BY t.id, tu.usage_date ORDER BY tu.usage_date DESC;"
```

**Month-to-date total for a specific user (psql):**
(Replace year/month/user values)

```bash
USER_ID=159
YEAR=2025
MONTH=12
docker compose exec -T postgres psql -U postgres -d postgres \
  -c "select sum(total_tokens) as total from token_usage where user_id = ${USER_ID} and date_part('year', usage_date)=${YEAR} and date_part('month', usage_date)=${MONTH};"
```

## Design Decisions

### Why Sessions = Threads?

The original implementation plan proposed treating CLI sessions as threads because:

1. **Consistency**: Website already uses threads for token tracking
2. **Minimal Schema Changes**: Reuses existing `thread` and `message` tables
3. **Natural Mapping**: A CLI session is conceptually a conversation thread
4. **Future-Proof**: Enables features like conversation history, limits, and quotas

### Token Extraction Strategy

Token usage extraction uses best-effort parsing because:

- Claude Agent SDK may expose usage in different attributes depending on version
- Different message types may have usage in different locations
- We want to be resilient to SDK changes without breaking token tracking

If no usage is found, the interaction is still persisted (messages saved), but token counts remain zero. This ensures the response path never fails due to missing token data.

### Error Handling

Token tracking is designed to be non-blocking:

- Missing token usage: Logged as warning, but doesn't fail the request
- Database errors: Caught and logged, but don't interrupt the response
- Missing user_id: Thread creation skipped, but query still processes

This ensures token tracking enhances observability without impacting CLI functionality.
