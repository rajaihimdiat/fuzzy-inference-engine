[//]: # (Markdown: dillinger.io/ shows a nice example of Markdown commands with a viewer.)
[//]: # (Comments in Markdown: http://stackoverflow.com/questions/4823468/comments-in-markdown)
[//]: # (C++ Project Structure: http://hiltmon.com/blog/2013/07/03/a-simple-c-plus-plus-project-structure/)
[//]: # (C++ Library Creation: http://www.adp-gmbh.ch/cpp/gcc/create_lib.html)

# Fuzzy Inference Engine

This fuzzy inference system is based on the Mamdani's fuzzy inference method.
The Mamdani fuzzy inference method is the most commonly used fuzzy methodology.
Fuzzy inference leverages human expertise, in lieu of an accurate mathematical
model, as a set of lingustic rules to compute a decision in an intuitive
manner.

This implementation can:

+ handle an arbitrary number of rules
+ handle rules with an arbitrary number of output variables
+ produce a result even if some input values are missing

Technologies used:

+ Python
+ SciKit-Fuzzy
+ Matplotlib


## Requirements

+ Python 3.6.3
+ pip3
+ virtualenvwrapper


## Installation

We recommend installing in a Python virtual envirnment. Various packages of
specific versions will be installed (see requirements.txt or setup.py) that
could break your Python system environment. We use virtualenvwrapper.

```
$ mkvirtualenv blfuzzy
$ pip install git+https://github.com/jcasse/fuzzy-inference-engine
$ echo "backend: TkAgg" > ~/.matplotlib/matplotlibrc
```

To uninstall, run

```
$ pip uninstall blfuzzy
```


## Usage

```python
import blfuzzy
engine = blfuzzy.FuzzyInferenceEngine(data_dictionary)
engine.run()
```


## Examples

Refer to the examples directory for an example definition of
The Tipping Problem, a classic problem used to showcase fuzzy inference.


## Tests

Refer to the tests directory for instructions.


## Development

Download the source code and install it with the `-e` option:

```
$ git clone git@github.com:jcasse/fuzzy-inference-engine.git
$ mkvirtualenv blfuzzy-dev
$ pip install -e ./fuzzy-inference-engine
```

Now, any change to the code will be reflected when running the code.


## References

+ [Matlab Fuzzy Inference Process](https://www.mathworks.com/help/fuzzy/fuzzy-inference-process.html)
+ [SciKit-Fuzzy The Tipping Problem](http://pythonhosted.org/scikit-fuzzy/auto_examples/plot_tipping_problem.html)
+ [Project Packaging](https://packaging.python.org)
+ [Sample Package](https://github.com/pypa/sampleproject)
+ [Package Setup](https://pythonhosted.org/an_example_pypi_project/setuptools.html)
+ [Licensing](https://choosealicense.com/licenses)
+ [Testing](https://docs.pytest.org/en/latest/goodpractices.html)

[//]: # (http://docs.python-guide.org/en/latest/writing/structure)
[//]: # (https://github.com/kennethreitz/samplemod)
[//]: # (http://the-hitchhikers-guide-to-packaging.readthedocs.io/en/latest/index.html)
[//]: # (https://jeffknupp.com/blog/2013/08/16/open-sourcing-a-python-project-the-right-way)

License
----

[//]: # "A short snippet describing the license (MIT, Apache, etc.)"

[//]: # (http://choosealicense.com/)

Copyright (C) 2017 Juan Casse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

## TODO

* [x] auto generate missing membership functions
* [x] add unit tests using unittest
* [ ] install example data (in setup.py)
