#!/usr/bin/env python3
# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
#
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!! IMPORTANT: READ THIS BEFORE EDITING! !!!!!!!!!!!!!!!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Please keep each docstring sentence on its own unwrapped line. It looks like crap in a
# text editor, but it has no effect on rendering, and it allows much more useful diffs.
# (This does not apply to code comments.) Thank you!
# ======================================================================================

import argparse
import logging
from pathlib import Path

from anydyce.anydice.fetch import (
    extract_program_id_and_url,
    fetch_anydice_program,
    sharded_subpath_from_program_id,
)

_LOGGER = logging.getLogger(__name__)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Extract AnyDice programs from sources and write them to local text files within a sharded directory space."
    )
    parser.add_argument(
        "--shard-dir",
        metavar="PATH",
        type=Path,
        default=Path("program"),
        help=f"the path of the top-level directory for the shards",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        metavar="LEVEL",
        help="Logging verbosity. "
        "One of DEBUG, INFO, WARNING, ERROR, CRITICAL (default: WARNING).",
    )
    parser.add_argument(
        "html_locs",
        metavar="HEX ID | PATH | URL",
        nargs="*",
        help="locations from which to harvest the programs (one per file)",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s: %(message)s",
    )

    shard_dir: Path = args.shard_dir
    if not shard_dir.is_dir():
        _LOGGER.info(f"creating shard dir: {shard_dir}")
        shard_dir.mkdir(exist_ok=True, parents=True)

    shard_dirs_seen: set[Path] = set()
    for html_file in args.html_locs:
        try:
            program_id, initial_url = extract_program_id_and_url(html_file)
        except Exception as exc:
            _LOGGER.error(f"{exc} (skipping {html_file})")
            continue
        program_shard_file = shard_dir / sharded_subpath_from_program_id(program_id)
        program_shard_dir = program_shard_file.parent
        if program_shard_dir not in shard_dirs_seen:
            if not program_shard_dir.is_dir():
                _LOGGER.info(f"creating shard dir: {program_shard_dir}")
                program_shard_dir.mkdir(exist_ok=True, parents=True)
            shard_dirs_seen.add(program_shard_dir)
        if program_shard_file.exists():
            _LOGGER.info(f"skipping existing program file: {program_shard_file}")
            continue

        try:
            _, _, _final_url, program = fetch_anydice_program(initial_url)
        except Exception as exc:
            _LOGGER.error(f"{exc} (skipping {html_file})")
            continue

        _LOGGER.info(f"writing {program_id} to program file: {program_shard_file}")
        _LOGGER.debug(program)
        program_shard_file_tmp = program_shard_file.with_suffix(".txt.tmp")
        program_shard_file_tmp.write_text(program, encoding="utf-8")
        program_shard_file_tmp.replace(program_shard_file)


if __name__ == "__main__":
    main()
