# pylint: disable=invalid-name
# pylint: disable=line-too-long
import struct
import pprint
import os
import zlib
import shutil
import crc32

JFFS2_COMPR_NONE    = 0x00
JFFS2_COMPR_ZERO    = 0x01
JFFS2_COMPR_RTIME    = 0x02
JFFS2_COMPR_RUBINMIPS    = 0x03
JFFS2_COMPR_COPY    = 0x04
JFFS2_COMPR_DYNRUBIN    = 0x05
JFFS2_COMPR_ZLIB    = 0x06
JFFS2_COMPR_LZO    = 0x07

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
JFFS2_XPREFIX_USER	= 1 # for 'user.'
JFFS2_XPREFIX_SECURITY	= 2 # for 'security.'
JFFS2_XPREFIX_ACL_ACCESS	= 3 # for 'system.posix_acl_access'
JFFS2_XPREFIX_ACL_DEFAULT	= 4 # for 'system.posix_acl_default'
JFFS2_XPREFIX_TRUSTED	= 5 # for 'trusted.*'
JFFS2_ACL_VERSION	= 0x0001
JFFS2_NODETYPE_CHECKPOINT	= (JFFS2_FEATURE_RWCOMPAT_DELETE | JFFS2_NODE_ACCURATE | 3)
JFFS2_NODETYPE_OPTIONS	= (JFFS2_FEATURE_RWCOMPAT_COPY | JFFS2_NODE_ACCURATE | 4)
JFFS2_INO_FLAG_PREREAD	= 1 # Do read_inode() for this one at
JFFS2_INO_FLAG_USERCOMPR	= 2 # User has requested a specific


header_unpack_fmt = '<HHL'
header_struct_size = struct.calcsize(header_unpack_fmt)

inode_unpack_fmt = '<LLLLHHLLLLLLLBBHLL'
inode_struct_size = struct.calcsize(inode_unpack_fmt)

dirent_unpack_fmt = '<LLLLLBBBLL'
dirent_struct_size = struct.calcsize(dirent_unpack_fmt)

class JFFS:
    DebugLevel = 0
    DumpMagicError = False
    def __init__(self):
        self.INodeMap = {}
        self.DirentMap = {}
        self.OrigFilename = None

    def parse(self, filename, target_filename = ''):
        self.OrigFilename = filename
        fd = open(filename, 'rb')
        data = fd.read()
        fd.close()

        data_offset = 0
        total_count = 0

        last_magic = 0
        last_nodetype = 0
        last_totlen = 0
        last_data_offset = 0

        while 1:
            error = False

            hdr = data[data_offset:data_offset+header_struct_size]
            try:
                (magic, nodetype, totlen) = struct.unpack(header_unpack_fmt, hdr)
            except:
                break
