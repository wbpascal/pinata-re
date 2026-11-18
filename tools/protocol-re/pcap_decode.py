"""Decode Fiesta client<->server traffic from a .pcap/.pcapng capture and check it against docs/protocol.

usage: python3 -I pcap_decode.py <capture.pcapng|.pcap> [--port 9010=login ...] [--show-secrets] [--out DIR]
       python3 -I pcap_decode.py --transcript DIR <capture> ...   # only <name>.txt per capture: ADR 0008 transcript, passwords not masked
       python3 -I pcap_decode.py --selftest
outputs: <capture>.decoded.txt, <capture>.report.md, <capture>.json   (next to the capture, or in --out)

stdlib only. Framing / XOR-499 cipher / seed rules: docs/protocol/README.md section 1. Usage and limits: docs/knowledge/P01.md.
"""
import bisect, collections, glob, json, os, re, struct, sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
DOCS = os.path.join(ROOT, "docs/protocol")
EXPORTS = os.path.join(ROOT, "re-data/exports")
XOR499 = bytes.fromhex(re.search(r"## Appendix A.*?```\s*([0-9a-f]+)\s*```",
                                 open(os.path.join(DOCS, "README.md")).read(), re.S).group(1))
assert len(XOR499) == 499
CLIENT_CLASS = {"login": "CParserClient", "wm": "CParserClient", "zone": "ShineObjectClass::ShinePlayer"}
FIRST_C2S = {"login": 0x0C65, "wm": 0x0C0F, "zone": 0x0806}   # README section 2: first client packet per server
C2S, S2C = "C→S", "S→C"


# ---------------------------------------------------------------- capture files
def read_capture(path):
    """-> (frames, comments). frame = (ts, linktype, bytes); comments = {frame_index: text}"""
    data = open(path, "rb").read()
    magic = data[:4]
    if magic == b"\x0a\x0d\x0d\x0a":
        return read_pcapng(data)
    for e in "<>":
        m = struct.unpack(e + "I", magic)[0]
        if m in (0xA1B2C3D4, 0xA1B23C4D):
            frac = 1e9 if m == 0xA1B23C4D else 1e6
            link = struct.unpack(e + "I", data[20:24])[0] & 0x0FFFFFFF
            frames, p = [], 24
            while p + 16 <= len(data):
                s, us, incl, _ = struct.unpack(e + "IIII", data[p:p + 16])
                frames.append((s + us / frac, link, data[p + 16:p + 16 + incl]))
                p += 16 + incl
            return frames, {}
    raise ValueError(f"{path}: not a pcap/pcapng file")


def read_pcapng(data):
    frames, comments, ifs, e, p = [], {}, [], "<", 0
    while p + 12 <= len(data):
        if data[p:p + 4] == b"\x0a\x0d\x0d\x0a":            # section header: fix byte order
            e = "<" if data[p + 8:p + 12] == b"\x4d\x3c\x2b\x1a" else ">"
            ifs = []
        btype, blen = struct.unpack(e + "II", data[p:p + 8])
        if blen < 12:
            raise ValueError(f"pcapng: bad block length at {p}")
        body = data[p + 8:p + blen - 4]
        if btype == 1:                                       # interface description
            link = struct.unpack(e + "H", body[:2])[0]
            res = 1e-6
            for code, val in pcapng_options(body[8:], e):
                if code == 9 and val:
                    res = 2.0 ** -(val[0] & 0x7F) if val[0] & 0x80 else 10.0 ** -val[0]
            ifs.append((link, res))
        elif btype in (6, 3):                                # enhanced / simple packet
            if btype == 6:
                iface, hi, lo, cap = struct.unpack(e + "IIII", body[:16])[:4]
                pkt, opts = body[20:20 + cap], body[20 + ((cap + 3) & ~3):]
                link, res = ifs[iface]
                ts = ((hi << 32) | lo) * res
                for code, val in pcapng_options(opts, e):
                    if code == 1:
                        comments[len(frames)] = val.decode("utf-8", "replace").rstrip("\0")
            else:
                link, res = ifs[0]
                pkt, ts = body[4:4 + struct.unpack(e + "I", body[:4])[0]], 0.0
            frames.append((ts, link, pkt))
        p += blen
    return frames, comments


def pcapng_options(buf, e):
    p = 0
    while p + 4 <= len(buf):
        code, ln = struct.unpack(e + "HH", buf[p:p + 4])
        if code == 0:
            break
        yield code, buf[p + 4:p + 4 + ln]
        p += 4 + ((ln + 3) & ~3)


def ipv4_of(link, pkt):
    """link-layer frame -> IPv4 packet bytes or None"""
    if link == 1:                                            # Ethernet (+802.1Q)
        p, et = 14, pkt[12:14]
        while et == b"\x81\x00":
            et, p = pkt[p + 2:p + 4], p + 4
        return pkt[p:] if et == b"\x08\x00" else None
    if link in (0, 108):                                     # BSD/Npcap loopback: 4-byte family (2 = IPv4)
        fam = pkt[:4]
        return pkt[4:] if fam in (b"\x02\0\0\0", b"\0\0\0\x02") else None
    if link in (101, 228, 12, 14):                           # raw IP
        return pkt if pkt[:1] and pkt[0] >> 4 == 4 else None
    if link == 113:                                          # Linux cooked
        return pkt[16:] if pkt[14:16] == b"\x08\x00" else None
    return None


def tcp_of(ip):
    if len(ip) < 20 or ip[0] >> 4 != 4 or ip[9] != 6:
        return None
    ihl, total = (ip[0] & 15) * 4, struct.unpack(">H", ip[2:4])[0]
    if struct.unpack(">H", ip[6:8])[0] & 0x3FFF:             # shortcut: IP fragments are dropped (TCP is not fragmented in practice)
        return None
    t = ip[ihl:total or len(ip)]
    sport, dport, seq = struct.unpack(">HHI", t[:8])
    off, flags = (t[12] >> 4) * 4, t[13]
    return (".".join(map(str, ip[12:16])), sport, ".".join(map(str, ip[16:20])), dport, seq, flags, t[off:])


# ---------------------------------------------------------------- TCP reassembly
class Direction:
    def __init__(self):
        self.isn, self.segs = None, []                       # segs: (seq, frame, data)

    def assemble(self):
        """-> chunks [(rel_off, bytes)], gaps [(rel_off, missing)], frame map [(rel_end, frame)], stats"""
        if not self.segs:
            return [], [], [], 0
        base = self.isn if self.isn is not None else self.segs[0][0]
        rel = lambda s: ((s - base + 2**31) % 2**32) - 2**31
        segs = sorted(((rel(s), f, d) for s, f, d in self.segs), key=lambda x: (x[0], x[1]))
        start = 0 if self.isn is not None else min(0, segs[0][0])
        chunks, gaps, fmap, cur, dup = [], [], [], start, 0
        buf, buf_off = bytearray(), start
        for off, f, d in segs:
            if off + len(d) <= cur:
                dup += 1
                continue
            if off > cur:
                gaps.append((cur, off - cur))
                if buf:
                    chunks.append((buf_off, bytes(buf)))
                buf, buf_off, cur = bytearray(), off, off
            buf += d[cur - off:]
            cur = off + len(d)
            fmap.append((cur, f))
        if buf:
            chunks.append((buf_off, bytes(buf)))
        return chunks, gaps, fmap, dup


def max_frame(fmap, a, b):
    """latest frame that delivered any byte of [a, b)"""
    i = bisect.bisect_right(fmap, (a, 1 << 62))
    best = 0
    while i < len(fmap):
        best = max(best, fmap[i][1])
        if fmap[i][0] >= b:
            break
        i += 1
    return best


# ---------------------------------------------------------------- framing + cipher
def parse_frame(buf, p):
    """-> (body_start, body_len) or None if incomplete/invalid"""
    if p >= len(buf):
        return None
    if buf[p]:
        start, n = p + 1, buf[p]
    elif p + 3 <= len(buf):
        start, n = p + 3, struct.unpack("<H", buf[p + 1:p + 3])[0]
    else:
        return None
    return (start, n) if n >= 2 and start + n <= len(buf) else None


