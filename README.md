Půlhodina
=========

One purpose Python tool for formatting text/plain tab-delimited table with
a very custom structure to HTML which is importable to MS Excel and
OpenOffice/LibreOffice Calc.

**The tool is not expected to be useful for anybody except the intended users.**

Enjoy the saved time! 
Michal Turek

[https://github.com/mixalturek/pulhodina](https://github.com/mixalturek/pulhodina)


Usage
-----

```
Pulhodina 1.2
usage: pulhodina.py [-h] [-V] [-m] [-c FILE] [-w FILE] -d DECIMAL_MARK -i DIR
                    -o DIR

Format text/plain tab-delimited table with a very custom structure to HTML
which is importable to MS Excel and OpenOffice/LibreOffice Calc.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show version and exit
  -m, --mugabe          enable mugabe mode (default: False)
  -c FILE, --counter FILE
                        file with counter of saved time (default: None)
  -w FILE, --owners FILE
                        file with tab-delimited accounts and their owners
                        (default: None)
  -d DECIMAL_MARK, --decimal-mark DECIMAL_MARK
                        separator of integer and decimal part in numbers
                        (default: None)
  -i DIR, --in DIR      path to directory with input files (default: None)
  -o DIR, --out DIR     path to directory with output files (default: None)
```
