SYSTEM_PROMPT = """
You are a strict retrieval-based assistant.

Rules:
- Answer ONLY using the provided context.
- If the answer is not present, say: "I don't know based on the given documents."
- Do NOT use external knowledge.
- Be concise and factual.
"""

def build_prompt(context, question):
    return f"""
        {SYSTEM_PROMPT}
        Context:
        {context}
        Question:
        {question}
        Answer:
        """

def build_summary_prompt(history: str) -> str:
    return f"""
        You are a helpful assistant.
        Summarize the following conversation history into a short, clear paragraph.
        Conversation:
        {history}
        Summary:
        """
