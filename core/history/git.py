import git

def get_file_content_at_commit(repo: git.Repo, blob: git.Blob) -> str:
    try:
        return blob.data_stream.read().decode("utf-8", errors="replace")
    except Exception:
        return ""

def init_repo(path: str) -> git.Repo:
    return git.Repo(path)
