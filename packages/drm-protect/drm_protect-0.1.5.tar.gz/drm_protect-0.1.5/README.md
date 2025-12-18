# drm-protect

`drm-protect` is a Python module and CLI designed to help developers protect
their Python projects against **tampering** and **unauthorized redistribution**.

> ⚠️ This project is in an early stage. The public API and internal protection
> mechanisms are experimental and may change.

---

## Features (planned)

- Protect individual files or entire package trees
- Configurable “protection profiles” (encryption, obfuscation, signing, etc.)
- Simple CLI (`drm-protect`) and Python API
- Designed to integrate with build pipelines (sdist / wheel generation)

---

## Installation

```bash
pip install drm-protect
```

(Once published to PyPI.)

For development:

```bash
git clone https://github.com/yourname/drm-protect.git
cd drm-protect
pip install -e ".[dev]"
```

---

## Usage

### CLI

```bash
drm-protect path/to/your_project
```

### Python API

```python
from drm_protect import protect_path, ProtectionConfig

config = ProtectionConfig(recursive=True)
targets = protect_path("path/to/your_project", config=config)

for t in targets:
    print("Will protect:", t)
```

---

## Development

Run tests:

```bash
pytest
```

---

## License

MIT
