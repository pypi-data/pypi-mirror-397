# Trame

## Concepts

- A **Trame** is a list of **Pieces**, which are themselves made of **Actors**
- The goal is to display information, *Piece by Piece*




## Dev / Install


### Install locally with dev dependencies

```bash
pip3 install -e ".[dev]"
```

**If you don't need dev dependencies, you can install locally without the `.[dev]` suffix :**

```bash
pip3 install -e .
```


### Install

```bash
pip install pca-trame
```

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "pca-trame[dev]==0.0.2"
```


### Try it out !

```bash
python -m trame_tests.sandbox README.md
python -m trame_tests.sandbox README.md --style src/trame_tests/data/obvious-style.css
```

### Install locally

```bash
pip install -e .
```

### Run unit tests

```bash
python -m trame_tests
```

### Sandbox

```bash
python -m trame_tests.sandbox /path/to/markdown.md
python -m trame_tests.sandbox /path/to/markdown.md --port=8000 --style=/path/to/style.css
```


```bash
python -m trame_tests.sandbox src/trame_tests/data/dummy.md
python -m trame_tests.sandbox src/trame_tests/data/rgpd_maths.pm.md --port=8000 --style=/path/to/style.css
```

### Release

```bash
python -m trame_tests
python -m build
python -m twine upload dist/* --verbose
```

### Play with test trame

```python
from kame_tests.get_trame import get_trame_from_test
trame = get_trame_from_test("get_trame_from_test")
```
