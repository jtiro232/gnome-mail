"""Background thread for Ollama LLM calls. No Pygame imports."""

import threading


def send_message(conversation_id, model, message, result_queue):
    """Spawn a daemon thread to call Ollama and push result to result_queue."""

    def _worker():
        try:
            import ollama

            response = ollama.chat(
                model=model, messages=[{"role": "user", "content": message}]
            )
            result_queue.put(
                {
                    "conversation_id": conversation_id,
                    "success": True,
                    "response_text": response["message"]["content"],
                }
            )
        except Exception as e:
            result_queue.put(
                {
                    "conversation_id": conversation_id,
                    "success": False,
                    "error_text": str(e),
                }
            )

    t = threading.Thread(target=_worker, daemon=True)
    t.start()
