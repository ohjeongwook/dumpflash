import pprint
import struct
from ECC import *

class FlashFile:	
	def __init__(self,filename, page_size=0x200, oob_size=0x10, page_per_block=0x20):
		self.DebugLevel=0
		self.FileSize=0

		self.Open(filename)
		self.SetPageInfo(page_size,oob_size,page_per_block)

	def SetPageInfo(self, page_size, oob_size, page_per_block):
		self.PageSize=page_size
		self.OOBSize=oob_size
		self.PagePerBlock=page_per_block
		self.BlockSize = (self.PageSize+self.OOBSize) * self.PagePerBlock
		self.RawPageSize=self.PageSize+self.OOBSize
		self.PageCount=(self.FileSize)/self.PageSize

		print 'self.PageSize:',self.PageSize
		print 'self.OOBSize:',self.OOBSize
		print 'self.PagePerBlock:',self.PagePerBlock
		print 'self.BlockSize:',self.BlockSize
		print 'self.RawPageSize:',self.RawPageSize
		print 'self.PageCount:',self.PageCount

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
	
	def readPage(self,pageno,remove_oob=False):
		self.fd.seek(pageno*self.RawPageSize)

		if remove_oob:
			return self.fd.read(self.PageSize)
		else:
			return self.fd.read(self.RawPageSize)

	def readOOB(self,pageno):
		self.fd.seek(pageno*self.RawPageSize+self.PageSize)
		return self.fd.read(self.OOBSize)

	def GetBlockOffset(self,block):
		return block * self.BlockSize


	def AddOOB(self,filename, output_filename, size=0):
		fd=open(filename,'rb')
		wfd=open(output_filename,"wb")

		current_block_number=0
		current_output_size=0
		while 1:
			page=fd.read(self.PageSize)

			if not page:
				break

			(ecc0, ecc1, ecc2) = self.CalcECC(page)

			oob_postfix='\xFF' * 13
			if current_output_size% self.BlockSize==0:
				if current_block_number%2==0:
					oob_postfix="\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00"
				current_block_number+=1

			data=page + struct.pack('BBB',ecc0,ecc1,ecc2) + oob_postfix
			wfd.write(data)
			current_output_size += len(data)

		#Write blank pages
		while size>current_output_size:
			if current_output_size% self.BlockSize==0:
				wfd.write("\xff"*0x200+ "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00")
			else:
				wfd.write("\xff"*0x210)
			current_output_size+=0x210

		fd.close()
		wfd.close()

	def RemoveOOBByPage(self, output_filename, start_page=0, end_page=-1, preserve_oob = False):
		if end_page==-1:
			end=self.BlockSize*self.RawPageSize*self.PagePerBlock
		else:
			end=end_page * self.RawPageSize

		return self.RemoveOOB(output_filename, start_page * self.RawPageSize, end, preserve_oob)

	def RemoveOOB(self, output_filename, start=0, end=-1, preserve_oob = False):
		if end==-1:
			end=self.BlockSize*self.RawPageSize*self.PagePerBlock

		wfd=open(output_filename,"wb")

		start_block = start / self.BlockSize
		start_block_offset = start % self.BlockSize
		start_page = start_block_offset / self.RawPageSize
		start_page_offset = start_block_offset % self.RawPageSize

		end_block = end / self.BlockSize
		end_block_offset = end % self.BlockSize
		end_page = end_block_offset / self.RawPageSize
		end_page_offset = end_block_offset % self.RawPageSize

		print 'Dumping blocks (Block: 0x%x Page: 0x%x ~  Block: 0x%x Page: 0x%x)' % (start_block, start_block_offset, end_block, end_block_offset)

		for block in range(start_block,end_block+1,1):
			ret=self.IsBadBlock(block)

			if ret==self.CLEAN_BLOCK:
				current_start_page=0
				current_end_page=self.PagePerBlock

				if block==start_block:
					current_start_page=start_page
				elif block==end_block:
					current_end_page=end_page+1

				for page in range(current_start_page,current_end_page,1):
					current_offset= block * self.BlockSize + page * self.RawPageSize 

					self.fd.seek( current_offset )

					data = self.fd.read(self.RawPageSize)

					if preserve_oob:
						write_size=self.RawPageSize
					else:
						write_size=self.PageSize

					if block==start_block and page==current_start_page and start_page_offset>0:
						wfd.write(data[start_page_offset:write_size])

					elif block==end_block and page==current_end_page-1 and end_page_offset>=0:
						wfd.write(data[0:end_page_offset])

					else:
						wfd.write(data[0:write_size])

			elif ret==self.ERROR:
				break

			else:
				print "Skipping block %d" % block
		
		wfd.close()