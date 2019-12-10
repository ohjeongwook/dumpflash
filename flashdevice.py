# pylint: disable=invalid-name
# pylint: disable=line-too-long
from array import array as Array
import time
import struct
import sys
import traceback
from pyftdi import ftdi
import ecc
import flashdevice_defs

class IO:
    def __init__(self, do_slow = False, debug = 0, simulation_mode = False):
        self.Debug = debug
        self.PageSize = 0
        self.OOBSize = 0
        self.PageCount = 0
        self.BlockCount = 0
        self.PagePerBlock = 0
        self.BitsPerCell = 0
        self.WriteProtect = True
        self.CheckBadBlock = True
        self.RemoveOOB = False
        self.UseSequentialMode = False
        self.UseAnsi = False
        self.Slow = do_slow
        self.Identified = False
        self.SimulationMode = simulation_mode

        try:
            self.Ftdi = ftdi.Ftdi()
        except:
            print("Error openging FTDI device")
            self.Ftdi = None

        if self.Ftdi is not None:
            try:
                self.Ftdi.open(0x0403, 0x6010, interface = 1)
            except:
                traceback.print_exc(file = sys.stdout)

            if self.Ftdi.is_connected:
                self.Ftdi.set_bitmode(0, self.Ftdi.BITMODE_MCU)

                if self.Slow:
                    # Clock FTDI chip at 12MHz instead of 60MHz
                    self.Ftdi.write_data(Array('B', [ftdi.Ftdi.ENABLE_CLK_DIV5]))
                else:
                    self.Ftdi.write_data(Array('B', [ftdi.Ftdi.DISABLE_CLK_DIV5]))

                self.Ftdi.set_latency_timer(self.Ftdi.LATENCY_MIN)
                self.Ftdi.purge_buffers()
                self.Ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x0, 0x1]))

        self.WaitReady()
        self.GetID()

    def IsInitialized(self):
        return self.Identified

    def SetUseAnsi(self, use_ansi):
        self.UseAnsi = use_ansi

    def WaitReady(self):
        if self.Ftdi is None or not self.Ftdi.is_connected:
            return

        while 1:
            self.Ftdi.write_data(Array('B', [ftdi.Ftdi.GET_BITS_HIGH]))
            data = self.Ftdi.read_data_bytes(1)
            if not data or len(data) <= 0:
                raise Exception('FTDI device Not ready. Try restarting it.')

            if  data[0] & 2 == 0x2:
                return

            if self.Debug > 0:
                print('Not Ready', data)

        return

    def nandRead(self, cl, al, count):
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= flashdevice_defs.ADR_CL
        if al == 1:
            cmd_type |= flashdevice_defs.ADR_AL

        cmds += [ftdi.Ftdi.READ_EXTENDED, cmd_type, 0]

        for _ in range(1, count, 1):
            cmds += [ftdi.Ftdi.READ_SHORT, 0]

        cmds.append(ftdi.Ftdi.SEND_IMMEDIATE)

        if self.Ftdi is None or not self.Ftdi.is_connected:
            return

        self.Ftdi.write_data(Array('B', cmds))
        if self.getSlow():
            data = self.Ftdi.read_data_bytes(count*2)
            data = data[0:-1:2]
        else:
            data = self.Ftdi.read_data_bytes(count)
        return data.tobytes()

    def nandWrite(self, cl, al, data):
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= flashdevice_defs.ADR_CL
        if al == 1:
            cmd_type |= flashdevice_defs.ADR_AL
        if not self.WriteProtect:
            cmd_type |= flashdevice_defs.ADR_WP

        cmds += [ftdi.Ftdi.WRITE_EXTENDED, cmd_type, 0, ord(data[0])]
        for i in range(1, len(data), 1):
            #if i == 256:
            #    cmds += [Ftdi.WRITE_SHORT, 0, ord(data[i])]
            cmds += [ftdi.Ftdi.WRITE_SHORT, 0, ord(data[i])]

        if self.Ftdi is None or not self.Ftdi.is_connected:
            return

        self.Ftdi.write_data(Array('B', cmds))

    def sendCmd(self, cmd):
        self.nandWrite(1, 0, chr(cmd))

    def sendAddr(self, addr, count):
        data = ''

        for _ in range(0, count, 1):
            data += chr(addr & 0xff)
            addr = addr>>8

        self.nandWrite(0, 1, data)

    def Status(self):
        self.sendCmd(0x70)
        status = self.readFlashData(1)[0]
        return status

    def readFlashData(self, count):
        return self.nandRead(0, 0, count)

    def writeData(self, data):
        return self.nandWrite(0, 0, data)

    def getSlow(self):
        return self.Slow

    def GetID(self):
        self.Name = ''
        self.ID = 0
        self.PageSize = 0
        self.ChipSizeMB = 0
        self.EraseSize = 0
        self.Options = 0
        self.AddrCycles = 0

        self.sendCmd(flashdevice_defs.NAND_CMD_READID)
        self.sendAddr(0, 1)
        flash_identifiers = self.readFlashData(8)

        if not flash_identifiers:
            return False

        for device_description in flashdevice_defs.DEVICE_DESCRIPTIONS:
            if device_description[1] == flash_identifiers[0]:
                (self.Name, self.ID, self.PageSize, self.ChipSizeMB, self.EraseSize, self.Options, self.AddrCycles) = device_description
                self.Identified = True
                break

        if not self.Identified:
            return False

        #Check ONFI
        self.sendCmd(flashdevice_defs.NAND_CMD_READID)
        self.sendAddr(0x20, 1)
        onfitmp = self.readFlashData(4)

        onfi = (onfitmp == [0x4F, 0x4E, 0x46, 0x49])

        if onfi:
            self.sendCmd(flashdevice_defs.NAND_CMD_ONFI)
            self.sendAddr(0, 1)
            self.WaitReady()
            onfi_data = self.readFlashData(0x100)
            onfi = onfi_data[0:4] == [0x4F, 0x4E, 0x46, 0x49]

        if flash_identifiers[0] == 0x98:
            self.Manufacturer = 'Toshiba'
        elif flash_identifiers[0] == 0xec:
            self.Manufacturer = 'Samsung'
        elif flash_identifiers[0] == 0x04:
            self.Manufacturer = 'Fujitsu'
        elif flash_identifiers[0] == 0x8f:
            self.Manufacturer = 'National Semiconductors'
        elif flash_identifiers[0] == 0x07:
            self.Manufacturer = 'Renesas'
        elif flash_identifiers[0] == 0x20:
            self.Manufacturer = 'ST Micro'
        elif flash_identifiers[0] == 0xad:
            self.Manufacturer = 'Hynix'
        elif flash_identifiers[0] == 0x2c:
            self.Manufacturer = 'Micron'
        elif flash_identifiers[0] == 0x01:
            self.Manufacturer = 'AMD'
        elif flash_identifiers[0] == 0xc2:
            self.Manufacturer = 'Macronix'
        else:
            self.Manufacturer = 'Unknown'

        idstr = ''
        for idbyte in flash_identifiers:
            idstr += "%X" % idbyte
        if idstr[0:4] == idstr[-4:]:
            idstr = idstr[:-4]
            if idstr[0:2] == idstr[-2:]:
                idstr = idstr[:-2]
        self.IDString = idstr
        self.IDLength = int(len(idstr) / 2)
        self.BitsPerCell = self.GetBitsPerCell(flash_identifiers[2])
        if self.PageSize == 0:
            extid = flash_identifiers[3]
            if ((self.IDLength == 6) and (self.Manufacturer == "Samsung") and (self.BitsPerCell > 1)):
                self.Pagesize = 2048 << (extid & 0x03)
                extid >>= 2
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 1:
                    self.OOBSize = 128
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 2:
                    self.OOBSize = 218
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 3:
                    self.OOBSize = 400
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 4:
                    self.OOBSize = 436
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 5:
                    self.OOBSize = 512
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 6:
                    self.OOBSize = 640
                else:
                    self.OOBSize = 1024
                extid >>= 2
                self.EraseSize = (128 * 1024) << (((extid >> 1) & 0x04) | (extid & 0x03))
            elif ((self.IDLength == 6) and (self.Manufacturer == 'Hynix') and (self.BitsPerCell > 1)):
                self.PageSize = 2048 << (extid & 0x03)
                extid >>= 2
                if (((extid >> 2) & 0x04) | (extid & 0x03)) == 0:
                    self.OOBSize = 128
                elif (((extid >> 2) & 0x04) | (extid & 0x03)) == 1:
                    self.OOBSize = 224
                elif (((extid >> 2) & 0x04) | (extid & 0x03)) == 2:
                    self.OOBSize = 448
                elif (((extid >> 2) & 0x04) | (extid & 0x03)) == 3:
                    self.OOBSize = 64
                elif (((extid >> 2) & 0x04) | (extid & 0x03)) == 4:
                    self.OOBSize = 32
                elif (((extid >> 2) & 0x04) | (extid & 0x03)) == 5:
                    self.OOBSize = 16
                else:
                    self.OOBSize = 640
                tmp = ((extid >> 1) & 0x04) | (extid & 0x03)
                if tmp < 0x03:
                    self.EraseSize = (128 * 1024) << tmp
                elif tmp == 0x03:
                    self.EraseSize = 768 * 1024
                else: self.EraseSize = (64 * 1024) << tmp
            else:
                self.PageSize = 1024 << (extid & 0x03)
                extid >>= 2
                self.OOBSize = (8 << (extid & 0x01)) * (self.PageSize >> 9)
                extid >>= 2
                self.EraseSize = (64 * 1024) << (extid & 0x03)
                if ((self.IDLength >= 6) and (self.Manufacturer == "Toshiba") and (self.BitsPerCell > 1) and ((flash_identifiers[5] & 0x7) == 0x6) and not flash_identifiers[4] & 0x80):
                    self.OOBSize = 32 * self.PageSize >> 9
        else:
            self.OOBSize = int(self.PageSize / 32)

        if self.PageSize > 0:
            self.PageCount = int(self.ChipSizeMB*1024*1024 / self.PageSize)
        self.RawPageSize = self.PageSize + self.OOBSize
        self.BlockSize = self.EraseSize
        self.BlockCount = int((self.ChipSizeMB*1024*1024) / self.BlockSize)

        if self.BlockCount <= 0:
            self.PagePerBlock = 0
            self.RawBlockSize = 0
            return False

        self.PagePerBlock = int(self.PageCount / self.BlockCount)
        self.RawBlockSize = self.PagePerBlock*(self.PageSize + self.OOBSize)

        return True

    def GetBitsPerCell(self, cellinfo):
        bits = cellinfo & flashdevice_defs.NAND_CI_CELLTYPE_MSK
        bits >>= flashdevice_defs.NAND_CI_CELLTYPE_SHIFT
        return bits+1

    def DumpInfo(self):
        print('Full ID:\t', self.IDString)
        print('ID Length:\t', self.IDLength)
        print('Name:\t\t', self.Name)
        print('ID:\t\t0x%x' % self.ID)
        print('Page size:\t 0x{0:x}({0:d})'.format(self.PageSize))
        print('OOB size:\t0x{0:x} ({0:d})'.format(self.OOBSize))
        print('Page count:\t0x%x' % self.PageCount)
        print('Size:\t\t0x%x' % self.ChipSizeMB)
        print('Erase size:\t0x%x' % self.EraseSize)
        print('Block count:\t', self.BlockCount)
        print('Options:\t', self.Options)
        print('Address cycle:\t', self.AddrCycles)
        print('Bits per Cell:\t', self.BitsPerCell)
        print('Manufacturer:\t', self.Manufacturer)
        print('')

    def CheckBadBlocks(self):
        bad_blocks = {}
