import argparse
import sys
import os
import json
import importlib.resources as pkg_resources
import subprocess
import shutil
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def cprint(msg: str, color: str = Fore.WHITE) -> None:
    print(f"{color}{msg}{Style.RESET_ALL}")

from .create_venv import create_venv, install_packages_in_venv, install_packages, offer_activation_shell
from .handle_data import (
    clear_project_default_if_inside,
    get_project_default_interpreter,
    interpreters_data,
)


def choose_interpreter(interpreter_arg: str | None) -> str | None:
    """Return interpreter path to use.

    If interpreter_arg is provided, return it. Otherwise prompt the user to choose
    from configured interpreters. Pressing Enter chooses the default interpreter.
    Returns None if no interpreter could be determined.
    """
    if interpreter_arg:
        return interpreter_arg

    # Prefer project-local default, fall back to global default
    project_default = get_project_default_interpreter()
    default = project_default or interpreters_data.default_interpreter
    interpreters = interpreters_data.interpreters or []

    if not interpreters and not default:
        return None

    print("Select interpreter to use for venv creation:")
    for idx, p in enumerate(interpreters, 1):
        marker = "(default)" if p == default else ""
        print(f"  [{idx}] {p} {marker}")
    if default and default not in interpreters:
        print(f"  [D] {default} (default)")

    print("Press Enter to use the default interpreter.")
    print("Or enter the number of the interpreter to use:")
    choice = input("> ").strip()
    if not choice:
        return default

    # allow 'D' to choose explicit default path
    if choice.upper() == "D" and default:
        return default

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(interpreters):
            return interpreters[idx]
    except Exception:
        pass

    print("Invalid selection.")
    return None


def cmd_add_interpreter(args):
    path = args.path
    if interpreters_data.interpreters is None:
        interpreters_data.interpreters = []
    if path in interpreters_data.interpreters:
        print("Interpreter already exists in .pynstal.")
        return
    interpreters_data.interpreters.append(path)
    interpreters_data.save()
    cprint(f"Added interpreter: {path}", Fore.GREEN)


def _print_interpreters_with_indices() -> None:
    interpreters = interpreters_data.interpreters or []
    default = interpreters_data.default_interpreter
    for idx, p in enumerate(interpreters, 1):
        marker = " (default)" if p == default else ""
        print(f"{idx}. {p}{marker}")


def cmd_interpreter_add(args):
    """Interactively add interpreter paths until the user presses Enter."""
    changed = False
    while True:
        path = input("Path to the interpreter (return to finish): ").strip()
        if not path:
            break
        if not os.path.isfile(path):
            cprint(f"Interpreter not found: {path}", Fore.YELLOW)
            continue
        if interpreters_data.interpreters is None:
            interpreters_data.interpreters = []
        if path in interpreters_data.interpreters:
            cprint("Interpreter already exists in .pynstal.", Fore.YELLOW)
            continue
        interpreters_data.interpreters.append(path)
        changed = True
        cprint(f"Added interpreter: {path}", Fore.GREEN)

    if changed:
        # set default if none exists
        if not interpreters_data.default_interpreter and interpreters_data.interpreters:
            interpreters_data.default_interpreter = interpreters_data.interpreters[0]
        interpreters_data.save()
    return 0


def cmd_interpreter_remove(args):
    """Interactively remove interpreters by number until the user presses Enter."""
    if not interpreters_data.interpreters:
        cprint("No interpreters configured.", Fore.YELLOW)
        return 0

    while True:
        print("Currently configured interpreters:")
        _print_interpreters_with_indices()
        choice = input("-> ").strip()
        if not choice:
            break
        try:
            idx = int(choice) - 1
        except Exception:
            cprint("Invalid selection.", Fore.RED)
            continue

        if 0 <= idx < len(interpreters_data.interpreters):
            removed = interpreters_data.interpreters.pop(idx)
            # adjust default if needed
            if interpreters_data.default_interpreter == removed:
                interpreters_data.default_interpreter = interpreters_data.interpreters[0] if interpreters_data.interpreters else None
            interpreters_data.save()
            cprint(f"Removed {removed}", Fore.GREEN)
        else:
            cprint("Invalid selection.", Fore.RED)

    return 0