def xor(body, idx):
    out = bytearray(body)
    for i in range(len(out)):
        out[i] ^= XOR499[idx]
        idx = 0 if idx >= 498 else idx + 1
    return bytes(out), idx


def op_at(body, idx):
    """opcode of an encrypted body if the keystream starts at idx"""
    return (body[0] ^ XOR499[idx]) | (body[1] ^ XOR499[(idx + 1) % 499]) << 8


def best_idx(bodies, known, prefer=None):
    """brute-force the XOR start index: the one under which most bodies get a known opcode.
    -> (idx, score, n_tied). Tie-break: first opcode == prefer, then idx 0, then lowest."""
    best = []
    for i0 in range(499):
        idx, score = i0, 0
        for b in bodies:
            score += op_at(b, idx) in known
            idx = (idx + len(b)) % 499
        best.append((score, i0))
    top = max(s for s, _ in best)
    tied = [i for s, i in best if s == top]
    pick = sorted(tied, key=lambda i: (op_at(bodies[0], i) != prefer, i != 0, i))[0]
    return pick, top, len(tied)


def find_sync(buf, p, enc, known, window=4096):
    """after a gap / mid-stream start: first offset where a chain of frames has known opcodes"""
    for off in range(p, min(len(buf), p + window)):
        bodies, q = [], off
        while len(bodies) < 4:
            fr = parse_frame(buf, q)
            if not fr:
                break
            bodies.append(buf[fr[0]:fr[0] + fr[1]])
            q = fr[0] + fr[1]
        if not bodies or (len(bodies) < 3 and q != len(buf)):
            continue
        need = len(bodies) if len(bodies) < 3 else len(bodies) - 1   # a chain of 3+ may contain one unknown opcode
        if enc:
            if any(op_at(bodies[0], i) in known for i in range(499)) and best_idx(bodies, known)[1] >= need:
                return off
        elif struct.unpack("<H", bodies[0][:2])[0] in known and \
                sum(struct.unpack("<H", b[:2])[0] in known for b in bodies) >= need:
            return off
    return None


def deframe(chunks, gaps, fmap, synced_start, enc, known):
    """-> list of dict(off, body, frame, resync) + problems"""
    out, problems = [], []
    for ci, (coff, buf) in enumerate(chunks):
        p, need = 0, not (synced_start and coff == 0)
        if need:
            s = find_sync(buf, 0, enc, known)
            if s is None:
                problems.append(f"could not find a frame boundary in {len(buf)} bytes at stream offset {coff}")
                continue
            if s:
                problems.append(f"skipped {s} bytes at stream offset {coff} to resynchronise")
            p = s
        first = True
        while p < len(buf):
            fr = parse_frame(buf, p)
            if not fr:
                problems.append(f"truncated packet at stream offset {coff + p} ({len(buf) - p} bytes left)")
                break
            st, n = fr
            out.append(dict(off=coff + p, body=buf[st:st + n], frame=max_frame(fmap, coff + p, coff + st + n),
                            resync=first and need))
            first, p = False, st + n
    return out, problems


# ---------------------------------------------------------------- documentation
def client_dir(d):
    """annotation 'dir' -> C2S / S2C for client-facing packets. Items label the client side 'C' and the server by
    name ('C→WM', 'WM→C', 'Z→C', 'C→Z'); 'C→S' / 'S→C' pass through. Server-to-server labels are kept as they are."""
    if d in (C2S, S2C):
        return d
    parts = [x.strip() for x in (d or "").split("→")]
    if len(parts) == 2 and parts[0] == "C" and parts[1] != "C":
        return C2S
    if len(parts) == 2 and parts[1] == "C" and parts[0] != "C":
        return S2C
    return d


def load_docs():
    ann = json.load(open(os.path.join(DOCS, "annotations.json")))
    structs, packets, variants = dict(ann.get("structs", {})), {}, {}
    for f in [None] + sorted(glob.glob(os.path.join(DOCS, "annotations/*.json"))):
        a = ann if f is None else json.load(open(f))
        structs.update(a.get("structs", {}))
        for srv, d in a.get("packets", {}).items():
            for op, v in d.items():
                packets[(srv, int(op, 16), client_dir(v.get("dir")))] = v
        # P02 sweep (batch 2): an `evidence` entry may carry a captured variant `layout` of a packet whose hand
        # annotation belongs to a file sorting after P02.json (W04 0x7C07 short form, 0x7037 trailing bytes)
        for srv, d in a.get("evidence", {}).items():
            for op, v in d.items():
                if "layout" in v:
                    variants.setdefault((srv, int(op, 16), client_dir(v.get("dir"))), []).append(v["layout"])
    names = {}
    known = {k: {C2S: set(), S2C: set()} for k in list(CLIENT_CLASS) + ["link"]}
    for e in json.load(open(os.path.join(DOCS, "opcodes.json"))):
        op = int(e["op"], 16)
        names[op] = e["name"]
        for r in e["received_by"]:
            b, cls = r.split(":")[0], ":".join(r.split(":")[1:-1])
            if b in CLIENT_CLASS and cls == CLIENT_CLASS[b]:
                known[b][C2S].add(op)
    layouts = {}
    for b in CLIENT_CLASS:
        lp = os.path.join(EXPORTS, b, "layouts.json")
        l = json.load(open(lp)) if os.path.exists(lp) else {"s2c": {}, "c2s": {}}
        layouts[b] = {S2C: {int(k, 16): v for k, v in l["s2c"].items()},
                      C2S: {int(k, 16): v[CLIENT_CLASS[b]] for k, v in l["c2s"].items() if CLIENT_CLASS[b] in v}}
        known[b][S2C] |= set(layouts[b][S2C]) | {op for op in names if op not in known[b][C2S]}
        known[b][C2S] |= set(layouts[b][C2S])
    for (srv, op, d) in packets:
        if srv in known and d in known[srv]:
            known[srv][d].add(op)
    # server links (plaintext): one table for both directions; the annotations carry free-form dirs ("WM→CharDB",
    # "Z→WM", ...), the first one per opcode wins (same rule as make_dissector.py)
    # P02 batch 2: one opcode can have several link layouts (0x10D2 CharDB→Zone free-stat ack vs CharDB→WM single-option
    # block); decode_packet tries them all in this order (link_alts) and keeps the first that fits the payload
    link_ann, link_alts = {}, {}
    for (srv, op, d), v in sorted(packets.items(), key=lambda x: (x[0][0], x[0][1], str(x[0][2]))):
        if d not in (C2S, S2C):
            link_ann.setdefault(op, v)
            link_alts.setdefault(op, []).append(v)
    known["link"][C2S] = known["link"][S2C] = set(names) | set(link_ann)
    # PDB layouts, fallback below hand annotations and above layouts.json: the 2016 server PDBs (work item S01, same
    # build, "pdb2016") first, then the 2017 client PDB (work item C02, "pdb2017"). A pdb2016 struct that is only a
    # name-alias guess yields to pdb2017's own struct (0x182a). Each entry carries its label in "src".
    pdb = {}
    for fn, lab in (("pdb2016-layouts.json", "pdb2016"), ("pdb-layouts.json", "pdb2017")):
        pp = os.path.join(DOCS, fn)
        pj = json.load(open(pp)) if os.path.exists(pp) else {"opcodes": {}, "structs": {}}
        for n, st in pj["structs"].items():
            structs.setdefault(n, st)
        for k, v in pj["opcodes"].items():
            op, old = int(k, 16), pdb.get(int(k, 16))
            if "fields" in v and (old is None or old.get("struct_alias") and not v.get("struct_alias")):
                pdb[op] = dict(v, src=lab)
    errs = {int(k, 16): v.get("text") or v.get("literal") for k, v in
            json.load(open(os.path.join(DOCS, "client-error-codes.json"))).items()}
    return dict(structs=structs, packets=packets, names=names, known=known, layouts=layouts, errors=errs, pdb=pdb,
                link_ann=link_ann, link_alts=link_alts, variants=variants)


