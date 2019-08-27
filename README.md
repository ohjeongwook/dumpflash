# DumpFlash
DumpFlash is a tool to retrieve and write Flash data to the physical NAND Flash memory or virtual image file. Various operations like ECC check and on-image pattern recognition, extraction and rewriting for u-Boot bootloader and JFFS2 file system are supported.

## Prerequisites

### PyUSB

### libusb-1.0
http://zadig.akeo.ie/

### pyftdi 0.13.x version (0.2x.y is Python 3+ only!)
Use one of the following options.
* Install from source https://github.com/eblot/pyftdi
* ```pip install pyftdi==0.13.4``` - latest as of 2017-09-13


## Documentations
For more details, please read following:

   * https://www.blackhat.com/docs/us-14/materials/us-14-Oh-Reverse-Engineering-Flash-Memory-For-Fun-And-Benefit-WP.pdf
   * https://www.blackhat.com/docs/us-14/materials/us-14-Oh-Reverse-Engineering-Flash-Memory-For-Fun-And-Benefit.pdf
   * http://recon.cx/2014/slides/Reverse%20Engineering%20Flash%20Memory%20for%20Fun%20And%20Benefit.pdf
   * Black Hat USA 2014 https://www.youtube.com/watch?v=E8BSnS4-Kpw
   * Recon 2014 https://www.youtube.com/watch?v=nTPfKT61730
   * Updated by O.Kleinecke in March/April 2015 to improve LP-NAND-Chip support.
   * KNOWN ISSUES : TODO : Add (cleaner!?) OOB/ECC Support for LP-Devices.
   * TODO : Add create/read BBT functions
   * Investigate FTDI/Code based malwritten/malread bytes (byte mismatch for read/write after chip erase every 256/256+1/256+2 bytes)

## LICENSE
Copyright (c) 2014, Jeong Wook Oh
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
   * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
   * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
   * Neither the name of the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

