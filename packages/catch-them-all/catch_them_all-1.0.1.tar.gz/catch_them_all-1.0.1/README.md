# Catch Them All

[![PyPI version](https://badge.fury.io/py/catch-them-all.svg)](https://pypi.org/project/catch-them-all/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python versions](https://img.shields.io/pypi/pyversions/catch-them-all.svg)](https://pypi.org/project/catch-them-all/)

Not just a traceback formatter — but a universal exception handler.  
A Single `@decorator` that transforms every exception into a structured, multi‑format report

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Import Behavior](#on-import)
- [Usage](#usage)
- [Pokeball Decorator](#pokeball-decorator)

- [PokedexReport Object](#pokedexreport-object)

- [Exception Hook](#exception-hook)

- [Style Customization](#style-customization)

- [Public API](#public-api)
- [Notes](#notes)  
- [Contributing](#contributing) 
- [Author](#author) 
- [Licenses](#licenses) 
- [Acknowledgements](#acknowledgements) 

---

## Features

```bash
╭── Features Overview
│
├── Catching & Handling Exceptions
│      ├── @pokeball decorator     : Wrap functions to catch exceptions automatically.
│      ├── PokedexReport           : Structured report object with multiple formats (.show(), .str_format, .to_log(), etc.).
│      ├── on_catch() hook         : Run custom logic (logging, retries, alerts) on catch.
│      ├── log flag                : Optional auto-logging to file.
│      ╰── Scales anywhere         : OS- and framework-agnostic – web apps, CLI tools, scripts, pipelines.
│
╰── Beautiful Traceback Formatting (shared by @pokeball and uncaught exceptions)
       ├── Intelligent summaries   : Auto-extracted from exception docstrings for concise context.
       ├── Structured panels       : Clear layout with visual boundaries.
       ├── Smart color grouping    : Highlighted exceptions, code, unified labels, and matching colors for function ↔ line number  
       ╰── Style class             : Full Rich-powered theme customization.
```



## Installation

---
Install via pip:

```bash
pip install catch-them-all
```





## On Import

---
When you import `catch_them_all`, these behaviours trigger automatically:

1. **Exception scanning**  
   - All imports (and their dependencies) are scanned for exception classes.  
   - A summary registry is built, keyed as `module__name__.exception__name__`, storing names and docstring summaries for use in reports.

2. **Exception hook**  
   - A custom `sys.excepthook` replaces Python’s default traceback, giving clear, structured output right away.  
   - To keep the default traceback, disable the hook:
     ```python
     from catch_them_all import disable_excepthook
     
     disable_excepthook()
     ```



## Usage

---
+ ###  Pokeball

**Description:**  
Wrap functions with `@pokeball` to automatically catch exceptions, format them with your chosen theme, and optionally log the report.

**Example 1:**
+ **Instead of manually adding `try/except` blocks:**
```python
try:
    something()
except Exception as e:
    logger.exception(e)
```


+ **You can simply do this:**

```python
from catch_them_all import pokeball

@pokeball(log="errors.log") 
def something():
    raise RuntimeError

```
- *The `log` flag is optional and writes reports to the specified file.*


**Log file :**

---
![Formatted exception report appended to errors.log file](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/usage-pokeball_errors_log.png)
- Note : *A decorator always adds a frame in the traceback, that why you see `wrapper()` in the Stack, it is the natural behaviour of **Python Decorators***

---
**Example 2:**
+ **Instead of importing custom exceptions and scattering `try/except` blocks:**

```python
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sklearn.exceptions import NotFittedError, ConvergenceWarning

try:
    func_might_raise()
except ConnectionError:
    handling_logic()
```
+ **You can decorate the function with `@pokeball` and pass `handling_logic` `func` to it:**

```python
from catch_them_all import pokeball

@pokeball(on_catch=handling_logic)
def func_might_raise():
    ... # code
```
**+  This eliminates the need to import and manage multiple *Custom* `exception` classes manually**

+  **Keeping error handling *Clean, Centralized, and Easier to Maintain*.**

+  + **`Exception` ➜ Raises ➜ `Pokeball` ➜ Catches ➜ `On_Catch` ➜ Triggers ➜ `User` ➜ Decides.**
---
+ ### Excepthook

**Description:**  
`excepthook` is a custom traceback formatter from `catch_them_all`.  
It is fully customizable, leveraging Rich’s styling and color features to produce clearer, structured tracebacks.



- Automatic setup → styled tracebacks are enabled out of the box.
- Global hook → replaces Python’s default `sys.excepthook`.
- Fully Customisable → via `Style` class.

*More info in  [Exception Hook](#exception-hook) section.*

**Example:**
```python
import catch_them_all

raise RuntimeError("Uncaught exception demo")
```

- **Output: *Fully Styled Traceback*:** 

![Styled traceback for uncaught RuntimeError using catch-them-all custom excepthook](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/usage-excepthook-ex1.png)



---
- **instead of Python's native traceback**

![Standard Python traceback for the same uncaught RuntimeError](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/usage-excepthook-normal_traceback.png)

---






## Pokeball Decorator

---

A simple example using `requests` to demonstrate how exceptions are caught, context is injected, and reports are handled

- **Decorator usage** → wrapping the entry function with `@pokeball`.  
- **Context injection** → enriching the report with runtime variables.  
- **Passing `on_catch`** → supplying a custom handler for caught exceptions.  
- **Programmatic intervention** → retrying or logging based on exception type.


**Example:**

```python

import requests
from catch_them_all import pokeball, rescan_imports


# Import Catch Them All last (after libraries you want scanned)
# or call rescan_imports() explicitly if needed


def re_run():
    print("Retrying request...")
    # user code ...


# Context variables that would normally flow through your integration layer
web_address = "http://nonexistent.example.com"
ip = "192.168.0.42"  # imagine from get_ip()
user_agent = "Mozilla/5.0"  # imagine from get_user_agent()


def on_catch(report, web_address, ip, user_agent):
    # Inject context into the report
    report.inject_context({
        "web_address": web_address,
        "ip": ip,
        "user_agent": user_agent,
    })

    # Show Rich Format traceback
    report.show()

    # Conditional handling
    if report.name == "ConnectionError" and report.module.startswith("requests"):
        re_run()  # handle programmatically
    else:
        report.to_log("errors.log")


@pokeball(on_catch=on_catch, on_catch_args=(web_address, ip, user_agent))
def main():
    # This will raise a requests.exceptions.ConnectionError
    requests.get(web_address)


if __name__ == "__main__":
    obj = main()
    # If no exception was raised, obj is the normal return value.
    # If exception was caught, obj is a PokedexReport instance.

```
**Note:** These Exceptions are excluded:

- `KeyboardInterrupt`  `SystemExit`  `GeneratorExit`  and`MemoryError`  as these are **Critical System Exceptions** that must propagate.
- `SyntaxError`, `TabError`, and `IndentationError`, which occur at parse time before runtime.


**Note:** 
- *The ~12‑second delay observed in the `@pokeball` example is due to `requests` trying to resolve a non‑existent address. It’s <u>**not**</u> related to `catch_them_all` itself.*

---
**IDE Output when an `Exception` is raised:**
- Dual Exception Panel for Convenience.
- User Injected Context Panel
- Indented Stack Frames

![Rich formatted report in console with injected context, stack trace, and retry message](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/pokebal-advanced-usage-cta-output.png)

---
**Instead of Python's native traceback:**
![Default Python traceback showing full requests exception chain](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/pokebal-advanced-usage-traceback-output-ex.png)



---
**Note:** *Use `.str_format` for plain, CLI‑friendly output without Rich color codes. it's especially useful when Rich colors aren't supported.*


```python
# Show Str Format traceback
print(report.str_format)
```

**CLI output :**
![Plain text exception report using .str_format, suitable for CLI and logs](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/pokebal-advanced-usage-cli-output.png)

---

## PokedexReport Object

---
*The `PokedexReport` object is created whenever an exception is caught.  
It unifies error details, context, and multiple output formats into a single structure,  
making it easy to inspect, log, or display exceptions programmatically.*

```python
╭── PokedexReport Instance:
│
├── Attributes:
│      ├── name          : Exception class name (e.g., "ConnectionError"). ─────────────────────╮
│      ├── module        : Module where the exception is defined (e.g., "requests.exceptions")  │
│      ├── msg           : Exception message / string representation.                           │
│      ├── summary       : One-line human-readable summary from the registry.                   │
│      ├── frames        : List of distilled stack frame dicts.(e.g., line_no, file...).        ├──{Error Info}
│      ├── timestamp     : ISO timestamp when the exception occurred.                           │
│      ├── caused_by     : Chain of causing exceptions (if any).                                │
│      ├── user_context  : User-provided context (e.g., user_id, request data). ────────────────╯
│      │
│      ├── formatted_object : Internal Formatter instance for rendering. ──────────────────╮
│      │        ├── header        : Exception box (summary + metadata).                    ├──{Formatter components}
│      │        ├── frames        : Stack trace frames.                                    │
│      │        └── context_panel : Injected user context. ────────────────────────────────╯
│      │        (In case a user requires specific component)
│      │
│      ├── json_format   : Cached dict representation. ───────────────────────────────────╮
│      ├── log_format    : Plain-text version without footer, suitable for logs.          ├──{Output formats}
│      ├── rich_format   : Rich object for styled terminal display.                       │
│      ╰── str_format    : Plain-text CLI-friendly version. ──────────────────────────────╯
│
├── Methods:
│      ├── .to_dict()          : Return attributes as a Python dict. ──────────────────────╮
│      ├── .to_log(path)       : Append plain-text report to a log file.                   │
│      ├── .to_json(path=None) : Serialize to JSON string, or write to file if path given. ├──{Report methods}
│      ├── .show()             : Render rich report to console.                            │
│      ╰── .inject_context(ctx): Add user-defined context dictionary. ─────────────────────╯
│
╰──────────────────────────────────────────────────────────────────────────────────────────╯
```



---

## Exception Hook:


---

By default, `catch_them_all` installs its custom `sys.excepthook`, so uncaught exceptions are automatically formatted with the same styled traceback used by `@pokeball`.

- Automatic setup → styled tracebacks are enabled out of the box.
- Global hook → replaces Python’s default `sys.excepthook`.
- Styled output → applies your configured `Style` to uncaught exceptions.
- Persistent theme → if you’ve set a global style or exported one.
- disable_excepthook() → restore Python’s default hook.

**Disabling Excepthook** :

```python
from catch_them_all import disable_excepthook, Style, set_global_style

# excepthook is enabled by default, but you can disable it:
disable_excepthook()   # back to Python's default
```

**Changing Exception Hook Theme:**
```python
from catch_them_all import Style, set_global_style

# customize style
style = Style(header_border="dark_cyan",
              header_message="dark_slate_gray3",
              stack_border="deep_sky_blue3",
              )
# trigger an uncaught exception
raise RuntimeError("Uncaught exception demo")
```
**Note:** *You can use `Style.colors()` and `Style.styles()` to print and return a list of **Rich styles** and **colors** to use, or visit* [Rich docs](https://rich.readthedocs.io/en/stable/appendix/colors.html).


**Output:**
![Uncaught RuntimeError with custom dark cyan themed traceback](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/excepthook-change-theme-ex-1.png)



---
## Style Customization

---

Customizing traceback output with the `Style` class:

- Full customization → adjust the formatted traceback exactly as you like.
- Rich compatibility → pass any values supported by Rich `TextStyle`.
- Granular control → override a single attribute or multiple at once.
- Shared usage → applies to both `excepthook` and `@pokeball` formatted tracebacks.

```python
╭── Style Instance
│
├── Attributes:
│      ├── labels   : Style for metadata labels (e.g. "message:", "code:", "info:").   ├── Generic 
│      ├── muted    : Style for secondary or de‑emphasized text. 
│      │
│      ├── header_border       : Border style for header panel. (e.g., "medium_turquoise") ─────────────────────╮
│      ├── header_exception    : Style for exception type in header. (e.g., "bold yellow")                      │
│      ├── header_timestamp    : Style for timestamp in header. (e.g., "italic #af00ff")                        ├──{Exception Header Propoerties} 
│      ├── header_summary      : Style for summary line. (e.g., "italic rgb(175,0,255)")                        │
│      ├── header_message      : Style for message label.                                                       │
│      ├── header_cause        : Style for cause label. ────────────────────────────────────────────────────────╯
│      │
│      ├── stack_indent               : Indentation spaces per frame level (0–6).─────────────────────╮
│      ├── stack_border               : Border style for frame panels.                                ├──{Traceceback Stack Properties} 
│      ├── stack_func_and_line_no     : Style for function name + line number.                        │
│      ├── stack_file_path            : Style for file path. ─────────────────────────────────────────╯
│      │  
│      ├── context_border : Border style for user context panel.────────────────────────────────────────╮
│      ├── context_keys   : Style for user context Dict keys.                                           ├──{User Injected Context Properties}
│      ╰── context_values : Style for user context Dict values.─────────────────────────────────────────╯
│
├── Methods:
│      ├── styles()       : Return list of available Rich text styles.
│      ├── colors()       : Return list of available Rich colors.                                           
│      ├── export_style() : Export current Style to JSON file.
│      ├── load_style()   : Load Style from JSON file or defaults.
│      ╰── to_dict()      : Serialize Style instance to dictionary.
│
╰─────────────────────────────────────────────────────────────────╯
```

**Changing Theme:**

```python
from catch_them_all import Style, set_global_style

# build style
custom_style = Style(
    header_border="red",
    header_exception="red on grey7",
    header_timestamp="light_cyan3",
    stack_border="navajo_white3",
    stack_func_and_line_no="grey63",
    stack_code="medium_purple2 on grey19"
)

# set style globally
set_global_style(custom_style)

# or save it — next time you use catch_them_all, it will load automatically
custom_style.export_style()  # if no path is provided, saves to ~/.catch_them_all/style.json

def demo_function():
    try:
        # Inner exception
        raise TypeError("TypeError message demo.")
    except TypeError as inner:
        try:
            # Another nested exception
            raise ValueError("ValueError message demo.") from inner
        except ValueError as outer:
            # Final wrapping to show cause chain
            raise RuntimeError("RuntimeError wrapping ValueError.") from outer

# Call the function to trigger the styled traceback
demo_function()
```
**Output:**
![Chained exception (RuntimeError → ValueError → TypeError) with custom red and gray theme](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/excepthook-change-style.png)

---
**Restoring Default Theme:**

```python
from catch_them_all import restore_default_style

# You simply run 
restore_default_style()
```
**Note :** *`restore_default_style()` exports the default style, which will be loaded automatically on the next run.*

**Output:**
![Chained exception traceback after restoring default catch-them-all theme](https://raw.githubusercontent.com/AnasseGX/catch-them-all/refs/heads/master/docs/excepthook-change-style-default.png)

---
## Public API

---

- `pokeball` → decorator for catching and formatting exceptions.  
- `rescan_imports()` → rescans modules that were imported after *`catch_them_all`*.  
- `Style` → class for customizing traceback appearance.  
- `set_global_style()` → apply a custom style globally.  
- `restore_default_style()` → restore the default theme for `excepthook` and `@pokeball`.
- `disable_excepthook()` → restore Python’s default behavior. 
- `install_excepthook()` → only needed to re‑enable the custom formatter if it was disabled, without re‑importing the module.  

## Contributing

---
This project is maintained as time and resources permit. The community is encouraged to contribute, fork, and modify the code freely. Contributions are always welcome and appreciated.

You are encouraged to:

- Submit pull requests for bug fixes or feature enhancements.  
- Fork the repository and adapt it to suit your needs.  
- There are no strict guidelines or requirements for contributing.  
- This project is a collaborative effort for the benefit of the community.  

Contributions are appreciated, though reviews may be slow. With limited maintainer availability, pull requests might remain open for an extended period before approval.


### Publishing to PyPI

---
This project is published on PyPI as `catch_them_all`.  
If you contribute a significant feature and would like to publish it, please request to be added as a maintainer on PyPI by opening an issue.  
Alternatively, feel free to fork this project and publish your version independently.

## Author
Created by [Anasse Gassab](https://github.com/AnasseGX).

## Licenses

---
- `catch_them_all` is licensed under the MIT License – see the [LICENSE](https://github.com/AnasseGX/catch_them_all/blob/master/LICENSE.txt) file for details.
- `Rich` is licensed under the MIT license. See [Rich License](https://github.com/Textualize/rich/blob/master/LICENSE) for details.

## Acknowledgements

---

- This project uses the [Rich](https://pypi.org/project/rich/) library for advanced text formatting and styling.

- ***Thanks to the Python community for the awesome libraries like  `rich`.***
- ***Created to make debugging less painful and more fun — saving developers time on boilerplate and ugly tracebacks, with a Pokémon twist, for the whole community to enjoy.***
