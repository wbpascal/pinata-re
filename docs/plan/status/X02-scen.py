#!/usr/bin/env python3
"""X02 part 8: which medium / low sections each capture scenario of docs/plan/capture-scenarios.md reaches.

A scenario is described by the opcodes it should put on the wire (whole departments, opcode ranges, single
opcodes). A section counts as reached when it is rated medium or low by X02-rate.py and names at least one of
those opcodes that no capture holds yet. That is a reach count, not a proof: the scenario's prediction says
what must be seen.

    python3 -I docs/plan/status/X02-scen.py order      # table for capture-scenarios.md §2
    python3 -I docs/plan/status/X02-scen.py cover      # table for capture-scenarios.md §7
    python3 -I docs/plan/status/X02-scen.py left <ID>  # uncaptured opcodes of <ID> that no scenario names
    python3 -I docs/plan/status/X02-scen.py write      # replace both tables in capture-scenarios.md
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..', '..'))
OUT = os.path.join(ROOT, 'docs', 'plan', 'capture-scenarios.md')


def D(*depts):
    return [(d << 10, (d << 10) | 0x3ff) for d in depts]


def R(lo, hi=None):
    return [(lo, hi if hi is not None else lo)]


def O(*ops):
    return [(o, o) for o in ops]


# number: (title, minutes of user time, needs, opcode ranges)
SCEN = {
    14: ('Second client in sight', 5, '2 clients',
         D(7) + R(0x2003, 0x2006) + O(0x2009) + R(0x200c, 0x200f) + R(0x201e, 0x2025) + R(0x2074, 0x2076)
         + O(0x0817, 0x0818)),
    15: ('Party across two zones', 8, '2 clients',
         D(14) + R(0x2014, 0x2016) + O(0x1818)),
    16: ('Raid', 6, '2 clients (3 better)', D(44)),
    17: ('Friends and character titles', 4, '2 clients', D(21, 24) + R(0x34bf, 0x34c0)),
    18: ('Guild life cycle and guild storage', 12, '2 clients, GM',
         D(29) + R(0x3026, 0x3027) + R(0x3471, 0x3475) + R(0x3490, 0x3495)),
    19: ('Guild academy', 6, '2 clients, GM',
         D(38) + R(0x302f, 0x3032) + R(0x3482, 0x3488) + O(0x1096)),
    20: ('Trade and booth', 10, '2 clients',
         D(19, 26) + O(0x200b) + R(0x343b, 0x343d) + R(0x3453, 0x3456)),
    21: ('Items II: drop, split, storage, use, shop', 10, 'GM',
         D(20, 15) + O(0x3001, 0x3007, 0x3008, 0x300d, 0x300e, 0x3010, 0x3013, 0x3019, 0x301b)
         + R(0x301c, 0x301f) + R(0x3028, 0x302b) + R(0x3039, 0x303a) + R(0x3048, 0x304b) + R(0x3057, 0x305d)
         + R(0x3067, 0x306a) + R(0x340c, 0x3437) + R(0x343e, 0x3445) + R(0x344b, 0x3452) + R(0x3459, 0x345a)
         + R(0x345f, 0x3462) + R(0x346a, 0x346e) + R(0x3476, 0x3477) + R(0x347f, 0x3481) + R(0x349e, 0x34ab)
         + R(0x34b0, 0x34b2) + R(0x34b7, 0x34bc) + R(0x34c9, 0x34cc) + O(0x1130)),
    22: ('Upgrade, gems, random options, endurance', 8, 'GM',
         R(0x3017, 0x3018) + R(0x3035, 0x3038) + R(0x3040, 0x3046) + R(0x3051, 0x3054) + R(0x3061, 0x3066)
         + R(0x306b, 0x3070) + R(0x3447, 0x3448) + R(0x348d, 0x348f) + R(0x3496, 0x349d) + R(0x34ac, 0x34af)
         + R(0x34b3, 0x34b4) + R(0x34c1, 0x34c8) + R(0x34cd, 0x34d4)),
    23: ('Quest: accept, kill, finish, give up; class change', 8, 'GM',
         D(17) + R(0x100a, 0x100b) + O(0x1021) + R(0x10cc, 0x10cd) + R(0x10d5, 0x10d6) + R(0x3404, 0x3409)
         + R(0x345b, 0x345d) + R(0x4005, 0x4006) + R(0x305e, 0x3060) + R(0x34bd, 0x34be) + R(0x1056, 0x105a)),
    24: ('Skills, abstates, stat points', 10, 'GM, 2 clients for revive',
         D(18) + R(0x240e, 0x240f) + R(0x2427, 0x242a) + O(0x2434, 0x2438, 0x243c) + R(0x243e, 0x2445)
         + O(0x244d) + R(0x244f, 0x2457) + R(0x245a, 0x245f) + R(0x105c, 0x1067) + R(0x10d1, 0x10d2)
         + O(0x103c, 0x1035, 0x10df) + R(0x4007, 0x400a) + R(0x100c, 0x100e) + R(0x1023, 0x1025)),
    25: ('Pet', 8, 'GM',
         D(53) + O(0x1014, 0x1011, 0x4033)),
    26: ('Mounts and minimon', 5, 'GM',
         D(51) + R(0x203f, 0x2046) + R(0x1124, 0x112d) + O(0x3050)),
    27: ('Wing stone and silver wing', 5, 'GM',
         R(0x1814, 0x1817) + R(0x181c, 0x1820) + O(0x1809, 0x301a, 0x304e, 0x304f, 0x10b8, 0x10b9, 0x3029)),
    28: ('Mini-house', 10, '2 clients, GM',
         D(35) + R(0x2027, 0x202c) + R(0x3033, 0x3034) + R(0x3467, 0x3469) + R(0x347d, 0x347e)
         + R(0x3489, 0x348c) + O(0x100f) + R(0x1076, 0x1077)),
    29: ('Wedding', 15, '2 clients, GM',
         R(0x1082, 0x1095) + R(0x10aa, 0x10ab) + O(0x10b2) + R(0x204e, 0x205e) + R(0x065b, 0x065f)),
    30: ('Kingdom quest', 20, '2 clients, GM, SHN / schedule setup',
         D(22, 27) + R(0x1828, 0x1829) + R(0x1812, 0x1813) + R(0x2072, 0x2073) + R(0x2077, 0x207d)
         + R(0x2082, 0x2083) + O(0x101a) + R(0x0441, 0x0442) + O(0x1050)),
    31: ('Instance dungeon', 10, '2 clients (party), GM',
         D(41) + O(0x0810, 0x10b1, 0x182c)),
    32: ('GM command session', 12, 'GM, 2 clients',
         R(0x1068, 0x106c) + R(0x10ad, 0x10ae) + O(0x10c6) + R(0x1810, 0x1811) + O(0x0811, 0x083d, 0x2010)
         + R(0x3401, 0x3403) + D(25) + O(0x240d) + R(0x2458, 0x2459) + R(0x347a, 0x347c)),
    33: ('Prison', 8, 'GM, 2 clients', D(31)),
    34: ('Premium inventory, charged buffs', 5, 'DB setup',
         D(36) + R(0x3022, 0x3023) + R(0x302c, 0x302e) + R(0x3055, 0x3056) + R(0x3463, 0x3466)
         + R(0x34b5, 0x34b6) + O(0x101b, 0x1032) + R(0x112e, 0x112f) + R(0x086e, 0x0871)),
    35: ('Dice table, gamble house, card collection', 10, 'GM, mini-house',
         D(43, 47, 49) + R(0x303b, 0x303f) + R(0x10dc, 0x10dd) + R(0x10e2, 0x10e9)),
    36: ('Block list, reports, options, megaphone', 5, '2 clients',
         D(42, 32, 28) + R(0x0844, 0x0848) + R(0x085f, 0x0869) + R(0x204b, 0x204c) + R(0x10ca, 0x10cb)
         + O(0x10d3, 0x7037)),
    37: ('Login side: idle heartbeat, refusals, character delete', 6, 'DB / config setup',
         R(0x0c06, 0x0c08) + O(0x0c15) + R(0x0c23, 0x0c2b) + O(0x0c33) + R(0x0c35, 0x0c66) + D(5, 45, 40)
         + R(0x0801, 0x080d) + R(0x081b, 0x081e) + O(0x1002, 0x1006) + R(0x1008, 0x101a) + R(0x101e, 0x1032)
         + R(0x082a, 0x0830) + O(0x1802, 0x1804, 0x180f, 0x182a)),
    38: ('Session loss, kicks, back to character select', 10, 'GM, 2 clients, process kill',
         O(0x0c11, 0x0c19, 0x0c1a, 0x0c31, 0x0c32, 0x1037) + R(0x1071, 0x1072) + R(0x106b, 0x106c)
         + R(0x1078, 0x107f) + O(0x081f, 0x0843)),
    39: ('Combat extras: death penalty, PK, revive item, knock-back', 8, '2 clients, GM',
         O(0x2411, 0x242e, 0x2449, 0x244b, 0x104f, 0x1102, 0x1103, 0x10af, 0x10b0) + R(0x2049, 0x204a)
         + O(0x204d) + R(0x2069, 0x206a) + R(0x3039, 0x303a) + D(23) + R(0x0791, 0x0791)
         + O(0x2434, 0x2438, 0x2444, 0x2445, 0x244a, 0x0429, 0x1073, 0x3832)),
    40: ('Gathering, production, item emotes, way-finding gate, tutorial, attendance', 8, 'GM',
         R(0x202d, 0x203c) + R(0x2067, 0x2068) + R(0x206f, 0x2071) + R(0x3457, 0x3458) + R(0x1110, 0x111d)
         + R(0x10ed, 0x10f6) + R(0x086a, 0x086d) + O(0x10bc, 0x10c1, 0x10cf, 0x10d0, 0x10d8) + O(0x482c)),
    41: ('Test client: crafted client packets', 15, 'test client',
         O(0x7001, 0x7002, 0x980d, 0x3802, 0x0812, 0x300d, 0x304e, 0x5401, 0x581a, 0x1814, 0x0840, 0x0841,
           0x080f, 0x0819, 0x081a, 0x0827, 0x0836) + R(0x0813, 0x0816)
         # T15-T22 (X05)
         + O(0x0804, 0x0805, 0x3028, 0x3007, 0x3c07, 0x300e, 0x5001, 0x5005, 0x5006, 0x5007, 0x2022, 0x2023,
             0x101e, 0x1804, 0x104c, 0x2434, 0x2440, 0x0c66, 0x0c15)
         # T23-T25 (X07)
         + R(0x4811, 0x4814) + O(0x0c1a, 0x0c17, 0x105c, 0x105f, 0x1061, 0x1062, 0x1067, 0x10d1, 0x10d2)
         + R(0x243e, 0x243f)
         # T26-T28 (X09)
         + R(0x3059, 0x305a) + R(0x2020, 0x2021) + R(0x300b, 0x300c) + R(0x3428, 0x3429) + O(0x3001)),
    42: ('Races: drop menu, two money pick-ups, link with a dead WM session', 10, '2 clients',
         R(0x3416, 0x341b) + R(0x3438, 0x343a) + O(0x180d, 0x180e)),
    43: ('OPTool listener (test tool)', 15, 'test tool',
         D(10, 52) + R(0x0828, 0x0828) + R(0x0834, 0x0835)),
    44: ('Holy promise (mentor and pupil)', 8, '2 clients, GM', D(37)),
    # 45-50: added by X05 after capture batch 3 (what s14 / s21 / s37 and batch 2 left open)
    45: ('Second client in sight II', 8, '2 clients',
         R(0x2017, 0x2018) + R(0x201f, 0x2023) + O(0x200e, 0x2438, 0x2444, 0x2445, 0x1805)),
    46: ('Items III: no DB change', 12, 'GM',
         R(0x300b, 0x300c) + R(0x3431, 0x3432) + R(0x342b, 0x342c) + R(0x3059, 0x305a) + O(0x305d, 0x3004, 0x5001, 0x5005)
         + R(0x34b9, 0x34bc) + O(0x4014)),
    47: ('Items IV: the zone and the DB disagree', 25, 'GM, DB / table setup per step, 2 clients for step 6',
         R(0x3422, 0x3427) + O(0x3005, 0x3004, 0x305a, 0x340c, 0x34a0, 0x34a1, 0x3016, 0x300c) + R(0x3441, 0x3443)
         + R(0x34b9, 0x34bc) + R(0x3431, 0x3433) + R(0x342b, 0x342d) + R(0x3459, 0x345a)),
    48: ('WM stop and start with its log', 10, 'server PC only',
         O(0x9804, 0x0821, 0x0802)),
    49: ('Items V: refusals by the Character server', 25, 'DB setup per step, a second client or drops',
         R(0x340a, 0x340f) + R(0x3410, 0x3415) + R(0x3416, 0x3418) + R(0x341c, 0x3421) + R(0x3428, 0x342a)
         + O(0x3004, 0x300c, 0x3011, 0x3013, 0x3008, 0x300a) + R(0x3444, 0x3445) + R(0x3c07, 0x3c08)
         + R(0x34b9, 0x34ba) + O(0x3059, 0x305a)),
    50: ('Timing with one clock and without delayed ACKs', 15, 'capture on the server PC, a registry change',
         O(0x7004, 0x700c, 0x700d, 0x7c06, 0x7c07, 0x1003, 0x0849, 0x080e)),
    # 51-52: added by X07 after capture batch 4 (what s24 / s37b / s38 left open)
    51: ('Skills II: what `s24` left open', 80, 'GM, 2 clients for steps 2 (heals) and 4, DB setup S21 for steps 6–7',
         R(0x4801, 0x4804) + R(0x4811, 0x4814) + O(0x0c1a, 0x0c17) + R(0x245c, 0x245d) + O(0x2428, 0x2429, 0x1c18)
         + R(0x4009, 0x400a) + O(0x103d) + R(0x9005, 0x900f)),
    52: ('Character select and session II: what `s37b` / `s38` left open', 15,
         'GM, 2 clients, DB setup S20, a zone restart',
         R(0x1001, 0x1004) + R(0x1110, 0x1113) + R(0x1410, 0x1412) + O(0x0c1a, 0x0c17, 0x0c18, 0x2011, 0x1068)
         + O(0x1801, 0x1804)),
    # 53-54: added by X09 after capture batch 5 (what s45 / s46 / s52 left open)
    53: ('Items VI: what `s46` left open: a stack that may not move back, a stack\'s buy-back, a second soul-stone '
         'purchase, and the logout', 15, 'GM, DB setup S22',
         R(0x300b, 0x300c) + R(0x3428, 0x3429) + O(0x3001, 0x3c08, 0x3444, 0x1071, 0x0c18, 0x0c31, 0x0410)
         + R(0x4001, 0x4035)
         # steps 5-6 (X09 review): 0x366C with a stack, 0x5005 {0x741} with a second purchase in flight
         + O(0x3059, 0x305a, 0x305c, 0x305d, 0x3422, 0x3423, 0x5001, 0x5003, 0x5005, 0x3441, 0x3442)),
    54: ('Shared names, the emote keys and a refused rename: what `s45` / `s52` left open', 15,
         'GM, 3 clients, DB setups S23, S24, S20',
         R(0x2020, 0x2023) + O(0x1c06) + R(0x200c, 0x200f) + O(0x3802, 0x3803, 0x3805, 0x3807, 0x0c1a, 0x0c17,
                                                               0x1068, 0x2011) + R(0x140f, 0x1412)),
}

# Recorded scenarios (capture batch): their row counts what the opcode set still leaves uncaptured.
RECORDED = {14: 'batch 3', 21: 'batch 3', 37: 'batches 3 and 4', 24: 'batch 4', 38: 'batch 4', 45: 'batch 5',
            46: 'batch 5', 52: 'batch 5'}

# Not a scenario of its own: records that every scenario produces on the server links (README §3.13, §3.15).
LINKS = D(1, 50, 16)


def load():
    src = open(os.path.join(HERE, 'X02-rate.py')).read()
    g = {'__name__': 'x02rate', '__file__': os.path.join(HERE, 'X02-rate.py')}
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        exec(compile(src, 'X02-rate.py', 'exec'), g)
        return g['build']()
    finally:
        os.chdir(cwd)


def inset(op, ranges):
    return any(lo <= op <= hi for lo, hi in ranges)


def analyse():
    rows = load()
    reach = {n: [0, set()] for n in SCEN}
    docs = []
    for path, ident, secs in rows:
        st = collections.Counter()
        left = collections.Counter()
        by = collections.Counter()
        for s, sig, rating, why, up in secs:
            if rating not in ('medium', 'low'):
                continue
            st['ml'] += 1
            if not sig['ops']:
                st['noop'] += 1
                continue
            unc = {int(o, 16) for o in sig['ops'] - sig['cap']}
            if not unc:
                st['cap'] += 1
                continue
            hit = False
            for n, (title, mins, needs, ranges) in SCEN.items():
                got = {o for o in unc if inset(o, ranges)}
                if got:
                    reach[n][0] += 1
                    reach[n][1] |= got
                    by[n] += 1
                    hit = True
            if hit:
                st['scen'] += 1
            elif any(inset(o, LINKS) for o in unc):
                st['links'] += 1
            else:
                st['left'] += 1
            for o in unc:
                if not any(inset(o, r) for _, _, _, r in SCEN.values()) and not inset(o, LINKS):
                    left[o] += 1
        docs.append((ident, st, by, left))
    return reach, docs


# Order for the rebuild (decided 2026-11-16: client-facing compatibility only). Rank = cost of a wrong assumption
# for the rebuild, then how early the feature comes, then capture cost. (when, [(scenario, why)]).
PRIORITY = [
    ('before the rebuild starts', [
        (37, 'its refusal steps 3–6 not yet run (S10, S11, X6) finish the login side; `s37b` ran only the character-select refusals'),
        (51, 'the skill paths the client reached only with one learned step: empower wrap, toggle steps, skill-save columns'),
    ]),
    ('early: core gameplay', [
        (53, 'closes what 46 left open: a stack that may not move back (`0x24A`, `0x20A`, `irm_Move`) and the logout saves'),
        (39, 'party / PK death and exp loss are not captured at all; not captured in batch 5 either'),
        (54, 'closes what 45 / 52 left open: the emote pause key, lookups by a shared name, the refused rename'),
        (36, 'cheap, high reach; settles the option-save tail of `0x7037`'),
        (23, 'the quest engine has no capture-confirmed section'),
        (22, 'item attribute changes the client displays directly'),
        (15, 'party is the first social feature; the zone change itself is captured'),
        (17, 'cheap; fills the WM social packets'),
        (20, 'not captured at all; item duplication if wrong'),
    ]),
    ('with its feature', [
        (18, 'largest uncaptured area; log in again afterwards for the guild load blocks'),
        (19, 'same session as 18'),
        (16, 'builds on party'),
        (25, 'log in again afterwards for the pet load blocks'),
        (26, 'small, self-contained'),
        (27, 'small, self-contained'),
        (34, 'needed once charged items are sold'),
        (40, 'several small systems in one run'),
        (32, 'only for the commands the rebuild keeps'),
        (28, 'log in again afterwards for the house load blocks; 35 needs it'),
        (35, 'many uncaptured opcodes, but late content'),
        (31, 'needs party first'),
        (30, 'longest setup; only the WM minute skips are captured'),
        (29, 'late content'),
        (44, 'late content'),
        (33, 'late content, small'),
    ]),
    ('optional', [
        (41, 'how the original reacts to bad input: validation rules, not features'),
        (42, 'original race behaviour; the rebuild designs its own locking'),
        (43, 'only if the original OPTool must work'),
        (49, 'DB faults the rebuild\'s own persistence does not have'),
        (47, 'every step tampers with the DB or tables under an online player'),
    ]),
    ('dropped (original processes only)', [
        (48, 'the WM\'s own stop cause and log'),
        (50, 'timing between the original processes'),
    ]),
    ('recorded', [
        (14, 'continued by 45'),
        (21, 'continued by 46, 47, 49'),
        (24, 'continued by 51 (refusals the client pre-empted: T23, T24, T25 in 41)'),
        (38, 'continued by 52'),
        (46, 'continued by 53 (refusals the client pre-empted: T26 in 41, T18 for the soul stones)'),
        (45, 'continued by 54 (the emote keys; `0x2020 {6}`: T27 in 41)'),
        (52, 'continued by 54 (step 6: the refused rename)'),
    ]),
]


def order_table(reach):
    out = ['| Rank | # | Scenario | When | Needs | Minutes | Sections reached | Opcodes not yet captured | Why at this rank |',
           '|---|---|---|---|---|---|---|---|---|']
    ranked = [n for _, rows in PRIORITY for n, _ in rows]
    assert sorted(ranked) == sorted(SCEN), 'PRIORITY must name every scenario once'
    rank = 0
    for when, rows in PRIORITY:
        for n, why in rows:
            title, mins, needs, _ = SCEN[n]
            if n in RECORDED:
                title += ' *(recorded, %s)*' % RECORDED[n]
            numbered = when not in ('recorded', 'dropped (original processes only)')
            rank += numbered
            out.append('| %s | %d | %s | %s | %s | %d | %d | %d | %s |' % (
                rank if numbered else '–', n, title, when, needs, mins, reach[n][0], len(reach[n][1]), why))
    return '\n'.join(out)


def cover_table(docs):
    out = ['| Document | Medium / low sections | No opcode | Opcodes all captured | Reached by a scenario | Link records only '
           '| Not reached | Scenarios (sections) |',
           '|---|---|---|---|---|---|---|---|']
    tot = collections.Counter()
    for ident, st, by, left in docs:
        if not st['ml']:
            continue
        tot.update(st)
        top = ', '.join('%d (%d)' % (n, c) for n, c in by.most_common(5))
        out.append('| %s | %d | %d | %d | %d | %d | %d | %s |' % (
            ident.replace('K:', 'knowledge '), st['ml'], st['noop'], st['cap'], st['scen'], st['links'],
            st['left'], top))
    out.append('| **Total** | %d | %d | %d | %d | %d | %d | |' % (
        tot['ml'], tot['noop'], tot['cap'], tot['scen'], tot['links'], tot['left']))
    return '\n'.join(out)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'order'
    reach, docs = analyse()
    if cmd == 'order':
        print(order_table(reach))
    elif cmd == 'cover':
        print(cover_table(docs))
    elif cmd == 'left':
        names = {v['op'].lower(): v.get('name') or '?' for v in json.load(
            open(os.path.join(ROOT, 'docs', 'protocol', 'opcodes.json')))}
        want = sys.argv[2:] or None
        agg = collections.Counter()
        for ident, st, by, left in docs:
            if want is None or ident in want:
                agg.update(left)
        for o, c in sorted(agg.items()):
            print('0x%04x %-44s %d' % (o, names.get('0x%04x' % o, '?'), c))
    elif cmd == 'write':
        text = open(OUT).read()
        for tag, table in (('ORDER', order_table(reach)), ('COVER', cover_table(docs))):
            pat = re.compile(r'(<!-- %s:begin -->\n).*?(<!-- %s:end -->)' % (tag, tag), re.S)
            if not pat.search(text):
                sys.exit('marker %s missing in %s' % (tag, OUT))
            text = pat.sub(lambda m: m.group(1) + table + '\n' + m.group(2), text)
        open(OUT, 'w').write(text)
        print('tables written')


if __name__ == '__main__':
    main()
