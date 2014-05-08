import sys
import struct
import pprint
import os
from zlib import decompress

filename=sys.argv[1]

fd=open(filename,'rb')
data=fd.read()
fd.close()

JFFS2_COMPR_NONE	= 0x00
JFFS2_COMPR_ZERO	= 0x01
JFFS2_COMPR_RTIME	= 0x02
JFFS2_COMPR_RUBINMIPS	= 0x03
JFFS2_COMPR_COPY	= 0x04
JFFS2_COMPR_DYNRUBIN	= 0x05
JFFS2_COMPR_ZLIB	= 0x06
JFFS2_COMPR_LZO	= 0x07

# Compatibility flags. 
JFFS2_COMPAT_MASK	= 0xc000 
JFFS2_NODE_ACCURATE	= 0x2000

# INCOMPAT: Fail to mount the filesystem 
JFFS2_FEATURE_INCOMPAT	= 0xc000

# ROCOMPAT: Mount read-only 
JFFS2_FEATURE_ROCOMPAT	= 0x8000

# RWCOMPAT_COPY: Mount read/write, and copy the node when it's GC'd 
JFFS2_FEATURE_RWCOMPAT_COPY	= 0x4000

# RWCOMPAT_DELETE: Mount read/write, and delete the node when it's GC'd 
JFFS2_FEATURE_RWCOMPAT_DELETE	= 0x0000
JFFS2_NODETYPE_DIRENT	= (JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 1)
JFFS2_NODETYPE_INODE	= (JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 2)
JFFS2_NODETYPE_CLEANMARKER	= (JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 3)
JFFS2_NODETYPE_PADDING	= (JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 4)
JFFS2_NODETYPE_SUMMARY	= (JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 6)
JFFS2_NODETYPE_XATTR	= (JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 8)
JFFS2_NODETYPE_XREF	= (JFFS2_FEATURE_INCOMPAT | JFFS2_NODE_ACCURATE | 9)

# XATTR Related 
JFFS2_XPREFIX_USER	= 1 # for "user." 
JFFS2_XPREFIX_SECURITY	= 2 # for "security." 
JFFS2_XPREFIX_ACL_ACCESS	= 3 # for "system.posix_acl_access" 
JFFS2_XPREFIX_ACL_DEFAULT	= 4 # for "system.posix_acl_default" 
JFFS2_XPREFIX_TRUSTED	= 5 # for "trusted.*" 
JFFS2_ACL_VERSION	= 0x0001
JFFS2_NODETYPE_CHECKPOINT	= (JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 3)
JFFS2_NODETYPE_OPTIONS	= (JFFS2_FEATURE_RWCOMPAT_COPY | JFFS2_NODE_ACCURATE | 4)
JFFS2_INO_FLAG_PREREAD	= 1 # Do read_inode() for this one at
JFFS2_INO_FLAG_USERCOMPR	= 2 # User has requested a specific


header_unpack_fmt="<HHL"
header_struct_size=struct.calcsize(header_unpack_fmt)

inode_unpack_fmt="<LLLLHHLLLLLLLBBHLL"
inode_struct_size=struct.calcsize(inode_unpack_fmt)

dirent_unpack_fmt="<LLLLLBBBLL"
dirent_struct_size=struct.calcsize(dirent_unpack_fmt)

data_offset = 0
total_count = 0

last_magic = 0
last_nodetype = 0
last_totlen = 0
last_data_offset = 0

inode_map = {}
dirent_map = {}

