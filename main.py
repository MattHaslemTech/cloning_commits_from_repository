from pydriller import Repository
import os
from git import Repo, Git

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

OUTPUT_DIR = "output_repos"

COMMIT_MSG_STR = "Merge branch 'staging' into 'master'"

ERROR_MSGS = []

def clone_it(hash, clone_path):
    full_path = os.path.join(PROJECT_PATH, clone_path)

    if not os.path.exists(clone_path):
        # Clone the repo
        print(f"Cloning to: {full_path}")
        try:
            repo = Repo.clone_from(REPO_SRC, clone_path)
        except Exception as e:
            error_msg = f"[ERROR] There was an issue cloning the repo. {e}"
            print(error_msg)
            ERROR_MSGS.append(error_msg)
            return False

        # Won't output on windows because file paths are too long..
        if os.name == 'nt':
            repo.git.config('core.longpaths', 'true')

        # Checkout the repo
        print(f"Checking out commit: {hash}")
        try:
            repo.git.checkout(hash)
            return True
        except Exception as e:
            error_msg = f"[ERROR] There was an issue with checking out the commit. {e}"
            print(error_msg)
            ERROR_MSGS.append(error_msg)
            return False

    else:
        error_msg = f"[ERROR] Path already exists: {full_path}"
        print(error_msg)
        ERROR_MSGS.append(error_msg)

def write_it(commit, clone_path):
    txt_file_path = os.path.join(clone_path, "_COMMIT_INFO.txt")

    full_path = os.path.join(PROJECT_PATH, txt_file_path)

    print(f"Writing to file: {full_path}")
    try:
        f = open(txt_file_path, "w")

        output_str = f'Commit: {commit.hash} \n'
        output_str += f'Author: {commit.author.name} <{commit.author.email}> \n'
        output_str += f'Author Date: {commit.author_date} \n'
        output_str += f'Committer: {commit.committer.name} <{commit.committer.email}> \n'
        output_str += f'Committer Date: {commit.committer_date} \n'
        output_str += f'Message: {commit.msg} \n'
        output_str += f'Parents: {commit.parents} \n'
        output_str += f'Merge: {commit.merge} \n'
        output_str += f'Insertions: {commit.insertions} \n'
        output_str += f'Deletions: {commit.deletions} \n'
        output_str += f'Files Changed: {len(commit.modified_files)}'

        f.write(output_str)

        f.close()

        return True

    except Exception as e:
        error_msg = f"[ERROR] There was an issue writing the commit summary file. {e}"
        print(error_msg)
        ERROR_MSGS.append(error_msg)
        return False


# Get user inputs
REPO_SRC = input("Enter Repository to read (remote or local path): ")
verify_check = "N"
while verify_check.lower() != "y":
    print(f"\nLooking for commits with the phrase \"{COMMIT_MSG_STR}\"")
    verify_check = input(f"Is this correct? (Y/N): ")

    if verify_check.lower() == "n":
        COMMIT_MSG_STR = input(f"Which phrase should we look for? : ")


# Start going through the commits!
total_commits = 0
found_count = 0
successfully_cloned_count = 0

try:
    for commit in Repository(REPO_SRC).traverse_commits():

        total_commits += 1

        # If the commit contains the message we're looking for.
        if COMMIT_MSG_STR.lower() in commit.msg.lower():
            hash = commit.hash
            c_date = commit.committer_date.strftime('%Y-%d-%m')

            print("\n===================== COMMIT FOUND =====================================")
            print(f"Commit => {commit.msg}")
            print(f"Hash => {hash}")
            print(f"Date => {c_date}")
            # Set output path
            output_folder = f"{c_date} ({hash})"
            clone_path = os.path.join(PROJECT_PATH, f"{OUTPUT_DIR}/{output_folder}")

            # Clone the commit
            if clone_it(hash, clone_path):
                # Create the text file
                if write_it(commit, clone_path):
                    successfully_cloned_count += 1

            found_count += 1
            print("========================================================================")

except Exception as e:
    print(f"\n[ERROR] Cannot read commits from repo: {REPO_SRC}")
    exit()


print("--------------- Results ------------------------")
print(f"\nLooked through {total_commits} commits.")
print(f"\nFound {found_count} commits with the phrase \"{COMMIT_MSG_STR}\"")
print(f"Successfully cloned {successfully_cloned_count} commits.")

if len(ERROR_MSGS) > 0:
    error_path = "debug/error.txt"
    full_path = os.path.join(PROJECT_PATH, error_path)
    f = open(error_path, "w")
    error_str = ""
    for error_msg in ERROR_MSGS:
        error_str += "\n============================================="
        error_str += f"\n{error_msg}"
    f.write(error_str)

    f.close()

    print(f"\nThere were {len(ERROR_MSGS)} errors.")
    print(f"Error messages written to {full_path}")



