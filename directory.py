from collections import defaultdict
from git import Repo
import os
from typing import Dict, List
from concurrent.futures import ProcessPoolExecutor


COMMIT_PCT_SCORE_WEIGHT = .6
FILE_PCT_SCORE_WEIGHT = .4
LINES_PCT_SCORE_WEIGHT = .5
# TODO_CNT_SCORE_WEIGHT = .1
TIME_PERCENT_SCORE_WEIGHT = .45

MILI_IN_24_HOURS = 86400000

class Directory:
    """Represents a directory in a git repo
    
    Here are the existing scoring functions:
    - commit percentage
        - percentage of all commits in that directory were authored by that committer
        - uses `git log`
    - file percentage
        - percent of files in that directory that were touched by that committer
        - uses `git log`
    - line percentage
        - percent of lines in that directory that were touched by that committer
        - uses `git blame`
    - time percentage
        - amount of time the author spent committing relative to the age of the repo
        - uses `git log`
    Each percentage is then weighted and aggregated to get the final score
    """


    def __init__(self, path : str, repo: Repo, branch='master'):
        self.directory = path
        self.expert_scores = defaultdict(float) # dictionary where the keys are author email addresses and the values are their scores
        self.repo = repo
        self.branch = branch
        self.calculate_and_aggregate_expert_scores()

    def calculate_and_aggregate_expert_scores(self) -> None:
        """calls each scoring function and aggregates the scores"""
        # since most our the tasks are I/O bound, multithreading is preferred. 
        # However, gitpython is not thread safe
        with ProcessPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(func) for func in [self.calculate_commit_pct_score, self.calculate_file_pct_score, self.calculate_lines_pct_score, self.calculate_time_pct_score]]
            scores = [future.result() for future in futures]
        authors = set()
        for score in scores:
            authors.update(score.keys())
        
        for author in authors:
            for score in scores:
                self.expert_scores[author] += score[author]

    def calculate_commit_pct_score(self) -> Dict[str, float]:
        """calculate score based on the percentage of all commits in that directory were authored by that committer"""
        author_commits = defaultdict(int)
        total_commits = 0

        commits = self.repo.iter_commits(paths=self.directory)

        for commit in commits:
            author_commits[commit.author.email] += 1
            total_commits += 1

        author_percentages = {author: commits / total_commits * 100 for author, commits in author_commits.items()}

        expert_scores = defaultdict(float)
        for author, percentage in author_percentages.items():
            expert_scores[author] += percentage * COMMIT_PCT_SCORE_WEIGHT
        return expert_scores
    
    def calculate_file_pct_score(self) -> Dict[str, float]:
        """calculate score based on the percent of files in that directory that were touched by that committer"""
        authors = defaultdict(set)
        all_files = set()
        commits = self.repo.iter_commits(paths=self.directory)

        for commit in commits:
            for modified_file in commit.stats.files:
                if modified_file.startswith(self.directory):
                    authors[commit.author.email].add(modified_file)
                    all_files.add(modified_file)

        total_files_cnt = len(all_files)
        author_percentages = {author: len(files) / total_files_cnt * 100 for author, files in authors.items()}

        expert_scores = defaultdict(float)
        for author, percentage in author_percentages.items():
            expert_scores[author] += percentage * FILE_PCT_SCORE_WEIGHT
        return expert_scores
        
    def calculate_lines_pct_score(self) -> Dict[str, float]:
        """calculate score based on the percent of lines in that directory that were touched by that committer"""
        author_lines = defaultdict(set)
        total_lines = 0

        dir_path = os.path.join(self.repo.working_dir, self.directory)

        # walk through the directory and all the files, and for each line in each file, find the author of that line
        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                # this only takes into the account the last person to touch the line since they will have the most up-to-date info
                # (also because git log on each line for all files is expensive and complex considering the scope of this project)
                for blame_entry in self.repo.blame_incremental('HEAD', file_path):
                    lines = set(range(blame_entry.linenos.start, blame_entry.linenos.stop))
                    author_lines[blame_entry.commit.author.email].update(lines)
                    total_lines += len(lines)

        author_percentages = {author: len(lines) / total_lines * 100 for author, lines in author_lines.items()}

        expert_scores = defaultdict(float)
        for author, percentage in author_percentages.items():
            expert_scores[author] += percentage * LINES_PCT_SCORE_WEIGHT
        return expert_scores
        
    def calculate_time_pct_score(self) -> Dict[str, float]:
        """calculate score based on the amount of time the author spent committing relative to the age of the repo"""

        # calculate repo age
        first_commit = next(self.repo.iter_commits(self.branch, reverse=True))
        last_commit = list(self.repo.iter_commits(self.branch, max_count=1))[0]
        age = last_commit.committed_date - first_commit.committed_date

        author_commit_times = {} # author: {first_commit: datetime, last_commit: datetime}
        commits = self.repo.iter_commits(paths=self.directory)

        # traverse all commits and find the first and last commit for each author
        for commit in commits:
            if commit.author.email not in author_commit_times:
                # for people that have only committed once, we want to give them a time range of 24 hours
                author_commit_times[commit.author.email] = {'first_commit': commit.committed_date, 'last_commit': commit.committed_date + MILI_IN_24_HOURS}
            else:
                if commit.committed_date < author_commit_times[commit.author.email]['first_commit']:
                    author_commit_times[commit.author.email]['first_commit'] = commit.committed_date
                if commit.committed_date > author_commit_times[commit.author.email]['last_commit']:
                    author_commit_times[commit.author.email]['last_commit'] = commit.committed_date
        
        expert_scores = defaultdict(float)
        for author, dates in author_commit_times.items():
            author_commit_time_pct = (dates['last_commit'] - dates['first_commit']) / age * 100
            expert_scores[author] += author_commit_time_pct * TIME_PERCENT_SCORE_WEIGHT
        return expert_scores
    
    def get_top_authors(self, n=3) -> List[str]:
        return sorted(self.expert_scores, key=lambda item: item[1], reverse=True)[:n]