def default_ports():
    """ServerInfo.txt type-20 rows -> {port: kind}, plus the server-link listeners as link"""
    ports = {}
    path = os.path.join(ROOT, "Files/Server/2016/9Data/ServerInfo/ServerInfo.txt")
    for line in open(path, encoding="latin-1") if os.path.exists(path) else []:
        m = re.match(r'\s*SERVER_INFO\s+"([^"]+)",\s*\d+,\s*\d+,\s*\d+,\s*20,\s*"[^"]*",\s*(\d+)', line)
        if m:
            n = m.group(1).upper()
            ports[int(m.group(2))] = "login" if "LOGIN" in n else "wm" if n.endswith("_WM") else "zone"
    ports = ports or {9010: "login", 9110: "wm", 9210: "zone", 9212: "zone", 9214: "zone", 9216: "zone"}
    return {**{p: "link" for p in link_ports()}, **ports}


def link_ports():
    """ServerInfo.txt server-link listeners (types 0-3 DB servers, 5 Login<-WM, 6 WM<->zone) -> {port: name}"""
    path, out = os.path.join(ROOT, "Files/Server/2016/9Data/ServerInfo/ServerInfo.txt"), {}
    for line in open(path, encoding="latin-1") if os.path.exists(path) else []:
        m = re.match(r'\s*SERVER_INFO\s+"PG_([^"]+)",\s*\d+,\s*\d+,\s*\d+,\s*([0-356]),\s*"[^"]*",\s*(\d+)', line)
        if m:
            out[int(m.group(3))] = m.group(1)
    return out


# ---------------------------------------------------------------- field decoding
INT = {"u8": "<B", "i8": "<b", "u16": "<H", "i16": "<h", "u32": "<I", "i32": "<i", "u64": "<Q", "i64": "<q",
       "f32": "<f", "char": "<B", "byte": "<B"}


def cstr(b):
    return b.split(b"\0", 1)[0].decode("cp1252", "replace")


def struct_of(base, structs):
    """struct definition by name; "Inner" also finds a nested "Outer::Inner" when the suffix is unique (P02)"""
    if base in structs:
        return structs[base]
    hits = [k for k in structs if k.endswith("::" + base)]
    return structs[hits[0]] if len(hits) == 1 else None


def inline_struct(typ):
    """'{u8,u8}[n]' or '{u8 a; u16 b}[n]' -> (base, struct dict, '[n]') or None (anonymous element types of hand
    annotations; named members since P02 batch 4: Z32's 0xBCD5 `{u8 Machine; u16 BetUnits}[3]`)"""
    m = re.fullmatch(r"\{([\w,; ]+)\}((?:\[[\w.]*\])*)", typ)
    if not m:
        return None
    parts = [x.split() for x in re.split(r"[,;]", m.group(1)) if x.strip()]
    if not parts or not all(len(t) in (1, 2) and t[0] in INT for t in parts):
        return None
    fs, off = [], 0
    for i, t in enumerate(parts):
        fs.append([off, t[0], t[1] if len(t) == 2 else f"f{i}", ""])
        off += struct.calcsize(INT[t[0]])
    return "{" + m.group(1) + "}", dict(size=off, fields=fs), m.group(2)


