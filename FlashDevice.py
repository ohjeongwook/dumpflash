"""TODO"""
# pylint: disable=invalid-name
# pylint: disable=line-too-long
from array import array as Array
import time
import struct
import sys
import traceback
from pyftdi import ftdi
import ECC

class NandIO:
    ADR_CE = 0x10
    ADR_WP = 0x20
    ADR_CL = 0x40
    ADR_AL = 0x80

    NAND_CMD_READ0 = 0
    NAND_CMD_READ1 = 1
    NAND_CMD_RNDOUT = 5
    NAND_CMD_PAGEPROG = 0x10
    NAND_CMD_READOOB = 0x50
    NAND_CMD_ERASE1 = 0x60
    NAND_CMD_STATUS = 0x70
    NAND_CMD_STATUS_MULTI = 0x71
    NAND_CMD_SEQIN = 0x80
    NAND_CMD_RNDIN = 0x85
    NAND_CMD_READID = 0x90
    NAND_CMD_ERASE2 = 0xd0
    NAND_CMD_PARAM = 0xec
    NAND_CMD_RESET = 0xff
    NAND_CMD_LOCK = 0x2a
    NAND_CMD_UNLOCK1 = 0x23
    NAND_CMD_UNLOCK2 = 0x24
    NAND_CMD_READSTART = 0x30
    NAND_CMD_RNDOUTSTART = 0xE0
    NAND_CMD_CACHEDPROG = 0x15
    NAND_CMD_ONFI = 0xEC
    NAND_CI_CHIPNR_MSK = 0x03
    NAND_CI_CELLTYPE_MSK = 0x0C
    NAND_CI_CELLTYPE_SHIFT = 2

    NAND_STATUS_FAIL = (1<<0) # HIGH - FAIL,  LOW - PASS
    NAND_STATUS_IDLE = (1<<5) # HIGH - IDLE,  LOW - ACTIVE
    NAND_STATUS_READY = (1<<6) # HIGH - READY, LOW - BUSY
    NAND_STATUS_NOT_PROTECTED = (1<<7) # HIGH - NOT,   LOW - PROTECTED

    LP_Options = 1
    DeviceDescriptions = [
        # name, ID, PageSize, ChipSizeMb, EraseSize, Options, AddrCycles
        ["NAND 1MiB 5V 8-bit",        0x6e, 256, 1, 0x1000, 0, 3],
        ["NAND 2MiB 5V 8-bit",        0x64, 256, 2, 0x1000, 0, 3],
        ["NAND 4MiB 5V 8-bit",        0x6b, 512, 4, 0x2000, 0, 3],
        ["NAND 1MiB 3,3V 8-bit",    0xe8, 256, 1, 0x1000, 0, 3],
        ["NAND 1MiB 3,3V 8-bit",    0xec, 256, 1, 0x1000, 0, 3],
        ["NAND 2MiB 3,3V 8-bit",    0xea, 256, 2, 0x1000, 0, 3],

        ["NAND 4MiB 3,3V 8-bit",    0xe3, 512, 4, 0x2000, 0, 3],
        ["NAND 4MiB 3,3V 8-bit",    0xe5, 512, 4, 0x2000, 0, 3],
        ["NAND 8MiB 3,3V 8-bit",    0xd6, 512, 8, 0x2000, 0, 3],
        ["NAND 8MiB 1,8V 8-bit",    0x39, 512, 8, 0x2000, 0, 3],
        ["NAND 8MiB 3,3V 8-bit",    0xe6, 512, 8, 0x2000, 0, 3],
        ["NAND 16MiB 1,8V 8-bit",    0x33, 512, 16, 0x4000, 0, 3],
        ["NAND 16MiB 3,3V 8-bit",    0x73, 512, 16, 0x4000, 0, 3],
        ["NAND 32MiB 1,8V 8-bit",    0x35, 512, 32, 0x4000, 0, 3],
        ["NAND 32MiB 3,3V 8-bit",    0x75, 512, 32, 0x4000, 0, 3],
        ["NAND 64MiB 1,8V 8-bit",    0x36, 512, 64, 0x4000, 0, 4],
        ["NAND 64MiB 3,3V 8-bit",    0x76, 512, 64, 0x4000, 0, 4],
        ["NAND 128MiB 1,8V 8-bit",    0x78, 512, 128, 0x4000, 0, 3],
        ["NAND 128MiB 1,8V 8-bit",    0x39, 512, 128, 0x4000, 0, 3],
        ["NAND 128MiB 3,3V 8-bit",    0x79, 512, 128, 0x4000, 0, 4],
        ["NAND 256MiB 3,3V 8-bit",    0x71, 512, 256, 0x4000, 0, 4],

        # 512 Megabit
        ["NAND 64MiB 1,8V 8-bit",    0xA2, 0,  64, 0, LP_Options, 4],
        ["NAND 64MiB 1,8V 8-bit",    0xA0, 0,  64, 0, LP_Options, 4],
        ["NAND 64MiB 3,3V 8-bit",    0xF2, 0,  64, 0, LP_Options, 4],
        ["NAND 64MiB 3,3V 8-bit",    0xD0, 0,  64, 0, LP_Options, 4],
        ["NAND 64MiB 3,3V 8-bit",    0xF0, 0,  64, 0, LP_Options, 4],

        # 1 Gigabit
        ["NAND 128MiB 1,8V 8-bit",    0xA1, 0, 128, 0, LP_Options, 4],
        ["NAND 128MiB 3,3V 8-bit",    0xF1, 0, 128, 0, LP_Options, 4],
        ["NAND 128MiB 3,3V 8-bit",    0xD1, 0, 128, 0, LP_Options, 4],

        # 2 Gigabit
        ["NAND 256MiB 1,8V 8-bit",    0xAA, 0, 256, 0, LP_Options, 5],
        ["NAND 256MiB 3,3V 8-bit",    0xDA, 0, 256, 0, LP_Options, 5],

        # 4 Gigabit
        ["NAND 512MiB 1,8V 8-bit",    0xAC, 0, 512, 0, LP_Options, 5],
        ["NAND 512MiB 3,3V 8-bit",    0xDC, 0, 512, 0, LP_Options, 5],

        # 8 Gigabit
        ["NAND 1GiB 1,8V 8-bit",    0xA3, 0, 1024, 0, LP_Options, 5],
        ["NAND 1GiB 3,3V 8-bit",    0xD3, 0, 1024, 0, LP_Options, 5],

        # 16 Gigabit
        ["NAND 2GiB 1,8V 8-bit",    0xA5, 0, 2048, 0, LP_Options, 5],
        ["NAND 2GiB 3,3V 8-bit",    0xD5, 0, 2048, 0, LP_Options, 5],

        # 32 Gigabit
        ["NAND 4GiB 1,8V 8-bit",    0xA7, 0, 4096, 0, LP_Options, 5],
        ["NAND 4GiB 3,3V 8-bit",    0xD7, 0, 4096, 0, LP_Options, 5],
        ["NAND 4GiB 3,3V 8-bit",    0x2C, 0, 4096, 0, LP_Options, 5],

        # 64 Gigabit
        ["NAND 8GiB 1,8V 8-bit",    0xAE, 0, 8192, 0, LP_Options, 5],
        ["NAND 8GiB 3,3V 8-bit",    0xDE, 0, 8192, 0, LP_Options, 5],

        # 128 Gigabit
        ["NAND 16GiB 1,8V 8-bit",    0x1A, 0, 16384, 0, LP_Options, 5],
        ["NAND 16GiB 3,3V 8-bit",    0x3A, 0, 16384, 0, LP_Options, 5],

        # 256 Gigabit
        ["NAND 32GiB 1,8V 8-bit",    0x1C, 0, 32768, 0, LP_Options, 6],
        ["NAND 32GiB 3,3V 8-bit",    0x3C, 0, 32768, 0, LP_Options, 6],

        # 512 Gigabit
        ["NAND 64GiB 1,8V 8-bit",    0x1E, 0, 65536, 0, LP_Options, 6],
        ["NAND 64GiB 3,3V 8-bit",    0x3E, 0, 65536, 0, LP_Options, 6],

    ]

    Debug = 0
    Slow = False
    PageSize = 0
    OOBSize = 0
    PageCount = 0
    BlockCount = 0
    PagePerBlock = 0
    BitsPerCell = 0

    WriteProtect = True
    CheckBadBlock = True
    RemoveOOB = False
    UseSequentialMode = False

    def __init__(self, do_slow = False):
        self.Slow = do_slow
        self.UseAnsi = False
        self.Ftdi = ftdi.Ftdi()
        try:
            self.Ftdi.open(0x0403, 0x6010, interface = 1)
        except:
            traceback.print_exc(file = sys.stdout)
            return

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
        """TODO"""
        return self.Identified

    def SetUseAnsi(self, use_ansi):
        """TODO"""
        self.UseAnsi = use_ansi

    def WaitReady(self):
        """TODO"""
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
        """TODO"""
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= self.ADR_CL
        if al == 1:
            cmd_type |= self.ADR_AL

        cmds += [ftdi.Ftdi.READ_EXTENDED, cmd_type, 0]

        for _ in range(1, count, 1):
            cmds += [ftdi.Ftdi.READ_SHORT, 0]

        cmds.append(ftdi.Ftdi.SEND_IMMEDIATE)
        self.Ftdi.write_data(Array('B', cmds))
        if self.getSlow():
            data = self.Ftdi.read_data_bytes(count*2)
            data = data[0:-1:2]
        else:
            data = self.Ftdi.read_data_bytes(count)
        return data.tobytes()

    def nandWrite(self, cl, al, data):
        """TODO"""
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= self.ADR_CL
        if al == 1:
            cmd_type |= self.ADR_AL
        if not self.WriteProtect:
            cmd_type |= self.ADR_WP

        cmds += [ftdi.Ftdi.WRITE_EXTENDED, cmd_type, 0, ord(data[0])]
        for i in range(1, len(data), 1):
            #if i == 256:
            #    cmds += [Ftdi.WRITE_SHORT, 0, ord(data[i])]
            cmds += [ftdi.Ftdi.WRITE_SHORT, 0, ord(data[i])]
        self.Ftdi.write_data(Array('B', cmds))

    def sendCmd(self, cmd):
        """TODO"""
        self.nandWrite(1, 0, chr(cmd))

    def sendAddr(self, addr, count):
        """TODO"""
        data = ''

        for _ in range(0, count, 1):
            data += chr(addr & 0xff)
            addr = addr>>8

        self.nandWrite(0, 1, data)

    def Status(self):
        """TODO"""
        self.sendCmd(0x70)
        status = self.readFlashData(1)[0]
        return status

    def readFlashData(self, count):
        """TODO"""
        return self.nandRead(0, 0, count)

    def writeData(self, data):
        """TODO"""
        return self.nandWrite(0, 0, data)

    def getSlow(self):
        """TODO"""
        return self.Slow

    def GetID(self):
        """TODO"""
        self.sendCmd(self.NAND_CMD_READID)
        self.sendAddr(0, 1)
        flash_identifiers = self.readFlashData(8)

        self.Identified = False
        self.Name = ''
        self.ID = 0
        self.PageSize = 0
        self.ChipSizeMB = 0
        self.EraseSize = 0
        self.Options = 0
        self.AddrCycles = 0

        for device_description in self.DeviceDescriptions:
            if device_description[1] == flash_identifiers[0]:
                (self.Name, self.ID, self.PageSize, self.ChipSizeMB, self.EraseSize, self.Options, self.AddrCycles) = device_description
                self.Identified = True
                break

        if not self.Identified:
            return

        #Check ONFI
        self.sendCmd(self.NAND_CMD_READID)
        self.sendAddr(0x20, 1)
        onfitmp = self.readFlashData(4)

        onfi = (onfitmp == [0x4F, 0x4E, 0x46, 0x49])

        if onfi:
            self.sendCmd(self.NAND_CMD_ONFI)
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
            self.PageCount = int(self.ChipSizeMB*1024*1024/self.PageSize)
        self.RawPageSize = self.PageSize+self.OOBSize
        self.BlockSize = self.EraseSize
        self.BlockCount = int((self.ChipSizeMB*1024*1024)/self.BlockSize)

        if self.BlockCount <= 0:
            self.PagePerBlock = 0
            self.RawBlockSize = 0
            return False

        self.PagePerBlock = int(self.PageCount/self.BlockCount)
        self.RawBlockSize = self.PagePerBlock*(self.PageSize + self.OOBSize)
        return True

    def GetBitsPerCell(self, cellinfo):
        """TODO"""
        bits = cellinfo & self.NAND_CI_CELLTYPE_MSK
        bits >>= self.NAND_CI_CELLTYPE_SHIFT
        return bits+1

    def DumpInfo(self):
        """TODO"""
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
        """TODO"""
        bad_blocks = {}
