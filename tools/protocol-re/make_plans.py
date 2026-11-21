"""Generate docs/plan/items/<ID>.md (one self-contained plan per work item) from the definitions below.

usage: python3 -I tools/protocol-re/make_plans.py      (run from repo root after re-data/exports exist)
Scope tables are computed from re-data/exports/<bin>/handlers.json, so they list the exact handlers.
"""
import json, os, re

R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
E = f"{R}/re-data/exports"
cat = {c["op"]: c for c in json.load(open(f"{R}/docs/protocol/opcodes.json"))}

DEPT = {2: "MISC", 3: "USER", 4: "CHAR", 5: "AVATAR", 6: "MAP", 7: "BRIEFINFO", 8: "ACT", 9: "BAT", 10: "OPTOOL",
        12: "ITEM", 13: "ITEMDB", 14: "PARTY", 15: "MENU", 16: "CHARSAVE", 17: "QUEST", 18: "SKILL", 19: "TRADE",
        20: "SOULSTONE", 21: "FRIEND", 22: "KQ", 23: "WT", 24: "CT", 25: "ANNOUNCE", 26: "BOOTH", 27: "SCENARIO",
        28: "CHAR_OPTION?", 29: "GUILD", 31: "ZONE?", 32: "DATA", 35: "MINIHOUSE", 36: "CHARGED", 37: "HOLY",
        38: "GUILD_ACADEMY", 40: "PROMOTION", 41: "INSTANCE", 42: "?", 43: "DICE", 44: "RAID", 45: "USER2",
        47: "GAMBLE", 49: "COLLECT", 51: "MOVER", 52: "EVENT", 53: "PET"}

ALL = None
# Shared first step of the DB items (D01-D05); details and the match table are in docs/plan/db-backups.md.
DB_STEP = ("**Database backups:** read `docs/plan/db-backups.md` first (which backup is which, which version to trust). "
           "Start with `python3 -I tools/protocol-re/bak.py cover <bin>`: it lists every procedure your server calls, the "
           "backups and `Fixes/` scripts that have it, and whether the parameter count matches. For every procedure you "
           "document, print its source (`bak.py Files/Server/2016/_Database/<file>.bak proc <name>`; compare the versions "
           "when several backups have it) and use it for the tables and columns touched, the result-set column order and "
           "the meaning of each return code (the Korean header comments list them). The backups come from private servers "
           "and are not the 2016 build: confirm against the binary (parameter count of the `{CALL …}` string, "
           "`SQLGetData` order and C types, result codes checked) and mark facts only a backup shows *(db-backup)*. Say "
           "which version you used, and flag procedures that exist only as private-server work. Name tables and columns "
           "only as the procedure source spells them.")
