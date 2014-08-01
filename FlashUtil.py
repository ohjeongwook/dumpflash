from optparse import OptionParser
from FlashFile import *
from FlashDevice import *
from DumpUBoot import *
from ECC import *
import os

class FlashUtil:
	def __init__(self, filename='', page_size=0x200, oob_size=0x10, page_per_block=0x20,slow=False):
		self.UseAnsi=False
		self.UseSequentialMode=False
		self.DumpProgress=True

		if filename:
			self.io = FlashFile(filename, page_size, oob_size, page_per_block)
		else:
			self.io = NandIO(slow)
		
	def SetUseAnsi(self,use_ansi):
		self.UseAnsi=use_ansi
		self.io.SetUseAnsi(use_ansi)

	def CheckECC(self):
		block = 0
		end_of_file=False
		count=0
		error_count=0

		ecc=ECC()
		while 1:
			for page in range(0,self.io.PagePerBlock,1):
				data=self.io.readPage(block * self.io.PagePerBlock)

				if not data:
					end_of_file=True
					break
	
				count+=1
				body = data[0:self.io.PageSize]
				ecc0_ = ord(data[self.io.PageSize])
				ecc1_ = ord(data[self.io.PageSize+1])
				ecc2_ = ord(data[self.io.PageSize+2])
		
				if ecc0_==0xff and ecc1_==0xff and ecc2_==0xff:
					continue
		
				(ecc0, ecc1, ecc2) = ecc.CalcECC(body)
		
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
			current_page=block * self.io.PagePerBlock + page
			oob=self.io.readOOB(block * self.io.PagePerBlock + page)
			bad_block_byte = oob[6:7]
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
				print "Bad block: %d (at 0x%x)" % (block, (block * self.io.BlockSize ))
	
			elif ret==self.ERROR:
				break

			block += 1

			if block>self.io.BlockCount:
				break

		print "Checked %d blocks and found %d errors" % (block,error_count)

	def readPages(self,start_page=-1,end_page=-1,remove_oob=False, filename='', append=False, maximum=0):
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
				if maximum!=0:
					if length<maximum:
						fd.write(data[0:maximum-length])
					else:
						break
				else:
					fd.write(data)
			else:
				whole_data+=data
			
			length+=len(data)
			current = time.time()

			if self.DumpProgress:
				block=page/self.io.PagePerBlock
				if self.UseAnsi:
					sys.stdout.write('Reading page: %d/%ld block: 0x%x speed: %d bytes/sec)\n\033[A' % (page, end_page, block, length/(current-start)))
				else:
					sys.stdout.write('Reading page: %d/%ld block: 0x%x speed: %d bytes/sec)\n' % (page, end_page, block, length/(current-start)))
		
		if filename:
			fd.close()

		if maximum!=0:
			return whole_data[0:maximum]
		return whole_data

	def readSeqPages(self, start_page=-1, end_page=-1, remove_oob=False, filename='', append=False, maximum = 0):
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
		for page in range(start_page,end_page,self.io.PagePerBlock):
			data=self.io.readSeq(page, remove_oob)

			if filename:
				if maximum!=0:
					if length<maximum:
						fd.write(data[0:maximum-length])
					else:
						break
				else:
					fd.write(data)
			else:
				whole_data+=data

			length+=len(data)
			current = time.time()

			if self.DumpProgress:
				block=page/self.io.PagePerBlock
				if self.UseAnsi:
					sys.stdout.write('Reading page: %d/%ld block: 0x%x %d bytes/sec\n\033[A' % (page, end_page, block, length/(current-start)))
				else:
					sys.stdout.write('Reading page: %d/%ld block: 0x%x%d bytes/sec\n' % (page, end_page, block, length/(current-start)))

		if filename:
			fd.close()

		if maximum!=0:
			return whole_data[0:maximum]
		return whole_data

	def AddOOB(self,filename, output_filename, jffs2=False):
		fd=open(filename,'rb')
		wfd=open(output_filename,"wb")

		current_block_number=0
		current_output_size=0
		ecc=ECC()
		while 1:
			page=fd.read(self.io.PageSize)

			if not page:
				break

			(ecc0, ecc1, ecc2) = ecc.CalcECC(page)

			oob_postfix='\xFF' * 13

			if current_output_size% self.io.BlockSize==0:
				if jffs2 and current_block_number%2==0:
					oob_postfix="\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00"
				current_block_number+=1

			data=page + struct.pack('BBB',ecc0,ecc1,ecc2) + oob_postfix
			wfd.write(data)
			current_output_size += len(data)

		#Write blank pages
		"""
		while size>current_output_size:
			if current_output_size% self.BlockSize==0:
				wfd.write("\xff"*0x200+ "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x85\x19\x03\x20\x08\x00\x00\x00")
			else:
				wfd.write("\xff"*0x210)
			current_output_size+=0x210
		"""

		fd.close()
		wfd.close()

	def CopyPages(self, output_filename, start_page=0, end_page=-1, remove_oob = True):
		if start_page==-1:
			start_page=0

		if end_page==-1:
			end=self.io.BlockSize*self.io.RawPageSize*self.io.PagePerBlock
		else:
			end=end_page * self.io.RawPageSize

		return self.CopyPagesByOffset(output_filename, start_page * self.io.RawPageSize, end, remove_oob)

	def CopyPagesByOffset(self, output_filename, start=0, end=-1, remove_oob = True):
		if start==-1:
			start=0

		if end==-1:
			end=self.BlockSize*self.RawPageSize*self.PagePerBlock

		wfd=open(output_filename,"wb")

		start_block = start / self.io.BlockSize
		start_block_offset = start % self.io.BlockSize
		start_page = start_block_offset / self.io.RawPageSize
		start_page_offset = start_block_offset % self.io.RawPageSize

		end_block = end / self.io.BlockSize
		end_block_offset = end % self.io.BlockSize
		end_page = end_block_offset / self.io.RawPageSize
		end_page_offset = end_block_offset % self.io.RawPageSize

		print 'Dumping blocks (Block: 0x%x Page: 0x%x ~  Block: 0x%x Page: 0x%x)' % (start_block, start_block_offset, end_block, end_block_offset)

		for block in range(start_block,end_block+1,1):
			ret=self.IsBadBlock(block)

			if ret==self.CLEAN_BLOCK:
				current_start_page=0
				current_end_page=self.io.PagePerBlock

				if block==start_block:
					current_start_page=start_page
				elif block==end_block:
					current_end_page=end_page+1

				for page in range(current_start_page,current_end_page,1):
					data=self.io.readPage(block * self.io.PagePerBlock + page)

					if not remove_oob:
						write_size=self.io.RawPageSize
					else:
						write_size=self.io.PageSize

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

		self.DumpProgress=False
		data=''
		append=False
		maximum=length
		for block in blocks:
			start_page=block * self.io.PagePerBlock
			end_page=(block+1) * self.io.PagePerBlock
			if block==start_block:
				start_page+=start_block_page

			if self.UseSequentialMode:
				data+=self.readSeqPages(start_page, end_page, True, filename, append=append, maximum = maximum)
			else:
				data+=self.readPages(start_page,end_page,True, filename, append=append, maximum = maximum)

			maximum-=self.io.PagePerBlock*self.io.PageSize

			if len(data)>length:
				break

			append=True

		self.DumpProgress=True
		return data[0:length]


	def FindUBootImages(self):
		print 'Finding U-Boot Images'
		block = 0

		while 1:
			ret=self.IsBadBlock(block)

			if ret==self.BAD_BLOCK:
				pass
			elif ret==self.ERROR:
				break

			magic=self.io.readPage(block*self.io.PagePerBlock)[0:4]

			if magic=='\x27\x05\x19\x56':
				print 'U-Boot Image found at block 0x%x' % ( block )
				uimage=uImage()
				uimage.ParseHeader(self.readData(block*self.io.PagePerBlock, 64))
				uimage.DumpHeader()
				block_size=uimage.size / self.io.BlockSize
				print "Block count:", block_size
				print "0x%x - 0x%x" % (block, block+block_size)
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

				try:
					os.unlink(output_filename)
				except:
					pass
				self.readData(pageno, 0x40+uimage.size, output_filename)
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

		while 1:
			ret = self.IsBadBlock(block) 
			if ret == self.CLEAN_BLOCK:
				oob = self.io.readOOB(block*self.io.PagePerBlock)
	
				if not oob:
					break

				if oob[8:] == '\x85\x19\x03\x20\x08\x00\x00\x00':
					print "JFFS2 block: %d (at file offset 0x%x)" % (block, (block * self.io.BlockSize ))

			elif ret == self.ERROR:
				break
			else:
				print 'Bad block', block

			block += 1

if __name__=='__main__':
	import sys
	filename=sys.argv[1]
	flash_util=FlashUtil(filename)
	flash_util.FindUBootImages()
