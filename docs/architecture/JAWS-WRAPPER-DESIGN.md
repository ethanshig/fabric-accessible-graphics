# JAWS-Friendly Claude Code Wrapper -- Architecture Design

Date: 2026-02-26
Status: PROPOSAL
Author: Architect Agent (Ethan's request)


## Problem Statement

Claude Code is a Node.js TUI app using Ink (React for terminals). When a JAWS
screen reader user runs it in WSL2 on Windows, four specific problems occur:

Problem 1 -- Streaming noise. Claude Code streams tokens character by character.
JAWS reads ALL terminal output as it arrives: partial words, ANSI escape codes,
spinner frames, progress bars. The user hears gibberish. Even pressing INSERT+S
(JAWS silence key) does not help because new output keeps refreshing the screen
buffer, restarting JAWS speech.

Problem 2 -- No navigation. Once Claude finishes, the response scrolls off the
terminal. The user cannot go back and review what Claude said. JAWS reads the
visible terminal buffer, not a scrollback log.

Problem 3 -- AskUserQuestion blocks. Claude asks questions with selectable
options rendered as a React component. The blind user cannot see the options
or interact with the selection UI.

Problem 4 -- JAWS silence defeat. Normally JAWS users press INSERT+S to silence
speech, then re-read at their own pace. But Claude Code continuously writes to
the terminal, which triggers JAWS to resume speaking. The user has no way to
"pause" the output.


## Existing Mitigations

We already have:
- Settings in .claude/settings.json: prefersReducedMotion, spinnerTipsEnabled=false,
  terminalProgressBarEnabled=false, CLAUDE_CODE_DISABLE_TERMINAL_TITLE
- Hooks on Stop, Notification, PreToolUse(AskUserQuestion), PostToolUse(Bash)
  that pipe text through announce.js -> announce.ps1 -> JAWS API (JFWSayString)
- announce.ps1 speaks via JAWS DLL, falls back to NVDA, falls back to SAPI

These help but do not solve the core problem: Claude Code's terminal output
is inherently hostile to JAWS.


## Fundamental Constraint

We cannot modify Claude Code source code. It is a closed-source Node.js binary.
We must work with:
- CLI flags (-p, --output-format, --input-format)
- The Claude Agent SDK (@anthropic-ai/claude-agent-sdk)
- Hooks (shell commands triggered on events)
- Process-level I/O manipulation (pipes, PTYs, log files)


## Three Options

Each option is progressively more capable and more complex. They are not
mutually exclusive -- Option A can be a stepping stone to B, and B to C.


------------------------------------------------------------------------
## OPTION A: Log + Announce (Minimal Wrapper)
------------------------------------------------------------------------

### Concept

Do not let JAWS read the terminal at all. Instead:
1. Run Claude Code in a hidden/suppressed terminal
2. Capture output to a log file
3. Announce only completed responses via JAWS API
4. Let the user review the log at their own pace in a second window

### Architecture

```
  User types in:   Windows CMD/PowerShell (JAWS reads this normally)
       |
       v
  [launch.ps1]  -- starts Claude Code in WSL2 with output redirected
       |
       |--- claude -p --output-format stream-json ... 2>/dev/null
       |       |
       |       +---> output piped to: tee /tmp/claude-session.jsonl
       |
       +--- [watcher.ps1] -- tail -f /tmp/claude-session.jsonl
                |
                +--- on "result" event: extract .result text
                |       |
                |       +---> JFWSayString(result_text)
                |       +---> append to readable-log.txt
                |
                +--- on "assistant" event: extract text blocks
                        |
                        +---> append to readable-log.txt
```

The user has two windows:
- Window 1: The command window. User types prompts, hears announcements.
- Window 2: A text file (readable-log.txt) open in Notepad or a text editor.
  JAWS reads this normally with full cursor navigation.

### Components

1. launch.ps1 (PowerShell on Windows)
   - Takes user prompt as argument
   - Calls: wsl claude -p "PROMPT" --output-format stream-json > session.jsonl
   - Starts watcher.ps1 in background
   - Waits for completion
   - Approximately 40 lines of PowerShell

2. watcher.ps1 (PowerShell on Windows)
   - Reads session.jsonl line by line (tail-follow pattern)
   - Parses each JSON line
   - On type=="result": speaks via JAWS, writes to log
   - On type=="assistant": writes text to log
   - Approximately 60 lines of PowerShell

3. readable-log.txt (plain text file)
   - Updated after each Claude response
   - Timestamped entries
   - The user opens this in Notepad and uses JAWS cursor commands to review

### How It Solves Each Problem

Problem 1 (Streaming noise): SOLVED. Claude runs in -p mode. Its stdout goes
to a JSONL file, not to a terminal JAWS can see. No streaming text reaches JAWS.

Problem 2 (No navigation): PARTIALLY SOLVED. The readable-log.txt file is
navigable with standard JAWS text navigation. But the user must Alt-Tab to
the Notepad window and refresh (close+reopen or use a file that auto-reloads).

Problem 3 (AskUserQuestion): NOT SOLVED. In -p mode, Claude does not use
AskUserQuestion. But the user also cannot have a multi-turn conversation.
Each invocation is a single prompt-response. For multi-turn, user must
use --continue flag on next invocation.

Problem 4 (Silence defeat): SOLVED. No terminal output reaches JAWS.
Announcements are discrete JFWSayString calls the user can interrupt normally.

### Technology Stack

- PowerShell 5.1+ (ships with Windows)
- wsl.exe (ships with WSL2)
- JAWS API (jfwapi.dll, already used in announce.ps1)
- No additional dependencies

### Complexity

- Estimated: 4-8 hours to build
- 2-3 files, ~150 lines total
- Low risk, easy to debug

### Limitations

- Single-turn only per invocation (must use --continue for multi-turn)
- No real-time progress feedback ("Claude is thinking..." silence)
- No tool approval (must use --allowedTools or --dangerously-skip-permissions)
- User cannot cancel mid-operation
- Log file review requires Alt-Tab to another window


------------------------------------------------------------------------
## OPTION B: Filtered Terminal (Process Interceptor)
------------------------------------------------------------------------

### Concept

Run Claude Code normally in interactive mode, but intercept its PTY output
before it reaches the terminal JAWS reads. A filter process strips streaming
tokens, ANSI codes, and spinners. It only passes through complete sentences
and structured events. JAWS sees a clean, quiet terminal.

### Architecture

```
  [Windows Terminal with JAWS]
       ^
       | (clean output only)
       |
  [filter-proxy.js]  -- Node.js process running in WSL2
       ^       |
       |       v
  (raw PTY)  (user input passthrough)
       ^       |
       |       v
  [claude]  -- Claude Code interactive mode
```

The filter-proxy sits between Claude Code and the terminal:

```
  User keyboard --> filter-proxy stdin --> Claude Code stdin
  Claude Code stdout --> filter-proxy (buffer+filter) --> Terminal stdout
```

This is implemented as a PTY proxy: filter-proxy allocates a pseudo-terminal,
spawns Claude Code inside it (so Claude thinks it has a real terminal and
renders its Ink UI normally), then reads from Claude's PTY master and writes
filtered output to its own stdout (which is the real terminal JAWS reads).

### Components

1. filter-proxy.js (Node.js, ~300 lines)
   - Uses node-pty to spawn Claude Code
   - Buffers all output from Claude
   - State machine with modes:
     * THINKING: Claude is generating. Suppress all output. Optionally emit
       a single "Claude is thinking..." line.
     * TOOL_USE: Claude is running a tool. Emit "Running: <tool_name>..."
     * RESPONSE_COMPLETE: Claude finished responding. Emit the full response
       as clean plaintext (strip markdown, ANSI codes).
     * INPUT: User is typing. Pass through normally.
   - Detects state transitions by pattern-matching Claude's Ink output:
     * Spinner characters (braille dots, arrows) = THINKING
     * Tool use indicators = TOOL_USE
     * Prompt indicator ("> ") = INPUT (response is complete)
   - ANSI code stripper: removes all ESC[ sequences
   - Markdown stripper: removes **, ##, ```, etc.

2. announce-bridge.js (enhancement to existing announce.js)
   - When filter-proxy detects a complete response, it also triggers
     a JAWS announcement via the existing PowerShell bridge
   - Announces: "Claude responded. [first 200 chars]. Press up arrow to read."

3. question-handler.js (~100 lines)
   - When filter-proxy detects an AskUserQuestion pattern, it:
     * Suppresses the React UI rendering
     * Emits a clean numbered list: "Question: ... 1. option 2. option"
     * Reads user input (a number or text)
     * Sends the appropriate keystrokes to Claude's PTY

### How It Solves Each Problem

Problem 1 (Streaming noise): SOLVED. The filter suppresses all partial tokens.
Only complete, cleaned responses reach the terminal.

Problem 2 (No navigation): PARTIALLY SOLVED. Complete responses are emitted
to the terminal as plain text. The user can use JAWS review cursor to read
them. But long responses may still scroll off. Could be combined with a
scrollback log file for full review.

Problem 3 (AskUserQuestion): SOLVED (with caveats). The question-handler
detects the UI pattern and re-renders it as a simple numbered list. But this
depends on pattern-matching Claude Code's Ink output, which could break with
updates.

Problem 4 (Silence defeat): SOLVED. No streaming output reaches the terminal.
Only discrete, complete text blocks are emitted.

### Technology Stack

- Node.js 18+ (already installed for Claude Code)
- node-pty (npm package for PTY allocation, ~50KB)
- strip-ansi (npm package, trivial)
- Existing announce.ps1 bridge

### Complexity

- Estimated: 2-4 days to build
- The PTY proxy pattern is well-established but tricky to debug
- Main risk: Claude Code updates change the Ink UI rendering, breaking
  the pattern matching
- Need to handle edge cases: long tool outputs, permission prompts,
  multi-line code blocks

### Limitations

- Fragile: depends on pattern-matching Claude Code's terminal output format.
  Any update to Claude Code's Ink UI could break the filter.
- Cannot parse structured data (we are guessing from rendered terminal output)
- PTY proxying has latency (~50ms per frame)
- AskUserQuestion detection is heuristic, not guaranteed
- Hard to test automatically (visual output patterns)
- Does not work with -p mode (only interactive mode)


------------------------------------------------------------------------
## OPTION C: Accessible Client (Full Alternative Interface)
------------------------------------------------------------------------

### Concept

Do not use Claude Code's terminal UI at all. Build a custom accessible client
using the Claude Agent SDK (@anthropic-ai/claude-agent-sdk). This client
communicates with the same Claude Code backend but presents a JAWS-optimized
interface. The user interacts through a simple line-mode interface that JAWS
handles natively.

### Architecture

```
  [Windows Terminal / CMD]
       ^       |
       |       v
  [accessible-claude.js]  -- Custom Node.js client in WSL2
       |
       |--- @anthropic-ai/claude-agent-sdk (V2 API)
       |       |
       |       +---> unstable_v2_createSession({ model, tools, ... })
       |       +---> session.send(userPrompt)
       |       +---> for await (msg of session.stream()) { ... }
       |
       |--- JAWS Bridge (announce to screen reader)
       |--- Response Buffer (reviewable history)
       |--- Question Handler (custom permission/question UI)
       |--- MCP Server Config (tactile, rhinomcp)
```

### Components

1. accessible-claude.js (main client, ~500 lines)

   The core loop:

   ```
   create session with SDK
   load settings (allowed tools, MCP servers, system prompt)
   loop:
     print "> " prompt
     read user input from stdin (readline)
     if input is a command (/history, /repeat, /quit, /tools):
       handle locally
     else:
       session.send(input)
       set status: "Thinking..."
       announce("Claude is thinking")
       for await (msg of session.stream()):
         if msg.type == "assistant":
           buffer the complete text
         if msg.type == "result":
           clean the text (strip markdown, etc)
           print cleaned text to terminal
           announce first 200 chars via JAWS
           save to history buffer
       print "Done."
   ```

   Key design: during streaming, NOTHING is printed to the terminal.
   Only when the response is complete does the full text appear.
   This means JAWS sees a quiet terminal, then a block of text, then "Done."

2. question-handler.js (~150 lines)

   Handles the canUseTool callback from the SDK:

   ```
   canUseTool: async (toolName, input, options) => {
     // Announce what Claude wants to do
     announce(`Claude wants to use ${toolName}`)
     print(`Claude wants to run: ${toolName}`)
     print(`Details: ${summarize(input)}`)
     print(`1. Allow  2. Allow always  3. Deny`)
     print(`Type 1, 2, or 3:`)
     const answer = await readline()
     if answer == "1": return { behavior: "allow" }
     if answer == "2": return { behavior: "allow", updatedPermissions: ... }
     if answer == "3": return { behavior: "deny", message: "User denied" }
   }
   ```

   This is the SDK's native permission callback. It replaces both the
   AskUserQuestion UI AND the permission prompt UI with a simple numbered
   choice that JAWS reads and the user answers by typing a number.

3. history-buffer.js (~100 lines)

   Stores all responses in memory and optionally on disk:

   ```
   /history       -- show numbered list of past responses
   /history 3     -- re-read response #3
   /repeat        -- re-read last response
   /repeat full   -- read full last response (not truncated)
   /save          -- save session to file
   /export        -- export session as plain text
   ```

   Each response is stored as { index, timestamp, prompt, response, tools_used }.
   The /history command prints a numbered list the user can navigate.

4. announce-bridge.js (reuse/enhance existing)

   Already built. Pipes text to announce.ps1 which calls JFWSayString.
   Enhanced to support:
   - Priority levels (interrupt current speech for urgent messages)
   - Queue mode (queue non-urgent messages)
   - Brevity control (short announcement + "press up arrow for full text")

5. session-config.js (~100 lines)

   Loads configuration from the existing .claude/settings.json and .mcp.json:
   - Reads allowed tools
   - Loads MCP server configs (tactile, rhinomcp)
   - Loads system prompt and CLAUDE.md
   - Sets permission mode

6. startup script: acclaude (bash wrapper, ~20 lines)

   ```bash
   #!/bin/bash
   # acclaude -- Accessible Claude for JAWS users
   cd /mnt/c/Users/ethan/fabric-accessible-graphics
   exec node src/accessible-client/accessible-claude.js "$@"
   ```

   The user types `acclaude` to start. Or `acclaude "convert floor plan"` for
   one-shot mode.

### Detailed SDK Integration

The V2 SDK API maps perfectly to this design:

```typescript
import {
  unstable_v2_createSession,
  unstable_v2_resumeSession
} from "@anthropic-ai/claude-agent-sdk";

// Create session with full Claude Code capabilities
const session = unstable_v2_createSession({
  model: "claude-sonnet-4-6",
  systemPrompt: {
    type: "preset",
    preset: "claude_code",
    append: "Output plain text only. No markdown. No emojis. Short sentences."
  },
  settingSources: ["user", "project", "local"],
  tools: { type: "preset", preset: "claude_code" },
  allowedTools: [
    "Read", "Glob", "Grep",
    "mcp__tactile__image_to_piaf",
    "mcp__tactile__list_presets",
    "mcp__rhinomcp__*"
  ],
  mcpServers: loadFromMcpJson(),
  canUseTool: questionHandler.canUseTool,
  hooks: {
    Stop: [{ hooks: [announceHook] }],
    Notification: [{ hooks: [announceHook] }]
  }
});
```

Session resume works naturally:

```typescript
// Save session ID when session ends
saveSessionId(session.sessionId);

// Resume later
const resumed = unstable_v2_resumeSession(savedId, { ...sameOptions });
```

### How It Solves Each Problem

Problem 1 (Streaming noise): FULLY SOLVED. The SDK streams messages as
structured objects. We buffer them in code and only print the final text.
No streaming tokens ever reach the terminal. Zero noise.

Problem 2 (No navigation): FULLY SOLVED. The history buffer stores every
response. /history lists them. /history N re-reads response N. /repeat
re-reads the last response. /save exports to a file. Full navigation.

Problem 3 (AskUserQuestion): FULLY SOLVED. The SDK's canUseTool callback
intercepts ALL permission prompts and tool approvals. We render them as
simple numbered choices ("Type 1, 2, or 3:"). JAWS reads this natively.
No React UI, no selection widgets.

Problem 4 (Silence defeat): FULLY SOLVED. Nothing is written to the terminal
during thinking/streaming. The terminal is quiet. When the response arrives,
it appears as a block of text. JAWS can read it with cursor commands at the
user's own pace.

### User Experience Flow

```
$ acclaude
Accessible Claude. Type your message or /help for commands.
Session started.

> Convert the Marygrove floor plan to tactile
Claude is thinking...
[5 seconds of silence -- terminal is quiet, JAWS is quiet]
[JAWS speaks: "Claude responded. Conversion complete. Output saved to..."]

Conversion complete.
Output file: /mnt/c/Users/ethan/output/marygrove_piaf.pdf
Density: 18.3 percent, acceptable.
Labels detected: 24 Braille labels placed.
Pages: 1.
Done.

> /repeat
[JAWS re-reads the entire response above]

> /history
1. [14:30] Convert the Marygrove floor plan to tactile
2. [14:32] Create a site boundary 200 by 150

> Create a site boundary 200 by 150
Claude wants to run: Bash
Details: tasc site 200 150
1. Allow  2. Allow always  3. Deny
Type 1, 2, or 3: 2

Claude is thinking...
[JAWS speaks: "Site boundary created. 200 by 150 feet."]

Site boundary created.
Name: site
Dimensions: 200 by 150 feet.
Done.

> /quit
Session saved. Goodbye.
```

### Technology Stack

- Node.js 18+ (already installed)
- @anthropic-ai/claude-agent-sdk (npm install)
- readline (Node.js built-in, for line-mode input)
- Existing announce.ps1 bridge for JAWS
- Existing .claude/settings.json and .mcp.json for config

### Complexity

- Estimated: 3-5 days to build initial version
- ~800-1000 lines across 5-6 files
- Medium risk: SDK is marked "unstable preview" but is Anthropic's official
  supported approach
- Main risk: SDK V2 API changes before stabilizing
- Mitigation: V1 query() API is stable and works the same way, just more verbose

### Limitations

- Does not run Claude Code's Ink UI, so some visual features are unavailable
  (diff viewer, file tree, etc.) -- but those are inaccessible anyway
- SDK V2 is "unstable preview" -- API may change
- Requires npm install of the SDK package
- Initial session startup takes 2-3 seconds (spawning Claude Code subprocess)
- Some edge cases in tool output formatting may need tuning


------------------------------------------------------------------------
## Comparison Matrix
------------------------------------------------------------------------

```
                          Option A         Option B         Option C
                          Log+Announce     Filtered PTY     SDK Client
------------------------------------------------------------------------
Problem 1 (streaming)     SOLVED           SOLVED           SOLVED
Problem 2 (navigation)    PARTIAL (file)   PARTIAL (term)   SOLVED (/history)
Problem 3 (questions)     NOT SOLVED       FRAGILE          SOLVED (canUseTool)
Problem 4 (silence)       SOLVED           SOLVED           SOLVED

Multi-turn conversation   No (use -c)      Yes              Yes
Real-time progress        No               Limited          Yes (status msgs)
Tool approval             No (pre-allow)   Fragile          Native (SDK callback)
Fragility                 Very stable      Fragile          Moderate (SDK API)
Build effort              4-8 hours        2-4 days         3-5 days
Maintenance               Minimal          High (breaks)    Low-moderate
Dependencies              PowerShell only  node-pty         claude-agent-sdk
Works without changes     Yes              Yes              Yes
MCP server support        Via CLI flags    Via interactive   Native (SDK config)
Session resume            Via --continue   Via interactive   Native (SDK sessions)
```


------------------------------------------------------------------------
## Recommendation
------------------------------------------------------------------------

Build Option C (Accessible Client via Agent SDK).

Rationale:

1. It is the only option that fully solves all four problems.

2. The Agent SDK is Anthropic's official supported way to build custom clients.
   It gives us structured message objects instead of parsing terminal output.
   This is the correct abstraction layer.

3. Option B (filtered PTY) is fragile. It depends on reverse-engineering
   Claude Code's Ink rendering, which changes with every update. We would
   spend more time maintaining the filter than building features.

4. Option A is a reasonable stopgap but leaves Problem 3 (AskUserQuestion)
   unsolved and limits the user to single-turn interactions. Daniel's workflow
   requires multi-turn conversations (design a building, then iterate).

5. The SDK's canUseTool callback is a perfect fit for JAWS. It lets us replace
   ALL visual permission/question UI with simple "Type 1, 2, or 3:" prompts
   that any screen reader handles natively.

6. Build effort is comparable to Option B (3-5 days vs 2-4 days) but Option C
   is far more maintainable and extensible.

Implementation plan:

Phase 1 (Day 1-2): Core client
- Install SDK, create session, basic send/receive loop
- Strip markdown from responses, print clean text
- Basic JAWS announcement on response complete
- /quit, /help commands

Phase 2 (Day 2-3): Permission handling + history
- Implement canUseTool callback with numbered choices
- History buffer with /history, /repeat, /save
- Session resume with /continue

Phase 3 (Day 3-4): MCP + polish
- Load MCP servers (tactile, rhinomcp) from .mcp.json
- Load CLAUDE.md project instructions
- Status announcements ("Claude is thinking...", "Running tool...")
- Error handling and graceful degradation

Phase 4 (Day 4-5): Testing with Daniel
- Test with actual JAWS on Windows
- Tune announcement timing and verbosity
- Add any missing /commands based on feedback
- Write user documentation

Optional Phase 5: One-shot mode
- acclaude "prompt here" for single-turn (like -p mode)
- acclaude --continue for continuing last session
- Integration with existing tact and tasc CLIs


------------------------------------------------------------------------
## Technical Notes
------------------------------------------------------------------------

### SDK V2 vs V1

The V2 API (unstable_v2_createSession) is cleaner but marked "unstable preview."
If it changes, we can fall back to the V1 query() API which is stable:

```typescript
// V1 equivalent
const q = query({
  prompt: userInput,
  options: { model, canUseTool, ... }
});
for await (const msg of q) {
  // same message handling
}
```

The main difference is V1 requires an async generator for multi-turn, while
V2 uses simple send()/stream() calls. For our use case, both work fine.

### JAWS Speech Priorities

JFWSayString with interrupt=true cuts off any current speech. We should use:
- interrupt=true for: permission prompts, errors, "Done."
- interrupt=false for: status updates, progress messages

### WSL2 Considerations

The SDK spawns a Claude Code subprocess. In WSL2, this works natively since
Claude Code is installed in WSL. The announce bridge calls powershell.exe
via WSL2's Windows interop, which is already proven to work.

### MCP Server Loading

The SDK accepts mcpServers as a config object. We read .mcp.json and pass it:

```typescript
const mcpConfig = JSON.parse(readFileSync(".mcp.json", "utf8"));
// mcpConfig.mcpServers -> pass to SDK's mcpServers option
```

### Readline vs Raw Mode

Node.js readline in line mode is perfect for JAWS:
- User types a full line, presses Enter
- JAWS reads back what they type character by character (normal behavior)
- No cursor positioning, no React rendering, no ANSI codes
- Tab completion can be added later for commands


------------------------------------------------------------------------
## File Structure (Option C)
------------------------------------------------------------------------

```
src/accessible-client/
  accessible-claude.js    -- Main client entry point
  session-manager.js      -- SDK session create/resume/config
  question-handler.js     -- canUseTool callback for permissions
  history-buffer.js       -- Response storage + /history commands
  text-cleaner.js         -- Strip markdown/ANSI from responses
  announce.js             -- Enhanced JAWS bridge (reuses existing)
  config-loader.js        -- Read settings.json, .mcp.json, CLAUDE.md

bin/
  acclaude                -- Bash launcher script
```


------------------------------------------------------------------------
## References
------------------------------------------------------------------------

- Claude Agent SDK TypeScript: https://platform.claude.com/docs/en/agent-sdk/typescript
- Claude Agent SDK V2 Preview: https://platform.claude.com/docs/en/agent-sdk/typescript-v2-preview
- Claude Code CLI Reference: https://code.claude.com/docs/en/cli-reference
- Claude Code Headless Mode: https://code.claude.com/docs/en/headless
- JAWS API (JFWSayString): Freedom Scientific JAWS SDK documentation
- node-pty: https://github.com/microsoft/node-pty
- Existing hooks: src/hooks/screen-reader/announce.js, announce.ps1
