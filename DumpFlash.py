from optparse import OptionParser
from FlashPage import *
from FlashIO import *

parser = OptionParser()

parser.add_option("-i", action="store_true", dest="information", default=False)

parser.add_option("-r", action="store_true", dest="read", default=False,
				help="Read NAND Flash to a file")
parser.add_option("-w", action="store_true", dest="write", default=False,
				help="Write file to a NAND Flash")
parser.add_option("-e", action="store_true", dest="erase", default=False,
				help="Erase")
parser.add_option("-u", action="store_true", dest="find_uboot_images", default=False,
				help="Find U-Boot images")
parser.add_option("-c", "--command", dest="command", default='',
				help="Commands (CheckBadBlocks, CheckECC, DumpJFFS2, AddOOB)", metavar="COMMAND")

parser.add_option("-B", action="store_true", dest="RemoveOOB", default=False,
				help="Remove OOB when processing")
parser.add_option("-s", action="store_true", dest="seq", default=False,
				help="Set sequential row read mode - some NAND models supports")
parser.add_option("-S", action="store_true", dest="slow", default=False,
				help="Set clock FTDI chip at 12MHz instead of 60MHz")
parser.add_option("-f", "--filename", dest="filename", default='',
				help="Use file instead of device for operations", metavar="FILENAME")
parser.add_option("-o", type="int", default=0, dest="offset")
parser.add_option("-p", type="int", nargs=2, dest="pages")
parser.add_option("-b", type="int", nargs=2, dest="blocks")
parser.add_option("-z", type="int", default=0, dest="size")
	
parser.add_option("-P", type="int", default=512, dest="page_size")
parser.add_option("-E", type="int", default=16, dest="oob_size")
parser.add_option("-K", type="int", default=32, dest="pages_per_block")

(options, args) = parser.parse_args()

start_page=-1
end_page=-1
if options.pages!=None:
	if len(options.pages)>0:
		start_page=options.pages[0]
	if len(options.pages)>1:
		end_page=options.pages[1]

if options.filename:
	flash_page = Page()
	flash_page.SetPageInfo(options.page_size, options.oob_size, options.pages_per_block)

	if options.blocks!=None:
		if len(options.blocks)>0:
			start_page=options.blocks[0] * options.pages_per_block
		if len(options.blocks)>1:
			end_page=(options.blocks[1] + 1 ) * options.pages_per_block

	if flash_page.Open(options.filename):
		if options.command=="CheckBadBlocks":
			print 'Check bad blocks:'
			flash_page.CheckBadBlocks()
	
		if options.command=="CheckECC":
			print 'Check ECC:'
			flash_page.CheckECC()
	
		if options.command=="DumpJFFS2":
			print 'Dump JFFS2:'
			flash_page.DumpJFFS2()

		if options.RemoveOOB:
			print 'Extract pages(0x%x - 0x%x) to %s' % ( start_page, end_page, args[0])
			flash_page.RemoveOOBByPage(args[0],  start_page , end_page )

		if options.command=="AddOOB":
			flash_page.AddOOB(filename,args[0],options.size)

		if options.find_uboot_images:
			flash_page.FindUBootImages()

		flash_page.Close()

else:
	nand_io = NandIO(options.slow)

	nand_io.DumpInfo()
	if options.information:
		pass

	if options.blocks!=None:
		if len(options.blocks)>0:
			start_page=options.blocks[0] * nand_io.PagePerBlock
		if len(options.blocks)>1:
			end_page=(options.blocks[1] + 1 ) * nand_io.PagePerBlock

	"""
	if options.DumpJFFS2:
		[minimum_pageno, maximum_pageno] = nand_io.CheckJFFS2()
		start_page=minimum_pageno
		end_page=maximum_pageno
	"""

	if options.read:
		filename=args[0]
		if options.seq:
			nand_io.readSeqPages(filename, start_page, end_page, options.RemoveOOB)
		else:
			nand_io.readPages(filename, start_page, end_page, options.RemoveOOB)

	if options.write:
		filename=args[0]
		nand_io.writePages(filename, options.offset, start_page, end_page)

	if options.command=="CheckBadBlocks":
		nand_io.CheckBadBlocks()

	if options.command=="CheckJFFS2":
		nand_io.CheckJFFS2()

	if options.erase:
		nand_io.EraseBlock(options.blocks[0], options.blocks[1])
