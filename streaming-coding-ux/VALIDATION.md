# acpx Streaming Validation Results

**Date:** 2026-04-12
**acpx version:** 0.5.3
**Claude Code version:** 2.1.89
**Gemini CLI version:** 0.37.0
**Codex CLI version:** 0.118.0

---

## Test Results

### ✅ Test 1: acpx outputs JSON-RPC line-by-line in real-time

**Result: CONFIRMED ✅**

```
$ acpx --format json --json-strict claude exec "say the word hello"
{"jsonrpc":"2.0","id":0,"method":"initialize",...}
{"jsonrpc":"2.0","id":0,"result":{...}}          ← agent info
{"jsonrpc":"2.0","id":1,"method":"session/new",...}
{"jsonrpc":"2.0","id":1,"result":{"sessionId":"...",...}}  ← session created
{"jsonrpc":"2.0","id":2,"method":"session/prompt",...}
{"jsonrpc":"2.0","method":"session/update",...}   ← streaming notifications
{"jsonrpc":"2.0","id":2,"error":{"code":-32000,"message":"Authentication required"}}
```

Each JSON object is on its own line. The protocol sequence is:
1. `initialize` (handshake)
2. `session/new` (create session)
3. `session/prompt` (send user message)
4. `session/update` notifications (streaming: agent_message_chunk, tool_call, etc.)
5. Final response (with `id` matching session/prompt)

### ✅ Test 2: ACP notification types visible

**Result: CONFIRMED ✅**

Even before auth failure, we can see:
- `initialize` response with `agentInfo` (name, version, capabilities)
- `session/new` response with `sessionId`, `models`, `modes`, `configOptions`
- `session/update` with `available_commands_update`
- Error response with `id: null` (streaming error notification)

When authenticated, we would see:
- `session/update` with `sessionUpdate: "agent_message_chunk"` → text streaming
- `session/update` with `sessionUpdate: "agent_thought_chunk"` → thinking
- `session/update` with `sessionUpdate: "tool_call"` → tool start
- `session/update` with `sessionUpdate: "tool_call_update"` → tool progress/done

### ⚠️ Test 3: Claude Code authentication

**Result: NOT AUTHENTICATED ⚠️**

```
$ claude auth status
{"loggedIn": false, "authMethod": "none", "apiProvider": "firstParty"}
```

Need to run: `claude setup-token` or `claude login`

### ⚠️ Test 4: Gemini authentication

**Result: NOT AUTHENTICATED ⚠️**

```
error: Gemini API key is missing or not configured.
```

Need to set: `GEMINI_API_KEY` env var or `gemini login`

### ⚠️ Test 5: Codex availability

**Result: INSTALLED BUT NOT TESTED ⚠️**

```
$ codex --version
codex-cli 0.118.0
```

### ✅ Test 6: acpx session management

**Result: CONFIRMED ✅**

```
$ acpx claude sessions new --name test1
[acpx] created session test1 (e56ff717-e624-4694-9eef-326624dd0815)
{"action":"session_ensured","created":true,...}
```

Session lifecycle works: `sessions new`, `sessions list`, `sessions close`, `sessions show`, `sessions history`, `sessions read`

### ✅ Test 7: acpx top-level options

**Result: CONFIRMED ✅**

All top-level options go BEFORE the subcommand:
```bash
acpx --format json --json-strict --approve-all --timeout 20 claude exec "..."
#     ↑ top-level options                        ↑ subcommand
```

Available top-level options:
- `--format text|json|quiet`
- `--json-strict`
- `--approve-all` / `--approve-reads` / `--deny-all`
- `--timeout <seconds>`
- `--ttl <seconds>`
- `--model <id>`
- `--allowed-tools <list>`
- `--max-turns <count>`
- `--suppress-reads`
- `--verbose`
- `--cwd <dir>`
- `--auth-policy <policy>`

---

### ✅ Test 8: Full streaming with CLAUDE_CODE_OAUTH_TOKEN

**Result: FULLY WORKING ✅**

```bash
export CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-..."
acpx --format json --json-strict --approve-all claude exec "write a hello world function in python"
```

Output (streaming line-by-line in real-time):
```
Line 1:  initialize → agentInfo: @agentclientprotocol/claude-agent-acp 0.25.3
Line 2:  session/new → sessionId: 4af5be1c-..., 3 models, 6 modes
Line 3:  session/prompt → "write a hello world function..."
Line 4:  🔥 session/update: available_commands_update
Line 5:  🔥 session/update: agent_message_chunk: ""
Line 6:  🔥 session/update: agent_message_chunk: "```"
Line 7:  🔥 session/update: agent_message_chunk: "python\ndef hello_world():\n    print(\"Hello, World!\")\nhello_world()\n```"
Line 8:  🔥 session/update: usage_update (15805 tokens, $0.022)
Line 9:  ✅ result: end_turn
```

### 🔑 Auth Key Discovery (from OpenAB docs)

```bash
# WRONG: ANTHROPIC_API_KEY (doesn't work with ACP adapter)
export ANTHROPIC_API_KEY="sk-ant-api03-..."  # ❌

# CORRECT: CLAUDE_CODE_OAUTH_TOKEN (from `claude setup-token`)
export CLAUDE_CODE_OAUTH_TOKEN="sk-ant-oat01-..."  # ✅
```

OpenAB uses the same approach:
```bash
kubectl exec -it deployment/openab-claude -- claude setup-token
helm upgrade ... --set agents.claude.env.CLAUDE_CODE_OAUTH_TOKEN="***"
```

---

## Conclusion

### 🎯 Verdict: **Option D CONFIRMED AND WORKING**

acpx already does ACP JSON-RPC streaming over stdout with `CLAUDE_CODE_OAUTH_TOKEN`. We do NOT need to reimplement the ACP protocol layer.

### What we need to build (revised scope):

```
streaming_coder/
├── __init__.py
├── acp_parser.py      # Parse acpx JSON-RPC stdout into AcpEvent objects
├── editor.py          # StreamingEditor (1.5s edit loop + compose_display)
├── reactions.py       # StatusReactionController (debounce + stall + tool classification)
├── config.py          # Config + defaults (including CLAUDE_CODE_OAUTH_TOKEN)
├── bridge.py          # Hermes integration (GatewayStreamConsumer adapter)
└── pool.py            # Session tracking (thread_id → acpx session name)
```

### Revised effort estimate:

| Component | Old estimate | New estimate | Why |
|-----------|-------------|-------------|-----|
| ACP protocol layer | 2h | **0h** | acpx handles it |
| ACP parser | 0h | **1h** | Parse JSON lines into events |
| Editor + reactions | 1.5h | **1.5h** | Same |
| Integration | 1h | **1.5h** | GatewayStreamConsumer extension |
| Testing | 0.5h | **0.5h** | Same |
| **Total** | **5h** | **~4.5h** | Saved ~0.5h |
