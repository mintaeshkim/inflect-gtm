class GlobalMemory:
    def __init__(self):
        self.memory = {
            "customers": None,
            "segment_function_code": None,
            "strategies": None,
            "segments": None,
            "onboarding_docs": None,
            "emails_sent": None,
            "meeting_summary": None,
            "upcoming_events": None,
        }

    def set(self, key, value):
        if key not in self.memory:
            raise KeyError(f"Invalid global memory key: {key}")
        self.memory[key] = value

    def get(self, key):
        if key not in self.memory:
            raise KeyError(f"Invalid global memory key: {key}")
        return self.memory[key]

    def dump(self):
        return self.memory