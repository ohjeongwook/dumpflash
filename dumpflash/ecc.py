# pylint: disable=invalid-name
# pylint: disable=line-too-long

class Calculator:
    Parity = (
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 
        0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0
    )

    DebugLevel = 0

    def calc(self, body):
        p8 = 0
        p8_ = 0
        p16 = 0
        p16_ = 0
        p32 = 0
        p32_ = 0
        p64 = 0
        p64_ = 0
        p128 = 0
        p128_ = 0
        p256 = 0
        p256_ = 0
        p512 = 0
        p512_ = 0
        p1024 = 0
        p1024_ = 0
        p2048 = 0
        p2048_ = 0
        p1 = 0
        p1_ = 0
        p2 = 0
        p2_ = 0
        p4 = 0
        p4_ = 0
        for i in range(0, len(body), 1):
            ch = body[i]
            bit0 = ch & 0x1
            bit1 = (ch >> 1) & 0x1
            bit2 = (ch >> 2) & 0x1
            bit3 = (ch >> 3) & 0x1
            bit4 = (ch >> 4) & 0x1
            bit5 = (ch >> 5) & 0x1
            bit6 = (ch >> 6) & 0x1
            bit7 = (ch >> 7) & 0x1

            xor_bit = bit7 ^ bit6 ^ bit5 ^ bit4 ^ bit3 ^ bit2 ^ bit1 ^ bit0

            if self.DebugLevel > 0:
                print("%3x  " % i, bit7, bit6, bit5, bit4, bit3, bit2, bit1, bit0)

            if i & 0x01 == 0x01:
                p8 = xor_bit ^ p8
            else:
                p8_ = xor_bit ^ p8_
            if i & 0x02 == 0x02:
                p16 = xor_bit ^ p16
            else:
                p16_ = xor_bit ^ p16_
            if i & 0x04 == 0x04:
                p32 = xor_bit ^ p32
            else:
                p32_ = xor_bit ^ p32_
            if i & 0x08 == 0x08:
                p64 = xor_bit ^ p64
            else:
                p64_ = xor_bit ^ p64_
            if i & 0x10 == 0x10:
                p128 = xor_bit ^ p128
            else:
                p128_ = xor_bit ^ p128_
            if i & 0x20 == 0x20:
                p256 = xor_bit ^ p256
            else:
                p256_ = xor_bit ^ p256_
            if i & 0x40 == 0x40:
                p512 = xor_bit ^ p512
            else:
                p512_ = xor_bit ^ p512_
            if i & 0x80 == 0x80:
                p1024 = xor_bit ^ p1024
            else:
                p1024_ = xor_bit ^ p1024_
            if i & 0x100 == 0x100:
                p2048 = xor_bit ^ p2048
            else:
                p2048_ = xor_bit ^ p2048_
            p1 = bit7 ^ bit5 ^ bit3 ^ bit1 ^ p1
            p1_ = bit6 ^ bit4 ^ bit2 ^ bit0 ^ p1_
            p2 = bit7 ^ bit6 ^ bit3 ^ bit2 ^ p2
            p2_ = bit5 ^ bit4 ^ bit1 ^ bit0 ^ p2_
            p4 = bit7 ^ bit6 ^ bit5 ^ bit4 ^ p4
            p4_ = bit3 ^ bit2 ^ bit1 ^ bit0 ^ p4_

        ecc0 = (p64 << 7) + (p64_ << 6) + (p32 << 5) + (p32_ << 4) + (p16 << 3) + (p16_ << 2) + (p8 << 1) + (p8_ << 0)
        ecc1 = (p1024 << 7) + (p1024_ << 6) + (p512 << 5) + (p512_ << 4) + (p256 << 3) + (p256_ << 2) + (p128 << 1) + (p128_<< 0)
        ecc2 = (p4 << 7) + (p4_ << 6) + (p2 << 5) + (p2_ << 4) + (p1 << 3) + (p1_ << 2) + (p2048 << 1) + (p2048_ << 0)

        return (ecc0 ^ 0xff, ecc1 ^ 0xff, ecc2 ^ 0xff)

    def calc2(self, body):
        par = 0
        rp = [0] * 18

        for i in range(0, len(body), 1):
            cur = body[i]
            par ^= cur

            # compute the row parities by testing
            # the r^th bit of the address i
            for r in range(0,9):
                if (i >> r) & 1:
                    rp[2*r + 1] ^= cur
                else:
                    rp[2*r + 0] ^= cur

        code0 = 0
        code1 = 0

        for i in range(0,8):
            code0 |= self.Parity[rp[i+0]] << i
            code1 |= self.Parity[rp[i+8]] << i

        # column parities
        cp5 = par & 0b11110000
        cp4 = par & 0b00001111
        cp3 = par & 0b11001100
        cp2 = par & 0b00110011
        cp1 = par & 0b10101010
        cp0 = par & 0b01010101

        # 512-byte blocks squeeze the extra row parities into code2
        code2 = 0 \
            | (self.Parity[cp5] << 7) \
            | (self.Parity[cp4] << 6) \
            | (self.Parity[cp3] << 5) \
            | (self.Parity[cp2] << 4) \
            | (self.Parity[cp1] << 3) \
            | (self.Parity[cp0] << 2) \
            | (self.Parity[rp[17]] << 1) \
            | (self.Parity[rp[16]] << 0)

        code0 ^= 0xFF
        code1 ^= 0xFF
        code2 ^= 0xFF

        return (code0, code1, code2)