#            magci_header_offset = data_offset

            if magic != 0x1985:
                if self.DumpMagicError:
                    print('* Magic Error:', hex(data_offset), '(', hex(magic), ', ', hex(nodetype), ')')
                    print('\tLast record:', hex(last_data_offset), '(', hex(last_magic), ', ', hex(last_nodetype), ', ', hex(last_totlen), ')')

                while data_offset < len(data):
                    tag = data[data_offset:data_offset+4]
                    if tag == b'\x85\x19\x02\xe0':
                        if self.DumpMagicError:
                            print('\tFound next inode at 0x%x' % data_offset)
                            print('')

                        break
                    data_offset += 0x4

                if data_offset < len(data):
                    (magic, nodetype, totlen) = struct.unpack(header_unpack_fmt, data[data_offset:data_offset+header_struct_size])

                if magic != 0x1985:
                    break

            if nodetype == JFFS2_NODETYPE_INODE:
                node_data = data[data_offset+header_struct_size:data_offset+header_struct_size+inode_struct_size]
                (hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc) = struct.unpack(inode_unpack_fmt, node_data)

                payload = data[data_offset+0x44: data_offset+0x44+csize]
                if compr == 0x6:
                    try:
                        payload = decompress(payload)
                    except:
                        if self.DebugLevel > 0:
                            print('* Uncompress error')
                            error = True

                    if self.DebugLevel > 0:
                        print('payload length:', len(payload))

                if self.DebugLevel > 1:
                    pprint.pprint(payload)

                if ino not in self.INodeMap:
                    self.INodeMap[ino] = []

                self.INodeMap[ino].append({
                    'data_offset': data_offset, 
                    'ino': ino, 
                    'hdr_crc': hdr_crc, 
                    'version': version, 
                    'mode': mode, 
                    'uid': uid, 
                    'gid': gid, 
                    'isize': isize, 
                    'atime': atime, 
                    'mtime': mtime, 
                    'ctime': ctime, 
                    'offset': offset, 
                    'csize': csize, 
                    'dsize': dsize, 
                    'compr': compr, 
                    'usercompr': usercompr, 
                    'flags': flags, 
                    'data_crc': data_crc, 
                    'node_crc': node_crc, 
                    'totlen': totlen, 
                    'payload': payload
                })

                if error or (target_filename != '' and ino in self.DirentMap and self.DirentMap[ino]['payload'].find(target_filename) >= 0):
                    #if self.DebugLevel>0:
                    if True:
                        print(' = '*79)
                        print('* JFFS2_NODETYPE_INODE:')
                        print('magic: %x nodetype: %x totlen: %x' % (magic, nodetype, totlen))
                        print('data_offset: %x offset: %x csize: %x dsize: %x next_offset: %x' % (data_offset, offset, csize, dsize, data_offset + 44 + csize))
                        print('ino: %x version: %x mode: %x' % (ino, version, mode))
                        print('uid: %x gid: %x' % (uid, gid))
                        print('atime: %x mtime: %x ctime: %x' % (atime, mtime, ctime))
                        print('compr: %x usercompr: %x' % (compr, usercompr))
                        print('flags: %x isize: %x' % (flags, isize))
                        print('hdr_crc: %x data_crc: %x node_crc: %x' % (hdr_crc, data_crc, node_crc))
                        print('')

            elif nodetype == JFFS2_NODETYPE_DIRENT:
                (hdr_crc, pino, version, ino, mctime, nsize, ent_type, _, node_crc, name_crc) = struct.unpack(dirent_unpack_fmt, data[data_offset+header_struct_size:data_offset+header_struct_size+dirent_struct_size])
                payload = data[data_offset+header_struct_size+dirent_struct_size+1: data_offset+header_struct_size+dirent_struct_size+1+nsize]

                if ino not in self.DirentMap or self.DirentMap[ino]['version'] < version:
                    self.DirentMap[ino] = {
                        'hdr_crc': hdr_crc, 
                        'pino': pino, 
                        'version': version, 
                        'mctime': mctime, 
                        'nsize': nsize, 
                        'ent_type': ent_type, 
                        'node_crc': node_crc, 
                        'name_crc': name_crc, 
                        'payload': payload
                    }

                if target_filename != '' and payload.find(target_filename) >= 0:
                    print(' = '*79)
                    print('* JFFS2_NODETYPE_DIRENT:')
                    print('data_offset:\t', hex(data_offset))
                    print('magic:\t\t%x' % magic)
                    print('nodetype:\t%x' % nodetype)
                    print('totlen:\t\t%x' % totlen)
                    print('hdr_crc:\t%x' % hdr_crc)
                    print('pino:\t\t%x' % pino)
                    print('version:\t%x' % version)
                    print('ino:\t\t%x' % ino)
                    print('node_crc:\t%x' % node_crc)

                    parent_node = ''
                    if pino in self.DirentMap:
                        parent_node = self.DirentMap[pino]['payload']

                    print('Payload:\t%s' % (parent_node + '\\' + payload))
                    print('')

            elif nodetype == 0x2004:
                pass

            else:
                print(' = '*79)
                print('data_offset:\t', hex(data_offset))
                print('magic:\t\t%x' % magic)
                print('nodetype:\t%x' % nodetype)
                print('totlen:\t\t%x' % totlen)

            (last_magic, last_nodetype, last_totlen) = (magic, nodetype, totlen)

            last_data_offset = data_offset

            if totlen%4 != 0:
                totlen += 4-(totlen%4)

            data_offset += totlen

            current_page_data_len = data_offset % 0x200
            if (0x200-current_page_data_len) < 0x8:
                data_offset += 0x200-current_page_data_len

            if self.DebugLevel > 0:
                print('* Record (@%x):\tMagic: %x\tType: %x\tTotlen %x\tPadded Totlen: %x' % (last_data_offset, last_magic, last_nodetype, last_totlen, totlen))
            total_count += 1

        print('Total Count:', total_count)
        if self.DebugLevel > 0:
            pprint.pprint(self.DirentMap)

    def get_path(self, ino):
        path = ''

        while ino != 0 and ino in self.DirentMap:
            path = '/' + self.DirentMap[ino]['payload'] + path
            ino = self.DirentMap[ino]['pino']

        return path

    def read_file_data(self, inode_map_record, dump = False):
        data = []
        for record in inode_map_record:
            if dump:
                print('offset: %x dsize: %x data offset: %x length: %x (ver: %x) totlen: %x' % (record['offset'], record['dsize'], record['data_offset'], len(record['payload']), record['version'], record['totlen']))

            offset = record['offset']
            dsize = record['dsize']

            new_data_len = offset+dsize-len(data)

            if new_data_len > 0:
                try:
                    data += [b'\x00'] * new_data_len
                except:
                    print('offset: %x dsize: %x data offset: %x length: %x (ver: %x) totlen: %x' % (record['offset'], record['dsize'], record['data_offset'], len(record['payload']), record['version'], record['totlen']))

            data[offset:offset+dsize] = record['payload']

        return ''.join(data)

    def read_file_seq_data(self, inode_map_record, dump = False):
        next_offset = 0
        data = ''

        for record in inode_map_record:
            if dump:
                print(len(inode_map_record))
                print('Version: %x Offset: %x DSize: %x Data Offset: %x Payload Length: %x' % (record['version'], record['offset'], record['dsize'], record['data_offset'], len(record['payload'])))

            offset = record['offset']
            if offset == next_offset:
                next_offset = offset + record['dsize']
