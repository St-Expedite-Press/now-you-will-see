# Texgraph — Markdown-to-LuaLaTeX Poetry Collection Builder

# ---------------------------------------------------------------------------
# Python interpreter — .venv/bin/python on Unix, .venv/Scripts/python on Windows
# ---------------------------------------------------------------------------
ifdef WINDIR
    PYTHON := .venv/Scripts/python
    PIP    := .venv/Scripts/pip
    RUFF   := .venv/Scripts/ruff
    MYPY   := .venv/Scripts/mypy
    PYTEST := .venv/Scripts/pytest
    TEXGRAPH := .venv/Scripts/texgraph
else
    PYTHON := .venv/bin/python
    PIP    := .venv/bin/pip
    RUFF   := .venv/bin/ruff
    MYPY   := .venv/bin/mypy
    PYTEST := .venv/bin/pytest
    TEXGRAPH := .venv/bin/texgraph
endif

.PHONY: install build watch studio clean clean-all lint test

# ---------------------------------------------------------------------------
# install: create project venv and install texgraph + studio backend deps
# ---------------------------------------------------------------------------
install:
	python -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	$(PIP) install -r machinery/studio/requirements-studio.txt

# ---------------------------------------------------------------------------
# build: compile the collection to PDF via LuaLaTeX
# ---------------------------------------------------------------------------
build:
	$(TEXGRAPH) build

# ---------------------------------------------------------------------------
# watch: rebuild on content changes
# ---------------------------------------------------------------------------
watch:
	$(TEXGRAPH) watch

# ---------------------------------------------------------------------------
# studio: launch Texgraph Studio (FastAPI + opens browser)
# ---------------------------------------------------------------------------
studio:
	$(TEXGRAPH) studio

# ---------------------------------------------------------------------------
# clean: remove generated TeX and PDF files but keep directory structure
# ---------------------------------------------------------------------------
clean:
	$(PYTHON) -c "import shutil, glob; [shutil.rmtree(p, ignore_errors=True) or None for p in glob.glob('output/tex/*') + glob.glob('output/pdf/*')]"

# ---------------------------------------------------------------------------
# clean-all: remove virtual environment and entire output directory
# ---------------------------------------------------------------------------
clean-all:
	$(PYTHON) -c "import shutil; shutil.rmtree('.venv', ignore_errors=True); shutil.rmtree('output', ignore_errors=True)"

# ---------------------------------------------------------------------------
# lint: run ruff (style/lint) and mypy (type checking)
# ---------------------------------------------------------------------------
lint:
	$(RUFF) check .
	$(MYPY) machinery/src/

# ---------------------------------------------------------------------------
# test: run the test suite
# ---------------------------------------------------------------------------
test:
	$(PYTEST) machinery/tests/ -v
