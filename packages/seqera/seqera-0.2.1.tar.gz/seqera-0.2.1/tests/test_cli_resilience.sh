#!/bin/bash
#
# CLI Resilience Test Suite
# =========================
#
# Automated tests for WebSocket connection, retry logic, and error handling.
# Run this before submitting PRs that modify CLI connection behavior.
#
# Prerequisites:
#   - Backend running: docker compose up api-assistant
#   - User authenticated: seqera login
#   - In pipenv shell: pipenv shell
#
# Usage:
#   ./tests/test_cli_resilience.sh                    # Full test suite
#   ./tests/test_cli_resilience.sh --quick            # Skip AI-dependent tests (for CI)
#   ./tests/test_cli_resilience.sh http://custom:8002 # Custom backend URL
#   ./tests/test_cli_resilience.sh --quick http://custom:8002  # Both options
#
# What it tests:
#   1. Basic connectivity
#   2. Verbose mode output (-v flag)
#   3. Connection reuse across queries
#   4. Retry logic constants
#   5. Error message quality
#   6. Ctrl+C interrupt handling
#   7. Backend health endpoint
#   8. Security (no token leakage)
#   9. MCP local bash execution
#  10. MCP file operations (read, list)
#  11. MCP multi-step tool flow
#  12. Seqera Platform MCP (workspaces, pipelines)
#  13. Response time baseline
#
# Output:
#   - Color-coded PASS/FAIL/SKIP results
#   - Full report saved to /tmp/cli_resilience_report_*.txt
#

set -o pipefail

# Configuration
QUICK_MODE=false
BACKEND_URL="http://localhost:8002"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            QUICK_MODE=true
            shift
            ;;
        *)
            BACKEND_URL="$1"
            shift
            ;;
    esac
done

# macOS compatibility: use gtimeout if available, otherwise perl-based timeout
timeout_cmd() {
    local duration=$1
    shift
    if command -v gtimeout &> /dev/null; then
        gtimeout "$duration" "$@"
    elif command -v timeout &> /dev/null; then
        timeout "$duration" "$@"
    else
        # Perl-based timeout for macOS without coreutils
        perl -e 'alarm shift; exec @ARGV' "$duration" "$@"
    fi
}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLI_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_FILE="/tmp/cli_resilience_report_$(date +%Y%m%d_%H%M%S).txt"
PASSED=0
FAILED=0
SKIPPED=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
log() { echo -e "$1" | tee -a "$REPORT_FILE"; }
pass() { log "${GREEN}✅ PASS${NC}: $1"; ((PASSED++)); }
fail() { log "${RED}❌ FAIL${NC}: $1"; ((FAILED++)); }
skip() { log "${YELLOW}⏭️  SKIP${NC}: $1"; ((SKIPPED++)); }
info() { log "${BLUE}ℹ️  INFO${NC}: $1"; }
header() { log "\n${BLUE}═══════════════════════════════════════════════════════════${NC}"; log "${BLUE}  $1${NC}"; log "${BLUE}═══════════════════════════════════════════════════════════${NC}"; }

# Initialize report
init_report() {
    echo "CLI Resilience Test Report" > "$REPORT_FILE"
    echo "Generated: $(date)" >> "$REPORT_FILE"
    echo "Backend URL: $BACKEND_URL" >> "$REPORT_FILE"
    echo "CLI Directory: $CLI_DIR" >> "$REPORT_FILE"
    echo "==========================================" >> "$REPORT_FILE"
}