def decode_ann(payload, fields, structs, docs):
    """annotation fields [[off, type, name, note]] -> (list of (name, value), covered bytes, end, problem)

    Type forms: INT names, char[n], u8/byte[n], `bytes` (rest of the payload), struct names (also the suffix of a
    nested `Outer::Inner`), inline `{u8,u16}` elements, dims `[n]` / `[countField]` / `[]` (rest of the payload),
    `struct[count]` followed by `name[i].member` fields at the element offsets. A struct whose first field is
    `datasize` is variable-length: each element takes 1 + datasize bytes (PROTO_ITEMPACKET_INFORM)."""
    out, cov, pos, vals, variable = [], set(), 0, {}, False
    fields, k = list(fields), 0
    while k < len(fields):
        off, typ, name, _ = fields[k][:4]
        typ = re.sub(r"\s*\([^)]*\)", "", typ)                 # "tm (9×i32)[28]" -> "tm[28]" (comment in the type)
        k += 1
        if not variable:
            pos = off
        sub = []                                               # `struct[num]` + `name[i].x` overlay (Z11, Z17)
        while k < len(fields) and str(fields[k][2]).startswith(name + "[i]."):
            sub.append([fields[k][0] - off, fields[k][1], fields[k][2][len(name) + 4:], ""])
            k += 1
        inl = inline_struct(typ)
        if inl:
            base, sdef, dimtxt = inl
        else:
            # a dim may name a count field (pdb2017: dotted); PDB nested anonymous element types keep their
            # "Outer::<unnamed-type-member>" name (P02 batch 3: 0x180F maparray, 0xBCD5 MachineIndex)
            m = re.fullmatch(r"(\w+(?:::(?:\w+|<unnamed-type-\w+>))*)((?:\[[\w.]*\])*)", typ)
            if not m:
                return out, cov, pos, f"unparsed type {typ}"
            base, dimtxt = m.group(1), m.group(2)
            sdef = struct_of(base, structs)
            if sub:
                sdef = dict(size=max(o + elem_size(t, structs) for o, t, _, _ in sub), fields=sub)
        dims = re.findall(r"\[([\w.]*)\]", dimtxt)
        dims_n = []
        dsz = bool(sdef) and sdef["fields"] and sdef["fields"][0][2] == "datasize"
        esz = sdef["size"] if sdef else struct.calcsize(INT[base]) if base in INT else 1
        for d in dims:
            if d.isdigit():
                dims_n.append(int(d))
            else:
                variable = True
                c = vals.get(d)
                dims_n.append(c if isinstance(c, int) else None if dsz else max(0, len(payload) - pos) // max(esz, 1))
        if sdef:
            n = dims_n[0] if dims_n else 1
            items, q = [], pos
            while (n is None and q < len(payload)) or (n is not None and len(items) < n):
                ssz = 1 + payload[q] if dsz and q < len(payload) else sdef["size"]
                if q + ssz > len(payload):
                    return out, cov, q + ssz, f"{name}[{len(items)}]: needs {ssz} bytes at {q}, payload has {len(payload)}"
                items.append(dict(decode_ann(payload[q:q + ssz], sdef["fields"], structs, docs)[0]))
                q += ssz
            val, size = items if dims_n else items[0], q - pos
        else:
            esz = 1 if base not in INT else struct.calcsize(INT[base])
            count = 1
            for d in dims_n:
                count *= d
            size = esz * count if dims_n or base != "bytes" else max(0, len(payload) - pos)
            if pos + size > len(payload):
                return out, cov, pos + size, f"{name}: needs {size} bytes at {pos}, payload has {len(payload)}"
            raw = payload[pos:pos + size]
            if base == "char" and dims_n:
                val = cstr(raw)
            elif base in ("u8", "byte") and dims_n:
                val = raw
            elif base in INT:
                vs = [struct.unpack(INT[base], raw[i:i + esz])[0] for i in range(0, size, esz)]
                val = vs[0] if not dims_n else vs
            else:
                val = raw
            if base == "bytes":
                variable = True
        vals[name] = val
        if isinstance(val, int) and re.search(r"error|reason", name) and val in docs["errors"]:
            val = f"{val:#06x} ({docs['errors'][val]})"
        out.append((name, val))
        cov.update(range(pos, pos + size))
        pos += size
    return out, cov, pos, None


def elem_size(typ, structs):
    """byte size of one annotation field type with fixed dims (used for `name[i].x` overlays)"""
    m = re.fullmatch(r"(\w+(?:::\w+)*)((?:\[\d+\])*)", typ)
    if not m:
        return 1
    sdef = struct_of(m.group(1), structs)
    n = sdef["size"] if sdef else struct.calcsize(INT[m.group(1)]) if m.group(1) in INT else 1
    for d in re.findall(r"\[(\d+)\]", m.group(2)):
        n *= int(d)
    return n


def decode_gen(payload, fields):
    """generated layout fields {off: {type,size}} -> (list of (name, value), covered)"""
    out, cov = [], set()
    for off in sorted(fields, key=int):
        f, o = fields[off], int(off)
        if o in cov or o >= len(payload):
            continue
        t, n = f["type"], f.get("size") or 0
        if t.startswith("char") and (n > 1 or t == "char*"):
            n = n or (payload.find(b"\0", o) + 1 or len(payload)) - o
            val = cstr(payload[o:o + n])
        elif t in INT and o + struct.calcsize(INT[t]) <= len(payload):
            n = struct.calcsize(INT[t])
            val = struct.unpack(INT[t], payload[o:o + n])[0]
        else:
            n = n or len(payload) - o
            val = payload[o:o + n]
        if any(i in cov for i in range(o, o + n)):
            continue
        out.append((f"+{o}", val))
        cov.update(range(o, o + n))
    return out, cov


def const_of(expr):
    m = re.fullmatch(r"'(\\?)(.)'", expr)
    if m:
        return 0 if m.group(0) == "'\\0'" else ord(m.group(2))
    try:
        return int(expr, 0)
    except ValueError:
        return None


def pdb_pick(e, n):
    """PDB entry or one of its alias layouts ("alts", same opcode value) whose size fits an n-byte payload"""
    return next((c for c in [e] + e.get("alts", []) if c["size"] == n or c["variable"] and n >= c["size"]), e)


def decode_packet(kind, d, op, payload, docs):
    """-> dict(name, source, fields, covered, doc_size, issues)"""
    issues = []
    ann = docs["link_ann"].get(op) if kind == "link" else docs["packets"].get((kind, op, d))
    src = "annotation"
    if ann is None and op in docs.get("pdb", {}):
        ann, src = pdb_pick(docs["pdb"][op], len(payload)), docs["pdb"][op].get("src", "pdb2017")
    name = (ann or {}).get("name") or docs["names"].get(op)
    lay = docs["layouts"].get(kind, {}).get(d, {}).get(op)
    for c in (lay or {}).get("len_checks", []) if d == C2S else []:
        m = re.fullmatch(r"[=!]= (0x[0-9a-f]+|\d+)", c)
        if m and int(m.group(1), 0) != len(payload) + 2:      # length checks compare the body (opcode + payload)
            issues.append(f"length check violated: handler requires body length {int(m.group(1), 0)}, got {len(payload) + 2}")
    if ann is not None:
        fields, cov, end, prob = decode_ann(payload, ann["fields"], docs["structs"], docs)
        for alt in docs.get("link_alts", {}).get(op, [])[1:] if kind == "link" and (prob or end != len(payload)) else []:
            r = decode_ann(payload, alt["fields"], docs["structs"], docs)
            if not r[3] and r[2] == len(payload):
                (fields, cov, end, prob), name = r, alt.get("name") or name
                break
        for alt in docs.get("variants", {}).get((kind, op, d), []) if kind != "link" and (prob or end != len(payload)) else []:
            r = decode_ann(payload, alt, docs["structs"], docs)
            if not r[3] and r[2] == len(payload):
                (fields, cov, end, prob), src = r, "annotation (captured variant)"
                break
        # P02 batch 2: a client-facing hand annotation whose types the decoder cannot read (Z03 0x240C `struct`,
        # 0x2452 `struct[targetnum]`) or that does not fit: use the PDB layout when it decodes the payload exactly
        if kind != "link" and src == "annotation" and (prob or end != len(payload)) and op in docs.get("pdb", {}):
            alt = pdb_pick(docs["pdb"][op], len(payload))
            r = decode_ann(payload, alt["fields"], docs["structs"], docs)
            if not r[3] and r[2] == len(payload):
                (fields, cov, end, prob), src = r, docs["pdb"][op].get("src", "pdb2017") + " (annotation did not fit)"
        if prob:
            issues.append(prob)
        elif end != len(payload):
            issues.append(f"size {len(payload)} != documented {end}")
        return dict(name=name, source=src, fields=fields, covered=cov, doc_size=end, issues=issues)
    if lay is None:
        return dict(name=name, source=None, fields=[], covered=set(), doc_size=None, issues=issues)
    if d == C2S:
        fields, cov = decode_gen(payload, lay["fields"])
        for off, f in lay["fields"].items():
            if f["checks"]:
                issues.append(f"info: +{off} handler checks {f['checks']}")
        return dict(name=name, source="generated", fields=fields, covered=cov, doc_size=None, issues=issues)
    sites = [s for s in lay if s["size"] == len(payload)] or [s for s in lay if s["size"] is None]
    if not sites:
        issues.append(f"size {len(payload)} matches no send site (documented: {sorted({s['size'] for s in lay})})")
        sites = lay
    fields, cov = decode_gen(payload, sites[0]["fields"])
    for off in sites[0]["fields"]:                       # constants written at every matching send site
        allowed = set()
        for s in sites:
            f = s["fields"].get(off)
            cs = (f["values"] + [const_of(x) for x in f["exprs"]]) if f else [None]
            if not cs or None in cs:
                allowed = None
                break
            allowed |= {(c, f["type"], f["size"]) for c in cs}
        if allowed and int(off) < len(payload):
            t, n = next(iter(allowed))[1:]
            n = struct.calcsize(INT[t]) if t in INT else n or 1
            v = int.from_bytes(payload[int(off):int(off) + n], "little")
            okv = {c & ((1 << 8 * n) - 1) for c, _, _ in allowed}
            if v not in okv:
                issues.append(f"+{off}: value {v:#x} not among the constants the code writes {sorted(okv)}")
    sz = {s["size"] for s in sites}
    return dict(name=name, source="generated", fields=fields, covered=cov,
                doc_size=sz.pop() if len(sz) == 1 else None, issues=issues)


# ---------------------------------------------------------------- main decode
def decode_capture(path, ports, show_secrets=False):
    docs = load_docs()
    frames, comments = read_capture(path)
    t0 = frames[0][0] if frames else 0.0
    conns, order = {}, []
    for i, (ts, link, pkt) in enumerate(frames):
        ip = ipv4_of(link, pkt)
        t = ip and tcp_of(ip)
        if not t:
            continue
        sip, sp, dip, dp, seq, flags, data = t
        if dp in ports:
            key, d = (sip, sp, dip, dp), C2S
        elif sp in ports:
            key, d = (dip, dp, sip, sp), S2C
        else:
            continue
        if key not in conns:
            conns[key] = {C2S: Direction(), S2C: Direction(), "first": i}
            order.append(key)
        dr = conns[key][d]
        if flags & 0x02:                                     # SYN
            dr.isn = (seq + 1) % 2**32
        elif data:
            dr.segs.append((seq, i, data))
    streams, packets = [], []
    count, lnames = collections.Counter(), link_ports()
    for key in order:
        kind = ports[key[3]]
        label = lnames.get(key[3], f"link{key[3]}") if kind == "link" else kind   # link streams: listener name
        count[label] += 1
        sid = f"{label}#{count[label]}"
        st = dict(id=sid, kind=kind, client=f"{key[0]}:{key[1]}", server=f"{key[2]}:{key[3]}",
                  first_frame=conns[key]["first"], gaps={}, problems=[], seeds=[], decrypt=[])
        streams.append(st)
        plist = {}
        for d in (C2S, S2C):
            dr = conns[key][d]
            chunks, gaps, fmap, dup = dr.assemble()
            st["gaps"][d] = gaps
            if dup:
                st["problems"].append(f"{d}: {dup} retransmitted/duplicate segments ignored")
            pk, probs = deframe(chunks, gaps, fmap, dr.isn is not None, d == C2S and kind != "link", docs["known"][kind][d])
            st["problems"] += [f"{d}: {p}" for p in probs]
            plist[d] = pk
        # seeds from the server side, then decrypt the client side
        seeds = []
        for p in plist[S2C]:
            p["op"], p["payload"] = struct.unpack("<H", p["body"][:2])[0], p["body"][2:]
            if p["op"] == 0x0807 and len(p["payload"]) >= 2:
                s = struct.unpack("<H", p["payload"][:2])[0]
                seeds.append((p["frame"], s))
                st["seeds"].append(dict(frame=p["frame"], seed=s, start_index=s % 499))
        idx, si, group = None, 0, []

        def flush():
            if group:
                i0, score, tied = best_idx([g["body"] for g in group], docs["known"][kind][C2S],
                                           FIRST_C2S.get(kind) if group[0]["off"] == 0 else None)
                st["decrypt"].append(f"no seed for {len(group)} client packet(s) from frame {group[0]['frame']}: "
                                     f"brute-forced start index {i0} ({score}/{len(group)} known opcodes, {tied} candidate(s) tied)")
                for g in group:
                    g["dec"], i0 = xor(g["body"], i0)
                group.clear()
        for p in plist[C2S]:
            if kind == "link":                               # server links: no cipher
                p["dec"] = p["body"]
                continue
            while si < len(seeds) and seeds[si][0] <= p["frame"]:
                flush()
                idx = seeds[si][1] % 499
                st["decrypt"].append(f"seed {seeds[si][1]} (frame {seeds[si][0]}): index {idx}")
                si += 1
            # offset 0 of a capture without the SYN: a seed seen before it still applies (P02)
            if p["resync"] and p["off"]:
                flush()
                idx = None
            if idx is None:
                group.append(p)
            else:
                p["dec"], idx = xor(p["body"], idx)
        flush()
        for p in plist[C2S]:
            p["op"], p["payload"] = struct.unpack("<H", p["dec"][:2])[0], p["dec"][2:]
        for d in (C2S, S2C):
            for p in plist[d]:
                payload = p["payload"]
                if kind == "login" and d == C2S and p["op"] == 0x0C5A and not show_secrets:
                    payload = payload[:260] + b"*" * max(0, min(296, len(payload)) - 260) + payload[296:]
                dp = decode_packet(kind, d, p["op"], payload, docs)
                packets.append(dict(frame=p["frame"], time=frames[p["frame"]][0] - t0, abs_time=frames[p["frame"]][0],
                                    stream=sid, server=kind, dir=d, op=p["op"], stream_offset=p["off"],
                                    payload=payload, **dp))
    packets.sort(key=lambda p: (p["frame"], p["stream"], p["stream_offset"]))
    for i, p in enumerate(packets):
        p["i"] = i
    return dict(capture=path, frames=frames, t0=t0, comments=comments, streams=streams, packets=packets, docs=docs)


def fmt_val(v):
    if isinstance(v, bytes):
        return v.hex() if len(v) <= 64 else v[:64].hex() + f"… ({len(v)} B)"
    if isinstance(v, str):
        return v if re.fullmatch(r"0x[0-9a-f]{4} \(.*\)", v) else repr(v)
    if isinstance(v, int):
        return f"{v} ({v:#x})" if v > 9 else str(v)
    if isinstance(v, list) and len(v) > 16 and all(isinstance(x, int) for x in v):
        return "[" + ", ".join(map(str, v[:16])) + f", … {len(v)} items]"
    return json.dumps(v, ensure_ascii=False, default=bytes.hex) if isinstance(v, (list, dict)) else str(v)


def write_decoded(res, f):
    f.write(f"# {os.path.basename(res['capture'])}: {len(res['packets'])} packets, {len(res['frames'])} frames\n")
    f.write("# fields marked (gen) come from generated layouts (layouts.json), unverified\n\n")
    comm = sorted(res["comments"].items())
    ci = 0
    for p in res["packets"]:
        while ci < len(comm) and comm[ci][0] <= p["frame"]:
            fr = comm[ci][0]
            f.write(f"===== frame {fr} +{res['frames'][fr][0] - res['t0']:.6f}  COMMENT: {comm[ci][1]}\n")
            ci += 1
        f.write(f"[{p['i']:5}] f{p['frame']:<6} +{p['time']:.6f}  {p['dir']}  {p['stream']:<8} "
                f"0x{p['op']:04X}  {p['name'] or '?'}  ({len(p['payload'])} B)\n")
        tag = {"generated": " (gen)", "pdb2016": " (pdb2016)", "pdb2017": " (pdb2017)"}.get(p["source"], "")
        for name, v in p["fields"]:
            f.write(f"          {name}{tag} = {fmt_val(v)}\n")
        unc = [i for i in range(len(p["payload"])) if i not in p["covered"]]
        if unc:
            f.write(f"          undocumented +{unc[0]}..: {p['payload'][unc[0]:unc[0] + 64].hex(' ')}"
                    f"{' …' if len(p['payload']) - unc[0] > 64 else ''}\n")
        for s in p["issues"]:
            if not s.startswith("info:"):
                f.write(f"          !! {s}\n")
    for fr, text in comm[ci:]:
        f.write(f"===== frame {fr} +{res['frames'][fr][0] - res['t0']:.6f}  COMMENT: {text}\n")


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and out[-1][1] == x - 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out)


