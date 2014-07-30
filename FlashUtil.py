from optparse import OptionParser
from FlashFile import *
from FlashIO import *
from DumpUBoot import *
from ECC import *

class FlashUtil:
	def __init__(self, filename=''):
		self.UseSequentialMode=False

		if filename:
			self.io = FlashFile(filename)
		else:
			self.io = NandIO()
			self.io.DumpInfo()

	def CheckECC(self):
		block = 0
		end_of_file=False
		count=0
		error_count=0

		while 1:
			for page in range(0,self.PagePerBlock,1):
				offset = (block * (self.PageSize+self.OOBSize) * self.PagePerBlock) + page * (self.PageSize+self.OOBSize)
				self.fd.seek(offset,0)
				data = self.fd.read(self.PageSize+self.OOBSize)
				
				if not data:
					end_of_file=True
					break
	
				count+=1
				body = data[0:self.PageSize]
				ecc0_ = ord(data[self.PageSize])
				ecc1_ = ord(data[self.PageSize+1])
				ecc2_ = ord(data[self.PageSize+2])
		
				if ecc0_==0xff and ecc1_==0xff and ecc2_==0xff:
					continue
		
				(ecc0, ecc1, ecc2) = self.CalcECC(body)
		
				ecc0_xor = ecc0 ^ ecc0_
				ecc1_xor = ecc1 ^ ecc1_
				ecc2_xor = ecc2 ^ ecc2_
		
				if ecc0_xor != 0 or ecc1_xor != 0 or ecc2_xor != 0:
					error_count+=1
					print "Checksum error block: %d page: %d at 0x%x" % (block, page, offset)
					print "Orig: 0x%2x 0x%2x 0x%2x" % ( ecc0_, ecc1_, ecc2_)
					print "Calc: 0x%2x 0x%2x 0x%2x" % ( ecc0, ecc1, ecc2)
					print "XOR:  0x%2x 0x%2x 0x%2x" % ( ecc0 ^ ecc0_, ecc1 ^ ecc1_, ecc2 ^ ecc2_)
					print ''
		
			if end_of_file:
				break
		
			block += 1
	
		print "Checked %d ECC record and found %d errors" % (count,error_count)

		
	def IsBadBlockPage(self,oob):
		bad_block=False
		
		if oob[0:3] != '\xff\xff\xff':
			bad_block=True
			if oob[0x8:] == '\x85\x19\x03\x20\x08\x00\x00\x00': #JFFS CleanMarker
				bad_block=False

		return bad_block

	CLEAN_BLOCK=0
	BAD_BLOCK=1
	ERROR=2

	def IsBadBlock(self,block):
		for page in range(0,2,1):
			bad_block_byte = self.readData(block * self.io.PagePerBlock, self.io.PageSize + 6)[self.io.PageSize + 5:self.io.PageSize + 6]
			if not bad_block_byte:
				return self.ERROR

			if bad_block_byte == '\xff':
				return self.CLEAN_BLOCK
			
		return self.BAD_BLOCK

	def CheckBadBlocks(self):
		block = 0
		error_count=0

		while 1:
			ret=self.IsBadBlock(block)

			if ret==self.BAD_BLOCK:
				error_count+=1
				print "Bad block: %d (at 0x%x)" % (block, (block * self.BlockSize ))
	
			elif ret==self.ERROR:
				break

			block += 1

		print "Checked %d blocks and found %d errors" % (block,error_count)

	def readPages(self,start_page=-1,end_page=-1,remove_oob=False, filename='', append=False):
		if filename:
			if append:
				fd=open(filename,'ab')
			else:
				fd=open(filename,'wb')
		
		if start_page==-1:
			start_page=0

		if end_page==-1:
			end_page=self.io.PageCount+1

		whole_data=''
		length=0
		start = time.time()
		for page in range(start_page,end_page,1):
			data=self.io.readPage(page,remove_oob)

			if filename:
				fd.write(data)
			else:
				whole_data+=data
			
			length+=len(data)
			current = time.time()
			#sys.stdout.write('%d/%ld (%d bytes/sec)\n' % (page, end_page, length/(current-start)))
		
		if filename:
			fd.close()

		return whole_data

	def readData(self,start_page,length,filename=''):
		start_block=start_page / self.io.PagePerBlock
		start_block_page=start_page % self.io.PagePerBlock

		expected_data_length=0
		block=start_block
		blocks=[]
		for start_page in range(start_block*self.io.PagePerBlock,self.io.PageCount,self.io.PagePerBlock):
			is_bad_block=False
			for pageoff in range(0,2,1):
				oob=self.io.readOOB(start_page+pageoff)

				if oob and oob[5]!='\xff':
					is_bad_block=True
					break
			
			if not is_bad_block:
				if start_page <= start_page and start_page <= start_page+self.io.PagePerBlock: #First block
					expected_data_length += (self.io.PagePerBlock-start_block_page) * self.io.PageSize
					blocks.append(block)
				else:
					expected_data_length += self.io.PagePerBlock * self.io.PageSize
					blocks.append(block)

			if expected_data_length>=length:
				break
			block+=1

		data=''
		for block in blocks:
			start_page=block * self.io.PagePerBlock
			end_page=(block+1) * self.io.PagePerBlock
			if block==start_block:
				start_page+=start_block_page

			if self.UseSequentialMode:
				data+=self.readSeqPages(start_page, end_page, True, filename, append=True)
			else:
				data+=self.readPages(start_page,end_page,True, filename, append=True)
			
			if len(data)>length:
				break

		return data[0:length]


	def FindUBootImages(self):
		print 'Finding U-Boot Images'
		block = 0

		while 1:
			ret=self.IsBadBlock(block)

			if ret==self.BAD_BLOCK:
				pass
			elif ret==self.ERROR:
				print 'Error found', block
				break

			magic=self.readData(block*self.io.PagePerBlock, 4)

			if magic=='\x27\x05\x19\x56':
				print 'U-Boot Image found at block 0x%x' % ( block )
				uimage=uImage()
				uimage.ParseHeader(magic+self.readData(block*self.io.PagePerBlock, 60))
				print ''

			block += 1

		print "Checked %d blocks" % (block)

	def DumpUBootImages(self):
		seq=0
		for pageno in range(0,self.io.PageCount,self.io.PagePerBlock):
			data=self.io.readPage(pageno)

			if data[0:4]=='\x27\x05\x19\x56':
				print 'U-Boot Image found at block 0x%x' % ( pageno / self.io.PagePerBlock )
				uimage=uImage()
				uimage.ParseHeader(data[0:0x40])
				uimage.DumpHeader()
				
				output_filename='U-Boot-%.2d.dmp' % seq
				seq+=1

				self.readData(pageno, uimage.size, output_filename)
				print ''

				uimage=uImage()
				uimage.ParseFile(output_filename)
				uimage.Extract()

	def FindJFFS2(self):
		bad_blocks={}
		minimum_pageno=-1
		maximum_pageno=-1
		for pageno in range(0,self.io.PageCount,self.io.PagePerBlock):
			oob=self.io.readOOB(pageno)

			if oob[8:]=='\x85\x19\x03\x20\x08\x00\x00\x00':
				print 'JFFS2 block found:', pageno

				if minimum_pageno == -1:
					minimum_pageno = pageno
				maximum_pageno = pageno
			elif oob[0:3]=='\xff\xff\xff':
				print 'blank page'
			else:
				print 'OOB: ', pageno, pprint.pprint(oob)

		return [minimum_pageno, maximum_pageno]
	
	def IsJFFS2Block(self,block):
		ret = self.IsBadBlock(block) 
		if ret == self.CLEAN_BLOCK:
			page=0
			block_offset = (block * self.BlockSize ) + (page * (self.PageSize + self.OOBSize))
			self.fd.seek( block_offset + self.PageSize)
			oob = self.fd.read(16)
	
			if not oob:
				return 0

			if oob[8:] == '\x85\x19\x03\x20\x08\x00\x00\x00' and oob[0:3]!='\xff\xff\xff':
				return 2

		elif ret == self.ERROR:
			return 0
		return 1

	def FindJFFS2(self):
		block = 0
		end_of_file=False
		error_count=0

		while 1:
			ret = self.IsBadBlock(block) 
			if ret == self.CLEAN_BLOCK:
				page=0
				block_offset = (block * self.BlockSize ) + (page * (self.PageSize + self.OOBSize))
				self.fd.seek( block_offset + self.PageSize)
				oob = self.fd.read(self.OOBSize)
	
				if not oob:
					break

				if oob[8:] == '\x85\x19\x03\x20\x08\x00\x00\x00': # and oob[0:3]!='\xff\xff\xff'
					print "JFFS2 block: %d (at file offset 0x%x) - ECC: %.2x %.2x %.2x" % (block, (block * self.BlockSize ), ord(oob[0]), ord(oob[1]), ord(oob[2]))

			elif ret == self.ERROR:
				break

			block += 1

if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	flash_util=FlashUtil(filename)
	flash_util.FindUBootImages()
