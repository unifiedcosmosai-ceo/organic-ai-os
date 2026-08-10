
# llm_evolver_ollama.py - Echte LLM Version mit Ollama
# pip install ollama
# ollama run codellama:7b  oder mistral

import ollama

class OllamaMutator:
    def __init__(self, model="codellama:7b"):
        self.model = model
    
    def mutate(self, code, instruction):
        response = ollama.chat(model=self.model, messages=[
            {"role": "system", "content": "Du bist ein Python Mutator. Antworte nur mit Code."},
            {"role": "user", "content": f"{instruction}\n\n{code}"}
        ])
        return response['message']['content']
