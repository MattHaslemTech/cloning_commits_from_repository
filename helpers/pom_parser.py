import xml.etree.ElementTree as ET
import os
from _settings import settings as _s
from glob import glob
from classes.Dependency import Dependency

def find_main_pom(path):
    for root, dirs, files in os.walk(path):
        if "pom.xml" in files:
            return os.path.join(root, "pom.xml")
    return None

def find_all_poms(cloned_path):
    pom_list = []
    for pom_path in glob(f"{cloned_path}/**/pom.xml", recursive=True):
        # print(f"Pom paths => {pom_path}")
        pom_list.append(pom_path)

    return pom_list

# Return a list of dependencies and their versions for a project
def parse_pom(pom_file):

    # Find the pom file
    # pom_file = find_main_pom(repo_path)

    print(f"Parsing: {pom_file}")
    try:
        tree = ET.parse(pom_file)
    except Exception as e:
        error_msg = f"[ERROR] Cannot parse pom file. {e}"
        print(error_msg)
        _s.add_error(error_msg)
        return {}

    root = tree.getroot()
    # print("PARSING! nice =>")
    # print(root.attrib)


    nm = root.tag.split('}')[0].strip('{')
    # print(f"nm => {nm}")
    namespace = {'m': nm}

    # versions_dict = {} # Dict to hold all the versions

    # Get the project version
    project_version_element = root.find('m:version', namespace)
    if project_version_element is not None:
        project_version = project_version_element.text
        _s.add_version("project", project_version)

    # Get all the versions from properties (if it has some)
    properties_element = root.find('m:properties', namespace)
    if properties_element is not None:

        for property in properties_element:
            if "project" in property.tag:
                prop_tag_name = property.tag.split('}')[1].split('.')[0]
            else:
                prop_tag_name = property.tag.split('}')[1].split('.version')[0]

            prop_value = property.text
            _s.add_version(prop_tag_name, prop_value)
            # versions_dict[prop_tag_name] = prop_value

    # Get all the dependency info. Put in list
    dependencies = []
    # dep_elements = root.findall('m:dependencyManagement/m:dependencies/m:dependency', namespace)
    dep_elements = root.findall('.//m:dependencies/m:dependency', namespace)
    for dependency in dep_elements:
        group_id = dependency.find('m:groupId', namespace).text
        artifact_id = dependency.find('m:artifactId', namespace).text

        print(f"Gathering dependency info for: {artifact_id}")

        dependency_obj = Dependency(group_id, artifact_id)


        # Get the dependency version if it has one
        version_element = dependency.find('m:version', namespace)
        if version_element is not None:
            version = version_element.text
            if "${" in version:
                version_tag = version.split('${')[1].split('}')[0].split(".version")[0]
                if version_tag in _s.FOUND_VERSIONS:
                    version = _s.FOUND_VERSIONS[version_tag]
            dependency_obj.set_version(version)
        else:
            print(f"Version Not found..")

        dependencies.append(dependency_obj)


    return dependencies


