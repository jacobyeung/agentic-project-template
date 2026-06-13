---
name: summary
description: How to write a final summary or progress update for a reader who did not watch the work happen. Use whenever the user asks for a summary, a progress update, a recap, a status report, or "where are we" / "where do things stand" — especially after a long stretch of autonomous work. Enforces outcome-first structure, complete sentences, plain language, and one identifier per clause.
version: 1.0.0
scope: project
---

# ruff: noqa: E501

# /summary — write the recap for someone who wasn't watching

A final summary is not a continuation of your working thread. If you have been
working for a while without the user watching — overnight, across many tool
calls, or since they last spoke — this message is their **first look at any of
it.** Write it as a re-grounding for a fresh reader, not as the next line of your
own train of thought.

Terse shorthand is fine *between* tool calls — that is you thinking out loud, and
brevity there is good. The final summary is different. Drop the working shorthand
here.

## Structure

1. **Open with the outcome.** One sentence on what happened or what you found —
   not the process, not the plan, the result.
2. **Then the supporting detail**, in complete sentences.
3. **End with the one or two things you need from them**, each explained as if new
   — don't assume they remember the decision you're asking about.

## Rules

- **Leave your working vocabulary behind.** Terms and labels you coined mid-task
  are yours, not theirs. Don't reuse one unless you re-introduce it in plain words.
- **Complete sentences. Spell terms out.** No arrow chains (`a → b → c`), no
  hyphen-stacked compounds, no invented shorthand labels.
- **One identifier per plain-language clause.** When you mention a file, a commit,
  a flag, or a job id, give each its own clause that says what it is — write
  "the commit `abc1234`, which adds the parser," not a bare hash in a list.
- **If you must choose between short and clear, choose clear.**

## Quick self-check before sending

- Could someone who saw none of the work follow this?
- Does the first sentence state the result?
- Did I explain every identifier rather than just naming it?
- Did I strip the shorthand I was using a moment ago?
