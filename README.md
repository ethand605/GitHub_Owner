# GitHub Owner

## Getting Started

### Prerequisites

- Python 3.x
- Conda (optional)

### Running the Project

1. Load the dependencies by running the following script:

   ```bash
   ./load_dep.sh
   ```

2. Run the main Python script:
   ```bash
   python main.py
   # or
   python3 main.py
   ```

When asked "Please enter the subdirectory:", you can input `./.github` or `./api`. (It is recommended to `cd` into `./go` and run `ls` first to see what directories are available.)

It is also recommended to query subdirectories instead of root directory. There are definitely room for improvements for execution time/performance, but due to time constraint I will not be implementing them.

## TODOs

- Unify the commit traversal logic
  - Currently, the commit history is traversed multiple times
- Use tqdm for progress bars
  - Progress bar for overall progress
  - Progress bar for each scoring function
- Multithreading for each subdirectory
  - Each subdirectory is independent of each other

## Ideas for Future Work

1. Break it down to smaller unit - file/line level
2. Pull requests/issues support
3. (Wild idea) If queried frequently, translate commit graph to a graph database, e.g., neo4j. No need for aggregation/parsing
4. Assuming this is a long-running server, implement re-pull and cache invalidation
5. Different weights for different files, e.g., README.md is more important than .gitignore
6. Support recursive query: querying a parent directory should also calculate and cache the experts for its subdirectories
   - a. https://imgur.com/rr7gWz4
   - b. this would require reworking the current `git log` logic and exclude subdirectories, not implmemented due to time constraint
   - c. will also need to take into considertaion of weights of subdirectories
