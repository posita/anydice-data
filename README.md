<!---
  Copyright and other protections apply.
  Please see the accompanying LICENSE file for rights and restrictions governing use of this software.
  All rights not expressly waived or licensed are reserved.
  If that file is missing or appears to be modified from its original, then please contact the author before viewing or using this software in any capacity.

  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!! IMPORTANT: READ THIS BEFORE EDITING! !!!!!!!!!!!!!!!
  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  Please keep each sentence on its own unwrapped line.
  It looks like crap in a text editor, but it has no effect on rendering, and it allows much more useful diffs.
  Thank you!
-->

# anydice-data

A corpus of [AnyDice](https://anydice.com/) programs, along with the tooling used to assemble and verify it.

This corpus is the empirical reference used to reverse-engineer and validate the AnyDice-compatible interpreter in [`anydyce`](https://github.com/posita/anydyce/).
Every divergence between the cleanroom interpreter and AnyDice's own output has been triaged against programs in this corpus.
The buckets are documented as annotations in the SQLite DBs.

## Cloning

Unless history is desired for some reason, a shallow clone is recommended to avoid fetching obsolete versions of large files:

```sh
git clone --depth 1 https://github.com/posita/anydice-data.git
```

## Layout

| File                                                 | Description                                                                                                            |
|------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| `anydice.com/program/<XX>/<YY>/<id>.txt`             | Raw AnyDice source, one program per file, sharded by the last 4 hex chars of the zero-padded program ID (~175k files). |
| `anydice.com-<TIMESTAMP>.tar.gz`                     | Raw HTML crawl tarball (provenance archive).                                                                           |
| `anydice-programs.db.gz`                             | Small curated corpus (~3MB compressed).                                                                                |
| `anydice-programs.db.sha256`                         | sha256 sidecar (uncompressed + compressed).                                                                            |
| `anydice-programs-all.db.gz.part-<NN>.bin`           | Full corpus, byte-split shards (~160k programs, ~270MB total across 7 shards, each shard <50MB).                       |
| `anydice-programs-all.db.sha256`                     | sha256 sidecar (uncompressed + compressed).                                                                            |
| [`assemble-programs-db.sh`](assemble-programs-db.sh) | Reassembles shards into `anydice-programs-all.db.gz`.                                                                  |
| [`pack-programs-db.sh`](pack-programs-db.sh)         | Re-compresses `.db` → `.db.gz` with rsyncable gzip (for updating the committed shards and sidecar after a fresh pack). |
| [`anydice-programs.py`](anydice-programs.py)         | CLI: fetch, annotate, verify, etc. Inflates and verifies `.db.gz`  automatically on first use.                         |
| [`harvest-program-txt.py`](harvest-program-txt.py)   | Extracts program from AnyDice source HTML into the sharded `.txt` tree.                                                |
| [`MISSING.md`](MISSING.md)                           | IDs that couldn't be re-harvested due to server-side glitches during the 2026-05-17 crawl.                             |

## Using the corpus

### Individual programs

The sharded `.txt` files are addressable via `raw.githubusercontent.com`:

```
https://raw.githubusercontent.com/posita/anydice-data/refs/heads/main/anydice.com/program/<XX>/<YY>/<id>.txt
```

`<XX>` and `<YY>` are the last 4 hex characters of the program ID (left-padded to 4 chars with zeros), split into two-character segments.
For example, program `4d2` is left-padded to `04d2`, and lives at [`anydice.com/program/04/d2/4d2.txt`](https://raw.githubusercontent.com/posita/anydice-data/refs/heads/main/anydice.com/program/04/d2/4d2.txt).
Program `1ab2c` lives at [`anydice.com/program/ab/2c/1ab2c.txt`](https://raw.githubusercontent.com/posita/anydice-data/refs/heads/main/anydice.com/program/ab/2c/1ab2c.txt).

### Unique programs in a SQLite database

Not all program IDs are stored in the big corpus database.
Where multiple programs result in the same parse tree, those with lower IDs are omitted.

Set up a local working tree:

```sh
uv venv --clear --prompt "$( basename "${PWD}" )" --relocatable
source .venv/bin/activate
uv pip install -r requirements.txt

# For the big corpus only, reassemble the .db.gz from the committed shards
./assemble-programs-db.sh
```

Then use the helper:

```sh
uv run ./anydice-programs.py --help

# Show the program saved to ID
uv run ./anydice-programs.py --db anydice-programs-all.db show 4d2

# Verify our anydyce interpreter against AnyDice's produced output for every program
uv run ./anydice-programs.py --db anydice-programs-all.db verify --isolated-workers 2 --timeout 60 --all

# List annotations (known AnyDice defect classes)
uv run ./anydice-programs.py --db anydice-programs-all.db annotate --list
```

The helper inflates and verifies `.db.gz` to `.db` automatically on first invocation.

## Provenance

Programs were retrieved from `anydice.com/program/<id>` for hex IDs starting at `1` and walking forward.
The crawl tarball (`anydice.com-<TIMESTAMP>.tar.gz`) is committed alongside the extracted `.txt` files so anyone can verify the extraction independently.
The highest retrieved program ID was [`4327d`](https://raw.githubusercontent.com/posita/anydice-data/refs/heads/main/anydice.com/program/32/7d/4327d.txt).

The `.txt` files were extracted from the crawled HTML via [`harvest-program-txt.py`](harvest-program-txt.py).
Extracted programs with `\r` line endings were normalized to `\n` via `git add --renormalize` per the project's `.gitattributes` (`text eol=lf`), since AnyDice's parser is whitespace-insensitive but Git's diff tools work better with consistent line endings.
Among those retrieved, the sole program to contain carriage returns was [`220`](https://raw.githubusercontent.com/posita/anydice-data/refs/heads/main/anydice.com/program/02/20/220.txt).

## Updates and integrity

To publish changes after updating either SQLite DB (e.g., adding additional programs, annotations, etc.):

```sh
# Regenerate .db.gz + .sha256
./pack-programs-db.sh anydice-programs-all.db

# For the big corpus only, resplit
split -b 45M -d -a 2 --additional-suffix=.bin \
    anydice-programs-all.db.gz anydice-programs-all.db.gz.part-
```

If the shard count changes, update `EXPECTED_SHARD_COUNT` in [`assemble-programs-db.sh`](assemble-programs-db.sh) accordingly.

[`pack-programs-db.sh`](pack-programs-db.sh) uses `gzip --rsyncable`, so most shard *contents* stay bit-identical across re-packs — only shards covering changed regions are rewritten.
This keeps the git history clean across the corpus's slow update cadence (~once per 1-2 years).

## License

[MIT](LICENSE).
The AnyDice source programs themselves were authored by their respective AnyDice users
This repository's license covers only the harvesting and assembly tooling as well as the curatorial work of organizing the corpus.