def build_report(res):
    docs, by = res["docs"], collections.OrderedDict()
    for p in res["packets"]:
        by.setdefault((p["server"], p["dir"], p["op"]), []).append(p)
    rows = []
    for (kind, d, op), ps in sorted(by.items()):
        sizes = collections.Counter(len(p["payload"]) for p in ps)
        nz = set()
        for p in ps:
            nz |= {i for i, b in enumerate(p["payload"]) if b and i not in p["covered"]}
        issues = collections.Counter(s for p in ps for s in p["issues"])
        known = op in docs["known"][kind][d] or op in docs["names"]
        rows.append(dict(server=kind, dir=d, op=f"0x{op:04X}", name=ps[0]["name"], count=len(ps),
                         sizes=dict(sizes), doc_size=ps[0]["doc_size"], source=ps[0]["source"],
                         known_opcode=known, nonzero_undocumented=ranges(nz) if nz else "",
                         issues=dict(issues)))
    return rows


def write_report(res, rows, f):
    f.write(f"# Capture report: {os.path.basename(res['capture'])}\n\n")
    f.write(f"{len(res['frames'])} frames, {len(res['packets'])} game packets, {len(res['comments'])} comments.\n\n## Streams\n\n")
    f.write("| Stream | Client | Server | First frame | Seeds | Gaps C→S / S→C |\n|---|---|---|---|---|---|\n")
    for s in res["streams"]:
        f.write(f"| {s['id']} | {s['client']} | {s['server']} | {s['first_frame']} | "
                f"{', '.join(str(x['seed']) for x in s['seeds']) or '–'} | "
                f"{len(s['gaps'][C2S])} / {len(s['gaps'][S2C])} |\n")
    for s in res["streams"]:
        notes = s["decrypt"] + s["problems"] + [f"{d}: gap of {n} bytes at offset {o}" for d in (C2S, S2C) for o, n in s["gaps"][d]]
        if notes:
            f.write(f"\n**{s['id']}**\n\n" + "".join(f"- {n}\n" for n in notes))
    f.write("\n## Packet types\n\nsource: `annotation` = hand-verified layout, `pdb2016` = 2016 server PDB struct (pdb2016-layouts.json), `pdb2017` = 2017 client PDB struct (pdb-layouts.json), `generated` = layouts.json, "
            "`–` = no layout documented. *Undoc ≠0* = payload offsets that no documented field covers but were nonzero.\n\n")
    f.write("| Server | Dir | Opcode | Name | Count | Sizes seen | Doc size | Source | Undoc ≠0 | Issues |\n"
            "|---|---|---|---|---|---|---|---|---|---|\n")
    for r in rows:
        sizes = ", ".join(f"{k}×{v}" for k, v in sorted(r["sizes"].items()))
        iss = "; ".join(f"{k} (×{v})" for k, v in r["issues"].items() if not k.startswith("info:"))
        name = r["name"] or ("?" if r["known_opcode"] else "**UNDOCUMENTED OPCODE**")
        f.write(f"| {r['server']} | {r['dir']} | {r['op']} | {name} | {r['count']} | {sizes} | "
                f"{'' if r['doc_size'] is None else r['doc_size']} | {r['source'] or '–'} | {r['nonzero_undocumented']} | {iss} |\n")
    undoc = [r for r in rows if not r["known_opcode"]]
    f.write(f"\n## Opcodes never documented for that server/direction\n\n"
            + ("".join(f"- {r['server']} {r['dir']} {r['op']} (×{r['count']})\n" for r in undoc) or "none\n"))
    info = [(r, k) for r in rows for k in r["issues"] if k.startswith("info:")]
    if info:
        f.write("\n## Value checks in C→S handlers (for manual comparison)\n\n"
                + "".join(f"- {r['server']} {r['op']}: {k[6:]}\n" for r, k in info))


