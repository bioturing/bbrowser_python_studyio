# Walnut

This library is in charge of read/write data of a BBrowser study

## Installation

```bash
python -m pip install git+ssh://git@github.com/bioturing/bbrowser_python_studyio@main#egg=walnut
```

If you use python < 3.8, please also install `typing_extensions`:
```bash
python -m pip install typing_extensions
```

## Getting started

```python
from walnut.study import Study
study = Study("/path/to/your/BBrowser/study")
```