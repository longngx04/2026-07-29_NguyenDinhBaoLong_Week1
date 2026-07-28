# Deferred WebGoat ground-truth reference

This document records an upstream candidate dataset for the Week-2 evaluation work. It is
not an input to the Week-1 scanner commands and no evaluation metric is derived from it yet.

## Pinned upstream reference

- Repository: <https://github.com/dmk1en/gt>
- Upstream default branch when checked: `main`
- Pinned commit: [`ab1b67414825a0cceadf84213575b05a7ccfe659`](https://github.com/dmk1en/gt/commit/ab1b67414825a0cceadf84213575b05a7ccfe659)
- Commit title: `v2`
- Checked: 2026-07-28
- License: no license was declared in the GitHub repository metadata when checked.

The repository is recorded by URL and immutable commit only. Its contents are not vendored,
automatically downloaded, or modified by Project Sentinel.

## Deferred Week-2 use

Before consuming this source, the team must:

1. Review its schema and licensing/permission for the intended use.
2. Confirm that its target/version assumptions are compatible with this project's pinned
   WebGoat `v2025.3` source commit (`c3ed45a733377bc7313b93f57ff518254d81380f`).
3. Create a versioned mapping from ground-truth entries to normalized Week-1 findings while
   preserving the native OpenGrep JSON and FindSecBugs SARIF files unchanged.
4. Define the evaluation protocol before reporting precision, recall, false positives,
   false negatives, baseline comparisons, or ablation results.

Until those checks are complete, this reference is provenance only and must not be presented
as validated ground truth for the current scanner output.
