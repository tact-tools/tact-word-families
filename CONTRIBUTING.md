# Contributing to Tact Word Families

Tact Word Families generates English word-family variant rows for Tact
dictionary builds. The repository is intentionally small: the source of truth is
the generator script plus licensing and attribution metadata.

## Project Scope

The generator code and repository documentation are licensed under the MIT
License. Generated data artifacts, including `en_US/variants.tsv`, are derived
from input datasets and carry source-data attribution requirements. Keep
`README.md`, `NOTICE`, and `LICENSE` aligned whenever the source data changes.

The current generated data is derived from the Leipzig Corpora Collection
English news corpus frequency list. Do not add MorphyNet, downloaded corpora, or
other third-party derived data unless its license has been reviewed and the
attribution text has been updated.

Generated TSV files are build artifacts. Do not commit `en_US/variants.tsv`
unless the project explicitly decides to publish that artifact from this
repository.

## Development Setup

The generator is a standalone Python script and should run with the system
Python available in the development environment.

Generate the variant file from the repo root:

```bash
python3 scripts/generate_en_us_variants.py
```

The script expects the Tact dictionary lexicon at:

```text
../dictionary/build/en_US/language-data/en_US/lexicon.tsv
```

Use `--lexicon` and `--output` if you need alternate paths:

```bash
python3 scripts/generate_en_us_variants.py \
  --lexicon /path/to/lexicon.tsv \
  --output /tmp/variants.tsv
```

## Validation

Before committing generator changes, run:

```bash
python3 -m py_compile scripts/generate_en_us_variants.py
python3 scripts/generate_en_us_variants.py
```

Then check the generated TSV for basic structure:

```bash
python3 - <<'PY'
import csv
from pathlib import Path

path = Path("en_US/variants.tsv")
rows = []
bad = []
with path.open(newline="") as handle:
    for line_number, row in enumerate(csv.reader(handle, delimiter="\t"), 1):
        if len(row) != 3:
            bad.append((line_number, row))
            continue
        rows.append(tuple(row))

print("rows", len(rows))
print("malformed", len(bad))
print("duplicate triples", len(rows) - len(set(rows)))
PY
```

Expected results for a clean generated file are zero malformed rows and zero
duplicate triples.

## Data Quality Guidelines

Prefer precision over broad recall. A candidate being a valid English word is
not enough evidence that it belongs to the same word family.

Use curated tables for high-risk morphology:

- irregular verbs
- classical plurals
- known family edges
- negative-prefix derivations
- demonyms and proper adjectives
- denylisted surface collisions

Be conservative with rules that touch short stems, proper-name-like lemmas,
archaic final-`e` forms, and surface-form collisions. If a rule creates rows
like `cord -> record`, `sense -> nonsense`, or `coole -> cooler`, prefer a
curated allowlist or denylist over broad confidence changes.

When changing collision handling, verify both sides of the intended behavior:
valid homographs should be able to coexist, while truncated stems and
surname-like forms should not displace ordinary lemmas.

## Commit Workflow

Keep commits atomic. A typical change should include the generator edit and any
necessary documentation or attribution updates. Avoid committing regenerated
`en_US/variants.tsv` unless the artifact is intentionally being published.

Commit summaries use:

```text
prefix: Capitalized summary
```

The summary must stay under 72 characters. Use a lowercase prefix such as
`project:`, `license:`, `generator:`, `variants:`, or `docs:`.

Commit bodies must contain at least three paragraphs:

1. Describe the repository state immediately before the commit is applied.
2. Explain the limitation or missing capability in that state.
3. Start with `This commit` and describe the specific change being made.

Use a fourth paragraph for multi-commit series to say what later commits will
do, or to close the series when the final commit reaches the stated goal.

Body lines must wrap at 75 characters. Do not use `Co-Authored-By` trailers for
AI-generated assistance. Use the word `this` only as part of `This commit`.

Before committing, check:

```bash
git status --short
git diff --stat
```

Do not commit editor swap files, downloaded source corpora, generated caches, or
temporary review TSVs.
