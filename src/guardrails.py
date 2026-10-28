import re
from typing import Tuple

BANNED_WORDS = {"guarantee", "investment"}

class GuardrailChain:
    """Runs deterministic validation checks on the LLM‑generated tweet.

    Returns a tuple ``(passed: bool, reason: str)``. An empty ``reason``
    indicates success.
    """

    def _length_ok(self, text: str) -> bool:
        return len(text) <= 280

    def _banned_word_ok(self, text: str) -> bool:
        lowered = text.lower()
        return not any(word in lowered for word in BANNED_WORDS)

    def _groundedness_ok(self, original: str, generated: str) -> bool:
        # Extract URLs and @‑mentions from both strings
        pattern = r"(?:http\S+|@\w+)"
        orig_entities = set(re.findall(pattern, original))
        gen_entities = set(re.findall(pattern, generated))
        # All entities in generated must be a subset of original
        return gen_entities.issubset(orig_entities)

    def validate(self, original_text: str, llm_text: str) -> Tuple[bool, str]:
        if not self._length_ok(llm_text):
            return False, "Length > 280"
        if not self._banned_word_ok(llm_text):
            return False, "Banned word detected"
        if not self._groundedness_ok(original_text, llm_text):
            return False, "Groundedness violation (new URL/@mention)"
        return True, ""