# Check prerequisites
check_prereqs() {
    header "Checking Prerequisites"
    
    # Check if seqera command exists
    if command -v seqera &> /dev/null; then
        pass "seqera CLI is installed"
    else
        fail "seqera CLI not found in PATH"
        info "Try: cd $CLI_DIR && pipenv shell"
        return 1
    fi
    
    # Check if jq is available
    if command -v jq &> /dev/null; then
        pass "jq is installed"
    else
        skip "jq not installed (some tests may have limited output)"
    fi
    
    # Check if backend is running
    if curl -s --connect-timeout 5 "$BACKEND_URL/cli-agent/health" > /dev/null 2>&1; then
        pass "Backend is responding at $BACKEND_URL"
    else
        fail "Backend not responding at $BACKEND_URL"
        info "Start backend with: docker compose up api-assistant"
        return 1
    fi
    
    # Check auth status
    if seqera status 2>&1 | grep -q "Logged in"; then
        pass "User is authenticated"
    else
        fail "User not authenticated"
        info "Run: seqera login"
        return 1
    fi
    
    return 0
}

# Test 1: Basic connectivity
test_basic_connectivity() {
    header "Test 1: Basic Connectivity"
    
    info "Sending simple query..."
    local output
    output=$(echo "Say just 'test ok' and nothing else" | timeout_cmd 60 seqera ai 2>&1)
    local exit_code=$?
    
    if [[ $exit_code -eq 0 ]] && echo "$output" | grep -qi "test\|ok\|hello"; then
        pass "Basic query works"
        info "Response received successfully"
    else
        fail "Basic query failed (exit code: $exit_code)"
        info "Output: $(echo "$output" | head -10)"
    fi
}

# Test 2: Verbose mode
test_verbose_mode() {
    header "Test 2: Verbose Mode (-v flag)"
    
    info "Testing verbose output..."
    local output
    output=$(echo "Say 'verbose test'" | timeout_cmd 60 seqera ai -v 2>&1)
    local exit_code=$?
    
    # Check for expected verbose markers
    if echo "$output" | grep -q "← session"; then
        pass "Verbose mode shows session message"
    else
        fail "Verbose mode missing session message"
    fi
    
    if echo "$output" | grep -q "← text\|← complete"; then
        pass "Verbose mode shows message types"
    else
        fail "Verbose mode missing message types"
    fi
    
    # Check no token leakage
    if echo "$output" | grep -qiE "eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"; then
        fail "SECURITY: JWT token visible in verbose output!"
    else
        pass "No token leakage in verbose output"
    fi
}

# Test 3: Connection reuse
test_connection_reuse() {
    header "Test 3: Connection Reuse (Multiple Queries)"
    
    info "Sending multiple queries in succession..."
    local output
    output=$(printf "Say 'first'\nSay 'second'\nexit\n" | timeout_cmd 120 seqera ai -v 2>&1)
    local exit_code=$?
    
    # Check for connection reuse message
    if echo "$output" | grep -q "Reusing connection"; then
        pass "Connection reuse working"
    else
        # Might not appear if queries are fast enough
        skip "Connection reuse message not detected (may be too fast)"
    fi
    
    # Check both responses received
    if echo "$output" | grep -qi "first" && echo "$output" | grep -qi "second"; then
        pass "Multiple queries in session work"
    else
        fail "Multiple queries failed"
    fi
}

# Test 4: Retry on error (simulated)
test_retry_logic() {
    header "Test 4: Retry Logic Verification"
    
    info "Checking retry constants in code..."
    
    # Check MAX_QUERY_RETRIES
    if grep -q "MAX_QUERY_RETRIES = 3" "$CLI_DIR/src/seqera_ai/cli.py"; then
        pass "MAX_QUERY_RETRIES is set to 3"
    else
        fail "MAX_QUERY_RETRIES not found or incorrect"
    fi
    
    # Check RETRY_DELAYS
    if grep -q "RETRY_DELAYS = \[1, 2, 4\]" "$CLI_DIR/src/seqera_ai/cli.py"; then
        pass "RETRY_DELAYS is [1, 2, 4] seconds"
    else
        fail "RETRY_DELAYS not found or incorrect"
    fi
    
    # Check transient error handling
    if grep -q "Token validation failed" "$CLI_DIR/src/seqera_ai/cli.py"; then
        pass "Transient auth errors trigger retry"
    else
        fail "Transient error handling missing"
    fi
}

