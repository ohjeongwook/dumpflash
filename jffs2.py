# pylint: disable=invalid-name
# pylint: disable=line-too-long
from optparse import OptionParser
import pprint
import os
import struct
import sys
import time
import flashfile
import flashdevice
import uboot
import ecc

class Util:
    def __init__(self, flash_image_io):
        self.FlashImageIO = flash_image_io

    def find_blocks(self):
        #bad_blocks = {}
        minimum_pageno = -1
        maximum_pageno = -1
        last_jffs2_page = -1

        print('Find JFFS2: page count: 0x%x' % (self.FlashImageIO.SrcImage.PageCount))
        for pageno in range(0, self.FlashImageIO.SrcImage.PageCount, self.FlashImageIO.SrcImage.PagePerBlock):
            oob = self.FlashImageIO.SrcImage.read_oob(pageno)

            if oob[8:] == b'\x85\x19\x03\x20\x08\x00\x00\x00':
                print('JFFS2 block found:', pageno, pageno-last_jffs2_page)
                last_jffs2_page = pageno

                if minimum_pageno == -1:
                    minimum_pageno = pageno
                maximum_pageno = pageno
            elif oob[0:3] == b'\xff\xff\xff':
                print('blank page')
            else:
                print('OOB: ', pageno, pprint.pprint(oob))

        return [minimum_pageno, maximum_pageno]

    def find(self):
        start_block = -1
        end_block = 0
        jffs2_blocks = []

        for block in range(0, self.FlashImageIO.SrcImage.BlockCount, 1):
            ret = self.FlashImageIO.CheckBadBlock(block)

            ret = self.FlashImageIO.CLEAN_BLOCK

            if ret == self.FlashImageIO.CLEAN_BLOCK:
                oob = self.FlashImageIO.SrcImage.read_oob( block * self.FlashImageIO.SrcImage.PagePerBlock)

                if not oob:
                    break

                if oob[8:] == b'\x85\x19\x03\x20\x08\x00\x00\x00' or oob[8:] == b'\x3f\xff\x03\x85\x19\x03\x20\x08':
                    if start_block == -1:
                        start_block = block
                    distance_to_last_block = block - end_block
                    if distance_to_last_block > 10:
                        print('JFFS2 block found: %d ~ %d' % (start_block, block))
                        jffs2_blocks.append([start_block, block])
                        start_block = -1
                    end_block = block

            elif ret == self.FlashImageIO.ERROR:
                break
            else:
                print('Bad block', block)

        if start_block != -1:
            jffs2_blocks.append([start_block, block])
            print('JFFS2 block found: %d ~ %d' % (start_block, block))

        return jffs2_blocks

    def dump(self, name_prefix = ''):
        i = 0
        for (start_block, end_block) in self.FindJFFS2():
            print('Dumping %d JFFS2 block Block: %d - %d ...' % (i, start_block, end_block))
            if name_prefix:
                filename = '%s%.2d.dmp' % (name_prefix, i)
            else:
                filename = 'JFFS2-%.2d.dmp' % i

            self.FlashImageIO.read_pages(
                start_block * self.FlashImageIO.SrcImage.PagePerBlock,
                (end_block+1) * self.FlashImageIO.SrcImage.PagePerBlock,
                remove_oob = True,
                filename = filename,
                seq = self.FlashImageIO.UseSequentialMode)

            i += 1
