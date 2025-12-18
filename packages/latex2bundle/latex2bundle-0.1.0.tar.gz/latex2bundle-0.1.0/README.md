# LaTeX2Bundle

![LaTeX2Bundle banner](assets/banner.svg)

**LaTeX2Bundle** packages a LaTeX project into a single ZIP archive.
It resolves `\\input{}` and `\\include{}`, collects figures and auxiliary files (e.g. `.bib`, `.cls`), optionally reduces bibliographies to cited entries, and produces a ready-to-share bundle.

---

## Features

* Resolves `\\input{}` and `\\include{}` directives
* Copies figures and auxiliary files into a self-contained directory
* Optionally reduces `.bib` files to only cited entries
* Optionally renames figures for portability
* Produces a single ZIP archive

---

## Usage

```bash
latex2bundle path/to/main.tex [options]
```

### Options

* `-c, --copy-files <files...>`
  Include additional files (e.g. `extra.bib myclass.cls`)

* `-t, --target-dir <dir>`
  Output directory (defaults to the main file’s directory)

* `-v`
  Verbose logging

* `--no-reduce-bib`
  Keep full `.bib` files (disable citation-based reduction)

* `--no-rename-figures`
  Keep original figure filenames

---

## Examples

```bash
# Basic: bundle main.tex into ./bundle and create main.zip
latex2bundle path/to/main.tex

# Include extra files with verbose output
latex2bundle path/to/main.tex -c extra.bib myclass.cls -v

# Write bundle to a specific directory
latex2bundle path/to/main.tex -t /tmp/output

# Disable bibliography reduction and figure renaming
latex2bundle path/to/main.tex --no-reduce-bib --no-rename-figures
```

---

## Packaging & Publishing

Build source and wheel:

```bash
python -m pip install --upgrade build twine
python -m build
```

Upload to PyPI (test first):

```bash
python -m twine upload --repository testpypi dist/*
# Production
python -m twine upload dist/*
```

---

## License

See `LICENSE`.