#        end_page = self.PageCount

        if self.PageCount%self.PagePerBlock > 0.0:
            self.BlockCount += 1

        curblock = 1
        for block in range(0, self.BlockCount):
            page += self.PagePerBlock
            curblock = curblock + 1
            if self.UseAnsi:
                sys.stdout.write('Checking bad blocks %d Block: %d/%d\n\033[A' % (curblock/self.BlockCount*100.0, curblock, self.BlockCount))
            else:
                sys.stdout.write('Checking bad blocks %d Block: %d/%d\n' % (curblock/self.BlockCount*100.0, curblock, self.BlockCount))
            for pageoff in range(0, 2, 1):
                oob = self.ReadOOB(page+pageoff)

                if oob[5] != b'\xff':
                    print('Bad block found:', block)
                    bad_blocks[page] = 1
                    break
        print('Checked %d blocks and found %d bad blocks' % (block+1, len(bad_blocks)))
        return bad_blocks

    def ReadOOB(self, pageno):
        """TODO"""
        bytes_to_send = []
        if self.Options&self.LP_Options:
            self.sendCmd(self.NAND_CMD_READ0)
            self.sendAddr((pageno<<16), self.AddrCycles)
            self.sendCmd(self.NAND_CMD_READSTART)
            self.WaitReady()
            bytes_to_send += self.readFlashData(self.OOBSize)
        else:
            self.sendCmd(self.NAND_CMD_READOOB)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_send += self.readFlashData(self.OOBSize)

        data = ''

        for ch in bytes_to_send:
            data += chr(ch)
        return data

    def ReadPage(self, pageno, remove_oob = False):
        """TODO"""
        bytes_to_read = bytearray()

        if self.Options&self.LP_Options:
            self.sendCmd(self.NAND_CMD_READ0)
            self.sendAddr(pageno<<16, self.AddrCycles)
            self.sendCmd(self.NAND_CMD_READSTART)
            if self.PageSize > 0x1000:
                length = self.PageSize+self.OOBSize
                while length > 0:
                    read_len = 0x1000
                    if length < 0x1000:
                        read_len = length
                    bytes_to_read += self.readFlashData(read_len)
                    length -= 0x1000
            else:
                bytes_to_read = self.readFlashData(self.PageSize+self.OOBSize)

            #TODO: Implement remove_oob
        else:
            self.sendCmd(self.NAND_CMD_READ0)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_read += self.readFlashData(self.PageSize/2)

            self.sendCmd(self.NAND_CMD_READ1)
            self.WaitReady()
            self.sendAddr(pageno<<8, self.AddrCycles)
            self.WaitReady()
            bytes_to_read += self.readFlashData(self.PageSize/2)

            if not remove_oob:
                self.sendCmd(self.NAND_CMD_READOOB)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                bytes_to_read += self.readFlashData(self.OOBSize)

        return bytes_to_read

    def ReadSeq(self, pageno, remove_oob = False, raw_mode = False):
        """TODO"""
        page = []
        self.sendCmd(self.NAND_CMD_READ0)
        self.WaitReady()
        self.sendAddr(pageno<<8, self.AddrCycles)
        self.WaitReady()

        bad_block = False

        for i in range(0, self.PagePerBlock, 1):
            page_data = self.readFlashData(self.RawPageSize)

            if i in (0, 1):
                if page_data[self.PageSize+5] != 0xff:
                    bad_block = True

            if remove_oob:
                page += page_data[0:self.PageSize]
            else:
                page += page_data

            self.WaitReady()

        self.Ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x1, 0x1]))
        self.Ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x0, 0x1]))

        data = ''

        if bad_block and not raw_mode:
            print('\nSkipping bad block at %d' % (pageno/self.PagePerBlock))
        else:
            for ch in page:
                data += chr(ch)

        return data

    def EraseBlockByPage(self, pageno):
        """TODO"""
        self.WriteProtect = False
        self.sendCmd(self.NAND_CMD_ERASE1)
        self.sendAddr(pageno, self.AddrCycles)
        self.sendCmd(self.NAND_CMD_ERASE2)
        self.WaitReady()
        err = self.Status()
        self.WriteProtect = True

        return err

    def WritePage(self, pageno, data):
        """TODO"""
        err = 0
        self.WriteProtect = False

        if self.Options&self.LP_Options:
            self.sendCmd(self.NAND_CMD_SEQIN)
            self.WaitReady()
            self.sendAddr(pageno<<16, self.AddrCycles)
            self.WaitReady()
            self.writeData(data)
            self.sendCmd(self.NAND_CMD_PAGEPROG)
            self.WaitReady()
        else:
            while 1:
                self.sendCmd(self.NAND_CMD_READ0)
                self.sendCmd(self.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[0:256])
                self.sendCmd(self.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err&self.NAND_STATUS_FAIL:
                    print('Failed to write 1st half of ', pageno, err)
                    continue
                break

            while 1:
                self.sendCmd(self.NAND_CMD_READ1)
                self.sendCmd(self.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[self.PageSize/2:self.PageSize])
                self.sendCmd(self.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err&self.NAND_STATUS_FAIL:
                    print('Failed to write 2nd half of ', pageno, err)
                    continue
                break

            while 1:
                self.sendCmd(self.NAND_CMD_READOOB)
                self.sendCmd(self.NAND_CMD_SEQIN)
                self.WaitReady()
                self.sendAddr(pageno<<8, self.AddrCycles)
                self.WaitReady()
                self.writeData(data[self.PageSize:self.RawPageSize])
                self.sendCmd(self.NAND_CMD_PAGEPROG)
                err = self.Status()
                if err&self.NAND_STATUS_FAIL:
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
        """TODO"""
        fd = open(filename, 'rb')
        fd.seek(offset)
        data = fd.read()

        if start_page == -1:
            start_page = 0

        if end_page == -1:
            end_page = self.PageCount-1

        end_block = end_page/self.PagePerBlock

        if end_page%self.PagePerBlock > 0:
            end_block += 1

        start = time.time()
        ecc = ECC.ECC()

        page = start_page
        block = page/self.PagePerBlock
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
                orig_page_data = data[current_data_offset:current_data_offset+self.PageSize]
                current_data_offset += self.PageSize
                length += len(orig_page_data)
                orig_page_data += (self.PageSize-len(orig_page_data)) * b'\x00'
                (ecc0, ecc1, ecc2) = ecc.CalcECC(orig_page_data)

                oob = struct.pack('BBB', ecc0, ecc1, ecc2) + oob_postfix
                page_data = orig_page_data+oob
            else:
                page_data = data[current_data_offset:current_data_offset+self.RawPageSize]
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
                block = page/self.PagePerBlock
            page += 1

        fd.close()

        print('\nWritten %x bytes / %x byte' % (length, len(data)))

    def Erase(self):
        """TODO"""
        block = 0
        while block < self.BlockCount:
            self.EraseBlockByPage(block * self.PagePerBlock)
            block += 1

    def EraseBlock(self, start_block, end_block):
        """TODO"""
        print('Erasing Block: 0x%x ~ 0x%x' % (start_block, end_block))
        for block in range(start_block, end_block+1, 1):
            print("Erasing block", block)
            self.EraseBlockByPage(block * self.PagePerBlock)
