import os
import shutil
import xml.etree.ElementTree as ET
from _settings import settings as _s
from glob import glob
import requests
# from helpers.pom_parser import find_all_poms
from helpers.pom_finder import find_pom_path_with_artifact_id
# from classes.Pom import PomFile

class Dependency:
    def __init__(self, group_id, artifact, version_number, parent_repo):
        self.group_id = group_id
        self.artifact = artifact
        self.version = version_number
        self.parent_repo = parent_repo
        self.maven_url = ""
        self.file_path = "" # The pom file this dependency came from

        self.checked = False
        self.cloned = False

        # self.path_to_clone = ""
        # self.pom_paths = []
        self.found_in_pom_file = False

        self.path_to_clone = self.find_dependency_code()

        # Some dependencies have parent artifacts. We need to create a PomFile for those
        #   Note:   we're doing this here and not in Pom.py so we can try to get the version from the parent before this
        #           dependency is cloned
        self.parent_pom = self.fetch_parent_pom()

        self.pom_paths = self.find_all_poms()


        if "aviagames" in self.group_id:
            self.clone_dependency_code()

    def set_version(self, version):
        self.version = version

    def set_path_to_clone(self, path):
        self.path_to_clone = path

    def set_checked(self):
        self.checked = True

    def set_cloned(self):
        self.cloned = True

    def find_dependency_code(self):
        artifact_name = self.artifact
        print(f"[Dependency.py] Finding Code for Dependency: {artifact_name}")

        # See if we already found this dependency
        # dep_path = _s.get_dependency_path(artifact_name)
        dep_path = False

        if "aviagames" in self.group_id:
            # Try to find a POM that defines this artifact.
            for pom_path in self.parent_repo.all_poms:
                tree = ET.parse(pom_path)
                root = tree.getroot()
                nm = root.tag.split('}')[0].strip('{')
                namespace = {'m': nm}
                artifact_element = root.find('m:artifactId', namespace)

                if artifact_element is not None:
                    if artifact_element.text == artifact_name:
                        dep_path = os.path.dirname(os.path.realpath(pom_path))
                        print(f"[Dependency.py] FOUND DEPENDENCY DEFINED IN A POM => {pom_path}")
                        self.found_in_pom_file = True
                        return dep_path


            # Check folders for code
            # if not dep_path:
            # Commons artifacts have 'commons-' before the folder name
            if ".commons" in self.group_id and "commons-" not in artifact_name:
                folder_to_search_for = "commons-" + artifact_name
            else:
                folder_to_search_for = artifact_name

            print(f"[Dependency.py] Looking through existing files...")
            for folder_path in glob(f"{_s.DEPENDENCY_SRC}/**/{folder_to_search_for}", recursive=True):
                dep_path = folder_path


                # if dep_path:
                #     _s.add_found_dependency(artifact_name, dep_path)
                # else:
                #     print("Not Found.")

        # Attempt to get from Maven
        if not dep_path:
            print(f"[Dependency.py] Looking in Maven Repo...")
            group_id = self.group_id
            version = self.version
            dep_path = self.download_maven_artifact(group_id, artifact_name, version)

        if dep_path:
            self.path_to_clone = dep_path
            return dep_path
        else:
            print(f"[Dependency.py] Dependency not found: {artifact_name}")
            return ""

    def download_file(self, url, dest_folder):
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)

            file_name = os.path.join(dest_folder, url.split('/')[-1])
            with open(file_name, 'wb') as f:
                shutil.copyfileobj(response.raw, f)
            return True
        else:
            return False

    def download_maven_artifact(self, group_id, artifact_id, version, repo_url='https://repo1.maven.org/maven2'):
        group_path = group_id.replace('.', '/')

        artifact_url = f'{repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.jar'

        self.maven_url = artifact_url

        dest_folder = os.path.join(_s.PROJECT_PATH, 'maven_downloads', group_id, artifact_id, version)

        if self.download_file(artifact_url, dest_folder):
            return dest_folder
        else:
            return ""

    # Copy all the dependency code into the cloned folder
    def clone_dependency_code(self):
        dep_path = self.path_to_clone

        self.set_checked()

        if dep_path != "":
            src = dep_path
            dest = os.path.join(self.parent_repo.clone_path, _s.DEPENDENCY_CLONE_DIR, self.artifact + "-" + self.version)
            if not os.path.isdir(dest):
                print(f"[Dependency.py] Cloning Dependency from: {src}")

                destination = shutil.copytree(src, dest)
                if destination:
                    self.set_cloned()
                    self.cloned = True
                    print(f"[Dependency.py] Dependency cloned to: {destination}")
            else:
                print(f"[Dependency.py] Dependency already cloned: {self.artifact}")
                # self.set_cloned()

    # If this dependency has a parent, create a PomFile object for it
    def fetch_parent_pom(self):
        if self.path_to_clone == "" or "aviagames" not in self.group_id:
            return

        # if self.version != "":
        #     return

        artifact_pom_path = os.path.join(self.path_to_clone, "pom.xml")

        tree = ET.parse(artifact_pom_path)

        artifact_root = tree.getroot()

        artifact_nm = artifact_root.tag.split('}')[0].strip('{')
        artifact_namespace = {'m': artifact_nm}


        parent_element = artifact_root.find('m:parent', artifact_namespace)
        if parent_element is not None:
            artifact_element = parent_element.find('m:artifactId', artifact_namespace)

            if artifact_element is not None:
                artifact_name = artifact_element.text
                pom_path = find_pom_path_with_artifact_id(artifact_name, self.parent_repo)

                print(f"[Dependency.py] Generating PomFile for Parent Pom of '{self.artifact}' from: {pom_path}")
                if pom_path != "":

                    # Check if we already have a pom for this. If not, create one
                    pom_obj = self.parent_repo.get_pom(pom_path)
                    if not pom_obj:
                        pom_obj = self.parent_repo.create_pom(pom_path, self.parent_repo)

                    # If version wasn't set in this Dependency, see if we can get it from the parent pom
                    if self.version == "":
                        print(f"[Dependency.py] Looking for version for {self.artifact}")
                        version_number = ""

                        if pom_obj:
                            version_number = pom_obj.get_version_number_by_artifact(self.artifact)
                        # PomFile object might not be done being recreated yet.
                        #   Note:   This is a problem because this Dependency is being created as a result of
                        #           creating a PomFile object for its parent (the parent can't finish being created until
                        #           all of it dependencies and sub-dependencies are created (including this one))
                        #
                        #           So see if this Dependency was already created at some point and grab the version from that
                        #           We need the version so we don't create duplicates
                        else:
                            temp_dep = self.parent_repo.get_dependency_by_artifact(self.artifact)
                            if temp_dep:
                                version_number = temp_dep.version

                        self.version = version_number



        return pom_obj

    def find_all_poms(self):
        pom_list = []
        if self.path_to_clone != "":
            print(f"[Dependency.py] Looking for poms in: {self.path_to_clone}")

            for pom_path in glob(f"{self.path_to_clone}/**/pom.xml", recursive=True):
                # print(f"[Dependency.py] Pom paths => {pom_path}")

                pom_list.append(pom_path)

        return pom_list

    def set_file_path(self, file_path):
        self.file_path = file_path

    def debug_print(self):
        print(f"\t---------------------------------")
        print(f"\tArtifact: {self.artifact}")
        print(f"\tgroup_id: {self.group_id}")
        print(f"\tversion: {self.version}")
        print(f"\tpath to clone: {self.path_to_clone}")
        print(f"\tMaven URL: {self.maven_url}")
        print(f"\tPom File: {self.file_path}")
        print(f"\tFound in Pom: {self.found_in_pom_file}")
        print(f"\tCloned: {self.cloned}")