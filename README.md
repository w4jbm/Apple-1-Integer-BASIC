# Apple-1-Integer-BASIC
I am currently working on a project to port the original version of Apple Integer BASIC to the PAL-1, a clone of the KIM-1 single-board computer. In the process, I have learned a lot about the construction and working of Integer BASIC and wanted to captures some of that for my own reference down the road as well as anyone else who is interested.

As of May 2021, this is still a work in progress.


## Approach to Porting

I originally started with source code Jeff Tranter has in github. I was able to quickly migrate the code to assembler under 64tass (my preferred assembler) and got started making tweaks.

It didn't work...

Admittedly I cludged things together a bit. In some places I had to add code to patch the I/O routines and that created branches that couldn't reach code they previously could. Because of that, I tweaked some branches into using JuMPs instead. Ultimately I could get a command prompt but anything I entered gave me an error.

After some thought, my initial assumption was that I had probably broken some of the indexed addressing by moving the location of things in relation to page boundaries.

For anyone wanting to get Integer BASIC running on another machine and if you have a bit more than 4K of memory to do it in, I suggest starting with the original 4K image and then 'patching' that. I use jumps out of the initialization and I/O routines to some code that immediately follows the Integer BASIC image.

Integer BASIC is a bit 'fragile', not because of how it is built but rather because of how it has been reconstructed. There are portions of the source code where values are loaded into registers without a clear understanding of 'why'. That is just a 'necessary evil' of starting with a disassembly to recreate code.

For example, there is code along the lines of:

```
LDA     text_index
ADC     #$00
STA     pverb
LDA     #$00
TAX
ADC     #$02
STA     pverb+1
LDA     (pverb,X)
```

After a bit of digging, it becomes clearer that this is actually pointing into the buffer area:

```
LDA     text_index      ; Should be $FF
ADC     #<buffer        ; pverb = text_index + buffer ($0200) + C flag
STA     pverb
LDA     #$00
TAX                     ; ...and zero X while we're at it...
ADC     #>buffer        
STA     pverb+1
LDA     (pverb,X)       ; Load what we are pointing at
```       

Figuring out that the $02 is actually pointing to the page where the buffer is helps us understand the context of other code in that area.

To save space, certain registers or flags may go unchanged through significant portions of code and then suddenly used for something. Even a small tweak can break that type of code.

The bottom line is that this is an incredibly compact, interdependent piece of code and that there is still a lot more left to figure out...


## Maximum Negative Value

I have seen comments about the fact that -32767 is the largest negative value Integer BASIC allows, while -32768 can actually be stored in 16 bits.

The is actually a reason for the limit. (And it has nothing to do with wanting to only have one error message referencing 32767 as I've seen speculated in place.)

If you have a statement such as:

```
A=-32767
```
This is actually parsed out with the `-` as a unary operator for negation of the integer value of `32767`. So the limit on negative numbers being entered directly is that the digits are evaluated to their value first and only after that is the unary negation applied. Because of this, we can't parse any input that is larger than 32,767.

Consider the following:

![Negative Numbers](https://github.com/w4jbm/Apple-1-Integer-BASIC/raw/main/images/neg_num.png)

Here we get a glimpse of what is going on. There is no error in line 30 when we calculate a -32,768. Instead the error occurs in line 35 when we try to print the value. You can see that before the error message, Integer BASIC has printed a negative sign. It is only when it goes to try to convert the magnitude (excluding the sign) that it encounters the error (and throws the error message).

If we delete line 35 (the print statement) and run it again, we can see that the value of -32,768 is calculated and there is no error message.

So there the value -32,768 was not excluded on a whim. The limit of -32,767 is the result of how the unary negation operator interacts with the magnitude of the number in certain situations.


## Error Messages

| Pointer | Message |
|:-----:|:--------:
| 00 | ">32767" |
| 06 | "TOO LONG" |
| 0E | "SYNTAX" |
| 14 | "MEM FULL" |
| 1C | "TOO MANY PARENS" |
| 2B | "STRING" |
| 31 | "NO END" |
| 37 | "BAD BRANCH" |
| 41 | ">8 GOSUBS" |
| 4A | "BAD RETURN" |
| 54 | ">8 FORS" |
| 5B | "BAD NEXT" |
| 63 | "STOPPED AT " |
| 6E | "*** " |
| 72 | " ERR.\n" |
| 77 | ">255" |
| 7B | "RANGE" |
| 80 | "DIM" |
| 83 | "STR OVFL" |
| 8B | "\\\n" |
| 8D | "RETYPE LINE\n" |
| 99 | "?" |


## Credits and Recognition

First and most obvious, thanks to Steve 'Woz' Wozniak for creating Apple 1 Integer BASIC in the first place.

For the starting place of my analysis, thanks to Eric Smith and to Jeff Tranter. Without Jeff's source code, I probably would never have considered tinkering with Integer BASIC in the first place.

I have also made use of a disassembly of Apple 2 Integer BASIC by Paul R. Santa-Maria. He further credits William Luebbert's "What's Where in the Apple" and Peeking at Call-A.P.P.L.E., Vol 2, 1979 (pp44-61).


## The fine print...

These files are shared for educational and archival purposes only. Some of this was written by me. Much of it draws heavily on others.

To the extent applicable, material created by me is released under the following license:

Copyright (C) 2021 by Jim McClanahan

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
