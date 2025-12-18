# openapi-spec-tools

This is a small set of tools to help provide easy to use, flexible tools for display complex objects for a CLI.

## Getting started

The project has been published to PyPi, so you should be able to install it with something like one of the following (depending on how you do Python package management):
```terminal
% pip install rich-objects
% poetry add rich-objects
```

The sections below provide a brief description with links to more examples and details.

## Background

This module extends the [rich](https://github.com/Textualize/rich) module to provide pretty printing of complex data objects. The most common use case is a CLI that displays the json/yaml data that is returned to a CLI client in several different formats.

The easiest way to leverage this library is using the `display()` function. You can provide a `fmt` and `style` to provide different means of displaying the data.


Here are some of the lower level elements:
* `OutputFormat` and `OutputSyle` are enums suitable to use as a CLI argument to support different displays
* `RichTable` class is a thin wrapper derived from `rich.Table`. It contains some default formatting for the tables, since it becomes confusing when tables are nested.
* Added several functions starting with `rich_table_factory()` to create a `RichTable` with appropriate nesting based on the data returned by the data in the object.
* The `console_factory()` is the default means for printing the output, but this just sets the `rich.Console` width.


## Examples

In general, this can be used in any enviroment where CLI output is used. 

### Typer Example

Here's a simple Python example to leverage the new code:
```Python
#!/usr/bin/env python3
from typer import Typer
from rich_objects import OutputFormat, display

DATA = [
    {"name": "sna", "prop1": 1, "prop B": None, "blah": "zay"},
    {
        "name": "foo",
        "prop2": 2,
        "prop B": True,
    },
    {
        "name": "bar",
        1: "inverse",
    },
]

app = Typer()

@app.command()
def print_data(
    output_fmt: OutputFormat = OutputFormat.TEXT,
    output_style: OutputStyle = OutputStyle.ALL,
    indent: int = 2,
):
    data = DATA  # TODO: figure out how to get your data here
    display(data, fmt=output_fmt, style=output_style, indent=indent)

if __name__ == "__main__":
    app()
```

Here's some sample output:
```shell
(.venv) > ./example.py
┏━━━━━━┳━━━━━━━━━━━━━━━━┓
┃ Name ┃ Properties     ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━┩
│ sna  │  prop1   1     │
│      │  prop B  None  │
│      │  blah    zay   │
├──────┼────────────────┤
│ foo  │  prop2   2     │
│      │  prop B  True  │
├──────┼────────────────┤
│ bar  │  1  inverse    │
└──────┴────────────────┘
Found 3 items            
(.venv) > ./example.py --output-fmt json
[
  {
    "name": "sna",
    "prop1": 1,
    "prop B": null,
    "blah": "zay"
  },
  {
    "name": "foo",
    "prop2": 2,
    "prop B": true
  },
  {
    "name": "bar",
    "1": "inverse"
  }
]
(.venv) > ./example.py --output-fmt yaml
- blah: zay
  name: sna
  prop B: null
  prop1: 1
- name: foo
  prop B: true
  prop2: 2
- name: bar
  1: inverse

(.venv) > 
```


## Contributing

This project is just getting going... More development instructions will be added later. If you have any suggestions, please email Rick directly (rickwporter@gmail.com).
