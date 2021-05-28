#!/usr/bin/env python
#
# Apple 1 Integer BASIC Relocator
#
# GENERATE list of lines sith $Ex in them.
#
# Copyright (C) 2021 by Jim McClanahan, W4JBM
#
# Usage: ./a1bmoveg.py
#
# - Name input file a1basic.in
# - Run Generate Process with ./a1bmoveg.py
# - Edit file to delete or comment out lines which
#   are not to be changed
# - Run Modification Process with ./a1movem.py to
#   create a1basic.out
# 

from sys import argv;

fin = open("a1basic.in", 'rt')
fmod = open("a1basic.mod", 'w')


fmod.write('# Apple 1 Integer BASIC Relocator\n')
fmod.write('#\n')
fmod.write('# *=$E000\n')
fmod.write('#\n')

lin = 0

for line in (fin):
    lin = lin + 1
    if '$E' in line:
        fmod.write(str(lin)+'\n')