def to_json(res, rows):
    return dict(capture=os.path.basename(res["capture"]), frames=len(res["frames"]), start_time=res["t0"],
                comments=[dict(frame=fr, time=res["frames"][fr][0] - res["t0"], text=t) for fr, t in sorted(res["comments"].items())],
                streams=[{k: v for k, v in s.items()} for s in res["streams"]],
                packets=[dict(i=p["i"], frame=p["frame"], time=round(p["time"], 6), abs_time=p["abs_time"],
                              stream=p["stream"], server=p["server"], dir=p["dir"], op=f"0x{p['op']:04X}",
                              name=p["name"], size=len(p["payload"]), payload=p["payload"].hex(),
                              source=p["source"], fields=[[n, v] for n, v in p["fields"]],
                              issues=p["issues"]) for p in res["packets"]],
                report=rows)


def transcript_problems(res):
    """reasons why the client-facing streams of res cannot give an exact transcript (ADR 0008)"""
    out = []
    for s in res["streams"]:
        if s["kind"] == "link":
            continue
        out += [f"{s['id']}: {d}: gap of {n} bytes at offset {o}" for d in (C2S, S2C) for o, n in s["gaps"][d]]
        out += [f"{s['id']}: {x}" for x in s["problems"] if "retransmitted/duplicate" not in x]
        out += [f"{s['id']}: {x}" for x in s["decrypt"] if "brute-forced" in x]
    return out


def transcript_lines(res):
    """ADR 0008 transcript, format in server/docs/technical/testing.md. res must be decoded with show_secrets=True."""
    out = [f"# transcript of {os.path.basename(res['capture'])} (format: server/docs/technical/testing.md)",
           f"# start {res['t0']:.6f}"]
    for p in res["packets"]:
        if p["server"] != "link":
            out.append(f"{p['abs_time']:.6f} {p['stream']} {'C' if p['dir'] == C2S else 'S'} "
                       f"0x{p['op']:04X} {p['payload'].hex() or '-'}")
    return out


def run(path, ports, show_secrets=False, out_dir=None):
    res = decode_capture(path, ports, show_secrets)
    rows = build_report(res)
    out_dir = out_dir or os.path.dirname(os.path.abspath(path))
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.join(out_dir, os.path.basename(path))
    with open(stem + ".decoded.txt", "w") as f:
        write_decoded(res, f)
    with open(stem + ".report.md", "w") as f:
        write_report(res, rows, f)
    with open(stem + ".json", "w") as f:
        json.dump(to_json(res, rows), f, indent=1, ensure_ascii=False, default=bytes.hex)
    return res, rows, stem


