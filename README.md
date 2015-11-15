## tracemerge.py
### A tool to combine python's [trace](https://docs.python.org/2/library/trace.html) coverage reports

Written in python 2.7 and tested in MacOS X.

```
$ ./tracemerge.py -h
usage: tracemerge.py [-h] file [file ...]

Merge trace coverage reports

positional arguments:
  file        coverage report files to merge

  optional arguments:
    -h, --help  show this help message and exit
```

First of all, collect the coverage data of your python program. Once you have all the cover reports (YOUR_PY_SCRIPT.cover.*), a possible command to invoke the tool could be:
```
$ ls YOUR_PY_SCRIPT.cover.* | xargs ./tracemerge.py > YOUR_PY_SCRIPT.cover
```
