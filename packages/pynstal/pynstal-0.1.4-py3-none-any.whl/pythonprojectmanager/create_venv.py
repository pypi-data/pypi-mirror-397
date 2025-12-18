from .handle_data import (
    interpreters_data,
    set_project_default_interpreter,
)
import os
import subprocess
import sys
import colorama
from colorama import Fore, Style

colorama.init(autoreset=True)

def cprint(msg: str, color: str = Fore.WHITE) -> None:
    print(f"{color}{msg}{Style.RESET_ALL}")

def _create_venv(interpreter_path: str, venv_dir: str, dry_run: bool = False) -> tuple[bool, str, str]:
    abs_interpreter = os.path.abspath(interpreter_path)
    abs_venv = os.path.abspath(venv_dir)
    cmd = [abs_interpreter, "-m", "venv", abs_venv]

    if dry_run:
        stdout = f"DRY RUN: would run: {cmd}"
        return True, stdout, ""

    
    cprint(f"Running command: {' '.join(cmd)}", Fore.CYAN)
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=False,
        universal_newlines=True,
        bufsize=1,  # Line buffered
    )

    out_lines: list[str] = []
    try:
        if process.stdout:
            for line in iter(process.stdout.readline, ''):
                if line is None: # type: ignore
                    break
                line = line.rstrip('\n')
                out_lines.append(line)
                print(line)
                sys.stdout.flush()  # Ensure immediate display
            process.stdout.close()
        returncode = process.wait()
        stdout = "\n".join(out_lines)
        return returncode == 0, stdout, ""
    except Exception as e:
        try:
            process.kill()
        except Exception:
            pass
        return False, "", str(e)


def create_venv(interpreter_path: str, venv_dir: str, dry_run: bool = False, offer_activation: bool = True):
    if interpreters_data.interpreters is None:
        print("Warning: no interpreters configured in .pynstal; proceeding with provided interpreter.")

    success, stdout, stderr = _create_venv(interpreter_path, venv_dir, dry_run=dry_run)
    if success:
        if dry_run:
            print(stdout)
            return True
        cprint(f"Virtual environment created successfully at {venv_dir}.", Fore.GREEN)

        # Configure the newly-created venv as the project's default interpreter
        try:
            if sys.platform.startswith("win"):
                venv_python = os.path.join(venv_dir, "Scripts", "python.exe")
            else:
                venv_python = os.path.join(venv_dir, "bin", "python")

            venv_python = os.path.abspath(venv_python)
            if os.path.exists(venv_python):
                # ensure interpreters list exists and contains venv python
                if interpreters_data.interpreters is None:
                    interpreters_data.interpreters = [venv_python]
                else:
                    if venv_python not in interpreters_data.interpreters:
                        interpreters_data.interpreters.insert(0, venv_python)

                interpreters_data.save()

                # Set project-local default interpreter without touching global interpreters.json default
                try:
                    set_project_default_interpreter(venv_python)
                    cprint(f"Configured project default interpreter for {os.getcwd()}: {venv_python}", Fore.GREEN)
                except Exception as e:
                    cprint(f"Could not update project default interpreter: {e}", Fore.YELLOW)
                # Install pynstal into the newly-created venv.
                try:
                    # Decide whether to install local editable project (if running from a repo)
                    repo_cwd = os.getcwd()
                    use_editable = False
                    if os.path.exists(os.path.join(repo_cwd, "pyproject.toml")) or os.path.exists(os.path.join(repo_cwd, "setup.cfg")):
                        use_editable = True

                    if use_editable:
                        install_cmd = [venv_python, "-m", "pip", "install", "-e", repo_cwd]
                    else:
                        install_cmd = [venv_python, "-m", "pip", "install", "pynstal"]

                    cprint(f"Installing pynstal into venv: {' '.join(install_cmd)}", Fore.CYAN)
                    proc = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True, bufsize=1)
                    if proc.stdout:
                        for line in iter(proc.stdout.readline, ''):
                            if line is None:
                                break
                            print(line.rstrip('\n'))
                            sys.stdout.flush()
                        proc.stdout.close()
                    rc = proc.wait()
                    if rc != 0:
                        cprint("Failed to install pynstal into venv.", Fore.YELLOW)
                    else:
                        cprint("Installed pynstal into venv.", Fore.GREEN)
                except Exception as e:
                    cprint(f"Error installing pynstal into venv: {e}", Fore.YELLOW)

                if offer_activation:
                    offer_activation_shell(venv_dir)
        except Exception:
            pass

        return True
    else:
        cprint(f"Failed to create virtual environment. Error:\n{stderr}", Fore.RED)
        return False


