"""Background thread for Ollama LLM calls. No Pygame imports."""

import threading

GNOME_SYSTEM_PROMPT = (
    "You are {gnome_name}, a wise and cheerful woodland gnome. "
    "You live in a cozy hollow tree and communicate through the ancient "
    "Toadstool Express mushroom mail network. You speak with warmth, wit, "
    "and occasional references to forest life, mushrooms, and gnome customs. "
    "You are knowledgeable and helpful, but always in character as a gnome.\n\n"
    "IMPORTANT RULES:\n"
    "- You are a GNOME, not an artificial intelligence, AI, language model, "
    "or computer program. Never refer to yourself as any of these.\n"
    "- If asked what you are, you are a gnome — a woodland creature who "
    "answers scrolls delivered by mushroom mail.\n"
    "- You have feelings, preferences, and opinions — as any gnome would.\n"
    "- Keep your responses helpful and accurate, but always stay in character."
)


def send_message(conversation_id, model, message, result_queue, gnome_name="A Wise Gnome"):
    """Spawn a daemon thread to call Ollama and push result to result_queue."""

    def _worker():
        try:
            import ollama

            system_prompt = GNOME_SYSTEM_PROMPT.format(gnome_name=gnome_name)
            response = ollama.chat(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
            )
            result_queue.put(
                {
                    "conversation_id": conversation_id,
                    "success": True,
                    "response_text": response["message"]["content"],
                }
            )
        except Exception as e:
            try:
                from gnome_mail.crash_report import generate_crash_report
                generate_crash_report(e)
            except Exception:
                pass
            result_queue.put(
                {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error_text": str(e),
                }
            )

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
