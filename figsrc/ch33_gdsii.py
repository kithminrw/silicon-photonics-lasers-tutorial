"""A minimal GDSII stream writer and reader (Python standard library only), for Chapter 33.

It writes the tiny library of Section 33.2 record by record, following the GDSII Stream Format Manual,
Release 6.0 (Calma, 1987): every record is a 2-byte length (header included), a 1-byte record type, a
1-byte data type and its data; integers are big-endian two's complement; reals are 8-byte excess-64
base-16 numbers; odd-length strings are padded with a null byte.

    python -I -X utf8 figsrc/ch33_gdsii.py [out.gds]   # prints the records (and writes the file if a path is given)

ch33_figs.py imports build_tiny() and records() to draw Figure 33.2. figsrc/ch33_klayout.py reads the same
file back with KLayout in Docker to check it.
"""
from fractions import Fraction
import struct
import sys

# record types (third byte) and data types (fourth byte), from Section 4 of the manual
RT = dict(HEADER=0x00, BGNLIB=0x01, LIBNAME=0x02, UNITS=0x03, ENDLIB=0x04, BGNSTR=0x05, STRNAME=0x06,
          ENDSTR=0x07, BOUNDARY=0x08, PATH=0x09, SREF=0x0A, AREF=0x0B, TEXT=0x0C, LAYER=0x0D,
          DATATYPE=0x0E, WIDTH=0x0F, XY=0x10, ENDEL=0x11, SNAME=0x12, COLROW=0x13, TEXTTYPE=0x16,
          STRING=0x19, STRANS=0x1A, MAG=0x1B, ANGLE=0x1C, PATHTYPE=0x21)
RT_NAME = {v: k for k, v in RT.items()}
NODATA, BITARRAY, INT2, INT4, REAL4, REAL8, ASCII = range(7)


def real8(x):
    """Encode x as a GDSII 8-byte real: sign bit, 7-bit excess-64 exponent of 16, 56-bit fraction in [1/16, 1)."""
    if x == 0:
        return bytes(8)
    sign = 0x80 if x < 0 else 0
    m, e = Fraction(abs(x)), 64             # the exact value of the double: no rounding until the end
    while m >= 1:
        m /= 16; e += 1
    while m < Fraction(1, 16):
        m *= 16; e -= 1
    frac = round(m * 2 ** 56)               # rounded to the nearest 56-bit fraction
    if frac == 2 ** 56:                     # rounding carried into a new hex digit
        frac //= 16; e += 1
    return bytes([sign | e]) + frac.to_bytes(7, "big")


def unreal8(b):
    """Decode a GDSII 8-byte real."""
    if not any(b):
        return 0.0
    sign = -1.0 if b[0] & 0x80 else 1.0
    return sign * int.from_bytes(b[1:8], "big") / 2 ** 56 * 16.0 ** ((b[0] & 0x7F) - 64)


def rec(name, data=b"", dtype=None):
    """One record: 2-byte total length, record type, data type, data."""
    if dtype is None:
        dtype = NODATA
    if dtype == ASCII and len(data) % 2:
        data += b"\0"                       # odd-length strings are padded with a null
    n = 4 + len(data)
    assert n % 2 == 0 and n <= 65535
    return struct.pack(">HBB", n, RT[name], dtype) + data


def i2(*v): return struct.pack(">%dh" % len(v), *v)
def i4(*v): return struct.pack(">%di" % len(v), *v)
def s(t): return t.encode("ascii")
def xy(pts): return rec("XY", i4(*[c for p in pts for c in p]), INT4)


STAMP = (2026, 11, 19, 12, 0, 0)            # fixed time stamp, so the file is the same every run


