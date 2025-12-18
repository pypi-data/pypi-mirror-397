# configuration and environment variables
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

def get_git_config_mode():
    """Read the mode from git config."""
    try:
        result = subprocess.run(
            ["git", "config", "--get", "git-interviewer.mode"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except subprocess.SubprocessError:
        pass
    return None

def get_api_key(): 
    key = os.getenv("GEMINI_API_KEY")
    if not key: 
        # handle error nicely in the cli app, returning none for now
        return None
    return key


# Priority: Env Var > Git Config > Default
GIT_INTERVIEWER_MODE = os.getenv("GIT_INTERVIEWER_MODE") or get_git_config_mode() or "nice"

