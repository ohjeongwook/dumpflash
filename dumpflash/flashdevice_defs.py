ADR_CE = 0x10
ADR_WP = 0x20
ADR_CL = 0x40
ADR_AL = 0x80

NAND_CMD_READ0 = 0
NAND_CMD_READ1 = 1
NAND_CMD_RNDOUT = 5
NAND_CMD_PAGEPROG = 0x10
NAND_CMD_READ_OOB = 0x50
NAND_CMD_ERASE1 = 0x60
NAND_CMD_STATUS = 0x70
NAND_CMD_STATUS_MULTI = 0x71
NAND_CMD_SEQIN = 0x80
NAND_CMD_RNDIN = 0x85
NAND_CMD_READID = 0x90
NAND_CMD_ERASE2 = 0xd0
NAND_CMD_PARAM = 0xec
NAND_CMD_RESET = 0xff
NAND_CMD_LOCK = 0x2a
NAND_CMD_UNLOCK1 = 0x23
NAND_CMD_UNLOCK2 = 0x24
NAND_CMD_READSTART = 0x30
NAND_CMD_RNDOUTSTART = 0xE0
NAND_CMD_CACHEDPROG = 0x15
NAND_CMD_ONFI = 0xEC
NAND_CI_CHIPNR_MSK = 0x03
NAND_CI_CELLTYPE_MSK = 0x0C
NAND_CI_CELLTYPE_SHIFT = 2

NAND_STATUS_FAIL = (1<<0) # HIGH - FAIL,  LOW - PASS
NAND_STATUS_IDLE = (1<<5) # HIGH - IDLE,  LOW - ACTIVE
NAND_STATUS_READY = (1<<6) # HIGH - READY, LOW - BUSY
NAND_STATUS_NOT_PROTECTED = (1<<7) # HIGH - NOT,   LOW - PROTECTED

