# LOPK (Lightweight Operational Progress Kit)

A lightweight and versatile Python library for creating beautiful terminal progress indicators, spinners, countdown timers, and terminal utilities.

## Features

- **ProgressBar**: Customizable progress bars with color support, ETA, and time tracking
- **Spinner**: Animated loading indicators with context manager support
- **CountdownTimer**: Simple countdown timer functionality
- **MultiProgressBar**: Manage multiple progress bars simultaneously
- **Terminal Utilities**: Clear terminal screen, colored text output, and more

## Installation

```bash
pip install lopk
```

### Optional GUI Support

```bash
pip install lopk[gui]
```

## Usage Examples

### Basic Progress Bar

```python
from main.lopk import ProgressBar

pb = ProgressBar(total=100, title="Downloading", color="green")
for i in range(101):
    pb.update(i)
    time.sleep(0.1)
pb.finish()
```

### Spinner

```python
from main.lopk import Spinner

with Spinner("Loading...", spinner_type="dots"):
    # Your long-running task here
    time.sleep(3)
```

### Countdown Timer

```python
from main.lopk import CountdownTimer

timer = CountdownTimer(10, "Time left")
timer.start()
```

## Demo

Run the interactive demo:

```bash
lopk-demo
```

Run the GUI demo:

```bash
lopk-demo-tk
```

## License

GNU General Public License v3.0

## GitHub Repository

https://github.com/l-love-china/lopk
