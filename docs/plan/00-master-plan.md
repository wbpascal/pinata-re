# Master plan: reconstructing the server in pseudocode

Goal: a behavioural reconstruction of every server process (Login, World manager, Zone, Account,
AccountLog, Character, GameLog) as structured pseudocode. Each block cites the original function, and each
packet is cross-checked with the 2016 client. Format and depth follow `docs/pseudocode/login-server.md`
(Login is **done**).

## Progress

[`progress.md`](progress.md): how far along each server component is (handlers documented, functions cited, gaps, items done), generated
by `tools/protocol-re/coverage.py --overview` from the docs in the tree, so it is the same in every branch with the same
docs. Every item runs it via `regen.sh` at its end. **After merging item branches, run
`python3 -I tools/protocol-re/coverage.py --overview` and commit**: the merge keeps one side's file (`.gitattributes`
`merge=ours`, so it never conflicts) and the regeneration makes it correct for the merged docs. One-time setup per
clone: `git config merge.ours.driver true` (without it the file conflicts; resolve by running the same command).

## How to run a work item

An item runs as a series of short sessions, **one part per session**. Each plan's **Parts** table lists the parts:
handler groups of about 2,500 decompiled lines, then a sweep part and a review part. Every turn re-reads the whole
context, so several short sessions cost much less than one long one (W04 in one long session: ~15M weighted tokens,
median context 200–250k). Each session reads `docs/plan/status/<ID>.md`, does the first open part, writes the
status (`**State:** part n of m done` plus short working notes for later parts), commits, and stops.

**Tutorial (Claude Code)**

1. Commit everything the item needs on `master`, then create a worktree for the item (herdr workspace or
   `git worktree add ../fiesta-rea-<ID> -b <ID>`) and open a terminal in its root.
2. Start the next part:
   - `tools/protocol-re/item.sh <ID>`: one interactive session. When it has committed its part, close it with
     `/exit` and run the command again for the next part. Do not type "continue" or use `/resume`: that keeps
     the large context and undoes the saving.
   - `tools/protocol-re/item.sh <ID> --auto`: headless, one session per part, until the status says done. It
     prints a short summary after each part and stops when a session commits nothing or the item awaits review.
     **Inside Herdr** (recommended), `--auto` opens each part as an interactive session in a new tab of the current
     space (`<ID> part <n>`), so you can watch it and step in. When the session has committed and gone idle, the tab
     closes and the next part starts. If a session goes idle without a commit, or blocks or exits, its tab stays
     open and the loop stops: finish or close that tab, then run `item.sh <ID> --auto` again.
3. Options as environment variables: `MODEL` (default `opus`), `EFFORT` (`high`), `PERM` (`auto`; use
   `PERM=manual` interactively to approve actions yourself). Example: `EFFORT=medium tools/protocol-re/item.sh Z09`.
4. After a usage limit or a crash: do not resume the old session. Check `git status` in the worktree (commit or
   discard what the cut-off part left), then run `item.sh` again. It continues from the status file.
5. When the status says done: merge the branch into `master` (see Progress above for `progress.md`).

`item.sh` starts lean sessions: no plugins, no MCP servers (no REA; use the exports, `objdump` or Python over the
PE), no web or artifact tools. That cuts the start context from 35–56k to ~16k tokens, which every turn re-reads.

**Other agents** (Codex, OMP): start a fresh session in the worktree per part with
> Execute the next part of `docs/plan/items/<ID>.md` as its "How to work" section describes (one part per session).

`AGENTS.md` is loaded automatically (`CLAUDE.md` is a symlink to it for Claude Code). It holds the shared conventions,
the data locations (`re-data/exports`, `re-data/ghidra`) and the facts already established, so no session
re-decompiles or re-derives anything.

Items in the same phase can run in parallel: they write disjoint files (see "Shared files" in `AGENTS.md`). Parallel
sessions share one usage limit. Dependencies are soft. An item can start before its dependencies finish, but it will
produce better results after them, so respect the order when you can.

