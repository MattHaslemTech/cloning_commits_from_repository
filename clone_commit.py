from git import Repo, Git
import os
from _settings import settings as _s

def clone_it(hash, clone_path):
    full_path = os.path.join(_s.PROJECT_PATH, clone_path)

    if not os.path.exists(clone_path):
        # Clone the repo
        print(f"Cloning to: {full_path}")
        try:
            repo = Repo.clone_from(_s.REPO_SRC, clone_path)
        except Exception as e:
            error_msg = f"[ERROR] There was an issue cloning the repo. {e}"
            print(error_msg)
            _s.add_error(error_msg)
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
            _s.add_error(error_msg)
            return False

    else:
        error_msg = f"[ERROR] Path already exists: {full_path}"
        print(error_msg)
        _s.add_error(error_msg)

def write_it(commit, clone_path):

    txt_file_path = os.path.join(clone_path, "_COMMIT_INFO.txt")

    full_path = os.path.join(_s.PROJECT_PATH, txt_file_path)

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
        _s.add_error(error_msg)
        return False