# ---------------------------------------------------------------- self-test
def selftest():
    import tempfile

    def frame(body):
        return (bytes([len(body)]) if len(body) < 256 else b"\0" + struct.pack("<H", len(body))) + body

    docs = load_docs()
    gen_op, gen_site, gen_off = next((op, sites[0], off) for op, sites in sorted(docs["layouts"]["wm"][S2C].items())
                                     if ("wm", op, S2C) not in docs["packets"] and op not in docs["pdb"] and len(sites) == 1 and sites[0]["size"]
                                     for off, f in sites[0]["fields"].items()
                                     if f["type"] == "u8" and f["values"] and not f["exprs"] and int(off) < sites[0]["size"])
    unknown_op = next(op for op in range(0xFFFF, 0, -1) if op not in docs["names"] and op not in docs["known"]["login"][S2C])

    def tcp(src, dst, sp, dp, seq, data, flags=0x18):
        t = struct.pack(">HHIIBBHHH", sp, dp, seq, 0, 5 << 4, flags, 65535, 0, 0) + data
        ip = struct.pack(">BBHHHBBH4s4s", 0x45, 0, 20 + len(t), 0, 0x4000, 64, 6, 0,
                         bytes(map(int, src.split("."))), bytes(map(int, dst.split(".")))) + t
        return b"\x02\0\0\0\x01\x02\x02\0\0\0\x01\x01\x08\x00" + ip

    C, S = "10.0.0.2", "10.0.0.1"
    pkts = []                                                # (ethernet frame, comment)
    seed, version, user, pw = 0x1234, b"20151116141627".ljust(64, b"\0"), b"tester", b"secret"
    worlds = b"".join(bytes([i]) + f"World{i}".encode().ljust(16, b"\0") + b"\x06" for i in range(16))
    c2s_bodies = [struct.pack("<H", 0x0C65) + version,
                  struct.pack("<H", 0x0C5A) + user.ljust(256, b"\0") + b"\0" * 4 + pw.ljust(36, b"\0") + b"\0" * 20]
    enc, idx = [], seed % 499
    for b in c2s_bodies:
        e, idx = xor(b, idx)
        enc.append(e)
    cs, ss = 1000, 5000
    pkts.append((tcp(C, S, 50000, 9010, cs - 1, b"", 0x02), None))
    pkts.append((tcp(S, C, 9010, 50000, ss - 1, b"", 0x12), None))
    s1 = frame(struct.pack("<HH", 0x0807, seed))
    pkts.append((tcp(S, C, 9010, 50000, ss, s1), None)); ss += len(s1)
    c1 = frame(enc[0])
    pkts.append((tcp(C, S, 50000, 9010, cs, c1), "user: client started")); cs += len(c1)
    s2 = frame(struct.pack("<HB", 0x0C67, 1) + b"\0")
    pkts.append((tcp(S, C, 9010, 50000, ss, s2), None)); ss += len(s2)
    c2 = frame(enc[1])                                       # long form (318-byte body), split over two frames, sent out of order + retransmit
    assert c2[0] == 0
    pkts.append((tcp(C, S, 50000, 9010, cs + 100, c2[100:]), None))
    pkts.append((tcp(C, S, 50000, 9010, cs, c2[:100]), "user: pressed login"))
    pkts.append((tcp(C, S, 50000, 9010, cs + 100, c2[100:]), None)); cs += len(c2)
    c3 = frame(xor(struct.pack("<H", 0x0C37) + b"t" * 10, idx)[0])   # token login with wrong length
    pkts.append((tcp(C, S, 50000, 9010, cs, c3), None)); cs += len(c3)
    s3 = frame(struct.pack("<HB", 0x0C0A, len(worlds) // 18) + worlds)
    assert s3[0] == 0                                        # 291-byte body: long form
    pkts.append((tcp(S, C, 9010, 50000, ss, s3[:150]), None))
    pkts.append((tcp(S, C, 9010, 50000, ss + 150, s3[150:] + frame(struct.pack("<HH", 0x0C09, 0x45))
                  + frame(struct.pack("<HBB", 0x0C05, 1, 7)) + frame(struct.pack("<HB", unknown_op, 0))), None))
    # wm stream captured mid-session: no SYN, no seed -> framing sync + brute-forced start index
    wb = [struct.pack("<HB", 0x1001, 0), struct.pack("<H", 0x0C0F) + b"tester".ljust(256, b"\0") + bytes(64),
          struct.pack("<HB", 0x1001, 1)]
    widx, wdata = 400, b""
    for b in wb:
        e, widx = xor(b, widx)
        wdata += frame(e)
    gpay = bytearray(gen_site["size"])
    gpay[int(gen_off)] = (gen_site["fields"][gen_off]["values"][0] + 1) & 0xFF    # contradicts the constant
    pkts.append((tcp(C, S, 50002, 9110, 123456, wdata), None))
    pkts.append((tcp(S, C, 9110, 50002, 654321, frame(struct.pack("<H", gen_op) + bytes(gpay))), None))
    # zone stream: client 0x0806 before the seed (start index unknown -> brute force), then seeded traffic
    zseed, zi0 = 321, 77
    zb = [struct.pack("<H", 0x0806), struct.pack("<H", 0x1803)]
    pkts.append((tcp(C, S, 50001, 9210, 7000 - 1, b"", 0x02), None))
    e0, _ = xor(zb[0], zi0)
    pkts.append((tcp(C, S, 50001, 9210, 7000, frame(e0)), None))
    pkts.append((tcp(S, C, 9210, 50001, 9000, frame(struct.pack("<HH", 0x0807, zseed))), None))
    e1, _ = xor(zb[1], zseed % 499)
    pkts.append((tcp(C, S, 50001, 9210, 7000 + 3, frame(e1)), None))
    # second zone stream without SYN ("displayed packets" save, P02): the seed comes before the first client packet
    z2seed = 5
    pkts.append((tcp(S, C, 9212, 50003, 11000, frame(struct.pack("<HH", 0x0807, z2seed))), None))
    pkts.append((tcp(C, S, 50003, 9212, 12000, frame(xor(struct.pack("<H", 0x1803), z2seed % 499)[0])), None))
    # server link (plaintext, no seed), e.g. WM <-> Character DB
    lop, lv = next((op, v) for op, v in sorted(docs["link_ann"].items())
                   if v["fields"] and all(f[1] in ("u8", "u16", "u32") for f in v["fields"]))
    lpay = bytes(range(1, 1 + max(f[0] + {"u8": 1, "u16": 2, "u32": 4}[f[1]] for f in lv["fields"])))
    lport = min(p for p, n in link_ports().items() if n.endswith("CDB"))
    pkts.append((tcp(S, S, 50010, lport, 100, frame(struct.pack("<H", lop) + lpay)), None))
    pkts.append((tcp(S, S, lport, 50010, 200, frame(struct.pack("<H", lop) + lpay)), None))

    tmp = tempfile.mkdtemp()
    for fmt in ("pcapng", "pcap"):
        path = os.path.join(tmp, f"synthetic.{fmt}")
        with open(path, "wb") as f:
            if fmt == "pcap":                                # Npcap loopback (DLT_NULL) instead of Ethernet
                f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 0))
                for i, (p, _) in enumerate(pkts):
                    p = b"\x02\0\0\0" + p[14:]
                    f.write(struct.pack("<IIII", 1700000000 + i, 0, len(p), len(p)) + p)
            else:
                f.write(struct.pack("<IIIHHq", 0x0A0D0D0A, 28, 0x1A2B3C4D, 1, 0, -1) + struct.pack("<I", 28))
                f.write(struct.pack("<IIHHI", 1, 20, 1, 0, 65535) + struct.pack("<I", 20))
                for i, (p, c) in enumerate(pkts):
                    opt = b""
                    if c:
                        cb = c.encode()
                        opt = struct.pack("<HH", 1, len(cb)) + cb.ljust((len(cb) + 3) & ~3, b"\0") + b"\0\0\0\0"
                    ts = (1700000000 + i) * 10**6
                    body = struct.pack("<IIIII", 0, ts >> 32, ts & 0xFFFFFFFF, len(p), len(p)) \
                        + p.ljust((len(p) + 3) & ~3, b"\0") + opt
                    f.write(struct.pack("<II", 6, len(body) + 12) + body + struct.pack("<I", len(body) + 12))
        res, rows, stem = run(path, default_ports())
        ps = res["packets"]
        got = [(p["stream"], p["dir"], p["op"]) for p in ps]
        want = [("login#1", S2C, 0x0807), ("login#1", C2S, 0x0C65), ("login#1", S2C, 0x0C67),
                ("login#1", C2S, 0x0C5A), ("login#1", C2S, 0x0C37), ("login#1", S2C, 0x0C0A),
                ("login#1", S2C, 0x0C09), ("login#1", S2C, 0x0C05), ("login#1", S2C, unknown_op),
                ("wm#1", C2S, 0x1001), ("wm#1", C2S, 0x0C0F), ("wm#1", C2S, 0x1001), ("wm#1", S2C, gen_op),
                ("zone#1", C2S, 0x0806), ("zone#1", S2C, 0x0807), ("zone#1", C2S, 0x1803),
                ("zone#2", S2C, 0x0807), ("zone#2", C2S, 0x1803),
                 (f"{link_ports()[lport]}#1", C2S, lop), (f"{link_ports()[lport]}#1", S2C, lop)]
        assert got == want, got
        login = dict(ps[3]["fields"])
        assert login["sUserName"] == "tester" and set(login["sPassword"]) == {"*"}, login   # L00 names (pdb2017)
        assert ps[1]["payload"] == c2s_bodies[0][2:]
        assert ps[3]["payload"][:260] == c2s_bodies[1][2:262] and ps[3]["payload"][296:] == c2s_bodies[1][298:]
        wl = dict(ps[5]["fields"])
        assert wl["count"] == 16 and wl["worlds"][3]["world_name"] == "World3" and not ps[5]["issues"], ps[5]
        assert "Please check ID" in dict(ps[6]["fields"])["error"]
        assert any("length check violated" in s for s in ps[4]["issues"]), ps[4]["issues"]
        # pdb2017 fallback: an unannotated fixed-size PDB packet decodes cleanly; dotted count fields work
        pop = next(o for o, v in sorted(docs["pdb"].items()) if ("zone", o, S2C) not in docs["packets"]
                   and v["size"] > 0 and not v["variable"])
        r = decode_packet("zone", S2C, pop, bytes(docs["pdb"][pop]["size"]), docs)
        assert r["source"] == docs["pdb"][pop]["src"] and not r["issues"], r
        assert docs["pdb"][0x1801]["src"] == "pdb2016" and docs["pdb"][0x1801]["size"] == 1590     # Name8[49] checksum
        assert docs["pdb"][0x182a]["src"] == "pdb2017" and docs["pdb"][0x182a]["size"] == 0       # alias guess yields
        p17 = next(o for o, v in sorted(docs["pdb"].items()) if v["src"] == "pdb2017" and ("zone", o, S2C) not in docs["packets"]
                   and v["size"] > 0 and not v["variable"])
        r = decode_packet("zone", S2C, p17, bytes(docs["pdb"][p17]["size"]), docs)
        assert r["source"] == "pdb2017" and not r["issues"], r
        assert pdb_pick(docs["pdb"][0x0830], 3)["name"] == "NC_MISC_SERVERPARAMETER_ACK"   # alias layout by size
        # annotation that does not fit -> exact PDB fallback (P02 part 12: Z03's 0x240C `struct`)
        r = decode_packet("zone", S2C, 0x240C, bytes(docs["pdb"][0x240C]["size"]), docs)
        assert r["source"].endswith("(annotation did not fit)") and not r["issues"], r
        # captured variant layout from an `evidence` entry (P02 sweep: W04 0x7C07 4-byte short form)
        vk = ("wm", 0x7C07, S2C)
        assert vk in docs["variants"], sorted(docs["variants"])
        r = decode_packet(vk[0], vk[2], vk[1], bytes(decode_ann(b"\0" * 4096, docs["variants"][vk][0], docs["structs"], docs)[2]), docs)
        assert r["source"] == "annotation (captured variant)" and not r["issues"], r
        f = decode_ann(b"\x02\x01\x00\x02\x00", [[0, "u8", "a.num", ""], [1, "u16[a.num]", "arr", ""]], {}, docs)
        assert f[0] == [("a.num", 2), ("arr", [1, 2])] and f[2] == 5 and not f[3], f
        # type forms added by P02: [] = rest, bytes = rest, Outer::Inner suffix, inline {u8,u8}, name[i].x overlay, datasize
        f = decode_ann(b"\x07\x01\x00\x02\x00", [[0, "u8", "k", ""], [1, "u16[]", "rest", ""]], {}, docs)
        assert f[0] == [("k", 7), ("rest", [1, 2])] and not f[3], f
        f = decode_ann(b"\x07abc", [[0, "u8", "k", ""], [1, "bytes", "tail", ""]], {}, docs)
        assert f[0] == [("k", 7), ("tail", b"abc")] and not f[3], f
        st = {"Outer::Inner": dict(size=2, fields=[[0, "u8", "x", ""], [1, "u8", "y", ""]])}
        f = decode_ann(b"\x01\x02\x03\x04", [[0, "Inner[2]", "e", ""]], st, docs)
        assert f[0] == [("e", [{"x": 1, "y": 2}, {"x": 3, "y": 4}])] and not f[3], f
        f = decode_ann(b"\x02\x01\x02\x03\x04", [[0, "u8", "n", ""], [1, "{u8,u8}[n]", "p", ""]], {}, docs)
        assert f[0] == [("n", 2), ("p", [{"f0": 1, "f1": 2}, {"f0": 3, "f1": 4}])] and not f[3], f
        f = decode_ann(b"\x01\x00\x09\x02\x00\x08", [[0, "S[2]", "s", ""], [0, "u16", "s[i].a", ""], [2, "u8", "s[i].b", ""]], {}, docs)
        assert f[0] == [("s", [{"a": 1, "b": 9}, {"a": 2, "b": 8}])] and not f[3], f
        st = {"V": dict(size=3, fields=[[0, "u8", "datasize", ""], [1, "u8", "id", ""]])}
        f = decode_ann(b"\x01\x05\x02\x06\xff", [[0, "V[]", "v", ""]], st, docs)
        assert f[0] == [("v", [{"datasize": 1, "id": 5}, {"datasize": 2, "id": 6}])] and not f[3], f
        assert [client_dir(d) for d in ("C→WM", "Z→C", C2S, "WM→Z")] == [C2S, S2C, C2S, "WM→Z"]
        f10 = dict(ps[10]["fields"])                         # C01 names it user_id, W01 (merged later) userId
        assert f10.get("userId", f10.get("user_id")) == "tester" and dict(ps[11]["fields"])["slot"] == 1
        assert any("not among the constants" in s for s in ps[12]["issues"]), ps[12]
        assert any("brute-forced start index 400 (3/3" in s for s in res["streams"][1]["decrypt"]), res["streams"][1]
        r = {(x["server"], x["op"]): x for x in rows}
        assert r[("login", "0x0C05")]["nonzero_undocumented"] == "1" and r[("login", f"0x{unknown_op:04X}")]["known_opcode"] is False
        assert res["streams"][0]["seeds"][0]["seed"] == seed
        assert any("1 retransmitted" in s for s in res["streams"][0]["problems"]), res["streams"][0]["problems"]
        assert any("brute-forced start index" in s for s in res["streams"][2]["decrypt"])
        z2 = res["streams"][3]                               # seed before the first client packet, no SYN (P02)
        assert z2["seeds"][0]["seed"] == z2seed and not any("brute-forced" in s for s in z2["decrypt"]), z2
        for lp in ps[-2:]:                                   # link packets: plaintext, decoded from the link annotation
            f0 = lv["fields"][0]
            want0 = int.from_bytes(lpay[f0[0]:f0[0] + {"u8": 1, "u16": 2, "u32": 4}[f0[1]]], "little")
            assert lp["payload"] == lpay and lp["source"] == "annotation" and dict(lp["fields"])[f0[2]] == want0, lp
            assert not lp["issues"] and lp["server"] == "link", lp["issues"]
        rep = open(stem + ".report.md").read()
        assert "| login | C→S | 0x0C5A |" in rep and "secret" not in open(stem + ".decoded.txt").read()
        if fmt == "pcapng":
            assert sorted(res["comments"].values()) == ["user: client started", "user: pressed login"]
            assert "COMMENT: user: pressed login" in open(stem + ".decoded.txt").read()
        j = json.load(open(stem + ".json"))
        assert j["packets"][3]["op"] == "0x0C5A" and b"secret".hex() not in json.dumps(j)
        res2 = decode_capture(path, default_ports(), show_secrets=True)
        assert dict(res2["packets"][3]["fields"])["sPassword"] == "secret"
        tl = transcript_lines(res2)
        assert tl[0].startswith("# transcript of ") and tl[1].startswith("# start "), tl[:2]
        assert all(re.fullmatch(r"\d+\.\d{6} (login|wm|zone)#\d+ [CS] 0x[0-9A-F]{4} ([0-9a-f]+|-)", x) for x in tl[2:])
        nc = sum(p["server"] != "link" for p in res2["packets"])
        assert len(tl) - 2 == nc < len(res2["packets"])
        p0 = res2["packets"][0]
        assert tl[2] == f"{p0['abs_time']:.6f} login#1 S 0x0807 " + p0["payload"].hex(), tl[2]
        pw = [x for x in tl if b"secret".hex() in x]
        assert pw and all(" C 0x0C5A " in x for x in pw)
        assert any("brute-forced" in x for x in transcript_problems(res2))
    # gap handling: drop the first half of the long 0x0C0A -> report gap, resync on 0x0C09
    path = os.path.join(tmp, "gap.pcap")
    with open(path, "wb") as f:
        f.write(struct.pack("<IHHiIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1))
        for i, (p, _) in enumerate(pkts):
            if p is not pkts[9][0]:
                f.write(struct.pack("<IIII", 1700000000 + i, 0, len(p), len(p)) + p)
    res = decode_capture(path, default_ports())
    st = res["streams"][0]
    assert st["gaps"][S2C] == [(len(s1) + len(s2), 150)], st["gaps"]
    assert [p["op"] for p in res["packets"] if p["stream"] == "login#1" and p["dir"] == S2C][-3:] == [0x0C09, 0x0C05, unknown_op]
    # PDB nested anonymous element type (P02 batch 3, 0xBCD5): "Outer::<unnamed-type-x>[count]" resolves by exact name
    st_ = {"O::<unnamed-type-m>": dict(size=3, fields=[[0, "u8", "Machine", ""], [1, "u16", "BetUnits", ""]])}
    r = decode_ann(bytes.fromhex("03000a0001640002f401"), [[0, "u8", "n", ""], [1, "O::<unnamed-type-m>[n]", "m", ""]],
                   st_, {})
    assert r[3] is None and r[2] == 10 and [x["BetUnits"] for x in dict(r[0])["m"]] == [10, 100, 500], r
    print(f"selftest OK ({tmp})")


def main(argv):
    if "--selftest" in argv:
        return selftest()
    ports, show, out, files, i, tdir = default_ports(), False, None, [], 0, None
    while i < len(argv):
        a = argv[i]
        if a == "--port":
            p, k = argv[i + 1].split("=")
            assert k in CLIENT_CLASS or k == "link", f"--port PORT=login|wm|zone|link, got {k}"
            ports[int(p)] = k
            i += 1
        elif a == "--show-secrets":
            show = True
        elif a == "--out":
            out, i = argv[i + 1], i + 1
        elif a == "--transcript":
            tdir, i = argv[i + 1], i + 1
        else:
            files.append(a)
        i += 1
    if not files:
        print(__doc__)
        return 1
    rc = 0
    for path in files:
        if tdir is not None:
            res = decode_capture(path, ports, True)
            bad = transcript_problems(res)
            if bad:
                print(f"{path}: no transcript:", file=sys.stderr)
                print("\n".join("  " + b for b in bad), file=sys.stderr)
                rc = 1
                continue
            lines = transcript_lines(res)
            os.makedirs(tdir, exist_ok=True)
            target = os.path.join(tdir, os.path.splitext(os.path.basename(path))[0] + ".txt")
            with open(target, "w", encoding="ascii", newline="\n") as f:
                f.write("\n".join(lines) + "\n")
            print(f"{path}: {len(lines) - 2} packets -> {target}")
            continue
        res, rows, stem = run(path, ports, show, out)
        print(f"{path}: {len(res['packets'])} packets in {len(res['streams'])} streams -> {stem}.decoded.txt/.report.md/.json")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
