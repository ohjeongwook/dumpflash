"""TODO"""
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

        self.Open(filename)
        self.SetPageInfo(page_size, oob_size, page_per_block)

    def IsInitialized(self):
        """TODO"""
        return True

    def DumpInfo(self):
        return ""

    def SetUseAnsi(self, use_ansi):
        """TODO"""
        self.UseAnsi = use_ansi

    def SetPageInfo(self, page_size, oob_size, page_per_block):
        """TODO"""
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

    def Open(self, filename):
        """TODO"""
        try:
            self.fd = open(filename, 'rb')
            if self.Length > 0:
                self.FileSize = self.Length
            else:
                self.FileSize = os.path.getsize(filename) - offset

        except:
            print('Can\'t open a file:', filename)
            return False
        return True

    def Close(self):
        """TODO"""
        self.fd.close()

    def GetBlockOffset(self, block):
        """TODO"""
        return block * self.RawBlockSize

    def GetPageOffset(self, pageno):
        """TODO"""
        return pageno * self.RawPageSize

    def ReadPage(self, pageno, remove_oob = False):
        """TODO"""
        offset = self.GetPageOffset(pageno)

        if offset > self.FileSize:
            return b''

        self.fd.seek(self.BaseOffset + offset)

        if remove_oob:
            return self.fd.read(self.PageSize)
        return self.fd.read(self.RawPageSize)

    def ReadOOB(self, pageno):
        """TODO"""
        self.fd.seek(self.BaseOffset + pageno*self.RawPageSize+self.PageSize)
        return self.fd.read(self.OOBSize)
