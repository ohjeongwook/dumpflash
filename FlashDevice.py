from pyftdi.pyftdi.ftdi import *
from array import array as Array
import time
import sys
import pprint
from DumpUBoot import *

class NandIO:
	ADR_CE=0x10
	ADR_WP=0x20
	ADR_CL=0x40
	ADR_AL=0x80

	NAND_CMD_READID=0x90

	NAND_CMD_READ0=0
	NAND_CMD_READ1=1
	NAND_CMD_RNDOUT=5
	NAND_CMD_PAGEPROG=0x10
	NAND_CMD_READOOB=0x50
	NAND_CMD_ERASE1=0x60
	NAND_CMD_STATUS=0x70
	NAND_CMD_STATUS_MULTI=0x71
	NAND_CMD_SEQIN=0x80
	NAND_CMD_RNDIN=0x85
	NAND_CMD_READID=0x90
	NAND_CMD_ERASE2=0xd0
	NAND_CMD_PARAM=0xec
	NAND_CMD_RESET=0xff
	NAND_CMD_LOCK=0x2a
	NAND_CMD_UNLOCK1=0x23
	NAND_CMD_UNLOCK2=0x24
	NAND_CMD_READSTART=0x30
	NAND_CMD_RNDOUTSTART=0xE0
	NAND_CMD_CACHEDPROG=0x15
	NAND_CMD_ONFI=0xEC

	NAND_STATUS_FAIL=(1<<0) # HIGH - FAIL,  LOW - PASS
	NAND_STATUS_IDLE=(1<<5) # HIGH - IDLE,  LOW - ACTIVE
	NAND_STATUS_READY=(1<<6) # HIGH - READY, LOW - BUSY
	NAND_STATUS_NOT_PROTECTED=(1<<7) # HIGH - NOT,   LOW - PROTECTED

	LP_Options=1
	DeviceDescriptions=[
		["NAND 1MiB 5V 8-bit",		0x6e, 256, 1, 0x1000, 0, 3],
		["NAND 2MiB 5V 8-bit",		0x64, 256, 2, 0x1000, 0, 3],
		["NAND 4MiB 5V 8-bit",		0x6b, 512, 4, 0x2000, 0, 3],
		["NAND 1MiB 3,3V 8-bit",	0xe8, 256, 1, 0x1000, 0, 3],
		["NAND 1MiB 3,3V 8-bit",	0xec, 256, 1, 0x1000, 0, 3],
		["NAND 2MiB 3,3V 8-bit",	0xea, 256, 2, 0x1000, 0, 3],
	
		["NAND 4MiB 3,3V 8-bit",	0xe3, 512, 4, 0x2000, 0, 3],
		["NAND 4MiB 3,3V 8-bit",	0xe5, 512, 4, 0x2000, 0, 3],
		["NAND 8MiB 3,3V 8-bit",	0xd6, 512, 8, 0x2000, 0, 3],
		["NAND 8MiB 1,8V 8-bit",	0x39, 512, 8, 0x2000, 0, 3],
		["NAND 8MiB 3,3V 8-bit",	0xe6, 512, 8, 0x2000, 0, 3],
		["NAND 16MiB 1,8V 8-bit",	0x33, 512, 16, 0x4000, 0, 3],
		["NAND 16MiB 3,3V 8-bit",	0x73, 512, 16, 0x4000, 0, 3],
		["NAND 32MiB 1,8V 8-bit",	0x35, 512, 32, 0x4000, 0, 3],
		["NAND 32MiB 3,3V 8-bit",	0x75, 512, 32, 0x4000, 0, 3],
		["NAND 64MiB 1,8V 8-bit",	0x36, 512, 64, 0x4000, 0, 4],
		["NAND 64MiB 3,3V 8-bit",	0x76, 512, 64, 0x4000, 0, 4],
		["NAND 128MiB 1,8V 8-bit",	0x78, 512, 128, 0x4000, 0, 3],
		["NAND 128MiB 1,8V 8-bit",	0x39, 512, 128, 0x4000, 0, 3],
		["NAND 128MiB 3,3V 8-bit",	0x79, 512, 128, 0x4000, 0, 4],
		["NAND 256MiB 3,3V 8-bit",	0x71, 512, 256, 0x4000, 0, 4],

		# 512 Megabit
		["NAND 64MiB 1,8V 8-bit",	0xA2, 0,  64, 0, LP_Options, 4],
		["NAND 64MiB 1,8V 8-bit",	0xA0, 0,  64, 0, LP_Options, 4],
		["NAND 64MiB 3,3V 8-bit",	0xF2, 0,  64, 0, LP_Options, 4],
		["NAND 64MiB 3,3V 8-bit",	0xD0, 0,  64, 0, LP_Options, 4],
		["NAND 64MiB 3,3V 8-bit",	0xF0, 0,  64, 0, LP_Options, 4],

		# 1 Gigabit
		["NAND 128MiB 1,8V 8-bit",	0xA1, 0, 128, 0, LP_Options, 4],
		["NAND 128MiB 3,3V 8-bit",	0xF1, 0, 128, 0, LP_Options, 4],
		["NAND 128MiB 3,3V 8-bit",	0xD1, 0, 128, 0, LP_Options, 4],

		# 2 Gigabit
		["NAND 256MiB 1,8V 8-bit",	0xAA, 0, 256, 0, LP_Options, 5],
		["NAND 256MiB 3,3V 8-bit",	0xDA, 0, 256, 0, LP_Options, 5],

		# 4 Gigabit
		["NAND 512MiB 1,8V 8-bit",	0xAC, 0, 512, 0, LP_Options, 5],
		["NAND 512MiB 3,3V 8-bit",	0xDC, 0, 512, 0, LP_Options, 5],

		# 8 Gigabit
		["NAND 1GiB 1,8V 8-bit",	0xA3, 0, 1024, 0, LP_Options, 5],
		["NAND 1GiB 3,3V 8-bit",	0xD3, 0, 1024, 0, LP_Options, 5],

		# 16 Gigabit
		["NAND 2GiB 1,8V 8-bit",	0xA5, 0, 2048, 0, LP_Options, 5],
		["NAND 2GiB 3,3V 8-bit",	0xD5, 0, 2048, 0, LP_Options, 5],

		# 32 Gigabit
		["NAND 4GiB 1,8V 8-bit",	0xA7, 0, 4096, 0, LP_Options, 5],
		["NAND 4GiB 3,3V 8-bit",	0xD7, 0, 4096, 0, LP_Options, 5],

		# 64 Gigabit
		["NAND 8GiB 1,8V 8-bit",	0xAE, 0, 8192, 0, LP_Options, 5],
		["NAND 8GiB 3,3V 8-bit",	0xDE, 0, 8192, 0, LP_Options, 5],

		# 128 Gigabit
		["NAND 16GiB 1,8V 8-bit",	0x1A, 0, 16384, 0, LP_Options, 5],
		["NAND 16GiB 3,3V 8-bit",	0x3A, 0, 16384, 0, LP_Options, 5],

		# 256 Gigabit
		["NAND 32GiB 1,8V 8-bit",	0x1C, 0, 32768, 0, LP_Options, 6],
		["NAND 32GiB 3,3V 8-bit",	0x3C, 0, 32768, 0, LP_Options, 6],

		# 512 Gigabit
		["NAND 64GiB 1,8V 8-bit",	0x1E, 0, 65536, 0, LP_Options, 6],
		["NAND 64GiB 3,3V 8-bit",	0x3E, 0, 65536, 0, LP_Options, 6],

		["NAND 4MiB 3,3V 8-bit",	0xd5, 512, 4, 0x2000, 0, 3]
	]

	Debug=0
	
	PageSize=0
	OOBSize=0
	PageCount=0
	BlockCount=4096
	PagePerBlock=32

	WriteProtect=True
	CheckBadBlock=True
	CheckBadBlocksForWriting=False
	RemoveOOB=False
	UseSequentialMode=False

	def __init__(self, do_slow=False):
		self.UseAnsi=False
		self.Ftdi = Ftdi()
		self.Ftdi.open(0x0403,0x6010,interface=1)
		self.Ftdi.set_bitmode(0, self.Ftdi.BITMODE_MCU)

		if do_slow:
			# Clock FTDI chip at 12MHz instead of 60MHz
			self.Ftdi.write_data(Array('B', [Ftdi.ENABLE_CLK_DIV5]))
		else:
			self.Ftdi.write_data(Array('B', [Ftdi.DISABLE_CLK_DIV5]))

		self.Ftdi.set_latency_timer(1)
		self.Ftdi.purge_buffers()
		self.Ftdi.write_data(Array('B', [Ftdi.SET_BITS_HIGH,0x0,0x1]))
		self.waitReady()
		self.GetID()

	def SetUseAnsi(self,use_ansi):
		self.UseAnsi=use_ansi

	def Test(self):
		self.Ftdi.write_data(Array('B', [Ftdi.SET_BITS_HIGH,0x0,0x1]))

		while 1:
			self.Ftdi.write_data(Array('B', [Ftdi.GET_BITS_HIGH]))
			data = self.Ftdi.read_data_bytes(1)
			print hex(data[0])

	def waitReady(self):
		while 1:
			self.Ftdi.write_data(Array('B', [Ftdi.GET_BITS_HIGH]))
			data = self.Ftdi.read_data_bytes(1)
			
			if data[0]&2==0x2:
				return
			else:
				if self.Debug>0:
					print 'Not Ready', data

	def nandRead(self,cl,al,count):
		cmds=[]
		cmd_type=0
		if cl==1:
			cmd_type|=self.ADR_CL
		if al==1:
			cmd_type|=self.ADR_AL

		cmds+=[Ftdi.READ_EXTENDED, cmd_type, 0]

		for i in range(1,count,1):
			cmds+=[Ftdi.READ_SHORT, 0]

		cmds.append(Ftdi.SEND_IMMEDIATE)
		self.Ftdi.write_data(Array('B', cmds))
		data = self.Ftdi.read_data_bytes(count)
		return data.tolist()

	def nandWrite(self,cl,al,data):
		cmds=[]
		cmd_type=0
		if cl==1:
			cmd_type|=self.ADR_CL
		if al==1:
			cmd_type|=self.ADR_AL
		if not self.WriteProtect:
			cmd_type|=self.ADR_WP

		cmds+=[Ftdi.WRITE_EXTENDED, cmd_type, 0, ord(data[0])]

		for i in range(1,len(data),1):
			cmds+=[Ftdi.WRITE_SHORT, 0, ord(data[i])]

		self.Ftdi.write_data(Array('B', cmds))

	def sendCmd(self,cmd):
		self.nandWrite(1,0,chr(cmd))

	def sendAddr(self,addr,count):
		data=''

		for i in range(0,count,1):
			data += chr(addr & 0xff)
			addr=addr>>8

		self.nandWrite(0,1,data)

	def Status(self):
		self.sendCmd(0x70)
		status=self.readFlashData(1)[0]
		return status

	def readFlashData(self,count):
		return self.nandRead(0,0,count)

	def writeData(self,count):
		return self.nandWrite(0,0,count)

	def GetID(self):
		self.sendCmd(self.NAND_CMD_READID)
		self.sendAddr(0,1)
		id=self.readFlashData(8)

		self.Name=''
		self.ID=0
		self.PageSize=0
		self.ChipSizeMB=0
		self.EraseSize=0
		self.Options=0
		self.AddrCycles=0

		for device_description in self.DeviceDescriptions:
			if device_description[1]==id[1]:
				(self.Name,self.ID,self.PageSize,self.ChipSizeMB,self.EraseSize,self.Options,self.AddrCycles)=device_description
				
		#Check ONFI
		self.sendCmd(self.NAND_CMD_READID)
		self.sendAddr(0x20,1)
		id=self.readFlashData(4)

		onfi=False
		if id[0]=='O' and id[1]=='N' and id[2]=='F' and id[3]=='I':
			onfi=True

		if onfi:
			self.sendCmd(self.NAND_CMD_ONFI)
			self.sendAddr(0,1)
			self.waitReady()
			onfi_data=self.readFlashData(0x100)
			if onfi_data[0]==0x4F and onfi_data[1]==0x4E and onfi_data[2]==0x46 and onfi_data[3]==0x49:
				onfi=True
			else:
				onfi=False

		if self.PageSize==0:
			ext_id=id[3]
			#TODO:
		else:
			self.OOBSize = self.PageSize / 32

		if id[0]==0x98:
			self.Manufacturer="Toshiba";
		if id[0]==0xec:
			self.Manufacturer="Samsung";
		if id[0]==0x04:
			self.Manufacturer="Fujitsu";
		if id[0]==0x8f:
			self.Manufacturer="National Semiconductors";
		if id[0]==0x07:
			self.Manufacturer="Renesas";
		if id[0]==0x20:
			self.Manufacturer="ST Micro";
		if id[0]==0xad:
			self.Manufacturer="Hynix";
		if id[0]==0x2c:
			self.Manufacturer="Micron";
		if id[0]==0x01:
			self.Manufacturer="AMD";
		if id[0]==0xc2:
			self.Manufacturer="Macronix";

		if self.PageSize>0:
			self.PageCount=(self.ChipSizeMB*1024*1024)/self.PageSize

		self.RawPageSize=self.PageSize+self.OOBSize
		self.BlockSize=self.PagePerBlock*self.RawPageSize

	def DumpInfo(self):
		print 'Name:\t\t',self.Name
		print 'ID:\t\t0x%x' % self.ID
		print 'Page size:\t0x%x' % self.PageSize
		print 'OOB size:\t0x%x' % self.OOBSize
		print 'Page count:\t0x%x' % self.PageCount
		print 'Size:\t\t0x%x' % self.ChipSizeMB
		print 'Erase size:\t0x%x' % self.EraseSize
		print 'Options:\t',self.Options
		print 'Address cycle:\t',self.AddrCycles
		print 'Manufacturer:\t',self.Manufacturer
		print ''

	def CheckBadBlocks(self):
		bad_blocks={}
		for pageno in range(0,self.PageCount,self.PagePerBlock):
			for pageoff in range(0,2,1):
				oob=self.readOOB(pageno+pageoff)

				if oob[5]!='\xff':
					print 'Bad block found:', pageno
					bad_blocks[pageno]=1
					break
		return bad_blocks

	def readOOB(self,pageno):
		bytes=[]
		if self.Options&self.LP_Options:
			pass #TODO:
		else:
			self.sendCmd(self.NAND_CMD_READOOB)
			self.waitReady()
			self.sendAddr(pageno<<8,self.AddrCycles)
			self.waitReady()
			bytes+=self.readFlashData(self.OOBSize)

		data=''

		for ch in bytes:
			data+=chr(ch)
		return data

	def readPage(self,pageno,remove_oob=False):
		bytes=[]

		if self.Options&self.LP_Options:
			self.sendCmd(self.NAND_CMD_READ0)
			self.waitReady()
			self.sendAddr(pageno<<16,self.AddrCycles)
			self.waitReady()
			self.sendCmd(self.NAND_CMD_READSTART)
			self.waitReady()
			if self.PageSize>0x1000:
				len=self.PageSize
				while len>0:
					read_len=0x1000
					if len<0x1000:
						read_len=len
					bytes+=self.readFlashData(read_len)
					len-=0x1000
			else:
				bytes=self.readFlashData(self.PageSize)

			self.sendCmd(self.NAND_CMD_READ0)
			self.waitReady()
			self.sendAddr((pageno<<16)+self.PageSize,self.AddrCycles)
			self.waitReady()
			self.sendCmd(self.NAND_CMD_READSTART)
			self.waitReady()
			bytes+=self.readFlashData(self.PageSize)

			#TODO: Implement remove_oob
		else:
			self.sendCmd(self.NAND_CMD_READ0)
			self.waitReady()
			self.sendAddr(pageno<<8,self.AddrCycles)
			self.waitReady()
			bytes+=self.readFlashData(self.PageSize/2)

			self.sendCmd(self.NAND_CMD_READ1)
			self.waitReady()
			self.sendAddr(pageno<<8,self.AddrCycles)
			self.waitReady()
			bytes+=self.readFlashData(self.PageSize/2)

			if not remove_oob:
				self.sendCmd(self.NAND_CMD_READOOB)
				self.waitReady()
				self.sendAddr(pageno<<8,self.AddrCycles)
				self.waitReady()
				bytes+=self.readFlashData(self.OOBSize)

		data=''

		for ch in bytes:
			data+=chr(ch)
		return data
		
	def readSeq(self,pageno,remove_oob=False):
		page=[]
		self.sendCmd(self.NAND_CMD_READ0)
		self.waitReady()
		self.sendAddr(pageno<<8,self.AddrCycles)
		self.waitReady()

		bad_block=False

		for i in range(0,self.PagePerBlock,1):
			page_data = self.readFlashData(self.RawPageSize)

			if i==0 or i==1:
				if page_data[self.PageSize+5]!=0xff:
					print 'Skipping bad block %d (%.2x)' % (pageno+i, page_data[self.PageSize+5])
					pprint.pprint(page_data[self.PageSize:])
					bad_block = True
			if remove_oob:
				page += page_data[0:self.PageSize]
			else:
				page += page_data

			self.waitReady()

		self.Ftdi.write_data(Array('B', [Ftdi.SET_BITS_HIGH,0x1,0x1]))
		self.Ftdi.write_data(Array('B', [Ftdi.SET_BITS_HIGH,0x0,0x1]))

		data=''

		if not bad_block or not self.CheckBadBlock:
			for ch in page:
				data+=chr(ch)

		return data

	def eraseBlockByPage(self,pageno):
		self.WriteProtect=False
		self.sendCmd(self.NAND_CMD_ERASE1);
		self.sendAddr(pageno, self.AddrCycles);
		self.sendCmd(self.NAND_CMD_ERASE2);
		self.waitReady();
		err=self.Status()
		self.WriteProtect=True

		return err

	def writePage(self,pageno,data):
		err=0
		self.WriteProtect=False

		if self.Options&self.LP_Options:
			self.sendCmd(self.NAND_CMD_SEQIN)
			self.waitReady()
			self.sendAddr(pageno<<16,self.AddrCycles)
			self.waitReady()
			self.writeData(data)
			self.sendCmd(self.NAND_CMD_PAGEPROG)
			self.waitReady()
		else:
			while 1:
				self.sendCmd(self.NAND_CMD_READ0)
				self.sendCmd(self.NAND_CMD_SEQIN)
				self.waitReady()
				self.sendAddr(pageno<<8,self.AddrCycles)
				self.waitReady()
				self.writeData(data[0:256])
				self.sendCmd(self.NAND_CMD_PAGEPROG)
				err=self.Status()
				if err&self.NAND_STATUS_FAIL:
					print 'Failed to write 1st half of ', pageno, err
					#return err
					continue
				break

			while 1:
				self.sendCmd(self.NAND_CMD_READ1)
				self.sendCmd(self.NAND_CMD_SEQIN)
				self.waitReady()
				self.sendAddr(pageno<<8,self.AddrCycles)
				self.waitReady()
				self.writeData(data[self.PageSize/2:self.PageSize])
				self.sendCmd(self.NAND_CMD_PAGEPROG)
				err=self.Status()
				if err&self.NAND_STATUS_FAIL:
					print 'Failed to write 2nd half of ', pageno, err
					#return err
					continue
				break

			while 1:
				self.sendCmd(self.NAND_CMD_READOOB)
				self.sendCmd(self.NAND_CMD_SEQIN)
				self.waitReady()
				self.sendAddr(pageno<<8,self.AddrCycles)
				self.waitReady()
				self.writeData(data[self.PageSize:self.RawPageSize])
				self.sendCmd(self.NAND_CMD_PAGEPROG)
				err=self.Status()
				if err&self.NAND_STATUS_FAIL:
					print 'Failed to write OOB of ', pageno, err
					#return err
					continue
				break

		self.WriteProtect=True
		return err

	def writeBlock(self,block_data):
		nand_tool.eraseBlockByPage(0)
		page=0
		for i in range(0,len(data),self.RawPageSize):
			print 'Writing page:', page
			nand_tool.writePage(pageno,data[i:i+self.RawPageSize])
			page+=1

	def writePages(self,filename,offset=0,start_page=-1,end_page=-1):
		fd=open(filename,'rb')
		fd.seek(offset)
		data=fd.read()

		if start_page==-1:
			start_page=0

		if end_page==-1:
			end_page=self.PageCount-1

		if self.CheckBadBlocksForWriting:
			bad_blocks = self.CheckBadBlocks()

		bytes=0
		start = time.time()
		page=start_page
		block=0
		current_data_offset=0
		current_block=0
		while current_data_offset<len(data) and current_block<self.BlockCount:
			if page%self.PagePerBlock == 0:
				current_block+=1
				if self.CheckBadBlocksForWriting and bad_blocks.has_key(page):
					print 'Skipping bad block at ', page
					page+=self.PagePerBlock
					continue
				self.eraseBlockByPage(page)
			
			page_data=data[current_data_offset:current_data_offset+self.RawPageSize]

			if len(page_data)<=0:
				print 'Not enough source data'
				break

			self.writePage(page,page_data)
			
			bytes+=len(page_data)
			current = time.time()

			print 'self.UseAnsi', self.UseAnsi
			if self.UseAnsi:
				sys.stdout.write('Writing page: %x/%lx (%d bytes/sec)\n\033[A' % (page, self.PageCount, bytes/(current-start)))
			else:
				sys.stdout.write('Writing page: %x/%lx (%d bytes/sec)\n' % (page, self.PageCount, bytes/(current-start)))

			page+=1

			current_data_offset+=self.RawPageSize

			if page>=end_page:
				break

		fd.close()

	def Erase(self):
		current_block=0
		while current_block<self.BlockCount:
			self.eraseBlockByPage(curret_block * self.PagePerBlock)

	def EraseBlock(self,start_block, end_block):
		for block in range(start_block, end_block+1, 1):
			print "Erasing block", block
			self.eraseBlockByPage(block * self.PagePerBlock)
