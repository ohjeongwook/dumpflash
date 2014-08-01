import struct
import zlib

class uImage:
	HEADER_PACK_STR=">LLLLLLLBBBB32s"
	MAGIC=0x27051956

	IH_OS_INVALID=0
	IH_OS_OPENBSD=1
	IH_OS_NETBSD=2
	IH_OS_FREEBSD=3
	IH_OS_4_4BSD=4
	IH_OS_LINUX=5
	IH_OS_SVR4=6
	IH_OS_ESIX=7
	IH_OS_SOLARIS=8
	IH_OS_IRIX=9
	IH_OS_SCO=10
	IH_OS_DELL=11
	IH_OS_NCR=12
	IH_OS_LYNXOS=13
	IH_OS_VXWORKS=14
	IH_OS_PSOS=15
	IH_OS_QNX=16
	IH_OS_U_BOOT=17
	IH_OS_RTEMS=18
	IH_OS_ARTOS=19
	IH_OS_UNITY=20

	IH_OS_STR_INVALID="Invalid OS"
	IH_OS_STR_OPENBSD="OpenBSD"
	IH_OS_STR_NETBSD="NetBSD"
	IH_OS_STR_FREEBSD="FreeBSD"
	IH_OS_STR_4_4BSD="4.4BSD"
	IH_OS_STR_LINUX="Linux"
	IH_OS_STR_SVR4="SVR4"
	IH_OS_STR_ESIX="Esix"
	IH_OS_STR_SOLARIS="Solaris"
	IH_OS_STR_IRIX="Irix"
	IH_OS_STR_SCO="SCO"
	IH_OS_STR_DELL="Dell"
	IH_OS_STR_NCR="NCR"
	IH_OS_STR_LYNXOS="LynxOS"
	IH_OS_STR_VXWORKS="VxWorks"
	IH_OS_STR_PSOS="pSOS"
	IH_OS_STR_QNX="QNX"
	IH_OS_STR_U_BOOT="Firmware"
	IH_OS_STR_RTEMS="RTEMS"
	IH_OS_STR_ARTOS="ARTOS"
	IH_OS_STR_UNITY="Unity OS"

	IH_CPU_INVALID=0
	IH_CPU_ALPHA=1
	IH_CPU_ARM=2
	IH_CPU_I386=3
	IH_CPU_IA64=4
	IH_CPU_MIPS=5
	IH_CPU_MIPS64=6
	IH_CPU_PPC=7
	IH_CPU_S390=8
	IH_CPU_SH=9
	IH_CPU_SPARC=10
	IH_CPU_SPARC64=11
	IH_CPU_M68K=12
	IH_CPU_NIOS=13
	IH_CPU_MICROBLAZE=14
	IH_CPU_NIOS2=15
	IH_CPU_BLACKFIN=16
	IH_CPU_AVR32=17

	IH_CPU_STR_INVALID="Invalid CPU"
	IH_CPU_STR_ALPHA="Alpha"
	IH_CPU_STR_ARM="ARM"
	IH_CPU_STR_I386="Intel x86"
	IH_CPU_STR_IA64="IA64"
	IH_CPU_STR_MIPS="MIPS"
	IH_CPU_STR_MIPS64="MIPS  64 Bit"
	IH_CPU_STR_PPC="PowerPC"
	IH_CPU_STR_S390="IBM S390"
	IH_CPU_STR_SH="SuperH"
	IH_CPU_STR_SPARC="Sparc"
	IH_CPU_STR_SPARC64="Sparc 64 Bit"
	IH_CPU_STR_M68K="M68K"
	IH_CPU_STR_NIOS="Nios-32"
	IH_CPU_STR_MICROBLAZE="MicroBlaze"
	IH_CPU_STR_NIOS2="Nios-II"
	IH_CPU_STR_BLACKFIN="Blackfin"
	IH_CPU_STR_AVR32="AVR32"

	IH_TYPE_INVALID=0
	IH_TYPE_STANDALONE=1
	IH_TYPE_KERNEL=2
	IH_TYPE_RAMDISK=3
	IH_TYPE_MULTI=4
	IH_TYPE_FIRMWARE=5
	IH_TYPE_SCRIPT=6
	IH_TYPE_FILESYSTEM=7
	IH_TYPE_FLATDT=8

	IH_TYPE_STR_INVALID="Invalid Image"
	IH_TYPE_STR_STANDALONE="Standalone Program"
	IH_TYPE_STR_KERNEL="OS Kernel Image"
	IH_TYPE_STR_RAMDISK="RAMDisk Image"
	IH_TYPE_STR_MULTI="Multi-File Image"
	IH_TYPE_STR_FIRMWARE="Firmware Image"
	IH_TYPE_STR_SCRIPT="Script file"
	IH_TYPE_STR_FILESYSTEM="Filesystem Image (any type)"
	IH_TYPE_STR_FLATDT="Binary Flat Device Tree Blob"

	COMP_NONE=0
	COMP_GZIP=1
	COMP_BZIP2=2

	def __init__(self):
		pass

	def GetOSString(self,os):
		if os==self.IH_OS_INVALID:
			return self.IH_OS_STR_INVALID
		if os==self.IH_OS_OPENBSD:
			return self.IH_OS_STR_OPENBSD
		if os==self.IH_OS_NETBSD:
			return self.IH_OS_STR_NETBSD
		if os==self.IH_OS_FREEBSD:
			return self.IH_OS_STR_FREEBSD
		if os==self.IH_OS_4_4BSD:
			return self.IH_OS_STR_4_4BSD
		if os==self.IH_OS_LINUX:
			return self.IH_OS_STR_LINUX
		if os==self.IH_OS_SVR4:
			return self.IH_OS_STR_SVR4
		if os==self.IH_OS_ESIX:
			return self.IH_OS_STR_ESIX
		if os==self.IH_OS_SOLARIS:
			return self.IH_OS_STR_SOLARIS
		if os==self.IH_OS_IRIX:
			return self.IH_OS_STR_IRIX
		if os==self.IH_OS_SCO:
			return self.IH_OS_STR_SCO
		if os==self.IH_OS_DELL:
			return self.IH_OS_STR_DELL
		if os==self.IH_OS_NCR:
			return self.IH_OS_STR_NCR
		if os==self.IH_OS_LYNXOS:
			return self.IH_OS_STR_LYNXOS
		if os==self.IH_OS_VXWORKS:
			return self.IH_OS_STR_VXWORKS
		if os==self.IH_OS_PSOS:
			return self.IH_OS_STR_PSOS
		if os==self.IH_OS_QNX:
			return self.IH_OS_STR_QNX
		if os==self.IH_OS_U_BOOT:
			return self.IH_OS_STR_U_BOOT
		if os==self.IH_OS_RTEMS:
			return self.IH_OS_STR_RTEMS
		if os==self.IH_OS_ARTOS:
			return self.IH_OS_STR_ARTOS
		if os==self.IH_OS_UNITY:
			return self.IH_OS_STR_UNITY
		return ""

	def GetArchString(self,arch):
		if arch==self.IH_CPU_INVALID:
			return self.IH_CPU_STR_INVALID
		elif arch==self.IH_CPU_ALPHA:
			return self.IH_CPU_STR_ALPHA
		elif arch==self.IH_CPU_ARM:
			return self.IH_CPU_STR_ARM
		elif arch==self.IH_CPU_I386:
			return self.IH_CPU_STR_I386
		elif arch==self.IH_CPU_IA64:
			return self.IH_CPU_STR_IA64
		elif arch==self.IH_CPU_MIPS:
			return self.IH_CPU_STR_MIPS
		elif arch==self.IH_CPU_MIPS64:
			return self.IH_CPU_STR_MIPS64
		elif arch==self.IH_CPU_PPC:
			return self.IH_CPU_STR_PPC
		elif arch==self.IH_CPU_S390:
			return self.IH_CPU_STR_S390
		elif arch==self.IH_CPU_SH:
			return self.IH_CPU_STR_SH
		elif arch==self.IH_CPU_SPARC:
			return self.IH_CPU_STR_SPARC
		elif arch==self.IH_CPU_SPARC64:
			return self.IH_CPU_STR_SPARC64
		elif arch==self.IH_CPU_M68K:
			return self.IH_CPU_STR_M68K
		elif arch==self.IH_CPU_NIOS:
			return self.IH_CPU_STR_NIOS
		elif arch==self.IH_CPU_MICROBLAZE:
			return self.IH_CPU_STR_MICROBLAZE
		elif arch==self.IH_CPU_NIOS2:
			return self.IH_CPU_STR_NIOS2
		elif arch==self.IH_CPU_BLACKFIN:
			return self.IH_CPU_STR_BLACKFIN
		elif arch==self.IH_CPU_AVR32:
			return self.IH_CPU_STR_AVR32

		return "Unknown"

	def GetTypeString(self,type):
		if type==self.IH_TYPE_INVALID:
			return self.IH_TYPE_STR_INVALID
		elif type==self.IH_TYPE_STANDALONE:
			return self.IH_TYPE_STR_STANDALONE
		elif type==self.IH_TYPE_KERNEL:
			return self.IH_TYPE_STR_KERNEL
		elif type==self.IH_TYPE_RAMDISK:
			return self.IH_TYPE_STR_RAMDISK
		elif type==self.IH_TYPE_MULTI:
			return self.IH_TYPE_STR_MULTI
		elif type==self.IH_TYPE_FIRMWARE:
			return self.IH_TYPE_STR_FIRMWARE
		elif type==self.IH_TYPE_SCRIPT:
			return self.IH_TYPE_STR_SCRIPT
		elif type==self.IH_TYPE_FILESYSTEM:
			return self.IH_TYPE_STR_FILESYSTEM
		elif type==self.IH_TYPE_FLATDT:
			return self.IH_TYPE_STR_FLATDT
		return ""

	def GetCompString(self,comp):
		if comp==self.COMP_NONE:
			return "None"
		elif comp==self.COMP_GZIP:
			return "gzip"
		elif comp==self.COMP_BZIP2:
			return "bzip2"

	def ParseFile(self,filename):
		self.filename=filename
		fd=open(self.filename,'rb')
		header=fd.read(0x40)
		fd.close()

		self.ParseHeader(header)

	def ParseHeader(self,header):
		(self.magic,self.hcrc,self.time,self.size,self.load,self.ep,self.dcrc,self.os,self.arch,self.type,self.comp,self.name)=struct.unpack(self.HEADER_PACK_STR, header)

	def DumpHeader(self):
		print 'Magic:\t0x%x'% (self.magic)
		print 'HCRC:\t0x%x'% (self.hcrc)
		print 'Time:\t0x%x'% (self.time)
		print 'Size:\t0x%x'% (self.size)
		print 'Load:\t0x%x'% (self.load)
		print 'EP:\t0x%x'% (self.ep)
		print 'DCRC:\t0x%x'% (self.dcrc)
		print 'OS:\t0x%x (%s)'% (self.os, self.GetOSString(self.os))
		print 'Arch:\t0x%x (%s)'% (self.arch, self.GetArchString(self.arch))
		print 'Type:\t0x%x (%s)'% (self.type, self.GetTypeString(self.type))
		print 'Comp:\t0x%x (%s)'% (self.comp, self.GetCompString(self.comp))
		print 'Name:\t%s'% (self.name)

	def CheckCRC(self):
		fd=open(self.filename,'rb')
		header=fd.read(0x40)
		data=fd.read(self.size)
		fd.close()

		print 'Read %08X bytes out of %08X' % (len(data), self.size)
		new_header=header[0:4] + struct.pack("L",0) + header[8:]
		print '%08X' % (zlib.crc32(new_header) & 0xFFFFFFFF)
		print '%08X' % (zlib.crc32(data) & 0xFFFFFFFF)

	def FixHeader(self):
		fd=open(self.filename,'rb')
		header=fd.read(0x40)
		data=fd.read(self.size)
		fd.close()

		print 'New length: 0x%08x / Original length: 0x%08x' % (len(data), self.size)

		self.dcrc=zlib.crc32(data)& 0xFFFFFFFF
		print 'New DCRC: %08x' % self.dcrc

		new_header=header[0:4] + struct.pack("L",0) + header[8:]
		self.size=len(data)
		self.hcrc=0
		header=struct.pack(self.HEADER_PACK_STR, self.magic,self.hcrc,self.time,self.size,self.load,self.ep,self.dcrc,self.os,self.arch,self.type,self.comp,self.name)

		self.hcrc=zlib.crc32(header)& 0xFFFFFFFF
		print 'New HCRC: %08X' % self.hcrc

		header=struct.pack(self.HEADER_PACK_STR, self.magic,self.hcrc,self.time,self.size,self.load,self.ep,self.dcrc,self.os,self.arch,self.type,self.comp,self.name)
		
		fd=open(self.filename,'rb+')
		fd.write(header)
		fd.close()

	def CheckCRC(self):
		fd=open(self.filename,'rb')
		header=fd.read(0x40)
		data=fd.read(self.size)
		fd.close()

		print 'Read 0x%08x bytes out of 0x%08x' % (len(data), self.size)
		new_header=header[0:4] + struct.pack("L",0) + header[8:]
		print 'HCRC: 0x%08x' % (zlib.crc32(new_header) & 0xFFFFFFFF)
		print 'DCRC: 0x%08x' % (zlib.crc32(data) & 0xFFFFFFFF)

	def Extract(self):
		seq=0
		if self.type==self.IH_TYPE_MULTI:
			fd=open(self.filename,'rb')
			fd.seek(0x40)
			lengths=[]
			while 1:
				(length,)=struct.unpack(">L",fd.read(4))

				if length>0:
					print "Found multi image of length 0x%x" % (length)
					lengths.append(length)
				elif length==0:
					break

			for length in lengths:
				data=fd.read(length)

				wfilename="%s-%.2d" % (self.filename, seq)
				seq+=1
				print "Extracting to %s" % wfilename
				wfd=open(wfilename, "wb")
				wfd.write(data)
				wfd.close()

			fd.close()
		else:
			fd=open(self.filename,'rb')
			fd.seek(0x40)
			data=fd.read(self.size)
			fd.close()

			if self.comp==self.COMP_NONE:
				wfilename="%s-%.2d" % (self.filename, seq)
				print "Extracting to %s" % wfilename
				wfd=open(wfilename, "wb")
				wfd.write(data)
				wfd.close()

		

if __name__=='__main__':
	import sys

	from optparse import OptionParser
	parser = OptionParser()

	parser.add_option("-f", action="store_true", dest="fix_header", default=False)
	parser.add_option("-c", action="store_true", dest="check_crc", default=False)
	parser.add_option("-e", action="store_true", dest="extract", default=False)

	(options, args) = parser.parse_args()
	filename=args[0]

	uimage=uImage()
	uimage.ParseFile(filename)
	uimage.DumpHeader()

	if options.fix_header:
		uimage.FixHeader()

	elif options.check_crc:
		uimage.CheckCRC()

	elif options.extract:
		uimage.Extract()

