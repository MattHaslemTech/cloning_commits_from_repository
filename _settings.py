import os

# global REPO_SRC
# global ERROR_MSGS
# global PROJECT_PATH
# global OUTPUT_DIR
# global COMMIT_MSG_STR
class Settings:
    REPO_SRC = ""
    DEPENDENCY_SRC = "" # The directory to look for dependency code. It assumes it's just one directory above the repo source

    ERROR_MSGS = []
    WARNING_MSGS = []


    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))

    OUTPUT_DIR = "output_repos"
    DEPENDENCY_CLONE_DIR = "dependencies"

    COMMIT_MSG_STR = "Merge branch 'staging' into 'master'"
    # COMMIT_MSG_STR = "create"

    FOUND_DEPENDENCIES = {} # Dict to hold path of found dependency code just so we don't have to search for it again
                            #   Key: artifact
                            #   Val: path to dep code

    FOUND_VERSIONS = {} # Key: artifact. Val: version


    def set_repo(self, repo):
        self.REPO_SRC = repo
        self.DEPENDENCY_SRC = os.path.dirname(repo)

    def set_commit(self, msg):
        self.COMMIT_MSG_STR = msg

    def add_found_dependency(self, artifact, path):
        self.FOUND_DEPENDENCIES[artifact] = path

    def get_dependency_path(self, artifact):
        if artifact in self.FOUND_DEPENDENCIES:
            return self.FOUND_DEPENDENCIES[artifact]
        else:
            return ""

    # Add versions we found set in the Poms
    def add_version(self, artifact, version):
        if not artifact in self.FOUND_VERSIONS:
            self.FOUND_VERSIONS[artifact] = version

    def reset_versions(self):
        self.FOUND_VERSIONS = {}

    def add_error(self, msg):
        self.ERROR_MSGS.append(msg)

    def add_warning(self, msg):
        self.WARNING_MSGS.append(msg)

    def write_errors(self):

        print(f"\nThere were {len(self.ERROR_MSGS)} errors.")
        print(f"There were {len(self.WARNING_MSGS)} warnings.\n")

        if len(self.ERROR_MSGS) > 0:
            error_path = "debug/error.txt"
            full_path = os.path.join(self.PROJECT_PATH, error_path)
            f = open(error_path, "w")
            error_str = ""
            for error_msg in self.ERROR_MSGS:
                error_str += "\n============================================="
                error_str += f"\n{error_msg}"
            f.write(error_str)

            f.close()

            print(f"Error messages written to {full_path}")

        if len(self.WARNING_MSGS) > 0:
            warning_path = "debug/warning.txt"
            full_path = os.path.join(self.PROJECT_PATH, warning_path)
            f = open(warning_path, "w")
            warning_str = ""
            for warning_msg in self.WARNING_MSGS:
                warning_str += "\n============================================="
                warning_str += f"\n{warning_msg}"
            f.write(warning_str)

            f.close()

            print(f"Warning messages written to {full_path}")

    def debug_print(self):
        print(f"Project => {self.PROJECT_PATH}")
        print(f"REPO_SRC => {self.REPO_SRC}")
        print(f"Dependency source => {self.DEPENDENCY_SRC}")

        print(f"COMMIT_MSG_STR => {self.COMMIT_MSG_STR}")


settings = Settings()

