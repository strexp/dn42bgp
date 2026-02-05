import os
import logging
from datetime import datetime
from typing import List, Optional
from git.exc import GitCommandError
from git.objects import Commit

from core.config import settings
from core.history.config import CONFIG
from core.history.git import init_repo, get_file_content_at_commit
from core.history.rpsl import parse_rpsl, is_valid_aut_num
from core.history.storage import load_state, save_state, export_final_json

def process() -> None:
    logging.info("Starting history collection module...")

    if not os.path.exists(settings.REGISTRY_PATH):
        logging.error(f"Registry repository not found at {settings.REGISTRY_PATH}")
        return

    repo = init_repo(str(settings.REGISTRY_PATH))

    state = load_state()
    timeline_data = state["timeline_data"]
    active_states = state["active_states"]
    last_commit_sha: Optional[str] = state["last_commit"]

    rev_range = "master"
    if last_commit_sha:
        try:
            repo.commit(last_commit_sha) 
            rev_range = f"{last_commit_sha}..master"
            logging.info(f"Fetching updates: {rev_range}")
        except Exception:
            logging.warning("Can not find last stats, reprocessing full history...")
            timeline_data = {k: {} for k in CONFIG.keys()}
            active_states = {k: {} for k in CONFIG.keys()}
            last_commit_sha = None

    try:
        commits: List[Commit] = list(repo.iter_commits(rev_range, reverse=True))
    except GitCommandError as e:
        logging.error(f"Git command error (maybe branch is not master?): {e}")
        return

    total_commits = len(commits)
    if total_commits == 0 or (total_commits == 1 and commits[0].hexsha == last_commit_sha):
        logging.info("No new commits found.")
        export_final_json(timeline_data, active_states)
        return

    logging.info(f"{total_commits} commits found, processing...")
    
    current_commit_sha = last_commit_sha

    for i, commit in enumerate(commits):
        current_commit_sha = commit.hexsha
        # avoid double processing
        if last_commit_sha and current_commit_sha == last_commit_sha:
            continue

        commit_date = datetime.fromtimestamp(commit.committed_date).isoformat()

        if i % 100 == 0:
            logging.info(f"Processing commit {i + 1}/{total_commits}: {commit.hexsha[:7]} ({commit_date})")

        parent = commit.parents[0] if commit.parents else None
        diffs = parent.diff(commit) if parent else []

        for diff in diffs:
            path = diff.b_path if diff.b_path else diff.a_path
            
            if not path or not path.startswith("data/"):
                continue

            parts = path.split("/")
            if len(parts) < 3:
                continue

            category = parts[1]
            filename = parts[2]

            if category not in CONFIG:
                continue

            if category == "aut-num" and not is_valid_aut_num(filename):
                continue

            cfg = CONFIG[category]
            change_type = diff.change_type

            # File Deleted
            if change_type == "D":
                if filename in active_states[category]:
                    state_obj = active_states[category].pop(filename)
                    if filename not in timeline_data[category]:
                        timeline_data[category][filename] = []

                    timeline_data[category][filename].append({
                        "value": state_obj["val"],
                        "start": state_obj["start"],
                        "end": commit_date,
                    })

            # File Added, Modified, or Renamed
            elif change_type in ["A", "M", "R"]:
                try:
                    content = get_file_content_at_commit(repo, diff.b_blob)
                    parsed = parse_rpsl(content)

                    # Extract only tracked fields
                    tracked_val = {field: parsed.get(field, "") for field in cfg["track_fields"]}
                    
                    current_state = active_states[category].get(filename)

                    # Only record if the tracked values actually changed
                    if current_state:
                        if current_state["val"] != tracked_val:
                            if filename not in timeline_data[category]:
                                timeline_data[category][filename] = []

                            timeline_data[category][filename].append({
                                "value": current_state["val"],
                                "start": current_state["start"],
                                "end": commit_date,
                            })

                            active_states[category][filename] = {
                                "val": tracked_val,
                                "start": commit_date,
                            }
                    else:
                        active_states[category][filename] = {
                            "val": tracked_val,
                            "start": commit_date,
                        }
                except Exception:
                    pass

    if current_commit_sha:
        save_state(current_commit_sha, timeline_data, active_states)
    
    export_final_json(timeline_data, active_states)