# (bin, parser substring, depts or ALL)
ITEMS = [
 dict(id="C01", phase=1, title="Client packet-handler inventory", out="docs/knowledge/C01.md + re-data/client-handlers.json",
      scope=[], deps=[],
      goal="Map every packet the 2016 client accepts: for each client scene/state (login, world/char select, in-game, …) "
           "find its dispatcher, list (opcode → client function), and describe briefly what the client does with each "
           "packet (fields read, UI text shown, state changed). This names most server→client opcodes and is the "
           "cross-reference every other item uses.",
      steps=["Start from the known login-scene dispatcher `FUN_0046f4d0` (switch on dept, cmd). Find sibling dispatchers "
             "with the same shape (callers of the same network-receive path, switches on `>> 10` / `& 0x3ff`, "
             "functions `FUN_004aaa40`, `FUN_00665920`, `FUN_00666ce0`, `FUN_00546270` are candidates for the game scene).",
             "Write `re-data/client-handlers.json`: `{\"0xOPCODE\": {\"scene\": …, \"func\": \"FUN_…\", \"summary\": …, "
             "\"fields\": [[off, type, name, note]], \"texts\": [text ids → strings]}}`.",
             "Use the 16 `On_NC_*` debug strings and client RTTI `ProtoStruct<PROTO_NC_…>` names to name opcodes "
             "(`grep -n 'NC_' re-data/exports/client/strings.tsv`).",
             "Resolve text ids with `tools/protocol-re/shn.py` on `TextData*.shn`, and error codes with `client-error-codes.json`.",
             "Extend `tools/protocol-re/catalog.py` (or add a small script) so names from `client-handlers.json` flow into "
             "`opcodes.json` with source `client`, then run `regen.sh`.",
             "Summarise per scene in `docs/knowledge/C01.md` (dispatcher address, opcode list, notable behaviour)."],
      done="Every client dispatcher found; ≥90 % of opcodes the zone/WM send to clients mapped to a client function; "
           "names fed back into the generated docs."),
 dict(id="C02", phase=1, title="2017 client PDB: official opcode names, packet structs, types, client function names",
      out="docs/knowledge/C02.md + docs/protocol/pdb-layouts.json + names/client/C02.json", scope=[], deps=["C01 (soft)"],
      goal="`Files/Client/2017/Fiesta.pdb` is the full private PDB of a slightly newer client (`patch_2017_08_p01`; GUID "
           "matches `Files/Client/2017/Fiesta.bin`). It holds the official protocol enums (`PROTOCOL_COMMAND` = dept, "
           "`PROTOCOL_COMMAND_<DEPT>` = cmd → 2600 opcode names), 2718 `PROTO_NC_*` packet structs with field names, "
           "offsets and sizes (538 of them DB/server-internal), shared types (`SHINE_ITEM_ATTRIBUTE` + 38 `ShineItemAttr_*`, "
           "`CHAR_PARAMETER_DATA`, `PROTO_AVATARINFORMATION`, enum `ABSTATEINDEX` (823 abstates), `ChrClassType`, 134 SHN "
           "row structs `<Table>::DataVersion`) and 30909 client function names. Turn it into evidence every item can use, "
           "without letting 2017 facts overwrite verified 2016 facts.",
      steps=["Reader: `python3 -I tools/protocol-re/pdb.py Files/Client/2017/Fiesta.pdb types|publics|json …` (stdlib, ~1 s). "
             "Opcode table = for each `NC_<X>` in enum `PROTOCOL_COMMAND`, the members of `PROTOCOL_COMMAND_<X>`; "
             "opcode = dept<<10 | cmd. 11 depts have no cmd enum (KQ, WT, CT, HOLY_PROMISE, AUCTION, …).",
             "Opcode names: feed them into `catalog.py` as name source `pdb2017`, ranked below `handler`/`client` and above "
             "`inferred(REQ+1)` and log literals. Measured against `opcodes.json` (2016 binaries): 1347 unnamed opcodes get a "
             "name, 933 agree, 110 conflict (51 `handler`, 41 `inferred(REQ+1)`, 18 log literals), 182 2016 opcodes are not in "
             "the 2017 enums, 210 2017 opcodes are not in the 2016 binaries. Conflicts are scattered, not a per-dept shift, so "
             "check each one in the 2016 code: several `handler` names come from one handler registered for two opcodes "
             "(e.g. zone `0x9884`/`0x9885` both named `…_DEPOSIT_RNG`), where the PDB name is the better one. Record the "
             "verdict per conflict in `docs/knowledge/C02.md`.",
             "Layouts: write `docs/protocol/pdb-layouts.json` (opcode → struct name, size, flattened fields "
             "`[offset, type, name]`, nested structs and arrays expanded one level) and make `packets.py`, `pcap_decode.py` and "
             "`make_dissector.py` use it as a source between hand annotations and generated `layouts.json` (label it "
             "`pdb2017`). Compare each struct size with the 2016 handler's length check / send size (`layouts.json`) and "
             "list mismatches (version drift) in the knowledge file. Server-internal packets about a player carry a 6-byte "
             "`ref` prefix that is **not** part of the PROTO struct (`docs/knowledge/Z01.md`): PDB offset = 2016 payload offset − 6.",
             "Hand annotations already made (L00 `annotations.json`, C01, W01, Z01): 96 of 112 with a PDB struct match the flattened PDB "
             "offsets; the rest are the `ref` prefix (W01/Z01 S2S packets), the 2-byte prefix in W01 `0x0c13`, `0x0C5A` "
             "(`sUserName` is 260 bytes, so our `unused` at 256 is the name's tail) and `0x0C66` (1-byte struct). Report per "
             "owning item; do not edit their files.",
             "Types catalogue in `docs/knowledge/C02.md`: which PDB types matter to which item (Z03 `ABSTATEINDEX`, Z04/Z05 "
             "`ShineItemAttr_*` and `SHINE_ITEM_STRUCT`, Z07 `CHAR_PARAMETER_DATA`, W01/D02 `PROTO_AVATARINFORMATION`, SHN "
             "row structs vs `shn.py` column names, enums such as `ITEM_LOOT_TYPE`, `PLAYER_QUEST_STATUS`, `GUILD_HISTORY_MSG_TYPE`). "
             "Point to the `pdb.py types REGEX` command instead of copying large dumps.",
             "Client function names: import `Files/Client/2017/Fiesta.bin` into `re-data/ghidra` as project `client2017` with "
             "the PDB applied (headless, PDB Universal analyzer, PDB next to the exe) and export it to "
             "`re-data/exports/client2017/` like the others. Port names to the 2016 client: first the `On_NC_*` handlers "
             "by opcode (same opcode → same handler in the scene dispatchers of both versions; 838 of C01's 901 handled opcodes "
             "have a 2017 name, 645 of them unnamed today), then callees and classes by call-graph / byte matching. Write "
             "`tools/protocol-re/names/client/C02.json`; mark ported names as `pdb2017` in the knowledge file.",
             "Evidence: a PDB fact applies to 2016 only after a 2016 binary agrees (same opcode in a handler table, same "
             "size check, same field use). Until then mark it *(pdb2017)* (see `AGENTS.md` evidence levels)."],
      done="PDB opcode names in `opcodes.json` with conflicts resolved; `pdb-layouts.json` used by the generated docs, decoder "
           "and dissector; 2016 client handlers named from the PDB; per-item follow-up list in `docs/knowledge/C02.md`."),
 dict(id="S01", phase=1, title="2016 server PDBs (NA2016): official names, types and packet layouts for the exact build",
      out="docs/knowledge/S01.md + docs/protocol/pdb2016-layouts.json + names/<bin>/S01.json", scope=[], deps=["C02"],
      goal="`Files/Server/NA2016/` holds the **same builds** as `Files/Server/2016/` (identical PE timestamps and RSDS "
           "GUID/age) plus the full private PDBs of Login, WorldManager, Zone, Account and AccountLog (no PDB for Character "
           "and GameLog). The PDBs therefore describe the 2016 code exactly: function and global names, class layouts "
           "(`ShineObjectClass::ShinePlayer` 0x2c058 bytes, absent from the 2017 client PDB), enums, and 2016 `PROTO_NC_*` "
           "packet structs (Zone 1286, WM 1218; e.g. `PROTO_NC_MAP_LOGIN_REQ` has `Name8[49] checksum`, 2017 has 50). "
           "Make that the top name/type/layout source and give every finished item a follow-up list.",
      steps=["Already done when the plan was written (2026-11-13): `re-data/exports/<bin>-pdb/` (login, wm, zone, account, "
             "accountlog) = the **unpatched 2016 exes** analysed with the NA2016 PDB loaded (`reanalyze.sh <bin>-pdb <exe> "
             "<pdb>`); every old function address is kept, separators carry qualified names (`CParserClient::fc_NC_…`). "
             "`tools/protocol-re/pdb_names.py` wrote `names/<bin>/S01.json` (official names for addresses no item had "
             "named; item files still win) and `docs/knowledge/S01-renames.tsv` (our name → official name per item). "
             "The old exports stay the input of `extract.py`/`layouts.py` (they pattern-match `FUN_`/`DAT_` names).",
             "Do not analyse the NA2016 exes: their `.reloc` section was replaced by a `custom` section holding private-server "
             "hook patches (WM: jmp hooks at 004135b4, 00414b51, 00417765, 00417a58, 0041c7ae, …; Zone: 00458d66 and 00459158 "
             "clamp a count to 0x20, plus byte edits at 00470265 and 00598580). Decode each patch (target code in the "
             "`custom` section, VA = image base + section RVA) and record what it changes: each is a hint at an original bug. "
             "List them in `docs/knowledge/S01.md` with the owning item, for X01's bug register.",
             "Packet layouts: write `docs/protocol/pdb2016-layouts.json` with `pdb.py <server pdb> layouts` for all five PDBs "
             "(merge; a dept present in several PDBs should agree, list disagreements) and make `regen.sh`, `packets.py`, "
             "`pcap_decode.py` and `make_dissector.py` prefer it over `pdb-layouts.json` (label `pdb2016`, ranked below hand "
             "annotations, above `pdb2017`). Opcode names: add the server enums to `catalog.py` the same way (`pdb2016` above "
             "`handler`/`client`). Report opcode/struct differences 2016 vs 2017 in the knowledge file.",
             "Per-item follow-up table in `docs/knowledge/S01.md` (same format as the C02 table in the master plan): per "
             "finished item, how many of its names get official names (`S01-renames.tsv`), which of its hand layouts / "
             "member offsets differ from the PDB (Z01's ShinePlayer offsets vs `pdb.py … types '^ShineObjectClass::ShinePlayer$'`), "
             "which of its `(ours)` names and `(pdb2017)` facts the 2016 PDB settles. Do not edit other items' files.",
             "Types catalogue: which server types matter to which item (ShinePlayer/ShineMobileObject/ShineNPC members, "
             "item/abstate/skill classes, WM session and guild classes, SHN row structs vs `shn.py` column names). Point to "
             "`pdb.py <pdb> types REGEX` instead of copying dumps.",
             "Third-party docs (local only, gitignored): `re-data/external/fiestaheroes/` = clone of "
             "github.com/FiestaHeroes/Documentation (doc.fiestaheroes.com, documents the NA2016 set): Lua API "
             "(`docs/Lua Scripting/documentation.md`, `static/files/fiesta.lua`, 243 of 245 names occur in the zone strings), "
             "86 SHN table pages, DB tables, GM commands. Map each to the items that should cross-check it (Z09 Lua/AI, Z11 GM "
             "commands, Z07/Z12/Z17 SHN columns, D0x tables). Evidence label *(fh-doc)*: third-party interpretation, below "
             "code.",
             "Data: `Files/Server/NA2016/9Data` differs from `Files/Server/2016/9Data` in ~37 files of content (the other ~1100 "
             "differ only by CRLF). List them; say which set the binaries' loaders accept if the code shows it (column counts, "
             "file names). The NA2016 DB backups add one Character procedure and `Options.bak` (tables only): note, nothing more."],
      done="`pdb2016-layouts.json` and server opcode names used by the generated docs; NA2016 patches decoded; per-item "
           "follow-up table and types catalogue in `docs/knowledge/S01.md`; `regen.sh` run."),
 dict(id="W01", phase=1, title="World manager core: sessions, world login, characters, zone handoff",
      out="docs/pseudocode/wm/W01-core.md", deps=[],
      scope=[("wm", "CParserClient", [2, 3, 4, 5, 45]), ("wm", "CParserLogin", ALL), ("wm", "CParserAccountDB", ALL),
             ("wm", "CParserAccountLogDB", ALL), ("wm", "CParserGameLogDB", ALL), ("wm", "CParserOPTool", ALL),
             ("wm", "CParserCharDB", [2, 3, 4, 5, 40, 45]), ("wm", "CParserZone", [2, 3, 4, 6, 16, 25, 31, 51, 52])],
      goal="Reconstruct the WM process: startup/config, all link types (Login, Zone servers, AccountDB, AccountLogDB, CharDB, "
           "GameLogDB, OPTool), session lifecycle, world login (0x0C0F validate key), avatar list/create/delete/select, "
           "zone assignment and handoff (0x1003, 0x1036 to zone), map changes between zones, logout, kick (0x0C16 → 0x0C17), "
           "return-to-world-select token (0x0C35/0x0C36), character data relay between CharDB and zones.",
      steps=["Use `docs/pseudocode/login-server.md` §5.3 (Login↔WM messages) as the counterpart.",
             "Identify WM global objects (session managers, zone table, user/char registries) and name them in `names/wm/W01.json`.",
             "Character create (0x1401) and the 130-byte AVATAR struct: confirm fields with the client char-select scene."]),
 dict(id="Z01", phase=1, title="Zone core: process, maps, objects, player session, map login/logout",
      out="docs/pseudocode/zone/Z01-core.md", deps=[],
      scope=[("zone", "ShinePlayer", [2, 3, 6, 45]), ("zone", "WorldManagerSession", [2, 3, 6]), ("zone", "ZoneListenSession", ALL),
             ("zone", "OPToolSession", ALL), ("zone", "GameLogSession", ALL), ("zone", "GameDBSession", [2, 16])],
      goal="Reconstruct the zone process skeleton that all other zone items build on: startup, SHN data loading (list every "
           "table and its loader), map/field instances, object handles and the object class hierarchy (RTTI), the "
           "ShinePlayer lifecycle, the send/broadcast primitives (who receives a packet: self, sight range, map, party), "
           "map login (0x1801 → WM → DB → 0x1802), the login-complete burst (0x1803), map links (moving between maps/zones), "
           "logout and character save (CHARSAVE 16 to GameDB), zone↔zone links (ZoneListenSession).",
      steps=["List object classes from RTTI (`python3 tools/protocol-re/rtti.py Files/Server/2016/w00_Zone00/5ZoneServer2.exe`) and document "
             "the hierarchy in `docs/knowledge/Z01.md`. Other zone items depend on it.",
             "Document ShinePlayer member offsets you identify (position at this+0x66, handle at this+4, …) in `docs/knowledge/Z01.md`.",
             "Name the broadcast helpers (e.g. `FUN_00428a40`, `FUN_00434ae0`) in `names/zone/Z01.json`."]),
 dict(id="W02", phase=2, title="World manager: party and raid", out="docs/pseudocode/wm/W02-party-raid.md", deps=["W01"],
      scope=[("wm", "CParserClient", [14, 44]), ("wm", "CParserZone", [14]), ("wm", "CParserOPTool", [14])]),
 dict(id="W03", phase=2, title="World manager: guild and guild academy", out="docs/pseudocode/wm/W03-guild.md", deps=["W01"],
      scope=[("wm", "CParserClient", [29, 38]), ("wm", "CParserCharDB", [29, 38]), ("wm", "CParserZone", [29, 38])],
      steps=["Open from C01 (`docs/knowledge/C01.md` §5): `0x742a`, `0x982e`, `0x985e` are counted as client-bound only "
             "*(inferred)* (guild / academy member broadcast). Settle who actually receives each (client, zone, CharDB) and "
             "record it in `docs/knowledge/W03.md`.",
             "C01 found no client handler for `0x980a`, `0x982a`, `0x982b`, `0x982d` although the WM sends them to a client: "
             "document them as ignored by the 2016 client, not as missing.",
             "Client guild packets are handled in `GuildTask_OnPacket` FUN_006b7e70, a byte-table switch Ghidra did not "
             "decompile; use the case list in `re-data/client-handlers.json` (C01 §2), not the decompiled switch."]),
 dict(id="W04", phase=2, title="World manager: friends, chat routing, KQ, holy promise, instances, misc",
      out="docs/pseudocode/wm/W04-social-misc.md", deps=["W01"],
      scope=[("wm", "CParserClient", [8, 21, 22, 28, 31, 32, 37, 41, 42]),
             ("wm", "CParserCharDB", [21, 28, 31, 37, 41, 42]),
             ("wm", "CParserZone", [8, 9, 18, 21, 22, 24, 36, 37, 41, 47]),
             ("wm", "CParserOPTool", [8, 10, 37, 52]), ("wm", "CParserAccountLogDB", [32])],
      steps=["Open from C01 (`docs/knowledge/C01.md` §5): `0x083a` (13 bytes, sent by `FUN_00408050`, which sends to "
             "in-game clients and to a zone). Settle which send carries 0x083a and who receives it; the client has no handler "
             "for it.",
             "Open from C01: `0x7c07`. Its catalog name NC_PRISON_ADD_GM_ACK † is borrowed from the log string of the "
             "`0x7c0f` handler `FUN_0040c350` and is probably wrong. 0x7c07 is sent by `FUN_00415530` (the `0x7c06` "
             "handler) and by `FUN_0040c350`. The client reads it in the character-select scene as {u16 code, u16 value} "
             "(code 0xDB0 → keeps the value, `FUN_00475fb0`). Give it a layout and a meaning, and a name only if a string "
             "supports one.",
             "C01 found no client handler for `0x5802`, `0x7038`, `0x703a`, `0xa415` although the WM sends them to a "
             "client: document them as ignored by the 2016 client, not as missing.",
             "Open from Z06 (§4.1, §8): the gamble system server `CGambleSystemServer` (init FUN_0043c1a0, "
             "`SendExchangeCoinInit` FUN_0043c2d0): when and how it computes the next daily coin reset and broadcasts "
             "`0xBC09 NC_GAMBLE_EXCHANGEDCOIN_INIT_CMD` to the zones. The zone side is documented in Z06 §4.1."]),
 dict(id="W05", phase=2, title="World manager: process services left out of W01-core (added by W04)",
      out="docs/pseudocode/wm/W05-process.md", deps=["W01"], scope=[],
      goal="W01's goal includes the WM process (startup/config, session lifecycle), but `W01-core.md` documents only "
           "the bootstrap, cleanup and accept ticks (§2) and never cites the main loop, the data loader or the session "
           "teardown chain. W02–W04 document the subsystems these call, not the functions themselves. Reconstruct the main "
           "loop, the table loader, the timed broadcasts and how a client session is torn down and reset.",
      steps=["Read `docs/pseudocode/wm/W01-core.md` §1, §2, §5.4 and `docs/knowledge/W01.md` first, and the coverage-boundary "
             "rows of `docs/pseudocode/wm/W04-social-misc.md` §20 that name W05.",
             "Main loop FUN_00406760: the order and period of every tick it runs. Most are documented by other items; cite them, "
             "do not redo them (`KQ_Tick` W04 §6.2, `CPrisonServer_Tick` W04 §9.1, `CGambleSystemServer_SendExchangeCoinInit` "
             "W04 §15.1, `EA_Schedule_Process` W04 §17.5, `NpcSched_Tick` W04 §17.6, `IndunRank_DailyReset` W04 §13.3, "
             "`GuildManager_Tick` W03, `PartyFinder_ExpireTick` W02, `Login_WorldStatus_0808` / `Zones_TimeSync_0821` W01 §2). "
             "Not documented yet: the once-a-minute 0x0849 date/time broadcast FUN_00437e30 (layout, receivers, client "
             "handler) and FUN_0043a120.",
             "Data loader FUN_00404100: every SHN table and config file the WM loads, in order, with the object offset each lands "
             "at, the fatal / non-fatal failures, and which item uses each table (W04 already documents the KQ, SpamerReport, "
             "GBHouse and MsgWorldManager rows: §2.5, §6.1, §6.2, §15.1). Also the client-SHN name list FUN_0045d8c0 (49 file "
             "names, no caller in the export: settle what uses it, e.g. a hash or version check).",
             "Session teardown and reset: FUN_00437660, FUN_00437fd0, FUN_00438630 (→ session destructor FUN_004352e0), "
             "FUN_00438a60 (→ reset FUN_00434530): which event triggers each (disconnect, kick, return to character select, "
             "duplicate login), what each releases (blobs, lists, party/guild/friend/KQ state; link to the W02–W04 functions "
             "it calls, e.g. `ChatRestrict_Destroy` W04 §14.1) and what it tells the other links.",
             "Then `python3 -I tools/protocol-re/coverage.py W01 --all`: W01's remaining gaps that are core rather than "
             "feature code (zone registration chain under 0x0802 FUN_00465ef0 / FUN_00465d60 / FUN_00465e10 / FUN_00460ba0, "
             "world login FUN_004129f0, `Session_Close` callees FUN_00466180 / FUN_00466060, map-login-done FUN_00432e10 / "
             "FUN_00432ce0, …) belong here; gaps inside W02–W04 subsystems go to those items' coverage boundary instead."],
      done="Main loop, data loader, 0x0849 broadcast and the session teardown/reset chain written as pseudocode; every core "
           "gap from `coverage.py W01` either documented here or assigned to another item with a reason."),
 dict(id="W06", phase=2, title="World manager: class-named functions no document cites and three unread guild / option "
                               "points (added by X02)",
      out="docs/pseudocode/wm/W06-leftovers.md", deps=["W03", "W04", "W05"], scope=[],
      goal="98 functions the 2016 `WorldManager.pdb` names `Class::Method` are cited by no document (2 019 lines; "
           "`CGuildMember` 15, `CGuild` 13, `CGuildAcademyMember` 12; `docs/review/confidence.md` §4.4), among them five "
           "`CGuild*::Recv_NC_GUILD_*` members without a direct caller. X02 also left three WM statements unread "
           "(`confidence.md` §3.5.3 E14, E15, E25).",
      steps=["List them: `python3 -I docs/plan/status/X02-cov.py game wm 100`. `rg` each name in `docs/pseudocode/wm` first; "
             "cite the § where one is already described under its name.",
             "The `Recv_NC_GUILD_*` members (`CGuild::Recv_NC_GUILD_WAR_TARGET_CMD` FUN_0045bdb0 and four more): find how they "
             "are reached (member-pointer table, virtual, or dead) and whether W03 documents the same opcode through another "
             "function.",
             "E14: W03 §2.5, the two helpers of 0x740C @ FUN_00419db0 that produce the result its three error exits return "
             "(0xCDE, 0xCD8, 0xCDB): is the trailing 0x0CDB dead? E15: W03 §3.5, client `GuildTask::"
             "Recv_NC_GUILD_WAR_ABLE_LIST_ACK` FUN_006b3e00: what it does with 0x0D1A / 0x0D1B. E25: W04 §12.3, the "
             "dice-game test that drops the answer of 0x9405 (the `n` cap of W04 §8.3 is confirmed: `confidence.md` §4.7).",
             "Bugs as `W06-B<n>`; corrections to W03 / W04 in `docs/knowledge/W06.md` §0."],
      done="Every function of the list is cited with pseudocode or a link, the five `Recv_` members have a stated caller or "
           "are shown dead, and E14 / E15 / E25 have a verdict."),
 dict(id="S02", phase=2, title="Shared server library: IOCP sockets, acceptor, packet buffers, CCsl script and GDP file "
                               "readers (added by W05)",
      out="docs/pseudocode/shared/S02-library.md", deps=["W05"], scope=[],
      goal="Login, WorldManager and Zone link the same network and config library (classes `CIOCP`, `CSocket_IOCP`, "
           "`CSocket_Acceptor`, `CIOBuffer` / `IOBufferContainer`, `CIOSpinLock`, `CPacket`, `CSendPacket`, `InetAddress`; "
           "the `CCsl` / `CToken` script parser that reads ServerInfo.txt and WMServerInfo.txt; the `CGdp` packed-file "
           "reader `CCsl::Read` opens files through). No item documents it: L00, W01, W05 and Z01 only call it (W05 §1, "
           "§4.5, §5.2 describe what the WM sees of it). Reconstruct it once, from the WM build (PDB names), and map the "
           "Login and Zone copies onto it: send queue and partial writes, receive buffer and framing hand-off to "
           "`CPacket`, close / shutdown / overlapped completion, accept thread and the 3-port listener, worker-thread "
           "loop, buffer pools and their limits; the script grammar (`#` commands, formats, data rows, includes, "
           "remarks, tokens) and the GDP container (chunks, `GdpDecryptData`).",
      steps=["Read `docs/pseudocode/wm/W05-process.md` §1.1–§1.5, §4.5, §5.2 and §9 (its coverage-boundary rows that name "
             "S02) and `docs/protocol/README.md` (framing, cipher) first; do not redo them.",
             "Network, WM build (`clean.py re-data/exports/wm-pdb - <addr> …`): `CIOCP` ctor FUN_00464350, Start FUN_004645c0, "
             "WorkThread FUN_004644f0, Register FUN_00464380, Stop FUN_004643c0, Close FUN_004646b0; `CSocket_Acceptor` "
             "FUN_00463960 … FUN_00463ee0 (Listen_Add FUN_00463a50, Listen_Start FUN_004642a0, AcceptThreadRing FUN_00463ee0, "
             "Get/SetAccepted FUN_00463bb0 / FUN_00463c40, Stop / Listen_Stop FUN_004639e0 / FUN_00463e10); `CSocket_IOCP` "
             "ctor FUN_00466420, Connect FUN_004665b0, Send FUN_004666f0, WriteCallback FUN_00466240, Receive FUN_00465f40, "
             "FreeBuffer FUN_00466140, dtor FUN_00466520; `CIOBuffer::Alloc` / `Free` FUN_00468e10 / FUN_00468f00, "
             "`IOBufferContainer` FUN_00468d80 (512 × 0x2010), `CIOSpinLock::Wait` FUN_00468d10, `InetAddress::WinSockStart` "
             "FUN_00468c40, `CSendPacket` FUN_0045fd30 … FUN_0045fe70, `CPacket` FUN_00467aa0 … FUN_004678c0. Then find the "
             "same functions in the Login (`login-pdb`) and Zone (`zone-pdb`) exports by name and note any difference.",
             "Script / file readers: `CCsl` FUN_00460a40 … FUN_004626f0 (ReadScript FUN_004626f0, ProcCmd FUN_004621f0, "
             "MakeFormat FUN_00460ea0, MakeData FUN_00461240, ProcRemark FUN_00460c90, IncludeFile FUN_00462090, "
             "ReadScriptDone FUN_00461520, Read FUN_00461730), `CToken` FUN_0045a080 … FUN_0045a6f0, `CGdp` FUN_0045ed50 … "
             "FUN_0045fac0. Write the grammar the shipped `ServerInfo.txt` / `WMServerInfo.txt` / Zone and Login configs "
             "use, check it against those files, and say whether any 2016 install ships a GDP container.",
             "Mark library behaviour that looks unintended as `(original bug) S02-B<n>`; end with the bugs table, "
             "uncertain section and coverage boundary as every item does."],
      done="Every function listed above cited with pseudocode at W05's depth; the Login / Zone copies mapped; the config "
           "grammar written and checked against the shipped files."),
 dict(id="L01", phase=2, title="Login server: process layer and session pools left out of login-server.md (added by S02)",
      out="docs/pseudocode/login/L01-process.md", deps=["L00", "S02"], scope=[],
      goal="`login-server.md` (L00) documents the Login handlers, startup order and listen ports, but cites none of the "
           "process layer around them: about 45 functions (~1.2k decompiled lines, `login-pdb`) of `LoginServer`, the "
           "session pools and the client / WM session managers. S02 §4.3 documents only the pieces that call the shared "
           "library (constructor, OnStart_Service, Start_Acceptor, ProcessStop, DissconnectAllSessions, ProcHeartBeat, "
           "session constructor). Reconstruct the rest at W05's depth (W05 §1 / §4 is the WM twin).",
      steps=["Read `docs/pseudocode/login-server.md` §1–§3, `docs/pseudocode/shared/S02-library.md` §1.6, §4.3 and "
             "`docs/pseudocode/wm/W05-process.md` §1, §4.1–§4.5 (the WM equivalents) first; cite them, do not redo them.",
             "Main thread and steps (`clean.py re-data/exports/login-pdb - <addr> …`): `MainThread` FUN_004030e0, "
             "`ProcessPacket` FUN_004024e0 (the packet pump: order of pools, per-pass limits, the bad-frame close), "
             "`OnStop_Service` FUN_00402b70, `ViewStartInfo` / `ViewStopInfo` FUN_00401120 / FUN_00401250.",
             "Session pools: `CLoginBaseSessionManager` ctor / InitSessions / EmptyToActive / ActiveSession / "
             "InactiveSession / FreeSessions / dtor (FUN_00409200 … FUN_004094d0), `CLoginClientSessionManager` "
             "(FUN_00409680 … FUN_00409bc0: ActiveSession, HandleIsValid, GetSession, Kickoff, Send, InitSessions, "
             "FreeSessions), `CLoginOPToolSessionManager` (FUN_00409c30 … FUN_00409d20), `CLoginWorldManagerSessionManager` "
             "(FUN_00409e40 … FUN_0040a420: ActiveSession, Get/SetWorldManagerConnectInfo, GetClientValidation, SetWMSession, "
             "InactiveSession, FreeSessions, InitSessions), `CLoginClientSession` ctor / dtor / Get/SetSessionMode "
             "(FUN_00409520 … FUN_00409670): pool sizes (from `nMaxAccept`), handles, which event frees a session.",
             "`LoginServer::m_LoginUserRatable` (256 × 6 ints set to 3, 5, 8, 10, 30, 95 in the constructor FUN_004029e0, "
             "S02 §4.3): find its readers and what the world status sent to the client is computed from.",
             "Parsers and members the constructor / dtor / ProcessPacket reach: `CParserWorldManager::Parser` FUN_004087d0 and "
             "its `pft_Store` FUN_004086b0 (compare with the other parsers L00 cites), `CLoginAccountDBSession` / "
             "`CLoginAccountLogDBSession` ctors FUN_00408cd0 / FUN_00408d00, `COTPLogin` ctor FUN_0040a560 and `~COTPData` "
             "FUN_0040a550; the per-parser copies of the 0x0801 / 0x0804 handlers L00 cites only once: "
             "`CParserAccountLogDB::fc_NC_MISC_S2SCONNECTION_RDY` / `fc_NC_MISC_HEARTBEAT_REQ` FUN_00404f50 / FUN_004050e0, "
             "`CParserOPTool::fc_NC_MISC_HEARTBEAT_REQ` FUN_00407480, `CParserWorldManager::fc_NC_MISC_HEARTBEAT_REQ` "
             "FUN_00408560 (same body as L00's copy or not).",
             "Sweep (L01 has no scope table, so `coverage.py L01` does not apply): list every caller and callee in "
             "`login-pdb` of the functions above and of `LoginServer::LoginServer` / `~LoginServer` / `MainThread` that no "
             "doc cites as `FUN_…` (S02 part 4 used such a script over `decomp.c`), and cover or bound each.",
             "Mark unintended behaviour `(original bug) L01-B<n>`; fix nothing in `login-server.md` (done item): put "
             "corrections in `docs/knowledge/L01.md`."],
      done="Every function named above cited with pseudocode; the session lifecycle (accept → pool → free) and the main "
           "loop order written; the sweep step finds no Login process function left uncited."),
 dict(id="Z02", phase=2, title="Zone: movement, chat, emotes, sight/briefinfo, NPC menus, scenario",
      out="docs/pseudocode/zone/Z02-actions.md", deps=["Z01"],
      scope=[("zone", "ShinePlayer", [7, 8, 15, 27]), ("zone", "WorldManagerSession", [8])],
      goal="Movement validation and broadcast, speed, collision/map checks, chat types (normal, shout, whisper path to WM), "
           "emotes, object appear/disappear (BRIEFINFO: what other players see), NPC click/menu flow, scenario/cutscenes."),
 dict(id="Z03", phase=2, title="Zone: combat, skills, abstates, damage", out="docs/pseudocode/zone/Z03-combat.md", deps=["Z01"],
      scope=[("zone", "ShinePlayer", [9, 18]), ("zone", "GameDBSession", [18])],
      goal="Attack flow (basic attack, skill cast/bash, cast abort), target validation, hit/miss/crit/block, damage formulas "
           "(use SHN tables ActiveSkill, PassiveSkill, DamageLvGapEVP, WeaponAttrib…), abstates (buffs/debuffs, AbState.shn, "
           "SubAbState.shn), death, experience and level-up, PvP rules.",
      steps=["Open from Z02 (§15): ShinePlayer flag byte `+0x1e78` bit 5 (read by vt 0xf20 = FUN_0055d5a0) blocks walking/running like Fear (bit 2, `SubAbnormalStateFear::sasa_Routine`). Find the abstate that sets it and list what each bit of `+0x1e78` means."]),
 dict(id="Z04", phase=2, title="Zone: items, inventory, equipment, upgrades (client side)",
      out="docs/pseudocode/zone/Z04-items.md", deps=["Z01"], scope=[("zone", "ShinePlayer", [12, 20])],
      goal="Inventory model (bags, slots, stacking), equip/unequip, use item, drop/pickup, enchant/upgrade/sockets, "
           "dismantle, soul stones, item info packets. Use ItemInfo/ItemInfoServer/ItemUpgrade/RandomOption SHN tables.",
      steps=["Open from Z02 (§9.2): the megaphone `0x204B NC_ACT_ROAR_REQ` consumes the item through `UseItemNormal.uib_AfterCast` and queues the text in the ring `g_RoarQueue` (DAT_008598c0, `RoarQueue_Push` FUN_0053f900), index in `p+0x2a79c`. Trace how and to whom the message is sent when the item effect runs (zone broadcast or WM)."]),
 dict(id="Z05", phase=2, title="Zone: item database protocol (ITEMDB, zone↔Character server)",
      out="docs/pseudocode/zone/Z05-itemdb.md", deps=["Z04"], scope=[("zone", "GameDBSession", [13])],
      goal="The 108 ITEMDB replies: how item changes are persisted and confirmed, item creation (item keys), "
           "consistency/rollback behaviour. Pair each with the request the zone sends and the client-facing result.",
      steps=["Open from Z07 (§11): production is live in 2016 (the client's `ProductTask` sends 0x2035); the cast end calls "
             "`smo_ply_ItemProduce` FUN_0046c2d0, which sends DB 0x3457. Document 0x3458 NC_ITEMDB_PRODUCE_ACK and what the "
             "2016 client sees (it has no handler for 0x203B/0x203C; it does handle 0x481D in `ProductTask`).",
             "Open from Z07 (§6.10): mini-house furniture/portal effects lock items and money and send 0x347D / 0x3489 "
             "(layout in `annotations/Z07.json`); document their answers 0x347E / 0x348A and how the effect is applied."]),
 dict(id="Z06", phase=2, title="Zone: trade, booths, gambling, dice", out="docs/pseudocode/zone/Z06-economy.md", deps=["Z04"],
      scope=[("zone", "ShinePlayer", [19, 26, 43, 47]), ("zone", "GameDBSession", [43, 47]), ("zone", "WorldManagerSession", [47])],
      steps=["Open from Z07 (§1.2): WM `0x10DD NC_CHAR_ZONE_COININFO_CMD` (handler FUN_00617830, profiler string says "
             "GAMBLE_ZONE_PREVMAPNAME) passes the gamble coin data to player vt 0xb00 (FUN_00615d10); document that method "
             "with the coin state it fills."]),
 dict(id="Z07", phase=2, title="Zone: character stats, progression, pets, mounts, mini-house, collection cards",
      out="docs/pseudocode/zone/Z07-character.md", deps=["Z01"],
      scope=[("zone", "ShinePlayer", [4, 35, 49, 51, 53]), ("zone", "GameDBSession", [4, 35, 49, 53]),
             ("zone", "WorldManagerSession", [4, 51, 53])],
      goal="Stat model (base/derived, the stat pairs in 0x1802), stat points, level/exp tables, revive, titles, "
           "pets (PET), mounts (MOVER), mini-house, collection cards.",
      steps=["Open from Z02 (§10): the wedding client handlers are documented in Z02 and read the player's copy of NC_CHAR_WEDDINGDATA_ACK at `p+0x5cc8`. Settle: how `Partner.RegisterNumber` (+0x5ced) is set before 0x204F (Z02 found no handler that reads the proposal target from the packet; 0x1095 NC_CHAR_WEDDING_PARTNER_INFO_RNG?), the meaning of the `Status.Main` / `Status.Sub` values, what the DB answers to 0x1083/0x1089/0x108B/0x108D/0x108F do, `WeddingHall.wh_Reserv` and the hall timetable (`g_WeddingHall` DAT_0086ea38), and FUN_005b92a0 (called after an accepted proposal).",
             "Open from Z02 (§8): production. 0x2035 NC_ACT_PRODUCE_CAST_REQ starts a cast whose end (0x203B / 0x203C) is handled in the player tick; the 2016 client has no handler for 0x2036/0x2038/0x203A/0x203B and produces through `ProductTask` (0x481D). Document the live production path and say whether the 0x2035 path is dead."]),
 dict(id="Z08", phase=2, title="Zone: quests, kingdom quests, instances, guild/party/friend zone side, holy promise",
      out="docs/pseudocode/zone/Z08-content.md", deps=["Z01"],
      scope=[("zone", "ShinePlayer", [14, 17, 21, 22, 23, 24, 29, 37, 38, 41]),
             ("zone", "GameDBSession", [17, 22, 23, 29, 36, 37, 38]),
             ("zone", "WorldManagerSession", [14, 17, 22, 24, 29, 31, 37, 38, 41, 44, 52])],
      steps=["Open from Z02 (§6.5): the instance-dungeon gate NPC roles `NPCRole_ID_Portal` (nrb_Role FUN_004c33f0), `NPCRole_Mode_ID_Portal` (FUN_004c35d0), `NPCRole_RandomMulti_Portal` (FUN_004c3850) and the server-menu callbacks `smfm_LinkToDungeon` (FUN_0050f070), `smfm_DeleteInstanceDungeon` (FUN_0050f370). Z02 documents the plain `Gate` role and the ServerMenuActor they build on."]),
 dict(id="Z09", phase=2, title="Zone: world simulation (mobs, NPCs, AI, spawns, drops, scripts, timers)",
      out="docs/pseudocode/zone/Z09-world.md", deps=["Z01", "Z03"], scope=[],
      goal="Everything not driven by a client packet: mob spawning (MobRegen/MobSetting data), AI and behaviours "
           "(MobBehaviorDescript), aggro, movement, drops (MobInfoServer, ItemDrop tables), NPC objects, Lua scripts "
           "(9Data/Shine/LuaScript), map events, the main tick and timers.",
      steps=["Open from Z02 (§15): the NPC AI-script events passed to `so_AIScriptFuncExec` (FUN_004ab3f0): 0x20 = clicked (0x200A), 0x3c = menu answer (0x2073); the map-script interrupts `sim_NPCClick` / `sim_AreaEntry` / `sim_AreaLeave` (Z02 §12) and the Lua chat/jump triggers. Document what the scripts can do with them.",
             "Open from Z02 (§5): how objects that leave a player's sight disappear on the client (the zone never sends 0x1C0E NC_BRIEFINFO_BRIEFINFODELETE_CMD); check the client's own sight handling and any zone-side cell-change exchange.",
             "Find subsystems via class names (RTTI) and profiler strings (`grep -n '::' re-data/exports/zone/strings.tsv`).",
             "Start from the main loop / tick functions found in Z01's knowledge file.",
             "Open from Z08 (`docs/knowledge/Z08.md` §2): the player routine that calls `sp_SendMyInform2PartyMember` "
             "FUN_0056df80 (party status every tick, Z08 §1.2); the prison release timer behind `so_Prison_Go` / `so_Prison_End` "
             "(FUN_005b94b0 / FUN_005b9730, map EldPri); what the GM events (`g_GMEvents` DAT_14d42940, activation FUN_0046d5c0) "
             "change; the map scripts that run kingdom quests (`ScenarioBookShelf`, `PineEventScriptNode::ShineEndOfKingdomQuest`, "
             "`ShineQuestResult`, `ShineQuestMobkill`). The KQ and guild-tournament objects themselves are Z16; the quest engine is Z15.",
             "Open from Z06 (§8): the drop-item dice game is a drop feature and belongs here: `ShineDropItem::so_DiceItemPickInit` "
             "FUN_00531020, `sd_DiceGameResult` FUN_00531470, the packets `0x303B` / `0x303E` / `0x303F`, the table "
             "`BelongDice.shn`, and the party/raid loot distribution FUN_00644f60."]),
 dict(id="Z10", phase=2, title="Zone: certification and the downloaded start script",
      out="docs/pseudocode/zone/Z10-certification.md", deps=["Z01"], scope=[],
      goal="The zone does not start on its own: it downloads an encrypted Lua script from a certification server "
           "(127.0.0.1:58492, fallback cert1.fo.gamigo:80), decrypts it with registry keys HKLM\\SOFTWARE\\GBO "
           "`Natural`/`Desert` and runs it; the script calls the registered `zs_service_*` / `zs_start_*` stages "
           "(Z01-core §2). Only the zone uses this (no other server binary has these strings). The original Gamigo "
           "script is lost, but a working replacement answer exists: the NA2016 service `_GamigoZR` "
           "(`Files/Server/NA2016/GamigoZR/GamigoZR.exe`) serves it on 127.0.0.1:58492 (S01 §1.5). Reconstruct the "
           "mechanism, decrypt that answer to recover the script it carries, and from both state what the script must "
           "do, so a rebuilt server knows which stage order and which values to use, and whether the certification "
           "can stop the server.",
      steps=["Read `docs/pseudocode/zone/Z01-core.md` §2 and `docs/knowledge/Z01.md` §1/§7 first. The stage functions and "
             "several entry points are not in `decomp.c`; decompile them against the persistent Ghidra project with a "
             "headless script (`analyzeHeadless re-data/ghidra zone -process -noanalysis -readOnly`, `createFunction` + "
             "`DecompInterface`), as Z01 did.",
             "Request/response: `FetchStartScript` FUN_005b07a0 and its callees FUN_00613440 (request build/send), "
             "FUN_00613750 (key setup from the two registry int64s), FUN_00613950 (decrypt), FUN_005d6d40 (Lua dostring). "
             "Document the wire format, what the request carries (world/zone numbers, version?), the `[a][b]` header "
             "checks (1 ≤ a ≤ 0x2760, b < 11) and the cipher as pseudocode with test vectors if possible.",
             "The GamigoZR answer (S01 §1.5, read it first): a .NET 4 Windows service \"Gamigo_Zone_Response_Service\" "
             "(2019, private-server tool, installed by `install.bat` / `_Install Services.ps1` as `_GamigoZR` and started "
             "5 s before the zones by `Start Services.ps1`), an `HttpListener` on `http://127.0.0.1:58492/` (the zone's "
             "primary certification address; the zone falls back to cert1.fo.gamigo:80, which no longer answers). Its "
             "UTF-16 strings hold the header `[10000][10][{( USA V.0.001 )}]` and 42 hex lines (2 680 hex digits). "
             "Read its IL (e.g. `monodis`/`ilspycmd` if installed, else parse the .NET metadata with Python) to get "
             "the line order and the exact HTTP reply (status, headers, body framing), check that the header passes "
             "the `[a][b]` checks, then decrypt the body with the zone's cipher. The registry keys `Natural`/`Desert` "
             "are not in the repo: look for them in the NA2016 files (`*.reg`, `*.ps1`, `*.bat`, readme) and, if absent, "
             "say whether the cipher can be solved without them (known plaintext: the script must call `zs_*` names). "
             "If the decrypted script is recovered, document it in full: it replaces the inferred stage order below "
             "and gives the real values (run/walk factors, server parameters). Do not run the service or the zone.",
             "Threads: `zs_service_certification` (thread FUN_005ab9c0) and `zs_service_stackchecker` (thread "
             "FUN_005a9f10). What do they check, how often, against what, and what happens on failure (log, shutdown, "
             "silent misbehaviour)? Look for time/expiry checks (`dhsmfskfWk` date helper, DAT_00aa43b8).",
             "The Lua surface: list every C function the script can call (FUN_005d7ca0 and any other `lua_setglobal` "
             "registrations), with arguments and effects. In particular the run/walk factors (`ekfflrlthreh` / "
             "`rjerlthreh` → 0x203E move speed) and any writer of the 0x0830 server parameters (DAT_0da5047c / "
             "DAT_0da50480). Check whether the script can read or set other globals.",
             "Infer the stage order from data dependencies between the stages (e.g. Field.txt before NPCs, packet "
             "tables before listeners, `zs_start_open` last) and from the Message.txt labels. Give one recommended order "
             "with the reason for each constraint, marked *(inferred)*.",
             "Diff with the 2015 zone (`Files/Server/2015/w00_Zone00`) only to see whether the mechanism changed; do "
             "not document 2015 otherwise.",
             "If a capture of a live zone start ever appears in `re-data/captures/`, it overrides inference.",
             "End with a recommendation for a rebuild: which values to hard-code, what to leave out."],
      done="Request/response and cipher documented; both threads explained with their failure behaviour; Lua surface "
           "listed; a recommended stage order with reasons; rebuild recommendation written."),
 dict(id="Z11", phase=2, title="Zone: GM ampersand (&) commands",
      out="docs/pseudocode/zone/Z11-gm-commands.md", deps=["Z01", "Z02"], scope=[],
      goal="A chat line that starts with '&' is an admin command, not chat (Z02 §3.3: `sp_AmpersandCommand` FUN_0041a060 → `so_ply_AdminCommand` FUN_00427a40 → command list DAT_0087c770, `FUN_00487c50`). The zone has 119 command functions `AmpersandCommand_ac_*` (names in `tools/protocol-re/names/zone/Z01.json`). Document every command: the word the GM types, its arguments, the admin level it needs, what it changes and which packets it sends.",
      steps=["Find where the `AmpersandCommandElement` list is built (registrations that fill DAT_0087c770): command word string, required admin level, handler. The argument parser is `ListIter_AmpCmdArgument`.",
             "Admin level: player `+0x7fa1` (vt 0x4d4), sent to the client as 0x10C6 at login (Z01 §6); the `AdminLvSet` table is loaded in `zs_start_sleep` (Z01 §2.3). Say how a level is granted and checked.",
             "Output one table (command, syntax, level, effect, packets) for all commands, plus full pseudocode for the ones that change persistent state (MakeItem, GetMoney, LevelUp, ClearInventory, learnskill, KingdomQuest, Wedding*, KQReward, BonusExp / BonusItem / FieldBonus) or reach other servers (WM, Character DB, GameLog).",
             "Several commands duplicate OPTool features (Z01 §9) or wrap handlers documented elsewhere (wedding Z02 §10, dice / TaiSai Z06): reference those instead of repeating them."],
      done="Every `AmpersandCommand_ac_*` function appears in the table; unknown words or levels are marked as such."),
 dict(id="Z12", phase=2, title="Zone: stat calculation, level/exp, login data parsing (added by Z07)",
      out="docs/pseudocode/zone/Z12-stats.md", deps=["Z03", "Z07"], scope=[],
      goal="Z07 documented the packets around stats and login but not the code that computes stats or reads the login "
           "data. Reconstruct the full stat model (every stat-matrix layer, max HP/SP/LP, stones), the level/exp tables and "
           "level-up side effects, and how the zone parses each WM login blob into the player object.",
      steps=["Read `docs/pseudocode/zone/Z07-character.md` §1–§2 and `docs/knowledge/Z07.md` first; Z03 §2 has the matrix "
             "formula `Total = (L0+L1)·L12·L10·L4·L14/10¹² + L5+L7+L9+L11+L13` and Z07 §1.5 confirmed layer 0 = base, 15 = total.",
             "`so_allparametercalculate` (vt 0x57c, FUN_0054f190): what fills each layer (class base stats per level from "
             "class data `p.vt[0x49c]() + 0x10858`, stat points via FUN_00517b60, items, upgrades, passives, abstates, titles, "
             "charged buffs `p+0x2a5a0`), and the order. MaxHP FUN_0054a670, MaxSP FUN_0055a8b0, MaxLP vt 0xd94, HP/SP stone "
             "maxima (`p+0x2a5a2/a4`). Which packets the refresh `vt 0x528` and `smo_NotifyParameterChange` (vt 0x34) send.",
             "Level/exp: `g_LevelExp` (DAT_0da504a8, u64 per level; Z07 found that the per-stat cap DAT_0da504a9 lies inside "
             "its level-0 entry: explain), the stat-point table DAT_0da50968 (loader, file, columns), exp gain and level-up "
             "side effects (FUN_0058bd10, reward table DAT_14d42940), level-up packets. Check Z03's output first so exp on kill "
             "is not documented twice.",
             "Login blob parsing (dispatch table in Z07 §1.2): `so_charsharpdata` FUN_0044ae80, `so_StoreQuestDoing/Done/Read` "
             "FUN_0044b3c0 / FUN_0044b500 / FUN_0044b640 / FUN_0044b770, `so_CharAbstateData` FUN_0044e0e0, `so_charskilldata` "
             "FUN_0044bf20, `so_CharChargedBuffData` FUN_0044e1e0, `so_charpassivedata` FUN_0044e5a0, "
             "`so_StoreInventoryFromServer` FUN_0044ddf0, `so_Storegamedata` FUN_0044c220, `so_ply_Getchestinform` FUN_0044c8a0, "
             "and the builder `vt 0x4b4` FUN_0055ab60. Give each body layout (compare the PDB `PROTO_NC_CHAR_*_CMD` structs and "
             "W01 §6.3) and the player members it fills.",
             "Smaller open points from Z07 §12: 0x10D3 NC_CHAR_ZONE_SINGLE_OPTION_CMD fields (FUN_0059d510, FUN_00560340, "
             "FUN_00560a10, vt 0xae8), the 0x10B8 LINK_FROM record (FUN_00444970, FUN_00570b30), the title progress reset rule "
             "FUN_0062e120 (0x1031)."],
      done="Every stat-matrix layer has a named source; level/exp tables and level-up documented; every login blob has a "
           "body layout and the members it fills."),
 dict(id="Z13", phase=2, title="Zone: mini-house object, wedding hall, pets and mounts internals (added by Z07)",
      out="docs/pseudocode/zone/Z13-objects.md", deps=["Z07"], scope=[],
      goal="Z07 documented the client requests and DB answers of these subsystems; the object methods and timers behind "
           "them are not reconstructed. Document them so a rebuild can implement the objects.",
      steps=["Read `docs/pseudocode/zone/Z07-character.md` §5, §6, §8, §9 and §12 and `docs/knowledge/Z07.md` first.",
             "ShineMiniHouse (type 3; vtable slot list in Z07 §6.1): enter/out/visit rules and password (vt 0x7c, 0x88, 0x90, "
             "0x98), LOGINCOMPLETE fill vt 0xa0 (player-list element layout), furniture create/rearrange/delete (vt 0xb8–0xc0) and "
             "their releasers `InvenCellReleaser_FurnitureReloc` / `FurnitureCellClear` (0x8C21 / 0x8C24 / 0x8C27), "
             "`smh_SendFurnitureInfo` (0x8C08 / 0x8C09), settings setters (vt 0xe4–0xf8, the limits behind the result codes), "
             "portals (vt 0x10c–0x124) and `so_Routine` (portal timeout), endurance (`MiniHouseEndure.shn`, item cell +0x25), "
             "`so_MH_EffectApply` FUN_005751f0 and `so_MH_PortalEffectApply` (player vt 0x128), the in-house dice game state "
             "(vt 0x2a0, player vt 0x170 / 0x190 / 0x194), furniture emotions (house vt 0x2d8, player vt 0x2b0, 0x2c0, "
             "0x2cc–0x2d4), the house box fill (player vt 0xcc FUN_00570260), and the 0x8C3F field mapping against "
             "`MiniHouseObjAni` (Z07 §6.9).",
             "Wedding hall and married state: `g_WeddingHall` (DAT_0086ea38) and `WeddingHall.wh_Reserv`, the hall timetable "
             "and ceremony flow (who sends `0x1091 NC_CHAR_WEDDING_DO_REQ`: grep `= 0x1091;` in the zone export), "
             "FUN_0059ef40, FUN_005b92a0 (called after an accepted proposal), player vt 0x40c / 0x410 / 0x418 / 0x960, "
             "`ZoneRingPacketRefreshWeddingInfo`. Z02 §10 has the client requests.",
             "Open question from D02 (`docs/pseudocode/db/D02-character.md` §11 end and §16): the Character DB stores "
             "sub-status 6 (= 2 + 4) for \"partner applied for divorce by agreement\" and adds 4 on divorce cancel (1 → 5, "
             "3 → 7), while Z07 §5.1 reads Sub values 1–4. Find out how the zone handles 5–7 when the `0x1081` Status byte "
             "(`nStatus | nSubStatus << 4`) arrives (masks bit 2, treats them as \"none\", or mis-handles them; "
             "`FUN_0059f2d0` area), and record the answer in `docs/knowledge/Z13.md`.",
             "Pets: the summon/unsummon flow (`so_PetSystem_Unsummon` FUN_004d2990 and its callees FUN_004d1ff0, FUN_004d2520, "
             "FUN_004d25d0; the pet item's UseEffect actor, Z04 §6.3), pet states 1/2/8 at `p+0x2ab60`, who sends 0xD405 "
             "ASK_NEW_NAME_REQ and 0xD401 SET_TENDENCY (mind/stress), the resummon after a map link (`p+0x2aba8`, WM 0xD412), "
             "the `ShinePet` object.",
             "Mounts: mover creation (which item or NPC allocates a `ShineMover`), `so_smv_GetOff` (vt 0xcbc FUN_0055f620), "
             "seat reservations (`+0x1ee0`), the mover script hook FUN_0055f0a0, `sp_HorseItemSave`, the 0xCC0C LINKDATA restore "
             "FUN_0045ddf0, hunger (link to Z02 §9.1).",
             "Smaller open points from Z07 §12: minimon list kinds (`MinimonInfo.shn` / `MinimonAutoUseItem.shn` columns, "
             "codes 0x362A / 0x362C), the return values of `cca_IsRewardCondition` FUN_00628d60 (read the assembly), and what "
             "the client task UIs do with the result codes that have no text (0xAC*, 0x36**, 0x16C*, 0x19D*, 0x2B9*)."],
      done="Every ShineMiniHouse slot Z07 lists is documented or marked unused; the wedding hall timetable and ceremony "
           "flow, the pet summon flow and the mover lifecycle are written as pseudocode."),
 dict(id="Z14", phase=2, title="Zone: instance dungeons, zone-ring storage handlers, raid internals (added by Z08)",
      out="docs/pseudocode/zone/Z14-instances.md", deps=["Z08"],
      scope=[("zone", "ZoneListenSession", [29, 38, 41])],
      goal="Z08 documented the client and WM handlers around instance dungeons, raids and guild/academy storage, but not "
           "the managers behind them. Z01 (`Z01-core.md` §10, table of ZoneListenSession handlers) handed the zone-ring "
           "handlers to Z08, which documented only their senders. Reconstruct the instance cluster manager, every "
           "ring handler in the scope table plus the two listed below, and the raid record and status packets.",
      steps=["Read `docs/pseudocode/zone/Z08-content.md` §1, §2, §5, §8, §10 and §15 and `docs/knowledge/Z08.md` first.",
             "Two more ZoneListenSession handlers outside the depts of the scope table: `0x10B1 NC_CHAR_EMPTY_INSTANCE_DUNGEON_RNG` "
             "FUN_00485120 and `0x441F` (job dungeon) FUN_005bfde0. Z08 §5.2 has their senders (`ZoneRingPacketEmtpyInstanceDungeon`, "
             "`ZoneRingPacketFindInstanceDungeon`, `ZoneRingPacketFindJobDungeon`); document the request, how the ring forwards it "
             "(`ZONERINGLINKAGESTART`, zcs_Send) and the Success/Failure callbacks on the originating zone.",
             "`MapClusterManager::ClusterManager` (`g_MapClusterMgr` DAT_0d742b30) and `MapCluster`: how instances are created "
             "(cm_FindEmpty / FindEmptyByRegnum / FindNotFull / AddTutorialMapCluster), the owner key `{category, regnum}`, "
             "`mc_ChangeCategory` (FUN_00485210, raid creation), `mc_DeleteInstanceDungeon` and the `DeleteDungeon` visitor, "
             "`mc_Routine` (empty-instance timeout, limit time `mc_GetLimitTime`, limit items `mc_SetLimitItem`), films "
             "(`mc_PlayAllFilm`, `mc_AllDropFilm`), `FUN_00486d80` (find-or-create used by the IDGate path), job dungeons "
             "(`so_ply_2JobDungeon`, `so_ply_FindJobDungeon`). Settle Z08's inference that map data type 3 = instance.",
             "The instance-dungeon data rows read by `IDInfo_Find` FUN_00484470 (fields +0x15…+0x6d, Z08 §5.1): which file and "
             "loader, column names (PDB row struct if one exists, `docs/knowledge/Z01.md` last section), and the Indun level table "
             "`g_IndunLevelData` DAT_0d026c30.",
             "Raid internals: the shared `Raid` record (FUN_0063d…/FUN_0063e…, compare the WM's `Raid` class in W02), `RaidTask` "
             "(`g_RaidTask` DAT_14d50830) and the raid status senders FUN_005cd8f0, FUN_005cd9c0, FUN_005cda50, FUN_005cdb50, "
             "FUN_005cdc00, FUN_005cd5a0 (0xB020…0xB026 to the client; check the client handlers).",
             "Guild academy reward storage: `so_ply_GuildAcademyRewardStorageRewardZoneRng` FUN_0046e750 (0x986C body), the storage "
             "close FUN_0046f7f0, withdraw grade vt 0x870 FUN_0046dea0; and the guild storage record `g_GuildStorage` "
             "(FUN_004751f0, FUN_00474970) behind the 0x7493 ring handler.",
             "Check Z08-B9 (level-select flag left set) and Z08-B5 against the eject path once the cluster lookup is understood."],
      done="Every handler in the scope table and the two extra ring handlers documented; the cluster manager lifecycle "
           "(create, own, change owner, timeout, delete) written as pseudocode; raid status packets have layouts."),
 dict(id="Z15", phase=2, title="Zone: quest script engine (added by Z08)",
      out="docs/pseudocode/zone/Z15-quest-engine.md", deps=["Z08"], scope=[],
      goal="Z08 §3 documented the quest packets and DB answers and listed the script commands by number, but not the "
           "engine that runs them. Reconstruct the quest data, the script interpreter and the reward path well enough that a "
           "rebuild can run the original quest scripts.",
      steps=["Read `docs/pseudocode/zone/Z08-content.md` §3 and §15 first. The 2017 PDB has the shared quest library "
             "(`CQuest`, `CQuestData`, `STRUCT_QSC` and its `Data` union, `QUEST_SCRIPT_COMMAND`, `PLAYER_QUEST_INFO`, "
             "`PLAYER_QUEST_DATA`); the client runs the same library, so compare the client functions (`pdb.py publics 'CQuest'`).",
             "Quest data: which file the zone loads (Z01 §2.3 loader list), the row layout read through `QuestData_Find` "
             "FUN_00635ff0 (fields Z08 used: +0x12 repeatable, +0x19/+0x1d/+0x1e/+0x20/+0x58/+0x5e start/end NPC flags), "
             "and how a quest's script is stored and found (`QuestScriptRun` FUN_005c0080, runner at CQuestZone+0xb8, "
             "`QuestScript_Next` FUN_006387f0).",
             "The interpreter: every `QUEST_SCRIPT_COMMAND` with its `Data` fields: IF/GOTO/MARK/SET/ADD/SUB and the script "
             "variables (CQuestZone+0xd0…), the GET_PLAYER_* getters (quest vt 0x64…0x78), SET/RESET/IS_ABSTATE, GET_ITEM_LOT, "
             "SCENARIO (`QuestPlayer_ScenarioRun` / `ScenarioDone_Server`, 0x440C), CALLPS (`PsStart` / `PsEnd`).",
             "Conditions and diary updates: FUN_0062fee0 (accept), FUN_006300d0 (done), FUN_00630570 (select start), "
             "FUN_006304d0 (give up), FUN_006304a0 (status), FUN_0062f3b0/4b0/550/5b0/680 and FUN_006302b0 (status changes), "
             "the 40-entry limit, daily/weekly/monthly/yearly repeat and the reset times of 0x441C.",
             "Rewards: `QuestCheckReward`, `QuestCheckSelectReward`, `QuestCheckRewardInven`, `QuestTakeReward` FUN_005bbe60 "
             "and the 0x441A NC_QUEST_DB_DONE_REQ body (money, exp, fame, character-title element, item creates, inventory lock "
             "`icl_QuestReward` / `InvenCellReleaser_QuestReward`).",
             "Other entry points: NPC click (`QuestPlayer_NPCClick` / `NPCClickCheck`, from Z02's NPC menu path), mob kill "
             "(`QuestActionMobKill`, `QuestPlayer_NPCMobKill`, `ShineQuestDiary_sqd_MobDead`, 0x440D NOTIFY_MOB_KILL), party "
             "quest checks (`PartyManufacture_pm_QuestCheck_*`), quest items (`sp_QuestItemGet`, `IsQuestDropItem`), the GM "
             "commands `&queststart`, `&questread`, `&questcomplete`, `&questrecieve`, `&questgiveup` (Z11 lists them).",
             "Settle Z08-B6 (silent give-up refusal) and give the meaning of every quest error number 0xB41…0xC10."],
      done="Every script command and every condition function documented; quest data file and row layout named; the "
           "reward path from DONE to 0x441B written as pseudocode."),
 dict(id="Z16", phase=2, title="Zone: kingdom quest element and guild tournament system (added by Z08)",
      out="docs/pseudocode/zone/Z16-events.md", deps=["Z08"], scope=[],
      goal="Z08 §4 and §8 documented the kingdom-quest (KQ) and guild-tournament packets. The per-event state behind them "
           "(KQ element, players, scores, rewards; the tournament system attached to a map) is not reconstructed.",
      steps=["Read `docs/pseudocode/zone/Z08-content.md` §4, §8 and §15 and `docs/knowledge/Z08.md` first. Map scripts "
             "themselves (ScenarioBookShelf, `PineEventScriptNode::*`) belong to Z09; document here only the KQ/GT objects "
             "they call.",
             "KQ: `KingdomQuest::KQElement` (`kqe_QuestStart`, `kqe_ReviveNumber`, `kqe_SetLimitTime`), `KQPlayerInfoList` "
             "(add/remove, knock-down counters, `kqpil_PlayerInformFunc`), `KingdomQuestContainer` (`g_KingdomQuests`, "
             "`kqc_MapUseCheck`), `KQContribute::KQContributeList` (`g_KQContribute`: `kqcl_NewKQ`, `kqpl_EndOfKQ`, how scores "
             "are counted), the end of a KQ and the reward request `0x5815 NC_KQ_REWARD_REQ` (who sends it: `cQuestResult`, "
             "`cQuestResult_Individual`, `PineEventScriptNode::ShineQuestResult`, `cEndOfKingdomQuest`), the KQ client packets "
             "sent during the event (grep `= 0x58` sends in the zone export), and the GM commands `&kingdomquest` / "
             "`&EndOfKingdomQuest` / `&Reroadkingdomquest`.",
             "Guild tournament: `FieldMap_fm_GetGuildTournamentSystem` and the GT system class (flag capture end callback "
             "FUN_00477c00, `FUN_00479510` flag check, guild skills `FUN_0047b9a0`, dice game `FUN_0047af20`, observers "
             "FUN_004788c0, member grades FUN_0047ccd0), the seed table DAT_0d55a3e0 / DAT_0d55a860, "
             "`wms_GuildTournamantStart`, `so_ply_Summon2GuildTournament` FUN_00478750, the join check FUN_00476860 "
             "(0x74E3 → 0x74E5), the match end and result reporting to the WM (W03 has the WM side), and the client packets "
             "0x74xx sent during a match.",
             "Settle Z08-B12 (seed bound 33 vs 32) and the 0x1A41/0x1A42 mode-vs-location order of 0x74AC (read the assembly)."],
      done="KQ lifecycle (make → start → pull-in → play → end → reward) and guild tournament match lifecycle written as "
           "pseudocode; every client packet sent during either event has a layout."),
 dict(id="Z17", phase=2, title="Zone: item actions and costume weapon/shield charges (added by Z06)",
      out="docs/pseudocode/zone/Z17-item-actions.md", deps=["Z03", "Z04"], scope=[],
      goal="Z03 pointed the item-action system and the costume weapon/shield charges to Z06, but they are item and combat "
           "effects, not trade or gambling, and no item covers them: what an item action is (condition → effect), when it "
           "fires, its cooldowns, and how costume charges are spent and refilled.",
      steps=["Read `docs/knowledge/Z03.md` / `Z04.md` first and the parts of `docs/pseudocode/zone/Z03-combat.md` / "
             "`Z04-items.md` you touch (abstates, skills, item use and equipment are documented there; cite them, do not redo "
             "them). Known so far: Z04 calls the item-action container on equip (FUN_005d1f20, condition {8,1,10,0}); Z03 "
             "says item actions feed hit/crit/shield rates; D02 loads/saves the cool times (`0x10CF`, "
             "`usp_Character_getItemActionCoolTime` / `setItemActionCoolTime`); C02 lists the PDB vs SHN column differences.",
             "Item actions: the tables `ItemAction*.shn`, `ItemActionCondition`, `ItemActionEffect` (loaders "
             "FUN_005b59c0…FUN_005b5d80), the player's item-action cooldown container (player `vt 0x5d0`), what triggers a "
             "check (item use, equip, hit, …), each condition and effect type, and any packet sent to the client.",
             "Costume weapon/shield charges: `sp_CostumWeaponChargeDecrease_*`, `WeaponChargeOk` FUN_00562160, where a charge "
             "is spent, what happens at 0, how charges are refilled, and the packets and ITEMDB requests involved (Z05 has the "
             "DB side)."],
      done="Item-action lifecycle (load → trigger → condition → effect → cooldown) and costume charge lifecycle written as "
           "pseudocode; every packet either sends has a layout."),
 dict(id="Z18", phase=2, title="Zone: leftovers of finished zone items from Z09's coverage boundary (added by Z09)",
      out="docs/pseudocode/zone/Z18-leftovers.md", deps=["Z01", "Z02", "Z03", "Z04", "Z06", "Z07", "Z09"], scope=[],
      goal="Z09's coverage boundary (`docs/pseudocode/zone/Z09-world.md` §31) assigns 221 zone functions and two packets to "
           "Z01, Z02, Z03, Z04, Z06 and Z07, whose plans include them, but those items were already done, so their own gap "
           "lists will never pick them up. Document them in one output, one section per owner, so that every one is cited "
           "as `FUN_…` in a zone doc (that is what `coverage.py` counts) and its behaviour is described at the owner's depth.",
      steps=["**The list:** `docs/knowledge/Z09.md` §3 (table: owner, count, the Z09 §31 rows to take, extras). Read those "
             "rows with `python3 -I tools/protocol-re/sect.py docs/pseudocode/zone/Z09-world.md 31.2` (and `31.3`, `31.5`); "
             "their addresses are written **without** `FUN_` on purpose. Sizes (decompiled lines, extras included): Z01 74 "
             "functions ~2.0k, Z02 29 ~1.0k, Z03 53 + 7 helpers + 0x2442 / 0x2443 ~2.8k, Z04 49 + 3 ~2.2k, Z06 7 ~0.1k, "
             "Z07 10 ~0.6k. Suggested parts: 1 = Z01 + Z06, 2 = Z03, 3 = Z04, 4 = Z02 + Z07, then sweep and review.",
             "**Per owner section:** first read the owner's knowledge file and the sections of its output that call or are "
             "called by these functions (`sect.py`), so each block says where it plugs in (link `Z0x §n`) instead of "
             "re-deriving context. Read the code in the PDB export (`clean.py re-data/exports/zone-pdb - <addr> …`, official "
             "names, *(pdb2016)*), several functions per call; group trivial ones (accessors, ctors / dtors, `BinaryDataBox` "
             "readers, STL-like wrappers) in one table row each with what they do, and write pseudocode blocks for the ones "
             "with logic. Do not edit the owners' files: corrections of their text go into `docs/knowledge/Z18.md` "
             "\"Corrections\" (for X01), one row each (owner, place, old statement, correction, evidence).",
             "**Packets and open points:** Z03 section: 0x2442 NC_BAT_SOMEONESKILLBASH_OBJ_CAST_CMD and 0x2443 "
             "NC_BAT_SOMEONESKILLBASH_FLD_CAST_CMD (sender `ShineMobileObject::smo_SkillBash_Blast_Trap`; layout with the 2016 "
             "PDB struct, receivers, client handler from `opcodes.json` / C01) and the \"Skill-side helpers\" open points of "
             "Z09 §31.5 (answer each or say why it stays open). Z04 section: Z09 §31.5 \"Items\" (`ItemAttr` class vt 0x2c "
             "group row → lot / upgrade, `so_ply_EquipmentChange` and the view slots, `sp_DestroyItem` overloads). Z07 "
             "section: `CCharacterTitleZone::CheckNewTitle`. Every client-facing packet gets its client handler and error codes "
             "resolved through `docs/protocol/client-error-codes.json`; verified layouts go into `docs/protocol/annotations/Z18.json`.",
             "**Coverage (no scope table, so `coverage.py Z18` does not apply):** (a) every address of the Z09 §3 rows is cited "
             "as `FUN_…` in the output (check with a scratch script over the §31 rows); (b) depth-1 gap check as Z09 §31.1 "
             "describes (roots = every `FUN_` of the output, `coverage.py`'s `Bin` and TINY / HUB / registered filters, "
             "\"covered\" = cited in a pseudocode doc): each callee found is documented here when it belongs to Z01–Z07, or "
             "listed in the \"Coverage boundary\" with its owner's plan line (items not started yet keep it through their own "
             "gap lists; write those addresses without `FUN_`). Record the before / after counts in the status file.",
             "Bugs as `Z18-B<n>` (owner named in the row). Do not re-document anything the owners or Z09 already describe "
             "(Z09 §28.12 / §28.13 took the small leftovers of Z01 / Z05 / Z07 / Z08)."],
      done="All 221 functions of `docs/knowledge/Z09.md` §3 are cited as `FUN_…` and described, the packets 0x2442 / 0x2443 have "
           "layouts and client handlers, every Z09 §31.5 open point of these owners is answered or argued open, and the "
           "depth-1 gap check of the output lists only functions with an owner whose plan line includes them."),
 dict(id="Z19", phase=2, title="Shared config-script reader CCsl and the server config file format (all servers; added by Z10)",
      out="docs/pseudocode/zone/Z19-config-script.md", deps=["Z01"], scope=[],
      goal="Every 2016 server reads its `*ServerInfo.txt` (and the shared `9Data/ServerInfo/ServerInfo.txt` it includes) "
           "through the same `CCsl` library (29–30 functions per binary, ~1.5k decompiled lines in the zone), which no item "
           "documents: Z10 §1.1 / §6.5 only cover the `CServerInfo` lookups on top of it. Reconstruct the file format and the "
           "parser so a rebuild can read the original config files unchanged.",
      steps=["Read `docs/pseudocode/zone/Z10-certification.md` §1.1 and §6.5 (the `CServerInfo` lookups, CSL `dwID` = index of "
             "the `#DEFINE`, SERVER_INFO fields) and `docs/knowledge/Z10.md` first.",
             "Zone copy, PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `CCsl::ReadScript` 00652500, `Read` 00651540, "
             "`ReadScriptDone` 00651330, `ProcCmd` 00652000 (`#DEFINE` / `#ENDDEFINE` / `#INCLUDE` / `#END` …), `IncludeFile` "
             "00651ea0, `ProcRemark` 00650aa0, `MakeFormat` 00650cb0 / `AddFormat` 00650f60 (type tokens `<STRING>`, `<INTEGER>`, …, "
             "`m_pCslParameterSize`), `MakeData` 00651050 / `ProcData` 006512a0 / `GetDataToken` 00650fa0 (row parsing, quoting, "
             "separators), `MakeFormatTable` 00650780 / `MakeDataTable` 00650800, `GetFormat` 00650900, `AddResultMsg` 00650880 "
             "(error messages), `WriteFormat` 00651780 / `WriteData` 006518a0, the clear / ctor / dtor functions. The accessors "
             "`GetNumDatas` / `GetDataInfo` / `GetData` are already in Z10 §6.5 / §11: cite, do not redo.",
             "Format spec: comment syntax, every directive, every parameter type and its stored size, string limits, include "
             "path resolution (relative to what), what an unknown row name or a wrong field count does, error reporting (the "
             "`0x401` flags of `ReadServerInfo`). Test the spec against every `*ServerInfo.txt` and `ServerInfo.txt` in "
             "`Files/Server/2016` (a short Python reader in the doc, run on them).",
             "Other servers: confirm Login, WM, Account, AccountLog use the same functions (names in `re-data/exports/<bin>-pdb`, "
             "compare sizes / a diff of 3–4 functions); Character and GameLog (no PDB): find the copy by its strings. Record "
             "differences, if any; list which config files each server reads with it.",
             "Bugs as `Z19-B<n>`; Coverage boundary as usual."],
      done="The config file format is specified (directives, types, limits, errors) with a reader tested on every 2016 config "
           "file, every `CCsl` function of the zone is cited as `FUN_…`, and the other servers' copies are confirmed or their "
           "differences recorded."),
 dict(id="Z20", phase=2, title="Zone: skill data box loader (SkillDataBox / PassiveDataBox, SkillDataIndex build; added by Z11)",
      out="docs/pseudocode/zone/Z20-skill-data.md", deps=["Z01", "Z03"], scope=[],
      goal="The zone builds one `SkillDataBox::SkillDataIndex` per active skill from five SHN tables (ActiveSkill, "
           "ActiveSkillInfoServer, ActiveSkillGroup, ToggleSkill, AreaSkill; Z01 §2.3 row FUN_00585f40) and the passive "
           "skills in `PassiveDataBox`. Z03 uses the rows (`docs/knowledge/Z03.md` SkillEntry) and Z11 §8.6 shows that "
           "`&reloaddata ActiveSkill` re-runs the loader at run time, but no item documents how the index is built: "
           "`sdb_Load` alone is ~1.1k decompiled lines. Reconstruct it so a rebuild can load the original tables unchanged.",
      steps=["Read `docs/pseudocode/zone/Z01-core.md` §2.3 (loader table), `docs/knowledge/Z03.md` (SkillEntry offsets), "
             "`docs/pseudocode/zone/Z03-combat.md` (who reads `SkillDataIndex` members), Z11 §8.6 (`&reloaddata`, bug Z11-B37) and "
             "Z10's loader stage list (`docs/pseudocode/zone/Z10-certification.md`, `sdb_Load` FUN_00585f40) first.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `SkillDataBox::sdb_Load` 00585f40 (files, order, "
             "`sdb_ValidArray` / `sdb_MaxValid`, `skillnametree`, sorting `sdb_compare` 005844e0, the area-skill vector), "
             "`SkillDataIndex::sdi_SetArgument` 00584800 and `sdi_Clear` 00584500 (which SHN columns become which "
             "`EnumStruct {exist, value}` / special-value members), the ctor / dtor 00447e30 / 00447e50, the `sdb_BinData` "
             "ctor / dtor 00585520 / 00585680, `BinaryDataBox<ActiveSkillInfo|ActiveSkillInfoServer|AreaSkill|ToggleSkill|"
             "CollectCardMobGroup>::bdb_ReadData` 00585030 / 00584f70 / 005850f0 / 005851b0 / 00648d50 (header check, "
             "\"readfail\" path), `_DebugMessageNew2` 0064f1f0 (the error message helper they call), `GetSkillIndexByName` "
             "00585ef0, `sdb_GetAreaSkillInfo` 00585730, `sdb_SpecSkillStruct` 0046a410; `PassiveDataBox` ctor 00585790, "
             "`pdb_Load` 005858d0, `sdb_GetSetAbstate` 00584f20, `sdb_SpecSkillStruct` 0059ebe0.",
             "Row structs: the 2016 PDB types (`pdb.py Files/Server/NA2016/Zone00/Zone.pdb types '^(ActiveSkillInfo|"
             "ActiveSkillInfoServer|AreaSkill|ToggleSkill|PassiveSkillInfo)$'`) against `docs/knowledge/S01-shn-structs.tsv` and "
             "the `shn.py` column names of each file; record the column → member map.",
             "Invariants a rebuild needs: id ranges, missing or duplicate rows, rows dropped by the loader, what lookups return "
             "for an unknown id (default blocks), and which other objects keep `SkillDataIndex*` (settles Z11-B37's holder list).",
             "Bugs as `Z20-B<n>`; Coverage boundary as usual."],
      done="`sdb_Load`, `sdi_SetArgument`, `sdi_Clear` and `pdb_Load` are written as pseudocode with a column → member map for "
           "every skill table, and every SkillDataBox / PassiveDataBox function of the zone is cited as `FUN_…`."),
 dict(id="Z21", phase=2, title="Zone: set items (SetItem / SetItemEffect / SetEffect tables, set detection, set-item abstates and skill effects; added by Z12)",
      out="docs/pseudocode/zone/Z21-set-items.md", deps=["Z03", "Z12"], scope=[],
      goal="Wearing several pieces of an item set grants extra stats, abnormal states, item actions and skill bonuses. "
           "Z12 §2.5 documents only how the set-item abstate refits the stat matrix (`siae_ParameterRefit`) and Z03 only "
           "reads the resulting skill bonuses (`g_SetEffect`), but no item documents how the zone detects a set, which "
           "tables define it and what is stored, saved and restored (about 900 decompiled lines, ~30 functions in "
           "`SetItemData::*`). Reconstruct the subsystem so a rebuild can load the original tables unchanged.",
      steps=["Read `docs/pseudocode/zone/Z12-stats.md` §2.5 (`siae_ParameterRefit` FUN_005108c0, bug Z12-B3, the ≥ 1000 "
             "`eb_Index` codes) and §6.4 (`siae_SetItemEffectRestore` at login), `docs/pseudocode/zone/Z03-combat.md` (every "
             "`g_SetEffect` DAT_1325edb0 reader, `smo_ply_SetItemEffect` vt 0xef8) and the Z01 / Z10 loader tables for "
             "`SetItem.shn`, `SetItemEffect.shn`, `SetEffect.shn` first.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `sp_SetItemCheck` 00510b50, "
             "`SetItemClassifier::sic_SetItemDefine` 00510370, `SetItemEffectList::siel_AppendEffect` 005104c0, "
             "`aeo_SetItemEffectStore` 00510670, `aeo_SetItemActionEffect` 00510810, `aeo_FillSetItemEffect` 004534f0, "
             "`SetItemAbstateEffect::siae_*` 00510030…00510350, `EffectDescription` / `EffectByPiece` 00510200…00510240 and "
             "`ed_Compare` 004a2ed0, `SkillEffect::se_Clear` 005105e0 / `operator[]` 00510010, "
             "`ShineMobileObject::smo_ply_SetItemEffect` 00510c80 and `ShinePlayer::smo_ply_SetItemEffect` 00510d20, "
             "`SetEffectTable` (ctor 005b1ec0, `Table::Load<SetEffectTable>` 005b5ec0, `ITableBase::Load` 005b35b0, "
             "`FindActionID` 005c7eb0), `Send_SETITEMHEALEFFECT` 005cfbb0 / `RecoverTypeEffect::_execute` 005cfc70, and the "
             "item-action hooks that add / remove set action ids (`icr_Apply` 0048ca20 / 0048cc60, "
             "`so_ply_ItemAction_UnEquip` 00565020, `sp_ItemActionSetup` 00566420; strings \"Setitem Can`t Add ActionID\").",
             "Row structs from the 2016 PDB against `docs/knowledge/S01-shn-structs.tsv` and `shn.py` of the three tables; record "
             "the column → member map and the piece-count rules (which pieces count, duplicates, costume / KQ items).",
             "Packets: the set-item heal effect and any client notification (client handlers via `re-data/client-handlers.json`), "
             "how the set abstate is saved (`p_Char_SetStateWithSetItemAndRestTime`, D02) and restored at login.",
             "Overlap with Z18: Z09 §31.2's \"Items, equipment, set items, random options\" row (owner Z04, taken by Z18 per "
             "`docs/knowledge/Z09.md` §3) also lists `Send_SETITEMHEALEFFECT` 005cfbb0, `SkillEffect::operator[]` 00510010, "
             "`se_Clear` 005105e0, the `SetItemAbstateEffect` ctor 00510350 and `ed_Compare` 004a2ed0. Check Z18's status and "
             "output first: if it already documents them, cite its § and add only the set-item context; otherwise document "
             "them here (Z21 owns the set-item subsystem) and say so in `docs/knowledge/Z21.md` so Z18 can cite Z21.",
             "Bugs as `Z21-B<n>`; Coverage boundary as usual."],
      done="Set detection, every `SetItemData::*` function and the three table loaders are written as pseudocode with their "
           "column → member maps, and every set-item function of the zone is cited as `FUN_…`."),
 dict(id="Z22", phase=2, title="Zone: abnormal-state actor classes (SubAbnormalStateActor* bodies: DoT/HoT, area damage, bomb, detach, rate buffs; added by Z12)",
      out="docs/pseudocode/zone/Z22-abstate-actors.md", deps=["Z03", "Z18"], scope=[],
      goal="Every abnormal state runs its effect through `AbnormalStateContainer::SubAbnormalStateActor*` objects (one class "
           "per `SubAbstateAction` kind). Z03 §6 documents the abstate container, the SubState → actor table and the "
           "matrix enchant, but lists the individual actor bodies as not reconstructed (`docs/pseudocode/zone/Z03-combat.md` "
           "'Not reconstructed', 'Abnormal states'); Z12 and Z18 only touch a few (`sasa_GetDamage` of Poison, bomb DoT "
           "damage for Z12-B7). 70 actor functions (~2.9k decompiled lines), 55 of them (~1.9k) cited by no doc. "
           "Reconstruct each actor's attach / routine / detach / apply so a rebuild reproduces every abstate effect.",
      steps=["Read `docs/pseudocode/zone/Z03-combat.md` §6 (abstate container, SubState → actor table, `asl_Routine`) and its "
             "'Not reconstructed' bullet, `docs/pseudocode/zone/Z12-stats.md` §2.5 (`aeo_ParameterEnchant`, which actions "
             "write the matrix) and §4.1 (B6 / B7, free-stat DoT slots), and Z18's output for the actor functions it took "
             "from Z09 §31 (do not redo them).",
             "List every `AbnormalStateContainer::SubAbnormalStateActor*` function in `re-data/exports/zone-pdb/decomp.c` "
             "(`//==== FUNC` lines) with its vftable (`tools/protocol-re/rtti.py`), and read them per class with "
             "`clean.py re-data/exports/zone-pdb - <addr> …`. Largest first: AreaDamage `sasa_Routine` 0040d640, DmgState "
             "`sasa_Routine` 0040dc60, DetachProcess `sasa_DetachObject` 0040c1c0, Bomb `sasa_ApplyAbstate` 0040c640 (with "
             "`sasa_SetAbstateToArea_TargetNum` 0040b670 and `AxialListNearScanEnemyorAll` 004c1830), Poison "
             "`sasa_GetDamage` 0040b360, DropUpRate / ExpUpRate `sasa_DetachObject` 00409230 / 00408f90.",
             "Per actor: the `SubAbState.shn` columns it reads (`AbStateStrArgument`), timers (`aeo_Tick`), the packets it "
             "sends (damage / heal / state broadcasts, with layouts and client handlers via `re-data/client-handlers.json`), "
             "and the objects it touches (caster lookup `aeo_GetCaster`, area scans).",
             "Bugs as `Z22-B<n>`; Coverage boundary as usual."],
      done="Every `SubAbnormalStateActor*` function of the zone is cited as `FUN_…` and described, with the SHN columns, "
           "timers and packets of each actor class."),
 dict(id="Z23", phase=2, title="Zone: per-player active skill list (CharaterSkillList / MoverSkillList: toggle skills, "
                               "cooldowns and delay groups, empower, mastery, skill buffers; added by Z20)",
      out="docs/pseudocode/zone/Z23-skill-list.md", deps=["Z03", "Z20"], scope=[],
      goal="Z03 documents the skill cast path and Z20 the skill tables, but about 1.4k decompiled lines of the per-player "
           "skill list are cited by no doc: the toggle skills (`ToggleSkill.shn` rows in `SkillDataIndex::sdi_ToggleData`, "
           "0x245C NC_BAT_TOGGLESKILL_ON_CMD / 0x245D NC_BAT_TOGGLESKILL_OFF_CMD; Z03 only names them), cooldowns and "
           "shared delay groups, empower points, mastery, learn/unlearn and the client/server skill buffers. Document them so "
           "a rebuild keeps the same cooldown, toggle and empower rules.",
      steps=["Read `docs/pseudocode/zone/Z20-skill-data.md` §1.3 (`SkillDataIndex` members: `sdi_ToggleData`, "
             "`sdi_ActiveSkillGroups`, delay group), §2.2 (ToggleSkill / ActiveSkillGroup columns), §5.2 (`skillnametree`, "
             "`csl_Learn`) and §7 (the list keeps skill IDs, not pointers); Z03 §5 (cast path: `csl_SPCheck`, "
             "`csl_Toggle_CanUseSkill`, `csl_EmpowerAlloc`, `csl_CoolTimeCheck`) and Z09's `csl_Toggle_CheckOnOff`; W03 / W04 "
             "for `csl_Store` / `csl_FillSaveBuffer`. Do not redo those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`), all uncited so far: toggle "
             "`csl_Toggle_CanUseSkill_WeaponType` 00444bd0, `csl_Toggle_GetToggleSkill` 00445680, `csl_Toggle_IsOn` 004456c0, "
             "`csl_Toggle_Store` 00448c60, `csl_Toggle_SetOnOff` 00448ce0, `ShinePlayer::so_ply_ToggleSkill_IsOn / _On / _Off "
             "/ _AllOff` 005794f0 / 00579500 / 005795d0 / 00579670 (vtable slots 0xbc4 / 0xbc8 / 0xbcc, Z03 §5); cooldown "
             "`csl_UpdateCoolTime` 004468c0, `csl_GetDelayGroup` 00448950, `csl_SetCoolTime` 00448ab0 (0x4821 "
             "NC_SKILL_COOLTIME_CMD), `csl_DmgCoolTimeDown` 00449080, `MoverSkillList::msl_UpdateCoolTime` 00446370, "
             "`msl_CoolTimeCheck` 004463d0, `msl_SetCoolTime` 00449270; empower `csl_EmpowerClear` 00445190, "
             "`csl_EmpowerStruct` 004482c0; `csl_AddMastery` 00446730; `csl_FillSendBuffer_Server` 00445260 / "
             "`_Client` 00445460; `csl_CheckDefSkill` 00447fb0, `csl_MaximumSkill` 00448240, `csl_PreProduceCheck` 0046ab70, "
             "`csl_UnLearn` 0057e930; the Z03 leftovers reached from `smo_SkillBlast` / `smo_SkillBash_Blast`: "
             "`ShineMobileObject::smo_Dispel` 0057d8e0, `smo_ClearSkillResultBuffer_Miss` 0057a550, "
             "`AbstateElementInObject::aeo_IsMine` 00408880; the mount skill users `ShineMover::so_smv_SkillBash_Location` "
             "00580cf0 and `ShineMover::so_ply_CanMyTarget` 004ae450 (the other `so_*_CanMyTarget` / `so_smv_SkillBash_Object` "
             "are cited already).",
             "Packets: 0x245C / 0x245D, 0x4821 and the mastery send of `csl_AddMastery` (layouts with the 2016 PDB structs, "
             "client handlers via C01 / `opcodes.json`).",
             "Then every caller of these functions (vtable slots included) until what remains is Z03 / Z12 / Z20.",
             "Bugs as `Z23-B<n>`; Coverage boundary as usual."],
      done="Every function listed above is cited as `FUN_…` with pseudocode, the toggle on/off rules (condition, weapon check, "
           "abstates, packets) and the cooldown / delay-group rules are specified, and the packets have layouts and client "
           "handlers."),
 dict(id="Z24", phase=2, title="Zone: item-side data loaders (UsedItemEffect, ItemUseFunction, ChargedItemEffectDataBox, "
                               "MoverDataBox, cStateItemDataBox, MysteryVaultTable, RidePetDataBox) and CharClassDataBox (added by Z20)",
      out="docs/pseudocode/zone/Z24-item-data.md", deps=["Z01", "Z04", "Z20"], scope=[],
      goal="Z01 §2.3 lists these loaders in one table row each and Z20 §7 shows that they store `SkillDataIndex*` "
           "(the use-effect table that dangles after `&reloaddata ActiveSkill`), but no item documents how they build their "
           "tables (about 2k decompiled lines): which SHN / text files, columns, lookups, fatal checks and invariants. Z04 "
           "(done) also left the class-to-class-type helpers of NC_ITEM_CLASS_CHANGE_REQ uncited. Document them so a rebuild "
           "can load the original files unchanged.",
      steps=["Read `docs/pseudocode/zone/Z01-core.md` §2.3 (loader table and stages), Z10 (`docs/pseudocode/zone/"
             "Z10-certification.md`, loader stage list and its read-dependencies), Z20 §2.1 (the `BinaryDataBox<T>::bdb_ReadData` "
             "template and its bug Z20-B1) and §7 (holder table), Z04 for the item handlers that use these tables. Do not redo "
             "those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `UseEffect::UsedItemEffect::uie_Load` 0059cc30, "
             "`uie_SetChargedBuffer` 005963e0, `uie_BroadCast` 005963c0, `uie_UseSkillID` 0059cba0 (Z20 §5.2); "
             "`ChargedItemEffectDataBox<RIDING|ChargedItemEffect|MiniHouse|MiniHouseFurniture>::cideb_Load` 00450070 / 005af300 / "
             "005af4d0 / 005af6d0 and accessors `cideb_Next` 0044f9e0 / 00570cf0, `cideb_GetIndex` 0045e0b0, `cideb_GetItem` "
             "00570d40, `cideb_Get` 00570d20; `RidePetDataBox::rpdb_Load` 00450270; `ItemUseFunction::iuf_Load` 0049b770; "
             "`MoverDataBox::mvdb_Load` 004bf960, `~MoverDataBoxIndex` 004bf920; `cStateItemDataBox::sidb_Load` 0058c920, "
             "`sidb_GetElement` 0058c190 (+ vector helpers 0058c850 / 0058c560 / 0058c480, folded dtor 005d49c0); "
             "`MysteryVaultTable::DataProcess` 005c8590 (+ 005c8520, `GetTotal` 005c83b0); the readers "
             "`BinaryDataBox<MoverMain|MoverAbility|MoverHG|MoverItem|ChargedItemEffect|MiniHouse|MiniHouseFurniture|RIDING|"
             "ItemUseEffect|StateItem|GatherInfo>::bdb_ReadData` 004bf320 / 004bf3e0 / 004bf4a0 / 004bf560 / 005ae790 / "
             "005ae840 / 005ae8f0 / 0044fd50 / 00596b20 / 0058bfe0 / 0046a4a0 (file, key, row size; same template as Z20 §2.1); "
             "`CharClassDataBox::ccdb_ClassToUseClassType` 00640c20, `ccdb_BitToClass` 00640b90, `ccdb_ClassToBit` 00640850 "
             "(from `sp_NC_ITEM_CLASS_CHANGE_REQ` 0051f5c0 / `sp_OpenClassChangeMenu` 0051fd10); "
             "`GatherProduce::RecipeBook::operator[]` 00444b50; `ItemDataBox::ReadData` 006494f0 (the `idb_btree` name "
             "index; `idb_Load` 00649780 is cited) and `ItemGroupClassifier::igc_Store` 004900f0.",
             "Row structs: the 2016 PDB types against `docs/knowledge/S01-shn-structs.tsv` and `shn.py`; record the column → "
             "member map of every file, and the 2016 data invariants (id ranges, duplicates, rows dropped).",
             "Bugs as `Z24-B<n>`; Coverage boundary as usual."],
      done="Every function listed above is cited as `FUN_…` with pseudocode, every file it loads has a column → member map, "
           "and the reload behaviour (which tables `&reloaddata` can rebuild, Z11 §8.6) is stated for each."),
 dict(id="Z25", phase=2, title="Zone: skill special effects (dispel / cure bodies, SkillSpecial handlers of smo_SkillBlast, reflection damage; added by Z17)",
      out="docs/pseudocode/zone/Z25-skill-specials.md", deps=["Z03", "Z22"], scope=[],
      goal="Z03 §5 summarises `smo_SkillBlast` (FUN_00581160, ~1000 decompiled lines) but lists its `SkillSpecial` handlers "
           "(mana burn, dispel variants, HP→SP, jump / dash, chain targets, steal enchant, summon, metamorphosis), "
           "`smo_Dispel` and `smo_ReflectionDamage` (0x245B) as only named (`docs/pseudocode/zone/Z03-combat.md` 'Not "
           "reconstructed', `smo_SkillBlast` bullet). Z17 §3.7 documents `smo_Dispel` FUN_0057d8e0 (the dispel mask) but "
           "not what the mask removes. No item covers these bodies. Reconstruct them so a rebuild reproduces every "
           "special skill effect.",
      steps=["Read `docs/pseudocode/zone/Z03-combat.md` §5 (skill cast and blast, `SkillEntry` layout §5.1, the special table "
             "+0xa0…+0x260) and its 'Not reconstructed' bullets, Z17 §3.7 (`smo_Dispel` mask bits), Z09's magic-field sections "
             "(already documented there, do not redo) and Z22's output for the abstate actors once it exists.",
             "Dispel / cure: `ShineMobileObject::so_Dispel` 0042bf70 (vt 0x5a8) and `so_SkillCure` 0042c440 (vt 0x5a4): which "
             "states each mask bit (2, 0x4 DEBUFF, 0x8 DISEASE, 0x10 POISON, 0x20 CURSE, 0x18 cure, 0x100 DEEPER, 0x200 DETECT, "
             "0x400 BOMBDISPELALL) removes (`DispelIndex` / `SubDispelIndex` of `AbState.shn`), the `so_MiscTable` vt 0x984 "
             "servant kill (Z09 §13.3 `mds_Dead.ByDebuff` row), and the packets / result flags.",
             "`smo_SkillBlast` 00581160: walk every `SkillSpecial` / `sdi_*` flag branch in order (read with `clean.py "
             "re-data/exports/zone-pdb - 581160`, PDB names), one pseudocode block per special with its SHN columns "
             "(`ActiveSkill.shn` / `ActiveSkillInfoServer.shn`), state changes, packets (layouts, client handlers via "
             "`re-data/client-handlers.json`, codes via `docs/protocol/client-error-codes.json`).",
             "`smo_ReflectionDamage` 0055dbc0 and packet 0x245B; any other function these reach that no doc cites.",
             "Bugs as `Z25-B<n>`; Coverage boundary as usual (no scope table: do the caller / callee check by hand)."],
      done="`so_Dispel`, `so_SkillCure`, `smo_ReflectionDamage` and every special-effect branch of `smo_SkillBlast` are "
           "described with their SHN columns, state changes and packets, each sent packet has a layout and client handler."),
 dict(id="Z26", phase=2, title="Zone: silver-wing teleport item (saved location, server menu, portal cast and blast; added by Z23)",
      out="docs/pseudocode/zone/Z26-silver-wing.md", deps=["Z02", "Z04", "Z23"], scope=[],
      goal="Z04 lists `UseItemSilverWing` only by address in its item-use table and Z23 §3.6 only its cooldown check; the "
           "flow in between is cited by no doc: the server menu the item opens, saving a location in the item, the "
           "portal cast and the blast that links the player. Document it so a rebuild keeps the same menu, checks, "
           "cooldown and link.",
      steps=["Read `docs/pseudocode/zone/Z04-items.md` §6 (item-use framework: `uib_CanUseItem` / `uib_DirectUse` / "
             "`uib_AfterCast` / `uib_Effect`, the table near line 580), Z02 (server menus: `sp_ServerMenuOpen`, "
             "`ServerMenuFuncter`), Z23 §3.2 / §3.6 (`csl_CoolTimeCheck`, `so_ply_SilverWingCoolTime`, bug Z23-B5) and the "
             "Z01 link path (`so_LinkTo`). Do not redo those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `UseItemSilverWing::uib_CanUseItem` 00598000, "
             "`uib_DirectUse` 0059c260, `uib_AfterCast` 0053ff70; `ShinePlayer::sp_SilverWingMenu` 0059c090 (menu strings "
             "SilverWingTitle / SilverWingPortal / SilverWingLocSet, the portal entry only when the item holds a location); "
             "the menu functors `ServerMenuFuncter::smfm_Silverwing_Portal` 0059bbe0, `smfm_Silverwing_LocSet` 0059bff0 and "
             "`smfm_Silverwing_Cancel` 0059bb30; `sp_SilverWing_PortalCast` 00597b30 (cast struct fill, cooldown check, error 0x70D); "
             "`sp_SilverWing_PortalBlast` 00597cf0 (map / position from the item attribute, vt 0x304 / 0x91c / 0x600: the "
             "link) and who calls it from the cast routine (`ShineMobileObject::so_Routine` FUN_0056a080 item branch, "
             "Z23 §3.6); `itemdatabox.idb_specialid.sii_silverwing`; the item attribute layout that stores the location "
             "and its DB update.",
             "Client: the menu packets and the portal effect (C01 handlers); error codes via `client-error-codes.json`.",
             "Bugs as `Z26-B<n>`; Coverage boundary as usual."],
      done="Every function listed above is cited as `FUN_…` with pseudocode, the saved-location format and the "
           "menu → cast → blast → link flow are specified, and every packet has a layout and client handler."),
 dict(id="Z27", phase=2, title="Zone: item table loader `ItemDataBox::idb_Load` (ItemInfo, ItemInfoServer, GradeItemOption, "
                               "ItemDropLog, ItemSort, CollectCardMobGroup, ItemMoney; special item IDs) (added by Z24)",
      out="docs/pseudocode/zone/Z27-item-table.md", deps=["Z01", "Z04", "Z24"], scope=[],
      goal="`ItemDataBox::idb_Load` FUN_00649780 (stage home, about 1036 decompiled lines) builds the zone's whole item "
           "index (`itemdatabox` 0x14d4fb90: `idb_index`, `idb_btree`, `idb_maxItemhandle`, the special item IDs) from seven "
           "SHN files, but no item documents it: Z04 §1.2 only uses the index, Z01 §2.3 lists it in one row, Z24 §7.3 covers "
           "only the dead stand-alone reader `ItemDataBox::ReadData`. Document it so a rebuild loads the original files "
           "unchanged and builds the same index.",
      steps=["Read Z24 §7.3 (`ItemDataBox` ctor FUN_0064b5d0, dead `ReadData` FUN_006494f0, accessors `idb_GetItemInxName` / "
             "`idb_iter_*`), Z04 §1.2 (index layout as the handlers use it), Z20 §2.1 (`BinaryDataBox<T>::bdb_ReadData` template), "
             "Z24 §1.3 (`uie_Load` reads `sii_*` special IDs such as `sii_JustReviveItem` / `sii_ImmediateDivorce`, bugs "
             "Z24-B1 / B2). Do not redo those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `ItemDataBox::idb_Load` 00649780, the readers "
             "`BinaryDataBox<ItemInfo>::bdb_ReadData` 00648a50 / `BinaryDataBox<ItemInfoServer>::bdb_ReadData` 00648b10 (and "
             "those of GradeItemOption, ItemDropLog, ItemSort, CollectCardMobGroup, ItemMoney reached from `idb_Load`), the "
             "`idb_BinData` ctor / dtor 00649280 / 00649420, `~ItemDataBox` 00649700, `idb_SpecialItems` 00418fe0 and every "
             "special-ID assignment (ItemFunc / class tests, fatal \"cannot find …\" checks; `idb_MakeSpecialID` is inlined "
             "or folded: find it from its strings).",
             "Per file: column → member map (2016 PDB row structs against `docs/knowledge/S01-shn-structs.tsv` and `shn.py`), "
             "how rows join ItemInfo (by ID or InxName), fatal checks, and the 2016 data invariants (id ranges, duplicate IDs / "
             "names, rows dropped, ItemInfoServer rows without ItemInfo and vice versa).",
             "Reload behaviour (Z11 §8.6: `&reloaddata` cannot rebuild it) and the consumers of each derived member (one line "
             "each, linking the items that read them). Bugs as `Z27-B<n>`; Coverage boundary as usual."],
      done="`idb_Load` and every reader / helper it calls are cited as `FUN_…` with pseudocode, every file it loads has a "
           "column → member map with its 2016 invariants, and every special item ID it sets is listed with its source."),
 dict(id="Z28", phase=2, title="Zone: collection-card data tables and card roll (CollectCard*.shn `SHND::CommonData` "
                               "loaders, `g_CardCollectMake`, album / bookmark loaders) (added by Z27)",
      out="docs/pseudocode/zone/Z28-card-tables.md", deps=["Z07", "Z09", "Z27"], scope=[],
      goal="Z07 §7 documents the card-collection packets but only names the six card tables; Z27 §2 documents the "
           "`CollectCardMobGroup` loader only. Nobody documents how the other tables are loaded and indexed, nor the card "
           "roll `g_CardCollectMake` that turns a dropped unidentified mob card into a card ID and star count. Document "
           "them so a rebuild loads the original files unchanged and rolls cards with the same odds.",
      steps=["Read Z07 §7 (card packets, `CollectCard` lookup FUN_00627e30, reward `ccr_Load` FUN_00629160), Z27 §2 "
             "(`CommonData<CollectCardMobGroup>` ctor / `cd_Load` / `cd_Find` FUN_00629700 / 005b7b10 / 00627ed0), Z20 §2.1 "
             "(`bdb_ReadData` template, identical-code folding). Do not redo those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): the static initialisers FUN_0069ba10 (CollectCard.shn), "
             "0069bac0 (StarRate), 0069bae0 (Reward), 0069bb00 (Title) and the DropRate one (string CollectCardDropRate.shn), "
             "the `SHND::CommonData<…>` / `IndexedCommonData<CollectCard>` `cd_Load` bodies (`CollectCard` 00629840 and the "
             "others reached from `ZoneServer_zs_start_long` FUN_005b8c00), their `cd_Find` variants (`CmpCardCollect`, "
             "`CmpCollectCard_MobGroup`, `CmpCollectCard_ItemIndex`, `CmpCollectCardStarRate`, …), "
             "`CardCollection::CardCollectionAlbum::cca_Load` FUN_006298c0, `CardCollectionBookmark::ccb_Load` FUN_00629a50.",
             "`g_CardCollectMake` FUN_00628880 (mob → MobGroup → cards of the group, cumulative DropRate roll with "
             "`rb_1000000`, then StarRate roll by card grade) and its caller `ItemAttrCls_CardCollect_Close::iac_DropItemMake` FUN_0063faf0 (the unidentified-card item "
             "attribute at drop); per file column → member map and 2016 invariants (shn.py), odds as numbers.",
             "Bugs as `Z28-B<n>`; Coverage boundary as usual."],
      done="Every loader / finder / initialiser above and `g_CardCollectMake` are cited as `FUN_…` with pseudocode, every "
           "card table has a column → member map with its 2016 invariants, and the card / star roll is specified."),
 dict(id="Z29", phase=2, title="Zone: party experience tables (`PartyBonusByMember.shn` / `PartyBonusLimit.shn` loaders "
                               "of `HitMeList::hml_Load` and their readers) (added by Z28)",
      out="docs/pseudocode/zone/Z29-exp-tables.md", deps=["Z03", "Z28"], scope=[],
      goal="Z03 §8.2 documents the experience split but says \"which loader fills which table was not traced\". Z28 §3.8 "
           "documents the level-handicap table (`lh4ed_Load`, `PartyBonusByLvDiff.shn`). The party bonus and the per-level "
           "group experience cap are still undocumented. Document them so a rebuild loads the original files unchanged "
           "and gives the same party experience.",
      steps=["Read Z03 §8.2 (`el_ExpDistribute` FUN_004828b0, `ExperienceDistribute::lid_Call` FUN_00483360, `ed_GiveExperience` "
             "FUN_00481890) and Z28 §3.8 (`lh4ed`). Do not redo those.",
             "PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`): `HitMeList::hml_Load` FUN_004824d0 (zs_start_yellow, "
             "Z10 §7.1), `PartyExperienceBonusDouble::pebd_Load` FUN_00481bf0 (PartyBonusByMember.shn: `PB_PartyMember` u8 → "
             "`pebd_Bonus[]` = ratio / 1000, `pebd_MaxNum` check with ShineExit \"Buffer max num\", \"Data error\" asserts), its "
             "static initialiser `dynamic_initializer_for_'pebd'` FUN_006960f0 (built-in defaults; where `pebd_MaxNum` is set), "
             "`MaxExpGainAtGroup::megag_Load` FUN_00481980 (PartyBonusLimit.shn: `PSE_ChrLv` u8 → `megag_ExpLimit[151]`, "
             "unchecked index, \"Data error\" for a level 1…150 without a row) and its reader "
             "`GroupExpDistribute::NearFriendInformationSummary::nfis_ExpLimitCut` FUN_00482560 (who calls it, what the cut "
             "amount does).",
             "How `lid_Call` FUN_00483360 reads `pebd_Bonus` (index range, the Z03 §8.2 table `g_PartyExpBonus` DAT_0075d480: "
             "same object or not) and whether World/ExpRecalculation.txt (`ByPartyMem`, `ByLevelDiff`) overrides the SHN values.",
             "Column → member map and 2016 invariants of both files (shn.py). Bugs as `Z29-B<n>`; Coverage boundary as usual."],
      done="`hml_Load`, `pebd_Load`, the `pebd` initialiser, `megag_Load` and `nfis_ExpLimitCut` are cited as `FUN_…` with "
           "pseudocode, both files have a column → member map with their 2016 invariants, and the party experience formula "
           "with these tables is specified."),
 dict(id="Z30", phase=2, title="Zone: handler-reachable leftovers (`coverage.py` gaps: change-character-ID handlers, item "
                               "dismantling, SP / HP stones, title set, spam rules, party / guild helpers)",
      out="docs/pseudocode/zone/Z30-leftovers.md", deps=["Z01", "Z04", "Z08", "Z14"],
      scope=[("zone", "WorldManagerSession", [45]), ("zone", "GameDBSession", [45]), ("zone", "ShinePlayer", [16])],
      goal="After the done zone items, `coverage.py --overview` still lists 48 zone functions reachable from packet handlers "
           "that no doc cites, plus two registered handlers in no item's scope. The docs name some of them, but none "
           "describes what they do. Document each one so the zone handler code is fully covered.",
      steps=["Read with PDB names (`clean.py re-data/exports/zone-pdb - <addr> …`). Where an existing doc already calls the "
             "function by name (Z01 §… `0xB410`, Z04 §12.1 dismantle, Z04 HP stone, Z08 titles / guild zone, Z11 ring "
             "search, Z14 raid table), link that section instead of repeating it.",
             "Scope handlers: `wms_NC_USER_CONNECTION_ZONE_CHANGE_CHAR_ID_CMD` FUN_0044caa0 (with `RaidSystem::GetInRaidNumber` "
             "0063d8b0, `Raid::iterator::UpdateMemberName` 0063d620, `CParty::MemberGetNo` 00645280) and "
             "`gds_NC_USER_CONNECTION_DB_CHANGE_CHAR_ID_ITEM_USE_ACK` FUN_0051b6d0: the rest of the rename-by-item flow after "
             "Z01's `0xB410`. Client side via C01. `sp_NC_MISC_DB_UI_STATE_SAVE_REQ` FUN_00562f40 is in scope so it has an "
             "owner; Z01 already cites it, check it is complete.",
             "Item dismantling internals (Z04 §12.1 'not read'): `ItemDismantleProducer::idp_WhereDismantleProductStore` "
             "00528be0, `idp_DismantleProductExecute` 00529110, dtor 00528ba0, and the `FUN_005290f0` codes. Soul stones: "
             "`sp_SPStoneUse` 00588a40, `sp_SPStoneReserv` 00588c50, `sp_HPStoneReserv` 00589410 (the HP side is in Z04 by name).",
             "Character title: `CCharacterTitleZone::Send_NC_CT_SET_CURRENT_ACK` 005ca9e0, `Send_NC_CT_SET_CURRENT_DB_CMD` "
             "005cadd0, `CT_SellNPC` 005cbff0, `CCharacterTitle::Clear` 0062e370, `sp_CharTitleChangeAvailable` 005608e0. "
             "Spam rules: `SpamerPenaltyDataBox::spdb_SpamePenaltyGet{SecondRule,RepeatRule,ChatBlockTime,ProbateTime}` "
             "00589820 / 00589850 / 00589870 / 00589900 (which table / config, units).",
             "Zone ring and sight: `HolyPromiseCenTransferManager::hpctm_Process` 00483860, "
             "`ZoneRingPacketFindPlayerByNormalUser::zrpb_Success` 005a7cf0 / `zrpb_Failure` 005a8170, "
             "`so_HideExceptMeOff_BriefInfo` 00441700, `so_BroadcastEndOfTrade` 00552e10.",
             "Party / raid / guild helpers: `CParty::SwapPartyMember` 006459e0, `GetEmptyParty` 00645070, "
             "`PARTY_MEMBER_SLOT::operator=` 006455a0, `Raid::iterator::operator==` 0063d0a0, `CGuildZone::Add` 005cc900, "
             "`GUILD_ZONE::operator=` 005cc790, `Send_NC_GUILD_ZONE_LIST_REQ` 005cc980, `GuildWarManager::gwm_IsEnemyGuild` "
             "00481070 / `gwm_EnemyCheck` 00481190, `garse_GuildCheck` 00470800, `~ItemGuildStorage` 00643280.",
             "Remaining helpers: `ItemMixData::GetMixItemIndex` 00635820, `ShineDateTime::operator+=` 00517a80 (term "
             "extension arithmetic), `TownPortalData::operator[]` 0049fd60, `BoothStoreManager::RemoveItem` 0043a420, "
             "`CItemAuthorityBase::IA_IsWork{Chr,Acc}Belonged` 00632180 / 006321e0, `CShnDataFileCheckSum::GetDataFile"
             "{CheckSum,Name}` 006313d0 / 00631430 (login data-file check), `NameString::operator[]` 004519d0, `WELLRNG512a` "
             "0063c8c0 (the RNG: seed, state, who else uses it), `AxialListCount` ctor 00428200, `sp_SetNormalLogoutTick` "
             "005620f0, `fc_GetFieldOption` 00419390, `ShineCommonParameter::operator->` 004192f0, `sp_GetServerMenuactor` "
             "0048cec0, `sp_IsInTrade` 004c2420.",
             "Finish with `coverage.py --overview`: zone gaps 0 or each remaining one argued in the Coverage boundary. Bugs as "
             "`Z30-B<n>`."],
      done="Every function and handler above is cited as `FUN_…` with pseudocode (or a link to the doc section that already "
           "describes it), and `coverage.py --overview` shows no unexplained zone gap."),
 dict(id="Z31", phase=2, title="Zone: class-named functions no document cites (player / object members without a direct "
                               "caller, inventory lock list, item attribute classes, table loaders) and open points of "
                               "Z01-Z04 (added by X02)",
      out="docs/pseudocode/zone/Z31-class-remainder.md", deps=["Z01", "Z04", "Z30", "S01"], scope=[],
      goal="`coverage.py` starts at packet handlers and follows direct calls, so it never sees functions reached only "
           "through virtual calls, member-pointer tables, timers or start-up code. X02 counted them "
           "(`docs/review/confidence.md` §4.4): 1 158 functions the 2016 `Zone.pdb` names `Class::Method` are cited by no "
           "document (25 865 decompiled lines; 789 have no direct caller). Document them, except the gamble classes (Z32).",
      steps=["List the work: `python3 -I docs/plan/status/X02-cov.py game zone 1200` (class, function, lines; largest "
             "first). Drop `CGambleDiceTaiSaiObject`, `CGambleObject`, `DiceTaiSai`, `SlotMachine::*` (Z32). In the first "
             "session group the rest by class into parts of about 2 500 lines and write the list into the status file. For "
             "each function first `rg` its name in `docs/pseudocode` and `docs/knowledge`: where a document already describes "
             "it under its name (an identical-code fold or an uncited address), cite the § and the address and go on.",
             "Start with the 15 named functions of `confidence.md` §4.4: `so_ply_GuildReNameItemUseSuccess` FUN_00473ea0, "
             "`so_ply_GuildReTypeItemUseSuccess` FUN_00474250, `sp_CanUseItemCheck_ByTable` FUN_0056eae0, `sp_CanItemMakeItem` "
             "FUN_0049b6c0, `sp_LogoutDuringParty` FUN_004cd340, `so_ply_BanByServerDisconnect` FUN_00566930, "
             "`so_SpamSendDataToCharDB` FUN_00562990, `sp_SpamSendDataToWM` FUN_00562bc0, `so_ply_DecreaseDmgPassiveSkill` "
             "FUN_005651e0, `so_ply_WeaponSpeedSet` FUN_0043d3c0, `so_ply_WeaponRangeSet` FUN_0043f520, "
             "`sp_ChatColor_Save2World` FUN_00563c70; then `ShinePlayer::~ShinePlayer` FUN_00559300, "
             "`ShineMobileObject::so_smo_AbnormalStateAttribute` FUN_004a8010, the 17 `InventoryLocking::"
             "InventoryCellLockList` members (`icl_IsLocked` FUN_0048b0f0 / FUN_0048af30, `icl_StoreItem` FUN_00488db0, "
             "`icl_ItemInfoZoneRng` FUN_00489aa0, `icl_UseItem` FUN_004895d0, `icl_ItemSell` FUN_00489ec0, ...) and the four "
             "`Table::Load<...>` instances of the level-gap and belong-dice tables.",
             "For a virtual member, find its vtable slot (`rtti.py`, `docs/knowledge/Z01.md` §3) and its callers by slot "
             "offset (`rg '\\+ 0x<slot>\\)\\)\\(' re-data/exports/zone-pdb/decomp.c`), so each block says who calls it and when. "
             "A PDB name on a tiny function may be an identical-code fold: read the body (`docs/knowledge/X02.md`).",
             "Open points of finished first-wave items (`confidence.md` §4.6 rows 5-8): Z02: where the handlers' third "
             "argument `hnd` comes from, the setter of `p+0x5cb9` bit 2, how a roar is delivered; Z01: a table of all "
             "player modes (`*(p+0xe9c)`) with who sets and who tests each; Z04: the BELONGED_CANCEL codes 0x2885-0x288f "
             "branch by branch, and what schedules the auto-arrange; Z03: the builder of the 0x244C payload.",
             "Bugs as `Z31-B<n>`; corrections to older documents in `docs/knowledge/Z31.md` §0 (format of "
             "`docs/knowledge/Z07.md` §0). Finish with `X02-cov.py game zone`: every remaining function argued in the "
             "Coverage boundary."],
      done="Every class-named zone function of `X02-cov.py game zone` outside the gamble classes is cited with pseudocode "
           "or a link to the section that already describes it, and the four open points of rows 5-8 are answered."),
 dict(id="Z32", phase=2, title="Zone: gamble internals (TaiSai dice table object, slot machine classes; added by X02)",
      out="docs/pseudocode/zone/Z32-gamble-internals.md", deps=["Z06"], scope=[],
      goal="Z06 (done) documents the gamble handlers and lists as open in its §7 the TaiSai win tables and the slot "
           "machine's draw, line patterns and jackpot. The classes behind them are cited by no document "
           "(`docs/review/confidence.md` §4.4): `CGambleDiceTaiSaiObject` 36 functions / 2 408 lines, `CGambleObject` 22 / "
           "302, `DiceTaiSai` 1 / 166, the `SlotMachine::*` classes about 1 000 lines.",
      steps=["Read `docs/pseudocode/zone/Z06-economy.md` §7 and its gamble sections (`sect.py`), `docs/knowledge/Z06.md`, "
             "and `confidence.md` §3.4.8 (re-check of Z06) and row L6 of §3.3.3 (the two logout gates are TaiSai tests).",
             "List the functions: `python3 -I docs/plan/status/X02-cov.py game zone 1200 | rg -e Gamble -e TaiSai -e "
             "SlotMachine`. TaiSai: `GDTSO_DiceTaiSai_Result_DiceRoll` FUN_0061a350, `GDTSO_DiceTaiSai_Out` FUN_0061c330 "
             "and the other `GDTSO_*` members: table states and timers, bet kinds and limits, the roll (which RNG), the win "
             "table per bet kind with its multipliers, payout and money messages, what leaving or logging out mid-game "
             "does, manual mode. Slot machine: `SlotMachineAnalyse::sma_ScreenMatch` FUN_00621dd0, `SlotMachineScreen*`, "
             "`SlotMachineCluster`, `SlotMachineJackPotRanking`: reel draw, line patterns, payout table, jackpot pool and "
             "ranking, the data tables each reads (`shn.py`).",
             "Client side for every packet these send (C01, `client-handlers.json`); DB procedures via D03. Bugs as "
             "`Z32-B<n>`."],
      done="Every function of the listed classes is cited with pseudocode; a rebuild can compute the outcome and payout of "
           "a TaiSai round and of a slot-machine spin from the document and the data tables alone."),
 dict(id="D01", phase=2, title="Account and AccountLog servers", out="docs/pseudocode/db/D01-account.md", deps=[],
      scope=[("account", "", ALL), ("accountlog", "", ALL)],
      goal="Every request, the SQL/stored procedure it calls (strings like `{CALL usp_…(?,?)}`), parameters/columns, "
           "and the reply. **Resolve the open question from the Login docs:** which conditions produce result -1/-2, "
           "the blocked flag (0x47), the flag behind 0x48, and AccountLog's region flag (0x51).",
      steps=[DB_STEP,
             "Account server: `Account.bak` has 7 of its 15 procedures. Start the Login open question from "
             "`usp_User_loginGame` (6 parameters, matches the binary): it returns `@userNo` (-1 when ID/password are wrong "
             "or the account is deleted), `@authID`, `@block` (re-checked through `usp_User_chkBlock`) and `@isLoginable` "
             "(group policy, `tUserAuth.bIsLoginAble`), which are likely the sources of the 0x47/0x48 flags *(db-backup)*; "
             "confirm in the binary. The binary also calls `usp_User_LoginGame` with 5 parameters; SQL Server names are not "
             "case-sensitive, so against this DB that call would fail: find which code path uses it. Missing: "
             "`usp_User_LoginNetmarble`, `usp_JPUser_insert`, `usp_TWUser_insert`, `usp_Pcbang_chkIP`, `usp_Event_addCash`, "
             "`p_UserKey_Get_FromAccount`, `p_UserPlayRemainTime_Get_FromAccount`, `p_UserPlayRemainTime_Set_FromAccount`.",
             "AccountLog server: `AccountLog.bak` and `StatisticsData.bak` (ODBC `Statistics`) have 8 of its 12 procedures, "
             "all with the same parameter count. `Fixes/IP Block/p_IPBlock_IsBlock.sql` is a private-server edit; the "
             "`AccountLog.bak` copy is the one to use. Missing: `p_Event_L20_Get`, `p_Event_L20_Set`, "
             "`p_SameTimeCharClass_Add`, `usp_AccountLog_GetDateDiffLastlogout`. `OperatorTool.bak` belongs to the separate "
             "operator tool, not to these servers."]),
 dict(id="D02", phase=2, title="Character server: characters, avatars, save/load", out="docs/pseudocode/db/D02-character.md",
      deps=[], scope=[("character", "", [2, 3, 4, 5, 10, 16, 40, 45])],
      goal="Character/avatar create/delete/list, full character load (NC_CHAR_CHARDATA) and save (CHARSAVE). "
           "Document each stored procedure and the column order (SQLGetData C types: -28 u8, -17 i16, -16 i32, -18 u32, 11 timestamp, 1 string). "
           "The 130-byte AVATAR record builder `FUN_0046bff0` is already decoded (annotations.json).",
      steps=[DB_STEP,
             "Character server: `Character.bak` (older, 2008 R2) and `w00_Character.bak` (newer, 2017, private-server fixes "
             "applied) together have 296 of the 311 procedures it calls, 294 with the same parameter count. In your area: "
             "`usp_CharacterLoading` takes 11 parameters in the binary but 6 in both backups; missing are "
             "`usp_CharacterLoadingDetailInfo`, `p_Promotion_Get`, `p_Promotion_Set`, `p_IsPromotionUser`. Key map, game "
             "option, shortcut, chat colour, tutorial and attendance procedures exist only in `w00_Character`. `Fixes/` "
             "changed `p_Char_Create` (duplicate names), `p_Char_Rename`, `usp_Character_setChangeID` and "
             "`usp_Tutorial_setCharInfo`: use the `Character.bak` copy or note the difference.",
             "Write the table list you meet (table → columns as the procedures use them) into `docs/knowledge/D02.md`; "
             "D03 and D04 build on it.",
             "Open from Z07 (§5): the zone never sets the wedding partner itself; `Partner.RegisterNumber` arrives only in "
             "`0x1081 NC_CHAR_WEDDINGDATA_ACK`. Find how the Character server chooses and stores the partner before a proposal "
             "(0x1080 / 0x1083 and their procedures), and when the divorce requests 0x1089 / 0x108B / 0x108D answer "
             "Success 0 (the zone has already taken the 250 000 / 750 000 fee and does not refund it, Z07-B11).",
             "Open from Z07 (§2): stats are saved with `0x10D1 NC_CHAR_FREESTAT_SET_DB_REQ` only (both raise and lower; the "
             "zone never sends 0x105D / 0x1063). Document the procedure, the meaning of `nErrorType` (0xAC1 ok) and how the "
             "restat item in `DecItemInfo` is consumed."]),
 dict(id="D03", phase=2, title="Character server: items (ITEMDB), economy, pets, house", out="docs/pseudocode/db/D03-character-items.md",
      deps=["D02"], scope=[("character", "", [13, 35, 36, 43, 47, 49, 53])],
      steps=[DB_STEP,
             "Missing in every backup: pets (`usp_Pet_*`, 5), `usp_LinkScroll_SetDestMap`, "
             "`p_Item_MiniHouse_Effect_Resource_Del`, `p_MiniHouseURL_Get`, `p_MiniHouseURL_Set`. Gamble/slot machine, card "
             "collection, safe trade, auto-mon and belonged items exist only in `w00_Character`. The gem enchant procedures "
             "(`usp_Item_*Enchant*`, author `<KHRISMIZER>`) may be private-server work. `p_Item_BuyAll` and `p_Item_BuyLot` "
             "match the binary only in `w00_Character` (the older copy has one parameter fewer). `Fixes/` changed "
             "`usp_ChargeItem_Draw` and `usp_ChargeItem_GetList` (premium inventory slots): compare with `Character.bak`.",
             "Open from Z07 (§7): after `0xC412 NC_COLLECT_REWARD_DB_ACK` the zone does not add the RewardID to its rewarded "
             "list, so a player can request the same card reward again in one session. Say whether the 0xC411 procedure "
             "refuses an already-given RewardID (if not, it is an original bug to add to Z07's list via X01). 0xC411 also "
             "carries a new item key and attribute (0x77 bytes in 2016; the 2017 struct is 8 bytes).",
             "Open from Z07 (§9): pet create/load/rename (0xD40D / 0xD40B / 0xD403) and their result codes 0x3408 / 0x3420 / "
             "0x3418 as the zone expects them."]),
 dict(id="D04", phase=2, title="Character server: social, guild, quests, skills", out="docs/pseudocode/db/D04-character-social.md",
      deps=["D02"], scope=[("character", "", [17, 18, 21, 22, 23, 24, 28, 29, 31, 37, 38, 42])],
      steps=[DB_STEP,
             "The two Character backups cover almost all of your scope. Missing in every backup: `p_Guild_SetMoney`, "
             "`usp_GuildTournament_setRefundNotice`. Private-server reconstructions, not original: `usp_GuildEmblem_*` (3) "
             "and `usp_GuildAcademy_setHistory` (header copied from `usp_Guild_SetToken`; `usp_GuildEmblem_SetInfo` has a parameter named `@nUnk`), and "
             "`usp_Guild_getHistoryList` / `usp_Guild_setHistory` (only in `Fixes/`). `usp_Character_setFriendpoint` takes 2 "
             "parameters in the binary but 3 in `w00_Character`.",
             "Open from Z08 (`docs/knowledge/Z08.md` §2): the quest procedures behind 0x4403 SET_INFO, 0x4405 CLEAR, 0x4409 "
             "GIVE_UP, 0x4418 READ and 0x441A DONE (success code 0xB41; the zone's diary status values are `PLAYER_QUEST_STATUS`), "
             "WT licence 0x5C05 / 0x5C07 (success 0x9B9 / 0x9E1), guild tournament join 0x74E5 (success 0x1C40), holy promise "
             "0x943E / 0x9442 (success 0x1C68): give each its error codes so Z08's tables can be completed."]),
 dict(id="D05", phase=2, title="GameLog server", out="docs/pseudocode/db/D05-gamelog.md", deps=[], scope=[("gamelog", "", ALL)],
      goal="What is logged (all ~200 log messages), table/procedure per message. Can be summarised in tables rather than "
           "full pseudocode where handlers are uniform.",
      steps=[DB_STEP,
             "`GameLog.bak` (older) and `w00_GameLog.bak` (newer) match well: 22 of the 23 procedures the GameLog server "
             "calls have source with the same parameter count; only `usp_Login_setChannel` is missing, and "
             "`p_GameLog_Add_TypeL` exists only in `w00_GameLog`. The `p_GameLog_Add_Type1…L` sources show which "
             "`tGameLog` column each parameter fills, which gives the meaning of the generic log fields. Eight of them "
             "differ between the two backups (Type1, 4, 5, 6, D, E, H, J): compare both."]),
 dict(id="D06", phase=2, title="Database behaviour the backups do not give us (added by D02; run last, before X01)",
      out="docs/pseudocode/db/D06-db-inferred.md", deps=["D01", "D02", "D03", "D04", "D05"], scope=[],
      goal="D01–D05 describe what each DB server does around its stored procedures and take the procedure bodies from the "
           "private-server backups (`docs/plan/db-backups.md`). Some procedures the 2016 binaries call have no source "
           "anywhere or a different parameter count, and several statements about what the database does are only "
           "*(inferred)*. A rebuild has to write these procedures itself. Collect every such gap, infer as far as the "
           "evidence allows what each procedure reads, writes and returns, and the table schema behind it, and write the "
           "result as a spec a rebuild can implement.",
      steps=["Scope, taken at the end of D02 (re-run `python3 -I tools/protocol-re/bak.py cover <bin>` for `account`, "
             "`accountlog`, `character`, `gamelog` first; it may have changed). No source anywhere: account "
             "`p_UserKey_Get_FromAccount`, `p_UserPlayRemainTime_Get_FromAccount`, `p_UserPlayRemainTime_Set_FromAccount`, "
             "`usp_Event_addCash`, `usp_JPUser_insert`, `usp_Pcbang_chkIP`, `usp_TWUser_insert`, `usp_User_LoginNetmarble`; "
             "accountlog `p_Event_L20_Get`, `p_Event_L20_Set`, `p_SameTimeCharClass_Add`, "
             "`usp_AccountLog_GetDateDiffLastlogout`; character `p_Guild_SetMoney`, `p_IsPromotionUser`, "
             "`p_Item_MiniHouse_Effect_Resource_Del`, `p_MiniHouseURL_Get`, `p_MiniHouseURL_Set`, `p_Promotion_Get`, "
             "`p_Promotion_Set`, `usp_CharacterLoadingDetailInfo`, `usp_GuildTournament_setRefundNotice`, "
             "`usp_LinkScroll_SetDestMap`, `usp_Pet_getInfo`, `usp_Pet_setCreate`, `usp_Pet_setDelete`, `usp_Pet_setName`, "
             "`usp_Pet_setTendency`; gamelog `usp_Login_setChannel`. Parameter count differs from the backups: account "
             "`usp_User_LoginGame` (5 vs 6), character `usp_Character_setFriendpoint` (2 vs 3), `usp_CharacterLoading` "
             "(11 vs 6).",
             "Also in scope: call strings built at run time (character `SQL_BuildCallString` FUN_00460bf0, e.g. "
             "`p_Char_SetStateWithSetItemAndRestTime`; `docs/knowledge/D02.md`), which `cover` does not see: find every "
             "caller and check each name against the backups. And every *(inferred)* or *(db-backup)* statement about "
             "database behaviour in the D01–D05 outputs (their \"Not reconstructed / uncertain\" sections, "
             "`docs/plan/status/D0*.md`, `docs/knowledge/D0*.md`) where the backup's procedure may not be the 2016 one: e.g. "
             "D02's `p_Char_GetAllData` 37th column (D02-B19), the result codes −1091 / −1092 / −1094 the Character server "
             "handles for `usp_Character_setStatPoint` but the source does not produce, the 2016 `tCharacterLoading` columns.",
             "The table schema: merge the table → column lists of `docs/knowledge/D01.md`–`D05.md` into one schema, with types "
             "from the ODBC bind and fetch types (C type −16 i32, −28 u8, −17 u16, −18 u32, −25 i64, −27 u64, 1 string, "
             "−2 binary, 11 timestamp; `docs/knowledge/D02.md` lists the getters), keys and the constraint names "
             "`bak.py names` shows.",
             "Evidence for a procedure without source, strongest first: the call site (parameter count, C and SQL types, bind "
             "direction 1 in / 2 in-out / 4 out, the result columns the code fetches and their order; read the wrapper "
             "`SQL_<procedure>` and its callers, and the assembly with `/usr/bin/objdump -d -M intel` when the decompiler "
             "loses arguments); how the handler maps the return codes (client texts via `docs/protocol/client-error-codes.json`); "
             "procedures of the same family in the backups (same prefix, author header, tables); the 2017 PDB struct the "
             "result goes into; captures; the 2015 binaries for an older call (diffing only).",
             "Several versions of a procedure: compare `bak.py proc` of Character.bak, w00_Character.bak and `Fixes/*.sql` "
             "with what the 2016 binary passes, and say which version a rebuild should follow and why.",
             "If Docker or a Windows SQL Server is available, restoring the backups (SQL Server 2017 or newer) gives the real "
             "schema, defaults and constraints, which `bak.py` cannot extract. Record in the status file whether it was done.",
             "One block per procedure instead of per handler: signature with types and directions, tables and columns read "
             "and written, return codes and result rows, the calling handlers (`@ FUN_…`, link to the D0x section), and for "
             "each statement what it is inferred from. Do not edit D01–D05 outputs; corrections go into "
             "`docs/knowledge/D06.md` under \"Corrections\"."],
      done="Every procedure in scope and every run-time call string has a block (or a note that nothing can be inferred, "
           "with the reason); the schema lists every table the 2016 servers use; each open DB statement of D01–D05 is "
           "confirmed, corrected or left open with a reason."),
 dict(id="D07", phase=2, title="Character server: D04 residue (academy reward storage, tournament reward items) (added by D04)",
      out="docs/pseudocode/db/D07-character-reward-items.md", deps=["D04", "D03"], scope=[],
      goal="D04 documented all 120 social/guild/quest/skill handlers of the Character server but left two item-attribute "
           "internals summarised (`docs/pseudocode/db/D04-character-social.md` §12): how 0x986B "
           "NC_GUILD_ACADEMY_DB_ACADEMY_REWARD_REQ picks, merges and moves item stacks in the academy reward storage, and how "
           "0x74AA NC_GUILD_TOURNAMENT_DB_REWARD_CREATE_REQ turns its ITEM_OPT records into item attributes.",
      steps=["Read `docs/pseudocode/db/D04-character-social.md` §6.4 (0x74AA), §9.3 (0x986B), §11 and §12, `docs/knowledge/D04.md`, "
             "and D03's item helpers (`docs/pseudocode/db/D03-character-items.md` §1.2–1.3, §5.3). If W03 is done, take the "
             "ITEM_OPT field names from its WM sender of 0x74AA (W03 scope row 0x74AB, FUN_0040bef0 in the wm export).",
             "0x986B `fc_NC_GUILD_ACADEMY_DB_ACADEMY_REWARD_REQ` FUN_0041de10 (character export): trace the stack choose / merge / "
             "move rule in the academy reward storage (decompiled lines ~107–170 and ~300–397): `AcademyStorage_List`, "
             "`CGameDB_Item_GetItemOptions`, `ItemAttr_Save`, `p_Item_SetStorageAndOwner(…, 1)`, `Item_DropAll`, `Item_Insert`, "
             "`ItemAttr_MakeWithLot` FUN_00468000, the attribute-class helpers FUN_0044ff60 / FUN_0044d340 "
             "(`g_ItemAttrClassContainer`). Derive the exact `EACH_MODIFY_ITEM` entries, `nWantItemCnt` and the want-lot rule of "
             "the 0x986C answer and of the 0x9882 NC_GUILD_ACADEMY_DB_REWARD_WANT_CMD sent to the WM. Use the disassembly where "
             "Ghidra's stack names are ambiguous.",
             "`GTReward_MakeItemAttr` FUN_00467c60: map the 0x21-byte ITEM_OPT record of 0x74AA field by field (bytes 0x00–0x20) "
             "and the SHINE_ITEM_ATTRIBUTE it builds for every ItemInfo class (+0x66), including the random-option block for "
             "class 4; check against the 2017 PDB (`PROTO_NC_GUILD_TOURNAMENT_DB_REWARD_CREATE_REQ::ITEM_OPT` if present) and "
             "`ItemInfo.shn` classes.",
             "Write the results to your own output file only (do not edit D04's files); record bugs as `D07-B<n>` and say in "
             "`docs/knowledge/D07.md` which D04 §12 bullets are now closed and what D04's text should be read as instead."],
      done="The 0x986C / 0x9882 contents are fully derived from the code for every storage situation (no stack, partial "
           "stack, full storage, item failure); every ITEM_OPT byte and every class branch of FUN_00467c60 is named or marked "
           "unused."),
 dict(id="D08", phase=2, title="DB servers: process layer and shared-class copies of Account / AccountLog / Character / "
                               "GameLog, SOAP item-shop client, open points of D01 / D02 (added by X02)",
      out="docs/pseudocode/db/D08-db-process.md", deps=["D01", "D02", "D05", "S02", "L01"], scope=[],
      goal="D01-D05 document the packet handlers of the four database servers. Their process layer was never compared with "
           "the shared library (S02 §6 leaves it open): 389 (Account) and 382 (AccountLog) class-named functions are cited "
           "by no document (`WinService`, `MiniDumper`, `CSocket_*`, `CSession*`, `DataServer`, `cLogSystem`, and the data "
           "loaders `ItemAttrCls_*`, `ItemDataBox`, `MapDataBox`, `CShnDataFileCheckSum`); Character and GameLog have no PDB "
           "and 2 171 / 990 uncited functions (`docs/review/confidence.md` §4.4). D02 also leaves its SOAP item-shop client "
           "undescribed.",
      steps=["Account and AccountLog (PDB exports `account-pdb`, `accountlog-pdb`): `python3 -I docs/plan/status/X02-cov.py "
             "game account 400` and `game accountlog 400`. For each class compare with the document that describes the same "
             "class in another server (S02, L01, W05, Z01, Z27) and write only the differences; where the code is the "
             "same, one table row (class, functions, 'same as <doc> §'). Document start-up (`DataServer`: config keys via "
             "Z19, listeners, ODBC connections and worker threads), shutdown and the timers in full.",
             "Character and GameLog (no PDB): match their functions to the Account ones by strings and shape (same "
             "compiler, same library), name what matches in `tools/protocol-re/names/<bin>/D08.json`, and state per "
             "server what is different (ODBC pool sizes, queues, which tables the Character server loads and why).",
             "SOAP item-shop client of the Character server: FUN_0043f690 and below (`confidence.md` §4.6 row 10; D02's "
             "open point): the HTTP / SOAP requests built (URL and action strings from `strings.tsv`), when each is sent, "
             "the answers parsed, timeouts, and what the zone-facing handlers do when the shop host does not answer.",
             "Open points of D01 / D02 (`confidence.md` §4.6 rows 4 and 9): D01 the TEENAGER `nType` 1 arithmetic; D02 the "
             "`nStatusDone` filters of 0x1004, the 0x1017 item-record sender FUN_004056a0, the field names of 0x0812-0x0815 "
             "(2016 WM / Zone PDB structs first). Already closed by X02, do not repeat: the 0x0804 handlers and the "
             "Character 0x0801 handler (`confidence.md` §4.7).",
             "Bugs as `D08-B<n>`; corrections to D01-D05 in `docs/knowledge/D08.md` §0."],
      done="Every class-named function of Account / AccountLog is cited or covered by a 'same as' row, the Character and "
           "GameLog process layers are matched and their differences stated, the SOAP client has pseudocode for every "
           "request, and rows 4 and 9 are answered."),
 dict(id="P01", phase=1, title="Packet capture decoder", out="tools/protocol-re/pcap_decode.py + docs/knowledge/P01.md",
      scope=[], deps=[],
      goal="A pure-Python (stdlib only: no scapy/dpkt/tshark on this machine) tool that turns a capture of real "
           "client↔server traffic into a decoded, annotated packet log, and checks it against our documentation. "
           "It must work before any capture exists: test it on synthetic captures it generates itself.",
      steps=["Captures are recorded with Wireshark on the (Windows) PC running the game and copied here. tshark is NOT available on "
             "this machine, so parse the files directly.",
             "Input: `.pcapng` (primary, Wireshark default) and `.pcap`; link types Ethernet, Npcap loopback (DLT_NULL/LOOP) and raw IP; IPv4 TCP. "
             "Read pcapng **packet comments** (EPB `opt_comment`) and show them in the decoded log as markers. P02 uses them to tie "
             "packets to the user's actions. Reassemble each TCP "
             "stream by sequence number (handle retransmits and out-of-order data, report gaps).",
             "Classify streams by server port from `Files/Server/2016/9Data/ServerInfo/ServerInfo.txt` (type-20 client ports: Login 9010, "
             "WM 9110, zones 9210/9212/9214/9216). Make the port map overridable on the command line (a live server may use other ports).",
             "De-frame per `docs/protocol/README.md` §1.1. Decrypt client→server bodies with the XOR-499 table (Appendix A) starting at "
             "`seed % 499` from the stream's first server→client `0x0807`. The index runs on across packets. If the seed was not "
             "captured, brute-force the start index (499 candidates) by checking that decrypted opcodes are known.",
             "Decode each packet using `docs/protocol/opcodes.json` (name), `annotations.json` + `annotations/*.json` (verified "
             "fields, preferred), and `re-data/exports/<bin>/layouts.json` (generated fields, marked as such). Unknown regions → hex.",
             "Validation report per packet type: count, observed payload sizes vs documented size, fields whose observed "
             "values contradict documented constants or ranges, opcodes never documented, documented C→S checks violated "
             "(e.g. length checks), and bytes the docs leave undocumented that are not always zero.",
             "Outputs: `<capture>.decoded.txt` (time, direction, server, opcode, name, fields), `<capture>.report.md`, and "
             "`<capture>.json` (machine-readable for P02). Mask the password field of `0x0C5A` by default (`--show-secrets` to keep it).",
             "Self-test: `pcap_decode.py --selftest` builds a synthetic pcap (seed, encrypted 0x0C65/0x0C5A, server 0x0C0A, "
             "a long-form packet ≥256 bytes, a TCP segment split across two frames) and asserts that decoding round-trips.",
             "Document usage and limits in `docs/knowledge/P01.md` and add a short section to `docs/protocol/README.md`."],
      done="`--selftest` passes; decoding a synthetic capture yields correct opcodes, decrypted payloads and a report; "
           "usage documented."),
 dict(id="P02", phase=2, title="Capture validation (run once per batch of captures)", out="docs/protocol/capture-validation.md",
      scope=[], deps=["P01", "captures in re-data/captures/"],
      goal="Use real captures to confirm or correct the documented packet layouts, value ranges, error codes and message "
           "order. Re-run this item whenever new captures are added or a phase of items finishes.",
      steps=["Run `tools/protocol-re/pcap_decode.py` on every capture in `re-data/captures/` that has not yet been processed "
             "(keep a list in `docs/plan/status/P02.md`). Use the packet comments inside each capture (shown as markers by the decoder) and the scenario notes next to it (see "
             "`docs/plan/capture-guide.md`).",
             "For each opcode seen: compare with annotations and generated layouts. Confirmed fields → add `\"evidence\": "
             "\"capture:<file>\"` to the field note in `docs/protocol/annotations/P02.json`. Name fields from what changes "
             "between scenarios (e.g. level, coordinates, item ids against the SHN tables).",
             "Message order: check the sequences in `docs/protocol/README.md` §2 and the pseudocode (e.g. login burst after 0x1803) "
             "against the captured order. Record differences.",
             "Write `docs/protocol/capture-validation.md`: per opcode the status (confirmed / corrected / contradicted / never seen), "
             "and a list of discrepancies addressed to the owning work item (look up the opcode in `docs/plan/items/*.md`).",
             "Do not edit other items' pseudocode. Report contradictions in `capture-validation.md` and in `docs/knowledge/P02.md`."],
      done="All captures processed; every observed opcode has a status; discrepancies listed per work item."),
 dict(id="P03", phase=1, title="Wireshark dissector (Lua plugin, generated from the docs)",
      out="tools/protocol-re/make_dissector.py → tools/wireshark/fiesta.lua + docs/knowledge/P03.md", scope=[], deps=["P01 (soft: its synthetic capture is a handy test file)"],
      goal="Let the user see decrypted, named, field-decoded Fiesta packets live in Wireshark on the PC that runs the game, "
           "so they can comment packets accurately while recording. The plugin is generated from our docs and rebuilt by "
           "`regen.sh`, so it improves as other items add names and layouts.",
      steps=["Wireshark is not installed on this machine; the user installs the plugin on the capture PC (Windows): copy `fiesta.lua` "
             "to `%APPDATA%\\Wireshark\\plugins\\` (or the global plugins folder) and restart Wireshark / Ctrl+Shift+L. Document this.",
             "Register on the type-20 client ports from `Files/Server/2016/9Data/ServerInfo/ServerInfo.txt` (9010, 9110, 9210/9212/9214/9216) and "
             "expose the port list as a protocol preference.",
             "Framing via `dissect_tcp_pdus` (handles TCP segmentation): length = 1-byte form, or 0x00 + u16 long form "
             "(`docs/protocol/README.md` §1.1). One Fiesta packet per subtree; several per TCP segment.",
             "Decryption of client→server bodies: XOR-499 table (README Appendix A), start index = `seed % 499` from the server's "
             "`0x0807` on the same conversation, advancing across packets. Wireshark re-dissects packets in any order, so compute "
             "the index **once** on the first pass (`not pinfo.visited`) and cache it per frame + PDU offset (and the running index "
             "per conversation). Show both raw and decrypted bytes (new data source tab).",
             "Opcode → name from `docs/protocol/opcodes.json` (dept/cmd shown too); fields from `annotations.json` + "
             "`annotations/*.json` (verified, preferred) and `re-data/exports/<bin>/layouts.json` (generated, labelled \"guess\"). "
             "Field types u8/u16/u32/i16/i32/char[n]/bytes; structs like AVATAR/WORLD as repeated subtrees with count fields.",
             "Expert info for: unknown opcode, payload shorter/longer than documented, packet before seed (cannot decrypt).",
             "Mask the `0x0C5A` password field by default (preference to show it).",
             "Make `make_dissector.py` part of `tools/protocol-re/regen.sh`.",
             "Testing without Wireshark here: keep framing/decrypt logic in pure Lua functions and test them with a standalone `lua` "
             "interpreter if one is installed (`which lua`). Otherwise port the same test vectors from P01's self-test into a Python "
             "check of the generated tables. Ask the user to confirm the plugin on their PC with P01's synthetic capture and a real one."],
      done="`fiesta.lua` generated by `regen.sh`; decryption and framing logic tested; installation and usage documented in "
           "`docs/plan/capture-guide.md` (section \"Live decoding in Wireshark\") and `docs/knowledge/P03.md`."),
 dict(id="P04", phase=2, title="Protocol README: corrections from capture validation (added by P02)",
      out="docs/protocol/README.md (corrected in place) + docs/knowledge/P04.md", scope=[], deps=["P02"],
      goal="`docs/protocol/README.md` is the entry point every item reads for framing, seeds, heartbeats and the login → WM → "
           "zone flow, but its owners (P01, L00) are done and X01 may not write it. The first capture batch (P02) "
           "contradicted or extended several of its statements. Bring the README in line with the captures and the code, "
           "so later readers do not have to know `capture-validation.md` to avoid the old statements.",
      steps=["Read `docs/protocol/capture-validation.md` §2 (transport), §7 (message order against README §2) and the "
             "`README (P01/L00)` rows of the Corrections table in `docs/knowledge/P02.md`; do not re-derive them.",
             "README §1.4 (seed table, zone row) and the Unknowns line \"Whether the zone also sends the seed unprompted on "
             "accept\": the zone sends `0x0807` on accept (`ZoneServer::zs_connect` @ FUN_005aa840 → "
             "`ShinePlayer::so_EncSeedSet` @ FUN_0054f660, global counter `seed` +1 mod 499; `Send_NC_MISC_SEED_ACK` @ "
             "FUN_0045b120); the `0x0806` path (FUN_00451a30) is dead for this client (Z18-leftovers, Z18-B2).",
             "README §1.5 (heartbeat): server (WM, zone) sends `0x0804` after ~30 s of client silence, client answers "
             "`0x0805`; unsolicited client `0x0805` to the WM during map loads (capture-validation §2.4, §4.4, §5.5).",
             "README §2: add the steps the captures show (0x0C04/0x0C05, token login 0x0C37, the 0x0C1B/0x0C1C world-list "
             "poll, 0x080D/0x080E game time, WM option pushes 0x7032–0x7034, zone blob copies before 0x1802, the 0x1803 "
             "client tick, map change, logout to the world list, duplicate-login kick), each citing the capture-validation § "
             "and the pseudocode § that documents it; mark what is *(captured)*.",
             "Keep the README a sketch: link to the pseudocode for detail. Record what was changed (old → new, with source) in "
             "`docs/knowledge/P04.md` so X01's \"Superseded statements\" table can cite it."],
      done="README §1.4, §1.5, §2 and the Unknowns list agree with capture-validation §2 / §7; every changed statement is listed "
           "in `docs/knowledge/P04.md`."),
 dict(id="P05", phase=2, title="Protocol README: the flows of capture batch 4 (added by P02)",
      out="docs/protocol/README.md (corrected in place) + docs/knowledge/P05.md", scope=[], deps=["P04", "P02 (batch 4)"],
      goal="P04 brought `docs/protocol/README.md` §1–§2 in line with capture batches 1–3; its sweep (part 3, commit e20c6b3) "
           "ran before P02 checked batch 4 (captures `s37b`, `s38`, `s24`; capture-validation §22–§25), and only its review "
           "is left. X06 writes only `docs/pseudocode/README.md`. Batch 4 captured flows README §2 omits or states "
           "differently: back to character select from in game (`0x0C18 {1}`), the quit to the desktop (`0x0C18 {0}`, two "
           "`0x0C19`, P02-B35's four saves or one), the client's own logout after losing the zone socket, the zone's 10-s "
           "Kickout and 13-s Logout timers, the WM's `0x1002 {0x145}` with the zones down or after a tutorial skip, the "
           "create refusal and both renames. Bring README §2 up to date with batch 4.",
      steps=["Read capture-validation §11 (rows from \"Character create refused\" on), §22.2–§22.5, §23.2–§23.4, §23.6 and "
             "§25.9, and the \"(batch 4)\" rows of the Corrections table in `docs/knowledge/P02.md` (outline with `sect.py`, "
             "then the sections); do not re-read code: P02's rows give the `@ FUN_…` and the evidence.",
             "README §2.4 (leaving the game): add back to character select from in game (`0x0C18 {1}`: one save `StoreType` 9 "
             "+ `0x0C31`, WM `0x1037` / `0x081F` / `0xC807`, list reload `0x0C12` → `0x0C13` → `0x0C14`, the client's 1-byte "
             "`0x0C1F`; §22.5) and the quit (`0x0C18 {0}` to WM and zone, `0x0C19` from the 0x0C18 handler and from "
             "`Client_OnClosed`, four saves 4 / 7 / 4 / 9 or one, P02-B35; §22.5, §25.9); the two logout timers (§23.3); "
             "the client's own logout when the zone connection is lost (`0x0C18 {0}` to every open socket, \"Disconnected "
             "from the server.\", §23.4). Check the existing sentence \"From the character list the client sends only "
             "`0x0C33` → `0x0C34`\" against §22.5.",
             "README §2.6 / §2.2 / §2.7: the create refusal (`0x1403` → `0x1404`, §22.1), the free rename and the rename right "
             "(dept 45, §22.3 / §22.4), the WM's `0x1002 {0x145}` (\"The Map is under maintenance\") with all zones down "
             "(§23.6) or after a tutorial skip of a listed character (P02-B33, §22.2); mark each *(captured)* with the "
             "capture-validation §.",
             "Keep the README a sketch: link to the pseudocode for detail. Record every change (old → new, with source) in "
             "`docs/knowledge/P05.md` so X06 / X01 can cite it; run `tools/protocol-re/regen.sh`."],
      done="README §2 agrees with capture-validation §11's batch-4 rows and §22.5 / §23.3 / §23.4 / §25.9; every changed "
           "statement is listed in `docs/knowledge/P05.md`."),
 dict(id="X01", phase=3, title="Integration and review", out="docs/pseudocode/README.md", deps=["all"], scope=[],
      goal="Read all item outputs, fix contradictions, write the architecture overview (processes, links, data flow), "
           "a cross-server sequence index (feature → messages → handlers in each server), a glossary, a register of "
           "original-server bugs, and regenerate all docs. List remaining gaps.",
      steps=["Original-server bug register: a section \"Original-server bugs\" in `docs/pseudocode/README.md` that lists every "
             "behaviour of the 2016 servers that looks unintended, so a rebuild can decide per entry to reproduce or fix it. "
             "One table row per bug: ID, server and handler (`@ FUN_…`, link to the pseudocode section), the 2016 behaviour, "
             "the visible effect, the likely intent, evidence level (read in code / *(inferred)* / *(captured)*) and the "
             "owning item. Keep the items' IDs (`<item>-B<n>`). Sources: each item's \"Original-server bugs\" section and "
             "every `(original bug)` tag (AGENTS.md convention; W02-party-raid.md §9 is the reference). Items done before "
             "that convention (L00, W01, Z01–Z03, C01, C02, P01, P03) left free-text notes instead: grep "
             "`docs/pseudocode/**/*.md` and `docs/knowledge/*.md` for `bug`, `sic`, `never reach`, `uninitialised`, "
             "`not initialised`, `ignored`, `copy-paste`, `typo` and give those entries IDs `<item>-B<n>`. Include "
             "client-side mismatches (server sends a code or opcode the client does not handle) and client text typos. "
             "Do not change the owning items' files; if an entry needs more evidence, list it as a gap.",
             "Corrections between items: later items record corrections to earlier ones in their knowledge file instead of "
             "editing them (e.g. `docs/knowledge/Z07.md` §0 corrects Z02-B5 and Z02 §10 on the produce path and the wedding "
             "partner; `docs/knowledge/Z02.md` §1 corrects Z01). Collect every such section (grep `docs/knowledge/*.md` for "
             "`Correction`), apply them in the overview and the bug register (mark superseded entries), and list them in a "
             "\"Superseded statements\" table in `docs/pseudocode/README.md` so readers of the older files are warned."]),
 dict(id="X03", phase=3, title="Integration update: X02's corrections and the bugs of X02 and its follow-ups into the "
                               "README register and the superseded-statements list (added by X02)",
      out="docs/pseudocode/README.md", deps=["X01", "X02", "Z31", "Z32", "W06", "D08 (soft: run without the ones not done)"],
      scope=[],
      goal="X01 is done and its plan has no recurring step, but its output `docs/pseudocode/README.md` is the only place "
           "where readers of the older documents are warned. X02 recorded 68 corrections to other items' statements "
           "(`docs/knowledge/X02.md` §0) and twelve bugs (`docs/review/confidence.md` §5, X02-B1 … B12) after X01 ran; "
           "the follow-up items Z31, Z32, W06 and D08 add more. Bring the README up to date with them. This item edits "
           "X01's sections of the README in place (the one exception to 'never edit another item's output'); it does not "
           "touch the owners' pseudocode.",
      steps=["Superseded statements (README §5): one row per row of `docs/knowledge/X02.md` §0 (owner document and §, the "
             "old statement, the correct one with its `@ FUN_…`, the X02 re-check ID). Rows X01 already lists and X02 "
             "only confirmed stay as they are; rows X02 marks 'superseded' in `confidence.md` §3 need no new entry. Then "
             "the same for the `Correction` / §0 sections of `docs/knowledge/Z31.md`, `Z32.md`, `W06.md`, `D08.md` where "
             "they exist.",
             "Bug register: add X02-B1 … B12 in the register's row format (`confidence.md` §5 has it; evidence level and "
             "reachability from `docs/knowledge/X02.md` §3), then every `<item>-B<n>` of Z31, Z32, W06, D08. Where an X02 "
             "re-check withdrew or changed an existing register entry (`confidence.md` §3, result 'corrected' or "
             "'refined' on a row that names a bug ID), change that entry and say so.",
             "README item table and overview: the rows of X02, Z31, Z32, W06, D08 (the X02 row still says 'not started'), "
             "links to `docs/review/confidence.md` and `docs/plan/capture-scenarios.md`, and the feature → message index "
             "for anything the four follow-ups add.",
             "Run `tools/protocol-re/regen.sh`. No code reading is needed beyond checking a row that looks wrong; report "
             "such rows in `docs/knowledge/X03.md` §0 instead of changing the claim."],
      done="Every row of `docs/knowledge/X02.md` §0 is in the superseded-statements list, every X02 bug and every bug of the "
           "finished follow-ups is in the register, and the README item table matches the status files."),
 dict(id="X02", phase=3, title="Confidence review and targeted capture/DB experiments",
      out="docs/review/confidence.md + docs/plan/capture-scenarios.md", deps=["all phase-2 items", "X01 (soft)"], scope=[],
      goal="User review of finished items has corrected several assumptions per item, so the static analysis is only "
           "low-to-medium confidence. Re-check the claims everything else depends on, give each section a confidence "
           "rating, and turn whatever static reading cannot settle into concrete capture scenarios (beyond the 13 in "
           "`capture-guide.md`), many of them set up with direct database edits so an effect shows up in one short "
           "session.",
      steps=["Learn from past mistakes first. Collect every correction made so far: the `Correction` sections in "
             "`docs/knowledge/*.md`, the corrected or contradicted entries in `docs/protocol/capture-validation.md`, and "
             "`git log -p` on `docs/pseudocode` and `docs/knowledge` (commits after an item's first commit are mostly "
             "corrections after user review). Group them into error classes (for example: a field's meaning guessed from "
             "its size, the wrong branch of a switch, a PDB 2017 fact taken for 2016, a struct offset off by the `ref` "
             "prefix, a callee assumed to do what its name says, a client handler not checked). Write the classes with "
             "counts to `docs/review/confidence.md` §1. They decide what to re-check.",
             "Rate every pseudocode section (per `docs/pseudocode/**/*.md` heading, and per `docs/knowledge/*.md` struct "
             "table): **high** = read in code and confirmed by a capture or by the client handler; **medium** = read in code "
             "only; **low** = *(inferred)*, *(pdb2017)* only, or one of the error classes from §1 applies. One table per "
             "file in §2: section, rating, reason, what would raise it.",
             "Adversarial re-check of the load-bearing claims, worst first: claims many other items cite (shared structs, "
             "the `ref` prefix, player-object offsets, ITEMDB message order, zone↔WM handoff), every low rating in a "
             "client-facing packet, and every instance of an error class from §1. For each, re-read the function with "
             "`clean.py`, then try to disprove the claim, not confirm it (check the other branches, the callers, the client "
             "side, and the 2015 binaries if behaviour looks odd). Record the result in §3: confirmed / corrected (with the "
             "correct statement and `@ FUN_…`) / still open. Do not edit other items' files; corrections go to "
             "`docs/knowledge/X02.md` §0 in the same table format as `docs/knowledge/Z07.md` §0, so X01 and the owners pick "
             "them up.",
             "Capture scenarios: for every claim still medium or low after the re-check, write a scenario in "
             "`docs/plan/capture-scenarios.md` (numbered from 14, continuing `capture-guide.md`). Each has: claims it tests "
             "(doc + section), setup, exact steps for the user, the **prediction** (opcodes in order with the field values "
             "our docs expect), and what result would disprove it. Group scenarios so one session covers several claims; "
             "order by claims settled per minute of user time.",
             "Database setups: where a state is slow to reach in play (high level, rare item, full inventory, guild with "
             "N members, quest at step K, money near the cap, expired item, banned/blocked account, character in a "
             "deleted or odd state), give the SQL that puts a test character in that state. Use only real table, column "
             "and procedure names, read from the backups (`bak.py`, `docs/plan/db-backups.md`) and checked against the "
             "2016 binaries' `{CALL …}` strings; never guess a column. Each setup states which server must be stopped or "
             "which character must be logged out first (find where the Character/Account server caches the row), a "
             "`SELECT` to save the old values and the `UPDATE` that restores them, and a warning to run it on the test "
             "server only. Also use GM commands (`docs/pseudocode/zone/Z11-*.md`) where they reach the state faster than "
             "SQL, and boundary values (0, max, max+1, negative, wrong type id) to test the checks the docs describe.",
             "Also list in `capture-scenarios.md` the experiments that need a modified SHN table or server config "
             "(`Files/Server/2016/9Data`) instead of SQL, with the exact row/key to change.",
             "Items finished before the plan files had the \"Coverage boundary\" and review steps (status files without a "
             "\"Review\" section): run `coverage.py <ID>` for each, and add their uncovered, unargued gaps to "
             "`docs/review/confidence.md` §4 per item, so a follow-up session of that item can close them.",
             "Link the new scenarios from `docs/plan/capture-guide.md` (one line under the scenarios table; that is the only "
             "edit to another file). After the user records them, P02 validates them as usual; then re-run X02 to update the "
             "ratings."],
      done="Every pseudocode section has a rating; all high-traffic claims re-checked with results in §3 and corrections in "
           "`docs/knowledge/X02.md`; every remaining medium/low client-facing claim has a scenario with a prediction; DB "
           "setups use only verified names and come with restore statements."),
 dict(id="X04", phase=3, title="Integration update: P02's capture batches 2 and 3 (corrections, bugs P02-B5 … B32, "
                               "captured evidence) into the README register and the superseded-statements list "
                               "(added by P02)",
      out="docs/pseudocode/README.md + docs/knowledge/X04.md", scope=[],
      deps=["X01", "P02", "X03 (soft: not at the same time, both edit README §5 / §6)"],
      goal="X01 ran after the second capture batch was added but integrated only P02's batch 1: README §5 (Superseded "
           "statements) holds P02's batch-1 rows, the register (README §6) lists P02-B1 … B4, and its four links "
           "`capture-validation.md#8-original-server-bugs` point at a section batch 2 renumbered (§8 → §12). Batches 2 and "
           "3 (capture-validation §7–§10, §16–§21) added P02-B5 … B32, about 70 correction rows for done items "
           "(capture-validation §13, statuses \"→ X01\" from batch 2 and \"→ X04\"), captured evidence for other items' "
           "bugs (§12, second table) and 40 confirmed or corrected flows (§11). X03 covers only X02 and its follow-ups. "
           "Bring the README up to date with P02. Like X03, this item edits X01's README sections in place; it does not "
           "touch the owners' pseudocode.",
      steps=["Read capture-validation §11, §12, §13 and the Corrections table of `docs/knowledge/P02.md` (outline with "
             "`sect.py`, then the sections); do not re-read code: P02's rows give the `@ FUN_…` and the evidence.",
             "Superseded statements (README §5): for every §13 row whose status names X01 or X04, `rg` README §5 for its "
             "owner § and opcode; add the missing ones in §5's row format (owner document and §, old statement, correct "
             "statement with `@ FUN_…`, source `P02; capture-validation §n`). Rows already fixed by an annotation "
             "override (\"corrected (P02.json …)\", \"fixed by P02\") get a row only when a reader of the owner's text "
             "would still be misled. Drop or mark withdrawn the register entries §13 contradicts (L00-B6: `UserIP` is "
             "filled; also README §3.15's \"IP zeroed, L00-B6\").",
             "Bug register (README §6): add P02-B5 … P02-B31 from capture-validation §12 (first table) in the register's "
             "row format (handler `@ FUN_…`, 2016 behaviour, effect, intent, evidence, owner P02). For each row of §12's "
             "second table (other items' bugs seen on the wire) set that entry's evidence to *(captured)* with the §; "
             "the P02 rows that only extend another item's bug (P02-B16 on 0x305C, P02-B29 on W04's whisper flag, P02-B30 "
             "on Z18 / Z05 paths) say so in both entries.",
             "Links: the README cites capture-validation by § number and by anchor. Batch 2 renumbered old §7–§11 to "
             "§11–§15 (message order §11, bugs §12, discrepancies §13, uncertain §14, coverage boundary §15) and batch 3 "
             "put §16–§21 before §11. Fix every link and § citation (`rg -n 'capture-validation' docs/pseudocode/README.md`).",
             "Sequence index (README §3): add *(captured)* and the capture-validation § to the steps §11's batch-2 and "
             "batch-3 rows confirm (link round trips, character load, hand-over, saves, kill, level-up, death and revive, "
             "character create / delete, WM and zone start, sight entry, chat, GM visibility, item operations, storage, "
             "sell / buy back, soul stones, failed purchase, expiry), and apply the order corrections (W01 §4.1 0x1407 → "
             "0x1413, W01 §7.2, W05 §1.3, Z01 §8.4).",
             "Run `tools/protocol-re/regen.sh`. Record per README table how many rows were added or changed, and every §13 "
             "row left out with the reason, in `docs/knowledge/X04.md`."],
      done="Every capture-validation §13 row of batches 2–3 that names X01 or X04 has a README §5 row or a stated reason in "
           "`docs/knowledge/X04.md`; P02-B5 … B32 are in the register; the §12 second-table entries carry *(captured)*; "
           "every README citation of capture-validation points at the current section."),
 dict(id="X05", phase=3, title="Capture scenarios and ratings after capture batch 3: X02's recurring re-run (added by P02)",
      out="docs/plan/capture-scenarios.md + docs/review/confidence.md (both updated in place) + docs/knowledge/X05.md",
      scope=[], deps=["P02 (batch 3)", "X02"],
      goal="X02 wrote capture scenarios 14–44, DB setups S1–S16 and table experiments X1–X7; its plan ends \"after the user "
           "records them, P02 validates them as usual; then re-run X02 to update the ratings\", and X02 is done. The "
           "third capture batch recorded scenarios 14, 21 (with S13, S16 and X3) and 37 (scenario 24 has notes but no "
           "capture). P02 checked them against the predictions (capture-validation §16–§21), found scenario texts that "
           "did not match what was recorded (§13 rows owned by X02), and listed what is still open (§14 batch-3 bullets, "
           "§15 rows naming X05). Do X02's re-run: update the scenarios and the ratings so the next recording session "
           "targets what is still open. This item edits X02's two output files in place; it does not touch the "
           "owners' pseudocode.",
      steps=["Read capture-validation §1 (batch-3 rows), the §13 rows owned by X02, the §14 bullets starting \"Batch 3\" and "
             "the §15 rows naming X05 (outline with `sect.py`); do not re-derive them.",
             "Results: under each recorded scenario (`capture-scenarios.md` §3.14, §3.21, §3.37, §8.14 S13, §8.17 S16, "
             "§9.4 X3) add a line \"Result (P02 batch 3)\": each prediction confirmed / disproved / not reached, with the "
             "capture-validation §.",
             "Fix the scenario texts §13 names: §3.37 step 1 (the login screen holds no connection, so idle there tests "
             "nothing; idle on the world list or character list instead), §3.14 steps (2), (4), (6) (walk and sit were not "
             "done; the unknown-name whisper put the name into the text), the `tools/capture/21` S13 / S16 / snapshot "
             "scripts (they ran for Test1235, not the scenario's Test2: name the character in one variable and print it).",
             "Open after batch 3, one scenario (or a step added to an existing one) each, with setup, steps, prediction "
             "and what disproves it: scenario 14 steps (2)–(4) (walk `0x2017` / `0x2018`, sit, whisper to an unknown name "
             "`0x200E`, emote stop `0x2022` / `0x2023`, shout out of sight); "
             "scenario 21 for the character the SQL snapshots name; buy back onto an empty cell (`0x34B9` / `0x34BA`); "
             "sell, buy-back and soul-stone refusals (`0x3427`, `0x366B`–`0x366F`, `0x5005`, `0x3443`); the storage page "
             "request `0x3028`; S16 with a fame or gamble-coin item (D03-B1); X3's untried paths of the over-full stack "
             "(sell `0x385`, use `0x702`, move-merge); an expired item worn or used before the minute check; scenario 24 "
             "(not captured); the WM's `Msg` log next to a WM restart (capture-validation §17.6).",
             "Batch-2 leftovers (capture-validation §15 rows that named X02): the WM → zone blobs of a character with a "
             "house, pet, emblem … and a failed map login `0x101E` (§7.5.3); item transaction failures (§8.2); PvP / "
             "party / guild-war deaths, exp loss, skill fail / abort, revive to another map, rebirth (§9); `0x7037` with "
             "two or more shortcut changes (§14); synced clocks for the per-minute phase and `0x7C07` timing, the "
             "`World::LoadMap` heartbeat points (map loads with markers), the extra `hpchangeorder` reads (§9.1) and the "
             "client-send flush point, the 0x10D2 single-option column names (§14). Map each to an existing scenario "
             "number, write one, or state why no capture is worth it (no layout or order depends on it).",
             "Ratings (`docs/review/confidence.md` §2): re-run `docs/plan/status/X02-rate.py` (it reads capture-validation "
             "§11 / §13), then check by hand the sections batches 2–3 confirm or correct (§11 rows, §13 rows) and update "
             "the hand ratings (`X02-rate-hand.py`).",
             "Link the new scenarios from `docs/plan/capture-guide.md` (the scenarios line). Record the changes in "
             "`docs/knowledge/X05.md`."],
      done="Every recorded batch-3 scenario has a result line; every §15 row naming X05 maps to a scenario number or a stated "
           "reason in `docs/knowledge/X05.md`; the §13 scenario-text rows are fixed; confidence ratings re-run after "
           "batch 3."),
 dict(id="X06", phase=3, title="Integration update: P02's capture batch 4 (corrections, bugs P02-B33 … B40, captured "
                               "evidence) into the README register and the superseded-statements list (added by P02)",
      out="docs/pseudocode/README.md + docs/knowledge/X06.md", scope=[],
      deps=["X04", "P02 (batch 4)"],
      goal="X04 brought P02's batches 2 and 3 into `docs/pseudocode/README.md` (superseded statements §5, bug register §6, "
           "sequence index §3) and is done. Batch 4 (captures `s37b`, `s38`, `s24`; capture-validation §22–§25) added "
           "P02-B33 … B40, 13 correction rows for done items (capture-validation §13, status \"batch-4 follow-up\" with "
           "an owner other than X02: W01 §3.3 / §6.2 ×2, W01 / Z01 quit, Z01 §8.3 Kickout timer, Z01 §8.4 auto-save, "
           "W01 / D02 `0x1037`, Z03 §9.1 `0x4812`, Z11 §4.4 ×2, Z23 §2.4, Z09 §23.9 / Z22 §10.7, Z03 §7.3), captured "
           "evidence for other items' bugs (§12 second table, rows citing §22–§25) and 21 confirmed or corrected flows "
           "(§11 rows from \"Character create refused\" on). Bring the README up to date with batch 4, as X04 did for "
           "batches 2–3. This item edits X01's README sections in place; it does not touch the owners' pseudocode.",
      steps=["Read capture-validation §11 (batch-4 rows), §12, §13 (rows with status \"batch-4 follow-up\") and the "
             "\"(batch 4)\" rows of the Corrections table in `docs/knowledge/P02.md` (outline with `sect.py`, then the "
             "sections); do not re-read code: P02's rows give the `@ FUN_…` and the evidence.",
             "Superseded statements (README §5): one row per §13 batch-4 row whose owner is not X02, in §5's row format "
             "(owner document and §, old statement, correct statement with `@ FUN_…`, source `P02; capture-validation "
             "§n`). The row \"P02 own (batch 4)\" of the knowledge table corrects P02's own §22.5 / §23.3 (already fixed "
             "there): no README row unless the README cites the old wording.",
             "Bug register (README §6): add P02-B33 … P02-B40 from capture-validation §12 (first table) in the register's "
             "row format; P02-B35 includes its extensions (§23.3 kicks inside the logout window, §25.9 quit variants). For "
             "each §12 second-table row citing §22–§25 (D04-B13, P02-B28, D03-B6, Z11-B32, D03-B11, Z07-B2, P02-B36 / "
             "D04-B13) set that entry's evidence to *(captured)* with the §.",
             "Sequence index (README §3): add *(captured)* and the capture-validation § to the steps §11's batch-4 rows "
             "confirm (create refusal, both renames, tutorial skip, zone down, back to select, quit, zone connection "
             "lost, zone kill, skill book, empower, stat points, reset capsules, skill saves, cast abort, ground target, "
             "toggle, abstate reset, damage over time, death and revive by skill), and apply the corrected ones (W01 §5.1 "
             "/ Z01 §8.1 quit with four saves when the zone handles the WM's kick first and one when it handles the client's "
             "own `0x0C18 {0}` first (§25.9), Z01 §8.3 the 10-s Kickout timer and StoreType 3, Z01 §8.4 10-min "
             "auto-save).",
             "Check every README citation of capture-validation still points at the right section (batch 4 put §22–§25 "
             "before §11; §11–§15 kept their numbers).",
             "Run `tools/protocol-re/regen.sh`. Record per README table how many rows were added or changed, and every "
             "§13 row left out with the reason, in `docs/knowledge/X06.md`."],
      done="Every capture-validation §13 batch-4 row not owned by X02 has a README §5 row or a stated reason in "
           "`docs/knowledge/X06.md`; P02-B33 … B40 are in the register; the batch-4 §12 second-table entries carry "
           "*(captured)*; the batch-4 §11 flows are marked in README §3."),
 dict(id="X07", phase=3, title="Capture scenarios and ratings after capture batch 4: X02's recurring re-run (added by P02)",
      out="docs/plan/capture-scenarios.md + docs/review/confidence.md (both updated in place) + docs/knowledge/X07.md",
      scope=[], deps=["P02 (batch 4)", "X05"],
      goal="X05 re-ran X02 after capture batch 3 and is done. The fourth batch recorded scenario 24 (skills, abstates, stat "
           "points), the character-select steps of scenario 37 (`s37b`: create and rename refusals, rename right, zones "
           "down) and scenario 38 (session loss, kicks, zone kills). P02 checked them (capture-validation §22–§25), found "
           "scenario notes that did not match what was recorded (§13 rows owned by X02, \"batch-4 follow-up\") and "
           "listed what is still open (§14 bullets starting \"Batch 4\", §15 rows naming X07). Do X02's re-run for "
           "batch 4: result lines, fixed scenario texts, scenarios for what is still open, ratings. This item edits "
           "X02's two output files in place; it does not touch the owners' pseudocode.",
      steps=["Read capture-validation §1 (batch-4 rows), the §13 rows owned by X02 with status \"batch-4 follow-up\" "
             "(4 rows: `s37b` step 2, `s38` steps 1–6, `s24` start / steps 1–3, `s24` steps 4–8), the §14 bullets "
             "starting \"Batch 4\" and the §15 rows naming X07 (outline with `sect.py`); do not re-derive them.",
             "Results: under scenarios 24, 37 and 38 (`capture-scenarios.md` §3.24, §3.37, §3.38) add a line \"Result "
             "(P02 batch 4)\": each prediction confirmed / disproved / not reached, with the capture-validation §; "
             "replace scenario 24's \"notes but no capture\" state line.",
             "Fix the scenario texts §13 names: the maintenance message of `s37b` step 2 comes from the tutorial skip "
             "(P02-B33), not the rename; `s38` step 2's in-game quit is missing and step 1 ran twice; the `s24` notes' "
             "STR values (DB 63, no STR total for free points), `&resetabstated` (invalid command), `&sethp 1` (no "
             "death; the poison stops at 1 HP), one Revive cast, assist without `0x243E`. Make the scripts copy their "
             "`-db.txt` next to the capture (`s38` lost it).",
             "Open after batch 4, one scenario (or a step added to an existing one) each, with setup, steps, prediction "
             "and what disproves it: a second `0x1001` with the stale \"RouT\" copy (P02-B33); the 2016 "
             "`p_Char_Rename` on a DB with the 2016 procedure (duplicate → 0xD1); a zone-initiated disconnect of a "
             "logged-in player (`&kickout` or an SHN mismatch: `0x0C1A` with a real `usrregnum`); an empower request "
             "with two learned steps of one line (Z23-B8: which `skill` the client names); the server refusals the "
             "client pre-empted (`0x4814` 0x882–0x889, `0x105F` / `0x1065` 0xAC2–0xAC7, `0x9009` / `0x900A`); a toggle "
             "kept on past its 23-min icon timer (P02-B39) and a toggle with a lower learned step (Z23-B1); the skill-save "
             "columns against a DB snapshot with the cool-time column; `0x243E NC_BAT_ASSIST_REQ` (never sent by the "
             "2016 client: state it if no client path sends it).",
             "Ratings (`docs/review/confidence.md` §2): re-run `docs/plan/status/X02-rate.py`, then check by hand the "
             "sections batch 4 confirms or corrects (§11 rows from \"Character create refused\" on, §13 batch-4 rows) and "
             "update the hand ratings (`X02-rate-hand.py`).",
             "Record the changes in `docs/knowledge/X07.md`."],
      done="Scenarios 24, 37 and 38 have result lines for batch 4; the four §13 X02 rows of batch 4 are fixed in the "
           "scenario texts; every §15 row naming X07 maps to a scenario number or a stated reason in "
           "`docs/knowledge/X07.md`; confidence ratings re-run after batch 4."),
 dict(id="P06", phase=2, title="Protocol README: the flows of capture batch 5 (added by P02)",
      out="docs/protocol/README.md (corrected in place) + docs/knowledge/P06.md", scope=[], deps=["P05", "P02 (batch 5)"],
      goal="P05 brought `docs/protocol/README.md` §2 in line with capture batch 4 and is done. Batch 5 (captures `s46`, "
           "`s45`, `s52`; capture-validation §26–§28) contradicts one README statement and captured flows README §2 / §3 "
           "describe only from the code or not at all: a rename onto a taken name goes through with `0xD0` (P02-B42; "
           "README §2.6 says the CharDB refuses it, *inferred*), the second `0x1001` after a tutorial skip is refused "
           "by the map lookup until a new list, a zone kick sends `0x0C1A` with the user number and the client gets "
           "`0x0C17 {0x68B}`, the SHN refusal sends `0x1804 {0x147, idx}` with `0x0C1A {0, 0, 0x68E}` and the client "
           "returns to the login screen, the unknown-name whisper gets `0x200E {0x0F69}`. Bring the README up to date "
           "with batch 5.",
      steps=["Read capture-validation §11 (rows from \"Split-and-merge, onto a full stack\" on), §27.5, §28.2–§28.6, "
             "§12 rows P02-B41 … B43 and the \"(batch 5)\" rows of the Corrections table in `docs/knowledge/P02.md` "
             "(outline with `sect.py`, then the sections); do not re-read code: P02's rows give the `@ FUN_…` and the "
             "evidence.",
             "README §2.6 (free rename): replace \"the CharDB answers it for a taken name *(inferred)*\" with the captured "
             "2016 behaviour (no name check in the WM `fc_NC_AVATAR_RENAME_REQ` @ FUN_0041a640, the Character server's "
             "`0x1411` handler @ FUN_00436030 or the 2016 `p_Char_Rename`; `0xD0` and two characters of one name, "
             "**(original bug) P02-B42**, capture-validation §28.3).",
             "README §2.7 (character login refused): add that every further `0x1001` of the same WM session after the "
             "skip gets `0x1002 {0x145}` in 4 ms without the tutorial round trip (map lookup in "
             "`fc_NC_CHAR_LOGIN_REQ` @ FUN_00422be0) until the list is reloaded in a new WM session (§28.2).",
             "README §2.4 / §3.2: a zone-initiated kick of a logged-in player (`&kickout`: zone `0x0C1A {usrregnum, "
             "wldmanhandle, 0x68B}` → WM `0x0C17 {0x68B}` → client \"Disconnected from the server.\", `0x0C18 {0}`, two "
             "`0x0C19`; §28.4) and the SHN refusal at the map login (`0x1804 {0x147, idx}` with `0x0C1A {0, 0, 0x68E}`, "
             "no `0x0C17`, the client closes the WM connection and returns to the login screen; idx = the "
             "`CShnDataFileCheckSum` table index, 32 = MapViewInfo; §28.6); the `0x200E {0x0F69, receiver}` row if "
             "§3.2 lists the chat packets (§27.5). Mark each *(captured)* with the capture-validation §.",
             "Keep the README a sketch: link to the pseudocode for detail. Record every change (old → new, with source) in "
             "`docs/knowledge/P06.md` so X08 / X01 can cite it; run `tools/protocol-re/regen.sh`."],
      done="README §2.4 / §2.6 / §2.7 and §3 agree with capture-validation §27.5 and §28.2–§28.6; every changed statement "
           "is listed in `docs/knowledge/P06.md`."),
 dict(id="X08", phase=3, title="Integration update: P02's capture batch 5 (corrections, bugs P02-B41 … B43, captured "
                               "evidence) into the README register and the superseded-statements list (added by P02)",
      out="docs/pseudocode/README.md + docs/knowledge/X08.md", scope=[],
      deps=["X06", "P02 (batch 5)"],
      goal="X06 brought P02's batch 4 into `docs/pseudocode/README.md` (superseded statements §5, bug register §6, "
           "sequence index §3) and is done. Batch 5 (captures `s46`, `s45`, `s52`; capture-validation §26–§28) added "
           "P02-B41 … B43, an extension of P02-B33, 7 correction rows for done items (capture-validation §13 rows with "
           "status \"→ X08\": Z04 §4.1 exchange branch, D03 §3.3 log tail, Z11 §4.2 `&mb` count, Z02 §4 client emote "
           "sends, D02 §3.5 rename onto a taken name, Z11 §4.5 `&kickout` notice, Z01 §5.2 DataFail log and the "
           "wrong-length crash), captured evidence for other items' bugs (§12 second table, rows citing §26–§28) and 15 "
           "confirmed or corrected flows (§11 rows from \"Split-and-merge, onto a full stack\" on). Bring the README up "
           "to date with batch 5, as X06 did for batch 4. This item edits X01's README sections in place; it does not "
           "touch the owners' pseudocode.",
      steps=["Read capture-validation §11 (batch-5 rows), §12, §13 (rows with status \"→ X08\") and the \"(batch 5)\" "
             "rows of the Corrections table in `docs/knowledge/P02.md` (outline with `sect.py`, then the sections); do "
             "not re-read code: P02's rows give the `@ FUN_…` and the evidence.",
             "Superseded statements (README §5): one row per §13 row with status \"→ X08\", in §5's row format (owner "
             "document and §, old statement, correct statement with `@ FUN_…`, source `P02; capture-validation §n`).",
             "Bug register (README §6): add P02-B41 … P02-B43 from capture-validation §12 (first table) in the register's "
             "row format and extend P02-B33's entry (the second `0x1001` of the session, §28.2). For each §12 "
             "second-table row citing §26–§28 (D03-B11, P02-B16, Z04-B2, Z11-B12, Z02-B2, P02-B29, P02-B19, P02-B36, "
             "P02-B28, P02-B35, Z09-B54, Z11-B6) set that entry's evidence to *(captured)* with the §.",
             "Sequence index (README §3): add *(captured)* and the capture-validation § to the steps §11's batch-5 rows "
             "confirm (split-and-merge and exchange, buy-back onto an empty cell, buy-back refusals, the bystander view "
             "of walk / emotes / shout / mob swings / cast abort / same-zone revive, whisper fail, spam filter, the "
             "second `0x1001` after a skip, the zone kick on one and across zones, the SHN refusal), and apply the "
             "corrected ones (D02 §3.5 rename onto a taken name, Z01 §5.2 DataFail).",
             "Check every README citation of capture-validation still points at the right section (batch 5 put §26–§28 "
             "before §11; §11–§15 kept their numbers).",
             "Run `tools/protocol-re/regen.sh`. Record per README table how many rows were added or changed, and every "
             "§13 row left out with the reason, in `docs/knowledge/X08.md`."],
      done="Every capture-validation §13 row with status \"→ X08\" has a README §5 row or a stated reason in "
           "`docs/knowledge/X08.md`; P02-B41 … B43 are in the register and P02-B33 is extended; the batch-5 §12 "
           "second-table entries carry *(captured)*; the batch-5 §11 flows are marked in README §3."),
 dict(id="X09", phase=3, title="Capture scenarios and ratings after capture batch 5: X02's recurring re-run (added by P02)",
      out="docs/plan/capture-scenarios.md + docs/review/confidence.md (both updated in place) + docs/knowledge/X09.md",
      scope=[], deps=["P02 (batch 5)", "X07"],
      goal="X07 re-ran X02 after capture batch 4 and is done. The fifth batch recorded scenarios 46 (items: stacking, "
           "buy-back onto an empty cell, refusals; X05), 45 (second client in sight II; X05) and 52 (character select "
           "and session II: stale tutorial copy, rename onto a taken name, `&kickout`, SHN refusal; X07); scenario 39 "
           "has a notes file but no capture. P02 checked them (capture-validation §26–§28), found scenario texts that "
           "did not match what was recorded (§13 rows with status \"→ X09\") and listed what is still open (§14 "
           "bullets starting \"Batch 5\", §15 rows naming X09). Do X02's re-run for batch 5: result lines, fixed "
           "scenario texts, scenarios for what is still open, ratings. This item edits X02's two output files in "
           "place; it does not touch the owners' pseudocode.",
      steps=["Read capture-validation §1 (batch-5 rows and paragraph), the §13 rows with status \"→ X09\" (3 rows: "
             "scenarios 46, 45, 52), the §14 bullets starting \"Batch 5\" and the §15 rows naming X09 (outline with "
             "`sect.py`); do not re-derive them.",
             "Results: under scenarios 45, 46 and 52 (`capture-scenarios.md` §45, §46, §52) add a line \"Result (P02 "
             "batch 5)\": each prediction confirmed / disproved / not reached, with the capture-validation §; under "
             "scenario 39 state that it was not captured (notes only).",
             "Fix the scenario texts §13 names: scenario 46's money refusal and soul-stone refusals are the client's "
             "(texts 810 500 413, 978 272 565, 1 677 983 971; no `0x3059` / `0x5001`), the buy-back goes to the first "
             "empty cell; scenario 45: four hits, 970 units apart, three aborts each by a step, no way of the three "
             "sends `0x2022`; scenario 52: one appended byte crashes the zone at start (only a changed byte inside a "
             "row gives `0x1804 {0x147, idx}`), the zone hashes the decrypted buffer, step 2 started the renamed "
             "character.",
             "Open after batch 5, one scenario (or a step added to an existing one) each, with setup, steps, prediction "
             "and what disproves it: the zone refusals the 2016 client pre-empts (`0x366C`, `0x5005`, `0x3443`: state it "
             "if no 2016 client path reaches them), `irm_Exchange`'s `0x24a` (an exchange whose way back "
             "`iba_CanInvenReloc` refuses), `0x2022` / `0x2023` through the client's key function 0x6F (pause / resume "
             "an emote), `0x2020 {6}`, lookups by a name two characters share after P02-B42 (whisper, `&kickout`, party "
             "invite), the `s46` logout; scenario 39 again (record it).",
             "Ratings (`docs/review/confidence.md` §2): re-run `docs/plan/status/X02-rate.py`, then check by hand the "
             "sections batch 5 confirms or corrects (§11 rows from \"Split-and-merge, onto a full stack\" on, §13 rows "
             "\"→ X08\" / \"→ X09\") and update the hand ratings (`X02-rate-hand.py`).",
             "Record the changes in `docs/knowledge/X09.md`."],
      done="Scenarios 45, 46 and 52 have result lines for batch 5 and scenario 39 a not-captured line; the three §13 "
           "rows \"→ X09\" are fixed in the scenario texts; every §15 row naming X09 maps to a scenario number or a "
           "stated reason in `docs/knowledge/X09.md`; confidence ratings re-run after batch 5."),
]


