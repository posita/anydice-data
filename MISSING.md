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

# Missing Programs

The following IDs are absent from `anydice.com/program/`:

- [`133a7`](https://anydice.com/program/133a7) —
- [`1452b`](https://anydice.com/program/1452b)
- [`279e0`](https://anydice.com/program/279e0)
- [`27c2c`](https://anydice.com/program/27c2c)
- [`27f7b`](https://anydice.com/program/27f7b)

These programs likely exist on anydice.com.
Their HTML pages were retrieved during the 2026-05-17 crawl, archived in `anydice.com-2026-05-17T15:08:22-0500.tar.gz`, but the corresponding HTML files don't contain extractable program source.
The retrieval errors appear to have occurred server-side during that crawl.
The HTML responses were structurally valid but missing a typical `loadedProgram` JavaScript variable that normally carries the program text.

Re-harvesting these IDs is not currently possible because anydice.com's program-retrieval functionality is broken (status as of 2026-05-25).
If the that functionality is restored, the missing programs can be re-fetched and added to the corpus.

The highest ID retrieved is [`4327d`](https://anydice.com/program/4327d).

---

The crawl was performed with `wget`, e.g.:

```sh
set -eux
(
    set +x
    for i in ...
    [ -f "$( printf 'anydice.com/program/%x.html' "${i}" )" ] || printf 'https://anydice.com/program/%x\n' "${i}"
    set -x
) \
    | xargs \
        --no-run-if-empty \
        wget \
        --adjust-extension \
        --convert-links \
        --backup-converted \
        --mirror \
        --page-requisites \
        --no-parent \
        --wait 0.5 \
        --random-wait
```
