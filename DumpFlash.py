from optparse import OptionParser
from FlashFile import *
from FlashDevice import *
from FlashUtil import *

parser = OptionParser()

parser.add_option("-i", action="store_true", dest="information", default=False)

parser.add_option("-r", action="store_true", dest="read", default=False,
				help="Read NAND Flash to a file")
parser.add_option("-w", action="store_true", dest="write", default=False,
				help="Write file to a NAND Flash")
parser.add_option("-e", action="store_true", dest="erase", default=False,
				help="Erase")
parser.add_option("-B", action="store_true", dest="check_bad_blocks", default=False,
				help="Check bad blocks")
parser.add_option("-C", action="store_true", dest="check_ecc", default=False,
				help="Check ECC")

parser.add_option("-o", action="store_true", dest="add_oob", default=False,
				help="Add OOB to the source")
parser.add_option("-O", action="store_true", dest="remove_oob", default=False,
				help="Remove OOB from the source")

parser.add_option("-u", action="store_true", dest="find_uboot_images", default=False,
				help="Find U-Boot images")
parser.add_option("-U", action="store_true", dest="dump_uboot_images", default=False,
				help="Dump U-Boot images")

parser.add_option("-j", action="store_true", dest="find_jffs2", default=False,
				help="Find JFFS2 Image")

parser.add_option("-s", action="store_true", dest="seq", default=False,
				help="Set sequential row read mode - some NAND models supports")
parser.add_option("-S", action="store_true", dest="slow", default=False,
				help="Set clock FTDI chip at 12MHz instead of 60MHz")
parser.add_option("-f", "--filename", dest="filename", default='',
				help="Use file instead of device for operations", metavar="FILENAME")

parser.add_option("-s", type="int", default=0, dest="offset")
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

flash_util=FlashUtil(options.filename,options.page_size, options.oob_size, options.pages_per_block,options.slow)

if options.blocks!=None:
	if len(options.blocks)>0:
		start_page=options.blocks[0] * flash_util.io.PagePerBlock
	if len(options.blocks)>1:
		end_page=(options.blocks[1] + 1 ) * flash_util.io.PagePerBlock

if options.information:
	flash_util.io.DumpInfo()

if options.read:
	filename=args[0]
	if options.seq:
		flash_util.readSeqPages(start_page, end_page, options.RemoveOOB, filename)
	else:
		flash_util.readPages(start_page, end_page, options.RemoveOOB, filename)

if options.write:
	filename=args[0]
	flash_util.writePages(filename, options.offset, start_page, end_page)

if options.erase:
	flash_util.EraseBlock(options.blocks[0], options.blocks[1])

if options.check_bad_blocks:
	flash_util.CheckBadBlocks()

if options.check_ecc:
	flash_util.CheckECC()

if options.add_oob:
	output_filename = args[0]
	print 'Remove OOB from pages(0x%x - 0x%x) to %s' % ( start_page, end_page, output_filename)
	flash_util.AddOOB(filename,output_filename,options.size)

if options.remove_oob:
	output_filename = args[0]
	print 'Remove OOB from pages(0x%x - 0x%x) to %s' % ( start_page, end_page, output_filename)
	flash_util.RemoveOOBByPage(output_filename,  start_page , end_page )

if options.find_uboot_images:
	flash_util.FindUBootImages()

if options.dump_uboot_images:
	flash_util.DumpUBootImages()

if options.find_jffs2:
	flash_util.FindJFFS2()

if options.DumpJFFS2:
	[minimum_pageno, maximum_pageno] = flash_util.FindJFFS2()
	start_page=minimum_pageno
	end_page=maximum_pageno