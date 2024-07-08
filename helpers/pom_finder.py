import os
import xml.etree.ElementTree as ET

# This will search every pom path and find the one that defines a given artifact
def find_pom_path_with_artifact_id(artifact_name, parent_repo):
    dep_path = ""
    for pom_path in parent_repo.all_poms:
        tree = ET.parse(pom_path)
        root = tree.getroot()
        nm = root.tag.split('}')[0].strip('{')
        namespace = {'m': nm}
        artifact_element = root.find('m:artifactId', namespace)

        if artifact_element is not None:
            if artifact_element.text == artifact_name:
                # dep_path = os.path.dirname(os.path.realpath(pom_path))
                # print(f"[pom_finder.py] FOUND ARTIFACT DEFINED IN A POM => {pom_path}")
                return pom_path

    return dep_path
