"""TODO"""
# pylint: disable=invalid-name
# pylint: disable=line-too-long
import sys
from optparse import OptionParser
import flashimage

parser = OptionParser()

parser.add_option("-c", dest = "command", default = "information", help = "Command (i[nformation], r[ead], w[rite], erase, e[xtract], extract_pages, add_oob, check_ecc, find_uboot, dump_uboot,find_jffs2, dump_jffs2, check_bad_blocks)")
parser.add_option("-i", dest = "raw_image_filename", default = '', help = "Use file instead of device for operations")
parser.add_option("-o", dest = "output_filename", default = 'output.dmp', help = "Output filename")

parser.add_option("-s", action = "store_true", dest = "seq", default = False, help = "Set sequential row read mode - some NAND models supports this")
parser.add_option("-L", action = "store_true", dest = "slow", default = False, help = "Set clock FTDI chip at 12MHz instead of 60MHz")
parser.add_option("-R", action = "store_true", dest = "raw_mode", default = False, help = "Raw mode - skip bad block before reading/writing")

parser.add_option("-j", action = "store_true", dest = "add_jffs2_oob", default = False, help = "Add JFFS2 OOB to the source")
parser.add_option("-C", dest = "compare_target_filename", default = '', help = "When writing a file compare with this file before writing and write only differences", metavar = "COMPARE_TARGET_FILENAME")


parser.add_option("-n", dest = "name_prefix", default = '', help = "Set output file name prefix")

parser.add_option("-t", type = "int", default = 0, dest = "offset")
parser.add_option("-l", type = "int", default = 0, dest = "length")

parser.add_option("-p", type = "int", nargs = 2, dest = "pages")
parser.add_option("-b", type = "int", nargs = 2, dest = "blocks")

parser.add_option("-P", type = "int", default = 512, dest = "page_size")
parser.add_option("-E", type = "int", default = 16, dest = "oob_size")
parser.add_option("-K", type = "int", default = 32, dest = "pages_per_block")

(options, args) = parser.parse_args()

use_ansi = False
try:
    import colorama
    colorama.init()
    use_ansi = True
except:
    try:
        import tendo.ansiterm
        use_ansi = True
    except:
        pass

start_page = -1
end_page = -1
if options.pages is not None:
    start_page = options.pages[0]
    if len(options.pages) > 1:
        end_page = options.pages[1]

print("options.offset: %x" % options.offset)
flash_io = flashimage.IO(options.raw_image_filename, options.offset, options.length, options.page_size, options.oob_size, options.pages_per_block, options.slow)

if not flash_io.IsInitialized():
    print('Device not ready, aborting...')
    sys.exit(0)

flash_io.SetUseAnsi(use_ansi)

if options.blocks is not None:
    if not options.blocks:
        start_page = options.blocks[0] * flash_io.SrcImage.PagePerBlock
    if len(options.blocks) > 1:
        end_page = (options.blocks[1] + 1) * flash_io.SrcImage.PagePerBlock

if options.command[0] == 'i':
    flash_io.SrcImage.DumpInfo()

elif options.command[0] == 'r':
    flash_io.ReadPages(start_page, end_page, False, options.output_filename, seq = options.seq, raw_mode = options.raw_mode)

elif options.command[0] == 'add_oob':
    if options.raw_image_filename:
        print('Add OOB to %s' % (options.raw_image_filename))
        flash_io.AddOOB(options.raw_image_filename, options.output_filename)

elif options.command == 'extract_pages':
    if options.raw_image_filename:
        print('Extract from pages(0x%x - 0x%x) to %s' % (start_page, end_page, options.output_filename))
        flash_io.ExtractPages(options.output_filename, start_page, end_page, remove_oob = False)

elif options.command[0] == 'e':
    if options.raw_image_filename:
        print('Extract data from pages(0x%x - 0x%x) to %s' % (start_page, end_page, options.output_filename))
        flash_io.ExtractPages(options.output_filename, start_page, end_page, remove_oob = True)

elif options.command[0] == 'w':
    filename = args[0]
    add_oob = False
    add_jffs2_eraser_marker = False
    if options.command == 'add_oob':
        add_oob = True

    if options.add_jffs2_oob:
        add_oob = True
        add_jffs2_eraser_marker = True

    if options.compare_target_filename != '':
        cfd = open(options.compare_target_filename, 'rb')
        cfd.seek(options.offset)

        fd = open(filename, 'rb')
        fd.seek(options.offset)

        current_page = 0
        while 1:
            cdata = cfd.read(flash_io.SrcImage.PageSize)
            data = fd.read(flash_io.SrcImage.PageSize)

            if not data:
                break

            if cdata != data:
                print('Changed Page:0x%x file_offset: 0x%x' % (start_page+current_page, options.offset + current_page*flash_io.SrcImage.PageSize))
                current_block = current_page / flash_io.SrcImage.PagePerBlock

                print('Erasing and re-programming Block: %d' % (current_block))
                flash_io.SrcImage.EraseBlockByPage(current_page)

                target_start_page = start_page+current_block*flash_io.SrcImage.PagePerBlock
                target_end_page = target_start_page+flash_io.SrcImage.PagePerBlock-1

                print('Programming Page: %d ~ %d' % (target_start_page, target_end_page))
                flash_io.SrcImage.WritePages(
                    filename, 
                    options.offset + current_block*flash_io.SrcImage.PagePerBlock*flash_io.SrcImage.PageSize, 
                    target_start_page, 
                    target_end_page, 
                    add_oob, 
                    add_jffs2_eraser_marker = add_jffs2_eraser_marker, 
                    raw_mode = options.raw_mode
                )

                current_page = (current_block+1)*flash_io.SrcImage.PagePerBlock+1
                fd.seek(options.offset+current_page * flash_io.SrcImage.PageSize)
                cfd.seek(options.offset+current_page * flash_io.SrcImage.PageSize)

            else:
                current_page += 1

    else:
        flash_io.SrcImage.WritePages(filename, options.offset, start_page, end_page, add_oob, add_jffs2_eraser_marker = add_jffs2_eraser_marker, raw_mode = options.raw_mode)

elif options.command == 'erase':
    if options.blocks is not None:
        start = options.blocks[0]
        end = options.blocks[1]
        flash_io.SrcImage.EraseBlock(start, end)
    else:
        flash_io.SrcImage.Erase()

if options.command == 'check_bad_blocks':
    flash_io.CheckBadBlocks()

if options.command == 'check_ecc':
    flash_io.CheckECC()

elif options.command == 'find_uboot':
    flash_io.FindUBootImages()

elif options.command == 'dump_uboot':
    flash_io.DumpUBootImages()

elif options.command == 'find_jffs2':
    flash_io.FindJFFS2()

elif options.command == 'dump_jffs2':
    flash_io.DumpJFFS2(options.name_prefix)
