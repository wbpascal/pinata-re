# Hand ratings of X02 (read by X02-rate.py; plain Python, executed in its namespace).
# OVERRIDE[(item, § number or heading text)] = (rating, reason, what would raise it)
# CAPS: (item, regex on the § number, highest rating allowed, reason, what would raise it)
# Part 2: Login, WM, shared library, DB servers. Part 3: zone documents and the knowledge files (item key 'K:<ID>').

OVERRIDE.update({
    # capture-validation §2.1: 1 365 packets (batch 1) parsed with no resync; the long form appears exactly for
    # bodies >= 256 bytes; batch 2 decodes all seven captures with 0 issues, links included (§7.1).
    ('S02', '1.7'): ('high', 'receive framing: every captured stream (client and server links) parses with no resync '
                     '(capture-validation §2.1, §7.1); buffer growth and error paths are code only', ''),
    ('S02', '1.8'): ('high', 'frame builder: short / long header of every captured Login and WM send matches '
                     '(capture-validation §2.1); pool exhaustion paths are code only', ''),
    # capture-validation §2.4: Login sent no heartbeat in any capture (the client polls 0x0C1B every 10 s).
    ('L01', '1.6'): ('medium', 'the 30 s / close rule is read in code and seen on the WM and the zone only; the 2016 client '
                     'holds no Login connection on the login screen and polls 0x0C1B every 10 s on the world list, so the '
                     'Login copy cannot fire with it (capture-validation §2.4, §16.2)', 'test-client case T15 '
                     '(capture-scenarios §3.41): a silent Login connection for 60 s'),
})

CAPS += [
    # Procedures without source in any backup: the capture of the caller's packet does not show the body.
    ('D06', r'^[2-7](\.|$)', 'medium', 'procedure body inferred from the binds and the caller (no source in a backup); '
     'a captured request shows the call, not what the database does', 'DB setup + capture of the answer (part 9), or the '
     'original procedure source'),
]