def build_tiny():
    """The tiny library of Section 33.2, in nanometre database units (user unit 1 um).

    WG  : one BOUNDARY, a 10 x 0.5 um straight waveguide on Si 1/0.
    TOP : an AREF of WG (1 column x 4 rows, 127 um apart), an SREF of WG turned by 90 degrees,
          a PATH 0.5 um wide on 1/0, and a TEXT label on 10/0.
    """
    out = [rec("HEADER", i2(600), INT2),                       # stream version 600 (Release 6.0)
           rec("BGNLIB", i2(*(STAMP + STAMP)), INT2),          # last modification, last access
           rec("LIBNAME", s("CH33.DB"), ASCII),
           rec("UNITS", real8(1e-3) + real8(1e-9), REAL8),     # dbu in user units, dbu in metres
           # ---- structure WG
           rec("BGNSTR", i2(*(STAMP + STAMP)), INT2),          # creation, last modification
           rec("STRNAME", s("WG"), ASCII),
           rec("BOUNDARY"), rec("LAYER", i2(1), INT2), rec("DATATYPE", i2(0), INT2),
           xy([(0, -250), (10000, -250), (10000, 250), (0, 250), (0, -250)]),   # closed: last = first
           rec("ENDEL"),
           rec("ENDSTR"),
           # ---- structure TOP
           rec("BGNSTR", i2(*(STAMP + STAMP)), INT2),
           rec("STRNAME", s("TOP"), ASCII),
           rec("AREF"), rec("SNAME", s("WG"), ASCII),
           rec("COLROW", i2(1, 4), INT2),                      # 1 column, 4 rows
           xy([(0, 0), (20000, 0), (0, 4 * 127000)]),          # origin, + 1 x column step, + 4 x row step
           rec("ENDEL"),
           rec("SREF"), rec("SNAME", s("WG"), ASCII),
           rec("STRANS", i2(0), BITARRAY),                     # no reflection, relative mag and angle
           rec("ANGLE", real8(90.0), REAL8),                   # degrees, counter-clockwise
           xy([(15000, 0)]),
           rec("ENDEL"),
           rec("PATH"), rec("LAYER", i2(1), INT2), rec("DATATYPE", i2(0), INT2),
           rec("PATHTYPE", i2(0), INT2), rec("WIDTH", i4(500), INT4),
           xy([(10000, 381000), (12500, 381000), (12500, 391000)]),
           rec("ENDEL"),
           rec("TEXT"), rec("LAYER", i2(10), INT2), rec("TEXTTYPE", i2(0), INT2),
           xy([(0, 381000)]),
           rec("STRING", s("opt_in_TE_1550_demo"), ASCII),
           rec("ENDEL"),
           rec("ENDSTR"),
           rec("ENDLIB")]
    return b"".join(out)


def records(data):
    """Split a stream into (offset, length, record name, data type, raw data, decoded value)."""
    out, k = [], 0
    while k < len(data):
        n, rt, dt = struct.unpack(">HBB", data[k:k + 4])
        raw = data[k + 4:k + n]
        if dt == INT2:
            val = struct.unpack(">%dh" % (len(raw) // 2), raw)
        elif dt == INT4:
            val = struct.unpack(">%di" % (len(raw) // 4), raw)
        elif dt == REAL8:
            val = tuple(unreal8(raw[j:j + 8]) for j in range(0, len(raw), 8))
        elif dt == ASCII:
            val = raw.rstrip(b"\0").decode("ascii")
        elif dt == BITARRAY:
            val = struct.unpack(">H", raw)
        else:
            val = None
        out.append((k, n, RT_NAME.get(rt, hex(rt)), dt, raw, val))
        k += n
        if RT_NAME.get(rt) == "ENDLIB":
            break
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    # The manual's examples (Section 7) of 1e-3, 1e-9 and 90.0. The manual's 1e-3 and 1e-9 differ from this
    # encoder (and from KLayout's and gdstk's, which give the same bytes as this one) in the last bits only.
    for x, manual in [(1e-3, "3E4189374BC6A7EF"), (1e-9, "3944B82FA09B5A51"), (90.0, "425A000000000000")]:
        got = real8(x).hex().upper()
        err_m = abs(unreal8(bytes.fromhex(manual)) - x) / x
        err_g = abs(unreal8(real8(x)) - x) / x
        print(f"real8({x:g}) = {got}; manual {manual}; relative errors {err_g:.1e} (here), {err_m:.1e} (manual)")
        assert err_g < 1e-16 and err_m < 1e-15
    data = build_tiny()
    if len(sys.argv) > 1:                   # write the file only where asked to
        with open(sys.argv[1], "wb") as f:
            f.write(data)
    print(f"{len(data)} bytes, {len(records(data))} records" + (f" -> {sys.argv[1]}" if len(sys.argv) > 1 else ""))
    for off, n, name, dt, raw, val in records(data):
        hx = (struct.pack(">H", n) + data[off + 2:off + 4] + raw).hex(" ").upper()
        print(f"{off:4d} {n:3d} {name:9s} {hx[:60]:60s} {val}")
