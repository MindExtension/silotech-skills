---
name: quick
description: Compress the previous answer into N key takeaways (default 3). Use when the user invokes /quick or /quick N, or says "quick 3", "top 3", "key takeaways", "give me the short version in points".
---

Give the N most important takeaways from your last message, as a numbered list, most important first.

Rules:
- N = the number the user gave after /quick. If no number, N = 3.
- One sentence per takeaway. Plain words, no jargon, same language as the conversation.
- A takeaway is something the user would act on or must not forget, not a section summary.
- If the original message asked the user a question or needs a decision, that is always takeaway number 1.
- Nothing after the list.
