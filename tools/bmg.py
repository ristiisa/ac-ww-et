"""AC:WW compressed BMG (Nintendo message) helpers.

Text encoding is Windows-1252. Control codes are 0x1A <len> <group> ...,
where <len> counts the whole code including the 0x1A byte. In editable text
they are written as {group payload...} in hex, e.g. {07 01 00 00}. Bytes that
are not valid cp1252 are written as {x81}. A literal brace is doubled: {{ }}.
"""
import re
import struct
import ndspy.lz10

CHUNK = 0x1000


def unwrap(data):
    """Decompress an AC:WW 'LZ77' wrapped file, or return raw data.

    Wrapper: b'LZ77', flag byte 0xF7, u24 decompressed size, then one u16 per
    0x1000-byte chunk giving the cumulative end offset of that chunk's
    compressed data. Each chunk is an independent LZ10 stream, or, if its
    first byte is 0x00, a 4-byte header followed by the raw bytes.
    """
    if data[:4] != b'LZ77':
        return bytes(data)
    assert data[4] == 0xF7, hex(data[4])
    size = int.from_bytes(data[5:8], 'little')
    nchunks = (size + CHUNK - 1) // CHUNK
    base = 8 + 2 * nchunks
    out = bytearray()
    prev = 0
    for i in range(nchunks):
        end = struct.unpack_from('<H', data, 8 + 2 * i)[0]
        chunk = data[base + prev:base + end]
        out += chunk[4:] if chunk[0] == 0 else ndspy.lz10.decompress(chunk)
        prev = end
    assert len(out) == size, (len(out), size)
    return bytes(out)


def wrap(data):
    """Inverse of unwrap."""
    chunks = [ndspy.lz10.compress(data[i:i + CHUNK]) for i in range(0, len(data), CHUNK)]
    ends, pos = [], 0
    for c in chunks:
        pos += len(c)
        ends.append(pos)
    assert pos <= 0xFFFF, 'compressed file too large for u16 offsets'
    hdr = b'LZ77' + bytes([0xF7]) + len(data).to_bytes(3, 'little')
    return hdr + b''.join(struct.pack('<H', e) for e in ends) + b''.join(chunks)


class Bmg:
    def __init__(self, data):
        assert data[:8] == b'MESGbmg1', data[:8]
        self.header = bytearray(data[:0x20])
        self.encoding = data[0x10]
        nsec = struct.unpack_from('<I', data, 0x0C)[0]
        pos = 0x20
        for _ in range(nsec):
            magic = data[pos:pos + 4]
            slen = struct.unpack_from('<I', data, pos + 4)[0]
            body = data[pos:pos + slen]
            if magic == b'INF1':
                count, self.entry_size = struct.unpack_from('<HH', body, 8)
                self.inf_extra = body[0x0C:0x10]
                offsets, self.attrs = [], []
                for i in range(count):
                    e = body[0x10 + i * self.entry_size:0x10 + (i + 1) * self.entry_size]
                    offsets.append(struct.unpack_from('<I', e)[0])
                    self.attrs.append(bytes(e[4:]))
            elif magic == b'DAT1':
                dat = body[8:]
            else:
                raise ValueError(f'unknown section {magic}')
            pos += slen
        self.messages = [dat[o:_msg_end(dat, o)] for o in offsets]
        self._null = [o == 0 for o in offsets]  # empty message sharing offset 0

    def build(self):
        dat = bytearray(b'\0')
        offsets = []
        for m, null in zip(self.messages, self._null):
            if not m and null:
                offsets.append(0)
            else:
                offsets.append(len(dat))
                dat += m + b'\0'
        inf = bytearray()
        for o, a in zip(offsets, self.attrs):
            inf += struct.pack('<I', o) + a
        inf = struct.pack('<HH', len(offsets), self.entry_size) + self.inf_extra + inf
        inf_sec = _section(b'INF1', inf)
        dat_sec = _section(b'DAT1', dat)
        out = bytearray(self.header)
        struct.pack_into('<II', out, 0x08, 0x20 + len(inf_sec) + len(dat_sec), 2)
        return bytes(out + inf_sec + dat_sec)


def _msg_end(dat, i):
    """Index of the 0x00 terminator, skipping control codes (which may contain 0x00)."""
    while dat[i]:
        i += dat[i + 1] if dat[i] == 0x1A else 1
    return i


def _section(magic, body):
    size = (8 + len(body) + 31) & ~31
    return magic + struct.pack('<I', size) + body + b'\0' * (size - 8 - len(body))


def decode(msg):
    """Message bytes -> editable text."""
    out = []
    i = 0
    while i < len(msg):
        b = msg[i]
        if b == 0x1A:
            n = msg[i + 1]
            out.append('{' + ' '.join(f'{x:02x}' for x in msg[i + 2:i + n]) + '}')
            i += n
            continue
        try:
            ch = bytes([b]).decode('cp1252')
        except UnicodeDecodeError:
            out.append(f'{{x{b:02x}}}')
        else:
            out.append({'{': '{{', '}': '}}'}.get(ch, ch))
        i += 1
    return ''.join(out)


_TOKEN = re.compile(r'\{\{|\}\}|\{x([0-9a-fA-F]{2})\}|\{([0-9a-fA-F ]*)\}|[^{}]', re.S)


def encode(text):
    """Editable text -> message bytes. Raises on characters not in cp1252."""
    out = bytearray()
    pos = 0
    for m in _TOKEN.finditer(text):
        if m.start() != pos:
            break
        pos = m.end()
        tok = m.group(0)
        if tok in ('{{', '}}'):
            out += tok[0].encode()
        elif m.group(1):
            out.append(int(m.group(1), 16))
        elif m.group(2) is not None:
            payload = bytes.fromhex(m.group(2))
            out += bytes([0x1A, len(payload) + 2]) + payload
        else:
            out += tok.encode('cp1252')
    if pos != len(text):
        raise ValueError(f'bad markup at {pos}: {text[pos:pos + 20]!r}')
    return bytes(out)