#                found_record = True
                data += record['payload']

        return data

    def write_data(self, output_filename, inode_map_record, data):
        shutil.copy(self.OrigFilename, output_filename)

        next_offset = 0
        while 1:
            found_record = False
            for record in inode_map_record:
                offset = record['offset']

                if offset == next_offset:
                    orig_data = data
                    if record['compr'] == 0x6:
                        try:
                            data = compress(data)
                        except:
                            print('* Compress error')

                    print('data_offset: %x offset: %x dsize: %x csize: %x' % (record['data_offset'], record['offset'], record['dsize'], record['csize']))
                    print('Trying to write: %x' % len(data))

                    if record['csize'] > len(data):
                        fd = open(output_filename, 'r+')
                        fd.seek(record['data_offset'])

                        record['csize'] = len(data)
                        record['dsize'] = len(orig_data)

                        fd.write(struct.pack(inode_unpack_fmt, 
                                             record['hdr_crc'], 
                                             record['ino'], 
                                             record['version'], 
                                             record['mode'], 
                                             record['uid'], 
                                             record['gid'], 
                                             record['isize'], 
                                             record['atime'], 
                                             record['mtime'], 
                                             record['ctime'], 
                                             record['offset'], 
                                             record['csize'], 
                                             record['dsize'], 
                                             record['compr'], 
                                             record['usercompr'], 
                                             record['flags'], 
                                             record['data_crc'], 
                                             record['node_crc']
                                            ) + data + (record['csize'] - len(data)) * b'\xff')
                        fd.close()

                    next_offset = offset + record['dsize']

                    if next_offset != offset:
                        found_record = True
                    break

            if not found_record:
                break

        return data

    def dump_file(self, filename, mod = '', out = ''):
        print('dump_file')
        for ino in list(self.DirentMap.keys()):
            if ino in self.INodeMap:
                path = self.get_path(ino)

                if path == filename:
                    print('')
                    print(' = '*80)
                    print(ino, self.get_path(ino), len(self.DirentMap[ino]['payload']))
                    pprint.pprint(self.DirentMap[ino])

                    data = self.read_file_data(self.INodeMap[ino])
                    print(data)

                    if mod != '':
                        fd = open(mod, 'rb')
                        self.write_data(out, self.INodeMap[ino], fd.read())
                        fd.close()

    def dump_info(self, output_dir, ino, target_filename = ''):
        path = self.get_path(ino)

        directory = os.path.dirname(path)
        basename = os.path.basename(path)

        local_dir = os.path.join(output_dir, directory[1:])
        local_path = os.path.join(local_dir, basename)

        write_file = True
        dump = False
        if target_filename != '':
            write_file = False
            if path.find(target_filename) >= 0:
                dump = True
                write_file = True
        else:
            write_file = True

        if dump:
            print('File %s (ino: %d)' % (path, ino))

        data = self.read_file_data(self.INodeMap[ino], dump = dump)

        if dump:
            print('\tFile length: %d' % (len(data)))
            print('')

        if len(data) == 0:
            return

        if write_file:
            if not os.path.isdir(local_dir):
                os.makedirs(local_dir)

            try:
                fd = open(local_path, 'wb')
                fd.write(data)
                fd.close()
            except:
                print('Failed to create file: %s' % (local_path))

    def dump(self, output_dir, target_filename = ''):
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)

        processed_ino = {}
        for ino in list(self.DirentMap.keys()):
            if ino in self.INodeMap:
                processed_ino[ino] = True
                self.dump_info(output_dir, ino, target_filename)

        for ino in list(self.INodeMap.keys()):
            if ino not in processed_ino:
                self.dump_info(output_dir, ino, target_filename)

    def list_data(self, inode_map_record):
        for record in inode_map_record:
            print('version: 0x%x' % record['version'])
            print('\toffset: 0x%x' % record['offset'])
            print('\tpayload: 0x%x' % len(record['payload']))
            print('\tdata_offset: 0x%x' % record['data_offset'])
            print('\tctime: 0x%x' % record['ctime'])
            print('\tmtime: 0x%x' % record['mtime'])
            print('\tatime: 0x%x' % record['atime'])

    def list_file(self, filename):
        print('Path\tInode\tNumber of records')
        for ino in list(self.DirentMap.keys()):
            if ino in self.INodeMap:
                if filename == '':
                    print(self.get_path(ino))
                    print('\tInode:', ino)
                    print('\tRecords:', len(self.INodeMap[ino]))
                else:
                    path = self.get_path(ino)
                    if path == filename:
                        print(self.get_path(ino))
                        print('\tInode:', ino)
                        print('\tRecords:', len(self.INodeMap[ino]))
                        self.list_data(self.INodeMap[ino])

    def make_inode(
            self, 
            ino = 0x683, 
            version = 0x1da, 
            mode = 0x81ed, 
            uid = 0x0, 
            gid = 0x0, 
            isize = 0x1bcb8, 
            atime = 0x498351be, 
            mtime = 0x498351be, 
            ctime = 0x31, 
            offset = 0, 
            dsize = 0x1000, 
            compr = 6, 
            usercompr = 0, 
            flags = 0, 
            payload = ''
    ):
        crc32_inst = crc32.CRC32()
        crc32_inst.set_sarwate()

        magic = 0x1985
        nodetype = JFFS2_NODETYPE_INODE
        totlen = len(payload)+0x44

        header = struct.pack(header_unpack_fmt, magic, nodetype, totlen)

        csize = len(payload)
        hdr_crc = 0
        data_crc = crc32_inst.calc(payload) #0x4d8bd458
        node_crc = 0x0 #0x6d423d5a

        inode = struct.pack(inode_unpack_fmt, hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc)
        hdr_crc = crc32_inst.calc(header) #0xca1c1cba
        inode = struct.pack(inode_unpack_fmt, hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc)

        ri = header+inode
        ri = ri[0:header_struct_size+inode_struct_size-8]
        node_crc = crc32_inst.calc(ri)
        inode = struct.pack(inode_unpack_fmt, hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc)

        data = header
        data += inode
        data += payload

        debug = 0
        if debug > 0:
            print('')
            print('header: %08X' % ((crc32_inst.calc(header)) & 0xFFFFFFFF))
            print('inode: %08X' % ((crc32_inst.calc(inode)) & 0xFFFFFFFF))
            print('header+inode: %08X' % ((crc32_inst.calc(ri)) & 0xFFFFFFFF))
            print('payload: %08X' % ((crc32_inst.calc(payload)) & 0xFFFFFFFF))
            print('data: %08X' % ((crc32_inst.calc(data)) & 0xFFFFFFFF))

        return data

    def make_inode_with_header(self, header, payload):
        (magic, nodetype, totlen) = struct.unpack(header_unpack_fmt, header[0:header_struct_size])

        print('magic: %X' % (magic))
        print('nodetype: %X' % (nodetype))
        print('totlen: %X' % (totlen))

        (hdr_crc, ino, version, mode, uid, gid, isize, atime, mtime, ctime, offset, csize, dsize, compr, usercompr, flags, data_crc, node_crc) = struct.unpack(inode_unpack_fmt, header[header_struct_size:header_struct_size+inode_struct_size])

        print('hdr_crc: %X' % (hdr_crc))
        print('ino: %X' % (ino))
        print('version: %X' % (version))
        print('mode: %X' % (mode))
        print('uid: %X' % (uid))
        print('gid: %X' % (gid))
        print('isize: %X' % (isize))
        print('atime: %X' % (atime))
        print('mtime: %X' % (mtime))
        print('ctime: %X' % (ctime))
        print('offset: %X' % (offset))
        print('csize: %X' % (csize))
        print('dsize: %X' % (dsize))
        print('compr: %X' % (compr))
        print('usercompr: %X' % (usercompr))
        print('flags: %X' % (flags))
        print('data_crc: %X' % (data_crc))
        print('node_crc: %X' % (node_crc))

        return self.make_inode(
            ino = ino, 
            version = version, 
            mode = mode, 
            uid = uid, 
            gid = gid, 
            isize = isize, 
            atime = atime, 
            mtime = mtime, 
            ctime = ctime, 
            offset = offset, 
            dsize = dsize, 
            compr = compr, 
            usercompr = usercompr, 
            flags = flags, 
            payload = payload
        )

    def make_inode_with_header_file(self, header_file, payload_file):
        fd = open(header_file, 'rb')
        header = fd.read()[0:header_struct_size+inode_struct_size]
        fd.close()

        fd = open(payload_file, 'rb')
        payload = fd.read()
        fd.close()

        return self.make_inode_with_header(header, payload)

    def write_ino(self, ino, target_filename, offset, size, new_data_filename, output_filename):
        path = self.get_path(ino)