def install_packages_in_venv(venv_dir: str, packages, dry_run: bool = False):
    """Install packages into the venv's Python using pip.

    Each entry in `packages` may be either:
      - a simple string: "numpy"
      - a dict: {"packages": ["torch","torchvision"], "args": ["--index-url", "https://download.pytorch.org/whl/cu130"]}

    Returns (success: bool, stdout: str, stderr: str).
    """
    if sys.platform.startswith("win"):
        py_exe = os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        py_exe = os.path.join(venv_dir, "bin", "python")

    return install_packages(py_exe, packages, dry_run=dry_run)
   
def install_packages(interpreter: str, packages, dry_run: bool = False):
    """Install packages using the specified interpreter's pip.

    Each entry in `packages` may be either:
      - a simple string: "numpy"
      - a dict: {"packages": ["torch","torchvision"], "args": ["--index-url", "https://download.pytorch.org/whl/cu130"]}

    Returns (success: bool, stdout: str, stderr: str).
    """
    abs_interpreter = os.path.abspath(interpreter)

    all_stdout: list[str] = []
    all_stderr: list[str] = []

    # Normalize allowed package specs: list[str|dict], dict, or str
    if isinstance(packages, (str, dict)):
        iterable = [packages]
    else:
        iterable = packages or []

    for entry in iterable:
        if isinstance(entry, str):
            pkg_list = [entry]
            extra_args = []
        elif isinstance(entry, dict): # type: ignore
            pkg_list = entry.get("packages") or entry.get("package") or []
            if isinstance(pkg_list, str):
                pkg_list = [pkg_list]
            extra_args = entry.get("args", []) or []
        else:
            # unsupported type; skip
            continue

        cmd = [abs_interpreter, "-m", "pip", "install"] + pkg_list + extra_args
        if dry_run:
            all_stdout.append(f"DRY RUN: would run: {cmd}")
            continue

        if not os.path.exists(abs_interpreter):
            return False, "", f"Interpreter executable not found: {abs_interpreter}"

        cprint(f"Running command: {' '.join(cmd)}", Fore.CYAN)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=False,
            universal_newlines=True,
            bufsize=1,  # Line buffered
        )

        pkg_out: list[str] = []
        try:
            if process.stdout:
                for line in iter(process.stdout.readline, ''):
                    if line is None: # type: ignore
                        break
                    line = line.rstrip('\n')
                    pkg_out.append(line)
                    print(line)
                    sys.stdout.flush()  # Ensure immediate display
                process.stdout.close()
            rc = process.wait()
            all_stdout.append("\n".join(pkg_out))
            if rc != 0:
                all_stderr.append(f"Command exited with {rc}")
                return False, "\n".join(all_stdout), "\n".join(all_stderr)
        except Exception as e:
            try:
                process.kill()
            except Exception:
                pass
            return False, "\n".join(all_stdout), str(e)

    return True, "\n".join(all_stdout), "\n".join(all_stderr)


def offer_activation_shell(venv_dir: str) -> None:
    """Prompt to open a subshell with the venv activated."""
    try:
        activate_now = input("Activate venv now in a subshell? [y/N]: ").strip().lower()
        if activate_now == 'y':
            if sys.platform.startswith('win'):
                cprint("On Windows: to activate, run: <venv_dir>\\Scripts\\activate.bat in your shell.", Fore.CYAN)
            else:
                shell = os.getenv('SHELL', '/bin/bash')
                newenv = os.environ.copy()
                venv_bin = os.path.join(os.path.abspath(venv_dir), 'bin')
                newenv['VIRTUAL_ENV'] = os.path.abspath(venv_dir)
                newenv['PATH'] = venv_bin + os.pathsep + newenv.get('PATH', '')
                cprint(f"Launching interactive shell ({shell}) with venv activated. Exit to return.", Fore.CYAN)
                subprocess.run([shell, '-i'], env=newenv)
    except Exception:
        # keep failures non-fatal so venv creation flow continues
        pass
