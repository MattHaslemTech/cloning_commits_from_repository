from pydriller import Repository
import os
from _settings import settings as _settings
from classes.ClonedRepo import ClonedRepo
from classes.Pom import PomFile
from helpers.pom_parser import *
from helpers.dependencies import *

if __name__ == "__main__":

    # List to hold all the generated repo objects
    ALL_REPOS = []

    # Get repo from user input
    temp_repo = input("Enter Repository to read (remote or local path): ")
    _settings.set_repo(temp_repo)

    # Confirm commit message to find
    verify_check = "N"
    while verify_check.lower() != "y":
        print(f"\nLooking for commits with the phrase \"{_settings.COMMIT_MSG_STR}\"")
        verify_check = input(f"Is this correct? (Y/N): ")

        if verify_check.lower() == "n":
            temp_commit = input(f"Which phrase should we look for? : ")
            _settings.set_commit(temp_commit)


    # Start going through the commits!
    total_commits = 0
    found_count = 0
    successfully_cloned_count = 0

    try:
        for commit in Repository(_settings.REPO_SRC).traverse_commits():

            total_commits += 1

            # If the commit contains the message we're looking for.
            if _settings.COMMIT_MSG_STR.lower() in commit.msg.lower():
                hash = commit.hash
                c_date = commit.committer_date.strftime('%Y-%d-%m')

                print("\n===================== COMMIT FOUND =====================================")
                print(f"Commit => {commit.msg}")
                print(f"Hash => {hash}")
                print(f"Date => {c_date}")
                # Set output path
                output_folder = f"{c_date} ({hash})"
                clone_path = os.path.join(_settings.PROJECT_PATH, f"{_settings.OUTPUT_DIR}/{output_folder}")

                # Create a ClonedRepo object to hold the information from this commit
                cloned_repo_obj = ClonedRepo(clone_path, commit)

                # Clone the commit
                if cloned_repo_obj.clone_it():

                    # Create the text file
                    if cloned_repo_obj.write_it():

                        # Make sure the object knows that cloning was successful
                        cloned_repo_obj.on_success()


                # Add object if repo was cloned successfully or already exists
                if cloned_repo_obj.successful:
                    ALL_REPOS.append(cloned_repo_obj)
                    successfully_cloned_count += 1

                found_count += 1
                print("========================================================================")
    except Exception as e:
        print(f"\n[ERROR] Cannot read commits from repo: {_settings.REPO_SRC}")
        exit()


    # Start gathering dependencies for all the commits that we cloned
    i = 0
    for repo_obj in ALL_REPOS:
        # if i > 0:
        #     break

        # Reset the dependency versions we found in the previous repo
        _settings.reset_versions()

        if repo_obj.successful:
            cloned_path = repo_obj.clone_path

            print("==========================================")
            print(f"Gathering Depencies for {cloned_path}")

            # Alright... Here's the plan...
            # 1. Get the path for the main pom file for this repo
            # 2. Create a PomFile object using that path.. Init'ing the PomFile will do the following:
            #   a) Parse the file:
            #       i) Save the versions set in the pom.xml
            #       ii) Save info for each dependency (artifact, groupId, version)
            #           ?) Replace the version variable with version number set in that pom.xml or a parent one.
            #   b) Check if the parent ClonedRepo object already has a dependency object with the artifact/version
            #       if not:
            #       i) Create a Dependency object for each
            #          this will:
            #           (1) Find the path to the dependency (either from given code or downloaded from maven [saved in {project_root}/maven_downloads/{groupId}/{artifact}/{version}
            #           (2) Copy the code/jar to {cloned_repo}/dependencies/{artifact}-{version})
            #           (3) Find/Store the poms in each of those dependencies to this dependency
            #   c) Go through each of the poms found by the dependency:
            #       i) Check if the ClonedRepo already has this Pom file (by path to the pom.xml)
            #          If not:
            #           (1) Create a new pom object for it to kick off this whole process again.
            #           (2) Store the pom file in the parent ClonedRepo object

            # Get the main pom (the one in root directory of cloned repo)
            main_pom_path = find_main_pom(cloned_path)
            main_pom = PomFile(main_pom_path, repo_obj)
            repo_obj.set_main_pom(main_pom)
            main_pom.debug_print()

            print(f"main => {repo_obj.main_pom.file_path}")


        print("++++++++++++++ NOT FOUND ++++++++++++++++++++")
        temp = repo_obj.dependencies
        not_found_count = 0
        found_count = 0
        cloned_count = 0
        for t in temp:
            if "aviagames" in t.group_id:
                if not t.found_in_pom_file:
                    t.debug_print()
                    not_found_count += 1
                else:
                    found_count += 1

                if t.cloned:
                    cloned_count += 1

        print(f"NOT FOUND => {not_found_count}")
        print(f"Cloned => {cloned_count}")

        i += 1




    # print("--------------- Results ------------------------")
    # print(f"\nLooked through {total_commits} commits.")
    # print(f"\nFound {found_count} commits with the phrase \"{_settings.COMMIT_MSG_STR}\"")
    # print(f"Successfully cloned {successfully_cloned_count} commits.")


    # Print errors file
    # _settings.write_errors()



