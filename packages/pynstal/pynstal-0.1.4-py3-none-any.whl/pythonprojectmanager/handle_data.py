from dataclasses import dataclass
import json
import os
import sys
from pathlib import Path

# Use global config dir: prefer XDG_CONFIG_HOME/pynstal, else ~/.pynstal
_xdg = os.getenv("XDG_CONFIG_HOME")
if _xdg:
    DATA_DIR = os.path.join(_xdg, "pynstal")
else:
    DATA_DIR = os.path.join(os.path.expanduser("~"), ".pynstal")

@dataclass
class InterpretersData:
    FILE_PATH: str
    
    interpreters: list[str] | None = None
    default_interpreter: str | None = None
    
    def is_empty(self) -> bool:
        return self.interpreters is None and self.default_interpreter is None
    
    def save(self) -> None:
        SAVE_PATH = os.path.join(DATA_DIR, self.FILE_PATH)
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.__dict__, f, indent=4)
            
    def __init__(self, file_path) -> None:
        self.FILE_PATH = file_path
        
        LOAD_PATH = os.path.join(DATA_DIR, self.FILE_PATH)
        if os.path.exists(LOAD_PATH):
            with open(LOAD_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.interpreters = data.get("interpreters")
                self.default_interpreter = data.get("default_interpreter")
        else:
            self.interpreters = None
            self.default_interpreter = None

        # If no default interpreter configured, default to current Python executable
        try:
            current = sys.executable
            if not self.default_interpreter and current and os.path.isfile(current):
                # ensure interpreters list exists and contains the current executable
                if self.interpreters is None:
                    self.interpreters = [current]
                else:
                    if current not in self.interpreters:
                        self.interpreters.insert(0, current)
                self.default_interpreter = current
                # persist the change
                self.save()
        except Exception:
            # avoid failing import/initialization on unexpected environments
            pass

interpreters_data = InterpretersData("interpreters.json")


# Project-scoped config (stored in ./.pynstal.json)
PROJECT_CONFIG_FILENAME = ".pynstal.json"


def _project_config_path(cwd: str | None = None) -> str:
    base = cwd or os.getcwd()
    return os.path.join(base, PROJECT_CONFIG_FILENAME)


def load_project_config(cwd: str | None = None) -> dict:
    """Load project-local configuration from ./pynstal.json."""
    path = _project_config_path(cwd)
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        pass
    return {}


def save_project_config(data: dict, cwd: str | None = None) -> None:
    """Persist project-local configuration to ./pynstal.json."""
    path = _project_config_path(cwd)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass


def get_project_default_interpreter(cwd: str | None = None) -> str | None:
    """Return project-local default interpreter if set."""
    data = load_project_config(cwd)
    val = data.get("default_interpreter")
    return val if isinstance(val, str) else None


def set_project_default_interpreter(path: str, cwd: str | None = None) -> None:
    """Set the project-local default interpreter path."""
    data = load_project_config(cwd)
    data["default_interpreter"] = path
    save_project_config(data, cwd)


def clear_project_default_if_inside(path_prefix: str, cwd: str | None = None) -> None:
    """Unset project default interpreter if it lives under path_prefix."""
    current = get_project_default_interpreter(cwd)
    if current and os.path.abspath(current).startswith(os.path.abspath(path_prefix)):
        data = load_project_config(cwd)
        data.pop("default_interpreter", None)
        save_project_config(data, cwd)
