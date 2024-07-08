import os
import shutil
from _settings import settings as _s
from glob import glob
import requests

def find_dependency_code(dep_obj):
    dep_path_list = [] # hold list of paths for each of the dependencies we find

    artifact_name = dep_obj.artifact
    print(f"Finding Code for Dependency: {artifact_name}")

    # See if we already found this dependency
    dep_path = _s.get_dependency_path(artifact_name)

    # Check folders for code
    if not dep_path:
        # Commons artifacts have 'commons-' before the folder name
        if ".commons" in dep_obj.group_id:
            folder_to_search_for = "commons-" + artifact_name
        else:
            folder_to_search_for = artifact_name

        for folder_path in glob(f"{_s.DEPENDENCY_SRC}/**/{folder_to_search_for}", recursive=True):
            print(f"Looking through existing files...")
            dep_path = folder_path

        if dep_path:
            _s.add_found_dependency(artifact_name, dep_path)
        else:
            print("Not Found.")


    # Attempt to get from Maven
    if not dep_path:
        print(f"Looking in Maven Repo...")
        group_id = dep_obj.group_id
        version = dep_obj.version
        dep_path = download_maven_artifact(group_id, artifact_name, version)


    if dep_path:
        dep_path_list.append(dep_path)
        return dep_path
    else:
        print(f"Dependency not found: {artifact_name}")
        return ""

    # for key, path in _s.FOUND_DEPENDENCIES.items():
    #     print(path)

    # return dep_path_list



def copy_dependencies():
    return False
    # destination = shutil.copytree(src, dest)

def download_file(url, dest_folder):
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

def download_maven_artifact(group_id, artifact_id, version, repo_url='https://repo1.maven.org/maven2'):
    group_path = group_id.replace('.', '/')

    artifact_url = f'{repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.jar'

    if artifact_id == "pagehelper-spring-boot-starter":
        print(f"TESTING => {artifact_url}")

    dest_folder = os.path.join(_s.PROJECT_PATH, 'maven_downloads', group_id, artifact_id, version)

    if download_file(artifact_url, dest_folder):
        return dest_folder
    else:
        return ""

