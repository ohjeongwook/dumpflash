# pylint: disable=invalid-name
# pylint: disable=line-too-long
import struct
import zlib

class uImage:
    HEADER_PACK_STR = '>LLLLLLLBBBB32s'
    MAGIC = 0x27051956

    IH_OS_INVALID = 0
    IH_OS_OPENBSD = 1
    IH_OS_NETBSD = 2
    IH_OS_FREEBSD = 3
    IH_OS_4_4BSD = 4
    IH_OS_LINUX = 5
    IH_OS_SVR4 = 6
    IH_OS_ESIX = 7
    IH_OS_SOLARIS = 8
    IH_OS_IRIX = 9
    IH_OS_SCO = 10
    IH_OS_DELL = 11
    IH_OS_NCR = 12
    IH_OS_LYNXOS = 13
    IH_OS_VXWORKS = 14
    IH_OS_PSOS = 15
    IH_OS_QNX = 16
    IH_OS_U_BOOT = 17
    IH_OS_RTEMS = 18
    IH_OS_ARTOS = 19
    IH_OS_UNITY = 20

    IH_OS_STR_INVALID = 'Invalid OS'
    IH_OS_STR_OPENBSD = 'OpenBSD'
    IH_OS_STR_NETBSD = 'NetBSD'
    IH_OS_STR_FREEBSD = 'FreeBSD'
    IH_OS_STR_4_4BSD = '4.4BSD'
    IH_OS_STR_LINUX = 'Linux'
    IH_OS_STR_SVR4 = 'SVR4'
    IH_OS_STR_ESIX = 'Esix'
    IH_OS_STR_SOLARIS = 'Solaris'
    IH_OS_STR_IRIX = 'Irix'
    IH_OS_STR_SCO = 'SCO'
    IH_OS_STR_DELL = 'Dell'
    IH_OS_STR_NCR = 'NCR'
    IH_OS_STR_LYNXOS = 'LynxOS'
    IH_OS_STR_VXWORKS = 'VxWorks'
    IH_OS_STR_PSOS = 'pSOS'
    IH_OS_STR_QNX = 'QNX'
    IH_OS_STR_U_BOOT = 'Firmware'
    IH_OS_STR_RTEMS = 'RTEMS'
    IH_OS_STR_ARTOS = 'ARTOS'
    IH_OS_STR_UNITY = 'Unity OS'

    IH_CPU_INVALID = 0
    IH_CPU_ALPHA = 1
    IH_CPU_ARM = 2
    IH_CPU_I386 = 3
    IH_CPU_IA64 = 4
    IH_CPU_MIPS = 5
    IH_CPU_MIPS64 = 6
    IH_CPU_PPC = 7
    IH_CPU_S390 = 8
    IH_CPU_SH = 9
    IH_CPU_SPARC = 10
    IH_CPU_SPARC64 = 11
    IH_CPU_M68K = 12
    IH_CPU_NIOS = 13
    IH_CPU_MICROBLAZE = 14
    IH_CPU_NIOS2 = 15
    IH_CPU_BLACKFIN = 16
    IH_CPU_AVR32 = 17

    IH_CPU_STR_INVALID = 'Invalid CPU'
    IH_CPU_STR_ALPHA = 'Alpha'
    IH_CPU_STR_ARM = 'ARM'
    IH_CPU_STR_I386 = 'Intel x86'
    IH_CPU_STR_IA64 = 'IA64'
    IH_CPU_STR_MIPS = 'MIPS'
    IH_CPU_STR_MIPS64 = 'MIPS  64 Bit'
    IH_CPU_STR_PPC = 'PowerPC'
    IH_CPU_STR_S390 = 'IBM S390'
    IH_CPU_STR_SH = 'SuperH'
    IH_CPU_STR_SPARC = 'Sparc'
    IH_CPU_STR_SPARC64 = 'Sparc 64 Bit'
    IH_CPU_STR_M68K = 'M68K'
    IH_CPU_STR_NIOS = 'Nios-32'
    IH_CPU_STR_MICROBLAZE = 'MicroBlaze'
    IH_CPU_STR_NIOS2 = 'Nios-II'
    IH_CPU_STR_BLACKFIN = 'Blackfin'
    IH_CPU_STR_AVR32 = 'AVR32'

    IH_TYPE_INVALID = 0
    IH_TYPE_STANDALONE = 1
    IH_TYPE_KERNEL = 2
    IH_TYPE_RAMDISK = 3
    IH_TYPE_MULTI = 4
    IH_TYPE_FIRMWARE = 5
    IH_TYPE_SCRIPT = 6
    IH_TYPE_FILESYSTEM = 7
    IH_TYPE_FLATDT = 8

    IH_TYPE_STR_INVALID = 'Invalid Image'
    IH_TYPE_STR_STANDALONE = 'Standalone Program'
    IH_TYPE_STR_KERNEL = 'OS Kernel Image'
    IH_TYPE_STR_RAMDISK = 'RAMDisk Image'
    IH_TYPE_STR_MULTI = 'Multi-File Image'
    IH_TYPE_STR_FIRMWARE = 'Firmware Image'
    IH_TYPE_STR_SCRIPT = 'Script file'
    IH_TYPE_STR_FILESYSTEM = 'Filesystem Image (any type)'
    IH_TYPE_STR_FLATDT = 'Binary Flat Device Tree Blob'

    COMP_NONE = 0
    COMP_GZIP = 1
    COMP_BZIP2 = 2

    def __init__(self):
        self.filename = None
        self.magic = None
        self.hcrc = None
        self.time = None
        self.size = None
        self.load = None
        self.ep = None
        self.dcrc = None
        self.os = None
        self.arch = None
        self.type = None
        self.comp = None
        self.name = None

    def get_os_string(self, os):
        if os == self.IH_OS_INVALID:
            return self.IH_OS_STR_INVALID
        if os == self.IH_OS_OPENBSD:
            return self.IH_OS_STR_OPENBSD
        if os == self.IH_OS_NETBSD:
            return self.IH_OS_STR_NETBSD
        if os == self.IH_OS_FREEBSD:
            return self.IH_OS_STR_FREEBSD
        if os == self.IH_OS_4_4BSD:
            return self.IH_OS_STR_4_4BSD
        if os == self.IH_OS_LINUX:
            return self.IH_OS_STR_LINUX
        if os == self.IH_OS_SVR4:
            return self.IH_OS_STR_SVR4
        if os == self.IH_OS_ESIX:
            return self.IH_OS_STR_ESIX
        if os == self.IH_OS_SOLARIS:
            return self.IH_OS_STR_SOLARIS
        if os == self.IH_OS_IRIX:
            return self.IH_OS_STR_IRIX
        if os == self.IH_OS_SCO:
            return self.IH_OS_STR_SCO
        if os == self.IH_OS_DELL:
            return self.IH_OS_STR_DELL
        if os == self.IH_OS_NCR:
            return self.IH_OS_STR_NCR
        if os == self.IH_OS_LYNXOS:
            return self.IH_OS_STR_LYNXOS
        if os == self.IH_OS_VXWORKS:
            return self.IH_OS_STR_VXWORKS
        if os == self.IH_OS_PSOS:
            return self.IH_OS_STR_PSOS
        if os == self.IH_OS_QNX:
            return self.IH_OS_STR_QNX
        if os == self.IH_OS_U_BOOT:
            return self.IH_OS_STR_U_BOOT
        if os == self.IH_OS_RTEMS:
            return self.IH_OS_STR_RTEMS
        if os == self.IH_OS_ARTOS:
            return self.IH_OS_STR_ARTOS
        if os == self.IH_OS_UNITY:
            return self.IH_OS_STR_UNITY
        return ""

    def get_arch_string(self, arch):
        if arch == self.IH_CPU_INVALID:
            return self.IH_CPU_STR_INVALID
        if arch == self.IH_CPU_ALPHA:
            return self.IH_CPU_STR_ALPHA
        if arch == self.IH_CPU_ARM:
            return self.IH_CPU_STR_ARM
        if arch == self.IH_CPU_I386:
            return self.IH_CPU_STR_I386
        if arch == self.IH_CPU_IA64:
            return self.IH_CPU_STR_IA64
        if arch == self.IH_CPU_MIPS:
            return self.IH_CPU_STR_MIPS
        if arch == self.IH_CPU_MIPS64:
            return self.IH_CPU_STR_MIPS64
        if arch == self.IH_CPU_PPC:
            return self.IH_CPU_STR_PPC
        if arch == self.IH_CPU_S390:
            return self.IH_CPU_STR_S390
        if arch == self.IH_CPU_SH:
            return self.IH_CPU_STR_SH
        if arch == self.IH_CPU_SPARC:
            return self.IH_CPU_STR_SPARC
        if arch == self.IH_CPU_SPARC64:
            return self.IH_CPU_STR_SPARC64
        if arch == self.IH_CPU_M68K:
            return self.IH_CPU_STR_M68K
        if arch == self.IH_CPU_NIOS:
            return self.IH_CPU_STR_NIOS
        if arch == self.IH_CPU_MICROBLAZE:
            return self.IH_CPU_STR_MICROBLAZE
        if arch == self.IH_CPU_NIOS2:
            return self.IH_CPU_STR_NIOS2
        if arch == self.IH_CPU_BLACKFIN:
            return self.IH_CPU_STR_BLACKFIN
        if arch == self.IH_CPU_AVR32:
            return self.IH_CPU_STR_AVR32

        return 'Unknown'

    def get_type_string(self, type_string):
        if type_string == self.IH_TYPE_INVALID:
            return self.IH_TYPE_STR_INVALID
        if type_string == self.IH_TYPE_STANDALONE:
            return self.IH_TYPE_STR_STANDALONE
        if type_string == self.IH_TYPE_KERNEL:
            return self.IH_TYPE_STR_KERNEL
        if type_string == self.IH_TYPE_RAMDISK:
            return self.IH_TYPE_STR_RAMDISK
        if type_string == self.IH_TYPE_MULTI:
            return self.IH_TYPE_STR_MULTI
        if type_string == self.IH_TYPE_FIRMWARE:
            return self.IH_TYPE_STR_FIRMWARE
        if type_string == self.IH_TYPE_SCRIPT:
            return self.IH_TYPE_STR_SCRIPT
        if type_string == self.IH_TYPE_FILESYSTEM:
            return self.IH_TYPE_STR_FILESYSTEM
        if type_string == self.IH_TYPE_FLATDT:
            return self.IH_TYPE_STR_FLATDT
        return ''

    def get_comp_string(self, comp):
        if comp == self.COMP_NONE:
            return 'None'
        if comp == self.COMP_GZIP:
            return 'gzip'
        if comp == self.COMP_BZIP2:
            return 'bzip2'
        return None

    def parse_file(self, filename):
        self.filename = filename
        fd = open(self.filename, 'rb')
        header = fd.read(0x40)
        fd.close()

        self.parse_header(header)

    def parse_header(self, header):
        (self.magic, self.hcrc, self.time, self.size, self.load, self.ep, self.dcrc, self.os, self.arch, self.type, self.comp, self.name) = struct.unpack(self.HEADER_PACK_STR, header)

    def dump_header(self):
        print('Magic:\t0x%x'% (self.magic))
        print('HCRC:\t0x%x'% (self.hcrc))
        print('Time:\t0x%x'% (self.time))
        print('Size:\t0x%x'% (self.size))
        print('Load:\t0x%x'% (self.load))
        print('EP:\t0x%x'% (self.ep))
        print('DCRC:\t0x%x'% (self.dcrc))
        print('OS:\t0x%x (%s)'% (self.os, self.get_os_string(self.os)))
        print('Arch:\t0x%x (%s)'% (self.arch, self.get_arch_string(self.arch)))
        print('Type:\t0x%x (%s)'% (self.type, self.get_type_string(self.type)))
        print('Comp:\t0x%x (%s)'% (self.comp, self.get_comp_string(self.comp)))
        print('Name:\t%s'% (self.name))

    def check_crc(self):
        fd = open(self.filename, 'rb')
        header = fd.read(0x40)
        data = fd.read(self.size)
        fd.close()

        print('Read %08X bytes out of %08X' % (len(data), self.size))
        new_header = header[0:4] + struct.pack('L', 0) + header[8:]
        print('%08X' % (zlib.crc32(new_header) & 0xFFFFFFFF))
        print('%08X' % (zlib.crc32(data) & 0xFFFFFFFF))

    def fix_header(self):
        fd = open(self.filename, 'rb')
        header = fd.read(0x40)
        data = fd.read(self.size)
        fd.close()

        print('New length: 0x%08x / Original length: 0x%08x' % (len(data), self.size))

        self.dcrc = zlib.crc32(data)& 0xFFFFFFFF
        print('New DCRC: %08x' % self.dcrc)

