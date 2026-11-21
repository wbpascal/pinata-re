# Capture scenarios 14–52 (X02; 45–50 added by X05, 51–52 by X07)

Continues the 13 scenarios of `docs/plan/capture-guide.md`. Those gave seven captures (login, idle, walk and
portals, shop and storage, combat with `&levelup` / `&linkto`); everything else in the reconstruction is read
from code only (`docs/review/confidence.md` §2: 2 042 sections rated medium or low after capture batch 4, 2 058 after batch 3). Each scenario here names the
claims it tests, the steps, and a **prediction**: the opcodes our documents expect, in order, with the field
values they give. A capture that differs from the prediction is a finding; P02 validates the captures as usual
(`docs/plan/items/P02.md`), then X02 is re-run to update the ratings.

State of this file: scenarios, GM setups and boundary values (X02 part 8); the SQL of the database setups
**S1–S21** (§8; S17–S19 added by X05, S20–S21 by X07) and the table / config experiments **X1–X7** (§9) (X02 part 9; §6 is the index). The SQL was
written from stored-procedure source and has not been run against a database: read §8's first paragraph.

State after capture batch 3 (X05): scenarios 14, 21 (with S13, S16, X3) and 37 are recorded and carry a "Result
(P02 batch 3)" line; scenario 24 was not captured then. What they and batch 2 left open is in scenarios
**45–50** (they stand after 44, before the tool scenarios 41–43), setups **S17–S19**, test-client cases
**T15–T22** and the "Added by X05" steps under scenarios 30, 36, 39 and 48. §2, §6 and §7 count all of them;
the map from each open thing to its scenario is `docs/knowledge/X05.md`.

State after capture batch 4 (X07): scenarios 24 (`s24`), 37 (second run `s37b`) and 38 (`s38`) are recorded and
carry a "Result (P02 batch 4)" line and a "Notes corrected" line (capture-validation §13); their steps carry the
fixes. The run kits under `tools/capture/` end with `collect` (§1). The map from each open thing of batch 4 to its
scenario is `docs/knowledge/X07.md`: scenarios **51** (skills) and **52** (character select and session), placed after
50, before 41, setups **S20–S21** and test-client cases **T23–T25**; §2, §6 and §7 count them, and 24 and 38 now
stand among the recorded rows of §2.

State after capture batch 5 (X09): scenarios 45 (`s45`), 46 (`s46`) and 52 (`s52`) are recorded and carry a "Result
(P02 batch 5)" line and a "Notes corrected" line (capture-validation §13, §26–§28); their setups name their run kits
and their steps and predictions carry the fixes (46: the client's money and soul-stone refusals, the first empty
cell; 45: four hits, 970 units, three aborts by a step, no `0x2022`; 52: a changed row, not an appended byte, the
decrypted buffer, the renamed character started). Scenario 39 has a notes template and a run kit but no capture.
The map from each open thing of batch 5 to its scenario is `docs/knowledge/X09.md`.

## 1. Conventions

- **Test server only.** Every scenario changes characters, some crash or disconnect on purpose (41, 42, 43).
  Test accounts only (`capture-guide.md` "Privacy").
- **Record the server links too.** Use the widened filter of capture batch 2 (`capture-validation.md` §7.1: the
  client ports plus the WM ↔ zone, zone ↔ Character server (9411) and GameLog links, loopback when all servers
  run on one PC). Half of every prediction is on those links; they are not encrypted.
- **Clients.** A = first test account, B = second account on a second client. "A and B on two zones" = A on a map
  of zone 0, B on a map another zone process hosts (`9Data/ServerInfo` map list; walk B through a gate first).
- **GM character.** A is a GM with admin level 100 (setup S1). `&` commands are typed into normal chat (Z11 §1.1).
  A GM login adds `0x10C6 NC_CHAR_ADMIN_LEVEL_INFORM_CMD {nAdminLevel}` to the login burst (Z11 §1.4): seeing it
  is the check that S1 worked.
- **Notes file** as in `capture-guide.md`: character names, levels, money before and after, item names and
  cells, the time of each step. For item scenarios also the `tItem` rows before and after
  (`docs/knowledge/D03.md` "For capture scenarios (X02)", 13 SQL checks that run alongside 20–22, 34, 35).
