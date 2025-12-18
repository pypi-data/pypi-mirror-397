# tkinter_colored_logging_handlers

A Tkinter logging handler that supports ANSI colored output.

![1693492901002](image/README/1693492901002.png)

## Installation

```bash
pip install tkinter_colored_logging_handlers
```

## Usage

```python
from tkinter_colored_logging_handlers import LoggingHandler
import logging
from tkinter import Tk, Text

root = Tk()
text_widget = Text(root)
text_widget.pack()

logger = logging.getLogger(__name__)
handler = LoggingHandler(text_widget)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

logger.info("This is a test message")
root.mainloop()
```

## Development

### Running Tests

```bash
pip install pytest
pytest tests/
```

## License

MIT
