import pprint
import struct
from ECC import *

class FlashFile:	
	def __init__(self,filename, page_size=0x200, oob_size=0x10, page_per_block=0x20):
		self.DebugLevel=0
		self.FileSize=0
		self.UseAnsi=False

		self.Open(filename)
		self.SetPageInfo(page_size,oob_size,page_per_block)
		
	def IsInitialized(self):
		return True

	def SetUseAnsi(self,use_ansi):
		self.UseAnsi=use_ansi

	def SetPageInfo(self, page_size, oob_size, page_per_block):
		self.PageSize=page_size
		self.OOBSize=oob_size
		self.RawPageSize=self.PageSize+self.OOBSize
		self.PagePerBlock=page_per_block
		self.BlockSize=self.PageSize * self.PagePerBlock
		self.RawBlockSize=self.RawPageSize * self.PagePerBlock
		self.PageCount=(self.FileSize)/self.PageSize
		self.BlockCount = self.PageCount/self.PagePerBlock

		print 'PageSize: 0x%x' % self.PageSize
		print 'OOBSize: 0x%x' % self.OOBSize
		print 'PagePerBlock: 0x%x' % self.PagePerBlock
		print 'BlockSize: 0x%x' % self.BlockSize
		print 'RawPageSize: 0x%x' % self.RawPageSize
		print 'PageCount: 0x%x' % self.PageCount
		print 'FileSize: 0x%x' % self.FileSize
		print ''

	def Open(self,filename):
		try:
			self.fd=open(filename,'rb')
			import os
			self.FileSize=os.path.getsize(filename)
		except:
			print "Can't open a file:",filename
			return False
		return True

	def Close(self):
		self.fd.close()

	def GetBlockOffset(self,block):
		return block * self.RawBlockSize

	def GetPageOffset(self,pageno):
		return pageno*self.RawPageSize

	def ReadPage(self,pageno,remove_oob=False):
		self.fd.seek(self.GetPageOffset(pageno))

		if remove_oob:
			return self.fd.read(self.PageSize)
		else:
			return self.fd.read(self.RawPageSize)

	def ReadOOB(self,pageno):
		self.fd.seek(pageno*self.RawPageSize+self.PageSize)
		return self.fd.read(self.OOBSize)