while 1:
	error=False

	try:
		(magic,nodetype,totlen) = struct.unpack(header_unpack_fmt, data[data_offset:data_offset+header_struct_size])
	except:
		break

	if magic!=0x1985:
		print '* Magic Error:', hex(data_offset), "(", hex(magic), ",", hex(nodetype), ")" 
		print '\tLast record:', hex(last_data_offset), "(", hex(last_magic), ",", hex(last_nodetype), ",", hex(last_totlen), ")" 
		while data_offset < len(data):
			tag = data[data_offset:data_offset+4]
			if tag=='\x85\x19\x02\xe0':
				print '\tFound next inode', hex(data_offset)
				print ''
				break
			data_offset+=0x4
	
		if data_offset < len(data):
			(magic, nodetype,totlen) = struct.unpack(header_unpack_fmt, data[data_offset:data_offset+header_struct_size])

		if magic!=0x1985:
			break

	if nodetype==JFFS2_NODETYPE_INODE:
		(hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc) = struct.unpack(inode_unpack_fmt, data[data_offset+header_struct_size:data_offset+header_struct_size+inode_struct_size])

		payload = data[data_offset+0x44: data_offset+0x44+csize]
			
		if compr == 0x6:
			#print "compressed payload length:", hex(len(payload))
			#pprint.pprint(payload)
			try:
				payload=decompress(payload)
			except:
				print "* Uncompress error"
				error=True
				pass

			#print "payload length:", len(payload)

		#pprint.pprint(payload)

		if not inode_map.has_key(ino):
			inode_map[ino] = []

		inode_map[ino].append( {
				"hdr_crc": hdr_crc, 
				"version": version, 
				"mode": mode, 
				"uid": uid, 
				"gid": gid, 
				"isize": isize, 
				"atime": atime, 
				"mtime": mtime, 
				"ctime": ctime, 
				"offset": offset, 
				"csize": csize, 
				"dsize": dsize, 
				"compr": compr, 
				"usercompr": usercompr, 
				"flags": flags, 
				"data_crc": data_crc, 
				"node_crc": node_crc, 
				"payload": payload
			})

		if error:
			print '='*79
			print 'data_offset:\t',hex(data_offset)
			print "magic:\t\t%x" % magic
			print "nodetype:\t%x" % nodetype
			print "totlen:\t\t%x" % totlen
			print "hdr_crc:\t%x" % hdr_crc
			print "ino:\t\t%x" % ino
			print "version:\t%x" % version
			print "mode:\t\t%x" % mode
			print "uid:\t\t%x" % uid
			print "gid:\t\t%x" % gid
			print "isize:\t\t%x" % isize
			print "atime:\t\t%x" % atime
			print "mtime:\t\t%x" % mtime
			print "ctime:\t\t%x" % ctime
			print "offset:\t\t%x" % offset
			print "csize:\t\t%x" % csize
			print "dsize:\t\t%x" % dsize
			print "compr:\t\t%x" % compr
			print "usercompr:\t%x" % usercompr
			print "flags:\t\t%x" % flags
			print "data_crc:\t%x" % data_crc
			print "node_crc:\t%x" % node_crc
			print ''


	elif nodetype==JFFS2_NODETYPE_DIRENT:
		(hdr_crc, pino, version, ino, mctime, nsize, ent_type, unused, node_crc, name_crc) = struct.unpack(dirent_unpack_fmt, data[data_offset+header_struct_size:data_offset+header_struct_size+dirent_struct_size])

		hdr_crc, pino, version, ino, mctime, nsize, type, unused, node_crc, name_crc

		payload = data[data_offset+header_struct_size+dirent_struct_size+1: data_offset+header_struct_size+dirent_struct_size+1+nsize]

		if not dirent_map.has_key(ino) or dirent_map[ino]['version']<version:
			dirent_map[ino] = {
					"hdr_crc": hdr_crc, 
					"pino": pino, 
					"version": version, 
					"mctime": mctime, 
					"nsize": nsize, 
					"ent_type": ent_type, 
					"node_crc": node_crc, 
					"name_crc": name_crc, 
					"payload": payload
				}

		if 0==1:
			print '='*79
			print 'data_offset:\t',hex(data_offset)
			print "magic:\t\t%x" % magic
			print "nodetype:\t%x" % nodetype
			print "totlen:\t\t%x" % totlen
			print "hdr_crc:\t%x" % hdr_crc
			print "pino:\t\t%x" % pino
			print "version:\t\t%x" % version
			print "ino:\t\t%x" % ino
			print "node_crc:\t%x" % node_crc
			print ''

	elif nodetype==0x2004:
		pass

	else:
		print '='*79
		print 'data_offset:\t',hex(data_offset)
		print "magic:\t\t%x" % magic
		print "nodetype:\t%x" % nodetype
		print "totlen:\t\t%x" % totlen
		
	(last_magic, last_nodetype, last_totlen) = (magic, nodetype, totlen)

	last_data_offset = data_offset

	if totlen%4 !=0 :
		totlen += 4-(totlen%4)
	
	data_offset += totlen

	current_page_data_len = data_offset % 0x200 
	if (0x200-current_page_data_len) < 0x8:
		data_offset += 0x200-current_page_data_len

	#print '* Record (@%x):\tMagic: %x\tType: %x\tTotlen %x\tPadded Totlen: %x' % (last_data_offset, last_magic, last_nodetype, last_totlen, totlen)
	total_count += 1

print "Total Count:",total_count

#pprint.pprint(dirent_map)

def get_data(inode_map_record):
	next_offset=0
	data=''
	while 1:
		found_record=False
		for record in inode_map_record:
			offset = record['offset']
			if offset == next_offset:
				next_offset = offset + record['dsize']

				if next_offset != offset:
					found_record=True
				data += record['payload']
				break
	
		if not found_record:
			break

	return data

for ino in dirent_map.keys():
	if inode_map.has_key(ino):
		filename = dirent_map[ino]["payload"]
		fd=open(os.path.join("tmp", filename),"wb")
		fd.write(get_data(inode_map[ino]))
		fd.close()
