# Wry Py

Python bindings for [Wry](https://github.com/tauri-apps/wry) for building desktop apps with webviews.

## Install

```bash
pip install wry_py
```

Linux needs GTK/WebKitGTK:

```bash
# Debian/Ubuntu
sudo apt install libgtk-3-dev libwebkit2gtk-4.1-dev

# Arch
sudo pacman -S gtk3 webkit2gtk-4.1
```

## Quick Start

```python
from wry_py import UiWindow, div, text, button

count = 0

def increment():
    global count
    count += 1
    render()

def render():
    root = (
        div()
        .size_full()
        .v_flex()
        .items_center()
        .justify_center()
        .gap(20)
        .child_builder(text(f"Count: {count}").text_size(32))
        .child_builder(
            button("Increment")
            .padding(10, 20)
            .bg("#3b82f6")
            .text_color("#fff")
            .on_click(increment)
        )
        .build()
    )
    window.set_root(root)

window = UiWindow(title="Counter", width=400, height=300)
render()
window.run()
```

## Examples

```bash
# Counter
python -m examples.counter

# Todo list with dialogs
python -m examples.todo_list

# Hover, focus, and transitions
python -m examples.styles
```

## Development

```bash
git clone https://github.com/Jacob-Walton/wry_py.git
cd wry_py
pip install maturin
maturin develop --release
```

## Docs

<https://jacob-walton.github.io/wry_py/>

## License

MIT
