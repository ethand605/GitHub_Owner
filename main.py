from directory import Directory
from git import Repo

def main():
    REPO_PATH = './go/'
    repo = Repo(REPO_PATH)

    sub_dir = ''

    cache = {}

    def format_gh_expert_output(top_authors, directory):
        return f'\nTop 3 authors for "{directory}":\n' + '\n'.join([f'{author}' for author in top_authors])

    while True:
        sub_dir = input("Please enter the subdirectory: ")
        # TODO: take in the n in top n authors as input as well
        try:
            if sub_dir not in cache:
                directory = Directory(sub_dir, repo)
                top_authors = directory.get_top_authors()
                cache[sub_dir] = format_gh_expert_output(top_authors, sub_dir) if top_authors else ''
            if cache[sub_dir]:
                print(cache[sub_dir])
                print()
            else:
                print("No Authors found/Invalid input. Please enter a valid subdirectory.\n")
        except Exception as e:
            print(e)
            # print out type of error
            print(type(e))
            print("Invalid input. Please enter a valid subdirectory.")

if __name__ == "__main__":
    main()