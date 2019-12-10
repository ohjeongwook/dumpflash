# pylint: disable=invalid-name
# pylint: disable=line-too-long
import os

class IO:
    def __init__(self, filename, base_offset = 0, length = 0, page_size = 0x200, oob_size = 0x10, page_per_block = 0x20):
        self.DebugLevel = 0
        self.FileSize = 0
        self.UseAnsi = False
        self.BaseOffset = base_offset
        self.Length = length

        self.open(filename)
        self.set_page_info(page_size, oob_size, page_per_block)

    def is_initialized(self):
        return True

    def dump_info(self):
        return ""

    def set_use_ansi(self, use_ansi):
        self.UseAnsi = use_ansi

    def set_page_info(self, page_size, oob_size, page_per_block):
        self.PageSize = page_size
        self.OOBSize = oob_size
        self.RawPageSize = self.PageSize+self.OOBSize
        self.PagePerBlock = page_per_block
        self.BlockSize = self.PageSize * self.PagePerBlock
        self.RawBlockSize = self.RawPageSize * self.PagePerBlock
        self.PageCount = int((self.FileSize) / self.PageSize)
        self.BlockCount = int(self.PageCount / self.PagePerBlock)

        print('PageSize: 0x%x' % self.PageSize)
        print('OOBSize: 0x%x' % self.OOBSize)
        print('PagePerBlock: 0x%x' % self.PagePerBlock)
        print('BlockSize: 0x%x' % self.BlockSize)
        print('RawPageSize: 0x%x' % self.RawPageSize)
        print('FileSize: 0x%x' % self.FileSize)
        print('PageCount: 0x%x' % self.PageCount)        
        print('')

    def open(self, filename):
        try:
            self.fd = open(filename, 'rb')
            if self.Length > 0:
                self.FileSize = self.Length
            else:
                self.FileSize = os.path.getsize(filename) - self.BaseOffset

        except:
            print('Can\'t open a file:', filename)
            return False
        return True

    def close(self):
        self.fd.close()

    def get_block_offset(self, block):
        return block * self.RawBlockSize

    def get_page_offset(self, pageno):
        return pageno * self.RawPageSize

    def read_page(self, pageno, remove_oob = False):
        offset = self.get_page_offset(pageno)

        if offset > self.FileSize:
            return b''

        self.fd.seek(self.BaseOffset + offset)

        if remove_oob:
            return self.fd.read(self.PageSize)
        return self.fd.read(self.RawPageSize)

    def read_oob(self, pageno):
        self.fd.seek(self.BaseOffset + pageno*self.RawPageSize+self.PageSize)
        return self.fd.read(self.OOBSize)
