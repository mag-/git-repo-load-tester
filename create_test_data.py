#!/usr/bin/env python3
import os
import random
import subprocess
import string
from git import GitCommandError, Repo
from tqdm import tqdm
    
# Constants
NUM_FILES = 1000
LINES_PER_FILE = 1000
NUM_COMMITS = 100000
if os.path.exists('/scratch'):
    REPO_PATH = '/scratch/git/big_repo'
else:
    REPO_PATH = './big_repo'
SRC_DIR = 'src'
FILE_PREFIX = 'file_'
FILE_EXTENSION = '.c'

# Create the src directory if it doesn't exist
os.makedirs(os.path.join(REPO_PATH, SRC_DIR), exist_ok=True)

# Create 1000 files each with 1000 lines
def create_files():
    for i in range(NUM_FILES):
        file_name = f"{FILE_PREFIX}{i}{FILE_EXTENSION}"
        with open(os.path.join(REPO_PATH, SRC_DIR, file_name), 'w') as file:
            for _ in range(LINES_PER_FILE):
                # Creating a realistic line of code, roughly 50-100 characters
                line = ''.join(random.choices(string.ascii_letters + string.digits + " ", k=random.randint(50, 100)))
                file.write(line + "\n")

# Randomly modify multiple lines in a file
def modify_file(file_path):
    with open(file_path, 'r+') as file:
        lines = file.readlines()
        num_lines_to_modify = random.randint(1, 10)  # Change up to 10 lines
        lines_to_modify = random.sample(range(len(lines)), num_lines_to_modify)
        
        for line_index in lines_to_modify:
            lines[line_index] = ''.join(random.choices(string.ascii_letters + string.digits + " ", k=random.randint(50, 100))) + "\n"

        file.seek(0)
        file.writelines(lines)
# Make a commit in the repository
def make_commit(repo_path, message):
    subprocess.run(['git', 'add', '.'], cwd=repo_path)
    subprocess.run(['git', 'commit', '-m', message], cwd=repo_path)


def main():
    os.chdir(REPO_PATH)

    # Step 1: Create files
    create_files()
    print("Files created.")
    # Initialize the git repository
    subprocess.run(['git', 'init','--initial-branch','main'], cwd=REPO_PATH)
    repo = Repo(REPO_PATH)
    repo.index.add([SRC_DIR])
    repo.index.commit("Initial commit")
    assert not repo.bare
    print("Git repository initialized.")

    # Step 2: Make commits
    for i in tqdm(range(NUM_COMMITS), desc="Making commits"):
        file_to_modify = f"{FILE_PREFIX}{random.randint(0, NUM_FILES - 1)}{FILE_EXTENSION}"
        modify_file(os.path.join(REPO_PATH, SRC_DIR, file_to_modify))        
        repo.index.add([os.path.join(SRC_DIR, file_to_modify)])

        commit_types = ['Add', 'Fix', 'Refactor', 'Update', 'Remove']
        commit_scope = ['feature X', 'bug Y', 'module Z', 'documentation', 'tests']
        commit_message = f"{random.choice(commit_types)} {random.choice(commit_scope)}"
        repo.index.commit(commit_message)
        # Create feature and hotfix branches at random
        if (i + 1) % 100 == 0:
            branch_type = random.choice(['feature', 'hotfix'])
            while True:
                new_branch_name = f"{branch_type}_{random.randint(1, 1000)}"
                if new_branch_name not in [head.name for head in repo.heads]:
                    break
            repo.git.checkout('HEAD', b=new_branch_name)
        if (i + 1) % 500 == 0:
            repo.index.commit(commit_message)
            repo.git.checkout('main')
            feature_branches = [head for head in repo.heads if head.name.startswith('feature_')]
            if feature_branches:
                branch_to_merge = random.choice(feature_branches)
                try:
                    repo.git.merge(branch_to_merge.name)
                except GitCommandError: # merge error
                    repo.git.add('--all')
                    repo.git.commit('-m', 'Merge resolved')

        # Tagging certain commits as release points
        if (i + 1) % 1000 == 0:
            tag_name = f"v{(i + 1) // 1000}"
            while tag_name in repo.tags:
                tag_name = f"v{(i + 1) // 1000}.{random.randint(1, 999)}"
            repo.create_tag(tag_name)
        # print(f"Commit {i + 1} made.")
        # Occasionally delete or rename files
if __name__ == "__main__":
    main()
