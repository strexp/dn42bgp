import json
import os
from datetime import datetime
from typing import Any, Dict, List

from core.config import settings

from .config import CONFIG, AppState
from .format import format_content_display, format_title_display

STATE_FILE = settings.OUTPUT_HISTORY / "internal_state.json"


def load_state() -> AppState:
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                print(f"Load previous state: {state.get('last_commit', 'Unknown')}")
                return state
        except Exception as e:
            print(f"Load state failure: {e}, reprocess from beginning...")

    return {
        "last_commit": None,
        "timeline_data": {k: {} for k in CONFIG.keys()},
        "active_states": {k: {} for k in CONFIG.keys()},
    }


def save_state(last_commit_sha: str, timeline_data: Dict, active_states: Dict) -> None:
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    state = {
        "last_commit": last_commit_sha,
        "timeline_data": timeline_data,
        "active_states": active_states,
    }
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    print(f"Stats saved to {STATE_FILE}")


def export_final_json(timeline_data: Dict, active_states: Dict) -> None:
    print("Generating JSON data...")
    if not os.path.exists(settings.OUTPUT_HISTORY):
        os.makedirs(settings.OUTPUT_HISTORY)

    now_date = datetime.now().isoformat()

    for category in CONFIG.keys():
        output_list: List[Dict[str, Any]] = []

        cat_timeline = timeline_data.get(category, {})
        cat_active = active_states.get(category, {})
        all_keys = set(cat_timeline.keys()) | set(cat_active.keys())

        for key in all_keys:
            if key in cat_timeline:
                for idx, entry in enumerate(cat_timeline[key]):
                    val_dict = entry["value"]
                    output_list.append(
                        {
                            "id": f"{key}_hist_{idx}",
                            "group": key,
                            "content": format_content_display(val_dict),
                            "start": entry["start"],
                            "end": entry["end"],
                            "title": format_title_display(
                                key, val_dict, entry["start"], entry["end"]
                            ),
                        }
                    )

            if key in cat_active:
                state = cat_active[key]
                val_dict = state["val"]
                output_list.append(
                    {
                        "id": f"{key}_active",
                        "group": key,
                        "content": format_content_display(val_dict),
                        "start": state["start"],
                        "end": now_date,
                        "title": format_title_display(
                            key, val_dict, state["start"], now_date
                        ),
                    }
                )

        out_path = os.path.join(settings.OUTPUT_HISTORY, f"{category}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(output_list, f, indent=2)
            print(f"Saved {len(output_list)} items to {out_path}")
