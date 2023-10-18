from git import Repo

repo = Repo('./go/')
# tree = repo.head.commit.tree

# print(tree)

# def get_commits_for_directory(repo_path, directory):
#     repo = Repo(repo_path)
#     commits = list(repo.iter_commits('master'))
#     print(len(commits))

#     directory_commits = []

#     for commit in commits[:100]:
#         for modified_file in commit.stats.files:
#             if modified_file.startswith(directory):
#                 directory_commits.append(commit)
#                 break

#     return directory_commits

# repo_path = './go/'
# directory = '.github'
# commits = get_commits_for_directory(repo_path, directory)

# for commit in commits:
#     print(commit)

from git import Repo
from collections import defaultdict
import os, subprocess
repo = Repo('/Users/ethand/Documents/uplimit-take-home/go')

def get_file_percentages(directory):
    authors = defaultdict(set)
    all_files = set()

    commits = list(repo.iter_commits(paths=directory))
    print(commits)
    for commit in commits:
        for modified_file in commit.stats.files:
            if modified_file.startswith(directory):
                # print(modified_file)

                authors[commit.author.email].add(modified_file)
                all_files.add(modified_file)

    author_percentages = {author: len(files) / len(all_files) for author, files in authors.items()}

    return author_percentages
print("Current working directory:", os.getcwd())
# def get_line_percentages(directory):
#     author_lines = defaultdict(int)
#     total_lines = 0

#     for root, dirs, files in os.walk(directory):
#         print(root, dirs, files)
#         print(files)
#         for file in files:
#             result = subprocess.run(['git', 'blame', '--line-porcelain', os.path.join(root, file)], capture_output=True, text=True)
#             lines = result.stdout.splitlines()
#             current_author = None
#             for line in lines:
#                 if line.startswith('author '):
#                     current_author = line[7:]
#                 elif line.startswith('\t') and not line.startswith('\t\t'):
#                     author_lines[current_author] += 1
#                     total_lines += 1

#     for author, lines in author_lines.items():
#         author_lines[author] = lines / total_lines

#     return author_lines

def get_line_percentages(directory):
    author_lines = defaultdict(int)
    total_lines = 0

    for commit in repo.iter_commits(paths=directory):
        for modified_file in commit.stats.files:
            if modified_file.startswith(directory):
                blame = list(repo.blame(commit, modified_file))
                for blob, lines in blame:
                    if blob.author.email not in author_lines:
                        author_lines[blob.author.email] = 0
                    author_lines[blob.author.email] += len(lines)
                    total_lines += len(lines)

    for author, lines in author_lines.items():
        author_lines[author] = lines / total_lines

    return author_lines

print(get_line_percentages('.github'))

print(get_line_percentages('.github'))
# print(get_file_percentages('.github'))