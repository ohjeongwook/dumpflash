"""TODO"""
# pylint: disable=invalid-name
# pylint: disable=line-too-long
from optparse import OptionParser
import pprint
import os
import struct
import sys
import time
import FlashFile
import FlashDevice
import DumpUBoot
import ECC

class FlashUtil:
    """TODO"""
    def __init__(self, filename = '', page_size = 0x800, oob_size = 0x40, page_per_block = 0x40, slow = False):
        """TODO"""
        self.UseAnsi = False
        self.UseSequentialMode = False
        self.DumpProgress = True
        self.DumpProgressInterval = 1

        if filename:
            self.io = FlashFile.FlashFile(filename, page_size, oob_size, page_per_block)
        else:
            self.io = FlashDevice.NandIO(slow)

    def IsInitialized(self):
        """TODO"""
        return self.io.IsInitialized()

    def SetUseAnsi(self, use_ansi):
        """TODO"""
        self.UseAnsi = use_ansi
        self.io.SetUseAnsi(use_ansi)

    def CheckECC(self, start_page = 0, end_page = -1):
        """TODO"""
        block = 0
        count = 0
        error_count = 0

        if end_page == -1:
            end_page = self.io.PageCount

#        start_block = 0
        end_block = end_page/self.io.PagePerBlock
        if end_page%self.io.PagePerBlock > 0:
            end_block += 1

        ecc = ECC.ECC()
        start = time.time()
        for page in range(0, self.io.PageCount, 1):
            block = page/self.io.PagePerBlock
            if self.DumpProgress:
                current = time.time()
                if current-start > self.DumpProgressInterval:
                    start = current
                    progress = (page-start_page) * 100 / (end_page-start_page)
                    if self.UseAnsi:
                        fmt_str = 'Checking ECC %d%% (Page: %3d/%3d Block: %3d/%3d)\n\033[A'
                    else:
                        fmt_str = 'Checking ECC %d%% (Page: %3d/%3d Block: %3d/%3d)\n'
                    sys.stdout.write(fmt_str % (progress, page, end_page, block, end_block))

            #if self.CheckBadBlock(block) == self.BAD_BLOCK:
            #    print 'Bad Block: %d' % block
            #    print ''

            data = self.io.ReadPage(page)

            if not data:
#                end_of_file = True
                break

            count += 1
            body = data[0:self.io.PageSize]
            oob_ecc0 = ord(data[self.io.PageSize])
            oob_ecc1 = ord(data[self.io.PageSize+1])
            oob_ecc2 = ord(data[self.io.PageSize+2])

            if (oob_ecc0 == 0xff and oob_ecc1 == 0xff and oob_ecc2 == 0xff) or (oob_ecc0 == 0x00 and oob_ecc1 == 0x00 and oob_ecc2 == 0x00):
                continue

            (ecc0, ecc1, ecc2) = ecc.CalcECC(body)

            ecc0_xor = ecc0 ^ oob_ecc0
            ecc1_xor = ecc1 ^ oob_ecc1
            ecc2_xor = ecc2 ^ oob_ecc2

            if ecc0_xor != 0 or ecc1_xor != 0 or ecc2_xor != 0:
                error_count += 1

#                page_in_block = page%self.io.PagePerBlock

                offset = self.io.GetPageOffset(page)
                print('ECC Error (Block: %3d Page: %3d Data Offset: 0x%x OOB Offset: 0x%x)' % (block, page, offset, offset+self.io.PageSize))
                print('  OOB:  0x%.2x 0x%.2x 0x%.2x' % (oob_ecc0, oob_ecc1, oob_ecc2))
                print('  Calc: 0x%.2x 0x%.2x 0x%.2x' % (ecc0, ecc1, ecc2))
                print('  XOR:  0x%.2x 0x%.2x 0x%.2x' % (ecc0 ^ oob_ecc0, ecc1 ^ oob_ecc1, ecc2 ^ oob_ecc2))
                print('')

        print('Checked %d ECC record and found %d errors' % (count, error_count))

    def CheckBadBlockPage(self, oob):
        """TODO"""
        bad_block = False

        if oob[0:3] != b'\xff\xff\xff':
            bad_block = True
            if oob[0x8:] == b'\x85\x19\x03\x20\x08\x00\x00\x00': #JFFS CleanMarker
                bad_block = False

        return bad_block

    CLEAN_BLOCK = 0
    BAD_BLOCK = 1
    ERROR = 2

    def CheckBadBlock(self, block):
        """TODO"""
        for page in range(0, 2, 1):