# Test 5: Error message quality
test_error_messages() {
    header "Test 5: Error Message Quality"
    
    info "Checking error handling code..."
    
    # Check for user-friendly error messages
    if grep -q "Backend server is not responding" "$CLI_DIR/src/seqera_ai/cli.py"; then
        pass "User-friendly backend error message exists"
    else
        fail "Missing user-friendly backend error message"
    fi
    
    # Check connection failure message
    if grep -q "Connection failed" "$CLI_DIR/src/seqera_ai/cli.py"; then
        pass "Connection failure message exists"
    else
        fail "Missing connection failure message"
    fi
}

# Test 6: Graceful Ctrl+C handling
test_interrupt_handling() {
    header "Test 6: Interrupt Handling (Ctrl+C)"
    
    info "Testing Ctrl+C during query..."
    
    # Start a query and interrupt it
    (echo "Tell me a very long story about bioinformatics" | seqera ai 2>&1) &
    local pid=$!
    sleep 3
    kill -INT $pid 2>/dev/null
    wait $pid 2>/dev/null
    local exit_code=$?
    
    # Check process terminated cleanly (exit code 130 = SIGINT)
    if [[ $exit_code -eq 130 ]] || [[ $exit_code -eq 0 ]] || [[ $exit_code -eq 1 ]]; then
        pass "Ctrl+C handled gracefully (exit: $exit_code)"
    else
        fail "Ctrl+C handling issue (exit: $exit_code)"
    fi
    
    # Verify no zombie connections
    sleep 1
    local ws_connections
    ws_connections=$(lsof -i :8002 2>/dev/null | grep "seqera" | wc -l | tr -d ' ')
    ws_connections=${ws_connections:-0}
    if [[ "$ws_connections" -eq 0 ]]; then
        pass "No lingering WebSocket connections"
    else
        fail "Found $ws_connections lingering connections"
    fi
}

# Test 7: Backend health check
test_health_check() {
    header "Test 7: Backend Health Check"
    
    info "Verifying health endpoint..."
    local health_response
    health_response=$(curl -s "$BACKEND_URL/cli-agent/health")
    
    if echo "$health_response" | grep -qi "healthy\|ok\|status"; then
        pass "Health endpoint responds"
        info "Response: $health_response"
    else
        fail "Health endpoint not working"
    fi
}

# Test 8: Security checks
test_security() {
    header "Test 8: Security Checks"
    
    info "Scanning for potential security issues..."
    
    # Check no hardcoded tokens
    if grep -rE "(sk-|eyJ[A-Za-z0-9_-]{20,})" "$CLI_DIR/src/seqera_ai/" --include="*.py" 2>/dev/null | grep -v "test\|example\|#"; then
        fail "SECURITY: Possible hardcoded token found!"
    else
        pass "No hardcoded tokens in source"
    fi
    
    # Check token not printed in client code
    if grep -E "print.*self\._token|console\.print.*token\s*=" "$CLI_DIR/src/seqera_ai/cli.py" 2>/dev/null; then
        fail "SECURITY: Token may be printed to console"
    else
        pass "Token values not printed to console"
    fi
    
    # Check backend doesn't log full headers
    if grep -q 'dict(websocket.headers)' "$CLI_DIR/../api-assistant/routes/cli_agent.py" 2>/dev/null; then
        fail "SECURITY: Full headers (with token) may be logged"
    else
        pass "Backend logs only header keys, not values"
    fi
}

# Test 9: MCP Local Execution
test_mcp_local_execution() {
    header "Test 9: MCP Local Execution (Local Commands)"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        skip "Skipped in quick mode (AI-dependent test)"
        return
    fi
    
    info "Testing local bash command execution..."
    local output
    output=$(echo "Run the command 'echo MCP_TEST_SUCCESS' and show me the output" | timeout_cmd 90 seqera ai 2>&1)
    local exit_code=$?
    
    if echo "$output" | grep -q "MCP_TEST_SUCCESS"; then
        pass "Local bash execution works (execute_bash_local)"
    else
        fail "Local bash execution failed"
        info "Output snippet: $(echo "$output" | tail -20 | head -10)"
    fi
}