# ---- part 3: zone documents ---------------------------------------------------------------------------------
# Baseline limit 1 (confidence.md §2.2): a section got "high" from opcodes it only mentions. Capture set: login,
# idle, walk / portals, shop (buy, equip, storage, sell, soulstones), combat (swing, Bash [01], pick-up, death,
# revive, &levelup, &linkto, Wooden Horse). No silver wing, pet, party, guild, KQ play, scripted map, second player.
OVERRIDE.update({
    ('Z02', '11'): ('medium', 'the captured opcodes are only mentioned here (0x2401 / 0x2402 targeting); the subject of the section (0x2070 / 0x2071 auto way-finding gate use) is in no capture', 'capture 0x2070, 0x2071'),
    ('Z04', '5.2'): ('medium', 'the captured opcodes are only mentioned here (0x3011 / 0x3410 of the normal equip, §5.1); the 2016 client equipped both rings of batch 3 with 0x300F (capture-validation §19.7), so the subject of the section (0x3010 ring equip) is in no capture', 'test client: send 0x3010'),
    ('Z04', '5.3'): ('medium', 'the captured opcodes are only mentioned here (0x3011 / 0x3410 of the normal equip, §5.1); the subject of the section (0x3050 mini-monster equip) is in no capture', 'capture 0x3050'),
    ('Z04', '8.2'): ('medium', 'the captured opcodes are only mentioned here (0x1047 / 0x104B / 0x104C of the login); the subject of the section (0x3022 / 0x3023 / 0x3465 premium withdraw) is in no capture', 'capture 0x3022, 0x3023 (DB setup: a charged item row, part 9)'),
    ('Z05', '2.5'): ('medium', 'the captured opcodes are only mentioned here (the shared buy answer 0x3004); the subject of the section (0x34A1 capsule buy) is in no capture', 'capture 0x34A1'),
    ('Z05', '2.6'): ('medium', 'the captured opcodes are only mentioned here (the shared buy answer 0x3004); the subject of the section (0x34B2 item-money buy) is in no capture', 'capture 0x34B2'),
    ('Z07', '6.2'): ('medium', 'the captured opcodes are only mentioned here (WM character-list opcodes); the subject of the section (0x8C01 mini-house activation) is in no capture', 'capture 0x8C01'),
    ('Z09', '5.9'): ('medium', 'the captured opcodes are only mentioned here (0x244A, 0x3004); the subject of the section (NPC object internals and the scheduled NPCs of 0x086A) is in no capture', 'capture 0x086A (event NPC schedule)'),
    ('Z09', '13.3'): ('medium', 'the captured opcodes are only mentioned here (0x1805 object removal); the subject of the section (servants / summoned mobs) is in no capture', 'capture a summoning mob (0x243C)'),
    ('Z09', '14.3'): ('medium', 'the captured opcodes are only mentioned here (0x1803, 0x200A); the subject of the section (Lua object and map events) is in no capture', 'a scripted map (KQ or instance) in a capture'),
    ('Z09', '16.5'): ('medium', 'the captured opcodes are only mentioned here (0x2011 / 0x2013 / 0x201C); the subject of the section (script actions of an NPC role) is in no capture', 'a scripted NPC in a capture'),
    ('Z09', '17.1'): ('medium', 'the captured opcodes are only mentioned here (0x2018 / 0x201A mob moves); the subject of the section (Lua move functions) is in no capture', 'a scripted map in a capture'),
    ('Z09', '24.2'): ('medium', 'the captured opcodes are only mentioned here (0x3449 / 0x344A of the ride item save); the subject of the section (Lua `itemcreate` / `itemerase`) is in no capture', 'a script that gives an item, in a capture'),
    ('Z09', '25.2'): ('medium', 'the captured opcodes are only mentioned here (0x2018 / 0x201A / 0x203E); the subject of the section (Lua mob settings) is in no capture', 'a scripted map in a capture'),
    ('Z09', '27.6'): ('medium', 'the captured opcodes are only mentioned here (0x0821, 0x3016); the subject of the section (boss-field tables) is in no capture', 'a boss field in a capture'),
    ('Z10', '5.4'): ('medium', 'the captured opcodes are only mentioned here (0x203E speed); the subject of the section (the 0x0830 speed-hack check) is in no capture', 'capture 0x0830 (custom client or a lagging one)'),
    ('Z11', '3.5'): ('medium', 'the captured opcodes are only mentioned here (0x1030 / 0x2002 of a normal chat); the subject of the section (the GM colour request 0x083D) is in no capture', 'capture 0x083D (GM command, part 8)'),
    ('Z11', '8.5'): ('medium', 'the captured opcodes are only mentioned here (0x2452 / 0x4821); the subject of the section (`&HP`, `&SP`, `&gmtestmode`) is in no capture', 'capture the commands (part 8)'),
    ('Z13', '6.4'): ('medium', 'the captured opcodes are only mentioned here (0x1805 / 0x244A); the subject of the section (the pet routine) is in no capture', 'capture with a pet summoned'),
    ('Z17', '4.5'): ('medium', 'the captured opcodes are only mentioned here (login and item-move packets); the subject of the section (the action-item box (premium emotes)) is in no capture', 'capture 0x2067, 0x3428 ff.'),
    ('Z23', '2.4'): ('medium', 'captured: the automatic switch-off of the toggle by unequip, low HP and map change (capture-validation §25.4, §11 row "Toggle skill"), and the capture extends the section (each removed state is broadcast twice, a switch-off cast costs HPRate HP; P02-B38, §13): a captured section in which a class applies', 'X06 folds P02-B38 into the section'),
    ('Z25', '6.8'): ('medium', 'the captured opcodes are only mentioned here (0x2452 / 0x2457 of Bash [01]); the subject of the section (chain blasts) is in no capture', 'capture a chain skill (0x245E)'),
    ('Z26', '2'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '3'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '3.1'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '3.2'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '4'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '4.1'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '4.2'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '4.4'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '5.2'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '5.4'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z26', '6'): ('medium', 'silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D)', 'scenario: save a location and fly with a silver wing (part 8)'),
    ('Z15', '1.1'): ('medium', 'the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step', 'capture: accept, progress and finish one quest'),
    ('Z15', '4'): ('medium', 'the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step', 'capture: accept, progress and finish one quest'),
    ('Z15', '4.1'): ('medium', 'the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step', 'capture: accept, progress and finish one quest'),
    ('Z15', '4.5'): ('medium', 'the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step', 'capture: accept, progress and finish one quest'),
    ('Z09', '10.1'): ('medium', 'one client citation (`MobNoFadeInTab`) in a list of server data files', 'second reading'),
    ('Z13', '5.8'): ('medium', 'captured only with no pet (0x4033 / 0xD412 `bDoResummon 0`, ids -1): the re-summon branch never ran', 'capture a map link with a pet out'),
    ('Z17', '3.4.1'): ('medium', 'capture credit comes from the shared 0x3016 / 0x482C; no capture is known to contain an item with an action set', 'capture: equip an item with an `ItemAction` row and kill a mob'),
    ('Z18', '3.8'): ('medium', 'table of 22 helpers; the captures touch the attack-timing rows (0x242B, 0x2440, moves) and, since batch 4, skill teach and empower (capture-validation §24.2, §24.3), not polymorph and the rest', 'per row: Z03 §3 for the timing, scenarios for the rest'),
})

