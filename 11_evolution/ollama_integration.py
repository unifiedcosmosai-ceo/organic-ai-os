
# llm_evolver_ollama.py - Echte LLM Version mit Ollama
# pip install ollama
# ollama run codellama:7b  (oder gemma4:e4b / mistral)

class OllamaMutator:
    """Ollama-gebundener Mutator. Import von 'ollama' laeuft LAZY,
    damit der Import dieses Moduls nie crasht, wenn Ollama nicht installiert ist.
    """

    def __init__(self, model="codellama:7b"):
        self.model = model
        self._ollama = None

    def _client(self):
        if self._ollama is None:
            try:
                import ollama
            except ModuleNotFoundError as e:
                raise ConnectionError(
                    "Ollama ist nicht installiert. Bitte 'pip install ollama' "
                    "und 'ollama run <model>' ausfuehren."
                ) from e
            self._ollama = ollama
        return self._ollama
    
    def mutate(self, code, instruction):
        ollama = self._client()
        response = ollama.chat(model=self.model, messages=[
            {"role": "system", "content": "Du bist ein Python Mutator. Antworte nur mit Code."},
            {"role": "user", "content": f"{instruction}\n\n{code}"}
        ])
        return response['message']['content']