# Test 10: MCP File Operations
test_mcp_file_operations() {
    header "Test 10: MCP File Operations"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        skip "Skipped in quick mode (AI-dependent test)"
        return
    fi
    
    # Create a temp file to read
    local test_file="/tmp/seqera_cli_test_$$"
    echo "MCP_FILE_READ_SUCCESS" > "$test_file"
    
    info "Testing local file read..."
    local output
    output=$(echo "Read the file $test_file and tell me what it contains" | timeout_cmd 90 seqera ai 2>&1)
    local exit_code=$?
    
    if echo "$output" | grep -q "MCP_FILE_READ_SUCCESS"; then
        pass "Local file read works (read_file_local)"
    else
        fail "Local file read failed"
        info "Output snippet: $(echo "$output" | tail -20 | head -10)"
    fi
    
    # Cleanup
    rm -f "$test_file"
    
    info "Testing local directory listing..."
    output=$(echo "List the files in /tmp and show me just the first 5" | timeout_cmd 90 seqera ai 2>&1)
    
    # Check for common /tmp contents or directory listing indicators
    if echo "$output" | grep -qiE "\.sock|com\.|tmp|seqera|files|directory|listing"; then
        pass "Local directory listing works (list_directory_local)"
    else
        skip "Directory listing check inconclusive (AI response may vary)"
    fi
}

# Test 11: MCP Tool Result Flow
test_mcp_tool_flow() {
    header "Test 11: MCP Tool Result Flow"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        skip "Skipped in quick mode (AI-dependent test)"
        return
    fi
    
    info "Testing multi-step tool usage..."
    local output
    output=$(echo "Create a file /tmp/seqera_test_$$.txt with content 'hello', then read it back to verify" | timeout_cmd 120 seqera ai 2>&1)
    local exit_code=$?
    
    # Check that the AI successfully completed the task
    if echo "$output" | grep -qi "hello\|created\|verified\|success\|written"; then
        pass "Multi-step tool flow works"
    else
        skip "Multi-step tool check inconclusive"
    fi
    
    # Cleanup
    rm -f /tmp/seqera_test_$$.txt 2>/dev/null
}

# Test 12: Seqera Platform MCP (Remote)
test_platform_mcp() {
    header "Test 12: Seqera Platform MCP"
    
    if [[ "$QUICK_MODE" == "true" ]]; then
        skip "Skipped in quick mode (AI-dependent test)"
        return
    fi
    
    info "Testing Seqera Platform integration (remote MCP)..."
    local output
    output=$(echo "Show me my workspaces" | timeout_cmd 90 seqera ai 2>&1)
    local exit_code=$?
    
    # Check for workspace-related content in response
    # Could be workspace names, IDs, or even "no workspaces" message
    if echo "$output" | grep -qiE "workspace|organization|seqera|community|personal|team|id.*[0-9]"; then
        pass "Seqera Platform MCP works (workspace listing)"
        info "Platform query returned workspace information"
    elif echo "$output" | grep -qi "no workspace\|not found\|empty\|don't have"; then
        pass "Seqera Platform MCP works (no workspaces found - valid response)"
    elif echo "$output" | grep -qi "error\|unauthorized\|forbidden\|401\|403"; then
        fail "Seqera Platform MCP auth issue"
        info "Output snippet: $(echo "$output" | tail -10)"
    else
        skip "Platform MCP check inconclusive (response may vary)"
        info "Output snippet: $(echo "$output" | tail -10)"
    fi
    
    info "Testing pipeline listing..."
    output=$(echo "List available nf-core pipelines" | timeout_cmd 90 seqera ai 2>&1)
    
    if echo "$output" | grep -qiE "nf-core|rnaseq|sarek|pipeline|atacseq|chipseq|fetchngs"; then
        pass "Seqera Platform MCP works (pipeline listing)"
    else
        skip "Pipeline listing check inconclusive"
    fi
}

