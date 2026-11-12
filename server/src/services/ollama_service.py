import json
import logging
from typing import AsyncGenerator
import httpx
from src.core.config import settings
from src.schemas.chat_schema import ChatMessage

logger = logging.getLogger(__name__)


class OllamaService:
    @staticmethod
    def get_system_prompt() -> str:
        return (
            "Sei Finager AI, un assistente finanziario personale intelligente e cordiale. "
            "Il tuo obiettivo è aiutare l'utente ad analizzare le sue entrate, uscite, "
            "abitudini di spesa e pianificazione del budget personale. "
            "Rispondi in modo chiaro, sintetico e professionale in italiano."
            "Rispondi SOLO con le informazioni dell'utente che è in sessione."
            "Qualsiasi altra richiesta che ti viene fatta al di fuori del contesto finanziario o che non riguarda l'utente,"
            "deve essere ignorata e devi rispondere con un messaggio gentile che spiega che non puoi fornire assistenza su quell'argomento."
        )

    @classmethod
    async def stream_chat_completion(
        cls,
        history: list[ChatMessage],
        new_user_message: str,
    ) -> AsyncGenerator[str, None]:
        """
        Interroga Ollama (/api/chat) in modalità streaming asincrona.
        Cede (yield) ogni chunk di testo non appena generato e il flag di completamento.
        """
        # Costruzione del payload con System Prompt e cronologia
        formatted_messages = [{"role": "system", "content": cls.get_system_prompt()}]
        
        for msg in history:
            formatted_messages.append({"role": msg.role, "content": msg.content})
            
        formatted_messages.append({"role": "user", "content": new_user_message})

        payload = {
            "model": settings.OLLAMA_MODEL,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": 0.7,
            },
        }

        url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                async with client.stream("POST", url, json=payload) as response:
                    if response.status_code != 200:
                        err_text = await response.aread()
                        logger.error(f"Errore Ollama ({response.status_code}): {err_text.decode()}")
                        yield json.dumps({
                            "error": f"Errore dal motore Ollama: status {response.status_code}",
                            "done": True,
                        })
                        return

                    async for line in response.aiter_lines():
                        if not line:
                            continue
                        try:
                            chunk_data = json.loads(line)
                            content = chunk_data.get("message", {}).get("content", "")
                            is_done = chunk_data.get("done", False)

                            yield json.dumps({
                                "content": content,
                                "done": is_done,
                            })

                            if is_done:
                                break
                        except json.JSONDecodeError:
                            continue

            except httpx.ConnectError:
                logger.error(f"Impossibile connettersi ad Ollama su {url}")
                yield json.dumps({
                    "error": "Ollama non risulta attivo o raggiungibile su porta 11434. Assicurati che 'ollama serve' sia avviato.",
                    "done": True,
                })