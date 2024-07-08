from git import Repo, Git
import os
import shutil
from _settings import settings as _s
from helpers.pom_parser import *
from helpers.dependencies import *
from classes.Pom import PomFile

class ClonedRepo:
    def __init__(self,repo_path, commitobj):
        self.clone_path = repo_path
        self.commit = commitobj
        self.successful = False
        self.dependencies = []
        self.created_pom_objects = []
        self.processing_poms = []


        # The list of every pom file in project directory and dependency directories
        self.all_poms = self.collect_all_pom_paths()


    def add_pom(self, pom_obj):
        self.created_pom_objects.append(pom_obj)

    # Create the PomFile object if it's not already created or processing
    def create_pom(self, pom_path, pomfile_called_from = None):
        if pom_path not in self.processing_poms:
            self.processing_poms.append(pom_path)
            print(f"\n[ClonedRepo.py] Creating PomFile object from: {pom_path}")
            pom_obj = PomFile(pom_path, self)
            self.add_pom(pom_obj)
            print(f"\n[ClonedRepo.py] FINISHED CREATING POMFILE FOR: {pom_path}")

            return pom_obj
        else:
            print(f"\n[ClonedRepo.py] PomFile object is already being created for: {pom_path}")
            pom_obj = self.get_pom(pom_path)
            if pom_obj:
                print(f"[ClonedRepo.py] PomFile object was already created!")
                return pom_obj



    def get_pom(self, pom_path):
        for pom in self.created_pom_objects:
            if pom.file_path == pom_path:
                return pom
        return False

    def set_main_pom(self, pom_obj):
        self.main_pom = pom_obj
        self.add_pom(pom_obj)

    # Returns all poms that aren't parsed yet (we're going to be adding more as files are added)
    def get_unparsed_poms(self):
        # return self.created_pom_objects
        return [pom for pom in self.created_pom_objects if not self.created_pom_objects[pom]]




    # Get all the dependency objects that haven't been cloned yet
    def get_uncloned_dependencies(self):
        return [dep_obj for dep_obj in self.dependencies if not dep_obj.cloned]


    def add_dependency(self, dep_obj):
        self.dependencies.append(dep_obj)

    # Get a dependency by artifact and version (if artifact exists but not version, update version)
    def get_dependency(self, artifact, version):
        for dep in self.dependencies:
            if dep.artifact == artifact and dep.version == version:
                return dep
        return None

    def get_dependency_by_artifact(self, artifact):
        for dep in self.dependencies:
            if dep.artifact == artifact:
                return dep
        return False



    # Get paths for every single pom file
    def collect_all_pom_paths(self):
        all_poms = []
        # Get all the poms in the cloned repo
        for pom_path in glob(f"{self.clone_path}/**/pom.xml", recursive=True):
            all_poms.append(pom_path)
            # print(f"REPO => {_s.REPO_SRC}")

        # Get all the poms in the dependency folders (skip the repo folder (server_game))
        for pom_path in glob(f"{_s.DEPENDENCY_SRC}/**/pom.xml", recursive=True):

            if _s.REPO_SRC in pom_path:
                continue
            all_poms.append(pom_path)

        return all_poms


    # Create a clone of this commit
    def clone_it(self):
        full_path = os.path.join(_s.PROJECT_PATH, self.clone_path)

        hash = self.commit.hash

        if not os.path.exists(self.clone_path):
            # Clone the repo
            print(f"Cloning to: {full_path}")
            try:
                repo = Repo.clone_from(_s.REPO_SRC, self.clone_path)
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
                # self.clone_path
                return True
            except Exception as e:
                error_msg = f"[ERROR] There was an issue with checking out the commit. {e}"
                print(error_msg)
                _s.add_error(error_msg)
                return False

        else:
            error_msg = f"[WARNING] Path already exists: {full_path}"
            print(error_msg)
            self.on_success()
            _s.add_warning(error_msg)

    # Write the Commt Info txt file
    def write_it(self):

        txt_file_path = os.path.join(self.clone_path, "_COMMIT_INFO.txt")

        full_path = os.path.join(_s.PROJECT_PATH, txt_file_path)

        commit = self.commit

        print(f"Writing to file: {full_path}")
        try:
            f = open(txt_file_path, "w", encoding="utf-8")

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

    # Set successful after cloning is done
    def on_success(self):
        self.successful = True