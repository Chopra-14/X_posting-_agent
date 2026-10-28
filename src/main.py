import os
import json
from datetime import datetime
from pathlib import Path

from src.state_manager import ScheduleManager
from src.llm_formatter import LLMService
from src.guardrails import GuardrailChain
from src.browser_actor import SocialMediaActor

# Paths (relative to project root)
DATA_DIR = Path("data")
CSV_PATH = DATA_DIR / "schedule.csv"
STATE_PATH = DATA_DIR / "posted_ids.json"
TRACE_PATH = DATA_DIR / "traces.jsonl"

def ensure_file(path: Path, default_content: str = ""):
    if not path.parent.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(default_content, encoding="utf-8")

def main():
    # Ensure trace file exists
    ensure_file(TRACE_PATH)
    # Initialise components
    scheduler = ScheduleManager(str(CSV_PATH), str(STATE_PATH))
    llm = LLMService()
    guard = GuardrailChain()
    actor = SocialMediaActor()

    due = scheduler.get_due_post()
    if not due:
        print("[INFO] No post due today.")
        return

    row_id = due["row_id"]
    raw_text = due["raw_text"]

    # LLM formatting
    formatted = llm.format_post(raw_text, row_id)
    llm_text = formatted.tweet_text if formatted else None

    # Guardrail validation
    if llm_text:
        passed, reason = guard.validate(raw_text, llm_text)
    else:
        passed, reason = False, "LLM call failed"

    final_text = llm_text if passed else raw_text
    action_status = "success" if actor.post_content(final_text) else "error"

    # Record trace
    trace_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "row_id": row_id,
        "raw_text": raw_text,
        "llm_text": llm_text,
        "guardrail_passed": passed,
        "guardrail_failure_reason": None if passed else reason,
        "final_posted_text": final_text,
        "action_status": action_status,
    }
    with open(TRACE_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(trace_entry) + "\n")

    # Update posted state on successful post
    if action_status == "success":
        scheduler.mark_as_posted(row_id)
        print(f"[INFO] Posted row {row_id} successfully.")
    else:
        print(f"[ERROR] Failed to post row {row_id}.")

if __name__ == "__main__":
    main()
