#!/usr/bin/env python3
"""X08 wrapper around X06's bug-register generator (docs/plan/status/X06-register.py, which runs X04-register.py,
X03-register.py and X01-register.py; all left unchanged).

Runs X06's wrapper in `md` mode and post-processes its rows for P02's capture batch 5 (captures s46, s45, s52;
capture-validation §26-§28):
  1. the Evidence column of P02-B41 ... B44 (X06's P02_EV stops at P02-B40): *(captured)* with the § of the capture
     the first table of capture-validation §12 cites, plus the part that stays deduced; P02-B44 was read in the code
     only (found in the batch-5 review);
  2. P02's own batch-4 rows X06 fixed by hand (its P02_EV list overrides X04's join of the second table): the
     batch-5 § of the second table / of the extended entry joined in (P02-B33 §28.2, P02-B35 §28.1 / §28.4,
     P02-B36 §27.8);
  3. the README §5.9 mark added by X08: P02-B33 (Extended: every further 0x1001 of the WM session, §28.2);
  4. cross notes (Handler column, "linked: ..."): P02-B41 <-> Z11-B6 (the two branches of zrpb_Request),
     P02-B43 -> W05-B6 / Z24-B17 (the other CDataReader::Read defects).
The other second-table rows citing §26-§28 (D03-B11, P02-B16, Z04-B2, Z11-B12, Z02-B2, P02-B29, P02-B19, P02-B28,
Z09-B54, Z11-B6) are joined by X04's reader already.

usage (repo root):  python3 -I docs/plan/status/X08-register.py write   # rewrite README §6.1
                    python3 -I docs/plan/status/X08-register.py md      # print the register
"""
import io, re, sys, contextlib, collections

README = 'docs/pseudocode/README.md'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'md'

# --- run X06's wrapper (md) and capture its output and helpers ---------------------------------------------------
buf = io.StringIO()
argv = sys.argv
sys.argv = ['docs/plan/status/X06-register.py', 'md']
ns = {'__name__': 'x06_register'}
with contextlib.redirect_stdout(buf):
    exec(compile(open(sys.argv[0], encoding='utf-8').read(), sys.argv[0], 'exec'), ns)
sys.argv = argv
text = buf.getvalue()
caplink, split_cells = ns['caplink'], ns['split_cells']

# --- 1. / 2. Evidence: § of the capture (capture-validation §12) -------------------------------------------------
P02_EV = {
    'P02-B33': ['§22.2', '§28.2'],
    'P02-B35': (['§22.5', '§23.3', '§25.9', '§28.1', '§28.4'], 'effect (no lost state) *(inferred)*'),
    'P02-B36': ['§22.5', '§23.5', '§25.9', '§27.8'],
    'P02-B41': ['§28.4'],
    'P02-B42': (['§28.3'], 'that lookups by name then find only one of the two *(inferred)*'),
    'P02-B43': (['§28.6'], 'server data only: no client path'),
}
EV_FIX = {
    'P02-B44': lambda: 'code (found in the batch-5 review of ' + caplink(['§26.3']) + ', not captured: the branch cannot run)',
}

# --- 3. marks (README §5.9 rows "added by X08") ----------------------------------------------------------------
MARKS = {
    'P02-B33': ('Extended', 'P02 capture-validation §28.2: every further `0x1001` of the same WM session gets `0x1002 {0x145}` without the tutorial round trip, from the map lookup of `fc_NC_CHAR_LOGIN_REQ` @ FUN_00422be0'),
}

# --- 4. cross notes ---------------------------------------------------------------------------------------------
NOTES = {
    'P02-B41': 'Z11-B6 (the cross-zone branch of the same `zrpb_Request`)',
    'Z11-B6': 'P02-B41 (the same-zone branch of the same `zrpb_Request`: the notice loses the name)',
    'P02-B43': 'W05-B6 (the WM\'s `CDataReader::Read` checks over the buffer size), Z24-B17 (an unchecked `CDataReader::Read` result)',
}

out, changed = [], collections.Counter()
for line in text.split('\n'):
    m = re.match(r'^\| ([A-Z]\d{2}-B\d+[a-z]?) \|', line)
    if not m or m.group(1) not in set(P02_EV) | set(EV_FIX) | set(MARKS) | set(NOTES):
        out.append(line); continue
    i = m.group(1)
    c = split_cells(line.strip()[1:-1])          # ID, handler, beh, eff, intent, ev, owner
    if len(c) != 7:
        c = [x.strip() for x in line.strip()[1:-1].split(' | ')]
    if len(c) != 7:
        print('BAD', i, len(c), file=sys.stderr); out.append(line); continue
    if i in P02_EV:
        v = P02_EV[i]
        secs, extra = (v if isinstance(v, tuple) else (v, ''))
        c[5] = f'*(captured)* ({caplink(secs)})' + (', ' + extra if extra else '')
        changed['p02-evidence'] += 1
    if i in EV_FIX:
        c[5] = EV_FIX[i]()
        changed['ev-fix'] += 1
    if i in MARKS:
        mk, note = MARKS[i]
        c[2] = f"**{mk}** ({note}; [§5.9](#59-bug-register-entries-a-later-item-changed)): " + c[2]
        changed['mark'] += 1
    if i in NOTES:
        c[1] = c[1] + '; linked: ' + NOTES[i]
        changed['note'] += 1
    out.append('| ' + ' | '.join(c) + ' |')
text = '\n'.join(out)

for i in list(P02_EV) + list(EV_FIX) + list(MARKS) + list(NOTES):
    if not re.search(r'^\| ' + re.escape(i) + r' \|', text, re.M):
        print('MISSING', i, file=sys.stderr)
print('x08 changes', dict(changed), file=sys.stderr)

if MODE == 'md':
    print(text)
elif MODE == 'write':
    doc = open(README, encoding='utf-8').read()
    m = re.search(r'<!-- register:begin [^\n]*-->\n', doc)
    a = '<!-- register:begin (generated by docs/plan/status/X08-register.py, which runs X06-register.py, X04-register.py, X03-register.py and X01-register.py) -->\n'
    j = doc.index('<!-- register:end -->')
    open(README, 'w', encoding='utf-8').write(doc[:m.start()] + a + text.rstrip('\n') + '\n\n' + doc[j:])