def entries(bin_, parser, depts):
    H = json.load(open(f"{E}/{bin_}/handlers.json"))
    src = open(f"{E}/{bin_}/decomp.c", encoding="utf-8", errors="replace").read()
    sizes = {m.group(1): m.group(2).count("\n") for m in
             re.finditer(r"^//==== FUNC ([0-9a-f]{8}) \S+\n(.*?)(?=^//==== FUNC |\Z)", src, re.S | re.M)}
    out = []
    for t in H["tables"]:
        if parser not in t["parser"]: continue
        for e in sorted(t["entries"], key=lambda e: e["op"]):
            if depts is not ALL and e["dept"] not in depts: continue
            c = cat.get(f"0x{e['op']:04x}", {})
            out.append((t["parser"], e, c.get("name"), sizes.get(e["handler"][-8:], 0)))
    return out


GENERIC = """## How to work

**One part per session.** Context is re-read on every turn, so a long session costs far more than several short ones.
{parts} At the start, read `docs/plan/status/{id}.md` (its **State** line and **Working notes**) and take the first part
not done (no status file: part 1). Do only that part, close it (step 6) and end the session, even if context is left.

1. `AGENTS.md` is already in your context (do not re-read it); follow its **Context budget** section. Part 1 only: read
   `docs/plan/00-master-plan.md`. Later parts: the status file's working notes replace it; do not re-derive what they record.
2. Read `docs/pseudocode/FORMAT.md`: the format and depth to match (not the whole `login-server.md`).
3. Read what exists for this part: the `docs/knowledge/*.md` sections of the items you depend on that touch it, and the
   `opcodes-*.md` / `packets-*.md` rows of its opcodes (one `rg -i -M 300 -e 0x<op> -e 0x<op> …
   docs/protocol/packets-<bin>.md` for all of them). For docs over ~15 KB and every `§` reference above, run
   `python3 -I tools/protocol-re/sect.py <file>` for the outline, then `sect.py <file> <§|regex>` for what you need. This
   includes your own output file: from part 2 on, never read it whole; use its outline and the sections you extend.
   For each packet, also look up the official name and struct in the 2017 client PDB:
   `python3 -I tools/protocol-re/pdb.py Files/Client/2017/Fiesta.pdb types '^PROTO_NC_(<NAME>|<NAME>)$'` (one regex for
   several; field names, offsets, sizes; also server-internal packets and shared enums/structs). It is a newer build:
   confirm against the 2016 code and mark unconfirmed PDB facts *(pdb2017)*. Read `docs/knowledge/C02.md` if it exists.
4. For the handlers of this part, in scope-table order, a few related handlers (one opcode family) at a time:
   - read them together: `python3 -I tools/protocol-re/clean.py re-data/exports/<bin> tools/protocol-re/names/<bin>
     <addr> <addr> …` (the only way to read code; never `sed`/`cat` on `decomp.c`). Registrations and sends of all of
     them in one query: `jq -c '.tables[].entries[] | select(.handler|IN("<FUN_…>","<FUN_…>"))' re-data/exports/<bin>/handlers.json`
   - follow the callees that carry the logic (skip logging/profiling/container boilerplate), again several per `clean.py` call
   - write their pseudocode blocks (`@ FUN_…`), with field names, checks, state changes, replies, error codes
   - for client-facing packets, check the client handler (C01's `re-data/client-handlers.json` / `docs/knowledge/C01.md`
     if available; otherwise search the client export) and resolve codes via `docs/protocol/client-error-codes.json`
   - record new names (`names/<bin>/{id}.json`) and verified layouts (`docs/protocol/annotations/{id}.json`)
5. Beyond the handlers, document the subsystem itself: data structures, tables loaded, timers, invariants. Write each
   in the part that first reaches it and note it in the working notes so later parts link to it instead of re-reading.
   **Be exhaustive within your item.** The scope table is the starting point, not the boundary: follow every callee,
   branch, error path, timer, table and packet these handlers reach, plus the matching client handlers and DB procedures,
   until what remains clearly belongs to another item. The sweep part then checks for what was missed: `rg` your
   subsystem's strings, SHN tables and opcodes (`opcodes.json`) for functions never opened, check every caller and callee
   of the documented functions, and every unnamed `FUN_` left in the text, and run
   `python3 -I tools/protocol-re/coverage.py {id}` (functions reachable from your handlers that no doc cites yet,
   largest first; cite each one you cover as `FUN_…` so it counts). Stopping early because the handlers are
   "done" is the most common gap in past items; reviews keep finding uncovered cases that were in scope.
6. Close the part: update `docs/plan/status/{id}.md`. Its first line is `**State:** part <n> of <total> done` (or
   `**State:** done` after the review part). Then: done handlers per part, remaining work, and **Working notes**: only what
   later parts need and cannot cheaply re-read (struct and member offsets, helper names and meanings, shared state, open
   questions for a later part, next free bug ID `{id}-B<n>`). Keep the notes short; every later session reads them.
   Commit on the current branch (`{id} part <n>: <what>`), then end the session. If context runs low before the part is
   done, finish the handler in hand, record the rest of the part as remaining, commit and end the same way.
   **Re-split when the parts are wrong.** The Parts table is sized from handler lines only; work outside the handlers
   (internals, tables, timers, the "also" list) is not counted. If a part still open looks too big for one session (or
   two are small enough to merge), write the new split as a **Parts** list in the status file (e.g. add part `3b`, with
   what it covers) and use its count as `<total>`; from then on the status file's list replaces the table. Do not edit
   this plan file (it is generated).
7. Sweep part, at the end: run `tools/protocol-re/regen.sh`, write `docs/knowledge/{id}.md` (facts others need), add the
   original-server bugs table and an "uncertain / not reconstructed" section to your output.
8. Also end your output with a "Coverage boundary" section: one row per thing you found but did not cover (function,
   packet, table, behaviour) with an argument why it is out of bounds for this item: either the existing item that
   covers it (ID and the line of its plan or scope table that includes it) or, if no item does, a new follow-up item
   you create yourself (after `rg` in `docs/plan/items/*.md` and `make_plans.py` confirms no item, open or planned,
   covers it): add a `dict(id=…)` to `ITEMS` in `tools/protocol-re/make_plans.py` (next free ID of its area; title ends
   "(added by {id})"; goal, steps naming the functions/§ to start from, done), run `python3 -I tools/protocol-re/make_plans.py`,
   add its row to the item table and the order list in `docs/plan/00-master-plan.md`, list it in
   `docs/plan/status/{id}.md` under "Follow-up items created", and name it in the boundary row (example: commit bcb1031, W05 added by W04). "Too large" or "ran out of context" is not out of bounds: that is unfinished work for the status file.
   **Never hand work to a finished item.** Before naming an item, read the first line of its status file. If it is
   `**State:** done`, name it only when its output already documents the thing (cite the §); nobody will reopen it.
   Otherwise: a small gap (a function, a packet layout, a code meaning; under ~1 h of work) you document now in your
   own output; a larger one becomes a new follow-up item as above, never a row pointing at the done item.
9. Review part: **review with fresh context** before marking the item done. The reviewer must not share your reading
   of the code. The review task is `docs/plan/review-prompt.md` (with `<ID>` = `{id}`).
   - If your agent tool can start a fresh-context subagent (not a fork of your session), give it that file's text with
     `<ID>` replaced by `{id}`, and wait for its numbered findings list.
   - Otherwise stop here: set the status file to "awaiting review" and end the session. The user runs the review as a
     separate session ("Review work item {id} as described in `docs/plan/review-prompt.md`") and then resumes this item,
     whose session finds the findings under "Review findings" in `docs/plan/status/{id}.md`.
   Fix every finding in your files, or write in `docs/plan/status/{id}.md` under "Review" why you reject it. Re-run
   `coverage.py {id}` and `regen.sh`, record the before/after coverage line in the status file, then mark the item done.

## Rules

- Only write your own files: `{out}`, `docs/knowledge/{id}.md`, `docs/plan/status/{id}.md`,
  `tools/protocol-re/names/<bin>/{id}.json`, `docs/protocol/annotations/{id}.json`.
  Exception: creating a follow-up item (step 8) adds to `make_plans.py`, `docs/plan/items/` and `00-master-plan.md`;
  never change existing items there.
- Mark deductions *(inferred)*. Never invent names; derive them from strings, client texts, or label them as ours.
- Never leave a half-documented handler at the end of a session; list unfinished ones in the status file.
"""