# ---- part 3: knowledge files -----------------------------------------------------------------------------------
OVERRIDE.update({
    ('K:P02', 'Corrections'): ('high', 'every row is a capture finding with its packet count and the code place', ''),
    ('K:P02', 'Facts'): ('high', 'capture facts (orders, timings, field values) with the code place; *(inferred)* marks the 8 deductions', ''),
    ('K:C01', 'AccountFrameWork'): ('high', 'dispatch table of the login scene: 11 of 12 opcodes captured and handled as listed', ''),
    ('K:C01', 'LoginWorldNetFrameWork'): ('high', 'dispatch table: 5 of 6 opcodes captured', ''),
    ('K:C01', 'ZoneLoginNetFrameWork'): ('high', 'dispatch table: 18 of 24 opcodes captured (the character-load burst)', ''),
    ('K:C01', 'LinkFrameWork'): ('high', 'dispatch table: 15 of 22 opcodes captured (map links)', ''),
})

# ---- part 4: after the re-check of confidence.md §3.2 ----------------------------------------------------------
OVERRIDE.update({
    ('K:Z01', '3'): ('high', 're-checked (§3.2.2 H1–H3): every range bound re-read in sohu_HandleSplit FUN_00633650, all 13 '
                     'object sizes are the class sizes of the 2016 Zone.pdb', ''),
    ('K:Z01', '4'): ('medium', 're-checked (§3.2.3): all 36 offsets are 2016 PDB members; 2 meanings corrected (+0x29638 = '
                     'character title, +0x2a800 = sp_isPossibleNewConnect, cleared by 0x0806 / 0x1801 only), 1 refined '
                     '(+0x1c00 = total, not base); read with docs/knowledge/X02.md §0', 'capture of a field per member '
                     '(0x1038 login burst for basedata)'),
    ('K:Z01', '6'): ('medium', 're-checked (§3.2.1): lookup pattern confirmed with counts over 307 handlers; the "PDB offset '
                     '= 2016 − 6" rule corrected (211 structs carry the header as a member) and "starts with" narrowed '
                     '(R2–R4, R6); read with docs/knowledge/X02.md §0', 'a captured DB→zone answer per header form'),
    ('K:Z03', '2'): ('medium', 're-checked (§3.2.4): every offset is a 2016 PDB member; names of 4 smo_Flag bits, the '
                     'EngageArgument fields and the abstate element +0x70 corrected, stat matrix and battle statistics '
                     'superseded by Z12 §1.1 / Z16 §3.1; read with docs/knowledge/X02.md §0', 'combat capture with an '
                     'abstate set and removed by walking (aeo_MiscData reset condition)'),
})

