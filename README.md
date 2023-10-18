## Getting Started

### Prerequisites

- Python 3.x
- Conda (optional)

### Running the Project

1. Load the dependencies by running the following script:

   ```
   git clone git@github.com:golang/go.git
   ```

   ```
   pip install -r requirements.txt
   ```

2. Run the main Python script:
   ```bash
   python main.py
   # or
   python3 main.py
   ```

When asked "Please enter the subdirectory:", you can input `./.github` or `./api`. (It is recommended to `cd` into `./go` and run `ls` first to see what directories are available.)

It is also recommended to query subdirectories instead of root directory. There are definitely room for improvements for execution time/performance, but due to time constraint I will not be implementing them.

## GitHub Owners: Expert Ranking System Summary

Our ranking system identifies the "owners" of a GitHub directory based on four key metrics:

- **Commit Contribution (%):** Measures the percentage of commits in a directory made by a contributor (`git log`).

- **File Touch (%):** Measures the percentage of files in a directory modified by a contributor (`git log`).

- **Line Touch (%):** Estimates the percentage of lines in a directory modified by a contributor (`git blame`).

- **Time Commitment (%):** Evaluates the time a contributor has spent committing relative to the repository's age (`git log`).

These metrics contribute to an overall "expert score" for each contributor, ranking them based on their engagement with the directory.

## TODOs

- Unify the commit traversal logic
  - Currently, the commit history is traversed multiple times
- Use tqdm for progress bars
  - Progress bar for overall progress
  - Progress bar for each scoring function
- Multithreading for each subdirectory
  - Each subdirectory is independent of each other and can be processed in parallel
  - most of the tasks are I/O bound

## Ideas for Future Work

1. Break it down to smaller units - file/line level scoring
2. Pull requests/issues support
3. (Wild idea) If queried frequently, translate commit graph to a graph database, e.g., neo4j. No need for aggregation/parsing at code level
4. Assuming this is a long-running server, implement re-pull and cache invalidation
   - invalidate cache when new commits are pushed
   - invalidating subdirectory cache also invalidates parent directory cache
5. Different weights for different files, e.g., README.md is more important than .gitignore
6. Support recursive query: querying a parent directory should also calculate and cache the experts for its subdirectories
   - https://imgur.com/rr7gWz4
   - this would require reworking the current `git log` logic and exclude subdirectories, not implmemented due to time constraint
   - will also need to take into considertaion of weights of subdirectories