#        directory = os.path.dirname(path)
#        basename = os.path.basename(path)

        if path == target_filename:
            print('File %s (ino: %d)' % (path, ino))
            print('%x %x' % (offset, size))

            data = []
            for record in self.INodeMap[ino]:
                record_offset = record['offset']
                record_dsize = record['dsize']

                if record_offset <= offset and offset <= record_offset+record_dsize:
                    record_data_offset = record['data_offset']
                    totlen = record['totlen']
                    print('%x (%x) -> file offset: %x (%x) totlen = %x' % (record_offset, record_dsize, record_data_offset, record['csize'], totlen))

                    fd = open(new_data_filename, 'rb')
                    fd.seek(record_offset)
                    data = fd.read(record_dsize)
                    fd.close()

                    new_data = zlib.compress(data)

                    new_inode = self.make_inode(
                        ino = record['ino'], 
                        version = record['version'], 
                        mode = record['mode'], 
                        uid = record['uid'], 
                        gid = record['gid'], 
                        isize = record['isize'], 
                        atime = record['atime'], 
                        mtime = record['mtime'], 
                        ctime = record['ctime'], 
                        offset = record['offset'], 
                        dsize = record['dsize'], 
                        compr = record['compr'], 
                        usercompr = record['usercompr'], 
                        flags = record['flags'], 
                        payload = new_data
                    )
                    new_inode_len = len(new_inode)
                    print(' new_inode: %x' % (len(new_inode)))

                    if totlen > new_inode_len:
                        new_inode += (totlen-new_inode_len) * b'\xff'

                    if output_filename != '':
                        #print 'Writing to %s at 0x%x (0x%x)' % (output_filename, record_data_offset, len(new_inode))
                        fd = open(output_filename, 'wb')

                        orig_fd = open(self.OrigFilename, 'rb')
                        old_data = orig_fd.read()
                        orig_fd.close()

                        #Save
                        ofd = open('old.bin', 'wb')
                        ofd.write(old_data[record_data_offset:record_data_offset+len(new_inode)])
                        ofd.close()

                        nfd = open('new.bin', 'wb')
                        nfd.write(new_inode)
                        nfd.close()

                        fd.write(old_data)
                        fd.seek(record_data_offset)
                        fd.write(new_inode)
                        fd.close()

    def write_file(self, target_filename, new_data_filename, offset, size, output_filename):
        processed_ino = {}
        for ino in list(self.DirentMap.keys()):
            if ino in self.INodeMap:
                processed_ino[ino] = True
                self.write_ino(ino, target_filename, offset, size, new_data_filename, output_filename)

        for ino in list(self.INodeMap.keys()):
            if ino not in processed_ino:
                self.write_ino(ino, target_filename, offset, size, new_data_filename, output_filename)