# ---- X05 part 4: after capture batch 3 (s14, s21, s21b-d, s37) -----------------------------------------------
# Lifted: Z02 §5.1 (0x1C01 captured 18 x in s14, capture-validation §18.2) and Z05 §6.1 (0x343E / 0x343F -> 0x3440
# captured in s21, §19.6): both are high by the baseline now. Reworded above: L01 §1.6, Z04 §5.2.
# New highs of the re-run checked against what batch 3 contains (second client in sight, whisper / shout / emote /
# jump, GM items, split / merge, drop / pick, destroy, potions, rings, storage money, sell / buy back, soul stones,
# login refusals, character create / delete, WM and zone stop / start); the incidental ones are medium by hand:
OVERRIDE.update({
    ('W03', '1.1'): ('medium', 'captured only as the start-up load of a world without a guild (0x7457 `NumOfGuild 0`, 0x74BD; capture-validation §17.3): no guild object was ever built', 'capture-scenarios 22 / 23 (guild with members)'),
    ('W04', '2.5'): ('medium', 'the captured opcodes are only mentioned here (0x200D of a normal whisper, §2.1); the subject of the section (the gold-spammer alert from 0x085F) is in no capture', 'capture 0x085F (report a spammer with a GM online)'),
    ('Z02', '9.2'): ('medium', 'the captured opcodes are only mentioned here (0x0720, 0x300C); the subject of the section (0x204B / 0x204C roar) is in no capture', 'capture 0x204B, 0x204C (use a megaphone item)'),
    ('Z04', '7.2'): ('medium', 'the storage open 0x3444 is captured (capture-validation §7.6.1), but the 2016 client never sent 0x3028 in batch 2 or 3: all four pages come with the open (§20.1)', 'test-client case T16 (capture-scenarios §3.41)'),
    ('Z05', '2.4'): ('medium', 'captured (two purchases, capture-validation §20.3), and the 0x3441 / 0x3442 layouts were corrected by that capture (§20.5: `{ref, lock}`); 0x3443 / 0x5005 are in no capture: in batch 5 the 2016 client refused both soul-stone cases itself (0 cen, at the limit; no 0x5001 sent, capture-validation §26.5)', 'test-client case T18 (0x5005); capture-scenarios 47 step 3 with S17 (0x3443, the DB-side refusal)'),
    ('Z09', '8.7'): ('medium', 'the captured opcodes are only mentioned here (0x2002 / 0x201F of player chat and shout); the subject of the section (a mob shout or scripted mob chat) is in no capture', 'a shouting mob in a capture'),
    ('Z09', '9.2'): ('medium', 'the captured opcodes are only mentioned here (0x2013, 0x2021, 0x2025 of a free player); the subject of the section (a blocked stop, emote or jump) is in no capture', 'capture a jump / emote on a blocked cell'),
    ('Z09', '16.6'): ('medium', 'the captured opcodes are only mentioned here (0x2448 / 0x2449 swings); the subject of the section (damage absorption) is in no capture', 'capture a swing against an absorb abstate'),
    ('Z09', '19.3'): ('medium', 'the captured opcodes are only mentioned here (0x2011, 0x201F, 0x2020 / 0x2021 from players); the subject of the section (the Lua notice, system-message, NPC chat and shout functions) is in no capture', 'a scripted map in a capture'),
    ('Z09', '25.3'): ('medium', 'the captured opcodes are only mentioned here (0x2002 / 0x201F of player chat and shout); the subject of the section (`npcchat`, `npcshout`, `maplight`, fog) is in no capture', 'a scripted map in a capture'),
    ('Z09', '28.8'): ('medium', 'the captured opcodes are only mentioned here (0x1C06 / 0x1C08 appear packets); the subject of the section (the vtable-only methods listed) is in no capture', 'second reading'),
    ('Z13', '6.5'): ('medium', 'the captured opcodes are only mentioned here (0x1805, 0x1C01); the subject of the section (pet brief info 0x1C1C / 0x1C1D) is in no capture', 'capture with a pet summoned'),
    ('Z16', '2.6'): ('medium', 'the captured opcodes are only mentioned here (0x3459 / 0x345A of the destroy and the expiry in batch 3); the subject of the section (KQ items) is in no capture', 'a KQ played in a capture (scenario 31)'),
    ('Z17', '3.4.2'): ('medium', 'capture credit comes from the swings 0x2448 / 0x2449; no capture is known to contain an item with an action set', 'capture: equip an item with an `ItemAction` row and kill a mob'),
    ('Z18', '4.9'): ('medium', 'the captured opcodes are only mentioned here (0x3016 / 0x301A of a potion); the subject of the section (item boxes, locks, lot sums, bracelet upgrade rows) is in no capture', 'per row: the scenario of its feature'),
    ('Z18', '6.3'): ('medium', 'the captured opcodes are only mentioned here (0x6004 / 0x6005 of the level-20 title marks, §6.2); the subject of the section (Lua `cAddCharacterTitle`) is in no capture', 'a script that gives a title, in a capture'),
    ('Z18', '6.6'): ('medium', 'the captured opcodes are only mentioned here (0x1C05, 0x200A, 0x200C); the subject of the section (weapon titles, group titles, card table lookups) is in no capture', 'capture 0x5C03, 0x5C0D'),
    ('Z21', '3.1'): ('medium', 'the captured opcodes are only mentioned here (0x2408, 0x5004); the subject of the section (the set-item structures) is in no capture', 'capture: wear a full set'),
    ('Z26', '1.4'): ('medium', 'silver wing used in no capture: 0x301A is the potion use of batch 3', 'scenario: save a location and fly with a silver wing'),
    ('Z27', '7.2'): ('medium', 'the captured opcodes are only mentioned here (0x3459 / 0x345A); the subject of the section (the index consumers listed) is in no capture', 'second reading'),
    ('Z30', '8'): ('medium', 'captured: only the guild list at zone start (0x7446 / 0x7447, no guild) and 0x1070; the other opcodes are mentions (0x300D); no party, raid or guild in a capture', 'capture-scenarios 15–17 (party / raid), 22 (guild)'),
    ('Z31', '9.6'): ('medium', '0x987A / 0x987B are captured only as the hourly push to a world without a guild; the storage elements are in no capture', 'capture-scenarios 22 / 23 (guild, academy)'),
    ('Z31', '10.2'): ('medium', 'the captured opcodes are only mentioned here (0x2008, 0x200C); the subject of the section (the `PacketContainer` send buffer) is in no capture', 'none on the wire (flush point: capture-scenarios §5 leftovers)'),
    ('Z32', '5.4'): ('medium', 'the captured opcodes are only mentioned here (0x3015 / 0x3016 of the ride item); the subject of the section (coin items 0xBC19 / 0xBC1A) is in no capture', 'capture: use a coin item'),
    ('S02', '1.1'): ('medium', 'the captured opcodes are only mentioned here (0x2008, 0x200C); the subject of the section (the library object model) is in no capture', 'none on the wire'),
})

