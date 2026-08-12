
"""
ORGANIC CODE PRINZIPIEN:
1. Code ist DNA - speichert sich selbst als String
2. Selbst-Replikation mit Mutation
3. Selbst-Heilung bei Fehlern
4. Wachstum durch Umgebungssignale
"""

class OrganicStrand:
    """Repräsentiert ein Stück lebenden Code - wie DNA."""
    def __init__(self, sequence: str, name: str):
        self.name = name
        self.sequence = sequence  # Python code als String
        self.fitness = 0.0
        self.age = 0
        self.mutations = []

    def transcribe(self):
        """DNA -> RNA -> ausführbarer Code"""
        # Einfach: exec in isoliertem Namespace
        local_ns = {}
        try:
            exec(self.sequence, {}, local_ns)
            return local_ns
        except Exception as e:
            return {"error": str(e), "strand": self}

    def mutate(self, rate=0.05):
        # Organische Mutation: zufälliges Einfügen/Ändern
        # In echt: LLM-gestützte Mutation
        self.mutations.append(f"mut@{self.age} rate={rate}")
        self.age += 1

    def replicate(self):
        child = OrganicStrand(self.sequence, f"{self.name}_child")
        child.mutations = self.mutations.copy()
        child.mutate()
        return child
