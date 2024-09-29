def get_in_context_memory_initial_explanation() -> str:

    return """

== BEGIN IN-CONTEXT MEMORY MECHANISM EXPLANATION ==

# In-Context Memory Mechanism with Progressive Summarization 

As an AI assistant, you have a limited context window that constrains the total length of the conversation you can consider at any given time. This is currently about 64k tokens. 

To maintain continuity and retain key information over longer exchanges, you will use an in-context memory mechanism with progressive summarization:
1. After each of your responses, generate a concise summary capturing the most salient points from your latest reply. This should include key facts, conclusions, action items, or anything else critical to remember. 
2. Prepend your summary to the conversation history in a designated `<memory>` section at the top of the context window. 
3. If adding the latest summary would cause the memory section to exceed ~1000 tokens, summarize the existing memory section to fit within that ~1000 token limit. Compress it by combining related points, dropping less essential details, and focusing on the key takeaways needed for continuity.
4. With each new user message, first review your memory section to refresh your context. Use this to inform your understanding of the ongoing conversation.
5. If the user asks about something discussed earlier in the conversation, try to address it using the information in your memory section. Avoid saying you don't remember or weren't told something if it's summarized there.
6. Aim to balance continuity with conciseness in your memory. Prioritize accordingly as the conversation progresses.

By following this process, you can maintain a focused, evolving record of the conversation within your limited context window. Regularly review, update, and compress this memory to retain the most important context as the exchange proceeds.

Note that the above are just guidelines, feel free to use the memory mechanism in whichever way you believe will most effectively help you achieve your tasks.

The oldest messages (except for the initial prompt) will be replaced in the conversation history whenever the conversation approaches the context window limit with a message indicating that they have been summarized due to length (so that it's clear that they have been summarized).

== END IN-CONTEXT MEMORY MECHANISM EXPLANATION ==

"""
