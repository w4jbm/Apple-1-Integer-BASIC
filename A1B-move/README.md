# Python Tools for A1B Relocation

This is a pair of simple (and far from optimized) Python tools that help you quickly and consistently move Apple 1 Integer BASIC (A1B) from it's normal location at $E000.

At the extremes of relocating approaches, you could fix the source code to automate much of this based on the origin address or, at the other extreme, manually edit things and hope you don't miss anything. This automated tool is designed to offer a middle-ground compromise, mainly because relocating the code isn't something you will likely need to do on a regular basis. With this tool it becomes a five minute process (at most) to facilitate a relocation.

The source should be named `a1basic.in` and you should first run `./a1bmoveg.py`. This will generate a file named `a1basic.mod` that lists the line numbers of all references to $Exxx.

The .mod file can be editted to comment out the lines you do not want to change. This can be a bit of trial and error (but not too much if you study the code). The example in this repository has the appropriate lines commented out.

Next you should edit `./a1bmovem.py` so that Line 36 replaces all occurances of '$E' with the right value. I suggest using multiple of $2000 for relocation. (More about that in a minute.) You can then run this code and it will result in a file named `a1basic.out` that has the addressing modified.

There is one final step...

There is a reference in line 761 where a `LDA #$76` is used followed by an `ROL` command (which has the effect of multiplying it by two resulting in A having a value of $EC). If you have stuck with a multiple of $2000, you just need to take the first hex digit, divide it by two, and replace the first hex digit in the constant.

At this point, you should have a source file that can be assembled and work from the selected location in memory.

I know you are safe moving to multiples of $2000. (I have working relocations to $8000 and $A000.) Because of some of the tricks used there would definatly be problems relocating anything that is not a page boundary. Can you select any page boundary? I'm not sure and would have to do some testing before I could say. (If you try successfully or unsuccessfully to relocate to something that is not a multiple of $2000, I would be interested in hearing your results!)


## The fine print...

Copyright 2021 by Jim McClanahan W4JBM

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