def cmd_set_default_interpreter(args):
    """Interactively choose and set the global default interpreter."""
    interpreters = interpreters_data.interpreters or []
    if not interpreters:
        cprint("No interpreters configured in .pynstal.", Fore.YELLOW)
        return 2

    current = interpreters_data.default_interpreter
    print("Choose a default interpreter:")
    for idx, p in enumerate(interpreters, 1):
        marker = "(current)" if p == current else ""
        print(f"  [{idx}] {p} {marker}")

    choice = input("> ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(interpreters):
            path = interpreters[idx]
            if not os.path.isfile(path):
                cprint(f"Interpreter not found on disk: {path}", Fore.RED)
                return 2
            interpreters_data.default_interpreter = path
            interpreters_data.save()
            cprint(f"Set default interpreter: {path}", Fore.GREEN)
            return 0
    except Exception:
        pass

    cprint("Invalid selection.", Fore.RED)
    return 1


def cmd_list(args):
    cprint("Interpreters:", Fore.CYAN)
    if interpreters_data.interpreters:
        for p in interpreters_data.interpreters:
            print(f" - {p}")
    else:
        cprint(" - (none)", Fore.YELLOW)
    cprint("Default interpreter:", Fore.CYAN)
    print(f" - {interpreters_data.default_interpreter}")


def load_templates():
    # Use a global templates file in the user's home directory (not CWD).
    # Prefer XDG-style config if available, otherwise ~/.pynstal/templates.json
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        data_dir = os.path.join(xdg, "pynstal")
    else:
        data_dir = os.path.join(os.path.expanduser("~"), ".pynstal")

    tpl_path = os.path.join(data_dir, "templates.json")
    if os.path.exists(tpl_path):
        try:
            with open(tpl_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # fall through to bundled resource
            pass

    try:
        text = pkg_resources.files(__package__).joinpath("templates.json").read_text(encoding="utf-8")
        return json.loads(text)
    except Exception:
        return {"templates": {}}


def save_templates(data):
    """Persist templates to a global templates.json under XDG or ~/.pynstal."""
    xdg = os.getenv("XDG_CONFIG_HOME")
    if xdg:
        data_dir = os.path.join(xdg, "pynstal")
    else:
        data_dir = os.path.join(os.path.expanduser("~"), ".pynstal")

    os.makedirs(data_dir, exist_ok=True)
    tpl_path = os.path.join(data_dir, "templates.json")
    with open(tpl_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def detect_interpreters(verbose: bool = False) -> list[dict]:
    """
    Scan system for Python installations.
    Returns list of dicts with {'path': str, 'version': str}.
    """
    candidates = set()
    
    if sys.platform == "win32":
        # Windows: Registry, common paths, pyenv-win
        candidates.update(_scan_windows_python())
    else:
        # Unix/Linux/Mac
        candidates.update(_scan_unix_python())
    
    # Add current interpreter
    candidates.add(sys.executable)
    
    # Scan conda environments
    candidates.update(_scan_conda_envs())
    
    # Scan pyenv
    candidates.update(_scan_pyenv())
    
    # Verify each candidate and extract version
    found = []
    for candidate in sorted(candidates):
        if candidate and os.path.isfile(candidate):
            try:
                version = _get_python_version(candidate)
                if version:
                    found.append({
                        'path': str(candidate),
                        'version': version
                    })
                    if verbose:
                        print(f"  Found: {candidate} (Python {version})")
            except Exception as e:
                if verbose:
                    print(f"  Skipped: {candidate} ({e})")
    
    # Remove duplicates based on path
    seen = set()
    unique = []
    for item in found:
        if item['path'] not in seen:
            seen.add(item['path'])
            unique.append(item)
    
    return unique


def _scan_windows_python() -> set:
    """Scan Windows common paths for Python."""
    paths = set()
    
    # Check common installation directories
    common_paths = [
        r"C:\Python310",
        r"C:\Python311",
        r"C:\Python312",
        r"C:\Python313",
    ]
    for base in common_paths:
        exe = os.path.join(base, "python.exe")
        if os.path.isfile(exe):
            paths.add(exe)
    
    # Check AppData\Local\Programs\Python
    appdata = os.getenv("APPDATA")
    if appdata:
        base = os.path.join(appdata, "..", "Local", "Programs", "Python")
        if os.path.isdir(base):
            for d in os.listdir(base):
                exe = os.path.join(base, d, "python.exe")
                if os.path.isfile(exe):
                    paths.add(exe)
    
    # Check pyenv-win
    pyenv_root = os.getenv("PYENV_ROOT", os.path.expanduser("~\\.pyenv"))
    versions_dir = os.path.join(pyenv_root, "versions")
    if os.path.isdir(versions_dir):
        for ver in os.listdir(versions_dir):
            exe = os.path.join(versions_dir, ver, "python.exe")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _scan_unix_python() -> set:
    """Scan Unix/Linux/Mac common paths for Python."""
    paths = set()
    
    common_dirs = [
        "/usr/bin",
        "/usr/local/bin",
        "/opt/python",
        os.path.expanduser("~/.local/bin"),
    ]
    
    for d in common_dirs:
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.startswith("python"):
                    full_path = os.path.join(d, f)
                    if os.path.isfile(full_path) and os.access(full_path, os.X_OK):
                        paths.add(full_path)
    
    return paths


def _scan_conda_envs() -> set:
    """Scan conda environments for Python."""
    paths = set()
    
    conda_roots = [
        os.path.expanduser("~/anaconda3"),
        os.path.expanduser("~/miniconda3"),
        os.path.expanduser("~/mambaforge"),
        os.getenv("CONDA_PREFIX"),
    ]
    
    for conda_root in conda_roots:
        if conda_root and os.path.isdir(conda_root):
            envs_dir = os.path.join(conda_root, "envs")
            if os.path.isdir(envs_dir):
                for env in os.listdir(envs_dir):
                    if sys.platform == "win32":
                        exe = os.path.join(envs_dir, env, "python.exe")
                    else:
                        exe = os.path.join(envs_dir, env, "bin", "python")
                    if os.path.isfile(exe):
                        paths.add(exe)
            
            # Also check root python
            if sys.platform == "win32":
                exe = os.path.join(conda_root, "python.exe")
            else:
                exe = os.path.join(conda_root, "bin", "python")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _scan_pyenv() -> set:
    """Scan pyenv for Python versions."""
    paths = set()
    
    pyenv_root = os.getenv("PYENV_ROOT", os.path.expanduser("~/.pyenv"))
    versions_dir = os.path.join(pyenv_root, "versions")
    
    if os.path.isdir(versions_dir):
        for ver in os.listdir(versions_dir):
            if sys.platform == "win32":
                exe = os.path.join(versions_dir, ver, "python.exe")
            else:
                exe = os.path.join(versions_dir, ver, "bin", "python")
            if os.path.isfile(exe):
                paths.add(exe)
    
    return paths


def _get_python_version(python_exe: str) -> str | None:
    """Get Python version from executable."""
    try:
        result = subprocess.run(
            [python_exe, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            # Output is "Python 3.12.4"
            return result.stdout.strip().replace("Python ", "")
    except Exception:
        pass
    return None


def cmd_create(args):
    interpreter = choose_interpreter(args.interpreter)
    if not interpreter:
        cprint("No interpreter selected; aborting.", Fore.RED)
        return 2
    venv_dir = args.venv_dir
    dry_run = args.dry_run
    success = create_venv(interpreter, venv_dir, dry_run=dry_run) #type: ignore
    sys.exit(0 if success else 1)


def cmd_create_from_template(args):
    template = args.template
    venv_dir = args.venv_dir
    dry_run = args.dry_run
    interpreter = args.interpreter

    data = load_templates()
    templates = data.get("templates", {})
    if template not in templates:
        cprint(f"Template '{template}' not defined. Available: {', '.join(templates.keys())}", Fore.RED)
        return 2

    packages = templates[template]

    # determine interpreter to use (may prompt)
    interpreter = choose_interpreter(interpreter)
    if not interpreter:
        cprint("No interpreter selected; aborting.", Fore.RED)
        return 2

    # create venv
    created = create_venv(interpreter, venv_dir, dry_run=dry_run, offer_activation=False)
    if not created:
        cprint("Failed to create venv; aborting package installation.", Fore.RED)
        return 1

    ok, out, err = install_packages_in_venv(venv_dir, packages, dry_run=dry_run)
    if ok:
        cprint("Packages installed successfully." if not dry_run else out, Fore.GREEN)
        if not dry_run:
            offer_activation_shell(venv_dir)
        return 0
    else:
        cprint(f"Failed installing packages. Error:\n{err}", Fore.RED)
        return 1
def cmd_template_list(args):
    data = load_templates()
    templates = data.get("templates", {})

    if not templates:
        print("No templates defined.")
        return 0
    print("Available templates:")
    for name, packages in templates.items():
        print(f"  {name}:")
        if isinstance(packages, list):
            for pkg in packages:
                if isinstance(pkg, str):
                    print(f"    - {pkg}")
                elif isinstance(pkg, dict):
                    pkgs = pkg.get("packages", [])
                    args_list = pkg.get("args", [])
                    print(f"    - {', '.join(pkgs)} (args: {' '.join(args_list)})")
        elif isinstance(packages, dict):
            pkgs = packages.get("packages", [])
            args_list = packages.get("args", [])
            print(f"    - {', '.join(pkgs)} (args: {' '.join(args_list)})")
    return 0


def cmd_template_add(args):
    name = args.name

    data = load_templates()
    templates = data.get("templates", {})

    if name in templates:
        cprint(f"Template '{name}' already exists.", Fore.YELLOW)
        return 2

    new_entries = []
    # Interactive loop to collect package groups and optional args
    while True:
        pkg_line = input("enter package to add: ").strip()
        if not pkg_line:
            break
        # allow multiple packages space-separated
        pkgs = pkg_line.split()
        args_line = input("special args: ").strip()
        if args_line:
            # store as complex entry
            new_entries.append({"packages": pkgs, "args": args_line.split()})
        else:
            # store each package as a simple string entry
            for p in pkgs:
                new_entries.append(p)

    templates[name] = new_entries
    data["templates"] = templates
    save_templates(data)
    cprint(f'added "{name}" as a new template!', Fore.GREEN)
    # Show template contents
    print(f"{name}: [")
    for e in new_entries:
        if isinstance(e, str):
            print(f'  "{e}",')
        else:
            pkgs = " ".join(e.get("packages", []))
            args_str = " ".join(e.get("args", []))
            print(f'  {pkgs} (args: {args_str}),')
    print("]")
    return 0


def cmd_template_remove(args):
    name = args.name
    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    del templates[name]
    data["templates"] = templates
    save_templates(data)
    cprint(f"Template '{name}' removed.", Fore.GREEN)
    return 0


def cmd_template_show(args):
    name = args.name
    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    packages = templates[name]
    cprint(f"Template '{name}':", Fore.CYAN)
    if isinstance(packages, list):
        for pkg in packages:
            if isinstance(pkg, str):
                print(f"  {pkg}")
            elif isinstance(pkg, dict):
                print(f"  {json.dumps(pkg, indent=4)}")
    return 0


def cmd_template_add_package(args):
    name = args.name
    packages = args.package if isinstance(args.package, list) else [args.package]

    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    entry = templates[name]
    if isinstance(entry, list):
        added = []
        for package in packages:
            if package in entry:
                cprint(f"Package '{package}' already exists in template '{name}'.", Fore.YELLOW)
            else:
                entry.append(package)
                added.append(package)
        templates[name] = entry
    elif isinstance(entry, dict):
        pkgs = entry.get("packages", []) or []
        added = []
        for package in packages:
            if package in pkgs:
                cprint(f"Package '{package}' already exists in template '{name}'.", Fore.YELLOW)
            else:
                pkgs.append(package)
                added.append(package)
        entry["packages"] = pkgs
        templates[name] = entry
    else:
        cprint(f"Unsupported template format for '{name}'.", Fore.RED)
        return 2

    data["templates"] = templates
    save_templates(data)
    if added:
        cprint(f"Added package(s) '{' '.join(added)}' to template '{name}'.", Fore.GREEN)
    return 0
def cmd_template_add_package_complex(args):
    name = args.name
    packages = args.package if isinstance(args.package, list) else [args.package]
    if hasattr(args, 'args_str') and args.args_str:
        pip_args = args.args_str.split() if isinstance(args.args_str, str) else args.args_str
    else:
        pip_args = []

    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    entry = templates[name]
    if isinstance(entry, list):
        # append a dict entry representing these packages + args
        entry.append({"packages": packages, "args": pip_args})
        templates[name] = entry
    elif isinstance(entry, dict):
        # merge into existing dict.packages
        pkgs = entry.get("packages", []) or []
        pkgs.extend([p for p in packages if p not in pkgs])
        entry["packages"] = pkgs
        # merge args if any (append)
        if pip_args:
            existing_args = entry.get("args", []) or []
            entry["args"] = existing_args + pip_args
        templates[name] = entry
    else:
        cprint(f"Unsupported template format for '{name}'.", Fore.RED)
        return 2

    data["templates"] = templates
    save_templates(data)
    cprint(f"Added complex package entry to template '{name}'.", Fore.GREEN)
    return 0


def cmd_template_remove_package(args):
    name = args.name

    data = load_templates()
    templates = data.get("templates", {})

    if name not in templates:
        cprint(f"Template '{name}' not found.", Fore.YELLOW)
        return 2

    entry = templates[name]

    # Interactive removal loop
    while True:
        print("which to remove:")
        if isinstance(entry, list):
            for idx, item in enumerate(entry, 1):
                if isinstance(item, str):
                    print(f"{idx}. {item}")
                elif isinstance(item, dict):
                    pkgs = " ".join(item.get("packages", []))
                    args_str = " ".join(item.get("args", []))
                    print(f"{idx}. {pkgs} (args: {args_str})")
        elif isinstance(entry, dict):
            pkgs = " ".join(entry.get("packages", []))
            args_str = " ".join(entry.get("args", []))
            print(f"1. {pkgs} (args: {args_str})")
        else:
            cprint(f"Unsupported template format for '{name}'.", Fore.RED)
            return 2

        choice = input("> ").strip()
        if not choice:
            break

        try:
            idx = int(choice) - 1
        except Exception:
            cprint("Invalid selection.", Fore.YELLOW)
            continue

        if isinstance(entry, list):
            if 0 <= idx < len(entry):
                removed_item = entry.pop(idx)
                templates[name] = entry
                data["templates"] = templates
                save_templates(data)
                if isinstance(removed_item, str):
                    cprint(f"Removed {removed_item} from \"{name}\"", Fore.GREEN)
                else:
                    pkgs = " ".join(removed_item.get("packages", []))
                    args_str = " ".join(removed_item.get("args", []))
                    cprint(f"Removed {pkgs} (args: {args_str}) from \"{name}\"", Fore.GREEN)
            else:
                cprint("Invalid index.", Fore.YELLOW)
        else:
            # single dict entry
            if idx == 0:
                removed_item = entry
                del templates[name]
                data["templates"] = templates
                save_templates(data)
                pkgs = " ".join(removed_item.get("packages", []))
                args_str = " ".join(removed_item.get("args", []))
                cprint(f"Removed {pkgs} (args: {args_str}) from \"{name}\"", Fore.GREEN)
                break
            else:
                cprint("Invalid index.", Fore.YELLOW)

    return 0


def cmd_remove_venv(args):
    venv_dir = args.venv_dir
    if not os.path.exists(venv_dir):
        cprint(f"Virtual environment directory not found: {venv_dir}", Fore.YELLOW)
        return 2

    cprint(f"About to remove virtual environment: {venv_dir}", Fore.CYAN)
    cprint("This will delete the directory and may update configured interpreters.", Fore.CYAN)
    confirm = input("Type 'yes' to confirm: ").strip().lower()
    if confirm != 'yes':
        print("Aborted.")
        return 1

    try:
        shutil.rmtree(venv_dir)
    except Exception as e:
        cprint(f"Failed to remove venv: {e}", Fore.RED)
        return 1

    # remove any interpreter entries that point into this venv
    try:
        if interpreters_data.interpreters:
            new_list = []
            removed = 0
            for p in interpreters_data.interpreters:
                if os.path.abspath(p).startswith(os.path.abspath(venv_dir)):
                    removed += 1
                else:
                    new_list.append(p)
            interpreters_data.interpreters = new_list

            # Update default_interpreter if it pointed to removed venv
            if interpreters_data.default_interpreter and os.path.abspath(interpreters_data.default_interpreter).startswith(os.path.abspath(venv_dir)):
                interpreters_data.default_interpreter = interpreters_data.interpreters[0] if interpreters_data.interpreters else None
            interpreters_data.save()
            # Clear project-local default if it pointed inside the removed venv
            clear_project_default_if_inside(venv_dir)
            cprint(f"Removed venv and {removed} interpreter entry(ies) referencing it.", Fore.GREEN)
        else:
            cprint("Removed venv.", Fore.GREEN)
    except Exception:
        # ignore save errors but report success of deletion
        cprint("Removed venv (failed to update interpreters).", Fore.YELLOW)

    return 0


def cmd_interpreter_detect(args):
    """Detect Python installations on the system."""
    cprint("Scanning for Python installations...", Fore.CYAN)
    found = detect_interpreters(verbose=False)
    
    if not found:
        cprint("No Python installations found.", Fore.YELLOW)
        return 1
    
    cprint(f"\nFound {len(found)} Python installation(s):\n", Fore.CYAN)
    for idx, item in enumerate(found, 1):
        print(f"  [{idx}] {item['path']}")
        print(f"      Version: {item['version']}")
    
    if args.add_all:
        # Add all without confirmation
        added_count = 0
        for item in found:
            if interpreters_data.interpreters is None:
                interpreters_data.interpreters = []
            if item['path'] not in interpreters_data.interpreters:
                interpreters_data.interpreters.append(item['path'])
                added_count += 1
        interpreters_data.save()
        print(f"\nAdded {added_count} interpreter(s) to .pynstal/interpreters.json")
        return 0
    
    elif args.add:
        # Interactive selection
        print("\nEnter the numbers of interpreters to add (comma-separated, e.g., 1,2,3):")
        print("Or press Enter to skip.")
        choice = input("> ").strip()
        
        if not choice:
            print("Skipped.")
            return 0
        
        try:
            indices = [int(x.strip()) - 1 for x in choice.split(",")]
            if interpreters_data.interpreters is None:
                interpreters_data.interpreters = []
            
            added_count = 0
            for idx in indices:
                if 0 <= idx < len(found):
                    path = found[idx]['path']
                    if path not in interpreters_data.interpreters:
                        interpreters_data.interpreters.append(path)
                        added_count += 1
                        print(f"  Added: {path}")
            
            interpreters_data.save()
            print(f"\nAdded {added_count} interpreter(s) to .pynstal/interpreters.json")
            return 0
        except (ValueError, IndexError) as e:
            print(f"Invalid input: {e}")
            return 1
    
    else:
        # Just list, don't add
        return 0


def cmd_install(args):
    """Install packages from a template into the current or specified interpreter."""
    template = args.template
    dry_run = args.dry_run
    interpreter = args.interpreter

    data = load_templates()
    templates = data.get("templates", {})
    if template not in templates:
        print(f"Template '{template}' not defined. Available: {', '.join(templates.keys())}")
        return 2

    packages = templates[template]

    # Determine interpreter to use
    if not interpreter:
        interpreter = get_project_default_interpreter() or interpreters_data.default_interpreter
        if not interpreter:
            interpreter = sys.executable

    if not interpreter:
        print("No interpreter specified and no default interpreter configured in .pynstal.")
        return 2

    # Install packages into the specified interpreter
    ok, out, err = install_packages(interpreter, packages, dry_run=dry_run)
    if ok:
        print("Packages installed successfully." if not dry_run else out)
        return 0
    else:
        print(f"Failed installing packages. Error:\n{err}")
        return 1


def main(argv=None):
    parser = argparse.ArgumentParser(prog="pynstal")
    sub = parser.add_subparsers(dest="cmd")

    a_add = sub.add_parser("add-interpreter", help="Add interpreter path to data/interpreters.json")
    a_add.add_argument("path", help="Path to python interpreter executable")
    a_add.set_defaults(func=cmd_add_interpreter)

    a_set_default = sub.add_parser("set-default-interpreter", help="Interactively set the default interpreter for the project")
    a_set_default.set_defaults(func=cmd_set_default_interpreter)

    a_detect = sub.add_parser("interpreter", help="Manage interpreters")
    a_detect_sub = a_detect.add_subparsers(dest="interpreter_cmd")
    
    a_detect_detect = a_detect_sub.add_parser("detect", help="Auto-detect Python installations on system")
    a_detect_detect.add_argument("--add", action="store_true", help="Interactively select interpreters to add")
    a_detect_detect.add_argument("--add-all", action="store_true", help="Add all detected interpreters without confirmation")
    a_detect_detect.set_defaults(func=cmd_interpreter_detect)

    a_detect_list = a_detect_sub.add_parser("list", help="List configured interpreters")
    a_detect_list.set_defaults(func=cmd_list)

    a_detect_add = a_detect_sub.add_parser("add", help="Interactively add interpreter paths")
    a_detect_add.set_defaults(func=cmd_interpreter_add)

    a_detect_remove = a_detect_sub.add_parser("remove", help="Interactively remove configured interpreters")
    a_detect_remove.set_defaults(func=cmd_interpreter_remove)

    a_create = sub.add_parser("create-venv", help="Create virtualenv using specified interpreter")
    a_create.add_argument("venv_dir", help="Directory to create venv in")
    a_create.add_argument("--interpreter", help="Interpreter path to use")
    a_create.add_argument("--dry-run", action="store_true", help="Do not actually run venv creation; show command")
    a_create.set_defaults(func=cmd_create)

    a_remove = sub.add_parser("remove-venv", help="Remove a virtualenv directory and update configured interpreters")
    a_remove.add_argument("venv_dir", help="Virtualenv directory to remove")
    a_remove.set_defaults(func=cmd_remove_venv)

    a_tpl = sub.add_parser("create-from-template", help="Create venv and install packages from a named template")
    a_tpl.add_argument("template", help="Template name (see bundled templates.json)")
    a_tpl.add_argument("venv_dir", help="Directory to create venv in")
    a_tpl.add_argument("--interpreter", help="Interpreter path to use (overrides data)")
    a_tpl.add_argument("--dry-run", action="store_true", help="Do not actually run commands; show what would run")
    a_tpl.set_defaults(func=cmd_create_from_template)

    a_install = sub.add_parser("install", help="Install packages from a template (without creating venv)")
    a_install.add_argument("template", help="Template name")
    a_install.add_argument("--interpreter", help="Interpreter path to use (defaults to default_interpreter or current Python)")
    a_install.add_argument("--dry-run", action="store_true", help="Do not actually run commands; show what would run")
    a_install.set_defaults(func=cmd_install)

    # Template management subcommands
    a_tm = sub.add_parser("template", help="Manage templates")
    tm_sub = a_tm.add_subparsers(dest="template_cmd")

    tm_list = tm_sub.add_parser("list", help="List all templates")
    tm_list.set_defaults(func=cmd_template_list)

    tm_add = tm_sub.add_parser("add", help="Add a new template interactively")
    tm_add.add_argument("name", help="Template name")
    tm_add.set_defaults(func=cmd_template_add)

    tm_remove = tm_sub.add_parser("remove", help="Remove a template")
    tm_remove.add_argument("name", help="Template name")
    tm_remove.set_defaults(func=cmd_template_remove)

    tm_add_pkg = tm_sub.add_parser("add-pkg", help="Add one or more packages to an existing template")
    tm_add_pkg.add_argument("name", help="Template name")
    tm_add_pkg.add_argument("package", nargs='+', help="One or more package names to add")
    tm_add_pkg.set_defaults(func=cmd_template_add_package)

    tm_add_pkg_complex = tm_sub.add_parser("add-pkg-complex", help="Add packages with pip args to an existing template")
    tm_add_pkg_complex.add_argument("name", help="Template name")
    tm_add_pkg_complex.add_argument("package", nargs='+', help="One or more package names to add")
    tm_add_pkg_complex.add_argument("--args-str", dest="args_str", help="Pip install args as a string")
    tm_add_pkg_complex.set_defaults(func=cmd_template_add_package_complex)

    tm_remove_pkg = tm_sub.add_parser("remove-pkg", help="Interactively remove packages from an existing template")
    tm_remove_pkg.add_argument("name", help="Template name")
    tm_remove_pkg.set_defaults(func=cmd_template_remove_package)

    tm_show = tm_sub.add_parser("show", help="Show template details")
    tm_show.add_argument("name", help="Template name")
    tm_show.set_defaults(func=cmd_template_show)

    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        parser.print_help()
        return 2
    return args.func(args)


def cli():
    raise SystemExit(main())
