import os
import json
from datetime import datetime
import pandas as pd
from typing import Dict, Any, Optional, Set

class ScheduleManager:
    """Handles CSV schedule parsing and persistence of posted IDs.

    Attributes
    ----------
    csv_path: str
        Path to the schedule CSV.
    state_path: str
        Path to the JSON file storing posted row IDs.
    posted_ids: Set[str]
        In‑memory set of IDs already processed.
    """

    def __init__(self, csv_path: str, state_path: str):
        self.csv_path = csv_path
        self.state_path = state_path
        self.posted_ids: Set[str] = self._load_state()

    def _load_state(self) -> Set[str]:
        """Load posted IDs from ``state_path``.

        Returns
        -------
        Set[str]
            Set of row IDs that have already been posted.
        """
        if not os.path.exists(self.state_path):
            return set()
        try:
            with open(self.state_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return set(data)
        except Exception:
            # Corrupted state – start fresh
            return set()

    def _save_state(self) -> None:
        """Persist the current ``posted_ids`` set to ``state_path``."""
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(list(self.posted_ids), f, indent=2)

    def get_due_post(self) -> Optional[Dict[str, Any]]:
        """Return the first row that is due today and not yet posted.

        The CSV must contain columns ``row_id``, ``post_date`` (YYYY‑MM‑DD) and
        ``raw_text``. If multiple rows are due, the earliest one in the file is
        chosen and a warning is logged.
        """
        if not os.path.exists(self.csv_path):
            return None
        df = pd.read_csv(self.csv_path, dtype=str)
        # Normalise column names
        df = df.rename(columns=lambda c: c.strip().lower())
        required = {"row_id", "post_date", "raw_text"}
        if not required.issubset(set(df.columns)):
            raise ValueError(f"CSV missing required columns: {required - set(df.columns)}")

        today_str = datetime.now().date().isoformat()
        due_mask = (df["post_date"] == today_str) & (~df["row_id"].isin(self.posted_ids))
        due_rows = df[due_mask]
        if due_rows.empty:
            return None
        # If more than one, log a warning (still only process the first)
        if len(due_rows) > 1:
            print(f"[WARN] Multiple rows due today ({len(due_rows)}). Processing the first one.")
        row = due_rows.iloc[0]
        return {
            "row_id": row["row_id"],
            "post_date": row["post_date"],
            "raw_text": row["raw_text"],
        }

    def mark_as_posted(self, row_id: str) -> None:
        """Add ``row_id`` to the persisted state to avoid duplicate posts."""
        self.posted_ids.add(row_id)
        self._save_state()