if __name__ == '__main__':
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option(
        '-o', '--output_dir', dest = 'output_dir', 
        help = 'Set output directory name', default = '', metavar = 'OUTPUT_DIR')

    parser.add_option(
        '-O', '--output_filename', dest = 'output_filename', 
        help = 'Set output filename', default = '', metavar = 'OUTPUT_FILENAME')

    parser.add_option(
        '-f', '--target_filename', dest = 'target_filename', 
        help = 'Set target filename', default = '', metavar = 'TARGET_FILENAME')

    parser.add_option(
        '-n', '--new_data_filename', dest = 'new_data_filename', 
        help = 'Set new data file name', default = '', metavar = 'NEW_DATA_FILENAME')

    parser.add_option('-l', action = 'store_true', dest = 'list')

    parser.add_option('-d', type = 'int', default = 0, dest = 'debug')

    parser.add_option('-t', type = 'int', default = 0, dest = 'offset')

    parser.add_option('-s', type = 'int', default = 0, dest = 'size')

    (options, args) = parser.parse_args()

    jffs2_filename = args[0]

    jffs = JFFS()
    jffs.parse(jffs2_filename, target_filename = options.target_filename)
    jffs.DebugLevel = options.debug


    if options.list:
        jffs.list_file(options.file)

    elif options.new_data_filename != '':
        jffs.write_file(options.target_filename, options.new_data_filename, options.offset, options.size, options.output_filename)

    elif options.output_dir != '':
        print('Dumping files to a folder: %s' % (options.output_dir))
        jffs.dump(options.output_dir, target_filename = options.target_filename)

    elif options.file != '' and options.output_filename != '':
        jffs.dump_file(options.target_filename, options.new_data_filename, options.output_filename)
