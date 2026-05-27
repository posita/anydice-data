#!/usr/bin/env bash
# ======================================================================================
# Copyright and other protections apply. Please see the accompanying LICENSE file for
# rights and restrictions governing use of this software. All rights not expressly
# waived or licensed are reserved. If that file is missing or appears to be modified
# from its original, then please contact the author before viewing or using this
# software in any capacity.
# ======================================================================================
#
# Reassemble anydice-programs-all.db.gz from its byte-split shards.
#
# The full ~270MB corpus .db.gz exceeds GitHub's 50MB soft warning, so it lives in this
# repo as a series of `anydice-programs-all.db.gz.part-NN.bin` shards. This script
# concatenates them back into the canonical `anydice-programs-all.db.gz` and verifies
# the result against the sha256 sidecar's compressed-hash line.
#
# Usage:
#     ./assemble-programs-db.sh
#
# Output:
#     anydice-programs-all.db.gz   (reassembled, sha256-verified)
# ======================================================================================
set \
    -o errexit \
    -o nounset \
    -o pipefail

# Force byte-order (POSIX) sorting for glob expansion + sort utilities, so shard
# concatenation order matches the original split order regardless of the user's locale.
# Without this, some locales' collation rules could reorder ASCII digit sequences in
# surprising ways. Has no effect at 7 zero-padded shards in any reasonable locale, but
# the failure mode would be silent (wrong reassembled bytes, sha256 mismatch) so the
# belt-and-suspenders is worth the one line.
export LC_ALL=C

# Expected number of shards. Update this constant alongside any re-pack that changes the
# shard count (i.e., whenever `split` produces a different number of part files for an
# updated corpus). NOTE: if the corpus ever grows past 99 shards, the 2-digit
# zero-padded suffix scheme (-00..-99) needs to expand (e.g., `split -a 3`); a mix of 2-
# and 3-digit suffixes would sort lexically wrong (-100 before -99).
EXPECTED_SHARD_COUNT=7

PROG_NAME="$( basename "${0}" )"
PROG_DIR="$( cd "$( dirname "${0}" )" && pwd )"
cd "${PROG_DIR}"

shards=( anydice-programs-all.db.gz.part-*.bin )
# `nullglob` is not set, so an unmatched glob leaves a single literal element. Test the
# first element's existence to distinguish "no matches" from "one real shard."
if ! [ -f "${shards[0]}" ] ; then
    echo 1>&2 "${PROG_NAME}: no shards found (anydice-programs-all.db.gz.part-*.bin)"
    exit 1
fi
if [ "${#shards[@]}" -ne "${EXPECTED_SHARD_COUNT}" ] ; then
    echo 1>&2 "${PROG_NAME}: found ${#shards[@]} shard(s), expected ${EXPECTED_SHARD_COUNT}"
    echo 1>&2 "  (if this is intentional after a re-pack, update EXPECTED_SHARD_COUNT in this script)"
    exit 1
fi
if ! [ -f anydice-programs-all.db.sha256 ] ; then
    echo 1>&2 "${PROG_NAME}: missing sha256 sidecar (anydice-programs-all.db.sha256)"
    exit 1
fi

echo "${PROG_NAME}: reassembling ${#shards[@]} shards..."
cat "${shards[@]}" > anydice-programs-all.db.gz

# `--ignore-missing` skips the .db (uncompressed) hash line, which we haven't inflated
# yet; the .db.gz hash line surfaces any mismatch with a FAILED marker.
if ! sha256sum --check --ignore-missing anydice-programs-all.db.sha256 ; then
    rm -f anydice-programs-all.db.gz
    echo 1>&2 "${PROG_NAME}: sha256 mismatch after reassembly; .db.gz removed"
    exit 1
fi