PART_LINES = 2500  # handler-body lines per session part; W04 (~8.8k) ran with a median context of 200–250k in one session


def parts_of(rows):
    """Split scope rows into session parts: whole departments (one subsystem across all parsers), packed in dept order
    up to PART_LINES; a department larger than 1.5 × PART_LINES is split by opcode. Returns ({(bin, parser, op): part},
    [(dept label, handlers, lines)])."""
    groups = {}
    for bin_, (p, e, n, sz) in rows:
        groups.setdefault((bin_, e["dept"]), []).append((bin_, p, e, sz))
    chunks = []
    for (bin_, d), g in sorted(groups.items()):
        g.sort(key=lambda r: r[2]["op"])
        if sum(r[3] for r in g) <= 1.5 * PART_LINES:
            chunks.append(g); continue
        cur = []
        for r in g:
            if cur and sum(x[3] for x in cur) + r[3] > PART_LINES:
                chunks.append(cur); cur = []
            cur.append(r)
        chunks.append(cur)
    packed = []
    for c in chunks:
        if packed and sum(r[3] for r in packed[-1]) + sum(r[3] for r in c) <= PART_LINES:
            packed[-1] += c
        else:
            packed.append(list(c))
    part, summary = {}, []
    for i, c in enumerate(packed, 1):
        depts = []
        for bin_, p, e, sz in c:
            part[bin_, p, e["op"]] = i
            lab = f"{e['dept']} {DEPT.get(e['dept'], '?')}"
            if lab not in depts: depts.append(lab)
        summary.append((", ".join(depts), len(c), sum(r[3] for r in c)))
    return part, summary


