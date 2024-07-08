import xml.etree.ElementTree as ET
from _settings import settings as _s
from classes.Version import Version
from helpers.pom_parser import *
from classes.Dependency import Dependency


class PomFile:
    def __init__(self, pom_path, repo_obj, pomfile_called_from = None):
        self.parent_repo = repo_obj # The ClonedRepo object that this pom file belongs to.
        self.pomfile_called_from = pomfile_called_from # The PomFile that had listed this one as a dependency
        self.file_path = pom_path # The absolute path for this Pom file
        self.dependencies = [] # List of dependency objects defined in this pom file


        print(f"[Pom.py] Parsing: {pom_path}")
        try:
            tree = ET.parse(pom_path)
        except Exception as e:
            error_msg = f"[ERROR] Cannot parse pom file. {e}"
            print(error_msg)
            _s.add_error(error_msg)
        self.root = tree.getroot()

        nm = self.root.tag.split('}')[0].strip('{')
        self.namespace = {'m': nm}

        # Get the info that's defined in this pom
        self.project_version = self.fetch_project_version()
        self.versions = self.fetch_all_versions()
        self.dependencies = self.fetch_dependencies()

        self.sub_poms = self.fetch_sub_poms()

    def fetch_project_version(self):
        project_version_element = self.root.find('m:version', self.namespace)
        if project_version_element is not None:
            project_version = project_version_element.text
            return project_version
        else:
            return ""

    def fetch_all_versions(self):
        all_versions = []
        properties_element = self.root.find('m:properties', self.namespace)

        if properties_element is not None:
            for property in properties_element:
                prop_tag_name = property.tag.split('}')[1]
                prop_value = property.text
                version_obj = Version(prop_tag_name, prop_value)
                all_versions.append(version_obj)

        return all_versions


    def fetch_dependencies(self):
        # Get all the dependency info. Put in list
        dependencies = []
        # dep_elements = root.findall('m:dependencyManagement/m:dependencies/m:dependency', namespace)
        # dep_elements = self.root.findall('.//m:dependencies/m:dependency', self.namespace)
        dep_elements = self.root.findall('.//m:dependency', self.namespace)
        for dependency in dep_elements:
            group_id = dependency.find('m:groupId', self.namespace).text
            artifact_id = dependency.find('m:artifactId', self.namespace).text

            print(f"\n[Pom.py] Gathering dependency info for: {artifact_id}")

            # Get the dependency version if it has one
            version_element = dependency.find('m:version', self.namespace)
            
            version_number = ""

            if version_element is not None:
                version = version_element.text
                if "${" in version:
                    # version_name = version.split('${')[1].split('}')[0].split(".version")[0]
                    version_name = version.split('${')[1].split('}')[0]
                    version_number = self.get_version_number_by_name(version_name)
                else:
                    version_number = version
            else:
                # If there's not a version element, it's probably set in a parent somewhere
                version_number = self.get_version_number_by_artifact(artifact_id)

            if version_number == "":
                # If we still don't have version number, do one last check from previously set dependencies
                temp_dep = self.parent_repo.get_dependency_by_artifact(artifact_id)
                if temp_dep:
                    version_number = temp_dep.version
                else:
                    print(f"[Pom.py] Version Not found..")

            # Remove the SNAPSHOT part
            if "-SNAPSHOT" in version_number:
                version_number = version_number.replace("-SNAPSHOT", "")


            # Check if we already have a Dependency object for this artifact
            dependency_obj = self.parent_repo.get_dependency(artifact_id, version_number)

            # Create Dependency object
            if dependency_obj is None:
                dependency_obj = Dependency(group_id, artifact_id, version_number, self.parent_repo)
                self.parent_repo.add_dependency(dependency_obj)
                dependency_obj.set_file_path(self.file_path)
            else:
                print(f"[Pom.py] We already checked this dependency: {dependency_obj.artifact}")

            dependencies.append(dependency_obj)


        return dependencies


    def get_version_number_by_name(self, name):
        version_number = ""
        # If it's the project version just get that
        if name == "project.version":
            return self.project_version

        for v in self.versions:
            if v.name == name:
                version_number = v.version_number
                return version_number

        # If one wasn't found, recursively check parent poms for version
        if self.pomfile_called_from:
            version_number = self.pomfile_called_from.get_version_number_by_name(name)

        return version_number

    # This will recursively go up the tree of parents to look for version number
    def get_version_number_by_artifact(self, artifact_id):
        version_number = ""

        for dep in self.dependencies:
            if dep.artifact == artifact_id:
                version_number = dep.version
                return version_number

        # If one wasn't found, recursively check parent poms for version
        if self.pomfile_called_from:
            version_number = self.pomfile_called_from.get_version_number_by_artifact(artifact_id)

        return version_number

    # Get all the poms in the dependency code
    def fetch_sub_poms(self):
        pom_objs = []
        for dep in self.dependencies:
            for pom_path in dep.pom_paths:
                pom_obj = self.parent_repo.get_pom(pom_path)

                if not pom_obj:
                    pom_obj = self.parent_repo.create_pom(pom_path, self)

                pom_objs.append(pom_obj)
        return pom_objs

    def debug_print(self):
        print("--------------- POM Summary ------------------")
        print(f"Pom path => {self.file_path}")
        print(f"Versions:")
        print(f"\tProject Version: {self.project_version}")
        for v in self.versions:
            v.debug_print()

        print(f"Dependencies:")
        for d in self.dependencies:
            d.debug_print()

        print(f"Sub Poms:")
        for pom in self.sub_poms:
            print(f"\t| {pom.file_path}")



