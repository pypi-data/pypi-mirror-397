# pytex-lib

**pytex-lib** is a Python library for inserting function outputs directly into LaTeX documents.
The `@write_to_latex` decorator automatically writes a function’s return value into a LaTeX
file at a specified keyword location.

This is useful for generating LaTeX reports, papers, or documents that include computed
results without manual editing.

## Example Usage

### Import the Library

```python
from pytex_lib import write_to_latex
````

### Define a Function Using the Decorator

Decorate a function that returns a string:

```python
@write_to_latex
def compute_square(x):
    return f"The square of {x} is {x**2}"
```

### Initial LaTeX Document (`document.tex`)

The output will be inserted **immediately after** the line containing the keyword.

```latex
\documentclass{article}
\begin{document}

Here is the computed result:
% RESULT_PLACEHOLDER

\end{document}
```

### Call the Function

Provide the LaTeX file path and keyword at call time:

```python
compute_square(
    4,
    file_path="document.tex",
    keyword="RESULT_PLACEHOLDER",
)
```

### Updated LaTeX Document

After execution, `document.tex` becomes:

```latex
\documentclass{article}
\begin{document}

Here is the computed result:
% RESULT_PLACEHOLDER
The square of 4 is 16

\end{document}
```

## Installation

```bash
pip install pytex-lib
```
