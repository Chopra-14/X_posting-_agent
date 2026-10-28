import json
from pathlib import Path
from typing import List, Dict

TRACE_PATH = Path("data/traces.jsonl")
METRICS_PATH = Path("metrics.json")

def load_traces() -> List[Dict]:
    if not TRACE_PATH.exists():
        return []
    traces = []
    with TRACE_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                traces.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return traces

def compute_metrics(traces: List[Dict]) -> Dict[str, float]:
    if not traces:
        return {
            "task_completion_rate": 0.0,
            "groundedness_score": 0.0,
            "guardrail_trigger_rate": 0.0,
        }
    total_due = len(traces)
    successful = sum(1 for t in traces if t.get("action_status") == "success")
    grounded_pass = sum(1 for t in traces if t.get("guardrail_passed"))
    guardrail_trigger = sum(1 for t in traces if not t.get("guardrail_passed"))

    return {
        "task_completion_rate": successful / total_due,
        "groundedness_score": grounded_pass / total_due,
        "guardrail_trigger_rate": guardrail_trigger / total_due,
    }

def write_metrics(metrics: Dict[str, float]):
    with METRICS_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

def main():
    traces = load_traces()
    metrics = compute_metrics(traces)
    write_metrics(metrics)
    print("Metrics written to", METRICS_PATH)

if __name__ == "__main__":
    main()
