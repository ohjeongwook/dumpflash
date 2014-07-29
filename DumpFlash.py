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

parser.add_option("-c", "--command", dest="command", default='',
				help="Commands (CheckBadBlocks, CheckECC, DumpJFFS2, AddOOB, RemoveOOB)", metavar="COMMAND")

parser.add_option("-O", "--output", dest="output",
                help="Output filename", metavar="OUTPUT")

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
	
(options, args) = parser.parse_args()

start_page=-1
end_page=-1
if options.pages!=None:
	if len(options.pages)>0:
		start_page=options.pages[0]
	if len(options.pages)>1:
		end_page=options.pages[1]

if options.filename:
	flash = FlashPage()

	if flash.Open(filename):
		if options.command=="CheckBadBlocks":
			print 'Check bad blocks:'
			flash.CheckBadBlocks()
	
		if options.command=="CheckECC":
			print 'Check ECC:'
			flash.CheckECC()
	
		if options.command=="DumpJFFS2":
			print 'Dump JFFS2:'
			flash.DumpJFFS2()

		if options.command=="RemoveOOB":
			start=0
			end=-1
			if options.pages!=None:
				start=options.pages[0]
				end=options.pages[1]

			print 'Extract pages(%x - %x) to %s' % ( start, end, options.output)
			flash.RemoveOOB(options.output,  start, end)

		if options.command=="AddOOB":
			flash.AddOOB(filename,options.output,options.size)

		flash.Close()

else:
	nand_tool = NandTool(options.slow)

	nand_tool.DumpInfo()
	if options.information:
		pass

	elif options.blocks!=None:
		if len(options.blocks)>0:
			start_page=options.blocks[0] * nand_tool.PagePerBlock
		if len(options.blocks)>1:
			end_page=(options.blocks[1] + 1 ) * nand_tool.PagePerBlock

	"""
	if options.DumpJFFS2:
		[minimum_pageno, maximum_pageno] = nand_tool.CheckJFFS2()
		start_page=minimum_pageno
		end_page=maximum_pageno
	"""

	if options.read:
		filename=args[0]
		if options.seq:
			nand_tool.readSeqPages(filename, start_page, end_page, options.RemoveOOB)
		else:
			nand_tool.readPages(filename, start_page, end_page, options.RemoveOOB)

	if options.write:
		filename=args[0]
		nand_tool.writePages(filename, options.offset, start_page, end_page)

	if options.command=="CheckBadBlocks":
		nand_tool.CheckBadBlocks()

	if options.command=="CheckJFFS2":
		nand_tool.CheckJFFS2()

	if options.erase:
		nand_tool.EraseBlock(options.blocks[0], options.blocks[1])