# The generator now also counts the "Opcodes" tables of capture-validation as capture evidence (102 captured opcodes had
# no evidence entry in annotations/P02.json, 73 of them from batches 1-2). New highs from that, incidental ones:
OVERRIDE.update({
    ('L01', '4.4'): ('medium', 'the captured opcodes are only mentioned here (the S2S handshake and heartbeat of §4.2, 0x0C18); the subject of the section (the OPTool handlers 0x2818 / 0x2819 and the other small bodies) is in no capture', 'second reading'),
    ('Z02', '9.1'): ('medium', 'the captured opcodes are only mentioned here (0x10C6, 0x2019); the subject of the section (0x2044 / 0x2046 ride feeding) is in no capture', 'capture 0x2044, 0x2046 (feed a mount)'),
    ('Z04', '6.4'): ('medium', 'the captured opcodes are only mentioned here (0x6401 / 0x6402 of the level-20 announcement); the subject of the section (the megaphone 0x204B / 0x204C) is in no capture', 'capture 0x204B, 0x204C (use a megaphone item)'),
    ('Z09', '23.8'): ('medium', 'the captured opcodes are only mentioned here (0x3401 of `&makeitem`, 0x3459 of the destroy); the subject of the section (Lua `costumecreate` / `costumetakeoff`) is in no capture', 'a scripted map in a capture'),
    ('Z12', '3.3'): ('medium', '0x1035 / 0x245F are captured as parameter pushes of other classes; no capture is known to contain a Sentinel or Savior', 'capture with a Sentinel character'),
    ('Z12', '7.4'): ('medium', 'the captured opcodes are only mentioned here (0x1031 title blob, 0x4016 title save); the subject of the section (a title progress reset) is in no capture', 'capture across the reset time of a title'),
    ('Z13', '5.3'): ('medium', 'the captured opcodes are only mentioned here (cast bar, item use, soul-stone and storage link packets); the subject of the section (the pet item, 0xD411) is in no capture', 'capture with a pet item used'),
    ('Z15', '5.3'): ('medium', 'the captured opcodes are only mentioned here (0x1033, 0x3001, 0x4401); the subject of the section (0x441B quest done) is in no capture', 'capture: accept, progress and finish one quest (scenario 19)'),
    ('Z18', '1.4'): ('medium', 'the captured opcodes are only mentioned here (the S2S handshake and heartbeat); the subject of the section (OPTool and zone-ring sessions) is in no capture', 'none with one zone PC and no OPTool'),
    ('Z18', '6.4'): ('medium', 'the captured opcodes are only mentioned here (the title blobs 0x1031 / 0x1049 of the login); the subject of the section (the weapon title after an equipment change) is in no capture', 'capture 0x5C03 (weapon with a title)'),
    ('Z21', '5.5'): ('medium', 'the captured opcodes are only mentioned here (the abstate blob and its saves 0x1023 / 0x4007 / 0x4011); the subject of the section (the set-item part of the block) is in no capture', 'capture: log out wearing a full set'),
    ('Z21', '5.6'): ('medium', 'the captured opcodes are only mentioned here (0x100C / 0x1023 abstate blobs, 0x104E); the subject of the section (restoring a set-item state) is in no capture', 'capture: log in wearing a full set'),
    ('Z22', '7.2'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the bomb actor) is in no capture', 'capture a skill with this abstate type'),
    ('Z22', '7.5'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (dispel, cure, steal) is in no capture', 'capture a dispel or cure skill'),
    ('Z22', '9.5'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the time-attack actor) is in no capture', 'capture a skill with this abstate type'),
    ('Z22', '10.7'): ('medium', 'captured: the toggle Heat of Fury goes through the skill-enchant keep-time path (capture-validation §25.4), and the capture extends the section (keep times above 2^31 − 1: 1 385 447 ms sent, 1 345 294 tenths set, P02-B39, §13): a captured section in which a class applies', 'capture-scenarios 51 (toggle kept past its 23-min icon timer); X06 folds P02-B39 into the section'),
    ('Z22', '12.4'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (party enchant) is in no capture', 'capture-scenarios 15 (party) with a party buff'),
    ('Z25', '1.3'): ('medium', 'the captures run these slots for player skills only: Bash [01] against a mob (batches 2–3) and, in batch 4, the casts of `s24` (Dash ground target, Heat of Fury toggle, Divine Shield abort, Revival; capture-validation §25.2–§25.4, §25.8); the mob-side slots and the other branches are code only', 'a mob skill; skills of other classes'),
    ('Z25', '2.7'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (SS_HOLDME) is in no capture', 'capture a skill with this special'),
    ('Z25', '2.8'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the keep-time specials) is in no capture', 'capture a skill with this special'),
    ('Z25', '2.10'): ('medium', 'the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25), 0x2452); the subject of the section (the multi-hit tail) is in no capture', 'capture a multi-hit skill'),
    ('Z31', '3.5'): ('medium', 'the captured opcodes are only mentioned here (0x1047, 0x3001); the subject of the section (the 51 attribute classes) is in no capture', 'per class: the scenario of its item type'),
})

# ---- X07 part 3: hand pass after capture batch 4 (s24, s37b, s38; capture-validation §22–§25) ----------------------
# Baseline limit 1 again: new highs from opcodes the section only mentions (skill book 0x4801 / 0x4802 / 0x4804, the
# DoT damage 0x243C, Dash 0x2450 / 0x2451, the invalid-command answer 0x2011, auto-arrange 0x304A).
OVERRIDE.update({
    ('Z03', '9.4'): ('medium', 'the captured opcodes are only mentioned here (0x4801 / 0x4802 / 0x4804 of the skill-book learn, capture-validation §24.2); the subject of the section (0x4822 production field) is in no capture', 'capture 0x4822'),
    ('Z09', '2.3'): ('medium', 'the captured opcodes are only mentioned here (0x2434, 0x243D); the subject of the section (the per-tick game-mode work: ride timer, mount hunger, pet reactions, title minute counters) is in no capture', 'a ride, a pet or a title counter in a capture'),
    ('Z09', '8.5'): ('high', 'no opcode; the blast-to-effect delay `HitTime × 10 / 1000 − 2` tenths matches all four skills of batch 4 within one tick (Heat of Fury 1.32–1.39 s, Dash 0.36–0.41 s, Divine Shield 0.217 s, Revival 0.80 s; capture-validation §25.4)', ''),
    ('Z09', '12.6'): ('medium', 'the captured opcodes are only mentioned here (0x1805, the DoT damage 0x243C of batch 4); the subject of the section (magic fields and axial flags) is in no capture', 'a magic field on a map in a capture'),
    ('Z09', '17.3'): ('medium', 'the captured opcodes are only mentioned here (0x243C / 0x244A of batch 4); the subject of the section (the Lua damage, heal, kill and revive functions) is in no capture', 'a scripted map in a capture'),
    ('Z09', '26.4'): ('medium', 'the captured opcodes are only mentioned here (0x1805, 0x243C); the subject of the section (the Pine nodes suicide / teleport) is in no capture', 'a KQ played in a capture (scenario 31)'),
    ('Z09', '29.2'): ('medium', 'bug table (class X); the captured opcodes are only mentioned here (0x1805, 0x2011, 0x243C, 0x2449); the world objects and the script infrastructure are in no capture', 'a scripted map / KQ in a capture'),
    ('Z13', '4.6'): ('medium', 'the captured opcodes are only mentioned here (0x2434, 0x3C02); the subject of the section (the partner summon SummonMate01) is in no capture', 'SummonMate01 in a capture'),
    ('Z20', '5.2'): ('medium', 'the captured opcodes are only mentioned here (0x4801 / 0x4802 of the skill-book learn); the subject of the section (the name trie built at start-up) is not on the wire', 'none on the wire'),
    ('Z23', '1.3'): ('medium', 'the captured opcodes are only mentioned here (0x4821, 0x900D); the subject of the section (the vtable slots used by the skill list) is not on the wire', 'none on the wire'),
    ('Z25', '1.1.1'): ('medium', 'the captured opcodes are only mentioned here (0x2440 / 0x2441 of the casts); the subject of the section (which code reads each SS_* special member) is in no capture beyond the specials of the `s24` skills', 'capture a skill per special'),
    ('Z26', '5.5'): ('medium', 'the captured opcodes are only mentioned here (Dash 0x2450 / 0x2451, the potion use 0x3016 / 0x301A); the subject of the section (0x304E NC_ITEM_USE_ACTIVESKILL_REQ) is in no capture', 'test client: send 0x304E'),
    # A class applies and the capture covers only a mention: stays low.
    ('Z11', '3.4'): ('low', 'README §5.6 row; 0x304A is captured from the client\'s own auto-arrange (capture-validation §24.8), not from a debug wrapper; `&queststart` / `&questread` / `&viewaggrolist` are in no capture', 'the wrapper commands in a capture'),
    ('Z11', '5.2'): ('low', 'weak markers (inferred 1, fh-doc 2); 0x2011 is the answer to the invalid `&resetabstated` and 0x243C the poison damage of batch 4 (capture-validation §25.6, §25.7); no mob tool was used', 'capture `&mobdist`, `&killallmob`, `&suicideallmob`'),
    # Corrected or unconfirmed by batch 4.
    ('Z03', '2.6'): ('low', '0x243E is in no capture: the 2016 client\'s assist sent a plain 0x2401 to the target\'s target (capture-validation §25.5, §13 "unconfirmed"), and the 2016 client export has no 0x243e literal (docs/knowledge/X07.md §2)', 'test-client case T25 (capture-scenarios §3.41)'),
})

# X07: the generator now reads table rows with several opcodes ("0x9007 / 0x9008", 78 more captured opcodes, most of
# them the WM / zone login lists of batch 2). Those lists were captured empty (n 0): like W03 §1.1 (a world with no
# guild), a section whose subject is the list content stays medium.
OVERRIDE.update({
    ('W04', '11'): ('medium', 'captured only as empty lists: CharDB 0x101B `{handle, 0}` and WM→Z 0x1032 `n 0` at every login (capture-validation §7.4, §7.5); no charged buff in a capture, 0x9001 / 0x9002 not captured', 'capture with an active charged buff (premium item), then a map login'),
    ('W04', '3.3'): ('medium', 'the captured opcode is only the passive list 0x1025, empty (`n 0`, capture-validation §7.5); the subject of the section (0x4820 passive skill learned) is in no capture', 'capture: learn a passive skill'),
    ('Z09', '14.5'): ('medium', 'the captured opcodes are only mentioned here (jump 0x2024 / 0x2025, emote 0x2020 / 0x2021 of batch 3); the subject of the section (Lua triggers on chat, jump, item use) is in no capture', 'a scripted map with a trigger in a capture'),
    ('Z15', '4.2'): ('medium', 'captured only as empty lists: 0x1021 / 0x10CD / 0x10D6 `n 0` at every map login (capture-validation §7.5; P02-B10); no quest in the diary of any captured character', 'capture-scenarios 19 (a quest accepted, then a map login)'),
    ('Z15', '5.7'): ('medium', 'captured only as empty lists: the saves 0x400F / 0x4029 / 0x402B `n 0` and the login lists `n 0` (capture-validation §7.5); no quest in the diary of any captured character', 'capture-scenarios 19 (a quest accepted, then a save and a map login)'),
    ('Z17', '3.5'): ('medium', 'captured only as empty lists: WM→Z 0x10D0 `n 0` and client 0x482C `num 0` (capture-validation §5.2, §7.5); 0x4023 / 0x4034 not captured; no item-action cool-down was persisted', 'capture: use an item with an item-action cool-down, then a map login'),
    ('Z28', '5.2'): ('medium', 'captured only as empty lists: 0x10E3 / 0x10E6 / 0x10E9 `{5, n 0}` at every map login (capture-validation §7.5; P02-B10); no card collection in a capture', 'capture with a collected card, then a map login'),
})

# ---- X07 review (part 5): two batch-4 highs whose own open point is a capture question ----------------------------
OVERRIDE.update({
    ('Z23', '4'): ('medium', 'empower allocation and reset captured with one learned step (capture-validation §24.3, '
                   '§24.4); the section\'s own inferred point, which step ID the client names in 0x4811 with two learned '
                   'steps of one line (it decides Z23-B8: the wrap to 15, 0x885 and the 0x68A kick), is not captured',
                   'capture-scenarios 51 step 1'),
    ('Z23', '2.5'): ('medium', 'switching on and off by cast captured with one learned step (capture-validation §25.4); '
                     'two points of the section are not: the lower-step case Z23-B1 and the crafted field cast of a toggle '
                     'that is on, Z23-B20 (inferred)', 'capture-scenarios 51 step 3; a crafted 0x2440 (test client, 41)'),
})

# ---- X09 part 3: hand pass after capture batch 5 (s45, s46, s52; capture-validation §26–§28) ----------------------
OVERRIDE.update({
    # captured only in part: the set request, not the load and push
    ('W04', '17.2'): ('medium', 'only the set path is captured (0x0846 -> CDB 0x0847, no reply; capture-validation '
                      '§27.4); the load 0x0844 and the push 0x0845 appeared in no capture (no usp_SpamFilter_get row for '
                      'any captured character, §7.4), so W04-B60 (the session copy not updated) could not show',
                      'set the filter, then a new character login and map login of the same account (0x0844 -> 0x0845 '
                      'with the set values or the old ones: W04-B60)'),
    # captured and corrected: a captured section in which a class applies (baseline low: cv corr, no opcode)
    ('Z11', '4.2'): ('medium', 'captured: `&mobbreed` and `&mb` in s45 (the wall "Mob : 5989", capture-validation '
                     '§27.6), and the capture corrected the section (the value is the zone\'s mob count, not the mob ID; '
                     '§13 -> X08): a captured section in which a class applies', 're-read the rest (§3); read with P02 '
                     '"Corrections"'),
    # captured beside a bystander; the shout of s45 reached a player out of sight (not in capture-validation §13)
    ('Z01', '3.2'): ('medium', 'sight delivery to a bystander is captured (walk relay, swings, casts, 0x1805; '
                     'capture-validation §27.2, §27.6, §27.7), but the section gives every so_AllInMap0..5 the sight '
                     'cells and ali_Work a sight check, while the shout of s45 (so_AllInMap1, "filtered as in Z01 §3.2" '
                     'per Z02 §3.2) reached a player out of sight (§27.4): one of the two statements is too general '
                     '(inferred; not in §13)', 're-read the rest (§3): which iterator and visitor so_AllInMap1 uses'),
    # corrected by batch 5; the open branches are scenarios of X09
    ('Z04', '4.1'): ('medium', 'captured: split-and-merge and the exchange onto a stack at MaxLot (capture-validation '
                     '§26.2), and the capture extended the branch list (b >= MaxLot -> irm_Exchange; §13 -> X08); the '
                     '0x24A refusal and the irm_Move / 0x20A branch are in no capture', 'capture-scenarios 53 (S22: a '
                     'character-bound stack in the account storage)'),
    ('Z02', '4'): ('medium', 'captured: Sit 0x2020 {7} -> 0x2021, the step that ends an emote, jump (capture-validation '
                   '§27.3), and the client side was extended (Stand and Esc send nothing; §13 -> X08); 0x2022 / 0x2023 '
                   'and 0x2020 {6} are in no capture', 'capture-scenarios 54 (key function 0x6F; /stand), test-client '
                   'case T27 (0x2020 {6})'),
})