## Phases and items

Sizes count the handlers in scope and their decompiled lines. Callee logic adds 2–10× more.

### Phase 1: foundations (run these first; all can run in parallel)

| ID | Item | Depends | Handlers | Lines |
|---|---|---|---|---|
| [C01](items/C01.md) | Client packet-handler inventory (names and meaning of server→client packets) | – | client | – |
| [C02](items/C02.md) | 2017 client PDB: official opcode names, `PROTO_NC_*` structs, shared types, client function names | C01 (soft) | – | – |
| [S01](items/S01.md) | 2016 server PDBs (NA2016): official names, types, `PROTO_NC_*` layouts of the exact build; per-item follow-ups | C02 | – | – |
| [W01](items/W01.md) | World manager core: sessions, world login, characters, zone handoff | – | see file | |
| [Z01](items/Z01.md) | Zone core: process, maps, objects, player session, map login/logout | – | see file | |
| [P01](items/P01.md) | Packet capture decoder + validator (pure Python, self-testing; needs no captures yet) | – | – | – |
| [P03](items/P03.md) | Wireshark Lua dissector generated from the docs (live decrypted, named packets while recording) | P01 (soft) | – | – |

C01 has the highest leverage: every later item uses its client cross-reference. Run it first if you
can only run one item at a time. C02 (added after C01, W01, Z01, P01, P03 were done) comes next: the 2017
PDB names 1347 opcodes that are unnamed today and gives field names for ~2300 packet structs, so run it
before the phase-2 items.

S01 (added 2026-11-13) has the highest leverage of all remaining work: `Files/Server/NA2016` turned out to be the same
server builds with their private PDBs (Login, WM, Zone, Account, AccountLog). The `<bin>-pdb` exports and
`names/<bin>/S01.json` already exist; run S01 for the layouts, patch analysis and the per-item follow-up table, then
continue the open phase-2 items with the PDB exports as their main reading source.

### Phase 2: subsystems (any order once their dependencies are done; up to ~4 in parallel works well)

