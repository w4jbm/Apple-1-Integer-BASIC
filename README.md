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

So the value -32,768 was not excluded on a whim. The limit of -32,767 is the result of how the unary negation operator interacts with the magnitude of the number in certain situations.


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


## A humourous tale of woe...

I originally started digging into Integer BASIC when I decided I would like to port it to the PAL-1, a clone of the KIM-1 (one of the first single board computers available).

I started with the source and changed the I/O routines, but typing anything at the command line returned an error message. After some thinking, I decided that I might have broken the syntax tables by shifting locations around. If something now crossed a page boundary, that could be problematic for the NMOS version of the 6502 processor.

After further thinking I decided to start with a freshly assembled version and then explicitly patch it to handle I/O. I did this one weekend morning and found that things started to work a bit better than before. Or, at least, not everything I typed threw an error message. But things still did not seem to work proprly.

I took a break for lunch and, when I returned, found I could not duplicate any of my earlier success. Frustrated, I worked at it for a bit longer but eventually packed it in for the day.

But that really bothered me. I couldn't understand how it had partially worked for a while and then, with not changes to the code, suddenly stopped working at all.

Then I remembered that I had started from scratch with the original source code when I decided to use "patches" in a separate source file. That file had the "normal" address for Integer BASIC ($E000). I had assembled it and started to load it into the PAL-1 before I noticed that I had not changed the address to $8000 where I had been working with things in RAM. I made the change, reassembled it, and reloaded it.

And things 'sort of' worked...

I tinkered with it for a while and seemed to be making progress until I broke for lunch.

When I returned, I was back to having anything I typed at the prompth immediately throw an error message!

What had changed? Why did things break?

In the middle of the night, it finally struck me. What happened only makes sense if you know a bit about the original KIM-1.

The original KIM-1 only decoded thinkgs to a 2K block. This was typically viewed as being from $0000 to $1FFF and included RAM, I/O, and ROM. Anyone familar with the 6502 knows that things like the reset vectors go up in the top of memory, but on the KIM this same 2K block "repeats" throughout the memory map. Even the more fully decoded systems like the PAL-1 have that 2K mirrored at the bottom ($0000-$1FFF) and the top ($E000-$FFFF) with everything in between more fully decoded.

So when I accidently assembled and uploade Integer BASIC at $E000, it actualy ended up going into both $0000 and $E000 on the PAL-1.

It set there in memory and was accessible by the static pointers to $Exxx in the code even when I moved the code down to $8000. The bottom three pages were corrupted because that is memory eWoz and Integer BASIC use. And things started getting corrupted from $EFFF down because Integer BASIC stores programs from the top down (and is designed with $0FFF as the top by default). But enough of the tables and subroutines remained in place to make things work more than they would have otherwise.

Things seemed to almost work and then I powered the system off for lunch. After lunch, things that had been working no longer worked because the fragments of code that were previously appearing up in $Exxx had been wiped out.

Although it didn't get me closer to really having Integer BASIC running on the PAL-1, it did make me feel better to understand what had gone wrong.


## Honey I Broke the Assembler

I have used 64TASS as my assembler for 6502 work for years and been very, very happy with it.

After some tweaks to the code, I had A1B to the point where I could type and even run a program--but the listing was always garbled. I spent an entire weekend going through the code of the LIST portion of A1B looking for what might be broke. Several times I restarted tinkering with the code from scratch to make sure it wasn't something I was doing.

I always troubleshoot from the assembler list file... Except this time.

Because I was adding a lot of comments to the code as I would try to decipher what lines and segments of code did, I was looking at the source file.

Finally, in frustration, I decided I would compare the code byte by byte with a hex dump of the ROM. My assumption was that I was messing something up--maybe forcing the wrong address mode or something of that sort.

A quick scan of the assembler output listing stopped me in my tracks. Here is what jumped out at me:

```
.842b	dd 00 02	        CMP     buffer,X
.842e	b0 fa		        BCS     Le42a
.8430	b1 fe		        LDA     (synpag),Y
.8432	29 3f		        AND     #$3F
.8434	4a		        LSR
.8435	d0 b6		        BNE     Le3ed
.8437	bd 00 02	        LDA     buffer,X
.843a	b0 06		        BCS     Le442
.81
.844d	29 80		        AND     #$80
.844f	c9 20		        CMP     #$20
.8451	f0 7a		        BEQ     Le4cd
.8453	b5 a8		        LDA     txtndxstk,X
.8455	85 c8		        STA     text_index
.8457	b5 d1		        LDA     tokndxstk,X
```
Lookin at the source, I couldn't see anything wrong:
```
        CMP     buffer,X
        BCS     Le42a
        LDA     (synpag),Y
        AND     #$3F
        LSR
        BNE     Le3ed
        LDA     buffer,X
        BCS     Le442
        ADC     #$3F
        CMP     #$1A
        BCC     Le4b1
Le442:  ADC     #$4F
        CMP     #$0A
        BCC     Le4b1
Le448:  LDX     synstkdx
Le44a:  INY
        LDA     (synpag),Y
        AND     #$80
        CMP     #$20
        BEQ     Le4cd
        LDA     txtndxstk,X
        STA     text_index
        LDA     tokndxstk,X
        STA     token_index
```
I have not had a chance to try to dig into what was causing this, but using CA65 (which is what Jeff Tranter was using) fixed the issue and everything started working.

I would still like to figure out what is happening here, but just haven't had any spare cycles to spend on it.


## Credits and Recognition

First and most obvious, thanks to Steve 'Woz' Wozniak for creating Apple 1 Integer BASIC in the first place.

For the starting place of my analysis, thanks to Eric Smith and to Jeff Tranter. Without Jeff's source code, I probably would never have considered tinkering with Integer BASIC in the first place.

I have also made use of a disassembly of Apple 2 Integer BASIC by Paul R. Santa-Maria. He further credits William Luebbert's "What's Where in the Apple" and Peeking at Call-A.P.P.L.E., Vol 2, 1979 (pp44-61).

In working on this, I have also made use of the Apple 1js emulator at https://www.scullinsteel.com/apple1/


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
