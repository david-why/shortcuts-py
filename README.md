# shortcuts-py

Create iOS shortcuts with Python code.

## Example usage

Save the following file as `number.py` and run it.

```python
from shortcuts_py import *

begin_shortcut()

data = ask_for_input(int, "What's your favorite number?", default=42)
show_result(t('Great! I love ', data, ' too!'))

shortcut = build_shortcut(sign=True)
with open('number.shortcut', 'wb') as f:
    f.write(shortcut)
```
