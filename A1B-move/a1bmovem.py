#!/usr/bin/env python
#
# Apple 1 Integer BASIC Relocator
#
# MODIFY list of lines sith $Ex in them.
#
# Copyright (C) 2021 by Jim McClanahan, W4JBM
#
# Usage: ./a1bmovem.py
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
fmod = open("a1basic.mod", 'rt')
fout = open("a1basic.out", 'w')

src_lines = fin.readlines()

lin = 0

for line in (fmod):
    if not '#' in line:
        plin = int(line)
        print(plin)
        while lin < (plin - 1):
           fout.write(src_lines[lin])
           lin = lin + 1
        fout.write(src_lines[lin].replace('$E', '$A'))
        lin = lin +1

while lin < len(src_lines):
    fout.write(src_lines[lin])
    lin = lin + 1
    