#            current_page = block * self.io.PagePerBlock + page
            pageno = block * self.io.PagePerBlock + page
            print('pageno(%d) = block(%d) * PagePerBlock(%d) + page(%d)' % (pageno, block, self.io.PagePerBlock, page))
            oob = self.io.ReadOOB(pageno)
            bad_block_marker = oob[6:7]
            if not bad_block_marker:
                return self.ERROR

            if bad_block_marker == b'\xff':
                return self.CLEAN_BLOCK

        return self.BAD_BLOCK

    def CheckBadBlocks(self):
        """TODO"""
        block = 0
        error_count = 0

#        start_block = 0
#        end_page = self.io.PageCount
        for block in range(self.io.BlockCount):
            ret = self.CheckBadBlock(block)

            progress = (block+1)*100.0/self.io.BlockCount
            sys.stdout.write('Checking Bad Blocks %d%% Block: %d/%d at offset 0x%x\n' % (progress, block+1, self.io.BlockCount, (block * self.io.BlockSize)))

            if ret == self.BAD_BLOCK:
                error_count += 1
                print("\nBad Block: %d (at physical offset 0x%x)" % (block+1, (block * self.io.BlockSize)))

            elif ret == self.ERROR:
                break
        print("\nChecked %d blocks and found %d errors" % (block+1, error_count))

    def ReadPages(self, start_page = -1, end_page = -1, remove_oob = False, filename = '', append = False, maximum = 0, seq = False, raw_mode = False):
        """TODO"""
        print('* ReadPages: %d ~ %d' % (start_page, end_page))

        if seq:
            return self.ReadSeqPages(start_page, end_page, remove_oob, filename, append = append, maximum = maximum, raw_mode = raw_mode)

        if filename:
            if append:
                fd = open(filename, 'ab')
            else:
                fd = open(filename, 'wb')
        if start_page == -1:
            start_page = 0

        if end_page == -1:
            end_page = self.io.PageCount

        end_block = int(end_page/self.io.PagePerBlock)
        if end_page%self.io.PagePerBlock:
            end_block += 1

        if start_page == end_page:
            end_page += 1

        whole_data = ''
        length = 0
        start = time.time()
        last_time = time.time()
        for page in range(start_page, end_page, 1):
            data = self.io.ReadPage(page, remove_oob)

            if filename:
                if maximum != 0:
                    if length < maximum:
                        fd.write(data[0:maximum-length])
                    else:
                        break
                else:
                    fd.write(data)
            else:
                whole_data += data

            length += len(data)


            if self.DumpProgress:
                current = time.time()
                if current-last_time > self.DumpProgressInterval:
                    lapsed_time = current-start
                    last_time = current

                    progress = (page-start_page) * 100 / (end_page-start_page)
                    block = page/self.io.PagePerBlock
                    if self.UseAnsi:
                        fmt_str = 'Reading %3d%% Page: %3d/%3d Block: %3d/%3d Speed: %8d bytes/s\n\033[A'
                    else:
                        fmt_str = 'Reading %3d%% Page: %3d/%3d Block: %3d/%3d Speed: %8d bytes/s\n'

                    if lapsed_time > 0:
                        bps = length/lapsed_time
                    else:
                        bps = -1

                    sys.stdout.write(fmt_str % (progress, page, end_page, block, end_block, bps))
        if filename:
            fd.close()

        if maximum != 0:
            return whole_data[0:maximum]
        return whole_data

    def ReadSeqPages(self, start_page = -1, end_page = -1, remove_oob = False, filename = '', append = False, maximum = 0, raw_mode = False):
        """TODO"""
        if filename:
            if append:
                fd = open(filename, 'ab')
            else:
                fd = open(filename, 'wb')
        if start_page == -1:
            start_page = 0

        if end_page == -1:
            end_page = self.io.PageCount

        end_block = end_page/self.io.PagePerBlock
        if end_page%self.io.PagePerBlock:
            end_block += 1

        whole_data = ''
        length = 0
        start = time.time()
        for page in range(start_page, end_page, self.io.PagePerBlock):
            data = self.io.ReadSeq(page, remove_oob, raw_mode)

            if filename:
                if maximum != 0:
                    if length < maximum:
                        fd.write(data[0:maximum-length])
                    else:
                        break
                else:
                    fd.write(data)
            else:
                whole_data += data

            length += len(data)
            current = time.time()

            if self.DumpProgress:
                block = page/self.io.PagePerBlock
                progress = (page-start_page) * 100 / (end_page-start_page)
                lapsed_time = current-start

                if lapsed_time > 0:
                    if self.UseAnsi:
                        sys.stdout.write('Reading %d%% Page: %d/%d Block: %d/%d Speed: %d bytes/s\n\033[A' % (progress, page, end_page, block, end_block, length/(current-start)))
                    else:
                        sys.stdout.write('Reading %d%% Page: %d/%d Block: %d/%d Speed: %d bytes/s\n' % (progress, page, end_page, block, end_block, length/(current-start)))

        if filename:
            fd.close()

        if maximum != 0:
            return whole_data[0:maximum]
        return whole_data

    def AddOOB(self, filename, output_filename, jffs2 = False):
        """TODO"""
        fd = open(filename, 'rb')
        wfd = open(output_filename, "wb")

        current_block_number = 0
        current_output_size = 0
        ecc = ECC.ECC()
        while 1:
            page = fd.read(self.io.PageSize)

            if not page:
                break

            (ecc0, ecc1, ecc2) = ecc.CalcECC(page)

            oob_postfix = b'\xff' * 13

            if current_output_size% self.io.BlockSize == 0:
                if jffs2 and current_block_number%2 == 0:
                    oob_postfix = b'\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00'
                current_block_number += 1

            data = page + struct.pack('BBB', ecc0, ecc1, ecc2) + oob_postfix
            wfd.write(data)
            current_output_size += len(data)

        #Write blank pages
        """
        while size>current_output_size:
            if current_output_size% self.RawBlockSize == 0:
                wfd.write(b"\xff"*0x200+ "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00")
            else:
                wfd.write(b"\xff"*0x210)
            current_output_size += 0x210
        """

        fd.close()
        wfd.close()

    def CopyPages(self, output_filename, start_page = 0, end_page = -1, remove_oob = True):
        """TODO"""
        if start_page == -1:
            start_page = 0

        if end_page == -1:
            end = self.io.BlockSize*self.io.RawPageSize*self.io.PagePerBlock
        else:
            end = end_page * self.io.RawPageSize

        return self.CopyPagesByOffset(output_filename, start_page * self.io.RawPageSize, end, remove_oob)

    def CopyPagesByOffset(self, output_filename, start = 0, end = -1, remove_oob = True):
        """TODO"""
        if start == -1:
            start = 0

        if end == -1:
            end = self.io.RawBlockSize*self.io.BlockCount

        wfd = open(output_filename, 'wb')

        start_block = int(start / self.io.RawBlockSize)
        start_block_offset = start % self.io.RawBlockSize
        start_page = int(start_block_offset / self.io.RawPageSize)
        start_page_offset = start_block_offset % self.io.RawPageSize

        end_block = int(end / self.io.RawBlockSize)
        end_block_offset = end % self.io.RawBlockSize
        end_page = int(end_block_offset / self.io.RawPageSize)
        end_page_offset = end_block_offset % self.io.RawPageSize

        print('Dumping blocks (Block: 0x%x Offset: 0x%x ~  Block: 0x%x Offset: 0x%x)' % (start_block, start_block_offset, end_block, end_block_offset))
        print('0x%x - 0x%x' % (start, end))

        for block in range(start_block, end_block+1, 1):
            ret = self.CheckBadBlock(block)

            if ret == self.CLEAN_BLOCK:
                current_start_page = 0
                current_end_page = self.io.PagePerBlock

                if block == start_block:
                    current_start_page = start_page
                elif block == end_block:
                    current_end_page = end_page+1

                for page in range(current_start_page, current_end_page, 1):
                    data = self.io.ReadPage(block * self.io.PagePerBlock + page)

                    if not remove_oob:
                        write_size = self.io.RawPageSize
                    else:
                        write_size = self.io.PageSize

                    if block == start_block and page == current_start_page and start_page_offset > 0:
                        wfd.write(data[start_page_offset:write_size])

                    elif block == end_block and page == current_end_page-1 and end_page_offset >= 0:
                        wfd.write(data[0:end_page_offset])

                    else:
                        wfd.write(data[0:write_size])

            elif ret == self.ERROR:
                break

            else:
                print("Skipping block %d" % block)

        wfd.close()

    def readData(self, start_page, length, filename = ''):
        """TODO"""
        start_block = start_page / self.io.PagePerBlock
        start_block_page = start_page % self.io.PagePerBlock

        expected_data_length = 0
        block = start_block
        blocks = []
        for _start_page in range(start_block*self.io.PagePerBlock, self.io.PageCount, self.io.PagePerBlock):
            is_bad_block = False
            for pageoff in range(0, 2, 1):
                oob = self.io.ReadOOB(_start_page+pageoff)

                if oob and oob[5] != b'\xff':
                    is_bad_block = True
                    break

            if not is_bad_block:
                if _start_page <= start_page and _start_page <= start_page+self.io.PagePerBlock: #First block
                    expected_data_length += (self.io.PagePerBlock-start_block_page) * self.io.PageSize
                    blocks.append(block)
                else:
                    expected_data_length += self.io.PagePerBlock * self.io.PageSize
                    blocks.append(block)

            if expected_data_length >= length:
                break
            block += 1

        self.DumpProgress = False
        data = ''
        append = False
        maximum = length
        for block in blocks:
            start_page = block * self.io.PagePerBlock
            end_page = (block+1) * self.io.PagePerBlock
            if block == start_block:
                start_page += start_block_page

            data += self.ReadPages(start_page, end_page, True, filename, append = append, maximum = maximum, seq = self.UseSequentialMode)

            maximum -= self.io.PagePerBlock*self.io.PageSize

            if len(data) > length:
                break

            append = True

        self.DumpProgress = True
        return data[0:length]


    def FindUBootImages(self):
        """TODO"""
        print('Finding U-Boot Images')
        block = 0

        while 1:
            ret = self.CheckBadBlock(block)

            if ret == self.BAD_BLOCK:
                pass
            elif ret == self.ERROR:
                break

            magic = self.io.ReadPage(block*self.io.PagePerBlock)[0:4]

            if magic == b'\x27\x05\x19\x56':
                uimage = DumpUBoot.uImage()
                uimage.ParseHeader(self.readData(block*self.io.PagePerBlock, 64))
                block_size = uimage.size / self.io.BlockSize
                print('\nU-Boot Image found at block %d ~ %d (0x%x ~ 0x%x)' % (block, block+block_size, block, block+block_size))
                uimage.DumpHeader()
                print('')

            block += 1

        print("Checked %d blocks" % (block))

    def DumpUBootImages(self):
        """TODO"""
        seq = 0
        for pageno in range(0, self.io.PageCount, self.io.PagePerBlock):
            data = self.io.ReadPage(pageno)

            if data[0:4] == b'\x27\x05\x19\x56':
                print('U-Boot Image found at block 0x%x' % (pageno / self.io.PagePerBlock))
                uimage = DumpUBoot.uImage()
                uimage.ParseHeader(data[0:0x40])
                uimage.DumpHeader()

                output_filename = 'U-Boot-%.2d.dmp' % seq
                seq += 1

                try:
                    os.unlink(output_filename)
                except:
                    pass
                self.readData(pageno, 0x40+uimage.size, output_filename)
                print('')

                uimage = DumpUBoot.uImage()
                uimage.ParseFile(output_filename)
                uimage.Extract()