#        new_header = header[0:4] + struct.pack("L", 0) + header[8:]
        self.size = len(data)
        self.hcrc = 0
        header = struct.pack(self.HEADER_PACK_STR, self.magic, self.hcrc, self.time, self.size, self.load, self.ep, self.dcrc, self.os, self.arch, self.type, self.comp, self.name)

        self.hcrc = zlib.crc32(header)& 0xFFFFFFFF
        print('New HCRC: %08X' % self.hcrc)

        header = struct.pack(self.HEADER_PACK_STR, self.magic, self.hcrc, self.time, self.size, self.load, self.ep, self.dcrc, self.os, self.arch, self.type, self.comp, self.name)

        fd = open(self.filename, 'rb+')
        fd.write(header)
        fd.close()

    def extract(self):
        seq = 0
        if self.type == self.IH_TYPE_MULTI:
            fd = open(self.filename, 'rb')
            fd.seek(0x40)
            lengths = []
            while 1:
                (length, ) = struct.unpack('>L', fd.read(4))

                if length > 0:
                    print('Found multi image of length 0x%x' % (length))
                    lengths.append(length)
                elif length == 0:
                    break

            for length in lengths:
                data = fd.read(length)

                wfilename = '%s-%.2d' % (self.filename, seq)
                seq += 1
                print('Extracting to %s' % wfilename)
                wfd = open(wfilename, 'wb')
                wfd.write(data)
                wfd.close()

            fd.close()
        else:
            fd = open(self.filename, 'rb')
            fd.seek(0x40)
            data = fd.read(self.size)
            fd.close()

            if self.comp == self.COMP_NONE:
                wfilename = '%s-%.2d' % (self.filename, seq)
                print('Extracting to %s' % wfilename)
                wfd = open(wfilename, 'wb')
                wfd.write(data)
                wfd.close()

    def merge(self, header_file, files, output_filename):
        fd = open(header_file, 'rb')
        header = fd.read(0x40)
        fd.close()

        ofd = open(output_filename, 'wb')
        ofd.write(header)
        ofd.write(b'\x00' * (len(files)+1)*4)

        dcrc = 0
        lengths = []
        for file_ in files:
            fd = open(file_, 'rb')
            data = fd.read()
            fd.close()

            ofd.write(data)

            lengths.append(len(data))
            dcrc = zlib.crc32(data, dcrc)

        ofd.seek(0x40)
        for length in lengths:
            ofd.write(struct.pack('>L', length))
        ofd.close()

        self.parse_file(output_filename)
        self.fix_header()

