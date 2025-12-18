# cif2ice

Version 0.4.1

A small utility to prepare a new ice structure for [GenIce2](https://github.com/vitroid/GenIce) from a CIF file.

(Note: this is not necessary for GenIce3 since the CIF loader is implemented.)

The source can be

1. A `.cif` file.
2. An URL to a `.cif` file.
3. <strike>The three-letter code of Zeolites.</strike>

## Installation

    pip install cif2ice

## Usage

    usage: cif2ice.x [-h] [--rep REP REP REP] [--debug] [--quiet] [--force] name
    
    positional arguments:
      name                  CIF file, Zeolite 3-letter code, or URL
    
    options:
      -h, --help            show this help message and exit
      --rep, -r REP REP REP
                            Repeat the unit cell in x,y, and z directions. [1,1,1]
      --debug, -D           Output debugging info.
      --quiet, -q           Do not output progress messages.
      --force, -f           Force overwrite.


## Example

1.  <strike>(To obtain a Zeolite RHO structure from the Zeolite DB)</strike> It is no longer supported because the URLs at Zeolite DB has been changed. Please download the CIF file by hand and follow the next instruction. Sorry for inconvenience.

        cif2ice MTN

2.  To generate a python module from the `foo.cif` file:

        cif2ice ./MTN.cif

3.  To make the python module from a remote `.cif` file:

        cif2ice http://somewhere/MTN.cif

To use the module with GenIce, make a folder named `lattices/` in the current working directory and put `MTN.py` there.

    genice2 MTN > MTN.gro