| ID | Item | Depends |
|---|---|---|
| [W02](items/W02.md) | WM: party and raid | W01 |
| [W03](items/W03.md) | WM: guild and guild academy | W01 |
| [W04](items/W04.md) | WM: friends, chat routing, KQ, holy promise, instances, misc | W01 |
| [W05](items/W05.md) | WM: process services left out of W01-core: main loop, data loader, 0x0849 broadcast, session teardown (added by W04) | W01 |
| [S02](items/S02.md) | Shared server library (Login / WM / Zone): IOCP sockets, acceptor, packet buffers, `CCsl` config-script and GDP file readers (added by W05) | W05 |
| [L01](items/L01.md) | Login server: process layer and session pools left out of `login-server.md` (main thread, packet pump, session pools, world status table) (added by S02) | L00, S02 |
| [Z02](items/Z02.md) | Zone: movement, chat, emotes, sight, NPC menus, scenario | Z01 |
| [Z03](items/Z03.md) | Zone: combat, skills, abstates, damage | Z01 |
| [Z04](items/Z04.md) | Zone: items, inventory, equipment, upgrades | Z01 |
| [Z05](items/Z05.md) | Zone: ITEMDB protocol (item persistence) | Z04 |
| [Z06](items/Z06.md) | Zone: trade, booths, gambling, dice | Z04 |
| [Z07](items/Z07.md) | Zone: stats, progression, pets, mounts, mini-house, cards | Z01 |
| [Z08](items/Z08.md) | Zone: quests, KQ, instances, guild/party/friend zone side | Z01 |
| [Z09](items/Z09.md) | Zone: world simulation (mobs, AI, spawns, drops, scripts, timers) | Z01, Z03 |
| [Z10](items/Z10.md) | Zone: certification and the downloaded start script (stage order, run/walk factors, kill switch?) | Z01 |
| [Z11](items/Z11.md) | Zone: GM ampersand (&) commands (added by Z02: 119 `AmpersandCommand_ac_*` functions) | Z01, Z02 |
| [Z12](items/Z12.md) | Zone: stat calculation, level/exp, login data parsing (added by Z07) | Z03, Z07 |
| [Z13](items/Z13.md) | Zone: mini-house object, wedding hall, pets and mounts internals (added by Z07) | Z07 |
| [Z14](items/Z14.md) | Zone: instance dungeons, zone-ring storage handlers, raid internals (added by Z08) | Z08 |
| [Z15](items/Z15.md) | Zone: quest script engine (added by Z08) | Z08 |
| [Z16](items/Z16.md) | Zone: kingdom quest element and guild tournament system (added by Z08) | Z08 |
| [Z17](items/Z17.md) | Zone: item actions and costume weapon/shield charges (added by Z06) | Z03, Z04 |
| [Z18](items/Z18.md) | Zone: leftovers of finished zone items from Z09's coverage boundary (221 functions for Z01–Z04, Z06, Z07) (added by Z09) | Z01–Z04, Z06, Z07, Z09 |
| [Z19](items/Z19.md) | Shared config-script reader `CCsl` and the server config file format (`*ServerInfo.txt`), all servers (added by Z10) | Z01 |
| [Z20](items/Z20.md) | Zone: skill data box loader (`SkillDataBox::sdb_Load`, `SkillDataIndex` build, `PassiveDataBox`) (added by Z11) | Z01, Z03 |
| [Z21](items/Z21.md) | Zone: set items (`SetItem` / `SetItemEffect` / `SetEffect` tables, set detection, set-item abstates and skill effects) (added by Z12) | Z03, Z12 |
| [Z22](items/Z22.md) | Zone: abnormal-state actor classes (`SubAbnormalStateActor*` bodies: DoT/HoT, area damage, bomb, detach, rate buffs) (added by Z12) | Z03, Z18 |
| [Z23](items/Z23.md) | Zone: per-player active skill list (`CharaterSkillList` / `MoverSkillList`: toggle skills, cooldowns, delay groups, empower, mastery) (added by Z20) | Z03, Z20 |
| [Z24](items/Z24.md) | Zone: item-side data loaders (`UsedItemEffect`, `ItemUseFunction`, `ChargedItemEffectDataBox`, `MoverDataBox`, `cStateItemDataBox`, `MysteryVaultTable`, `RidePetDataBox`) and `CharClassDataBox` (added by Z20) | Z01, Z04, Z20 |
| [Z25](items/Z25.md) | Zone: skill special effects (dispel / cure bodies, `SkillSpecial` handlers of `smo_SkillBlast`, reflection damage) (added by Z17) | Z03, Z22 |
| [Z26](items/Z26.md) | Zone: silver-wing teleport item (saved location, server menu, portal cast and blast) (added by Z23) | Z02, Z04, Z23 |
| [Z27](items/Z27.md) | Zone: item table loader `ItemDataBox::idb_Load` (ItemInfo, ItemInfoServer, GradeItemOption, ItemDropLog, ItemSort, CollectCardMobGroup, ItemMoney; special item IDs) (added by Z24) | Z01, Z04, Z24 |
| [Z28](items/Z28.md) | Zone: collection-card data tables and card roll (CollectCard*.shn `SHND::CommonData` loaders, `g_CardCollectMake`, album / bookmark loaders) (added by Z27) | Z07, Z09, Z27 |
| [Z29](items/Z29.md) | Zone: party experience tables (`PartyBonusByMember.shn` / `PartyBonusLimit.shn` loaders of `HitMeList::hml_Load` and their readers) (added by Z28) | Z03, Z28 |
| [Z30](items/Z30.md) | Zone: handler-reachable leftovers (`coverage.py` gaps: change-character-ID handlers, item dismantling, SP / HP stones, title set, spam rules, party / guild helpers) | Z01, Z04, Z08, Z14 |
| [Z31](items/Z31.md) | Zone: class-named functions no document cites (player / object members without a direct caller, inventory lock list, item attribute classes, table loaders) and open points of Z01–Z04 (added by X02) | Z01, Z04, Z30, S01 |
| [Z32](items/Z32.md) | Zone: gamble internals (TaiSai dice table object, slot machine classes) (added by X02) | Z06 |
| [W06](items/W06.md) | World manager: class-named functions no document cites and three unread guild / option points (added by X02) | W03, W04, W05 |
| [D01](items/D01.md) | Account + AccountLog servers (resolves open Login error conditions) | – |
| [D02](items/D02.md) | Character server: characters, avatars, save/load | – |
| [D03](items/D03.md) | Character server: items, economy, pets, house | D02 |
| [D04](items/D04.md) | Character server: social, guild, quests, skills | D02 |
| [D05](items/D05.md) | GameLog server | – |
| [D06](items/D06.md) | Database behaviour the backups do not give us: missing procedures, schema, inferred DB statements of D01–D05 (added by D02; run last, before X01) | D01–D05 |
| [D07](items/D07.md) | Character server: D04 residue — academy reward storage merge (0x986B) and tournament reward item attributes (0x74AA) (added by D04) | D04, D03 |
| [D08](items/D08.md) | DB servers: process layer and shared-class copies of Account / AccountLog / Character / GameLog, SOAP item-shop client, open points of D01 / D02 (added by X02) | D01, D02, D05, S02, L01 |
| [P02](items/P02.md) | Capture validation: confirm/correct layouts and message order with real traffic. **Recurring:** run after each batch of captures and after each phase | P01, captures |
| [P04](items/P04.md) | Protocol README: zone seed on accept, server-initiated heartbeat, §2 flows as captured (added by P02) | P02 |

