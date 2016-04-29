#!/usr/bin/env python
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
parser.add_option("-R", action="store_true", dest="raw_mode", default=False,
				help="Raw mode - skip bad block before reading/writing")
parser.add_option("-c", action="store_true", dest="check_ecc", default=False,
				help="Check ECC")

parser.add_option("-O", action="store_true", dest="add_oob", default=False,
				help="Add OOB to the source")
parser.add_option("--OJ", action="store_true", dest="add_jffs2_oob", default=False,
				help="Add JFFS2 OOB to the source")
parser.add_option("-o", action="store_true", dest="remove_oob", default=False,
				help="Remove OOB from the source")

parser.add_option("-u", action="store_true", dest="find_uboot_images", default=False,
				help="Find U-Boot images")
parser.add_option("-U", action="store_true", dest="dump_uboot_images", default=False,
				help="Dump U-Boot images")

parser.add_option("-j", action="store_true", dest="find_jffs2", default=False,
				help="Find JFFS2 Image")
parser.add_option("-J", action="store_true", dest="dump_jffs2", default=False,
				help="Dump JFFS2 Image")
parser.add_option("-n", "--name_prefix", dest="name_prefix", default='',
				help="Set output file name prefix")

parser.add_option("-s", action="store_true", dest="seq", default=False,
				help="Set sequential row read mode - some NAND models supports")
parser.add_option("-S", action="store_true", dest="slow", default=False,
				help="Set clock FTDI chip at 12MHz instead of 60MHz")
parser.add_option("-f", "--filename", dest="filename", default='',
				help="Use file instead of device for operations", metavar="FILENAME")

parser.add_option("-C", "--compare_target_filename", dest="compare_target_filename", default='',
				help="When writing a file compare with this file before writing and write only differences", metavar="COMPARE_TARGET_FILENAME")

parser.add_option("-t", type="int", default=0, dest="offset")
parser.add_option("-p", type="int", nargs=2, dest="pages")
parser.add_option("-b", type="int", nargs=2, dest="blocks")

parser.add_option("-P", type="int", default=512, dest="page_size")
parser.add_option("-E", type="int", default=16, dest="oob_size")
parser.add_option("-K", type="int", default=32, dest="pages_per_block")

(options, args) = parser.parse_args()

use_ansi=False
try:
	import colorama
	colorama.init()
	use_ansi=True
except:
	try:
		import tendo.ansiterm
		use_ansi=True
	except:
		pass

start_page=-1
end_page=-1
if options.pages!=None:
	if len(options.pages)>0:
		start_page=options.pages[0]
	if len(options.pages)>1:
		end_page=options.pages[1]

flash_util=FlashUtil(options.filename,options.page_size, options.oob_size, options.pages_per_block,options.slow)

if not flash_util.IsInitialized():
	print 'Device not ready, aborting...'
	sys.exit(0)

flash_util.SetUseAnsi(use_ansi)

if options.blocks!=None:
	if len(options.blocks)>0:
		start_page=options.blocks[0] * flash_util.io.PagePerBlock
	if len(options.blocks)>1:
		end_page=(options.blocks[1] + 1 ) * flash_util.io.PagePerBlock

if options.information:
	flash_util.io.DumpInfo()

if options.read:
	output_filename=args[0]

	if options.filename:
		if options.add_oob:
			print 'Add OOB to %s' % (options.filename)
			flash_util.AddOOB(options.filename,output_filename)
		else:
			if options.remove_oob:
				print 'Removing OOB from pages(0x%x - 0x%x) to %s' % ( start_page, end_page, output_filename)
			else:
				print 'Copying OOB from pages(0x%x - 0x%x) to %s' % ( start_page, end_page, output_filename)

			flash_util.CopyPages(output_filename,  start_page , end_page, options.remove_oob )
	else:
		flash_util.ReadPages(start_page, end_page, options.remove_oob, output_filename, seq=options.seq, raw_mode=options.raw_mode)

if options.write:
	filename=args[0]
	add_oob=False
	add_jffs2_eraser_marker=False
	if options.add_oob:
		add_oob=True
	if options.add_jffs2_oob:
		add_oob=True
		add_jffs2_eraser_marker=True

	if options.compare_target_filename!='':
		cfd=open(options.compare_target_filename,'rb')
		cfd.seek(options.offset)

		fd=open(filename,'rb')
		fd.seek(options.offset)

		current_page=0
		while 1:
			cdata=cfd.read(flash_util.io.PageSize)
			data=fd.read(flash_util.io.PageSize)

			if not data:
				break

			if cdata!=data:
				print 'Changed Page:0x%x file_offset: 0x%x' % ( start_page+current_page, options.offset + current_page*flash_util.io.PageSize)
				current_block=current_page / flash_util.io.PagePerBlock

				print 'Erasing and re-programming Block: %d' % (current_block)
				flash_util.io.EraseBlockByPage(current_page)
				
				target_start_page=start_page+current_block*flash_util.io.PagePerBlock
				target_end_page=target_start_page+flash_util.io.PagePerBlock-1

				print 'Programming Page: %d ~ %d' % (target_start_page, target_end_page)
				flash_util.io.WritePages(
									filename, 
									options.offset + current_block*flash_util.io.PagePerBlock*flash_util.io.PageSize,
									target_start_page, 
									target_end_page, 
									add_oob, 
									add_jffs2_eraser_marker=add_jffs2_eraser_marker, 
									raw_mode=options.raw_mode
								)
				
				current_page=(current_block+1)*flash_util.io.PagePerBlock+1
				fd.seek(options.offset+current_page * flash_util.io.PageSize)
				cfd.seek(options.offset+current_page * flash_util.io.PageSize)

			else:
				current_page+=1

	else:
		flash_util.io.WritePages(filename, options.offset, start_page, end_page, add_oob, add_jffs2_eraser_marker=add_jffs2_eraser_marker, raw_mode=options.raw_mode)

if options.erase:
	if options.blocks!=None:
		start=options.blocks[0]
		end=options.blocks[1]
		flash_util.io.EraseBlock(start,end)
	else:
		flash_util.io.Erase()

if options.check_bad_blocks:
	flash_util.CheckBadBlocks()

if options.check_ecc:
	flash_util.CheckECC()

if options.find_uboot_images:
	flash_util.FindUBootImages()

if options.dump_uboot_images:
	flash_util.DumpUBootImages()

if options.find_jffs2:
	flash_util.FindJFFS2()

if options.dump_jffs2:
	flash_util.DumpJFFS2(options.name_prefix)
