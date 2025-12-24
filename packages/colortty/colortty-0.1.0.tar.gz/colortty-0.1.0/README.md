# colortty

A tiny Python helper to build ANSI escape sequences for terminal styling. It composes colors and text attributes and returns the styled string. Output/printing is up to you.

- English | [中文说明](data/README_zh_CN.md)

## Requirements

- Python 3.11+

## Install

- From PyPI (once published):

```cmd
pip install colortty
```

- From source (in this repository):

```cmd
pip install .
```

## Usage

Two common ways to use it:

- Build and immediately style a string:

```python
from src.colortty import colortty, ColorTTY

print(
    colortty("Hello")
    .set(ColorTTY.Color.red())
    .set(ColorTTY.BackgroundColor.blue())
    .make()
)
# -> "\033[31;44mHello\033[0m"
```

- Build a reusable style and apply it later:

```python
from src.colortty import colortty, ColorTTY

red_text = colortty().set(ColorTTY.Color.red())
print(red_text.make("Error:"))
print(red_text.set(ColorTTY.BackgroundColor.white(lighter=True)).make("Critical"))
```

### More examples

- Bright 8‑color variant:

```python
colortty("Bright red").set(ColorTTY.Color.red(lighter=True)).make()
```

- 256‑color index and truecolor (RGB):

```python
colortty("Indexed").set(ColorTTY.Color.color_256(208)).make()
colortty("RGB").set(ColorTTY.Color.color(255, 128, 64)).make()
```

- Text attributes and background:

```python
from src.colortty import bold, underline, sparking, inverse, invisible

colortty("Styled").set(bold()).set(underline()).set(sparking()).set(inverse()).set(invisible(False)).make()
colortty("Warn").set(ColorTTY.BackgroundColor.yellow(lighter=True)).set(bold()).make()
```

## API (brief)

- `colortty(s: str | None = None) -> Statement`
- `Statement.set(step) -> Statement`
- `Statement.make(s: str | None = None) -> str`
- `ColorTTY.Color`: `.black/.red/.green/.yellow/.blue/.magenta/.cyan/.white(lighter=False)`, `.color_256(index)`, `.color(r,g,b)`
- `ColorTTY.BackgroundColor`: same as `ColorTTY.Color`
- Attributes: `bold(enable=True)`, `underline(enable=True)`, `sparking(enable=True)`, `inverse(enable=True)`, `invisible(enable=True)`

## License

MIT. See [LICENSE](LICENSE).