def render(it):
    lines = [f"# {it['id']}: {it['title']}\n",
             f"**Phase:** {it['phase']} · **Depends on:** {', '.join(it['deps']) or 'nothing (can start immediately)'} · "
             f"**Output:** `{it['out']}`\n"]
    if it.get("goal"): lines += ["## Goal\n", it["goal"] + "\n"]
    if it.get("steps"):
        lines += ["## Item-specific guidance\n"] + [f"- {s}" for s in it["steps"]] + [""]
    if it.get("done"): lines += ["## Done when\n", it["done"] + "\n"]
    nparts = 0
    if it["scope"]:
        scoped = [(bin_, parser, depts, entries(bin_, parser, depts)) for bin_, parser, depts in it["scope"]]
        part, parts = parts_of([(bin_, r) for bin_, _, _, rows in scoped for r in rows])
        nparts = len(parts)
        lines.append("## Parts (one session each, see \"How to work\")\n")
        lines.append("| Part | Depts | Handlers | Lines |\n|---|---|---|---|")
        for i, (dl, n, sz) in enumerate(parts, 1):
            lines.append(f"| {i} | {dl} | {n} | {sz} |")
        if nparts == 1:  # small item: a separate sweep session would cost more than it saves
            lines[-1] = lines[-1].replace("| 1 | ", "| 1 | handlers, then sweep and close (steps 5, 7, 8): ", 1)
            lines += ["| 2 | review (step 9) | | |", ""]
        else:
            lines += [f"| {nparts + 1} | sweep and close (steps 5, 7, 8) | | |", f"| {nparts + 2} | review (step 9) | | |", ""]
        lines.append("## Scope: registered handlers\n")
        total, tl = 0, 0
        for bin_, parser, depts, rows in scoped:
            if not rows: continue
            dlabel = "all depts" if depts is ALL else ", ".join(f"{d} {DEPT.get(d, '?')}" for d in depts)
            lines.append(f"### `{bin_}` · {parser or 'all parsers'} · {dlabel}\n")
            lines.append("| Opcode | Dept/Cmd | Name (from binaries) | Handler | Lines | Parser | Part |\n|---|---|---|---|---|---|---|")
            for p, e, n, sz in rows:
                lines.append(f"| `0x{e['op']:04x}` | {e['dept']}/{e['cmd']} | {n or '?'} | `{e['handler']}` | {sz} | {p.split('::')[-1]} | {part[bin_, p, e['op']]} |")
                total += 1; tl += sz
            lines.append("")
        lines.insert(2, f"**Size:** {total} handlers, ~{tl} decompiled lines in handler bodies (callees add more)\n")
    parts_txt = ("Part 1 is the handlers plus the sweep, part 2 the review (see the **Parts** table)." if nparts == 1 else
                 f"Parts 1–{nparts} are in the **Parts** table (column *Part* of the scope table); part {nparts + 1} is the "
                 f"sweep, part {nparts + 2} the review." if nparts else
                 "This item has no scope table: in the first session, split the work into parts of similar size (about "
                 f"{PART_LINES} decompiled lines each, plus a sweep part and a review part) and write the list into the status file.")
    lines.append(GENERIC.format(id=it["id"], out=it["out"], parts=parts_txt))
    return "\n".join(lines)


os.makedirs(f"{R}/docs/plan/items", exist_ok=True)
os.makedirs(f"{R}/docs/plan/status", exist_ok=True)
summary = []
for it in ITEMS:
    txt = render(it)
    open(f"{R}/docs/plan/items/{it['id']}.md", "w").write(txt)
    m = re.search(r"\*\*Size:\*\* (\d+) handlers, ~(\d+)", txt)
    summary.append((it["id"], it["phase"], it["title"], ", ".join(it["deps"]) or "–", m.group(1) if m else "–", m.group(2) if m else "–"))
json.dump(summary, open(f"{R}/docs/plan/items/_summary.json", "w"), indent=1)
for s in summary: print(*s, sep=" | ")