- **Run kits** (`tools/capture/<n>/<n>-server.ps1`) write the capture, `-prep.txt` and `-db.txt` into their `out\`
  folder. End every run with `<n>-server.ps1 collect -Dest <folder of the notes file>` (24 and 37b: or `cleanup -Dest
  …`; 38: `-Pcap <capture file>` as well), which copies all three and warns about a missing one. `s38` lost its `-db.txt`
  because only the pcapng was copied by hand (capture-validation §23; X07).
- **Notation.** `C→Z`, `Z→D` … as in `docs/pseudocode/README.md` §3.1 (C client, L Login, W WM, Z zone, D
  Character server, G GameLog, AL AccountLog). `{…}` = payload fields by our documents' names. "all Z" = the WM
  broadcast to every zone link. A section reference is the place the prediction was taken from.
- **Verdict words in "Disproved by":** a missing packet, another opcode, another order, or another value of a
  named field. A prediction that holds raises the section to high; one that fails becomes a correction row in
  `docs/knowledge/X02.md` §0.

Common GM setups (Z11 §2; all persistent unless noted):

| Need | Command | What to expect on the wire |
|---|---|---|
| level | `&levelup <n>` | per level `0x240C`, `0x240D`, `0x2446`, W `0x1074`, G `0x041E`, save (captured once, Z11 §7.3) |
| money | `&getmoney <n>` | D `0x3438`, C `0x1033`, `0x300A` (Z11 §7.4) |
| an item | `&makeitem <InxName> [-l<lot>] [-u<n>]` | D `0x3401` → `0x3402`, C `0x3001` (Z11 §4.3) |
| empty inventory | `&cleariv` | D `0x3459` → `0x345A`, C `0x3001` per cell (Z11 §4.3) |
| full HP / SP | `&fullpoint` | nothing (Z11 §4.4) |
| a skill | `&learnskill <skillId>` | D `0x4801` → `0x4802`, C `0x4804` (Z11 §4.4) |
| go to a map | `&linkto <map> [<x> <y>]` | `0x1809` or the zone change of README §3.11 (captured) |
| mobs | `&mobbreed <Mob> 1 10 n 5` | mob appear packets, `0x2011` "Mob : %d" (Z11 §4.2) |

`InxName` values come from `ItemInfo.shn` / `MobInfo.shn`
(`python3 -I tools/protocol-re/shn.py Files/Server/2016/9Data/Shine/ItemInfo.shn | rg -i <word>`).

## 2. Order of work

The order is the order for the **rebuild** (decided 2026-11-16: the rebuild must match the 2016 client only, it
does not replace the original processes one by one). Rank = what a wrong assumption would cost the rebuild, then
how early the feature comes, then the capture cost; the ranking and its reasons are the `PRIORITY` list of
`docs/plan/status/X02-scen.py`, which also holds each scenario's opcode set. Only ranks 1–3 belong before the
rebuild starts; the rest is recorded shortly before its feature is implemented, and the ranks under "with its
feature" follow the rebuild's own feature order. 48 and 50 are dropped: they test the original processes among
themselves (a stop cause, timing). 47 and 49 are optional for the same reason: their refusals need a DB or table
changed under an online player (49's steps were not re-read for a refusal a normal client can reach).

"Sections reached" = sections rated medium or low that name at least one opcode the scenario should put on the
wire and no capture holds yet. It is a reach count, not a proof, and no longer the sort key (until X05 the table
was sorted by sections per minute). A row marked *(recorded)* counts what its opcode set still leaves uncaptured,
not what a second run of its steps would bring: 37's set holds the character-load blocks (`0x1008`–`0x1032`) and
the whole Login / WM departments, of which one login of Test2 delivers only the blocks that character has; the
uncaptured rest needs another character (guild, pet, house: log in again after scenarios 18, 25, 28) or the
refusals of its steps 3–6 not yet run (`s37b` of batch 4 ran only the character-select refusals). 14 and 21 are
continued by 45 and by 46, 47, 49; 24 and 38 (batch 4) by 51 and 52 (X07), with T23–T25 of 41 for the refusals
the 2016 client pre-empted.

<!-- ORDER:begin -->
| Rank | # | Scenario | When | Needs | Minutes | Sections reached | Opcodes not yet captured | Why at this rank |
|---|---|---|---|---|---|---|---|---|
| 1 | 37 | Login side: idle heartbeat, refusals, character delete *(recorded, batches 3 and 4)* | before the rebuild starts | DB / config setup | 6 | 134 | 71 | its refusal steps 3–6 not yet run (S10, S11, X6) finish the login side; `s37b` ran only the character-select refusals |
| 2 | 52 | Character select and session II: what `s37b` / `s38` left open | before the rebuild starts | GM, 2 clients, DB setup S20, a zone restart | 15 | 19 | 2 | closes the session paths `s37b` / `s38` left open: the stale tutorial copy, the zone-initiated kick with a real user number |
| 3 | 51 | Skills II: what `s24` left open | before the rebuild starts | GM, 2 clients for steps 2 (heals) and 4, DB setup S21 for steps 6–7 | 80 | 8 | 5 | the skill paths the client reached only with one learned step: empower wrap, toggle steps, skill-save columns |
| 4 | 46 | Items III: no DB change | early: core gameplay | GM | 12 | 10 | 5 | closes what 21 left open on stack moves and buy-back |
| 5 | 39 | Combat extras: death penalty, PK, revive item, knock-back | early: core gameplay | 2 clients, GM | 8 | 50 | 27 | party / PK death and exp loss are not captured at all |
| 6 | 45 | Second client in sight II | early: core gameplay | 2 clients | 8 | 8 | 3 | walk, sit, emote stop: the remaining movement relays |
| 7 | 36 | Block list, reports, options, megaphone | early: core gameplay | 2 clients | 5 | 65 | 89 | cheap, high reach; settles the option-save tail of `0x7037` |
| 8 | 23 | Quest: accept, kill, finish, give up; class change | early: core gameplay | GM | 8 | 86 | 49 | the quest engine has no capture-confirmed section |
| 9 | 22 | Upgrade, gems, random options, endurance | early: core gameplay | GM | 8 | 53 | 58 | item attribute changes the client displays directly |
| 10 | 15 | Party across two zones | early: core gameplay | 2 clients | 8 | 53 | 52 | party is the first social feature; the zone change itself is captured |
| 11 | 17 | Friends and character titles | early: core gameplay | 2 clients | 4 | 40 | 38 | cheap; fills the WM social packets |
| 12 | 20 | Trade and booth | early: core gameplay | 2 clients | 10 | 28 | 65 | not captured at all; item duplication if wrong |
| 13 | 18 | Guild life cycle and guild storage | with its feature | 2 clients, GM | 12 | 158 | 242 | largest uncaptured area; log in again afterwards for the guild load blocks |
| 14 | 19 | Guild academy | with its feature | 2 clients, GM | 6 | 97 | 147 | same session as 18 |
| 15 | 16 | Raid | with its feature | 2 clients (3 better) | 6 | 37 | 66 | builds on party |
| 16 | 25 | Pet | with its feature | GM | 8 | 29 | 19 | log in again afterwards for the pet load blocks |
| 17 | 26 | Mounts and minimon | with its feature | GM | 5 | 27 | 23 | small, self-contained |
| 18 | 27 | Wing stone and silver wing | with its feature | GM | 5 | 47 | 13 | small, self-contained |
| 19 | 34 | Premium inventory, charged buffs | with its feature | DB setup | 5 | 39 | 23 | needed once charged items are sold |
| 20 | 40 | Gathering, production, item emotes, way-finding gate, tutorial, attendance | with its feature | GM | 8 | 68 | 45 | several small systems in one run |
| 21 | 32 | GM command session | with its feature | GM, 2 clients | 12 | 42 | 18 | only for the commands the rebuild keeps |
| 22 | 28 | Mini-house | with its feature | 2 clients, GM | 10 | 81 | 92 | log in again afterwards for the house load blocks; 35 needs it |
| 23 | 35 | Dice table, gamble house, card collection | with its feature | GM, mini-house | 10 | 83 | 140 | many uncaptured opcodes, but late content |
| 24 | 31 | Instance dungeon | with its feature | 2 clients (party), GM | 10 | 34 | 34 | needs party first |
| 25 | 30 | Kingdom quest | with its feature | 2 clients, GM, SHN / schedule setup | 20 | 94 | 93 | longest setup; only the WM minute skips are captured |
| 26 | 29 | Wedding | with its feature | 2 clients, GM | 15 | 50 | 44 | late content |
| 27 | 44 | Holy promise (mentor and pupil) | with its feature | 2 clients, GM | 8 | 25 | 41 | late content |
| 28 | 33 | Prison | with its feature | GM, 2 clients | 8 | 16 | 17 | late content, small |
| 29 | 41 | Test client: crafted client packets | optional | test client | 15 | 85 | 34 | how the original reacts to bad input: validation rules, not features |
| 30 | 42 | Races: drop menu, two money pick-ups, link with a dead WM session | optional | 2 clients | 10 | 15 | 5 | original race behaviour; the rebuild designs its own locking |
| 31 | 43 | OPTool listener (test tool) | optional | test tool | 15 | 60 | 59 | only if the original OPTool must work |
| 32 | 49 | Items V: refusals by the Character server | optional | DB setup per step, a second client or drops | 25 | 37 | 13 | DB faults the rebuild's own persistence does not have |
| 33 | 47 | Items IV: the zone and the DB disagree | optional | GM, DB / table setup per step, 2 clients for step 6 | 25 | 23 | 11 | every step tampers with the DB or tables under an online player |
| – | 48 | WM stop and start with its log | dropped (original processes only) | server PC only | 10 | 0 | 0 | the WM's own stop cause and log |
| – | 50 | Timing with one clock and without delayed ACKs | dropped (original processes only) | capture on the server PC, a registry change | 15 | 0 | 0 | timing between the original processes |
| – | 14 | Second client in sight *(recorded, batch 3)* | recorded | 2 clients | 5 | 47 | 25 | continued by 45 |
| – | 21 | Items II: drop, split, storage, use, shop *(recorded, batch 3)* | recorded | GM | 10 | 131 | 90 | continued by 46, 47, 49 |
| – | 24 | Skills, abstates, stat points *(recorded, batch 4)* | recorded | GM, 2 clients for revive | 10 | 61 | 38 | continued by 51 (refusals the client pre-empted: T23, T24, T25 in 41) |
| – | 38 | Session loss, kicks, back to character select *(recorded, batch 4)* | recorded | GM, 2 clients, process kill | 10 | 20 | 13 | continued by 52 |
<!-- ORDER:end -->

Sessions that fit together (same setup): **I** one client, GM (51 needs a second one for steps 2 and 4): 51, 46, 22, 23, 27, 40, 26, 25, 34, 32 (37, 21 and 24
are recorded; 37's steps 3–6 with S10, S11, X6 where `s37` did not reach them, see its result line; 51's step 4
needs B for a few minutes, step 2 B or `&sethp` for 25 minutes, steps 6–7 S21; about 80 minutes in all).
**II** two clients: 45, 17, 15, 16, 36, 44, 18, 19, 20, 39 (14 is recorded). **III** content with a longer setup:
28, 35, 29, 31, 30, 33, 52 (38 is recorded; 52 needs S20 and a zone restart). **IV** tools: 42, 41 (T15–T25 with
the others), 43. **V** DB and table setups under an
online owner, one short capture per step, the SQL window open next to the client (added by X05): 47, 49.
**VI** server PC only (added by X05): 48, 50.

## 3. Scenarios

### 14. Second client in sight

- **Claims:** Z02 §2 movement relays, §4 emotes, §5 sight and brief info (`0x1C01`, `0x1C06`, `0x1C07`: in no
  capture), §3.2 shout, W04 §2.1 whisper, Z03 §3 `SOMEONE…` attack packets; Z11 §3.1 `&hide` / `&show` /
  `&dimension` (re-check V24).
- **Setup:** A (GM) and B stand out of sight of each other on one map, then B walks to A.
- **Steps:** (1) B walks into A's sight. (2) B switches the client to walking (its walk / run toggle), walks a
  few steps, switches back and runs, jumps, uses the action "Sit" (`ActionViewInfo` 6), then "Stand" (7), then
  changes the combat stance. (3) B plays an emote, then moves while it plays. (4) A shouts with B in sight; B runs
  out of A's sight on the same map (more than `MapInfo.Sight`, 1600 in RouN) and A shouts again; B whispers A; A
  whispers with a name no character has (`X14Nobody`) as the **receiver** of the whisper, any text. (5) B attacks a
  mob next to A with a swing and one skill. (6) A types `&hide`, `&show`, `&dimension 1`, `&dimension 0`; after
  each command both stand still for 10 s, then **B alone** takes a step, 10 s later **A alone** takes a step, and
  the notes say after whose step the other one reappeared. (7) B walks out of sight.
  *(Steps 2, 4 and 6 reworded by X05: in `s14` B only ran and never sat, the shout was never out of sight, the
  unknown name went into the whisper's text, and the notes could not tell whose step brought A back,
  capture-validation §13.)* The shouter must have the shout level (a level-1 character is refused without a packet,
  capture-validation §18.4): A shouts, not a new B.
- **Prediction:** (1) Z→A `0x1C06 NC_BRIEFINFO_LOGINCHARACTER_CMD` for B's handle (and Z→B for A); if a client
  meets an unknown handle first it asks with `0x1C01 {nMyHnd, …}` and gets the brief info packet of that object
  (Z02 §5.1). (2) B's `0x2003` → A `0x2004`; `0x2005` → `0x2006`; `0x2024` → `0x2025`; sit / stand → A `0x2009
  NC_ACT_SOMEONECHANGEMODE_CMD`. (3) `0x2020` → A `0x2021`; when the client stops the emote it sends `0x2022 {emoticonid,
  emoticonframe}` → A `0x2023` (Z02 §4). (4) `0x201E` →
  `0x201F` to every client of the map instance, also out of sight (README §3.16); whisper C→W `0x200C` → target
  `0x200D`, sender `0x200F`, W→sender's zone `0x6006`; unknown name → sender `0x200E`. (5) A receives the
  `SOMEONE` forms (`0x2449`, `0x242E`, `0x2438`, `0x244F`) while B receives the own-attack forms captured before
  (Z03 §3, §5). (6) `&hide`: abstate inform for STA_GMHIDEMODE and B loses A (removal packet of Z02 §5);
  `&show`: abstate reset, **no appear broadcast from the command itself** (V24): B sees A again only through the
  next sight update; `&dimension 1`: A disappears for B and stays so; `&dimension 0`: A is **not** shown to B
  again until A changes map (the command does not re-enter the map, V24).
- **Disproved by:** a shout that stops at sight range; a `0x1C07` where we expect `0x1C06`; B seeing A right
  after `&dimension 0`; a `0x200F` for the unknown name.
- **Result (P02 batch 3, `s14`, capture-validation §18):**
  (1) **confirmed**: `0x1C06` both ways when B came within 1600 units, each followed by the other's abstate list
  `0x1C19`; 18 × `0x1C01` each answered by the appear packet and the last move (§18.2). `0x1C07` is not in `s14`
  (nobody in sight at a map login); `s21` has it at B's map login, `0x1C06` for the one already there (§18.2).
  (2) **run, jump, stance confirmed; the move opcodes of the prediction are wrong**: the client sends `0x2019` →
  others `0x201A`, stop `0x2012` → `0x2013` (Z02 §2.2); no `0x2003` … `0x2006` is in the capture. `0x2024` → A
  `0x2025` (only in sight), `0x2008 {2}` → A `0x2009` (§18.3). **Stand disproved as predicted**: it is the emote
  `0x2020 {7}` → `0x2021`, not `0x2009`. **Not reached**: a walk (`0x2017` → `0x2018` from a player) and the sit
  (`0x2020 {6}` *(inferred from the stand)*).
  (3) **confirmed** for `0x2020` → `0x2021` (7 emotes; also echoed to B itself); `0x2022` / `0x2023` **not reached**
  (the client never sent a stop) (§18.3).
  (4) **shout confirmed in sight only**: A's `0x201E` → `0x201F` to A and B; B (level 1) got nothing for its own
  shout; out of sight **not reached**. **Whisper confirmed**: WM `0x200D` to the target, `0x200F` to the sender,
  `0x6006` to the sender's zone, one WM pass. `0x200E` **not reached** (the whisper went to X14B with the text
  "X14Nobody") (§18.4).
  (5) **confirmed** for `0x2449` and `0x244F` (A only; B got its own forms); `0x242E` / `0x2438` **not reached** (no
  other skill path was used) (§18.5).
  (6) **confirmed** on all four counts: `&hide` → A `0x242A` (STA_GMHIDEMODE), B `0x1805`; `&show` → `0x2428` to
  both and no appear packet (B got A back through `0x1C01` after **A's** step); `&dimension 1` → B `0x1805`;
  `&dimension 0` → nothing for B, also after B's step (§18.6). Not predicted: the appear + delete storm while the
  layers differ (P02-B27) and the values −1 / 70000 being accepted.
  (7) not recorded (the capture ends before it). None of the "Disproved by" events occurred; the first and the last
  of them were not reached.
- **Open after batch 3 (X05):** every "not reached" above is a step of **scenario 45** (walk, sit, emote stop, shout
  out of sight, unknown receiver, `0x242E`, `0x2438`, leaving sight); `0x2022` by a crafted packet is T19 of
  scenario 41. Scenario 14 itself needs no second recording.

### 15. Party across two zones

- **Claims:** W02 §2 (invite, accept, leave, kick, master), §4.1 map-login refresh and party-release maps
  (re-check W7), §8 zone broadcasts; Z08 §1.2–§1.3 zone mirror and status packets; W04 §2.3 party chat; W02 has
  no capture at all.
- **Setup:** A and B on one zone, no party. Find a party-release map with X2.
- **Steps:** (1) A invites B; B refuses. (2) A invites again; B accepts. (3) Both say something in party chat.
  (4) B walks through a gate to another zone and back. (5) A hands the master role to B. (6) B logs out and in
  again. (7) B kicks A. (8) Form the party again and walk A into a party-release map.
- **Prediction:** (1) C→W `0x3802 {target}`, W→B `0x3803 {mastername}`, B→W `0x3805` (no payload); what A receives
  is W02 §2.3's answer. (2) `0x3804` → W→all Z `0x3801 NC_PARTY_FUNDAMENTAL_CMD`, members `0x3807 {name,
  class, 0x4C1}`, B `0x3809` member list; each client then sends Z `0x3848` and gets `0x3832` / `0x3833` /
  `0x3849` for members **on its own zone only** (README §3.17 a). (3) C→W `0x2014` → both `0x2015`, sender
  `0x2016`, W→sender's Z `0x6006`. (4) the map change of README §3.11, then on W `0x180C`: member list, all Z
  `0x383C`, members `0x383D`; while B is on the other zone A gets no `0x3833` for B. (5) `0x382A` (W02 §2;
  Z08 §1.3). (6) logout: all Z `0x3846`, A `0x3847`; with only A online the party is **released**: all Z `0x381F`,
  A `0x381E` (README §3.17 c: ≤ 1 member online). (7) with three members: `0x3814` → all Z `0x3816`; with two the
  kick dissolves the party (`0x381F` / `0x381E`). (8) on W `0x180C` with `IsPartyRelease = 1` (offset 0x2e, W7)
  the WM makes A leave: all Z `0x380C`, `0x380B`, and the party of two dissolves.
- **Disproved by:** the party surviving step 6 with one member online; status packets for a member on another
  zone; `0x180C +0x2e` = 0 on the release map while the party still ends (then the map test
  `IsInPartyReleaseMap` is the cause, W7 says either).

### 16. Raid

- **Claims:** W02 §5 (all raid requests), §6 map login / logout, §8; Z08 §2; Z14 §5.2–§5.3 raid status packets.
- **Setup:** A is master of a party with B (scenario 15 step 2). A third account C makes the invitation step
  real; without it use steps 1, 4, 5 only.
- **Steps:** (1) A makes the raid. (2) A invites C; C accepts. (3) A moves B to another slot, makes B a
  sub-leader, changes the looter. (4) B changes map. (5) B leaves; A dismisses the raid.
- **Prediction:** (1) C→W `0xB001` → A `0xB002`, members `0xB003`, all Z `0xB004 NC_RAID_ZONE_MAKE_CMD`.
  (2) `0xB00C` → invitee; `0xB00F` → inviter `0xB011`, members `0xB012`, all Z `0xB013`. (3) requests in
  `0xB014`…`0xB03A`, zone broadcasts `0xB02A`, `0xB02F`, `0xB034`, `0xB039`, `0xB03E` (W02 §5.6–§5.11).
  (4) on W `0x180C`: all Z `0xB01D`. (5) leave: all Z `0xB017`; dismiss: all Z `0xB007` (README §3.18).
- **Disproved by:** a raid request answered on another opcode than its W02 § gives; no `0xB004` to a zone that
  holds no member (the broadcast is to all zones).

### 17. Friends and character titles

- **Claims:** W04 §5.2–§5.6 friends, §7 titles; Z08 §6, §7.2; D04 §3; the friend-point item path (`0x34BF` /
  `0x34C0`, Z05).
- **Steps:** (1) A sends B a friend request; B refuses. (2) again; B accepts. (3) B changes map, levels up
  (`&levelup` needs B as GM, else kill mobs), logs out and in. (4) A deletes B from the list. (5) A opens the
  title window and picks another title.
- **Prediction:** (1) C→W `0x5401` → A `0x5402`, B `0x5403`; refusal → A `0x540B`. (2) B→W `0x5404` → D `0x5410`
  → W `0x5411` → both `0x5408 NC_FRIEND_ADD_CMD`, both zones `0x6007 NC_CT_ADD_FRIEND_CMD`, `0x5402`. (3) map
  login → A `0x540D`; level → A `0x540F` (from Z→W `0x1074`); logout → `0x540A`; login → `0x5409`, B's own list
  `0x5407`, W→D `0x5414` (README §3.22). (4), (5): W04 §5.4, §7.
- **Disproved by:** `0x5408` before the DB answer `0x5411`; a `0x6007` to one zone only.

### 18. Guild life cycle and guild storage

- **Claims:** W03 §2 (make, invite, join, leave, kick, grade, notice), §3.6 chat, §4 session hooks, §9.5 storage
  grade, §10 zone mirror; Z08 §8; Z05 §7.2; D04 §6; D03 §5.2. W03 has no capture (63 sections medium or low).
- **Setup:** A level ≥ 20 with the guild fee (`&levelup`, `&getmoney`), B without a guild.
- **Steps:** (1) A creates a guild; repeat with a name that exists (second GM character) for the refusal.
  (2) A invites B; B refuses; again; B accepts. (3) guild chat from both. (4) A changes the notice and B's
  grade. (5) A opens the guild storage, deposits an item, B withdraws it (if the grade allows; else note the
  refusal). (6) B logs out and in. (7) A kicks B; invite again; B leaves. (8) A dismisses the guild.
- **Prediction:** (1) C→W `0x7405` → D `0x7458` → W `0x7459` → C `0x7406`, members `0x7436`, all Z `0x7448`
  (README §3.19); item and money refusals come from the Character server's answer. (2) `0x7409` → invitee;
  `0x740C` → D `0x7469` → W `0x746A` → members `0x7436`, all Z `0x744A`; a refused invitation is **not** reported
  to the inviter. (3) C→W `0x7473` → online members. (4) notice `0x7410`, grade `0x7416` (W03 §2.8, §2.9).
  (5) C→Z `0x7491` → D `0x3471` → Z `0x3473` → C `0x7492`, and in parallel Z→W `0x749E` → Z `0x749F`; withdraw
  C→Z `0x3026` → D `0x3474` → Z `0x3475` → C `0x3027`, ring `0x7493`, members on the origin zone and the next
  ring zone `0x7494` (not further: Z14-B10). (6) W03 §4 hooks on W `0x180C` / logout. (7) kick `0x740E` → D
  `0x7471` → W `0x7472`; leave `0x741C` → D `0x746B` → W `0x746C`; all Z `0x744B`. (8) `0x7407` → D; the zones
  get `0x7449` when the DB executes the deletion (W03 §2.3, §9.2: possibly not at once; note the time).
- **Disproved by:** a message to the inviter on B's refusal; `0x7494` reaching a guild member on a third zone;
  `0x7449` in the same second as `0x7407` if W03 §2.3 says the deletion is delayed.

### 19. Guild academy

- **Claims:** W03 §5–§6, Z08 §10, Z14 §4, D04 §9, D07; re-check E18 (`0x980D`).
- **Setup:** the guild of scenario 18 before step 8; B without a guild, level below the academy limit.
- **Steps:** (1) B opens the academy list and joins A's academy. (2) academy chat / notice by A. (3) B opens the
  academy member list. (4) B gains levels (`&levelup 1` three times). (5) A opens the academy reward storage,
  puts in an item, B takes it. (6) A takes B from the academy into the guild. (7) alternative end: B leaves.
- **Prediction:** (1)–(2) dept 38 requests → D → W → members, all Z `0x9876` / `0x9877` (README §3.20).
  (3) `0x980D` → `0x980E` with the list (B has an academy and no guild: the handler does not close, E18).
  (4) each `0x1074` → academy points and level-up records W ↔ D (`0x9855`), all Z `0x987A` / `0x987B`; D07
  reward items. (5) C→Z → D `0x3483`…`0x3488`, grade Z→W `0x9870` → `0x9871`, other zones by ring `0x9872`,
  `0x9874`. (6) `0x740C` → D `0x982F` → W `0x9830` → all Z `0x9879`, members `0x982E` (the 2016 client ignores
  it).
- **Disproved by:** a guild-join that uses `0x7469` for an academy member; `0x980E` with zeros for a member.

### 20. Trade and booth

- **Claims:** Z06 §1 trade (35 `NC_TRADE_*` opcodes, none captured), §2 booth (re-check V9); Z05 §9.10–§9.11;
  D03 §14 and `docs/knowledge/D03.md` checks 6 and 7; bug Z06-B15 (complete before the DB answer).
- **Setup:** A and B next to each other; A holds a stack of 10, a weapon and money; B has free cells.
- **Steps:** (1) A asks B to trade; B refuses. (2) again, accepted: A puts up the weapon and 100 money, B
  nothing; A takes the weapon off the board and puts it back; both lock and decide. (3) A starts a trade and
  walks away. (4) A opens a sell booth with the stack at a price; B visits, buys 3, then the remaining 7.
  (5) B opens a buy booth for the same item; A sells into it. (6) B tries to buy from A's booth with too little
  money (set B's money with S2).
- **Prediction:** (2) dept 19 requests zone-only (Z06 §1.2–§1.3); on the second `0x4C1F NC_TRADE_DECIDE_REQ`
  both clients get `0x4C24 NC_TRADE_TRADECOMPLETE_CMD` **before** Z→D `0x343B`; then D→Z `0x343D` per partner,
  cell changes `0x3001`, money `0x1033`; G `0x0460` / `0x0461` / `0x044A`. (3) the next board request finds the partner too
  far: `sp_tradebreak`, the cancel packets of Z06 §1 to both. (4) C→Z `0x680D` → D `0x3455` (split, 3 of 10) then `0x3453` (whole stack) →
  Z `0x3456 {nLotTraded = 0}`; the owner gets `0x680F`; **the buyer gets no `0x680E {0xA41}`** (V9: success is
  shown by the item arriving). (5) the same three DB requests from the buy-booth side (`StreetBoothBuy::sb_Trade`, Z06 §2.5).
  (6) buyer `0x680E` with the money code of Z06 §2.5 (one of 0xA42…0xA59).
- **Disproved by:** `0x343B` before `0x4C24`; a `0x680E {0xA41}`; a non-zero `nLotTraded`.
- **With a DB setup (separate run):** S15 (§8.16), one booth purchase whose money move fails at the DB; its
  prediction and what disproves it are in that section.

### 21. Items II: drop, split, storage, use, shop

- **Claims:** Z04 §2 (repurchase, capsule and item-money shops), §3 (drop, destroy, pick: re-checks Q23, E37),
  §4.2 split (V5), §5.2–§5.3 ring and minimon equip, §6 use, §7 storage, §12, §13 soul stones; Z05 §2–§6 and
  §10 (V4); D03 §1–§7. The shop capture covered buy, sell, equip and the storage open only.
- **Setup:** `&makeitem` a stackable consumable (lot 10), a second stack of the same item (lot 3), a ring, a
  non-stackable item; a filled inventory for step 7 (`&makeitem` until `0x3402` stops coming; silent when full).
  The server-side scripts are `tools/capture/21` (`21-server.ps1 <action> -Char <name>`): `-Char` is the character
  that plays the run, named once and printed at the top of every output *(X05: in batch 3 the snapshots and the
  S13 / S16 runs were made for another character than the one played, capture-validation §19.8, §21)*. Step 12's
  three runs must name the character that logs in for them.
- **Steps:** (1) split 4 off the stack into a free cell; merge them back; split onto the lot-3 stack. (2) drop
  the lot-3 stack; pick it up. (3) drop the non-stackable item; pick it up with B if a second client runs
  (else skip). (4) destroy an item (drag out + confirm destroy). (5) use one consumable; use the last one of a
  stack. (6) equip the ring, then a second ring. (7) with a full inventory: unequip the ring. (8) storage:
  deposit a stack, change the page, withdraw; deposit and withdraw money. (9) sell an item to an NPC and buy it
  back from the repurchase list. (10) buy HP and SP soul stones; use both; use one at full HP. (11) pick-up
  over a kingdom-quest item's `PickupLimit` (`KQItem.shn`, 2016 data: `KQ_InvincibleHammer` and `KQ_Ice01`, both
  1): hold one, pick up a second. Try `&makeitem KQ_Ice01` twice and drop one (whether `&makeitem` and the drop
  accept these items was not read; if not, do it inside the kingdom quest that hands them out, scenario 30).
  (12) separate runs with a changed table or DB: X3's over-full stack (§9.4), one NPC purchase with S16 installed
  (§8.17), and S13's expired item, two minutes after login (§8.14).
- **Prediction:** (1) C→Z `0x300D` → D `0x3434` → Z `0x3435` → C cell changes; merge `0x342E` → `0x342F`;
  split-and-merge `0x3431` → `0x3432`; refusals come as `0x300E {0x442…0x44C}` (a split of 0 or of the whole
  lot: `{0x442}`), and whether a success sends `0x300E` too is for the capture to show (Z04 §4.2 lists refusal
  codes only). (2) `0x3007` → D `0x3416
  DROPALL` → `0x3417` → `0x3008 {0x301}` and the ground object (created in the success answer, V2); pick
  `0x3009` → D `0x341C` (or `0x341F` when it merges) → `0x300A`. (3) B's pick-up as (2) on B's links; whether `0x301B
  NC_ITEM_PICKOTHER_ACK` appears is Z04 §3.3's rule. (4) D `0x346A NC_ITEMDB_ITEMBREAK_REQ` → `0x346B` (Z04 §3.2).
  (5) `0x3015` → D `0x343E USELOT` (lot > 1) or `0x343F USEALL` (last one) → `0x3440` → C `0x3016 {0x700}`;
  others in sight `0x3029` (Z05 §6.1). (6) `0x3010 NC_ITEM_RINGEQUIP_REQ` → the equip round trip of Z04 §5.1 (D `0x3410` → `0x3411`, C `0x3011`); the
  second ring goes to the other ring slot (Z04 §5.2).
  (7) `0x3012` → `0x3013 {0x2C2}` or `{0x2C4}`, never 0x2C1; client text "Failed to unequip the item." (V4).
  (8) `0x301C` → D `0x345F` → `0x3460` → `0x301D`; `0x3028` page; `0x301E` → D `0x3461` → `0x3462` → `0x301F`;
  storage rows `nStorageType = 6`, `nOwner = userNo` (D03 check 3). (9) `0x305B NC_ITEM_SELL_ITEM_LIST_CMD`
  after the sale; `0x3059` → D `0x34B9` / `0x34BB` → `0x305A`, `0x305D`. (10) `0x5001` / `0x5002` → D `0x3441`
  → `0x3442` → `0x5003` / `0x5004`; use → others `0x500B` / `0x500C`; a refused use → `0x5006` (empty) (Z04 §13).
  (11) `0x300A {0x34A}` and the client text "Failed to obtain the item." (the generic text: the client has none
  of its own for 0x34A, X02-B8 / Q23; "Inventory is full." is 0x346 only). The refusal is
  `KQItemDataBox::kqidb_CanPickUp` @ FUN_0064bc90, called by `so_ply_PickupItem` @ FUN_0052faf0 with the lot
  already owned + the lot picked: item in `KQItem.shn`, `PickupLimit` ≠ 0, sum > limit. A stack over `MaxLot` is
  not this path. (12) X3: open, no prediction (§9.4); S16 and S13: the predictions of §8.17 and §8.14.
- **Disproved by:** a split refusal on another opcode than `0x300E`; the ground object appearing before `0x3417`; `0x3013
  {0x2C1}`; another text than "Failed to obtain the item." for 0x34A; 0x34A for an item that is not in `KQItem.shn`.
- **Result (P02 batch 3, `s21`, capture-validation §19–§20; the character was Test2):**
  (1) **confirmed**, and the open question answered: a successful split ends with `0x300E {0x441}` after the two
  `0x3001`; the merge (a `0x300B` move onto the stack) is `0x342E` → `0x342F` → `0x300C {0x241}`. Split onto the
  lot-3 stack: **refused** `0x300E {0x446}` without a DB request (3 ×), so `0x3431` / `0x3432` were **not reached**;
  `{0x442}` not reached either (the client offers 1 … lot − 1 only) (§19.3).
  (2) **confirmed**: `0x3416` → `0x3417` → ground object `0x1C0A` and `0x3008 {0x301}` (V2: the object comes after
  the answer). Not predicted: the confirmation menu `0x3C01` with a first `0x3008 {0x301}` before the DB request,
  and the cell emptied with the request. Pick-up onto the stack: `0x341F` → `0x3420` → `0x300A {0x341}`. A drop of
  part of a stack: `0x3008 {0x303}` (Z04-B4) (§19.4).
  (3) **confirmed** on B's links (`0x341C` → `0x341D` → `0x300A`), allowed 20 s after the drop (`looting`); no
  `0x301B`; the others in sight get `0x3014 NC_ITEM_SOMEONEPICK_CMD` (§19.4).
  (4) **confirmed** (`0x346A` → `0x346B`, two menus before it, `0x3024` after it) (§19.5).
  (5) **confirmed** for `0x343E` / `0x343F` → `0x3440` → `0x3016 {0x700}`, with `0x301A` before the DB answer. No
  `0x3029` reached B. A potion at full HP: `0x3016 {0x713}` without a DB request (§19.6).
  (6) **confirmed except the opcode**: the client sent `0x300F` for both rings, not `0x3010`; `0x3410` → `0x3411` →
  `0x3011 {0x281}`, the second ring in slot 16 (§19.7).
  (7) **confirmed**: `0x3013 {0x2C2}` and "Failed to unequip the item." (first `0x3013` on the wire) (§19.7).
  (8) **money confirmed** (`0x301C` → `0x345F` → `0x3460` → `0x301D`; `0x301E` → `0x3461` → `0x3462` → `0x301F`); the
  stack went in and out as a `0x300B` move (`0x3428` → `0x3429`). `0x3028` **not reached**: changing the page sends
  nothing, the four pages come at the open (§20.1). D03 check 3 not checked: the SQL snapshots list another character
  (§19.8).
  (9) **confirmed with another opcode**: every sale is followed by `0x305C` (one entry), never `0x305B`; buy-back
  `0x3059` → `0x34BB` → `0x34BC` → `0x305D`, `0x305A {0x3668}`, always onto the stack in cell 0. `0x34B9` (onto an
  empty cell) **not reached**. The stack of 3 the notes could not buy back was refused `0x305A {0x3671}` because
  another NPC had been clicked (P02-B31), not because it was a stack (§20.2).
  (10) **confirmed**: `0x5001` / `0x5002` → `0x3441` → `0x3442` → `0x5003` / `0x5004` (and `0x3004 {0x201}`); a use
  → B `0x500B` / `0x500C`. `0x5006` **not reached**: at full HP the client sends no `0x5007` (§20.3).
  (11) **confirmed**: `0x300A {0x34A}` without a DB request and "Failed to obtain the item."; a full inventory gives
  `0x300A {0x346}` "Inventory is full." (§19.4). `&makeitem` and the drop accept `KQ_Ice01`.
  (12) see the result lines of §8.17, §8.14 and §9.4 (run with Test1235). None of the "Disproved by" events occurred.
- **Open after batch 3 (X05):** **scenario 46** (no DB change: `0x3431` / `0x3432` by a drag onto a fuller stack,
  buy-back onto an empty cell `0x34B9` / `0x34BA`, the refusals `0x366B`–`0x366D` and `0x5005`, and the SQL
  snapshots for the character that plays); **scenario 47** (DB and table setups: `0x3424` / `0x3427`, `0x3443`,
  `0x366E`, S16 with fame or coins, X3's sell / use / move, S13 worn, ridden, used); test-client cases **T16–T18**
  of scenario 41 for what the 2016 client never sends (`0x3028`, a split of 0 or of the whole lot `{0x442}`,
  `0x5007` at full HP → `0x5006`, soul-stone numbers over the limit).

### 22. Upgrade, gems, random options, endurance

- **Claims:** Z04 §9 upgrades (all four requests and the roll §9.4), §10 gem sockets, §11 random options, §12
  endurance charge; Z05 §8; Z17 §4 costume weapon charges; `docs/knowledge/D03.md` checks 1, 2, 9.
- **Setup:** at an upgrade NPC: `&makeitem` a weapon, 20 upgrade stones of its tier, left / right protection
  stones, `&getmoney`. Note the weapon's `tItemOptions` rows.
- **Steps:** (1) upgrade until one success, one failure and (without protection) one downgrade or break are
  recorded. (2) one upgrade with left, right and middle stones. (3) boundary: an upgrade at the item's limit
  (`&makeitem … -u<max>`), and one with less money than the fee. (4) add a socket, add a gem, remove it.
  (5) change random options with an item; recover them. (6) charge a costume weapon's endurance.
- **Prediction:** (1) C→Z `0x3017 {equip, raw, raw_left, raw_right, gift_money, raw_middle}` → D `0x3447` with
  `change` ∈ {+1, +2, 0, −1, 100} and `destroyed` = 1 only with 100 (Z04 §9.1) → `0x3448` → C `0x3018 {err}`
  and `0x3001` for the weapon and every stone cell (each stone loses one). (3) at the limit `0x3018 {0x8CA}`,
  too little money `{0x8CB}`, both **without** a DB request. (4) `0x3044` → D `0x349A` → C `0x3045`; `0x3040` → D `0x3496` → C `0x3041`; `0x3042` → D `0x3498` → C `0x3043`
  (requests: Z04 §10; each DB answer is the request opcode + 1, Z05 §8). (5) `0x3053` → D `0x34B3` → C `0x3054`;
  recover `0x306B` → D `0x34CD` → C `0x306C`; `tItemOptions` types 503–519 change (D03 check 2). (6) `0x3035` →
  D `0x348D` (shield: `0x3064` → `0x34C6`) → C `0x3036`, `0x3037` (Z04 §12).
- **Disproved by:** a DB request on the two refusals of step 3; a `change` value outside the five; a stone
  cell that keeps its lot.

### 23. Quest: accept, kill, finish, give up; class change

- **Claims:** Z15 §3–§7 (script interpreter, diary, DONE round trip, codes), §5.8 worked trace; Z08 quest parts;
  D04 §1; `docs/knowledge/Z15.md`; Z07 class change (`0x1056`–`0x105A`, `0x305E`–`0x3060`).
- **Setup:** a new level-1 character (the first Roumen kill quest with an item reward), or S3 to put a chosen
  quest at its last step.
- **Steps:** (1) click the quest NPC, read the dialogue, accept. (2) kill the quest mobs one by one; pick up a
  quest drop if the quest has one. (3) relog in the middle. (4) return, choose a reward if offered, finish.
  (5) accept a second quest and give it up. (6) with S4 (level 20, class-change quest done): change class at
  the NPC.
- **Prediction:** (1) NPC click → Z→C `0x4401 NC_QUEST_SCRIPT_CMD_REQ {Cmd 2 SAY}`; each page C→Z `0x4402`;
  accept → D `0x4403 NC_QUEST_DB_SET_INFO_REQ` → `0x4404` → the diary record (Z15 §4, §6.1). (2) per kill one
  `0x440D NC_QUEST_NOTIFY_MOB_KILL_CMD {NumOfActionQuest, …}` for all quests the kill counts for (Z15 §6.2); we
  expect no DB message per kill *(inferred* from README §3.13: the diary is saved by `0x4005` in a full save*)*. (3) the zone save sends `0x4005`; at login the WM replays `0x1021` (doing), `0x10CD`
  (read), `0x10D6` (repeat). (4) as Z15 §5.8: `0x4401` / `0x4402`, Z→D `0x441A {NPCID, nQSC 10, QuestInfo
  (status 2), nMoney, nExp, lock, items}` → `0x441B {…, 0xB41}` → C `0x1033`, exp packets, `0x3001`, `0x4401
  {Cmd 10}`. (5) `0x4407` → D `0x4409` → `0x440A` → `0x4408`. (6) the class-change packets of Z07 (`0x1056`–`0x105A`; the WM cache gets `0x1058`, README §3.13).
- **Disproved by:** a DB write per kill; the reward arriving before `0x441B`; a result code other than 0xB41
  on success.

### 24. Skills, abstates, stat points

- **Claims:** Z03 §2 (assist), §5 skills (cast abort, field skills), §6 abstates (re-check C18: reset
  conditions), §7 revive, §9 learn / empower; Z23 §2 toggle skills, §4 empower; Z25; Z22; Z07 §2 stat points;
  Z12 recompute; D04 §2.
- **Setup:** A level 20+ with free stat and empower points (`&levelup 20` on a fresh character), money; a
  toggle skill and a buff with a movement reset condition (X4 lists the candidates from the misc-data table);
  B in sight for step 6, but out of the DoT mob's reach in steps 7–8 (in `s24` the Trumpy killed B unnoticed).
- **Steps:** (1) learn a skill at the skill master. (2) put 1 empower point into it; reset empower with the
  item if at hand. (3) add 3 stat points to one stat; remove one with a restat item (else note the refusal). Read
  WCmin / WCmax in the character window, not the STR total: the server sends no STR total for free points (`0x1035`
  without flag 0, capture-validation §24.4); the DB's STR column holds the free points (63 after three points, not 53).
  (4) start a long cast and move to abort it; cast a ground-target skill. (5) switch a toggle skill on, walk
  through a gate, switch it off. (6) take the buff, then walk / run / attack: one action per buff, noting which
  removes it. Assist: the 2016 client sends no `0x243E`; it sends `0x2401` with B's target once B attacks (§25.5),
  so note when A's target changes. Clear with `&resetabstate` (one word; `&resetabstated` is an invalid command,
  `0x2011`); it leaves the newbie states 730 / 732 behind (P02-B40). (7) get poisoned or burned by a mob (DOT).
  (8) die by the mob's hit, not by `&sethp 1`: the flat DoT stops at 1 HP and `&sethp 1` kills nothing (§25.7); B
  casts the revive skill **once**; A takes "Revival" in the death menu (the 2016 client has no decline, so the
  `0x482B` refusal path is unreachable). Note every death, town revive and extra cast, also B's.
- **Prediction:** (1) `0x4801` → D → `0x4802` → C `0x4804` (Z03 §9). (2) `0x4811` → D `0x4812` → answer (Z23
  §4). (3) per point C→Z `0x105C {stat}` → D `0x10D1 {nMaxStat, nFreeStat[5] (target), nLockIndex, nItemNum 0}`
  → `0x10D2 {…, 0xAC1}` → C `0x105F {stat}`; the dedicated `0x105D` is never sent; a fourth point with none left
  → `0x1061 {0xAC2}` without a DB request (Z07 §2.2, §2.4). (4) abort C→Z `0x2444` → `0x2445`;
  field skill `0x2441` → `0x2450` / sight `0x2451`. (5) `0x245C NC_BAT_TOGGLESKILL_ON_CMD`; the link saves the
  abstate (`0x4007`) and the skill is **off** on the new map (`0x245D`, Z23 §2.4). (6) the abstate goes
  (`0x2428` / sight `0x1C18`) on exactly the action its `mdas_ResetCondition` names and on no other (C18).
  (7) `0x243C NC_BAT_DOTDAMAGE_CMD` per tick, `0x240E`. (8) dead player `0x4829` (empty; accept dialog), answer C→Z `0x482A`, sight `0x481F`; a refusal
  makes the zone send `0x482B`, which the client ignores (Z03 §7.3, Z03-B3).
- **Disproved by:** `0x105D` on the wire; a DB request for the refused fourth point; a buff that survives its
  reset action or falls to another one; a toggle skill still on after the link.
- **State after batch 4 (X07):** recorded as `s24` (`26_11_16_24_skills-abstates-stat-points`, capture-validation
  §24–§25); the notes form, the prep and the DB readings are next to it. Result below; what it left open:
  "Open after batch 4". (After batch 3 the scenario was not captured.)
- **Notes corrected (capture-validation §13, X07):** start / steps 1–3: "STR in the DB 53" is 63 in the `-db.txt`;
  "STR 593 (+63)" is no server value (no STR total for free points; WCmin / WCmax rose by 3, §24.4); the auto-arrange
  at 667.0 and the Damaged Mystery Vault opened at 1707.8 are missing (§24.8). Steps 4–8: step 6's
  "`&resetabstated`" was an invalid command (`0x2011` at 1574.1); step 8's "`&sethp 1` … A died" did not happen (HP
  1, no `0x104D`; the poison stopped, §25.7): A died 38 s later from a Trumpy swing; the second Revive cast is not
  on the wire (one cast at 1949.7, accepted 41 s later); B's death by the Trumpy (1741.2) and town revive (1914.4)
  are missing; assist sent no `0x243E` (§25.1, §25.5). The steps above carry these fixes.
- **Result (P02 batch 4, `s24`, capture-validation §24–§25):**
  (1) **confirmed** with the book use in front: `0x3015` → D `0x343F` → `0x3440 {0x700}` → D `0x4801 {skill 0,
  removeid 0xFFFF}` → `0x4802` (11 ms) → G `0x0432` → C `0x4804 {0, 0}` + `0x1035`; DB row `nSkillLevel 1` (§24.2).
  (2) **confirmed**: `0x4811` → D `0x4812` (40 bytes; 41 with a partly used scroll, `bUseItem 1`) → `0x4813 {0x881}` →
  C `0x4814 {skill, 0x881}` "Skill empower succeeded"; plus and minus carry the new totals; stale bytes in the request
  (P02-B37, no effect). The take-back without an item was refused by the client (no `0x4811`), so the server's 0x886
  is untested. The full reset capsule: D `0x9006` → `0x9008` → C `0x900D {49}`, no text (§24.3, §24.5).
  (3) **confirmed** per point: `0x105C {0}` → D `0x10D1 {130, [61|62|63, 67, 0, 0, 0], lock 0, 0 items}` →
  `0x10D2 {0xAC1}` → C `0x105F {0}` + `0x1035`; `0x105D` never on the wire. The fourth point's `0x1061 {0xAC2}`:
  **not reached**: the client counts the free points and sent nothing. Restat item: `0x1062` → `0x10D1` with
  `DecItemInfo` → `0x10D2` → G `0x0459` → C `0x1065 {0}`; full capsule `0x9005` → `0x9007` → `0x900C {130}`, MaxHP
  re-sent (§24.4, §24.5).
  (4) **confirmed with an addition**: `0x2444` → `0x2438 CASTCUT` to the sight including the caster, then
  `0x2445 {0x20E8}`, then `0x243D`; no cooldown (the second cast 12 s later was accepted). Field skill `0x2441` →
  `0x2450` + `0x2435`, sight `0x2451`; the warp adds a second `0x2450` (new index, x + 5) and `0x4828` (§25.2, §25.3).
  (5) **confirmed with a correction**: `0x245C` on the next tick, effect after `HitTime`; the link's CharDB burst
  carries `0x4007` with `abstatenum 0` (1236.110: the toggle states have `AbStateSaveType 0`, so nothing is saved),
  `0x245D` goes in the ms of `0x181B` without a `0x2428` (`csl_Toggle_AllOff` removes nothing), and on the new map
  the toggle and its states are gone. Off by itself on weapon change and HP ≤ 5 %; at HP 100 the cast is refused with
  `0x2434 {0xFD5}`. Not predicted: two `0x2428` per removed state (P02-B38) and the 23-min icon `keepTime` of a
  37.4-h server state (P02-B39) (§25.4).
  (6) **confirmed** for StaNeglect (run / walk / attack), StaHide (attack / attacked) and StaBuckler (shield off):
  each state went on exactly its `AbStateReset` actions, one `0x2428` in the tick of the cause. "Attack" means an
  attack start (`0x242B`, a cast), not each swing; "attacked" includes a missed swing (§25.5).
  (7) **confirmed**: `0x243C {…, damage 200, abstate 179}` every 3.00 s to A and the sight, `0x240E` to A with each;
  29 ticks. Not predicted: the ticks stop at 1 HP (the flat DoT never kills) while the state stays (§25.7).
  (8) **confirmed**: A `0x4829` (empty) at the Revive effect; the client offers "Revival" in the death menu; A's
  `0x482A` → `0x481E {3836, 2029, 0}` to A, `0x481F {8003, …}` to the sight (the field holds the revived player).
  `0x482B`: **not reached** (no decline in the 2016 client). Not predicted: no experience loss on RouN
  (`ExpLostAtDeadByMob` 0, no `0x2411`) (§25.8).
  None of the "Disproved by" events occurred: no `0x105D`, no DB request for the refused fourth point (no request at
  all), no state outlived its reset action or fell to another one, the toggle was off after the link.
- **Open after batch 4 (X07):** scenario **51** (empower with two learned steps, Z23-B8; a toggle past its 23-min
  icon timer, P02-B39; a toggle with a lower learned step, Z23-B1; the skill-save columns against the DB; two
  consecutive auto-saves; the charged reset failures `0x9009` / `0x900A` with S21) and test-client cases **T23**
  (`0x4814` 0x882–0x889), **T24** (`0x1061` / `0x1067` 0xAC5–0xAC7; T10 has 0xAC2 / 0xAC3) and **T25** (`0x243E`,
  which no 2016 client path sends).
- **Run kit (2026-11-16):** notes form `re-data/captures/26_11_16_24_skills-abstates-stat-points.md` (the capture
  name; was `26_11_15_…`, blank). `tools/capture/24/24-server.ps1` runs on the server: `prep` (`24-prep.sql`: X24A
  → Gladiator 100 GM with 3 free stat points, money, skills 7300 toggle / 452 ground target; X24B → HighCleric 20
  GM with 1620 revive / 1800 cast; skills written to `tSkill` with `p_Skill_Set`, so no `&learnskill` on the wire;
  tutorial marked done; both at Skill Master Ruby), `capture-start` (dumpcap), `snapshot` (stats / skill rows),
  `cleanup` (`p_Char_Delete` on both; with `-Dest` it ends with `collect`, which copies the capture, `-prep.txt` and
  `-db.txt` next to the notes). The typing files `24-setupA/B.txt`, `24-items.txt`, `24-moveA/B.txt`,
  `24-step7.txt` go through `gmtype.ps1`. The two characters are still created in the client: the Character
  server's create writes items, skills, quests, shortcuts and the tutorial row (D02 §3), which SQL would only copy.

### 25. Pet

- **Claims:** Z13 §5–§6 (summon state machine, naming, tendency, re-summon), Z07 §9, D03 §13 (pet procedures,
  no source: check 10); re-checks P1 (`0xD411` on destroy) and Q11 (tendency, no animation).
- **Setup:** `&makeitem` a pet item (class 36); a gathering spot nearby; A is GM (`&getpetinfo`).
- **Steps:** (1) use the pet item (first summon); name the pet. (2) `&getpetinfo`; play an emote; gather once;
  `&getpetinfo` again. (3) walk through a gate to another zone with the pet out. (4) try to destroy the pet
  item while the pet is out. (5) use the item again (unsummon); relog; summon again.
- **Prediction:** (1) cast, then Z→D `0xD40D NC_PET_CREATE_DB_REQ` → `0xD40E` (RegNum) → `0xD40B` → `0xD40C`,
  sight `0x1C1C`; naming prompt `0xD405` → C `0xD407` → D `0xD403` → `0xD404` (Z13 §5.2, §5.5). (2) the two
  `0x2011` answers differ in stress / mind by the `TendencyModifyData` amounts for `PFC_S_DANCE` and
  `PFC_S_GATHER`; **no pet packet** is sent by the emote or the gather (Q11). (3) ZA→W `0x4033 {nCharNo,
  bDoResummon 1, xResummonCode = charNo + 0x1BEC48797BAFC8B0, nSummonSlot, nId, nRegNum}`; ZB gets `0xD412`, and
  after `0x1803` sends D `0xD40B` → `0xD40C`, no name prompt (Z13 §5.8; the captures hold `bDoResummon 0`
  only). (4) `0xD411 NC_PET_USE_ITEM_FAIL_ACK`, no `0x346A` (P1). (5) second summon: `0xD40B` only, no `0xD40D`.
- **Disproved by:** an animation packet tied to step 2; `0xD40D` on a re-summon; an item-break request in
  step 4.

### 26. Mounts and minimon

- **Claims:** Z13 §7–§9, Z07 §4, §8; Z02 §9. The captures hold one ride (Wooden Horse) without feeding.
- **Steps:** (1) ride on, wait for the hunger message, feed, ride off. (2) get hit by a mob while mounted.
  (3) equip a minimon (`0x3050`), switch the normal and the charged auto-use slots on and off; let HP drop below
  the threshold so that it uses a potion.
- **Prediction:** (1) `0xCC01` / `0x203F`, sight `0x2040`; `0x2046 NC_ACT_RIDE_HUNGRY_CMD`; `0x2044` feed;
  `0x2042` / sight `0x2043` (Z13 §7). (2) the dismount rule of Z13 §7 (`0x2041` on a refused ride). (3) C→Z
  `0x1124` / `0x1126` / `0x1128` / `0x112A` with their answers; the automatic use sends `0x112C` and the normal
  item-use packets (Z07 §4.1).
- **Disproved by:** an answer opcode other than the pair Z07 §4.1 gives for each request.

### 27. Wing stone and silver wing

- **Claims:** Z26 (all 20 sections: no silver wing in any capture); Z01 §7.2 wing save / fly (re-checks Q3,
  Q4, bug X02-B7); Z02 §6.6 server menu.
- **Setup:** `&makeitem` a sparrow wing, wing stones, a silver wing (item 2504 per Z26 §2).
- **Steps:** (1) save a location with the wing (`0x1814`); fly to it from another map (`0x1816`). (2) use the
  silver wing, choose "Save location". (3) go to another map; use it, choose "Fly", stand still to the cast
  end. (4) use it and cancel; use it, choose "Fly" and move during the cast. (5) use it on a map that forbids
  recall (a KQ or instance map, if reachable).
- **Prediction:** (1) `0x1814` → `0x1815` with 0x1141 … 0x1146 (Q3); `0x1816` → `0x1817`, cast, then `0x301A
  NC_ITEM_USECOMPLETE_CMD` (no body) and the map link (Q4). (2) `0x3015` → **no** `0x3016` yet → `0x3C01` menu;
  `0x3C02 {reply}` → D `0x3449 ITEMCHANGE_REQ`, C `0x3016 {0x700}`. (3) menu, then at the next routine tick the
  cool-down `0x4821`, at cast end `0x301A`, `0x3016 {0x700}`, then `0x1809` (same zone) or W `0x180D`; no
  `0x3029` to others (Z26 §2). (4) cancel → `0x3016 {0x700}`; moving during the cast: C→Z `0x3019 NC_ITEM_USEABORT_CMD`
  (Z04 §6.2) and the cast ends without `0x301A` and without a link (Z26 §3.2, §5.1). (5) `0x3016 {0x70F}` with `0x181D` and a `0x2011` notice.
- **Disproved by:** a `0x3016` straight after `0x3015`; a `0x3029` broadcast; a link without `0x301A`.

### 28. Mini-house

- **Claims:** Z07 §6 (60 uncaptured opcodes), Z13 §1–§3, Z05 §9.5 (re-check V3), D03 §8, Z02 §7 tents.
- **Setup:** A owns a mini-house item (`&makeitem`) and furniture; B next to A. For V3 the creation must fail:
  setup S5.
- **Steps:** (1) A pitches the tent (`0x2027`), folds it. (2) A activates the house (`0x8C01`), B sees it.
  (3) B visits from within 100 units, and once from further away. (4) A places a piece of furniture, moves it,
  removes it; uses a furniture emote. (5) A adds a portal, deletes it. (6) A changes the house settings, B gets
  thrown out; A closes the house. (7) with S5: A activates the house again.
- **Prediction:** (2) `0x8C01` → D `0x3467 NC_ITEMDB_CREATEMUSHROOM_REQ` → `0x3468` → build packets, sight
  `0x1C13` / `0x1C14` (Z13 §1). (3) `0x8C10` → the link into the house map (README §3.29); from too far: the
  refusal code of Z07 §6.5, no link. (4) `0x8C23` / `0x8C20` / `0x8C27` families with `0x8C21` to the visitors.
  (5) D dept 35 portal add / delete, answers `0x8C5A` family (Z07 §6.12). (7) D answers `0x3469`; **the client
  gets no packet at all** (V3).
- **Disproved by:** any client packet after `0x3469`; a visit accepted from beyond 100 units.

### 29. Wedding

- **Claims:** Z02 §10, Z07 §5 (status values with names of ours: re-check V13, not re-checked in code), Z13
  §4, D02 §11; Z11 §6.1 GM wedding commands.
- **Setup:** A and B, opposite gender, the wedding items of Z02 §10 (`&makeitem`); or the GM route:
  `&propose <B> <word>`, `&reserve`, `&enterready`, `&enter`, `&wedding` (Z11 §6.1) which run the same handlers.
- **Steps:** (1) A proposes to B; B refuses; again; B accepts. (2) reserve the hall; both enter; hold the
  ceremony with one guest if a third client exists. (3) relog both; A asks for partner info (`0x1093`) with B
  online on another zone, then with B offline. (4) A summons B (partner summon). (5) divorce by agreement:
  request, cancel, request, accept. (6) marry again (S6 resets the waiting time) and divorce by force.
- **Prediction:** (1) A→Z `0x204F NC_ACT_WEDDING_PROPOSEREQ_REQ` → Z→B `0x2050` → B→Z `0x2051` → Z→A `0x2052` (Z02 §10); on
  acceptance Z→D `0x1083` → `0x1084`;
  reload `0x1080` → `0x1082 NC_CHAR_WEDDINGDATA_CMD`; ring `0x10AB` to reload the partner on another zone.
  (2) `0x2053` → `0x2054`, G `0x065D`; entrance ring `0x2055`; `0x1091` → `0x1092`; G `0x065E`. (3) partner
  here or by ring `0x1095`; offline → D `0x1093` → Z `0x1094`, which the 2016 client has **no handler** for
  (README §3.29). (4) ring `0x10AA`. (5), (6) `0x1089`…`0x1090`, `0x205B`…`0x205E` (Z07 §5.2). After every step
  note `tMarriage` (S6 gives the SELECT): its `Main` / `Sub` values are what V13 needs named.
- **Disproved by:** a status value outside Z07 §5.1's table; a client reaction to `0x1094`.

### 30. Kingdom quest

- **Claims:** W04 §6 (schedule, lists, join, start), Z16 §2–§3 (element, entrance, reward; bugs Z16-B2, B4), Z09
  Lua layer (§14–§17, §24–§25: no scripted map in any capture), D04 §3 reward, Z15 Lua quest functions.
- **Setup:** X5 moves one `KingdomQuest.shn` row to start a few minutes after the server start with a minimum
  of 1–2 players. A and B on different zones. Shorter variant without the WM: `&kingdomquest <map> <script>`
  (Z11 §8.4: runs the script film only, no KQ element, no reward).
- **Steps:** (1) both open the KQ list; A joins, cancels, joins; B joins. (2) wait for the start; accept the
  entry prompt. (3) play to the end (or `&killallmob` as GM); note every script message and door. (4) collect
  the reward; get moved out. (5) second run: B is voted out (needs a third joiner) or leaves by logout.
- **Prediction:** WM→all Z `0x580D {PROTO_KQ_INFO}`; `0x580E {hquest, 0x981}` from the zone hosting the **last**
  listed map only (Z16-B2); C→W `0x581B` → list diffs `0x581C`…`0x581F`; `0x5805` → `0x5806`; cancel `0x5807` →
  all Z `0x583B`; countdown notice `0x580B`, `0x5825` each second for 10 s; W→all Z `0x580F {info, joiners}`;
  every zone links its own joiners at 0, 2, 5, 7, 10 s (G `0x0441`); C→Z `0x581A` links without a joiner check;
  during play `0x2079` script messages, `0x2082` / `0x2083` cinematics, mob and door packets (Z09 §14–§17); end
  Z→W `0x5810` → all Z `0x5811`; Z→D `0x5815 {fame, cen, item list}` → `0x5816` / `0x5817` (README §3.23).
- **Disproved by:** a `0x580E` from a zone that does not host the last map; a joiner on another zone who is not
  linked; a reward before `0x5816`.


- **Added by X05 (batch-2 leftover: revive to another map, capture-validation §9.5 / §15):** step (6) inside the
  running KQ, A dies to a mob and takes the death menu's revive. Claim: Z07 §3.1 `sp_ReviveReqProcess` @ FUN_00451bd0.
  On a normal field the revive target is the map's own regen point (`0x104F NC_CHAR_REVIVESAME_CMD`, captured in
  `combat`); only a KQ with a revive count (`kqe_ReviveNumber`) or a guild-tournament map
  (`fm_IsGuildTournametnMap` @ FUN_00475770) takes the other branch, whose target is the map's regen city or the
  KQ team point. Prediction: `0x104E` → `so_LinkTo(target, 4, 0x4F, 0x50)`: `0x104F` when the target is served by
  the same zone process, **`0x1050 NC_CHAR_REVIVEOTHER_CMD`** with the other zone's address when it is not *(inferred
  from the two opcode arguments, as `0x1809` / `0x180A` for a link)*; HP ≈ 30 % (`MaxHP × 307 / 1024`) after the
  map login; no `0x2411` *(inferred: Z03 §7.2 `sp_LostExperienceByKilled` returns 0 for a protected player and names the KQ
  as an example)*. Disproved by: a revive that stays on the KQ map after the revive count is used up.

### 31. Instance dungeon

- **Claims:** Z14 §1–§2, Z08 §5, W04 §13, Z09 instance scripts; bugs Z14-B8.
- **Setup:** A and B in a party at an instance gate (`&linkto`); a second gate hosted by another zone and a
  level-select gate (ModeIDGate) if the map list has them (X2 lists both).
- **Steps:** (1) enter through the gate; B follows. (2) both leave; wait 20 s; then A (leader) answers the
  "delete now" menu. (3) enter the level-select gate, choose a level. (4) dissolve the party while an instance
  exists.
- **Prediction:** (1) NPC menu → `so_LinkTo` (README §3.11); gate on another zone: ring `0xA404` first.
  (2) Z→W `0xA401` → members `0x0810 NC_MISC_RESTMINUTE_CMD {1, 300}`, all Z `0xA402`; "delete now" → ring
  `0x10B1`; players back → Z→W `0xA403` → members `0x0810 {1, 0}`. (3) Z→W `0xA408` → dest Z `0xA40A` → W
  `0xA40B` → origin `0xA409`; then `0xA40E` → `0xA410` → `0xA411` → `0xA40F` → link; client `0x182C
  NC_MAP_INDUN_LEVEL_VIEW_CMD`. (4) all Z `0x381F`: the instance is deleted on every zone (README §3.24).
- **Disproved by:** `0x0810` with other values than `{1, 300}` / `{1, 0}`; an instance that survives step 4.

### 32. GM command session

- **Claims:** Z11 (56 medium sections; only `&levelup` and `&linkto` are captured); Z01 §10 ring messages;
  re-checks C4 (`&captivate`), V25 (`&killallmob`), Z11-B15, B17, B31, B32.
- **Setup:** A = GM level 100 on zone 0; B on another zone; a quest with a kill count active on A (scenario 23
  step 1).
- **Steps, one command per line, 5 s apart:** `&pfind <B>`; `&psummon <B>`; `&distribute`; `&fieldbonus`;
  `&itembonus x 2000`; `&expbonus A 2000`; `&mobbreed <questMob> 3 10 n 5`; `&killallmob`; `&makeitem <item>`;
  `&cleariv`; `&getmoney 1000`; `&getmoney -1`; `&fullpoint`; `&immortal` (twice); `&captivate 1`, wait 10 s,
  `&captivate`; `&silence <B>` then B chats; `&HP`, `&SP`, `&gmtestmode` (arguments: Z11 §8.5); a GM chat colour change;
  `&speed 2000`, walk; `&kickout <B>` with B on A's zone, then with B on another zone.
- **Prediction:** `&pfind`: ring `0x1068` → `0x1069`, `0x2011` with the place, then A's map change to B.
  `&psummon`: ring `0x106A`, B's map change. `&expbonus A`: ring `0x1810` to every zone, **no effect on EXP**
  (Z11-B15); `&itembonus x`: local only, no ring. `&killallmob`: kill packets per mob with A as killer, drops,
  EXP and `0x440D` quest counts as for normal kills (V25, *(inferred)* until seen). `&getmoney -1`: money grows
  by 2³² − 1 (B31; D `0x3438`, `0x1033`), and the `0x300A` repeats the last pick message (B32). `&captivate 1`:
  `0x2011`, then A moves by mob AI without client input (C4). `&silence`: only the answer text; B's chat still
  arrives (B17). Chat colour: W `0x083D`. `&kickout` same zone: Z→W `0x0C1A {userNo, wmHandle, 0x68B}`, B `0x0C17
  {0x68B}`; other zone: ring `0x1068`, B is **not** kicked (Z11-B6).
- **Disproved by:** an EXP change after `&expbonus`; B silenced; B kicked across zones; no `0x440D` after
  `&killallmob` (then V25's "as for a kill" is wrong for quests).

### 33. Prison

- **Claims:** W04 §9, Z08 §12 (re-check V17), D04 §7, Z01 `EldPri` login; bugs W04-B24, B25, X01-B4.
- **Setup:** the GM request `0x7C01` needs the client's GM prison command if the 2016 client has one (C01), else
  the test client of scenario 41; the map-login path needs only S7 (prison minutes in the database).
- **Steps:** (1) S7 on B, B logs in. (2) B waits 3+ minutes; asks for the remaining time. (3) A changes the
  time, then releases B. (4) A imprisons B online (`0x7C01`), then an offline character by name.
- **Prediction:** (1) B's map login lands in `EldPri`; Z→C `0x7C05 {minutes·60}`; C→W `0x7C06` → D `0x7C0E` → W
  `0x7C0F` → C `0x7C07`. (2) W→D `0x7C0D` every 3 minutes; `0x7C04` answers with **milliseconds read as
  seconds** (W04-B24). (3) `0x7C09` → D `0x7C10` → W `0x7C11` → prisoner `0x7C03` or release, GM `0x7C0A`; the
  minutes and reason of the request are never copied (W04-B25); at 0: C `0x7C05 {0x0DA8}`, Z `0x7C12`.
  (4) W→B's Z `0x7C13` → Z→W `0x7C14 {…, err 0xDC0}` (0x178 bytes) → D `0x7C0B` → W `0x7C0C` → GM `0x7C02`;
  offline: D `0x7C0B` directly (README §3.27).
- **Disproved by:** a remaining time in step 2 that matches the wall clock; `0x7C14` shorter than 0x178 bytes.

### 34. Premium inventory, charged buffs

- **Claims:** Z04 §8, Z05 §7.4, D03 §5.4 and §9 (checks 5 and 13), W04 §11, Z08, Z24; bug D03-B10.
- **Setup:** S8 inserts charged-item rows for the test account (3 rows; then 600 rows for B10).
- **Steps:** (1) open the premium inventory; withdraw one item; use it if it is a buff item. (2) change map.
  (3) relog. (4) with 600 rows: open and page through the list.
- **Prediction:** (1) `0x3020` → D `0x3463` → `0x3464` → `0x3021`; `0x3022` → D `0x3465` → `0x3466` → `0x3023`,
  G `0x04BE`; the buff: Z→D and Z→W `0x9001 NC_CHARGED_SETBUFF_CMD`. (2) W→new Z `0x1032` with the buff. (3) the
  buff is in the login blocks (`0x101B` / `0x1032`). (4) at most 511 rows arrive (D03-B10).
- **Disproved by:** all 600 rows arriving; `0x9001` to one of the two receivers only.

### 35. Dice table, gamble house, card collection

- **Claims:** Z06 §3–§4 (re-checks V10, L6), D03 §10–§12 (check 9: procedures only in the 2017 backup), W04
  §15, Z07 §7, Z28; Z11 §6.7.
- **Setup:** a mini-house with a TaiSai table (scenario 28) or the gamble house map; coins (S9 or the exchange
  NPC); a card item (`&makeitem`). GM: `&ts_DiceFix 111` fixes the next throw.
- **Steps:** (1) join the table, bet, win once (`&ts_DiceFix`) and lose once. (2) bet, then click logout while
  the table is in the rolling state. (3) gamble house: exchange coins, play one slot game, leave. (4) register
  a card, bookmark it, claim a collection reward, claim it again.
- **Prediction:** (1) dept 43 requests and their DB round trips (Z06 §3); the 2016 zone has no handler for
  the manual roll `0xAC20` (V10): a table in manual mode never rolls on request. (2) the zone's logout is
  held back: `0x0C31` and the socket close come about 50 ticks later than in the idle capture (L6). (3) dept
  47 (Z06 §4), `0x10DC` / `0x10DD` coin info, D `usp_Gamble_addCoin` (check 8). (4) dept 49 (Z07 §7); the
  second claim → `0x2BA9`, no second item (check 9).
- **Disproved by:** a logout in step 2 with the idle timing; a second reward item.

### 36. Block list, reports, options, megaphone

- **Claims:** W04 §8 (options: `0x7001` family), §10 reports, §14 block list, §17.2 / §17.4 spam report and
  chat ban; D04 §5, §10; D01 §4; Z02 §9 megaphone.
- **Steps:** (1) A blocks B; B whispers A; A unblocks. (2) A reports B (each report kind the client offers).
  (3) A changes game options, key bindings and shortcuts, then relogs. (4) A uses a megaphone item. (5) A
  reports B as a gold spammer.
- **Prediction:** (1) dept 42 → D → W → C; B's whisper still reaches A's client (`0x200D`), which drops it
  itself (README §3.16). (2) C→W `0x8001` / `0x8003` / `0x8005` → AL `0x8007` / `0x8009` / `0x800B` → W
  `0x8008` / `0x800A` / `0x800C` → C `0x8002` / `0x8004` / `0x8006`. (3) nothing at the change; in the logout
  tick `0x7011`, `0x7015`, `0x7016`, `0x703B`, no answers (captured once); the next login pushes the saved
  values. (4) `0x204B` → `0x204C`, item use, the roar to the map (Z02 §9). (5) `0x085F` → `0x0860` (W04 §17.4).
- **Disproved by:** the WM dropping the blocked whisper; an answer to an option save.


- **Added by X05 (batch-2 leftover: the `0x7037` tail, capture-validation §4.2 / §14):** step (6) in one session
  drag **three** different skills or items onto empty quick-slot cells, then log out; in a second session change
  two cells and log out. Prediction: one `0x7037 NC_CHAR_OPTION_IMPROVE_SET_SHORTCUTDATA_REQ` per logout with
  `n` = the number of changed cells (the captured one had `n = 1` and 11 bytes = `1 + 7n + 3`). **Open, no
  prediction for the tail:** `n = 3` gives 25 bytes if the tail is a fixed 3 bytes and 31 if it is 3 per entry
  (`n = 2`: 18 or 21). Either way the WM drops the packet without an answer (W04 §8.2) and the next login's
  shortcut block is the Character server's (so the changed cells come back only if another packet saved them: note
  what the quick slots show after the relog). Disproved by: a size that is neither `1 + 7n + 3` nor `1 + 10n`; an
  answer from the WM. How the 2016 client builds the opcodes of its option saves (no `0x7037` / `0x7011` /
  `0x7015` / `0x703B` immediate in the client) is not a capture question: it stays a client-reading note in
  capture-validation §14.

### 37. Login side: idle heartbeat, refusals, character delete

- **Claims:** L01 §1.6 (hand-rated: the Login heartbeat never fired in a capture), L00 / L01 refusal codes,
  D01 §3–§4, W01 §4 (delete, rename), W05 §4.5; D02 §3.
- **Setup:** S10 (blocked account), S11 (account not login-able), X6 (world closed / full in the server config).
- **Steps:** (1) *(dropped by X05: the client opens the Login connection only when the login form is submitted,
  so an idle login screen holds no connection and tests nothing, capture-validation §16.2. The idle tests are steps
  2 and 6; a Login connection that stays silent needs the test client: scenario 41, T15.)* (2) log in, stay on the world
  list 70 s. (3) log in with the blocked account; with the not-login-able account. (4) select the closed world.
  (5) delete a character (wrong confirmation first if the client asks one), create one with the same name.
  (6) stay 4 minutes on the character list.
- **Prediction:** (1) *(needs a silent Login connection, which this client never has)* Login → C `0x0804` after 30 s
  without a received packet, C → `0x0805`; no close (L01 §1.6). (2) the client's own `0x0C1B` poll keeps the link alive: no `0x0804`. (3) `0x0C09 {0x47}` "The ID
  has been blocked."; `{0x48}` "The World Servers are down for maintenance."; AL `0x0720` / `0xC802` for both
  (README §3.15). (4) the world-select refusal of L01 with the world's status byte. (5) W ↔ D delete, G
  `0x0412` twice (W and D), `0xC805`; create: `0x0411`, `0xC804`. (6) WM heartbeat every 30 s; no close at
  30 + 180 s as long as the client answers (W05 §4.5).
- **Disproved by:** a close in step 1 or 6 while `0x0805` is answered; another code than 0x47 / 0x48.
- **Result (P02 batch 3, `s37`, capture-validation §16):**
  (1) **not reached**: nothing was sent to the Login port during the 70 s; in no capture did Login send `0x0804`
  (§16.2). L01 §1.6 stays hand-rated; the test is now T15 of scenario 41.
  (2) **confirmed**: `0x0C1B` every 10.0 s, no `0x0804` (§16.2).
  (3) **confirmed**: `0x0C09 {0x47}` and `{0x48}` with the two texts, AccountLog `0x0720` + `0xC802` for both
  (§16.1).
  (4) **closed world confirmed with a correction**: `0x0C0C {0}` and "Server is closed. Please try login later.",
  but the refusal also carries the WM address and unwritten `validate_new` bytes, not zeros (P02-B23, §16.3).
  **Full world (X6) confirmed to the byte**: `0x0C10`, `0x0721`, `0x0C0D` before `0x0C0C {5}` (§16.1).
  (5) **confirmed**: delete W → D `0x1413` → `0x1414` → `0x1408` → `0x140B`, GameLog `0x0412` twice (Character
  server first, WM 10 ms later), `0xC805`; create `0x0411`, `0xC804`. The client refuses a wrong confirmation without
  a packet. Not predicted: AccountDB `0x140D` / `0x140E`, `0x9424` → `0x9425`, `0x10B2` to every zone (§16.1).
  (6) **confirmed**: `0x0804` 30.0 s after the last client packet, 12 times in 7 minutes, no close (§16.2).
  None of the "Disproved by" events occurred.
- **Open after batch 3 (X05):** T15 of scenario 41 (the silent Login connection) and **scenario 48** (why the first
  WM start of `s37` ended, capture-validation §17.6: the WM's `Msg` log next to a stop / start).
- **Second run `s37b` (batch 4)**: the character-select paths `s37` did not reach (capture-validation §4.2 "never seen
  on the WM"). Run kit `tools/capture/37/37b-server.ps1` (`prep`: `X37Del` renamed to `X37-Ren` in the DB, an open
  `tCharacterChangeID` row for Test2; `stop-zones` / `start-zones`; `snapshot`; `cleanup`; `collect`), notes form
  `re-data/captures/26_11_16_37b_char-select-rename-refusals.md`. Steps as run: (b1) create a character with a name
  in use; one with a space. (b2) select the `-` character (the client opens the free rename itself): the old name,
  then a name in use, then a free name; start each time. (b3) the rename right of Test2: a name in use, then a free
  name; start. (b4) all zones stopped: start a character; zones back: start again; quit. **Fixed for a rerun (X07,
  capture-validation §13):** the `-` character must not be in tutorial state 0, or step b2's start meets P02-B33
  first ("The Map is under maintenance" from the tutorial skip, not from the rename; capture-validation §22.2): give it
  a tutorial row in state 2 in the prep (`37b-prep.sql` does it since the X07 review, `usp_Tutorial_setCharInfo` as
  in `24-prep.sql`), or create it in the same session. The test DB runs the private 2018
  `p_Char_Rename`, which answers 0xD0 without renaming; the 2016 behaviour needs the 2016 procedure on the test DB.
  Predictions (the form's "expected" lines and W01 §4 / §6.2): (b1) W → D `0x1402` → `0x1403 {0x181}` → C `0x1404
  {0x181}` "The name is already in use."; the space refused by the client. (b2) the old name refused by the client;
  W ↔ D `0x1411` / `0x1412`, C `0x1410`; a name in use fails with 0xD1 (2016 procedure). (b3) `0xB409` → D `0xB40A` →
  `0xB40B` → C `0xB40C`: 0x20D1 "The name is already taken by another user."; 0x20C0 "Character name successfully
  changed." with `0xB40F` to all Z. (b4) `0x1002 {0x145}` "The Map is under maintenance" without a CharDB round trip.
- **Result (P02 batch 4, `s37b`, capture-validation §22):**
  (b1) **confirmed**: `0x1401` → `0x1402` → `0x1403 {err 0x181}` → `0x1404 {0x181}` in 58 ms; the client's text is
  "The name is already in use. Please choose another"; "X37 Sp" refused by the client without a packet (§22.1).
  (b2) the old name: **confirmed** (client, no packet). The name in use: **not reached** for the 2016 procedure: the
  test DB's 2018 copy answered `0x1412 {0xD0}` without renaming, the WM stored the new name in its avatar copy, and the
  start failed at the map login on the name mismatch (`0x104B` → `0x104C {−1, −1}` → `0x0C1A {usrregnum 0, 0x689}`,
  "Disconnected"); this confirms W01 §4.1, §7.2, §5.2 and Z01 §5.3 (§22.3). The free name: the same 0xD0 path. The
  first start ended in "The Map is under maintenance" from the tutorial skip of a listed state-0 character
  (`0x1111` → `0x1112` / `0x1113` → `0x1002 {0x145}`, P02-B33; §22.2).
  (b3) the name in use: **disproved for the client**: `0xB40C {0x20D1, slot 7}` came back, but the slot byte is stack
  garbage and the client returns before the message: no text (P02-B34, §22.4). The free name: **confirmed**:
  `0xB40B {0x20C0}`, `0xB40F` to the four zone links 1 ms before `0xB40C`, "Character name successfully changed.", the
  row's `bFlag` 1.
  (b4) **confirmed**: `0x1002 {0x145}` 7 ms after `0x1001`, no CharDB round trip, the client stays on the list; after
  the restart `0x1003` in 671 ms (§22.1). Also seen: the WM's list copy patches the map of state-0 characters to "RouT"
  (W01 §3.3 corrected), and the quit gives four saves (StoreType 4, 7, 4, 9; P02-B35, §22.5).
- **Notes corrected (`s37b`, capture-validation §13, X07):** step 2's "Map under Maintenance" comes from the tutorial
  skip (P02-B33), not from the rename to "Test1235"; the disconnects come from the 2018 `p_Char_Rename` (0xD0 without a
  rename, so the WM's name and the DB's differ at the map login); step 3's silent refusal is P02-B34, not a success.
- **Open after batch 4 (X07):** scenario **52** steps 1 (a second `0x1001` with the stale "RouT" copy, P02-B33) and 2
  (the 2016 `p_Char_Rename` with S20: a duplicate → 0xD1).

### 38. Session loss, kicks, back to character select

- **Claims:** Z01 §8 (logout, kick, socket loss; re-checks L5, L6), W01 §5 and §7.3 (`0x0C31`, W8), W05 §4.5,
  Z09 §1.5, README §3.12 b, c, e; re-check E41 (money is saved only as deltas); bug X01-B3.
- **Setup:** A in game with a known money value; a tool that closes one TCP connection of the client (TCPView
  "Close Connection" or a firewall rule on the zone port only). Run kit: `tools/capture/38/38-server.ps1` (`prep`,
  `close-zone-conn`, `kill-client`, `kill-zone`, `getmoney-kill`, `snapshot`; at the end `collect -Dest <folder of
  the notes> -Pcap <capture>`).
- **Steps:** (1) return to character select with the menu's "character select" (the world-list button closes the WM
  session, `0x0C33`, capture-validation §23.2), select the same character again. (2) quit the game from inside and
  let the 10-s countdown run out; wait until the client has closed before step 3 (in `s38` this step is missing:
  the event at 292.5 is a `close-zone-conn`, §23.1). (3) close only the **zone** connection of the client; note what
  the client shows; log in again within 10 s. (4) kill the client process; log in again. (5) pick up 100 money (no
  mob of the 2016 data drops money: `&getmoney 100`, the same commit), wait for `0x3439`, then kill the **zone
  process** (no clean stop); restart, log in, read the money. (6) `&getmoney 500`, then the same kill within a second.
  Do each step once; write every extra try (a second step 1, a `&getmoney` or a kill not followed through) into the
  notes with its time.
- **Prediction:** (1) `0x0C18 {1}` to W and Z; the WM runs the character logout but keeps the session; the
  zone saves (dept 16), sends W `0x0C31 {…, wmHandle, charNo}`; the next `0x1001` is accepted only after it
  (W8). (2) as the captured logout without the token steps. (3) the zone's socket-close path sends **no**
  `0x0C31` (the flag is 0, L5); the WM session lives on; a new login of the account kicks it (`0x0C17 {0x683}`),
  and the new session has `playingCharNo = −1`, so `0x1001` is accepted. If instead the client returns to the
  character list on the same WM session, `0x1001` is refused with `0x1002 {0x145}`. (4) both sockets close: WM
  `Client_OnClosed` (AL `0x0722`, `0xC803`, zones `0x0C19`), zone save with reason 7. (5) the money is there:
  the pick-up was committed by `0x3438` → `0x3439`. (6) either all 500 or none, never a partial value; nothing
  else of the last 10 minutes is saved (auto save 600 s).
- **Disproved by:** a `0x0C31` in step 3; a money value in step 5 or 6 that is neither the committed sum nor
  the old value.
- **Result (P02 batch 4, `s38`, capture-validation §23):**
  (1) **confirmed** (778.8): `0x0C18 {1}` to Z and W in one ms, 10.0 s after `0x1071`; the zone saves once
  (StoreType 9) and sends `0x0C31 {10000, 2}` 3 ms later; the WM's `CharacterLogout` (`0x1037`, `0x081F`, `0xC807`)
  without `0x0C11`; `0x0C1F` → the list reloaded from CharDB → `0x1001` → in game 4.4 s after the quit (§23.2). The
  first try went to the world list (`0x0C33`): the WM closed the session and handed the client to the Login by OTP.
  (2) **not reached in `s38`**; the quits of `s37b` and `s24` show it (§22.5, §25.9): `0x0C18 {0}` to Z and W, `0x0C19`
  from the WM twice; four saves (StoreType 4, 7, 4, then 9 + `0x0C31` 13 s after `0x1071`) when the zone handles the
  WM's kick first (P02-B35), one save 9 + `0x0C31` when it handles the client's `0x0C18` first.
  (3) **confirmed**: no `0x0C31` (saves 4, 7, 4, then 3 by `sp_Schedule_Kickout` 9.9 s later, §23.3). **Disproved**:
  "the WM session lives on": the client itself sends `0x0C18 {0}` to the WM 14–27 ms after the zone socket's reset,
  closes everything and shows "Disconnected from the server." (§23.4), so the WM closes the session (`0x0C11 {0x780}`,
  `0x0C19` ×2). The new login's `0x0C17 {0x683}` kick and the `0x1002 {0x145}` on the same session are **not
  reachable** with the 2016 client; the new login only sends `0x0C16` kicks, which re-run `so_banning` (one more save 4).
  (4) **confirmed**: both sockets reset; `Client_OnClosed` 9 ms later (`0x0C11`, AL `0x0722`, `0xC803`, one `0x0C19`
  broadcast); zone saves 4 and 7; the pending `0x1071` timer then saved 9 with `0x0C31` (§23.7, §23.3).
  (5) **confirmed** (with `&getmoney 100`, see step 5): `0x3438` → `0x3439` in 15–22 ms, before the kill; the next
  login's blob and the DB hold the sum (…4824) (§23.5).
  (6) **confirmed**: all 500 (`0x3439` 17 ms, kill 0.58 s after `0x3438`, DB …5324); the position walked to was lost
  (relogin at the last save's spot). The auto-save is every **10 min** (StoreType 10, `tAutoSaveTime` from the map
  login; Z01 §8.4 corrected). Not predicted: the WM's `0x1037` carries its stale login copy of money and position,
  which reaches the GameLog's `0x040B` but not the character row (P02-B36); `0x1001` for a dead zone's map →
  `0x1002 {0x145}` without a CharDB round trip (§23.6).
  None of the "Disproved by" events occurred.
- **Notes corrected (`s38`, capture-validation §13, X07):** step 2's in-game quit is not in the capture (the 292.5
  event is a server-side reset without `0x1071`); step 1 was done twice (the first try went on to the world list);
  step 5 has a first `&getmoney` without a kill (547.2) and two kills (1412.1, 1567.5) before the one the notes
  record; the DB readings file was not copied (the run kits now have `collect`). The steps above carry these fixes.
- **Open after batch 4 (X07):** scenario **52** steps 3 (`&kickout`: `0x0C1A` with a real `usrregnum` → `0x0C17`) and 4
  (SHN mismatch: `0x1804 {0x147}`, `0x0C1A` with usrregnum 0); scenario **51** step 5 (two consecutive auto-saves);
  a `0x0C1A` with a real `usrregnum` also ends scenario 51 step 1 (0x68A) if Z23-B8 happens.

### 39. Combat extras: death penalty, PK, revive item, knock-back

- **Claims:** Z03 §7–§8 (`0x2411` exp loss, revive choices), Z07 §3.1–§3.2, Z12, Z25 (knock-back / reinforce
  moves), Z09 PK fields and the world kill announcement, W03 §3.2–§3.4 guild war kills, W04 §3.
- **Setup:** A level 20+ (exp loss applies), a revive item (`&makeitem`), B; a PK field map (X2) or a guild war
  between two test guilds (scenario 18 twice).
- **Steps:** (1) die to a mob with the revive item: use it. (2) die again: revive in town. (3) on the PK field:
  B kills A. (4) declare a guild war, B kills A outside the PK field. (5) kill a mob with a knock-back skill
  (`&learnskill`), and get knocked back by a mob. (6) kill a boss that is announced (if one is in reach).
- **Prediction:** (1) `0x2411 NC_BAT_EXPLOST_CMD`; `0x3039 NC_ITEM_REVIVEITEMUSE_CMD` and the revive on the
  spot (Z04 §12, Z07 §3.1); without the item `0x303A`. (2) `0x104E` → `0x104F NC_CHAR_REVIVESAME_CMD` or the map change (captured for
  the other-map case). (3) Z→W `0x244A` → announcement; `0x244B` to the client (W04 §3). (4) WM tick `0x7443` /
  `0x7444` to all Z at start / end; kill Z→W `0x7445` → both guilds' members `0x742A` (no 2016 client handler).
  (5) the forced move `0x2069 NC_ACT_REINFORCERELOC_CMD` to sight and `0x204A NC_ACT_REINFORCE_STOP_CMD {x, y}` to
  the moved player (Z09 §9.3, Z25). (6) Z→W `0x2458` → clients
  `0x2459`.
- **Disproved by:** an exp loss below the level Z03 §8 gives; a client reaction to `0x742A`.


- **Added by X05 (batch-2 leftovers: capture-validation §9 / §15 "PvP / party / guild-war deaths, exp loss, skill
  fail / abort, rebirth"; batch 2 holds one PvE death of a level-5 character and successful casts only):**
  - **Correction to step 2 as written:** the death captured in `combat` was answered with `0x104F` (same zone);
    `0x1050` was never captured, and a normal field always revives onto its own map (Z07 §3.1). The other-map
    revive is scenario 30 step 6.
  - **Setup addition:** A's exp well above the start of its level (kill a few mobs after `&levelup`), noted from
    the character window before each death; A and B in one party for step 8 (scenario 15 step 2).
  - **Steps:** (7) A casts a skill at a mob from beyond its range; twice in a row inside its cool-time; with less
    SP than its cost (spend the SP first); then starts a cast with a cast time and presses Esc (the abort of
    scenario 24 step 4, here with B in sight). (8) in the party, A dies to a mob; then on the PK field B kills A
    (step 3 with the party kept, if the field allows attacking a party member: note it). (9) A takes the buff
    whose abstate is `StaRebirth` (`AbState.shn` row 48; the skill or item that sets it is found with X4's table
    read), dies to a mob, and accepts the resurrection offered in the death menu; the same again, refused, then
    the town revive. (10) each death of steps 1–4 and 8 with the exp before and after noted.
  - **Prediction:** (7) no `0x244E` / `0x2435`; `0x2434 NC_BAT_SKILLBASH_CAST_FAIL_ACK {u16 err}`: `0xFCA` out of
    range, `0xFC8` in the cool-time, `0xFC9` not enough SP (Z03 §5.2); if the client refuses any of them itself
    (no `0x2440` on the wire) the case moves to T21. Abort: C → Z `0x2444` → sight including A `0x2438
    NC_BAT_SOMEONESKILLBASH_CASTCUT_CMD {caster}` and then A `0x2445 {0x20E8}`; no `0x2457` follows (Z03 §5.4).
    (8) to A the packets of the captured PvE death (`0x104D`, GameLog `0x042B`, `0xC80A`); B gets the bystander
    packets of capture-validation §18.5 and, at the next party status tick, `0x3832 NC_PARTY_MEMBERINFORM_CMD` with
    `hp 0` for A (Z08 §1.2–§1.3) and nothing party-specific at the death itself; the party stays. Killed by B on
    the PK field: Z → W `0x244A {killerWmHandle, killerCharNo, pkCount}`, A and B `0x244B {killer, victim,
    pkCount}`, GameLog **`0x0429 NC_LOG_GAME_PKED`** instead of `0x042B`, `0xC80B` for B and `0xC80A` with kind 0
    (Z03 §7.2). (9) the `0x104D` of that death has its last field (`canReviveHere`) = 1 when the map allows it
    (`field.flags & 2`), 0 in the captured death; accept: C → Z **`0x1102 NC_CHAR_REBIRTH_CMD`** (empty) → revive
    on the spot (`sp_ReviveNow`), no map login; refuse: C → Z **`0x1103 NC_CHAR_REBIRTH_REJECT_CMD`** (empty), no
    answer, and the later `0x104E` runs the town revive (Z07 §3.2; that the `StaRebirth` buff is what sets the
    offer is *(inferred)* from the `SelfRevive` sub-actor of Z03 §7.2). (10) `0x2411 NC_BAT_EXPLOST_CMD {u32
    lost}` and Z → W `0x1073` only from the level `g_ExpLossMinLevel` on (the client text says 20): by a mob `lost
    = (exp of next level − exp of this level) / 100 × FieldList ExpLostAtDeadByMob / 1000`, by a player on the
    PK field the level table's value × `ExpLostAtDeadByPly / 1000`, never below the start of the level, and 0 (no
    `0x2411`) where the map's rate is 0; the GameLog `0x042B.exp` carries the same number (0 in `combat`).
  - **Disproved by:** a `0x2434` code other than the three; a `0x2445` before the `0x2438`; a party packet at the
    moment of the death; `0x042B` for the PK death; a `0x2411` whose number differs from the formula with the
    map's `FieldList` row (read it with `shn.py`), or one below the minimum level; a map login after `0x1102`.
- **State after batch 5 (X09): not captured.** `re-data/captures/26_11_16_39_death-pk-revive-knockback-guildwar.md`
  (commit caf8817) is the notes template of the run kit `tools/capture/39/39-server.ps1` (`prep`: X39A SharpShooter 40
  and X39B Guardian 40, GM 100, 2 000 000 cen, A's exp mid-level, A Power Shot / Distant Shot, B Rebirth; `snapshot`,
  `cleanup`, `collect`) with its blanks not filled; there is no pcapng and no `-db.txt` (capture-validation §1).
  Every prediction of steps 1–10 is still open; record it as written (the run kit's notes file is the checklist).

### 40. Gathering, production, item emotes, way-finding gate, tutorial, attendance

- **Claims:** Z02 §8, §9, §11, §12; Z07 §3.5–§3.7, §11; Z17 §3–§4 item actions; W04 §17.5–§17.6 attendance and
  NPC schedule; Z09 §5.9 scheduled NPCs; Z01 tutorial (bug X02-B5).
- **Steps:** (1) gather at a node: finish once, cancel once by moving. (2) produce an item from the gathered
  material: finish once, abort once. (3) use a premium emote item (action-item box). (4) equip an item with an
  `ItemAction` row (X7 lists some) and kill a mob. (5) use the auto way-finding to a gate and let it pass the
  gate. (6) a new character: play the tutorial steps, skip one. (7) first login of the day: attendance window,
  claim. (8) toggle auto pick-up.
- **Prediction:** (1) `0x202D` → `0x202E`, sight `0x202F`; `0x2032` → `0x2033`, sight `0x2034`; cancel `0x2030`
  / sight `0x2031` (Z02 §8). (2) `0x2035` → cast, sight `0x2038`; `0x203B`; Z→D `0x3457` → `0x3458`, mastery
  `0x481D`; abort `0x2039` / `0x203A` (Z07 §11). (3) `0x2067` → `0x2068` (Z17 §4.5). (4) the action's packets
  (`0x206F` heal effect, cool-down `0x10D0` at a save; Z17 §3.4.1). (5) `0x2070` → `0x2071` (Z02 §11). (6)
  `0x1116` / `0x1117`, saves `0x1118` → `0x1119`, item `0x1112` → `0x1113` (Z07 §3.7; W01 for the WM side). (7) the attendance
  request is sent once per WM session (first map login, W7), `0x10ED`…`0x10F6`. (8) `0x10BC {bEnable}` → W
  `0x10C1`.
- **Disproved by:** a second attendance list after a map change; a gather that completes without `0x2032`.

### 44. Holy promise (mentor and pupil)

- **Claims:** W04 §12 (21 KB, all offsets ours), D04 §8, Z08 §9, Z30 §6.1; bugs W04-B34, Z08-B14, X02-B11.
- **Setup:** A high level (mentor), B a new low-level character; note both `tCharacter.nMoney`.
- **Steps:** (1) B (pupil) asks A to be its master; A refuses; again; A accepts. (2) B levels up twice; B buys an item
  for cen at an NPC. (3) A opens the mentor window, collects the cen reward, withdraws it. (4) both relog.
  (5) B deletes the mentor; asks again at once.
- **Prediction:** (1) C→W `0x9401 NC_HOLY_PROMISE_SET_UP_REQ` → requester `0x9403
  NC_HOLY_PROMISE_SET_UP_CONFIRM_ING {UpCharID}` ("You've asked %s to be your master."), target the prompt
  `0x9404`, target→W `0x9405 {CharID, UpCharID, bAccept}`; a target playing the mini-house dice game drops the
  prompt and sends no `0x9405`; refusals `0x9402` (W04 §12.3) → D `0x941E` → W `0x941F` → both `0x9415
  NC_HOLY_PROMISE_ADD_CMD`. (2) Z→W `0x1074` → mentor `0x9419`
  level; the purchase credits price / 10 to the mentor's promise money (D03 check 13). (3) C→Z `0x943C` → D
  `0x943E` → Z `0x943F` → C `0x943D`; withdraw `0x9440` → D `0x9442` → Z `0x9443` → C `0x9441`, money `0x1033`
  (README §3.29). (4) `0x9416` / `0x9417` presence. (5) `0x9406` → D `0x9420` → `0x9421` → `0x9407`, `0x9418`;
  the new request is refused by the rejoin date (W04 §12.1: the dates are kept, W04-B34).
- **Disproved by:** a credit other than price / 10; a second promise accepted inside the rejoin time.

### 45. Second client in sight II: what `s14` left open (added by X05)

- **Claims:** Z02 §2.2 (walk relay `0x2017` → `0x2018` from a player), §3.2 (shout to the whole map instance), §4
  (sit as an emote, emote stop `0x2022` / `0x2023`), W04 §2.1 (`0x200E`), Z03 §3.5 (`0x242E`), Z03 §5 cast abort
  (`0x2438`). Every one is a "not reached" of §3.14's result line (capture-validation §18.8, §15).
- **Setup:** as 14: A (GM, above the shout level) and B on one map, in sight (RouN, `MapInfo.Sight` 1600). B owns a
  skill with a cast bar; a mob that attacks stands near. No `&hide` / `&dimension` in this run (their appear /
  delete storm, P02-B27, hides the packets looked for).
- **Steps:** (1) B switches to walking, walks five steps, switches back, runs two steps. (2) B uses the action
  "Sit", 5 s later "Stand". (3) B plays a dance emote and ends it three ways, 10 s apart, the notes saying which:
  the same emote again, Esc, a step. (4) B runs out of A's sight on the same map (more than 1600 units; A no longer
  sees B); A shouts; B runs back. (5) A whispers with `X45Nobody` (no such character) as the **receiver**.
  (6) B lets a mob hit it next to A (inside A's sight; in `s45` B stood 970 units away) without hitting back, then
  kills it; a level-30 mob (Archmage Book) kills a level-40 B in four swings, so count the hits and revive first if
  B dies. (7) B starts the cast and steps before the bar is full (the client cuts the cast itself on a step; do it
  once and note how many tries there were: `s45` had three); then casts once to the end. (8) B walks out of A's sight
  and stops (step 7 of 14). Run kit: `tools/capture/45/45-server.ps1` (`prep`, `capture-start`, `snapshot`,
  `cleanup -Dest`, `collect` with the server logs).
- **Prediction:** (1) B `0x2017 {from, to}` → A `0x2018 NC_ACT_SOMEONEMOVEWALK_CMD` for B's handle, nothing to B;
  the run steps `0x2019` → `0x201A` as captured. (2) B `0x2020 {6}` → `0x2021 {B, 6}` to A **and** B, then `{7}`
  *(inferred from the captured stand)*; no `0x2009`. (3) none of the three ways sends `0x2022` (corrected after
  `s45`, capture-validation §27.3): the same emote again is a new `0x2020` → `0x2021` to both (the dance restarts),
  Esc sends nothing (the dance goes on), a step ends it on both screens through the move relay (`0x2019` → A
  `0x201A`). The 2016 client's only `0x2022` sender is its key function 0x6F (pause / resume an emote, "Open after
  batch 5" below); without that key the packet stays test-client case T19. (4) `0x201F` reaches B out of sight (the whole map
  instance, `so_AllInMap1`). (5) WM → A `0x200E {ErrorType 0x0F69, receiver "X45Nobody"}` (25 bytes raw); no
  `0x200D`, no `0x200F`, no `0x6006` to A's zone. (6) as captured before (capture-validation §9.2, §18.5): B gets
  `0x2447` / `0x2448` per swing of the mob, A the bystander forms `0x2447` / `0x2449`; **no `0x242E`, no `0x242D`**.
  Z03 §3.5 names the mob's normal attack as a caller of `so_Bash`, but every mob hit of batches 2–3 (28 `0x2448`,
  the killing blow included) came as a swing, so `0x242E` is left to the `&` test commands (which one was not looked up: knowledge X05 §6); the
  step stays as the check with a bystander and a player who does not hit back. (7) B `0x2444` → `0x2438 {caster B}`
  to A and B, then B `0x2445 {0x20E8}`; the full cast gives A `0x244F` as captured. (8) A gets `0x1805` for B's
  handle when B leaves the sight range *(inferred: the removal packet `&hide` produced in `s14`)*.
- **Disproved by:** `0x2018` also to B; a `0x2009` for the sit; a shout that stops at sight range; `0x200F` or
  `0x6006` for the unknown receiver, or another `ErrorType`; a `0x242E` / `0x242D` for a mob's hit (then Z03 §3.5 holds for that mob: note its `MobInfo` row); a cast
  abort without `0x2438` to A.
- **State after batch 5 (X09):** recorded as `s45` (`26_11_21_45_walk-sit-emote-stop-shout-whisper-cast-abort`, with
  the prep / DB readings and the server `-logs/` folder; capture-validation §27): X45A (A, Trickster 40) and X45B (B,
  SharpShooter 40) on zone 0, RouN, from one client PC.
- **Notes corrected (`s45`, capture-validation §13, X09):** step 6: the book hit B **four** times (250, 238, 276, 86)
  and B died before it could kill it (notes: "three hits"); B stood 970 units from A (notes: "~400"); B was revived
  in town, came back and killed the book with one Distant Shot. Step 7: **three** aborted casts (93, 266 and 881 ms
  into the cast, each cut by a step) before the full one (notes: one). Step 3: the step ended the emote; Esc did not.
  Step 4: "x45 shoud A" is the notes' typo (the wire has "shout"). The steps above carry these fixes.
- **Result (P02 batch 5, `s45`, capture-validation §27):**
  (1) **confirmed** (§27.2): each B `0x2017` reached A 16–23 ms later as `0x2018 {handle 8005, from = the server's
  position, to, speed 33 (B's walk speed), moveattr}` (stale `moveattr` bytes, Z02-B2); the runs as `0x201A {speed
  127}`; no `0x2018` / `0x201A` with B's own handle went to B (decoder count, X09); no `0x203E` after a move.
  (2) **disproved in part** (§27.3): the client sends `0x2020 {7}` for the sit (as `s14`), never `{6}`; the server
  relays it as `0x2021 {8005, 7}` to B and then A (`includeSelf` 1), no `0x2009`; the stand sends **no** packet (the
  client drops every `0x2020` in emotion state 4 and stands the character up locally, FUN_004ce0d0 / FUN_0049e520
  *(inferred)*); how A saw B stand is not settled.
  (3) **disproved**: none of the three ways sends `0x2022` (same emote: a new `0x2020` / `0x2021`, the dance
  restarts; Esc: nothing; a step: `0x2019` + `0x2012`, A `0x201A` / `0x2013`, the dance stops on both screens);
  `0x2022` / `0x2023` still never seen. The 2016 sender FUN_0049e580 is reached only through key function 0x6F (§27.3).
  (4) **confirmed** (§27.4): B left A's sight at 1607 units (`0x1C0E` both ways); A's shout `0x201F {"X45A", flag
  0x64, "x45 shout A"}` went to A **and** B out of sight (`so_AllInMap1`), so 1 ≤ `g_ShoutLevel` ≤ 39 with `s14`'s
  level-1 refusal. Not predicted: A's client sent WM `0x0846 {0, 1, 55}` → CharDB `0x0847` (W04 §17.2, no answer).
  (5) **confirmed** (§27.5): WM → A `0x200E {0x0F69, "X45Nobody"}` 10 ms after the `0x200C` (22 bytes payload, 25
  raw); no `0x200D`, `0x200F`, `0x6006`; client "Cannot find the recipient". First capture of `0x200E`.
  (6) **confirmed** (§27.6): four swings of the book (MobInfo 34), each B `0x2447` + `0x2448` + `0x240E`, A `0x2447` +
  `0x2449` (no damage number) in the same ms; **no `0x242E` / `0x242D`**; `hpchangeorder` B *n*, A *n*+1, B's
  `0x240E` *n*+2. Not predicted: B's death sends A only the `0x2449 {resthp 0}` (no death packet to the sight); the
  town revive reaches A as `0x2427` + `0x1C18` + `0x1805 {8005}`, not `0x1C0E` (same-zone link).
  (7) **confirmed with a different order** (§27.7): per abort B `0x2438 {8005}` + `0x2445 {0x20E8}` 4–11 ms after the
  `0x2444`, then A `0x2438` 11–14 ms after B; `0x243D` to both 51–71 ms later; no SP change, no `0x2457`, no message
  on B's screen. The full casts gave A `0x244F` at the start and the blast `0x2452` 1.5–1.6 s after `0x244E`, A's
  32 ms before B's.
  (8) **disproved**: leaving sight at walk speed gives `0x1C0E` both ways (1611 units, 731.3), not `0x1805`; A got no
  relay after it (Z09 §9.6 `ali_Work`). `0x1805` is the removal of a same-zone revive or teleport (step 6).
  None of the "Disproved by" events occurred; (2), (3) and (8) failed on points the list did not name.

### 46. Items III: what `s21` left open, no DB change (added by X05)

- **Claims:** Z04 §2.4, §2.5 (buy-back onto an empty cell, the three request-side refusals), §4.1
  (`irm_Split_N_Merge` @ FUN_00532a20), §13.1 (`0x5005`); Z05 §2.2, §4; D03 §2.2 (`0x34B9` @ FUN_0042e060), §3.3
  (`0x3431` @ FUN_0040c000) and its SQL checks for **the character that plays** (capture-validation §19.8: the
  `s21` snapshots listed another one).
- **Setup:** one client, GM character `<Char>`; run kit `tools/capture/46/46-server.ps1` (`prep`, `capture-start`,
  `snapshot -Label …` before the login and after the logout, `cleanup -Dest`, `collect`; the snapshot prints the
  name first: compare it with the notes). Stop the capture only **after** the logout (`s46` stopped with the
  character still in the world, so its logout save is not on the wire).
  `&makeitem BestLowHpPotion -l40` and `-l30` (`MaxLot` 50), `&makeitem LeatherBoots` (not stackable), one item whose
  `ItemInfo.BuyDemandLv` is above the character's level and whose `SellPrice` is not 0 (2016 data: `NormalEar117`,
  117: **the character must be below that level**, the level-120 GM of the earlier batches gets no `0x366B`; if
  `&makeitem` refuses it, any row of
  `python3 -I tools/protocol-re/shn.py …/ItemInfo.shn` with a higher `BuyDemandLv` than the level), one weapon that
  sells for more than the merchant's cheapest item costs.
- **Steps:** (1) drag the lot-30 stack onto the lot-40 stack; then the rest (20) onto the full stack. (2) at the
  storage keeper deposit a stack (for D03 check 3) and **all** cen. (3) at one item merchant, without clicking any
  other NPC until step 7 (P02-B31): sell the boots, buy them back. (4) sell the weapon, buy the merchant's cheapest item, try to buy the weapon back (the cen are 0 since
  step 2 and step 3 nets 0, so the purse now holds less than the weapon's price; this step must come before the
  next one, whose sale leaves cen in the purse). (5) sell the `BuyDemandLv` item, try to buy it back. (6) `&makeitem` until the
  inventory is full (no `0x3402` any more), sell the boots, `&makeitem` once more, try to buy the boots back.
  (7) deposit the cen the sales brought (storage keeper), then at the healer with 0 cen: buy one HP soul stone; withdraw the cen
  (storage keeper), back at the healer buy HP stones up to the number the window allows, then ask for more if the
  client lets the number be typed.
- **Prediction:** (1) `0x300B` → D `0x3431 {MoveLot 10, nFromItemLot 30, nToItemLot 40}` → `0x3432 {…, 10, 20, 50}`
  → `0x300C {0x241}`, the two cells at 20 and 50; G `0x0456`. The second drag (target full): no `0x3431`. `sp_ItemReloc` @ FUN_00536780 tests
  `MaxLot <= lot of the target` before it calls `irm_Split_N_Merge` and takes `irm_Exchange` instead (Z04 §4.1
  does not show this branch; X05 review): D `0x342B NC_ITEMDB_EXCHANGE_REQ` → `0x342C` → `0x300C {0x241}`, the two
  stacks swap cells (20 where the 50 was). Only an item that may not be relocated back (`iba_CanInvenReloc` 0) is
  refused by the zone, `0x300C {0x24A}`. (2) as captured (§3.21 result 8); the after-snapshot holds the stack with `nStorageType = 6`,
  `nOwner = userNo` (D03 check 3). (3) sale `0x3422` → `0x3423` → `0x305C`, `0x3005 {0x381}`; buy-back `0x3059` → D
  `0x34B9 NC_ITEMDB_REPURCHASE_ALL_REQ` (a **new** item key made by the zone, `nSellItemKey` = the sold one) →
  `0x34BA {0x3668}` → `0x305D`, `0x305A {0x3668}`, the boots by `0x3001` in the **first empty unlocked cell**
  (`ii_RepurchaseAll` @ FUN_00537ca0; not the cell they were sold from); G `0x07FD {0x7F8, nInt3 = the price}`,
  `0xC815`; the after-snapshot has the boots under the new key only. (4) **nothing on the wire** (corrected after
  `s46`, capture-validation §26.4): the 2016 client compares its purse with the entry's price itself and shows
  810 500 413 "Cannot make the purchase due to insufficient money."; no `0x3059`, so the zone's `0x305A {0x366C}`
  "Not enough money to buy the item." is out of reach of the 2016 client ("Open after batch 5" below). (5) `0x3059` → **`0x3004 {0x366B}`** (a BUY_ACK,
  Z04-B2), no `0x305A`, no DB request, no text *(inferred: the buy handler has texts for its own codes only, Z05
  §2.4)*. (6) `0x305A {0x366D}` "Inventory is full.",
  no DB request. (7) both refusals are the **client's** (corrected after `s46`, capture-validation §26.5): with 0 cen
  978 272 565 "You have insufficient money.", at the limit (held = `maxnum`) 1 677 983 971 "Cannot purchase more.",
  no `0x5001` / `0x5002` for either; the number dialog offers at most `min(purse / price, maxnum − held)`. The zone's
  `0x5005 NC_SOULSTONE_BUYFAIL_ACK` / `0x3443` refusals (Z04 §13.1) stay test-client case T18. The allowed purchase:
  `0x5001 {n}` → D `0x3441 {flag 0, number n, price n × hp.price}` → `0x3442` → `0x1033`, `0x5003`, `0x3004 {0x201}`.
- **Disproved by:** a `0x3431` or a refusal for the second drag (predicted: an exchange `0x342B`); `0x34BB` for the boots; the sold key
  coming back; `0x305A {0x366B}`; a DB request in (4)–(7); a refusal in (4)–(6) that removes the entry from the
  repurchase list (`0x305D`).
- **State after batch 5 (X09):** recorded as `s46` (`26_11_16_46_items-merge-buyback-refusals`, with the prep output
  and the DB snapshots "after prep", "after setup", "after logout"; capture-validation §26): X46A (charNo 11,
  Trickster 20, GM 100, 1 000 cen, `admin` userNo 103), one client, zone 0, RouN. Setup items: `BestLowHpPotion`
  ×40 / ×30, `LeatherBoots`, `NormalEar117` (Frozen Earrings), `BroadSword` in cells 0–4.
- **Notes corrected (`s46`, capture-validation §13, X09):** step 3: the bought-back boots went to the first empty
  cell (0, emptied by step 2's deposit), not the cell they were sold from (2; the notes had "an empty cell, e.g. 2" and
  corrected themselves). Step 4: the money refusal is the client's text 810 500 413 with no packet (the notes' text),
  not the zone's `0x366C`. Step 7: both soul-stone refusals are the client's (978 272 565, 1 677 983 971), no
  `0x5001`; the number could not be typed (the dialog offered 36). The capture ends at 751.3 s with X46A in the world:
  the logout is not on the wire, its save only in the "after logout" snapshot. The setup, steps and predictions
  above carry these fixes.
- **Result (P02 batch 5, `s46`, capture-validation §26):**
  (1) **confirmed** (§26.2): `0x300B` → D `0x3431 {lock 8, 3500, MoveLot 10, cell 1 → cell 0, lots 30 / 40}` (44 bytes
  = ref + the pdb2016 struct; layout corrected in P02.json) → `0x3432 {…, 10, 20, 50}` → `0x3001` ×2, `0x300C {0x241}`;
  G `0x0456` with the target's result lot before the source's (D03 §3.3 corrected). The second drag onto the full
  stack: **exchange as predicted**, `0x342B` → `0x342C` +11 ms → the two swap, `0x300C {0x241}`, no GameLog row;
  `0x300C {0x24A}` and the `irm_Move` / `0x20a` branch were not reached (§26.2's branch table).
  (2) **confirmed**: the ×20 to account storage cell 3 by `0x3428` (owner 11 → 103), `0x301C {1000}` → `0x345F` →
  `0x3460` → `0x301D`; the after-logout snapshot has it with `nStorageType 6`, `nOwner 103` (D03 check 3).
  (3) **confirmed with the cell corrected** (§26.3): sale `0x3006` → `0x3422 {price 2}` → `0x305C`; buy-back `0x3059 {0}`
  → D `0x34B9 {lock 13, location 0x2400 (cell 0), a new key, nPrice 2, nSellItemKey = the sold key, UserNo 103,
  Vendor 28}` + 13 attribute bytes (77 bytes; layout corrected) → `0x34BA {0x3668}` +10 ms, G `0x07FD {0x7F8, nInt3 2}`
  and `0xC815 {BuyMoney 2}` → `0x1033`, `0x3001` cell 0, `0x305D`, `0x305A {0x3668}`; the snapshot has the boots
  under the new key only. No `0x34BB`.
  (4) **disproved**: no `0x3059` on the wire; the client refused with 810 500 413; the entry stayed listed (§26.4).
  (5) **confirmed** (§26.4): seven `0x3059 {2}` → seven `0x3004 NC_ITEM_BUY_ACK {0x366B}` 0–17 ms later, no `0x305A`,
  no DB request, no text on the client (`On_NC_ITEM_BUY_ACK` FUN_004ab770 has no case for it): Z04-B2 captured; the
  level check comes before the money check (the purse would have paid).
  (6) **confirmed** (§26.4): `0x3059 {3}` → `0x305A {0x366D}` +8 ms, no DB request, "Inventory is full."; on the way
  the 46th `&makeitem` into the full bag got no answer at all (Z11-B12, as §19.2).
  (7) **disproved**: both refusals are the client's, nothing sent (§26.5); the allowed purchase of 36 went `0x5001
  {36}` → `0x3441 {flag 0, 36, price 972}` → `0x3442` → `0x1033 {89435}`, `0x5003 {51}`, `0x3004 {0x201}`.
  Not predicted: the auto-save at 631.0 (`StoreType 10`, 600.014 s after the `0x1803`, §23.5).
  None of the "Disproved by" events occurred; (4) and (7) failed because the client never sent the request.

### 47. Items IV: the zone and the DB disagree (added by X05)

- **Claims:** D03 §2.2 (`0x3424` / `0x3427`, `0x366E`), §2.4 (`0x3443 {0x744}`), §1.2 `ItemBuy_Create` (D03-B1);
  Z05 §2.2 (Z05-B1), §2.4; Z04 §2.4 (`0x385`), §6.1 (`0x702`), §4.1 with an over-full stack; Z24 §6.7
  (`sp_ChargedItemLimitCheck` @ FUN_00451530 for a worn item and a ridden mount). All are DB or table setups: one
  short capture per step, each named in the notes, the scripts of `tools/capture/21` run with `-Char <Char>`.
- **Setup:** S12, S17, S16, X3, S13 as named per step. The character stays in the game for S12 and S17 (that is the
  point) and logs out right after each, before the restore.
- **Steps and predictions:**
  (1) **S12, whole stack.** A lot-10 stack; S12 as written (DB lot 9); sell the whole stack. Z → D `0x3422 {nLot
  10}` → `0x3424 NC_ITEMDB_SELLALLFAIL_ACK {0x389}` (stored lot < `nLot`) → C **`0x3005 {the player's object
  handle}`** (Z05-B1), text "Failed to sell the item."; no money, no `0x305C`, the cell keeps 10.
  (2) **S12, part of a stack.** Run S12's `UPDATE` with `- 3` (DB lot 7, the zone shows 10); sell 1. Z → D `0x3425`
  (remaining lot 9) → `0x3427 NC_ITEMDB_SELLLOTFAIL_ACK {0x38D}` (stored lot < remaining lot) → C `0x3005 {object
  handle}` as in (1). A DB lot only 1 lower passes (9 is not < 9): the sale succeeds and the DB keeps 9.
  (3) **S17, money.** With the DB money at 0 and cen in the client: buy one HP soul stone → D `0x3441` → `0x3443
  {0x744}` → C `0x3004 {0x744}`, no `0x5003`, no text; sell the boots (the sale succeeds and
  **credits the DB row** with the price, `p_Char_MoneyAdd`), then **run S17's `UPDATE` again** (the buy-back price
  is that same `SellPrice × lot`, so without it `p_Char_MoneySub` ends at exactly 0 and the buy-back succeeds; X05
  review), then buy them back → D `0x34B9` → `0x34BA {0x366E}` → C `0x305A {0x366E}`, no text (D03-B2), no `0x305D`
  *(inferred: the list entry is removed by the lock's apply only)*; with a stack of the item in the inventory the
  same order (sell, `UPDATE`, buy back) through `0x34BB` → `0x34BC {0x366E}`.
  (4) **S16 with fame.** A character with fame (each `&levelup` level adds its number, Z11 §7.3) buys, with the
  trigger installed, an item with `BuyFame` > 0 (2016 data: 106 rows, e.g. `MightySoul01`, 1200) whose class writes
  an option row; note `tCharacter.nFame` before and after. Wire as §8.17's result (`0x340C {0x206}` → `0x3004
  {0x206}`); DB: **`nFame` lower by `BuyFame`**, cen unchanged, no item row (D03-B1). If the purchase succeeds, the
  class writes no option row: take another item. The gamble-coin form goes through the capsule purchase `0x34A0` (a `LuckyCapsule*` item, `BuyGBCoin` 1000 /
  5000, the 4 coin rows; coins by S9) and has **two outcomes, the content decides** (D03 §2.5 inserts the content
  first, `Item_Insert` with its attribute write, and calls `ItemBuy_Create` for the capsule only after it): (a) the
  content item writes an option row → the trigger fails step 1, `0x34A1 NC_ITEMDB_BUYCAPSULE_ACK {0x206}` **before
  any debit**, `nCoin` unchanged, D03-B1 not reached; (b) the content writes none and the capsule does → `0x34A1
  {0x206}` from step 2 with `tGambleCoin.nCoin` lower by `BuyGBCoin` (D03-B1), the content row deleted. Note
  `nCoin` before and after and the content's item id (`0x34A0` @0x95); which of the two a given capsule gives was
  not looked up, and whether an NPC sells `MightySoul01` or the capsules was not checked (X05 review): if none
  does, this step has no client path and stays open.
  (5) **X3, the over-full stack** (§9.4 steps 1–3 done: 50 in the cell, `MaxLot` 49, a second stack of 10): sell
  one of the 50 → C `0x3005 {0x385}`, no DB request; use one → C `0x3016 {0x702, itemid, 9}`, no DB request; drag
  the 10 onto the 50 → no `0x3431` (`MaxLot <= lot of the target` in `sp_ItemReloc` @ FUN_00536780, as scenario 46
  step 1) but an exchange D `0x342B` → with the Character server still on the old table `0x342C`, the cells swap;
  with it restarted on the new one `0x342D NC_ITEMDB_EXCHANGEFAIL_ACK {0x84F}` (D03 §3.2: a lot above `MaxLot`) → C
  `0x300C {0x84F}`; drag the 50 onto the 10 → `0x3431 {MoveLot 39}` → with the Character
  server still on the old table (X3 restarts the zones only) `0x3432 {…, 39, 11, 49}`, with it restarted on the new
  one `0x3433 {0x40D}` (stored 50 > `MaxLot`): the notes say whether the Character server was restarted.
  (6) **S13, worn.** S13 on an item in the equipment (`nStorageType` 8; pick it from S13's list), login, stand in
  B's sight for two minutes. At the first minute check D `0x3459` for the key and the equipment cell emptied on
  `0x345A`; what B sees of it (an unequip packet or nothing until the next brief info) and whether A's stats are
  sent again was not read: note both.
  (7) **S13, ridden mount.** S13 on a mount (option row 1601); login and mount within the first minute; ride for
  three minutes; dismount. No `0x3459` while riding (class 23 and mode 6 are skipped); `0x3459` at the first minute
  check after the dismount. That the expired mount can be mounted at all is *(inferred: Z04 §6.1 names no end-time
  check)*.
  (8) **S13, used before the check.** S13 on a timed item that can be used (action item, option row 1900); use it
  within the first minute. `0x3016 {0x700}` *(inferred as in 7)*, and the item still goes at the minute check.
- **Disproved by:** (1), (2) a `0x3005` with the DB code (0x389 / 0x38D) instead of the handle, or a `0x305C`; (3) a
  `0x5003`, a `0x305D`, or any client text; (4) `nFame` unchanged (D03-B1 is wrong) or the item kept; for the capsule a `0x34A1` code other than `0x206`, or `nCoin` lower in outcome (a); (5) a DB
  request for the sale or the use, a `0x3431` or a zone-side refusal for the first drag, or a disconnect `0x68C`; (6)–(8) a
  refusal at the mount or the use that names the end time, a `0x3459` while riding, or the worn item surviving two
  minutes.

### 48. WM stop and start with its log (added by X05)

- **Claims:** W05 §1.3 (`ProcessLink` @ FUN_00404bf0 stops the WM when `Listen_Zone` / `Listen_Client` fails), §1.6
  (`ViewStopInfo` @ FUN_00403d40); capture-validation §17.6: the first WM start of `s37` ended 1.09 s after its
  CharDB load and the wire cannot tell why.
- **Setup:** server PC only, no client; the link capture running; note the wall-clock time of every step. Keep the
  WM's `.\DebugMessage\Msg_<date>.txt`, `Assert<date><hh>.txt` and `ExitLog<date><hh>.txt` of the hour (W05 §3)
  next to the capture.
- **Steps:** (1) stop the WM the way it was stopped in `s37` (service stop or console close: note which). (2) start
  it; wait for the zones to register. (3) stop it; occupy the WM's client port with another listener
  (`[System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, <port of the WM's client row in
  ServerInfo>).Start()` in a PowerShell that stays open); start the WM. (4) close that PowerShell, start the WM again.
- **Prediction:** (1) the `ProcessStop` close order of §17.1 and a stop time in the `Msg` log (`ViewStopInfo`); no
  "FAILED LISTEN" line. (2) the start of §17 up to `0x9804`, then the zone registrations. (3) the same bytes up to
  `0x9804`, then the WM closes all its links about 1 s later without any zone or client connection (the `s37`
  pattern), and the `Msg` log has "*FAILED LISTEN ADD, IP=…:<port>, From=…*". (4) as (2).
- **Disproved by:** a WM that runs on in step 3 (the listen failure does not stop it, so `s37`'s first stop was the
  operator's); no "FAILED LISTEN" text in any log file of step 3; a stop in step 3 at another point than after
  `0x9804`.


- **Added by X05 (batch-2 leftover: the phase of the per-minute `0x0821`, capture-validation §14):** the capture of
  steps 2 and 4 already holds the answer, nothing more to do than keep recording for three minutes after each WM
  start. The zones' per-minute block runs on the WM's `0x0821` (Z09 §1.2), the WM sends it on a 60-s timer (W01 §2)
  and it left at :42 in both batch-2 captures; what sets the phase was *(inferred)*. Read from the capture: the
  time of the first `0x0821` on each zone link after the WM start, against (a) the WM's `0x9804` (end of its start)
  and (b) that zone's `0x0802` registration. **Open between two readings**, the capture decides: the timer runs from the WM's start (first `0x0821` 60 s
  after it, a zone registering later gets none of its own), or a zone's registration forces a send and re-arms the
  timer (a `0x0821` within one pass of the last zone's `0x0802` answer, the next 60.0 s later). In both, one send
  goes to all registered zones in the same ms and every later one follows 60.0 s after the one before, whatever
  second the wall clock shows. Disproved by: sends aligned to the wall-clock minute; an interval other than 60 s.

### 49. Items V: refusals by the Character server (added by X05)

Batch-2 leftover (capture-validation §8.2 / §15): the captures hold only successful item transactions; batch 3 added
`0x340C {0x206}` (S16) and scenarios 46 / 47 the sell, buy-back and soul-stone refusals. This one takes the rest of
the `*FAIL_ACK` family. Every step is a DB setup under an **online** owner; several end in a disconnect, so one
short capture per step, links recorded, the setup named in the notes.

- **Claims:** D03 §2.1 (`0x340C` / `0x340F`), §3.1 (`0x3412`, `0x3415`, D03-B5), §3.2 (`0x342A`), §3.4 (`0x3418`,
  `0x341E`, `0x3421`), §5.1 (`0x3445`, D03-B6); Z05 §2.1, §3.1, §3.2, §4, §5.1 (Z05-B1: the object handle in the
  code field; Z05-B5: the wrong lock freed), §7.1.
- **Setup:** S17, S12, S18, S19 as named per step; A next to a merchant and the storage keeper; a weapon and a
  stack of 10 potions in the inventory, a ring worn; a mob that drops (X1) or B dropping items for A.
- **Steps and predictions:**
  (1) **S17, purchase.** DB money 0, cen in the client: buy an item that takes a new cell → Z → D `0x340A` →
  `0x340C NC_ITEMDB_BUYALLFAIL_ACK {0x205}` → C `0x3004 {0x205}`; buy one more of the potions onto the stack → D
  `0x340D` → **`0x340F NC_ITEMDB_BUYLOTFAIL_ACK {0x207}`** → C `0x3004 {0x207}`. No `0x3001`, no `0x1033`; note
  the client text for each (S16's `0x206` showed none).
  (2) **S18 on the weapon** (row removed, the zone still shows it): move it to another inventory cell → D `0x3428`
  → `0x342A NC_ITEMDB_RELOCFAIL_ACK {0x247}` (`p_Item_IsValidOwner` 1 = no such item) → C `0x300C {0x247}`, the
  weapon stays in its cell; then equip it into an empty equipment slot → D `0x3410` → `0x3412 NC_ITEMDB_EQUIPFAIL_ACK {0x28A}` (`0x28B`–`0x28D` or
  `0x28A` when it replaces a worn item, D03 §3.1) → C **`0x3011 {A's object handle}`** (Z05-B1), nothing worn; then drop it → the cell empties at once (`0x3001`), D `0x3416` →
  `0x3418 NC_ITEMDB_DROPALLFAIL_ACK {0x306}` → C `0x3008 {object handle}` and the zone disconnects A with reason
  `0x684`; no drop object appears.
  (3) **S18 on the worn ring:** unequip it → D `0x3413` → `0x3415 NC_ITEMDB_UNEQUIPFAIL_ACK {0x28A, lock}` → C
  **`0x3013 {object handle}`**, the ring stays worn; the zone frees lock index `0x28A` instead of the request's
  (Z05-B5), so the ring's cell and the target cell stay locked: a second unequip or a move onto that inventory
  cell is refused by the zone itself without a DB request (note the code), until the relog.
  (4) **S12 on the potion stack** (DB lot 9, zone 10): drop the whole stack → D `0x3416` → `0x3418 {0x348}` (a
  PICK code; the stored lot differs) → C `0x3008 {object handle}` + disconnect `0x684`. Second run, same setup:
  pick up one more potion onto the stack → D `0x341F` → **`0x3421 NC_ITEMDB_PICKMERGEFAIL_ACK {0x348}`** → C
  `0x300A {itemid 0xFFFF, lot 0, error = object handle, 0xFFFF}` + disconnect `0x684`.
  (5) **S19 on `tItem`:** pick up an item that takes a new cell → D `0x341C` → **`0x341E
  NC_ITEMDB_PICKALLFAIL_ACK {0x347}`** → C `0x300A {0xFFFF, 0, object handle, 0xFFFF}` + disconnect `0x684`. The
  pick-up was applied before the answer (Z05 §3: style 2), so until the disconnect the client shows the item;
  after the relog it is gone (no row) and the drop object no longer exists either: the item is lost.
  (6) **S19 on `tUserMoney`** (the account's storage-money row removed first): talk to the storage keeper → D
  `0x3444` → **`0x3445 NC_ITEMDB_OPENSTORAGE_FAIL_ACK`** whose 2 code bytes are never written (D03-B6) → C `0x3C07
  NC_MENU_OPENSTORAGE_FAIL_CMD {those bytes}`, text "An error has occurred while using the Storage.", no `0x3C08`.
  The 2016 zone asks for four pages at the open (four `0x3444`, capture-validation §20.1) and each one runs
  `p_User_MoneyGet`: expect **up to four** `0x3445` / `0x3C07`; note how many arrive.
  (7) **S19 on `tItem`, buy-back** (added in the X05 sweep: the one repurchase code 46 and 47 do not reach): sell
  the Leather Boots (the sale deletes the row and succeeds), install S19 (a), buy them back → D `0x34B9` →
  **`0x34BA {0x366F}` or `{0x366E}`, open between the two** (X05 review). D03 §2.2 gives `0x366F` when
  `ItemBuy_Create` returns neither 0 nor 1. S16's result does not carry over: there the trigger fired in a separate
  call (`ItemAttr_Save`); here it fires inside `p_Item_BuyAll` *(db-backup)*, after `p_Char_MoneySub` has set `@nRet
  = 1`, and its rollback aborts the batch before `SET @nRet = @CreateItemRet`. If no output parameter comes back,
  the wrapper FUN_00462380 keeps its initial −1 → `0x366F`; if the stale 1 comes back → `0x366E`, the money code,
  although the money was not the cause. → C `0x305A {that code}`, no text (D03-B2), no `0x305D`, no `0x1033`; the entry stays in the repurchase list *(inferred as in 47
  step 3)*: drop the trigger and buy back again in the same capture, which must succeed (`0x34BA {0x3668}`). No
  disconnect in this step.
- **Disproved by:** a DB code (0x28A, 0x306, 0x347, 0x348) in the client packet where the handle is predicted, or
  the handle where the code is predicted (`0x3004`, `0x300C`); no disconnect after a drop or pick refusal; a
  second unequip in step 3 that reaches the DB; a `0x3C08` in step 6; any `0x1033` in step 1; in step 7 a
  successful buy-back, a code other than `0x366E` / `0x366F`, a lower `tCharacter.nMoney` after the refusal (the
  rollback must undo the debit), or a second buy-back that finds the list entry gone.
- **After each step:** A at the login screen, then the setup's restore; compare `tItem` / `tItemOptions` of A with
  `21-server.ps1 snapshot-*` before and after (rows the refusal left behind are findings: the equip path does not
  undo its `unequip[]` moves, D03 §3.1).

### 50. Timing with one clock and without delayed ACKs (added by X05)

Batch-2 leftovers that are about **when**, not what (capture-validation §14: "0x0849 / 0x080E clock offset", "0x7C07
timing", "client sends after a mob-tick event"). No layout and no order within one connection depends on them; they
are worth one run because a rebuild that answers in the same order but in other segments would look different to a
reader of the old captures.

- **Claims:** W05-B1 and S02 §1.4 (the passes sleep ≈ 15.6 ms; no `TCP_NODELAY`: Nagle holds a second small
  segment until the first is ACKed); capture-validation §4.1, §7.4, §7.5.4 (the 47–74 ms holds read as Nagle +
  the client's delayed ACK), §9.5 / §9.6 (client packets of a mob-tick event leave 18–27 ms after the link
  packets).
- **Setup:** capture **on the server PC** (client and links in one file, one clock: this alone removes the
  0x0849 / 0x080E offset question, the stamps are then the server's). Run A as recorded so far. Run B with delayed
  ACK switched off on the client PC (`TcpAckFrequency` = 1 on its network interface, reboot; restore after).
- **Steps (both runs):** (1) log in to the character list, select a character (`0x7004`, `0x700C`, `0x7C06` and
  their answers). (2) walk through a gate (`0x1003` after the link). (3) let a mob kill A; kill a mob with a
  skill; kill one with swings.
- **Prediction:** run A repeats the captured holds (`0x7C07` leaving with `0x700D` 73–74 ms after `0x7C06`; 47–52
  ms after `0x1003`). Run B: every held segment leaves within one WM pass of its cause (`0x7C07` ≤ 20 ms after
  `0x7C06`, before `0x700D`), the order of packets unchanged. Step 3 in both runs: at A's death and at the skill
  kill the GameLog / WM link packets precede the client packets of the same event by one to two zone passes
  (the mob tick queues client data that a later point of the pass flushes), a swing kill sends both in one ms;
  run B must not change that (it is not an ACK effect).
- **Disproved by:** the 73 ms hold surviving run B (then it is not Nagle: re-read W05 §1 for a per-session send
  timer); a changed packet order in run B; the 18–27 ms gap vanishing in run B.

### 51. Skills II: what `s24` left open (added by X07)

Batch-4 leftovers of scenario 24 (capture-validation §14 "Batch 4, skills and stats" and "skills II"): the paths the
2016 client reached only with one learned step, never kept on long enough, or refused before the server could.
The client-side refusals are test-client cases T23 / T24 (scenario 41); `0x243E` is T25.

- **Claims:** Z23 §4 (`csl_EmpowerAlloc`, Z23-B8) and Z03 §9.1; Z23 §2.2 / §2.5 (`csl_Toggle_SetOnOff`, Z23-B1);
  capture-validation §25.4 (P02-B39, P02-B38); Z23 §7 / §7.1, D02 §6 (`0x4009` → `p_Skill_Set`), Z12 (`0x103D`
  `cooltime`); Z08 §11 and D03 (`0x9005` / `0x9006` failures, `usp_ChargeItem_UseStatPointInitDel` /
  `…UseSkillPowerInitDel`); Z01 §8.3 and W01 §5.2 (`0x0C1A` → `0x0C17`).
- **Setup:** the run kit of scenario 24 (`tools/capture/24/24-server.ps1 prep`: X24A Gladiator 100 GM with Heat of
  Fury [01] (7300) and Dash [01] (452); X24B HighCleric 20 GM with Revive [01] (1620) and Invincible [01] (1800));
  `24-setupA.txt` (Titanic Axe: Heat of Fury needs a two-hand weapon) and `24-items.txt` (2 Skill Reset Scrolls
  `SkillReloadbundleOne`, the two capsules). Slice and Dice [01] (skill 0) as in `s24` step 1 (book) or
  `&learnskill 0`. `snapshot` before and after each step; the snapshot now lists `nSkillExp`, `nSkillWriteTime` and
  `nSkillCoolTime` (X07). S21 for steps 6 and 7 only. One capture; the notes give the time of each step.
- **Steps and predictions:**
  (1) **Empower with two learned steps (Z23-B8).** A puts 1 damage point on Slice and Dice [01] (as `s24` step 2:
  `0x4811 {0, plus {damage 1}}` → `0x4814 {0, 0x881}`); `&learnskill 1` (Slice and Dice [02]: D `0x4801` → `0x4802`
  → C `0x4804`); `snapshot` (row 0 damage 1, row 1 damage 0); then take the point back in the skill window with one
  Skill Reset Scroll. **Note the `skill` of this `0x4811`.** If it is **1** (the highest learned step, *inferred* in
  Z23 §4): the line sum (1) passes the check, the subtraction hits step [02]'s own 0 and wraps to 15: D `0x4812
  {…, skill 1, empower {damage 15}, bUseItem 1}` → `0x4813 {0x885}` (`p_Skill_SetPowerAll` refuses a field above 5)
  → C `0x4814 {1, 0x885}` "Skill Empower failed." → the zone disconnects A: Z → W **`0x0C1A {usrregnum = A's user
  number, wldmanhandle = A's WM handle, 0x68A}`** → W → C `0x0C17 {0x68A}` (the client acts only on 0x683), A's
  sockets close; the next login shows the point still on [01] (the skill rows unchanged) but the Skill Reset Scroll
  **gone** (one fewer in the lot, or its row deleted): the Character server destroys it before `p_Skill_SetPowerAll`
  and does not give it back when the procedure refuses (D04 §2, D04-B5). The refusal needs the procedure's "> 5 →
  `nRet` 0" check: before the step print `EXEC sp_helptext 'p_Skill_SetPowerAll'` on the test CharDB (as S20 prints
  `sp_helpindex`); the w00 version and the second version in `Character.bak` have it, the first (2007) version of
  `Character.bak` only runs the UPDATE, which writes damage 15 and answers `0x881` (`0x4814 {1, 0x881}`, A stays in
  the game, row 1 damage 15). If it is **0**: `0x4814 {0, 0x881}`,
  the point leaves [01]; Z23-B8 then needs a crafted `0x4811 {1, 0, minus {damage 1}}` (test client, scenario 41
  T23's form).
  (2) **Toggle past its icon timer (P02-B39).** A switches Heat of Fury [01] on next to a mob (as `s24` step 5) and
  keeps it on for 25 minutes: HP above 5 %, weapon unchanged, no link (each of these switches it off, Z23 §2.4).
  The toggle drains 2 % of MaxHP per second (76 HP/s for A in `s24`, capture-validation §25.4), so it switches itself
  off after about 48 s from full HP: keep A's HP up with `&sethp <MaxHP>` (76 = 2 % ⇒ MaxHP 3 800 at `s24`'s step 5,
  *inferred*; read it from the character window; `&sethp 100` there put HP
  below 5 % and switched the toggle off) every 30–40 s, or with B healing A (Heal, B next to A). Each `&sethp` gives
  A the HP update `s24` recorded after `&sethp` (`0x240E`, §25), each heal B's cast packets and A's HP change in
  sight; none of them switches the toggle off.
  At 23 min 5 s (1 385 447 ms after `0x2429`) the client's icon of `StaBurnPainMe` runs out; **no packet** in either
  direction *(inferred: the client asks nothing)*, no `0x2428` / `0x1C18` from the server (it keeps the state 37.4 h).
  At 25 min A switches it off by a cast: `0x245D {7300}` and **two** `0x2428` per state still set (P02-B38), sight
  `0x1C18`. Note what the shortcut bar and the buff bar show after 23 min.
  (3) **Toggle with a lower learned step (Z23-B1).** `&learnskill 7745`, `&learnskill 7746` (Heat of Fury [02],
  [03]); keep [01] on a shortcut from before; wait 5 s between casts (`DlyTime` 5000, one delay group 207 for the line). Cast [01]: `0x245C {7300}` (on: [01] and the one step above, [02]; [03]
  keeps "off", Z23-B1). Then cast [03]: **`0x245C {7746}`** again (the server finds [03] off and switches it on), not
  `0x245D`; cast [03] once more: `0x245D {7746}`, all steps off. A cast of [02] after [01] instead gives `0x245D
  {7745}` (one step up is updated). If the client casts only the highest learned step (the shortcut changes to [03]
  or the cast of [01] is refused without a packet), note it: this step then needs a crafted `0x2440 {7300}` (test
  client).
  (4) **Skill-save columns (D02 §6).** A learns Violence [01] (453, `DlyTime` 120 s, `UseClass` 6 like Heat of Fury) with
  `&learnskill 453`: the `0x4801` path that gave the book's row `nSkillLevel 1` in `s24` (capture-validation §24.2),
  so its row starts at **1**, unlike the prep rows (`p_Skill_Set`, level 0, §24.6); `snapshot`. B casts Invincible
  [01] (1800, 120 s), A casts Violence [01] next to a mob; 20 s later both quit to the login screen; `snapshot` once
  the quit saves are in (they come 10–13 s after `0x1071`: the 10-s quit countdown, capture-validation §23.2 /
  §23.3). Prediction per cooling skill: CharDB `0x4009 NC_CHARSAVE_SKILL_REQ` record `{savetime, skillid, cooltime ≈
  87–90 (seconds left at the save, 120 − 20 − 10…13), empow, mastery}` (Z23 §7.1: a skill still cooling is in every
  save, incremental or full) → `0x400A`; the row: `nSkillLevel` **0** for Violence too (D02 §6: the save writes 0),
  `nSkillExp` = mastery, `nSkillWriteTime` = `savetime` (seconds since 1970), `nSkillCoolTime` = the seconds left,
  the four `nSkillPower*` = empower. Log in again 30 s after the save: the `0x103D NC_CHAR_CLIENT_SKILL_CMD` record
  carries `cooltime = max(0, saved − offline seconds)` (Z23 §7: sent ≈ 57–60 for both). Note the client's cooldown
  display. (Dash's 60 s would be about 0 at the relogin and give no data point for the formula.)
  (5) **Two consecutive auto-saves** (capture-validation §23.5, Z01 §8.4): log in and stand still 21 minutes on one
  map (no link, no item move, no level). CharDB save bursts with `StoreType` 10 at map login + 600 s and + 1200 s
  (± 1 s). Then `&levelup 1` (a save, Z11 §7.3) and stand 11 more minutes: the next `StoreType` 10 comes **600 s
  after the `&levelup` save**, not on the old 600-s grid: every `ws_save2DB` @ FUN_00455a10 restarts the auto-save
  timer through vt 0xac0 `so_SetAutoSaveTime(cw_CurrTick, 600)` (`tAutoSaveTime` +0x2aa40, Z31's slot table;
  capture-validation §23.5).
  (6) **Charged reset failures (S21).** A has 1 empower point on a skill and spent stat points. With S21 (b)
  installed, use the Full Skill Reset Capsule: Z → D `0x9006 {…, isdelete 1}` → **`0x900A
  NC_CHARGED_SKILLEMPOW_INITIALIZE_DB_FAIL_ACK {ref, lockindex, 0x108B}`** (`nRet` 1; `{0x1092}` if the error
  reaches the ODBC call instead, D03) → C `0x900F {err}`, which the 2016 client ignores (no text, Z08 §11); the
  capsule stays in its cell and usable (lock cancelled), the empower point stays (memory and DB). Drop (b), install
  (a), use the Full Stat Reset Capsule: `0x9005` → **`0x9009 {…, 0x1083}`** (or `{0x108A}`) → C `0x900E`, silent;
  stats and capsule unchanged. Drop (a); use both capsules again: `0x9008` / `0x9007` as in `s24`.
  (7) **The scroll's destruction refused (`0x4813` 0x887 / 0x888, S21 (c) / (d)).** A has one empower point placed and
  Skill Reset Scrolls. With S21 (d) installed and a stack of **two** scrolls (the lot drops by one: `ItemAttr_Save` →
  `p_Item_SetOption` on `tItemOptions`, *inferred* from D04 §2's count bit 7), take a point back in the skill window:
  D `0x4812 {…, bUseItem 1}` → **`0x4813 {0x887}`** (`p_Skill_SetPowerAll` not called) → C `0x4814 {1, 0x887}`
  "Skill Empower failed." → the zone disconnects A (`0x0C1A {A's user number, 0x68A}` → `0x0C17 {0x68A}`, as step
  1); after the relogin the point is back where it was and both scrolls are there (the trigger rolled the lot back).
  Drop (d), install (c), keep **one** scroll (the row is deleted: `Item_Delete` → `p_Item_Delete`): the same with
  **`0x4813 {0x888}`**, `0x4814 {1, 0x888}`, the scroll still there after the relogin. Drop (c).
- **Disproved by:** (1) `0x4814 {1, 0x881}` with skill 1 named while `sp_helptext` shows the "> 5" check, no
  disconnect after a refusal, a `0x0C1A` with usrregnum 0, or the scroll still there after a refusal; (2) a
  `0x2428` for `StaBurnPainMe` between 23 and 25 min, or the switch-off finding no state (no
  `0x2428`); (3) `0x245D {7746}` at the first [03] cast after [01]; (4) a DB `nSkillCoolTime` in another unit than
  seconds, Violence's `nSkillLevel` still 1 after the save, or the relogin giving the full cooldown again; (5) no second
  `StoreType` 10 at + 1200 s, or the save after `&levelup` on the old grid;
  (6) a client text, the capsule gone, or the point removed while the trigger stands; (7) `0x4813 {0x881}` or another
  code while (c) / (d) stands, A staying in the game, or the scroll or the point changed after the relogin.

### 52. Character select and session II: what `s37b` / `s38` left open (added by X07)

- **Claims:** W01 §4.2 / §6.2 (`0x1001`, `TutorialLoginProcess`, P02-B33), W01 §3.3 (the list's "RouT" copy); D02 §3.5
  (`p_Char_Rename`, 0xD0 / 0xD1); Z11 §4.5 (`&kickout`, Z11-B6), Z01 §8.3, W01 §5.2 (`0x0C1A` → `0x0C17`); Z01 §5.2
  (SHN checksum, `0x1804 {0x147}`, 0x68E).
- **Setup:** run kit `tools/capture/52/52-server.ps1` (`prep` installs S20 and renames the `-` character, `move-b`,
  `shn-break` / `shn-restore`, `snapshot`, `cleanup -Dest`, `collect` with the server logs); A (GM, S1) and B on two
  clients, both on a map of **one** zone process for step 3's first kick (the other-zone kick is broken, Z11-B6).
- **Steps and predictions:**
  (1) **Second `0x1001` with the stale "RouT" copy (P02-B33).** Create a character, quit to the login screen (so the
  next list comes from `0x0C13` with `nTutorialState` 0), log in, select it, answer **No** to "start the tutorial?":
  `0x1001` → `0x1110` → `0x1111 {1}` → D `0x1112` → `0x1113 {0x31E8}` → C `0x1002 {0x145}` "The Map is under
  maintenance" (as `s37b` b2). **Start it again at once** (same WM session, list not reloaded): C `0x1001` → W
  **`0x1002 {0x145}` within a few ms, no `0x1110`, no `0x1112`, no CharDB `0x1004`** (the WM's copy now has state 2
  and still the map "RouT", W01 §4.2; capture-validation §22.2 *inferred*). Then leave to the server list, enter the
  world again (new `0x0C13`: state 2, RouN) and start: `0x1004` … `0x1003`, in game on RouN. This is the opposite of
  `s37b`'s rerun fix (§3.37: there the `-` character must **not** be in state 0): use another character.
  `52-server.ps1 collect` copies the server logs written since `prep` (WM, zones) next to the notes: the first
  start logs "TutorialMap Search Fail" (capture-validation
  §22.2, not on the wire); note whether the second logs it too or another line (not predicted: which check of the
  second start answers 0x145 is *inferred* from W01 §4.2).
  (2) **The 2016 `p_Char_Rename` (S20).** With S20 installed (note what its `sp_helpindex` printed), select the `-`
  character (tutorial state 2: `37b-prep.sql` writes it, §3.37), give the name of another existing character: W → D
  `0x1411` → `0x1412 {0xD1}` → C `0x1410 {slot, name, 0xD1}` "The name cannot be used.", the WM keeps the old name
  (W01 §4.1), the DB row unchanged; the name still has its `-`, so selecting it opens the forced rename window again
  *(inferred from capture-validation §22.1: the client opens it itself for a name with `-`)*: start is reached only
  through a successful rename. Then a free name: `0x1412 {0xD0}`, `0x1410 {0xD0}`, the DB
  row renamed, start works. **If `tCharacter.sID` has no unique index** (the test DB of `s52` has none, capture-validation
  §28.3), the UPDATE succeeds and two characters share the name (`0xD0`, P02-B42): then start the renamed character
  (it logs in under the shared name, `0x1007 charid` = that name) and the free-name rename is not reached. Note which
  character you started (`s52`'s notes kept the template's "selected X52Ren"). Restore S20 at the end.
  (3) **Zone-initiated disconnect with a real `usrregnum` (`&kickout`).** A types `&kickout <B's name>`: Z → W
  **`0x0C1A NC_USER_CONNECTCUT2WORLDMANAGER_CMD {0xFFFF, −1, usrregnum = B's user number, wldmanhandle = B's WM
  handle, 0x68B}`** → W → B `0x0C17 {0x68B}` (W01 §5.2: sent only when the session's user number matches; `s37b`'s
  `0x0C1A` had 0 and got none); A gets "<B> is banned" (`0x2011`, Z11 §4.5); the zone runs `so_banning` (B's save
  burst) and drops B's socket; B's client logs out by itself (`0x0C18 {0}`, "Disconnected from the server.",
  capture-validation §23.4). Then B logs in on a map of **another** zone process and A kicks again: nothing reaches B;
  A gets "… is not in game" with the name read one byte early (Z11-B6); with the zone ↔ zone ports in the filter, the
  ring `0x1068` (0x1E bytes).
  (4) **SHN mismatch.** On the server, keep a copy of one zone-side View table the zone hashes (`9Data/Shine/View/MapViewInfo.shn`;
  only the 14 View tables of the zone's "SHN - ViewData Checksum - …" log strings count, `PupView.shn` is not one),
  **change one byte inside a row** (`52-server.ps1 shn-break`, default `-Mode row`: the file keeps its length) and
  restart that zone only; log in to a map it hosts: C `0x1801` → Z → C **`0x1804 {0x147, idx}`** (idx 32 =
  MapViewInfo) "The client has been illegally manipulated. Please reinstall the client." (first login); the zone log
  `ZoneLinktoError` has `sp_NC_MAP_LOGIN_REQ : DataFail [CharID=…]`, without the table name; Z → W `0x0C1A {usrregnum
  0, 0x68E}` (the user number is set only by `0x104C`, which this path never reaches, Z01 §5.2–§5.3), so **no**
  `0x0C17`. Restore the file, restart the zone. The zone hashes the **decrypted** buffer, and the SHN cipher's key
  starts from the file length: one **appended** byte (`-Mode append`) garbles the header and crashes the zone at start
  (`std::bad_alloc` in `CDataReader::Read`, P02-B43; capture-validation §28.6), so it never reaches the login check.
- **Disproved by:** (1) a `0x1110` or a CharDB round trip on the second start, or the second start succeeding; (2)
  `0x1412 {0xD0}` for the name in use while `sp_helpindex` shows a unique `sID` index, or the WM storing the refused
  name; (3) a `0x0C1A` with usrregnum 0, no `0x0C17`, or B staying in the game; (4) a `0x1804` with another code, or
  a `0x0C17` to the client.
- **State after batch 5 (X09):** recorded as `s52` (`26_11_21_52_stale-tutorial-rename-kickout-shn`, with the prep
  output, DB snapshots and the server `-logs/` folder; capture-validation §28): account `admin` (userNo 103) with
  `X52-Dash` (charNo 7, slot 2, the prep's rename of `X37Del`) and `X52Tut` (14, created in step 1); `testaccountB`
  (104) with `X52B` (13); zone 0 (9210) and zone 1 (9212, RouVal01, the SHN zone). S20 was installed;
  `sp_helpindex tCharacter` showed only the primary key on `nCharNo` (no unique `sID`).
- **Notes corrected (`s52`, capture-validation §13, X09):** step 4 had a first attempt the notes leave out: one byte
  **appended** to MapViewInfo.shn (12:47:09) made zone 1 crash at start, twice (two minidumps, P02-B43); only the
  second break (a byte changed inside a row, the md5 the notes record) reached the login check. The zone hashes the
  decrypted buffer, not the raw file. Step 2's "selected X52Ren, Start" lines are the notes template's: the character
  started was the renamed X52-Dash (now "Test1235"), at its prep position 5874 / 6530 (the notes guessed the old
  Test1235's). Step 1: the world was entered a second time between the create and the first start (214.2–224.3).
  The world is listed as "INITIO" by the login server ("Enid" is the client text). The steps above carry these fixes.
- **Result (P02 batch 5, `s52`, capture-validation §28):**
  (1) **confirmed** (§28.2): first start `0x1001` → `0x1110` (1 byte 0xD5, P02-B28) → `0x1111 {1}` → D `0x1112` →
  `0x1113 {0x31E8}` → `0x1002 {0x145}` 20 ms after the answer, WM log "TutorialMap Search Fail" *(captured: server
  log)*; second `0x1001` → `0x1002 {0x145}` **4 ms** later, no `0x1110`, no CharDB packet, **no** WM log line: the
  `GetServiceMapZoneNo("RouT")` = −1 exit of `fc_NC_CHAR_LOGIN_REQ` @ FUN_00422be0 (the state-2 copy skips the
  tutorial path). After a new WM session (list: RouN, state 2) `0x1001` → `0x1004` → `0x1003`, in game at the create
  position without a tutorial question: P02-B33 is cleared only by a new list.
  (2) **disproved** (§28.3): the taken name was accepted: `0x140F {2, "Test1235"}` → D `0x1411` → `0x1412 {0xD0}` →
  `0x1410 {2, "Test1235", 0xD0}`, the client showed no message and listed the name; the DB has two `Test1235` rows
  (charNo 2 and 7). Nothing on the 2016 path checks a taken name (P02-B42; D02 §3.5's "a duplicate fails on the unique
  name" contradicted); `0x1412 {0xD1}` stays uncaptured. The renamed character starts normally (`0x1007 charid
  "Test1235"`, the WM resolves `0x104B` by the session handle, so the two do not mix at the map login). The free
  name and the second forced-rename window were not reached.
  (3) **confirmed** (§28.4, §28.5): same zone: `0x0C1A {0xFFFF, −1, usrregnum 104, wldmanhandle 1, 0x68B}` → WM → B
  `0x0C17 {0x68B}` 5 ms later, "Disconnected from the server.", B `0x0C18 {0}`; `so_banning`'s save burst
  (`StoreType 4`), A `0x1805 {8002}` and `0x2011 " is banned"` **without the name** (P02-B41, not predicted). Other
  zone: the ring `0x1068` zone 0 → 1 → 2 → 3 → 0 (first hop 28 bytes, then 27), A `0x2011 "\x0CX52B is not in game"`
  (the name read one byte early, Z11-B6 confirmed), B stayed in game, no `0x0C1A`.
  (4) **confirmed with the setup corrected** (§28.6): with a changed row, `0x1801` → Z → W `0x0C1A {usrregnum 0,
  wldmanhandle 0, 0x68E}`, C `0x1804 {0x147, 32}` (32 = MapViewInfo in `CShnDataFileCheckSum` @ FUN_00631450), the
  client's "illegally manipulated" text and the login screen; no `0x0C17` (the WM logs the user out when the client
  closes its connection). The zone's log line names no table. With one appended byte the zone does not start at all.
  Not predicted: A's auto-save came 599.92 s after the `&levelup` save, not after the `0x1803`: every `ws_save2DB`
  restarts the 10-min timer (§28.7).
  Of the "Disproved by" events only (2)'s first one occurred (`0x1412 {0xD0}` for the name in use; `sp_helpindex`
  showed no unique `sID` index, so this is the case the step named, not a contradiction of the unique-index rule).

### 41. Test client: crafted client packets

These need a scripted client (framing and XOR-499 cipher of `docs/protocol/README.md`; a replay of a captured
login plus one crafted packet is enough). One connection per case: several end in a disconnect.

| # | Claim | Send | Prediction | Disproved by |
|---|---|---|---|---|
| T1 | E23, X02-B10 (W04 §8.2) | to the WM, in game: `0x7001` (no body); new session: `0x7002` | the WM closes the client connection, no answer | any answer, or the session staying open |
| T2 | E18 (W03 §5) | `0x980D` from a character with no guild and no academy; then from one with an academy | `0x980E` with zeros; then the list | a close in either case (a close is predicted only with guild **and** academy set) |
| T3 | E12 (W02 §2.1) | `0x3802 {name}` on the WM link after `0x0C0F`, before a character is selected | connection closed, no `0x3807` | `0x3807` |
| T4 | Q5, Z01-B6 | to the zone: `0x0812` without item 0x9C9 in inventory cell 0; then with it (`&makeitem`, move to cell 0) | first: no packet to anyone; second: Z→D `0x0812` with the appended `buylot` part, D echoes 0x5a bytes, the item's lot in zone memory + 1 per round trip (visible at the next stack operation: disconnect `0x68C`, I3, *(inferred)*) | an answer without the item |
| T5 | V5 (Z04 §4.2) | `0x300D` with a source cell in box 2 (reward inventory) | no packet; the zone log gets the assert "Invalid Item from box" | a `0x300E` or a DB request |
| T6 | Z26 §5.5 | `0x304E NC_ITEM_USE_ACTIVESKILL_REQ` on the silver wing's cell | blast and link at once, then a skill cast (no menu) | the menu `0x3C01` |
| T7 | E30, X02-B11 | A sends `0x5401` naming B in the instant B's client process is killed (script both) | sometimes A is disconnected (the handler returns B's failed send) | never in 20 tries: the window does not exist in practice |
| T8 | Z16-B4 | `0x581A` during a KQ start from a character that did not join | linked to KQ map 0 | a refusal |
| T9 | Q3, Z01-B3 | `0x1814` with no wing in the inventory | silence | any `0x1815` |
| T10 | Z07 §2.2 | `0x105C {5}` (stat index out of range); `0x105C {0}` with the stat already at the maximum | `0x1061 {0xAC3}`; then `0x1067 {0xAC2}` (**DEC** opcode on an INC request, original bug) | `0x1061` in the second case |
| T11 | Z04 §9.1 boundaries | `0x3017` with `equip = 0xFF`; with `raw` = an empty cell; with `gift_money` = money + 1 | `0x3018 {0x8C8}`, `{0x8C9}`, `{0x8CB}`, no DB request | a DB request |
| T12 | W04-B1 | `0x2010` notice from a level-100 GM with a 140-byte text (**crashes the WM**: last test of a session) | WM stack overflow above 131 bytes | a clean `0x2011` |
| T13 | W04 §17.3 | `0x0840` loading-failure report | W→D `0x0841`, no answer | an answer |
| T14 | X02-B6 (T10 of §3.4.1) | none (server-internal); listed for completeness: needs a tournament observer, scenario 43 | – | – |
| T15 | L01 §1.6, L01-B11 (added by X05: scenario 37 step 1 cannot reach it, capture-validation §16.2) | to Login: connect, read the seed `0x0807`, send nothing, answer `0x0804` with `0x0805`; second connection: the same without answering; third: a replayed login (`0x0C65` … world list), then silence (no `0x0C1B`), answering `0x0804` | first: `0x0804` 30 s after the connect, and the `0x0805` answer closes the connection at once (the parser rejects it before the login request, L01-B11); second: `0x0804` at 30 s, close 180 s later; third: `0x0804` every 30 s, no close | no `0x0804`; the first connection staying open after its `0x0805`; a close in the third |
| T16 | Z04 §7.2, Z04-B9 (added by X05: the 2016 client never sends `0x3028`, the four pages come at the open, capture-validation §20.1) | in game: `0x3028 {page 1}` with the storage closed; with the storage window open (after the keeper's menu) `{1}`, then `{16}` | closed: **`0x3007 {0x803}`** (the DROP_REQ number, Z04-B9), no DB request; open: Z → D `0x3444 {ref, page 1, userNo, 0}` and the page answer as at the open; `{16}`: `0x3C07 {0x804}` | a DB request with the storage closed; a refusal on another opcode than `0x3007` / `0x3C07` |
| T17 | Z04 §4.2 (added by X05: the client offers 1 … lot − 1 only, capture-validation §19.3) | `0x300D` on a lot-10 stack into a free cell with lot 0; with lot 10 | `0x300E {0x442}` both times, no DB request | a `0x3434`; another code |
| T18 | Z04 §13.1, §13.2 (added by X05: at full HP the client sends no `0x5007`, capture-validation §20.3; use only if scenario 46 step 7 was refused by the client) | at the healer: `0x5001 {number = limit + 1}`; with 0 cen `0x5001 {1}`; away from every NPC `0x5001 {1}`; in the field at full HP `0x5007` | `0x5005 {0x742}`; `{0x743}`; `{0x741}`; `0x5006` (empty); no DB request in any | a `0x3441`; a `0x5008` at full HP |
| T19 | Z02 §4 (added by X05; use only if scenario 45 step 3 put no `0x2022` on the wire) | B in A's sight: `0x2022 {emoticonid of a dance, emoticonframe 5}`; `0x2022 {emoticonid 255, 0}` (no such `ActionViewInfo` row); then a third character walks into sight | A gets `0x2023 {B, emoticonid, 5}`, nothing to B; nothing for id 255; the newcomer's brief info of B (`0x1C06`) carries the emote id and frame 5 | a `0x2023` to the sender or for the unknown id |
| T20 | W01 §7.2, Z07 §1.4 (added by X05: the `0x101E` fail path, capture-validation §7.5.3; a race, as T7) | a replayed login up to the zone's seed; send the zone `0x1801` and close the **WM** connection in the same instant (script both; vary the gap 0–30 ms over 20 tries) | three outcomes by timing: WM session gone before `0x104B`: `0x104C {usrregnum −1, chrregnum −1}` and the zone drops the client (`0x689`, Z01 §8); gone between `0x104B` and `0x101C`: WM → Z **`0x101E NC_CHAR_ZONE_CHARDATAFAIL_ACK {ref, 0x141}`** (8 bytes) → C `0x1804 {u16 = the client's object handle, 0xFF}` (the handle in the code field, Z07 §1.4 original bug); gone later: a normal `0x1802`, then the WM's logout notices | a `0x101E` of another size; a `0x1804` carrying `0x141`; never in 20 tries: the window is below one WM pass and the row stays code-only |
| T21 | Z03 §5.2 (added by X05; use only for the codes scenario 39 step 7 could not put on the wire because the client refused first) | in game: `0x2440 {skill, target}` with a target handle that does not exist; with a skill the character has not learned; in a town map (`FieldList.CanSkill` 0, X2) | `0x2434 {0xFC4}` "Casting another skill now." for the unknown handle (Z03-B2); `{0xFC6}`; `{0xFC3}` | a silent drop; `0x244E` for the unlearned skill |
| T22 | `login-server.md` §3 (`0x0C65`), L00-B1; W01 §3 (added by X05: failure paths capture-validation §14 lists as never seen) | to Login: `0x0C65` with a version key one digit off; to the WM: a replayed login whose `0x0C0F` carries a changed validate key | `0x0C66` with **one payload byte** that is never written (L00-B1), no close by the server (the client quits); WM: `0x0C15 NC_USER_LOGINWORLDFAIL_ACK {0x44}` | an empty `0x0C66`; a `0x0C15` with another code; a WM close without `0x0C15` |
| T23 | Z03 §9.1, Z23 §4, Z23-B8 / B9 (added by X07: the 2016 client refused each first, capture-validation §24.3; use with scenario 51 step 1) | in game, Slice and Dice [01] (skill 0) learned with 1 damage point, no Skill Reset Scroll: (a) `0x4811 {0, plus 0, minus {damage 1}}`; (b) `{0, plus {damage 1}, minus {damage 1}}`; (c) `{0, plus {damage 5}}`; (d) `{0, plus {15, 15, 15, 15}}` (more than the level's points); (e) dead (mode 3, killed by a mob) `{0, plus {sp 1}}`; (f) after `&learnskill 1` and with one scroll: `{1, 0, minus {damage 1}}`; (g) **last test of the session**: `{0xFFFE (no such skill), 0, 0}` | (a) `0x4814 {0, 0x886}`; (b) `{0, 0x889}`; (c) `{0, 0x884}` (1 + 5 > 5); (d) `{0, 0x883}`; (e) `{0xFFFF, 0x882}`; none with a DB request, the client shows "Skill Empower failed." each time; (f) D `0x4812 {…, empower {damage 15}}` → `0x4813 {0x885}` → `0x4814 {1, 0x885}`, then `0x0C1A {A's user number, …, 0x68A}` → `0x0C17 {0x68A}` (Z23-B8); (g) the zone crashes (null `skilldatabox` entry, Z23-B9) | a DB request for (a)–(e); another code; (f) `0x881`; (g) any answer |
| T24 | Z07 §2.2 / §2.3 (added by X07; complements T10: the 2016 client counts the points and sends nothing it would refuse, capture-validation §24.4) | in game with free stat points left: (a) `0x1062 {0}` without a Stat Reset Scroll; (b) with one scroll `0x1062 {s}` for a stat `s` with no free point in it; (c) two `0x105C {0}` in one segment; (d) dead (mode 3): `0x105C {0}`, then `0x1062 {0}` with a scroll | (a) `0x1067 {0xAC6}`; (b) `0x1067 {0xAC5}`; (c) one D `0x10D1`; `0x1061 {0xAC7}` for the second (free stats locked until `0x10D2`), then `0x105F {0}` for the first; (d) `0x1061 {0xAC7}`; **no reply** to the `0x1062` (Z07 §2.3 original bug); no DB request in (a), (b), (d); no client text for any (`StatPointReqTask`) | a DB request in (a), (b), (d); a second `0x10D1` in (c); a reply to the dead `0x1062` |
| T25 | Z03 §2.6 (added by X07: **no client path**: the 2016 client export has no `0x243e` literal, and in the 2017 client `GameFrameWork::Assist` @ 0x4c8690 takes the target's last attack target locally and otherwise calls `GameFrameWork::NcBatAssistReq` @ 0x4a2130, an empty function *(pdb2017)*; capture-validation §25.5) | A, B and a mob; B targets the mob, the mob fights A: `0x243E {tanker = B's handle}`; `{tanker = the mob's handle}`; `{tanker = 0xFFFE}` (no object); B without a target: `{B's handle}` | `0x243F NC_BAT_ASSIST_ACK {target = the mob's handle}`; `{A's handle}` (the mob's current target); nothing; `{0xFFFF}`; the server changes no target (the client would follow with a TARGETTING_REQ) | an answer for the unknown handle; A's target changed by the server |

### 42. Races: drop menu, two money pick-ups, link with a dead WM session

- **Claims:** re-checks E37 / V2 (X02-B9, `ii_DropLot` is latent), I4 (pending flag is one byte), W4 (X02-B3),
  I3 (`0x68C` after a move).
- **Steps and predictions:**
  1. **Stack grows while the drop menu is open (E37).** A holds a full-stack item that asks for a drop
     confirmation (every accepted `0x3007` drop opens it, no table decides: X7), lot 5; five more of it lie on the ground
     (dropped before from a second stack). Drag the stack out (`0x3007`, lot 5), leave the confirmation open,
     pick up the ground stack (if the client lets you; else B trades or a quest gives one more), then confirm.
     Prediction: `sp_ItemDropOK` sees `req.lot < cell.lot` → Z→D `0x3419 NC_ITEMDB_DROPLOT_REQ` and a ground
     object of lot 5 **before** the answer, then `0x341A` → `0x3008 {0x301}`. Disproved by: `0x3416` (then the
     menu blocks the pick-up and the branch stays dead), or the pick-up refused while the menu is open (note
     the code).
  2. **Two money pick-ups in one tick (I4).** Kill several mobs on one spot (`&mobbreed` + `&killallmob`),
     auto pick-up on (`0x10BC {1}`). Prediction: two `0x3438` requests in flight at once on the 9411 link (the
     second sent before the first `0x3439`), both answered, final money = sum. Disproved by: the second pick
     refused or delayed until the first answer (then the callers test the flag, and I4's "open" closes as
     "tested by the callers").
  3. **Zone change with the WM session gone (W4).** A walks through a gate at the moment its WM connection
     is closed with the connection tool of scenario 38. Prediction: ZA sends `0x180B`, the save, `0x180D`; the
     WM returns nothing; the client stays connected to ZA, unable to act, until it is closed. Disproved by: a
     `0x180E`, or a zone-side timeout that frees the player.
  4. **Lot mismatch after a move (I3).** Needs S12 (change a stack's lot row in `tItemOptions` while the character is
     online). Move that stack to another cell. Prediction: C `0x300C {0x241}` first, then the disconnect `Z→W
     0x0C1A {…, 0x68C}`, client `0x0C17 {0x68C}`. Disproved by: a refused move, or no disconnect.

### 43. OPTool listener (test tool)

- **Claims:** W04 §4 (OPTool requests), §16 GM events; `login-server.md` §5.4; Z01 §3.3; D01 §2; D05 §5; Z16 §6
  tournament control; Z08 §13.
- **Setup:** a script that connects to each process's OPTool port (`ServerInfo.txt`) with the server-to-server
  handshake of S02 and sends one request. No original OPTool binary is in the repository.
- **Steps and prediction:** (1) dept 10 status and user-count requests to Login, WM, a zone, the DataServers:
  the answers of the cited sections. (2) `0x2829 NC_OPTOOL_KICK_USER_REQ {userNo}` at the WM with A in game:
  every Z `0x0C16`, A `0x0C17 {0x068F}`, OPTool `0x282A` (README §3.28). (3) `0x2827` find. (4) GM event add
  `0xD001`…: all Z `0xD00B`; delete while active: `0xD00C`, the event **keeps running** in the zones (W04-B50).
  (5) OPTool notice `0x2010` → every client `0x2011`. (6) KQ and tournament controls `0x2811`… (W04 §4.2,
  §4.4): the only way to reach the guild tournament (W03 §8, Z16 §6) on a test server without waiting for its
  schedule.
- **Disproved by:** a kick that reaches the WM client but no zone; an event withdrawn by the delete.

## 4. Boundary values (run inside the scenario named)

| Check our docs describe | Value to try | Scenario | Expected |
|---|---|---|---|
| stat index ≤ 4 (Z07 §2.2) | 5 | 41 T10 | `0x1061 {0xAC3}` |
| free points left | add with 0 left | 24 | `0x1061 {0xAC2}`, no DB request |
| upgrade at the limit / fee (Z04 §9.1) | `-u<max>`; money = fee − 1 (S2) | 22 | `0x3018 {0x8CA}` / `{0x8CB}` |
| `&getmoney` argument (Z11-B31) | −1 | 32 | money + 2³² − 1; with money near the cap (S2): note the cap behaviour, Z11 §7.4 |
| `&levelup` over the level limit (Z11-B30) | `&levelup 200` on a level-100 test character | 32 | every level applied, no limit; note the first packet that breaks the client |
| `&mobbreed` ranges (`num` 1–64, `count` ≤ 250) | `num` 0, 65; `count` 251 | 32 | the range handling of Z11 §4.2 (refused or clamped: note which) |
| `&dimension` (no range test, V24) | −1, 70000 | 14 | accepted; A leaves sight |
| shout level (`shoutlevel` of `0x0830`) | a level-1 character shouts | 14 | refused per Z02 §3.2 |
| party size (W02 §2.1) | invite with the party full (needs 5+ clients) | 15 | `0x3807` refusal; skip if clients are missing |
| guild create level 20 (W03 §2.2) | level 19, then 20 | 18 | refusal code of W03 §2.2, then success |
| booth money (Z06 §2.5) | buyer money = price − 1 (S2) | 20 | `0x680E` money code, no DB request |
| inventory full | unequip, pick up, quest reward, `&makeitem` with 0 free cells | 21, 23, 32 | `0x3013 {0x2C2}`; `0x300A {0x346}` "Inventory is full."; the DONE request is not sent (Z15 §5.1); silence |
| pick-up over a KQ item's `PickupLimit` (`KQItem.shn`) | owned + picked = limit + 1 | 21 step 11 | `0x300A {0x34A}`, text "Failed to obtain the item." (X02-B8) |
| pick-up onto a stack over `MaxLot` | X3 | 21 step 12 (recorded, `s21d`) | see the result line of §9.4 (capture-validation §21.3); the paths not tried are the next row |
| sell / use / merge with a stack over `MaxLot` (added by X05) | X3: 50 in the cell, `MaxLot` 49 | 47 step 5 | `0x3005 {0x385}`; `0x3016 {0x702}`; the 10 onto the 50: exchange `0x342B` (→ `0x342D {0x84F}` on the new table), no `0x3431` |
| merge onto a full stack (added by X05; the check is in `sp_ItemReloc` @ FUN_00536780, not in Z04 §4.1) | 20 onto 50 of `MaxLot` 50 | 46 step 1 | exchange `0x342B` → `0x342C`, no `0x3431` |
| split lot (added by X05; the client offers 1 … lot − 1) | 0 and the whole lot | 41 T17 | `0x300E {0x442}`, no DB request |
| stored lot against the zone's (added by X05) | DB lot 1 lower, then 3 lower, sell 1 (S12) | 47 step 2 | 1 lower: the sale succeeds; 3 lower: `0x3427 {0x38D}` → `0x3005 {object handle}` |
| soul-stone number and money (added by X05) | limit + 1; 0 cen | 46 step 7, 41 T18 | `0x5005 {0x742}`; `{0x743}`; no DB request |
| storage page (added by X05) | page 16; any page with the storage closed | 41 T16 | `0x3C07 {0x804}`; `0x3007 {0x803}` (Z04-B9) |
| mini-house visit distance | 101 units | 28 | refused |
| notice length (W04-B1) | 131 and 132 bytes | 41 T12 | 131 delivered; 132 corrupts the WM stack |
| premium list size (D03-B10) | 511 and 512 rows (S8) | 34 | 511 arrive |
| expired item | an item past its end time (S13) at login and at use | 21 (recorded, `s21c`: in the inventory, at the minute check); 47 steps 6–8: worn, ridden, used before the check | the result line of §8.14 (capture-validation §21.2); 47: `0x3459` at the first minute check, none while riding |
| money near the cap | `nMoney` = cap − 10 (S2), then pick up 100 | 21 | the cap rule of Z04 §3.3 |
| character in a deleted state | S14, then the character list | 37 | not in the character list (D02 §3) *(inferred)* |

## 5. What the scenarios do not reach

- **Sections with no opcode (793 of the 2 042; counts of §7 as rebuilt by X07 after batch 4; X05: 796 of 2 058):** data tables, formulas, loaders, internal classes (most of Z09,
  Z10, Z12, Z19–Z22, Z24, Z27–Z29, S02). A capture raises them only through an effect: a damage or stat number
  (Z12, Z20, Z21: note the character window before and after each equip in 21 and 22), a drop rate (X1), a
  table value (X1–X7). The rest is second reading, as `confidence.md` §2 says per row.
- **Link records only (18 sections):** GameLog and AccountLog records and the dept-16 saves appear in every
  scenario when the server links are recorded; D05 and D01 §4 are checked against all of them at once.
- **Opcodes no scenario names** (`X02-scen.py left`): `0x0C1D` / `0x0C1E` / `0x0C20` (Netmarble / Outspark login:
  no first sender in the 2016 client, E4), `0x0820`, `0x0823`–`0x0825`, `0x0832`, `0x0837`–`0x083A` (event and
  repair messages of other regions' services, no trigger found in the 2016 binaries). Since the re-run after
  batch 3 also `0x106E NC_CHAR_SOMEONEGUILDCHANGE_CMD` (if the zone sends it, a bystander of scenario 18's create /
  leave steps gets it: keep B in sight there and note it) and `0x203D NC_ACT_REINFORCE_FOLDTENT_CMD` (one past
  scenario 40's range; no step folds a tent). Two sections are left with only such opcodes.
- **Guild tournament** (W03 §8, Z16 §6): reachable only through its schedule or the OPTool controls
  (scenario 43 step 6, or `&startGT` of Z11 §6.3 on one zone).
- **Not re-checked claims that stay code-only:** W03 §2.5 helpers, W03 §3.5 client codes, W04 §12.3 (item W06;
  W04 §8.3, Z04 §13.2 and D02 §2 were read in the sweep, `confidence.md` §4.7); the *(db-backup)* rows of D01 / D02 are DB experiments (part 9).


**Batch-2 leftovers no capture is worth (X05; capture-validation §15 rows that named X05):**

- **WM → zone `0x1026` (house), `0x1028` ("maspup"), `0x102A` (emblem), `0x102B` (pet), `0x102C` (arena), `0x102D`
  (sea war):** unreachable in the 2016 set. The WM sends a blob only when its session slot is filled, the only
  writers of these six slots are the CharDB blocks `0x100F`, `0x1011`, `0x1013`–`0x1016` (W01 §6.3), and the 2016
  Character server never sends those (D02 §4: no `SetOpcode` with these values in the binary). A character with a
  house, a pet or an emblem gets the same hand-over as Test2; house, pet and guild data travel in their own
  departments (scenarios 28, 25, 18).
- **WM → zone `0x102F NC_CHAR_ZONE_CHESTINFO_CMD`:** the zone has the handler (Z07 §1.2) but the WM's hand-over
  table has no row for the slot (+0x630 is filled by `0x1018`, which the Character server never sends, and by the
  zone's `0x4014`; W01 §6.3 "not in 0x101C"). Only the save direction can be captured: Z → W `0x4014` *(inferred to follow a
  chest change)*; open one present box in scenario 46 with the links recorded and note whether it appears.
- **WM → zone `0x10B8 NC_CHAR_ZONE_LINK_FROM_CMD`:** only after the zone's `0x4019`, whose one sender is the
  guild-tournament observer entry onto another zone (`sp_Guild_Tournamnet_Observer_Enter` @ FUN_004788c0, Z12
  §7.3). It needs a tournament in `guildtournamentinfo`: scenario 43 step 6 (the OPTool controls), then `0x74D7`
  from a client or `&observerlinkto <seed>` from a GM on a zone that does not host the tournament map. Prediction:
  Z → W `0x4019 {wmHandle, charNo, map, x, y}` (0x1a bytes) before the link, W → new Z `0x10B8` (0x1e bytes with the
  ref) once after the character blobs, and `0x74DB` brings the observer back to that position. No own scenario: it
  rides on 43.
- **`0x101E`:** a race only (the WM session must vanish between `0x104B` and `0x101C` of one map login): test-client
  case T20.
- **`World::LoadMap` heartbeat call points:** which of the client's 8 call points fire in one map load is a client
  trace (a debugger on `Fiesta.bin`), not a capture: the wire shows only how many heartbeats left (already in
  capture-validation §4.4), and the servers accept a heartbeat answer at any time. Nothing in the server spec
  depends on it.
- **The extra `hpchangeorder` reads (capture-validation §9.1):** every read of the counter advances it (`vt 0x7e8`,
  Z03 §2.3; 21 candidate call sites `(… + 0x7e8)` in the zone export), and the reads that send nothing leave no packet, so a capture can only show
  the gaps it already shows (2 per hit on a mob, 3 on the player). It is a code-reading question (the callers on the
  damage path), and the client uses the value only to order HP updates *(inferred)*: a rebuild needs "strictly
  increasing per defender", which the captures confirm.
- **The client-send flush point:** read from the timing only (18–27 ms after the link packets of the same
  mob-tick event); scenario 50 separates it from the ACK effect, the exact point in the zone's pass is S02's
  process layer and changes no order within a connection.
- **The `0x10D2` single-option column names:** not a capture question, and answered from the DB backup:
  `usp_Character_getSingleOption` *(db-backup, `w00_Character.bak`)* selects `bMysteryBolt`, `bAutoPick`,
  `dRestExpLastExecuteTime`, `nChatBan` from `tCharacterSingleOption` (it inserts the row when missing; error
  −3192). So P02's `nOption1` / `nOption2` / `tTime` / `nOption4` are these four, and the timestamp is the last
  rest-exp run, not a "last save" time (it equalled the `0x101A` `dKQDate` in both captures because both were
  written at the same logout *(inferred)*).

## 6. Database setups and table experiments these scenarios need

Written in X02 part 9: the SQL is in §8, the table and config experiments in §9. Every table, column and procedure
name was read from the stored-procedure source in the backups and, where the 2016 binaries call the procedure,
checked against their `{CALL …}` strings (`bak.py cover`); the "Checked against" column of §8.1 says which.

| ID | Used by | State to create | Where |
|---|---|---|---|
| S1 | all GM steps | character admin level 100 | §8.2 |
| S2 | 20, 21, 22, §4 | character money to a chosen value (0, fee − 1, cap − 10) | §8.3 |
| S3 | 23 | a quest one kill before its end | §8.4 |
| S4 | 23 | level 20 with the job-change quest one kill before its end | §8.5 |
| S5 | 28 | mini-house creation fails at the DB | §8.6 |
| S6 | 29 | wedding state: read `tMarriage`; end a waiting time | §8.7 |
| S7 | 33 | prison minutes for a character | §8.8 |
| S8 | 34 | charged-item rows for an account (3, 511, 512, 600) | §8.9 |
| S9 | 35 | gamble coins | §8.10 |
| S10 | 37 | blocked account (`bIsBlock`) | §8.11 |
| S11 | 37 | account not login-able (`bIsLoginAble` of its `tUserAuth` row) | §8.12 |
| S12 | 42; 47 steps 1–2 (the `- 3` variant); 49 step 4 | change a stack's lot while the owner is online | §8.13 |
| S13 | 21 step 12 (recorded), §4; 47 steps 6–8 | an item past its end time | §8.14 |
| S14 | §4 | a character flagged deleted | §8.15 |
| S15 | 20, last line (D03 check 7) | a booth purchase whose money move fails at the DB | §8.16 |
| S16 | 21 step 12 (D03 check 13; recorded); 47 step 4 (fame, gamble coins) | a purchase whose attribute write fails | §8.17 |
| S17 | 47 step 3; 49 step 1 | the DB money lowered to 0 while the owner is online (added by X05) | §8.18 |
| S18 | 49 steps 2–3 | an item row removed while the owner is online (added by X05) | §8.19 |
| S19 | 49 steps 5–7 | a forced insert failure on `tItem` / `tUserMoney` for one owner (added by X05) | §8.20 |
| S20 | 52 step 2 | the 2016 `p_Char_Rename` on the test DB (added by X07) | §8.21 |
| S21 | 51 steps 6–7 | a forced failure of the charged stat / empower reset or of an item's destruction for one character (added by X07) | §8.22 |
| X1 | 39, §5 | drop experiments: limited drop `Num` runs out (V22, Z09-B20); Hunter voucher vs `SNS_DropUp` (V19) | §9.2 |
| X2 | 15, 31, 39 | party-battle maps, maps without party, instance gates, PK fields | §9.3 (read only) |
| X3 | 21 step 12 (recorded); 47 step 5 (sell, use, move-merge: §9.4 steps 4–7) | a stack that holds more than the item's `MaxLot`, then a pick-up onto it | §9.4 |
| X4 | 24 | buffs with a walk / run / attack reset condition | §9.5 (read only) |
| X5 | 30 | a kingdom quest that starts within minutes with one player | §9.6 |
| X6 | 37 | a world closed / full | §9.7 |
| X7 | 40, 42 | items with an `ItemAction` row; the drop confirmation | §9.8 (read only) |

## 7. Reach per document

Counted by `docs/plan/status/X02-scen.py cover` over the sections rated medium or low. "Reached" = names an
uncaptured opcode of at least one scenario; "link records only" = only GameLog / AccountLog / save opcodes
(§5); the last column gives the scenarios that reach most sections of the document.
Rebuilt by X05 after capture batch 3: ratings as re-run in `confidence.md` §2 (49 documents, 61 knowledge files),
scenarios 45–50 and the added steps counted (first build: 1 882 sections, 1 103 reached, 86 all captured, 1 not
reached).
Rebuilt by X07 after capture batch 4: ratings as re-run in `confidence.md` §2 (50 documents, 61 knowledge files with
a medium or low section), scenarios 51–52 and T23–T25 counted, 24 and 38 recorded (X05's build: 2 058 sections, 1 061
reached, 183 all captured, 16 link records only; now 2 042, 1 004, 225, 18; 2 not reached in both).

<!-- COVER:begin -->
| Document | Medium / low sections | No opcode | Opcodes all captured | Reached by a scenario | Link records only | Not reached | Scenarios (sections) |
|---|---|---|---|---|---|---|---|
| L00 | 12 | 3 | 2 | 7 | 0 | 0 | 37 (6), 41 (3), 43 (1) |
| L01 | 14 | 8 | 2 | 4 | 0 | 0 | 43 (3), 37 (2) |
| W01 | 24 | 2 | 3 | 19 | 0 | 0 | 37 (9), 41 (7), 43 (4), 40 (4), 38 (3) |
| W02 | 37 | 1 | 0 | 36 | 0 | 0 | 16 (21), 15 (20), 41 (3), 17 (1) |
| W03 | 54 | 2 | 1 | 51 | 0 | 0 | 18 (48), 19 (20), 37 (19), 43 (2), 41 (1) |
| W04 | 47 | 1 | 1 | 44 | 0 | 1 | 43 (11), 36 (8), 17 (8), 30 (5), 33 (5) |
| W05 | 23 | 8 | 7 | 8 | 0 | 0 | 30 (2), 40 (2), 41 (2), 43 (2), 19 (1) |
| W06 | 16 | 5 | 0 | 11 | 0 | 0 | 18 (7), 19 (3), 37 (2), 44 (1), 36 (1) |
| Z01 | 29 | 8 | 5 | 16 | 0 | 0 | 37 (9), 41 (7), 27 (6), 52 (5), 28 (3) |
| Z02 | 27 | 3 | 2 | 22 | 0 | 0 | 40 (7), 14 (6), 36 (6), 21 (4), 30 (4) |
| Z03 | 36 | 17 | 7 | 12 | 0 | 0 | 24 (9), 39 (3), 41 (1), 32 (1), 19 (1) |
| Z04 | 53 | 5 | 7 | 41 | 0 | 0 | 21 (16), 22 (12), 30 (4), 49 (4), 41 (4) |
| Z05 | 45 | 6 | 1 | 38 | 0 | 0 | 21 (20), 49 (9), 22 (8), 28 (7), 18 (6) |
| Z06 | 23 | 2 | 0 | 21 | 0 | 0 | 20 (11), 35 (11), 43 (3), 21 (1) |
| Z07 | 39 | 5 | 4 | 30 | 0 | 0 | 28 (13), 40 (4), 29 (4), 37 (3), 39 (3) |
| Z08 | 23 | 2 | 0 | 21 | 0 | 0 | 15 (5), 23 (5), 39 (4), 16 (3), 17 (3) |
| Z09 | 217 | 112 | 27 | 76 | 2 | 0 | 30 (35), 14 (13), 18 (11), 31 (8), 40 (7) |
| Z10 | 31 | 29 | 1 | 1 | 0 | 0 | 37 (1) |
| Z11 | 55 | 22 | 10 | 23 | 0 | 0 | 30 (7), 32 (7), 52 (4), 18 (3), 21 (3) |
| Z12 | 32 | 15 | 12 | 5 | 0 | 0 | 24 (2), 27 (2), 29 (1) |
| Z13 | 68 | 8 | 3 | 56 | 1 | 0 | 28 (17), 26 (15), 25 (14), 29 (11), 14 (6) |
| Z14 | 24 | 7 | 1 | 16 | 0 | 0 | 31 (7), 19 (5), 16 (4), 23 (3), 18 (2) |
| Z15 | 46 | 16 | 0 | 30 | 0 | 0 | 23 (30), 27 (1), 30 (1) |
| Z16 | 43 | 6 | 2 | 35 | 0 | 0 | 18 (22), 30 (13), 36 (2), 41 (2), 27 (1) |
| Z17 | 31 | 18 | 3 | 9 | 1 | 0 | 22 (6), 40 (4), 21 (1), 26 (1) |
| Z18 | 33 | 15 | 4 | 14 | 0 | 0 | 39 (4), 24 (3), 37 (2), 14 (2), 17 (2) |
| Z19 | 17 | 17 | 0 | 0 | 0 | 0 |  |
| Z20 | 20 | 19 | 1 | 0 | 0 | 0 |  |
| Z21 | 27 | 20 | 4 | 3 | 0 | 0 | 21 (2), 40 (1), 39 (1) |
| Z22 | 47 | 28 | 16 | 3 | 0 | 0 | 39 (2), 24 (1) |
| Z23 | 29 | 14 | 12 | 3 | 0 | 0 | 24 (2), 27 (1), 41 (1), 34 (1), 51 (1) |
| Z24 | 32 | 22 | 0 | 10 | 0 | 0 | 21 (6), 34 (4), 27 (3), 40 (1) |
| Z25 | 28 | 12 | 10 | 6 | 0 | 0 | 24 (5), 27 (1), 41 (1) |
| Z26 | 19 | 3 | 8 | 8 | 0 | 0 | 27 (6), 21 (5), 41 (4) |
| Z27 | 31 | 30 | 0 | 0 | 1 | 0 |  |
| Z28 | 24 | 18 | 1 | 5 | 0 | 0 | 35 (5), 21 (1) |
| Z29 | 11 | 11 | 0 | 0 | 0 | 0 |  |
| Z30 | 11 | 2 | 0 | 9 | 0 | 0 | 21 (3), 37 (2), 44 (2), 19 (2), 27 (2) |
| Z31 | 78 | 57 | 11 | 9 | 1 | 0 | 21 (5), 37 (2), 40 (2), 28 (2), 18 (1) |
| Z32 | 40 | 18 | 1 | 21 | 0 | 0 | 35 (20), 21 (2) |
| D01 | 17 | 4 | 4 | 9 | 0 | 0 | 37 (8), 43 (2), 38 (1), 36 (1) |
| D02 | 24 | 4 | 4 | 16 | 0 | 0 | 37 (6), 29 (5), 28 (4), 36 (4), 23 (4) |
| D03 | 43 | 7 | 1 | 35 | 0 | 0 | 21 (18), 49 (9), 22 (6), 47 (5), 23 (5) |
| D04 | 25 | 1 | 0 | 24 | 0 | 0 | 18 (9), 19 (6), 17 (5), 39 (4), 36 (4) |
| D05 | 25 | 6 | 1 | 10 | 8 | 0 | 39 (3), 29 (2), 43 (2), 30 (1), 40 (1) |
| D06 | 49 | 19 | 4 | 25 | 0 | 1 | 37 (10), 18 (4), 21 (3), 28 (3), 36 (3) |
| D07 | 15 | 4 | 1 | 10 | 0 | 0 | 19 (9), 18 (3) |
| D08 | 47 | 23 | 4 | 19 | 1 | 0 | 43 (8), 37 (4), 34 (4), 19 (3), 22 (3) |
| S02 | 32 | 28 | 1 | 3 | 0 | 0 | 32 (3), 14 (1) |
| knowledge L01 | 2 | 0 | 1 | 1 | 0 | 0 | 37 (1), 43 (1) |
| knowledge W01 | 2 | 0 | 0 | 2 | 0 | 0 | 40 (1), 36 (1), 37 (1) |
| knowledge W02 | 2 | 1 | 0 | 1 | 0 | 0 | 15 (1), 16 (1), 17 (1) |
| knowledge W03 | 2 | 0 | 0 | 2 | 0 | 0 | 18 (2), 19 (1), 37 (1) |
| knowledge W04 | 2 | 0 | 0 | 2 | 0 | 0 | 30 (2), 36 (2), 40 (2) |
| knowledge W05 | 2 | 0 | 0 | 2 | 0 | 0 | 19 (1), 23 (1) |
| knowledge W06 | 3 | 0 | 0 | 3 | 0 | 0 | 18 (2), 19 (2), 37 (1), 44 (1) |
| knowledge Z01 | 7 | 4 | 1 | 2 | 0 | 0 | 36 (2), 19 (1), 29 (1), 27 (1), 33 (1) |
| knowledge Z02 | 3 | 0 | 1 | 2 | 0 | 0 | 26 (1), 28 (1), 14 (1), 21 (1), 36 (1) |
| knowledge Z03 | 1 | 0 | 1 | 0 | 0 | 0 |  |
| knowledge Z04 | 5 | 3 | 0 | 2 | 0 | 0 | 21 (1), 24 (1), 36 (1), 39 (1), 18 (1) |
| knowledge Z05 | 3 | 0 | 1 | 2 | 0 | 0 | 21 (2), 49 (2), 15 (1), 41 (1), 17 (1) |
| knowledge Z06 | 3 | 1 | 1 | 1 | 0 | 0 | 20 (1), 21 (1), 35 (1), 43 (1) |
| knowledge Z07 | 3 | 0 | 0 | 3 | 0 | 0 | 24 (1), 29 (1), 40 (1), 39 (1), 28 (1) |
| knowledge Z08 | 2 | 0 | 0 | 2 | 0 | 0 | 15 (2), 16 (2), 39 (2), 31 (1), 17 (1) |
| knowledge Z09 | 3 | 0 | 0 | 3 | 0 | 0 | 23 (2), 24 (2), 30 (2), 18 (1), 21 (1) |
| knowledge Z10 | 5 | 5 | 0 | 0 | 0 | 0 |  |
| knowledge Z11 | 4 | 1 | 2 | 1 | 0 | 0 | 24 (1), 25 (1), 29 (1), 30 (1), 32 (1) |
| knowledge Z12 | 4 | 1 | 1 | 2 | 0 | 0 | 24 (2), 27 (1), 37 (1) |
| knowledge Z13 | 9 | 0 | 1 | 8 | 0 | 0 | 29 (4), 26 (2), 22 (2), 28 (1), 21 (1) |
| knowledge Z14 | 1 | 0 | 0 | 1 | 0 | 0 | 15 (1), 16 (1), 18 (1), 19 (1), 23 (1) |
| knowledge Z15 | 3 | 0 | 1 | 2 | 0 | 0 | 23 (2) |
| knowledge Z16 | 3 | 1 | 0 | 2 | 0 | 0 | 18 (2), 30 (1) |
| knowledge Z17 | 5 | 1 | 1 | 2 | 1 | 0 | 22 (2), 40 (1) |
| knowledge Z18 | 1 | 0 | 0 | 1 | 0 | 0 | 27 (1), 37 (1), 41 (1) |
| knowledge Z19 | 1 | 1 | 0 | 0 | 0 | 0 |  |
| knowledge Z20 | 3 | 3 | 0 | 0 | 0 | 0 |  |
| knowledge Z21 | 5 | 4 | 0 | 1 | 0 | 0 | 40 (1) |
| knowledge Z22 | 5 | 5 | 0 | 0 | 0 | 0 |  |
| knowledge Z23 | 5 | 2 | 2 | 1 | 0 | 0 | 24 (1) |
| knowledge Z24 | 4 | 2 | 0 | 2 | 0 | 0 | 34 (2), 21 (1), 40 (1) |
| knowledge Z25 | 3 | 1 | 0 | 2 | 0 | 0 | 24 (2) |
| knowledge Z26 | 4 | 0 | 1 | 3 | 0 | 0 | 21 (2), 27 (2), 41 (2) |
| knowledge Z27 | 2 | 1 | 1 | 0 | 0 | 0 |  |
| knowledge Z28 | 6 | 5 | 1 | 0 | 0 | 0 |  |
| knowledge Z29 | 5 | 5 | 0 | 0 | 0 | 0 |  |
| knowledge Z30 | 2 | 0 | 0 | 2 | 0 | 0 | 27 (1), 37 (1), 21 (1), 44 (1) |
| knowledge Z31 | 4 | 0 | 0 | 3 | 1 | 0 | 21 (3), 20 (2), 18 (1), 28 (1), 19 (1) |
| knowledge Z32 | 5 | 2 | 1 | 2 | 0 | 0 | 35 (2) |
| knowledge D01 | 3 | 0 | 1 | 2 | 0 | 0 | 43 (2), 36 (1), 37 (1) |
| knowledge D02 | 3 | 1 | 0 | 2 | 0 | 0 | 37 (2), 38 (1) |
| knowledge D03 | 3 | 1 | 0 | 2 | 0 | 0 | 20 (2), 23 (2), 35 (2), 17 (1), 21 (1) |
| knowledge D04 | 4 | 1 | 0 | 3 | 0 | 0 | 19 (2), 18 (1), 36 (1), 37 (1), 30 (1) |
| knowledge D05 | 4 | 2 | 0 | 1 | 1 | 0 | 43 (1) |
| knowledge D06 | 8 | 5 | 0 | 3 | 0 | 0 | 37 (3), 18 (1), 19 (1), 25 (1), 28 (1) |
| knowledge D07 | 2 | 0 | 0 | 2 | 0 | 0 | 19 (2) |
| knowledge D08 | 7 | 2 | 1 | 4 | 0 | 0 | 43 (3), 35 (2), 37 (1), 41 (1), 19 (1) |
| knowledge S01 | 21 | 8 | 2 | 11 | 0 | 0 | 39 (6), 32 (5), 37 (5), 35 (5), 17 (4) |
| knowledge S02 | 5 | 4 | 0 | 1 | 0 | 0 | 32 (1) |
| knowledge C01 | 11 | 2 | 1 | 8 | 0 | 0 | 41 (3), 30 (3), 37 (3), 40 (3), 18 (2) |
| knowledge C02 | 11 | 4 | 1 | 6 | 0 | 0 | 37 (6), 41 (4), 21 (4), 35 (4), 19 (4) |
| knowledge P01 | 6 | 2 | 1 | 3 | 0 | 0 | 37 (3) |
| knowledge P03 | 5 | 1 | 2 | 2 | 0 | 0 | 37 (2) |
| knowledge P04 | 2 | 1 | 0 | 1 | 0 | 0 | 37 (1) |
| knowledge X01 | 4 | 2 | 0 | 2 | 0 | 0 | 43 (2), 44 (2), 23 (1), 30 (1), 33 (1) |
| knowledge X02 | 4 | 3 | 0 | 1 | 0 | 0 | 14 (1), 15 (1), 17 (1), 18 (1), 19 (1) |
| knowledge X03 | 2 | 2 | 0 | 0 | 0 | 0 |  |
| knowledge X04 | 4 | 1 | 2 | 1 | 0 | 0 | 37 (1) |
| knowledge X05 | 7 | 1 | 0 | 6 | 0 | 0 | 21 (4), 39 (4), 41 (4), 47 (4), 14 (4) |
| knowledge X07 | 4 | 0 | 0 | 4 | 0 | 0 | 24 (4), 41 (4), 34 (2), 51 (2), 29 (1) |
| knowledge K01 | 15 | 8 | 7 | 0 | 0 | 0 |  |
| **Total** | 2042 | 793 | 225 | 1004 | 18 | 2 | |
<!-- COVER:end -->

## 8. Database setups (S1–S21)

**Run these on the test server only.** They change or delete rows, two of them install a trigger that makes the
server fail on purpose, and none of them was run: no SQL Server holds these backups yet (`db-backups.md`), so
every statement is written from procedure source, not from a schema. Read the save query's output before running
the change; if a column is reported missing, stop and report it (that is a finding, not a typo to work around).

### 8.1 Conventions and what was verified

- **Databases** as the shipped `9Data/ServerInfo/ServerInfo.txt` names them (`ODBC_INFO` rows): `Account`,
  `AccountLog`, `StatisticsData`, `w00_Character`, `w00_GameLog`. The Character DB's own wrappers reach the
  account data as `Account.dbo.…` (`usp_ChargeItem_GetList`), so both sit on one SQL Server instance.
  The recording install of batch 3 names the Character DB **`World00_Character`** (the `tools/capture/21` scripts
  say `USE World00_Character`): replace `w00_Character` in every script of this chapter, S17–S19 included, by the
  name the install's `ServerInfo.txt` gives (X05 review).
- **Placeholders:** `TestCharA` / `TestCharB` = character names (`tCharacter.sID`), `testaccount` = login name
  (`tUser.sUserID`). Every script starts by resolving them. Only some of the scripts stop by themselves when the name is not found
  (S4, S6, S7 and S10–S15 do not): check that the save query returned a row before running the change.
- **Save / restore:** each setup copies the rows it changes into a table named `dbo.X02_save_<n>` (our name, not
  a server table) with `SELECT … INTO`, and the restore block copies them back and drops that table. Run the
  restore before the next setup that uses the same number. `SELECT … INTO` fails when the save table already
  exists: that protects the first copy.
- **Two parts per script,** separated by the `-- restore` comment: run the part above it before the test and the
  part below it after. The restore part uses only the save table, so it runs in a new query window. Where a
  script says "run this line first" or "from the list", run the `SELECT`, fill in the variable, then run the rest. S13 has no restore part: the test consumes the item.
- **Who must be offline** is stated per setup. "Account at the login screen" = no character of the account in
  the game **and** the client back at the login screen or closed: the WM holds the avatar list from world select
  on (D02 §3.1, W01 §3), the zone holds the whole character from `0x1004` on and writes parts of it back
  (README §3.13). No setup needs a server process stopped; §9 does.
- Two facts decide what is safe to edit while the character is offline: the 2016 Character server never calls
  `p_Char_SetAllData`, `p_Char_SetAdminLevel` or `p_Char_MoneySet` (they exist in both backups but are missing
  from `bak.py cover character`), so nothing writes `nAdminLevel` or an absolute `nMoney` back; money is kept as
  deltas only (`confidence.md` E41).

| Name used below | Read from | Checked against |
|---|---|---|
| `tCharacter` { `nCharNo`, `nUserNo`, `sID`, `nLevel`, `nMoney`, `nAdminLevel`, `nPrisonMin`, `sLoginZone`, `nLoginZoneX`, `nLoginZoneY`, `nLoginZoneD`, `bDeleted`, `dDeletedDate` } | `p_Char_GetAllData` (both Character backups, same text) | `{CALL p_Char_GetAllData(?)}`: 1 parameter, matches |
| `tCharacterShape` { `nCharNo`, `nClass` } | `p_Char_ChangeClass`, `p_Char_GetLoginData` | called by the binary (D02 §7.1, §3.2) |
| `tQuest` { `nCharNo`, `nQuestNo`, `nStatus`, `sData` varbinary(100) } | `p_Quest_Set`, `p_Quest_GetAllDoing` | `{CALL p_Quest_Set(?,?,?,?,?)}` @ FUN_004530e0 binds parameter 4 as 100 bytes from the record's `Data` |
| `tItem` { `nItemKey`, `nOwner`, `nStorageType`, `nStorage`, `nItemID`, `nFlags` } | `p_Item_Create` | `{CALL p_Item_Create(?,?,?,?,?,?,?)}` @ FUN_00461270 |
| `tItemOptions` { `nItemKey`, `nOptionType`, `nOptionData` } | `p_Item_SetOption` | 4 parameters, matches; option types from the save switch (D03 §1.3) |
| `tMarriage` { `nCharNo`, `nPartnerCharNo`, `nStatus`, `nSubStatus`, `dWhen`, `dSubWhen`, `nMarriageCount`, `nDivorceCancel` } | `p_Char_WeddingStatus_Get` / `_Set` | 1 and 8 parameters, match |
| `p_Prison_Add2`, `p_Prison_Alter2` (6 parameters), `tPrison` { `nCharID`, `nMinute`, `sReason`, `sGmID`, `sRemark`, `dPrisonDate` } | both Character backups | both called with 6 parameters (D04 §7) |
| `tGambleCoin` { `nCharNo`, `nCoin`, `sys_update_date` } | `usp_Gamble_addCoin`, `usp_Gamble_getCoin` | `w00_Character.bak` only (the 2017 database) *(db-backup)*; `usp_Gamble_getCoin` is called with 2 parameters, matches |
| `Account.dbo.tChargeItem` { `rowNo`, `userNo`, `orderNo`, `goodsNo`, `amount`, `isDraw`, `registerDate`, `drawDate` }, `usp_Charge_ItemInsert` (5 parameters) | `Account.bak` | not called by a game server (the item shop's procedure); the servers read the table through `usp_ChargeItem_GetList` (1 parameter, matches) |
| `Account.dbo.tUser` { `nUserNo`, `sUserID`, `bIsBlock`, `bIsDelete`, `nAuthID` }, `tUserAuth` { `nAuthID`, `sAuthName`, `bIsLoginAble` }, `tUserBlock` { `nBlockNo`, `nUserNo`, `nType`, `dEndDate`, `bStatus` } | `usp_User_loginGame`, `usp_User_chkBlock`, `usp_User_getAuthList` | `{CALL usp_User_loginGame(?,?,?,?,?,?)}`: 6 parameters, matches |

Not verified, and said so where it matters: column types beyond what a procedure declares, columns the
procedures never name (a NOT NULL column without a default would break an `INSERT` written here; only §8.10 has
one), constraints, and triggers that may already exist on `tItem` (D03 §1.1 suspects one for the option rows).

### 8.2 S1: admin level

Account at the login screen. Seeing `0x10C6 {nAdminLevel 100}` in the next login burst confirms it (§1).

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
IF @c IS NULL RAISERROR('character not found', 16, 1)
ELSE BEGIN
    SELECT nCharNo, sID, nAdminLevel INTO dbo.X02_save_1 FROM tCharacter WHERE nCharNo = @c;
    UPDATE tCharacter SET nAdminLevel = 100 WHERE nCharNo = @c;
END
-- restore
UPDATE c SET nAdminLevel = s.nAdminLevel FROM tCharacter c JOIN dbo.X02_save_1 s ON s.nCharNo = c.nCharNo;
DROP TABLE dbo.X02_save_1;
```

### 8.3 S2: money

Account at the login screen (the zone holds the amount while the character is in the game and the Character
server applies deltas to the row: an edit made online is neither seen nor kept consistent). `nMoney` is a
`bigint` (`p_Char_MoneySet @nSetMoney bigint`). Put the value the boundary row of §4 names in `@money`.

```sql
USE w00_Character;
DECLARE @money bigint = 0;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
IF @c IS NULL RAISERROR('character not found', 16, 1)
ELSE BEGIN
    SELECT nCharNo, nMoney INTO dbo.X02_save_2 FROM tCharacter WHERE nCharNo = @c;
    UPDATE tCharacter SET nMoney = @money WHERE nCharNo = @c;
END
-- restore
UPDATE c SET nMoney = s.nMoney FROM tCharacter c JOIN dbo.X02_save_2 s ON s.nCharNo = c.nCharNo;
DROP TABLE dbo.X02_save_2;
```

`&getmoney <n>` (§1) reaches most values faster; the SQL is for 0 and for values just under the cap, which a GM
command can only approach from below.

### 8.4 S3: a quest one kill before its end

A quest record is `tQuest.sData` = the 29-byte `PLAYER_QUEST_DATA` *(pdb2016)* followed by 71 bytes of stack
garbage (D04-B1): `StartTime` i64 @0, `EndTime` i64 @8, `RepeatCount` u32 @0x10, `ProgressStep` u8 @0x14,
`End_NPCMobCount[5]` u8 @0x15, flags @0x1A, `End_RunningTimeSec` u16 @0x1B. `nStatus` 6 = `PQS_ING`. The kill
counters are the five bytes at 0x15 (T-SQL position 22, one-based); which counter belongs to which mob follows
the order of the quest's kill conditions *(inferred)*.

Steps: accept the quest in the game (that writes the row), read the needed count off the quest window, go to
the login screen, then set the first counter to count − 1:

```sql
USE w00_Character;
DECLARE @quest int = 0;          -- nQuestNo, from the SELECT below
DECLARE @count tinyint = 0;      -- needed kills - 1
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT nQuestNo, nStatus, sData FROM tQuest WHERE nCharNo = @c AND nStatus = 6;   -- run this line first
IF @quest <> 0 BEGIN
    SELECT nCharNo, nQuestNo, nStatus, sData INTO dbo.X02_save_3 FROM tQuest WHERE nCharNo = @c AND nQuestNo = @quest;
    UPDATE tQuest
       SET sData = SUBSTRING(sData, 1, 21) + CAST(@count AS binary(1)) + SUBSTRING(sData, 23, DATALENGTH(sData) - 22)
     WHERE nCharNo = @c AND nQuestNo = @quest AND DATALENGTH(sData) >= 29;
END
-- restore
UPDATE q SET nStatus = s.nStatus, sData = s.sData
  FROM tQuest q JOIN dbo.X02_save_3 s ON s.nCharNo = q.nCharNo AND s.nQuestNo = q.nQuestNo;
DROP TABLE dbo.X02_save_3;
```

Prediction for the next login: `0x1021` carries the record with the edited counter, and one kill produces the
`0x440D` that completes the condition. Disproved by: the counter back at its old value (then the zone checks it
against something else), or the quest finishing only after the full count.

### 8.5 S4: level 20 with the job-change quest one kill before its end

The first job change is not a state the DB can grant: the zone sends `0x1056 NC_CHAR_CLASSCHANGE_REQ` from the
quest script (`so_ply_FirstJobChange` @ FUN_0049fa70, the `SCENARIO` commands of Z15 §5; quests 60006, 60010,
60011 … in the 2016 data) and `p_Char_ChangeClass` then writes `tCharacterShape.nClass`. So: `&levelup` to 20
(§1), accept the job quest at its NPC, then S3 on that quest. Save the class first, so the character can be
used again:

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT nCharNo, nClass INTO dbo.X02_save_4 FROM tCharacterShape WHERE nCharNo = @c;
-- restore (account at the login screen; the quest rows are restored by S3's block; learned skills are not removed
-- and the level and experience gained by `&levelup` stay: use a character you do not need at its old level)
UPDATE t SET nClass = s.nClass FROM tCharacterShape t JOIN dbo.X02_save_4 s ON s.nCharNo = t.nCharNo;
DROP TABLE dbo.X02_save_4;
```

### 8.6 S5: mini-house creation fails at the DB

`0x3467` creates one item row through `p_Item_Create` (D03 §7.1). A trigger that rolls back every insert for
the test character makes that call fail. The wrapper @ FUN_00461270 treats any ODBC result other than success
as failure and logs `ERROR - CSQLPItem::p_Item_Create, ret(%d), nRet(%d)`; that the driver reports a
trigger rollback as such a result is *(inferred)*: the log line is the check that the setup worked.
The character may be online: install the trigger just before step 7 of scenario 28 and drop it right after.
While it exists the character can receive no item at all (pick-up, purchase, `&makeitem` fail too).

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
DECLARE @sql nvarchar(max) = N'CREATE TRIGGER dbo.X02_tItem_fail ON dbo.tItem AFTER INSERT AS
IF EXISTS (SELECT 1 FROM inserted WHERE nOwner = ' + CAST(@c AS nvarchar(12)) + N')
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR(''X02 forced failure (S5)'', 16, 1);
END';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- restore
DROP TRIGGER dbo.X02_tItem_fail;
```

Prediction: D answers `0x3469 {lock, owner}`; the client gets nothing (V3). Guild storage rows have the guild
number in `nOwner` and account storage rows the user number (D03 §1.1): a guild or user whose number equals
`@c` is hit too while the trigger exists.

### 8.7 S6: wedding state

Read at any time; change only with **both** partners at the login screen (the zone loads the row with `0x1080`
and writes the whole row back with `0x1082`, D02 §11).

```sql
USE w00_Character;
SELECT c.sID, m.* FROM tMarriage m JOIN tCharacter c ON c.nCharNo = m.nCharNo
 WHERE c.sID IN (N'TestCharA', N'TestCharB');

-- end a waiting time (proposal 3 days, divorce 7 days, divorce by agreement 10 minutes: D02 §11) in one minute
SELECT m.* INTO dbo.X02_save_6 FROM tMarriage m JOIN tCharacter c ON c.nCharNo = m.nCharNo
 WHERE c.sID IN (N'TestCharA', N'TestCharB');
UPDATE m SET dSubWhen = DATEADD(minute, 1, GETDATE())
  FROM tMarriage m JOIN dbo.X02_save_6 s ON s.nCharNo = m.nCharNo;
-- restore
UPDATE m SET nPartnerCharNo = s.nPartnerCharNo, nStatus = s.nStatus, nSubStatus = s.nSubStatus, dWhen = s.dWhen,
             dSubWhen = s.dSubWhen, nMarriageCount = s.nMarriageCount, nDivorceCancel = s.nDivorceCancel
  FROM tMarriage m JOIN dbo.X02_save_6 s ON s.nCharNo = m.nCharNo;
DROP TABLE dbo.X02_save_6;
```

Which of `dWhen` / `dSubWhen` the zone compares for each status is Z07 §5.1's reading (rated low, wedding status
names not re-checked): the scenario's prediction is that the state moves on within a minute of the next login;
if it does not, repeat with `dWhen`.

### 8.8 S7: prison

Use the procedures the Character server itself calls for an offline target (`0x7C0B` / `0x7C10` with
`nImprisonRegNum` 0, D04 §7). Target character at the login screen (the zone counts the minutes down and saves
them with `0x7C0D`).

```sql
USE w00_Character;
DECLARE @err smallint;
SELECT nCharNo, nPrisonMin, sLoginZone, nLoginZoneX, nLoginZoneY, nLoginZoneD INTO dbo.X02_save_7
  FROM tCharacter WHERE sID = N'TestCharB' AND bDeleted = 0;
EXEC p_Prison_Add2 N'X02', N'TestCharB', 5, N'test', N'X02 scenario 33', @err OUTPUT;
SELECT @err AS err;   -- 0 ok, 1 no such character, 2 already in prison
-- restore
UPDATE c SET nPrisonMin = s.nPrisonMin, sLoginZone = s.sLoginZone, nLoginZoneX = s.nLoginZoneX,
             nLoginZoneY = s.nLoginZoneY, nLoginZoneD = s.nLoginZoneD
  FROM tCharacter c JOIN dbo.X02_save_7 s ON s.nCharNo = c.nCharNo;
DELETE p FROM tPrison p JOIN dbo.X02_save_7 s ON s.nCharID = p.nCharID WHERE p.sGmID = N'X02';
DROP TABLE dbo.X02_save_7;
```

The procedure moves the login position to `EldPri` (896, 1122). Boundary values for §4: 1 minute, 32767 (the
parameter is a `smallint`), and `p_Prison_Alter2 … 0 …` on a prisoner (release to `Rou` 5963 / 9793).

### 8.9 S8: charged-item rows

`usp_Charge_ItemInsert(@userNo, @orderNo, @goodsNo, @amount, @RET OUTPUT)` is the shop's own insert; `@orderNo`
0 skips its duplicate test. `goodsNo` must be a number the zone can turn into items: `ItemShop.shn` has
`{goodsNo, InxName, Lot}` rows (10002 = `HPIncrease1` × 20); that this table is the zone's goods table
`DAT_0d5745e8` of Z04 §8 is *(inferred)* from the column name. The list is read each time the premium storage
is opened (`0x3463`), so the account may stay online; close the storage window first.

```sql
USE Account;
DECLARE @n int = 600;            -- 3, 511, 512 or 600
DECLARE @u int = (SELECT nUserNo FROM tUser WHERE sUserID = N'testaccount' AND bIsDelete = 0);
DECLARE @ret int, @i int = 0;
IF @u IS NULL RAISERROR('account not found', 16, 1)
ELSE BEGIN
    SELECT @u AS userNo, ISNULL(MAX(rowNo), 0) AS lastRow INTO dbo.X02_save_8 FROM tChargeItem;
    WHILE @i < @n BEGIN
        EXEC usp_Charge_ItemInsert @u, 0, 10002, 1, @ret OUTPUT;
        SET @i = @i + 1;
    END
    SELECT COUNT(*) AS undrawn FROM tChargeItem WHERE userNo = @u AND isDraw = 0;
END
-- restore (also removes rows of this account that were withdrawn in the test)
DELETE t FROM tChargeItem t JOIN dbo.X02_save_8 s ON t.userNo = s.userNo AND t.rowNo > s.lastRow;
DROP TABLE dbo.X02_save_8;
```

Prediction (D03-B10): with 512 or 600 rows the `0x3464` parts carry 511 rows in all; with 3 or 511 every row.

### 8.10 S9: gamble coins

Character at the login screen. The table exists only in the 2017 backup *(db-backup)*; if the `SELECT` fails,
the 2016 database keeps coins elsewhere and this setup does not apply (use the coin exchange NPC instead).

```sql
USE w00_Character;
DECLARE @coin bigint = 1000;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT @c AS nCharNo, (SELECT nCoin FROM tGambleCoin WHERE nCharNo = @c) AS nCoin INTO dbo.X02_save_9;
IF EXISTS (SELECT 1 FROM tGambleCoin WHERE nCharNo = @c)
    UPDATE tGambleCoin SET nCoin = @coin WHERE nCharNo = @c;
ELSE
    INSERT INTO tGambleCoin (nCharNo, nCoin) VALUES (@c, @coin);   -- the column list usp_Gamble_addCoin uses
-- restore
UPDATE g SET nCoin = s.nCoin FROM tGambleCoin g JOIN dbo.X02_save_9 s ON s.nCharNo = g.nCharNo WHERE s.nCoin IS NOT NULL;
DELETE g FROM tGambleCoin g JOIN dbo.X02_save_9 s ON s.nCharNo = g.nCharNo WHERE s.nCoin IS NULL;
DROP TABLE dbo.X02_save_9;
```

### 8.11 S10: blocked account

Read at every login (`usp_User_loginGame`), nothing caches it: the account only has to be at the login screen
for the test itself. With no active `tUserBlock` row the flag stays set (`usp_User_chkBlock` clears it only for
an expired timed row).

```sql
USE Account;
SELECT nUserNo, bIsBlock INTO dbo.X02_save_10 FROM tUser WHERE sUserID = N'testaccount' AND bIsDelete = 0;
SELECT * FROM tUserBlock WHERE nUserNo = (SELECT nUserNo FROM dbo.X02_save_10) AND bStatus = 1;   -- expect no row
UPDATE u SET bIsBlock = 1 FROM tUser u JOIN dbo.X02_save_10 s ON s.nUserNo = u.nUserNo;
-- restore
UPDATE u SET bIsBlock = s.bIsBlock FROM tUser u JOIN dbo.X02_save_10 s ON s.nUserNo = u.nUserNo;
DROP TABLE dbo.X02_save_10;
```

### 8.12 S11: account not login-able

`bIsLoginAble` belongs to the authority group (`tUserAuth`), not to the account: clearing it locks out **every
account of that `nAuthID`** until the restore. Do it when no one else uses the test server, or first look for a
group that is already not login-able and move only the test account into it (second block).

```sql
USE Account;
SELECT nAuthID, sAuthName, bIsLoginAble FROM tUserAuth;                       -- look first
SELECT u.nUserNo, u.nAuthID AS userAuth, a.nAuthID, a.bIsLoginAble INTO dbo.X02_save_11
  FROM tUser u JOIN tUserAuth a ON a.nAuthID = u.nAuthID WHERE u.sUserID = N'testaccount' AND u.bIsDelete = 0;
UPDATE a SET bIsLoginAble = 0 FROM tUserAuth a JOIN dbo.X02_save_11 s ON s.nAuthID = a.nAuthID;
-- or, when a group <g> with bIsLoginAble = 0 exists:  UPDATE u SET nAuthID = <g> FROM tUser u JOIN dbo.X02_save_11 s ON s.nUserNo = u.nUserNo;
-- restore (covers both variants)
UPDATE a SET bIsLoginAble = s.bIsLoginAble FROM tUserAuth a JOIN dbo.X02_save_11 s ON s.nAuthID = a.nAuthID;
UPDATE u SET nAuthID = s.userAuth FROM tUser u JOIN dbo.X02_save_11 s ON s.nUserNo = u.nUserNo;
DROP TABLE dbo.X02_save_11;
```

### 8.13 S12: a stack's lot changed under an online owner

A stack's lot is **not** a `tItem` column: it is the item's `tItemOptions` row of type 1 (u8 lot classes), 2
(u16), 3 (u32), 300 (quest items) or 4 (amount), D03 §1.2 – §1.3. The owner stays in the game: the point is
that the zone's copy and the DB disagree.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT i.nItemKey, i.nStorageType, i.nStorage, i.nItemID, o.nOptionType, o.nOptionData        -- pick a stack
  FROM tItem i JOIN tItemOptions o ON o.nItemKey = i.nItemKey
 WHERE i.nOwner = @c AND i.nStorageType = 9 AND o.nOptionType IN (1, 2, 3) AND o.nOptionData > 1;
DECLARE @key bigint = 0;         -- nItemKey from the list
SELECT nItemKey, nOptionType, nOptionData INTO dbo.X02_save_12 FROM tItemOptions
 WHERE nItemKey = @key AND nOptionType IN (1, 2, 3);
UPDATE tItemOptions SET nOptionData = nOptionData - 1 WHERE nItemKey = @key AND nOptionType IN (1, 2, 3);
-- restore (after the disconnect the scenario predicts; the stack may have been changed by the game since)
UPDATE o SET nOptionData = s.nOptionData FROM tItemOptions o JOIN dbo.X02_save_12 s
    ON s.nItemKey = o.nItemKey AND s.nOptionType = o.nOptionType;
DROP TABLE dbo.X02_save_12;
```

Storage type 9 = inventory (D03 knowledge, check 4); `nStorage` is the cell.

*(X05)* Scenario 47 uses it twice: as written (`- 1`) before the sale of the **whole** stack (`0x3424`), and with
`- 3` in the `UPDATE` before the sale of **one** item (`0x3427`: the Character server refuses only when the stored
lot is below the lot the zone says remains, D03 §2.2, so `- 1` passes a sale of one). Log out before the restore.

### 8.14 S13: an item past its end time

The end time is the class's `deletetime` option row: type 417 (amulet), 521 (weapon), 620 / 720 / 820 (armor,
shield, boot), 906 (furniture), 1001 (decoration), 1601 (mount), 1900 (action item), 2821 (bracelet), D03 §1.3.
The value is a raw `ShineDateTime` *(pdb2016)*: `(year − 2000) | month << 8 | day << 13 | hour << 19 |
minute << 25`, month 1 – 12 (Z24 §6: `mktime(year + 100, month − 1, …)`). 2020-01-01 00:00 = 20 + 256 + 8192 =
**8468**. A year field of 0 means "no end" (Z24 `sp_ChargedItemLimitCheck`), so never write 0. Account at the
login screen.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT i.nItemKey, i.nStorageType, i.nStorage, i.nItemID, o.nOptionType, o.nOptionData        -- timed items
  FROM tItem i JOIN tItemOptions o ON o.nItemKey = i.nItemKey
 WHERE i.nOwner = @c AND o.nOptionType IN (417, 521, 620, 720, 820, 906, 1001, 1601, 1900, 2821) AND o.nOptionData <> 0;
DECLARE @key bigint = 0;         -- nItemKey from the list
SELECT * INTO dbo.X02_save_13a FROM tItem WHERE nItemKey = @key;
SELECT * INTO dbo.X02_save_13b FROM tItemOptions WHERE nItemKey = @key;
UPDATE tItemOptions SET nOptionData = 8468
 WHERE nItemKey = @key AND nOptionType IN (417, 521, 620, 720, 820, 906, 1001, 1601, 1900, 2821);
-- no restore: the item is deleted by the test. The two save tables are the record of what it was.
-- Drop them only after the test, in a separate run:
-- DROP TABLE dbo.X02_save_13a; DROP TABLE dbo.X02_save_13b;
```

Prediction: within the first per-minute check after login the zone sends D `0x3459` for the cell and clears it
(`sp_ChargedItemLimitCheck` @ FUN_00451530 → `sp_ItemDelete` → `sp_DestroyItem`, Z24 §6; inventory and equipment,
a mount being ridden is skipped); the client sees the cell emptied. Disproved by:
the item surviving two minutes, or being removed already in the login burst. The item is gone afterwards: use
one made with `&makeitem`. Re-inserting it from the save tables is possible but re-creates a deleted key; do not.

Result (P02 batch 3, `s21c`, capture-validation §21.2; run for Test1235 with `tools/capture/21/21-s13.sql`: a
`&makeitem` Leather Boots whose row 820 was set to 8468): **confirmed**. The boots came in the login burst
unchanged; at the WM's first minute change `0x0821` after the map login (59.1 s later) the zone sent `0x3459` with
the one key, and the client's `0x3001` emptied the cell on the `0x345A`. No text, no GameLog row. Neither "Disproved
by" event occurred. Not tried: wearing or using the item before that check.

Open after batch 3 *(X05)*: three more runs of this setup, scenario 47 steps 6–8: the item **worn** (pick a row
with `nStorageType = 8` from the list above), a **mount** (option row 1601) ridden across the minute check, and a
timed item **used** inside the first minute. `tools/capture/21/21-s13.sql` serves none of them (it takes a Leather
Boots in the inventory, `nStorageType = 9`, row 820): run the SQL above by hand with the key picked from its list,
after a logout that saved the item where the run needs it (worn: equip it first).

### 8.15 S14: a deleted character

`p_Char_Delete` is what the Character server calls for a client delete (D02 §3.4): it sets `bDeleted`,
`dDeletedDate` and renames the character to `<name>~<year><month><day>#<n>`. Account at the login screen.

```sql
USE w00_Character;
DECLARE @ret int;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharB' AND bDeleted = 0);
SELECT nCharNo, sID, bDeleted, dDeletedDate INTO dbo.X02_save_14 FROM tCharacter WHERE nCharNo = @c;
EXEC p_Char_Delete @c, @ret OUTPUT;
SELECT @ret AS ret, sID, bDeleted FROM tCharacter WHERE nCharNo = @c;   -- ret 0 = deleted now
-- restore
UPDATE c SET sID = s.sID, bDeleted = s.bDeleted, dDeletedDate = s.dDeletedDate
  FROM tCharacter c JOIN dbo.X02_save_14 s ON s.nCharNo = c.nCharNo;
DROP TABLE dbo.X02_save_14;
```

What to try against it (§4): a friend request, a whisper, a party invite and a guild invite by the old name from
A; the avatar list of B's account (prediction: the slot is free, `p_Char_GetListOfUserChar` filters `bDeleted =
0`). Guild membership, friend rows and the marriage row are not touched by the procedure: a deleted guild member
still listed is the kind of result to note.

### 8.16 S15: a booth purchase whose money move fails (D03 check 7, D03-B25)

`usp_SafeTrade_setAll` moves the money with `p_Char_MoneyMove`, which fails when the buyer's **row** holds less
than the price; the zone has already checked its own copy. So lower the buyer's row while the buyer is online,
just before the purchase: buyer B in the game with enough money, seller A's booth open with a capsule that has
content.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharB' AND bDeleted = 0);
SELECT nCharNo, nMoney INTO dbo.X02_save_15 FROM tCharacter WHERE nCharNo = @c;
UPDATE tCharacter SET nMoney = 0 WHERE nCharNo = @c;
-- restore: only with B at the login screen. The zone still believes in the old amount and keeps sending deltas;
-- log B out first, then
UPDATE c SET nMoney = s.nMoney FROM tCharacter c JOIN dbo.X02_save_15 s ON s.nCharNo = c.nCharNo;
DROP TABLE dbo.X02_save_15;
```

Prediction: the purchase fails with the procedure's −2623 path, the capsule stays with A, and its type-10
content rows have `nOwner` = B (`SELECT nItemKey, nOwner, nStorageType FROM tItem WHERE nOwner IN (<A>, <B>) AND
nStorageType = 10`). Disproved by: the content still owned by A. `usp_SafeTrade_setAll` exists only in the 2017
backup *(db-backup)*; the binary calls it with the same 7 parameters.

### 8.17 S16: a purchase whose attribute write fails (D03 check 13, D03-B1)

Same pattern as S5, on `tItemOptions`: the item row is created and paid by `p_Item_BuyAll`, then the first
`p_Item_SetOption` insert is rolled back. Install just before the purchase, drop right after. Buy an item whose
class writes an option row (anything stackable, a weapon, armor), paying with fame or gamble coins.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
DECLARE @sql nvarchar(max) = N'CREATE TRIGGER dbo.X02_tItemOptions_fail ON dbo.tItemOptions AFTER INSERT AS
IF EXISTS (SELECT 1 FROM inserted o JOIN dbo.tItem i ON i.nItemKey = o.nItemKey WHERE i.nOwner = ' + CAST(@c AS nvarchar(12)) + N')
BEGIN
    ROLLBACK TRANSACTION;
    RAISERROR(''X02 forced failure (S16)'', 16, 1);
END';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- restore
DROP TRIGGER dbo.X02_tItemOptions_fail;
```

Prediction: the item is deleted again, cen is refunded, fame or coins are not (compare `tCharacter.nFame` /
`tGambleCoin.nCoin` before and after). While the trigger exists every new item of the character loses its
attributes or fails; existing option rows are updated normally (the trigger fires on inserts only).

Result (P02 batch 3, `s21b`, capture-validation §21.1; run for Test1235, two purchases of Leather Boots for 13
cen): **confirmed for the item and the cen**: `0x340A` → `0x340C {0x206}` → `0x3004 {0x206}`, no `0x3001`, no
`0x1033`, no GameLog row; the DB balance of the next logins is unchanged *(the refund itself is not on the wire)* and
no boots row is left. The client shows nothing for 0x206. **Fame / coins not reached** (a cen-only item): D03-B1
is untested.

Open after batch 3 *(X05)*: the fame and the gamble-coin purchase, scenario 47 step 4. Items: `ItemInfo.shn` rows
with `BuyFame` > 0 (106 in the 2016 data, e.g. `MightySoul01`, 1200 fame) or `BuyGBCoin` > 0 (4: the `LuckyCapsule*`
rows); the trigger fires only if the item's class writes an option row.

### 8.18 S17: the DB money lowered under an online owner (added by X05)

The reverse of S2's rule: the character **stays in the game**, so the zone still holds the old amount and lets a
purchase through, and `p_Char_MoneySub` refuses it (*(db-backup)*: `@nRet = 0` when the balance would go below 0).
Used by scenario 47 step 3.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
IF @c IS NULL RAISERROR('character not found', 16, 1)
ELSE BEGIN
    SELECT nCharNo, nMoney INTO dbo.X05_save_17 FROM tCharacter WHERE nCharNo = @c;
    UPDATE tCharacter SET nMoney = 0 WHERE nCharNo = @c;
END
-- restore: with the account at the login screen (the sales of the test have added to the row since; this
-- puts back the amount saved before it)
UPDATE c SET nMoney = s.nMoney FROM tCharacter c JOIN dbo.X05_save_17 s ON s.nCharNo = c.nCharNo;
DROP TABLE dbo.X05_save_17;
```

Prediction: every DB-side debit fails while the zone-side check passes: `0x3443 {0x744}` for a soul stone, `0x34BA`
/ `0x34BC {0x366E}` for a buy-back **when the `UPDATE` is run again after the sale** (the sale credits the row with
exactly the buy-back price), `0x340C {0x205}` / `0x340F {0x207}` for an NPC purchase (D03 §2.1; scenario 49
step 1). Credits succeed (`p_Char_MoneyAdd`). Disproved by: a purchase that goes through. Not verified
here: no SQL Server on the analysis machine (as §8.1).


### 8.19 S18: an item row removed under an online owner (added by X05)

The owner **stays in the game**: the zone keeps the item in its cell while the Character server no longer finds
the key. `p_Item_SetStorage` returns `@@ROWCOUNT` (0 = "not found or error", *(db-backup)*: both Character
backups) and `p_Item_IsValidOwner` returns 1 for a missing item (D03 §2.2), so every request on that key is
refused. Used by scenario 49 steps 2 and 3.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
SELECT nItemKey, nStorageType, nStorage, nItemID FROM tItem WHERE nOwner = @c AND nStorageType IN (8, 9);  -- pick: 9 inventory, 8 worn
DECLARE @key bigint = 0;         -- nItemKey from the list
SELECT * INTO dbo.X05_save_18  FROM tItem        WHERE nItemKey = @key;
SELECT * INTO dbo.X05_save_18o FROM tItemOptions WHERE nItemKey = @key;
DELETE FROM tItem WHERE nItemKey = @key;
SELECT COUNT(*) AS option_rows_left FROM tItemOptions WHERE nItemKey = @key;   -- note it: 0 = a trigger removed them (D03 §1.1)
-- restore (A at the login screen; skip the row if the test dropped the item for good)
INSERT INTO tItem SELECT * FROM dbo.X05_save_18 s WHERE NOT EXISTS (SELECT 1 FROM tItem i WHERE i.nItemKey = s.nItemKey);
INSERT INTO tItemOptions SELECT * FROM dbo.X05_save_18o s
 WHERE NOT EXISTS (SELECT 1 FROM tItemOptions o WHERE o.nItemKey = s.nItemKey AND o.nOptionType = s.nOptionType);
DROP TABLE dbo.X05_save_18; DROP TABLE dbo.X05_save_18o;
```

Prediction: `0x342A {0x247}` for a move, `0x3412 {0x28A}` for an equip, `0x3415 {0x28A}` for an unequip, `0x3418
{0x306}` for a drop (scenario 49). The zone's save at logout writes no item rows *(inferred: items are written per
transaction, D03 §1; the logout sends the item blob to the WM only, `0x4013`)*, so the restore brings the item back as it was. Disproved by: any of the four requests succeeding.
Not verified: `INSERT … SELECT *` fails if `tItem` has an identity or computed column (then name the columns of
§8.1's table); no SQL Server on the analysis machine (as §8.1).

### 8.20 S19: a forced insert failure on one table for one owner (added by X05)

S16's trigger pattern on another table. Two uses in scenario 49: on `tItem` for the character (step 5: every new
item row of A fails, so a pick-up into a free cell and a purchase into a free cell are refused), and on
`tUserMoney` for the account (step 6: `p_User_MoneyGet` inserts the row at the first storage access and reports an
error when that fails, *(db-backup)*). Install just before the step, drop right after.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
DECLARE @u int = (SELECT nUserNo FROM tCharacter WHERE nCharNo = @c);
-- (a) tItem, for the character
DECLARE @sql nvarchar(max) = N'CREATE TRIGGER dbo.X05_tItem_fail ON dbo.tItem AFTER INSERT AS
IF EXISTS (SELECT 1 FROM inserted WHERE nOwner = ' + CAST(@c AS nvarchar(12)) + N')
BEGIN ROLLBACK TRANSACTION; RAISERROR(''X05 forced failure (S19 a)'', 16, 1); END';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- (b) tUserMoney, for the account: A must never have opened the storage in this session
SELECT * INTO dbo.X05_save_19 FROM tUserMoney WHERE nUserNo = @u;
DELETE FROM tUserMoney WHERE nUserNo = @u;
SET @sql = N'CREATE TRIGGER dbo.X05_tUserMoney_fail ON dbo.tUserMoney AFTER INSERT AS
IF EXISTS (SELECT 1 FROM inserted WHERE nUserNo = ' + CAST(@u AS nvarchar(12)) + N')
BEGIN ROLLBACK TRANSACTION; RAISERROR(''X05 forced failure (S19 b)'', 16, 1); END';
IF @u IS NULL RAISERROR('account not found', 16, 1) ELSE EXEC (@sql);
-- restore (a)
DROP TRIGGER dbo.X05_tItem_fail;
-- restore (b)
DROP TRIGGER dbo.X05_tUserMoney_fail;
INSERT INTO tUserMoney SELECT * FROM dbo.X05_save_19; DROP TABLE dbo.X05_save_19;
```

Run (a) and (b) in separate steps, not together. Prediction: (a) `0x341E {0x347}` for the pick-up (`Item_Insert`
returns the error of `p_Item_Create`), `0x340C {0x206}` or `{0x205}` for a purchase into a free cell and `0x34BA {0x366F}` or `{0x366E}` for a buy-back
(open between the two: the trigger rolls back inside `p_Item_BuyAll` after the money step set `@nRet = 1`, see
scenario 49 step 7); (b) `0x3445`. Disproved
by: the item or the storage arriving. While (a) exists, every other source of a new row for A fails too (quest
rewards, `&makeitem`, chests): do nothing else in that capture. Not verified: `tUserMoney` has exactly the two
columns the procedure inserts (`nUserNo`, `nUserMoney`); no SQL Server on the analysis machine.

### 8.21 S20: the 2016 `p_Char_Rename` on the test DB (added by X07)

The test DB runs the private 2018 copy (`_Database/Fixes/Free Name Change/p_Char_Rename.sql`): without an open
`tCharacterChangeID` row (`bFlag` 0) it returns `@nRet` 0 **without renaming**, so the Character server answers 0xD0
and the WM's name and the DB's differ (capture-validation §22.3). The 2016 build (`Character.bak`, D02 §3.5) only runs
the `UPDATE` and returns `@@ERROR`. Swap it in for scenario 52 step 2; the account at the login screen while the
procedure is changed is not needed (the Character server calls it per request).

```sql
USE w00_Character;
EXEC sp_helpindex N'dbo.tCharacter';      -- note whether an index on sID is unique: it decides the duplicate case
SELECT OBJECT_DEFINITION(OBJECT_ID(N'dbo.p_Char_Rename')) AS def INTO dbo.X07_save_20;
EXEC (N'ALTER PROCEDURE dbo.p_Char_Rename @nCharNo int, @sID nvarchar(40), @nRet int OUTPUT AS
SET NOCOUNT ON
UPDATE tCharacter SET sID = @sID WHERE nCharNo = @nCharNo
SET @nRet = @@ERROR');
-- restore
DECLARE @d nvarchar(max) = (SELECT def FROM dbo.X07_save_20);
SET @d = STUFF(@d, PATINDEX(N'%CREATE%PROC%', @d), 6, N'ALTER');   -- the saved text starts with CREATE PROCEDURE
EXEC (@d);
DROP TABLE dbo.X07_save_20;
```

Check before the restore that `def` holds the 2018 text (`tCharacterChangeID` in it). Prediction and disproof:
scenario 52 step 2. Not verified: no SQL Server on the analysis machine.

### 8.22 S21: a forced failure of the charged stat / empower reset or of an item's destruction for one character (added by X07)

S19's trigger pattern on an `UPDATE`. `usp_ChargeItem_UseSkillPowerInitDel` / `…UseStatPointInitDel` (*db-backup*)
first set every `nSkillPower*` / free-stat column of the character to 0, roll back and return `@nRet` 1 when that
`UPDATE` fails, then delete the capsule. The triggers fire only on that reset (all four powers or all five stats to
0 from a non-zero row), so the empower and stat saves of the same session pass. Install one just before scenario 51
step 6, drop it right after. (c) and (d) (review fix) are for step 7: they refuse the delete or the option write of
any item of A, so nothing else may move A's items while one stands.

```sql
USE w00_Character;
DECLARE @c int = (SELECT nCharNo FROM tCharacter WHERE sID = N'TestCharA' AND bDeleted = 0);
DECLARE @sql nvarchar(max);
-- (a) the stat reset (0x9005)
SET @sql = N'CREATE TRIGGER dbo.X07_tCharacter_fail ON dbo.tCharacter AFTER UPDATE AS
IF EXISTS (SELECT 1 FROM inserted i JOIN deleted d ON d.nCharNo = i.nCharNo
           WHERE i.nCharNo = ' + CAST(@c AS nvarchar(12)) + N'
             AND i.nStrength + i.nConstitute + i.nDexterity + i.nIntelligence + i.nMentalPower = 0
             AND d.nStrength + d.nConstitute + d.nDexterity + d.nIntelligence + d.nMentalPower > 0)
    RAISERROR(''X07 forced failure (S21 a)'', 16, 1);';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- (b) the empower reset (0x9006): run instead of (a)
SET @sql = N'CREATE TRIGGER dbo.X07_tSkill_fail ON dbo.tSkill AFTER UPDATE AS
IF EXISTS (SELECT 1 FROM inserted i JOIN deleted d ON d.nCharNo = i.nCharNo AND d.nSkillNo = i.nSkillNo
           WHERE i.nCharNo = ' + CAST(@c AS nvarchar(12)) + N'
             AND i.nSkillPowerDemage + i.nSkillPowerSP + i.nSkillPowerKeepTime + i.nSkillPowerCoolTime = 0
             AND d.nSkillPowerDemage + d.nSkillPowerSP + d.nSkillPowerKeepTime + d.nSkillPowerCoolTime > 0)
    RAISERROR(''X07 forced failure (S21 b)'', 16, 1);';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- (c) deleting one of A's items (step 7, one scroll: Item_Delete → p_Item_Delete), S19's ROLLBACK pattern
SET @sql = N'CREATE TRIGGER dbo.X07_tItem_delfail ON dbo.tItem AFTER DELETE AS
IF EXISTS (SELECT 1 FROM deleted WHERE nOwner = ' + CAST(@c AS nvarchar(12)) + N')
BEGIN ROLLBACK TRANSACTION; RAISERROR(''X07 forced failure (S21 c)'', 16, 1); END';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- (d) an option write on one of A's items (step 7, a stack of two: ItemAttr_Save → p_Item_SetOption)
SET @sql = N'CREATE TRIGGER dbo.X07_tItemOptions_fail ON dbo.tItemOptions AFTER INSERT, UPDATE AS
IF EXISTS (SELECT 1 FROM inserted o JOIN dbo.tItem t ON t.nItemKey = o.nItemKey
           WHERE t.nOwner = ' + CAST(@c AS nvarchar(12)) + N')
BEGIN ROLLBACK TRANSACTION; RAISERROR(''X07 forced failure (S21 d)'', 16, 1); END';
IF @c IS NULL RAISERROR('character not found', 16, 1) ELSE EXEC (@sql);
-- restore (a)
DROP TRIGGER dbo.X07_tCharacter_fail;
-- restore (b)
DROP TRIGGER dbo.X07_tSkill_fail;
-- restore (c) / (d)
DROP TRIGGER dbo.X07_tItem_delfail;
DROP TRIGGER dbo.X07_tItemOptions_fail;
```

Run the part of (a), (b), (c) or (d) only (the script above installs all when run whole). (c) and (d) roll back
(S19's pattern): the batch ends and the Character server's ODBC call fails, which `Item_Delete` / `ItemAttr_Save`
report as an error *(inferred)*: `0x4813 {0x888}` / `{0x887}` (D04 §2). The trigger raises without a
rollback, so the procedure's own `IF @@ERROR <> 0` path should run (`@nRet` 1 → 0x1083 / 0x108B, D03); if the error
reaches the Character server's ODBC call instead, the code is the "other failure" one (0x108A / 0x1092). Both give
`0x9009` / `0x900A`. While (b) stands, an empower take-back to 0 on every field fails too (`p_Skill_SetPowerAll`):
do nothing else in that capture. Prediction and disproof: scenario 51 step 6. Not verified: no SQL Server on the
analysis machine; which of the two codes comes is *(inferred)*.

## 9. Table and config experiments (X1–X7)

### 9.1 Conventions

- The servers read `9Data` at start: **stop the named process, change the file, start it, test, put the original
  back and restart.** Keep a copy of every file you change next to it (`<name>.orig`). The repository's `Files/`
  tree is the reference: never edit it, edit the test installation.
- Text tables (`9Data/Shine/World/*.txt`, `9Data/ServerInfo/*.txt`) are CP949 text: use an editor that keeps the
  bytes it does not understand (the comments are Korean) and change only the digits named below. Columns are
  separated by tabs or spaces; `#` inside a value stands for a space.
- `.shn` tables: `python3 -I docs/plan/status/X02-shnset.py <in.shn> <out.shn> <KeyColumn>=<value>
  <Column>=<number> …` rewrites integer cells in place (same size, same cipher; self-tested by decoding the result
  with `shn.py`). Example: `… KingdomQuest.shn /tmp/KingdomQuest.shn ID=0 StartWaitTime=2`.
- **49 tables are hashed and compared with the client's copy at every map login** (`CShnDataFileCheckSum`, enum
  `SHN_DATA_FILE_INDEX` *(pdb2016)*; mismatch → `0x1804 {0x147, idx}` and disconnect 0x68E, Z01 §5.2). Among the
  tables used here that is `ItemInfo.shn`, `ChargedEffect.shn` and `MapInfo.shn`: a changed copy must also replace
  the client's `ressystem/<name>.shn` (the shipped server and client files are byte-identical). Not in the list
  and free to change on the server alone: `KingdomQuest.shn`, `ItemShop.shn`, `ItemAction*.shn`, every `World/*.txt`.
  The full list is the enum (`pdb.py Files/Server/NA2016/Zone00/Zone.pdb types '^SHN_DATA_FILE_INDEX$'`).

### 9.2 X1: drops

File `9Data/Shine/World/ItemDropTable.txt`, table `ItemGroup`, one `#RECORD` per mob: `MapArea MobId MinLevel
MaxLevel AbStateCnt MinCen MaxCen CenRate TradeBoxA RateA … DrItem1 DrItem1R UpGradeMin01 UpGradeMax01 Rule1 Num1
DrItem2 …` (25 drop entries). `DrItem<n>R` is a rate out of 1 000 000, `Num<n>` the count limit (−1 = no limit).
Stop and restart the zone that hosts the map (all four when unsure: they share the file).

1. **Limited drop runs out for the whole server (Z09-B20, V22).** In the `Slime` record (first record:
   `- Slime 1 11 0 0 0 0 - 0 - 0 - 0 Potion01 50000 0 0 r -1 …`) change entry 1 from `Potion01 50000 0 0 r -1`
   to `Potion01 1000000 0 0 r 3`. Kill slimes with A, then with B. Prediction: the entry passes its rate roll
   every time but is still subject to the per-entry gate roll (Z09 §11.2); exactly three drops in total come
   from entry 1, none after that for either player until the zone restarts. Disproved by: a fourth
   drop from entry 1, or a count per player or per mob. Entry 2 is also `Potion01` (rate 40000): set its rate to
   0 for the test so every `Potion01` drop is entry 1's.
2. **Drop-rate items (V19).** No file change. 2016 `ChargedEffect.shn` has 13 rows with `EffectEnum` 16: seven
   at `EffectValue` 1500 (`Huntervoucher`, `Huntervoucher01`, `02`, `02_1`, `02_2`, `02_3`, `11`), five at 2000
   (`Huntervoucher00_TD`, `01_TD`, `03_1`, `03_7`, `03_30`) and `SNS_DropUp` at 1100. With entry 1 of experiment
   1 set to `Potion01 1000000 0 0 r -1`, count drops over 100 slime kills three times: no item, `&makeitem
   SNS_DropUp` used, `&makeitem Huntervoucher02_1` used (1 h). Prediction (Z09 §11.2): the share of kills that
   drop rises by the gate bonus, +100 ‰ and +500 ‰. Disproved by: equal shares (then enum 16 does not feed the
   gate). This is a statistical test: 100 kills separate +500 ‰ from nothing, not +100 ‰ from nothing.

### 9.3 X2: maps with special rules (read only)

`9Data/Shine/World/Field.txt`, table `FieldList` (columns `MapIDClient … KQ … Pker EnemyGuild Party Monster
Summoned IsPKKQ IsFreePK IsPartyBattle … CanParty …`; a map can have several rows, one per `Serial`):

| Need | Rows in the 2016 data |
|---|---|
| party battle (`IsPartyBattle` 1) | `ValDn02`, `CemDn02`, `GblDn02`, `ElfDn02`, `PriDn02`, `ForDn02`, `FireDn02`, `SwaDn02`, `AlDn02`, `PsyInDn02`, `ArkDn02`, `Fbattle01` – `Fbattle04` |
| free PK (`IsFreePK` 1) | `KDHBat1` only |
| PK kingdom quest (`IsPKKQ` 1) | `KDHero`, `KDHBat1`, `OX_field` |
| no party (`CanParty` 0) = party-release map | `KDHero`, `KDHBat1`, `OX_field`, `Wedding`, `Job1_Dn01`, `Job2_Dn01`, `Job2_Dn02`, `KDSpring`, `KDSoccer_W`, `RouT`, and the kingdom-quest copies of `Rou` (`Serial` 98, 101; the town row, `Serial` 0, has 1) |
| `Pker` column | 1 on 122 rows, 2 on 25 (the `Fbattle` and `KDHero` rows among them), 0 on 6 |

The zone derives the flag the WM tests: `FieldMap::fm_Regist2WMS` @ FUN_00461cf0 *(pdb2016)* writes each
`0x180F` entry as `{ canparty = fm_FieldOption->canparty, mapname, IsPartyReleaseMap = (canparty == 0) }`. So a
map is a party-release map exactly when its `CanParty` is 0, and "cannot form a party there" and "leaves the
party on entering" are one flag. `Wedding` (`KQ` 0) is the one row that is not a kingdom-quest or job-quest
map: use it for scenario 15 step 8.

Instance gates: table `InstanceDungeon` of the same file (`Argument IDNo ZoneNumber MapIDClient ScriptName
ModeIDLv EntranceType Guild Individual NeedQuest NeedItem Consume LimitTime MaxUseChr`), 17 rows. Gates with two
`ModeIDLv` rows (the level-select menu of scenario 31): `UrgFire017` (`UrgDragon`, needs item `DragonRelicNeck`),
`IDGate011` (`Leviathan`, `lighthouseKey`), `LabGate00` (`Tower03`, zone 1, no item), `BerFrz013` (`Siren`, zone
2, no item). Single-mode gates without an item: `GateRouVal016` (`Tower01`), `Urg12` (`Tower02`), `AdlFGate00`,
`WarN01`, `WarBL01` (all `ZoneNumber` 3; `UrgFire017` and `IDGate011` too).

### 9.4 X3: a stack limit lower than an existing stack

`ItemInfo.shn` column `MaxLot` (2016 data: 976 items at 50, 319 at 99, 132 at 10). Test item: `BestLowHpPotion`
(ID 3500, `MaxLot` 50).

1. With the original files: `&makeitem BestLowHpPotion -l50` twice, drop one stack (whole stacks only), keep 50.
2. Stop all four zones and the client. `python3 -I docs/plan/status/X02-shnset.py ItemInfo.shn out.shn
   InxName=BestLowHpPotion MaxLot=49`; put `out.shn` as `ItemInfo.shn` into the server's `9Data/Shine` **and**
   the client's `ressystem` (§9.1: hashed table). Start, log in.
3. The inventory stack now holds 50 with a limit of 49. `&makeitem BestLowHpPotion -l10`, drop it, pick it up.

For the over-full stack the free amount `MaxLot − lot` is negative; what the pick-up does with it is open (scenario 21 step 12; no prediction, and it is not the 0x34A path, which is the
`KQItem.shn` `PickupLimit` test of step 11 only): note the `0x3001` cells and the `tItemOptions` lot rows after. Disproved for "no check": a refusal
code at login or at the pick-up. Restore both copies of the file afterwards; a client left with the changed file
is disconnected (0x68E) by any unchanged server.

Result (P02 batch 3, `s21d`, capture-validation §21.3; run for Test1235): the open question is **answered**. No
refusal at login or at the pick-up ("no check" holds): the stack loads with 50 and is never touched. The pick-up of
10 did **not** merge: `so_ply_PickupItem` merges only when `cell.lot + picked ≤ MaxLot` (no negative free amount is
computed), so the 10 went into an empty cell with `0x341C` → `0x341D` → `0x300A {0x341}`. Not tried: selling, using
and moving a stack onto the over-full one.

Open after batch 3 *(X05)*: steps 4–7 on the same changed table, predictions in scenario 47 step 5.

4. Sell one item of the over-full stack to an item merchant.
5. Use one item of it.
6. Drag the lot-10 stack onto the over-full one.
7. Drag the over-full stack onto the lot-10 one. Note whether the Character server was restarted with the changed
   `ItemInfo.shn` (it checks `MaxLot` itself, D03 §3.3).

### 9.5 X4: abstates removed by an action (read only)

`9Data/Shine/World/MiscDataTable.txt`, table `AbStateReset` (`Serial AbState Run Walk Attack Attacked EquipWhere
EquipClass CheckSum`), all 7 rows of the 2016 data:

| AbState | Run | Walk | Attack | Attacked | Equipment |
|---|---|---|---|---|---|
| `StaBuckler` | 0 | 0 | 0 | 0 | `LeftHand` `Shield` |
| `StaNeglect` | 1 | 1 | 1 | 0 | – |
| `StaHide` | 0 | 0 | 1 | 1 | – |
| `StaMesmerize` | 0 | 0 | 0 | 1 | – |
| `StaEntrapHide` | 0 | 0 | 1 | 1 | – |
| `StaGTIConfusion` | 0 | 0 | 0 | 1 | – |
| `StaGTIHide` | 0 | 0 | 1 | 1 | – |

So scenario 24's "buff with a movement reset condition" has one candidate, `StaNeglect` (removed by run, walk
and attack, not by being hit); `StaHide` tests attack / attacked; `StaBuckler` tests the equipment condition
(take the shield off). Prediction per `confidence.md` C18: the state ends (the abstate removal packets of Z03, as scenario 24 lists them)
on the first action whose column is 1 and survives the others.

### 9.6 X5: a kingdom quest within minutes

`KingdomQuest.shn` is read by the WM (W04 §6.2) and is not a hashed table. Row `ID` 0 ("King Slime's
Counterattack": `ST_Day` 1, `ST_Hour` 0, `ST_Minute` 0, `StartWaitTime` 30, `NextStartDeleyMin` 120, levels 5 –
16, `MinPlayers` 1, `MaxPlayers` 15) already runs with one player. Stop the WM (and the zones, which reconnect
to it), then:

```bash
python3 -I docs/plan/status/X02-shnset.py KingdomQuest.shn out.shn ID=0 NextStartDeleyMin=10 StartWaitTime=2
```

Prediction (W04 §6.2): the schedule steps from the 1st of the month 00:00 in 10-minute steps, so a start falls
on every full ten minutes of the clock; at that minute the WM broadcasts `0x580D NC_KQ_W2Z_MAKE_REQ` to all
zones, a level 5 – 16 character can join, and two minutes later the quest starts with the one joiner. Disproved
by: starts at other minutes (then `ST_Year` / `ST_Month` / `ST_Second` are used after all), or no start with
one joiner. Do not set `NextStartDeleyMin` to 0: the schedule loop then never ends (W04-B57). The client has its
own, different `KingdomQuest.shn`; what its quest list shows comes from the server's packets (W04 §6), a
difference in the displayed time is worth a note.

### 9.7 X6: a world closed or full

No file needs to change for "closed", one number for "full":

1. **Closed (status 0).** Stop the WM process and wait for the Login server to release the link. Prediction: the
   world list (`0x0C0A` / `0x0C1C`) shows `worldstatus` 0, a world select gets `0x0C0C {worldstatus 0}` and the
   client text "Server is closed. Please try login later." (L01 §3).
2. **Full (status 5).** The WM reports `{NumOfUser, MaxOfUser}` in `0x0808` every 30 s and Login computes the band
   as `NumOfUser ≥ 95 × MaxOfUser / 100` (integer division). `MaxOfUser` is the WM's client-session capacity
   (`Login_WorldStatus` @ FUN_00438d10 in W01: `g_Clients.capacity`, or the OPTool limit of `0x280E`); that it comes from the last number of the WM's client row in
   `9Data/ServerInfo/ServerInfo.txt` (`SERVER_INFO "PG_W00_WM", 5, 0, 0, 20, "0.0.0.0", 9110, 100, 2500`) is
   *(inferred)*. Change that 2500 to 1 and restart the WM: `95 × 1 / 100` = 0, so the world is full with nobody
   online. Prediction: status 5 in the list, and on world select `0x0C0C {5}` **with** the WM address, after
   Login has already sent AccountDB `0x0C10`, AccountLog `0x0721` and WM `0x0C0D` (L00-B3); the client shows
   "Server is full. Please try again later." and does not connect. Disproved by: no `0x0C0D` on the WM link. If
   the status stays 6, the capacity comes from somewhere else: note the `0x0808` payload from the capture.

### 9.8 X7: item actions and the drop confirmation (read only)

- **Drop confirmation.** No table decides it: every accepted `0x3007` drop opens the server menu
  (`ItemDropper_id_Drop` @ FUN_0048dc90, Z04 §3.1), and a bound item goes to the two break confirmations
  instead. Scenario 42 step 1 can use any droppable stack.
- **Item actions.** `ItemAction.shn` (1114 rows: `ItemActionID`, `ConditionID`, `EffectID`, `CoolTime`,
  `CoolGroupActionID`) is referenced by `ActionEffectItem.shn` (372 rows) and `SetEffect.shn` (1043 rows) through
  their `ItemActionID` column; `ActionEffectAbState.shn` has the column and no rows. List the items of the first
  with `python3 -I tools/protocol-re/shn.py Files/Server/2016/9Data/Shine/ActionEffectItem.shn | head -20` and
  take one that `&makeitem` can create; a set item with a `SetEffect.shn` row tests the same path through the
  set bonus (Z17 §1, Z21).