The DB items (D01–D05) don't depend on the zone/WM items and can fill gaps in parallel runs.

### Phase 3

| ID | Item | Depends |
|---|---|---|
| [X01](items/X01.md) | Integration: architecture overview, feature → message index, glossary, contradictions, original-server bug register, regen | all |
| [X02](items/X02.md) | Confidence review: rate every section, adversarially re-check load-bearing claims, write targeted capture scenarios (with DB/SHN/GM setups and predictions). **Recurring:** re-run after P02 processes those captures | all phase-2 items, X01 (soft) |
| [X03](items/X03.md) | Integration update: X02's corrections and the bugs of X02 and its follow-ups into the README register and the superseded-statements list (added by X02) | X01, X02; Z31, Z32, W06, D08 (soft) |
| [X04](items/X04.md) | Integration update: P02's capture batches 2 and 3 (corrections, bugs P02-B5 … B32, captured evidence) into the README register and the superseded-statements list (added by P02) | X01, P02; X03 (soft: not at the same time) |
| [X05](items/X05.md) | Capture scenarios and ratings after capture batch 3: result lines, fixed scenario texts, scenarios for what is still open, confidence re-rating (X02's recurring re-run, added by P02) | P02 (batch 3), X02 |
| [P05](items/P05.md) | Protocol README: the flows of capture batch 4 (back to select, quit, zone connection lost, logout timers, 0x145, create refusal, renames) (added by P02) | P04, P02 (batch 4) |
| [X06](items/X06.md) | Integration update: P02's capture batch 4 (corrections, bugs P02-B33 … B40, captured evidence) into the README register, the superseded-statements list and the sequence index (added by P02) | X04, P02 (batch 4) |
| [X07](items/X07.md) | Capture scenarios and ratings after capture batch 4: result lines for scenarios 24 / 37 / 38, fixed scenario texts, scenarios for what is still open, confidence re-rating (X02's recurring re-run, added by P02) | P02 (batch 4), X05 |
| [P06](items/P06.md) | Protocol README: the flows of capture batch 5 (rename onto a taken name, the second 0x1001 after a skip, zone kick 0x0C1A → 0x0C17, SHN refusal 0x1804, whisper fail 0x200E) (added by P02) | P05, P02 (batch 5) |
| [X08](items/X08.md) | Integration update: P02's capture batch 5 (corrections, bugs P02-B41 … B44, captured evidence) into the README register, the superseded-statements list and the sequence index (added by P02) | X06, P02 (batch 5) |
| [X09](items/X09.md) | Capture scenarios and ratings after capture batch 5: result lines for scenarios 45 / 46 / 52 (39 not captured), fixed scenario texts, scenarios for what is still open, confidence re-rating (X02's recurring re-run, added by P02) | P02 (batch 5), X07 |
| [X10](items/X10.md) | Superseded statement Z01 §3.2 (broadcast reach) into the README list: X09's code read, not in capture-validation §13 (added by X09) | X09, X08 |

Exact handler counts and line sizes per item: `docs/plan/items/_summary.json` and the scope table at the top
of each item file.

## Packet captures

Static analysis tells us what the code *can* send. Captures confirm what it *does* send. How to record
them, which scenarios, and privacy notes: [`capture-guide.md`](capture-guide.md). Put captures and their
notes in `re-data/captures/`, then run P02. Capture-confirmed facts are the strongest evidence level
(see `AGENTS.md`). P02 reports contradictions per owning work item, so the owner can fix them in a
follow-up session.

## Suggested order with limited budget

1. C01 → W01 → Z01, plus P01 and P03 (both cheap; install the dissector, record capture scenarios 1–5, run P02 early)
1b. C02, then the follow-ups above (C01, W01, L00 first)
1c. S01, then its follow-ups (`docs/knowledge/S01.md`) for finished items
2. Z02, Z03, Z04, W02 (core gameplay)
3. Z07, Z08, Z05, Z06, W03, W04
4. D02, D01, D03, D04, D05, Z09, Z10, Z11, Z12, Z13, Z14, Z15, Z16, Z17, Z18, Z19, Z20, Z21, Z22, Z23, Z24, Z25, Z26, Z27, Z28, Z29, Z30, W05, S02, L01, then D06
5. P04 (README corrections from the first capture batch), P02 again with fuller captures, then X01
6. X02 → user records its scenarios → P02 → X02 again (repeat until the low ratings are gone or not worth a capture)
7. The follow-ups X02 created, any order: Z31, Z32, W06, D08; then X03 for the register and the corrections
8. X04 (P02's batches 2–3 into the README; after X03 or at least not alongside it) and X05 (X02's re-run after batch 3) → user records the new scenarios → P02 again
9. P05 (batch 4 into the protocol README; after P04), X06 (P02's batch 4 into the README; after X04) and X07 (X02's re-run after batch 4) → user records the new scenarios → P02 again
10. P06 (batch 5 into the protocol README; after P05), X08 (P02's batch 5 into the README; after X06) and X09 (X02's re-run after batch 5), X10 (X09's Z01 §3.2 row; after X08) → user records the new scenarios → P02 again

Large items (Z04, Z05, Z08, D03, D04) will probably need two or three sessions each. Starting a new session
with the same plan file resumes from the status file.

## Output layout

```
docs/pseudocode/login-server.md           done (reference format)
docs/pseudocode/wm/W0x-*.md               world manager
docs/pseudocode/zone/Z0x-*.md             zone
docs/pseudocode/db/D0x-*.md               database servers
docs/pseudocode/README.md                 X01: overview + index
docs/knowledge/<ID>.md                    cross-item facts (structs, offsets, subsystem notes)
docs/plan/status/<ID>.md                  progress logs
tools/protocol-re/names/<bin>/<ID>.json   discovered names (merged by clean.py)
docs/protocol/annotations/<ID>.json       verified packet layouts (merged by packets.py / regen.sh)
re-data/client-handlers.json              C01: client opcode → handler map
docs/protocol/pdb-layouts.json            C02: PROTO_NC_* layouts from the 2017 PDB
```

## Regenerating the plans

The item definitions live in `tools/protocol-re/make_plans.py`. To change scope or wording, edit that file
and run `python3 -I tools/protocol-re/make_plans.py`. Don't hand-edit `docs/plan/items/*.md`.
