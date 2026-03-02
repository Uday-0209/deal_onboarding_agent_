from v5.Backend.redis_client import get_messages, get_intake_field
from v5.Backend.llm_client import chat_llm

def generate_deal_summary(deal_id: str) -> str:
    """
    Generate a concise deal summary using the full conversation
    and extracted intake fields.
    """

    intake = get_intake_field(deal_id)
    messages = get_messages(deal_id)

    # Build a readable conversation transcript
    conversation_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in messages
    )

    system_prompt = (
        "You are a professional deal analyst.\n\n"
        "Your task is to generate a concise, structured summary of a deal.\n"
        "Use the extracted deal fields as the source of truth.\n"
        "Use the conversation only for additional context.\n\n"
        "Do NOT invent information.\n"
        "Do NOT ask questions.\n"
        "Return a clear paragraph suitable for long-term storage."
    )

    user_prompt = f"""
Deal Intake Fields:
{intake}

Full Conversation:
{conversation_text}

Produce the deal summary now.
"""

    summary = chat_llm([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ])

    return summary.strip()