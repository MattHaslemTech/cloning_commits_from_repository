# cloning_commits_from_repository
Traverses the commits of a repository and clones any commit that contains a particular phrase

`pipenv install`

`pipenv run python main.py`

Enter the repository. Either remote HTTPS address or full local path.

Confirm the substring to search commits for.

Repos will be written to a `/output_repos` directory within the project. They will each have a `_COMMIT_INFO.txt` file with a summary of the commit. 

Errors will be outputted to `/debug/error.txt` within the project