LP_OPTIONS = 1
DEVICE_DESCRIPTIONS = [
    # name, ID, PageSize, ChipSizeMb, EraseSize, Options, AddrCycles
    ["NAND 1MiB 5V 8-bit",        0x6e, 256, 1, 0x1000, 0, 3],
    ["NAND 2MiB 5V 8-bit",        0x64, 256, 2, 0x1000, 0, 3],
    ["NAND 4MiB 5V 8-bit",        0x6b, 512, 4, 0x2000, 0, 3],
    ["NAND 1MiB 3,3V 8-bit",    0xe8, 256, 1, 0x1000, 0, 3],
    ["NAND 1MiB 3,3V 8-bit",    0xec, 256, 1, 0x1000, 0, 3],
    ["NAND 2MiB 3,3V 8-bit",    0xea, 256, 2, 0x1000, 0, 3],

    ["NAND 4MiB 3,3V 8-bit",    0xe3, 512, 4, 0x2000, 0, 3],
    ["NAND 4MiB 3,3V 8-bit",    0xe5, 512, 4, 0x2000, 0, 3],
    ["NAND 8MiB 3,3V 8-bit",    0xd6, 512, 8, 0x2000, 0, 3],
    ["NAND 8MiB 1,8V 8-bit",    0x39, 512, 8, 0x2000, 0, 3],
    ["NAND 8MiB 3,3V 8-bit",    0xe6, 512, 8, 0x2000, 0, 3],
    ["NAND 16MiB 1,8V 8-bit",    0x33, 512, 16, 0x4000, 0, 3],
    ["NAND 16MiB 3,3V 8-bit",    0x73, 512, 16, 0x4000, 0, 3],
    ["NAND 32MiB 1,8V 8-bit",    0x35, 512, 32, 0x4000, 0, 3],
    ["NAND 32MiB 3,3V 8-bit",    0x75, 512, 32, 0x4000, 0, 3],
    ["NAND 64MiB 1,8V 8-bit",    0x36, 512, 64, 0x4000, 0, 4],
    ["NAND 64MiB 3,3V 8-bit",    0x76, 512, 64, 0x4000, 0, 4],
    ["NAND 128MiB 1,8V 8-bit",    0x78, 512, 128, 0x4000, 0, 3],
    ["NAND 128MiB 1,8V 8-bit",    0x39, 512, 128, 0x4000, 0, 3],
    ["NAND 128MiB 3,3V 8-bit",    0x79, 512, 128, 0x4000, 0, 4],
    ["NAND 256MiB 3,3V 8-bit",    0x71, 512, 256, 0x4000, 0, 4],

    # 512 Megabit
    ["NAND 64MiB 1,8V 8-bit",    0xA2, 0,  64, 0, LP_OPTIONS, 4],
    ["NAND 64MiB 1,8V 8-bit",    0xA0, 0,  64, 0, LP_OPTIONS, 4],
    ["NAND 64MiB 3,3V 8-bit",    0xF2, 0,  64, 0, LP_OPTIONS, 4],
    ["NAND 64MiB 3,3V 8-bit",    0xD0, 0,  64, 0, LP_OPTIONS, 4],
    ["NAND 64MiB 3,3V 8-bit",    0xF0, 0,  64, 0, LP_OPTIONS, 4],

    # 1 Gigabit
    ["NAND 128MiB 1,8V 8-bit",    0xA1, 0, 128, 0, LP_OPTIONS, 4],
    ["NAND 128MiB 3,3V 8-bit",    0xF1, 0, 128, 0, LP_OPTIONS, 4],
    ["NAND 128MiB 3,3V 8-bit",    0xD1, 0, 128, 0, LP_OPTIONS, 4],

    # 2 Gigabit
    ["NAND 256MiB 1,8V 8-bit",    0xAA, 0, 256, 0, LP_OPTIONS, 5],
    ["NAND 256MiB 3,3V 8-bit",    0xDA, 0, 256, 0, LP_OPTIONS, 5],

    # 4 Gigabit
    ["NAND 512MiB 1,8V 8-bit",    0xAC, 0, 512, 0, LP_OPTIONS, 5],
    ["NAND 512MiB 3,3V 8-bit",    0xDC, 0, 512, 0, LP_OPTIONS, 5],

    # 8 Gigabit
    ["NAND 1GiB 1,8V 8-bit",    0xA3, 0, 1024, 0, LP_OPTIONS, 5],
    ["NAND 1GiB 3,3V 8-bit",    0xD3, 0, 1024, 0, LP_OPTIONS, 5],

    # 16 Gigabit
    ["NAND 2GiB 1,8V 8-bit",    0xA5, 0, 2048, 0, LP_OPTIONS, 5],
    ["NAND 2GiB 3,3V 8-bit",    0xD5, 0, 2048, 0, LP_OPTIONS, 5],

    # 32 Gigabit
    ["NAND 4GiB 1,8V 8-bit",    0xA7, 0, 4096, 0, LP_OPTIONS, 5],
    ["NAND 4GiB 3,3V 8-bit",    0xD7, 0, 4096, 0, LP_OPTIONS, 5],
    ["NAND 4GiB 3,3V 8-bit",    0x2C, 0, 4096, 0, LP_OPTIONS, 5],

    # 64 Gigabit
    ["NAND 8GiB 1,8V 8-bit",    0xAE, 0, 8192, 0, LP_OPTIONS, 5],
    ["NAND 8GiB 3,3V 8-bit",    0xDE, 0, 8192, 0, LP_OPTIONS, 5],

    # 128 Gigabit
    ["NAND 16GiB 1,8V 8-bit",    0x1A, 0, 16384, 0, LP_OPTIONS, 5],
    ["NAND 16GiB 3,3V 8-bit",    0x3A, 0, 16384, 0, LP_OPTIONS, 5],

    # 256 Gigabit
    ["NAND 32GiB 1,8V 8-bit",    0x1C, 0, 32768, 0, LP_OPTIONS, 6],
    ["NAND 32GiB 3,3V 8-bit",    0x3C, 0, 32768, 0, LP_OPTIONS, 6],

    # 512 Gigabit
    ["NAND 64GiB 1,8V 8-bit",    0x1E, 0, 65536, 0, LP_OPTIONS, 6],
    ["NAND 64GiB 3,3V 8-bit",    0x3E, 0, 65536, 0, LP_OPTIONS, 6],

]
