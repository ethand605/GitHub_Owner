from directory import Directory
from git import Repo

REPO_PATH = './go/'
repo = Repo(REPO_PATH)

sub_dir = ''
top_auth_cnt = 3


cache = {}

def format_gh_expert_output(top_authors, directory):
    return f'\nTop {top_auth_cnt} authors for "{directory}":\n' + '\n'.join([f'{author}' for author in top_authors])

while True:
    sub_dir = input("Please enter the subdirectory: ")
    # TODO: take in the n in top n authors as input as well
    try:
        if sub_dir not in cache:
            directory = Directory(sub_dir, repo)
            top_authors = directory.get_top_authors()
            res = format_gh_expert_output(top_authors, sub_dir)
            cache[sub_dir] = format_gh_expert_output(top_authors, sub_dir)
        print(cache[sub_dir])
        print()
    except Exception as e:
        print(e)
        print(type(e).__name__)
        raise e
        print("Invalid input. Please enter a valid subdirectory.")