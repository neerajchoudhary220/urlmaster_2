import subprocess
from pathlib import Path
from fastapi import HTTPException

def get_git_branches(directory_path: str):
    git_dir = Path(directory_path) / ".git"
    if not git_dir.exists():
        return []  # Not a git repo

    try:
        result = subprocess.run(
            ["git", "branch"],
            cwd=directory_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            return []  # Git error (maybe not a repo)

        branches = []
        for line in result.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            branches.append({
                "name": line.replace("* ", "").strip(),
                "active": line.startswith("*")
            })
        return branches

    except Exception as e:
        return []
 
def get_current_branch(directory_path: str ):
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=directory_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode == 0:
       return result.stdout.strip()
    else:
        return   
def switch_branch(path:str, branch:str):
    path = Path(path) 
    if not path.exists():
        raise HTTPException(400,detail='Invalid path')
        

# Run 'git checkout master'
    result = subprocess.run(
        ["git", "checkout", branch],
        cwd=path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result)
    if result.returncode ==1:
        raise HTTPException(400,detail=result.stderr)
    
    return result.stdout

    # print("Return code:", result.returncode)
    # print("Output:", result.stdout)
    # print("Error:", result.stderr)