#        end_page = self.PageCount

        if self.PageCount%self.PagePerBlock > 0.0:
            self.BlockCount += 1

        curblock = 1
        for block in range(0, self.BlockCount):
            page += self.PagePerBlock
            curblock = curblock + 1
            if self.UseAnsi:
                sys.stdout.write('Checking bad blocks %d Block: %d/%d\n\033[A' % (curblock / self.BlockCount*100.0, curblock, self.BlockCount))
            else:
                sys.stdout.write('Checking bad blocks %d Block: %d/%d\n' % (curblock / self.BlockCount*100.0, curblock, self.BlockCount))
            for pageoff in range(0, 2, 1):
                oob = self.ReadOOB(page+pageoff)

                if oob[5] != b'\xff':
                    print('Bad block found:', block)
                    bad_blocks[page] = 1
                    break
        print('Checked %d blocks and found %d bad blocks' % (block+1, len(bad_blocks)))
        return bad_blocks

    def ReadOOB(self, pageno):
        bytes_to_send = []
        if self.Options & flashdevice_defs.LP_OPTIONS:
            self.sendCmd(flashdevice_defs.NAND_CMD_READ0)
            self.sendAddr((pageno<<16), self.AddrCycles)
            self.sendCmd(flashdevice_defs.NAND_CMD_READSTART)
            self.WaitReady()
            bytes_to_send += self.readFlashData(self.OOBSize)
        else:
            self.sendCmd(flashdevice_defs.NAND_CMD_READOOB)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_send += self.readFlashData(self.OOBSize)

        data = ''

        for ch in bytes_to_send:
            data += chr(ch)
        return data

    def ReadPage(self, pageno, remove_oob = False):
        bytes_to_read = bytearray()

        if self.Options & flashdevice_defs.LP_OPTIONS:
            self.sendCmd(flashdevice_defs.NAND_CMD_READ0)
            self.sendAddr(pageno<<16, self.AddrCycles)
            self.sendCmd(flashdevice_defs.NAND_CMD_READSTART)
            if self.PageSize > 0x1000:
                length = self.PageSize + self.OOBSize
                while length > 0:
                    read_len = 0x1000
                    if length < 0x1000:
                        read_len = length
                    bytes_to_read += self.readFlashData(read_len)
                    length -= 0x1000
            else:
                bytes_to_read = self.readFlashData(self.PageSize+self.OOBSize)

            #d: Implement remove_oob
        else:
            self.sendCmd(flashdevice_defs.NAND_CMD_READ0)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_read += self.readFlashData(self.PageSize/2)

            self.sendCmd(flashdevice_defs.NAND_CMD_READ1)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_read += self.readFlashData(self.PageSize/2)

            if not remove_oob:
                self.sendCmd(flashdevice_defs.NAND_CMD_READOOB)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                bytes_to_read += self.readFlashData(self.OOBSize)

        return bytes_to_read

    def ReadSeq(self, pageno, remove_oob = False, raw_mode = False):
        page = []
        self.sendCmd(flashdevice_defs.NAND_CMD_READ0)
        self.WaitReady()
        self.sendAddr(pageno<<8, self.AddrCycles)
        self.WaitReady()

        bad_block = False

        for i in range(0, self.PagePerBlock, 1):
            page_data = self.readFlashData(self.RawPageSize)

            if i in (0, 1):
                if page_data[self.PageSize + 5] != 0xff:
                    bad_block = True

            if remove_oob:
                page += page_data[0:self.PageSize]
            else:
                page += page_data

            self.WaitReady()

        if self.Ftdi is None or not self.Ftdi.is_connected:
            return ''

        self.Ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x1, 0x1]))
        self.Ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x0, 0x1]))

        data = ''

        if bad_block and not raw_mode:
            print('\nSkipping bad block at %d' % (pageno / self.PagePerBlock))
        else:
            for ch in page:
                data += chr(ch)

        return data

    def EraseBlockByPage(self, pageno):
        self.WriteProtect = False
        self.sendCmd(flashdevice_defs.NAND_CMD_ERASE1)
        self.sendAddr(pageno, self.AddrCycles)
        self.sendCmd(flashdevice_defs.NAND_CMD_ERASE2)
        self.WaitReady()
        err = self.Status()
        self.WriteProtect = True

        return err

    def WritePage(self, pageno, data):
        err = 0
        self.WriteProtect = False

        if self.Options & flashdevice_defs.LP_OPTIONS:
            self.sendCmd(flashdevice_defs.NAND_CMD_SEQIN)
            self.WaitReady()
            self.sendAddr(pageno<<16, self.AddrCycles)
            self.WaitReady()
            self.writeData(data)
            self.sendCmd(flashdevice_defs.NAND_CMD_PAGEPROG)
            self.WaitReady()
        else:
            while 1:
                self.sendCmd(flashdevice_defs.NAND_CMD_READ0)
                self.sendCmd(flashdevice_defs.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[0:256])
                self.sendCmd(flashdevice_defs.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err & flashdevice_defs.NAND_STATUS_FAIL:
                    print('Failed to write 1st half of ', pageno, err)
                    continue
                break

            while 1:
                self.sendCmd(flashdevice_defs.NAND_CMD_READ1)
                self.sendCmd(flashdevice_defs.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[self.PageSize/2:self.PageSize])
                self.sendCmd(flashdevice_defs.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err & flashdevice_defs.NAND_STATUS_FAIL:
                    print('Failed to write 2nd half of ', pageno, err)
                    continue
                break

            while 1:
                self.sendCmd(flashdevice_defs.NAND_CMD_READOOB)
                self.sendCmd(flashdevice_defs.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[self.PageSize:self.RawPageSize])
                self.sendCmd(flashdevice_defs.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err & flashdevice_defs.NAND_STATUS_FAIL:
                    print('Failed to write OOB of ', pageno, err)
                    continue
                break

        self.WriteProtect = True
        return err

#    def writeBlock(self, block_data):
#        nand_tool.EraseBlockByPage(0) #need to fix
#        page = 0
#        for i in range(0, len(data), self.RawPageSize):
#            nand_tool.WritePage(pageno, data[i:i+self.RawPageSize])
#            page += 1

    def WritePages(self, filename, offset = 0, start_page = -1, end_page = -1, add_oob = False, add_jffs2_eraser_marker = False, raw_mode = False):
        fd = open(filename, 'rb')
        fd.seek(offset)
        data = fd.read()

        if start_page == -1:
            start_page = 0

        if end_page == -1:
            end_page = self.PageCount-1

        end_block = end_page/self.PagePerBlock

        if end_page % self.PagePerBlock > 0:
            end_block += 1

        start = time.time()
        ecc_calculator = ecc.Calculator()

        page = start_page
        block = page / self.PagePerBlock
        current_data_offset = 0
        length = 0

        while page <= end_page and current_data_offset < len(data) and block < self.BlockCount:
            oob_postfix = b'\xff' * 13
            if page%self.PagePerBlock == 0:

                if not raw_mode:
                    bad_block_found = False
                    for pageoff in range(0, 2, 1):
                        oob = self.ReadOOB(page+pageoff)

                        if oob[5] != b'\xff':
                            bad_block_found = True
                            break

                    if bad_block_found:
                        print('\nSkipping bad block at ', block)
                        page += self.PagePerBlock
                        block += 1
                        continue

                if add_jffs2_eraser_marker:
                    oob_postfix = b"\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00"

                self.EraseBlockByPage(page)

            if add_oob:
                orig_page_data = data[current_data_offset:current_data_offset + self.PageSize]
                current_data_offset += self.PageSize
                length += len(orig_page_data)
                orig_page_data += (self.PageSize - len(orig_page_data)) * b'\x00'
                (ecc0, ecc1, ecc2) = ecc_calculator.Calc(orig_page_data)

                oob = struct.pack('BBB', ecc0, ecc1, ecc2) + oob_postfix
                page_data = orig_page_data+oob
            else:
                page_data = data[current_data_offset:current_data_offset + self.RawPageSize]
                current_data_offset += self.RawPageSize
                length += len(page_data)

            if len(page_data) != self.RawPageSize:
                print('Not enough source data')
                break

            current = time.time()

            if end_page == start_page:
                progress = 100
            else:
                progress = (page-start_page) * 100 / (end_page-start_page)

            lapsed_time = current-start

            if lapsed_time > 0:
                if self.UseAnsi:
                    sys.stdout.write('Writing %d%% Page: %d/%d Block: %d/%d Speed: %d bytes/s\n\033[A' % (progress, page, end_page, block, end_block, length/lapsed_time))
                else:
                    sys.stdout.write('Writing %d%% Page: %d/%d Block: %d/%d Speed: %d bytes/s\n' % (progress, page, end_page, block, end_block, length/lapsed_time))
            self.WritePage(page, page_data)

            if page%self.PagePerBlock == 0:
                block = page / self.PagePerBlock
            page += 1

        fd.close()

        print('\nWritten %x bytes / %x byte' % (length, len(data)))

    def Erase(self):
        block = 0
        while block < self.BlockCount:
            self.EraseBlockByPage(block * self.PagePerBlock)
            block += 1

    def EraseBlock(self, start_block, end_block):
        print('Erasing Block: 0x%x ~ 0x%x' % (start_block, end_block))
        for block in range(start_block, end_block+1, 1):
            print("Erasing block", block)
            self.EraseBlockByPage(block * self.PagePerBlock)