class Util:
    def __init__(self, flash_image_io):
        self.FlashImageIO = flash_image_io

    def find(self):
        print('Finding U-Boot Images')
        block = 0

        while 1:
            ret = self.FlashImageIO.CheckBadBlock(block)

            if ret == self.FlashImageIO.BAD_BLOCK:
                pass
            elif ret == self.FlashImageIO.ERROR:
                break

            magic = self.FlashImageIO.SrcImage.read_page(block*self.FlashImageIO.SrcImage.PagePerBlock)[0:4]

            if magic == b'\x27\x05\x19\x56':
                uimage = uImage()
                uimage.parse_header(self.FlashImageIO.extract_data(block * self.FlashImageIO.SrcImage.PagePerBlock, 64))
                block_size = uimage.size / self.FlashImageIO.SrcImage.BlockSize
                print('\nU-Boot Image found at block %d ~ %d (0x%x ~ 0x%x)' % (block, block+block_size, block, block+block_size))
                uimage.dump_header()
                print('')

            block += 1

        print("Checked %d blocks" % (block))

    def dump(self):
        seq = 0
        for pageno in range(0, self.FlashImageIO.SrcImage.PageCount, self.FlashImageIO.SrcImage.PagePerBlock):
            data = self.FlashImageIO.SrcImage.read_page(pageno)

            if data[0:4] == b'\x27\x05\x19\x56':
                print('U-Boot Image found at block 0x%x' % (pageno / self.FlashImageIO.SrcImage.PagePerBlock))
                uimage = uImage()
                uimage.parse_header(data[0:0x40])
                uimage.dump_header()

                output_filename = 'U-Boot-%.2d.dmp' % seq
                seq += 1

                try:
                    os.unlink(output_filename)
                except:
                    pass
                self.FlashImageIO.extract_data(pageno, 0x40 + uimage.size, output_filename)
                print('')

                uimage = uImage()
                uimage.parse_file(output_filename)
                uimage.extract()

if __name__ == '__main__':

    from optparse import OptionParser
    parser = OptionParser()

    parser.add_option('-f', action = 'store_true', dest = 'fix_header', default = False)
    parser.add_option('-c', action = 'store_true', dest = 'check_crc', default = False)
    parser.add_option('-e', action = 'store_true', dest = 'extract', default = False)
    parser.add_option('-m', action = 'store_true', dest = 'merge', default = False)
    parser.add_option('-o', '--output_filename', dest = 'output_filename', default = '', 
                      help = 'Set output_filename filename', metavar = 'output_filename')
    parser.add_option('-H', '--header_file', dest = 'header_file', default = '', 
                      help = 'Set header filename', metavar = 'header')

    (options, args) = parser.parse_args()
    f = args[0]

    uimage = uImage()

    if options.fix_header:
        uimage.parse_file(f)
        uimage.dump_header()
        uimage.fix_header()

    elif options.check_crc:
        uimage.parse_file(f)
        uimage.dump_header()
        uimage.check_crc()

    elif options.extract:
        uimage.parse_file(f)
        uimage.dump_header()
        uimage.extract()

    elif options.merge:
        uimage.merge(options.header_file, args, options.output_filename)
