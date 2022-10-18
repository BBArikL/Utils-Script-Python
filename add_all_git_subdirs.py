import os
import re
import subprocess


def get_conf(path: str) -> str:
    conf: str
    with open(f"{path}config", "rt") as file:
        conf = file.read()
    return conf


# Add all git folders in parent git (get repo and construct console query)
def get_git_conf_val(git_conf_file: str, section: str, param: str):
    if section not in git_conf_file:
        return None

    section_string = re.split(f'\\[\\w* "{section}"]', git_conf_file, maxsplit=1)[1]
    lines = section_string.splitlines()
    res = None
    for line in lines:
        match = re.match(f"{param} = ([\\w@:/.\\-_]*)", line.strip())

        if match is not None:
            res = match.group(1)
            break
    return res


def get_git_modules(path: str) -> str:
    MODULES_FILE = ".gitmodules"
    path = f"{path}{MODULES_FILE}"
    if not os.path.exists(path):
        return ""

    text: str
    with open(path, "rt") as f:
        text = f.read()
    return text


if __name__ == "__main__":
    BASE_DIR = "./"
    GIT_DIR = ".git/"
    if not os.path.exists(f"{BASE_DIR}{GIT_DIR}"):
        print("Not a git directory!")
        exit(1)

    git_modules = get_git_modules(BASE_DIR)

    for f in os.listdir(BASE_DIR):
        subdir = f"{BASE_DIR}{f}/"
        if (
            os.path.isdir(subdir)
            and os.path.exists(f"{subdir}{GIT_DIR}")
            and f not in git_modules
        ):
            print(f"Git dir not in git modules file found: {f}")

            git_conf = get_conf(f"{subdir}{GIT_DIR}")
            git_url = get_git_conf_val(git_conf, "origin", "url")

            if git_url is not None:
                final_url = git_url
                command = ["git", "submodule", "add", final_url, f"{f}/"]
                print(" ".join(command))
                pr = subprocess.Popen(command)
                pr.wait()
