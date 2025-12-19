<!-- toc:insertAfterHeading=pymarkdownroh -->
<!-- toc:insertAfterHeadingOffset=4 -->

![PyPI - Version](https://img.shields.io/pypi/v/pymarkdownroh)
![PyPI - License](https://img.shields.io/pypi/l/pymarkdownroh)
![PyPI - Downloads](https://img.shields.io/pypi/dm/pymarkdownroh)
[![Publish PyPi](https://github.com/IT-Administrators/pymarkdownroh/actions/workflows/release.yml/badge.svg?branch=main)](https://github.com/IT-Administrators/pymarkdownroh/actions/workflows/release.yml)
[![CI](https://github.com/IT-Administrators/pymarkdownroh/actions/workflows/ci.yaml/badge.svg)](https://github.com/IT-Administrators/pymarkdownroh/actions/workflows/ci.yaml)

# pymarkdownroh

_The pymarkdownroh package contains pyhton modules to create markdown text from python scripts._


## Table of Contents

1. [Introduction](#introduction)
1. [Getting started](#getting-started)
    1. [Prerequisites](#prerequisites)
    1. [Installation](#installation)
1. [How to use](#how-to-use)
    1. [How to import](#how-to-import)
    1. [Using the module](#using-the-module)
1. [Releasing](#releasing)
1. [License](#license)

## Introduction

This package contains different modules which enable users to write markdown text via python objects. It implements all aspects of the official [Markdown Documentation](https://daringfireball.net/projects/markdown/syntax).

The intention of this package is to automatically write markdown files using scripts with templates.

Currently it does not support extended functionality like tables which are often used in github flavored markdown.

## Getting started

### Prerequisites

- Python installed
- Operatingsystem: Linux or Windows, not tested on mac
- IDE like VS Code, if you want to contribute or change the code

### Installation

There are two ways to install this module depending on the way you work and the preinstalled modules:

1. ```pip install pymarkdownroh```
2. ```python -m pip install pymarkdownroh```

## How to use

### How to import

You can import the module in two ways:

```python
    import pymarkdownroh
```

This will import all functions. Even the ones that are not supposed to be used (helper functions).

```python
    from pymarkdownroh import *
```

This will import only the significant functions, meant for using.

### Using the module

Example 1:

```python
# Import all modules from package.
from pymarkdownroh import *

print(create_headline(1, "Document Title"))

# Output:
# 
# "# Document Title"
```

```python
# Import all modules from package.
from pymarkdownroh import *

l = ["Apples", "Bananas", "Cherries"]

print(create_list(l, True, True))

# Output:
#
# 1. [] Apples
# 2. [] Bananas
# 3. [] Cherries
```

## Releasing

Releases are published automatically when a tag is pushed to GitHub.

```Powershell
# Create release variable.
$Release = "x.x.x"
# Create commit.
git commit --allow-empty -m "Release $Release"
# Create tag.
git tag -a $Release -m "Version $Release"
# Push from original.
git push origin --tags
# Push from fork.
git push upstream --tags
```

## License

[MIT](./LICENSE)