#    def IsJFFS2Block(self, block):
#        """TODO"""
#        ret = self.CheckBadBlock(block)
#        if ret == self.CLEAN_BLOCK:
#            page = 0
#            block_offset = (block * self.io.RawBlockSize) + (page * self.io.RawPageSize)
#            self.fd.seek(block_offset + self.io.PageSize)
#            oob = self.fd.read(16)
#
#            if not oob:
#                return 0
#
#            if oob[8:] == b'\x85\x19\x03\x20\x08\x00\x00\x00' and oob[0:3] != '\xff\xff\xff':
#                return 2
#
#        elif ret == self.ERROR:
#            return 0
#        return 1

    def FindJFFS2Blocks(self):
        """TODO"""
        #bad_blocks = {}
        minimum_pageno = -1
        maximum_pageno = -1
        last_jffs2_page = -1

        print('Find JFFS2: page count: 0x%x' % (self.io.PageCount))
        for pageno in range(0, self.io.PageCount, self.io.PagePerBlock):
            oob = self.io.ReadOOB(pageno)

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


    def FindJFFS2(self):
        """TODO"""
        start_block = -1
        end_block = 0
        jffs2_blocks = []

        for block in range(0, self.io.BlockCount, 1):
            ret = self.CheckBadBlock(block)
            if ret == self.CLEAN_BLOCK:
                oob = self.io.ReadOOB(block*self.io.PagePerBlock)

                if not oob:
                    break

                if oob[8:] == b'\x85\x19\x03\x20\x08\x00\x00\x00':
                    if start_block == -1:
                        start_block = block
                    distance_to_last_block = block - end_block
                    if distance_to_last_block > 10:
                        print('JFFS2 block found: %d ~ %d' % (start_block, block))
                        jffs2_blocks.append([start_block, block])
                        start_block = -1
                    end_block = block

            elif ret == self.ERROR:
                break
            else:
                print('Bad block', block)

        if start_block != -1:
            jffs2_blocks.append([start_block, block])
            print('JFFS2 block found: %d ~ %d' % (start_block, block))

        return jffs2_blocks

    def DumpJFFS2(self, name_prefix = ''):
        """TODO"""
        i = 0
        for (start_block, end_block) in self.FindJFFS2():
            print('Dumping %d JFFS2 block Block: %d - %d ...' % (i, start_block, end_block))
            if name_prefix:
                filename = '%s%.2d.dmp' % (name_prefix, i)
            else:
                filename = 'JFFS2-%.2d.dmp' % i

            self.ReadPages(start_block*self.io.PagePerBlock, (end_block+1)*self.io.PagePerBlock, remove_oob = True, filename = filename, seq = self.UseSequentialMode)
            i += 1

if __name__ == '__main__':
    f = sys.argv[1]
    flash_util = FlashUtil(f)
    flash_util.FindUBootImages()
