[//]: # (Markdown: dillinger.io/ shows a nice example of Markdown commands with a viewer.)
[//]: # (Comments in Markdown: http://stackoverflow.com/questions/4823468/comments-in-markdown)
[//]: # (C++ Project Structure: http://hiltmon.com/blog/2013/07/03/a-simple-c-plus-plus-project-structure/)
[//]: # (C++ Library Creation: http://www.adp-gmbh.ch/cpp/gcc/create_lib.html)

# Tests

Unit and functional tests.

## Requirements

+ Python 3.6.3
+ pip3
+ virtualenvwrapper

## Installation

We recommend installing in a Python virtual envirnment. Various packages of
specific versions will be installed (see requirements.txt or setup.py) that
could break your Python system environment. We use virtualenvwrapper.

```
$ git clone git@github.com:jcasse/fuzzy-inference-engine.git
$ mkvirtualenv blfuzzy
$ pip install ./fuzzy-inference-engine
$ echo "backend: TkAgg" > ~/.matplotlib/matplotlibrc
```

## Usage

```
$ workon blfuzzy
$ cd /path/to/repository/tests
$ pytest
```
