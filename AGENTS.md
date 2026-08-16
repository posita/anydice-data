# `anydice-data` maintenance guidance

This repository contains the AnyDice program corpus and the tools used to assemble, annotate, and verify it.
It is the empirical reference for the AnyDice-compatible interpreter in `anydyce`.

Read `README.md` before corpus maintenance.
It defines the current layout, setup, assembly, packing, and verification commands.
The code and README are authoritative when this guidance becomes stale.

## Working safely

Treat the live working tree as authoritative.
Before editing an existing file, inspect its working-tree, staged, and `HEAD` versions, then record and immediately recheck a content hash.
If it changed, re-read it and preserve the newer work.
After editing, inspect the diff and limit it to the requested regions.
Do not stage changes unless the user asks.

Corpus operations can be expensive, destructive, or network-sensitive.
Resolve exact database and program targets before running them.
Do not start a crawl, corpus-wide computation, or corpus-wide verification as a routine validation step.

## Corpus integrity

The compressed archives, full-corpus shards, SHA-256 sidecars, harvested source files, and crawl archives preserve corpus data or provenance.
They are not disposable build artifacts.

The large uncompressed database and reassembled full-corpus gzip are local derivatives.
Use the small curated database unless the task requires corpus-wide evidence.

Do not hand-edit compressed archives, shards, sidecars, or SQLite bytes.
Do not rewrite harvested user programs for style.
Program source files use LF line endings as enforced by `.gitattributes`.

`anydice-programs.py` checks available hashes when inflating databases.
A mismatch is an integrity failure, not an invitation to regenerate the sidecar.
Use `assemble-programs-db.sh` and `pack-programs-db.sh` only for their documented roles.

Packing uses `gzip --rsyncable` to keep unchanged shard regions stable.
Do not substitute ordinary gzip or change shard sizing casually; either can create enormous diffs.
If the full-corpus shard count changes, update `EXPECTED_SHARD_COUNT` in `assemble-programs-db.sh` in the same change.

After an intentional corpus update, verify symlinks, sidecar hashes, shard ordering, shard count, and the Git diff before committing.

## External and expensive operations

Commands such as `fetch`, `link`, `recanon`, `compute`, and `annotate add/remove` can mutate a database.
Inspect their help and specify the intended database.
Keep annotations evidence-based and preserve their explanatory notes.

Remote operations require `--allow-remote` where supported.
That flag is an intentional consent boundary.
Do not bypass it or contact anydice.com without user authorization.
Respect the crawl delay and load guidance in `MISSING.md` and `README.md`.

`verify --all` can take a long time.
Use targeted program IDs while developing.
Keep worker isolation and timeout safeguards in place for pathological programs.

## Style

Python docstrings use Markdown and keep one sentence per source line.
Comments should explain integrity, provenance, external boundaries, or counterintuitive behavior rather than restating code.