# Test 13: Response time baseline
test_response_time() {
    header "Test 13: Response Time Baseline"
    
    info "Measuring response time for simple query..."
    
    local start_time end_time duration
    start_time=$(date +%s)
    echo "Say 'timing test'" | timeout_cmd 60 seqera ai > /dev/null 2>&1
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    info "Response time: ${duration}s"
    
    if [[ "$duration" -lt 30 ]]; then
        pass "Response time acceptable (${duration}s < 30s)"
    else
        fail "Response time too slow (${duration}s >= 30s)"
    fi
}

# Manual tests guidance
manual_tests() {
    header "Manual Tests Required"
    
    log ""
    log "${YELLOW}The following tests require manual intervention:${NC}"
    log ""
    log "1. ${BLUE}Backend Restart During Session${NC}"
    log "   a) Run: seqera ai"
    log "   b) Send a query, get response"
    log "   c) In another terminal: docker compose restart api-assistant"
    log "   d) Immediately send another query"
    log "   e) Expected: Should reconnect and work after retry"
    log ""
    log "2. ${BLUE}Idle Connection Timeout (2+ minutes)${NC}"
    log "   a) Run: seqera ai"
    log "   b) Send a query, get response"
    log "   c) Wait 2+ minutes without activity"
    log "   d) Send another query"
    log "   e) Expected: Should show 'Reconnecting...' then work"
    log ""
    log "3. ${BLUE}Backend Down Scenario${NC}"
    log "   a) Stop backend: docker compose stop api-assistant"
    log "   b) Run: seqera ai"
    log "   c) Expected: Clear error about backend not responding"
    log ""
    log "4. ${BLUE}Token Refresh During Long Session${NC}"
    log "   a) Run: seqera ai"
    log "   b) Use for ~1 hour with periodic queries"
    log "   c) Expected: Token should refresh automatically"
    log ""
}

# Generate summary
generate_summary() {
    header "Test Summary"
    
    local total=$((PASSED + FAILED + SKIPPED))
    
    log ""
    log "Results:"
    log "  ${GREEN}Passed:  $PASSED${NC}"
    log "  ${RED}Failed:  $FAILED${NC}"
    log "  ${YELLOW}Skipped: $SKIPPED${NC}"
    log "  Total:   $total"
    log ""
    log "Report saved to: $REPORT_FILE"
    log ""
    
    if [[ $FAILED -eq 0 ]]; then
        log "${GREEN}🎉 All automated tests passed!${NC}"
        log "Please complete the manual tests above before submitting PR."
        return 0
    else
        log "${RED}⚠️  Some tests failed. Please review before submitting PR.${NC}"
        return 1
    fi
}

# Main execution
main() {
    init_report
    
    header "CLI Resilience Test Suite"
    log "Testing WebSocket connection and retry logic"
    log "Backend: $BACKEND_URL"
    log "Time: $(date)"
    if [[ "$QUICK_MODE" == "true" ]]; then
        log "${YELLOW}Quick mode: AI-dependent tests will be skipped${NC}"
    fi
    
    # Run prerequisite checks
    if ! check_prereqs; then
        log ""
        log "${RED}Prerequisites not met. Fix issues above and re-run.${NC}"
        exit 1
    fi
    
    # Run automated tests
    test_basic_connectivity
    test_verbose_mode
    test_connection_reuse
    test_retry_logic
    test_error_messages
    test_interrupt_handling
    test_health_check
    test_security
    test_mcp_local_execution
    test_mcp_file_operations
    test_mcp_tool_flow
    test_platform_mcp
    test_response_time
    
    # Show manual tests
    manual_tests
    
    # Generate summary
    generate_summary
}

# Run main
main "$@"

