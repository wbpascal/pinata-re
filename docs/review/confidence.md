# Confidence review (X02)

How far each part of the reconstruction can be trusted, what was re-checked, and what only a capture can settle.
Sources: every pseudocode and knowledge file in the tree, `docs/protocol/capture-validation.md` (P02),
`docs/pseudocode/README.md` §5 (X01's list of superseded statements) and the git history. Corrections that X02 itself
finds go to `docs/knowledge/X02.md` §0; the capture scenarios that follow from the ratings are in
`docs/plan/capture-scenarios.md`.

| § | Content | State |
|---|---|---|
| 1 | Error classes: what went wrong so far, with counts | done (part 1) |
| 2 | Rating of every pseudocode section and knowledge struct table | done (parts 2–3) |
| 3 | Adversarial re-check of the load-bearing claims | §3.2 done (part 4), §3.3 done (part 5), §3.4 done (parts 6, 6b), §3.5 done (part 7) |
| 4 | Coverage gaps of items finished without a review part | done (part 10); §4.7 points closed in the sweep (part 11) |
| 5 | Original-server bugs found by the re-check (X02-B1 … B12) | done (part 11) |
| 6 | Not reconstructed / uncertain | done (part 11) |
| 7 | Coverage boundary, follow-up items Z31, Z32, W06, D08 | done (part 11) |

## 1. Error classes

### 1.1 What was collected

| Source | Statements |
|---|---|
| `docs/pseudocode/README.md` §5.1–§5.8 (X01 part 3: every knowledge "Corrections" section, S01 §3.3, P02 batch 1, passages in later items) | 207 rows |
| P02 batch 2 (`docs/knowledge/P02.md` "Corrections", `capture-validation.md` §13), written after X01 collected §5 and missing there | 32 rows |
| **Classified in §1.2** | **239** |
| Bug-register entries a later item changed (README §5.9) plus L00-B6 (P02) | 23 (22 + 1); 7 of them are also rows above |
| Review parts: 35 commits on `docs/pseudocode` / `docs/knowledge` name a review; ten state their count | 103 findings in those ten (8, 17, 10, 8, 12, 9, 7, 8, 15, 9), fixed in place and not classified |

Of the 239 rows, 42 are additions (an open point answered, an *(inferred)* statement confirmed, a rename) and 3 are
decoder fixes. **194 are statements that were wrong or incomplete.**

Three facts about them decide how §2 rates and what §3 re-checks:

- **A plain statement is not a safe statement.** Of the 207 README §5 rows, only 30 superseded statements carried a
  hedge (*(inferred)*, "not traced", "open", "probably"). The other 177 were written as read in the code. The
  evidence level "plain = read in the code" therefore rates **medium** at best (plan rule), and **low** where one of
  the classes below applies.
- **Most errors were found by reading more code, not by captures.** README §5: 132 rows by a later item reading the
  callee or the caller, 32 by D06 re-reading the DB wrappers against both backups, 22 from the 2016 PDBs, 21 from
  captures. Batch 2 added 32 rows from seven short captures (most of them traced back to the code after the capture showed the bytes). So a capture of a path finds what reading
  did not (mostly classes U, T, L, F), and following one more call level finds classes N, S, B, R.
- **Old items carry most of the errors.** Items written before the 2016 PDBs were available (S01, 2026-11-13: L00,
  W01–W04, Z01–Z08, D01–D05) own 166 of the 194 (175 with C01 and P01's README and generated files). The items after it read `<bin>-pdb` exports with official names
  and typed members; their recorded errors are few (Z09 5, Z12 4, W05 4, Z13 1, Z15 1), but they were also tested
  less: nothing later re-read them, and batch 1 / 2 touch them only at the edges.

### 1.2 The classes

Counts: rows of README §5 + rows of P02 batch 2. "Find more" is how §2 detects further instances that nobody has
corrected yet (part 2 turns these into the rating rules).

| Class | Meaning | Count | Examples | Find more |
|---|---|---|---|---|
| **N** name guess | a callee, global or table given a name of ours and then treated as if it did what the name says; the body was not read | 33 (32 + 1) | Z01 §6 `sp_ConnectFromWhere` "asks the WM 0x082A" (sends a GM notice); Z01 §8.4 "tutorial save" (= `SendCoolTimes2DB` 0x4023); Z03 §8.1 `questDiary.MobKill` (= `CT_KillMob`, a title counter); Z03 `g_HitRateScale` (= the start script's security factor) | names of ours (`Xxx_Yyy`, "(ours)") in pre-S01 docs that `docs/knowledge/S01-renames.tsv` maps to an official name with another meaning; a call described in one line with no `@ FUN_` of the callee |
| **B** branch / condition / code | a condition missed, the wrong branch or return value, a result code read wrong | 26 (23 + 3) | Login / WM handlers "ignore" a bad packet (they return 0 and the parser closes the session); Z01 §6 tail of 0x1803 "unconditional" (P02-B4); Z08 0x7C13 codes 0xDC0–0xDC2; D02 0x0844 / 0x10CA "zeros on error" (nothing is sent) | "always", "unconditional", "ignored", "no-op", "returns" in handler text; code lists without the client text; handlers whose `return 0` path was not followed to the parser |
| **F** field meaning | the meaning or unit of a field guessed from its size, position or one value | 24 (20 + 4) | `g_Now` "milliseconds" (0.1 s); 0x0810 "minutes" (seconds); 0x441E "counters" (`time_t` period starts); 0x340A `attrLen` (an offset); 0x180C `always99` (GameLog store type); Z07 §4.1 enum reversed | annotation fields named `unk…`, `?`, or typed differently from `pdb2016-layouts.json`; units in prose ("ms", "minutes") without the divisor's `@ FUN_`; a field explained by one observed value |
| **U** unwritten bytes / missed bug | the wire content assumed clean: uninitialised or stale bytes, length off by one, a missing check not noticed | 18 (10 + 8) | P02-B1 … B21 (0x182A byte, 0x302D / 0x3C08 extra byte, 0x305C 100 stale bytes, WM blobs 2 / 4 bytes too long); Z04 §3.3 party money crash (Z09-B22); 0x2032 gather without a time check | sends from a global or stack buffer with a fixed length; lengths built from a callee's return value; "zeroed" claims; every packet no capture has shown yet |
| **S** offset / member / index | a struct member, vtable slot, table index or capacity misidentified | 17 | Z03 §2 `obj+0x1e78` "ran once" (invalid-position flag); Z03 §6.1 "296 slots" (28); `g_LevelExp` base (off by 8: `nextexp[lv − 1]`); W05 class mask "bit 0 = Fig" (bit n = class n); vt 0xc70 "GM-invincible" | `p+0x…` / `vt 0x…` in pre-S01 docs not listed in `S01-player-offsets.tsv`; indices "± 1"; capacities quoted without the allocating call |
| **D** DB backup version | a procedure body, parameter order or bind taken from the backup that does not match the 2016 call | 16 | `p_Char_Create`, quest filters (`=` not `<>`), `p_Guild_Member_SetGrade`, wedding timers: all w00, not `Character.bak`; `@nRet` bound as input (D06-B8); `usp_GuildTournament_setRegist` does charge the fee | *(db-backup)* statements citing `Character.bak` for one of the 27 procedures D06 §8.5 lists as different; any SQL in D01–D05 not re-read by D06 |
| **R** reachability / caller | live code called dead or dead code called live; the wrong caller or trigger | 13 (10 + 3) | Z03 §3.5 mob melee `so_attack` (dead in 2016); Z02-B5 0x2035 "legacy" (live); `ws_save2worldmanager` "on logout" (only `so_LinkTo`); 0x0806 handler unreachable; 0xBC06 / 0xA001 have no sender; 0x080A is the answer to AccountLog's 0x0809 | "dead", "legacy", "never sent", "no sender", "called on … and …"; paths reached only through a vtable (`coverage.py` does not see them); opcodes with a handler but no sender in any `handlers.json` `sends` |
| **L** layout | field order, width, size, a missing header or prefix | 9 (4 + 5) | 0x0C36 result before handle; 0x0802 six fields; Login → WM 0x0C16 is 10 bytes; `pdb2016-layouts.json` for CharDB ↔ zone packets lacks the 6-byte ref; 0x2802 entry order; 0x7037 three extra bytes | annotation size ≠ PDB struct size (± 6 ref, ± 2 / 4 WM blob tail); server-internal packets about a player without `ref`; raw-header sends (`{len, opLo, opHi}`) |
| **O** opcode identity | the wrong opcode or packet name; a "packet" that is none | 8 (7 + 1) | 0x1002 = LOGINFAIL (REQ + 1 guess); WM 0x1407 sends 0x1413, not 0x1408; W04 0x940A answers with opcode 0x9407; 0x10D2 has two layouts; zone "0x0E0D" is a byte array | names in `handlers.json` without a pdb2016 opcode name; replies built with a raw header; one opcode sent by two functions |
| **C** client not checked | a statement about the client that its handler contradicts, or a client handler said to be missing | 8 | Z07 §5.3 "no handler for 0x1094" (there is one); D04 texts for 0x949 / 0x952 ("DB Error"); Z02 §6.2 0x201C always answered by 0x201D; C01: 0x2011 "ignored" | client statements without a client `FUN_`; error codes whose text was taken from `client-error-codes.json` without reading the handler's own switch |
| **T** order / timing / direction | message order, who sends first, startup order, timing | 7 (4 + 3) | zone seed on accept; heartbeat runs server → client; listeners (OPTool first); W01 §7.2 0x101C send order; per-character updates arrive out of order on four links (P02-B12) | sequences written in prose across two processes; README §2 flows; every "then" between packets of different functions |
| **M** formula | arithmetic read wrong | 4 | Z03 §4.1 stat total (division after every factor, L14 scales the flat part); Z03 §5.6 hit roll (one random number), empower bonus (keep time, not rate); Login token (MD5) | formulas with several factors or `/ 1000`; table index arithmetic; anything the decompiler shows as float or 64-bit math |
| **P** 2017 for 2016 | a 2017 PDB fact used for 2016 | 4 | W04 `MobKillAnnounceType` 0–9 (2016: 0–7); Z05 0x34A9 (2017 struct is truncated); D05 `nType` "2017-only" (they exist in 2016) | *(pdb2017)* markers; `S01.md` §2.3 (differences 2016 vs 2017) |
| **X** bug diagnosis | a register entry withdrawn, superseded or narrowed (counted from README §5.9 + L00-B6: 4 withdrawn, 6 superseded, 9 narrowed, 4 extended) | 23 | W01-B5, D01-B10, D02-B19, L00-B6 are not bugs; Z02-B5 / B12 too strong | bug rows whose effect is *(inferred)* and whose handler has no capture |
| A addition | an open point answered or an inference confirmed; not an error | 42 | | |
| Z decoder | tooling (`pcap_decode.py`, annotation types) | 3 | | |

How the rows map to classes (`n` = the n-th row of that README subsection):

**§5.1:** 1T 2T 3A 4O 5O 6O 7Z
**§5.2:** 1T 2N 3B 4B 5B 6B 7B 8N 9L 10M 11L 12A 13A 14C 15F 16B 17N
**§5.3:** 1N 2B 3B 4B 5B 6F 7X 8A 9A 10O 11F 12N 13C 14N 15A 16F 17F 18O 19A 20U 21P 22N 23A 24S 25L 26B 27F 28R 29A 30P 31S 32T 33S 34S 35O
**§5.4:** 1F 2N 3N 4A 5R 6N 7N 8B 9N 10F 11S 12A 13F 14F 15B 16A 17N 18N 19R 20B 21C 22A 23S 24R 25U 26A 27A 28U 29X 30N
**§5.5:** 1S 2S 3S 4U 5R 6M 7S 8A 9R 10S 11U 12B 13A 14S 15N 16M 17M 18B 19N 20S 21S 22N 23N 24F 25N 26B 27A 28N 29S 30R 31N 32S 33R
**§5.6:** 1U 2N 3A 4A 5U 6X 7U 8N 9N 10F 11S 12A 13N 14P 15U 16F 17F 18N 19F 20A 21C 22A 23N 24R 25A 26A 27A 28F 29F 30A 31N 32B 33A 34B 35B 36X 37N 38A 39B 40A 41F 42N 43A 44A 45F
**§5.7:** 1A 2A 3B 4D 5F 6L 7X 8A 9D 10U 11D 12D 13D 14D 15D 16D 17A 18D 19X 20D 21A 22B 23D 24A 25R 26D 27C 28A 29D 30D 31D 32C 33A 34A 35D 36P 37N
**§5.8:** 1C 2C 3O

P02 batch 2 (order of `docs/knowledge/P02.md` "Corrections", rows not in README §5): L00 0x0C16 **L**; L00-B6 **X**;
D01 0x080A trigger **R**; W04 0x7037 **L**; D02 0x0844 / 0x10CA **B**; D02 P02-B7 … B9 **U**; D02 0x10D2 **O**; W01
blob tails **U**; W01 0x101C order **T**; Z01 `ws_save2worldmanager` list and callers **R**; Z01 0x180C `always99`
**F**; link round robin **T**; W03 0x987A **U**; Z13 `PacketOrder` **U**; Z04 `attrLen` / `bind` **F**; Z05 0x305C
**U**; Z05 0x3C08 **U**; D03 0x0446 **U**; S01 layouts without ref (two rows) **L L**; Z03 death "by the dead bit"
**F**; Z03 SkillDamage flag **U**; Z03 0x240C / 0x2452 types **Z**; Z09 hunt-log flush **B**; Z04 0x500B recipients
**B**; Z01 0x4001 / 0x401A **F**; D02 0x400B **L**; Z02 `FUN_005cc2a0` **N**; Z12 0x4025 sender **A**; P02's own WM
pass timing **T** and 0x10B3 "not sent" **R**; decoder struct types **Z**.

### 1.3 Errors per owning item

Owner = the first item named in the row's "Older place". Errors = all classes except A and Z.

| Owner | Errors | By class |
|---|---|---|
| Z03 | 28 | N6 S9 F2 B3 R2 M3 U3 |
| W01 | 20 | N4 F4 O2 B4 T1 C1 P1 U2 X1 |
| L00 | 17 | N3 F1 L3 B6 T1 M1 C1 X1 |
| Z01 | 15 | N5 S1 F5 B1 R2 T1 |
| D02 | 15 | L1 O1 B1 D9 U2 X1 |
| Z02 | 13 | N4 S1 B2 R2 C1 U2 X1 |
| Z04 | 11 | N3 S1 F2 B1 U3 X1 |
| Z07 | 7 | N2 F3 R1 C1 |
| Z08 | 7 | N1 F2 B3 X1 |
| P01 (README, generated files) | 6 | F1 O3 T2 |
| W03 | 6 | S1 F1 L1 B1 R1 U1 |
| D01 | 6 | F1 L1 B1 R1 D1 X1 |
| Z05 | 5 | N1 P1 U3 |
| Z09 | 5 | N2 F1 B2 |
| D03 | 5 | B1 R1 D2 U1 |
| D04 | 5 | C2 D3 |
| W05 | 4 | S3 T1 |
| Z12 | 4 | N1 S1 R2 |
| W04 | 3 | L1 O1 P1 |
| D05 | 3 | N1 D1 P1 |
| C01 | 3 | O1 C2 |
| S01, P02 | 2 each | L2; R1 T1 |
| Z13, Z15 | 1 each | U1; F1 |

No recorded error: W02, Z06, Z10, Z11, Z14, Z16–Z30 (except the rows above), D06, D07, S02, L01. For these the
absence means "not re-read by anyone", not "confirmed": P02 lists what the captures confirm per item
(`capture-validation.md` §13, last paragraph), and that is the only positive evidence.

### 1.4 What follows for the ratings (§2) and the re-check (§3)

1. **Rating rule.** *high* needs a capture row (`capture-validation.md`) or a cited client handler that uses the
   fields. *medium* = read in code, none of the classes applies. *low* = *(inferred)* / *(pdb2017)* only, or a class
   applies by its "Find more" test. A section a later item superseded (README §5, P02) is rated by the corrected
   statement and points to it.
2. **Pre-S01 documents start one step lower for names and offsets** (classes N and S, 50 of 194): L00, W01–W04,
   Z01–Z08, D01–D05. A call or member they name is *low* until an official name (`S01-renames.tsv`,
   `S01-player-offsets.tsv`) or a later item's § confirms it. Character and GameLog have no PDB at all: every
   name in D02–D05 and D07 is ours.
3. **Wire content is not trusted without a capture** (class U, 18 rows; 16 of the 21 P02 bugs are unwritten bytes or a wrong length): a layout read from a
   send site gives the fields, not the unwritten bytes or the length. A client-facing or link packet that no capture
   shows stays *medium* even when the client handler agrees.
4. **Re-check order for §3** (worst first, by errors found per claim that other items cite): Z03 (28; S and N: the
   combat context and abstate tables), W01 (20; B and F: session states, hand-over), L00 (17; B: return paths),
   Z01 (15; N and F: login burst, saves), D02 (15; D: procedure versions), Z02 and Z04. Inside each, first the
   statements that match a "Find more" test and that §5 has not already corrected.
5. **Scenarios** (`capture-scenarios.md`) aim at the classes only a capture settles: U (every packet not yet seen),
   T (order across processes), L (sizes), F (units and enum values, with known UI values), C (which text the client
   shows), and B where a result code can be forced by a DB or SHN setup.

## 2. Ratings per document

State: re-run after capture batch 5 (X09 parts 3 and 4). 49 pseudocode documents (2 249 headings: 149 high, 1 565
medium, 209 low, 326 not rated) and 65 knowledge files (342 headings: 13 high, 253 medium, 28 low, 48 not rated; rated
for the first time: `P05.md`, `X06.md` and `X09.md` §1–§7); 130 hand rows (125 + 5 of X09; Z01 §3.2's reason
rewritten in part 4 after the code read of `docs/knowledge/X09.md` §4). Hand passes: Login, WM, the
shared library and the DB servers (X02 part 2), the zone documents and the knowledge files (part 3), 4 rows set by
the re-check of §3.2 (part 4: `Z01.md` §3 → high, §4 and §6 low → medium, `Z03.md` §2 stays medium), the passes
after batch 3 (X05), batch 4 (X07) and batch 5 (X09), all at the end of §2.2. Before the batch-5 re-run: 150 high,
1 561 medium, 212 low, 326 not rated over the same 49 documents; knowledge 13 / 241 / 28 / 42 over 62 files; 125
hand rows. The ratings are the input of §3; §3 and new captures change them (re-run the generator).

### 2.1 Method

The tables in §2.4 ff. are generated: `python3 -I docs/plan/status/X02-rate.py write` reads every `##`–`####`
heading of `docs/pseudocode/**/*.md` (not `README.md`, `FORMAT.md`) and of `docs/knowledge/*.md` (§2.53 ff.) and
rates the text under it (its own body, up to the next heading) with the rules of §1.4. Hand ratings are in `docs/plan/status/X02-rate-hand.py` and replace
the baseline; such rows say "(hand; baseline: …)". Re-run it after new captures (`annotations/P02.json`), new
README §5 rows or new hand ratings. `… X02-rate.py show <ID> [low]` prints one item, `… sig <ID> <§>` the raw
signals of one section.

What the generator reads:

| Signal | Source | Use |
|---|---|---|
| `cap n/m` | the opcodes written in the section (`0x…`, known to `opcodes.json`) that have an evidence entry in `annotations/P02.json` or a row with "Seen" > 0 in an "Opcodes" table of `capture-validation.md` (`n`), of all its opcodes (`m`). The second source was added by X05: 102 captured opcodes have a table row and no evidence entry (73 of batches 1–2, 29 of batch 3, e.g. `0x0804`, `0x1802`, `0x240E`, `0x3441` / `0x3442`); the batch-4 tables (§22.6, §23.8, §24.9, §25.10) and the batch-5 tables (§26.7, §27.9, §28.8) are read the same way. X07 widened the row form to cells with several opcodes (`0x9007 / 0x9008`, "Seen" `1 / 2`, `2 + 2`, `5 each`): 78 more opcodes, most of them the WM / zone login lists of batch 2 | capture evidence |
| `cv ok` | the § is named in a **confirmed** row of `capture-validation.md` (§11) or in its list of orders confirmed in full (end of §11) | capture evidence |
| `cv corr` | the § is named in `capture-validation.md` §13 (corrected / contradicted / extended by a capture); the correct statement is in `docs/knowledge/P02.md` "Corrections" | class applies |
| `sup×n (README §5.x)` | `n` rows of README §5 name this item and § as "Older place" (a § that is no heading counts for its nearest parent) | class applies |
| `client×n` | lines that cite a client function (an address of `re-data/client-handlers.json`, or "client FUN_…") | client evidence |
| `weak inf / p17 / fh / dbb` | counts of *(inferred)*, *(pdb2017)*, *(fh-doc)*, *(db-backup)* | low when ≥ 3 and ≥ 1 per 2 KB of text, else a note |
| `D: proc …` | D01–D05 only: the section names one of the 27 procedures that differ between `Character.bak` and `w00_Character` (D06 §8.5) | class D |
| `S: p+0x…` | zone only: `p+0x…` offsets that neither `S01-player-offsets.tsv` nor the 2016 `Zone.pdb` knows as a member of `ShinePlayer` / `ShineMobileObject` / `ShineObject` (members flattened 3 levels: 1 587 offsets; plus the 16 × 51 cells of `smo_Param`, Z12 §1.1). Low from 2, in a pre-S01 document from 1. Part 3 added the PDB lookup: of 214 distinct `p+0x…` offsets in the zone documents and knowledge files, 2 remain unknown (`p+0xaad8` in Z04 §3.2, a u32 index: ×4 = +0x2ab60 `sp_PetInfo`; `p+0x2` in Z15, a packet pointer) | class S |
| `S: n offset lines …` | knowledge files of pre-S01 items: at least 3 lines with a `+0x…` offset and none of them names a 2016 PDB member | class S (and N: the member names are ours) |
| `pdb n/m` | knowledge files: of the `m` lines that write a `+0x…` offset next to a member name of a 2016 server PDB (any struct of the five PDBs; names with more than 12 different offsets are skipped), `n` have the PDB's offset. Cache: `docs/plan/status/X02-pdb-members.tsv` (`X02-rate.py pdbcache`) | struct evidence |
| `N: name` | the section uses a name README §4.8 lists as misleading for this item | class N |
| `B×n` | "packet / request is ignored", "else ignored", "no-op", "unconditional" (not: a field or a result ignored) | class B: low in a pre-S01 document, a note from 3 elsewhere |
| `R×n` | "dead code", "legacy", "never sent", "no sender", "unreachable", "never called", "no caller" | class R: low in a pre-S01 document, else a note |
| `ours×n`, `no PDB` | names marked as ours in a pre-S01 document; Character / GameLog documents (no server PDB) | note |
| `no function cited` | no `FUN_` and no opcode under the heading | low in a pre-S01 document, else medium |

### 2.2 The ratings and how to read them

- **high**: read in code, and a capture shows it: at least half of the section's opcodes have capture evidence
  (and at least two, or the opcode is in the heading), or `capture-validation.md` confirms the § and a third of its
  opcodes are captured; and no class of §1.2 applies. A section without opcodes is high when it cites the client
  function that does what it says. "High" covers the paths the captures took: the normal path. Error branches of a
  high section are still code only.
- **medium**: read in code only. Also: a captured section in which a class applies (the captured part is right, the
  rest was already wrong once), a DB section whose packets were captured (a capture shows the link packets, not
  the SQL), and every bug table (class X: the effect of a bug is a deduction until a capture shows it; captured
  bugs are marked in README §6.1).
- **low**: a class of §1.2 applies and no capture covers the section, or the section rests on weak markers.
- **–** (not rated): "Not reconstructed", "Coverage boundary" and headings that only introduce their subsections.
- **Knowledge files** (§2.53 ff.): their sections are fact lists for other items, so a captured opcode that is
  mentioned raises nothing (`cap n/m` is shown, not used). A section is **high** when it is a struct table whose
  offsets are the 2016 PDB's (`pdb n/m` with m ≥ 3 and n ≥ 80 %): the compiler's record is the second source for
  the layout, as a capture is for a packet. The meaning column of such a table is still code only. `pdb n/m` with
  fewer than half agreeing is a note, not a rating: most such lines write an absolute offset of a nested member
  (`X02-rate.py pdbmiss K:<ID>` lists them; §3 part 4 reads the list). Low as for pseudocode, plus the two `S:` rows
  of §2.1.

"Raise by" names the cheapest step: `capture 0x…` = the client-facing opcodes of the section no capture has shown
(they become scenarios in `docs/plan/capture-scenarios.md`, part 8); `re-read the rest (§3)` = the section already
had a correction, the adversarial re-check of §3 takes it; `D06 §8.5 version` = replace the backup version;
`follow the return value to the parser` = class B; `PDB member` = look the offset up in the 2016 PDB.

Limits of the baseline (why the hand passes exist):

- An opcode counts as captured when any capture shows it, on any link. A section that only mentions a captured
  opcode gets the credit too. The rule "at least two, or in the heading" removes most of these.
- A capture confirms the fields and the order on the path taken. Unwritten bytes show only when they differ from
  zero, and branches not taken stay unconfirmed (class U: 16 of 21 P02 bugs).
- The keyword tests find candidates. A `B×1` or `R×1` row may be a correct statement: §3 decides.
- A section with no signal is medium because nothing was checked, not because something agrees.

**Hand pass, part 2 (Login, WM, shared library, DB servers): what the tables show.**

| Document(s) | Finding | Consequence |
|---|---|---|
| L00 `login-server.md` | 16 coarse sections; §4 (all client handlers) and §5.1–§5.3 are captured on the normal path but carry most of the 17 rows of README §5.2 (mostly class B, then N and L). L01 re-read the process and the parsers with PDB names | read L00 only together with L01 and README §5.2; §3 re-checks the handler return paths that L01 did not list (§5.4 OPTool: nothing captured, 2 corrections) |
| L01 | no low section; high where the captures show the session pool, the seed counter and the world table. Login's own heartbeat never fired in a capture (hand: §1.6 medium) | one scenario: 60 s on the login screen |
| W01 | 10 low, 15 medium of 33: the most corrected WM document (§2 startup, §4.1 create / delete, §5.1 / §5.4 logout, §6 CharDB link, §7.1 zone registration). §7.2–§7.5 (hand-over, saves) are captured and corrected by P02 batch 2: medium, read with `docs/knowledge/P02.md` | §3 part 5 (hand-over) starts from P02's corrected order, not from W01 §7.2 |
| W02 party / raid | 1 high section of 45 (§4.3, hooks on the map login): no party or raid was ever captured. All replies and result codes are code + client only | highest yield for a scenario: two clients, party then raid (part 8) |
| W03 guild | no high section: the captures show a character without a guild (only the load and 0x987A / 0x987B at :00). 11 low (academy, tournament data, emblem) | guild scenarios need the DB setup "guild with N members" (part 9) |
| W04 | high only for what a solo session shows (notice §2.2, PK field §3.1, friend list §5.1, option push at login §8.1, holy-promise relation object §12.1, chat block list §14); KQ, prison, reports, holy-promise requests and instance ranking are uncaptured | scenarios by feature; 0x7037 (§8.2) corrected by a capture |
| W05 | written with the PDB; high where captured (session take / reset, zone saves §5.5, world-login entry §5.3) | none beyond the opcodes listed |
| S02 | library code, no opcodes: medium throughout except the receive framing §1.7 and the frame builder §1.8 (hand: high, every captured stream parses) | error paths (pool exhaustion, partial frames) can only be tested with a custom client |
| D01 | 9 low of 18: 6 superseded statements (README §5.7) and the "packet is ignored" wording of §1.1 / §2 (class B: `return 0` in a DataServer handler was never followed to the parser) | §3 part 7 |
| D02 | 19 low of 27: the document with the most class-D rows (9); every section that names one of the differing procedures is low until read with D06 §8.5; §6 saves and §12 attendance corrected by captures | a rebuild reads D06 §8 first; §3 re-checks §4 (character load, captured) against the w00 procedures |
| D03 | 17 low of 50; §2 shop is the only confirmed section (item transaction, `capture-validation.md` §7.6.1). Dice, gamble, mini-house, pets: nothing captured and weak markers | scenarios with DB setups (part 9: `docs/knowledge/D03.md` "For capture scenarios (X02)") |
| D04 | 15 low of 29: almost every section rests on *(db-backup)* procedure bodies (60 markers) and no capture reaches quests, skills, guild or prison writes with a visible result | as D03 |
| D05 GameLog | 12 low: `nType` meanings marked *(pdb2017)* (§2.3, §4.3), commands "no 2016 server sends" (§2.4, class R) | §3 part 7 checks §2.4 against every `handlers.json` `sends` |
| D06 | sections §2–§7 describe procedures that no backup contains: never high, even when the calling packet was captured (rule for all DB documents, and a cap in the hand file) | DB setup + capture of the answer, per procedure |
| D07 | all medium: read in code after S01, no PDB for the Character server, nothing captured (reward items) | scenario with a reward row inserted by SQL |

Counts of this pass are in §2.3. The low rows of L00, W01, D01 and D02 are the input of §3 parts 5 and 7; the
`capture 0x…` cells of W02, W03, W04 and D03 are the input of the scenarios (part 8).

**Hand pass, part 3 (zone documents): what the tables show.** The capture set is: login and character load, idle,
walk / run / stop, town and link portals, one shop session (buy, equip, storage, unequip, sell, HP / SP stones), one
combat session (swings, Bash [01], pick-up, death, revive, `&levelup 3`, `&linkto`, the Wooden Horse mover), with
the server links in the last two. No capture has a second player in sight, a party, a guild, a pet, a silver wing, a
quest step, a KQ being played or a scripted map. Every "high" of the baseline was checked against that list: 43 of
the 96 zone rows were high only because the section mentions opcodes of another flow (baseline limit 1) and are
medium by hand.

| Document(s) | Finding | Consequence |
|---|---|---|
| Z01 | high: map login §5 / §5.2 / §5.3 and disconnect §8.3 (captured in every session, links included). §6 (0x1803 burst) and §8.4 (saves) are captured **and** corrected by P02 (3 + 2 rows): medium. 11 low: startup, objects, seed, wing, the handshake §3.3 | §3 parts 4–5 start from the P02 rows, not from Z01 §6 / §8.4 |
| Z02 | high stays for stop, mode change, NPC menu ack; §5.1 (client 0x1C01) and §11 (0x2070) were incidental. 9 low are flows never captured and already corrected once (emotes, role actions, gathering, wedding, scenario areas) | scenarios: emote, gathering, second client in sight |
| Z03 | the worst owner (§1.3): 17 low, all `sup` (README §5.5). High only for what the combat capture walks through: targeting, bash stop, Bash [01] cast, player death. The damage formula §4 is low throughout: a capture shows the result, not the terms | §3 part 4 (combat context, abstate tables); scenario with known stats so the 0x2448 damage can be predicted |
| Z04 | 4 high (move, unequip, storage close, premium inventory open); ring / mini-monster equip and premium withdraw were incidental. 13 low: drop, pick, enchant, endure, reward inventory (P02-B3) | scenarios per request; DB setup for a charged item and a reward item (part 9) |
| Z05 | no high left: capsule buy, item-money buy and item use only shared the buy answer 0x3004 / 0x3016. The commit model §1 is confirmed by P02 for both styles but §1.4 was corrected (P02-B16): medium | §3 part 5 (ITEMDB order) |
| Z06 | 1 high (coin state at login and save); booths, dice, coin exchange uncaptured, 6 low (`g_NoBooth`, range check names) | two-client booth scenario |
| Z07 | 2 high (revive, 0x10B4); 16 low, mostly `sup` (blob handlers §1.2, wedding §5, mini-house §6, cards §7) | §3 part 6; mini-house and card scenarios |
| Z08 | 1 high (quest reset times); party status, quests, KQ, licences, guild: 8 low, nothing captured | scenarios need a second client or DB setups |
| Z09 | 268 sections, 8 high after the hand pass (per-minute block, mob routine and fighting, weapons timing, MoveManager, mob paths, sight, drop items). 9 were incidental: NPC internals, servants, Lua events / actions / moves / item functions / mob settings, boss fields, data files | the Lua layer has no capture at all: one scripted map (a KQ) is the highest-yield zone scenario |
| Z10 | no high left (0x0830 speed check not captured); otherwise medium, written after S01 | custom-client test only |
| Z11 GM commands | no high left; only `&levelup` and `&linkto` were captured (rated in Z12 §5.2, Z01 §7). 56 medium | GM commands are cheap to capture: one session running the list (part 8) |
| Z12 | 4 high (level-up side effects, character blocks §6.2 / §6.3, single options §7.1). Two `S:` lows of the baseline (§6.1 and the bug table) were exact PDB members (generator fixed) | none |
| Z13 | 9 high: the mount (ride item cast, mover object, speed, brief info, map-link rebuild) and mini-monster info, all from the Wooden Horse and the login. Pets: re-summon §5.8 captured only with no pet (medium), routine §6.4 incidental | pet scenario |
| Z14, Z19–Z22, Z24, Z27–Z29 | no high, no low: data loaders and tables written after S01, read in code with PDB names, nothing on the wire | a wrong table read shows only as a wrong effect in play; SHN experiments (part 9) |
| Z15 | no high left: the four "client" highs cited the client only for sharing the quest library | quest scenario (accept, progress, finish) |
| Z16 | 1 high: KQ make 0x580D / 0x580E (WM timer, captured on the links). Everything a player does in a KQ is medium | KQ scenario |
| Z17 | 2 high (cool-down groups, login restore: 0x482C in every login) | item with an action set |
| Z18 | 6 high: login-burst helpers, session accept / seed, abstate batch, server menus, blast queue, collection-card blocks | none |
| Z23, Z25 | 1 high each: WM skill cache saves §7.3; blast selection §6.1 (Bash [01]: 0x244E → 0x2457 → 0x2452). Toggle skills and chain blasts were incidental | skills of other classes |
| Z26 silver wing | **all 11 highs removed**: no capture contains a silver wing. The baseline matched the NPC server menu, the ride item and `&linkto` | one scenario settles the whole document: save a location, fly (part 8) |
| Z30 | 1 high (0x4025 UI state save, captured after the level-up) | none |

**Hand pass, part 3 (knowledge files).** 272 headings in 52 files; most are fact lists, 32 are not rated (containers, open points).

| File(s) | Finding | Consequence |
|---|---|---|
| `Z01.md` §4 ShinePlayer members | **low**: 36 offset lines with our names and 3 *(inferred)*; S01 mapped every offset to a PDB member (`S01-player-offsets.tsv`) and corrected 2 meanings (+0x29638 title object, flag bit 3 `SoloingMode`). The most cited table of the tree | first target of §3 part 4: compare meaning by meaning with the TSV, not offset by offset |
| `Z02.md` §2, `Z06.md` §1–§2, `Z07.md` §2, `W02.md`, `W04.md` | **low**: offset lists of pre-S01 items without one PDB member name (22, 11 + 6, 10, 7, 18 lines) | §3 part 4 resolves them with `pdb.py`; a rebuild uses the PDB struct, not these lists |
| `Z10.md`, `Z15.md` §2, `Z16.md`, `Z18.md`, `Z20.md`, `Z09.md` §0 | **high**: struct tables whose offsets are the PDB's (7/7, 3/3, 8/8, 5/6, 3/3, 3/3) | none |
| `Z03.md` | medium, but about ten `player+0x…` lines carry our names; `player+0x17d0c` "CharaterSkillList" against `Z23.md` "`sp_SkillList` at +0x17d08 (0x24 bytes)": the same object, 4 bytes apart | §3 part 4 (which one is the list, which a member of it) |
| `D01.md`, `D02.md`, `D04.md`, `D05.md` | low where they name a procedure that differs between the backups (class D) or state facts without a function | read with D06 §8.5 |
| `S01.md` §2.3, §3 | low by the weak-marker rule: these sections list the 2017-vs-2016 differences and open follow-ups, which is their purpose | none (not claims about the server) |
| `C01.md` | hand **high** for the four scene dispatch tables whose opcodes the captures show (Account, LoginWorld, ZoneLogin, Link); the other scenes medium (read in the client only) | scenes of uncaptured features follow their scenarios |
| `P02.md` | hand **high**: capture findings | none |

**Hand pass after capture batch 3 (X05 part 4).** The two tables above describe the state after batch 2 and are
kept as written; their counts no longer match §2.3. The re-run reads three things that changed since: the batch-3
evidence in `annotations/P02.json` (captures `s14`, `s21`, `s21b`–`s21d`, `s37`), the batch-3 rows of
`capture-validation.md` §11 / §13, and the README §5 rows added since (X03, X04). Batch 3 adds to the capture set: a
second client in sight (appear packets, `0x1C01`, moves, jump, emote, stance, shout, whisper, a fight seen by a
third player, `&hide` / `&show` / `&dimension`), GM items (`&makeitem`, `&getmoney`, `&cleariv`), split and merge,
drop and pick-up, destroying an item, potions, rings, unequip with a full inventory, storage money, selling and
buying back, soul-stone purchases, a failed purchase (S16), an expired item (S13), a stack over `MaxLot` (X3), login
refusals, character create and delete, 7 min idle on the character list, and a stop and start of the WM and the
zones on all links. Still in no capture: party, raid, guild (the world has none), pet, silver wing, quest step, KQ
play, scripted map, booth, mini-house.

The re-run also fixes a gap of the generator: `cap n/m` read only the evidence entries of `annotations/P02.json`,
and 102 opcodes that the "Opcodes" tables of `capture-validation.md` count as seen have none (§2.1). Sections were
therefore told to "capture" packets that are captured (the heartbeat `0x0804`, `0x1802`, `0x240E` / `0x240F`, the
abstate packets `0x1C18` / `0x2428` – `0x242A`, the GM item pair `0x3401` / `0x3402`, `0x3441` / `0x3442`).

Of the sections that existed before, 123 changed their rating (the four new documents and the new knowledge files
are rated for the first time):

| Change | Rows | Why |
|---|---|---|
| medium → high | 52 | a capture shows the section's own packets (batch 3, or batches 1–2 through the table rows now read). These are the rows left after the check: every new high of the baseline (103: 50 of these rows, 5 in the new documents Z31 / Z32, 48 below) was compared with the capture set; 48 were high only from opcodes the section mentions (baseline limit 1), or captured with a correction, and are medium by hand, see below. Two older hand rows were lifted (Z02 §5.1: `0x1C01` 18 × in `s14`, capture-validation §18.2; Z05 §6.1: `0x343E` / `0x343F` → `0x3440` in `s21`, §19.6) |
| low → medium | 35 | a section with a class (README §5 row, `cv corr`, B / R keyword) that a capture now covers: "a captured section in which a class applies" (§2.2). L00 §5.1 / §5.3, W01 §2 / §4.1 / §5.1 / §6.3 / §7.1 (create, delete and the restart in `s37`), W03 §4.5, W04 §6.1 / §15.2, W05 §1.4 / §5.2, Z01 §1 / §3.3 (S2S handshake), Z02 §1 / §5, Z04 §3.1 / §3.3 / §6.3 / §8.3 (drop, pick-up, potions), Z05 §3.1 / §5.1 / §7.1 / §9.5, Z07 §1.2 / §1.5 / §5.4, Z09 §2.4, D02 §3 / §6 / §7.1, D03 §1.2 / §2.1 / §2.2 / §5.1 |
| medium → low | 27 | not from a capture: README §5 rows added after X02 (X03 / X04 moved superseded statements into the register) name these sections as "Older place", and no capture covers them. W02 §1.1 / §1.6 / §4.1, W03 §2.8 / §6.3, W04 §12.4, Z01 §4.3 / §8.1 / §8.2, Z02 §3.4, Z03 §1 / §6.6, Z04 §12.5 / §12.6, Z05 §1.3, Z06 §5, Z08 §10, Z09 §6.1, Z11 §3.4, Z15 §6.3, D01 §4.1, D02 §1.1, D03 §12, D05 §7.5, and the bug tables of L01, Z12, Z16 |
| high → medium | 5 | captured sections that a new README §5 row or a batch-3 correction names: Z01 §5.2, §5.3, §8.3, Z07 §10.2, Z09 §9.6 (the appear packets are confirmed, capture-validation §18.2; the row is the sight correction of §13) |
| not rated → low / medium | 4 | containers whose own text a README §5 row names (L00 §1, Z01 §3, Z07 §6 low; Z05 §1 medium) |

Hand rows of this pass (`X02-rate-hand.py`, the two blocks "X05 part 4": 48 new rows, 2 lifted, 2 reworded):

| Row(s) | Hand rating | Reason |
|---|---|---|
| W03 §1.1 | medium | the guild manager is captured only as the start-up load of a world with 0 guilds (`0x7457`, `0x74BD`, capture-validation §17.3) |
| Z04 §7.2 | medium | the storage open `0x3444` is captured, the page request `0x3028` was never sent by the 2016 client (§20.1): test-client case T16 |
| Z05 §2.4 | medium | soul-stone purchase captured twice, and the capture corrected the `0x3441` / `0x3442` layouts (§20.5); the refusals `0x3443` / `0x5005` are open (scenarios 46 / 47) |
| Z04 §5.2 (reworded, stays medium) | medium | both rings of `s21` were equipped with `0x300F` (§19.7): the 2016 client did not send `0x3010` |
| L01 §1.6 (reworded, stays medium) | medium | the client holds no Login connection on the login screen and polls `0x0C1B` on the world list (§16.2): the Login heartbeat needs test-client case T15 |
| Z12 §3.3, Z25 §1.3 | medium | captured for another case only: parameter pushes of other classes (no Sentinel or Savior in a capture *(inferred from the classes the captures name)*); the blast slots only for Bash [01] of a player against a mob |
| W04 §2.5, L01 §4.4, Z02 §9.1 / §9.2, Z04 §6.4, Z09 §8.7 / §9.2 / §16.6 / §19.3 / §23.8 / §25.3 / §28.8, Z12 §7.4, Z13 §5.3 / §6.5, Z15 §5.3, Z16 §2.6, Z17 §3.4.2, Z18 §1.4 / §4.9 / §6.3 / §6.4 / §6.6, Z21 §3.1 / §5.5 / §5.6, Z22 §7.2 / §7.5 / §9.5 / §10.7 / §12.4, Z25 §2.7 / §2.8 / §2.10, Z26 §1.4, Z27 §7.2, Z30 §8, S02 §1.1 | medium | baseline limit 1: the captured opcodes are player chat, shout, emote, swings, the abstate packets of the login list / Bash [01] / a potion, the potion's `0x301A`, the destroy pair `0x3459` / `0x345A`, `&makeitem`'s `0x3401`, the title blobs and marks, the S2S handshake and heartbeat, or the guild list of a zone start; the section's subject (spammer alert, OPTool, ride feeding, roar / megaphone, mob shout, block checks, absorption, Lua functions, title reset, pet, quest done, KQ items, item actions, set items, the abstate actors bomb / dispel / time attack / enchant, skill specials, silver wing, party / guild helpers, library objects) is in no capture |
| Z31 §3.5, §9.6, §10.2, §11.5, Z32 §5.4 | medium | the same limit in the two documents written after X02's pass (attribute classes, guild buffs of a world without a guild, the send buffer, auto-arrange `0x304A`, coin items) |

Kept high after the check (the capture walks the section's own path): L01 §1.4 / §2.2 / §4.2 / §4.3, W01 §2.1, W03
§9.1, W04 §2.1 / §2.4 / §6.2 / §6.3, W05 §1.2 / §1.5 / §1.6 / §4.5 / §5.4, Z02 §2.4 / §5.1, Z03 §6.3 / §7, Z04 §7.1 /
§13.1, Z05 §1.5 / §2.1 / §2.2 / §3.2 / §6.1 / §6.4 / §9.1, Z07 §1.4 / §3.3, Z09 §11.8 / §19 (`cScriptMsg_World` at
zone start, Z09-B72), Z11 §1.1 / §4.3 / §7.3, Z12 §4.2 / §4.3 / §6.1, Z13 §2.7 (the end-time check shared with the
charged items, capture-validation §21.2; no furniture expired), Z18 §2.3 / §3.2 / §4.3 / §4.4 / §6 / §6.2, Z22 §1.4,
Z25 §6.2, Z26 §5.3 (`uib_AfterCast` of the potions, not a silver wing), Z30 §3, Z31 §2.5 / §4.2 / §9.5 / §10.1, Z32
§3.3, D02 §3.4, D03 §3.3 / §4. As before, "high" is the path taken: of W04 §2.1 the failure `0x200E`, of Z05 §2.2
the refusals and `0x34BA`, of Z05 §3.2 the three fail answers, of W05 §5.4 the house / pet / emblem blobs, of D03
§3.3 `0x3431` are open (capture-scenarios 45–47, 49). The check was made from the section titles, their opcode
lists and the capture-validation text; no code and no section body was re-read in this pass, so a "kept high" row
means "its own packets are in a capture", not "re-verified".

**Hand pass after capture batch 4 (X07 part 3).** The batch-3 block above is kept as written. The re-run reads the
batch-4 evidence (captures `s24`, `s37b`, `s38`: the "Opcodes" tables §22.6, §23.8, §24.9, §25.10 of
`capture-validation.md` and the batch-4 entries of `annotations/P02.json`) and the batch-4 rows of §11 (from
"Character create refused" on) and §13. Batch 4 adds to the capture set: the create refusal, both renames (free
rename, rename right `0xB40F`), a tutorial skip refused (P02-B33), a zone down at character login, back to character
select and quit on all links, the zone connection lost and the 10-s Kickout save, zone kills after `&getmoney`, the
10-min auto-save; the skill master and a skill book, empower, stat points up and down, both reset capsules, skill
saves `0x4009` / `0x400A`, auto-arrange, a Damaged Mystery Vault; cast abort, Dash (ground target), the toggle Heat of
Fury with its area drain, abstate reset conditions, `&resetabstate`, poison damage over time, death by a mob, revive
by skill and town revive. Still in no capture: party, raid, guild, pet, silver wing, quest step, KQ play, scripted
map, booth, mini-house, mob skills, `0x243E` (the client's assist sends `0x2401`), the server refusals the client
pre-empts (capture-scenarios 51, T23, T24).

Of the sections that existed before, 37 changed their rating (`X07.md` §1–§3 are rated for the first time; the
review of X07 part 5 set two of the 23 new highs back, last row):

| Change | Rows | Why |
|---|---|---|
| medium → high | 23 | a batch-4 capture shows the section's own packets or confirms it in §11: W01 §10 and Z03 §10 (client cross-check summaries, now 14 of 21 / 31 of 43 opcodes captured), Z03 §5.5 / §9.3, Z05 §9.8 (Mystery Vault, §24.8), Z07 §2.2 / §2.3 / §2.4, Z08 §11, Z09 §9.3 (Dash), Z22 §3.3 (DoT) / §4.2 (the area part of the toggle, only its `num 0` path: no enemy in range, §25.4), Z23 §2.3 / §2.5 / §3.1 / §4 / §6.2 / §7.1 / §7.2 (skill-save wire; the DB columns against a snapshot with the cool-time column are open, capture-scenarios 51), Z25 §6.3, Z30 §1.2; by hand Z09 §8.5 (no opcode: the blast-to-effect delay rule matches all four batch-4 skills within one tick, §25.4) and Z31 §11.5 (the X05 hand row is removed: `0x304A` → `0x304B` → exchange captured, §24.8) |
| low → medium | 12 | a section with a class (README §5 row, `cv corr`, D, weak markers) that batch 4 now covers: "a captured section in which a class applies". D01 §4.2, D02 §3.3 / §3.5 / §7.2 / §14, D04 §2 (DB sections whose link packets are captured), W01 §5.4 / §6.1 / §6.2, Z01 §8.1, Z03 §5.4, Z04 §12.5 |
| high → medium | 1 | W01 §3.3: batch 4 corrects it (the list's map is patched to "RouT", §13 → X06) |
| medium → low | 1 | Z03 §2.6 `0x243E`: the client's assist sent a plain `0x2401` (§25.5), and the 2016 client has no path that sends `0x243E` (`X07.md` §2); hand row with that reason, raise by test-client case T25 |
| high → medium (review, part 5) | 2 | Z23 §2.5 and Z23 §4 (hand rows `X07 review`): batch 4 captured them with one learned step only; each keeps an uncaptured point of its own (the lower-step case Z23-B1 and the inferred Z23-B20 field cast; the step ID the client names in `0x4811` with two learned steps, which decides Z23-B8): capture-scenarios 51 steps 1 and 3. Net: 21 medium → high |

Generator change (`X02-rate.py` `load_inputs`): an "Opcodes" table row may name several opcodes in one cell (`0x9007 /
0x9008`, `0x1021 / 0x10CD / 0x10D6`); the old pattern read only rows with one opcode and an `NC_…` name, so 78
captured opcodes (the batch-2 login lists `0x1021` – `0x10E9`, `0x400F` / `0x4029` / `0x402B`, soul-stone and shop
pairs, the toggle pair `0x245C` / `0x245D`, `0x9008`) counted as uncaptured. Read now, they raised 7 sections, all
set back to medium by hand (the lists were captured empty, below).

Hand rows of this pass (`X02-rate-hand.py`, the two blocks "X07": 22 new rows, 1 removed, 11 reworded):

| Row(s) | Hand rating | Reason |
|---|---|---|
| Z03 §9.4, Z09 §2.3 / §12.6 / §17.3 / §26.4 / §29.2, Z13 §4.6, Z20 §5.2, Z23 §1.3, Z25 §1.1.1, Z26 §5.5 | medium | baseline limit 1: the captured opcodes are the skill-book learn (`0x4801` / `0x4802` / `0x4804`), the DoT damage `0x243C`, Dash `0x2450` / `0x2451`, the invalid-command answer `0x2011`, the potion use; the section's subject (`0x4822` production field, game-mode tick work, magic fields, Lua and Pine functions, the Z09 bug table, the partner summon, the skill-name trie, vtable slots, special-member readers, `0x304E`) is in no capture or not on the wire |
| Z11 §3.4, §5.2 | low (kept) | a class applies and the batch-4 opcodes are mentions only: `0x304A` came from the client's own auto-arrange, not a debug wrapper; `0x2011` / `0x243C` are the invalid `&resetabstated` and the poison, no mob tool was used |
| W04 §3.3 / §11, Z09 §14.5, Z15 §4.2 / §5.7, Z17 §3.5, Z28 §5.2 | medium | raised by the widened table read only: the login lists (quest diary, passives, charged buffs, item-action cool-downs, card collection) were captured empty (`n 0`, capture-validation §5.2, §7.4, §7.5), like the guild list of W03 §1.1; Z09 §14.5's jump / emote are mentions |
| Z03 §2.6 | low | see the table above |
| Z09 §8.5 | high | see the table above |
| Z22 §10.7, Z23 §2.4 (reworded, stay medium) | medium | now captured (the toggle's keep-time path; its automatic switch-off by unequip, low HP, map change, §25.4) but extended by batch 4 (P02-B39, P02-B38; §13 → X06): a captured section in which a class applies |
| Z25 §1.3, Z18 §3.8 (reworded, stay medium) | medium | the reasons name the batch-4 skills (Dash, Heat of Fury, Divine Shield, Revival) and skill teach / empower; the mob-side slots, polymorph and the other helper rows are still code only |
| Z22 §7.2 / §7.5 / §9.5 / §12.4, Z25 §2.7 / §2.8 / §2.10 (reworded, stay medium) | medium | the list of captured abstates names batch 4 too; the bomb, dispel / cure, time-attack and party-enchant actors and the skill specials are still in no capture |

Kept as the baseline rates them after the check: Z03 §5.2, W01 §5.2, Z05 §6.1, Z12 §7.1 (high, unchanged); the other
sections batch 4 names stay medium because a class applies (W01 §3.2 / §4.1 / §4.2 / §5.1 / §7.2, Z01 §5.3 / §6 /
§8.3 / §8.4, Z03 §7.3 / §9.1, Z11 §4.4 / §7.4, D02 §6, D03 §9: README §5 rows or §13 corrections) or only part of
the section is captured (Z03 §9.5 skill unlearn `0x4824`: in no capture; its `cv ok` is a false match of the §11 row "Death by mob, revive by
skill", whose `§9.5` is capture-validation's own §9.5; Z09 §28.3: only the
`AbStateReset` part of `MiscDataTable` is confirmed, `0x10AF` is not captured; Z25 §6.4: the one-hit queuing path,
not the multi-hit one). D02 §5 stays low (class D: `p_Char_Login` / `p_Char_Logout` differ between the backups; the
capture shows `0x1037` with the WM's copy, P02-B36). As in the batch-3 pass, the check used the section titles, their
opcode lists and the capture-validation text; "high" is the path the captures took (of Z07 §2.2 – §2.4 the refusal
codes 0xAC2 – 0xAC7 of `0x1061` / `0x1067`: test-client cases T10, T24; of Z08 §11 the failures `0x9009` / `0x900A` / `0x900E` / `0x900F`:
capture-scenarios 51; of Z23 §4 / Z03 §9.1 the refusals of `0x4814` 0x882 – 0x889: T23; of Z03 §9.3 the teach failures `0x4803`
/ `0x4805` are open).

**Hand pass after capture batch 5 (X09 part 3).** The batch-3 and batch-4 blocks above are kept as written. The
re-run reads the batch-5 evidence (captures `s45`, `s46`, `s52`: the "Opcodes" tables §26.7, §27.9, §28.8 of
`capture-validation.md` and the batch-5 entries of `annotations/P02.json`) and the batch-5 rows of §11 (from
"Split-and-merge, onto a full stack" on) and §13 (the rows "→ X08"; the three "→ X09" rows correct scenario texts,
which have no rating). Batch 5 adds to the capture set: split-and-merge onto a fuller stack and the exchange onto a
stack at `MaxLot`, a buy-back onto the first empty cell, the level and full-inventory buy-back refusals; a second
player in sight seen by a bystander (walk relay, leaving and entering sight at both speeds, sit and the step that
ends it, jump, a shout out of sight, a mob's swings and B's death, three cast aborts by a step and a full cast, a town
revive on the same zone), the spam-filter set `0x0846` → `0x0847`, a whisper to an unknown name (`0x200E`),
`&mobbreed` / `&mb`; the second `0x1001` with the stale tutorial copy, a rename onto a taken name with the 2016
procedure (P02-B42), `&kickout` on one zone (`0x0C1A` with a real user number → `0x0C17`) and across zones (Z11-B6),
the SHN refusal `0x1804 {0x147, idx}` and the start-up crash on a table with one byte appended (P02-B43). Still in
no capture: party, raid, guild, pet, silver wing, quest step, KQ play, scripted map, booth, mini-house, mob skills,
`0x243E`, the zone refusals the 2016 client pre-empts (`0x366C`, `0x5005`; the money and soul-stone refusals of `s46`
were the client's), `0x3443`, `irm_Exchange`'s `0x24A` and the `irm_Move` / `0x20A` branch, `0x2022` / `0x2023`,
`0x2020 {6}`, lookups by a name two characters share (capture-scenarios 47, 53, 54, T18, T26–T28).

Of the sections that existed before, 6 changed their rating (`P05.md`, `X06.md`, `X09.md` are rated for the first
time; the generator alone changed 8, two of which the hand rows below set back):

| Change | Rows | Why |
|---|---|---|
| medium → high | 1 | Z01 §11 (client cross-check summary): `0x1804` (§28.6) makes 9 of its 18 opcodes captured, as X07 raised W01 §10 / Z03 §10 |
| low → medium | 3 | a section with a class (README §5 rows, `cv corr`) that batch 5 now covers: Z02 §4 (emotes: Sit `0x2020 {7}` → `0x2021`, the step that ends it, §27.3; hand row with the open sends), Z03 §5.6 (effect application of a full cast beside a bystander, §27.7), Z03 §7.1 (the death of B beside A, §27.6) |
| high → medium | 2 | captured and corrected by batch 5 (§13 → X08): Z04 §4.1 (the `b ≥ MaxLot` exchange branch; hand row: `0x24A` and `irm_Move` / `0x20A` are scenario 53) and D03 §3.3 (the `0x0456` log tail order) |

Hand rows of this pass (`X02-rate-hand.py`, block "X09 part 3": 5 new rows, 1 reworded):

| Row(s) | Hand rating | Reason |
|---|---|---|
| W04 §17.2 | medium (baseline: high) | only the set path `0x0846` → `0x0847` is captured (§27.4); the load `0x0844` and the push `0x0845` appeared in no capture (no `usp_SpamFilter_get` row, §7.4), so W04-B60 could not show. Raise by: set the filter, then a new character login and map login of the same account |
| Z11 §4.2 | medium (baseline: low) | the baseline saw only `cv corr` (no opcode in the section), but `&mobbreed` / `&mb` are captured in `s45` ("Mob : 5989", §27.6): a captured section in which a class applies |
| Z04 §4.1, Z02 §4 | medium (as the baseline) | the reason names the batch-5 paths and the "raise by" the scenario of the open branches: 53 (`0x24A`, `irm_Move` / `0x20A`), 54 and T27 (`0x2022` / `0x2023`, `0x2020 {6}`) |
| Z01 §3.2 | medium (as the baseline) | sight delivery to a bystander is captured, but the section gives every `so_AllInMap0..5` the sight cells and `ali_Work` a sight check, while the shout of `s45` (`so_AllInMap1`, "receivers filtered as in Z01 §3.2" per Z02 §3.2) reached a player out of sight (§27.4): one of the two statements is too general *(inferred; not in §13)*. Raise by: re-read the rest (§3) |
| Z05 §2.4 (reworded, stays medium) | medium | in `s46` the 2016 client refused both soul-stone cases itself (no `0x5001`, §26.5): `0x5005` needs test-client case T18, `0x3443` scenario 47 step 3 (S17) |

Kept as the baseline rates them after the check: Z05 §2.2 (sell and repurchase: the first empty cell, §26.3), Z04
§13.1 (soul-stone purchase; its refusals are the client's), Z02 §2.4 (jump), Z03 §3.4 / §7.2, Z23 §3.1, W04 §2.1
(whisper, now with `0x200E`), W01 §5.2 (kicks) stay high: the captures walk their own path, and their open branches
are the uncaptured list above. The other sections batch 5 names stay medium because a class applies (Z04 §2.5 / §4.2,
Z05 §4, D03 §2.2 (class D), Z02 §2.2 / §3.2, Z09 §9.6, Z01 §5.2 / §7.1 / §8.3, Z03 §3.2 / §5.4 / §7.3 / §9.1, W01
§4.1 / §4.2 / §6.2, Z11 §4.5: README §5 rows or §13 corrections) or the capture contradicts them in part: D02 §3.5
(no duplicate check anywhere, P02-B42: "contradicted" in §13, kept medium as a captured section in which a class
applies; its open point, the lookups by a shared name, is scenario 54). As in the earlier passes, the check used the
section titles, their opcode lists (`X02-rate.py sig`) and the capture-validation text; no section body was re-read
except W04 §17.2 and Z01 §3.2, so "high" is the path the captures took, not "re-verified".

<!-- X02-RATINGS:BEGIN (generated by docs/plan/status/X02-rate.py write; do not edit) -->

### 2.3 Summary per file (generated)

Pseudocode documents (`docs/pseudocode/`):

| File | Item | Sections | high | medium | low | not rated | hand |
|---|---|---|---|---|---|---|---|
| `login-server.md` | L00 | 16 | 1 | 8 | 4 | 3 | 0 |
| `login/L01-process.md` | L01 | 27 | 8 | 13 | 1 | 5 | 2 |
| `wm/W01-core.md` | W01 | 33 | 4 | 22 | 2 | 5 | 0 |
| `wm/W02-party-raid.md` | W02 | 45 | 1 | 29 | 8 | 7 | 0 |
| `wm/W03-guild.md` | W03 | 63 | 1 | 42 | 12 | 8 | 1 |
| `wm/W04-social-misc.md` | W04 | 70 | 11 | 38 | 9 | 12 | 4 |
| `wm/W05-process.md` | W05 | 42 | 11 | 22 | 1 | 8 | 0 |
| `wm/W06-leftovers.md` | W06 | 21 | 0 | 16 | 0 | 5 | 0 |
| `zone/Z01-core.md` | Z01 | 33 | 2 | 16 | 12 | 3 | 1 |
| `zone/Z02-actions.md` | Z02 | 36 | 5 | 20 | 7 | 4 | 4 |
| `zone/Z03-combat.md` | Z03 | 52 | 10 | 19 | 17 | 6 | 2 |
| `zone/Z04-items.md` | Z04 | 72 | 5 | 44 | 10 | 13 | 6 |
| `zone/Z05-itemdb.md` | Z05 | 61 | 8 | 38 | 7 | 8 | 3 |
| `zone/Z06-economy.md` | Z06 | 29 | 1 | 16 | 7 | 5 | 0 |
| `zone/Z07-character.md` | Z07 | 52 | 6 | 25 | 14 | 7 | 1 |
| `zone/Z08-content.md` | Z08 | 30 | 2 | 14 | 9 | 5 | 0 |
| `zone/Z09-world.md` | Z09 | 268 | 11 | 207 | 10 | 40 | 23 |
| `zone/Z10-certification.md` | Z10 | 38 | 0 | 28 | 3 | 7 | 1 |
| `zone/Z11-gm-commands.md` | Z11 | 62 | 3 | 52 | 3 | 4 | 5 |
| `zone/Z12-stats.md` | Z12 | 46 | 7 | 28 | 4 | 7 | 2 |
| `zone/Z13-objects.md` | Z13 | 87 | 10 | 67 | 1 | 9 | 5 |
| `zone/Z14-instances.md` | Z14 | 28 | 0 | 24 | 0 | 4 | 0 |
| `zone/Z15-quest-engine.md` | Z15 | 51 | 0 | 45 | 1 | 5 | 7 |
| `zone/Z16-events.md` | Z16 | 47 | 1 | 42 | 1 | 3 | 1 |
| `zone/Z17-item-actions.md` | Z17 | 38 | 2 | 31 | 0 | 5 | 4 |
| `zone/Z18-leftovers.md` | Z18 | 50 | 12 | 33 | 0 | 5 | 6 |
| `zone/Z19-config-script.md` | Z19 | 22 | 0 | 17 | 0 | 5 | 0 |
| `zone/Z20-skill-data.md` | Z20 | 26 | 0 | 20 | 0 | 6 | 1 |
| `zone/Z21-set-items.md` | Z21 | 32 | 0 | 27 | 0 | 5 | 3 |
| `zone/Z22-abstate-actors.md` | Z22 | 61 | 3 | 47 | 0 | 11 | 5 |
| `zone/Z23-skill-list.md` | Z23 | 43 | 6 | 29 | 0 | 8 | 4 |
| `zone/Z24-item-data.md` | Z24 | 37 | 0 | 32 | 0 | 5 | 0 |
| `zone/Z25-skill-specials.md` | Z25 | 37 | 3 | 28 | 0 | 6 | 6 |
| `zone/Z26-silver-wing.md` | Z26 | 24 | 1 | 19 | 0 | 4 | 13 |
| `zone/Z27-item-table.md` | Z27 | 36 | 0 | 31 | 0 | 5 | 1 |
| `zone/Z28-card-tables.md` | Z28 | 29 | 0 | 24 | 0 | 5 | 1 |
| `zone/Z29-exp-tables.md` | Z29 | 15 | 0 | 11 | 0 | 4 | 0 |
| `zone/Z30-leftovers.md` | Z30 | 17 | 3 | 11 | 0 | 3 | 1 |
| `zone/Z31-class-remainder.md` | Z31 | 95 | 5 | 77 | 1 | 12 | 3 |
| `zone/Z32-gamble-internals.md` | Z32 | 48 | 1 | 40 | 0 | 7 | 1 |
| `db/D01-account.md` | D01 | 18 | 0 | 8 | 9 | 1 | 0 |
| `db/D02-character.md` | D02 | 27 | 1 | 11 | 13 | 2 | 0 |
| `db/D03-character-items.md` | D03 | 50 | 2 | 30 | 14 | 4 | 0 |
| `db/D04-character-social.md` | D04 | 29 | 0 | 11 | 14 | 4 | 0 |
| `db/D05-gamelog.md` | D05 | 31 | 0 | 12 | 13 | 6 | 0 |
| `db/D06-db-inferred.md` | D06 | 59 | 0 | 47 | 2 | 10 | 0 |
| `db/D07-character-reward-items.md` | D07 | 18 | 0 | 15 | 0 | 3 | 0 |
| `db/D08-db-process.md` | D08 | 54 | 0 | 47 | 0 | 7 | 0 |
| `shared/S02-library.md` | S02 | 44 | 2 | 32 | 0 | 10 | 3 |
| **total** | | 2249 | 149 | 1565 | 209 | 326 | 120 |

Knowledge files (`docs/knowledge/`):

| File | Item | Sections | high | medium | low | not rated | hand |
|---|---|---|---|---|---|---|---|
| `L01.md` | L01 | 2 | 0 | 2 | 0 | 0 | 0 |
| `W01.md` | W01 | 3 | 0 | 1 | 1 | 1 | 0 |
| `W02.md` | W02 | 3 | 0 | 0 | 2 | 1 | 0 |
| `W03.md` | W03 | 2 | 0 | 1 | 1 | 0 | 0 |
| `W04.md` | W04 | 3 | 0 | 1 | 1 | 1 | 0 |
| `W05.md` | W05 | 3 | 0 | 2 | 0 | 1 | 0 |
| `W06.md` | W06 | 3 | 0 | 3 | 0 | 0 | 0 |
| `Z01.md` | Z01 | 9 | 1 | 5 | 2 | 1 | 3 |
| `Z02.md` | Z02 | 4 | 0 | 2 | 1 | 1 | 0 |
| `Z03.md` | Z03 | 3 | 0 | 1 | 0 | 2 | 1 |
| `Z04.md` | Z04 | 6 | 0 | 4 | 1 | 1 | 0 |
| `Z05.md` | Z05 | 4 | 0 | 2 | 1 | 1 | 0 |
| `Z06.md` | Z06 | 3 | 0 | 0 | 3 | 0 | 0 |
| `Z07.md` | Z07 | 5 | 0 | 1 | 2 | 2 | 0 |
| `Z08.md` | Z08 | 3 | 0 | 2 | 0 | 1 | 0 |
| `Z09.md` | Z09 | 4 | 1 | 3 | 0 | 0 | 0 |
| `Z10.md` | Z10 | 6 | 1 | 5 | 0 | 0 | 0 |
| `Z11.md` | Z11 | 4 | 0 | 4 | 0 | 0 | 0 |
| `Z12.md` | Z12 | 4 | 0 | 4 | 0 | 0 | 0 |
| `Z13.md` | Z13 | 9 | 0 | 9 | 0 | 0 | 0 |
| `Z14.md` | Z14 | 2 | 0 | 1 | 0 | 1 | 0 |
| `Z15.md` | Z15 | 5 | 1 | 3 | 0 | 1 | 0 |
| `Z16.md` | Z16 | 4 | 1 | 3 | 0 | 0 | 0 |
| `Z17.md` | Z17 | 6 | 0 | 5 | 0 | 1 | 0 |
| `Z18.md` | Z18 | 2 | 1 | 1 | 0 | 0 | 0 |
| `Z19.md` | Z19 | 1 | 0 | 1 | 0 | 0 | 0 |
| `Z20.md` | Z20 | 4 | 1 | 3 | 0 | 0 | 0 |
| `Z21.md` | Z21 | 5 | 0 | 5 | 0 | 0 | 0 |
| `Z22.md` | Z22 | 5 | 0 | 5 | 0 | 0 | 0 |
| `Z23.md` | Z23 | 5 | 0 | 5 | 0 | 0 | 0 |
| `Z24.md` | Z24 | 5 | 0 | 4 | 0 | 1 | 0 |
| `Z25.md` | Z25 | 3 | 0 | 3 | 0 | 0 | 0 |
| `Z26.md` | Z26 | 4 | 0 | 4 | 0 | 0 | 0 |
| `Z27.md` | Z27 | 2 | 0 | 2 | 0 | 0 | 0 |
| `Z28.md` | Z28 | 6 | 0 | 6 | 0 | 0 | 0 |
| `Z29.md` | Z29 | 5 | 0 | 5 | 0 | 0 | 0 |
| `Z30.md` | Z30 | 2 | 0 | 2 | 0 | 0 | 0 |
| `Z31.md` | Z31 | 4 | 0 | 4 | 0 | 0 | 0 |
| `Z32.md` | Z32 | 5 | 0 | 5 | 0 | 0 | 0 |
| `D01.md` | D01 | 3 | 0 | 1 | 2 | 0 | 0 |
| `D02.md` | D02 | 4 | 0 | 1 | 2 | 1 | 0 |
| `D03.md` | D03 | 4 | 0 | 3 | 0 | 1 | 0 |
| `D04.md` | D04 | 5 | 0 | 2 | 2 | 1 | 0 |
| `D05.md` | D05 | 4 | 0 | 1 | 3 | 0 | 0 |
| `D06.md` | D06 | 8 | 0 | 8 | 0 | 0 | 0 |
| `D07.md` | D07 | 2 | 0 | 2 | 0 | 0 | 0 |
| `D08.md` | D08 | 9 | 0 | 7 | 0 | 2 | 0 |
| `S01.md` | S01 | 27 | 0 | 18 | 3 | 6 | 0 |
| `S02.md` | S02 | 5 | 0 | 5 | 0 | 0 | 0 |
| `C01.md` | C01 | 16 | 4 | 11 | 0 | 1 | 4 |
| `C02.md` | C02 | 12 | 0 | 11 | 0 | 1 | 0 |
| `P01.md` | P01 | 6 | 0 | 6 | 0 | 0 | 0 |
| `P02.md` | P02 | 2 | 2 | 0 | 0 | 0 | 2 |
| `P03.md` | P03 | 5 | 0 | 5 | 0 | 0 | 0 |
| `P04.md` | P04 | 4 | 0 | 2 | 0 | 2 | 0 |
| `P05.md` | P05 | 5 | 0 | 3 | 0 | 2 | 0 |
| `X01.md` | X01 | 4 | 0 | 4 | 0 | 0 | 0 |
| `X02.md` | X02 | 6 | 0 | 3 | 1 | 2 | 0 |
| `X03.md` | X03 | 2 | 0 | 2 | 0 | 0 | 0 |
| `X04.md` | X04 | 6 | 0 | 4 | 0 | 2 | 0 |
| `X05.md` | X05 | 7 | 0 | 7 | 0 | 0 | 0 |
| `X06.md` | X06 | 6 | 0 | 4 | 0 | 2 | 0 |
| `X07.md` | X07 | 6 | 0 | 4 | 0 | 2 | 0 |
| `X09.md` | X09 | 7 | 0 | 5 | 0 | 2 | 0 |
| `K01.md` | K01 | 19 | 0 | 15 | 0 | 4 | 0 |
| **total** | | 342 | 13 | 253 | 28 | 48 | 10 |

### 2.4 L00: `login-server.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process structure | **low** | no function cited; sup×1 (README §5.2) | re-read the rest (§3) |
| · 1.1 Session object (`ClientSession`, fields seen) | medium | cap 1/1; weak p171 | capture (class U) |
| 2. Startup and main loop | medium | cap 4/4; sup×2 (README §5.2) | re-read the rest (§3) |
| 3. Receiving packets | – | container (see its subsections) |  |
| · 3.1 Framing and decryption (shared network library) | **low** | sup×1 (README §5.2) | re-read the rest (§3) |
| · 3.2 Client dispatcher and login state machine | **low** | sup×2 (README §5.2); B×1 | re-read the rest (§3); follow the return value to the parser |
| 4. Client handlers (CParserClient, registered @ FUN_00406e30) | medium | cap 23/27; cv ok; client×1; sup×5 (README §5.2); cv corr; B×2; weak inf2 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser; capture 0x0C66 |
| 5. Server-link handlers | – | container (see its subsections) |  |
| · 5.1 AccountDB replies (CParserAccountDB, registered @ FUN_00404… | medium | cap 16/27; cv ok; sup×3 (README §5.2); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 5.2 AccountLogDB replies (CParserAccountLogDB, registered @ FUN… | medium | cap 8/12; cv ok; sup×3 (README §5.2); cv corr; R×1 | re-read the rest (§3); read with P02 "Corrections"; callers incl. vtable slots; senders in every `handlers.json` |
| · 5.3 World manager links (CParserWorldManager, registered @ FUN_… | medium | cap 9/12; cv ok; client×1; sup×4 (README §5.2); B×1 | re-read the rest (§3); follow the return value to the parser |
| · 5.4 OPTool (operator tool, CParserOPTool, registered @ FUN_0040… | **low** | cap 2/15; sup×2 (README §5.2) | re-read the rest (§3) |
| 6. End-to-end: what happens when a player logs in | **high** | cap 22/23; cv ok |  |
| Original-server bugs | medium | cap 11/14; bug table (class X: effects are deductions) | capture 0x0C66 |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Client side (cross-referenced with `Files/Client/2016/Fiesta… | medium | cap 11/15; client×4; sup×1 (README §5.2); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x0C15, 0x0C66 |

### 2.5 L01: `login/L01-process.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process object and main thread | – | container (see its subsections) |  |
| · 1.1 `LoginServer` (`gServer`, one global object) | medium | no function cited | cite and re-read the function |
| · 1.2 Main thread and work steps | medium | cap 0/1; R×1 | capture (class U) |
| · 1.3 ProcessLink (step LINK) | medium | cap 1/1 | capture (class U) |
| · 1.4 ProcessConnect (accept) | **high** | cap 3/3 |  |
| · 1.5 ProcessPacket (packet pump) | medium | read in code | second reading / client check |
| · 1.6 ProcessDisconnect (heartbeats and closing) | medium | the 30 s / close rule is read in code and seen on the WM and the zone only; the 2016 client holds no Login connection on the login screen and polls 0x0C1B every 10 s on the world list, so the Login copy cannot fire with it (capture-validation §2.4, §16.2) (hand; baseline: medium) | test-client case T15 (capture-scenarios §3.41): a silent Login connection for 60 s |
| · 1.7 Destruction | medium | read in code | second reading / client check |
| · 1.8 Entry point and Windows-service shell | medium | read in code | second reading / client check |
| 2. Session pools | – | container (see its subsections) |  |
| · 2.1 `CLoginBaseSessionManager`: two lists over one node array | medium | read in code | second reading / client check |
| · 2.2 Session objects | **high** | cap 2/2 |  |
| · 2.3 Client pool (`CLoginClientSessionManager`) | **high** | cap 7/7; client×2 |  |
| · 2.4 OPTool pool (`CLoginOPToolSessionManager`) | medium | read in code | second reading / client check |
| · 2.5 WM pool and world table (`CLoginWorldManagerSessionManager`) | **high** | cap 11/11 |  |
| · 2.6 Session lifecycle: accept → pool → free | **high** | cap 9/9 |  |
| 3. World status and the load table (`m_LoginUserRatable`) | **high** | cap 5/8; client×1 |  |
| 4. Parsers and the per-parser handler copies | – | container (see its subsections) |  |
| · 4.1 Handler tables and the shared server-link parser | medium | read in code | second reading / client check |
| · 4.2 0x0801 / 0x0803 / 0x0804 / 0x0805 per parser | **high** | cap 5/5 |  |
| · 4.3 One-time-token list object (`COTPLogin`, `COTPData`) | **high** | cap 2/2; weak inf1; R×1 |  |
| · 4.4 Connection check, small handler bodies, template destructors | medium | the captured opcodes are only mentioned here (the S2S handshake and heartbeat of §4.2, 0x0C18); the subject of the section (the OPTool handlers 0x2818 / 0x2819 and the other small bodies) is in no capture (hand; baseline: high) | second reading |
| · 4.5 Value types and message helpers used by the L00 handlers | medium | cap 2/5 | capture (class U) |
| · 4.6 Library copies in Login (pointer table) | medium | read in code | second reading / client check |
| Original-server bugs | **low** | cap 5/8; sup×1 (README §5.2); bug table (class X: effects are deductions) | re-read the rest (§3) |
| 5. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 6. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.6 W01: `wm/W01-core.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process structure | **low** | sup×2 (README §5.3) | re-read the rest (§3) |
| · 1.1 Client session (size 0x1f7b8; fields used by the core) | **high** | cap 13/13; ours×1 |  |
| 2. Startup, links and timers | medium | cap 8/9; cv ok; client×1; sup×4 (README §5.3); N: `BootstrapTick`, `SessionCleanupTick`; weak inf1 | re-read the rest (§3); README §4.8 |
| · 2.1 Server-to-server handshake (all outgoing links) | **high** | cap 4/4; cv ok |  |
| 3. World login (client → WM) | – | container (see its subsections) |  |
| · 3.1 Pending world logins (Login → WM) | medium | cap 3/3; sup×2 (README §5.3) | re-read the rest (§3) |
| · 3.2 Client connects to the WM | medium | cap 8/9; cv ok; sup×2 (README §5.3); cv corr; N: `AcceptTick` | re-read the rest (§3); read with P02 "Corrections"; README §4.8; capture 0x0C15 |
| · 3.3 Newbie / comeback classification, then the avatar list | medium | cap 6/10; cv ok; client×1; sup×1 (README §5.3); cv corr; weak inf1 p171 | re-read the rest (§3); read with P02 "Corrections"; capture 0x0C15 |
| 4. Character select (client → WM) | – | container (see its subsections) |  |
| · 4.1 Create / delete / rename | medium | cap 24/26; cv ok; sup×2 (README §5.3); cv corr; weak inf4 | re-read the rest (§3); read with P02 "Corrections"; code or capture for the marked statements; capture 0x140A |
| · 4.2 Character login (enter the game) | medium | cap 16/17; cv ok; client×1; sup×4 (README §5.3); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; capture 0x111D |
| · 4.3 Beauty shop at character select (CHairShopFrameWork) | medium | cap 0/8 | capture 0x1079, 0x107D |
| 5. In-game client requests (core) | – | container (see its subsections) |  |
| · 5.1 Logout and return to character select | medium | cap 7/7; cv ok; client×1; sup×3 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 5.2 Kicks | **high** | cap 3/3; cv ok |  |
| · 5.3 Small client requests | medium | cap 4/20 | capture 0x0813, 0x0819, 0x086F, 0x3041 |
| · 5.4 CharacterLogout (shared by logout, disconnect, return to se… | medium | cap 6/7; cv ok; sup×2 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 6. Character DB link (CParserCharDB) | medium | read in code | second reading / client check |
| · 6.1 AVATAR (0x82 bytes; char-select list entry) | medium | cap 5/5; sup×2 (README §5.3); cv corr; weak inf6 p172; ours×1 | re-read the rest (§3); read with P02 "Corrections"; code or capture for the marked statements |
| · 6.2 Avatar and character replies | medium | cap 6/17; cv ok; sup×4 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x086F, 0x1079, 0x107D |
| · 6.3 Character blob cache (CharDB → WM → zone) | medium | cap 73/96; sup×2 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x1010, 0x1011, 0x102A |
| 7. Zone links (CParserZone) | – | container (see its subsections) |  |
| · 7.1 Zone registration and map table | medium | cap 4/5; sup×2 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 7.2 Character data for a zone (map login and map change) | medium | cap 12/13; cv ok; sup×1 (README §5.3); cv corr; weak p172 | re-read the rest (§3); read with P02 "Corrections" |
| · 7.3 Map login done, map change, logout notices | medium | cap 24/27; cv ok; sup×4 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x5425, 0xB016 |
| · 7.4 Character state saves (dept 16 and others; zone → WM cache) | medium | cap 4/7; sup×3 (README §5.3, §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 7.5 Level change | medium | cap 2/4; sup×1 (README §5.4); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| · 7.6 Other zone messages in scope | medium | cap 2/19; cv ok; client×1; weak inf1 | capture 0x7C02 |
| 8. AccountDB / AccountLogDB / GameLogDB links (rest) | medium | cap 3/12; cv ok; client×1 | capture 0x8002, 0x8004, 0x8006 |
| 9. OPTool (CParserOPTool) | medium | cap 6/55 | capture 0x0813, 0x7419, 0x7477, 0x9418 |
| 10. Client cross-check (summary) | **high** | cap 16/21 |  |
| Original-server bugs | **low** | cap 10/11; sup×3 (README §5.3); weak inf1; bug table (class X: effects are deductions) | re-read the rest (§3) |
| 11. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.7 W02: `wm/W02-party-raid.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data structures | – | container (see its subsections) |  |
| · 1.1 Client session fields used here (see W01-core §1.1 for the … | **low** | cap 2/5; sup×1 (README §5.3); weak p171; ours×1 | re-read the rest (§3); capture 0xB020 |
| · 1.2 Party registry `g_Parties` (DAT_0055e128 = g_WM + 0xc4100) | **low** | sup×1 (README §5.3); N: `Party_GetRole` | re-read the rest (§3); README §4.8 |
| · 1.3 Party send helpers | medium | cap 0/15 | capture 0x3809, 0x380B, 0x3815, 0x3829 … |
| · 1.4 Raid registry `g_Raids` (DAT_006bdf60 = g_WM + 0x223f38), c… | medium | cap 0/9; weak inf1 | capture 0xB005, 0xB006, 0xB02E, 0xB038 … |
| · 1.5 Party finder `g_PartyFinder` (DAT_0055e134 = g_WM + 0xc410c) | medium | cap 0/1; weak p171 | capture 0x3856 |
| · 1.6 Map flags from the zones' map registration | **low** | cap 1/2; sup×2 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 2. Party: client handlers (CParserClient, dept 14) | – | container (see its subsections) |  |
| · 2.1 0x3802 NC_PARTY_JOIN_REQ { char target[20] }  (invite) | medium | cap 0/3 | capture 0x3803, 0x3807 |
| · 2.2 0x3804 NC_PARTY_JOINPROPOSE_ALLOW_ACK (no payload; accept) | medium | cap 0/6 | capture 0x3807, 0x3809 |
| · 2.3 0x3805 NC_PARTY_JOINPROPOSE_REJECT_ACK (no payload) | **low** | cap 0/3; sup×1 (README §5.3); N: `Party_GetRole`; weak inf1 | re-read the rest (§3); README §4.8; capture 0x3807 |
| · 2.4 0x380A NC_PARTY_LEAVE_REQ (no payload) and the shared leave… | **low** | cap 0/6; sup×1 (README §5.3); N: `Party_GetRole` | re-read the rest (§3); README §4.8; capture 0x380B, 0x381E |
| · 2.5 0x3814 NC_PARTY_KICKOFF_REQ { char member[20] } | medium | cap 0/4; client×1 | capture 0x3815, 0x381E |
| · 2.6 0x3828 NC_PARTY_CHANGEMASTER_REQ { char newmaster[20] } | medium | cap 0/3; client×1 | capture 0x3829 |
| · 2.7 0x384B NC_PARTY_ITEM_LOOTING_SET { u8 lootingtype, u8 nItem… | medium | cap 0/3; client×1 | capture 0x384C |
| · 2.8 0x385A NC_PARTY_SET_LOOTER_REQ { char sNewLooterCharID[20] } | medium | cap 0/5 | capture 0x385B, 0x385C, 0x385D |
| · 2.9 Party finder: 0x3850 / 0x3852 / 0x3854 | medium | cap 0/6 | capture 0x3851, 0x3853, 0x3855 |
| 3. Party: zone and OPTool handlers | – | container (see its subsections) |  |
| · 3.1 0x384E NC_PARTY_MEMBERINFORM_REQ { u16 partyregnum }  (CPar… | medium | cap 0/2 | capture (class U) |
| · 3.2 0x3860 NC_PARTY_ZONE_JOIN_CMD { u32 nMasterCharNo, u32 nJoi… | medium | cap 0/4 | capture 0x3807 |
| · 3.3 0x3861 NC_PARTY_ZONE_LEAVE_CMD { u32 nCharNo } | medium | cap 0/1 | capture (class U) |
| 4. Party lifecycle hooks (called from W01 paths) | – | container (see its subsections) |  |
| · 4.1 Map login (0x180C, W01 §7) | **low** | cap 1/5; sup×1 (README §5.3) | re-read the rest (§3); capture 0x383D, 0xB015 |
| · 4.2 Character logout (W01 §5.4 CharacterLogout, FUN_00436d50) | **low** | cap 0/4; sup×1 (README §5.3); N: `Party_GetRole` | re-read the rest (§3); README §4.8; capture 0x381E, 0x3847 |
| · 4.3 Other hooks | **high** | cap 2/2 |  |
| 5. Raid: client handlers (CParserClient, dept 44) | – | container (see its subsections) |  |
| · 5.1 0xB001 NC_RAID_MAKE_REQ (no payload)  (turn my party into a… | medium | cap 0/4 | capture 0xB002, 0xB003 |
| · 5.2 0xB008 NC_RAID_LOOTING_TYPE_REQ { u8 nItemGrade, u8 nLootin… | medium | cap 0/4 | capture 0xB009, 0xB00A |
| · 5.3 0xB00C NC_RAID_INVITATION_REQ { char sInvitationCharID[20] } | medium | cap 0/3; client×1 | capture 0xB00D, 0xB00E |
| · 5.4 0xB00F NC_RAID_INVITATION_ANSWER_REQ { u8 bIsAllow, char sM… | medium | cap 0/5 | capture 0xB010, 0xB011, 0xB012 |
| · 5.5 0xB014 NC_RAID_LEAVE_REQ (no payload) | medium | cap 0/4 | capture 0xB015, 0xB016 |
| · 5.6 0xB018 NC_RAID_VANISH_REQ { char sVanishCharID[20] }  (lead… | medium | cap 0/5 | capture 0xB019, 0xB01A, 0xB01B |
| · 5.7 0xB027 NC_RAID_SLOT_MOVE_REQ { PrePosition{u16 nPartyNo, u8… | medium | cap 0/4 | capture 0xB028, 0xB029 |
| · 5.8 0xB02B NC_RAID_SET_LEADER_REQ { char sNewLeaderCharID[20] } | medium | cap 0/5 | capture 0xB02C, 0xB02D, 0xB02E |
| · 5.9 0xB030 NC_RAID_SET_SUB_LEADER_REQ { char sNewSubLeaderCharI… | medium | cap 0/5 | capture 0xB031, 0xB032, 0xB033 |
| · 5.10 0xB035 NC_RAID_DEL_SUB_LEADER_REQ { char sDelSubLeaderChar… | medium | cap 0/5 | capture 0xB036, 0xB037, 0xB038 |
| · 5.11 0xB03A NC_RAID_SET_LOOTER_REQ { char sNewLooterCharID[20] } | medium | cap 0/5 | capture 0xB03B, 0xB03C, 0xB03D |
| · 5.12 0xB03F NC_RAID_CHAT_REQ / 0xB042 NC_RAID_WARNING_REQ { u8 … | medium | cap 0/6 | capture 0xB040, 0xB041, 0xB043, 0xB044 |
| 6. Raid lifecycle hooks | – | container (see its subsections) |  |
| · 6.1 Map login | medium | cap 0/2 | capture 0xB01E |
| · 6.2 Logout | medium | cap 0/2 | capture 0xB020 |
| 7. Result codes and client texts | **low** | cap 0/20; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x3807, 0x380B, 0x3815, 0x3829 … |
| 8. Messages to the zones (summary) | medium | cap 0/27 | capture (class U) |
| 9. Original-server bugs (decide for a rebuild) | medium | cap 0/16; client×1; weak inf1; bug table (class X: effects are deductions) | capture 0x3807, 0x381E, 0x3829, 0x385B … |
| 10. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.8 W03: `wm/W03-guild.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data structures | – | container (see its subsections) |  |
| · 1.1 Guild manager `g_GuildManager` (DAT_006c4cc0) | medium | captured only as the start-up load of a world without a guild (0x7457 `NumOfGuild 0`, 0x74BD; capture-validation §17.3): no guild object was ever built (hand; baseline: high) | capture-scenarios 22 / 23 (guild with members) |
| · 1.2 Guild entry (`CGuildServer` + members + academy, 0x1BAA8 by… | **low** | cap 1/2; sup×4 (README §5.3); weak p174 | re-read the rest (§3); code or capture for the marked statements |
| · 1.3 Member table `M` (entry+0x7A0) | medium | cap 0/2; weak p172 | capture (class U) |
| · 1.4 Academy member table `A` (entry+0x17BA4) | medium | weak p172 | second reading / client check |
| · 1.5 Client-session fields used here | medium | cap 2/9; ours×1 | capture (class U) |
| · 1.6 Helper index (small callees, named here so other items can … | medium | cap 2/44 | capture 0x7432, 0x7480, 0x74FE, 0x9825 … |
| 2. Guild: client handlers (CParserClient, dept 29) and their Ch… | medium | cap 0/10 | capture (class U) |
| · 2.1 0x7403 NC_GUILD_LIST_REQ (no payload) | medium | cap 0/3 | capture 0x7404 |
| · 2.2 0x7405 NC_GUILD_MAKE_REQ { Name4 Name; Name3 Password; u8 T… | medium | cap 0/8; client×1 | capture 0x7406, 0x7436 |
| · 2.3 0x7407 NC_GUILD_DISMISS_REQ { Name4 Name; Name3 Password } … | medium | cap 0/8; client×1 | capture 0x7408, 0x742F |
| · 2.4 0x7409 NC_GUILD_MEMBER_INVITE_REQ { Name5 ToCharID }  (0x14) | medium | cap 0/5 | capture 0x740A, 0x740B, 0x982F |
| · 2.5 0x740C NC_GUILD_MEMBER_JOIN_ACK { Name4 GuildName; u8 JoinA… | **low** | cap 0/11; client×1; sup×1 (README §5.3); R×1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json`; capture 0x740D, 0x7436, 0x750A, 0x982F |
| · 2.6 0x740E NC_GUILD_MEMBER_VANISH_REQ { Name5 CharID }  (kick, … | medium | cap 0/10; client×1 | capture 0x740F, 0x7437 |
| · 2.7 0x741C NC_GUILD_MEMBER_LEAVE_REQ (no payload) | medium | cap 0/8; client×1 | capture 0x741D, 0x7438 |
| · 2.8 0x7410 NC_GUILD_NOTIFY_REQ { u16 nNotifyLength; char sNotif… | **low** | cap 1/7; client×1; sup×1 (README §5.3) | re-read the rest (§3); capture 0x7411, 0x742D |
| · 2.9 0x7416 NC_GUILD_MEMBER_GRADE_REQ { Name5 CharID; u8 MemberG… | medium | cap 0/7 | capture 0x7417, 0x7439 |
| · 2.10 0x7418 NC_GUILD_MY_GUILD_INFO_REQ (no payload) | medium | cap 0/3 | capture 0x7419 |
| · 2.11 0x741A NC_GUILD_MEMBER_LIST_REQ (no payload) and the membe… | medium | cap 0/5 | capture 0x741B |
| · · 2.11.1 Members_OnLoaded (FUN_0044c5f0) | medium | read in code | second reading / client check |
| 3. Guild: war, lists, chat, name lookup, tokens, history, emblem | – | container (see its subsections) |  |
| · 3.1 War state (in the requesting guild's entry only) | medium | cap 0/3 | capture (class U) |
| · 3.2 0x7422 NC_GUILD_WAR_REQ { Name4 TargetName }  (0x10) | medium | cap 0/8 | capture 0x7423, 0x7432 |
| · 3.3 War timer `Guilds_WarTick` (FUN_0044ce00, from the guild ma… | medium | cap 0/8; client×1 | capture 0x7433, 0x7434, 0x7435, 0x987D … |
| · 3.4 War scoring: zone 0x7445 NC_GUILD_ZONE_WAR_KILL_CMD { u16 h… | medium | cap 0/1 | capture (class U) |
| · 3.5 War lists and zone war queries | **low** | cap 4/11; client×1; sup×1 (README §5.3); B×1 | re-read the rest (§3); follow the return value to the parser; capture 0x7425, 0x7427 |
| · 3.6 0x7473 NC_GUILD_CHAT_REQ { u8 itemLinkDataCount; u8 len; co… | medium | cap 0/3; client×1 | capture 0x7474, 0x7475 |
| · 3.7 0x7476 NC_GUILD_NAME_REQ { u32 nNo } | medium | cap 0/3; client×1 | capture 0x7477 |
| · 3.8 Guild tokens | medium | cap 1/7; client×1 | capture 0x74BF, 0x74C2 |
| · 3.9 0x74C3 NC_GUILD_MY_GUILD_TOURNAMENT_MATCH_TIME_REQ (no payl… | medium | cap 0/2; client×1 | capture 0x74C4 |
| · 3.10 Guild history 0x74FD NC_GUILD_HISTORY_LIST_REQ (no payload) | medium | cap 0/4; client×1; weak p171 | capture 0x74FE |
| · 3.11 Guild emblem | medium | cap 2/16; client×1 | capture 0x7502, 0x7506, 0x7509, 0x750A … |
| 4. Guild and academy hooks in the character life cycle (W01 han… | – | container (see its subsections) |  |
| · 4.1 Character login data from the Character DB | medium | cap 2/2; B×1 | follow the return value to the parser |
| · 4.2 Map login: `Client_RefreshGuildState` (FUN_004360f0) | medium | cap 3/12 | capture 0x741B, 0x7427, 0x743D, 0x7441 … |
| · 4.3 Members_OnLoaded (FUN_0044c5f0), the end of a member-table … | medium | cap 0/1; weak p171 | capture 0x743E |
| · 4.4 Logout (`CharacterLogout` FUN_00436d50, W01 §5.4) → `Guild_… | medium | cap 0/2 | capture 0x743E, 0x9862 |
| · 4.5 Character delete: guild check (0x1407 → 0x1413 → 0x1414 / 0… | medium | cap 4/10; cv ok; sup×1 (README §5.3); B×2 | re-read the rest (§3); follow the return value to the parser; capture 0x140A |
| · 4.6 Rename / delete of a character: `CWMClientSession::CharIDCh… | medium | cap 0/1 | capture 0xB40E |
| · 4.7 Level change: zone 0x1074 NC_CHAR_LEVEL_CHANGED_CMD (FUN_00… | medium | cap 1/7 | capture 0x7440, 0x9866 |
| 5. Guild academy: client handlers (CParserClient, dept 38) | **low** | cap 0/73; sup×1 (README §5.3); R×1; weak inf1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json`; capture 0x7474, 0x9808, 0x980C, 0x980E … |
| 6. Guild academy: Character DB answers, zone messages and timers | – | container (see its subsections) |  |
| · 6.1 Start-up (states 0x11–0x18 of §9.1) | medium | cap 2/7 | capture 0x980E |
| · 6.2 Membership answers | medium | cap 0/23 | capture 0x7436, 0x9812, 0x9813, 0x9817 … |
| · 6.3 Notice, chat ban, rewards, ranking (DB answers relayed to t… | **low** | cap 0/28; sup×1 (README §5.3) | re-read the rest (§3); capture 0x9822, 0x9823, 0x9825, 0x9826 … |
| · 6.4 Academy points, level-up and the weekly balance | **low** | cap 2/6; sup×1 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 7. Guild manager tick (`GuildManager_Tick` FUN_0044fd60, called… | medium | cap 0/4 | capture 0x750A |
| 8. Guild tournament (WM side) | – | container (see its subsections) |  |
| · 8.1 Data | **low** | cap 1/3; sup×2 (README §5.3); weak p171 | re-read the rest (§3) |
| · 8.2 Client requests | **low** | cap 0/11; client×1; sup×1 (README §5.3) | re-read the rest (§3); capture 0x747B, 0x747F, 0x74EA |
| · 8.3 Zone requests | medium | cap 0/7 | capture (class U) |
| · 8.4 Schedule and phases | **low** | cap 2/18; sup×1 (README §5.3); B×1 | re-read the rest (§3); follow the return value to the parser; capture 0x747B, 0x7480, 0x74ED, 0x74F8 |
| · 8.5 Match end and rewards: `Tournament_OnEnd` (FUN_00446340, lo… | medium | cap 1/11; weak p171 | capture 0x7490, 0x74E2, 0x74ED, 0x74F0 … |
| 9. Guild: start-up load, deletion, rename / retype, storage rig… | – | container (see its subsections) |  |
| · 9.1 Start-up sequence (CharDB link state machine, `FUN_00405aa0… | **high** | cap 14/21; cv ok |  |
| · 9.2 Deletion (dismissal executed by the DB) and dismissal cancel | **low** | cap 0/14; B×3 | follow the return value to the parser; capture 0x742F, 0x7430, 0x985F |
| · 9.3 Rename (item, zone-driven) | medium | cap 0/7 | capture 0x74AD, 0x74AE |
| · 9.4 Retype (guild type / combat propensity, item, zone-driven) | medium | cap 0/6 | capture 0x74B6 |
| · 9.5 Storage withdraw rights (zone asks for the member grade) | medium | cap 0/6 | capture (class U) |
| 10. Messages to the zones and the client-bound broadcasts (summ… | medium | cap 4/29 | capture 0x74AE, 0x74ED, 0x750B |
| 11. Original-server bugs | **low** | cap 2/51; client×2; R×1; bug table (class X: effects are deductions) | callers incl. vtable slots; senders in every `handlers.json`; capture 0x7406, 0x742F, 0x7434, 0x7435 … |
| 12. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 13. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.9 W04: `wm/W04-social-misc.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Shared data and helpers | – | container (see its subsections) |  |
| · 1.1 Client-session fields used by this item (see W01-core §1.1 … | medium | cap 2/7; weak p171 | capture (class U) |
| · 1.2 Helpers (named here) | medium | cap 0/1; ours×1 | capture 0x2004 |
| 2. Chat routing (dept 8 ACT) | – | container (see its subsections) |  |
| · 2.1 Whisper: client 0x200C NC_ACT_WHISPER_REQ (CParserClient) | **high** | cap 5/5; cv ok; client×2 |  |
| · 2.2 Notice: 0x2010 NC_ACT_NOTICE_REQ (three parsers) | **high** | cap 1/2; client×1 |  |
| · 2.3 Party chat: client 0x2014 NC_ACT_PARTYCHAT_REQ | medium | cap 1/4; client×1 | capture 0x2015, 0x2016 |
| · 2.4 Zone 0x207D NC_ACT_SCRIPT_MSG_WORLD_CMD (CParserZone) | **high** | cap 2/2; cv ok; client×1 |  |
| · 2.5 Gold-spammer alert to GMs (0x200D, reached from W01's 0x085… | medium | the captured opcodes are only mentioned here (0x200D of a normal whisper, §2.1); the subject of the section (the gold-spammer alert from 0x085F) is in no capture (hand; baseline: high) | capture 0x085F (report a spammer with a GM online) |
| 3. Zone notifications (dept 9 BAT, 18 SKILL) | – | container (see its subsections) |  |
| · 3.1 0x244A NC_BAT_PKINPKFIELD_WMS_CMD | **high** | cap 2/3 |  |
| · 3.2 0x2458 NC_BAT_WORLD_MOB_KILL_ANNOUNCE_CMD | medium | cap 0/2; client×1; weak p171 | capture 0x2459 |
| · 3.3 0x4820 NC_SKILL_PASSIVESKILL_LEARN_CMD | medium | the captured opcode is only the passive list 0x1025, empty (`n 0`, capture-validation §7.5); the subject of the section (0x4820 passive skill learned) is in no capture (hand; baseline: high) | capture: learn a passive skill |
| 4. Operator tool (dept 10 OPTOOL and the other CParserOPTool ha… | medium | cap 0/1 | capture (class U) |
| · 4.1 Server status | **low** | cap 1/15; B×1 | follow the return value to the parser |
| · 4.2 Kingdom-quest schedule (OPTool side) | medium | cap 0/7 | capture (class U) |
| · 4.3 Users and characters | medium | cap 3/14; cv ok; weak inf1 | capture 0x540C, 0x7438, 0x9860 |
| · 4.4 Guild and guild tournament (OPTool side; W03 owns the guild… | medium | cap 6/22 | capture 0x7419, 0x7439, 0x7477 |
| 5. Friends (dept 21 FRIEND) | – | container (see its subsections) |  |
| · 5.1 Friend list in the client session | **high** | cap 1/2; cv ok |  |
| · 5.2 Loading and presence (not handlers; reached from W01's logi… | medium | cap 2/12 | capture 0x1010, 0x5407, 0x5408, 0x5409 … |
| · 5.3 Friend request (CParserClient 0x5401 → 0x5403 → client 0x54… | medium | cap 0/9; client×1 | capture 0x5402, 0x5403, 0x5408, 0x540B |
| · 5.4 Delete | medium | cap 1/7 | capture 0x5406, 0x540C |
| · 5.5 Offline friend details | medium | cap 0/2 | capture 0x5408 |
| · 5.6 Friend points, find friends, special item | medium | cap 1/9; client×1 | capture 0x541E, 0x5420, 0x5424, 0x5425 |
| 6. Kingdom quest (dept 22 KQ) | – | container (see its subsections) |  |
| · 6.1 The `CKQ` object (`g_InstanceMaps`, DAT_0055e15c) and the p… | medium | cap 5/9; N: `KQ_CanReturnToMap` | README §4.8; capture 0x5804, 0x5830 |
| · 6.2 Tick (once per second) | **high** | cap 6/9; cv ok; client×2; weak p171 |  |
| · 6.3 Zone answers (CParserZone) | **high** | cap 2/3 |  |
| · 6.4 Client requests: list, status, join (CParserClient) | **low** | cap 6/20; client×1; B×2 | follow the return value to the parser; capture 0x5804, 0x5806, 0x5808, 0x580A … |
| · 6.5 Vote ban, team choice, joiner list | **low** | cap 1/18; client×3; N: `KQ_CanReturnToMap` | README §4.8; capture 0x5828, 0x5829, 0x582B, 0x582C … |
| 7. Character title relay (dept 24 CT) | medium | cap 1/4 | capture (class U) |
| 8. Character options (dept 28 CHAR_OPTION) | – | container (see its subsections) |  |
| · 8.1 Session cache and the login push | **high** | cap 10/17 |  |
| · 8.2 Client requests | **low** | cap 14/41; sup×2 (README §5.3); cv corr; B×3 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser |
| · 8.3 CharDB answers | **low** | cap 7/26; client×2; B×1; R×1 | follow the return value to the parser; callers incl. vtable slots; senders in every `handlers.json`; capture 0x7003, 0x7007, 0x7009, 0x700B … |
| 9. Prison (dept 31) | **low** | no function cited; sup×1 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 9.1 `CPrisonServer` (the WM's release timer) | medium | cap 1/4; weak inf1 | capture 0x7C05 |
| · 9.2 Client requests (CParserClient) | medium | cap 2/16; client×3; weak inf1 | capture 0x7C02, 0x7C03, 0x7C05, 0x7C0A |
| · 9.3 Zone and CharDB answers | medium | cap 2/18; client×2; weak p171 | capture 0x5808, 0x7C02, 0x7C03, 0x7C05 … |
| 10. Player reports (dept 32 REPORT) | **low** | cap 0/12; client×1; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x8002, 0x8004, 0x8006 |
| 11. Charged (premium) buffs (dept 36, CParserZone) | medium | captured only as empty lists: CharDB 0x101B `{handle, 0}` and WM→Z 0x1032 `n 0` at every login (capture-validation §7.4, §7.5); no charged buff in a capture, 0x9001 / 0x9002 not captured (hand; baseline: high) | capture with an active charged buff (premium item), then a map login |
| 12. Holy promise (master / apprentice, dept 37) | medium | cap 0/2 | capture (class U) |
| · 12.1 The relation object in the session (`HP` = session +0x1DFB… | **high** | cap 2/2 |  |
| · 12.2 Loading, presence, level change (not handlers) | medium | cap 6/13; client×3 | capture 0x9416, 0x9417, 0x9419, 0x9445 |
| · 12.3 Client requests and their CharDB answers | **low** | cap 0/23; client×7; sup×1 (README §5.3); B×1 | re-read the rest (§3); follow the return value to the parser; capture 0x9402, 0x9403, 0x9404, 0x9407 … |
| · 12.4 Character deletion and the zone query | **low** | cap 1/6; cv ok; sup×1 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x9418 |
| 13. Instance dungeons (dept 41) | – | container (see its subsections) |  |
| · 13.1 Empty-dungeon countdown and reset (CParserZone) | medium | cap 0/4; client×1 | capture 0x0810 |
| · 13.2 Level-select relay (ModeIDGate, Z08 §5.3) | medium | cap 0/8 | capture (class U) |
| · 13.3 Instance ranking (`g_IndunRank`, DAT_006c5568, all names *… | medium | cap 2/16; client×6 | capture 0xA421, 0xA422, 0xA423, 0xA424 … |
| 14. Chat block list (dept 42 CHAT_RESTRICT) | **high** | client×1 |  |
| · 14.1 The list in the session (`CR` = session +0x1E290, all name… | **high** | cap 2/4; client×1 |  |
| · 14.2 Client requests and the CharDB answers | medium | cap 9/27; client×2 | capture 0x1C07, 0x1C10, 0x1C11, 0x1C12 … |
| 15. Gamble house: daily coin reset and the return map (dept 47) | – | container (see its subsections) |  |
| · 15.1 `CGambleSystemServer` (daily reset of the exchanged-coin c… | medium | cap 1/2 | capture (class U) |
| · 15.2 Return map (CParserZone) | medium | cap 2/2; B×1 | follow the return value to the parser |
| 16. GM events (dept 52 EVENT, CParserOPTool) | – | container (see its subsections) |  |
| · 16.1 `GMEventManager` (`g_GMEventManager` DAT_006c5488 = WM +0x… | medium | cap 0/1; weak p171 | capture (class U) |
| · 16.2 Handlers | medium | cap 0/12 | capture (class U) |
| 17. Dept-2 MISC relays, attendance event, NPC schedule (W01 han… | – | container (see its subsections) |  |
| · 17.1 Account-server event relay 0x083A (C01 open item) | medium | cap 1/5; weak p171 | capture (class U) |
| · 17.2 Chat spam filter settings (0x0844 / 0x0845 / 0x0846) | medium | only the set path is captured (0x0846 -> CDB 0x0847, no reply; capture-validation §27.4); the load 0x0844 and the push 0x0845 appeared in no capture (no usp_SpamFilter_get row for any captured character, §7.4), so W04-B60 (the session copy not updated) could not show (hand; baseline: high) | set the filter, then a new character login and map login of the same account (0x0844 -> 0x0845 with the set values or the old ones: W04-B60) |
| · 17.3 Client loading-failure report (0x0840 → CharDB 0x0841) | medium | cap 0/2 | capture (class U) |
| · 17.4 Gold-spammer report and GM chat ban (0x085F … 0x0869) | medium | cap 2/13 | capture 0x0860, 0x0862, 0x0867 |
| · 17.5 Attendance event (`cEvent_Attendance`, `g_Attendance` DAT_… | medium | cap 4/14; cv ok; ours×2 | capture 0x10ED, 0x10F0, 0x10F2, 0x10F5 … |
| · 17.6 NPC schedule (`CNpcScheduleServer`, DAT_006c536c = WM +0x2… | medium | cap 0/4 | capture 0x086C, 0x086D |
| 18. Original-server bugs | medium | cap 17/106; weak inf1; bug table (class X: effects are deductions) | capture 0x0845, 0x10ED, 0x10F0, 0x10F2 … |
| 19. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 20. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.10 W05: `wm/W05-process.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process lifecycle | – | container (see its subsections) |  |
| · 1.1 Start-up (WinMain → Windows service) | medium | R×1 | second reading / client check |
| · 1.2 Main thread and the work steps | **high** | cv ok |  |
| · 1.3 ProcessLink (start-up links) | medium | cap 1/2; cv ok; sup×1 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 1.4 ProcessConnect and ProcessPacket (accept and packet pump) | medium | cap 2/2; sup×1 (README §5.3) | re-read the rest (§3) |
| · 1.5 ProcessDisconnect (heartbeats and closing links) | **high** | cap 2/2 |  |
| · 1.6 Shutdown | **high** | cap 5/5 |  |
| 2. Timed services (`ProcessContents`) | – | container (see its subsections) |  |
| · 2.1 Order and period | medium | cap 1/1 | capture (class U) |
| · 2.2 Server time for the clients (0x0849) | medium | cap 4/4; cv ok; client×1; sup×1 (README §5.3); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| · 2.3 Quest reset times (`CDailyQuestTimer`, 0x441C / 0x441D) | **high** | cap 3/4 |  |
| 3. Data loader (`ReadGlobalGameData`) and the SHN reader | medium | read in code | second reading / client check |
| · 3.1 `CDataReader`: the SHN reader all tables use | medium | read in code | second reading / client check |
| · 3.2 `ReadGlobalGameData`: order, destination, checks | **low** | sup×1 (README §5.3); weak inf1 | re-read the rest (§3) |
| · 3.3 Table accessors | medium | cap 0/1 | capture (class U) |
| · 3.4 Client-SHN checksum list (`CShnDataFileCheckSum`) | medium | cap 1/1 | capture (class U) |
| 4. Session pools and the client session lifecycle | – | container (see its subsections) |  |
| · 4.1 Pool structure (`CWMBaseSessionManager`) | medium | weak inf1 | second reading / client check |
| · 4.2 Handles | medium | cap 1/1; weak inf1 | capture (class U) |
| · 4.3 Client session: construct, take, reset | **high** | cap 10/10 |  |
| · 4.4 Pending-login groups per IP | medium | cap 1/1 | capture (class U) |
| · 4.5 Release: which event closes a client session | **high** | cap 10/11 |  |
| · 4.6 Destroy (process stop and exit) | medium | read in code | second reading / client check |
| · 4.7 Newbie-guide list on the first map login (0x10D9) | **high** | cap 4/4; client×1; weak p171 |  |
| 5. W01 core gaps | – | container (see its subsections) |  |
| · 5.1 Handler return value and `fc_dummyfunction` (corrects W01 §… | medium | read in code | second reading / client check |
| · 5.2 Zone registration 0x0802 (completes W01 §7.1) | medium | cap 3/4; cv ok; sup×1 (README §5.3) | re-read the rest (§3) |
| · 5.3 World-login entry (0x0C0D / 0x0C0F helpers; corrects W01 §3… | **high** | cap 8/8 |  |
| · 5.4 Character blob cache: CharDB pushes (W01 §6.3 per handler) | **high** | cap 30/45 |  |
| · 5.5 Zone state saves (W01 §7.4 per handler) | **high** | cap 17/21 |  |
| · 5.6 Ping-test relay (OPTool ↔ WM ↔ client / CharDB / zone) | medium | cap 0/8; client×2 | capture 0x0813 |
| · 5.7 Small helpers and the log systems | **high** | cap 7/9 |  |
| · 5.8 Triage of the W01 handlers `coverage.py` lists as undocumen… | medium | cap 25/63; client×1 | capture 0x0813, 0x1010 |
| · 5.9 Uncertain (part 4) | – | open points / boundary list, no claim to rate |  |
| 6. Construction, service shell and small helpers (sweep) | – | container (see its subsections) |  |
| · 6.1 Parser handler tables (`PROTOCOLFUNCTIONTEMPLETE<T>`) | medium | cap 1/1 | capture (class U) |
| · 6.2 Member and session constructors | medium | cap 0/1 | capture (class U) |
| · 6.3 Windows-service shell, crash dump, checksums | medium | read in code | second reading / client check |
| · 6.4 Small helpers | medium | cap 0/2 | capture 0x7433, 0x7434 |
| 7. Original-server bugs | medium | cap 10/13; weak inf2; bug table (class X: effects are deductions) | capture 0x5830 |
| 8. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.11 W06: `wm/W06-leftovers.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Guild classes shared with the client (`CGuild`, `CGuildMembe… | – | container (see its subsections) |  |
| · 1.1 Classes and vftables | medium | read in code | second reading / client check |
| · 1.2 Slot map and reachability | medium | cap 0/42; weak inf1 | capture 0x7406, 0x740A, 0x7419, 0x741B … |
| · 1.3 Live slots | medium | cap 0/7; weak inf2 | capture 0x7419, 0x741B, 0x980E, 0x9825 |
| · 1.4 Dead slots (client-side handlers compiled into the WM) | medium | cap 0/1 | capture (class U) |
| · 1.5 `CGuildWar m_GuildWar` (CGuild+0x438): the war list | medium | cap 0/1 | capture 0x7427 |
| · 1.6 Guild constructors, destructors, copy operators | medium | read in code | second reading / client check |
| 2. Verdicts on X02's open points | – | open points / boundary list, no claim to rate |  |
| · 2.1 E14: the trailing 0x0CDB of 0x740C (W03 §2.5) is **not** de… | medium | cap 0/2; R×1 | capture 0x740D |
| · 2.2 E15: client 0x7425 `GuildTask::Recv_NC_GUILD_WAR_ABLE_LIST_… | medium | cap 0/2; client×1 | capture 0x7425 |
| · 2.3 E25 (second half): W04 §12.3, the dice-game test that drops… | medium | cap 0/2; client×1; weak inf1 | capture 0x9403 |
| 3. The other leftover functions (shared code, destructors, CRT) | – | container (see its subsections) |  |
| · 3.1 `RandomBox rndbox` and `cWell512Random` (the global random … | medium | cap 0/1 | capture (class U) |
| · 3.2 `ItemOptionsData itemoptiondata`, `rewarddata`, `fprewardda… | medium | weak inf1 | second reading / client check |
| · 3.3 Destructors of live WM objects | medium | read in code | second reading / client check |
| · 3.4 Packet-builder destructors (stack objects of send functions) | medium | cap 0/2 | capture 0x3809, 0x747F |
| · 3.5 `Raid::iterator::operator!=` FUN_00462e60 | medium | cap 0/1 | capture 0xB02E |
| · 3.6 MSVC runtime `type_info` | medium | read in code | second reading / client check |
| Original-server bugs | medium | cap 0/6; client×3; weak inf2; bug table (class X: effects are deductions) | capture 0x7425, 0x9825 |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.12 Z01: `zone/Z01-core.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process structure | medium | cap 2/2; sup×1 (README §5.4); cv corr; ours×2 | re-read the rest (§3); read with P02 "Corrections" |
| 2. Startup | – | container (see its subsections) |  |
| · 2.1 Entry and the downloaded start script | **low** | sup×1 (README §5.4); weak inf1; ours×1 | re-read the rest (§3) |
| · 2.2 Lua globals registered for the start script | medium | read in code | second reading / client check |
| · 2.3 Data tables and their loaders | **low** | sup×1 (README §5.4) | re-read the rest (§3) |
| 3. Network layer | **low** | no function cited; sup×2 (README §5.4) | re-read the rest (§3) |
| · 3.1 Packet buffer and send primitives | medium | weak inf1 | second reading / client check |
| · 3.2 Broadcast (who receives a packet) | medium | sight delivery to a bystander is captured (walk relay, swings, casts, 0x1805; capture-validation §27.2, §27.6, §27.7) and so is a whole-map shout to a player out of sight (§27.4); the section is too general there (code read in X09 part 4, docs/knowledge/X09.md §4): so_AllInMap FUN_0054b8c0 -> so_AllInMapNomal FUN_0054be00 walks the whole map list with a layer filter only, and FUN_0049ac70 in ali_Work is so_SubLayer_CanSee, not a sight check; the sight radius is so_AllOfRange FUN_0054baf0 (hand; baseline: medium) | the README §5 superseded-statement row (X08) and a capture of a so_AllOfRange broadcast not reaching a player just outside MapInfo.Sight |
| · 3.3 Server-to-server handshake and heartbeat | medium | cap 7/9; cv ok; sup×1 (README §5.4); cv corr; B×3 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser |
| 4. Objects | **low** | no function cited; sup×7 (README §5.4) | re-read the rest (§3) |
| · 4.1 Class hierarchy (RTTI) | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |
| · 4.2 ShineObjectManager and handles | medium | cap 0/1; ours×1 | capture 0x202C |
| · 4.3 Player mode | **low** | cap 4/11; sup×1 (README §5.4) | re-read the rest (§3); capture 0x181F |
| 5. Map login | **high** | cap 12/13 |  |
| · 5.1 Seed | **low** | cap 1/2; sup×1 (README §5.4) | re-read the rest (§3) |
| · 5.2 0x1801 NC_MAP_LOGIN_REQ | medium | cap 3/3; cv ok; client×2; sup×1 (README §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 5.3 WM answers | medium | cap 11/12; cv ok; sup×1 (README §5.4) | re-read the rest (§3) |
| 6. 0x1803 NC_MAP_LOGINCOMPLETE_CMD (login burst) | medium | cap 9/15; cv ok; client×2; sup×7 (README §5.4); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; capture 0x0810, 0x182C, 0x7C05 |
| 7. Moving between maps | – | container (see its subsections) |  |
| · 7.1 so_LinkTo (gate, NPC, script, skill teleport) | medium | cap 9/10; cv ok; client×2; sup×1 (README §5.4); weak inf2 | re-read the rest (§3) |
| · 7.2 Wing (saved locations) | **low** | cap 0/4; sup×1 (README §5.4); R×1; weak inf1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json`; capture 0x1815, 0x1817 |
| · 7.3 Town portal and multi-link NPC | medium | cap 2/9; client×1 | capture 0x181F, 0x1820, 0x2028, 0x2029 … |
| · 7.4 0x181C NC_MAP_TONORMALCOORD_CMD and so_ply_ToNormalLoc | medium | cap 1/4; weak inf1 | capture (class U) |
| 8. Logout, kick and character save | **low** | no function cited; sup×1 (README §5.4) | re-read the rest (§3) |
| · 8.1 Normal logout | medium | cap 2/2; cv ok; sup×4 (README §5.3, §5.4); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| · 8.2 sp_RefreshWMSSocket | **low** | cap 1/1; sup×1 (README §5.4) | re-read the rest (§3) |
| · 8.3 Disconnect and kick | medium | cap 5/5; cv ok; sup×3 (README §5.3, §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 8.4 Character save (WholeSaver) | medium | cap 23/27; cv ok; sup×4 (README §5.4); cv corr; B×2; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser |
| 9. Other client and WM messages in scope | **low** | cap 1/22; sup×3 (README §5.4); B×1; weak p171 | re-read the rest (§3); follow the return value to the parser; capture 0x0812, 0x0813, 0xB413 |
| 10. Zone ring (ZoneListenSession / ZoneConnectSession) | medium | cap 3/25 | capture (class U) |
| 11. Client cross-check (summary) | **high** | cap 9/18 |  |
| Original-server bugs | **low** | cap 5/19; sup×4 (README §5.4); B×1; weak inf1; bug table (class X: effects are deductions) | re-read the rest (§3); follow the return value to the parser; capture 0x0812, 0x181F, 0x1820, 0x2028 … |
| 12. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.13 Z02: `zone/Z02-actions.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Conventions used in this file | medium | cap 6/9; sup×2 (README §5.4); ours×5 | re-read the rest (§3); capture 0x2004, 0x2075, 0x74CC |
| 2. Movement | medium | weak inf1 | second reading / client check |
| · 2.1 0x2003 NC_ACT_WALK_REQ / 0x2005 NC_ACT_RUN_REQ `{ u32 from.… | medium | cap 2/6; weak inf1 | capture 0x2004, 0x2006 |
| · 2.2 0x2017 NC_ACT_MOVEWALK_CMD / 0x2019 NC_ACT_MOVERUN_CMD `{ u… | medium | cap 6/6; cv ok; client×1; sup×1 (README §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 2.3 0x2012 NC_ACT_STOP_REQ `{ u32 loc.x, loc.y }` | **high** | cap 3/3 |  |
| · 2.4 0x2024 NC_ACT_JUMP_CMD (no payload) | **high** | cap 2/2; cv ok |  |
| · 2.5 0x2008 NC_ACT_CHANGEMODE_REQ `{ u8 mode }` | **high** | cap 2/2; client×1; weak inf1 |  |
| 3. Chat | – | container (see its subsections) |  |
| · 3.1 0x2001 NC_ACT_CHAT_REQ `{ u8 itemLinkDataCount, u8 len, u8 … | medium | cap 2/3; sup×2 (README §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 3.2 0x201E NC_ACT_SHOUT_CMD `{ u8 itemLinkDataCount, u8 len, u8… | medium | cap 2/3; cv ok; sup×2 (README §5.4); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 3.3 Admin ("&") commands | medium | read in code | second reading / client check |
| · 3.4 Spam filter | **low** | cap 1/3; client×1; sup×1 (README §5.4) | re-read the rest (§3); capture 0x0848 |
| 4. Emotes | medium | captured: Sit 0x2020 {7} -> 0x2021, the step that ends an emote, jump (capture-validation §27.3), and the client side was extended (Stand and Esc send nothing; §13 -> X08); 0x2022 / 0x2023 and 0x2020 {6} are in no capture (hand; baseline: medium) | capture-scenarios 54 (key function 0x6F; /stand), test-client case T27 (0x2020 {6}) |
| 5. Sight and brief info (what other players see) | medium | cap 1/2; cv ok; sup×1 (README §5.4) | re-read the rest (§3); capture 0x748D |
| · 5.1 0x1C01 NC_BRIEFINFO_INFORM_CMD `{ u16 nMyHnd, u16 ReceiveNe… | **high** | cap 2/2; cv ok |  |
| · 5.2 Brief-info exchange (login, regen, teleport) | medium | cap 3/4; cv ok; sup×3 (README §5.4); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; capture 0x1C07 |
| 6. NPC click, NPC roles and server menus | – | container (see its subsections) |  |
| · 6.1 Data | **low** | B×1 | follow the return value to the parser |
| · 6.2 0x200A NC_ACT_NPCCLICK_CMD `{ u16 npchandle }` | medium | cap 3/3; sup×1 (README §5.4); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| · 6.3 0x201D NC_ACT_NPCMENUOPEN_ACK `{ u8 ack }` | **high** | cap 1/1 |  |
| · 6.4 0x200B NC_ACT_ENDOFTRADE_CMD, 0x2073 NC_ACT_NPC_MENU_CMD | medium | cap 1/3 | capture 0x3C0F |
| · 6.5 Role actions | **low** | cap 4/12; sup×1 (README §5.4) | re-read the rest (§3); capture 0x181F, 0x3C03, 0x3C04, 0x3C06 … |
| · 6.6 Server menus (generic yes/no dialogs) and 0x3C02 NC_MENU_SE… | medium | cap 2/3; sup×1 (README §5.4); N: `sma_Reset` | re-read the rest (§3); README §4.8; capture 0x3C0F |
| 7. Tents (mini-house rest mode) | medium | cap 0/6; client×1; weak inf1 | capture 0x2028, 0x2029, 0x202B, 0x202C |
| 8. Gathering and production | **low** | cap 0/15; sup×4 (README §5.4); weak inf2 p171; R×1 | re-read the rest (§3); code or capture for the marked statements; callers incl. vtable slots; senders in every `handlers.json`; capture 0x202E, 0x202F, 0x2031, 0x2033 … |
| 9. Mounts, megaphone, item emotes | – | container (see its subsections) |  |
| · 9.1 0x2044 NC_ACT_RIDE_FEEDING_REQ `{ u8 slot }` | medium | the captured opcodes are only mentioned here (0x10C6, 0x2019); the subject of the section (0x2044 / 0x2046 ride feeding) is in no capture (hand; baseline: high) | capture 0x2044, 0x2046 (feed a mount) |
| · 9.2 0x204B NC_ACT_ROAR_REQ `{ u8 slot, u8 len, u8 content[len] … | medium | the captured opcodes are only mentioned here (0x0720, 0x300C); the subject of the section (0x204B / 0x204C roar) is in no capture (hand; baseline: high) | capture 0x204B, 0x204C (use a megaphone item) |
| · 9.3 0x2067 NC_ACT_ACTIONBYITEM_REQ `{ u8 slot }` (premium emote… | medium | cap 0/2 | capture 0x2068 |
| 10. Wedding | **low** | cap 1/23; sup×3 (README §5.4); weak inf2 | re-read the rest (§3); capture 0x2050, 0x2052, 0x2054, 0x2057 … |
| 11. 0x2070 NC_ACT_AUTO_WAY_FINDING_USE_GATE_REQ (no payload) | medium | the captured opcodes are only mentioned here (0x2401 / 0x2402 targeting); the subject of the section (0x2070 / 0x2071 auto way-finding gate use) is in no capture (hand; baseline: high) | capture 0x2070, 0x2071 |
| 12. Scenario areas and script interrupts | **low** | cap 0/4; client×1; sup×1 (README §5.4) | re-read the rest (§3); capture 0x6C05, 0x6C07 |
| 13. Field (map) permissions used here | medium | cap 2/5 | capture (class U) |
| 14. Client cross-check (summary) | medium | cap 17/44 | capture 0x0848, 0x1C07, 0x2004, 0x2006 … |
| Original-server bugs | **low** | cap 7/30; R×1; bug table (class X: effects are deductions) | callers incl. vtable slots; senders in every `handlers.json`; capture 0x202E, 0x204C, 0x2052, 0x2054 … |
| 15. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.14 Z03: `zone/Z03-combat.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Conventions used in this file | **low** | sup×4 (README §5.4, §5.5); ours×4 | re-read the rest (§3) |
| 2. Targeting | **low** | no function cited; sup×2 (README §5.5) | re-read the rest (§3) |
| · 2.1 State | medium | read in code | second reading / client check |
| · 2.2 NC_BAT_TARGETTING_REQ `0x2401` (C→Z) @ FUN_0042ffe0 | **high** | cap 1/2 |  |
| · 2.3 Target information | medium | cap 1/1; client×1 | capture (class U) |
| · 2.4 Server-side target change | medium | cap 0/1 | capture 0x244D |
| · 2.5 NC_BAT_UNTARGET_REQ `0x2408` (C→Z) @ FUN_0042b6a0 | **high** | cap 1/1 |  |
| · 2.6 NC_BAT_ASSIST_REQ `0x243E` (C→Z) @ FUN_0042b7a0 | **low** | 0x243E is in no capture: the 2016 client's assist sent a plain 0x2401 to the target's target (capture-validation §25.5, §13 "unconfirmed"), and the 2016 client export has no 0x243e literal (docs/knowledge/X07.md §2) (hand; baseline: low) | test-client case T25 (capture-scenarios §3.41) |
| 3. Basic attack ("bash" / swing) | – | container (see its subsections) |  |
| · 3.1 NC_BAT_BASHSTART_CMD `0x242B` (C→Z) @ FUN_00430fa0 | medium | cap 1/1; sup×1 (README §5.5) | re-read the rest (§3) |
| · 3.2 The swing cycle | medium | cap 3/3; cv ok; sup×3 (README §5.5); cv corr; N: `g_HitRateScale` | re-read the rest (§3); read with P02 "Corrections"; README §4.8 |
| · 3.3 Who may be hit | **low** | sup×1 (README §5.5) | re-read the rest (§3) |
| · 3.4 Stopping | **high** | cap 3/3 |  |
| · 3.5 The older "bash" packets | **low** | cap 0/1; sup×1 (README §5.5) | re-read the rest (§3); capture 0x242E |
| 4. Rules of engagement (hit, critical, damage) | – | container (see its subsections) |  |
| · 4.1 The stat matrix | **low** | sup×3 (README §5.5) | re-read the rest (§3) |
| · 4.2 The context and the four rule sets | **low** | sup×3 (README §5.5) | re-read the rest (§3) |
| · 4.3 Hit rate | **low** | sup×2 (README §5.5); N: `g_HitRateScale` | re-read the rest (§3); README §4.8 |
| · 4.4 Item-action rates | medium | read in code | second reading / client check |
| · 4.5 `roe_CalcDamage` @ FUN_00505c00 | **low** | sup×3 (README §5.5); N: `g_HitRateScale` | re-read the rest (§3); README §4.8 |
| · 4.6 Attack power, defence, damage | **low** | sup×1 (README §5.5); weak inf1 | re-read the rest (§3) |
| 5. Skills | **low** | no function cited; sup×1 (README §5.5) | re-read the rest (§3) |
| · 5.1 Data | **low** | sup×1 (README §5.5) | re-read the rest (§3) |
| · 5.2 NC_BAT_SKILLBASH_OBJ_CAST_REQ `0x2440` (C→Z) @ FUN_0057fa50 | **high** | cap 2/2; cv ok; client×1 |  |
| · 5.3 Cost | medium | read in code | second reading / client check |
| · 5.4 Casting, abort, blast | medium | cap 9/9; cv ok; client×1; sup×2 (README §5.5) | re-read the rest (§3) |
| · 5.5 NC_BAT_SKILLBASH_FLD_CAST_REQ `0x2441` (C→Z) @ FUN_0057f400 | **high** | cap 1/1; cv ok |  |
| · 5.6 Effect application | medium | cap 1/2; cv ok; sup×5 (README §5.5); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x2453 |
| 6. Abnormal states | – | container (see its subsections) |  |
| · 6.1 Tables and structures | **low** | cap 1/1; sup×4 (README §5.5) | re-read the rest (§3) |
| · 6.2 Setting a state | **low** | cap 1/1; sup×1 (README §5.5) | re-read the rest (§3) |
| · 6.3 Packets | **high** | cap 5/5 |  |
| · 6.4 Expiry and removal | medium | read in code | second reading / client check |
| · 6.5 NC_BAT_ABSTATE_ERASE_REQ `0x2454` (C→Z) @ FUN_0042b900 | medium | cap 0/2; client×1 | capture 0x2455 |
| · 6.6 The status flag byte `obj + 0x1e78` (open question from Z02) | **low** | sup×2 (README §5.5); weak inf1 | re-read the rest (§3) |
| 7. Damage, death | **high** | cap 2/2 |  |
| · 7.1 Common part | medium | cv ok; sup×2 (README §5.5); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 7.2 Player death | **high** | cap 6/10; cv ok; weak inf1 |  |
| · 7.3 Revive by skill: NC_SKILL_REPLYREVIVE_CMD `0x482A` (C→Z) @ … | medium | cap 5/6; cv ok; sup×1 (README §5.5); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x482B |
| 8. Mob death, experience, level-up | – | container (see its subsections) |  |
| · 8.1 Mob death | medium | cap 1/3; cv ok; sup×1 (README §5.5) | re-read the rest (§3) |
| · 8.2 Experience | **low** | sup×2 (README §5.5) | re-read the rest (§3) |
| · 8.3 `ShinePlayer::sp_GainExp` @ FUN_0042d830 | medium | cap 8/10; cv ok; client×1; sup×1 (README §5.5) | re-read the rest (§3); capture 0x5C0D |
| 9. Skill learning, empowering, unlearning | – | container (see its subsections) |  |
| · 9.1 NC_SKILL_EMPOWALLOC_REQ `0x4811` (C→Z) @ FUN_0044f150 | medium | cap 4/4; cv ok; client×1; sup×1 (README §5.5); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 9.2 Empower reset answers (DB→Z) | medium | cap 0/5 | capture 0x480E, 0x480F |
| · 9.3 Skill teach answers (DB→Z) | **high** | cap 3/6; cv ok |  |
| · 9.4 NC_SKILL_PRODUCTFIELD_REQ `0x4822` (C→Z) @ FUN_0046c820 | medium | the captured opcodes are only mentioned here (0x4801 / 0x4802 / 0x4804 of the skill-book learn, capture-validation §24.2); the subject of the section (0x4822 production field) is in no capture (hand; baseline: high) | capture 0x4822 |
| · 9.5 NC_SKILL_UNLEARN_REQ `0x4824` (C→Z) @ FUN_0057ad80 | medium | cap 0/4; cv ok; client×1 | capture 0x4827 |
| 10. Client cross-check (packets sent by this subsystem) | **high** | cap 31/43; client×1 |  |
| Original-server bugs | **low** | cap 3/5; sup×2 (README §5.5); bug table (class X: effects are deductions) | re-read the rest (§3); capture 0x482B |
| 11. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.15 Z04: `zone/Z04-items.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data model | – | container (see its subsections) |  |
| · 1.1 Cell address (`ITEM_INVEN`) | **low** | cap 1/1; sup×1 (README §5.6); R×1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json` |
| · 1.2 Item cell and item | medium | weak p171 | second reading / client check |
| · 1.3 Belong types (`BelongTypeInfo.shn`, `g_BelongType` DAT_150b… | medium | ours×1 | second reading / client check |
| · 1.4 Inventory locking and DB requests | medium | ours×1 | second reading / client check |
| · 1.5 Server-menu confirmations | **low** | cap 0/1; N: `ItemMenu_Open`; ours×1 | README §4.8; capture 0x1829 |
| 2. Shop: buy and sell | – | container (see its subsections) |  |
| · 2.1 NC_ITEM_BUY_REQ `0x3003` (C→Z) @ FUN_00524a60 | medium | cap 3/5; sup×4 (README §5.4, §5.6); cv corr; N: `NPCRangeCheck_Check`; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; README §4.8 |
| · 2.2 Buying with items ("item money") @ FUN_00526ac0 `so_ply_Ite… | medium | cap 0/2 | capture (class U) |
| · 2.3 Buying with guild tokens @ FUN_00526ef0 `so_ply_ItemBuyGuil… | medium | cap 1/3; client×1 | capture (class U) |
| · 2.4 NC_ITEM_SELL_REQ `0x3006` (C→Z) @ FUN_00539020 | medium | cap 6/6; cv ok; client×1; sup×1 (README §5.6); N: `NPCRangeCheck_Check` | re-read the rest (§3); README §4.8 |
| · 2.5 NC_ITEM_REPURCHASE_REQ `0x3059` (C→Z) @ FUN_00538580 | medium | cap 7/8; cv ok; client×1; sup×1 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x305B |
| 3. Dropping, destroying, picking up | – | container (see its subsections) |  |
| · 3.1 NC_ITEM_DROP_REQ `0x3007` (C→Z) @ FUN_00529f50 | medium | cap 3/5; cv ok; client×1; sup×1 (README §5.6); N: `ItemMenu_Open` | re-read the rest (§3); README §4.8; capture 0x1829 |
| · 3.2 Destroying an item (ItemBreaker) | **low** | cap 1/4; sup×1 (README §5.6); S: p+0xaad8; N: `ItemMenu_Open` | re-read the rest (§3); PDB member (`pdb.py` ShinePlayer); README §4.8; capture 0x1829, 0xD411 |
| · 3.3 NC_ITEM_PICK_REQ `0x3009` (C→Z) @ FUN_00530a50 | medium | cap 6/7; cv ok; client×1; sup×3 (README §5.6); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| 4. Moving items | – | container (see its subsections) |  |
| · 4.1 NC_ITEM_RELOC_REQ `0x300B` (C→Z) @ FUN_00537170 → FUN_00536… | medium | captured: split-and-merge and the exchange onto a stack at MaxLot (capture-validation §26.2), and the capture extended the branch list (b >= MaxLot -> irm_Exchange; §13 -> X08); the 0x24A refusal and the irm_Move / 0x20A branch are in no capture (hand; baseline: medium) | capture-scenarios 53 (S22: a character-bound stack in the account storage) |
| · 4.2 NC_ITEM_SPLIT_REQ `0x300D` (C→Z) @ FUN_00539a40 | medium | cap 3/3; cv ok; client×1; sup×2 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 5. Equipment | – | container (see its subsections) |  |
| · 5.1 NC_ITEM_EQUIP_REQ `0x300F` (C→Z) @ FUN_0052b8d0 | medium | cap 3/3; client×1; sup×2 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 5.2 NC_ITEM_RINGEQUIP_REQ `0x3010` (C→Z) @ FUN_0052c5b0 | medium | the captured opcodes are only mentioned here (0x3011 / 0x3410 of the normal equip, §5.1); the 2016 client equipped both rings of batch 3 with 0x300F (capture-validation §19.7), so the subject of the section (0x3010 ring equip) is in no capture (hand; baseline: high) | test client: send 0x3010 |
| · 5.3 NC_ITEM_MINIMON_EQUIP_REQ `0x3050` (C→Z) @ FUN_0052d020 | medium | the captured opcodes are only mentioned here (0x3011 / 0x3410 of the normal equip, §5.1); the subject of the section (0x3050 mini-monster equip) is in no capture (hand; baseline: high) | capture 0x3050 |
| · 5.4 NC_ITEM_UNEQUIP_REQ `0x3012` (C→Z) @ FUN_0053a990 | **high** | cap 3/3; client×1 |  |
| 6. Using items | – | container (see its subsections) |  |
| · 6.1 NC_ITEM_USE_REQ `0x3015` (C→Z) @ FUN_005416b0 | medium | cap 2/2; sup×1 (README §5.6); ours×2 | re-read the rest (§3) |
| · 6.2 NC_ITEM_USEABORT_CMD `0x3019` (C→Z) @ FUN_0053f960 | medium | cap 0/1 | capture (class U) |
| · 6.3 UseEffect actors | medium | cap 2/2; cv ok; sup×2 (README §5.6); cv corr; B×1 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser |
| · 6.4 Megaphone (answers Z02 §9.2) | medium | the captured opcodes are only mentioned here (0x6401 / 0x6402 of the level-20 announcement); the subject of the section (the megaphone 0x204B / 0x204C) is in no capture (hand; baseline: high) | capture 0x204B, 0x204C (use a megaphone item) |
| 7. Storage | – | container (see its subsections) |  |
| · 7.1 NC_ITEM_DEPOSIT_REQ `0x301C` / NC_ITEM_WITHDRAW_REQ `0x301E… | **high** | cap 6/6; cv ok; client×1 |  |
| · 7.2 NC_ITEM_OPENSTORAGEPAGE_REQ `0x3028` (C→Z) @ FUN_00536650 | medium | the storage open 0x3444 is captured (capture-validation §7.6.1), but the 2016 client never sent 0x3028 in batch 2 or 3: all four pages come with the open (§20.1) (hand; baseline: high) | test-client case T16 (capture-scenarios §3.41) |
| · 7.3 NC_ITEM_ACCOUNT_STORAGE_OPEN_CMD `0x304C` / CLOSE_CMD `0x30… | **high** | cap 1/2 |  |
| · 7.4 NC_ITEM_GUILD_STORAGE_WITHDRAW_REQ `0x3026` (C→Z) @ FUN_005… | medium | cap 0/3; client×1 | capture 0x3027 |
| · 7.5 Guild-academy reward storage money: NC_ITEM_GUILD_ACADEMY_R… | medium | cap 0/6; client×1 | capture 0x3030 |
| 8. Premium ("charged") and reward inventories | – | container (see its subsections) |  |
| · 8.1 NC_ITEM_CHARGEDINVENOPEN_REQ `0x3020` (C→Z) @ FUN_004923c0 | **high** | cap 3/3 |  |
| · 8.2 NC_ITEM_CHARGED_WITHDRAW_REQ `0x3022` (C→Z) @ FUN_00492660 | medium | the captured opcodes are only mentioned here (0x1047 / 0x104B / 0x104C of the login); the subject of the section (0x3022 / 0x3023 / 0x3465 premium withdraw) is in no capture (hand; baseline: high) | capture 0x3022, 0x3023 (DB setup: a charged item row, part 9) |
| · 8.3 NC_ITEM_REWARDINVENOPEN_REQ `0x302C` (C→Z) @ FUN_004fc060 | medium | cap 3/4; sup×1 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x302E |
| · 8.4 NC_ITEM_MH_FURNITURE_ENDURE_KIT_USE_REQ `0x3033` (C→Z) @ FU… | **low** | cap 0/2; client×1; sup×1 (README §5.6) | re-read the rest (§3); capture 0x3034 |
| 9. Upgrades (enhancement) | – | container (see its subsections) |  |
| · 9.1 NC_ITEM_UPGRADE_REQ `0x3017` (C→Z) @ FUN_0053d220 | medium | cap 0/3 | capture 0x3018 |
| · 9.2 NC_ITEM_NEW_UPGRADE_REQ `0x306D` (C→Z) @ FUN_0053e360 | medium | cap 0/6 | capture 0x306E, 0x3807 |
| · 9.3 NC_ITEM_BRACELET_UPGRADE_REQ `0x306F` (C→Z) @ FUN_0053ec40 | medium | cap 2/6 | capture 0x3070, 0x3C04 |
| · 9.4 The roll @ FUN_0053ca10 `Item_Upgrade_Table_mode` | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 9.5 NC_ITEM_MOVER_UPGRADE_REQ `0x3051` (C→Z) @ FUN_0051c850 | medium | cap 0/4 | capture 0x3052 |
| 10. Enchanting (gem sockets) | medium | read in code | second reading / client check |
| · 10.1 NC_ITEM_ENCHANT_ADD_GEM_REQ `0x3040` (C→Z) @ FUN_00522560 | **low** | cap 0/5; client×1; sup×1 (README §5.6) | re-read the rest (§3); capture 0x2082, 0x2083, 0x3041 |
| · 10.2 NC_ITEM_ENCHANT_REMOVE_GEM_REQ `0x3042` (C→Z) @ FUN_005229… | medium | cap 0/3 | capture 0x3043 |
| · 10.3 NC_ITEM_ENCHANT_ADD_NEW_SOCKET_REQ `0x3044` (C→Z) @ FUN_00… | medium | cap 0/3 | capture 0x3045 |
| 11. Random options | – | container (see its subsections) |  |
| · 11.1 NC_ITEM_RANDOMOPTION_CHANGE_REQ `0x3053` (C→Z) @ FUN_00520… | medium | cap 0/3; client×1 | capture 0x3054 |
| · 11.2 NC_ITEM_RANDOMOPTION_CHANGE_ACCEPT_REQ `0x3061` (C→Z) @ FU… | medium | cap 0/3 | capture 0x3062 |
| · 11.3 NC_ITEM_RANDOMOPTION_RECOVER_COUNT_LIMIT_REQ `0x306B` (C→Z… | medium | cap 0/3 | capture 0x306C |
| 12. Other item services | – | container (see its subsections) |  |
| · 12.1 NC_ITEM_DISMANTLE_REQ `0x302A` (C→Z) @ FUN_005293c0 | medium | cap 0/3 | capture 0x302B |
| · 12.2 NC_ITEM_WEAPONENDURE_CHARGE_REQ `0x3035` / NC_ITEM_SHIELDE… | **low** | cap 0/8; client×1; sup×1 (README §5.6) | re-read the rest (§3); capture 0x3036, 0x3037, 0x3065, 0x3066 |
| · 12.3 NC_ITEM_REVIVEITEMUSE_CMD `0x3039` (C→Z) @ FUN_00417580 | medium | cap 0/3 | capture 0x303A, 0x482B |
| · 12.4 NC_ITEM_DICE_GAME_START_REQ `0x303C` (C→Z) @ FUN_00517d70 | medium | cap 0/6 | capture 0x2004, 0x303B, 0x303D, 0x303E … |
| · 12.5 NC_ITEM_AUTO_ARRANGE_INVEN_REQ `0x304A` (C→Z) @ FUN_0051c3… | medium | cap 2/2; sup×1 (README §5.6) | re-read the rest (§3) |
| · 12.6 NC_ITEM_EQUIP_BELONGED_CANCEL_USE_REQ `0x3048` (C→Z) @ FUN… | **low** | cap 0/3; sup×1 (README §5.6); weak inf2 | re-read the rest (§3); capture 0x3049 |
| · 12.7 NC_ITEM_USE_ACTIVESKILL_REQ `0x304E` (C→Z) @ FUN_00540b90 | **low** | cap 0/2; sup×1 (README §5.6) | re-read the rest (§3); capture 0x304F |
| · 12.8 NC_ITEM_CHAT_COLOR_CHANGE_REQ `0x3055` (C→Z) @ FUN_0051e580 | medium | cap 0/4; client×1 | capture 0x3056 |
| · 12.9 NC_ITEM_TERMEXTEND_REQ `0x3057` (C→Z) @ FUN_0051eb40 | medium | cap 0/3 | capture 0x3058 |
| · 12.10 NC_ITEM_CLASS_CHANGE_REQ `0x305E` (C→Z) @ FUN_0051f5c0 | medium | cap 0/4 | capture 0x305F, 0x3060 |
| · 12.11 NC_ITEM_MAPLINK_SCROLL_REQ `0x3067` (C→Z) @ FUN_00520130 | medium | cap 0/3; weak inf1; ours×1 | capture 0x3068 |
| · 12.12 NC_ITEM_MIX_ITEM_REQ `0x3069` (C→Z) @ FUN_00521540 | medium | cap 0/3 | capture 0x306A |
| 13. Soul stones (HP / SP potions) | – | container (see its subsections) |  |
| · 13.1 NC_SOULSTONE_HP_BUY_REQ `0x5001` / SP_BUY_REQ `0x5002` (C→… | **high** | cap 5/6; cv ok; client×1 |  |
| · 13.2 NC_SOULSTONE_HP_USE_REQ `0x5007` / SP_USE_REQ `0x5009` (C→… | medium | cap 6/7; cv ok; sup×1 (README §5.6); cv corr; B×1 | re-read the rest (§3); read with P02 "Corrections"; follow the return value to the parser; capture 0x5006 |
| Original-server bugs | **low** | cap 12/30; sup×3 (README §5.4, §5.6); bug table (class X: effects are deductions) | re-read the rest (§3); capture 0x3030, 0x3034, 0x303A, 0x3C07 … |
| 14. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.16 Z05: `zone/Z05-itemdb.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Transaction model | medium | cv ok; no function cited; sup×3 (README §5.6) | re-read the rest (§3) |
| · 1.1 Two commit styles | medium | cv ok; sup×2 (README §5.6) | re-read the rest (§3) |
| · 1.2 `InventoryLocking::InventoryCellLockList` vtable (`p+0xfaa8… | medium | cv ok; B×1 | follow the return value to the parser |
| · 1.3 Apply and free @ FUN_0048be90, FUN_0048c100, FUN_0048b2c0 | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 1.4 Releasers (what "apply" does), `InventoryLocking::InvenCell… | **low** | cap 5/13; sup×3 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x8C20, 0x8C21, 0x8C24, 0x8C27 … |
| · 1.5 Client packets produced by an apply | **high** | cap 2/2; client×1 |  |
| · 1.6 Handler skeleton and the error helpers | medium | read in code | second reading / client check |
| · 1.7 Requests and answers | medium | cap 53/181 | capture (class U) |
| 2. Shop | – | container (see its subsections) |  |
| · 2.1 Buy: `0x340B`/`0x340E` BUYALLSUC/BUYLOTSUC, `0x340C`/`0x340… | **high** | cap 5/10; cv ok; client×1; ours×1 |  |
| · 2.2 Sell and repurchase | **high** | cap 8/10; cv ok |  |
| · 2.3 Guild-token buy: `0x3491`/`0x3494` and fails | **low** | cap 1/6; B×1 | follow the return value to the parser |
| · 2.4 Soul stones: `0x3442` / `0x3443` | medium | captured (two purchases, capture-validation §20.3), and the 0x3441 / 0x3442 layouts were corrected by that capture (§20.5: `{ref, lock}`); 0x3443 / 0x5005 are in no capture: in batch 5 the 2016 client refused both soul-stone cases itself (0 cen, at the limit; no 0x5001 sent, capture-validation §26.5) (hand; baseline: high) | test-client case T18 (0x5005); capture-scenarios 47 step 3 with S17 (0x3443, the DB-side refusal) |
| · 2.5 Capsule buy: `0x34A1` | medium | the captured opcodes are only mentioned here (the shared buy answer 0x3004); the subject of the section (0x34A1 capsule buy) is in no capture (hand; baseline: high) | capture 0x34A1 |
| · 2.6 Item-money buy: `0x34B2` | medium | the captured opcodes are only mentioned here (the shared buy answer 0x3004); the subject of the section (0x34B2 item-money buy) is in no capture (hand; baseline: high) | capture 0x34B2 |
| 3. Drop, pick-up, money (style 2: applied before the DB answer) | – | container (see its subsections) |  |
| · 3.1 Drop: `0x3417`, `0x3418`, `0x341A`, `0x341B` | medium | cap 3/6; cv ok; sup×2 (README §5.6); cv corr; R×1 | re-read the rest (§3); read with P02 "Corrections"; callers incl. vtable slots; senders in every `handlers.json` |
| · 3.2 Pick-up: `0x341D`…`0x3421`, `0x3439`, `0x343A` | **high** | cap 4/7; client×1 |  |
| · 3.3 Money: `0x347B` / `0x347C` | medium | cap 0/3 | capture (class U) |
| 4. Moving and stacking | medium | cap 7/12; cv ok; sup×1 (README §5.6) | re-read the rest (§3) |
| 5. Equipment | – | container (see its subsections) |  |
| · 5.1 Equip / unequip: `0x3411`, `0x3412`, `0x3414`, `0x3415` | medium | cap 6/8; sup×1 (README §5.6) | re-read the rest (§3) |
| · 5.2 Reinforce unequip: `0x3480` / `0x3481` | medium | cap 0/4 | capture (class U) |
| · 5.3 Bound-item cancel: `0x34A7` | medium | cap 0/2; client×1 | capture 0x3049 |
| · 5.4 Item attribute change: `0x344A` | medium | cap 2/2; sup×1 (README §5.6) | re-read the rest (§3) |
| 6. Using, opening and destroying items | – | container (see its subsections) |  |
| · 6.1 Item use: `0x3440` | **high** | cap 2/2; cv ok |  |
| · 6.2 Chests (present boxes): `0x346E` → `0x3450` → `0x3451` / `0… | medium | cap 1/6 | capture (class U) |
| · 6.3 Capsules: `0x34A3` → `0x34A4` → `0x34A5` | medium | cap 1/5 | capture (class U) |
| · 6.4 Breaking and destroying: `0x346B`, `0x346C`, `0x345A` | **high** | cap 4/6; cv ok |  |
| · 6.5 Quest reward: `0x345C` | medium | cap 0/1 | capture (class U) |
| · 6.6 Card opening (collection cards): `0x34A9` → `0x34AA` → `0x3… | medium | cap 1/6 | capture 0xC407 |
| 7. Storage | – | container (see its subsections) |  |
| · 7.1 Account storage: `0x3446`, `0x3445`, `0x3460`, `0x3462` | medium | cap 6/8; sup×1 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections"; capture 0x3C07 |
| · 7.2 Guild storage: `0x3473`, `0x3472`, `0x3475` | medium | cap 1/6 | capture 0x3027 |
| · 7.3 Guild-academy reward storage: `0x3484`, `0x3483`, `0x3486`,… | medium | cap 0/8 | capture 0x3030 |
| · 7.4 Premium ("charged") inventory: `0x3464`, `0x3466` | medium | cap 1/4 | capture 0x3023 |
| 8. Upgrades, enchanting and item services | – | container (see its subsections) |  |
| · 8.1 Upgrade: `0x3448`, `0x34D2`, `0x34D4` | medium | cap 7/22 | capture 0x3018, 0x306E, 0x3070, 0x3803 … |
| · 8.2 Enchanting: `0x3497`, `0x3499`, `0x349B`, `0x349D` | medium | cap 0/8; client×1 | capture 0x3041, 0x3043, 0x3045 |
| · 8.3 Mounts: `0x34AD`, `0x34AF` | medium | cap 0/3; client×1 | capture 0x3052 |
| · 8.4 Random options: `0x34B4`, `0x34C2`, `0x34CE` | medium | cap 0/7 | capture 0x3054, 0x3062, 0x306C |
| · 8.5 Other item services | medium | cap 0/10 | capture 0x3056, 0x3058, 0x305F, 0x3068 … |
| · 8.6 Dismantle: `0x3477` | medium | cap 0/2 | capture 0x302B |
| · 8.7 Endurance charges: `0x348E`, `0x34C7` | medium | cap 0/4; client×1 | capture 0x3036, 0x3065 |
| 9. Miscellaneous answers | – | container (see its subsections) |  |
| · 9.1 GM item creation: `0x3402` / `0x3403` | **high** | cap 1/2 |  |
| · 9.2 Item list creation: `0x344E` / `0x344F` | medium | cap 0/3 | capture (class U) |
| · 9.3 `0x344C` NC_ITEMDB_ITEMTOTALINFORM_ACK @ FUN_00494eb0 | medium | cap 0/1 | capture (class U) |
| · 9.4 Production: `0x3458` (answers Z07 §11) | medium | cap 1/5 | capture 0x481D |
| · 9.5 Mushroom (mini-house creation): `0x3468` / `0x3469` | medium | cap 1/2; sup×1 (README §5.6); B×1 | re-read the rest (§3); follow the return value to the parser |
| · 9.6 Mini-house furniture effect: `0x347E` (answers Z07 §6.10) | **low** | cap 0/4; sup×1 (README §5.6) | re-read the rest (§3); capture 0x8C41, 0x8C57 |
| · 9.7 Furniture endurance: `0x348C` | medium | cap 0/3 | capture 0x3034, 0x8C61 |
| · 9.8 Mystery vault: `0x349F` | **high** | cap 3/3 |  |
| · 9.9 Friend points: `0x34C0` (answers Z08 knowledge) | medium | cap 0/3; client×1 | capture 0x5422 |
| · 9.10 Trade: `0x343C` / `0x343D` (Z06 owns the trade window) | medium | cap 0/4 | capture 0x4C23 |
| · 9.11 Booth trade: `0x3456` | medium | cap 0/2 | capture 0x680E |
| 10. Client handling of the answers (2016 client) | **low** | cap 23/64; client×1; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x3018, 0x3027, 0x302B, 0x3030 … |
| 11. Invariants and state | **low** | no function cited; sup×1 (README §5.6) | re-read the rest (§3) |
| Original-server bugs | **low** | cap 6/34; sup×1 (README §5.6); bug table (class X: effects are deductions) | re-read the rest (§3); capture 0x3027, 0x3030, 0x3036, 0x3065 … |
| 12. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.17 Z06: `zone/Z06-economy.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Player-to-player trade (dept 19 `NC_TRADE_*`) | – | container (see its subsections) |  |
| · 1.1 State | medium | cap 0/10 | capture 0x4C02, 0x4C09, 0x4C0C, 0x4C0F … |
| · 1.2 Proposal | medium | cap 0/11; client×1 | capture 0x4C02, 0x4C04, 0x4C08, 0x4C09 … |
| · 1.3 Board | medium | cap 0/17 | capture 0x4C0C, 0x4C0E, 0x4C0F, 0x4C10 … |
| · 1.4 Decide and commit | medium | cap 0/9; weak p171 | capture 0x4C20, 0x4C21, 0x4C22, 0x4C23 … |
| · 1.5 Inventory sizes used here | medium | weak inf1 | second reading / client check |
| 2. Street booths (dept 26 `NC_BOOTH_*`) | – | container (see its subsections) |  |
| · 2.1 State | **low** | cap 1/2; client×1; N: `g_NoBooth`; B×2; weak inf1; ours×1 | README §4.8; follow the return value to the parser; capture 0x680B |
| · 2.2 Open | medium | cap 0/3; client×1 | capture 0x6802, 0x6803 |
| · 2.3 Close and repair ("interior") | **low** | cap 0/8; N: `g_NoBooth` | README §4.8; capture 0x6805, 0x6806, 0x6811, 0x6812 … |
| · 2.4 Visit and refresh | **low** | cap 0/6; N: `g_NoBooth` | README §4.8; capture 0x6808, 0x6809, 0x680B, 0x680C |
| · 2.5 Buying from / selling to a booth | **low** | cap 1/9; client×3; sup×1 (README §5.6); R×1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json`; capture 0x6802, 0x680E, 0x680F |
| · 2.6 Market search | medium | cap 0/5; client×1 | capture 0x6814, 0x6816, 0x6817 |
| 3. Mini-house TaiSai dice table (dept 43 `NC_DICE_TAISAI_*`) | – | container (see its subsections) |  |
| · 3.1 Tables and state | medium | weak p171 | second reading / client check |
| · 3.2 Join, leave, mode | medium | cap 0/10 | capture 0xAC02, 0xAC03, 0xAC04, 0xAC05 … |
| · 3.3 Betting | medium | cap 0/7 | capture 0xAC1B, 0xAC1C, 0xAC1E, 0xAC1F … |
| · 3.4 The roll (house routine) | **low** | cap 0/9; sup×1 (README §5.6); R×1; weak p171 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json`; capture 0xAC22, 0xAC26, 0xAC27, 0xAC2A … |
| · 3.5 Owner income and ranking | medium | cap 0/12 | capture 0xAC0E, 0xAC12, 0xAC19 |
| · 3.6 Dice-table item and money card | medium | cap 0/3 | capture 0xAC0A, 0xAC2C |
| 4. Gamble house: coins, exit, seats, TaiSai (dept 47 `NC_GAMBLE… | medium | cap 0/1 | capture 0xBC1E |
| · 4.1 Player coin state and its persistence | **high** | cap 7/10; weak p172; ours×1 |  |
| · 4.2 Buying and selling coins | **low** | cap 2/29; client×1; N: `NPCRangeCheck_Check` | README §4.8; capture 0xBC0C, 0xBC0E, 0xBC10, 0xBC14 … |
| · 4.3 Leaving the house, seats | medium | cap 0/7; client×1 | capture 0xBC03, 0xBC18 |
| · 4.4 Gamble-house TaiSai (`CGambleDiceTaiSaiObject`) | medium | cap 0/30 | capture 0xBC1C, 0xBC65, 0xBC66, 0xBC67 … |
| 5. Slot machines (`SlotMachine::*`, dept 47 cmd 200–221) | **low** | cap 2/24; sup×1 (README §5.6); weak p171 | re-read the rest (§3); capture 0xBC1C, 0xBC1E, 0xBCC9, 0xBCCB … |
| 6. Original-server bugs | medium | cap 2/23; bug table (class X: effects are deductions) | capture 0x4C24, 0x680B, 0x680E, 0xBC03 … |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.18 Z07: `zone/Z07-character.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Character data at login (WM → zone) | – | container (see its subsections) |  |
| · 1.1 The character block inside ShinePlayer | **low** | no function cited; R×1 | callers incl. vtable slots; senders in every `handlers.json` |
| · 1.2 Blob handlers | medium | cap 28/30; sup×3 (README §5.6); weak inf2 | re-read the rest (§3) |
| · 1.3 NC_CHAR_ZONE_CHARTITLE_CMD `0x1031` (WM → zone) @ FUN_005a3… | medium | cap 2/2; sup×1 (README §5.6) | re-read the rest (§3) |
| · 1.4 NC_CHAR_ZONE_CHARDATA_ACK `0x101D` / CHARDATAFAIL_ACK `0x10… | **high** | cap 3/4 |  |
| · 1.5 CHAR_PARAMETER_DATA (in 0x1802 and the parameter refresh) @… | medium | cap 1/1; sup×1 (README §5.5) | re-read the rest (§3) |
| 2. Stat points (free stats) | – | container (see its subsections) |  |
| · 2.1 Data | **low** | R×1; ours×2 | callers incl. vtable slots; senders in every `handlers.json` |
| · 2.2 NC_CHAR_STAT_INCPOINT_REQ `0x105C` (C→Z) `{u8 stat}` @ FUN_… | **high** | cap 2/3; cv ok |  |
| · 2.3 NC_CHAR_STAT_DECPOINT_REQ `0x1062` (C→Z) `{u8 stat}` @ FUN_… | **high** | cap 2/2; cv ok |  |
| · 2.4 NC_CHAR_FREESTAT_SET_DB_ACK `0x10D2` (DB→Z) @ FUN_0058be50 | **high** | cap 3/3 |  |
| · 2.5 Legacy answers `0x105E` / `0x1060` / `0x1064` / `0x1066` (D… | medium | cap 2/6; weak inf1 | capture (class U) |
| · 2.6 Related DB answers | medium | cap 0/3 | capture (class U) |
| 3. Revive, logout, polymorph and other CHAR requests | – | container (see its subsections) |  |
| · 3.1 NC_CHAR_REVIVE_REQ `0x104E` (C→Z, no payload) @ FUN_0045298… | **high** | cap 2/3; cv ok |  |
| · 3.2 NC_CHAR_REBIRTH_CMD `0x1102` / NC_CHAR_REBIRTH_REJECT_CMD `… | medium | cap 0/2 | capture (class U) |
| · 3.3 NC_CHAR_LOGOUTREADY_CMD `0x1071` / NC_CHAR_LOGOUTCANCEL_CMD… | **high** | cap 2/3; weak inf1 |  |
| · 3.4 NC_CHAR_DEPOLYMORPH_CMD `0x10B0` (C→Z, no payload) @ FUN_00… | medium | cap 0/2 | capture 0x10AF |
| · 3.5 NC_CHAR_SAVE_LINK_REQ `0x10B9` (C→Z, no payload) @ FUN_0056… | medium | cap 0/1 | capture (class U) |
| · 3.6 NC_CHAR_CLIENT_AUTO_PICK_REQ `0x10BC` (C→Z) `{u8 bEnable}` … | medium | cap 0/2 | capture (class U) |
| · 3.7 NC_CHAR_TUTORIAL_STEP_ACK `0x1117` (C→Z) `{u8 nTutorialStep… | medium | cap 0/1 | capture (class U) |
| 4. Minimon auto-buff and charged buffs | – | container (see its subsections) |  |
| · 4.1 NC_CHAR_USEITEM_MINIMON_*_ITEM_ON/OFF_REQ `0x1124` / `0x112… | **low** | cap 1/9; client×1; sup×1 (README §5.6) | re-read the rest (§3); capture 0x1125, 0x1127, 0x1129, 0x112B |
| · 4.2 NC_CHAR_CHARGEDBUFF_ERASE_REQ `0x112E` (C→Z) @ FUN_005645e0 | medium | cap 0/2 | capture 0x112F |
| 5. Wedding (zone side; client requests are in Z02 §10) | – | container (see its subsections) |  |
| · 5.1 Data and status maintenance | **low** | cap 1/7; sup×1 (README §5.6); weak inf1 | re-read the rest (§3); capture 0x205D |
| · 5.2 DB answers | medium | cap 2/14 | capture 0x2052, 0x205D |
| · 5.3 Partner info | **low** | cap 0/3; sup×1 (README §5.6) | re-read the rest (§3) |
| · 5.4 NC_CHAR_WEDDING_CANCEL_WEDDING `0x10B2` (WM→Z) `{u32 Regist… | medium | cap 1/1; sup×1 (README §5.6) | re-read the rest (§3) |
| · 5.5 `FUN_005b92a0` after an accepted proposal (Z02 question) | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| 6. Mini-house (estate) | **low** | no function cited; sup×1 (README §5.6) | re-read the rest (§3) |
| · 6.1 Data | **low** | sup×1 (README §5.6); weak p171; ours×1 | re-read the rest (§3) |
| · 6.2 NC_MINIHOUSE_ACTIV_REQ `0x8C01` (C→Z) `{u8 slot}` @ FUN_005… | medium | the captured opcodes are only mentioned here (WM character-list opcodes); the subject of the section (0x8C01 mini-house activation) is in no capture (hand; baseline: high) | capture 0x8C01 |
| · 6.3 NC_MINIHOUSE_BUILDING_REQ `0x8C03` (C→Z) @ FUN_005769d0 | medium | cap 1/3 | capture 0x8C05 |
| · 6.4 NC_MINIHOUSE_LOGINCOMPLETE_REQ `0x8C0A` (C→Z, no payload) @… | medium | cap 0/11 | capture 0x8C08, 0x8C09, 0x8C0B, 0x8C0C … |
| · 6.5 Visiting | medium | cap 0/3 | capture 0x8C0F |
| · 6.6 Leaving and kicking | medium | cap 0/3 | capture (class U) |
| · 6.7 NC_MINIHOUSE_FUNITUREINFOCOMPLETE_REQ `0x8C1D` (C→Z) `{u8 f… | **low** | cap 0/1; sup×1 (README §5.6) | re-read the rest (§3) |
| · 6.8 Furniture and settings (owner only, `InHouseOwner` prefix) | medium | cap 0/18 | capture 0x8C21, 0x8C24, 0x8C27, 0x8C2D … |
| · 6.9 NC_MINIHOUSE_CHAR_ACTION_REQ `0x8C3D` (C→Z) `{u16 Handle, u… | **low** | cap 0/3; sup×1 (README §5.6) | re-read the rest (§3); capture 0x8C3E, 0x8C3F |
| · 6.10 NC_MINIHOUSE_FURNITURE_EFFECT_REQ `0x8C40` / PORTAL_EFFECT… | **low** | cap 0/6; sup×2 (README §5.6) | re-read the rest (§3); capture 0x8C41, 0x8C57 |
| · 6.11 Furniture emotions | medium | cap 0/6 | capture 0x8C63, 0x8C64, 0x8C66, 0x8C67 |
| · 6.12 Mini-house DB answers | medium | cap 0/5 | capture 0x8C4B |
| 7. Card collection (COLLECT, dept 49) | **low** | cap 3/21; sup×1 (README §5.6) | re-read the rest (§3); capture 0xC405, 0xC406, 0xC40B, 0xC40F … |
| 8. Mounts (MOVER, dept 51) | medium | cap 3/13 | capture 0x306A, 0x306C, 0x3070, 0xCC03 … |
| 9. Pets (PET, dept 53) | medium | cap 3/17 | capture 0xD408, 0xD40A, 0xD413 |
| 10. Other DB answers | – | container (see its subsections) |  |
| · 10.1 NC_CHAR_GET_ITEMLIST_BY_TYPE_ACK `0x1077` / _NUM_ACK `0x10… | medium | cap 1/3 | capture 0x302E |
| · 10.2 NC_CHAR_REGNUM_VARIFICATION_ACK `0x10B4` (DB→Z) @ FUN_0055… | medium | cap 1/1; sup×1 (README §5.6) | re-read the rest (§3) |
| 11. Production (answers Z02 §8) | **low** | cap 0/7; client×1; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x481D |
| Original-server bugs | **low** | cap 8/25; sup×1 (README §5.6); B×1; bug table (class X: effects are deductions) | re-read the rest (§3); follow the return value to the parser; capture 0x1125, 0xCC07 |
| 12. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.19 Z08: `zone/Z08-content.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Party mirror (WM → zone, dept 14) | – | container (see its subsections) |  |
| · 1.1 Data | medium | cap 0/1; ours×2 | capture 0x3832 |
| · 1.2 Party status broadcast (player tick) | **low** | cap 0/3; sup×1 (README §5.6) | re-read the rest (§3); capture 0x3832, 0x3833, 0x3849 |
| · 1.3 Handlers | medium | cap 0/13; weak inf1 | capture (class U) |
| 2. Raid mirror (WM → zone, dept 44) | medium | cap 0/18; weak p171 | capture 0xB020, 0xB021, 0xB022, 0xB023 … |
| 3. Quests (dept 17) | – | container (see its subsections) |  |
| · 3.1 Model | **low** | cap 5/11; client×1; sup×3 (README §5.6); weak p172 | re-read the rest (§3); capture 0x4412 |
| · 3.2 Client requests | medium | cap 0/15 | capture 0x4408, 0x440C, 0x4410, 0x4415 … |
| · 3.3 DB answers | medium | cap 1/9 | capture 0x4408, 0x4417 |
| · 3.4 Reset times (WM → zone) | **high** | cap 2/3 |  |
| 4. Kingdom quests (dept 22) | **low** | cap 3/12; sup×2 (README §5.6); weak p171; ours×1 | re-read the rest (§3); capture 0x5819 |
| 5. Instance dungeons (dept 41) and their NPC gates | **low** | no function cited; sup×1 (README §5.6) | re-read the rest (§3) |
| · 5.1 Model | medium | ours×2 | second reading / client check |
| · 5.2 Gate roles and menu callbacks (Z02 §6.5 open points) | – | open points / boundary list, no claim to rate |  |
| · 5.3 Level-select flow (ModeIDGate) | medium | cap 0/14 | capture 0x3C10, 0xA40C, 0xA418 |
| · 5.4 Leaving a group inside its dungeon | medium | cap 0/4; weak inf1; ours×1 | capture (class U) |
| 6. Friend points (dept 21) | medium | cap 0/4; client×1 | capture 0x5422 |
| 7. Weapon titles / licences (dept 23) and character titles (dep… | – | container (see its subsections) |  |
| · 7.1 Weapon licence | **low** | cap 0/11; client×1; sup×1 (README §5.6) | re-read the rest (§3); capture 0x5C02, 0x5C03 |
| · 7.2 Character titles | medium | cap 1/5 | capture 0x6002 |
| 8. Guild, guild war and guild tournament: zone side (dept 29) | medium | cap 1/1 | capture (class U) |
| · 8.1 Client requests | **low** | cap 1/24; sup×1 (README §5.6) | re-read the rest (§3); capture 0x7492, 0x749D, 0x74AD, 0x74B5 … |
| · 8.2 WM / DB messages | **low** | cap 2/24; sup×2 (README §5.3, §5.6) | re-read the rest (§3); capture 0x74D8 |
| 9. Holy promise (master / trainee, dept 37) | medium | cap 0/11 | capture 0x943D, 0x9441 |
| 10. Guild academy (dept 38) | **low** | cap 2/14; sup×1 (README §5.6) | re-read the rest (§3); capture 0x9820 |
| 11. Charged stat / skill-empower reset (dept 36, DB answers) | **high** | cap 6/10; cv ok |  |
| 12. Prison (dept 31, WM → zone) | **low** | cap 0/3; sup×2 (README §5.6) | re-read the rest (§3) |
| 13. GM events (dept 52, WM → zone) | medium | cap 0/2; ours×1 | capture (class U) |
| 14. Original-server bugs | medium | cap 3/30; weak inf1; bug table (class X: effects are deductions) | capture 0x3832, 0x4408, 0x5C02 |
| 15. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.20 Z09: `zone/Z09-world.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Main loop and global timers | – | container (see its subsections) |  |
| · 1.1 `ZoneServer::zs_mainthreadfunction` | medium | cap 1/2 | capture (class U) |
| · 1.2 Per-minute block (world time) | **high** | cap 1/1; cv ok; weak inf1 |  |
| · 1.3 Object routines | medium | read in code | second reading / client check |
| · 1.4 Other global containers | medium | read in code | second reading / client check |
| · 1.5 Session polling and reaping (network side of the tick) | medium | cv ok; sup×1 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 2. Player tick (`ShinePlayer::so_Routine`) | – | container (see its subsections) |  |
| · 2.1 Order of work | medium | cap 0/1; weak inf1 | capture 0x2453 |
| · 2.2 Region check on Elderine | medium | read in code | second reading / client check |
| · 2.3 Work done for a player in a game mode | medium | the captured opcodes are only mentioned here (0x2434, 0x243D); the subject of the section (the per-tick game-mode work: ride timer, mount hunger, pet reactions, title minute counters) is in no capture (hand; baseline: high) | a ride, a pet or a title counter in a capture |
| · 2.4 Status packets and per-minute player checks | medium | cap 3/3; cv ok; client×1; sup×1 (README §5.6) | re-read the rest (§3) |
| · 2.5 Client packets are handled inside the player tick | medium | read in code | second reading / client check |
| · 2.6 Script triggers held by the player | medium | read in code | second reading / client check |
| · 2.7 Player members used in this file *(pdb2016)* | medium | cap 1/1 | capture (class U) |
| 3. GM events (`gGMEventManager`, DAT_14d42940) | medium | cap 1/5 | capture 0x1010 |
| 4. Prison: the zone has no release timer | medium | cap 0/3 | capture 0x7C05 |
| 5. Mob object core (`ShineMob`, `ShineNPC`, `ShineBandit`) | – | container (see its subsections) |  |
| · 5.1 Mob data: `MobDataBox` (`mobdatabox` DAT_14d44a38) | medium | weak fh1 | second reading / client check |
| · 5.2 Mob members (offsets from the object start) | medium | cap 1/1 | capture (class U) |
| · 5.3 Spawn: `so_mob_Regenerate` and `so_mob_RegenComplete` | medium | cap 1/1; client×1 | capture (class U) |
| · 5.4 `ShineMob::so_Routine` (every tick) | **high** | cap 1/1; cv ok; client×1 |  |
| · 5.5 `ShineMobileObject::so_Routine`: the part before the cast (… | medium | read in code | second reading / client check |
| · 5.6 MobConditionServer: animation levels | medium | cap 0/1; client×1; weak p171 | capture 0x2076 |
| · 5.7 Placing the mob: `so_MapMarking` → `FieldMap::fm_Marking` | medium | read in code | second reading / client check |
| · 5.8 Small mob services | medium | cap 0/1; client×1; weak inf1 | capture 0x748D |
| · 5.9 `ShineNPC` and `NPCManager` | medium | the captured opcodes are only mentioned here (0x244A, 0x3004); the subject of the section (NPC object internals and the scheduled NPCs of 0x086A) is in no capture (hand; baseline: high) | capture 0x086A (event NPC schedule) |
| · 5.10 `ShineBandit` (scenario objects that switch between NPC an… | medium | cap 0/1; client×1 | capture 0x6C0B |
| 6. Mob AI 1: brain, target selectors, aggro, rescue | – | container (see its subsections) |  |
| · 6.1 Brain objects in the mob (`MobAggroManager` at +0x1fcc) | **low** | sup×1 (README §5.5); weak inf1; R×2 | re-read the rest (§3) |
| · 6.2 The aggro list | medium | weak inf2 | second reading / client check |
| · 6.3 Selecting a target (`mt_SelectTarget`, vt 0x28) | medium | read in code | second reading / client check |
| · · 6.3.1 Scan candidate test (`MobTargetSelector::ali_Work`, slot … | medium | read in code | second reading / client check |
| · 6.4 Top aggro (`so_mob_GetTopAggroTarget`, vt 0xc18) | medium | read in code | second reading / client check |
| · 6.5 Current target and battle state | medium | cap 1/1 | capture (class U) |
| · 6.6 Calling for help (`sm_Scream4Rescue`, `so_RescueRoutine`) | medium | read in code | second reading / client check |
| · 6.7 Target-type checks for mob weapons (`so_mob_CanMyTarget`, `… | medium | cap 0/1; weak inf2 | capture (class U) |
| · 6.8 Script and GM access to aggro and AI | medium | cap 0/1 | capture 0x244D |
| · 6.9 Not in this section | medium | read in code | second reading / client check |
| 7. Mob AI 2a: tactic state machine, weapons, attack sequences | – | container (see its subsections) |  |
| · 7.1 The tactic context and its states | medium | R×1 | second reading / client check |
| · 7.2 Idle states: Targetting, Wander, Roaming, going home | medium | weak inf1 | second reading / client check |
| · 7.3 Fighting states | **high** | cap 3/3 |  |
| · 7.4 Weapons: choosing and using | **high** | cap 2/4 |  |
| · 7.5 Weapon target by `MopAttackTarget` | medium | no function cited | cite and re-read the function |
| · 7.6 `MobAttackSequence`: scripted skill orders | medium | weak inf1 | second reading / client check |
| · 7.7 Captivated players | medium | cap 1/1 | capture (class U) |
| · 7.8 `so_attack` and `so_Bash` are dead code in 2016 | medium | R×1 | second reading / client check |
| · 7.9 Continued in §8 | medium | no function cited | cite and re-read the function |
| 8. Mob AI 2b: script control, chat, servant explosions, boss ho… | medium | cap 0/2 | capture 0x8004 |
| · 8.1 Skills ordered by scripts | medium | cap 1/2 | capture (class U) |
| · 8.2 Weapon rates set by scripts | medium | read in code | second reading / client check |
| · 8.3 Cross-counter (`so_smo_CrossCounterDamage`, vt 0x9ac) | medium | cap 1/1 | capture (class U) |
| · 8.4 Who may hit or heal whom (non-player classes) | medium | read in code | second reading / client check |
| · 8.5 `smo_SkillBlastTick` (vt 0xf14): delay between a skill's bl… | **high** | no opcode; the blast-to-effect delay `HitTime × 10 / 1000 − 2` tenths matches all four skills of batch 4 within one tick (Heat of Fury 1.32–1.39 s, Dash 0.36–0.41 s, Divine Shield 0.217 s, Revival 0.80 s; capture-validation §25.4) (hand; baseline: medium) |  |
| · 8.6 Mob chat (`MobChat::MobChatManager` `mobchatman`, DAT_0084c… | medium | cap 1/1; R×1 | capture (class U) |
| · 8.7 Mob shout and scripted mob chat | medium | the captured opcodes are only mentioned here (0x2002 / 0x201F of player chat and shout); the subject of the section (a mob shout or scripted mob chat) is in no capture (hand; baseline: high) | a shouting mob in a capture |
| · 8.8 Servant explosions (`MobExplosionElement`) | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 8.9 Boss-field hooks on mobs | medium | read in code | second reading / client check |
| · 8.10 `MobTargetPlayerCaptivate`: the target selector of a charm… | medium | read in code | second reading / client check |
| · 8.11 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 9. Movement, map blocks, path finding and sight | – | container (see its subsections) |  |
| · 9.1 `MoveManager` (obj+0x18c) | **high** | cap 2/3 |  |
| · 9.2 Block bitmaps and the per-class block checks | medium | the captured opcodes are only mentioned here (0x2013, 0x2021, 0x2025 of a free player); the subject of the section (a blocked stop, emote or jump) is in no capture (hand; baseline: high) | capture a jump / emote on a blocked cell |
| · 9.3 Server-driven moves | **high** | cap 5/9; cv ok; client×2 |  |
| · 9.4 `BlockDistribute`: random free spots | medium | read in code | second reading / client check |
| · 9.5 Mob paths: Navigator and MobRoam | **high** | cap 2/2 |  |
| · 9.6 Sight: how objects appear and disappear (answers Z02 §5) | medium | cap 3/3; cv ok; client×1; sup×1 (README §5.6); cv corr; weak p171 | re-read the rest (§3); read with P02 "Corrections" |
| · 9.7 Collision for placement | medium | read in code | second reading / client check |
| · 9.8 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 10. Spawns: MobHatchery, breeder groups, breeders, script spawn… | – | container (see its subsections) |  |
| · 10.1 Data files | medium | one client citation (`MobNoFadeInTab`) in a list of server data files (hand; baseline: high) | second reading |
| · 10.2 Objects | medium | read in code | second reading / client check |
| · 10.3 Loading the map's regen file | medium | weak inf1 | second reading / client check |
| · 10.4 The regen tick: `EventMobRegen` | medium | read in code | second reading / client check |
| · 10.5 `FamilyMobManagement::FamilyMobManager` (`g_FamilyMobManag… | medium | read in code | second reading / client check |
| · 10.6 Breeders created by scripts, Lua and GM commands | medium | read in code | second reading / client check |
| · 10.7 Direct spawns from Lua (`cMobRegen_*`) | medium | read in code | second reading / client check |
| · 10.8 `ScriptMobBreeder` (Pine `SysFunc` helpers) | medium | read in code | second reading / client check |
| · 10.9 GM view | medium | read in code | second reading / client check |
| · 10.10 Treasure chests: `MagicContainer` and `TreasureChestMaker` | medium | cap 0/3 | capture (class U) |
| · 10.11 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 11. Drops: mob drop tables, drop items, loot rights, party/raid… | medium | cap 1/2 | capture (class U) |
| · 11.1 Data files | medium | cap 0/1 | capture (class U) |
| · 11.2 The drop roll | **low** | cap 0/3; sup×3 (README §5.6); weak inf3 | re-read the rest (§3); code or capture for the marked statements; capture 0x202E |
| · 11.3 Creating the drop object | medium | cap 1/2; weak p171 | capture (class U) |
| · 11.4 `ShineDropItem` object and loot rights | **high** | cap 2/2; cv ok |  |
| · 11.5 Party / raid distribution (loot rule 1, and money) | medium | cap 0/1 | capture 0x301B |
| · 11.6 Dice game on a drop (loot rule 3) | medium | cap 5/12; client×1; weak inf2 | capture 0x303B, 0x303D, 0x303E, 0x303F |
| · 11.7 `DropLocationManager` (spiral placement) | medium | weak inf1 | second reading / client check |
| · 11.8 Other drop entry points (owned elsewhere) | **high** | cap 2/2 |  |
| · 11.9 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 12. Other world objects 1: magic fields and axial flags | medium | cap 1/1 | capture (class U) |
| · 12.1 `ShineMagicField` members (0x1c8 bytes) | medium | cap 0/1 | capture 0x1C0C |
| · 12.2 Who creates a field | medium | cap 1/1; weak fh1 | capture (class U) |
| · 12.3 Spreading: `so_mgcfld_MagicFieldSpread` (damage) and `…_Fr… | medium | cap 0/1 | capture 0x1C0C |
| · 12.4 The field tick: `ShineMagicField::so_Routine` (vt 0x4ac) | medium | cap 1/1 | capture (class U) |
| · 12.5 Damage, heal and aggro | medium | cap 1/1; weak inf1 | capture (class U) |
| · 12.6 Packets and the client | medium | the captured opcodes are only mentioned here (0x1805, the DoT damage 0x243C of batch 4); the subject of the section (magic fields and axial flags) is in no capture (hand; baseline: high) | a magic field on a map in a capture |
| · 12.7 `ShineAxialFlag`: the map anchors (0x188 bytes) | medium | read in code | second reading / client check |
| · 12.8 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 13. Other world objects 2: doors, effect objects, servants | – | container (see its subsections) |  |
| · 13.1 `ShineDoor` (kind 7, 0x1f14 bytes): script-built gates | medium | cap 2/5; weak p171 | capture 0x1C0F, 0x1C10, 0x6C09 |
| · 13.2 `ShineEffectObject` (kind 9, 0x1d3 bytes): a visual effect… | medium | cap 1/3; client×1; weak p171 fh1 | capture 0x1C11, 0x1C12 |
| · 13.3 `ShineServant` (kind 10, 0x2598 bytes): mobs summoned by a… | medium | the captured opcodes are only mentioned here (0x1805 object removal); the subject of the section (servants / summoned mobs) is in no capture (hand; baseline: high) | capture a summoning mob (0x243C) |
| · 13.4 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 14. Scripts 1: the Lua engine, script events, triggers, observe… | medium | read in code | second reading / client check |
| · 14.1 Script objects (`LuaScript`, 8 bytes) *(pdb2016)* | medium | weak inf1 | second reading / client check |
| · 14.2 Where the script objects come from | medium | read in code | second reading / client check |
| · 14.3 Script events: object events (`LuaAi`) and map events (`Lu… | medium | the captured opcodes are only mentioned here (0x1803, 0x200A); the subject of the section (Lua object and map events) is in no capture (hand; baseline: high) | a scripted map (KQ or instance) in a capture |
| · 14.4 Argument objects (`LuaScriptArgument::*`) *(pdb2016)* | medium | read in code | second reading / client check |
| · 14.5 Lua triggers (`LuaFuncTrigger`): chat, jump and item use n… | medium | the captured opcodes are only mentioned here (jump 0x2024 / 0x2025, emote 0x2020 / 0x2021 of batch 3); the subject of the section (Lua triggers on chat, jump, item use) is in no capture (hand; baseline: high) | a scripted map with a trigger in a capture |
| · 14.6 Lua functions of the script infrastructure | medium | cap 3/8; client×2 | capture 0x2074, 0x2075, 0x6C16, 0x6C21 … |
| · 14.7 The Lua observer (`g_LuaScriptObserver`, DAT_0087ef88) | medium | read in code | second reading / client check |
| · 14.8 Player observers (`Observer`, `IObserver`) *(pdb2016)* | medium | read in code | second reading / client check |
| · 14.9 The Lua function table (`LuaScriptScenario::ls_FuncSet` FU… | medium | weak fh2 | second reading / client check |
| · 14.10 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 15. Scripts 2: script interrupts and script areas | – | container (see its subsections) |  |
| · 15.1 Objects *(pdb2016)* | medium | read in code | second reading / client check |
| · 15.2 Setting an interrupt: Pine `interruptset` | medium | cap 0/2; R×1 | capture 0x6C05, 0x6C07 |
| · 15.3 Events: who raises them | medium | cap 1/3; weak inf1 | capture (class U) |
| · 15.4 Waiting: `waitinterrupt` and the per-kind checks | medium | cap 0/1 | capture 0x0810 |
| · 15.5 Removing interrupts | medium | read in code | second reading / client check |
| · 15.6 Unit interrupts: the registry and `WinGuild` | medium | read in code | second reading / client check |
| · 15.7 Script areas (`.aid`) and area queries | medium | cap 0/2; client×2 | capture (class U) |
| · 15.8 Answers to the open questions (Z02 §5 / §12 / §15) | – | open points / boundary list, no claim to rate |  |
| · 15.9 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 16. Scripts 3: NPCAction proximity triggers | – | container (see its subsections) |  |
| · 16.1 Data files and loading | medium | read in code | second reading / client check |
| · 16.2 Objects *(pdb2016)* | medium | read in code | second reading / client check |
| · 16.3 Running the triggers | medium | read in code | second reading / client check |
| · 16.4 Conditions | medium | R×2 | second reading / client check |
| · 16.5 Actions | medium | the captured opcodes are only mentioned here (0x2011 / 0x2013 / 0x201C); the subject of the section (script actions of an NPC role) is in no capture (hand; baseline: high) | a scripted NPC in a capture |
| · 16.6 Damage absorption (`DmgAbsorb`) | medium | the captured opcodes are only mentioned here (0x2448 / 0x2449 swings); the subject of the section (damage absorption) is in no capture (hand; baseline: high) | capture a swing against an absorb abstate |
| · 16.7 What the 2016 data uses | medium | no function cited | cite and re-read the function |
| · 16.8 Answers to open questions | – | open points / boundary list, no claim to rate |  |
| · 16.9 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 17. Scripts 4: Lua functions that control objects | medium | weak fh1 | second reading / client check |
| · 17.1 Moving objects | medium | the captured opcodes are only mentioned here (0x2018 / 0x201A mob moves); the subject of the section (Lua move functions) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 17.2 Animations, actions, visibility | medium | cap 0/8; client×1 | capture 0x0810, 0x2074, 0x2075, 0x207C … |
| · 17.3 Damage, healing, killing, revival | medium | the captured opcodes are only mentioned here (0x243C / 0x244A of batch 4); the subject of the section (the Lua damage, heal, kill and revive functions) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 17.4 Abnormal states | medium | cap 0/2 | capture 0x10AF |
| · 17.5 Mob and NPC settings | medium | cap 1/1; weak fh1 | capture (class U) |
| · 17.6 Map rules | medium | cap 2/6; client×1 | capture 0x1812, 0x1813, 0x1828, 0x1829 |
| · 17.7 Moving players between maps, parties | medium | cap 0/3 | capture 0x202C |
| · 17.8 Player items, money, stats, titles, equipment view | medium | cap 1/4 | capture (class U) |
| · 17.9 Answers and open points | – | open points / boundary list, no claim to rate |  |
| 18. Scripts 5: Lua functions that query objects, maps and lists | medium | weak fh1 | second reading / client check |
| · 18.1 Time and random numbers | medium | cap 0/1 | capture (class U) |
| · 18.2 Object state | medium | weak fh1 | second reading / client check |
| · 18.3 Positions, maps and areas | medium | read in code | second reading / client check |
| · 18.4 Items and script strings | medium | read in code | second reading / client check |
| · 18.5 Searches and lists | medium | read in code | second reading / client check |
| · 18.6 Effects, sounds and map marks (client packets) | medium | cap 0/3; client×1 | capture 0x207A, 0x207B, 0x6C17 |
| · 18.7 Answers and open points | – | open points / boundary list, no claim to rate |  |
| 19. Scripts 6: Lua functions for messages, dialogs and screen e… | **high** | cap 2/3; weak fh1 |  |
| · 19.1 Script messages from `ScriptMsg.shn` | medium | cap 2/5; client×2 | capture 0x6C11, 0x6C12, 0x6C15 |
| · 19.2 Dialog windows and face cuts | medium | cap 0/2; client×1 | capture 0x6C0C, 0x6C19 |
| · 19.3 Notices, system messages, NPC chat and shouts | medium | the captured opcodes are only mentioned here (0x2011, 0x201F, 0x2020 / 0x2021 from players); the subject of the section (the Lua notice, system-message, NPC chat and shout functions) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 19.4 Camera, top view, fog | medium | cap 0/3; client×1 | capture 0x6C0E, 0x6C14, 0x6C1A |
| · 19.5 Screen effects, timers, sounds, emotions, NPC menu | **low** | cap 4/14; client×1; sup×1 (README §5.6); weak inf1 p172 fh1 | re-read the rest (§3); code or capture for the marked statements; capture 0x2077, 0x2078, 0x2082, 0x2083 … |
| · 19.6 Answers and open points | – | open points / boundary list, no claim to rate |  |
| 20. Scripts 7: the Pine map-script language 1 — files, tokens, … | – | container (see its subsections) |  |
| · 20.1 Files | medium | read in code | second reading / client check |
| · 20.2 Reading a file: `PineEventScript::pes_Load` | medium | read in code | second reading / client check |
| · 20.3 Characters and tokens: `PineScriptReader` | medium | read in code | second reading / client check |
| · 20.4 Values and numbers | medium | no function cited | cite and re-read the function |
| · 20.5 Expressions: `Express`, `Term`, `Identify`, atoms | medium | weak inf1 | second reading / client check |
| · 20.6 Variables and the process stack: `PineScriptStack` | medium | R×1 | second reading / client check |
| · 20.7 `ScriptParameterPaser`: typed arguments for four nodes | medium | read in code | second reading / client check |
| · 20.8 Logging | medium | read in code | second reading / client check |
| · 20.9 Open points of this section | – | open points / boundary list, no claim to rate |  |
| 21. Scripts 8: the Pine map-script language 2 — statements, blo… | – | container (see its subsections) |  |
| · 21.1 Grammar of a script file | medium | no function cited | cite and re-read the function |
| · 21.2 The statement registry: `ps_statementlist` | medium | R×1 | second reading / client check |
| · 21.3 Blocks and the script | medium | read in code | second reading / client check |
| · 21.4 How a film runs | medium | read in code | second reading / client check |
| · 21.5 Control statements | medium | read in code | second reading / client check |
| · 21.6 Conditions and `@` system functions | medium | read in code | second reading / client check |
| · 21.7 The 2016 scripts against this grammar | medium | no function cited | cite and re-read the function |
| · 21.8 Answers to §20.9 and open points | – | open points / boundary list, no claim to rate |  |
| 22. Scripts 9: Pine action statements (base), `@` system functi… | medium | cap 0/3 | capture 0x5814, 0x5821, 0x6C04 |
| · 22.1 `OtherStatement`: the action-statement base | medium | read in code | second reading / client check |
| · 22.2 `@` system functions | medium | weak inf1 | second reading / client check |
| · 22.3 KQ score lists: `@KQResultList`, `@KQTopList` and 0x5814 /… | medium | cap 0/2; client×1 | capture 0x5814, 0x5821 |
| · 22.4 The nine `ScriptBase<>` statements | medium | cap 3/7; weak inf1 | capture 0x2023, 0x6C04 |
| · 22.5 The scenario book shelf | medium | read in code | second reading / client check |
| · 22.6 Dialog-string files: `KQScriptManager` and `ShineScript` | medium | read in code | second reading / client check |
| · 22.7 Answers to open questions and open points | – | open points / boundary list, no claim to rate |  |
| 23. Scripts 10: Pine action nodes A–C (abstates, aggro, animati… | medium | cap 3/12 | capture 0x1812, 0x1813, 0x6C0B, 0x6C0C … |
| · 23.1 Common shape | medium | read in code | second reading / client check |
| · 23.2 Changing an object's kind: `change2mob`, `change2npc`, `ch… | medium | cap 0/1; weak inf1 | capture 0x6C0B |
| · 23.3 Abnormal states: `abstateset`, `abstatereset` | medium | read in code | second reading / client check |
| · 23.4 Mobs and animation: `aggro`, `animate` | medium | cap 0/1; client×1 | capture 0x6C0D |
| · 23.5 Messages: `broadcast`, `chatwin`, `chatwinrange`, `briefef… | medium | cap 1/3; client×1 | capture 0x6C0C, 0x6C10 |
| · 23.6 Map battle modes: `battlestart`, `battlestop` | medium | cap 0/5; client×2 | capture 0x1812, 0x1813, 0x7483, 0x7484 … |
| · 23.7 Banning players from an area: `banfromarea` | medium | read in code | second reading / client check |
| · 23.8 Costumes: `costumecreate`, `costumetakeoff` | medium | the captured opcodes are only mentioned here (0x3401 of `&makeitem`, 0x3459 of the destroy); the subject of the section (Lua `costumecreate` / `costumetakeoff`) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 23.9 2016 use, answers and open points | – | open points / boundary list, no claim to rate |  |
| 24. Scripts 11: Pine action nodes D–I (items, drops, finding ob… | medium | cap 4/9 | capture 0x5812, 0x5813, 0x74D2, 0x74E2 |
| · 24.1 Script drops: `itemdrop` | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 24.2 Player items: `itemcreate`, `itemerase`, `itemattrset` | medium | the captured opcodes are only mentioned here (0x3449 / 0x344A of the ride item save); the subject of the section (Lua `itemcreate` / `itemerase`) is in no capture (hand; baseline: high) | a script that gives an item, in a capture |
| · 24.3 Searching inventories: `invensearch`, `itemowner` | medium | read in code | second reading / client check |
| · 24.4 Finding objects and players: `findhandle`, `findplayer` | medium | read in code | second reading / client check |
| · 24.5 Replacing and copying objects: `exchange2mob`, `duplicate` | medium | read in code | second reading / client check |
| · 24.6 HP and death counts: `heal`, `hpset`, `deathcountclear` | medium | weak inf1 | second reading / client check |
| · 24.7 KQ rewards: `invidualreward` | medium | read in code | second reading / client check |
| · 24.8 Guild-tournament end: `gtresult`, `endofgt`, `DiceGameStar… | medium | cap 0/5; client×3; R×1 | capture 0x5812, 0x5813, 0x74D2, 0x74E2 |
| · 24.9 2016 use, answers and open points | – | open points / boundary list, no claim to rate |  |
| 25. Scripts 12: Pine action nodes L–R (spawns, NPC talk, map li… | medium | cap 3/10 | capture 0x204D, 0x5812, 0x5813, 0x5823 … |
| · 25.1 Spawning and removing objects: `mobregen`, `npcstand`, `re… | medium | read in code | second reading / client check |
| · 25.2 Mob settings and scripted moves: `mobattr`, `mobdetectrang… | medium | the captured opcodes are only mentioned here (0x2018 / 0x201A / 0x203E); the subject of the section (Lua mob settings) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 25.3 NPC talk, map light and fog: `npcchat`, `npcshout`, `mapli… | medium | the captured opcodes are only mentioned here (0x2002 / 0x201F of player chat and shout); the subject of the section (`npcchat`, `npcshout`, `maplight`, fog) is in no capture (hand; baseline: high) | a scripted map in a capture |
| · 25.4 Sending players to other maps: `linkto`, `collect` | medium | read in code | second reading / client check |
| · 25.5 Waiting and tracing: `pause`, `printf` | medium | read in code | second reading / client check |
| · 25.6 KQ results and rewards: `questresult`, `reward`, `questmob… | medium | cap 0/4; client×2 | capture 0x5812, 0x5813, 0x5823 |
| · 25.7 Guild-tournament flags and gates: `RegisteFlag`, `RegisteG… | medium | read in code | second reading / client check |
| · 25.8 2016 use, answers and open points | – | open points / boundary list, no claim to rate |  |
| 26. Scripts 13: Pine action nodes S–W and `endofkq` (KQ end, sc… | medium | cap 3/8 | capture 0x0810, 0x5812, 0x5813 |
| · 26.1 KQ end and results: `endofkq`, `sendquestresult`, `scinari… | medium | cap 1/5 | capture 0x5812, 0x5813 |
| · 26.2 Dialog files and shouts: `scriptfile`, `someoneshout` | medium | cap 1/1 | capture (class U) |
| · 26.3 Summoning mobs and starting films: `summonmob`, `spawn` | medium | read in code | second reading / client check |
| · 26.4 Killing and moving objects: `suicide`, `teleport`, `telepo… | medium | the captured opcodes are only mentioned here (0x1805, 0x243C); the subject of the section (the Pine nodes suicide / teleport) is in no capture (hand; baseline: high) | a KQ played in a capture (scenario 31) |
| · 26.5 Time limits and waits: `timelimit`, `waitlogin`, `waitidle` | medium | cap 0/1; weak p171 | capture 0x0810 |
| · 26.6 Who clicked, who killed: `whoclickme`, `whokillme` | medium | read in code | second reading / client check |
| · 26.7 Wedding: `weddingcomplete` | medium | cap 0/2 | capture (class U) |
| · 26.8 2016 use, answers and open points | – | open points / boundary list, no claim to rate |  |
| 27. Scripts 14: films (`Movie::*`) and the boss-field tables (`… | – | container (see its subsections) |  |
| · 27.1 Objects | medium | read in code | second reading / client check |
| · 27.2 Starting a film | medium | read in code | second reading / client check |
| · 27.3 Running and stopping films | medium | read in code | second reading / client check |
| · 27.4 Time limits (`Movie::TimeLimit`, Pine `timelimit`) | medium | cap 0/1 | capture 0x0810 |
| · 27.5 Who starts and stops films | medium | read in code | second reading / client check |
| · 27.6 Boss-field tables (`BossFieldContent`) | medium | the captured opcodes are only mentioned here (0x0821, 0x3016); the subject of the section (boss-field tables) is in no capture (hand; baseline: high) | a boss field in a capture |
| · 27.7 Answers and open points | – | open points / boundary list, no claim to rate |  |
| 28. Sweep additions: map query functions, heal reports, the res… | – | container (see its subsections) |  |
| · 28.1 Map initialisation and the query functions per map kind | medium | read in code | second reading / client check |
| · 28.2 Heal reports: how mobs learn who healed their enemy (`SpyN… | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 28.3 The rest of `World/MiscDataTable.txt`: Polymorph, Neutrali… | medium | cap 0/1; cv ok | capture 0x10AF |
| · 28.4 Answers to the leftovers marked "sweep" | medium | cap 0/2 | capture (class U) |
| · 28.5 Small helpers reached from documented code | medium | read in code | second reading / client check |
| · 28.6 `OptionReader`: the `#`-command text tables | medium | read in code | second reading / client check |
| · 28.7 `CFindWay`: the old path finder is dead in 2016 | medium | R×2 | second reading / client check |
| · 28.8 Methods of the Z09 classes reached only through vtables | medium | the captured opcodes are only mentioned here (0x1C06 / 0x1C08 appear packets); the subject of the section (the vtable-only methods listed) is in no capture (hand; baseline: high) | second reading |
| · 28.9 Data files and opcodes against this file | medium | cap 1/9 | capture 0x1059, 0x105A, 0x2442, 0x2443 … |
| · 28.10 Last Z09 helpers of the gap list (part 17d) | medium | weak inf2; R×1 | second reading / client check |
| · 28.11 The game's own container and vector templates | medium | read in code | second reading / client check |
| · 28.12 Score boards, rankings, the instance-dungeon rank and the… | **low** | cap 1/8; client×4; sup×1 (README §5.6); cv corr; weak fh1; R×1 | re-read the rest (§3); read with P02 "Corrections"; capture 0x5814, 0x5821, 0x5836, 0x583C … |
| · 28.13 Small leftovers of finished items: capsule creation, clas… | medium | cap 3/14; client×2 | capture 0x1059, 0x105A, 0x1116 |
| 29. Original-server bugs (decide for a rebuild) | – | container (see its subsections) |  |
| · 29.1 Objects, mob core, AI, movement, spawns, drops (parts 1–7,… | **low** | cap 0/1; weak inf4 | code or capture for the marked statements; capture 0x2049 |
| · 29.2 World objects and script infrastructure (parts 8a–9c) | medium | bug table (class X); the captured opcodes are only mentioned here (0x1805, 0x2011, 0x243C, 0x2449); the world objects and the script infrastructure are in no capture (hand; baseline: high) | a scripted map / KQ in a capture |
| · 29.3 Lua C functions (parts 10–12) | medium | cap 0/4 | capture 0x207A, 0x6C11, 0x6C12, 0x6C15 |
| · 29.4 Pine engine (parts 14a–14c) | medium | weak inf1 | second reading / client check |
| · 29.5 Pine action nodes, films, sweep (parts 15a–17d) | medium | cap 0/6; weak inf2 | capture 0x0810, 0x202E, 0x7483, 0x74E2 |
| 30. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| · 30.1 Answered in this part | medium | read in code | second reading / client check |
| · 30.2 Main loop, player tick, mob core (§1, §2, §5) | medium | read in code | second reading / client check |
| · 30.3 Spawns and drops (§10, §11) | medium | cap 0/1; weak inf1 | capture (class U) |
| · 30.4 Movement, sight, world objects (§9, §12, §13, §27) | medium | cap 1/2 | capture 0x2049 |
| · 30.5 Script infrastructure and Lua functions (§14–§19) | medium | cap 1/4 | capture 0x2074, 0xA412 |
| · 30.6 Pine engine and action nodes (§20–§26) | medium | read in code | second reading / client check |
| · 30.7 Not reconstructed on purpose | – | open points / boundary list, no claim to rate |  |
| 31. Coverage boundary | – | open points / boundary list, no claim to rate |  |
| · 31.1 How the boundary was checked | medium | cap 0/2 | capture 0x2442, 0x2443 |
| · 31.2 Functions of other items | **low** | cap 1/3; sup×1 (README §5.6) | re-read the rest (§3); capture 0x440D |
| · 31.3 Packets and data files | **low** | cap 0/4; sup×1 (README §5.6) | re-read the rest (§3); capture 0x2442, 0x2443, 0x74F2, 0x8C4F |
| · 31.4 Library code | medium | no function cited | cite and re-read the function |
| · 31.5 Things named in earlier sections | medium | no function cited; weak fh1 | cite and re-read the function |

### 2.21 Z10: `zone/Z10-certification.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Overview | **low** | sup×1 (README §5.4) | re-read the rest (§3) |
| · 1.1 Process entry: WinMain, zs_start and the Windows service | medium | read in code | second reading / client check |
| 2. Fetching the script | – | container (see its subsections) |  |
| · 2.1 zs_start_old | medium | weak inf1 | second reading / client check |
| · 2.2 zs_LuaFromHTML | medium | read in code | second reading / client check |
| · 2.3 HTTP request (CHttpConnect over WinINet) | medium | weak inf1 | second reading / client check |
| · 2.4 Answer format and header checks | medium | no function cited | cite and re-read the function |
| · 2.5 Registry keys | medium | no function cited; weak inf1 | cite and re-read the function |
| · 2.6 Failure paths | medium | no function cited; R×1 | cite and re-read the function |
| 3. Cipher | – | container (see its subsections) |  |
| · 3.1 hs_Decoding: RSA blocks | medium | weak inf1 | second reading / client check |
| · 3.2 hs_Expand: LZ ring decompression | medium | read in code | second reading / client check |
| · 3.3 Test vectors (GamigoZR answer, keys of GBO.reg) | medium | no function cited | cite and re-read the function |
| · 3.4 Reference implementation (Python, tested on the GamigoZR an… | medium | no function cited | cite and re-read the function |
| 4. The replacement answer: GamigoZR | – | container (see its subsections) |  |
| · 4.1 The service (from its IL) | medium | no function cited | cite and re-read the function |
| · 4.2 The answer and the recovered script | medium | no function cited; weak inf1 | cite and re-read the function |
| · 4.3 What the script does | medium | no function cited | cite and re-read the function |
| 5. Lua host | – | container (see its subsections) |  |
| · 5.1 LuaScript / LuaScriptSecurity | medium | read in code | second reading / client check |
| · 5.2 Registered C functions (`LuaScriptSecurity::ls_FuncSet` FUN… | medium | read in code | second reading / client check |
| · 5.3 Shared state | medium | no function cited | cite and re-read the function |
| · 5.4 Movement speed factors and the 0x0830 server parameters | medium | the captured opcodes are only mentioned here (0x203E speed); the subject of the section (the 0x0830 speed-hack check) is in no capture (hand; baseline: high) | capture 0x0830 (custom client or a lagging one) |
| 6. Threads and the run-time certification | medium | read in code | second reading / client check |
| · 6.1 Main thread: the per-minute certification counter | medium | cap 1/1 | capture (class U) |
| · 6.2 Certification thread | medium | read in code | second reading / client check |
| · 6.3 The combat factor `lsf_Factor` | medium | read in code | second reading / client check |
| · 6.4 Stack checker thread (watchdog) | medium | read in code | second reading / client check |
| · 6.5 The other service stages | medium | R×1 | second reading / client check |
| · 6.6 What happens when the certification fails at run time | medium | read in code | second reading / client check |
| 7. Start stages and their order | – | container (see its subsections) |  |
| · 7.1 The stages, in script order | medium | weak inf1 | second reading / client check |
| · 7.2 Dependencies between the stages | **low** | no function cited; weak inf5 | code or capture for the marked statements |
| 8. 2015 zone: same mechanism | medium | no function cited | cite and re-read the function |
| 9. Recommendation for a rebuild | medium | no function cited | cite and re-read the function |
| Original-server bugs | **low** | sup×1 (README §5.6); weak inf1; bug table (class X: effects are deductions) | re-read the rest (§3) |
| 10. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 11. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.22 Z11: `zone/Z11-gm-commands.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The command system | – | container (see its subsections) |  |
| · 1.1 Entry: chat line → command  (registered nowhere; called fro… | **high** | cap 2/2 |  |
| · 1.2 Parsing: `ListIter_AmpCmdArgument` | medium | read in code | second reading / client check |
| · 1.3 The command table `ampcmd` (DAT_0087c770) | medium | cap 0/1 | capture (class U) |
| · 1.4 Admin levels | medium | cap 2/2; sup×1 (README §5.7); weak fh1 | re-read the rest (§3) |
| · 1.5 Replies and the command log | medium | cap 1/1 | capture (class U) |
| · 1.6 Helpers | medium | read in code | second reading / client check |
| 2. All commands | medium | cap 32/81; B×3 | capture 0x0810, 0x0867, 0x1812, 0x1813 … |
| 3. Commands, part 1 (handlers FUN_004194f0 … FUN_0041b030) | medium | read in code | second reading / client check |
| · 3.1 Visibility, layers and teleports | **low** | cap 1/1; sup×3 (README §5.6); cv corr; weak inf2 fh1 | re-read the rest (§3); read with P02 "Corrections"; code or capture for the marked statements |
| · 3.2 Information | medium | read in code | second reading / client check |
| · 3.3 Map, script and instance tools | medium | cap 1/2; weak fh1 | capture 0x0810 |
| · 3.4 Debug wrappers around other handlers | **low** | README §5.6 row; 0x304A is captured from the client's own auto-arrange (capture-validation §24.8), not from a debug wrapper; `&queststart` / `&questread` / `&viewaggrolist` are in no capture (hand; baseline: medium) | the wrapper commands in a capture |
| · 3.5 GM chat colour | medium | the captured opcodes are only mentioned here (0x1030 / 0x2002 of a normal chat); the subject of the section (the GM colour request 0x083D) is in no capture (hand; baseline: high) | capture 0x083D (GM command, part 8) |
| · 3.6 Words that do nothing | medium | weak inf1 fh1 | second reading / client check |
| 4. Commands, part 2 (handlers FUN_0041b1f0 … FUN_0041cec0) | medium | read in code | second reading / client check |
| · 4.1 Gates and doors: `&oxblock`, `&templink` | medium | cap 0/1; weak inf1 fh1 | capture 0x6C09 |
| · 4.2 Mobs: `&mobbreed`, `&mb` | medium | captured: `&mobbreed` and `&mb` in s45 (the wall "Mob : 5989", capture-validation §27.6), and the capture corrected the section (the value is the zone's mob count, not the mob ID; §13 -> X08): a captured section in which a class applies (hand; baseline: low) | re-read the rest (§3); read with P02 "Corrections" |
| · 4.3 Items: `&makeitem`, `&cleariv` | **high** | cap 4/4; weak inf3 |  |
| · 4.4 Character state: `&fullpoint`, `&sethp`, `&setsp`, `&learns… | medium | cap 6/8; sup×2 (README §5.6); cv corr; weak inf2 | re-read the rest (§3); read with P02 "Corrections"; capture 0x4805 |
| · 4.5 Players and information | medium | cap 1/3; cv ok; cv corr; weak inf1 | read with P02 "Corrections" |
| · 4.6 Empty quest and cool-time words | medium | read in code | second reading / client check |
| 5. Commands, part 3 (handlers FUN_0041cf90 … FUN_0041e880) | medium | read in code | second reading / client check |
| · 5.1 Finding and summoning: `&mfind`, `&pfind`, `&psummon` | medium | cap 1/3; weak fh1 | capture (class U) |
| · 5.2 Mob tools: `&mobdist`, `&killallmob`, `&suicideallmob`, `&s… | **low** | weak markers (inferred 1, fh-doc 2); 0x2011 is the answer to the invalid `&resetabstated` and 0x243C the poison damage of batch 4 (capture-validation §25.6, §25.7); no mob tool was used (hand; baseline: medium) | capture `&mobdist`, `&killallmob`, `&suicideallmob` |
| · 5.3 Combat debug: `&deathaura`, `&immortal`, `&staticdamage`, `… | medium | read in code | second reading / client check |
| · 5.4 Bonus events: `&expbonus`, `&itembonus`, `&fieldbonus` | medium | cap 0/2 | capture (class U) |
| · 5.5 Server and map tools | medium | cap 0/2 | capture (class U) |
| · 5.6 Player tools: `&horsespeed`, `&enterminihouse`, `&silence`,… | medium | cap 0/1; weak inf1 | capture (class U) |
| · 5.7 Information: `&charinform`, `&partyinfo`, `&루아인수`, `&parame… | medium | cap 1/1 | capture (class U) |
| 6. Commands, part 4 (handlers FUN_0041e9d0 … FUN_00420d30) | medium | read in code | second reading / client check |
| · 6.1 Wedding: `&propose`, `&proposeres`, `&weddingreset`, `&rese… | medium | cap 0/14; weak inf1 dbb1 | capture 0x2050, 0x2052, 0x2057 |
| · 6.2 Skills: `&unlearn`, `&unlearnpassive`, `&learnpassive` | medium | cap 3/8 | capture 0x4827 |
| · 6.3 Guild tournament: `&startGT`, `&flagcapture`, `&useguildski… | medium | cap 1/11; weak inf1 | capture 0x74CB, 0x74D0, 0x74D1, 0x74D8 |
| · 6.4 Character and combat: `&speed`, `&runto`, `&allcritical`, `… | medium | cap 1/1; weak inf1 | capture (class U) |
| · 6.5 Map tools: `&showid`, `&pvp`, `&ghostremove`, `&partblock`,… | medium | cap 0/2; weak inf1 | capture 0x1812, 0x1813 |
| · 6.6 Information and logs: `&curtime`, `&amibusy`, `&invenview`,… | medium | read in code | second reading / client check |
| · 6.7 Dice: `&ts_DiceFix`, `&ts_DiceProbability`, `&GB_DiceFix`, … | medium | read in code | second reading / client check |
| 7. Commands, part 5 (handlers FUN_00420ef0 … FUN_00422a90) | medium | read in code | second reading / client check |
| · 7.1 Raid tests: `&makeraid`, `&outraid` | medium | cap 0/1 | capture (class U) |
| · 7.2 Instance, link and tournament tests: `&PlayIns`, `&testlink… | medium | cap 1/10 | capture 0x181F, 0x1820, 0x2028, 0x2029 … |
| · 7.3 Skills and level: `&alllearnskill`, `&levelup` | **high** | cap 11/14; cv ok; weak inf2 |  |
| · 7.4 Items and money: `&getmoney`, `&iareset`, `&ebcu`, `&vanish… | medium | cap 6/11; cv ok; client×1; cv corr; weak inf1 | read with P02 "Corrections"; capture 0x3049 |
| · 7.5 NPC tools: `&fnpc`, `&RegenNPC`, `&ReleaseNPC` | medium | weak inf1 | second reading / client check |
| · 7.6 Character and movement: `&godmode`, `&setlp`, `&walkto`, `&… | medium | cap 0/2 | capture 0x6C14, 0xBC1C |
| · 7.7 Chat ban and pets: `&releasechatban`, `&getpetinfo`, `&setp… | medium | cap 0/7; weak inf1 | capture 0x0867 |
| 8. Commands, part 6 (handlers FUN_00422f90 … FUN_00425290) | medium | read in code | second reading / client check |
| · 8.1 Statistics: `&distribute`, `&showallchar`, `&fieldmobcount` | medium | cap 1/1 | capture (class U) |
| · 8.2 NPC and raid tests: `&npcrevive`, `&inraid` | medium | read in code | second reading / client check |
| · 8.3 Abnormal state: `&resetabstatetarget` | medium | cap 1/1 | capture (class U) |
| · 8.4 Kingdom quest: `&kqreward`, `&kingdomquest`, `&bigbang` | medium | cap 2/5; weak inf1 p171 | capture (class U) |
| · 8.5 Character tests: `&HP`, `&SP`, `&gmtestmode`, `&captivate`,… | medium | the captured opcodes are only mentioned here (0x2452 / 0x4821); the subject of the section (`&HP`, `&SP`, `&gmtestmode`) is in no capture (hand; baseline: high) | capture the commands (part 8) |
| · 8.6 Reloads: `&reloaddata`, `&reloadpetlua` | medium | weak inf1 | second reading / client check |
| · 8.7 Helpers in this address range | medium | read in code | second reading / client check |
| 9. Helpers reached by the commands (sweep) | – | container (see its subsections) |  |
| · 9.1 Parser and command list | medium | read in code | second reading / client check |
| · 9.2 Object, map and quest lookups | medium | read in code | second reading / client check |
| · 9.3 Skills, inventory and items | medium | weak inf1 | second reading / client check |
| · 9.4 Raid, party and save helpers | medium | cap 1/1 | capture (class U) |
| Original-server bugs | medium | cap 6/17; client×1; weak inf3; R×1; bug table (class X: effects are deductions) | capture 0x181F, 0x2052, 0x6C14 |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.23 Z12: `zone/Z12-stats.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The stat matrix (`Parameter::Container`) | – | container (see its subsections) |  |
| · 1.1 Layout | medium | cap 0/1 | capture (class U) |
| · 1.2 Erasers and clearing | medium | read in code | second reading / client check |
| · 1.3 `Parameter::Container::c_MakeTotal` @ FUN_004c9a40 (the Tot… | medium | read in code | second reading / client check |
| · 1.4 `so_allparametercalculate` (vt 0x57c) @ FUN_0054f190 and wh… | medium | read in code | second reading / client check |
| 2. The layer sources | – | container (see its subsections) |  |
| · 2.1 `PureCharParam` (layer 0): class tables and `c_Storepure` @… | medium | read in code | second reading / client check |
| · 2.2 Equipment: `so_RecalcEquipParam` (vt 0x35c) @ FUN_004cab70 | medium | read in code | second reading / client check |
| · 2.3 Weapon title: `smo_ply_WeaponTitleSet` (vt 0xec8) @ FUN_005… | medium | read in code | second reading / client check |
| · 2.4 Passive skills: `so_RecalcPassiveParam` (vt 0x364) @ FUN_00… | medium | cap 0/1; weak inf1 | capture 0x10DF |
| · 2.5 Abnormal states: `so_RecalcAbstateParam` (vt 0x360) @ FUN_0… | **low** | sup×1 (README §5.5) | re-read the rest (§3) |
| · 2.6 `LastTune` (layers 13, 14): `so_RecalcLastParam` (vt 0x368)… | medium | read in code | second reading / client check |
| · 2.7 Summary: which source feeds which cell | medium | no function cited | cite and re-read the function |
| 3. Maxima: HP, SP, LP and the soul-stone stock | – | container (see its subsections) |  |
| · 3.1 Class slots | medium | R×1 | second reading / client check |
| · 3.2 `ShinePlayer::sp_MaxHP` @ FUN_0054a670 and `sp_MaxSP` @ FUN… | medium | read in code | second reading / client check |
| · 3.3 LP (Sentinel / Savior): `so_ply_Sen_MaxLP` (vt 0xd94) @ FUN… | medium | 0x1035 / 0x245F are captured as parameter pushes of other classes; no capture is known to contain a Sentinel or Savior (hand; baseline: high) | capture with a Sentinel character |
| · 3.4 Soul-stone stock maxima | medium | weak inf1 | second reading / client check |
| 4. The refresh: `so_mobile_NotifyParameterChange` (vt 0x34) @ F… | medium | read in code | second reading / client check |
| · 4.1 Free-stat bonus rows (`ChrCommon.txt`, Z10 §5.4) | medium | cap 1/1 | capture (class U) |
| · 4.2 The notify | **high** | cap 2/3; R×1 |  |
| · 4.3 Packets | **high** | cap 3/4; client×1; R×1 |  |
| 5. Level and experience | – | container (see its subsections) |  |
| · 5.1 Tables (`ChrCommon.txt`, loader Z10 §5.4) | medium | read in code | second reading / client check |
| · 5.2 Level-up side effects (completing Z03 §8.3) | **high** | cap 6/6; client×1 |  |
| · 5.3 `sp_NextSaveExperience` @ FUN_0042d6f0 | medium | cap 1/1 | capture (class U) |
| · 5.4 Rest-exp buff: `RestExpCalculate::RestExpAbstateApplication… | medium | read in code | second reading / client check |
| 6. Login data parsing (WM → zone character blobs) | medium | cap 1/1 | capture (class U) |
| · 6.1 Summary | **high** | cap 30/34; R×1 |  |
| · 6.2 Base and shape | **high** | cap 2/2; client×1 |  |
| · 6.3 Quests | **high** | cap 4/4; client×1; R×1 |  |
| · 6.4 Abnormal states | **low** | cap 1/2; client×1; sup×1 (README §5.5) | re-read the rest (§3); capture 0x103C |
| · 6.5 Skills | medium | cap 1/1; client×1; R×1 | capture (class U) |
| · 6.6 Passives | medium | cap 1/1; client×1 | capture (class U) |
| · 6.7 Inventory | medium | cap 1/1; client×1 | capture (class U) |
| · 6.8 Chest locations, game data, charged buffs | medium | cap 4/4; client×1; sup×1 (README §5.5) | re-read the rest (§3) |
| · 6.9 End of data: `so_StoreCharData` (vt 0x4b4) and `sp_LoginIni… | medium | cap 1/1; weak inf1 | capture (class U) |
| 7. Single options, link-from position, title refresh (Z07 §12 o… | – | open points / boundary list, no claim to rate |  |
| · 7.1 NC_CHAR_ZONE_SINGLE_OPTION_CMD `0x10D3` (WM → zone) @ FUN_0… | **high** | cap 9/10; client×1 |  |
| · 7.2 Saving the options back to the WM: `sp_SingleOptionSave2Wor… | **low** | cap 1/1; sup×1 (README §5.5) | re-read the rest (§3) |
| · 7.3 NC_CHAR_ZONE_LINK_FROM_CMD `0x10B8` (WM → zone): the roll-b… | medium | cap 0/2; weak inf1 | capture (class U) |
| · 7.4 Title progress reset: `CCharacterTitleData::IsTitleRefresh`… | medium | the captured opcodes are only mentioned here (0x1031 title blob, 0x4016 title save); the subject of the section (a title progress reset) is in no capture (hand; baseline: high) | capture across the reset time of a title |
| · 7.5 Small helpers found in the sweep | medium | cap 1/1 | capture (class U) |
| Original-server bugs | **low** | cap 0/1; sup×1 (README §5.5); weak inf1; R×4; bug table (class X: effects are deductions) | re-read the rest (§3) |
| N. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| N+1. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.24 Z13: `zone/Z13-objects.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Mini-house object `ShineObjectClass::ShineMiniHouse` (object… | – | container (see its subsections) |  |
| · 1.1 Data | medium | cap 0/2; R×1 | capture 0x1C13 |
| · 1.2 Building, routine and removal | medium | cap 0/4 | capture 0x1C13, 0x8C27, 0x8C4F, 0x8C61 |
| · 1.3 Membership: enter, leave, visit checks, kick | medium | cap 0/8; weak inf3 | capture 0x8C0B, 0x8C0D, 0x8C0F, 0x8C11 … |
| · 1.4 Settings setters (owner requests of Z07 §6.8) | medium | cap 0/4; R×1 | capture 0x1C13, 0x1C14, 0x8C31, 0x8C4A |
| · 1.5 House methods with no caller in the 2016 zone | medium | cap 0/1 | capture 0xAC2C |
| · 1.6 Player side: the mini-house item, `MiniHouseStr`, build que… | medium | cap 5/9; sup×1 (README §5.6); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 1.7 Brief info: `0x1C13` / `0x1C14` | medium | cap 0/2; client×1 | capture 0x1C13, 0x1C14 |
| · 1.8 ShineMiniHouse vtable: status of every slot Z07 lists | medium | B×4; R×2 | second reading / client check |
| 2. Furniture (house boxes, placement, furniture lists) | – | container (see its subsections) |  |
| · 2.1 Data | medium | read in code | second reading / client check |
| · 2.2 Loading the boxes and sending the furniture lists | medium | cap 1/5; client×1 | capture 0x8C08, 0x8C09 |
| · 2.3 Placement area | medium | no function cited | cite and re-read the function |
| · 2.4 Create, rearrange, delete (house vt 0xbc / 0xb8 / 0xc0) | medium | cap 1/4 | capture 0x8C20, 0x8C23, 0x8C26 |
| · 2.5 Releasers: what the DB confirmation shows | medium | cap 3/9; client×1 | capture 0x8C20, 0x8C21, 0x8C23, 0x8C24 … |
| · 2.6 Moving an item into the house boxes | medium | cap 0/3 | capture 0x8C23 |
| · 2.7 Furniture expiry: `smh_FurnitureActiveCheck` | **high** | cap 2/2; cv ok |  |
| · 2.8 Other furniture helpers | **low** | cap 1/1; sup×1 (README §5.6); cv corr; weak inf1; R×1 | re-read the rest (§3); read with P02 "Corrections" |
| 3. Portals, effects, endurance, furniture animations and emotio… | – | container (see its subsections) |  |
| · 3.1 Portals (house vt 0x104–0x124) | medium | cap 0/5 | capture 0x8C24, 0x8C27, 0x8C4C, 0x8C4F |
| · 3.2 Furniture and portal effects | medium | cap 1/8 | capture 0x8C41, 0x8C42, 0x8C57, 0x8C58 |
| · 3.3 Endurance (durability) | medium | cap 0/5; weak inf2; R×3 | capture 0x3034, 0x8C61 |
| · 3.4 Furniture animations (`MiniHouseObjAni.shn`, 0x8C3D / 0x8C3… | medium | cap 0/2; weak inf1 | capture 0x8C3F |
| · 3.5 Furniture emotions (sitting / lying on furniture) | medium | cap 0/5; R×1 | capture 0x8C64, 0x8C67 |
| · 3.6 Client side (2016 client, `GameFrameWork` scene) | medium | cap 0/16; client×2 | capture 0x3034, 0x8C3F, 0x8C41, 0x8C42 … |
| 4. Wedding: hall, ceremony, married-state timers, partner summon | – | container (see its subsections) |  |
| · 4.1 Data | medium | cap 1/2 | capture (class U) |
| · 4.2 Reservation and the timetable | medium | cap 1/5; weak inf1 | capture (class U) |
| · 4.3 Ceremony | medium | cap 1/5 | capture (class U) |
| · 4.4 Married-state checks (`Checker`, per minute and on every 0x… | medium | cap 1/11 | capture 0x205D |
| · 4.5 Ring refresh of a partner's wedding data | medium | cap 1/4 | capture (class U) |
| · 4.6 Partner summon (`SummonMate01`, Z09 §28.4 hand-over) | medium | the captured opcodes are only mentioned here (0x2434, 0x3C02); the subject of the section (the partner summon SummonMate01) is in no capture (hand; baseline: high) | SummonMate01 in a capture |
| · 4.7 Client side | medium | cap 1/6 | capture 0x205D |
| · 4.8 The annulment item (`UseItemImmediateDivorce`, instant divo… | medium | cap 1/3 | capture (class U) |
| · 4.9 The proposal item (`UseItemPropose`): where the partner is … | medium | cap 0/5; client×1; weak p171; R×1 | capture 0x204E, 0x2050, 0x2052 |
| 5. Pets, player side: `PetInfoPlayer` and the summon flow | medium | cap 1/7 | capture (class U) |
| · 5.1 Data | medium | cap 0/2 | capture 0xD405 |
| · 5.2 State machine | medium | cap 0/4 | capture (class U) |
| · 5.3 Using the pet item (`UseEffect::UseItemPet`, Z04 §6.3) | medium | the captured opcodes are only mentioned here (cast bar, item use, soul-stone and storage link packets); the subject of the section (the pet item, 0xD411) is in no capture (hand; baseline: high) | capture with a pet item used |
| · 5.4 Summon (`sp_PetSystem_PlayerRoutine`, `sp_PetSystem_Summon`) | medium | cap 2/8 | capture 0xD411 |
| · 5.5 Naming prompt (`0xD405`) | medium | cap 0/10; client×1 | capture 0xD405, 0xD408, 0xD40A |
| · 5.6 Unsummon | medium | cap 1/5 | capture 0xD411 |
| · 5.7 Mind and stress (tendency) | medium | cap 0/1 | capture (class U) |
| · 5.8 Re-summon after a map link | medium | captured only with no pet (0x4033 / 0xD412 `bDoResummon 0`, ids -1): the re-summon branch never ran (hand; baseline: high) | capture a map link with a pet out |
| · 5.9 Other pet hooks in player code | medium | cap 0/2 | capture 0xD411 |
| · 5.10 Client side (2016 client, `GameFrameWork`) | medium | cap 9/20; R×1 | capture 0xD405, 0xD411 |
| 6. Pets, object side: `ShinePet`, `CPetData`, pet AI scripts | – | container (see its subsections) |  |
| · 6.1 Tables (`CPetData gPetData`) | medium | read in code | second reading / client check |
| · 6.2 Object (`ShinePet`, 0x25d4 bytes) and its overrides | medium | cap 0/2; B×3 | capture 0x1C1C, 0xD411 |
| · 6.3 Creation and spawn | medium | cap 0/1; weak inf1; R×1 | capture (class U) |
| · 6.4 Routine and removal | medium | the captured opcodes are only mentioned here (0x1805 / 0x244A); the subject of the section (the pet routine) is in no capture (hand; baseline: high) | capture with a pet summoned |
| · 6.5 Brief info: `0x1C1C NC_BRIEFINFO_REGENPET_CMD`, `0x1C1D NC_… | medium | the captured opcodes are only mentioned here (0x1805, 0x1C01); the subject of the section (pet brief info 0x1C1C / 0x1C1D) is in no capture (hand; baseline: high) | capture with a pet summoned |
| · 6.6 Lua interface and the pet AI script | medium | R×1 | second reading / client check |
| 7. Mounts, player side: horses (`RideCasting`) and the mover sy… | **high** | cap 2/4 |  |
| · 7.1 Data | medium | read in code | second reading / client check |
| · 7.2 Using a ride item and the cast | **high** | cap 3/5 |  |
| · 7.3 Horse on and off | medium | cap 1/6 | capture 0x203F, 0x2040, 0x2041, 0x2042 … |
| · 7.4 Mover summon, get on, get off | medium | cap 5/13 | capture 0x306A, 0xCC03, 0xCC07, 0xCC08 |
| · 7.5 Hunger and feeding | medium | cap 1/4 | capture 0x2046, 0xCC09 |
| · 7.6 Saving the ride item: `sp_HorseItemSave` | medium | cap 0/1 | capture (class U) |
| · 7.7 Login, map link, layer moves | **high** | cap 2/4; R×1 |  |
| · 7.8 Forced dismounts | medium | read in code | second reading / client check |
| · 7.9 Client side (2016 client, `GameFrameWork`) | medium | cap 2/16; client×1 | capture 0x203F, 0x2040, 0x2041, 0x2042 … |
| 8. Mounts, object side: `ShineMover` (object type 11) | – | container (see its subsections) |  |
| · 8.1 Object and vtable | **high** | cap 5/6 |  |
| · 8.2 Summon | medium | cap 1/1; R×1 | capture (class U) |
| · 8.3 Seats | medium | cap 6/13; R×1 | capture 0x306C, 0x306E, 0xCC03, 0xCC07 … |
| · 8.4 Routine and removal | medium | cap 2/5 | capture 0xCC08 |
| · 8.5 Map links: who rebuilds the mover, and the bookings | **high** | cap 4/8 |  |
| · 8.6 Hunger and feeding (mover side) | medium | cap 1/2; R×1 | capture 0xCC09 |
| · 8.7 Movement and speed | **high** | cap 6/6 |  |
| · 8.8 Abnormal states shared with the riders | medium | read in code | second reading / client check |
| · 8.9 Combat overrides (no effect with the 2016 data) | medium | cap 1/3; R×1 | capture (class U) |
| · 8.10 Brief info: `0x1C1A NC_BRIEFINFO_REGENMOVER_CMD`, `0x1C1B … | **high** | cap 1/2 |  |
| · 8.11 Client side (2016 client, `GameFrameWork` / `CharMgr`) | **high** | cap 7/12 |  |
| 9. Minimon auto-use, the card reward condition, client handling… | – | container (see its subsections) |  |
| · 9.1 Tables: `MinimonInfo.shn`, `MinimonAutoUseItem.shn` | medium | cap 0/2 | capture (class U) |
| · 9.2 Player state, login and saving | **high** | cap 5/5; weak inf1 |  |
| · 9.3 The ON / OFF requests (Z07 §4.1, completed) | medium | cap 1/9 | capture 0x1125, 0x1127, 0x1129, 0x112B |
| · 9.4 The auto-use routine | medium | cap 2/5 | capture 0x1127, 0x112B, 0x112D |
| · 9.5 Item changes and equipment hooks | medium | cap 0/2 | capture (class U) |
| · 9.6 Client side (2016 client, `GameFrameWork`) | medium | cap 2/11; client×1 | capture 0x1125, 0x1127, 0x1129, 0x112B … |
| · 9.7 `cca_IsRewardCondition` (Z07 §7, return values from the ass… | medium | cap 0/1; R×1 | capture (class U) |
| · 9.8 Client handling of result codes without text (Z07 §12) | medium | cap 2/14; client×2; weak inf1 | capture 0x1061, 0x1067, 0x1125, 0x1129 … |
| Original-server bugs | medium | cap 14/48; client×1; weak inf1; R×5; bug table (class X: effects are deductions) | capture 0x2041, 0x2050, 0x3034, 0x306A … |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.25 Z14: `zone/Z14-instances.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Instance dungeons: data and the cluster manager | – | container (see its subsections) |  |
| · 1.1 Data tables | medium | cap 1/1; weak inf1 | capture (class U) |
| · 1.2 Structures | medium | cap 0/1 | capture (class U) |
| · 1.3 Registration (zone start) | medium | read in code | second reading / client check |
| · 1.4 Finding and taking an instance | medium | read in code | second reading / client check |
| · 1.5 Changing the owner (raid creation) | medium | read in code | second reading / client check |
| · 1.6 Routine: empty instances, time limit, failure | medium | cap 1/5 | capture (class U) |
| · 1.7 Deleting an instance; films | medium | cap 0/2 | capture (class U) |
| · 1.8 Player side | medium | read in code | second reading / client check |
| · 1.9 Lifecycle summary | medium | cap 0/5 | capture (class U) |
| · 1.10 Object-kind masks | medium | read in code | second reading / client check |
| 2. Zone-ring handlers: instance and job dungeons (ZoneListenSes… | medium | read in code | second reading / client check |
| · 2.1 0xA404 NC_INSTANCE_DUNGEON_FIND_RNG (IDGate, party / raid i… | medium | cap 0/1 | capture (class U) |
| · 2.2 0x10B1 NC_CHAR_EMPTY_INSTANCE_DUNGEON_RNG (delete an instan… | medium | cap 0/1 | capture (class U) |
| · 2.3 0x441F NC_QUEST_JOBDUNGEON_FIND_RNG (job-change dungeon on … | medium | cap 0/2 | capture 0x4420 |
| 3. Guild storage across zones: 0x7493 | medium | cap 2/11; client×1 | capture 0x7492, 0x7494 |
| 4. Guild academy reward storage across zones: 0x9872, 0x9874, 0… | medium | cap 0/9 | capture 0x9873, 0x9875 |
| · 4.1 Withdraw / deposit (money and lots) | medium | cap 0/5; R×1 | capture 0x9873, 0x9875 |
| · 4.2 0x9884 NC_GUILD_ACADEMY_REWARDSTORAGE_ITEM_INFO_ZONE_RNG (i… | medium | cap 0/3 | capture 0x9873, 0x9875 |
| · 4.3 Academy rewards: 0x986C body and 0x9885 | medium | cap 0/5; client×1; R×1 | capture 0x9873, 0x9875 |
| 5. Raid internals (zone copy) | – | container (see its subsections) |  |
| · 5.1 Raid record and RaidSystem | medium | cap 0/1 | capture (class U) |
| · 5.2 RaidTask | medium | R×1 | second reading / client check |
| · 5.3 Raid status packets (zone → client) | medium | cap 0/7; client×1 | capture 0x384A, 0xB020, 0xB021, 0xB022 … |
| 6. Z08-B5 and Z08-B9 re-checked | medium | cap 0/1 | capture (class U) |
| 7. Original-server bugs | medium | cap 0/6; client×1; weak inf1; bug table (class X: effects are deductions) | capture 0xB026 |
| 8. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.26 Z15: `zone/Z15-quest-engine.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Quest data: `QuestData.shn` | – | container (see its subsections) |  |
| · 1.1 File and loader | medium | the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step (hand; baseline: high) | capture: accept, progress and finish one quest |
| · 1.2 `QUEST_DATA` row layout *(pdb2016; offsets confirmed by the… | medium | no function cited | cite and re-read the function |
| 2. The script language and its parser (`CQuestParserScript`) | – | container (see its subsections) |  |
| · 2.1 Objects | medium | cap 0/1 | capture (class U) |
| · 2.2 Keyword tables (static data) | medium | no function cited | cite and re-read the function |
| · 2.3 Name table `QuestParser.txt` | medium | read in code | second reading / client check |
| · 2.4 Opening a script: `ParserStart` | medium | read in code | second reading / client check |
| · 2.5 `ParserNext`: the grammar | medium | read in code | second reading / client check |
| · 2.6 `CommandRun`: control flow and variables | medium | read in code | second reading / client check |
| · 2.7 Choosing and opening the script of a quest | medium | cap 0/1 | capture (class U) |
| · 2.8 The shipped 2016 scripts *(data)* | medium | no function cited | cite and re-read the function |
| 3. The interpreter (`CQuestZone::QuestNext`) and the action com… | – | container (see its subsections) |  |
| · 3.1 Run state | medium | cap 0/5 | capture (class U) |
| · 3.2 The loop | medium | cap 0/1; R×1 | capture (class U) |
| · 3.3 Action commands | medium | cap 3/13; R×1 | capture 0x4412 |
| · 3.4 The client dialog: 0x4401 / 0x4402 | medium | cap 1/3; client×1; R×2 | capture (class U) |
| · 3.5 Diary requests of the interpreter: 0x4403, 0x4405 / 0x4406 | medium | cap 1/5 | capture (class U) |
| · 3.6 SCENARIO: server and client scenarios | medium | cap 2/9; client×3 | capture 0x181D, 0x440C, 0x4420 |
| · 3.7 CALLPS: Pine scripts | medium | read in code | second reading / client check |
| · 3.8 Player getters and the `CQuestZone` vftable | medium | read in code | second reading / client check |
| · 3.9 Worked trace | medium | cap 1/4; weak inf1 | capture (class U) |
| · 3.10 Script error codes (0x4401 `Cmd 0`, `Data.ErrCode`) | medium | cap 1/5 | capture (class U) |
| 4. The diary (`CQuest`), quest conditions and repeat resets | medium | the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step (hand; baseline: high) | capture: accept, progress and finish one quest |
| · 4.1 Members and the diary array | medium | the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step (hand; baseline: high) | capture: accept, progress and finish one quest |
| · 4.2 Loading the diary at login (WM 0x1021 / 0x1022 / 0x10CD / 0… | medium | captured only as empty lists: 0x1021 / 0x10CD / 0x10D6 `n 0` at every map login (capture-validation §7.5; P02-B10); no quest in the diary of any captured character (hand; baseline: high) | capture-scenarios 19 (a quest accepted, then a map login) |
| · 4.3 Status changes after a DB answer | medium | R×1 | second reading / client check |
| · 4.4 Quest conditions and the computed status | medium | cap 1/7; client×1 | capture (class U) |
| · 4.5 Event functions (`CQuest` vftable 0x04…0x24) | medium | the only client citation says the client shares the `CQuest` / `CQuestData` library code; nothing on the wire and no capture of a quest step (hand; baseline: high) | capture: accept, progress and finish one quest |
| · 4.6 Repeat rules (repeatable, daily, give-up) | medium | cap 0/2 | capture (class U) |
| · 4.7 Give-up, select-start, read and the SET_INFO answer | medium | cap 1/17; client×3; weak inf1; R×1 | capture 0x4408, 0x4410, 0x4415, 0x4417 |
| 5. Rewards, the DONE round trip, reset times and the character … | medium | cap 0/2 | capture (class U) |
| · 5.1 Reward data, selection and the room check | medium | cap 0/2; client×1; weak p171 | capture 0x4412 |
| · 5.2 `0x441A NC_QUEST_DB_DONE_REQ`: reserve and send | medium | cap 0/1; weak inf2; R×1 | capture (class U) |
| · 5.3 `0x441B NC_QUEST_DB_DONE_ACK`: apply or drop | medium | the captured opcodes are only mentioned here (0x1033, 0x3001, 0x4401); the subject of the section (0x441B quest done) is in no capture (hand; baseline: high) | capture: accept, progress and finish one quest (scenario 19) |
| · 5.4 The reward-request flag | medium | cap 0/1 | capture (class U) |
| · 5.5 The older two-step path: `0x345C NC_ITEMDB_QUESTREWARD_ACK` | medium | cap 0/4; R×2 | capture (class U) |
| · 5.6 Reset times: 0x441C / 0x441D → 0x441E | medium | cap 2/3; client×1; sup×1 (README §5.6); cv corr; weak inf1 | re-read the rest (§3); read with P02 "Corrections" |
| · 5.7 The diary in the character save and at map login | medium | captured only as empty lists: the saves 0x400F / 0x4029 / 0x402B `n 0` and the login lists `n 0` (capture-validation §7.5); no quest in the diary of any captured character (hand; baseline: high) | capture-scenarios 19 (a quest accepted, then a save and a map login) |
| · 5.8 Worked trace: a quest with an item reward | medium | cap 3/7 | capture (class U) |
| 6. Other entry points: NPC click, start request, kills, quest d… | medium | cap 0/1 | capture (class U) |
| · 6.1 NPC click and the start request 0x4414 | medium | cap 2/7; client×2 | capture 0x4415 |
| · 6.2 Mob kills: `so_KilledBy` → party / raid → the diary | medium | cap 0/1; client×2 | capture 0x440D |
| · 6.3 Quest drops | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 6.4 Other quest helpers reached from the world | medium | read in code | second reading / client check |
| · 6.5 Lua functions (handed over by Z09 §14.9) | medium | cap 0/7; client×1 | capture 0x305F, 0x3060, 0x5812, 0x5813 … |
| · 6.6 GM commands | medium | cap 0/2 | capture (class U) |
| 7. Quest result codes 0xB41…0xB5A | medium | cap 0/13; client×4; R×1 | capture 0x4408, 0x4410, 0x4413, 0x4415 … |
| 8. Original-server bugs | medium | cap 1/15; client×3; weak inf1; R×1; bug table (class X: effects are deductions) | capture 0x305F, 0x3060, 0x4408, 0x4415 |
| 9. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 10. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.27 Z16: `zone/Z16-events.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Kingdom quest: data structures and tables | medium | cap 2/6 | capture (class U) |
| · 1.1 Globals | medium | cap 1/2 | capture (class U) |
| · 1.2 The KQ element | medium | cap 1/1; R×1 | capture (class U) |
| · 1.3 Joiners: `KQPlayerInfoList` | medium | read in code | second reading / client check |
| · 1.4 Mob kills: `KQContribute::KQContributeList` | medium | cap 0/1; client×1 | capture 0x5822 |
| · 1.5 Entrance lists and gate keepers | medium | read in code | second reading / client check |
| 2. KQ lifecycle | – | container (see its subsections) |  |
| · 2.1 Make: 0x580D NC_KQ_W2Z_MAKE_REQ (WM → zone) | **high** | cap 2/2 |  |
| · 2.2 Start: 0x580F NC_KQ_W2Z_START_CMD (WM → zone) | medium | cap 0/1 | capture (class U) |
| · 2.3 Pull-in: the gate keeper and the client's entry answer | medium | cap 2/6 | capture 0x181D, 0x5819 |
| · 2.4 Playing: what the zone does on a KQ map | medium | cap 1/6; client×1; weak inf1 | capture 0x1812, 0x1818, 0x1828, 0x5818 … |
| · 2.5 Removing joiners, bans, end and destroy | medium | cap 1/4 | capture (class U) |
| · 2.6 KQ items | medium | the captured opcodes are only mentioned here (0x3459 / 0x345A of the destroy and the expiry in batch 3); the subject of the section (KQ items) is in no capture (hand; baseline: high) | a KQ played in a capture (scenario 31) |
| 3. KQ scoring, end, results and rewards | medium | cap 0/2 | capture 0x5814, 0x5821 |
| · 3.1 Battle statistics: `BattleStat` | medium | cap 0/2 | capture (class U) |
| · 3.2 End: `cEndOfKingdomQuest` | medium | cap 1/2 | capture (class U) |
| · 3.3 Results: `cQuestResult`, `cQuestResult_Individual` and `Axi… | medium | cap 0/3; client×1 | capture 0x5812, 0x5813 |
| · 3.4 Rewards: `cReward`, `cKQRewardIndex`, `sp_KQReward` and 0x5… | medium | cap 0/6; client×1; R×1 | capture 0x5823 |
| · 3.5 Other KQ Lua functions | medium | cap 0/3; client×1 | capture 0x0810, 0x5818, 0x5822 |
| · 3.6 Logout log and GM words | medium | read in code | second reading / client check |
| 4. Guild tournament: the system core | medium | read in code | second reading / client check |
| · 4.1 Data structures | medium | cap 0/3 | capture 0x74DE |
| · 4.2 Tables | medium | read in code | second reading / client check |
| · 4.3 Lifetime and the tick | medium | cap 0/1 | capture 0x74DD |
| · 4.4 Registration of fighters, flags, gates and portals | medium | cap 1/7; weak inf1 | capture 0x7483, 0x74CE, 0x74F2 |
| · 4.5 Flag capture | medium | cap 1/4; client×1 | capture 0x74CD, 0x74DD |
| · 4.6 Kills, scores, advantage and the enemy scan | medium | cap 0/5; client×1 | capture 0x7483, 0x74DD, 0x74DE, 0x74DF … |
| · 4.7 Result, master revive, error sink, map helpers | medium | cap 0/2 | capture (class U) |
| 5. Guild tournament: guild groups, guild skills, items and the … | medium | cap 0/2 | capture (class U) |
| · 5.1 `GuildGroup` and `DiceGame` layouts *(pdb2016)* | medium | read in code | second reading / client check |
| · 5.2 Manager user, win event, scores | medium | cap 0/3; client×2 | capture 0x74CE, 0x74DD, 0x74E1 |
| · 5.3 Guild skills: 0x74CF and the cool-downs | medium | cap 0/4; client×2 | capture 0x74CE, 0x74D0, 0x74D1 |
| · 5.4 Gates, team NPCs, advantage item boxes | medium | cap 0/1 | capture 0x74DD |
| · 5.5 Item boxes: `GTIEffect` and the GTI* tables | medium | cap 0/3; client×3; weak inf1 | capture 0x74F0, 0x74F1, 0x74F2 |
| · 5.6 The dice game | medium | cap 0/6; client×3 | capture 0x74D2, 0x74D4, 0x74D5, 0x74D6 … |
| 6. Guild tournament: the match lifecycle with the WM and the cl… | medium | cap 0/8 | capture 0x749B |
| · 6.1 Seed table and tournament map table | medium | cap 1/5 | capture 0x749D |
| · 6.2 Start: 0x7481 NC_GUILD_TOURNAMENT_START_CMD (WM → every zon… | medium | cap 0/3; R×1 | capture (class U) |
| · 6.3 Recall: 0x749B prompt, 0x749C answer, summon | medium | cap 2/5; client×2 | capture 0x749B, 0x749D |
| · 6.4 Observers | medium | cap 0/7; client×2 | capture 0x74D8, 0x74DC |
| · 6.5 Flag capture cast (0x74CA) | medium | cap 2/5; client×2 | capture 0x74CB, 0x74CC |
| · 6.6 Match end and result to the WM | medium | cap 0/2 | capture 0x7490 |
| · 6.7 Entry application (WM → zone → DB) | medium | cap 0/5 | capture (class U) |
| · 6.8 0x74AC / 0x74B4 check order (Z08 open point, assembly) | medium | cap 0/2 | capture (class U) |
| Original-server bugs | **low** | cap 2/13; client×2; sup×1 (README §5.6); bug table (class X: effects are deductions) | re-read the rest (§3); capture 0x749B, 0x74D0, 0x74D8, 0x74DD |
| N. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| N+1. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.28 Z17: `zone/Z17-item-actions.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Item-action data model | – | container (see its subsections) |  |
| · 1.1 Tables and loading | medium | read in code | second reading / client check |
| · 1.2 `ItemAction` rows → `Action` | medium | read in code | second reading / client check |
| · 1.3 `ItemActionCondition` rows → condition objects | medium | read in code | second reading / client check |
| · 1.4 Target validators | medium | read in code | second reading / client check |
| · 1.5 Condition test | medium | read in code | second reading / client check |
| · 1.6 `ItemActionEffect` rows → effect objects | medium | weak inf1 | second reading / client check |
| · 1.7 Where action ids come from | medium | read in code | second reading / client check |
| · 1.8 The 2016 data in short | medium | no function cited | cite and re-read the function |
| 2. Item-action runtime engine | medium | read in code | second reading / client check |
| · 2.1 Structures *(pdb2016)* | medium | read in code | second reading / client check |
| · 2.2 Adding and removing actions | medium | read in code | second reading / client check |
| · 2.3 Running a hook point | medium | read in code | second reading / client check |
| · 2.4 `Action::raise`: conditions, then effects | medium | weak inf1; R×1 | second reading / client check |
| · 2.5 Cool-down groups and `0x482C` | **high** | cap 2/2 |  |
| · 2.6 Effects: target selection and bodies | medium | cap 0/1; weak inf1 | capture 0x206F |
| · 2.7 Packets sent by the effects | medium | cap 0/4; client×2 | capture 0x206F, 0x3046 |
| · 2.8 `so_ItemActonAbstateApp`: skill-group rates on a state just… | medium | read in code | second reading / client check |
| 3. Item-action lifecycle and hook points | – | container (see its subsections) |  |
| · 3.1 Login: cool-time restore, then the action setup | **high** | cap 5/5; weak inf1 |  |
| · 3.2 Equip, unequip, drop | medium | cap 1/3 | capture (class U) |
| · 3.3 Gems and abnormal states | medium | cap 0/4 | capture 0x3046 |
| · 3.4 Hook points: the events that run the actions | – | container (see its subsections) |  |
| · · 3.4.1 Periodic, item use, kill | medium | capture credit comes from the shared 0x3016 / 0x482C; no capture is known to contain an item with an action set (hand; baseline: high) | capture: equip an item with an `ItemAction` row and kill a mob |
| · · 3.4.2 Normal attacks (swing) and the rule-set rates | medium | capture credit comes from the swings 0x2448 / 0x2449; no capture is known to contain an item with an action set (hand; baseline: high) | capture: equip an item with an `ItemAction` row and kill a mob |
| · · 3.4.3 Skills | medium | read in code | second reading / client check |
| · 3.5 Cool-down persistence: `0x482C` (full list), `0x4023`, `0x4… | medium | captured only as empty lists: WM→Z 0x10D0 `n 0` and client 0x482C `num 0` (capture-validation §5.2, §7.5); 0x4023 / 0x4034 not captured; no item-action cool-down was persisted (hand; baseline: high) | capture: use an item with an item-action cool-down, then a map login |
| · 3.6 Teardown | medium | read in code | second reading / client check |
| · 3.7 Helpers of finished items reached from the hooks | medium | cap 1/1 | capture (class U) |
| 4. Costume weapon / shield charges and the action-item box | medium | read in code | second reading / client check |
| · 4.1 Data and the charge counter | medium | cap 2/8; weak inf1; R×1 | capture (class U) |
| · 4.2 Where charges are spent: normal swings and damaging skill b… | medium | cap 0/6 | capture 0x3037, 0x3038, 0x3066 |
| · 4.3 Flushing the counter: packets | medium | cap 2/7; client×1 | capture 0x3037, 0x3038, 0x3066 |
| · 4.4 `sp_CheckBashAndEquipment`: skin without its base item | medium | read in code | second reading / client check |
| · 4.5 The action-item box (premium emote items) | medium | the captured opcodes are only mentioned here (login and item-move packets); the subject of the section (the action-item box (premium emotes)) is in no capture (hand; baseline: high) | capture 0x2067, 0x3428 ff. |
| Original-server bugs | medium | cap 2/6; bug table (class X: effects are deductions) | capture 0x206F, 0x3046 |
| 5. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 6. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.29 Z18: `zone/Z18-leftovers.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Z01: player login, handles, sessions, diagnostics, SHN boxes | – | container (see its subsections) |  |
| · 1.1 Login-burst helpers of `sp_NC_MAP_LOGINCOMPLETE_CMD` | **high** | cap 3/5 |  |
| · 1.2 Object handles: `ShineObjectHandleUnion` | medium | read in code | second reading / client check |
| · 1.3 Client sessions: accept, seed, session-mode filter, per-IP … | **high** | cap 6/8 |  |
| · 1.4 OPTool and zone-ring session glue | medium | the captured opcodes are only mentioned here (the S2S handshake and heartbeat); the subject of the section (OPTool and zone-ring sessions) is in no capture (hand; baseline: high) | none with one zone PC and no OPTool |
| · 1.5 Socket, packet and server-info functions documented elsewhe… | medium | read in code | second reading / client check |
| · 1.6 Diagnostics and logging | medium | read in code | second reading / client check |
| · 1.7 SHN boxes and fixed-length strings | medium | read in code | second reading / client check |
| · 1.8 Sweep additions: packet path helpers, profiler line, crash-… | medium | cap 0/1; weak inf1 | capture (class U) |
| 2. Z02: brief info, server menus, chat ban | – | container (see its subsections) |  |
| · 2.1 The batched brief-info exchange: `BriefInfoExchanger` | medium | cap 3/8; client×1 | capture 0x1C07, 0x1C0B, 0x1C14, 0x1C1B … |
| · 2.2 The abstate batch: one 0x1C19 per object | **high** | cap 1/1 |  |
| · 2.3 Brief packet objects and the tent view backup | **high** | cap 2/2 |  |
| · 2.4 Server menus: building the menu, the summon flag | **high** | cap 2/2 |  |
| · 2.5 Spam chat ban setter | medium | cap 1/2 | capture (class U) |
| · 2.6 Sweep additions: menu actor setters, divorce and Silver Win… | medium | cap 0/1 | capture (class U) |
| 3. Z03: combat, skills, abnormal states | medium | cap 0/2 | capture 0x2442, 0x2443 |
| · 3.1 The SubState → actor table: `ActorCluster` | medium | read in code | second reading / client check |
| · 3.2 Abstate elements and lists | **high** | cap 4/6 |  |
| · 3.3 Death shelters: `AbstateShelter` | medium | cap 1/2 | capture (class U) |
| · 3.4 Dispel, cure and the caster-side abstate | medium | read in code | second reading / client check |
| · 3.5 Skill target scans and random targets | medium | read in code | second reading / client check |
| · 3.6 0x2442 / 0x2443: trap blasts `smo_SkillBash_Blast_Trap` | medium | cap 1/3; client×2 | capture 0x2442, 0x2443 |
| · 3.7 Blast queue, multi-hit and damage tables | **high** | cap 4/4 |  |
| · 3.8 Player attack timing and the rest | medium | table of 22 helpers; the captures touch the attack-timing rows (0x242B, 0x2440, moves) and, since batch 4, skill teach and empower (capture-validation §24.2, §24.3), not polymorph and the rest (hand; baseline: high) | per row: Z03 §3 for the timing, scenarios for the rest |
| · 3.9 Open point: B31's player-rule twin | medium | read in code | second reading / client check |
| · 3.10 Sweep additions: element constructor, sub-state lookup, ac… | medium | read in code | second reading / client check |
| 4. Z04: items, equipment, set items, random options | – | container (see its subsections) |  |
| · 4.1 Item tables and `ItemDataBox` accessors | medium | cap 1/1 | capture (class U) |
| · 4.2 Equipment slot rules: `EquipEnumChanger` and `ItemServerEqu… | medium | read in code | second reading / client check |
| · 4.3 View slots and `so_ply_EquipmentChange` | **high** | cap 6/6; client×1; weak p171 |  |
| · 4.4 Destroying items: the `sp_DestroyItem` family and `0x3459` | **high** | cap 2/2 |  |
| · 4.5 Drop attributes (`ItemAttr` vt 0x2c), random options and ca… | medium | read in code | second reading / client check |
| · 4.6 Upgrade helpers | medium | read in code | second reading / client check |
| · 4.7 Item use broadcasts and use-effect table | medium | cap 0/2; client×2 | capture 0x206F, 0x3029 |
| · 4.8 Small state holders, set items and the rest | medium | read in code | second reading / client check |
| · 4.9 Sweep additions: item boxes, locks, lot sums, bracelet upgr… | medium | the captured opcodes are only mentioned here (0x3016 / 0x301A of a potion); the subject of the section (item boxes, locks, lot sums, bracelet upgrade rows) is in no capture (hand; baseline: high) | per row: the scenario of its feature |
| 5. Z06: trade, booths, gambling (constructors) | medium | read in code | second reading / client check |
| 6. Z07: character titles, collection cards | **high** | cap 2/3 |  |
| · 6.1 Title objects | medium | cap 1/2 | capture (class U) |
| · 6.2 Unlocking titles: `CheckNewTitle` | **high** | cap 3/4; client×1 |  |
| · 6.3 Lua `cAddCharacterTitle(charNo, type, element)` | medium | the captured opcodes are only mentioned here (0x6004 / 0x6005 of the level-20 title marks, §6.2); the subject of the section (Lua `cAddCharacterTitle`) is in no capture (hand; baseline: high) | a script that gives a title, in a capture |
| · 6.4 The weapon title after `so_ply_EquipmentChange` (answers §8… | medium | the captured opcodes are only mentioned here (the title blobs 0x1031 / 0x1049 of the login); the subject of the section (the weapon title after an equipment change) is in no capture (hand; baseline: high) | capture 0x5C03 (weapon with a title) |
| · 6.5 Collection cards | **high** | cap 3/3; client×1 |  |
| · 6.6 Sweep additions: weapon titles, group titles, card table lo… | medium | the captured opcodes are only mentioned here (0x1C05, 0x200A, 0x200C); the subject of the section (weapon titles, group titles, card table lookups) is in no capture (hand; baseline: high) | capture 0x5C03, 0x5C0D |
| 7. Original-server bugs | medium | cap 8/12; R×1; bug table (class X: effects are deductions) | capture 0x1C0B, 0x2442, 0x5C03 |
| 8. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary | – | open points / boundary list, no claim to rate |  |
| · 9.1 How the boundary was checked | medium | no function cited | cite and re-read the function |
| · 9.2 Functions of other items | medium | cap 0/3 | capture 0x440D |

### 2.30 Z19: `zone/Z19-config-script.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The library in the zone | – | container (see its subsections) |  |
| · 1.1 Zone functions | medium | read in code | second reading / client check |
| 2. File format specification | – | container (see its subsections) |  |
| · 2.1 Buffer and tokens | medium | read in code | second reading / client check |
| · 2.2 Remarks | medium | read in code | second reading / client check |
| · 2.3 Commands | medium | no function cited | cite and re-read the function |
| · 2.4 `#DEFINE`: formats and column types | medium | no function cited | cite and re-read the function |
| · 2.5 Rows | medium | no function cited | cite and re-read the function |
| · 2.6 `#INCLUDE` | medium | no function cited | cite and re-read the function |
| · 2.7 Binary chunk files (`#READ` / `#WRITE*`) | medium | read in code | second reading / client check |
| · 2.8 Result and diagnostics | medium | no function cited | cite and re-read the function |
| · 2.9 Limits (none checked) | medium | no function cited | cite and re-read the function |
| 3. Zone: which file, read when, used how | medium | read in code | second reading / client check |
| 4. Reference reader and test on every 2016 config file | medium | no function cited | cite and re-read the function |
| 5. The other servers' copies | – | container (see its subsections) |  |
| · 5.1 Method and result | medium | read in code | second reading / client check |
| · 5.2 Function addresses per build | medium | read in code | second reading / client check |
| · 5.3 The data servers' `CServerInfo` | medium | read in code | second reading / client check |
| · 5.4 Which files each server reads, and when | medium | read in code | second reading / client check |
| 6. Original-server bugs | medium | R×2; bug table (class X: effects are deductions) | second reading / client check |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.31 Z20: `zone/Z20-skill-data.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. SkillDataBox: data structures | – | container (see its subsections) |  |
| · 1.1 Globals | medium | read in code | second reading / client check |
| · 1.2 `SkillDataBox` and `sdb_BinData` | medium | read in code | second reading / client check |
| · 1.3 `SkillDataIndex` (one per active skill, 0x268) | medium | read in code | second reading / client check |
| 2. Tables and column → member maps | – | container (see its subsections) |  |
| · 2.1 Files and readers | medium | read in code | second reading / client check |
| · 2.2 Column → member maps | medium | read in code | second reading / client check |
| 3. `SkillDataBox::sdb_Load` | – | container (see its subsections) |  |
| · 3.1 Pseudocode | medium | read in code | second reading / client check |
| · 3.2 Sanity warnings | medium | read in code | second reading / client check |
| · 3.3 Invariants a rebuild needs (with the 2016 data) | medium | no function cited; weak inf1 | cite and re-read the function |
| 4. `sdi_Clear` and `sdi_SetArgument`: the special-effect members | medium | read in code | second reading / client check |
| 5. Lookups | – | container (see its subsections) |  |
| · 5.1 By ID and name | medium | read in code | second reading / client check |
| · 5.2 `skillnametree` (`BTree`) | medium | the captured opcodes are only mentioned here (0x4801 / 0x4802 of the skill-book learn); the subject of the section (the name trie built at start-up) is not on the wire (hand; baseline: high) | none on the wire |
| 6. PassiveDataBox | medium | read in code | second reading / client check |
| · 6.1 Data structures | medium | read in code | second reading / client check |
| · 6.2 Tables and column → member map | medium | read in code | second reading / client check |
| · 6.3 `PassiveDataBox::pdb_Load` | medium | read in code | second reading / client check |
| · 6.4 Lookups and iteration | medium | read in code | second reading / client check |
| · 6.5 The per-player side: `CharacterPassiveList` | medium | read in code | second reading / client check |
| · 6.6 Invariants a rebuild needs (with the 2016 data) | medium | no function cited | cite and re-read the function |
| 7. Holders of `SkillDataIndex*` | medium | weak inf2 | second reading / client check |
| Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| 8. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.32 Z21: `zone/Z21-set-items.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Overview: three set-item mechanisms | medium | no function cited; R×1 | cite and re-read the function |
| 2. Tables | – | container (see its subsections) |  |
| · 2.1 `SetItem.shn` (row struct `SetItem`, 0x41 bytes, 442 rows, … | medium | no function cited; weak inf1 | cite and re-read the function |
| · 2.2 `SetItemEffect.shn` (row struct `SetItemEffect`, 0xF1 bytes… | medium | no function cited; weak inf1 | cite and re-read the function |
| · 2.3 `SetEffect.shn` (row struct `SetEffect`, 0x23 bytes, 1043 r… | medium | read in code | second reading / client check |
| 3. Mechanism A: skill-effect sets (legacy, dead in 2016) | – | container (see its subsections) |  |
| · 3.1 Data structures *(pdb2016)* | medium | the captured opcodes are only mentioned here (0x2408, 0x5004); the subject of the section (the set-item structures) is in no capture (hand; baseline: high) | capture: wear a full set |
| · 3.2 Globals and their initialisation | medium | read in code | second reading / client check |
| · 3.3 `ShinePlayer::sp_SetItemCheck` @ FUN_00510b50 (count pieces… | medium | R×1 | second reading / client check |
| · 3.4 `SetItemClassifier::sic_SetItemDefine` @ FUN_00510370 (piec… | medium | read in code | second reading / client check |
| · 3.5 Per-cast snapshot: `smo_ply_SetItemEffect` (vt 0xEF8) and t… | medium | read in code | second reading / client check |
| · 3.6 `SetItemEffectList::siel_AppendEffect` @ FUN_005104c0 and t… | medium | read in code | second reading / client check |
| · 3.7 Readers of `setitemskilleffect` (= `g_SetEffect`) | medium | read in code | second reading / client check |
| · 3.8 Net effect in 2016 *(inferred from §3.2)* | medium | no function cited; R×1 | cite and re-read the function |
| 4. Mechanism B: item-action sets (`SetEffect.shn`) | medium | read in code | second reading / client check |
| · 4.1 Table load and lookup | medium | read in code | second reading / client check |
| · 4.2 Piece count: `ShinePlayer::so_EqualSetitemIndexNameCount` @… | medium | read in code | second reading / client check |
| · 4.3 When the set action ids are added and removed | medium | cap 0/1; weak inf1 | capture (class U) |
| · 4.4 What the set-granted actions do | medium | cap 1/1 | capture (class U) |
| · 4.5 `0x206F NC_ACT_SETITEMHEALEFFECT` (Z→C broadcast) | medium | cap 0/1; client×1; weak p171 | capture 0x206F |
| 5. Mechanism C: set-item values in abnormal states | – | container (see its subsections) |  |
| · 5.1 Data structure and codes *(pdb2016)* | medium | read in code | second reading / client check |
| · 5.2 Writer 1: `aeo_SetItemEffectStore` (mechanism A source, sto… | medium | weak inf1 | second reading / client check |
| · 5.3 Writer 2: the caster's item actions, `so_ItemActonAbstateAp… | medium | read in code | second reading / client check |
| · 5.4 Readers | medium | read in code | second reading / client check |
| · 5.5 Saving: `ABSTATEREADBLOCK.setitem[4]` | medium | the captured opcodes are only mentioned here (the abstate blob and its saves 0x1023 / 0x4007 / 0x4011); the subject of the section (the set-item part of the block) is in no capture (hand; baseline: high) | capture: log out wearing a full set |
| · 5.6 Restoring | medium | the captured opcodes are only mentioned here (0x100C / 0x1023 abstate blobs, 0x104E); the subject of the section (restoring a set-item state) is in no capture (hand; baseline: high) | capture: log in wearing a full set |
| · 5.7 The enchant path: `ShineMobileObject::so_SkillEnchant` (vt … | medium | weak inf1; R×1 | second reading / client check |
| · 5.8 Heal over time: `so_mobile_HPHealOverTime` / `so_mobile_SPH… | medium | cap 1/1; client×1 | capture (class U) |
| Original-server bugs | medium | weak inf1; R×2; bug table (class X: effects are deductions) | second reading / client check |
| 6. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 7. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.33 Z22: `zone/Z22-abstate-actors.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Framework | – | container (see its subsections) |  |
| · 1.1 The actor cluster: SubState → actor  @ FUN_00405a10 | medium | read in code | second reading / client check |
| · 1.2 Actor virtual slots | medium | B×15; R×1 | second reading / client check |
| · 1.3 How an element reaches its actor (the element layer) | medium | cap 1/1 | capture (class U) |
| · 1.4 Shared helpers | **high** | cap 3/3 |  |
| 2. The base actor `SubAbnormalStateActor` | – | container (see its subsections) |  |
| · 2.1 Attach  @ FUN_0040bbd0 | medium | cap 0/1 | capture 0x10AF |
| · 2.2 Detach  @ FUN_0040bc60 | medium | read in code | second reading / client check |
| · 2.3 Routine  @ FUN_00406d50 | medium | read in code | second reading / client check |
| · 2.4 Applying states to an area | medium | read in code | second reading / client check |
| 3. Damage over time | – | container (see its subsections) |  |
| · 3.1 Data | medium | no function cited | cite and re-read the function |
| · 3.2 Poison actor  @ FUN_0040d4c0 (types 22, 27, 33, 67, 83, 84,… | medium | read in code | second reading / client check |
| · 3.3 `sasa_GetDamage`  @ FUN_0040b360 | **high** | cv ok |  |
| · 3.4 Disease actor  @ FUN_0040b8a0 (type 34) | medium | read in code | second reading / client check |
| · 3.5 Applying the damage: `so_mobile_DamageOverTime`  (vt 0x730)… | medium | cap 1/1; client×1 | capture (class U) |
| 4. Area damage | – | container (see its subsections) |  |
| · 4.1 Data | medium | no function cited | cite and re-read the function |
| · 4.2 AreaDamage actor  @ FUN_0040d640 (types 82, 95, 101) | **high** | cap 2/2; client×2; R×1 |  |
| · 4.3 DmgState actor (dead code)  @ FUN_0040dc60 | medium | cap 1/1 | capture (class U) |
| 5. Heal over time | – | container (see its subsections) |  |
| · 5.1 Data | medium | no function cited | cite and re-read the function |
| · 5.2 Actors | medium | cap 1/1 | capture (class U) |
| 6. Other routine actors (documented elsewhere) | medium | read in code | second reading / client check |
| 7. Detach actions: bomb, detach process, exp / drop chains, dis… | – | container (see its subsections) |  |
| · 7.1 Removal flags and the friend scans | medium | read in code | second reading / client check |
| · 7.2 Bomb actor (type 97)  @ FUN_0040c520 / FUN_0040c640 | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the bomb actor) is in no capture (hand; baseline: high) | capture a skill with this abstate type |
| · 7.3 Detach process, exp-up and drop-up detach  @ FUN_0040c1c0 /… | medium | cap 1/1 | capture (class U) |
| · 7.4 Dispel actor (type 113)  @ FUN_0040ca20 | medium | cap 1/1 | capture (class U) |
| · 7.5 The removers: dispel, cure, steal and map refusal  @ FUN_00… | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (dispel, cure, steal) is in no capture (hand; baseline: high) | capture a dispel or cure skill |
| 8. Exp and drop rate actors (types 109, 110) | medium | read in code | second reading / client check |
| 9. Damage hooks | – | container (see its subsections) |  |
| · 9.1 Where they run | medium | read in code | second reading / client check |
| · 9.2 Shields  @ FUN_00407370, FUN_00407400, FUN_00402390 | medium | read in code | second reading / client check |
| · 9.3 Range intercept (type 59)  @ FUN_004074f0 | medium | read in code | second reading / client check |
| · 9.4 Damage ratios and hide damage  @ FUN_00407570, FUN_00407650… | medium | cap 1/1 | capture (class U) |
| · 9.5 Time attack (type 77)  @ FUN_0040ba30 | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the time-attack actor) is in no capture (hand; baseline: high) | capture a skill with this abstate type |
| · 9.6 Damage reductions  @ FUN_004023d0, FUN_00402450, FUN_004094… | medium | R×2 | second reading / client check |
| · 9.7 `so_smo_LastDamageOperation` (vt 0xdb4) and min HP  @ FUN_0… | medium | read in code | second reading / client check |
| 10. Skill, targeting and parameter hooks | – | container (see its subsections) |  |
| · 10.1 Cast time  @ FUN_004072b0, FUN_004024d0 | medium | read in code | second reading / client check |
| · 10.2 Silence  @ FUN_0063ecc0, FUN_00401d20 | medium | read in code | second reading / client check |
| · 10.3 Ignore cooldown (type 31)  @ FUN_00500380, FUN_0057c5b0, F… | medium | read in code | second reading / client check |
| · 10.4 SP cost  @ FUN_004021d0 | medium | read in code | second reading / client check |
| · 10.5 Cannot target (type 105)  @ FUN_004b8d20 | medium | read in code | second reading / client check |
| · 10.6 Max HP / SP actor (types 24, 25, 39, 40)  @ FUN_00401990 | medium | cap 1/1 | capture (class U) |
| · 10.7 Skill enchant (vt 0x5a0)  @ FUN_00431ca0 | medium | captured: the toggle Heat of Fury goes through the skill-enchant keep-time path (capture-validation §25.4), and the capture extends the section (keep times above 2^31 − 1: 1 385 447 ms sent, 1 345 294 tenths set, P02-B39, §13): a captured section in which a class applies (hand; baseline: medium) | capture-scenarios 51 (toggle kept past its 23-min icon timer); X06 folds P02-B39 into the section |
| 11. Death hooks (slot 0x14)  @ FUN_00407730, FUN_00407910 | medium | cap 0/2 | capture (class U) |
| 12. Element classes (`AbnormalStateElement` subclasses) | – | container (see its subsections) |  |
| · 12.1 Slots and callers | medium | read in code | second reading / client check |
| · 12.2 Which abstate uses which class  (`AbnormalStateList::Abnor… | medium | read in code | second reading / client check |
| · 12.3 Rest counts  @ FUN_00401a90, FUN_00401ab0 | medium | read in code | second reading / client check |
| · 12.4 Party enchant  @ FUN_00408680, FUN_00405280, FUN_0040ebc0 | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (party enchant) is in no capture (hand; baseline: high) | capture-scenarios 15 (party) with a party buff |
| · 12.5 Couple party enchant (wedding)  @ FUN_0040e5e0 | medium | cap 1/1; weak inf1 | capture (class U) |
| · 12.6 Guild academy master enchant  @ FUN_004053c0, FUN_004087b0… | medium | weak inf1 | second reading / client check |
| · 12.7 Forced movement and recover  @ FUN_004083a0, FUN_004085b0,… | medium | cap 1/2 | capture 0x2456 |
| · 12.8 Polymorph and GM hide  @ FUN_00406c80, FUN_00409c10 | medium | R×1 | second reading / client check |
| · 12.9 Element side effects elsewhere | medium | cap 1/1 | capture (class U) |
| Original-server bugs | medium | cap 2/2; weak inf1; R×3; bug table (class X: effects are deductions) | capture (class U) |
| 13. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 14. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.34 Z23: `zone/Z23-skill-list.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data structures | – | container (see its subsections) |  |
| · 1.1 `CharaterSkillList` (player + 0x17d08, `ShinePlayer::sp_Ski… | medium | read in code | second reading / client check |
| · 1.2 `MoverSkillList` (mount + 0x1f54, `ShineMover::smv_MoverSki… | medium | no function cited | cite and re-read the function |
| · 1.3 Vtable slots used here | medium | the captured opcodes are only mentioned here (0x4821, 0x900D); the subject of the section (the vtable slots used by the skill list) is not on the wire (hand; baseline: high) | none on the wire |
| 2. Toggle skills | – | container (see its subsections) |  |
| · 2.1 Condition: `csl_Toggle_CanUseSkill` and the weapon check | medium | read in code | second reading / client check |
| · 2.2 The toggle list | medium | read in code | second reading / client check |
| · 2.3 Player wrappers and packets | **high** | cap 2/2; R×1 |  |
| · 2.4 Automatic switch-off | medium | captured: the automatic switch-off of the toggle by unequip, low HP and map change (capture-validation §25.4, §11 row "Toggle skill"), and the capture extends the section (each removed state is broadcast twice, a switch-off cast costs HPRate HP; P02-B38, §13): a captured section in which a class applies (hand; baseline: medium) | X06 folds P02-B38 into the section |
| · 2.5 Switching by cast | medium | switching on and off by cast captured with one learned step (capture-validation §25.4); two points of the section are not: the lower-step case Z23-B1 and the crafted field cast of a toggle that is on, Z23-B20 (inferred) (hand; baseline: high) | capture-scenarios 51 step 3; a crafted 0x2440 (test client, 41) |
| 3. Cooldowns and delay groups | – | container (see its subsections) |  |
| · 3.1 When a cast sets the cooldown | **high** | cv ok |  |
| · 3.2 Setting: `smo_ply_SkillCoolTime` and `csl_SetCoolTime` | medium | cap 1/1; client×1; weak inf1 | capture (class U) |
| · 3.3 IgnoreCoolTime abstates ("chain cast") | medium | cap 1/1 | capture (class U) |
| · 3.4 Shortening: damage taken, item-set rates, charged buffs | medium | cap 1/1 | capture (class U) |
| · 3.5 Mount skills: `MoverSkillList` | medium | cap 1/1; R×2 | capture (class U) |
| · 3.6 Other callers that set or check skill cooldowns | medium | cap 1/2 | capture (class U) |
| 4. Empower points | medium | empower allocation and reset captured with one learned step (capture-validation §24.3, §24.4); the section's own inferred point, which step ID the client names in 0x4811 with two learned steps of one line (it decides Z23-B8: the wrap to 15, 0x885 and the 0x68A kick), is not captured (hand; baseline: high) | capture-scenarios 51 step 1 |
| 5. Mastery (production skills) | medium | cap 1/3; client×2; R×1 | capture 0x481D |
| 6. Learn, unlearn, load | – | container (see its subsections) |  |
| · 6.1 Membership tests | medium | read in code | second reading / client check |
| · 6.2 Skill scroll: `UseItemSkillScroll::uib_CanUseItem` | **high** | cap 1/1; cv ok |  |
| · 6.3 Learning and the default skills | medium | cap 1/1 | capture (class U) |
| · 6.4 Unlearning one step: `csl_UnLearn` | medium | weak inf1 | second reading / client check |
| 7. Buffers: save to the DB and the WM, list to the client | – | container (see its subsections) |  |
| · 7.1 Which entries are written (`cs_bSave`) | **high** | cap 2/3; cv ok |  |
| · 7.2 Character DB: `so_SaveSkill` / `csl_FillSaveBuffer` | **high** | cap 2/2 |  |
| · 7.3 World manager cache: `so_Send_NC_CHARSAVE_2WLDMAN_SKILL_CMD… | **high** | cap 4/4 |  |
| · 7.4 Client list: `csl_FillSendBuffer_Client` | medium | cap 1/1 | capture (class U) |
| 8. Dispel, cure and the miss result (Z03 leftovers) | medium | read in code | second reading / client check |
| · 8.1 The mask: `smo_Dispel` | medium | read in code | second reading / client check |
| · 8.2 Cure: `so_SkillCure` | medium | weak inf1 | second reading / client check |
| · 8.3 Dispel and steal: `so_Dispel` | medium | weak inf1 | second reading / client check |
| · 8.4 Order in `smo_SkillBlast` and the double run | medium | read in code | second reading / client check |
| · 8.5 The miss result: `smo_ClearSkillResultBuffer_Miss` | medium | cap 2/2; sup×1 (README §5.5); weak inf1 | re-read the rest (§3) |
| · 8.6 `RandomBox` (the dispel / steal pick of §8.3) | medium | read in code | second reading / client check |
| 9. Mount skills (`ShineMover`) | – | container (see its subsections) |  |
| · 9.1 Who fills `MoverSkillList` | medium | read in code | second reading / client check |
| · 9.2 Casting: `so_smv_SkillBash_Object` / `so_smv_SkillBash_Loca… | medium | cap 1/1 | capture (class U) |
| · 9.3 Mob weapons against a mount: `ShineMover::so_ply_CanMyTarge… | medium | read in code | second reading / client check |
| 10. Original-server bugs | medium | cap 4/4; bug table (class X: effects are deductions) | capture (class U) |
| 11. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 12. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.35 Z24: `zone/Z24-item-data.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The item use table `useditemeffect` (`UseEffect::UsedItemEff… | – | container (see its subsections) |  |
| · 1.1 Data structures | medium | cap 0/1 | capture 0x3029 |
| · 1.2 ItemUseEffect.shn | medium | read in code | second reading / client check |
| · 1.3 `uie_Load` (stage wide) | medium | read in code | second reading / client check |
| · 1.4 Helpers | medium | cap 0/1; client×1; weak inf1 | capture 0x3029 |
| · 1.5 Writers of `uie_FuncStruct`, in stage order | medium | cap 1/2 | capture 0x302B |
| · 1.6 Invariants with the 2016 data | medium | no function cited | cite and re-read the function |
| 2. `ItemUseFunction` (World/ItemUseFunction.txt, stage tough) | medium | cap 0/1 | capture 0x3029 |
| 3. `cStateItemDataBox` (StateItem.shn, stage sleep) and the "by… | medium | R×1 | second reading / client check |
| 4. `MysteryVaultTable` (MysteryVaultServer.shn, stage full) | medium | read in code | second reading / client check |
| 5. `MoverDataBox` (MoverMain / MoverAbility / MoverHG / MoverIt… | medium | read in code | second reading / client check |
| · 5.1 Data structures | medium | read in code | second reading / client check |
| · 5.2 Files, readers, column maps | medium | weak inf1 | second reading / client check |
| · 5.3 `mvdb_Load` | medium | read in code | second reading / client check |
| · 5.4 Accessors | medium | read in code | second reading / client check |
| · 5.5 Invariants with the 2016 data | medium | no function cited | cite and re-read the function |
| 6. `ChargedItemEffectDataBox` and `RidePetDataBox` (ChargedEffe… | – | container (see its subsections) |  |
| · 6.1 Data structures | medium | read in code | second reading / client check |
| · 6.2 Files, readers, column maps | medium | weak inf1 | second reading / client check |
| · 6.3 `cideb_Load` (one template, four instances) | medium | read in code | second reading / client check |
| · 6.4 `RidePetDataBox::rpdb_Load` and `zs_start_sun` | medium | read in code | second reading / client check |
| · 6.5 Accessors | medium | read in code | second reading / client check |
| · 6.6 Invariants with the 2016 data | medium | no function cited | cite and re-read the function |
| · 6.7 Applying the charged buffs (`ChargedItemEffectList`, the re… | medium | cap 1/6; cv ok; client×1; weak inf1 | capture 0x9004 |
| 7. `CharClassDataBox` and the other helpers | – | container (see its subsections) |  |
| · 7.1 `CharClassDataBox` (`UseClassTypeInfo.shn`, stage home) | medium | read in code | second reading / client check |
| · 7.2 `ItemGroupClassifier` (item drop groups of `ItemInfoServer.… | medium | read in code | second reading / client check |
| · 7.3 `ItemDataBox::ReadData` (stand-alone ItemInfo reader, unuse… | medium | R×1 | second reading / client check |
| · 7.4 Gathering and production tables (`Gather.shn`, `Produce.shn… | medium | read in code | second reading / client check |
| · 7.5 `CChargedDeletableBuff` (`ChargedDeletableBuff.shn`, stage … | medium | cap 0/2 | capture 0x112F |
| · 7.6 `CTermExtendMatchDataBox` (`TermExtendMatch.shn`, stage sle… | medium | cap 0/1 | capture (class U) |
| · 7.7 `cChatColorDataBox` (`ChatColor.shn`, stage sleep) | medium | cap 0/2; weak inf1 | capture (class U) |
| · 7.8 `ItemProducer` (the production result, reader of `ProductIn… | medium | cap 0/3 | capture (class U) |
| 8. Reload behaviour | medium | no function cited; R×1 | cite and re-read the function |
| Original-server bugs | medium | cap 0/3; weak inf1; R×1; bug table (class X: effects are deductions) | capture 0x302B |
| 9. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 10. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.36 Z25: `zone/Z25-skill-specials.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data used by the special effects | – | container (see its subsections) |  |
| · 1.1 Special members of `SkillDataIndex` | – | container (see its subsections) |  |
| · · 1.1.1 Who reads each special member (sweep) | medium | the captured opcodes are only mentioned here (0x2440 / 0x2441 of the casts); the subject of the section (which code reads each SS_* special member) is in no capture beyond the specials of the `s24` skills (hand; baseline: high) | capture a skill per special |
| · 1.2 Globals and structures | medium | cap 1/1 | capture (class U) |
| · 1.3 Virtual slots called by `smo_SkillBlast` (players / mobs) | medium | the captures run these slots for player skills only: Bash [01] against a mob (batches 2–3) and, in batch 4, the casts of `s24` (Dash ground target, Heat of Fury toggle, Divine Shield abort, Revival; capture-validation §25.2–§25.4, §25.8); the mob-side slots and the other branches are code only (hand; baseline: high) | a mob skill; skills of other classes |
| · 1.4 Sub-state rows by strength, and how a keep time is chosen | medium | read in code | second reading / client check |
| 2. `smo_SkillBlast`: one target, in code order  @ FUN_00581160 | medium | read in code | second reading / client check |
| · 2.1 Entry filters  (0x581160 – 0x5812f0) | medium | read in code | second reading / client check |
| · 2.2 Hit roll and the miss result  (0x5812f0 – 0x581640) | medium | no function cited | cite and re-read the function |
| · 2.3 Hit: DISPELABSTATE, result slot, aggro  (0x581640 – 0x58179… | medium | cap 1/1; R×1 | capture (class U) |
| · 2.4 Heal part: SS_HEALAMOUNT  (0x581790 – 0x5818f0) | medium | no function cited | cite and re-read the function |
| · 2.5 Damage part  (0x5818f0 – 0x582080) | medium | cap 0/1 | capture 0x482D |
| · · 2.5.1 `RuleOfEngagementHealAttack::roe_CalcDamage`  @ FUN_00500… | medium | read in code | second reading / client check |
| · 2.6 After the damage part: RECALL, HPCONVERTSP, MANABURN  (0x58… | medium | cap 0/1 | capture 0x482D |
| · 2.7 SS_HOLDME: the caster holds still  (0x582122 – 0x58221c) | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (SS_HOLDME) is in no capture (hand; baseline: high) | capture a skill with this special |
| · 2.8 Keep-time specials: SS_FIRETIMEADD, SS_CURSETIMEADD, SS_POS… | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25)); the subject of the section (the keep-time specials) is in no capture (hand; baseline: high) | capture a skill with this special |
| · 2.9 Single-hit tail: abstates, dispel, item actions, SS_SUCKHP … | medium | read in code | second reading / client check |
| · 2.10 Multi-hit tail: the step's abstates  (`hit.mha_HitStep ≥ 0… | medium | the captured opcodes are only mentioned here (0x1C18 / 0x2427 – 0x242A of the abstates the captures set (login list, Bash [01], potion; batch 4: the skills and states of `s24`, capture-validation §24–§25), 0x2452); the subject of the section (the multi-hit tail) is in no capture (hand; baseline: high) | capture a multi-hit skill |
| 3. Committing a result: `SkillDamageSender::sds_TemplateStore` … | medium | cap 1/1 | capture (class U) |
| 4. Damage reflection | – | container (see its subsections) |  |
| · 4.1 Trigger (in `smo_SwingDamage` FUN_00432f30 and `smo_SkillBl… | medium | read in code | second reading / client check |
| · 4.2 `ShineMobileObject::smo_ReflectionDamage(a, dmg, d)`  @ FUN… | medium | cap 1/2; client×1; weak inf1 | capture 0x245B |
| 5. Dispel and cure: what the masks remove | medium | cap 1/1 | capture (class U) |
| 6. Blast entry points, target scans and chained blasts (outside… | – | container (see its subsections) |  |
| · 6.1 Which blast runs: `ShineMobileObject::so_Routine`  @ FUN_00… | **high** | cap 3/4 |  |
| · 6.2 `ShineMobileObject::smo_SkillBash_Blast(Obj)(o, t, empower)… | **high** | cap 7/9; R×1 |  |
| · 6.3 `ShineMobileObject::smo_SkillBash_Blast(Loc)(o, xy, empower… | **high** | cap 2/3; cv ok |  |
| · 6.4 Queuing: `SkillBlastEffectContainer::sbec_Store`  @ FUN_004… | medium | read in code | second reading / client check |
| · · 6.4.1 The MultiHit table: `MultiHitData::MultiHitTable::mht_Loa… | medium | read in code | second reading / client check |
| · 6.5 Firing: `SkillBlastEffect::sbe_BlastObject` / `sbe_BlastLoc… | medium | cap 1/1 | capture (class U) |
| · 6.6 The skill target scanners | medium | read in code | second reading / client check |
| · 6.7 Per-target loops: `alsst_SkillBlast` / `alsst_SkillBlast_Ra… | medium | read in code | second reading / client check |
| · 6.8 Chain blasts ("lightning wave"): `smo_LightningWaveSkill`  … | medium | the captured opcodes are only mentioned here (0x2452 / 0x2457 of Bash [01]); the subject of the section (chain blasts) is in no capture (hand; baseline: high) | capture a chain skill (0x245E) |
| · 6.9 `smo_SkillResultPacket` sends nothing | medium | cap 1/1 | capture (class U) |
| Original-server bugs | medium | cap 6/7; weak inf1; R×1; bug table (class X: effects are deductions) | capture 0x245B |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.37 Z26: `zone/Z26-silver-wing.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data | – | container (see its subsections) |  |
| · 1.1 The item, its actor and its pseudo-skill | medium | read in code | second reading / client check |
| · 1.2 Saved location: the item attribute | medium | cap 1/1 | capture (class U) |
| · 1.3 Menu argument | medium | no function cited | cite and re-read the function |
| · 1.4 Cast fields used (`smo_SkillCast`, p+0x1d84, `SkillCastStru… | medium | silver wing used in no capture: 0x301A is the potion use of batch 3 (hand; baseline: high) | scenario: save a location and fly with a silver wing |
| 2. Flow | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| 3. Using the item (0x3015 → actor) | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 3.1 uib_CanUseItem | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 3.2 uib_DirectUse → sp_SilverWingMenu | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| 4. Menu replies (0x3C02 → `ServerMenuActor::sma_Reply`, Z02 §6.… | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 4.1 Save location | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 4.2 Fly: the portal cast | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 4.3 Cancel | medium | read in code | second reading / client check |
| · 4.4 Menu end without a silver-wing callback | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| 5. Cast end and blast | – | container (see its subsections) |  |
| · 5.1 ShineMobileObject::so_Routine, item branch @ FUN_0056a080 | medium | cap 1/1 | capture (class U) |
| · 5.2 smo_ply_ItemUse (shared, Z13 §9.4) @ FUN_0053fd10 | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 5.3 uib_AfterCast | **high** | cap 2/2 |  |
| · 5.4 sp_SilverWing_PortalBlast: the link | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| · 5.5 Unintended entry: 0x304E NC_ITEM_USE_ACTIVESKILL_REQ @ FUN_… | medium | the captured opcodes are only mentioned here (Dash 0x2450 / 0x2451, the potion use 0x3016 / 0x301A); the subject of the section (0x304E NC_ITEM_USE_ACTIVESKILL_REQ) is in no capture (hand; baseline: high) | test client: send 0x304E |
| 6. Packets and client handlers | medium | silver wing used in no capture: the captured opcodes are the NPC server menu (0x3C01 / 0x3C02), the ride item (0x3015 / 0x3016 / 0x3449) and `&linkto` (0x180D) (hand; baseline: high) | scenario: save a location and fly with a silver wing (part 8) |
| 7. Original-server bugs | medium | cap 8/9; weak inf1; bug table (class X: effects are deductions) | capture (class U) |
| 8. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.38 Z27: `zone/Z27-item-table.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Data structures | – | container (see its subsections) |  |
| · 1.1 `ItemDataBox` (global `itemdatabox` DAT_14d4fb90, size 0x94… | medium | weak inf1 | second reading / client check |
| · 1.2 `ItemDataBox::ItemDataBoxIndex` (one per item ID, size 0x28) | medium | no function cited | cite and re-read the function |
| · 1.3 `SpecialItemIdent` (`idb_specialid`, size 0x52) | medium | no function cited | cite and re-read the function |
| 2. Files and readers | medium | read in code | second reading / client check |
| 3. `ItemDataBox::idb_Load` (stage home) | medium | read in code | second reading / client check |
| · 3.1 Reading the files | medium | read in code | second reading / client check |
| · 3.2 ItemInfo and ItemInfoServer must have the same rows in the … | medium | no function cited | cite and re-read the function |
| · 3.3 Allocating the index | medium | read in code | second reading / client check |
| · 3.4 The per-item pass (index, name trie, ItemDropLog, ItemSort) | medium | read in code | second reading / client check |
| · 3.5 ItemDropLog count check | medium | no function cited | cite and re-read the function |
| · 3.6 GradeItemOption → `itemoption` | medium | no function cited | cite and re-read the function |
| · 3.7 Special IDs, first batch | medium | no function cited | cite and re-read the function |
| · 3.8 WeaponAttrib.shn → `MovingShot`, `AttackAngle`, `HitTimeArr… | medium | read in code | second reading / client check |
| · 3.9 Special IDs, second batch | medium | no function cited | cite and re-read the function |
| · 3.10 ItemInvenDel → `eDelConditionType` | medium | no function cited | cite and re-read the function |
| · 3.11 ItemMoney → `pBuyItemData` | medium | read in code | second reading / client check |
| 4. Special item IDs (`idb_specialid`) | medium | no function cited | cite and re-read the function |
| 5. Accessors over the index | medium | R×1 | second reading / client check |
| 6. The files: column → member maps and 2016 data invariants | – | container (see its subsections) |  |
| · 6.1 ItemInfo.shn → `ItemInfo` (0x17a, 57 columns, 14 989 rows) | medium | no function cited | cite and re-read the function |
| · 6.2 ItemInfoServer.shn → `ItemInfoServer` (0xde, 17 columns, 14… | medium | no function cited | cite and re-read the function |
| · 6.3 GradeItemOption.shn → `GradeItemOption` (0x3e, 16 columns, … | medium | no function cited | cite and re-read the function |
| · 6.4 ItemDropLog.shn → `ItemDropLog` (0x4, 1 column, 57 rows) | medium | no function cited | cite and re-read the function |
| · 6.5 ItemSort.shn → `ItemSort` (0x20, 1 column, 59 rows) | medium | no function cited | cite and re-read the function |
| · 6.6 ItemInvenDel.shn → `ItemInvenDel` (0x24, 2 columns, 19 rows) | medium | no function cited | cite and re-read the function |
| · 6.7 ItemMoney.shn → `ItemMoney` (0x42, 3 columns, 540 rows) | medium | no function cited | cite and re-read the function |
| · 6.8 WeaponAttrib.shn → `WeaponAttrib` (0xd, 4 members / 6 SHN c… | medium | no function cited | cite and re-read the function |
| 7. What the loaded data is used for | – | container (see its subsections) |  |
| · 7.1 Special item IDs: 2016 values and consumers | medium | read in code | second reading / client check |
| · 7.2 Index members: consumers | medium | the captured opcodes are only mentioned here (0x3459 / 0x345A); the subject of the section (the index consumers listed) is in no capture (hand; baseline: high) | second reading |
| · 7.3 `HitTimeArray` and the multi-hit swing | medium | no function cited; weak inf1 | cite and re-read the function |
| 8. Reload behaviour | medium | read in code | second reading / client check |
| Original-server bugs | medium | no function cited; weak inf1; R×1; bug table (class X: effects are deductions) | cite and re-read the function |
| 9. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 10. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.39 Z28: `zone/Z28-card-tables.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The card tables at a glance | medium | read in code | second reading / client check |
| 2. `SHND::CommonData<T, Cmp>`: the template | – | container (see its subsections) |  |
| · 2.1 Layout and vtable | medium | read in code | second reading / client check |
| · 2.2 Construction (static initialisers) | medium | read in code | second reading / client check |
| · 2.3 Loading and the CardID index | medium | read in code | second reading / client check |
| · 2.4 Load order (`ZoneServer::zs_start_long`) | medium | read in code | second reading / client check |
| · 2.5 Finders | medium | cap 0/1 | capture (class U) |
| 3. The files: column → member maps and 2016 data invariants | – | container (see its subsections) |  |
| · 3.1 CollectCard.shn → `CollectCard` (0x2a, 4 columns, 334 rows) | medium | no function cited | cite and re-read the function |
| · 3.2 CollectCardMobGroup.shn → `CollectCardMobGroup` (0x24, 2 co… | medium | no function cited | cite and re-read the function |
| · 3.3 CollectCardDropRate.shn → `CollectCardDropRate` (0x4, 2 col… | medium | no function cited | cite and re-read the function |
| · 3.4 CollectCardStarRate.shn → `CollectCardStarRate` (0x7, 3 col… | medium | no function cited | cite and re-read the function |
| · 3.5 CollectCardReward.shn → `CollectCardReward` (0x4a, 5 column… | medium | no function cited | cite and re-read the function |
| · 3.6 CollectCardTitle.shn → `CollectCardTitle` (0x24, 2 columns,… | medium | no function cited | cite and re-read the function |
| · 3.7 Not loaded by the zone | medium | read in code | second reading / client check |
| · 3.8 The folded DropRate reader also loads `PartyBonusByLvDiff.s… | medium | weak inf1 | second reading / client check |
| 4. The card roll and the card item classes | medium | read in code | second reading / client check |
| · 4.1 Item attribute classes | medium | weak inf2 | second reading / client check |
| · 4.2 `g_CardCollectMake` | medium | read in code | second reading / client check |
| · 4.3 Odds | medium | no function cited | cite and re-read the function |
| · 4.4 Opening: sealed attribute → opened card | medium | cap 1/5 | capture 0xC407 |
| 5. Per-player card state | – | container (see its subsections) |  |
| · 5.1 Containers | medium | read in code | second reading / client check |
| · 5.2 Loading from the WorldManager (0x10E3 / 0x10E6 / 0x10E9) | medium | captured only as empty lists: 0x10E3 / 0x10E6 / 0x10E9 `{5, n 0}` at every map login (capture-validation §7.5; P02-B10); no card collection in a capture (hand; baseline: high) | capture with a collected card, then a map login |
| · 5.3 Changes during the session | medium | cap 6/13; R×1 | capture 0xC40B |
| · 5.4 Reward request: which table columns are used | medium | cap 0/1 | capture (class U) |
| 6. Original-server bugs | medium | cap 1/5; bug table (class X: effects are deductions) | capture 0xC40B |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.40 Z29: `zone/Z29-exp-tables.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Tables and loaders | – | container (see its subsections) |  |
| · 1.1 Load order | medium | weak inf1 | second reading / client check |
| · 1.2 `PartyBonusByMember.shn` → `pebd` (party bonus factor by me… | medium | read in code | second reading / client check |
| · 1.3 `PartyBonusLimit.shn` → `g_MaxExpGainAtGroup` (per-level ex… | medium | read in code | second reading / client check |
| · 1.4 `World/ExpRecalculation.txt` is not read | medium | no function cited | cite and re-read the function |
| 2. Experience split per attacker unit | – | container (see its subsections) |  |
| · 2.1 Data structures | medium | read in code | second reading / client check |
| · 2.2 `el_ExpDistribute` and `ExperienceDistribute::lid_Call` | medium | read in code | second reading / client check |
| · 2.3 Collecting the members near the mob | medium | read in code | second reading / client check |
| · 2.4 The `nfis_*` steps | medium | read in code | second reading / client check |
| · 2.5 The formula | medium | read in code | second reading / client check |
| · 2.6 Corrections to Z03 §8.2 | medium | no function cited | cite and re-read the function |
| 3. Original-server bugs | medium | weak inf1; bug table (class X: effects are deductions) | second reading / client check |
| 4. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 5. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.41 Z30: `zone/Z30-leftovers.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Character rename by item: the zone side (dept 45 USER2) | medium | cap 3/7 | capture 0xB413 |
| · 1.1 GameDB 0xB412 NC_USER_CONNECTION_DB_CHANGE_CHAR_ID_ITEM_USE… | medium | cap 0/3; client×1 | capture 0xB413 |
| · 1.2 WM 0xB40F NC_USER_CONNECTION_ZONE_CHANGE_CHAR_ID_CMD (World… | **high** | cap 2/2; cv ok |  |
| · 1.3 Client 0x4025 NC_CHARSAVE_UI_STATE_SAVE_REQ | **high** | cap 4/4 |  |
| 2. Item dismantling internals (answers Z04 §12.1) | medium | cap 0/3 | capture 0x302B |
| 3. Soul stones: SP use and the queued use (answers Z04 §13.2) | **high** | cap 2/2; client×1; weak inf1; B×4 |  |
| 4. Character title helpers (answers Z08 §7.2) | medium | cap 2/6; client×1 | capture 0x6002, 0x6003 |
| 5. Spam-filter table getters (answers Z02 §3.4) | medium | read in code | second reading / client check |
| 6. Zone ring: holy-promise money transfer and the academy-maste… | – | container (see its subsections) |  |
| · 6.1 0x9436 NC_HOLY_PROMISE_CENTRANSFER_RNG (dead path in 2016) | medium | cap 0/2; client×1 | capture 0x941B |
| · 6.2 Finding an academy member across zones: `ZoneRingPacketFind… | medium | cap 0/5; client×1; weak inf1 | capture 0x181D, 0x9820 |
| 7. Sight and NPC callbacks | medium | read in code | second reading / client check |
| 8. Party, raid and guild helpers | medium | captured: only the guild list at zone start (0x7446 / 0x7447, no guild) and 0x1070; the other opcodes are mentions (0x300D); no party, raid or guild in a capture (hand; baseline: high) | capture-scenarios 15–17 (party / raid), 22 (guild) |
| 9. Remaining helpers | medium | cap 2/10; weak inf1 | capture (class U) |
| 10. Original-server bugs | medium | cap 0/7; R×2; bug table (class X: effects are deductions) | capture 0x181D |
| 11. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 12. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.42 Z31: `zone/Z31-class-remainder.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Work list | medium | no function cited | cite and re-read the function |
| 2. Player and mobile-object members named by `confidence.md` §4… | – | container (see its subsections) |  |
| · 2.1 Guild rename / retype: the commit after the item is consume… | medium | cap 0/10; client×1 | capture 0x74AD, 0x74B5 |
| · 2.2 Item-use checks: `UseItemByTable` and `UseItemSkillDummy2Re… | medium | cap 1/1 | capture (class U) |
| · 2.3 Logout: party slot release (`sp_LogoutDuringParty`) | medium | weak inf2 | second reading / client check |
| · 2.4 `so_ply_BanByServerDisconnect` (vt 0x4b0): no caller | medium | R×1 | second reading / client check |
| · 2.5 Chat-spam block state: load, save to the Character DB and t… | **high** | cap 2/4 |  |
| · 2.6 `so_ply_DecreaseDmgPassiveSkill` (vt 0xd34): the Background… | medium | weak inf1 | second reading / client check |
| · 2.7 Weapon swing interval and reach (vt 0x788 / 0x78c) | medium | read in code | second reading / client check |
| · 2.8 `sp_ChatColor_Save2World` | medium | cap 1/1 | capture (class U) |
| · 2.9 `~ShinePlayer` | medium | weak inf1 | second reading / client check |
| · 2.10 `ShineMobileObject::so_smo_AbnormalStateAttribute` (vt 0xa… | medium | read in code | second reading / client check |
| 3. Inventory lock list, item boxes, item attribute classes | – | container (see its subsections) |  |
| · 3.1 Lock list layout | medium | R×2 | second reading / client check |
| · 3.2 Lock-list vtable: every slot and its callers | medium | read in code | second reading / client check |
| · 3.3 Reserved quantities (`icl_ReservedQuantity`, releaser slot … | medium | read in code | second reading / client check |
| · 3.4 Item boxes, cells and iterators | medium | cap 1/1 | capture (class U) |
| · 3.5 Item attribute classes (`ItemAttributeClass`, 51 slots) | medium | the captured opcodes are only mentioned here (0x1047, 0x3001); the subject of the section (the 51 attribute classes) is in no capture (hand; baseline: high) | per class: the scenario of its item type |
| · · 3.5.1 Items created from a reward row (`iac_itemcreate`, vt 0x1… | medium | read in code | second reading / client check |
| · · 3.5.2 Amulet upgrade options (vt 0x7c / 0x80) | medium | read in code | second reading / client check |
| · · 3.5.3 Weapon licence slots (vt 0x48 … 0x58) | medium | read in code | second reading / client check |
| · 3.6 Item mall goods (`ItemMall`, `ItemShop.shn`) | medium | read in code | second reading / client check |
| · 3.7 Charged inventory, charged buffs, belong attribute: destruc… | medium | read in code | second reading / client check |
| · 3.8 `CellStack`: a path-search tracer, dead in 2016 | medium | read in code | second reading / client check |
| 4. The other `ShinePlayer` members | – | container (see its subsections) |  |
| · 4.1 Unregistered commands: `sp_DummyFunction` | medium | read in code | second reading / client check |
| · 4.2 Packets to the client and the WM | **high** | cap 11/16; client×3; weak p172 |  |
| · 4.3 Character save fillers (WholeSaver) | medium | weak inf1 | second reading / client check |
| · 4.4 Combat factors | medium | read in code | second reading / client check |
| · 4.5 Connection, socket and location | medium | cap 1/2; weak inf1; R×1 | capture (class U) |
| · 4.6 Mini-game (dice Tai Sai) state on the player | medium | read in code | second reading / client check |
| · 4.7 Party, raid and guild state | medium | read in code | second reading / client check |
| · 4.8 NPC menus, trade, booth, tent | **low** | sup×1 (README §5.6) | re-read the rest (§3) |
| · 4.9 Inventory arrange and storage | medium | cap 1/1 | capture (class U) |
| · 4.10 Plain accessors | medium | read in code | second reading / client check |
| · 4.11 Nested-type destructors | medium | read in code | second reading / client check |
| 5. `ShineObject`, `ShineMobileObject` and the other object clas… | – | container (see its subsections) |  |
| · 5.1 Construction, copy and destruction | medium | read in code | second reading / client check |
| · 5.2 Run-time type: `GetRTTI` and `ShineDynamicCast<T>` | medium | read in code | second reading / client check |
| · 5.3 Map removal, handles, start-up | medium | cap 1/1; R×1 | capture (class U) |
| · 5.4 `ShineMobileObject` members | medium | R×3 | second reading / client check |
| · 5.5 `ShineObject` defaults of player slots | medium | R×1 | second reading / client check |
| · 5.6 `ShineObject` defaults of mobile, mob, NPC and effect slots | medium | cap 0/1 | capture 0x202E |
| · 5.7 Folded bodies in the object vtables | medium | read in code | second reading / client check |
| 6. Abstate containers, character classes, attack rhythm, rules … | – | container (see its subsections) |  |
| · 6.1 Abnormal-state containers | medium | cap 1/1 | capture (class U) |
| · 6.2 Character classes (`CharClass`, 29 classes) | medium | read in code | second reading / client check |
| · 6.3 Attack rhythm: the swing animation number (`AttackRhythm`) | medium | cap 1/1 | capture (class U) |
| · 6.4 Rules of engagement: base slots, damage immunity, `EngNormA… | medium | read in code | second reading / client check |
| · 6.5 Mob AI objects | medium | weak p171 | second reading / client check |
| · 6.6 Use effects | medium | read in code | second reading / client check |
| · 6.7 Target analyser, looting, brief-info buffers, skill list | medium | cap 1/1 | capture (class U) |
| 7. Table templates: `BinaryDataBox<T>`, `SHND::CommonData<T, Cm… | – | container (see its subsections) |  |
| · 7.1 `CDataReader`, `BinaryData`, `BinaryDataBox<T>`: layout and… | medium | weak inf1 | second reading / client check |
| · 7.2 `SHND::CommonData<…>` of the gamble tables | medium | read in code | second reading / client check |
| · 7.3 `ITableBase<Row, Table>` singletons and `Table::Load<T>` | medium | read in code | second reading / client check |
| · 7.4 The other `ITableBase` instances: destructors and `GetTotal` | medium | read in code | second reading / client check |
| 8. Other loaders and parsers: item options, random options, soc… | – | container (see its subsections) |  |
| · 8.1 Item option cards (`ItemOptionsData`, `ItemOptions.shn`) | medium | R×1 | second reading / client check |
| · 8.2 Random options of dropped items (`ItemRandomOption::RandomO… | medium | read in code | second reading / client check |
| · 8.3 Gem socket count (`EnchantSocketRateTable`, `EnchantSocketR… | medium | read in code | second reading / client check |
| · 8.4 Accessory upgrades (`AccUpGradeDataBox`, `AccUpGradeTable`) | medium | read in code | second reading / client check |
| · 8.5 Small key tables: `ItemMixData`, `CSingleDataMap`, `CBadNam… | medium | read in code | second reading / client check |
| · 8.6 Area bitmaps (`BmpDataBox`, `BMP.shn`, `AreaBMP/*.bmp`) | medium | read in code | second reading / client check |
| · 8.7 Inventory item-count changes (`ItemLotAnalyser::LotAnalyser… | medium | read in code | second reading / client check |
| · 8.8 `OptionReader` remainder (Z09 §28.6) | medium | read in code | second reading / client check |
| · 8.9 Constructors and destructors of the other loader-owned obje… | medium | R×1 | second reading / client check |
| 9. NPC roles, merchant cities, item authority, booths, repurcha… | – | container (see its subsections) |  |
| · 9.1 NPC role objects (`NPCRoleBase` and its subclasses) | medium | cap 3/8 | capture 0x181F, 0x305B |
| · 9.2 Merchant cities (`MerchantCityData`, `ItemMerchantInfo.shn`) | medium | read in code | second reading / client check |
| · 9.3 Item authority: the box-to-box matrices (`CItemAuthorityBas… | medium | R×1 | second reading / client check |
| · 9.4 Duplicate-menu table, booth search categories, street booth… | medium | read in code | second reading / client check |
| · 9.5 Repurchase list (`CSellItemManager`, `p.sp_SellItemManager`) | **high** | cap 4/4 |  |
| · 9.6 Guild academy buffs, guild and academy storage elements | medium | 0x987A / 0x987B are captured only as the hourly push to a world without a guild; the storage elements are in no capture (hand; baseline: high) | capture-scenarios 22 / 23 (guild, academy) |
| · 9.7 Party table, object finders, map kick | medium | read in code | second reading / client check |
| · 9.8 Events, random slots, cease fire, announce, item list maker… | medium | cap 1/2; R×1 | capture (class U) |
| · 9.9 Constructors and destructors of the other containers | medium | read in code | second reading / client check |
| 10. Sessions, the player send buffer, broadcast visitors, path … | – | container (see its subsections) |  |
| · 10.1 Server-to-server sessions | **high** | cap 2/2 |  |
| · 10.2 The player's send buffer: `PacketContainer` | medium | the captured opcodes are only mentioned here (0x2008, 0x200C); the subject of the section (the `PacketContainer` send buffer) is in no capture (hand; baseline: high) | none on the wire (flush point: capture-scenarios §5 leftovers) |
| · 10.3 Broadcast visitors (`AxialList*`) | medium | cap 1/3; client×1 | capture (class U) |
| · 10.4 Map clusters: copy and teardown | medium | read in code | second reading / client check |
| · 10.5 Path finding: the rest of the dead tracers and `CFindWay` | medium | read in code | second reading / client check |
| · 10.6 Start-up geometry tables | medium | read in code | second reading / client check |
| · 10.7 Library and diagnostic classes | medium | read in code | second reading / client check |
| · 10.8 The remaining destructors | medium | read in code | second reading / client check |
| 11. Open points of Z01-Z04 (`confidence.md` §4.6 rows 5-8) | – | open points / boundary list, no claim to rate |  |
| · 11.1 The handlers' `hnd` argument | medium | cap 0/1 | capture (class U) |
| · 11.2 `p+0x5cb9` bit 2 (`sp_MiscFlag.BeSummoned`) | medium | read in code | second reading / client check |
| · 11.3 Player modes | medium | cap 6/13; client×3; weak p172 | capture 0x202C, 0x203D |
| · 11.4 0x3048 NC_ITEM_EQUIP_BELONGED_CANCEL_USE_REQ: every code | medium | cap 0/4 | capture 0x3049 |
| · 11.5 Auto-arrange: start, steps and end | **high** | cap 4/4; client×1 |  |
| Original-server bugs | medium | cap 7/10; client×2; weak inf4; R×1; bug table (class X: effects are deductions) | capture 0x202C |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.43 Z32: `zone/Z32-gamble-internals.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. TaiSai rules shared by both TaiSai games (`DiceTaiSai`, `Dic… | – | container (see its subsections) |  |
| · 1.1 Tables | medium | read in code | second reading / client check |
| · 1.2 Outcome index and dice | medium | read in code | second reading / client check |
| · 1.3 Outcome classification (`DiceTaiSai::Init`) | medium | read in code | second reading / client check |
| · 1.4 Winning bets of an outcome (`get_PrizeWinningBet`) | medium | read in code | second reading / client check |
| · 1.5 Bet groups, dividends and the bet limit (`DiceTaiSaiDividin… | medium | read in code | second reading / client check |
| · 1.6 Win table (what a rebuild needs) | medium | no function cited; weak inf1 | cite and re-read the function |
| 2. Gamble objects: base class and manager | – | container (see its subsections) |  |
| · 2.1 `CGambleObject` (base of `CGambleDiceTaiSaiObject`, `SlotMa… | medium | B×3 | second reading / client check |
| · 2.2 Base methods | medium | cap 0/1 | capture (class U) |
| · 2.3 Player animation (`go_PlayerAction`, `0xBC1E`) | medium | cap 0/1; client×1; weak inf1 | capture 0xBC1E |
| · 2.4 `CGambleObjectManager` (`gGambleObjectManager` DAT_14d70e58… | medium | cap 0/1 | capture (class U) |
| · 2.5 `GBReward` table | medium | read in code | second reading / client check |
| 3. Gamble-house TaiSai table (`CGambleDiceTaiSaiObject`) | – | container (see its subsections) |  |
| · 3.1 Layout, tables, states | medium | cap 0/2 | capture 0xBC80, 0xBC81 |
| · 3.2 Construction and initialisation | medium | read in code | second reading / client check |
| · 3.3 Player-side gamble state (`ShinePlayer::so_Gamble_*`) | **high** | cap 2/2 |  |
| · 3.4 Gamer records | medium | read in code | second reading / client check |
| · 3.5 Joining | medium | cap 0/5; client×3; R×1 | capture 0xBC65, 0xBC66, 0xBC67 |
| · 3.6 Betting, cancelling and the betting timer | medium | cap 0/3; client×1 | capture 0xBC73, 0xBC76, 0xBC81 |
| · 3.7 Leaving | medium | cap 0/4; client×1 | capture 0xBC6A, 0xBC80, 0xBC81 |
| · 3.8 Round routine and the round reset | medium | cap 0/3; client×1 | capture 0xBC6A, 0xBC80 |
| · 3.9 GM: fixed throw and outcome weights | medium | read in code | second reading / client check |
| · 3.10 Roll, result and payout | medium | cap 1/11; client×4; R×1 | capture 0xBC69, 0xBC6A, 0xBC77, 0xBC7B … |
| · 3.11 Unmarking and the logout gate | medium | cap 0/1; weak inf1 | capture 0xBC69 |
| · 3.12 Worked example round | medium | cap 1/10 | capture 0xBC77, 0xBC7B, 0xBC7C, 0xBC7F … |
| 4. Slot machines (`SlotMachine::*`) | – | container (see its subsections) |  |
| · 4.1 Tables and the three singletons | medium | cap 1/1 | capture (class U) |
| · 4.2 Symbol draw (`smsm_Action`) | medium | cap 0/2; weak inf1 | capture 0xBCCF |
| · 4.3 Patterns (`SlotMachineAnalyse`, `sms_LineRate`) | medium | read in code | second reading / client check |
| · 4.4 Jackpot pools (`SlotMachineJackPotRanking`) | medium | read in code | second reading / client check |
| · 4.5 Stop button: payout and settlement request (`SMS_StopButton… | medium | cap 0/7; client×1; weak dbb1; R×1 | capture 0xBCCF, 0xBCD1, 0xBCDD |
| · 4.6 Payout table (what a rebuild needs) | medium | cap 0/3 | capture 0xBCCF, 0xBCDD |
| · 4.7 Cluster and screen objects | medium | read in code | second reading / client check |
| · 4.8 Joining, leaving and unmarking | medium | cap 0/7; client×1 | capture 0xBC1C, 0xBC65, 0xBCC9, 0xBCCB … |
| · 4.9 Spin state machine: start, settlement answer, wheel stop | medium | cap 1/7; client×2; weak inf1 dbb1; R×1 | capture 0xBCCD, 0xBCD1 |
| · 4.10 Screen routine: idle kick and jackpot display | medium | cap 0/2; client×1; weak inf1; R×1 | capture 0xBCD2, 0xBCD8 |
| · 4.11 Jackpot pools from the DB, rankings, jackpot broadcast | medium | cap 2/9; client×2 | capture 0xBCDA, 0xBCDC, 0xBCDD |
| 5. Sweep additions: table loaders, base stubs, player accessors… | – | container (see its subsections) |  |
| · 5.1 Loaders of the shared GB tables | medium | read in code | second reading / client check |
| · 5.2 Base `GDTSO_*` stubs | medium | read in code | second reading / client check |
| · 5.3 Player-side mini-house TaiSai accessors (`sp_MiniGame`) | medium | read in code | second reading / client check |
| · 5.4 Coin items and the merchant's coin price | medium | the captured opcodes are only mentioned here (0x3015 / 0x3016 of the ride item); the subject of the section (coin items 0xBC19 / 0xBC1A) is in no capture (hand; baseline: high) | capture: use a coin item |
| · 5.5 Coin reservations in the lock list's reserved quantities | medium | read in code | second reading / client check |
| · 5.6 The jackpot reward's item list | medium | cap 0/1 | capture (class U) |
| 6. Original-server bugs | medium | cap 1/10; weak inf1 dbb1; R×1; bug table (class X: effects are deductions) | capture 0xBC65, 0xBC6A, 0xBCC9, 0xBCCF … |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 8. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.44 D01: `db/D01-account.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process structure (both servers) | **low** | sup×2 (README §5.7) | re-read the rest (§3) |
| · 1.1 Helpers used by every handler | **low** | B×1 | follow the return value to the parser |
| · 1.2 Copies of shared and library code (address aliases) | medium | cap 0/1 | capture (class U) |
| 2. Server-link handlers (CPFs, identical code in both binaries) | **low** | cap 5/14; sup×2 (README §5.7); B×1 | re-read the rest (§3); follow the return value to the parser |
| 3. Account server (CParserAccount, registered @ FUN_00404520) | medium | read in code | second reading / client check |
| · 3.1 Handlers that do nothing | medium | cap 4/4; capture shows the link packets, not the SQL | capture (class U) |
| · 3.2 Login checks (the result codes behind Login's 0x45 / 0x47 /… | medium | cap 4/15; weak dbb4 | capture (class U) |
| · 3.3 Return-user ("comeback") checks, for the WM | **low** | cap 2/3; sup×1 (README §5.7); weak dbb1; capture shows the link packets, not the SQL | re-read the rest (§3) |
| · 3.4 Web key, PC-bang, events, teen protection | **low** | cap 2/13; sup×2 (README §5.7); weak inf1 dbb1 | re-read the rest (§3) |
| 4. AccountLog server (CParserAccountLog) | medium | read in code | second reading / client check |
| · 4.1 Account log (`p_AccountLog_Add` → `tAccountLog`) | **low** | cap 4/4; sup×1 (README §5.7); cv corr; weak dbb1; capture shows the link packets, not the SQL | re-read the rest (§3); read with P02 "Corrections" |
| · 4.2 Statistics, events | medium | cap 2/6; cv ok; sup×2 (README §5.7); cv corr; weak inf1 dbb3 | re-read the rest (§3); read with P02 "Corrections"; code or capture for the marked statements |
| · 4.3 IP block checks (the source of Login's 0x51) | medium | cap 3/11; weak dbb1 | capture (class U) |
| · 4.4 Logout day, user reports | **low** | cap 0/11; sup×1 (README §5.7); weak inf1 dbb3 | re-read the rest (§3); code or capture for the marked statements; capture 0x8002, 0x8004, 0x8006 |
| · 4.5 Syslog lines (NC_SYSLOG_*) | **low** | cap 4/4; sup×2 (README §5.7); weak inf1 p171; capture shows the link packets, not the SQL | re-read the rest (§3) |
| 5. Procedures called, by server | **low** | cap 1/1; R×1 | callers incl. vtable slots; senders in every `handlers.json` |
| 6. Original-server bugs | medium | cap 2/19; weak dbb1; bug table (class X: effects are deductions) | capture (class U) |
| 7. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.45 D02: `db/D02-character.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process structure | **low** | sup×3 (README §5.7) | re-read the rest (§3) |
| · 1.1 Helpers used by every handler | **low** | sup×1 (README §5.7) | re-read the rest (§3) |
| 2. Server-link handlers (CPFs, registered @ FUN_0043d2f0) | **low** | cap 5/10; sup×1 (README §5.7); B×1; capture shows the link packets, not the SQL | re-read the rest (§3); follow the return value to the parser |
| 3. Avatars (char select): list, create, delete, rename, guild | medium | cv ok; no function cited; sup×1 (README §5.7); no PDB | re-read the rest (§3) |
| · 3.1 Avatar list | **low** | cap 3/3; weak inf1 dbb3; capture shows the link packets, not the SQL | code or capture for the marked statements |
| · 3.2 GetAvatarInfo (the 130-byte AVATAR record) | **low** | cap 1/1; sup×2 (README §5.7); cv corr; D: `p_Char_GetLoginData` differ between the backups; weak inf1 | re-read the rest (§3); read with P02 "Corrections"; D06 §8.5 version |
| · 3.3 Create | medium | cap 6/6; cv ok; client×1; D: `p_Char_Create`, `p_Quest_Set` differ between the backups; weak dbb2 | D06 §8.5 version |
| · 3.4 Delete | **high** | cap 3/4; cv ok; client×1; weak dbb2 |  |
| · 3.5 Rename (char select) and guild data | medium | cap 5/7; cv ok; cv corr; D: `p_Char_Rename` differ between the backups | read with P02 "Corrections"; D06 §8.5 version |
| · 3.6 Item list helper (shared with D03) | medium | no PDB | second reading / client check |
| 4. Character load: 0x1004 NC_CHAR_CHARDATA_REQ (CParserCharacte… | medium | cap 38/54; cv ok; client×2; sup×7 (README §5.7); cv corr; D: `p_Char_GetStateAllWithSetItemAndRestTime`, `p_Quest_GetAllDoing`, `usp_Character_getSingleOption` differ between the backups | re-read the rest (§3); read with P02 "Corrections"; D06 §8.5 version; capture 0x1010, 0x1011, 0x1C13 |
| · 4.1 GetCharBaseData: `p_Char_GetAllData` → `PROTO_NC_CHAR_BASE_… | **low** | cap 1/1; sup×2 (README §5.7); weak dbb1; capture shows the link packets, not the SQL | re-read the rest (§3) |
| 5. Login, logout, loading report | **low** | cap 5/6; sup×2 (README §5.3, §5.7); cv corr; weak inf1 dbb2; D: `p_Char_Login`, `p_Char_Logout` differ between the backups; capture shows the link packets, not the SQL | re-read the rest (§3); read with P02 "Corrections"; code or capture for the marked statements; D06 §8.5 version |
| 6. Character saves from the zone (dept 16 CHARSAVE) | medium | cap 13/24; cv ok; sup×2 (README §5.7); cv corr; D: `p_Quest_Set` differ between the backups; weak dbb1 | re-read the rest (§3); read with P02 "Corrections"; D06 §8.5 version |
| 7. Class, stats, fame, name check | – | container (see its subsections) |  |
| · 7.1 Class change, legacy stat points, fame, registration check | medium | cap 10/23; cv ok; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x1096 |
| · 7.2 Free-stat save: 0x10D1 NC_CHAR_FREESTAT_SET_DB_REQ (answers… | medium | cap 5/9; cv ok; sup×1 (README §5.7); weak inf2 dbb1 | re-read the rest (§3); code or capture for the marked statements; capture 0x1096 |
| 8. Tutorial | medium | cap 2/4; capture shows the link packets, not the SQL | capture (class U) |
| 9. Misc (chat bans, spam filter, guide, item shop URL, ping tes… | **low** | cap 2/15; sup×2 (README §5.7); D: `usp_Character_setChatBan` differ between the backups | re-read the rest (§3); D06 §8.5 version; capture 0x0812, 0x0813, 0x3043 |
| 10. Item lists by storage type, beauty shop | medium | cap 4/11; weak inf1 | capture 0x1079 |
| 11. Wedding (tMarriage) — answers the Z07 §5 questions | **low** | cap 2/27; cv ok; sup×1 (README §5.7); weak dbb4; D: `p_Char_Wedding_Divorce_by_Agree`, `p_Char_Wedding_Divorce_by_Force`, `p_Char_Wedding_Do` differ between the backups | re-read the rest (§3); code or capture for the marked statements; D06 §8.5 version |
| 12. Attendance event | **low** | cap 3/7; sup×2 (README §5.7); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| 13. Promotion (event) user and reward | **low** | cap 1/6; sup×1 (README §5.7) | re-read the rest (§3) |
| 14. Character rename with a rename item (dept 45) | medium | cap 5/7; cv ok; D: `usp_Character_setChangeID` differ between the backups; weak dbb1 | D06 §8.5 version |
| 15. Procedures called by these handlers | **low** | cap 18/37; sup×2 (README §5.7); D: `p_Char_Create`, `p_Char_GetLoginData`, `p_Char_GetStateAllWithSetItemAndRestTime` … differ between the backups | re-read the rest (§3); D06 §8.5 version |
| Original-server bugs | **low** | cap 9/23; sup×2 (README §5.7); weak inf2 dbb1; D: `p_Char_Create`, `usp_Character_setChatBan` differ between the backups; R×1; bug table (class X: effects are deductions) | re-read the rest (§3); code or capture for the marked statements; D06 §8.5 version; callers incl. vtable slots; senders in every `handlers.json` |
| 16. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.46 D03: `db/D03-character-items.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Item persistence model | – | container (see its subsections) |  |
| · 1.1 Tables (as the procedures use them, *(db-backup)*) | **low** | no function cited; sup×1 (README §5.7) | re-read the rest (§3) |
| · 1.2 Item helpers | medium | cv ok; D: `p_Item_BuyAll` differ between the backups; weak dbb2; no PDB | D06 §8.5 version |
| · 1.3 Attribute storage: `ItemAttr_Save` @ FUN_0046a730 and `Item… | medium | weak p171; no PDB | second reading / client check |
| · 1.4 Item lists sent to the zone | medium | no PDB | second reading / client check |
| · 1.5 Holy-promise cen reward | medium | no PDB | second reading / client check |
| 2. Shop (CParserCharacter, registered @ FUN_0043b040) | **high** | cap 2/2; cv ok |  |
| · 2.1 NPC purchase | medium | cap 5/8; cv ok; D: `p_Item_BuyLot` differ between the backups; weak dbb1 | D06 §8.5 version |
| · 2.2 Sell and repurchase | medium | cap 12/14; cv ok; cv corr; D: `p_Item_BuyLot` differ between the backups; weak dbb2 | read with P02 "Corrections"; D06 §8.5 version |
| · 2.3 Guild-token purchase (into guild storage) | medium | cap 1/8; weak dbb1 | capture (class U) |
| · 2.4 Soul stones | medium | cap 2/4; cv ok; sup×1 (README §5.7); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 2.5 Capsule purchase | medium | cap 2/4; capture shows the link packets, not the SQL | capture (class U) |
| · 2.6 Item-money purchase (paying with an item, e.g. tokens / med… | medium | cap 4/9 | capture (class U) |
| 3. Inventory: equip, move, stack, drop, pick, money | medium | weak dbb1; no PDB | second reading / client check |
| · 3.1 Equip / unequip | **low** | cap 5/8; weak dbb3; capture shows the link packets, not the SQL | code or capture for the marked statements |
| · 3.2 Relocation and exchange (inventory ↔ storage ↔ other owner) | medium | cap 5/7; weak dbb2; capture shows the link packets, not the SQL | capture (class U) |
| · 3.3 Merge and split | medium | cap 8/11; cv ok; cv corr; weak dbb1 | read with P02 "Corrections" |
| · 3.4 Drop and pick-up | **low** | cap 9/18; sup×1 (README §5.7); cv corr; capture shows the link packets, not the SQL | re-read the rest (§3); read with P02 "Corrections" |
| · 3.5 Money | medium | cap 3/8; weak dbb1 | capture (class U) |
| 4. Using and changing items | **high** | cap 7/7; cv ok |  |
| 5. Storage | – | container (see its subsections) |  |
| · 5.1 Account storage (shared by the account's characters) and it… | medium | cap 8/9; cv ok; sup×2 (README §5.7); cv corr; weak dbb1 | re-read the rest (§3); read with P02 "Corrections" |
| · 5.2 Guild storage | medium | cap 0/6; weak dbb1; no PDB | capture (class U) |
| · 5.3 Guild-academy reward storage | **low** | cap 0/8; D: `usp_GuildAcademy_withdrawMoney` differ between the backups; weak dbb1 | D06 §8.5 version |
| · 5.4 Premium ("charged") items from the item shop | medium | cap 5/9; weak dbb1; capture shows the link packets, not the SQL | capture (class U) |
| 6. Upgrades, enchanting and item services | medium | cap 2/2; capture shows the link packets, not the SQL | capture (class U) |
| · 6.1 Upgrade (`p_Item_Upgrade_CelllInAll`) | **low** | cap 4/17; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x3803, 0x3809, 0x3C04, 0x3C06 … |
| · 6.2 Enchanting (gem sockets, `tItemEnchant`) | medium | cap 0/9; weak dbb1; no PDB | capture 0x2082 |
| · 6.3 Mounts (movers) | medium | cap 0/6; no PDB | capture (class U) |
| · 6.4 Random options | medium | cap 2/11 | capture (class U) |
| · 6.5 Other item services | **low** | cap 2/16; sup×1 (README §5.7); weak p171 dbb2 | re-read the rest (§3); code or capture for the marked statements |
| · 6.6 Dismantle, endurance, bound items, reinforce | medium | cap 1/18; weak dbb1 | capture (class U) |
| 7. Creating, opening and destroying items | medium | no PDB | second reading / client check |
| · 7.1 Direct creation | medium | cap 5/15 | capture (class U) |
| · 7.2 Item lists (scripts, quests, events) @ FUN_00432090 | **low** | cap 1/5; sup×1 (README §5.7) | re-read the rest (§3) |
| · 7.3 Chests and capsules | medium | cap 2/11 | capture (class U) |
| · 7.4 Mystery vault, card rebuild, item info | medium | cap 4/10 | capture (class U) |
| · 7.5 Breaking, destroying, producing, quest rewards | medium | cap 5/15; weak inf1 | capture (class U) |
| · 7.6 Mini-house resources | medium | cap 0/3; no PDB | capture (class U) |
| 8. Mini-house (dept 35, CParserCharacter) | **low** | cap 0/12; sup×1 (README §5.7); weak inf1 dbb4 | re-read the rest (§3); code or capture for the marked statements |
| 9. Premium buffs and re-initialise items (dept 36) | medium | cap 6/28; cv ok; weak dbb1 | capture (class U) |
| 10. Dice "TaiSai" game machine (dept 43) | **low** | cap 0/11; weak dbb3; D: `usp_Dice_setDicePay`, `usp_Dice_setDiceResult` differ between the backups | code or capture for the marked statements; D06 §8.5 version; capture 0xAC2C |
| 11. Gamble coins, house dice and slot machines (dept 47) | **low** | cap 2/34; sup×1 (README §5.7); weak dbb3 | re-read the rest (§3); code or capture for the marked statements; capture 0x1C12 |
| 12. Card collection (dept 49) | **low** | cap 1/11; sup×1 (README §5.7); weak dbb2 | re-read the rest (§3) |
| 13. Pets (dept 53) | **low** | cap 3/17; sup×1 (README §5.7) | re-read the rest (§3) |
| 14. Trade and booths (Z06 owns the windows) | medium | cap 0/12; weak dbb2; no PDB | capture (class U) |
| 15. Procedures called by these handlers | **low** | cap 1/2; sup×1 (README §5.7); D: `p_Item_BuyAll`, `p_Item_BuyLot`, `usp_Dice_setDicePay` … differ between the backups | re-read the rest (§3); D06 §8.5 version |
| Original-server bugs | **low** | cap 17/55; D: `p_Item_BuyAll` differ between the backups; bug table (class X: effects are deductions) | D06 §8.5 version |
| 16. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 17. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.47 D04: `db/D04-character-social.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Quests (dept 17, CParserCharacter) | – | container (see its subsections) |  |
| · 1.1 Store one record | **low** | sup×1 (README §5.7); D: `p_Quest_Set` differ between the backups; weak dbb1 | re-read the rest (§3); D06 §8.5 version |
| · 1.2 Handlers | **low** | cap 0/19; R×1; weak inf1 dbb1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x4408 |
| 2. Skills (dept 18, CParserCharacter) | medium | cap 6/13; cv ok; weak dbb6 | code or capture for the marked statements |
| 3. Friends (dept 21) and the kingdom-quest reward (dept 22) | **low** | cap 0/17; sup×1 (README §5.7); weak dbb3 | re-read the rest (§3); code or capture for the marked statements; capture 0x1010, 0x5402, 0x5406 |
| 4. Weapon licences (dept 23 WEAPONTITLE) and character titles (… | medium | cap 0/4; weak dbb1; no PDB | capture (class U) |
| · 4.1 Weapon licences | medium | cap 2/12; weak dbb2 | capture 0x5C02 |
| · 4.2 Character titles | medium | cap 3/6; capture shows the link packets, not the SQL | capture (class U) |
| 5. Character options (dept 28 CHAR_OPTION), requests from the WM | – | container (see its subsections) |  |
| · 5.1 Old options (`p_Char_GetOpt*` / `p_Char_SetOpt*`) | medium | cap 7/21; weak dbb2 | capture (class U) |
| · 5.2 Improved options | **low** | cap 4/11; sup×1 (README §5.7); weak dbb7 | re-read the rest (§3); code or capture for the marked statements |
| 6. Guilds (dept 29 GUILD), requests from the WM | **low** | cap 0/7; sup×1 (README §5.7); weak dbb1 | re-read the rest (§3) |
| · 6.1 Loading guilds | **low** | cap 2/7; weak inf1 dbb2 | code or capture for the marked statements |
| · 6.2 Creating, deleting, dismissing | medium | cap 0/10; weak dbb2; no PDB | capture (class U) |
| · 6.3 Money, notice, introduction, war, members | **low** | cap 0/22; weak dbb5; D: `p_Guild_Member_SetGrade` differ between the backups | code or capture for the marked statements; D06 §8.5 version |
| · 6.4 Guild tournament | **low** | cap 5/32; sup×2 (README §5.7); weak inf1 dbb6; D: `usp_GuildTournament_setRegist` differ between the backups | re-read the rest (§3); code or capture for the marked statements; D06 §8.5 version |
| · 6.5 Rename, type, tokens, history | **low** | cap 2/8; weak p171 dbb2 | code or capture for the marked statements |
| · 6.6 Guild emblems (private-server procedures) | medium | cap 2/6 | capture (class U) |
| 7. Prison (dept 31, `NC_DATA_PRISON_*`), requests from the WM | **low** | cap 0/7; client×2; sup×2 (README §5.7); weak dbb5; D: `p_Prison_Add`, `p_Prison_Add2`, `p_Prison_UpdateCharPrisonMin` differ between the backups | re-read the rest (§3); code or capture for the marked statements; D06 §8.5 version |
| 8. Holy promise (master / apprentice, "Monarch"; dept 37) | **low** | cap 6/22; weak dbb7 | code or capture for the marked statements |
| 9. Guild academy (dept 38 GUILD_ACADEMY), requests from the WM … | medium | cap 0/6; no PDB | capture 0x982F |
| · 9.1 Loading and ranking | **low** | cap 4/14; D: `usp_GuildAcademy_getMemberList` differ between the backups; weak dbb2 | D06 §8.5 version |
| · 9.2 Members | medium | cap 0/24; weak dbb1; no PDB | capture 0x982F |
| · 9.3 Graduates and rewards | **low** | cap 0/19; sup×1 (README §5.7); D: `usp_GuildAcademy_withdrawMoney` differ between the backups; weak dbb1 | re-read the rest (§3); D06 §8.5 version |
| 10. Chat block list (dept 42 CHAT_RESTRICT), requests from the … | medium | cap 5/16; weak dbb1 | capture 0x1C07, 0x1C10, 0x1C13, 0x1C14 |
| 11. Procedures and helpers reached by these handlers | **low** | cap 0/1; D: `p_Guild_Member_SetGrade`, `p_Prison_Add`, `p_Prison_Add2` … differ between the backups | D06 §8.5 version |
| Original-server bugs | medium | cap 4/33; bug table (class X: effects are deductions) | capture (class U) |
| 12. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 13. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.48 D05: `db/D05-gamelog.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process and storage | – | container (see its subsections) |  |
| · 1.1 Process (the DataServer framework of D01 §1) | **low** | cap 0/1; sup×1 (README §5.7) | re-read the rest (§3) |
| · 1.2 `tGameLog` and the procedures | **low** | cap 1/2; sup×1 (README §5.7); weak dbb2 | re-read the rest (§3) |
| · 1.3 The handler skeleton | medium | weak p171; no PDB | second reading / client check |
| 2. NC_LOG_GAME handlers, commands 1–84 (CParserGameLog, part 1) | – | container (see its subsections) |  |
| · 2.1 Generic add with and without answer | **low** | cap 2/5; B×1 | follow the return value to the parser |
| · 2.2 Login: two procedures | **low** | cap 1/1; sup×1 (README §5.7); weak inf1 | re-read the rest (§3) |
| · 2.3 All handlers of this part | **low** | cap 17/52; cv ok; weak inf1 p1711; D: `p_GameLog_Add_Type6` differ between the backups; B×1 | code or capture for the marked statements; D06 §8.5 version; follow the return value to the parser |
| · 2.4 Commands no 2016 server sends | **low** | cap 0/23; R×2 | callers incl. vtable slots; senders in every `handlers.json` |
| 3. NC_LOG_GAME handlers, commands 85–857 (CParserGameLog, part … | – | container (see its subsections) |  |
| · 3.1 All logging handlers of this part | medium | cap 6/61; weak p171 | capture (class U) |
| · 3.2 Notes on single rows and the zone senders | **low** | cap 2/22; weak inf2 p171 | code or capture for the marked statements |
| · 3.3 Commands no 2016 server sends; no-op registrations | medium | cap 0/32; weak p171; no PDB | capture (class U) |
| 4. NC_LOG handlers, commands 858–1021 (CParserGameLog, part 3) | medium | cap 0/1; no PDB | capture (class U) |
| · 4.1 Guild academy rewards, MK2, mover, item money, random optio… | medium | cap 0/21; weak p171; ours×1; no PDB | capture (class U) |
| · 4.2 Notes on the part-3 rows | **low** | cap 0/10; R×1 | callers incl. vtable slots; senders in every `handlers.json` |
| · 4.3 NC_LOG_GAME_DATA_TYPE_0…L: one command per procedure | **low** | cap 1/22; weak p174 | code or capture for the marked statements |
| · 4.4 Zone script and tutorial senders | medium | cap 0/2; weak inf1; no PDB | capture (class U) |
| 5. Server-link handlers (CPFs, registered @ FUN_00409640 CPFs_c… | **low** | cap 5/14; sup×1 (README §5.7); B×1; weak p171 | re-read the rest (§3); follow the return value to the parser |
| 6. NC_SYSLOG handlers: text log for the data warehouse (dept 50… | – | container (see its subsections) |  |
| · 6.1 The log file | medium | weak inf1; no PDB | second reading / client check |
| · 6.2 The fourteen messages | medium | cap 11/14; capture shows the link packets, not the SQL | capture (class U) |
| 7. Process framework (part 4 sweep) | medium | cap 0/1; no PDB | capture (class U) |
| · 7.1 Start, Windows service, shutdown | **low** | sup×1 (README §5.7); R×1 | re-read the rest (§3); callers incl. vtable slots; senders in every `handlers.json` |
| · 7.2 Sessions: accept, receive, framing, heartbeat, close | **low** | cap 4/5; sup×1 (README §5.7); B×1; capture shows the link packets, not the SQL | re-read the rest (§3); follow the return value to the parser |
| · 7.3 ODBC connection | medium | no PDB | second reading / client check |
| · 7.4 Diagnostics: debug log, crash dump, asserts, scriptor report | medium | weak inf2; no PDB | second reading / client check |
| · 7.5 Linked-in code that no GameLog path uses | **low** | sup×1 (README §5.7) | re-read the rest (§3) |
| 8. Original-server bugs | medium | cap 2/9; bug table (class X: effects are deductions) | capture (class U) |
| 9. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 10. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.49 D06: `db/D06-db-inferred.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Conventions | – | container (see its subsections) |  |
| · 1.1 How a procedure block reads | medium | no function cited; weak inf1 | cite and re-read the function |
| · 1.2 ODBC codes in the binds | medium | no function cited | cite and re-read the function |
| 2. Account DB (`Account`, Account server) | medium | cap 1/8 | capture (class U) |
| · 2.1 `usp_Pcbang_chkIP` — PC-bang (internet café) IP check | medium | cap 0/3; weak inf1 | capture (class U) |
| · 2.2 `usp_Event_addCash` — event cash for an account ID | medium | cap 0/1; weak inf1 dbb1 | capture (class U) |
| · 2.3 Teen protection: `p_UserKey_Get_FromAccount`, `p_UserPlayRe… | medium | cap 0/3 | capture (class U) |
| · 2.4 Region logins: `usp_User_LoginNetmarble`, `usp_User_LoginGa… | **low** | cap 0/9; weak inf4 dbb2 | code or capture for the marked statements |
| · 2.5 Other Account login statements of D01 | medium | no function cited; weak dbb1 | cite and re-read the function |
| 3. AccountLog DB (`AccountLog`) and Statistics DB (`StatisticsD… | medium | cap 1/5; R×1 | capture (class U) |
| · 3.1 `p_SameTimeCharClass_Add` — concurrent players per class (S… | medium | cap 1/1; weak inf1 | capture (class U) |
| · 3.2 `p_Event_L20_Get` — has the account already had the level-2… | medium | cap 0/1 | capture (class U) |
| · 3.3 `p_Event_L20_Set` — record the reward | medium | cap 0/1; weak inf1 | capture (class U) |
| · 3.4 `usp_AccountLog_GetDateDiffLastlogout` — seconds since the … | medium | cap 2/3; weak inf2; capture shows the link packets, not the SQL | capture (class U) |
| · 3.5 Version check of the AccountLog / Statistics procedures tha… | medium | read in code | second reading / client check |
| 4. GameLog DB (`w00_GameLog`), GameLog server | – | container (see its subsections) |  |
| · 4.1 `usp_Login_setChannel` — the client channel tag of each cha… | medium | cap 3/3; weak inf1; capture shows the link packets, not the SQL | capture (class U) |
| · 4.2 `p_GameLog_Add_Type6` version (D05 §1.2 open point) | medium | no function cited; weak dbb1 | cite and re-read the function |
| 5. Character DB (`w00_Character`), Character server: pets, link… | – | container (see its subsections) |  |
| · 5.1 Pets: `usp_Pet_setCreate`, `usp_Pet_getInfo`, `usp_Pet_setN… | medium | cap 3/16; weak inf1 dbb1 | capture (class U) |
| · 5.2 `usp_LinkScroll_SetDestMap` — remember where a map-link scr… | medium | cap 1/2 | capture (class U) |
| · 5.3 `p_Item_MiniHouse_Effect_Resource_Del` — pay a mini-house f… | medium | cap 0/2; weak inf1 | capture 0x8C41 |
| · 5.4 `p_MiniHouseURL_Get`, `p_MiniHouseURL_Set` — the house owne… | medium | cap 0/6 | capture 0x8C36, 0x8C38 |
| · 5.5 `p_Guild_SetMoney` — set a guild's money | medium | cap 0/1 | capture (class U) |
| · 5.6 `usp_GuildTournament_setRefundNotice` — mark a refund as an… | medium | cap 0/3; weak inf1 | capture 0x74F8 |
| · 5.7 D04 version mismatches | medium | cap 3/8; weak inf1 | capture (class U) |
| 6. Character DB (`w00_Character`), Character server: loading re… | – | container (see its subsections) |  |
| · 6.1 Loading-failure reports: `usp_CharacterLoading` (11 vs 6), … | medium | cap 0/2; weak inf1 dbb1 | capture (class U) |
| · 6.2 `p_Char_GetAllData` column 37 (D02-B19): the map-link scrol… | medium | cap 1/2 | capture (class U) |
| · 6.3 `usp_Character_setFriendpoint` (2 markers, 3 binds) and `us… | medium | cap 2/4; weak inf1; capture shows the link packets, not the SQL | capture (class U) |
| · 6.4 Promotion: `p_IsPromotionUser`, `p_Promotion_Get`, `p_Promo… | medium | cap 0/5; weak inf1 p171 | capture (class U) |
| · 6.5 `usp_Character_setStatPoint` −1091 / −1092 / −1094 | medium | cap 2/4; weak inf1; capture shows the link packets, not the SQL | capture 0x1096 |
| 7. SQL built at run time (all four DB servers) | – | container (see its subsections) |  |
| · 7.1 Inventory: how the four servers reach SQL Server | medium | read in code | second reading / client check |
| · 7.2 `p_Char_SetStateWithSetItemAndRestTime` — save one abnormal… | medium | cap 2/2; weak inf3; capture shows the link packets, not the SQL | capture (class U) |
| · 7.3 Connection startup command (`ODBC_INFO` column 5, `DBRecord… | medium | read in code | second reading / client check |
| 8. Version choices for Character procedures that have source (D… | – | container (see its subsections) |  |
| · 8.1 `p_Item_BuyAll` (10) / `p_Item_BuyLot` (8): follow w00 | medium | read in code | second reading / client check |
| · 8.2 `usp_Character_setChatBan`: follow w00 | medium | cap 0/2 | capture (class U) |
| · 8.3 `usp_Gamble_addCoin` and D03-B21 | medium | cap 0/10; weak inf1; R×1 | capture (class U) |
| · 8.4 Enchant procedures (`usp_Item_*Enchant*`): follow w00 | medium | read in code | second reading / client check |
| · 8.5 Version sweep: every called procedure that exists in two ba… | medium | cap 4/7; capture shows the link packets, not the SQL | capture (class U) |
| · 8.6 Other open DB statements of D01–D05 settled in the sweep | **low** | cap 0/9; client×1; weak inf2 dbb2 | code or capture for the marked statements; capture 0x205D |
| 9. Table schema of the 2016 servers | – | container (see its subsections) |  |
| · 9.1 Source and method | medium | no function cited; weak dbb1 | cite and re-read the function |
| · 9.2 Types: what the 2016 binds put into these columns | medium | read in code | second reading / client check |
| · 9.3 Tables (from the restore) | – | container (see its subsections) |  |
| · · `Account` | medium | no function cited | cite and re-read the function |
| · · `AccountLog` | medium | no function cited | cite and re-read the function |
| · · `StatisticsData` | medium | no function cited | cite and re-read the function |
| · · `w00_Character` | medium | no function cited | cite and re-read the function |
| · · `w00_GameLog` | medium | no function cited | cite and re-read the function |
| · 9.4 Private-server additions in the restored tables | medium | no function cited | cite and re-read the function |
| · 9.5 Seed rows a rebuild must load | medium | no function cited; weak inf1 | cite and re-read the function |
| · 9.6 Tables and columns the 2016 servers need that no backup has… | medium | cap 1/1 | capture (class U) |
| · 9.7 `Character.bak` / `GameLog.bak` against the w00 copies | medium | no function cited | cite and re-read the function |
| 10. Original-server bugs | medium | cap 0/6; weak inf1; R×1; bug table (class X: effects are deductions) | capture 0x74F8 |
| 11. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 12. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.50 D07: `db/D07-character-reward-items.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Helpers shared by both handlers | – | container (see its subsections) |  |
| · 1.1 Item records of the academy reward storage | medium | cap 0/1; weak dbb1; no PDB | capture (class U) |
| · 1.2 Lot helpers | medium | no PDB | second reading / client check |
| · 1.3 Item attribute classes (`g_ItemAttrClassContainer`) | medium | cap 0/1; weak p172; no PDB | capture (class U) |
| 2. 0x986B NC_GUILD_ACADEMY_DB_ACADEMY_REWARD_REQ (from the zone… | medium | cap 0/3; no PDB | capture (class U) |
| · 2.1 Layouts | medium | cap 0/3; weak p171; no PDB | capture (class U) |
| · 2.2 Reading the configured reward | medium | cap 0/2; weak dbb1; no PDB | capture (class U) |
| · 2.3 Choosing stacks in the academy reward storage | medium | no function cited; no PDB | cite and re-read the function |
| · 2.4 Cen | medium | weak dbb1; no PDB | second reading / client check |
| · 2.5 Moving the items | medium | cap 1/1; weak dbb1 | capture (class U) |
| · 2.6 Answers | medium | cap 0/4; no PDB | capture 0x9883 |
| · 2.7 Outcome per storage situation | medium | cap 0/1; weak dbb1; no PDB | capture (class U) |
| 3. 0x74AA ITEM_OPT and `GTReward_MakeItemAttr` @ FUN_00467c60 | medium | cap 0/1; no PDB | capture (class U) |
| · 3.1 ITEM_OPT (0x21 bytes) | medium | no function cited; weak p171; no PDB | cite and re-read the function |
| · 3.2 Attribute per item class | medium | cap 0/2; weak p171; no PDB | capture (class U) |
| Original-server bugs | medium | cap 0/6; R×1; bug table (class X: effects are deductions); no PDB | capture (class U) |
| 4. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 5. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.51 D08: `db/D08-db-process.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. The DataServer process (Account build as reference) | – | container (see its subsections) |  |
| · 1.1 Objects | medium | cap 0/2 | capture (class U) |
| · 1.2 Start-up and the Windows-service shell | medium | read in code | second reading / client check |
| · 1.3 Main thread and the three ways to stop | medium | cap 1/3 | capture (class U) |
| · 1.4 Sessions, accept and receive (the older session framework) | medium | cap 3/3; R×1; capture shows the link packets, not the SQL | capture (class U) |
| · 1.5 Session workers and the job queue | medium | cap 1/2; R×1 | capture (class U) |
| · 1.6 Address table of the process layer | medium | read in code | second reading / client check |
| 2. Linked game-data and database classes (Account build) | – | container (see its subsections) |  |
| · 2.1 Static objects and who uses them | medium | R×1 | second reading / client check |
| · 2.2 `MapDataBox` (MapInfo.shn, loaded by the Character server o… | medium | read in code | second reading / client check |
| · 2.3 `CItemAuthorityBase`: the box-to-box move matrices | medium | read in code | second reading / client check |
| · 2.4 Random boxes and the reward-item option roll (zone code, de… | medium | read in code | second reading / client check |
| · 2.5 The ODBC wrapper (`Database`, `DBRecord`, `CGameDB_Connect`) | medium | read in code | second reading / client check |
| · 2.6 Address table of the data classes (Account; same as the cit… | medium | read in code | second reading / client check |
| · 2.7 Functions left after parts 1–3 (sweep): TinyXML, helpers, r… | medium | weak inf1 | second reading / client check |
| 3. AccountLog: differences against the Account build | medium | read in code | second reading / client check |
| · 3.1 Objects | medium | cap 0/2 | capture (class U) |
| · 3.2 Start-up, main thread, stop | medium | read in code | second reading / client check |
| · 3.3 The once-a-minute user-count poll (`CStatistics`) | medium | cap 3/3; capture shows the link packets, not the SQL | capture (class U) |
| · 3.4 Session workers, the two DB links, the dispatcher | medium | cap 10/21 | capture (class U) |
| · 3.5 The syslog text file (`cLogSystem`, `cLS_Queue<std::string>… | medium | cap 1/1 | capture (class U) |
| · 3.6 Address table (AccountLog functions identical to the Accoun… | medium | read in code | second reading / client check |
| · 3.7 D01 open point: TEENAGER `nType` 1 (confidence.md §4.6 row … | medium | cap 0/1 | capture (class U) |
| 4. Character: differences against the Account build | – | container (see its subsections) |  |
| · 4.1 Objects | medium | cap 0/1 | capture (class U) |
| · 4.2 Start-up, main thread, stop | medium | cap 0/2 | capture (class U) |
| · 4.3 The GameLog link | medium | cap 3/3; weak inf1; capture shows the link packets, not the SQL | capture (class U) |
| · 4.4 Workers, the DB link, the parser | medium | read in code | second reading / client check |
| · 4.5 Game data in the Character server (replaces the part-2 gues… | medium | read in code | second reading / client check |
| · 4.6 Library code the Character build links in addition | medium | read in code | second reading / client check |
| · 4.7 Address table (Character) | medium | read in code | second reading / client check |
| · 4.8 Functions left after parts 4–7 (sweep) and the runtime boun… | medium | weak inf2 | second reading / client check |
| 5. Character: the SOAP item-shop client (`cUKItemShop`, gSOAP 2… | medium | cap 0/1; weak inf1 | capture (class U) |
| · 5.1 Objects | medium | read in code | second reading / client check |
| · 5.2 Start-up: building the pool | medium | cap 0/1 | capture (class U) |
| · 5.3 0x0870 NC_MISC_ITEMSHOP_URL_DB_REQ | medium | cap 0/7; client×1; weak p171; R×2 | capture 0x086F, 0x3041, 0x3043 |
| · 5.4 The `getItemShopUrl` call on the wire | medium | cap 0/1 | capture 0x3043 |
| · 5.5 When the shop host does not answer | medium | cap 0/4; R×1 | capture 0x3041, 0x3043 |
| · 5.6 The proxy class and the unused operations | medium | weak inf1; R×3 | second reading / client check |
| · 5.7 Address table (Character, gSOAP) | medium | read in code | second reading / client check |
| 6. D02 open points (confidence.md §4.6 row 9) | – | open points / boundary list, no claim to rate |  |
| · 6.1 The four quest blocks of 0x1004 and their `nStatusDone` fil… | medium | cap 5/6; weak dbb1; capture shows the link packets, not the SQL | capture (class U) |
| · 6.2 The item blocks: 0x1017 NC_CHAR_ITEM_CMD | medium | cap 4/6; capture shows the link packets, not the SQL | capture 0x1C13 |
| · 6.3 0x0812–0x0815 ping tests: field names (2016 PDBs) | medium | cap 0/4 | capture 0x0812, 0x0813 |
| 7. GameLog: differences against the Account build | – | container (see its subsections) |  |
| · 7.1 Objects | medium | cap 0/1 | capture (class U) |
| · 7.2 Start-up, main thread, stop | medium | cap 0/1 | capture (class U) |
| · 7.3 Workers, the DB link, transactions | medium | cap 0/1 | capture (class U) |
| · 7.4 Linked library: what differs (dead code) | medium | read in code | second reading / client check |
| · 7.5 Address table (GameLog functions no other document cites) | medium | read in code | second reading / client check |
| · 7.6 Runtime boundary | medium | read in code | second reading / client check |
| Original-server bugs | medium | cap 2/5; weak inf1; bug table (class X: effects are deductions) | capture 0x0812 |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.52 S02: `shared/S02-library.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Network library | – | container (see its subsections) |  |
| · 1.1 Object model | medium | the captured opcodes are only mentioned here (0x2008, 0x200C); the subject of the section (the library object model) is in no capture (hand; baseline: high) | none on the wire |
| · 1.2 Send-buffer pool (`CIOBuffer`, `IOBufferContainer`, `CIOSpi… | medium | cap 0/1 | capture (class U) |
| · 1.3 `CIOCP`: completion port and worker threads | medium | read in code | second reading / client check |
| · 1.4 `CSocket_Acceptor`: listener thread and accepted ring | medium | cv ok; sup×1 (README §5.3); cv corr | re-read the rest (§3); read with P02 "Corrections" |
| · 1.5 `CSocket_IOCP`: connect, receive, send queue, close | medium | read in code | second reading / client check |
| · 1.6 Session glue: callbacks, register, connect, receive | medium | cap 1/1 | capture (class U) |
| · 1.7 `CPacket`: receive buffer and framing | **high** | receive framing: every captured stream (client and server links) parses with no resync (capture-validation §2.1, §7.1); buffer growth and error paths are code only (hand; baseline: medium) |  |
| · 1.8 `CSendPacket`: frame builder (Login, WM) | **high** | frame builder: short / long header of every captured Login and WM send matches (capture-validation §2.1); pool exhaustion paths are code only (hand; baseline: medium) |  |
| · 1.9 Login and Zone copies | medium | read in code | second reading / client check |
| · 1.10 Uncertain (part 1) | – | open points / boundary list, no claim to rate |  |
| 2. Config scripts: `CToken` and `CCsl` | – | container (see its subsections) |  |
| · 2.1 Data structures and constant tables | medium | no function cited | cite and re-read the function |
| · 2.2 `CToken`: the tokenizer | medium | read in code | second reading / client check |
| · 2.3 `CCsl`: the script reader | – | container (see its subsections) |  |
| · · 2.3.1 ReadScript: the main loop | medium | R×1 | second reading / client check |
| · · 2.3.2 Remarks and the remark-control commands | medium | read in code | second reading / client check |
| · · 2.3.3 Commands | medium | read in code | second reading / client check |
| · · 2.3.4 `#DEFINE`: formats | medium | read in code | second reading / client check |
| · · 2.3.5 Data rows | medium | read in code | second reading / client check |
| · · 2.3.6 `#INCLUDE` | medium | read in code | second reading / client check |
| · · 2.3.7 Binary chunk files (`#READ` / `#WRITE`) | medium | read in code | second reading / client check |
| · · 2.3.8 Construction, clearing, teardown | medium | read in code | second reading / client check |
| · 2.4 Grammar, checked against the shipped files | medium | no function cited; weak inf1 | cite and re-read the function |
| · 2.5 Users of the reader | medium | read in code | second reading / client check |
| · 2.6 Result messages (complete list) | medium | no function cited; weak inf1 | cite and re-read the function |
| · 2.7 Login and Zone copies | medium | R×1 | second reading / client check |
| · 2.8 Uncertain (part 2) | – | open points / boundary list, no claim to rate |  |
| 3. Packed files: `CGdp` | – | container (see its subsections) |  |
| · 3.1 Data structures | medium | no function cited | cite and re-read the function |
| · 3.2 What the servers execute: the pass-through | medium | R×1 | second reading / client check |
| · 3.3 Container mode: opening entries | medium | read in code | second reading / client check |
| · 3.4 Container mode: reading, writing, seeking | medium | read in code | second reading / client check |
| · 3.5 Container mode: directory maintenance | medium | read in code | second reading / client check |
| · 3.6 Login and Zone copies | medium | read in code | second reading / client check |
| · 3.7 Uncertain (part 3) | – | open points / boundary list, no claim to rate |  |
| 4. Library users and small helpers (sweep) | – | container (see its subsections) |  |
| · 4.1 Helpers | medium | read in code | second reading / client check |
| · 4.2 Destructors that tear the library down | medium | weak inf1 | second reading / client check |
| · 4.3 Login process glue the library reaches | medium | read in code | second reading / client check |
| · 4.4 Zone process glue the library reaches | medium | weak inf2; R×1 | second reading / client check |
| 5. Original-server bugs | medium | cap 0/1; weak inf1; bug table (class X: effects are deductions) | capture (class U) |
| 6. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| 7. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.53 L01 knowledge: `docs/knowledge/L01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Corrections to `login-server.md` (L00, done; not edited there) | medium | cap 4/8; R×1 | capture (class U) |
| Facts | medium | cap 5/5 | capture (class U) |

### 2.54 W01 knowledge: `docs/knowledge/W01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals (wm) | **low** | cap 2/3; S: 3 offset lines, no 2016 PDB member named (pre-S01 names are ours); ours×1 | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv |
| Facts other items need | medium | cap 28/31; pdb 2/2; weak inf1 p171 | capture (class U) |
| Open questions | – | open points / boundary list, no claim to rate |  |

### 2.55 W02 knowledge: `docs/knowledge/W02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals (wm) | **low** | no function cited; pre-S01 prose without a function; ours×1 | cite and re-read the function |
| Facts other items need | **low** | cap 4/16; S: 7 offset lines, no 2016 PDB member named (pre-S01 names are ours); weak p171 | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv; capture 0x540E |
| Open questions | – | open points / boundary list, no claim to rate |  |

### 2.56 W03 knowledge: `docs/knowledge/W03.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals and structures (wm) | **low** | cap 2/4; S: 12 offset lines, no 2016 PDB member named (pre-S01 names are ours); ours×1 | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv |
| Facts other items need | medium | cap 6/42 | capture 0x140A, 0x9808, 0x9812, 0x985A |

### 2.57 W04 knowledge: `docs/knowledge/W04.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals and structures (wm) | **low** | cap 4/12; S: 18 offset lines, no 2016 PDB member named (pre-S01 names are ours) | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv; capture 0x0845, 0x086C, 0x086D, 0x5830 … |
| Answers to other items' open questions | – | open points / boundary list, no claim to rate |  |
| Notes for a rebuild | medium | cap 0/3 | capture 0x10F2, 0x580B |

### 2.58 W05 knowledge: `docs/knowledge/W05.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Corrections | medium | cap 9/10; pdb 0/1; weak inf2; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 2. Facts for other items | medium | cap 2/3; pdb 0/2; 2 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 3. Open questions | – | open points / boundary list, no claim to rate |  |

### 2.59 W06 knowledge: `docs/knowledge/W06.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to earlier items | medium | cap 0/4; pdb 1/1; R×1 | capture 0x9825 |
| 1. Guild classes in the WM | medium | cap 0/12; R×1 | capture 0x741F, 0x742B, 0x742C, 0x742E … |
| 2. Other WM leftovers (W06 §2.3, §3) | medium | cap 0/1 | capture 0x9404 |

### 2.60 Z01 knowledge: `docs/knowledge/Z01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Names (read this first) | medium | cap 0/4 | capture (class U) |
| 2. Object class hierarchy (RTTI) | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |
| 3. Object handles | **high** | re-checked (§3.2.2 H1–H3): every range bound re-read in sohu_HandleSplit FUN_00633650, all 13 object sizes are the class sizes of the 2016 Zone.pdb (hand; baseline: medium) |  |
| 4. ShinePlayer members (offsets from the object start) | medium | re-checked (§3.2.3): all 36 offsets are 2016 PDB members; 2 meanings corrected (+0x29638 = character title, +0x2a800 = sp_isPossibleNewConnect, cleared by 0x0806 / 0x1801 only), 1 refined (+0x1c00 = total, not base); read with docs/knowledge/X02.md §0 (hand; baseline: low) | capture of a field per member (0x1038 login burst for basedata) |
| 5. Globals | medium | cap 2/2 | capture (class U) |
| 6. Conventions for reading zone handlers | medium | re-checked (§3.2.1): lookup pattern confirmed with counts over 307 handlers; the "PDB offset = 2016 − 6" rule corrected (211 structs carry the header as a member) and "starts with" narrowed (R2–R4, R6); read with docs/knowledge/X02.md §0 (hand; baseline: low) | a captured DB→zone answer per header form |
| 7. Startup | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |
| 8. Open questions for other items | – | open points / boundary list, no claim to rate |  |
| SHN loader check = DataVersionKey (C02 follow-up) | medium | read in code | second reading / client check |

### 2.61 Z02 knowledge: `docs/knowledge/Z02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Corrections and additions to Z01 | medium | cap 1/4; pdb 0/3; 3 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 2. Player offsets found here | **low** | cap 1/1; S: 22 offset lines, no 2016 PDB member named (pre-S01 names are ours) | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv |
| 3. Shared mechanisms | medium | cap 5/9; pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x0848, 0x1C07, 0x3C03, 0x3C0F |
| 4. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.62 Z03 knowledge: `docs/knowledge/Z03.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Answers to open questions | – | open points / boundary list, no claim to rate |  |
| 2. Shared mechanisms | medium | re-checked (§3.2.4): every offset is a 2016 PDB member; names of 4 smo_Flag bits, the EngageArgument fields and the abstate element +0x70 corrected, stat matrix and battle statistics superseded by Z12 §1.1 / Z16 §3.1; read with docs/knowledge/X02.md §0 (hand; baseline: medium) | combat capture with an abstate set and removed by walking (aeo_MiscData reset condition) |
| 3. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.63 Z04 knowledge: `docs/knowledge/Z04.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Inventory model (for Z05, Z06, Z07, D03) | medium | pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 2. Locking / DB hand-off (for Z05) | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |
| 3. Item use (for Z03, Z07, Z08) | medium | cap 3/6 | capture 0x204C, 0x482B |
| 4. Constants (named item ids read from the item-constant table) | medium | read in code | second reading / client check |
| 5. Quirks worth knowing | medium | cap 5/8 | capture 0x3027, 0x3030 |
| 6. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.64 Z05 knowledge: `docs/knowledge/Z05.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Commit model (for D03, Z06, Z07, Z13, X01) | medium | cap 3/3 | capture (class U) |
| 2. Answer layouts (for D03) | medium | cap 1/4 | capture 0x3803, 0x3C07 |
| 3. Facts for other items | **low** | cap 16/36; R×1 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x2072, 0x4C23, 0x5422, 0x680E … |
| 4. Open questions | – | open points / boundary list, no claim to rate |  |

### 2.65 Z06 knowledge: `docs/knowledge/Z06.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Player members | **low** | cap 1/1; S: 11 offset lines, no 2016 PDB member named (pre-S01 names are ours); N: `g_NoBooth` | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv; README §4.8 |
| 2. Facts for other items | **low** | cap 6/29; S: 6 offset lines, no 2016 PDB member named (pre-S01 names are ours) | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv; capture 0x303B, 0x303E, 0x303F, 0xAC2C |
| 3. Tables | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |

### 2.66 Z07 knowledge: `docs/knowledge/Z07.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to earlier items (read these before trusting the… | **low** | cap 1/10; client×1; R×1; weak inf2 | callers incl. vtable slots; senders in every `handlers.json`; capture 0x481D |
| 1. Answers to open questions | – | open points / boundary list, no claim to rate |  |
| 2. Player offsets found here | **low** | cap 0/1; S: 10 offset lines, no 2016 PDB member named (pre-S01 names are ours) | find the struct in the 2016 PDB (`pdb.py … types`), S01-renames.tsv |
| 3. Shared mechanisms | medium | cap 2/5 | capture (class U) |
| 4. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.67 Z08 knowledge: `docs/knowledge/Z08.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections / additions to earlier items | medium | cap 0/11 | capture 0x3832, 0x3833, 0x3849 |
| 1. Facts other items need | medium | cap 1/21 | capture 0x5C02 |
| 2. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.68 Z09 knowledge: `docs/knowledge/Z09.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections / additions to earlier items | **high** | cap 3/12; pdb 3/3; R×2 |  |
| 1. Facts other items need | medium | cap 1/23 | capture 0x1059, 0x105A, 0x1116, 0x2442 … |
| 2. Client-side findings (not server bugs, for C01) | medium | cap 2/6 | capture 0x1813, 0x1828, 0x1829, 0x6C15 |
| 3. Follow-ups for finished items | medium | cap 0/4 | capture 0x1059, 0x105A, 0x2442, 0x2443 |

### 2.69 Z10 knowledge: `docs/knowledge/Z10.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| For everyone working on the zone start | medium | read in code | second reading / client check |
| For Z03 / Z09 (combat factor) | medium | no function cited | cite and re-read the function |
| For Z02 / Z07 / Z12 (`ShineCommonParameter`, ChrCommon.txt) | **high** | cap 1/2; client×1; pdb 7/7 |  |
| For X01 (bug register) | medium | no function cited | cite and re-read the function |
| Corrections of other items (for X01) | medium | read in code | second reading / client check |
| Server config files (`*ServerInfo.txt`) | medium | no function cited | cite and re-read the function |

### 2.70 Z11 knowledge: `docs/knowledge/Z11.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Command system | medium | cap 1/1; pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 2. Commands that change persistent state or reach other servers | medium | cap 9/20 | capture (class U) |
| 3. Shared facts found on the way | medium | cap 1/1 | capture (class U) |
| 4. vtable slot method (used throughout Z11) | medium | no function cited | cite and re-read the function |

### 2.71 Z12 knowledge: `docs/knowledge/Z12.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to other items | medium | cap 1/1; pdb 2/2 | capture (class U) |
| 1. Stat matrix (`Parameter::Container`, `p+0xfc0`, size 0xdb0) | medium | cap 1/2; pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x10DF |
| 2. Login blobs and options | medium | cap 4/7; pdb 2/3; R×1 | capture 0x102A, 0x103C |
| 3. Open for other items | medium | no function cited | cite and re-read the function |

### 2.72 Z13 knowledge: `docs/knowledge/Z13.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Wedding sub-status 5–8 (answers D02 §11 end / §16) | medium | cap 1/5; client×1 | capture 0x205D |
| 2. Corrections to earlier items (wedding) | medium | cap 1/5 | capture (class U) |
| 3. Wedding hall facts | medium | cap 1/5 | capture (class U) |
| 4. Minimon auto-use and card rewards (part 9, output §9) | medium | cap 1/3; R×1 | capture (class U) |
| 5. Mini house (output §1–§3) | medium | cap 0/10; pdb 1/2; R×1 | capture 0x3034, 0x8C08, 0x8C3F, 0x8C51 … |
| 6. Pets (output §5–§6) | medium | cap 3/3 | capture (class U) |
| 7. Mounts (output §7–§8) | medium | cap 1/6; pdb 1/1; R×2 | capture 0x3068, 0xCC03, 0xCC07, 0xCC09 |
| 8. Result codes without client text (met in this item) | medium | cap 0/2 | capture 0x306E |
| 9. Review additions (part 11) | medium | cap 1/4; pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x204E, 0x205D |

### 2.73 Z14 knowledge: `docs/knowledge/Z14.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Facts other items need | medium | cap 0/14; pdb 1/1 | capture 0x384A, 0xB021, 0xB023, 0xB026 |
| 2. Open questions for other items | – | open points / boundary list, no claim to rate |  |

### 2.74 Z15 knowledge: `docs/knowledge/Z15.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections / additions to earlier items | medium | cap 0/1 | capture (class U) |
| 1. Quest data and script language | medium | cap 1/1 | capture (class U) |
| 2. Objects and offsets | **high** | cap 0/3; pdb 3/3 |  |
| 3. Flows other items touch | medium | cap 6/12; pdb 1/1 | capture (class U) |
| 4. Open points (see doc §9) | – | open points / boundary list, no claim to rate |  |

### 2.75 Z16 knowledge: `docs/knowledge/Z16.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals | medium | cap 0/1 | capture (class U) |
| Struct members | **high** | pdb 8/8; no function cited |  |
| Vtable slots (ShinePlayer unless noted) | medium | no function cited | cite and re-read the function |
| Facts and corrections for other items | medium | cap 1/8; R×1 | capture 0x580C |

### 2.76 Z17 knowledge: `docs/knowledge/Z17.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Item actions in one paragraph | medium | cap 1/1 | capture (class U) |
| Player members and slots (zone) | medium | pdb 1/2 | second reading / client check |
| Costume charges in one paragraph | medium | cap 1/7 | capture 0x3037, 0x3038, 0x3066 |
| Packets (layouts in `docs/protocol/annotations/Z17.json`) | medium | cap 2/12 | capture 0x206F, 0x3037, 0x3038, 0x3046 … |
| Corrections to other items' docs | medium | cap 1/2; pdb 2/2 | capture (class U) |
| Open questions | – | open points / boundary list, no claim to rate |  |

### 2.77 Z18 knowledge: `docs/knowledge/Z18.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Corrections | medium | cap 7/11; pdb 3/4; weak inf1; R×1 | capture (class U) |
| Facts other items need | **high** | cap 16/25; pdb 5/6 |  |

### 2.78 Z19 knowledge: `docs/knowledge/Z19.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Facts for other items | medium | weak inf1; R×1 | second reading / client check |

### 2.79 Z20 knowledge: `docs/knowledge/Z20.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals and lookups | **high** | pdb 3/3 |  |
| Load and reload | medium | no function cited | cite and re-read the function |
| Per-player lists | medium | read in code | second reading / client check |
| Open for other items | medium | no function cited | cite and re-read the function |

### 2.80 Z21 knowledge: `docs/knowledge/Z21.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Three mechanisms (§1) | medium | pdb 1/1; no function cited | cite and re-read the function |
| Corrections to done items | medium | read in code | second reading / client check |
| Shared functions documented here (cite Z21 instead of redoing) | medium | cap 1/2 | capture 0x206F |
| Player vtable slots (ShinePlayer; most shared by all mobile obj… | medium | R×1 | second reading / client check |
| Bugs for other registers | medium | bug table (class X: effects are deductions) | second reading / client check |

### 2.81 Z22 knowledge: `docs/knowledge/Z22.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to other items | medium | pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 1. Actors and elements | medium | pdb 1/1; R×1 | second reading / client check |
| 2. Dispel masks and the skill → abstate path | medium | pdb 0/1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`); R×1 | check the offsets with `pdb.py` |
| 3. Tables | medium | read in code | second reading / client check |
| 4. Bugs (for X01) | medium | no function cited | cite and re-read the function |

### 2.82 Z23 knowledge: `docs/knowledge/Z23.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Structures (pdb2016) | medium | pdb 3/4; no function cited | cite and re-read the function |
| Rules | medium | cap 5/6 | capture 0x481D |
| Vtable slots (ShinePlayer) | medium | cap 2/2 | capture (class U) |
| Utilities | medium | cap 2/2 | capture (class U) |
| Follow-up created | medium | no function cited | cite and re-read the function |

### 2.83 Z24 knowledge: `docs/knowledge/Z24.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals (zone, 2016) | medium | pdb 1/1; no function cited | cite and re-read the function |
| Corrections to other docs | medium | cap 0/2 | capture 0x9004 |
| Subsystem facts | medium | cap 0/4; pdb 0/2; 2 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x302B |
| Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| Follow-up items | – | open points / boundary list, no claim to rate |  |

### 2.84 Z25 knowledge: `docs/knowledge/Z25.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Structures and tables | medium | pdb 2/3 | second reading / client check |
| 2. Behaviour facts | medium | cap 1/3; client×1 | capture 0x245B, 0x245E |
| 3. Corrections to other docs | medium | cap 0/2; pdb 2/2 | capture 0x2442, 0x2443 |

### 2.85 Z26 knowledge: `docs/knowledge/Z26.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Data | medium | cap 2/2; pdb 0/2; 2 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| Flow | medium | cap 3/5 | capture 0x3029 |
| Server-menu facts (Z02 does not record them) | medium | cap 1/2 | capture 0x3C0F |
| Bugs | medium | cap 1/2; bug table (class X: effects are deductions) | capture (class U) |

### 2.86 Z27 knowledge: `docs/knowledge/Z27.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Global and layouts (zone, 2016; names *(pdb2016)*) | medium | pdb 2/2; no function cited | cite and re-read the function |
| Loading facts | medium | cap 1/1; R×1 | capture (class U) |

### 2.87 Z28 knowledge: `docs/knowledge/Z28.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals *(pdb2016)* | medium | pdb 1/1 | second reading / client check |
| Rows (member offsets) | medium | no function cited | cite and re-read the function |
| Card roll | medium | read in code | second reading / client check |
| Per-player state (`ShinePlayer`, *(pdb2016)*) | medium | cap 3/3; pdb 2/2 | capture (class U) |
| Shared code (identical-code folding) | medium | read in code | second reading / client check |
| Bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |

### 2.88 Z29 knowledge: `docs/knowledge/Z29.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals and loaders | medium | pdb 1/1 | second reading / client check |
| Formula (one attacker unit, share `S = trunc(MonEXP · (damage /… | medium | read in code | second reading / client check |
| `HitMeList::Enemy.e_Attacker` | medium | read in code | second reading / client check |
| Corrections to done items (for X01) | medium | no function cited | cite and re-read the function |
| Bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |

### 2.89 Z30 knowledge: `docs/knowledge/Z30.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| ShinePlayer vtable slots resolved here (rtti.py over the 2016 z… | medium | cap 0/3 | capture 0x181D, 0xB413 |
| Other facts | medium | cap 1/5 | capture 0x941B |

### 2.90 Z31 knowledge: `docs/knowledge/Z31.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to earlier items (read these before trusting the… | medium | cap 5/16; pdb 2/3; weak inf1; R×2 | capture 0x203D, 0x74AD, 0x74B5 |
| 1. Vtable slots identified (ShinePlayer byte offsets) | medium | cap 3/7; pdb 0/1; weak inf1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x106E, 0x1096, 0x305B |
| 2. Facts | medium | cap 7/8; pdb 4/6; R×1 | capture (class U) |
| 3. Original-server bugs | medium | cap 1/2; bug table (class X: effects are deductions) | capture (class U) |

### 2.91 Z32 knowledge: `docs/knowledge/Z32.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Globals | medium | no function cited | cite and re-read the function |
| Game types and data | medium | no function cited | cite and re-read the function |
| Player vtable slots (ShinePlayer) | medium | cap 1/2 | capture 0xBCDD |
| Coin reservations | medium | cap 1/1 | capture (class U) |
| Corrections to done items | medium | cap 1/6 | capture 0xBCDD |

### 2.92 D01 knowledge: `docs/knowledge/D01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Login result flags (answers the open question of login-server.m… | **low** | cap 4/4; pdb 1/1; weak dbb3; B×1; capture shows the link packets, not the SQL | code or capture for the marked statements; follow the return value to the parser |
| Packet facts | **low** | cap 8/33; B×1 | follow the return value to the parser; capture 0x8002, 0x8004, 0x8006 |
| Framework | medium | cap 4/7; capture shows the link packets, not the SQL | capture (class U) |

### 2.93 D02 knowledge: `docs/knowledge/D02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Framework (for D03 / D04) | medium | cap 6/10; capture shows the link packets, not the SQL | capture (class U) |
| Tables and columns (as the procedures use them; *(db-backup)*) | **low** | no function cited; D: `p_Char_Login`, `usp_Character_setChangeID` differ between the backups | D06 §8.5 version |
| Answers to open questions | – | open points / boundary list, no claim to rate |  |
| Corrections / additions for other items | **low** | cap 1/3; pdb 1/1; D: `p_Guild_Member_SetGrade`, `usp_GuildAcademy_withdrawMoney` differ between the backups | D06 §8.5 version |

### 2.94 D03 knowledge: `docs/knowledge/D03.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Persistence model (for Z04, Z05, D06, X01) | medium | no PDB | second reading / client check |
| Answers to open questions | – | open points / boundary list, no claim to rate |  |
| For other items | medium | cap 15/46 | capture (class U) |
| For capture scenarios (X02) | medium | cap 3/14 | capture (class U) |

### 2.95 D04 knowledge: `docs/knowledge/D04.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Answers to Z08's open questions (Z08 knowledge §2) | – | open points / boundary list, no claim to rate |  |
| For W03 / W04 (WM side of the answers) | medium | cap 4/15; weak p171 | capture (class U) |
| For D05 (GameLog) | medium | cap 4/19 | capture (class U) |
| For D06 (missing DB behaviour) | **low** | cap 0/1; D: `usp_GuildAcademy_withdrawMoney`, `usp_GuildTournament_setRegist` differ between the backups | D06 §8.5 version |
| Tables (db-backup) | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |

### 2.96 D05 knowledge: `docs/knowledge/D05.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| For senders (zone Z*, WM W01, Character D02–D04) | **low** | cap 5/13; B×1 | follow the return value to the parser |
| NC_SYSLOG (dept 50) text log | **low** | no function cited; pre-S01 prose without a function | cite and re-read the function |
| For D01 (Account / AccountLog, same DataServer code) | medium | cap 0/2; no PDB | capture (class U) |
| Data | **low** | no function cited; pre-S01 prose without a function; weak dbb1 | cite and re-read the function |

### 2.97 D06 knowledge: `docs/knowledge/D06.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Corrections | medium | cap 4/30; weak dbb1 | capture 0x205D, 0x74F8 |
| For a rebuild (Account DB) | medium | cap 0/1 | capture (class U) |
| For a rebuild (AccountLog / Statistics / GameLog) | medium | cap 1/4 | capture (class U) |
| For a rebuild (Character DB, D06 §5) | medium | no function cited | cite and re-read the function |
| For a rebuild (Character DB, D06 §6, §8) | medium | no function cited | cite and re-read the function |
| For a rebuild (all DB servers, D06 §7) | medium | no function cited | cite and re-read the function |
| For a rebuild (schema, D06 §9) | medium | no function cited | cite and re-read the function |
| For a rebuild (version choices, D06 §8.5) | medium | no function cited | cite and re-read the function |

### 2.98 D07 knowledge: `docs/knowledge/D07.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| What D04 §12 / §9.3 / §6.4 should be read as now | medium | cap 0/1; no PDB | capture (class U) |
| Facts for other items | medium | cap 0/2; weak dbb1; no PDB | capture (class U) |

### 2.99 D08 knowledge: `docs/knowledge/D08.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to finished items (their docs are not edited) | medium | cap 4/10; pdb 2/2; R×1 | capture 0x0812 |
| 1. Process layer facts (all four DB servers) | medium | cap 1/1; pdb 1/1 | capture (class U) |
| 2. Linked data classes and the ODBC wrapper (D08 §2) | medium | read in code | second reading / client check |
| 3. AccountLog differences (D08 §3) | medium | cap 1/2; pdb 1/1 | capture (class U) |
| 4. Character differences (D08 §4) | medium | cap 1/4; pdb 0/2; 2 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| 5. Character SOAP item-shop client (D08 §5) | medium | cap 0/5; R×1 | capture 0x3041, 0x3043 |
| 6. D02 open points (D08 §6) | – | open points / boundary list, no claim to rate |  |
| 7. GameLog differences (D08 §7) | medium | pdb 1/1; R×1 | second reading / client check |
| 8. Sweep results (D08 §2.7, §4.8, coverage boundary) | – | open points / boundary list, no claim to rate |  |

### 2.100 S01 knowledge: `docs/knowledge/S01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. NA2016 executables: private-server patches | – | container (see its subsections) |  |
| · 1.1 What differs from the 2016 exes | medium | cap 1/1 | capture (class U) |
| · 1.2 WorldManager hooks | medium | cap 1/3; pdb 2/4 | capture (class U) |
| · 1.3 Zone hooks and byte edits | medium | cap 2/2; pdb 0/1; weak inf1; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py` |
| · 1.4 Bug hints for the owning items (for X01) | medium | cap 6/12; weak inf1 | capture (class U) |
| · 1.5 Other NA2016 files | medium | read in code | second reading / client check |
| 2. Packet layouts and opcode names from the 2016 server PDBs | – | container (see its subsections) |  |
| · 2.1 `docs/protocol/pdb2016-layouts.json` and where it is used | medium | cap 5/11 | capture 0xB413 |
| · 2.2 Opcode names: `pdb2016` in `catalog.py` | medium | cap 1/3 | capture (class U) |
| · 2.3 Differences 2016 server PDBs vs 2017 client PDB | **low** | cap 22/46; weak inf2 p171 | code or capture for the marked statements; capture 0x0812, 0x0813, 0x3034, 0x3065 … |
| · 2.4 Several definitions of one type in a 2016 PDB; base-class m… | medium | cap 2/9; pdb 2/2 | capture (class U) |
| 3. Follow-ups per item | **low** | no function cited; weak p173 | code or capture for the marked statements |
| · 3.1 Summary table | **low** | cap 13/25; pdb 0/2; weak inf1 p172 fh1; 2 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | code or capture for the marked statements; check the offsets with `pdb.py`; capture 0x3034, 0x8C4C, 0x9407 |
| · 3.2 Hand annotations vs `pdb2016-layouts.json` | medium | cap 7/10 | capture (class U) |
| · 3.3 Details per item | medium | cap 18/48; pdb 14/30; weak inf2 p173; 16 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x3034, 0x3065, 0x3809, 0x3855 … |
| 4. Types catalogue: server types per item (part 4) | – | container (see its subsections) |  |
| · 4.1 Zone (`Zone.pdb`) | medium | cap 0/1 | capture 0x202C |
| · 4.2 WorldManager, Login, Account/AccountLog | medium | pdb 2/2 | second reading / client check |
| · 4.3 Variants settled (from §2.4) | medium | read in code | second reading / client check |
| 5. FiestaHeroes documentation → items (part 4) | medium | no function cited; weak fh1 | cite and re-read the function |
| 6. 9Data and DB backups: 2016 vs NA2016 (part 4) | – | container (see its subsections) |  |
| · 6.1 SHN header and the loaders' checks | medium | weak inf1 | second reading / client check |
| · 6.2 9Data content diff | medium | weak inf1 | second reading / client check |
| · 6.3 NA2016 DB backups | medium | no function cited | cite and re-read the function |
| 7. Original-server bugs (part 5) | medium | cap 5/8; client×1; weak inf1; bug table (class X: effects are deductions) | capture (class U) |
| 8. Not reconstructed / uncertain (part 5) | – | open points / boundary list, no claim to rate |  |
| 9. Coverage boundary (part 5) | – | open points / boundary list, no claim to rate |  |

### 2.101 S02 knowledge: `docs/knowledge/S02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Network (§1) | medium | cap 0/1; weak inf1 | capture (class U) |
| Config scripts (§2) | medium | R×1 | second reading / client check |
| Packed files (§3) | medium | no function cited; R×1 | cite and re-read the function |
| Corrections to other items' docs (done items; not edited) | medium | no function cited | cite and re-read the function |
| For open items | medium | no function cited | cite and re-read the function |

### 2.102 C01 knowledge: `docs/knowledge/C01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Receive path | medium | cap 5/6 | capture 0x0819 |
| 2. Dispatchers (found via RTTI: PgFrameWork subclasses, vtable … | medium | cap 1/4; weak inf1 p171 | capture 0x749D, 0x74D4, 0x74FE |
| 3. Names the client itself proves | medium | cap 6/10; client×2 | capture 0x204A, 0x242E, 0x6C11, 0x6C12 |
| 4. Per-scene handlers (pre-game scenes checked by hand) | medium | client×1 | second reading / client check |
| · · Net(pre-dispatch) | medium | cap 3/4 | capture 0x0819 |
| · · AccountFrameWork | **high** | dispatch table of the login scene: 11 of 12 opcodes captured and handled as listed (hand; baseline: medium) |  |
| · · LoginWorldNetFrameWork | **high** | dispatch table: 5 of 6 opcodes captured (hand; baseline: medium) |  |
| · · CharSelectFrameWork | medium | cap 21/29; client×6 | capture 0x111D, 0x140A, 0x580B, 0x7003 … |
| · · CharCreateFrameWork | medium | cap 4/4 | capture (class U) |
| · · CHairShopFrameWork | medium | cap 2/4 | capture 0x1079, 0x107D |
| · · ZoneLoginNetFrameWork | **high** | dispatch table: 18 of 24 opcodes captured (the character-load burst) (hand; baseline: medium) |  |
| · · LinkFrameWork | **high** | dispatch table: 15 of 22 opcodes captured (map links) (hand; baseline: medium) |  |
| · · GameFrameWork opcodes per dept | medium | no function cited | cite and re-read the function |
| · · ITask handlers | medium | cap 11/230 | capture 0x1061, 0x1067, 0x202E, 0x202F … |
| 5. Coverage of server → client packets | medium | cap 3/32; client×1 | capture 0x242E |
| 6. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.103 C02 knowledge: `docs/knowledge/C02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Tools and generated files | medium | cap 1/1 | capture (class U) |
| 2. Opcode names | medium | cap 3/10; pdb 0/1; weak p171; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`) | check the offsets with `pdb.py`; capture 0x181F, 0xAC2C |
| · Handler-name conflicts (51), verdicts in `pdb-name-verdicts.jso… | medium | cap 21/82 | capture 0xBCDA |
| · Weak 2016 names replaced by the PDB name (59, by rank) | medium | cap 14/59 | capture 0x10ED, 0x10F0, 0x2004, 0x2006 … |
| 3. Packet layouts (`pdb-layouts.json`) | medium | cap 1/1; weak inf1 p171 | capture (class U) |
| 4. Struct sizes vs the 2016 code | medium | cap 18/47 | capture 0x0812, 0x0813, 0x3034, 0x3036 … |
| 5. Hand annotations vs the PDB (per owner) | medium | no function cited | cite and re-read the function |
| 6. Types catalogue (which PDB types matter to whom) | medium | no function cited | cite and re-read the function |
| 7. Ghidra project `client2017` | medium | no function cited | cite and re-read the function |
| 8. 2016 client function names ported from 2017 | medium | weak p171 | second reading / client check |
| 9. Follow-ups per item | medium | cap 14/24 | capture 0x0C66 |
| 10. Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |

### 2.104 P01 knowledge: `docs/knowledge/P01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Usage | medium | cap 4/4 | capture (class U) |
| Outputs | medium | no function cited | cite and re-read the function |
| How it decodes | medium | cap 3/4 | capture (class U) |
| Validation checks (report) | medium | no function cited | cite and re-read the function |
| Limits | medium | cap 0/1; weak inf1 | capture (class U) |
| Tested | medium | cap 7/8 | capture (class U) |

### 2.105 P02 knowledge: `docs/knowledge/P02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Corrections | **high** | every row is a capture finding with its packet count and the code place (hand; baseline: medium) |  |
| Facts | **high** | capture facts (orders, timings, field values) with the code place; *(inferred)* marks the 8 deductions (hand; baseline: medium) |  |

### 2.106 P03 knowledge: `docs/knowledge/P03.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Install and use | medium | no function cited | cite and re-read the function |
| Fields | medium | cap 1/1 | capture (class U) |
| How it decodes | medium | cap 1/1 | capture (class U) |
| Tested | medium | cap 3/4 | capture (class U) |
| Limits | medium | cap 0/1 | capture (class U) |

### 2.107 P04 knowledge: `docs/knowledge/P04.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Changed statements | medium | cap 87/90; client×4; pdb 0/1; weak inf3; 1 PDB member(s) at another offset (nested or wrong: `X02-rate.py pdbmiss`); R×1 | check the offsets with `pdb.py`; capture 0x140A |
| Uncertain / not reconstructed | – | open points / boundary list, no claim to rate |  |
| Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.108 P05 knowledge: `docs/knowledge/P05.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Changes to `docs/protocol/README.md` | medium | cap 54/55; client×2; weak p171 | capture 0x111D |
| Sweep: README §2 against every batch-4 row of capture-validatio… | medium | cap 2/2 | capture (class U) |
| Original-server bugs | medium | cap 2/2; bug table (class X: effects are deductions) | capture (class U) |
| Not reconstructed / uncertain | – | open points / boundary list, no claim to rate |  |
| Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.109 X01 knowledge: `docs/knowledge/X01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| Where to look | medium | no function cited | cite and re-read the function |
| Names files | medium | no function cited | cite and re-read the function |
| Facts X01 established by re-reading code | medium | cap 2/8 | capture 0x9407, 0x940B |
| Bugs X01 owns | medium | cap 1/5; weak inf1; bug table (class X: effects are deductions) | capture (class U) |

### 2.110 X02 knowledge: `docs/knowledge/X02.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Corrections to earlier items (read these before trusting the… | **low** | cap 48/104; client×3; pdb 12/15; weak inf10 p176 fh1; B×5; R×7 | code or capture for the marked statements; capture 0x0812, 0x1815, 0x1817, 0x2004 … |
| 1. How to use the review (for X01, P02 and the owners) | medium | no function cited; weak inf1 p171 | cite and re-read the function |
| 2. Facts found on the way that no other file holds | medium | read in code | second reading / client check |
| 3. Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| 4. Follow-up items created by X02 | – | open points / boundary list, no claim to rate |  |
| 5. Open questions | – | open points / boundary list, no claim to rate |  |

### 2.111 X03 knowledge: `docs/knowledge/X03.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Rows and statements that look wrong (reported, not changed) | medium | no function cited | cite and re-read the function |
| 1. Where things are in the README after X03 | medium | no function cited | cite and re-read the function |

### 2.112 X04 knowledge: `docs/knowledge/X04.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Facts for other items | medium | cap 7/8 | capture (class U) |
| 1. Rows per README table | medium | cap 14/14 | capture (class U) |
| 2. capture-validation §13 rows left out of README §5, with the … | medium | cap 19/19 | capture (class U) |
| 3. Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| 4. Uncertain / not reconstructed | – | open points / boundary list, no claim to rate |  |
| 5. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.113 X05 knowledge: `docs/knowledge/X05.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Batch-2 leftovers (capture-validation §15 rows naming X05, §… | medium | cap 16/44; R×1 | capture 0x0C15, 0x0C66, 0x1011, 0x102A … |
| 2. Facts found on the way | medium | cap 2/3; weak dbb1 | capture 0x1050 |
| 3. Batch 3: what the recorded scenarios confirmed (one line eac… | medium | cap 39/47 | capture 0x2023, 0x242E, 0x301B, 0x3029 … |
| 4. Open after batch 3: where each thing went | medium | cap 11/20 | capture 0x2023, 0x242E, 0x5005, 0x5006 |
| 5. Predictions of X02 that were wrong as written (for the owner… | medium | cap 16/22 | capture 0x2006, 0x301B, 0x3029, 0x305B |
| 6. Left open on purpose | medium | cap 5/9; weak inf1 | capture 0x106E, 0x203D, 0x242E |
| 7. Ratings and the generator scripts | medium | no function cited | cite and re-read the function |

### 2.114 X06 knowledge: `docs/knowledge/X06.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 0. Facts for other items | medium | cap 3/3 | capture (class U) |
| 1. Rows per README table | medium | cap 11/12; weak inf1 | capture (class U) |
| 2. capture-validation §13 batch-4 rows left out of README §5, w… | medium | cap 1/1 | capture (class U) |
| 3. Original-server bugs | medium | no function cited; bug table (class X: effects are deductions) | cite and re-read the function |
| 4. Uncertain / not reconstructed | – | open points / boundary list, no claim to rate |  |
| 5. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.115 X07 knowledge: `docs/knowledge/X07.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Batch 4: result lines, corrected notes, run kits | medium | cap 10/13; R×1 | capture 0x1061, 0x482B |
| 2. Open after batch 4: where each thing went | medium | cap 20/31; client×1; pdb 1/1; weak p171 | capture 0x1061, 0x1067, 0x900E, 0x900F |
| 3. Ratings after batch 4 (`docs/review/confidence.md` §2) | medium | cap 2/3; R×1 | capture (class U) |
| 4. Order of work and reach after batch 4 (`capture-scenarios.md… | medium | cap 29/33 | capture 0x1067, 0x243F, 0x900F |
| 5. Left open, uncertain | – | open points / boundary list, no claim to rate |  |
| 6. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.116 X09 knowledge: `docs/knowledge/X09.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Batch 5: result lines, corrected notes, run kits | medium | cap 11/14 | capture 0x5005 |
| 2. What batch 5 left open → scenario | medium | cap 8/13; client×1 | capture 0x2023, 0x3807, 0x5005 |
| 3. Ratings after batch 5 | medium | cap 2/6; weak inf1 | capture 0x0845, 0x5005 |
| 4. Which broadcasts stop at sight (Z01 §3.2 against `s45`'s sho… | medium | read in code | second reading / client check |
| 5. Order of work and reach after batch 5 (`capture-scenarios.md… | medium | cap 25/30 | capture 0x2023, 0x3803, 0x3807 |
| 6. Left open, uncertain | – | open points / boundary list, no claim to rate |  |
| 7. Coverage boundary | – | open points / boundary list, no claim to rate |  |

### 2.117 K01 knowledge: `docs/knowledge/K01.md`

| § | Rating | Reason | Raise by |
|---|---|---|---|
| 1. Process roles | medium | cap 1/1 | capture (class U) |
| 2. How Login sees multiple worlds | medium | cap 8/8 | capture (class U) |
| 3. Which services are shared and which are per-world | medium | read in code | second reading / client check |
| 4. Config files and row format | – | container (see its subsections) |  |
| · 4.1 `9Data/ServerInfo/ServerInfo.txt` | medium | no function cited | cite and re-read the function |
| · 4.2 Per-process `MY_SERVER` | medium | no function cited | cite and re-read the function |
| 5. Zone configuration: identity, listeners, peers, maps | – | container (see its subsections) |  |
| · 5.1 Identity | medium | read in code | second reading / client check |
| · 5.2 Listeners and peers | medium | cap 2/2 | capture (class U) |
| · 5.3 Map assignment: `World/Field.txt` | medium | cap 4/4 | capture (class U) |
| · 5.4 Zone ring limits | medium | R×1 | second reading / client check |
| 6. `MHBasic` and `Fiesta = 99` | – | container (see its subsections) |  |
| · 6.1 What the map is | medium | read in code | second reading / client check |
| · 6.2 What 99 means | medium | no function cited | cite and re-read the function |
| · 6.3 Practical consequences | medium | no function cited | cite and re-read the function |
| 7. Adding a second world: checklist | medium | cap 2/2 | capture (class U) |
| 8. Adding or reducing zones within a world | medium | cap 1/1 | capture (class U) |
| 9. Open points / caveats | – | open points / boundary list, no claim to rate |  |
| Sources | medium | cap 2/2 | capture (class U) |

<!-- X02-RATINGS:END -->

## 3. Adversarial re-check

State: §3.1–§3.2 (part 4), §3.3 (part 5: ITEMDB order, zone ↔ WM hand-over) and §3.4 (parts 6 and 6b: low zone rows
Z01–Z13) and §3.5 (part 7: low client-facing Login / WM packets, remaining class B / R / O hits) done. §3 is
complete; what stayed open or was not re-checked is listed per part and goes to the scenarios (parts 8 and 9).

### 3.1 Method

Each row is one claim that other items build on. For each, the function was re-read with
`clean.py re-data/exports/zone-pdb - <addr>` and the claim was attacked from the side its author did not use: the
2016 `Zone.pdb` type (`pdb.py … types`), the vtable slot's real target (`rtti.py`: slot → address → PDB name), every
writer and reader of the member (a search of `zone-pdb/decomp.c` for the member name), and counts over all handlers
of a session class instead of the two or three the author read. Verdicts:

- **confirmed**: the attack failed; the evidence is named.
- **refined**: the statement holds, but its name or its scope was wrong in a way that misleads a reader.
- **corrected**: the statement is false; the correct one follows with `@ FUN_…`. Every corrected and refined row is
  also in `docs/knowledge/X02.md` §0 for X01 and the owners.
- **superseded**: a later item already recorded the correction (named); not repeated in `X02.md`.
- **open**: static reading cannot settle it; it goes to a capture scenario (part 8).

All names in this section are from the 2016 `Zone.pdb` *(pdb2016)* unless marked as ours.

### 3.2 Part 4: the `ref` header, object handles, player members, Z03's shared mechanisms

Result: 53 rows (each one line or one group of lines of the source): 34 confirmed, 8 refined, 7 corrected,
4 superseded, 0 open. No new original-server bug.

#### 3.2.1 The 6-byte `ref` header (`docs/knowledge/Z01.md` §6, `docs/knowledge/C02.md` §3)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| R1 | the prefix is `NETPACKETZONEHEADER { u16 clienthandle; u32 charregistnumber }`, 6 bytes *(pdb2017)* (Z01 §6) | confirmed | same struct, size 6, in the 2016 `Zone.pdb` and `WorldManager.pdb`: no longer *(pdb2017)* |
| R2 | "2017 `PROTO_*` structs mostly omit it, so a PDB offset = 2016 − 6" (Z01 §6, C02 §3) | **corrected** | The header is a **member** of 188 `PROTO_NC_*` structs of the 2016 `Zone.pdb` and 29 of `WorldManager.pdb` (211 different structs; first member in 178 / 23). All 197 of them that exist in the 2017 PDB carry it there too, at the same place. For these structs no offset shifts. The "− 6" rule holds only for the opcodes whose struct has **no** `NETPACKETZONEHEADER` member although the wire has one: the 81 server ↔ server opcodes of C02 §4 "same after the 6-byte header" (for example 0x3411 / 0x3414 / 0x3423 / 0x3428 / 0x3429, wire = header + struct *(captured)*, `docs/knowledge/P02.md` row S01). Rule for a reader: look for the member in the struct first; shift by 6 only when it is absent and the 2016 length says so |
| R3 | the header is always the first field (Z01 §6 "start with") | **corrected** | Not always. In 16 of the 211 structs it sits later: after a `u16` error or count (`PROTO_NC_DICE_TAISAI_DB_*`, 9 structs at +2 / +4 / +6), after the 3-byte raw frame header of the `…_SEND` wrappers (+3: `PROTO_NC_CHAR_ZONE_CHARDATAFAIL_ACK_SEND`, `PROTO_NC_USER_KICKOFFFROMWORLD_CMD_SEND`), or at the end of the ping-test bodies (+0x2e / +0x56: `PROTO_NC_MISC_PINGTEST_CLIENT_ZONE_DB`, `…_TOOL_WM_CLIENT_ZONE_DB`) |
| R4 | "WM→zone and DB→zone messages about a player start with the 6-byte `ref`" (Z01 §6) | refined | True for most, not all. Some answers about a player carry only a `u16` handle and no character number: `PROTO_NC_PET_SET_NAME_DB_ACK { u16 nError; u16 nMasterHandle; u32 nPetRegNum }` (8 bytes, no header), read as `som_GetObject(pkt+4)` by `GameDBSession::gds_NC_PET_SET_NAME_DB_ACK` @ FUN_004d1250. A handler's first lookup tells which form it is |
| R5 | "handlers look the player up with `som_GetObject(ref.objHandle)` and usually compare `charNo` and `IsClosing`" (Z01 §6) | confirmed, with numbers | Counted over every `GameDBSession::gds_NC_*` and `WorldManagerSession::wms_NC_*` function: DB 186 handlers, 163 call `som_GetObject`, of those 147 compare vt 0x344 (`so_GetCharRegistNumber`), 108 test vt 0x300, 102 do both, **10 neither**; WM 121 handlers, 41 call it, 30 / 34 / 27, **4 neither**. The zone-ring handlers (`ZoneListenSession`, 24) never test vt 0x300 (9 look up, 9 compare the number). The 14 "neither" handlers are listed under §3.2.6 |
| R6 | "zone-wide messages fill it with `{0xFFFF, -1}`" (Z01 §6) | refined | Also used in a per-player message: `ShinePlayer::so_RefreshWMSSocket` @ FUN_00552190 sends WM 0x0C31 as `{ header = {0xFFFF, 0xFFFFFFFF}, +6 u16 wmHandle (vt 0x340), +8 u32 charNo (vt 0x344) }`, 14 bytes with the opcode. `{0xFFFF, -1}` means "no zone object to answer to", not "zone-wide" |
| R7 | handlers get `packet` pointing at the opcode; payload offset 0 = `packet + 2` (Z01 §6) | confirmed | `gds_NC_HOLY_PROMISE_DB_WITHDRAW_CEN_REWARD_ACK` @ FUN_00484040 reads the handle at `param_1[1]` (`NETCOMMAND` is 2 bytes); FUN_004d1250 reads +4 = payload +2, the `nMasterHandle` of its struct |
| R8 | `vt[0x300]` = "IsClosing (also true when the session is closing)" (Z01 §4, §6) | refined | Official name `ShinePlayer::so_IsEmpty` @ FUN_00559880: `sp_WillDisconnect != 0`, or the session object's vt 0xc returns 0. "IsClosing" is our name |

#### 3.2.2 Object handles and classes (`docs/knowledge/Z01.md` §2–§3)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| H1 | the 13 handle ranges and type codes of §3 | confirmed | every bound re-read in `ShineObjectHandleUnion::sohu_HandleSplit` @ FUN_00633650 (Z01: `ObjectHandle_Decode`, our name): 8000, 0x251c, 0x2904, 0x34bc, 0x42bc, 0x43bc, 0x4bbc, 0x4fa4, 0x509e, 0x5486, 0x567a, 0x5a62, then 0x5c56…0x6231 for type 12; the subtracted bases give pool index = handle − range start |
| H2 | the table has no hole | refined | handles 23138–23637 (after the movers, before the pets) decode to type 0xFF / index 0xFFFF. The table shows the jump but does not say so |
| H3 | the object sizes of §3 (0x2568, 0x2c058, 0xd100, 0x28b, 0x188, 0x256c, 0x266c, 0x1d3, 0x1c8, 0x1f14, 0x2598, 0x202c, 0x25d4) | confirmed | all 13 are the class sizes in the 2016 `Zone.pdb` (`ShineMob`, `ShinePlayer`, `ShineMiniHouse`, `ShineDropItem`, `ShineAxialFlag`, `ShineNPC`, `ShineBandit`, `ShineEffectObject`, `ShineMagicField`, `ShineDoor`, `ShineServant`, `ShineMover`, `ShinePet`) |
| H4 | `vt[0x4d0]` = object type (Z01 §4, Z03 §1) | confirmed | the `ShinePlayer` slot points at FUN_005551b0, `return 2`. The PDB names it `ShineObject::so_GetKQTeamType`: the linker folded identical bodies, the name belongs to another function with the same code *(inferred)*. Used as the type test (`!= 2` → "Not Player Handle", `!= 12` → "Not Pet Handle") in FUN_004d1250. Do not take the PDB name of this slot |

#### 3.2.3 `ShinePlayer` members (`docs/knowledge/Z01.md` §4, 36 lines)

Checked line by line against the 2016 class layout (`docs/knowledge/S01-player-offsets.tsv`) and, where the accessor
is named, against the vtable slot's function.

| # | Line | Verdict | Evidence / correct statement |
|---|---|---|---|
| M1 | +0x04 handle, +0x66 → position, +0x6a → direction, +0x76 → layer, +0x7a → FieldMap | confirmed | `so_handle.sohu_Handle`, `so_LocateInfo.location` / `.direct` (pointers; `so_datasync` @ FUN_00559790 dereferences both), `so_layer.layer`, `so_Field` |
| M2 | +0xe9c ptr → u8 mode, `vt[0x484]` | confirmed | `smo_Mode { u8 tempmode; u8 *mode }` at +0xe98; `smo_GetMode` @ FUN_00549800 returns `*smo_Mode.mode` |
| M3 | +0x1c00 "base move speed" | refined | `smo_Param.Total.MoveSpeed`: the **total** layer (15) of stat 19, not a base value (layers: Z12 §1.1) |
| M4 | +0x5cb8 flags: 0x02 linking out, 0x04 set by vt 0x4b4, 0x08 hide-except-me | confirmed, named | `sp_MiscFlag`: bit 1 `JustLink` (set only in `so_LinkTo` @ FUN_0049ad30), bit 2 `DataRecieve` (set in `so_StoreCharData` @ FUN_0055ab60 = vt 0x4b4), bit 3 `SoloingMode` (set by `sp_NC_MISC_HIDE_EXCEPT_ME_ON_CMD` @ FUN_0043e880, cleared by `…_OFF_CMD` @ FUN_00441940, `sp_NC_MAP_LOGINCOMPLETE_CMD` @ FUN_00443390 and `sp_ReviveNow` @ FUN_0057d290). Not in Z01: bit 0 `JustRevive` (set by `sp_ReviveReqProcess` @ FUN_00451bd0, read by `so_SaveLocation` @ FUN_004542f0), bits 4 / 5 `AccountStorage_opened` / `AStorageAnywhere_opened`, bit 6 `LinkReserv_link` (cleared in `so_Routine` @ FUN_0056c790), bit 7 `InAdminImmortal` |
| M5 | +0x5e10 → ClientSession (`vt[0xa70]`), +0x7e28 / +0x7e2c send objects (`vt[0x2fc]` / `vt[0x2f8]`) | confirmed | `sp_SocketSession`; `sp_SocketContainer.gamestream` ← `so_GetGameSocketStream` @ FUN_00559870, `.datastream` ← `so_GetDataSocketStream` @ FUN_00559860 |
| M6 | +0x7f32 ptr → character block | confirmed, named | `sp_CharBriefInfo.bic_BriefInfo` (pointer into the brief-info packet buffer `bic_pack` at +0x7e34) |
| M7 | +0x7f39 userNo, +0x7f3d charNo, +0x7f41 name[20], +0x7f57 exp, +0x7f67 HP, +0x7f77 money, +0x7f7f map[12], +0x7f9f prison minutes | confirmed | `sp_CharData.usrregnum`, then `sp_CharData.toclient.basedata.{chrregnum, charid, Experience, CurHP, Cen, logininfo.currentmap, prisonmin}`; the two *(inferred)* marks (exp, money) can go (also Z07 §0). `+0x7f7f` is the **current** map of the login info, "savedMap" is our name |
| M8 | +0x7f8b "position/direction snapshot", `vt[0x4c0]` | confirmed, named | `basedata.logininfo.currentcoord { xy, dir }`, written by `so_datasync` @ FUN_00559790 from the live position and direction |
| M9 | +0x7fa1 u8, `vt[0x4d4]`, "0x10C6 at login" | confirmed, named | `basedata.adminlevel`; `so_AdministratorLevel` @ FUN_00559740 |
| M10 | +0x8e2c inventory, +0xfaa8 InventoryLocking (`vt[0x7d4]`) | confirmed | `sp_Item.itembag.ci_Inventory`, `sp_Item.invenlocklist` (`so_ply_GetInventoryLockList` @ FUN_0055a1d0); lock index `icl_Index` at +0xfaac |
| M11 | +0x17d5f trade partner, +0x17d7c last clicked NPC handle | confirmed | `sp_tradeboard.tb_opposit`, `sp_NPCProcess.npchandle` |
| M12 | +0x2931c wmHandle (`vt[0x340]`), +0x29620 opcode 0x203E, +0x2a7d4 connectFrom, +0x2a798 logout time, +0x2aa54 chat block until, +0x2ab44 tutorial info, +0x2ab49 requestedName[20] | confirmed | `sp_extra.pecd_worldmanagerhandle`, `sp_SpeedNotice.sn_NetCommand`, `sp_ConnectFrom`, `sp_NormalLogoutTick`, `sp_Spammer_ChatBan`, `sp_TutorialInfo.nTutorialState`, `sp_LoginCharID` |
| M13 | **+0x29638 "class/shape block", `vt[0x420]` (+0x488, +0x489, +0x48a)** | **corrected** | `sp_CharacterTitle`, a `CCharacterTitleZone` (0xcd0 bytes); vt 0x420 = `so_GetCharacterTitle` @ FUN_0055a1b0 returns its address. +0x488 / +0x489 are the current title's type and element (`CHARTITLE_BRIEFINFO`, Z12 §6.9, Z08 §7.2). It has nothing to do with class or shape (those are `sp_CharData.toclient.shape` at +0x7fa6). Later items use the right name (Z07 §1.3, Z18); still wrong in Z01 §4, in Z02-actions §3.1 / §3.2 (the calls FUN_005cc2a0 and FUN_005cc2d0 on `p+0x29638`, described as "class/shape block" hooks, are title counters) and in Z04-items §2.1 (`p.vt[0x420]` → FUN_005cc020, "quest/collection hook (inferred)", is a title hook) |
| M14 | **+0x2a800 "flag set by 0x0C32, cleared at the start of every handler", `vt[0x330]`** | **corrected** | `sp_isPossibleNewConnect`; vt 0x330 = `so_SetPossibleNewConnect(v)` @ FUN_00549420. It is cleared in exactly two handlers, the first two packets of a new client connection: `sp_NC_MISC_SEED_REQ` 0x0806 @ FUN_00451a30 and `sp_NC_MAP_LOGIN_REQ` 0x1801 @ FUN_00452590 (plus the constructor). It is set to 1 by three callers: `sp_NC_USER_USE_BEAUTY_SHOP_CMD` 0x0C32 @ FUN_005520d0, `so_ply_ToNormalLoc` @ FUN_00552350 and `GameDBSession::gds_NC_ITEMDB_CLASS_CHANGE_ACK` @ FUN_00469590. Its one reader (vt 0x334 `so_GetPossibleNewConnect` @ FUN_0055a5c0) is `so_RefreshWMSSocket` @ FUN_00552190 (vt 0x338): only when the flag is 1 does it send WM 0x0C31 (R6). Meaning: "this player is about to reconnect to a zone; tell the WM to expect it" *(inferred from the three setters, each followed by a client reconnect)*. Z01-core §9 ("every handler clears it on entry") and the open point in its §12 are wrong the same way |
| M15 | +0x2a944 u8 closing, `vt[0x300]` | confirmed | `sp_WillDisconnect`; see R8 |
| M16 | +0x2aa40 next save time, `vt[0xac0](now, 600)` = now + 6000 | confirmed | `tAutoSaveTime`; `so_SetAutoSaveTime(t, n)` @ FUN_005608c0 stores `t + n * 10` |
| M17 | "important vtable slots" list (0x2ec, 0x308, 0x338, 0x33c, 0x4d8, 0x57c, 0x5f8, 0x5fc, 0x600, 0x664, 0x784, 0x890, 0xa24) | confirmed | each slot resolves to the function of that name; two differ in prefix only: 0x338 is `so_RefreshWMSSocket` (its profiler string says `sp_…`), 0x784 is `so_ply_Notice` @ FUN_005977e0 (Z01: "send a system chat line") |

#### 3.2.4 Z03's shared mechanisms (`docs/knowledge/Z03.md` §1–§2, Z03-combat §1, §4.2, §6.1)

| # | Claim | Verdict | Evidence / correct statement |
|---|---|---|---|
| C1 | flag byte `obj+0x1e78`: bit 2 Fear, bit 3 killed, bit 5 Captivate | confirmed | `smo_Flag`: bit 2 `InFear`, bit 3 `DeadProcessComplete`, bit 5 `InCaptivate` |
| C2 | bit 0 "routine ran" | superseded | `Retrate` (README §5.5, Z09 §2.2) |
| C3 | bit 1 "alternate (ranged) damage path", bit 4 "skill blast armed", bit 6 "ignore-cooldown", bit 7 "generic switch (vt 0xbf0)" | **corrected** (names and two meanings) | bit 1 `DuringFlying`, bit 4 `InSkillShift`, bit 6 `ChineCast`, bit 7 `DamageAbsorb` (vt 0xbf0 = `smo_SetFlagDamageAbsorb(v)` @ FUN_005558d0). Bit 7 is the damage-absorb switch of the shield actors, not a generic one; bit 1 marks an object in flight. Later items use the official names (Z22, Z23, Z25; `DuringFlying` in Z09); Z03 §6.6 and `Z03.md` §1 still carry ours |
| C4 | `smo_SetCaptivate` = FUN_0055d570, vt 0xf1c | refined | FUN_0055d570 is the `ShineMobileObject` body (calls vt 0xa48, then sets bit 5). The **player's** slot 0xf1c is the override `ShinePlayer::smo_SetCaptivate` @ FUN_00564e50: it calls the base and, when switched on, allocates `m_pCaptivateAI` (a 0x324-byte `MobActionArgument` with the `targetting` actor and the player's own target selector), freed when switched off. A captivated player is driven by mob AI; Z11 §8.5 documents this for `&captivate`, Z03 §6.6 does not |
| C5 | stat matrix `param[layer*0xcc + stat*4]`, 51 stats, "≥ 16 layers", layer names "1 item, 5/6 upgrade, 8 weapon title …" | superseded | `Parameter::Container` = exactly 16 `Parameter::Cluster` layers of 51 `int`; the layer and field names of Z03 are replaced by Z12 §1.1 (PDB members; `+0xcd0` = `MissPercentFix`, `+0xcdc` = `PassiveCriDamageRatePlus`, in addition to the rows of README §5.5) |
| C6 | rule set at `obj+0x1e74` | confirmed | `smo_RulesOfNormalAttack` (`RulesOfEngagement *`): the pointer is the **normal-attack** rule set; a skill's rule set comes from its `SkillEntry +0x70` (same § of Z03) |
| C7 | `hpchangeorder` = `++(u16 obj+0x1d78)` via vt 0x7e8 | confirmed | `smo_HPChangeOrder`; `so_mobile_GetHPChangeOrder` @ FUN_00555890 pre-increments and returns it. The "getter" changes state: every call consumes a number |
| C8 | `+0x1d7c` dead flag (vt 0x28), cast state at `+0x1d84` (end time, skill id, target, xy, SkillEntry, produce recipe) | confirmed | `smo_BattleObject { u8 alreadydead; i32 damagereserve }`; `smo_SkillCast` = `SkillCastStruct` (0x2c): `scs_BlastTime`, `scs_Skill`, `scs_BattleSkill` (+8), `scs_ProduceSkill { sklidx, prdidx }` (+0x14), `scs_UseItem` (+0x1c), `scs_Empower` (+0x28), `scs_AttackCode` (+0x2a). Not in Z03: `damagereserve` and the use-item cast |
| C9 | `player+0x7f37` deferred cast error, `player+0x7f36` cease-fire flag | confirmed | `sp_SkillFinish.scf_ErrorType` (u16), `sp_CeaseFireSender.cfs_Flag` |
| C10 | `player+0x2a784` one-shot `TimeScheduler`, `player+0x173d0` delayed-hit queue | confirmed | `sp_TimerStr.ts_Limit`, `sp_NormalAttackDamageTick.nadt_DamageTime` |
| C11 | battle statistics vt 0x428: "+4 kills-exp, +8 damage dealt/taken, +0x1c deaths×50, +0x20/+0x24 PvP deaths/kills, +0x28 PvP rating" | superseded | `BattleStat` (0x2c) per KQ joiner, one shared static for everything else; fields and every writer in Z16 §3.1 (`bs_KillScore`, `bs_DamageAmount` (dealt only), `bs_HealAmount` (never written), `bs_SkillBlast`, `bs_KnockDownNum` += 50 per death). Z03's table omits +0xc / +0x10 and that outside a KQ all objects write one object (`so_GetBattleStat` @ FUN_00498d60) |
| C12 | `CharaterSkillList` at `player+0x17d0c` (entry +4 cooldown end, +8 empower bits) vs Z23's +0x17d08 | confirmed (both) | the object `sp_SkillList` starts at +0x17d08; +0x17d0c is its vector's first-element pointer `csl_Skill._Myfirst`, which the code reads directly. Entry layout: Z23 knowledge (0x14 bytes) |
| C13 | inventory lock index at `player+0xfaac`, locks in `player+0xfaa8` | confirmed | M10 |
| C14 | `BattleContext` (Z03 §4.2), our name, 0x2c bytes | confirmed, named, three fields corrected | `EngageArgument` (0x2c): `att`, `def`, `sklinfo`, **+0x0c `SKILL_EMPOWER empower`** (Z03: "reserved"), +0x0e `actionnumber`, +0x0f `attackcode`, +0x10 `iscritical`, +0x11 `ismiss`, +0x12 `isdead`, +0x13 `isshieldblock`, +0x14 `isresist`, **+0x15 `isDamege2Heal`** (missing in Z03), +0x16 `isImmune`, +0x18 `attackloc`, +0x1c `damagerate`, +0x20 `crirateadd`, **+0x24 `MultiHitArgument *pMultiHitArg`** (Z03: "ptr"), +0x28 `nBMPDamageRate` (Z03: "AP rate") |
| C15 | `AbStateEntry` (Z03 §6.1): +0 AbState row, +4 save-type row, +8 resist slot, +0xc + strength·0x24 blocks, strength 1…39 | confirmed, named | `AbnormalStateDictionary::AbState::AbStateStr` (0x5ac): `index`, `pSaveTypeInfo`, `int *debuffresist`, `AbStateStrArgument subabstate[40]` (0x24 each: `assa_info`, `assa_Effect[4] { SubAbstateAction action; int value }`). The array has 40 entries (index 0 exists). `debuffresist` is typed as a pointer; Z03 reads it as a byte offset into the parameter block: not re-read here, see Z22 |
| C16 | `AbstateElementInObject` 0x74 bytes; +0 flags, +4 index, +8 setter object, +0xc setter charNo, +0x10 level, +0x14 attack power, +0x18 strength, +0x1c set time, +0x20 end time, +0x24 next tick, +0x28 interval, +0x58 / +0x5c origin xy | confirmed | `aeo_Flag { f_Cured, f_Dispeled, f_SystemRemove }`, `aeo_Index`, `aeo_Caster { obj, chrregnum, nLevel, nAttackPower }`, `aeo_Strength`, `aeo_Tick { start, terminate, Metronome nextaction { m_NextTick, m_TickInterval } }`, `AbsSetData.CenterLoc` |
| C17 | element "+0x54 actor private value" | refined | `int aeo_RestCount` |
| C18 | **element "+0x70 skill id that set it"** | **corrected** | `MiscDataTable::MiscData_AbState *aeo_MiscData`, set in `aeo_Set` @ FUN_0040a340: the state's row of the misc-data table `{ u16 mdas_AbStateID; mdas_ResetCondition { run, walk, attack, attacked … }; mdas_ResetEquipment { eqwhere, eqclass } }`. `aeo_Run` @ FUN_004a41c0, `aeo_Walk` @ FUN_004a4230, `aeo_Attack` @ FUN_004a42a0, `aeo_Attacked` @ FUN_004a4310 and `aeo_ItemChange` @ FUN_004a4380 test it: it decides which player action removes the state. No skill id is stored in the element |
| C19 | element fields not in Z03 | refined | +0x2c `aeo_PartyEnchant[5] { ABSTATEINDEX soul; AbStateStr *skillindex }` (the five `PartyState` links of the AbState row), +0x60 `SetItemData::SetItemAbstateEffect aeo_SetItemEffect` (0x10; Z21 §5) |
| C20 | element list "at obj+0x1cc+0xcb0, 296 slots" | superseded | `AbstateListInObject { asl_Element[28]; List asl_List }` (0xcc8): 28 states per object (README §5.5, Z18 §3.2). `obj+0xe7c` is the list head, `obj+0xe94` = `smo_Abstate.parameterchange` (the recalculation request of Z03 §6.1: confirmed) |
| C21 | vt 0x3e4 "HasAbstate" FUN_00555a20, vt 0x638 set, vt 0x650 reset, vt 0x430 "GetParam", vt 0xef0 → `so_DamagedBy` (0x5c0) / `so_KilledBy` (0x5bc), vt 0xed8 `smo_BashStop`, vt 0xbf8 | confirmed, named | `so_AbnormalState_IsSet`, `ShinePlayer::so_AbnormalState_Set` @ FUN_004162d0, `ShinePlayer::so_AbnormalState_Reset` @ FUN_00559ef0, `so_parameter` @ FUN_00555720, `smo_AttackedDamage` @ FUN_0042aeb0, `ShinePlayer::so_DamagedBy` @ FUN_00431500, `ShinePlayer::so_KilledBy` @ FUN_00433be0, `ShinePlayer::smo_BashStop` @ FUN_0042e840, `so_ply_PassiveSetAbstate` @ FUN_005798e0 (0xbf8: superseded, README §5.5) |

#### 3.2.5 Candidates noted in part 3

| # | Candidate | Verdict | Evidence / correct statement |
|---|---|---|---|
| P1 | Z04-items §3.2: "class 36 PUP (minimon) and `p+0xaad8*4` in 1..8 (a minimon is summoned, inferred)" | **corrected** | `ItemBreaker::ib_OK` @ FUN_0048d0d0 tests `sp_PetInfo.nSummonState` (+0x2ab60) for `PSST_CASTING (1) … PSST_LINKING_RESUMMON (8)`, that is "not `PSST_NONE`": a **pet** is being summoned, is out, or is being put away (enum `ShinePlayer::PetSummonStateType`: 0 NONE, 1 CASTING, 2 CASTED, 3 WAIT_CREATING, 4 WAIT_1ST_LOADING, 5 1ST_SUMMONED, 6 RESUMMONED, 7 UNSUMMONNING, 8 LINKING_RESUMMON). `ITEMCLASS_PUP = 36` is the pet item class; the refusal is the pet packet 0xD411 `NC_PET_USE_ITEM_FAIL_ACK`. The minimon (auto-potion) state is another member, `sp_UseItemMinimon` at +0x2abec. `docs/knowledge/S01.md` §3.3 ("pet summon state") was right |
| P2 | `Z03.md` +0x17d0c vs `Z23.md` +0x17d08 | confirmed (both) | C12 |
| P3 | `X02-rate.py pdbmiss` lines of `K:Z01` and `K:Z03` (11 lines) | confirmed | all are members named next to another, correct, offset of the same line (`+0x7e28 / +0x7e2c`, `+0xfaac … +0xfaa8`, `+0x7f37 … +0x7f36`): no wrong offset among them |

#### 3.2.6 What the re-check adds for later parts

- **Handlers that trust the handle alone** (R5; no character-number and no `so_IsEmpty` test in the handler itself):
  DB `gds_NC_HOLY_PROMISE_DB_GET_CEN_REWARD_ACK` @ FUN_00483d10, `…_WITHDRAW_CEN_REWARD_ACK` @ FUN_00484040,
  `gds_NC_MISC_PINGTEST_CLIENT_ZONE_DB` @ FUN_00550fc0, `…_TOOL_WM_CLIENT_ZONE_DB` @ FUN_00551130,
  `gds_NC_CHARSAVE_DB_UI_STATE_SAVE_ACK` @ FUN_00551360, `gds_NC_CHAR_REGNUM_VARIFICATION_ACK` @ FUN_00551a80,
  `gds_NC_MINIHOUSE_DB_PORTAL_LIST_ACK` @ FUN_0056ed60, `…_PORTAL_ADD_ACK` @ FUN_0056eef0, `…_PORTAL_DEL_ACK`
  @ FUN_0056f080, `…_VISITER_COUNT_ACK` @ FUN_0056f1f0; WM `wms_NC_CHAR_TUTORIAL_INFO_ZONE_CMD` @ FUN_0044d3d0,
  `wms_NC_GUILD_TOURNAMENT_ZONE_OBSERVER_ENTER_ACK` @ FUN_00478be0, `wms_NC_INSTANCE_DUNGEON_LEVEL_SELECT_CHECK_ACK`
  @ FUN_00485540, `…_JOIN_ACK` @ FUN_00485b90. The count is a text test on the handler body: a handler that forwards
  to a virtual which then checks is in this list too. Read so far: FUN_00484040 forwards to vt 0x9d4
  (`so_ply_HolyPromiseWithdrawCenReward` @ FUN_00484100) with no check, which is the recorded bug Z08-B14 (the money
  goes to whoever holds the handle now). The other 13 are checked in part 6 (same pattern, same risk).
- **Error classes seen** (for §1's counts, not added to them): N (our name wrong or misleading) 9: R8, M3, M13, C3,
  C4, C14, C17, C18, P1; B / R (a "every" or "always" that is two call sites) 2: M14, R6; P (a 2017-PDB rule taken
  as general) 2: R2, R3; S 0: **no offset in `Z01.md` §4 or `Z03.md` §2 is wrong**; the errors are all in what the
  member means. This matches §1: an offset read from code is reliable, the label next to it is not.
- **PDB names of folded functions** (H4): a slot whose PDB name does not fit the use (`so_GetKQTeamType` for the
  type getter) is an identical-code fold. Read the body, not the name.
- **Ratings changed by this part** (hand rows in §2.2): `Z01.md` §3 → high, §4 and §6 → medium, `Z03.md` §2 → medium
  with the corrected rows named.

### 3.3 Part 5: ITEMDB message order, zone ↔ WM hand-over

Method as in §3.1. Zone and WM names are from the 2016 `Zone.pdb` / `WorldManager.pdb` *(pdb2016)*; the Character
server has no PDB, its names are ours. Packet layouts were checked against `docs/protocol/pdb2016-layouts.json`
first (part-4 rule R2 / R3). 35 rows: 23 confirmed (two with a part superseded by P02 / X01), 9 refined,
1 corrected, 1 open, 1 note.

#### 3.3.1 ITEMDB commit model (`docs/knowledge/Z05.md` §1–§2, Z05-itemdb §1, §3, §11)

The attack here is a count over **all** 102 `GameDBSession::gds_NC_ITEMDB_*` handlers (a text test on each body:
calls on the lock list's vt 0x14 / 0x1c / 0x20 / 0x28, `so_Disconnect` codes, the lookup tests), instead of the
handlers Z05 read one by one.

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| I1 | style 2 ("apply → DB, disconnect on failure") is used by drop, pick-up, pick money and `INC_DEC_MONEY` only (Z05.md §1, Z05 §1.1) | confirmed, with counts | Exactly 6 functions set the pending flag (lock-list vt 0x14 with 1): `ItemInventory::ii_DropAll` @ FUN_00529a70, `ii_DropLot` @ FUN_00529c20, `ii_PickAll` @ FUN_0052f1b0, `ii_PickMerge` @ FUN_0052f440, `ShinePlayer::so_ply_PickupMoney` @ FUN_0052fe80, `so_ply_IncDecMoney` @ FUN_0052ffc0. Exactly 6 answer handlers clear it (0x3417, 0x341A, 0x341D, 0x3420, 0x3439, 0x347B) and exactly their 6 FAIL partners call `so_Disconnect(0x684)`. No other ITEMDB handler touches vt 0x14 or uses 0x684 |
| I2 | style 1: success → `icl_Apply_N_Free`, failure → `icl_Free`, memory untouched on failure (Z05 §1.1) | confirmed, with counts | 50 handlers call apply (vt 0x1c or 0x20), 47 call free (vt 0x28), 31 hold both (one handler for success and failure codes). 24 handlers hold neither: they forward to a player virtual (USE, DEPOSIT, WITHDRAW, CHARGED_*, QUESTREWARD, the ENDURE pair, academy storage) or only answer the client (OPENSTORAGE, ITEMBREAK, ITEMTOTALINFORM); Z05 documents each under its § |
| I3 | "lot mismatch after a merge / split → `so_Disconnect(0x68c)`" (Z05.md §1, Z05 §11) | refined | 0x68c is in 5 success handlers: MERGESUC @ FUN_00533630, SPLIT_N_MERGESUC @ FUN_00533a40, SPLITSUC @ FUN_00539740 **and RELOCSUC @ FUN_00533070, EXCHANGESUC @ FUN_00533350**. In the two move handlers it follows the client ACK (`so_SendErrorCode(0xc, 0xc, 0x241)` = 0x300C `{0x241}`) when vt 0x968 (1) returns 0 (the `ItemLotInspector` check of Z05 §1.1). A plain move can disconnect with 0x68c too, after its success ACK went out |
| I4 | the pending flag "makes every other item request refused until the answer" (Z05 §1.1) | refined | True for the 65 functions that test the list's vt 0x10 / 0x18 (all client item requests, and `so_LinkTo`). But the flag is one byte (`L+0x7828 = arg`), not a counter, and the two money senders set it without testing it: `so_ply_PickupMoney` and `so_ply_IncDecMoney` change `sp_CharData…Cen`, send the request and set the flag unconditionally. Two style-2 requests can therefore be in flight; the first answer clears the flag while the second is still out. Whether their callers test first is **open** (scenario, part 8: pick up two money drops in one tick; a script money reward during a pick-up) |
| I5 | "no timeouts: a lost answer blocks the player's item operations until relog" (Z05.md §1, Z05 §11) | refined | It also blocks every map change: `so_LinkTo` @ FUN_0049ad30 tests the same vt 0x10 and returns after the log "Link during item operation" (Z01 §7.1 has the test, Z05 does not name the effect). Logout is **not** blocked: `sp_Schedule_Logout` @ FUN_00558160 never looks at the lock list (its two gates are in L6) |
| I6 | handler skeleton: `som_GetObject(ref.handle)`, then `so_IsEmpty` and the charNo compare; the handlers that skip a test are noted per handler (Z05 §1.6) | confirmed | Text test: 9 handlers use vt 0xbbc instead of `so_IsEmpty` (MOVER ×2, ITEMMONEY_BUY, RANDOMOPTION ×3, CLASS_CHANGE, MAPLINK, MIX: the list of §1.6); 8 more compare the charNo and never test `so_IsEmpty` (BELONGED_CANCEL, TERMEXTEND, ITEMREBUILD, ITEMINFO, REPURCHASE ×2, ITEMTRADE ×2) and 4 never compare the charNo (DROPALLSUC, DROPLOTSUC, OPENSTORAGE_FAIL, CHAT_COLOR). Z05 carries a "(no IsClosing)" / "no charNo check" note on each of those I looked up (§2.2, §2.6, §3.1, §5.3, §6.2, §6.6, §8.5) |
| I7 | the request has already changed memory and told the client when a style-2 answer arrives; the answer only sends the ACK (Z05 §3.1–§3.3) | confirmed *(captured)* | Pick-up: 0x341C and 0x3001 leave in the same ms, 0x300A `{0x341}` only after 0x341D (`capture-validation.md` §7.6.1, three pick-ups). `so_ply_PickupMoney` calls `so_ply_ChangeCen` (vt 0x448 → 0x1033) before it sets the flag: the money shows before the DB answered |
| I8 | answers for a closed or replaced player are dropped without freeing; "the lock list dies with the object" (Z05.md §1) | confirmed | Every handler returns on the failed test before it reaches the list; `sp_Schedule_Logout` and `so_banning` free the object without touching `sp_Item.invenlocklist`. The DB has committed by then: for style 1 the player gets the result at the next login, nothing is lost |
| I9 | Z05-B5: the Character server sends 0x3415 as `{ref, err 0x28a, lock}`, the zone reads the lock where the error is (Z05.md §3) | confirmed (Character side) | `fc_NC_ITEMDB_UNEQUIP_REQ` *(ours)* @ character FUN_0040afc0: failure = 0x3415, 10 bytes `{ref[6], u16 0x28a @+6, u16 lock @+8}`; success = 0x3414, 8 bytes `{ref[6], u16 lock @+6}` |
| I10 | Character server order for a purchase: DB write, answer, then logs (D03 §2.1; D03.md "every cen purchase credits 10 % to the holy-promise upper member") | confirmed | `fc_NC_ITEMDB_BUYALL_REQ` *(ours)* @ character FUN_00409300: `ItemBuy_Create` → 0x340B `{ref, lock}` to the zone → GameLog 0x0448 → GameLog 0xC80D → `usp_HolyPromise_setMoney(charNo, price × 100 / 1000, 10)`. The zone has its answer before the logs and the credit are written. Failure: 0x340C `{ref, err, lock}` with 0x205 (procedure result 1) or 0x206 (any other). No length test, as D03.md says |
| I11 | `NC_CHARSAVE_ALL_REQ` 0x4001 is 0x6f bytes `{u16 objHandle, u32 charNo, …, SaveLevel @+0xc, SaveLocation @+0x1d, SaveStat @+0x4d}` (Z01 §8.4) | confirmed | Sent with length 0x71 = opcode + 0x6f; 0x6f = `NETPACKETZONEHEADER` (6) + `PROTO_NC_CHARSAVE_ALL_REQ` (105). The struct's own first member `handle {bufferlocation, chrregnum}` is **not** the header: this is one of the "wire = header + struct" opcodes of R2. The three offsets are `level.level`, `location.map`, `stat.CurPwrStone` counted from the opcode |
| I12 | "position and money are saved by the zone's dept-16 messages" (D02 §4, note at 0x1037) | open | `PROTO_NC_CHARSAVE_ALL_REQ` has level, exp, fame, both locations, stones, HP / SP and the stat points, and **no money field**; `ws_save2DB` @ FUN_00455a10 sends 0x4018, 0x4001, 0x4005, 0x4007, 0x4009, 0x400B, 0x401A and none of their structs has one either. Money reaches the DB through the ITEMDB procedures (style 1 and 2 above) *(inferred)*. Which message, if any, writes `tCharacter` money outside an item operation is for part 7 (D02) |

#### 3.3.2 Zone ↔ WM hand-over, WM side (W01-core §6.3, §7.2–§7.4, `docs/knowledge/W01.md`)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| W1 | 0x104B: the WM answers with the real numbers only when the session's ticket is 1 and the name matches, and takes the ticket; otherwise `{-1, -1}` and session state 3 (W01 §7.2) | confirmed | `CParserZone::fc_NC_CHAR_REGISTNUMBER_REQ` @ FUN_0042f1e0. No session at all: `{-1, -1}` too, nothing else changes. Answer 0x104C = `PROTO_NC_CHAR_REGISTNUMBER_ACK` after the header, as W01 has it |
| W2 | 0x101C: 0x101E `{ref, 0x141}` without a session or CHARDATA, the reserved link destination replaces map / x / y once, then the blobs (W01 §7.2) | confirmed; order superseded | `fc_NC_CHAR_ZONE_CHARDATA_REQ` @ FUN_00428ba0: the destination is copied when the pending flag is 1 and the flag is cleared before the first blob goes out. The blob order of W01 §7.2 is superseded by the captured order (`docs/knowledge/P02.md` row W01 §7.2, 5 hand-overs) |
| W3 | 0x180D `{ref[6], u16 wmHandle @+6, u8 ? @+8, destMap[12] @+9, x @+0x15, y @+0x19, …}`; the WM stores the destination, sets the ticket and returns bytes 0x1d–0x3a in 0x180E (W01 §7.3) | refined | Layout = 2016 `PROTO_NC_MAP_LINKRESERVE_REQ` (59 bytes, header is its first member): `+8 u8 newmechineid` (the destination zone number, W01's `?`), `+9 linkto {mapname, location}`, `+0x1d linkother { link {u16 mapid, x, y}, sock {char zoneip[16], u16 zoneport}, u16 wldmanhandle }`; 0x180E = header + `linkother` (36 bytes). `fc_NC_MAP_LINKRESERVE_REQ` @ FUN_0042f420 looks the session up by `wldmanhandle` **only**: no charNo compare and no CHARDATA test, unlike its neighbours (W4, W5, W7–W9). `newmechineid` is not read by the WM |
| W4 | 0x180D for a handle with no session: "return" (W01 §7.3, not stated) | refined, X02-B3 | The handler returns 1 without an answer. The zone has already saved the character, set mode 0 and `sp_MiscFlag.JustLink` (Z01 §7.1) and waits for 0x180E: the player stays connected and stranded, the same end state as the "Link Fail Player Die" branch (X01 register) *(inferred: no timer re-sends 0x180D)* (original bug) |
| W5 | 0x180B `{u16 wmHandle, u32 charNo}`: `s.linking = 1` when the charNo matches (W01 §7.3) | confirmed, X02-B1 | Official `NC_MAP_LINKSTART_CMD {wmshandle, chrregnum}`, `fc_NC_MAP_LINKSTART_CMD` @ FUN_00429c90; a mismatch logs "ERROR … fc_NC_MAP_LIN…". The handler reads `m_pCharDataBase->chrregnum` **without the null test** its neighbours make: a 0x180B for a session back at character select (CHARDATA freed) is a null read in the WM (original bug), latent: it needs a zone that still holds the player after the WM dropped the character |
| W6 | `s.linking` (W01 §1.1, §5.1, §7.3) | refined | `CWMClientSession::m_ZoneLinking`. Writers: 1 at session init (`InitSessions` @ FUN_00437fd0), 1 by 0x180B and by the client's WM 0x0C18 (`fc_NC_USER_NORMALLOGOUT_CMD` @ FUN_00412df0), 0 only by 0x180C. Readers: `fc_NC_PARTY_JOIN_REQ` @ FUN_0041a940, `fc_NC_PARTY_ZONE_JOIN_CMD` @ FUN_0042e8c0, `CWMClientSession::JoinRaidPossible` @ FUN_00431140. Meaning: "not on a zone right now"; its only effect is that party and raid joins are refused meanwhile (W02) |
| W7 | 0x180C "map login done" `{u16 wmHandle, u16 ?, u32 charNo @+4, map[12] @+8, u8 zoneNo @+0x14, …, u8 flag @+0x2e}`; "attendance: if flagged" (W01 §7.3) | refined | Official `NC_MAP_LINKEND_CMD` (47 bytes): `+2 u16 zonehandle`, `+0x15 location {x, y}`, `+0x1d u8 StoreType`, `+0x1e u64 CharExp`, `+0x26 u64 CharMoney`, `+0x2e u8 IsPartyRelease`. `fc_NC_MAP_LINKEND_CMD` @ FUN_0042d8d0 uses `IsPartyRelease == 1` (or `CWMZoneSessionManager::IsInPartyReleaseMap(map)`) to make the character leave its party or raid (W02 §4.1 has this). The attendance request is gated by the **session's** first-join flag (`GetFirstJoinSendData`, cleared right after), not by a packet field |
| W8 | 0x0C31: `playingCharNo = -1` when it equals the charNo; "the zone finished the character logout; 0x1001 allowed again" (W01 §7.3, §5.4 note) | confirmed | `fc_NC_USER_POSSIBLE_NEW_CONNECT_CMD` @ FUN_0042c1c0, body `{u16 nWorldManagerHandle, u32 nCharNo}` after the `{0xFFFF, -1}` header. The zone sends it from two places (L5) |
| W9 | 0x400E base save: "stats u16×4 @+0x4d, u32×2 @+0x5d, u32 @+0x65, u16 @+0x69", "u16 ? @+2", "u32 @+0x15" (W01 §7.4) | refined | 2016 `PROTO_NC_CHARSAVE_2WLDMAN_ALL_CMD` (107 bytes): `+2 all.handle.bufferlocation` (the zone object handle), `+0x15 fame`, `+0x4d / 0x51 / 0x55 / 0x59 u32 CurPwrStone / CurGrdStone / CurHPStone / CurSPStone`, `+0x5d / 0x61 u32 CurHP / CurSP`, `+0x65 6 × u8 statdistribute` (Strength … RedistributePoint). `fc_NC_CHARSAVE_2WLDMAN_ALL_CMD` @ FUN_00429d40 copies only the **low 16 bits** of each stone count (the cache fields are u16); the KQ location (+0x31 … +0x48) is not copied |
| W10 | 0x4015 `{u16 wmHandle, u32 charNo, u16 partyNo @+7, u16 raidNo @+9, u32 @+6?, u8 @+0xa}`; party / raid numbers replaced by the WM's own (W01 §7.4) | confirmed, named | `{u16 wldmanhandle, u32 nCharNo, u8 game.zone.bIsGM @+6, u16 partyno @+7, u16 nRaidNo @+9}` (11 bytes). `fc_NC_CHARSAVE_2WLDMAN_GAME_CMD` @ FUN_0042a230 stores the 5 bytes +6 … +0xa after overwriting both numbers with `CParty::PartyGetNo` / `RaidSystem::GetInRaidNumber` when they differ. The cached block's first byte is `bIsGM` |
| W11 | 0x4017 `{u16 wmHandle, u64 money @+2, u32 @+0xa, u32 charNo @+0xe}` (W01 §7.4) | confirmed, named | `NC_CHARSAVE_2WLDMAN_MISC_CMD {wldmanhandle, cen, fame, nCharNo}`; @ FUN_0042a3f0 writes `Cen` and `fame` |
| W12 | "zone dept-16 handlers check `CHARDATA.charNo == payload charNo` before writing" (W01 §6.3) | confirmed for the 4 read | 0x400E, 0x4015, 0x4017 and 0x180C test session, CHARDATA and charNo; 0x180B tests the charNo without the null test (W5); 0x180D tests nothing (W3) |
| W13 | "the WM is the live owner of the character state between zones" (W01.md, first fact) | confirmed *(captured)*, scope | The cache is refreshed only by a link to another zone (`ws_save2worldmanager`, P02 row Z01 §8.4) and by the single-field messages (0x400E on level-up, 0x1073, 0x4017). After a same-zone map change or a logout it is as old as the last cross-zone link; nothing reads it then except 0x1037's log fields |
| W14 | the WM link names in `wm-pdb` | note | Ghidra resolves several `CWMClientSession` members to wrong names in `wm-pdb/decomp.c` (the ticket shows as `m_dwReportTickCount`, the session state as `_padding_`, `playingCharNo` as `m_ChatRestric._padding_`, the game block as `m_pCharDataCTData`). Use W01 §1.1's offsets for these; do not adopt the names |

#### 3.3.3 Zone ↔ WM hand-over, zone side (Z01-core §5, §7.1, §8)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| L1 | 0x104C → `so_SetRegistNumber`: name mismatch or a −1 number → `so_Disconnect(0x689)`; otherwise store the numbers and send 0x101C (Z01 §5.3) | confirmed, named | @ FUN_0044e900. `p.requestedName` = `sp_LoginCharID`; FUN_00560730 = `sp_SpamInitSpamerInfo`; the per-login resets are `csl_clear(sp_SkillList)`, vt 0xc78 (0), 0xc80 (10), 0xc8c, `ie_ViewSlot_ClearAll`, `ie_DecoActList_ClearAll`, `sp_nPolymorphAbstateIndex = MAX`, `ItemActionObserveManager::CoolTimeListClear` (vt 0x5d0). 0x101C is sent with length 0x1e = header + 22-byte struct |
| L2 | Z01-B1: 0x101E makes the zone send 0x1804 with the player's handle as the code (Z01 §5.3) | confirmed | `wms_NC_CHAR_ZONE_CHARDATAFAIL_ACK` @ FUN_005a3440 copies `param_1[1]` (the header's `clienthandle`) into the code field, then 0xFF. The error log reads "… : Invalid Object", not "Invalid ClientHandle [%d]" |
| L3 | 0x101D: a missing tutorial block "→ log"; no free tutorial map → 0x1804 `{0x31EC}` (Z01 §5.3) | refined, X02-B2 | `wms_NC_CHAR_ZONE_CHARDATA_ACK` @ FUN_005a3590. (a) After the 0x31EC failure the handler does **not** return: it marks the map and sends 0x1802 as well (already in Z07 §2, "falls through"; Z01 shows the same flow without the remark). (b) When vt 0xdfc returns null it logs "TutorialInfo Is Null" and then reads `*null` on the next line (original bug), latent: the getter returns a member that every login sets |
| L4 | 0x180E: charNo and `so_IsEmpty` tests, HP 0 or mode 3 → "Link Fail Player Die" and nothing else; else 0x180A (0x1e bytes), then `so_banning(0)` (Z01 §7.1) | confirmed; bug superseded | `wms_NC_MAP_LINKRESERVE_ACK` @ FUN_0049b510: 0x180A = the 30 bytes after the header (`linkother`), length 0x20. Between send and `so_banning` the session's vt 8 is called with `so_ply_GetClientSession` (vt 0xa70). The stranded player of the failure branch is in the X01 register |
| L5 | 0x0C31 is sent by `sp_Schedule_Logout` and by `sp_RefreshWMSSocket` (Z01 §8.1, §8.2) | confirmed; refines M14 | `sp_Schedule_Logout` @ FUN_00558160 sends it **unconditionally** after `so_Unmark(0, 1, 9)`. `so_RefreshWMSSocket` @ FUN_00552190 sends it only with `sp_isPossibleNewConnect` = 1 (M14) and has two callers: `so_ply_ToNormalLoc` @ FUN_00552350 and `ZoneServer::zs_disconnect` @ FUN_005abb60 (the socket-close path). With W8 the meaning of M14 is exact: 0x0C31 = "this character is off the zone and will not arrive by a link; the WM may accept 0x1001 for it again". A socket loss without the flag sends none |
| L6 | `sp_Schedule_Logout` waits while "`!p.vt[0x17c]()`: not ready to leave yet" and "`!p.vt[0xb2c]()`: pending save / operation *(inferred)*" (Z01 §8.1) | **corrected** | Both gates are dice-game tests: vt 0x17c = `so_IsCanSessionCloseing` @ FUN_00510ed0 (mini-game type `SMT_DICE_TAISAI`, the table object in state 2), vt 0xb2c = `so_Gamble_IsCanSessionCloseing` @ FUN_00615ee0 (`sp_Gamble_JoinType == GBT_DICETAISAI`, the gamble object in state 2). Each returns 0 until 0x32 ticks after the first refusal, then 1. Nothing about saves, items or the DB delays a logout. The Z06 names of these two (`…TaiSai_CanAutoRoll`, `S01-renames.tsv`) are wrong the same way |
| L7 | `so_Disconnect`: WM 0x0C1A `{header {0xFFFF, -1}, u32 usrregnum, u16 wldmanhandle, u16 reason}` unless silent, then `so_banning` (Z01 §8.3) | confirmed | @ FUN_0054f340: length 0x10; `usrregnum` from vt 0x348, handle from vt 0x340; layout = `PROTO_NC_USER_CONNECTCUT2WORLDMANAGER_CMD` after the header |
| L8 | `so_LinkTo` to another zone: 0x180B, `ws_save2DB`, `ws_save2worldmanager`, mode 0, 0x180D, `JustLink` (Z01 §7.1) | confirmed *(captured)* | Not re-read: the burst order is captured (`capture-validation.md` §7.5.4) and the 0x180D layout is the PDB's (W3): `{header, wldmanhandle, newmechineid, linkto, linkother}` = Z01's field list |
| L9 | the hand-over sequence of Z01 §5 / W01 §7.3 "end-to-end" | confirmed *(captured)* | 0x1801 → 0x104B → 0x104C → 0x101C → blobs + 0x101D → 0x1802 in all 7 map logins (`docs/knowledge/P02.md`, "Map-login hand-over") |

#### 3.3.4 What this part adds for later parts

- **Original-server bugs found** (for the table of the sweep part): X02-B1 WM 0x180B null read (W5), X02-B2 zone
  0x101D null read after its own log (L3), X02-B3 WM 0x180D without a session: no answer, player stranded (W4).
  All three are latent or need a race.
- **Error classes seen:** N 2 (L6: two functions named from their shape, by Z01 and again by Z06), F 3 (W7 the
  0x180C flag, W9 the stone widths, W10 `bIsGM`), R 2 (I3: 0x68c "after merge / split" is five handlers; I5: the
  lock test also stops links), U 2 (W5, L3 null reads). No layout or offset was wrong; the 2016 PDB struct named
  every `?` field W01 had left.
- **Counting beats sampling again:** I1 and I2 took one script over 102 handlers and settle the commit model for
  every opcode; the same script printed the handlers with missing tests (I6). Part 6 should start from such a count
  for each client-facing family.
- **Scenario inputs** (part 8): two money pick-ups in one tick, and a script reward during a pick-up (I4); a move
  that fails the lot inspector (I3; needs a DB edit that changes a lot between request and answer, part 9); logout
  at a TaiSai table in state 2 (L6: expect the 0x0C31 / socket close ~50 ticks late); kill the client's zone
  socket only and log in again (L5, W8: expect 0x1002 `{0x145}` if `playingCharNo` was not cleared); enter a
  party-release map while in a party (W7); stop the WM session during a link (W4, hard to stage).
- **Ratings changed by this part:** none by hand. Z01 §5 / §7.1 and W01 §7.2–§7.3 keep their generated rating
  (capture credit already counted); Z01 §8.1 stays medium with L6 as the correction; `Z05.md` §1 stays medium
  with I3–I5 as refinements.

### 3.4 Part 6: low ratings in client-facing zone packets

State: done. Z01–Z04 and the handle-trusting handlers of §3.2.6 in part 6 (§3.4.1–§3.4.6), Z05–Z13 (60 low rows)
in part 6b (§3.4.7–§3.4.13).

§2 rates 110 zone pseudocode sections low (Z01 11, Z02 9, Z03 17, Z04 13, Z05 10, Z06 6, Z07 16, Z08 8, Z09 10,
Z10 3, Z11 2, Z12 3, Z13 1). For each one the reason was split into its parts with one script: the README §5 rows
that name the section (`sup`: a later item already corrected a statement in it) and the lines that carry
*(inferred)*, *(pdb2017)* or a class B / R keyword. A section that is low **only** because of `sup` rows gets the
verdict superseded with the place of the correction; where the superseding statement could be attacked in one
read, it was (marked "re-read"). The remaining weak lines were re-read in `zone-pdb` and on the client side
(`re-data/client-handlers.json`, client `clean.py`, `TextData*.shn`). Sections with no client-facing packet
(process structure, loaders, the stat matrix, formulas) are listed in one row per document and not re-read here:
their `sup` rows already say what is wrong.

Result, part 6: 38 rows: 10 confirmed, 8 refined, 2 corrected, 15 superseded, 3 not re-checked. Part 6b: 27 rows:
10 confirmed, 3 refined, 1 corrected, 8 superseded, 5 not re-checked (§3.4.7).

#### 3.4.1 Handlers that trust the handle alone (the list of §3.2.6)

| # | Handler | Verdict | Evidence / correct statement |
|---|---|---|---|
| T1 | `gds_NC_HOLY_PROMISE_DB_GET_CEN_REWARD_ACK` @ FUN_00483d10 | confirmed, harmless | Forwards to vt 0x9d0 `so_ply_HolyPromiseGetCenReward` @ FUN_00483dd0, which only relays client 0x943D `{u16 nError, u64 nMoney}` (length 0xc). No state changes: a stale answer shows the next holder of the handle another character's amount. The sibling `…WITHDRAW…` @ FUN_00484040 is the one that pays (Z08-B14) |
| T2 | `gds_NC_MISC_PINGTEST_CLIENT_ZONE_DB` @ FUN_00550fc0 | refined (Z01 §9, Z01-B6) | The handle is not the header's: it is `hZoneClient` at payload +0xc of `PROTO_NC_MISC_PINGTEST_CLIENT_ZONE_DB` (0x5a bytes; the stamps are `ZoneRecvFromDB` +0x12 and `ZoneSendToClient` +0x16). The lot + 1 **and the 0x0812 answer to the client** are both inside the "cell 0 holds item 0x9C9" test. See Q5 for the request side |
| T3 | `gds_NC_MISC_PINGTEST_TOOL_WM_CLIENT_ZONE_DB` @ FUN_00551130 | confirmed | Copies the struct, stamps +0x3a / +0x3e, relays 0x0813 (0x84 with the opcode) to the object at +0x34. No state |
| T4 | `gds_NC_CHARSAVE_DB_UI_STATE_SAVE_ACK` @ FUN_00551360 | confirmed, harmless | Relays 0x4026 `{u16}` (the word after the header) to the holder. The 2016 client has no handler for 0x4026 (Z01-B5; no entry in `client-handlers.json`) |
| T5 | `gds_NC_CHAR_REGNUM_VARIFICATION_ACK` @ FUN_00551a80 (Z07 §10.2, rated high) | refined, X02-B4 | The struct is `{u16 zonehandle, u32 charregnum, u8 iscorrect}`: no header. vt 0x9f0 `so_ply_RegistNumberVarifyCheck` @ FUN_00551bb0 **does** compare `charregnum` with `sp_CharData.toclient.basedata.chrregnum`, but a mismatch is treated like `iscorrect == 0`: log to `InvalidRegistLog`, set the mode byte (`*(p+0xe9c)`) to 0, return 0 → `so_Disconnect(0x689)`. So an answer that arrives after the handle was reused disconnects the new holder (original bug), latent: it needs a logout and a new login on the same handle within one DB round trip. Z07's one line is right for the normal case |
| T6 | `gds_NC_MINIHOUSE_DB_PORTAL_LIST_ACK` @ FUN_0056ed60 | confirmed | vt 0xfc `so_ply_MH_SetMHPortalList` @ FUN_0056f660: the holder must be in a mini-house (vt 0x130), the house object (vt 0x138) must exist and its owner number (vt 0x80) must equal the holder's (vt 0x344); then `Error == 0x1A08` and `nPortalCnt < 0x33` → house vt 0x104, client 0x8C4B `{u16 n, n × {u16, u32}}`, house vt 0xd8. The owner test stands in for the character test; Z07 §6 text holds |
| T7 | `gds_NC_MINIHOUSE_DB_PORTAL_ADD_ACK` @ FUN_0056eef0 | refined | vt 0x100 `so_ply_MH_AddMHPortal` @ FUN_0056fa10 applies (`Error == 0x1A10`: lock list vt 0x1c) or frees (else: vt 0x28) `lockindex` on the **holder's** lock list before any identity test; only then come the in-house and owner tests of T6, house vt 0x108 (`so_mh_AddPortal`, Z13) and client 0x8C4C. Same pattern as the ITEMDB handlers of I6: a stale answer touches a lock of the wrong player. Z07's "not traced further" is traced in Z13 |
| T8 | `…PORTAL_DEL_ACK` @ FUN_0056f080, `…VISITER_COUNT_ACK` @ FUN_0056f1f0 | confirmed | Both only log when the object is gone and do nothing when it exists (Z07: "no effect", "dead") |
| T9 | `wms_NC_CHAR_TUTORIAL_INFO_ZONE_CMD` @ FUN_0044d3d0 | refined, X02-B5 | `PROTO_NC_CHAR_TUTORIAL_INFO_ZONE_CMD` = `{u16 nSessionHandle, u32 nCharNo, PROTO_TUTORIAL_INFO}`; the handler never reads `nCharNo` and calls vt 0xdf8 `so_ply_SetTutorialInfo` @ FUN_00561500, which writes `sp_TutorialInfo.nTutorialState / nTutorialStep` of whoever holds the handle (original bug), latent |
| T10 | `wms_NC_GUILD_TOURNAMENT_ZONE_OBSERVER_ENTER_ACK` @ FUN_00478be0 | refined, X02-B6 | `{u16 err, u8 nTournamentSeed, u16 nPlayerHnd}`: the packet carries no character number, so the zone cannot test one. After an RTTI test for `ShinePlayer`, `err == 0x1B60` runs `sp_Guild_Tournamnet_Observer_Enter(seed)` (a map change) on the holder; 0x1B61 → client error 0x1B61, 0x1B62 → 0x1B54, others ignored (Z08 and Z16 text confirmed). A reused handle moves the wrong player (original bug, in the packet design), latent |
| T11 | `wms_NC_INSTANCE_DUNGEON_LEVEL_SELECT_CHECK_ACK` @ FUN_00485540, `…_JOIN_ACK` @ FUN_00485b90 | confirmed; §3.2.6 corrected | False positives of the text count: both look the player up by **character number** (`som_FindPlayer(first dword)`, then vt 0xbbc), then test the NPC (`nm_FindNPCFunc`, object type 4, distance² ≤ 1 000 000). The handle they pass to `som_GetObject` is the NPC's. No handle trust here |

Of the 14 handlers, one pays money (known, Z08-B14), four change state of the wrong player in a handle-reuse race
(T5, T7, T9, T10), the rest relay or do nothing. All are latent: a handle is reused only after a logout, and the
answer must cross it.

#### 3.4.2 Z01 (11 low rows)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| Q1 | 0x0804 / 0x0805 from a client are a no-op @ FUN_004c2450 (Z01 §3.3; the same function as "JobManager: no-op" in Z02 §6.1) | confirmed | FUN_004c2450 is an empty function (`return`). Its PDB name `CQuest::Occure_LevelChange` is an identical-code fold (H4); it also fills `ShinePlayer` slots 0xa44 and 0xcec. Registered for 0x0804 and 0x0805 of the player parser (`handlers.json`). Which of them the session lets through before 0x1803: Z18 §1.3 |
| Q2 | the seed is the answer to 0x0806 (Z01 §5.1) | superseded | Z18 §1.3 (sent at accept; the 0x0806 handler is unreachable in practice, Z18-B2). Not re-read |
| Q3 | 0x1814 `NC_MAP_WING_SAVE_REQ`: codes 0x1146 / 0x1143 / 0x1141 / 0x1144, no reply without a wing (Z01 §7.2, Z01-B3) | refined | `sp_NC_MAP_WING_SAVE_REQ` @ FUN_00589c80: allowed modes mask 0x46 (1, 2, 6); wing = `sp_FindItemFromInventory(idb_specialid.sii_SparrowWing)` with attribute class 13. One gate is missing in Z01: before the slot is written, vt 0xa78 `so_ply_IsLink_In_MapAndSendErrorMsg` must return true; when it does not, the handler itself sends nothing (that function sends its own message, by its name; not read). Z01-B3 holds, and also covers a wing whose attribute class is not 13. Client FUN_004aeed0 has texts for 0x1141, 0x1143, 0x1144, 0x1146 only |
| Q4 | 0x1816 `NC_MAP_WING_FLY_REQ` queues a teleport; "the teleport itself runs when the cast ends *(inferred)*" (Z01 §7.2) | refined (inferred → read), X02-B7 | `sp_NC_MAP_WING_FLY_REQ` @ FUN_00589f00 as documented (`sp_CanRecallInThisMap`, `sii_WingStone`, `ui_SparrowWingStone.uib_AfterCast`, ring `queue_sparrowfly`, index in `sp_SparrowFly`). The other end, cited by no document: `UseEffect::UseItemWingStone::uib_Effect` @ FUN_0059a270 calls vt 0x918 `so_ply_SparrowWingFly` @ FUN_0058a1a0: index < 0x80, the entry's handle must equal the player's, the map id must be valid → client 0x301A `NC_ITEM_USECOMPLETE_CMD` (no body), `so_ply_ItemUsePacket(0x700, 9)`, vt 0x600 link to `{map name, x, y}` with arguments (6, 9, 10). Every failure only logs to `ChargedItemLog` ("Fly Null", "Fly Null map"): the stone is gone and the client gets nothing. The ring entry can be overwritten by later requests of other players before the cast ends (original bug), latent |
| Q5 | 0x0812 ping test (Z01 §9, Z01-B6) | refined | `sp_NC_MISC_PINGTEST_CLIENT_ZONE_DB` @ FUN_005509a0: **everything** after the two stamps (`hZoneClient` +0xc, `ZoneRecvFromClient` +0x1a) is inside the "cell 0 holds 0x9C9" test, the send to the GameDB too. Without that item a client's 0x0812 gets no answer at all. The appended part is the struct's `header` (+0x2e) and `buylot` (`PROTO_NC_ITEMDB_BUYLOT_REQ`, +0x34) with the item serialised at lot + 1. Character `fc_NC_MISC_PINGTEST_CLIENT_ZONE_DB` @ FUN_004167e0 stamps two times and echoes the first 0x5a bytes: it never reads `buylot`, so **no DB row changes**. B6's effect is therefore: the zone's lot runs ahead of the DB by one per round trip (T2), until a later ITEMDB message writes that stack's lot. The 2016 client has no 0x0812 handler |
| Q6 | 0x082F → 0x0830 `{u8 shoutlevel, u16 shoutdelay}`, names *(pdb2017)*, "source not found" (Z01 §9) | confirmed, mark resolved | `sp_NC_MISC_SERVERPARAMETER_REQ` @ FUN_005517c0 writes `shineparam.scp_param.shoutlevel` and `.shoutdelay` (2016 PDB member names; length 5). They are fields of the common parameter block (`ShineCommonParameter`, loaded by `scp_Load`, README §5.4). Z01-B5 confirmed: `client-handlers.json` has no handler for 0x0830, 0x0C24 or 0x4026 |
| Q7 | 0x0C23 → 0x0C24 `{u32 userNo}` (Z01 §9) | confirmed | `sp_NC_USER_REGISENUMBER_REQ` @ FUN_0056e8b0: vt 0x348, length 6 |
| Q8 | 0x0C32 sets `p+0x2a800`, "meaning not traced" (Z01 §9) | superseded | M14 / L5: `sp_isPossibleNewConnect` |
| Q9 | Z01 §1, §2.1, §2.3, §4, §4.1, §8 (no client packet), 0x0823 "no-op @ LAB_005a47b0" (WM → zone) | not re-checked | Their `sup` rows (README §5.4) and §3.2.3 / §3.3.3 above say what is wrong; nothing client-facing is left in them |

#### 3.4.3 Z02 (9 low rows)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| Q10 | `p.vt[0xa38](4, id, 0)` is a "script / quest hook" *(inferred)* (Z02 §4) | superseded, re-read | Slot 0xa38 = `ShinePlayer::notifyObservers` @ FUN_00577c10 (`rtti.py`), as Z09 §14.8 says |
| Q11 | "so_Routine makes the pet dance (FUN_004d2470(p, 1))" (Z02 §4); "FUN_004d2470(p, 5)  # pet reaction *(inferred)*" (Z02 §8) | **corrected** | FUN_004d2470 = `sp_PetSystem_ChangeTendency(PupFactorConditionTypeEnum)`: only with a pet out (`sp_PetInfo.nSummonState` = `PSST_1ST_SUMMONED` or `PSST_RESUMMONED`) it reads the pet's mind type (`CPetData::GetPetMindType(nMindMil / 1000)`) and the `TendencyModifyData` for the condition, and adds the amount to `sp_PetInfo.nStressDiffMil` (`PF_STRESS`) or `nMindDiffMil` (`PF_MIND`). It sends nothing and moves nothing: the argument says what the **master** did (1 = `PFC_S_DANCE`, 5 = `PFC_S_GATHER`, 6 `PFC_S_PROD`, 7 `PFC_S_MOVER`, 8 / 9 revival, 10 `PFC_S_RESTHOUSE`, 11 `PFC_S_STORE`). Any pet animation the client shows comes from elsewhere |
| Q12 | the zone never sends 0x1C0E (Z02 §5) | superseded *(captured)* | Z09 §9.6, P02 |
| Q13 | NPC role `JobManager`: no-op FUN_004c2450 (Z02 §6.1) | confirmed | Q1: the empty function |
| Q14 | ID / mode-ID / random-multi gates not traced (Z02 §6.5) | superseded | Z08 §5.2. T11 re-read the two WM answers of the mode-ID gate: 0xA40C is sent only inside the NPC range, and `sp_SetModeIDWaitState(0)` follows it |
| Q15 | Z02 §8: 0x2035 "probably legacy" *(inferred)*; 0x2032 timing; `GatherType` *(pdb2017)* | superseded; enum confirmed | Z07 §11 (the path is live), Z09 §11.2 (Z09-B128). `GatherType` in the 2016 `Zone.pdb`: `GT_HERBING` 0, `GT_MINING` 1, `GT_WOODCUTTING` 2, `GT_FISHING` 3: the *(pdb2017)* mark can go |
| Q16 | wedding Main / Sub values *(inferred)*, partner choice not traced (Z02 §10) | superseded | Z07 §5.1, §5.3; Z13 knowledge §2. Not re-read |
| Q17 | area reports 0x6C05…0x6C08 unchecked (Z02 §12, Z02-B12) | superseded | Z09 §15.8 ("too strong"). Not re-read |

Z02 §1 and its bug table have no weak line of their own beyond these.

#### 3.4.4 Z03 (17 low rows)

Every low row of Z03 is low because of `sup` rows; the document has one *(inferred)* line outside them (§4.6, the
order of an FPU sum), which is a formula and not a packet.

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| Q18 | `smo_SkillResultPacket` sends 0x2452 with one missed entry (Z03 §5.4) | superseded, re-read | FUN_0057a630 writes only the department bits (`op & 0x3ff \| 0x2400`) into the shared buffer, sets no length and sends nothing; it then calls vt 0x40 of the object returned by vt 0x49c. The README row (Z25) is right |
| Q19 | mob melee through `so_attack` / `so_Bash`, 0x2406 / 0x2407 / 0x242C–0x2431 (Z03 §3.5, §7.1) | superseded | Dead in 2016: Z09 §7.3, §7.8, X01 §6.2.2. Not re-read |
| Q20 | Z03 §5.6: two random numbers, keep-time bonus, one abstate loop, vt 0xbf4 | superseded | Z25 §2.2, §2.4; Z21 §5.7; Z22 §10.7 (four rows). Not re-read |
| Q21 | Z03 §6.1 actor table and list size, §6.2 `asl_AbstateSet` | superseded | Z18 §3.1–§3.2, Z22 §1, §7; the element layout was re-read in part 4 (C13–C18) |
| Q22 | Z03 §2, §3.3, §4.1–§4.6, §5, §5.1, §8.2 (no client packet of their own) | not re-checked | Formulas and tables; their corrections are Z12 §1, §4, Z09 §8.4–§8.5, Z25 §1.1, Z29 §2.6, Z10 §6 |

#### 3.4.5 Z04 (13 low rows)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| Q23 | client 0x300A: "inventory full" is shown for "`0x34a`/`0x346`, reached through nested branches the decompiler merged *(inferred)*"; "`0x342` silent" (Z04 §3.3) | **corrected**, X02-B8 | Client FUN_004aba00, branch by branch: 0x341 obtained; 0x344 → too far; 0x345 → no right; **0x346 → `TextData` 0xf4f9e3f0 "Inventory is full."**; 0x34b → `DropItemMgr::Remove(handle)` and no text; 0x2001 / 0x2002 / 0x2003 / 0x2005 / 0x2009 dice texts; 0x34c **and 0x2004** → "You don't have an item that allows you to roll the dice."; 0x34d; 0x34e → "The game continues with dice acquisition."; 0x342 → `TextData2` 0x17290d37, whose text is one space (a blank system line, not nothing); **every other code, 0x34a and 0x343 included**, → 0x35b67a82 "Failed to obtain the item.". So the refusal 0x34a of `so_ply_PickupItem` (the kingdom-quest pick-up limit, `KQItemDataBox::kqidb_CanPickUp` @ FUN_0064bc90: the item is in `KQItem.shn`, its `PickupLimit` is not 0 and the lot owned + the lot picked exceeds it; 2016 data: `KQ_InvincibleHammer` and `KQ_Ice01`, limit 1; corrected by review finding 2: it is not a stack limit) reaches the player as the generic failure (original bug: a code the client does not know). Server side re-read with it, `sp_NC_ITEM_PICK_REQ` @ FUN_00530a50: 0x342 (mode not in 1 / 2 / 6, `duplicatemenustate.dmc_Control & 0xc`, or the lock list busy), 0x34b with the handle (object gone), 0x343 (not visible, not an item object, no item data), 0x344 (distance² > 0x3d08), 0x345 (`so_drpitm_CanLooting` false), 0x34c (drop vt 0xaa8), then the raid (vt 0xa84) or party (vt 0x550) looting switch (`LOOTING_TYPE_FREE / ORDER / LOOTER / DICE`: `sp_RaidItemsidtribute`, `sp_partyitemdistribute`, `sp_DicePicking`, whose failure is 0x2003), else `so_ply_PickupItem` (vt 0x798) |
| Q24 | 0x304E: `smo_SkillBlastOption(p) == 2` "a blast is pending" (Z04 §12.7) | superseded, re-read | The comparison in `sp_NC_ITEM_USE_ACTIVESKILL_REQ` @ FUN_00540b90 is against the enum member `SB_SILENCE` (Z18 §3.1) |
| Q25 | `ItemMenu_Open` (Z04 §1.5, §3.1, §3.2); `p+0xaad8*4` (§3.2) | superseded | The function is `itembreakmenu` (README §4.8); the member is `sp_PetInfo` (P1, §3.2.5). The drop and break handlers themselves were not re-read |
| Q26 | Z04 §8.3 (0x302D tail byte), §8.4 (0x3034 codes), §9.4 (bracelet row), §10.1 (gem charge count), §12.2 (endure kits) | superseded | P02-B3 *(captured)*; Z13 §3.3; Z18 §4.9; Z17 knowledge (two rows). Not re-read |
| Q27 | reward inventory "not reachable by SPLIT" (Z04 §1.1); UseEffect "Effect = no-op" (§6.3) | not re-checked | Class R / B keyword hits. FUN_00514570 in the §6.3 line is `UseEffect::UseItemBase::uib_DirectUse` by the PDB, which fits; the SPLIT claim needs the split handler's box test and is left for part 6b's item pass (Z05 §4) |

#### 3.4.6 What this part adds for later parts

- **Original-server bugs found** (for the table of the sweep part): X02-B4 a late 0x10B4 disconnects the next
  holder of the handle (T5); X02-B5 tutorial info written without the `nCharNo` test (T9); X02-B6 tournament
  observer answer keyed by handle only (T10); X02-B7 `queue_sparrowfly` entry overwritten before the cast ends:
  stone used, no teleport, no message (Q4); X02-B8 pick-up code 0x34a has no client text (Q23). B4–B7 are latent.
- **Error classes seen:** N 2 (Q11: a function named from where it is called; Q1's fold), C 2 (Q23: client codes
  listed from the texts, not from the branches; Q5: "the client is answered" never tested without the item),
  R 1 (T11: a text count that took an NPC handle for a player handle). The 15 superseded rows confirm §1's
  picture for Z02–Z04: the later items already found the errors, and the old text was not edited.
- **`sup`-only rows cost little:** 26 of the 50 low rows of Z01–Z04 are low only through README §5 rows. A reader
  who applies README §5 gets a medium document; no rating was changed by hand, because the old text is still there.
- **Scenario inputs** (part 8): wing save and fly (Q3, Q4: expect 0x1815 / 0x1817 codes, then 0x301A and a map
  link at cast end; also a save with no wing: expect silence); a pick-up over the lot limit of an item (Q23:
  expect 0x300A `{0x34a}` and "Failed to obtain the item."); an emote and a gather with a pet out, then the pet's
  mind / stress values (Q11); 0x0812 sent by a test client with and without item 0x9C9 in cell 0 (Q5).
- **For part 6b:** the same script (`weak.py` in the notes) prints the `sup` rows and weak lines for Z05–Z13;
  Z07 (16), Z05 (10), Z09 (10), Z08 (8) are the large ones. Z05 §10 (client handling of 64 answers) and Z06 §2
  (booth, 4 rows with the `g_NoBooth` name) have weak lines of their own.

#### 3.4.7 Z05 (10 low rows; part 6b)

Part 6b result (§3.4.7–§3.4.12): 27 rows over the 60 low rows of Z05–Z13: 10 confirmed, 3 refined, 1 corrected,
8 superseded, 5 not re-checked. 28 of the 60 rows are low only through README §5 rows (no weak line of their own).

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V1 | 0x3491 / 0x3494: the WM message 0x74C0 is sent "first, unconditionally (even when the player is gone)" (Z05 §2.3) | confirmed | `gds_NC_ITEMDB_GUILD_TOKEN_BUYALLSUC_ACK` @ FUN_00525400 writes `0x74C0 {u32 nGuildNo, u32 nPriceGuildToken, u32 0}` (0xe bytes) to `sock2wldman` before `som_GetObject`; then object, vt 0x300, charNo (vt 0x344), lock apply (`L` vt 0x1c, log on failure), `p ← 0x3004 {0x201}`, vt 0xb44(1). Not a bug: the DB has already sold the item. Its profiler string is "gds_NC_ITEMDB_BUYALLSUC_ACK" (copied code) |
| V2 | 0x341A: "no drop object is created for a partial drop (unreachable, Z04-B4)" (Z05 §3.1) | **corrected**, X02-B9 | The handler `gds_NC_ITEMDB_DROPALLLOT_ACK` @ FUN_0052ad70 is as written (object, vt 0x300, no charNo test, `0x3008 {0x301}`, pending 0). But a partial drop does get its object, earlier: `ItemInventory::ii_DropLot` @ FUN_00529c20 (only caller `ShinePlayer::sp_ItemDropOK` FUN_0052b060) makes a new key (`iti_mkregnum` type 4), allocates the drop object and calls `so_ItemDrop` (vt 0x544) with it **before** it sends 0x3419; on 0x301 it lowers the cell's lot, calls vt 0x604, sends `0x3419` and sets pending 1; on another code it frees the object and answers 0x3008 with that code; a full object table → `0x3008 {0x304}` with the `ii_DropAll` assert text. So unlike DROPALL (object made in the success answer) the ground item exists before the DB commit, and Z05's DROPLOTFAIL path (0x3008, disconnect 0x684) does not take it back (original bug, latent while Z04-B4 keeps the branch dead; the reachability from `sp_ItemDropOK` was not re-read) |
| V3 | 0x3469: "vt 0x34c (no-op); Free" (Z05 §9.5) | confirmed | `gds_NC_ITEMDB_CREATEMUSHROOMFAIL_ACK` @ FUN_0043ef10: object, vt 0x300, charNo, vt 0x34c(payload), `L` vt 0x28(lockindex). Player slot 0x34c = FUN_005275b0 `ShinePlayer::so_NC_ITEMDB_ADMINCREATEFAIL_ACK` *(pdb2016)*: only the profiler frame and an unused charNo read. The client gets nothing on a failed mini-house creation |
| V4 | client 0x3013: "`0x2c1` (never sent, Z05-B2), others 'Failed to unequip the item.'" (Z05 §10) | confirmed | Client `On_NC_ITEM_UNEQUIP_ACK` FUN_004abd80: every code ≠ 0x2c1 → `TextData` 0x92ad77c0. Zone: the only 0x3013 sends are four vt 0x308 calls in `sp_NC_ITEM_UNEQUIP_REQ` FUN_0053a990 (0x2c2 three times, 0x2c4 once); no function writes opcode 0x3013 into the send buffer directly |
| V5 | reward inventory "not reachable by SPLIT" (Z04 §1.1; Q27 of §3.4.5) | confirmed | `sp_NC_ITEM_SPLIT_REQ` @ FUN_00539a40 switches on the box (`Inven >> 10`) of the source and of the destination: 0 guild-academy reward storage, 4 guild storage, 6 account storage (when `sp_MiscFlag.AccountStorage_opened` or `AStorageAnywhere_opened`), 9 inventory; 5 and every other box (2 = reward inventory included) → assert "Invalid Item from box" / "Invalid Item to box". Box 4 as destination is refused at once (vt 0x308). Same cell on both sides is refused first |
| V6 | Z05 §1.4 (`g_ItemUsage` class 2), §5.1 (three names of ours), §9.6 (mini-house effect request), the bug table | superseded | README §5.6: `gMinimonDataBox` role `MRT_USEITEM`; `so_ply_ViewSlot_EquipInfoSend`, `so_ply_DecoActList_Cehck`, `so_ply_ItemLotInspecting`; D06-B2. Not re-read |
| V7 | Z05 §7.1 (account storage), §11 (invariants, prose) | not re-checked | §7.1 is low through a capture correction (P02, `capture-validation.md`): the capture wins. §11 has no statement of its own; its content is rows I1–I12 of §3.3.1 |

#### 3.4.8 Z06 (6 low rows; part 6b)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V8 | `g_NoBooth` (Z06 §2.1, §2.3, §2.4); `NPCRangeCheck_Check` (§4.2) | superseded | README §4.8: `ShinePlayer::BoothSell::board` and `CurrentMenu::cm_MenuAction`. Checked on the way: player slot 0x3e0 = `so_ply_SendBoothSize` FUN_00535390 (RTTI table); the client stores the byte of 0x9010 when it is < 0x15 (`client-handlers.json`). The "no-op" slots 0x08 / 0x0c of the base object were not re-read |
| V9 | client 0x680E: "0xA41 'Item has been successfully sold.' (never sent on this opcode)" (Z06 §2.5) | confirmed | Every 0x680E send of the zone (vt 0x308(0x1a, 0xe, code), 21 sites in `sp_NC_BOOTH_ITEMTRADE_REQ`, `StreetBoothBuy::sb_Trade`, `StreetBoothSell::sb_Trade` / `sbs_SellAll` / `sbs_SellMerge` / `sbs_SellSplitCreate`): 0xa42, 0xa44, 0xa45, 0xa47, 0xa48, 0xa49, 0xa4c, 0xa54, 0xa59. The DB code is forwarded only in the else branch of `gds_NC_ITEMDB_BOOTHTRADE_ACK` @ FUN_005914a0 (`err` ≠ 0xa41), to the object its log calls "Buyer". Client `On_NC_BOOTH_ITEMTRADE_ACK` FUN_004a8620: 0xa41 → text 0x82a9e4e5 and a booth refresh request when a booth window is open; 0xa42–0xa55, 0xa59, 0xa5a one text each; any other code text 0x4db07b7f |
| V10 | Z06-B11: the manual-mode check vt 0x260 FUN_00513670 "has no caller and 0xAC20 is not registered" (Z06 §3.4) | confirmed | No call through slot 0x260 anywhere in the decompiled image; `handlers.json` has no entry for 0xAC20 (0xAC24 is the DB answer FUN_005171c0). FUN_00513670 = `ShineMiniHouse::so_mh_DiceTaiSai_CanDiceRoll` *(pdb2016)*: 0x1cd4 no player, 0x1cd5 / 0x1cd6 (player vt 0x174 / vt 0x170(1) false), 0x1cd9 (house vt 0x214 false), 0x1cdb not the owner, 0x1cda mode ≠ `DTGM_MANUAL`, 0x1cd7 status ≠ `DTGS_BETTING`, 0x1cd8 no bets, 0x1cd0 ok. The nine codes exist for a request the 2016 zone cannot receive |

#### 3.4.9 Z07 (16 low rows; part 6b)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V11 | Z07 §1.2 (0x10D3 "key-map / shortcut options", auto-pick *(inferred)*), §1.1 / §2.1 ("legacy" DEC path, `DAT_0da504a9` "inside the level-0 entry"), §1.5 (exp indexing) | superseded | README §5.6 (`resttime`, autopick, mystery_vault, `nChatBan`, `bFirstJoin`; ActionID) and §5.5 (`scp_param.LostExpLevel` / `MaxFreeStat`, `nextexp` u64[151]). The weak lines are exactly the corrected ones. Whether the DEC request path is dead was not re-read |
| V12 | Z07 §11: "the client ignores 0x2036, 0x2038, 0x203A and 0x203B (no handler)"; 0x481D is handled | confirmed (client side) | `re-data/client-handlers.json` has no entry for the four; 0x481D → client FUN_0069edd0. The server path (`smo_ply_ItemProduce` FUN_0046c2d0) was not re-read |
| V13 | wedding status values, names *(inferred)* (Z07 §5.1) | not re-checked | Names of ours for the `Main` / `Sub` values; the `Sub` 5–8 values are in README §5.6. Needs the wedding scenario (propose → hall → divorce) |
| V14 | Z07 §4.1, §5.3, §5.4, §5.5, §6.1, §6.7, §6.9, §6.10, §7, the bug table | superseded | README §5.6, one row each (`mauidb_CanUseItem` kinds reversed; the 2016 client does handle 0x1094; `AnnounceSystem_ProposeAccept`; `isAlreadyEnterPlayer`; the dead 0x8C1D branch; `UseRange` / `ApplyRange`; `cca_IsRewardCondition`; D06-B2). Not re-read. §6.1's `MiniHouseFurnitureObjEffect.shn` column names stay *(pdb2017)* |

#### 3.4.10 Z08 (8 low rows; part 6b)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V15 | quest record "0x20 bytes: `u16 ID, u8 Status, PLAYER_QUEST_DATA Data` *(pdb2017)*"; `QUEST_SCRIPT_COMMAND` *(pdb2017)* (Z08 §3.1) | refined | Both are in the 2016 `Zone.pdb`, so not *(pdb2017)*: `PLAYER_QUEST_INFO` (0x20) `{+0 ID, +2 Status, +3 PLAYER_QUEST_DATA Data}`; `PLAYER_QUEST_DATA` (0x1d) `{+0 i64 StartTime, +8 i64 EndTime, +0x10 u32 RepeatCount, +0x14 u8 ProgressStep, +0x15 u8 End_NPCMobCount[5], +0x1a bit 0 End_Location, bit 1 End_Scenario, +0x1b u16 End_RunningTimeSec}`; `QUEST_SCRIPT_COMMAND` 0 `QSC_ERROR`, 1 `QSC_END` … 33 `QSC_GET_ITEM_LOT`, 34 `QSC_MAX`, 35 `QSC_EOF`. The 0x65-byte struct of the same line was not looked up |
| V16 | `PROTO_KQ_INFO` "0x179 bytes *(pdb2017)*" (Z08 §4) | confirmed | 2016 `Zone.pdb`: `PROTO_KQ_INFO : PROTO_KQ_INFO_CLIENT`, size 0x179; own members from +0x8d (`NextStartMode`, `NextStartDelayMin`, `RepeatMode`, `RepeatCount`, +0x93 `RewardIndex`, `DemandMobKill`, +0x97 `ScheduleTime`, +0x9b `tm_ScheduleTime`, +0xbf `RunCounter`, +0xc0 `MapLink[4]`, +0x128 `ScriptLanguage[32]`, +0x148 `ScriptInitValue[32]`, +0x168 `IsTeamPVP`, +0x169 `TeamRegenXY[2]`) |
| V17 | 0x7C13 prison: the README §5.6 row that replaced Z08 §12 | superseded, re-read | `wms_NC_ZONE_PRISON_GO_REQ` @ FUN_005a4470 agrees with README §5.6: `err` preset 0xDC0; unknown handle (payload +0x11c) or vt 0x300 true → no answer at all; charNo (payload +0x11e) differs → 0xDC1; `so_Prison_Go` (vt 0x8a4, argument = the u16 at payload +0x122) returns 0 → 0xDC2. Answer 0x7C14 to the WM = the request's first 0x174 payload bytes copied, `u16 err` at +0x174 (packet length 0x178) |
| V18 | Z08 §1.2, §5, §7.1, §8.1, §8.2 | superseded | README §5.6 (`MapName`; KQ open points; 0x5C05 two PDB definitions, D04-B9; 0x1440 and the mode codes 0x1A41 / 0x1A59) and §5.3 (no 2016 component pays the tournament refund, D06-B3). Not re-read |

#### 3.4.11 Z09 (10 low rows; part 6b)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V19 | drop gate bonus: "`ChargedEffect.shn` EffectEnum 16 'SNS_DropUp' 1100 *(inferred)*"; PC-room +200 *(inferred)* (Z09 §11.2) | refined | 2016 `ChargedEffect.shn` has 13 EffectEnum 16 rows (recounted in part 9; part 6b wrote eight): seven `Huntervoucher*` with EffectValue **1500** (KeepTime 1 h to 720 h), five with **2000** (`Huntervoucher00_TD`, `01_TD`, `03_1`, `03_7`, `03_30`) and `SNS_DropUp` 1100: the gate bonus is +500 ‰, +1000 ‰ or +100 ‰. That enum 16 is what fills `cec_ItemDropRate` was not re-read (Z09 §2.4's `ciee_Activ`). "PC room" as the meaning of `sp_ConnectFrom` = 1 stays *(inferred)* |
| V20 | 0x6C1D `EFFECT_TIMER_FUNC` *(pdb2017)*; `EFFECT_MSG_TYPE` *(fh-doc)*, "15 slots *(pdb2017)*" (Z09 §19.5) | refined | `EFFECT_TIMER_FUNC {ETF_TIMER 0, ETF_REMOVE 1, ETF_MAX 2}` is in the 2016 `Zone.pdb`: not *(pdb2017)*. `EFFECT_MSG_TYPE` is not in it: the 15 value names stay *(fh-doc)*. Client handler of 0x6C1D: FUN_0049d8f0 |
| V21 | Z09 §2.4, §8.8, §24.1, §28.2, §31.2, §31.3; the group-row line of §11.2 | superseded | README §5.6 (`so_ChargedEffectContainerClear`; Z18 covers the trap blasts; no `iac_DropItemMake` reads `ig_itemid`; the requested heal is reported; `sp_RemoveField`; `iac_DropItemMake` and Z18-B8). Not re-read |
| V22 | Z09 §28.12 (`cIndunRankResult` not called by a 2016 script *(fh-doc)*; a ring branch "unreachable"), §29.1 (bug effects *(inferred)* of Z09-B2, B13, B20, B25) | not re-checked | Server-internal; the four effects are deductions from code that was read (class X). Z09-B20 (a limited drop runs out for the whole server) is the one a test can show: scenario input below |

#### 3.4.12 Z10–Z13 (9 low rows; part 6b)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| V23 | Z10 §1 (`zs_start`), §7.2 (load-order dependencies, five effects *(inferred)*), the bug table (Z10-B21) | superseded (§1) / not re-checked | README §5.4 for §1. §7.2 and Z10-B21 are start-up behaviour with no packet; the effects are what a missing table would cause, testable only by removing a data file (part 9, SHN / config experiments) |
| V24 | `&show`: "no appear broadcast here"; `&dimension`: main layer set, "0 returns to the normal layer" (Z11 §3.1) | confirmed (code) | `AmpersandCommand::ac_Show` @ FUN_0041a4d0: in a mini-house (vt 0x130) only the wall text; else `so_AbnormalState_Reset(0x120)` (vt 0x650) and `l_Sub` = 0; it sends nothing itself. `ac_Dimension` @ FUN_0041a5a0: `so_Logout(gm)`, then `l_Main` = the scanned number, nothing else (no re-login to the map, no range test on the number). What other clients then see stays *(inferred)*: needs a second client |
| V25 | `&killallmob` "EXP, drops and quest credit as for a kill *(inferred)*"; `&suicidemob` / `&mfind` against *(fh-doc)* (Z11 §5.2) | not re-checked | The doc already states where the code differs from the FiestaHeroes text. Scenario input below |
| V26 | Z12 §2.5, §6.4, §7.2 | superseded | README §5.5 (`so_ItemActonAbstateApp` is the writer; "is a party main"; `ws_save2worldmanager` runs only from `so_LinkTo`, re-checked as L-rows of §3.3.3) |
| V27 | `so_MH_SendFunitureInfoStart` FUN_00544de0 (player vt 0xd4): "No caller in the 2016 zone" (Z13 §2.8) | confirmed | No direct call by name; the four calls through a slot 0xd4 are all on a `CGambleDiceTaiSaiObject` (`GDTSO_DiceTaiSai_Enter`, `GDTSO_ExcuteLeaveGame`, `go_PlayerUnmarking`, `sp_NC_GAMBLE_DICE_TAISAI_GAME_LEAVE_REQ`) |

#### 3.4.13 What part 6b adds for later parts

- **Original-server bug found:** X02-B9 a partial drop puts its ground object down before the DB commit and the
  failure answer does not remove it (V2; latent, the branch is dead by Z04-B4).
- **Error classes seen:** P reversed, 3 times (V15, V16, V20: facts marked *(pdb2017)* that the 2016 `Zone.pdb`
  holds: the marker was right when Z08 / Z09 were written, before S01); T 1 (V2: when the object is created);
  F 1 (V19: one table row taken for the whole enum value). No offset, opcode or code value was wrong.
- **28 of 60 rows are `sup`-only**, as in Z01–Z04: the documents from Z05 on carry few weak lines of their own
  (Z07 16 rows: 13 with a `sup` row, 9 of them with nothing else). The re-read claims held more often than in part 6 (10 of 14 confirmed).
- **Scenario inputs** (part 8): a failed mini-house creation (V3: expect no packet at all); unequip with a full
  inventory (V4: 0x3013 `{0x2c2}` or `{0x2c4}`, never 0x2c1); a split from the reward inventory with a test
  client (V5: expect the assert in the zone log); booth buy from a second client (V9: the buyer never gets 0x680E
  `{0xa41}`); TaiSai table in manual mode (V10: bets stay); a Hunter voucher against `SNS_DropUp` on a mob 5
  levels below (V19); `&show` / `&dimension 1` / `&dimension 0` with a second client in sight (V24);
  `&killallmob` with a quest mob (V25); a mob with a limited drop `Num`, killed until it runs out (V22, Z09-B20);
  the wedding sequence (V13); prison send to a handle of another character (V17: 0x7C14 `{0xDC1}`).
- **For part 7:** nothing open from Z05–Z13 except the reachability of `ii_DropLot` from `sp_ItemDropOK`
  FUN_0052b060 (V2), which decides whether X02-B9 is latent.

### 3.5 Part 7: low ratings in client-facing Login / WM packets; remaining class B, R, O hits

Scope: the 44 low rows of the Login and WM documents (L00 5, W01 10, W02 5, W03 11, W04 10, W05 3; L01 has none),
the class B / R keyword hits left in L00, W01, Z01, Z02, Z04 and D02 (`X02-rate.py` `KW['B']`, `KW['R']`: 21 lines,
none in W01), and the two questions earlier parts left open (I12 of §3.3.1, the reachability behind X02-B9 of
§3.4.7). 40 rows: 21 confirmed, 4 refined, 3 corrected, 5 superseded, 6 not re-checked, 1 addition (E30). Names are from the 2016 `Login.pdb` /
`WorldManager.pdb` / `Zone.pdb` *(pdb2016)*; code was read in `login-pdb`, `wm-pdb`, `zone-pdb` and (no PDB)
`character`.

#### 3.5.1 Method: a return-value census instead of single re-reads

Class B's largest group is "a Login / WM handler *ignores* a packet" where the handler returns 0 and the parser
closes the session (README §5.2 rows 4–6, §5.3 row 5; rule: L01 §4.1, W05 §5.1). Instead of re-reading the lines
that say "ignored" or "no-op", every registered handler of both servers was scanned (`handlers.json` → body in
`<bin>-pdb/decomp.c`): the `return 0` statements beyond the one that follows `CheckConnectionValidation`, and the
handlers whose return value is assigned from a call (`return iVar; … iVar = …::Send(…)`).

| Server | Handlers | `return 0` outside the validation test | Result returned from a call |
|---|---|---|---|
| Login | 45 | 0x0C06, 0x0C18 (both known: README §5.2), 0x0803 on a failed validation, WM-link 0x0C0E (E5) | 16 from a send (13 to the peer itself or a DB link) |
| WM | 462 | 14 handlers: 0x0803 ×5 (failed validation), 0x7504 and 0x2010 (validation only, written as `if … return 1; return 0`), 0x7001, 0x7002 (E23), 0x3802 (E12), 0x8001 (validation only), 0xB001 (a failed send to the requester), 0x980D (E18), zone 0x101C (6, W01 §7.2 / §3.3.2) | 229; 66 client handlers return only `Send(requester)`; the others are E30 |

A zone handler returns `void` (E31): this error class does not exist there.

#### 3.5.2 Login (L00: 5 low rows, 4 keyword lines)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| E1 | §3.1 `lastRecvTime`; §3.2 "the packet is ignored" after a failed `<Peer>_CheckAlive`, unregistered opcodes ignored; §4 0x0C06 / 0x0C18 "no-op"; §5.1 0x0801 reply; §5.3 token, 0x0C36 order; §5.4 OPTool queries | superseded | README §5.2, the rows on §3.1, §3.2, §4, §5.1, §5.3 and §5.4 (L01 §4.1–§4.4, S02 §1.6). Re-read on the way: `CParserClient::fc_NC_USER_LOGIN_REQ` @ FUN_00406950 and `fc_NC_USER_NORMALLOGOUT_CMD` @ FUN_004062e0 are a bare `return 0` (client closed); `CheckConnectionValidation` @ FUN_00405f60 returns 0 when the session state ≠ 1 |
| E2 | §4 0x0805 "no-op" @ LAB_004074a0 | confirmed | One shared `return 1` (`CParserWorldManager::fc_NC_MISC_HEARTBEAT_ACK` @ FUN_004074a0, registered for 0x0805 in all five Login parsers): the session stays open |
| E3 | §5.3 0x0823 "no-op" @ FUN_00408660 | confirmed | `CParserWorldManager::fc_NC_MISC_START_THE_BOOM_CMD`: `return CheckConnectionValidation(…) != 0`, nothing else |
| E4 | §5.2 "0x0C2B / 0x0C3C / 0x0C41 / 0x0C4E: same shape for the legacy login variants" | refined (class R) | The four AccountLogDB answers (`fc_NC_USER_IS_IP_BLOCK_ACK` @ FUN_00405c80, `…_GER_…` @ FUN_00405180, `…_TW_…` @ FUN_004054c0, `…_JP_…` @ FUN_004056c0) and the AccountDB answers that lead to them (0x0C3A GER @ FUN_00404990 → 0x0C3B, 0x0C3F TW @ FUN_00403b50 → 0x0C40, 0x0C4C JP @ FUN_00403cd0 → 0x0C4D) are complete handlers, but **no Login function sends the first request of any of these chains**: the image has no 0x0C29, 0x0C2A, 0x0C39, 0x0C3E, 0x0C4B (no literal, no `sends` entry), and the client requests of those regions are refused at once: 0x0C1D `fc_NC_USER_LOGIN_NETMARBLE_REQ` @ FUN_00406280 → 0x0C09 `{0x4A}` + close, 0x0C20 `fc_NC_USER_LOGIN_OUTSPARK_REQ` @ FUN_004063d0 → 0x0C09 `{0x4C}` + close. In 2016 only the US chain (client 0x0C5A → AccountDB 0x0C5B / 0x0C5C → AccountLogDB → 0x0C5E) and the token login 0x0C37 can run; the seven handlers are reachable only if a DB server sends their opcode unasked. The same holds for 0x0C27 `fc_NC_USER_TEENAGER_ACK` @ FUN_00404050: neither Login nor the WM sends 0x0C26 |
| E5 | (addition, from the census) Login ← WM 0x0C0E `fc_NC_USER_WILLLOGIN_ACK` @ FUN_00408870 | confirmed, with one branch added | An invalid client handle is logged and returns 1. With a non-zero success byte and no connect info for the world (`GetWorldManagerConnectInfo` = 0) the client is closed **and the handler returns 0: the WM link is closed** by the parser (L01 §4.1). L00 §5.3 describes the client side of this branch only; not compared with L01's text |

#### 3.5.3 WorldManager (W01 10, W02 5, W03 11, W04 10, W05 3 low rows)

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| E6 | W01 §1, §2 (listeners, CharDB link state, link loss, heartbeat), §4.1 (bad-name check, delete → 0x1408, `shape` bits, rename right +0x77), §5.1, §5.4, §6.1, §6.2, §6.3, §7.1, W01-B5 | superseded | README §5.3 (every W01 row) and §5.9 (W01-B5 withdrawn by X01); nothing weak is left in these sections beside E7 and E8 |
| E7 | W01 §2: 0x0808 `{u16 currentUsers, u16 max}`, "Login derives the world status byte from it *(inferred)*" | confirmed | Login `CParserWorldManager::fc_NC_MISC_USER_COUNT_CMD` @ FUN_00408580 → `CLoginWorldManagerSessionManager::SetWorldManagerConnectInfo` FUN_0040a0c0 (status bands: L01 §3); on the first 0x0808 of a WM link (`m_bFirstConnectForBroadCastWorldStatus`) it also runs `CLoginClientSessionManager::BroadCastWorldStatus` |
| E8 | W01 §4.1: FUN_004382d0 "drop the character from WM-side registries *(inferred)*" | superseded, name added | W04 names it `Clients_OnCharacterDeleted`; official `CWMClientSessionManager::AvatarErase(charNo)`. Head re-read: for every in-game session (+0x704 = 1) that has the character as a friend, 0x540C `{Name5 charid}` is sent and the friend entry deleted; the rest of the body (academy member lists) was not re-read |
| E9 | W02 §1.2, §2.3, §2.4, §4.2: `Party_GetRole` FUN_00464b70 | refined (class N) | `CParty::MemberLeaveCheck(partyNo, charNo)` (`S01-renames.tsv`): not a role but what a leave would do: 4 = slot empty (not a raid party), 3 = not a member, 0 = raid-type party, 2 = fewer than 3 members (the party ends), else 1 for member index 0 (the master) and 0 for the others. In 0x3805 @ FUN_00419bb0: results 0 / 1 / 2 send 0x3807 `{Name5 charid, 0x4C6}` to member 0, result 2 also clears that member's party slot, 3 / 4 send nothing; `CParty::MemberLeave` runs in every case. W02's text follows these values; only the name misleads |
| E10 | W02 §2.3: the pending member "stays until reject, accept, logout or a new 0x3802 hits 0x4CB *(inferred)*" | confirmed for the reject | 0x3805 sets the sender's party slot to 0xFFFF before anything else and calls `MemberLeave`; when member 0's session is gone or holds another character it only removes the sender. The other three exits were not re-read |
| E11 | W02 §7, W02-B6: 0x4D1 "level gap" is never sent | confirmed | The only 0x4D1 of the WM image is in `fc_NC_PARTY_JOIN_REQ` @ FUN_0041a940, after `CParty::MemberIsJoinableLevel` @ FUN_00464ad0: `abs(minLevel − lv) < 1001 && abs(maxLevel − lv) < 1001` over `u8` levels, always true |
| E12 | (addition, census) 0x3802 `fc_NC_PARTY_JOIN_REQ` | confirmed, one branch added | With `m_pCharDataBase` or `m_pCharDataShape` null (a session not yet in the game) the handler returns 0: the client is closed, not answered |
| E13 | W03 §1.2, §8.1: `GT_COND_INFO`, `GUILD_ACADEMY_CLIENT`, `GUILD_EMBLEM_STATE`, `GUILD_SERVER`, `GUILD_TOURNAMENT_LIST` *(pdb2017)* | refined (class P reversed) | All five types are in the 2016 `WorldManager.pdb` (sizes 0x2b, 0x2e0, enum, 0x14, 0x15 = the offsets W03 uses): 2016 facts. The two README §5.3 rows on §1.2 (+0x438 = `CGuildWar`) and §8.1 (`JoinMoney` u32) stand |
| E14 | W03 §2.5: the trailing `err 0x0CDB` of 0x740C is dead code | not re-checked | Tail read only: `if (r == 0) return Send_NC_GUILD_MEMBER_JOIN_ERR(0xCDB); return 1` @ FUN_00419db0; the two helpers that produce `r` were not opened. The handler returns the helper's result on its three error exits (0xCDE, 0xCD8, 0xCDB) |
| E15 | W03 §3.5 "0x0D1A / 0x0D1B are ignored silently" (client) | not re-checked | A statement about result codes in the client's handler, which was not opened in this part |
| E16 | W03 §4.5: CharDB 0x1414 / 0x1416 "(else ignored)" without a client session | confirmed | `fc_NC_AVATAR_GUILD_DATA_ACK` @ FUN_0040c6e0 and `fc_NC_AVATAR_GUILD_MEMBER_DATA_ACK` @ FUN_0040c880 return 1 (link kept). Addition: 0x1414 looks the session up by handle only; the 0x1408 it then sends carries **that session's** `m_UserNo` and the packet's `chrregnum`, so after a handle reuse the delete runs under the new session's account (CharDB's owner test decides; D02's delete was not re-read) |
| E17 | W03 §5, W03-B31: 0x179C "may not ban yourself" is never sent | confirmed | No 0x179C in the WM image. 0x17A4 has one site, `CGuildAcademyMemberServer::Recv_NC_GUILD_ACADEMY_MEMBER_LEAVE_REQ` @ FUN_0044b990; "`LeastJoinTime` *(inferred)*" was not re-read |
| E18 | W03 §5 0x980D: "both set or none → 0x980E {0, 0, 0}" | **corrected** | `fc_NC_GUILD_ACADEMY_MEMBER_LIST_REQ` @ FUN_00422120: no character data, or the session's guild number **and** academy guild number both set → `return 0`: the client is **closed**, no 0x980E. 0x980E with zeros is sent when both are 0, when the guild is not found, or when the academy guild is not found. (The two session fields are shown under wrong member names in `wm-pdb`, W14 of §3.3.2; W03's reading of them is used here) |
| E19 | W03 §9.2: "no-op CharDB handlers" 0x7465, 0x748F, 0x7498, 0x749A (§8.4) | confirmed | All four are registered to `fc_NC_GUILD_DB_INTRO_ACK` @ FUN_0040bb50, which calls `CGuildManager::Recv_NC_GUILD_DB_INTRO_ACK` @ FUN_0045abc0 = `return 1` |
| E20 | W03 §9.2: 0x74EF "(else ignored)" without the OPTool session | confirmed | `fc_NC_GUILD_DB_DELETE_CANCEL_ACK` @ FUN_0040bac0: session lookup by `hTool`, `Recv_…` only when found, returns 1 |
| E21 | W04 §4.1: 0x281A "no-op stub" LAB_00414e40 | confirmed | The WM's shared `return 1` (PDB name `CParserZone::fc_NC_MISC_HEARTBEAT_ACK`, an identical-code fold), registered for 0x0805 on all eight links and for OPTool 0x281A |
| E22 | W04 §6.4: 0x5801 / 0x5809 `{StartHandle, EndHandle}` "(ignored)" | confirmed | `fc_NC_KQ_LIST_REQ` @ FUN_00413980 and `fc_NC_KQ_SCHEDULE_REQ` @ FUN_00413e00 never read the payload; both answer every time (0x5802 / 0x580A, handles 0xFFFFFFFF when the list is empty) |
| E23 | W04 §8.2: 0x7001 `NC_CHAR_OPTION_GET_ALL_REQ` "no-op (the parser returns)", 0x7002 "no-op (empty function)" | **corrected**, X02-B10 | FUN_00413fd0 and FUN_00413fe0 are `return 0`: a client that sends either opcode is **disconnected** (`CParserClient::Parser`, W05 §4.5 "a handler returns 0"). The 2016 client export holds neither constant, so the real client does not trip it *(text search only; an opcode built from dept and cmd would not show)* |
| E24 | W04 §10: 0x0F46 "There is no chatting log." is never sent by the WM | confirmed | No 0x0F46 in the WM image, and none in the zone image |
| E25 | W04 §8.3 "unreachable: the DB caps n at 95"; §12.3 the dice-game test drops 0x9405's answer | not re-checked | Neither function was opened. §12.3's 0x940A row is superseded (README §5.3 last row, X01-B6) |
| E26 | W04 §15.2: zone 0xBC1D `NC_GAMBLE_WORLD_PREVMAPNAME_CMD` "else ignored" | confirmed | `CParserZone::fc_NC_GAMBLE_WORLD_PREVMAPNAME_CMD` @ FUN_0042c570 stores three u32 only when the session exists, has character data and `chrregnum` equals the packet's; returns 1 either way |
| E27 | W04 §6.1, §6.5 `KQ_CanReturnToMap`; §9 0x7C07 scene; W05 §1.4, §3.2, §5.2 | superseded | README §5.3 (`CKQServer::IsExisted`; captured 0x7C07; `m_Packet` slots; class mask bit n = class n; CSL row strings inline) |
| E30 | (addition, census) a handler that returns the result of a send **to a third party** | X02-B11 | `CSocket_IOCP::Send` returns 0 when the target socket is already closed or `WriteFile` fails at once (S02 §1.5). Read: Login-link 0x0C36 `fc_NC_USER_CREATE_OTP_ACK` @ FUN_00424a70 returns `Send(client, 0x0C34)`; CharDB 0x1113 `fc_NC_CHAR_TUTORIAL_MAKE_ITEM_ACK` @ FUN_0040e2c0 returns `Send(client, 0x1002)` on both failure exits; client 0x5401 `fc_NC_FRIEND_SET_REQ` @ FUN_0041ca90 and 0x9401 `fc_NC_HOLY_PROMISE_SET_UP_REQ` @ FUN_00421990 end in one shared `return Send(target or requester, …)`. A 0 closes the **link the packet came in on** (Login link, CharDB link → `CLOSE_CHAR_DB`, W05 §1.5) or the **requesting** client. Same shape by the text census, bodies not opened: client 0x9405, 0x7C01, 0x0813 / 0x0815 / 0x0816, 0x2014; CharDB 0x9888. The window (a session still found by `GetSession` whose socket is already closed) is *(inferred)* |

#### 3.5.4 Remaining class B / R lines in Z01, Z02, Z04, D02, and the two open questions

| # | Claim (where) | Verdict | Evidence / correct statement |
|---|---|---|---|
| E31 | Z01 §3.3: 0x0805 "no-op" @ FUN_00509900 / FUN_00549070, 0x0803 @ LAB_004c8180; §8.4 0x401B / 0x401D; §9 0x0823 | confirmed | Both functions are empty `void` bodies (their PDB names, `CGambleObject::go_SMC_WinRank` and `ShineObject::so_ply_CollectCardOpen`, are folds). Zone handlers have no return value, so "no-op" cannot hide a close as it does in Login / WM. The LAB_ entries were not opened |
| E32 | Z01 §7.2, Z01-B3: 0x1142 "is never sent by this handler" | superseded | §3.4.2 (part 6: the wing-fly path). The one 0x1142 of the zone image is in `sp_NC_MAP_WING_FLY_REQ` @ FUN_00589f00 |
| E33 | Z01-B5: the client has no handler for 0x0830, 0x0C24, 0x4026 | confirmed | None of the three is among the 901 opcodes of `re-data/client-handlers.json` |
| E34 | Z02 §6.1: NPC role `JobManager` = "no-op (FUN_004c2450)"; §8 / Z02-B5 produce handlers "probably legacy" | confirmed / superseded | FUN_004c2450 is the shared empty function (§3.4.2). Z02-B5 was narrowed by README §5.4 / §5.9 (0x2035 is live); none of 0x2036 / 0x2038 / 0x203A / 0x203B is in `client-handlers.json` |
| E35 | Z04 §6.3: `UseEffect` base defaults "CanUse FUN_00596480 (0x700), DirectUse FUN_00514570 (false), Effect = no-op" (Q27 of §3.4.5) | confirmed | RTTI table of `UseEffect::UseItemBase`: slot +4 `uib_CanUseItem` FUN_00596480, +8 `uib_DirectUse` FUN_00514570, +0xc FUN_00402370 (an empty fold), +0x10 FUN_004c2450 (empty). Subclasses such as `UseItemAmountHP`, `UseItemCapsule`, `UseItemChest` keep the empty +0x10 and act in `uib_DirectUse`; `UseItemByAbstate`, `UseItemByTable`, `UseItemChargedBuff` override `uib_Effect` (the first eleven tables of the RTTI list were compared, not all) |
| E36 | Z04 §1.1 reward inventory "not reachable by SPLIT"; §13.2 `p+0x173bc = no-op` | superseded / not re-checked | §1.1: V5 of §3.4.7. §13.2 was not opened |
| E37 | X02-B9 (§3.4.7 V2): is `ii_DropLot` reachable? Z04-B4 says never | **refined** | Call chain: `sp_NC_ITEM_DROP_REQ` @ FUN_00529f50 lets a request pass to `ItemDropper::id_Drop` only when `cell.lot ≤ req.lot`; the confirmation comes back later through the server menu, `ServerMenuFuncter::smfm_ItemDropWarn` @ FUN_0048da60 → `sp_ItemDropOK` @ FUN_0052b060, which reads the cell's lot **again** and calls `ItemInventory::ii_DropLot` @ FUN_00529c20 when `req.lot < cell.lot`, else `ii_DropAll`. So the partial path is not dead code: it runs when the stack grew between the request and the menu answer. Whether anything can add to a stack while the drop menu is open (pick-up, quest reward, mail) was not established: scenario (part 8). Z04-B4 and X02-B9 are "latent", not "unreachable" |
| E38 | D02 §2: 0x0801 / 0x0805 "return 1 (no-op)" @ FUN_0043c7a0, FUN_004503c0 | not re-checked | Character has no PDB; D01 §1.1 states the parser rule for the DB servers ("the message says disconnect, the code does not") and was not re-read either |
| E39 | D02 §7.1: "0x105D and 0x1063 are legacy: the 2016 zone sends only 0x10D1" | confirmed | Neither constant is in the zone or the WM image; 0x10D1 is written at two sites, `sp_NC_CHAR_STAT_INCPOINT_REQ` @ FUN_0058ad10 and `sp_NC_CHAR_STAT_DECPOINT_REQ` @ FUN_0058b3f0 |
| E40 | D02-B18: the promotion reward table is never loaded | confirmed | `DAT_006ec934` has two references in the Character image, both reads in the 0xA004 handler FUN_0041eff0 (`!= 0 && i < *(p + 0x28)`); no SHN or text file of the 2016 data set carries a promotion table name. A write through the owning object's address would not show in this search: D02's *(inferred)* stays |
| E41 | I12 of §3.3.1; D02 §4 (note at 0x1037): "position and money are saved by the zone's dept-16 messages" | **corrected** (money) | Position: yes (0x4018 / `PROTO_NC_CHARSAVE_ALL_REQ`, I12). Money: **no message saves it as a value.** The Character image has no "set money" call: its `{CALL …}` strings that touch character money are `p_Char_MoneyAdd`, `p_Char_MoneySub`, `p_Char_MoneyMove`, `p_Char_MoneyGet` (and `p_Char_CreateSetDefaultData` at creation, D02 §3.3), all relative (their callers: D03, D04). `tCharacter.nMoney` therefore changes only by the deltas of committed operations; the zone's `Cen` is loaded from `p_Char_GetAllData` column 13 (D02 §4.1) and never written back as a value. A zone-side change with no DB message behind it would be lost at logout *(inferred)* |
| E42 | D01 / D02 low rows (9 + 19) | not re-checked | 25 of the 28 are low through *(db-backup)* statements or the D06 list of procedures that differ between the backups: SQL bodies, not client-facing packets. D06 re-read them; what a body really does on the 2016 server is a DB experiment (part 9), not a static question |

#### 3.5.5 What part 7 adds for later parts

- **Original-server bugs found:** X02-B10 WM 0x7001 / 0x7002 are registered to `return 0` (a client sending either
  is disconnected; latent with the 2016 client). X02-B11 handler result = result of a send to a third party (E30):
  the wrong party pays for a dead socket, up to the CharDB link.
- **Error classes seen:** B 3 (E18, E23, and E5 / E12 as missed branches), R 2 (E4 unreachable chains presented as
  variants; E37 "unreachable" that is latent), N 1 (E9), P reversed 1 (E13), F 1 (E41: a save message assumed to
  carry a field it does not have). No opcode identity (class O) error was found in the six documents.
- **23 of the 44 low Login / WM rows carry a README §5 row** (L00 5 of 5, W01 10 of 10, W05 3 of 3, W03 3 of 11,
  W04 2 of 10, W02 0 of 5): in L00 and W01 almost everything weak was already replaced by L01 / W05. The WM documents written before W05 (W02–W04) still hold the "ignored" wording: read it as
  "the handler returns 1" only where a row above says so.
- **Census tool for X01 / a rebuild:** the two tables of §3.5.1 are the complete list of Login / WM handlers
  that close a session by their return value; a rebuild must keep `return 0` = close.
- **Scenario inputs** (part 8): a stack that grows while the drop confirmation is open (E37: expect 0x3419 and a
  ground object); a test client sending 0x7001 (E23: disconnect) and 0x980D from a session with no guild (E18:
  0x980E zeros); 0x3802 before the character is in the game (E12: disconnect); a friend request to a player whose
  client was just killed (E30: the requester may be dropped); money check after a kill of the zone process
  (E41: the DB value is the sum of committed deltas). DB setups (part 9): `tCharacter.nMoney` can be edited with
  the character logged out, no other table mirrors it (E41).

## 4. Coverage gaps of items without a review part

Sixteen status files have no "Review" section: C01, C02, D01, D02, L00, P01, P03, W01, W02, Z01, Z02, Z03, Z04, Z05,
Z07, Z08. They were closed before the plan had the "Coverage boundary" and review steps, and none of their outputs has
a "Coverage boundary" section. This section says what `coverage.py` reports for them (§4.1), what that tool cannot see
(§4.2–§4.4), and which of their own open points nobody took up (§4.5). §4.6 is the work list. No other item's file
was edited; two small gaps are closed in §4.5 itself.

The numbers come from `docs/plan/status/X02-cov.py` (commands `items`, `weak`, `rest`, `game <bin>`, `who <ID>`); it
imports `coverage.py` and keeps its rules. Run it again after documents change.

### 4.1 What `coverage.py <ID>` reports

"Gap" = a function reachable from the item's scope handlers that no document of that server cites.

| Item | Handlers cited by the item | Reachable, depth 3 | Gaps | Reachable, depth 6 | Gaps | Reachable, no limit | Gaps |
|---|---|---|---|---|---|---|---|
| C01 | no scope table | – | – | – | – | – | – |
| C02 | no scope table | – | – | – | – | – | – |
| D01 | 52/52 | 120 | 0 | 132 | 10 | 132 | 10 |
| D02 | 75/75 | 279 | 0 | 307 | 27 | 309 | 29 |
| L00 | no scope table | – | – | – | – | – | – |
| P01 | no scope table | – | – | – | – | – | – |
| P03 | no scope table | – | – | – | – | – | – |
| W01 | 102/197 | 321 | 0 | 338 | 0 | 338 | 0 |
| W02 | 28/28 | 106 | 0 | 106 | 0 | 106 | 0 |
| Z01 | 74/74 | 368 | 0 | 493 | 23 | 611 | 128 |
| Z02 | 38/38 | 131 | 0 | 172 | 0 | 173 | 0 |
| Z03 | 19/19 | 86 | 0 | 115 | 0 | 124 | 0 |
| Z04 | 52/52 | 244 | 0 | 306 | 8 | 436 | 128 |
| Z05 | 102/102 | 98 | 0 | 172 | 1 | 193 | 1 |
| Z07 | 117/117 | 169 | 0 | 223 | 22 | 329 | 127 |
| Z08 | 111/111 | 373 | 0 | 497 | 24 | 617 | 129 |

- **Depth 3 (the tool's setting): no gap in any of the eleven items with a scope table.** The follow-up items
  (W03–W05, Z09–Z30, D03–D07) and X01 closed what the first documents left.
- **W01, 102 of 197 handlers.** The other 95 are not cited by W01's own documents; every one is cited by W05
  (`X02-cov.py who W01`: 44 by W05 alone, 30 by W04 and W05, the rest by W05 with W03, S02, P02, L01 or zone items).
  W01's scope table was split after it was written; nothing is missing.
- **No scope table (C01, C02, L00, P01, P03):** the tool does not apply. L00 is the Login server: the overview
  (`docs/plan/progress.md`) counts 43 of 43 Login handlers and 53 of 53 functions cited, with L01. C01's status file
  has its own measure (629 of 671 server → client opcodes have a client handler; the 42 others are classified in
  `docs/knowledge/C01.md` §5). C02, P01 and P03 are tools; their open points are in README §7.3 and §4.5 below.

### 4.2 Below depth 3

With the depth limit raised (other rules unchanged) the gaps are library code, with three exceptions:

| Item | Uncited below depth 3 | What they are |
|---|---|---|
| D01 | 10 | `cShineLogSystem::SLS_AddLog` (FUN_004179d0 account, FUN_00413530 accountlog; 94 lines each), `CIOBuffer::Alloc` / `Free`, `CIOSpinLock::Wait`, `cLS_Queue::lsq_QueueAllocate`, `operator new`. Shared network and log classes: S02's subject, and S02 §6 says the DB-server copies were not compared (§4.4) |
| D02 | 29 | all under FUN_00460bf0 (holds the `{CALL ` string) and FUN_004412f0 (holds `bad cast`): C++ stream and locale code *(inferred from the two strings; the Character server has no PDB)* |
| Z01, Z04, Z07, Z08 | 127–129 each | the same Lua 5.2 VM functions (`luaV_execute` FUN_006120c0 817 lines, garbage collector, tables, strings) reached through a script call. Library code. Not library: `CLooting::CLooting` FUN_00645370 (13 lines) and `TickTimer::TickTimer` FUN_00591fa0 (12 lines), two constructors |
| Z05 | 1 | `BoothItemInfo::GetAttrSize` FUN_0062dca0 (66 lines): documented in §4.5 (G1) |
| W01, W02, Z02, Z03 | 0 | – |

### 4.3 Cited is not the same as documented

The tool counts an address as covered when any document mentions it. The table splits the depth-3 functions of each
item by the strongest kind of mention: `@ FUN_…` on a pseudocode line or in a heading; a sentence or table cell; only
lines that list five or more addresses; only under a heading named "Not reconstructed", "Open questions" or similar.

| Item | Reachable (depth 3) | Cited with `@` or in a heading | Text only | List lines only | Only under an open-points heading |
|---|---|---|---|---|---|
| D01 | 120 | 44 | 62 | 14 | 0 |
| D02 | 279 | 121 | 106 | 52 | 0 |
| W01 | 321 | 173 | 132 | 16 | 0 |
| W02 | 106 | 72 | 24 | 9 | 1 |
| Z01 | 368 | 251 | 94 | 17 | 6 |
| Z02 | 131 | 76 | 51 | 1 | 3 |
| Z03 | 86 | 55 | 31 | 0 | 0 |
| Z04 | 244 | 124 | 109 | 5 | 6 |
| Z05 | 98 | 52 | 40 | 4 | 2 |
| Z07 | 169 | 101 | 64 | 3 | 1 |
| Z08 | 373 | 246 | 104 | 14 | 9 |

- The **list-only** functions are mostly library copies named in one line (`Name256Byte` constructors and
  assignments, `TiXmlNode::Identify`, `CSocket_IOCP::Send` in D01 §1.2 and S02 §1.9) and, for D02, the 52 SQL wrappers
  of its §15 table (one row per procedure). No handler logic was found among them.
- The **open-points-only** functions (28) are the ones their own document says it did not read. They count as covered
  but are not documented by the document that cites them; `X02-cov.py weak` lists each with its heading. Whether a
  later item documents them is §4.5.
- "Text only" is not a defect by itself: many documents describe a helper in a sentence. It is the reason a 100 % in
  `progress.md` must not be read as "every function has pseudocode".

### 4.4 Functions no document cites

The tool starts at packet handlers and follows direct calls. It does not see virtual calls, tables of member
pointers, timers or start-up code. Counted over whole binaries (functions of 6 lines or more, library code by PDB name
excluded):

| Binary | Functions (≥ 6 lines, not library) | Cited by some doc | Not cited | Lines not cited / all |
|---|---|---|---|---|
| login | 505 | 366 | 139 | 5465 / 19555 |
| wm | 1907 | 1666 | 241 | 7896 / 83475 |
| zone | 8797 | 6619 | 2178 | 63692 / 413175 |
| account | 850 | 254 | 596 | 16458 / 26286 |
| accountlog | 780 | 240 | 540 | 15265 / 23030 |
| character | 3216 | 1045 | 2171 | 72263 / 134283 |
| gamelog | 1408 | 418 | 990 | 31905 / 48038 |

Most uncited lines are CRT, Lua and STL code that the library filter does not match (the largest are `memcmp`,
`$I10_OUTPUT`, `memcpy`, `luaV_execute`, `llex`). Character and GameLog have no PDB, so library and game code cannot
be told apart there by name. The Account and AccountLog remainder is the process layer (`WinService`, `MiniDumper`,
`CSocket_*`, `CSession*`, `DataServer`, `cLogSystem`) and data loaders they share with the other servers
(`ItemAttrCls_*`, `ItemDataBox`, `MapDataBox`, `CShnDataFileCheckSum`): 389 and 382 class-named functions.

For the zone, restricted to functions the 2016 PDB names `Class::Method`:

Zone: 7438 class-named functions, 1158 not cited (25865 of 350966 lines); 789 of them have no direct caller (virtual / table-dispatched).

| Class | Functions not cited | Lines |
|---|---|---|
| `ShineObjectClass::ShinePlayer` | 139 | 2944 |
| `CGambleDiceTaiSaiObject` | 36 | 2408 |
| `ShineObjectClass::ShineObject` | 87 | 895 |
| `InventoryLocking::InventoryCellLockList` | 17 | 887 |
| `ShineObjectClass::ShineMobileObject` | 34 | 615 |
| `CMD5Checksum` | 6 | 408 |
| `Table` | 5 | 340 |
| `SlotMachine::SlotMachineAnalyse` | 4 | 317 |
| `CGambleObject` | 22 | 302 |
| `CellStack` | 6 | 280 |
| `NPCRole_Merchant` | 7 | 269 |
| `ItemAttrCls_Weapon` | 15 | 241 |
| `ItemMixData` | 3 | 232 |
| `AccUpGradeDataBox` | 3 | 222 |
| `CSellItemManager` | 5 | 216 |
| `SlotMachine::SlotMachineScreenManager` | 4 | 209 |
| `ItemAttrCls_Amulet` | 13 | 205 |
| `SlotMachine::SlotMachineScreen` | 5 | 176 |
| `LinearStep` | 4 | 173 |
| `DiceTaiSai` | 1 | 166 |
| `SlotMachine::SlotMachineCluster` | 6 | 160 |
| `BmpDataInfo` | 1 | 158 |
| `SlotMachine::SlotMachineJackPotRanking` | 3 | 150 |
| `CharacterInventory` | 2 | 147 |
| `ItemOptionsData::OptionCardStack` | 3 | 139 |
| (472 more classes) | 727 | 13606 |

The WM has 98 such functions (2 019 lines; `CGuildMember` 15, `CGuild` 13, `CGuildAcademyMember` 12, among them
`CGuild::Recv_NC_GUILD_WAR_TARGET_CMD` FUN_0045bdb0 and four more `Recv_NC_GUILD_*` members with no direct caller),
Login 5 (`type_info`, `String`).

An address that is not cited can still be described under its name, or be an identical-code fold of a cited
function. Of 23 large zone functions checked by name, 8 are mentioned somewhere and 15 are not mentioned at
all. The 15, with the item of this section whose subject they belong to *(attribution by name, ours; bodies not read)*:

| Function | Lines | Belongs to |
|---|---|---|
| `ShinePlayer::so_ply_GuildReNameItemUseSuccess` FUN_00473ea0, `so_ply_GuildReTypeItemUseSuccess` FUN_00474250 | 136, 133 | Z08 (guild content) |
| `ShinePlayer::sp_CanUseItemCheck_ByTable` FUN_0056eae0 | 88 | Z04 (item use) |
| `ShinePlayer::sp_CanItemMakeItem` FUN_0049b6c0 | 45 | Z04 (production) |
| `ShinePlayer::sp_LogoutDuringParty` FUN_004cd340 | 67 | Z01 (logout) / Z08 (party) |
| `ShinePlayer::so_ply_BanByServerDisconnect` FUN_00566930 | 54 | Z01 (kicks) |
| `ShinePlayer::so_SpamSendDataToCharDB` FUN_00562990, `sp_SpamSendDataToWM` FUN_00562bc0 | 68, 56 | Z02 (chat) |
| `ShinePlayer::so_ply_DecreaseDmgPassiveSkill` FUN_005651e0 | 67 | Z03 (damage) |
| `ShinePlayer::so_ply_WeaponSpeedSet` FUN_0043d3c0 (and `so_ply_WeaponRangeSet` FUN_0043f520) | 56, 56 | Z04 (equipment) / Z07 |
| `ShinePlayer::sp_ChatColor_Save2World` FUN_00563c70 | 44 | Z07 (character options) |
| `CGambleDiceTaiSaiObject::GDTSO_DiceTaiSai_Result_DiceRoll` FUN_0061a350, `GDTSO_DiceTaiSai_Out` FUN_0061c330 and 34 more `GDTSO_*` | 2 408 together | Z06 (reviewed item; its §7 lists the TaiSai win tables as open) |
| `SlotMachine::SlotMachineAnalyse::sma_ScreenMatch` FUN_00621dd0 and the other slot-machine classes | about 1 000 together | Z06 (§7: draw, line patterns, jackpot open) |

Also uncited and inside the 16 items' subjects: 17 members of `InventoryLocking::InventoryCellLockList`
(887 lines: `icl_IsLocked` FUN_0048b0f0 / FUN_0048af30, `icl_StoreItem` FUN_00488db0, `icl_ItemInfoZoneRng`
FUN_00489aa0, `icl_UseItem` FUN_004895d0, `icl_ItemSell` FUN_00489ec0, …; Z04 / Z05 describe the lock list from its
callers), `ShineMobileObject::so_smo_AbnormalStateAttribute` FUN_004a8010 (119 lines, Z03; named once in Z09),
`ShinePlayer::~ShinePlayer` FUN_00559300 (126 lines, Z01), four `Table::Load<…>` instances for the level-gap and
belong-dice tables (83 lines each, Z03 / Z09). Full list: `X02-cov.py game zone 200`.

This remainder is larger than a gap one session closes: part 11 (coverage boundary) decides the follow-up item.

### 4.5 Open points of the sixteen items, one by one

Every bullet of each "Not reconstructed / uncertain" section was searched in the later documents by its function
addresses, opcodes and names. README §7.3 gives the same sections in one line each and warns that a point "may
already be answered"; this table answers that per point. **taken up** = a later document has an `@` block for the
function or several mentions of the name (document named; its text was not re-read here, except where a § is given).
**open, owned** = still open and a document says whose it is. **open, unargued** = still open and nothing says who
closes it: the follow-up list. Bullets that only state a finding (a code without client text, "nothing is captured")
are left out.

| Item | Point | State | Where / what remains |
|---|---|---|---|
| L00 | DB conditions behind the AccountDB result flags | taken up | D01, D06 §2–§3 |
| L00 | reader of `builtinKey` | open, unargued | only X01 repeats it. Small: search the readers of the server-object member |
| L00 | OPTool status queries 0x2812 / 0x2814 / 0x2818; service install FUN_00402ba0; log plumbing FUN_00411bb0, FUN_00412bc0 | taken up | L01 (`@` FUN_00402ba0), S02 (FUN_00412bc0) |
| D01 | procedures without source | open, owned | D06 §2–§3 give contracts; README §7.2 "Lost DB sources" |
| D01 | `nUserNo == −2`; private edits of `usp_User_USloginGame` | open, owned | D06 §11 |
| D01 | TEENAGER `nType` 1: the value divided by 60 comes from an untraced FPU expression | open, unargued | read the x87 code of the handler in `account-pdb` (the PDB types the operands) |
| D01 | 0x0804 handler `LAB_00404db0` "not decompiled" (and D02: `LAB_0043cdf0`) | open, unargued | both are labels, not functions, in the exports; a few instructions with `objdump`. Until then "answers 0x0805" is *(inferred)* for Account and Character |
| D01 | syslog writer object `DAT_0064fa90` | open, unargued | where the log lines go is unknown for the Account server |
| D01 | session list, accept, service install, crash dumps, MapInfo / ItemInfo loading | open, owned | S02 §6: the DB-server copies of the shared classes are not compared (§4.4: 389 / 382 uncited class-named functions) |
| D02 | wedding sub-status 6 / +4 against the zone's reading | taken up | Z13 §4 (`@` FUN_0059f2d0) |
| D02 | 0x1004 steps 5–8: which `nStatusDone` filter is doing / done / read / repeat | open, unargued | D06 names `nStatusDone` once; D04 owns the blobs but not the filter order |
| D02 | holy-promise blocks and option packets of 0x1004 | taken up | W04, D04 |
| D02 | 0x1017 item record `Send_NC_CHAR_ITEM_CMD` FUN_004056a0 "is D03's" | open, unargued | no DB document other than D02 cites FUN_004056a0 or names 0x1017; D03 describes item rows for the ITEMDB answers, not this sender. Check D03 before reading |
| D02 | `p_Char_GetAllData` column 37; `usp_CharacterLoading`, promotion procedures; `setStatPoint` codes | open, owned | D06 §6, §11 |
| D02 | 0x0812–0x0815 field names (2017 structs are larger) | open, unargued | Z01 and W05 describe the opcodes from their side; the Character side keeps 2017 names |
| D02 | SOAP item-shop client (`cUKItemShop`, FUN_0043f690), unchecked URL length | open, unargued | cited by no other document; S01 names the class only. Not small (gSOAP, no PDB) |
| D02 | sender of 0x0841 | taken up | W04 (0x0840 → 0x0841) |
| W01 | feature callees, `g_InstanceMaps`, FUN_004382d0, FUN_00437d50, handlers 0x0840 … 0x10F1, OPTool | taken up | W04 (`@` FUN_00452580, §4.3), W05 §4.5 |
| W01 | AVATAR fields *(inferred)*, CHARDATA beyond the WM's offsets | open, owned | D02; the 2016 `WorldManager.pdb` has the struct (S01) |
| W02 | PARTY +0xcc, PARTY_MEMBER +0x20 never read | open, unargued | harmless as stated; the 2016 PDB names both members (one `pdb.py` call) |
| W02 | zone side of the notifications; `nChatBan`; FUN_0042cda0 | taken up | Z08, W04 (`@` FUN_0042cda0) |
| Z01 | start order | open, owned | Z10 §10, README §7.2 |
| Z01 | certification protocol, main thread, tick | taken up | Z10 (`@` FUN_00613440, FUN_00613750, FUN_005ab9c0), Z09 |
| Z01 | player modes other than 0 and 1 | open, unargued | later documents use single modes (mode 3 in X01-B5); no table of all values |
| Z01 | 0x0830 values, `p+0x2a800`, the 49-table list | taken up | Z10; S01 §3.3 and §3.2.3 here (`sp_isPossibleNewConnect`); `capture-scenarios.md` §9 names the 49 tables |
| Z01 | fields of 0x4001 | taken up | Z12, P02 (captured) |
| Z02 | source of `hnd` (third handler argument) | open, unargued | the dispatcher's second argument was never traced; every zone handler description rests on it |
| Z02 | setter of `+0x1e78` bit 5 | taken up | `docs/knowledge/Z03.md` §1 (Captivate) |
| Z02 | which client action sends 0x2003 / 0x2005 | open, owned | client question; the second-client scenario of `capture-scenarios.md` §3 that expects `0x2003` → `0x2004` shows whether the client still sends it |
| Z02 | sight removal, `&` commands, portal roles, wedding hall, AI events | taken up | Z09, Z11, Z14, Z13 |
| Z02 | roar delivery after the item cast (`p+0x2a79c`, ring `DAT_008598c0`) | open, unargued | only Z04 mentions the member (the cast side) |
| Z02 | setter of `p+0x5cb9` bit 2; FUN_005cc2a0 / FUN_005cc2d0 events | open, unargued | Z09 and Z18 mention the byte; no setter recorded |
| Z03 | formulas | open, owned | Z12, Z22 §13, README §7.2 "Floating-point formulas" |
| Z03 | stun chance FUN_00500170 | closed here | G2 below |
| Z03 | `smo_SkillBlast` specials, cooldowns, abstate actors, mob side, experience split, weapon charges | taken up | Z25, Z23, Z22, Z09, Z29 (`@` FUN_00482500, FUN_004826b0), Z17 (`@` FUN_00562160) |
| Z03 | SkillEntry layout beyond §5.1 | taken up | Z20 (by subject; the name "SkillEntry" is not used there) |
| Z03 | StaACMode / StaMRMode actors (FUN_0042aeb0) | taken up | Z25, Z22 (few mentions: check before relying on it) |
| Z03 | 0x244C payload builder (`mob+0x2234 .vt[0x30]`) | open, unargued | Z09 mentions the member; the builder is not read |
| Z04 | DB answers, lock commit, `UseEffect` actors, upgrade stat delta, dismantle, loot rules | taken up | Z05, Z17, Z24, Z26, Z13, Z11 (`@` FUN_005c5c60), Z30 (`@` FUN_005290f0), Z09 (`@` FUN_00644f60) |
| Z04 | merged branches whose code is *(inferred)* (SPLIT, PICK, BELONGED_CANCEL 0x2885–0x288f, MAPLINK, soul stone) | open, unargued | §3.4.5 and §3.4.7 here re-read SPLIT and PICK; 0x2885–0x288f are named by no other document |
| Z04 | inventory types 2 / 3 / 13 / 14 / 16; item attribute layout | taken up | Z13, Z05, D03; sizes per class also in G1 |
| Z04 | `ItemKey_Make` kinds | open, owned | Z24 §9 (`iti_mkregnum` kind 8 still open) |
| Z04 | auto-arrange scheduling (`p+0x2ab18`) and sort key | open, unargued | Z05 mentions the member only |
| Z04 | mover-upgrade rare roll | taken up | Z30, Z13 (few mentions: check) |
| Z05 | which DB check gives each code | open, owned | D03 |
| Z05 | `LC_Machine` as a vending machine | open, unargued | a name guess; no effect on behaviour |
| Z07 | stat layers, blob bodies, wedding, mini-house, minimon, mover, pet, `cca_IsRewardCondition` | taken up | Z12 (`@` FUN_0058bd10), Z13 (`@` FUN_005b92a0), Z28 |
| Z07 | `NC_CHAR_ZONE_SINGLE_OPTION_CMD` field meanings; LINK_FROM record use | open, unargued | Z12 names the packet twice; meanings stay *(inferred)* |
| Z08 | quest engine, KQ, instances, tournament, raid status, academy storage, GM events | taken up | Z15 (`@` FUN_006387f0), Z16 (`@` FUN_00476860), Z14 (`@` FUN_005cd9c0 … FUN_005cdc00), D07, Z09 (`@` FUN_0046d5c0) |
| Z08 | prison release timer, 0xDC1 vs 0xDC2 | open, owned | W04 §19; scenario 33 and setup S7 in `capture-scenarios.md` |
| Z08 | client source of `EncHandle` for 0x581A | open, owned | Z16, README §7.2 |
| C01 | `0x7c07`, `0x9010`, `0x103c`, `0x1047`, `0x1049`, `0x10de` by shape only; which send carries `0x083a`; live ITasks | open, owned | README §7.3 (C01 row) |
| C02 | 2017 names not confirmed in 2016 code; 70 size differences; `struct_alias` layouts | open, owned | S01 (`pdb2016-layouts.json`) settles the opcodes the five PDB servers handle; the rest is README §7.2 "2017-only facts" |
| P01, P03 | no "Not reconstructed" section | – | P02 validated the decoder on the captures (`capture-validation.md`); the dissector is generated from the same tables |

**Closed here** (small gaps, read in `zone-pdb`):

- **G1. `BoothItemInfo::GetAttrSize(ItemClassEnum)` @ FUN_0062dca0** *(pdb2016)*: the attribute size in bytes of an
  item of that class, a constant per class. 2: `ITEMCLASS_WORDLOT`, `QUESTITEM`, `KQSTEP`, `ACTIVESKILL`. 4: `DWRDLOT`,
  `HOUSESKIN`, `AMOUNT`, `COSWEAPON`, `ACTIONITEM`, `COSSHIELD`. 62: `AMULET`. 89: `WEAPON`. 37: `ARMOR`, `SHIELD`,
  `BOOT`, `BRACELET`. 36: `FURNITURE`. 8: `DECORATION`. 1: `SKILLSCROLL`, `RECALLSCROLL`, `UPSOURCE`, `WTLICENCE`,
  `KQ`, `UPRED`, `UPBLUE`, `FEED`, `UPGOLD`, `GBCOIN`, `NOEFFECT`, `ENCHANT`. 101: `BINDITEM`. 65: `ITEMCHEST`.
  19: `RIDING`. 12: `CAPSULE`. 9: `CLOSEDCARD`. 5: `OPENCARD`. 26: `PUP`. Any other class: 0. The values 19 (riding),
  26 (pet), 9 and 5 (cards) are the sizes Z13 and Z28 give for the per-class `iac_GetAttrSize` members.
- **G2. `RulesOfEngagement::roe_CriticalStunRate(EngageArgument*)` @ FUN_00500170** *(pdb2016)*: returns the constant
  200.0 and reads nothing from its argument. Z03 §4.5 compares it with `rand1000()` after a critical hit, so the stun
  (abstate 307) follows 20 % of critical hits *(the comparison is Z03's reading, not re-read)*.

### 4.6 Work list

For a follow-up session of the item named, smallest first:

| # | Item | What | Size |
|---|---|---|---|
| 1 | D01, D02 | read the two 0x0804 labels (`LAB_00404db0` account, `LAB_0043cdf0` character) with `objdump` | **closed, §4.7 G3** |
| 2 | W02 | PDB names of PARTY +0xcc and PARTY_MEMBER +0x20 | **closed, §4.7 G4** |
| 3 | L00 | readers of `builtinKey` | **closed, §4.7 G5** |
| 4 | D01 | TEENAGER `nType` 1 arithmetic | small: item D08 |
| 5 | Z02 | source of the handlers' third argument `hnd`; setter of `p+0x5cb9` bit 2; roar delivery | small each: item Z31 |
| 6 | Z01 | table of all player modes | small: item Z31 |
| 7 | Z04 | BELONGED_CANCEL codes 0x2885–0x288f branch by branch; auto-arrange scheduling | small each: item Z31 |
| 8 | Z03 | 0x244C payload builder | small: item Z31 |
| 9 | D02 | `nStatusDone` filters of 0x1004; 0x1017 item record sender FUN_004056a0; 0x0812–0x0815 field names | medium: item D08 |
| 10 | D02 | SOAP item-shop client (FUN_0043f690 and below) | large: item D08 |
| 11 | zone | the class-named functions no document cites (§4.4: 1 158 functions, 25 865 lines; the 15 named functions first) | large: items Z31 (all but the gamble classes) and Z32 (TaiSai, slot machine) |
| 12 | Account, AccountLog, Character, GameLog | process layer and shared-class copies (§4.4; S02 §6) | large: item D08 |
| 13 | wm | the 98 class-named functions no document cites (§4.4), E14 / E15 / E25 of §3.5.3 | medium: item W06 |

### 4.7 Points closed in the sweep (part 11)

The three "minutes" rows of §4.6 and three rows §3 had left as "not re-checked", read now. G1 and G2 are in §4.5.

| # | Claim (owner) | Verdict | Evidence |
|---|---|---|---|
| G3 | 0x0804 `NC_MISC_HEARTBEAT_REQ` in Account `LAB_00404db0` and Character `LAB_0043cdf0`: "not decompiled; reply 0x0805 as in Login *(inferred)*" (D01 §2, D02 §2) | **confirmed** (inferred → read) | Both are five instructions (`objdump`): `ecx = this->session (+4); push 3; push <const>; call Send; ret 8`. The constants at 0x4480fc (Account) and 0x4df0d8 (Character) are the bytes `02 05 08` = length 2, opcode 0x0805, no body. The callee is `CSession::Send` @ FUN_004055d0 *(pdb2016, Account)* / `Session_SendRaw` @ FUN_0043d620 (Character; name ours). The handler returns the send result, so a failed send returns 0 to the parser, on the link the request came in on |
| G4 | PARTY +0xcc "u8 (not used here)", PARTY_MEMBER +0x20 "u32 (unused)" (W02 §1.1) | **confirmed**, names added | 2016 `WorldManager.pdb`: `CParty::PARTY_SLOT` (0xd0) = `{u8 NumOfMember; PARTY_MEMBER_SLOT Members[5] @4; CLooting m_Looting @0xb8; bool IsBelongItemDiceGameIng @0xcc; bool isRaidTypeParty @0xcd}`; `PARTY_MEMBER_SLOT` (0x24) = `{PROTO_PARTY_MEMBER_AND_ZONEMERCHINE MemberInform; ShineObject* memberobj @0x20}`. The class is shared source with the zone: `memberobj` is the zone's object pointer and `IsBelongItemDiceGameIng` the zone's dice-looting flag; the WM has no use for either. `PROTO_PARTY_MEMBER_AND_ZONEMERCHINE` is a 2016 PDB type: W02's *(pdb2017)* marker on it can go |
| G5 | `builtinKey`: "33-byte constant at 0x428508 `037C4103B543CA6E…`; no reader found" (L00 §1, L00-B5) | **confirmed**, text refined | `LoginServer::ReadGlobalGameData` @ FUN_00401680 copies 33 bytes into `gServer.m_strHashValue` (`char[128]` at +0x5d0; the constructor zeroes it). The constant is `"E5DB037C4103B543CA6E6513075FED1D"`: 32 hex digits (the size of an MD5 value) and the terminator; L00 quotes it from its fifth character (the strings export lists the tail at 0x42850c because the copy loop references it). Readers: none. No typed access in `login-pdb/decomp.c` besides the two writers, no `+ 0x5d0` access besides the copy in `login/decomp.c`, and the absolute address 0x432f20 (`gServer` 0x432950 + 0x5d0) occurs nowhere in the exe. L00-B5 stands; the member's official name says "hash value", not "key": the link to the client's 0x0C04 XTrap key is L00's guess *(inferred)* |
| G6 | D02 §2: "0x0801 `NC_MISC_S2SCONNECTION_RDY`, 0x0805: return 1 (no-op) @ FUN_0043c7a0, FUN_004503c0" (E38 of §3.5.4) | **refined**, X02-B12 | FUN_004503c0 is `return 1` (0x0805; also registered for dept 2 cmd 5 only). FUN_0043c7a0 (0x0801) is not a no-op: it answers the sender with 0x0802 `NC_MISC_S2SCONNECTION_REQ {u8 echo_data; u8 server_to_id = 3; u8 server_from_id = DAT_004e2f68; u8 server_from_world_num = DAT_004e2f6c; u8 server_from_zone_num = 0; u16 key = server_from_id + 3}` (7 bytes; field names *(pdb2017)*, values read). `echo_data` is never written: one stack byte goes out (original bug), the same defect as the zone's Z01-B2. D02's comment line under the row says the handler "is registered with a sender of 0x0802"; the row itself misleads. The Account handler for 0x0801 (FUN_00404820) is a real `return 1` |
| G7 | W04 §8.3: "`n ≥ 0x60` … unreachable: the DB caps n at 95" (E25 of §3.5.3, first half) | **confirmed** | Character `fc_NC_CHAR_OPTION_IMPROVE_DB_INIT_KEYMAP_REQ` @ FUN_00422890: the fetch loop tests `0x5e < n` before it stores a row, logs "too many key map data 1" and stops, so n ≤ 95 in every 0x7058 it sends. The WM test is dead with this Character server |
| G8 | Z04 §13.2: `sp_HPStoneUse` sets "`p+0x173bc` = no-op" (E36 of §3.5.4, second half) | **confirmed**, addition | `ShinePlayer::sp_HPStoneUse` @ FUN_00589180: `sp_HPStoneManager.PointStoneCheck` (the member function pointer at that offset) is set to an empty function; the PDB shows it under the name `ShineObject::so_Gamble_ChangeCoin`, an identical-code fold (§3.2 H-rows: read the body). `StoneTick = now + 0x46`, the queue window `now + 0x32`, as Z04 says. Before the 0x5008 answer the function broadcasts `0x500B {u16 handle}` to the players in sight (`so_AllOfRange`) |

Still not read after the sweep, with an owner: E14, E15 and the second half of E25 (W03 §2.5, W03 §3.5, W04 §12.3) → item W06.

## 5. Original-server bugs

Found by the re-check (§3) and the sweep (§4.7). Each is tagged `(original bug)` in the row named. "Latent" = the
code is wrong but the 2016 client or the normal message order does not reach it. None was observed in a capture; the
scenario that would show it is named where one exists (`docs/plan/capture-scenarios.md`).

| ID | Handler | 2016 behaviour | Effect | Likely intent |
|---|---|---|---|---|
| X02-B1 | WM 0x180B `fc_NC_MAP_LINKSTART_CMD` @ FUN_00429c90 (§3.3.2 W5) | reads `m_pCharDataBase->chrregnum` without the null test its neighbours make | a 0x180B for a session that is back at character select is a null read in the WM (process crash). Latent: needs a zone that still holds the player after the WM freed the character | test the pointer, log and return |
| X02-B2 | zone 0x101D `wms_NC_CHAR_ZONE_CHARDATA_ACK` @ FUN_005a3590 (§3.3.3 L3) | when the tutorial-info getter (vt 0xdfc) returns null it logs "TutorialInfo Is Null" and reads through the pointer on the next line | null read in the zone. Latent: the getter returns a member every login sets | return after the log |
| X02-B3 | WM 0x180D (link request from a zone) for a handle with no session (§3.3.2 W4) | returns 1 without any answer | the zone has saved the character, set mode 0 and `JustLink` and waits for 0x180E: the player stays connected and stranded *(inferred: no timer re-sends 0x180D)* | answer with a failure so the zone can disconnect or restore the player |
| X02-B4 | zone 0x10B4 `gds_NC_CHAR_REGNUM_VARIFICATION_ACK` @ FUN_00551a80 / FUN_00551bb0 (§3.4.1 T5) | a `charregnum` that does not match the holder of `zonehandle` is treated like `iscorrect == 0`: `so_Disconnect(0x689)` | an answer that arrives after the handle was reused disconnects the new holder. Latent: logout and new login on the same handle within one DB round trip | drop the answer when the character number differs |
| X02-B5 | zone 0x1115 `wms_NC_CHAR_TUTORIAL_INFO_ZONE_CMD` @ FUN_0044d3d0 (§3.4.1 T9) | `nCharNo` is never read; vt 0xdf8 writes `sp_TutorialInfo` of whoever holds the handle | tutorial state of the wrong character after a handle reuse. Latent | compare `nCharNo` first |
| X02-B6 | zone 0x74DA `wms_NC_GUILD_TOURNAMENT_ZONE_OBSERVER_ENTER_ACK` @ FUN_00478be0 (§3.4.1 T10) | the packet has no character number; `err == 0x1B60` moves the holder of `nPlayerHnd` into the tournament map | a reused handle moves the wrong player. Latent; a defect of the packet design | carry and test the character number |
| X02-B7 | zone 0x1816 `sp_NC_MAP_WING_FLY_REQ` @ FUN_00589f00, `so_ply_SparrowWingFly` @ FUN_0058a1a0 (§3.4.2 Q4) | the ring `queue_sparrowfly` entry can be overwritten by other players' requests before the cast ends; every failure of the second half only logs to `ChargedItemLog` | wing stone used, no teleport, no message to the client. Latent: needs 0x80 other requests within one cast time | key the pending teleport by player, answer a failure code |
| X02-B8 | zone 0x3009 pick-up → client 0x300A, code 0x34a (§3.4.5 Q23) | the kingdom-quest pick-up limit refusal of `so_ply_PickupItem` @ FUN_0052faf0 (`KQItemDataBox::kqidb_CanPickUp` @ FUN_0064bc90: the item is in `KQItem.shn`, its `PickupLimit` is not 0 and the lot owned + the lot picked exceeds it; 2016 data: `KQ_InvincibleHammer` and `KQ_Ice01`, limit 1) is sent as 0x34a, which client FUN_004aba00 does not know | the player reads the generic "Failed to obtain the item." instead of a reason (scenario 21) | send a code the client has a text for |
| X02-B9 | zone `ItemInventory::ii_DropLot` @ FUN_00529c20 (§3.4.7 V2, §3.5.4 E37) | a partial drop creates its ground object before it sends 0x3419; the failure answer (0x3008, disconnect 0x684) does not remove it | a failed partial drop leaves an item on the ground and the full stack in the DB (duplication). Latent: the request refuses partial stacks, the path runs only when the stack grew while the drop menu was open (scenario 42) | create the object in the success answer, as `ii_DropAll` does |
| X02-B10 | WM 0x7001 `NC_CHAR_OPTION_GET_ALL_REQ` @ FUN_00413fd0, 0x7002 @ FUN_00413fe0 (§3.5.3 E23) | both handlers are `return 0` | a client that sends either is disconnected. Latent: the 2016 client export holds neither opcode constant (scenario 41) | `return 1` (ignore) |
| X02-B11 | WM handlers that return the result of a send to a third party: Login link 0x0C36 @ FUN_00424a70, CharDB 0x1113 @ FUN_0040e2c0, client 0x5401 @ FUN_0041ca90, 0x9401 @ FUN_00421990; same shape by text census, bodies not opened: client 0x9405, 0x7C01, 0x0813 / 0x0815 / 0x0816, 0x2014, CharDB 0x9888 (§3.5.3 E30) | `Send` returns 0 when the target's socket is already closed; the handler passes that 0 to its parser | the link or client the packet came in on is closed for another party's dead socket, up to the CharDB link (`CLOSE_CHAR_DB`). The window is *(inferred)* | return 1 after sending |
| X02-B12 | Character 0x0801 `NC_MISC_S2SCONNECTION_RDY` @ FUN_0043c7a0 (§4.7 G6) | the `echo_data` byte of the 0x0802 it sends is never written | one uninitialised stack byte to the peer (GameLog link); no known reader | zero it |

## 6. Not reconstructed / uncertain

- **§2 ratings are computed, not read.** The generator (`docs/plan/status/X02-rate.py`) rates a section from its
  recorded evidence (capture rows, markers, error-class keywords, PDB member matches). A "medium" row was not re-read;
  a keyword can make a sound section low and miss a wrong one that is written without hedging (only 30 of the 207
  superseded statements were hedged, §1). 56 hand rows correct the cases that were looked at.
- **§3 re-read 193 claims of several thousand.** The choice followed the error classes and the citation
  count; a document nobody cites and that uses no weak marker was not attacked. Rows marked "not re-checked" with a
  reason and no later reading: Q9, Q22 (their statements are replaced by README §5 rows), V7, V13, V22, V23, V25
  (scenario or table experiment named in §3.4.13), E42 (the *(db-backup)* rows of D01 / D02: DB experiments). E14, E15
  and half of E25 are item W06.
- **"Superseded" verdicts were not re-verified.** 32 rows of §3 and the 20 "taken up" rows of §4.5 rest on the later
  item's text (found by § reference, address or name), not on a second reading of the code behind it.
- **Latent bugs are argued, not shown.** B1–B7, B9–B11 need a message order no capture holds; the reuse window of a
  handle (B4–B6) and the closed-socket window of B11 are *(inferred)*. Whether anything can add to a stack while the
  drop menu is open (B9) is not established.
- **No prediction of `capture-scenarios.md` was run.** The opcode orders come from the documents under test, so a
  shared misreading shows only in the capture. 14 predictions were checked against their sections; the others are
  as the sequence index (README §3) gives them. Scenario 33 step 4 assumes the 2016 client has a prison UI; scenario
  43 needs an OPTool-side script (no OPTool binary in the repository).
- **No SQL of `capture-scenarios.md` §8 was executed** (no SQL Server holds the backups). Names are verified against
  procedure source and the binaries' `{CALL}` strings; column types, NOT NULL columns no procedure names, and
  whether the 2016 schema equals the backups' are unknown. S5 and S16 assume the ODBC driver reports a trigger
  rollback as an error result *(inferred)*. `tGambleCoin` and `usp_SafeTrade_setAll` exist only in the 2017 backup.
- **Table experiments:** `ItemShop.shn` as the zone's goods table and "WM capacity = last number of its client
  `SERVER_INFO` row" (X6) are *(inferred)*. `X02-shnset.py` was tested on copies only; the client hashes 49 tables,
  so a changed one of those needs the matching client file (§9.1 there).
- **Coverage numbers** (§4.4) count addresses that appear in a document, not understanding; the attribution of
  uncited zone functions to items is by name, and for Character / GameLog (no PDB) library and game code are not
  separated.
- **Ratings after captures:** nothing in §2 was raised by the scenarios yet. After P02 processes new captures,
  re-run X02 (`X02-rate.py write`, then the §3 rows whose "Raise by" names the scenario).

## 7. Coverage boundary

X02 has no scope table (`coverage.py X02`: "no scope table; coverage does not apply"). The rows are what the review
found and did not close itself.

| Found (function / packet / table / behaviour) | Covered by | Argument |
|---|---|---|
| 1 158 class-named zone functions no document cites (§4.4), without the gamble classes | new item **Z31** (added by X02) | about 22 000 lines, several sessions; they hang off virtual calls and tables, which no existing item's scope table (all built from packet handlers) can contain; Z30 covers only handler-reachable gaps and is done |
| `CGambleDiceTaiSaiObject`, `CGambleObject`, `DiceTaiSai`, `SlotMachine::*` (about 3 900 lines) | new item **Z32** (added by X02) | Z06 is done and its §7 lists exactly these as open (win tables, draw, line patterns, jackpot): not documented there, too large to do here |
| 98 uncited class-named WM functions, five `Recv_NC_GUILD_*` members without a caller; E14, E15, E25 (second half) | new item **W06** (added by X02) | W03 / W04 / W05 are done and do not cite them; about 2 000 lines |
| Process layer and shared-class copies of Account / AccountLog / Character / GameLog; SOAP item-shop client (§4.6 rows 10, 12); D01 / D02 open points (rows 4, 9) | new item **D08** (added by X02) | S02 §6 leaves the comparison open, D01 / D02 / D05 are done; several thousand lines |
| Open points of Z01–Z04 (§4.6 rows 5–8) and D01 (row 4) | **Z31**, step 4; **D08** | each is labelled small, but they are nine questions (more than a session together) about functions Z31 / D08 read anyway (player modes, handler arguments, payload builders; the TEENAGER arithmetic); both plans name them, the owners are done. The three that took minutes were closed here (§4.7 G3–G5) |
| The corrections of `docs/knowledge/X02.md` §0 (68 rows) in the list of superseded statements; the README item table still showing X02 as not started | new item **X03** (added by X02) | X02 may not edit other items' files; the list (README §5) is X01's output and X01 is done with no recurring line in its plan, so the update is its own item |
| Bugs X02-B1 … B12 (and those of Z31, Z32, W06, D08) in the bug register | **X03** | same: the register is X01's output; §5 above has X01's row format |
| Capture validation of scenarios 14–44 | P02 (recurring: "run once per batch of captures") | needs the user's recordings; then X02 is re-run for the ratings (plan, last guidance line) |
| The *(db-backup)* statements of D01 / D02 (E42) | `capture-scenarios.md` §8 (S1–S16), then P02 | what a procedure body does on the 2016 server is a DB experiment, not a static question; D06 (done) lists the 27 procedures that differ between backups in its §8.5 |
| Lua VM, CRT, STL code below depth 3 (§4.2) | nobody | library code: a rebuild links its own |
| Dead regional opcodes 0x0C1D / 0x0C1E / 0x0C20, 0x0820, 0x0823–0x0825, 0x0832, 0x0837–0x083A | L00 §3, Z01 (handlers documented); no scenario | no first sender in the 2016 client or servers (§3.5.2 E4): nothing can trigger them in a capture |
