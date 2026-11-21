# Client ⇄ Server Protocol Specification (recovered from binaries)

Recovered by static analysis of the shipped server binaries in `Files/Server/2016/`, then checked against packet
captures of a 2016 client on these servers ([capture-validation.md](capture-validation.md), work item P02). In this
file **observed** means read in the decompiled code, **inferred** means deduced from it, and *(captured)* means seen
on a real connection (the strongest evidence; where a capture and the code disagreed, the text below follows the
capture and cites the code that explains it). Open questions are listed in [Unknowns](#unknowns). Statements changed
after the captures are listed with their old wording in [`docs/knowledge/P04.md`](../knowledge/P04.md).

| Binary | SHA-256 (prefix) | Role | Client port |
|---|---|---|---|
| `Files/Server/2016/Login/3LoginServer2.exe` | `3513309c4422237f` | Login server | 9010 |
| `Files/Server/2016/w00_WorldManager/4WorldManagerServer2.exe` | `903d73807b77a30f` | World manager (WM) | 9110 |
| `Files/Server/2016/w00_Zone0{0..3}/5ZoneServer2.exe` (all four identical) | `a18129fd83d214df` | Zone (map) server | 9210 / 9212 / 9214 / 9216 |
| `Account`, `AccountLog`, `w00_Character`, `w00_GameLog` | – | DB servers (internal only) | – |

Ports come from `9Data/ServerInfo/ServerInfo.txt`. `SERVER_INFO` rows with type `20` are the client
listeners. The Login accept loop handles type `0x14` (20) sockets as clients and sends them the seed
packet (`3LoginServer2.exe` `FUN_004022a0`). Type `8` rows are bound to 127.0.0.1 and carry server links.

Generated per-server opcode tables (every handler, with the packets it sends):

- [opcodes-login.md](opcodes-login.md): 12 client handlers
- [opcodes-wm.md](opcodes-wm.md): 167 client handlers
- [opcodes-zone.md](opcodes-zone.md): 245 client handlers
- [opcodes.json](opcodes.json): all 2,572 opcodes sent or received in the 7 binaries or handled by the client
  (official names from the 2016 server PDBs, receivers)

Per-packet field layouts (what each packet contains, with values or where each value comes from):

- [packets-login.md](packets-login.md), [packets-wm.md](packets-wm.md), [packets-zone.md](packets-zone.md):
  generated layouts for every client handler (fields read, value checks) and every client-bound send site
  (fields written, constants, source expressions, `in(0xOP)+N` data flow). Hand-verified layouts with
  field names appear first in each section, marked **Verified layout**.
- [client-error-codes.json](client-error-codes.json): all 479 error codes the client knows, with the
  message it shows. Extracted from the 2016 client `Fiesta.bin` (`FUN_00416430`) and its
  `TextData*.shn` tables (`tools/protocol-re/errcodes.py`, `shn.py`).
- [annotations.json](annotations.json): the first hand-verified layouts (38 packets plus the `WORLD` and
  130-byte `AVATAR` structs); each work item adds its own in `annotations/<ID>.json` (about 1,700 more). Add a layout
  there as you confirm its fields, then regenerate (`tools/protocol-re/regen.sh`).
- [pdb2016-layouts.json](pdb2016-layouts.json): every packet struct of the 2016 server PDBs (S01), ranked below the
  annotations.

---

## 1. Transport

All three client-facing servers share one network library (`CSocket_IOCP`, `CSendPacket`), with the same
framing and the same cipher table.

### 1.1 Framing (observed, *captured*)

```
short packet  (body < 256 bytes):  [len:u8]               [body: len bytes]
long packet   (body ≥ 256 bytes):  [0x00] [len:u16 LE]    [body: len bytes]

body = [opcode:u16 LE] [payload]
len  = 2 + payload length       (the length prefix is not counted)
```

- `CSendPacket::SetSize` (Login `FUN_004122a0`) picks the short form when `payload+2 < 0x100`, otherwise the
  long form. Payloads of 0x1FFC bytes or more are rejected. Zone `ProtocolPacket::pp_SendPacket`
  (`FUN_004c89c0`) applies the same rule, with a limit of `< 0x1FFD`.
- Writes are queued in 0x2000-byte IO buffers. Several packets can share one TCP write.
- Hand-built packets in the code show the same layout, for example `{04, 07 08, seed_lo, seed_hi}` is
  `len=4, opcode=0x0807, u16 seed`.
- *(captured)* Every captured packet parses with this rule; the long form appears exactly for bodies ≥ 256 bytes
  (`0x0C5A`, `0x0C0F`, zone `0x1801`, large `0x1C09` / `0x581D`), and the servers put several packets in one TCP
  segment (capture-validation §2.1).

### 1.2 Opcode (observed)

```
opcode = (department << 10) | command          department: 6 bits, command: 10 bits
```

The dispatcher reads `dept = op >> 10` and `cmd = op & 0x3FF` (Login `FUN_00406680`). Handlers live in
`PROTOCOLFUNCTIONTEMPLETE<T>`, a `[cmd][dept]` table filled by `pft_Store(dept, cmd, handler)`. One table
exists per peer type (client, WM, account DB, and so on). An opcode with no handler, or one sent in the
wrong session state, is logged as `Invalid Client Session ...` and the session is closed (`*session = 3`).

Department prefixes from the handler names: 2 `NC_MISC`, 3 `NC_USER`, 4 `NC_CHAR`, 5 `NC_AVATAR`,
6 `NC_MAP`, 7 `NC_BRIEFINFO`, 8 `NC_ACT`, 9 `NC_BAT`, 10 `NC_OPTOOL`, 12 `NC_ITEM`, 13 `NC_ITEMDB`,
14 `NC_PARTY`, 15 `NC_MENU`, 17 `NC_QUEST`, 18 `NC_SKILL`, 19 `NC_TRADE`, 20 `NC_SOULSTONE`, 21 `NC_FRIEND`,
22 `NC_KQ`, 23 `NC_WT`, 24 `NC_CT`, 26 `NC_BOOTH`, 27 `NC_SCENARIO`, 29 `NC_GUILD`, 35 `NC_MINIHOUSE`,
37 `NC_HOLY`, 38 `NC_GUILD`(academy), 41 `NC_INSTANCE`, 43 `NC_DICE`, 44 `NC_RAID`, 47 `NC_GAMBLE`,
49 `NC_COLLECT`, 51 `NC_MOVER`, 53 `NC_PET`. See `opcodes.json` for the rest.

### 1.3 Encryption (observed, *captured*)

- **Client → server only.** Each received body (opcode + payload, not the length prefix) is XORed in
  place before dispatch (Login `FUN_0040b170`, WM `FUN_0045d4b0`, Zone `FUN_00631120`). Server → client traffic is plaintext: the send path (`CSocket_IOCP::Send`) has no cipher.
- Keystream: a fixed **499-byte table**, byte-identical in Login (`0x430430`), WM (`0x497840`) and Zone
  (`0x871608`). The table is reproduced in [Appendix A](#appendix-a-xor-table).
- The per-session index starts at `seed % 499`, advances by one per byte across packets, and wraps to 0
  after index 498.

```python
def decrypt(body: bytearray, state):         # state.idx starts at seed % 499
    for i in range(len(body)):
        body[i] ^= XOR499[state.idx]
        state.idx = 0 if state.idx >= 498 else state.idx + 1
```

*(captured)* On all three servers every client body decrypts with this rule from the stream's `0x0807` seed, across
packets; server → client traffic is plaintext (capture-validation §2.2). Server ↔ server links carry no seed and no
cipher (capture-validation §7.1); they open with a handshake instead: the listener sends `0x0801
NC_MISC_S2SCONNECTION_RDY` on accept, the connector `0x0802 NC_MISC_S2SCONNECTION_REQ {echo_data, server_to_id,
server_from_id, world, zone, key}`, the listener `0x0803 NC_MISC_S2SCONNECTION_ACK {echo_data, error 0}`
(capture-validation §17.2; W05 §1.4, Z01 §3.3).

### 1.4 Seed: `0x0807` NC_MISC_SEED_ACK (observed, *captured*)

Every client-facing server sends the seed **unasked, right after accept**, as the raw 5 bytes `{04, 07 08, u16 seed}`;
the server's decrypt index for that session starts at `seed % 499` (§1.3). The client never asks for it.

| Server | Sent by (on accept) | Seed value |
|---|---|---|
| Login | `LoginServer::ProcessConnect` (FUN_004022a0) → `CLoginClientSession::Send_NC_MISC_SEED_ACK` (FUN_00409610) | per-process counter `m_ClientSeed`: `rand()` after `srand(time)` at start (ctor FUN_00409680), then `(m_ClientSeed + 1) % 499` in `CLoginClientSessionManager::ActiveSession` (FUN_00409700) per accepted client (L01 §2) |
| WM | `WorldManagerServer::ProcessConnect` (FUN_00405860) → `Send_NC_MISC_SEED_ACK` (FUN_00430550) | same scheme in `CWMClientSessionManager::ActiveSession` (FUN_00438a60; W05 §1.4, §4.3) |
| Zone | `ZoneServer::zs_connect` (FUN_005aa840) → `ClientSession::Send_NC_MISC_SEED_ACK` (FUN_0045b120) | `ShinePlayer::so_EncSeedSet` (FUN_0054f660, vtable slot `0x2f4`): global `seed = seed + 1`, `0` once it reaches 499; also sets the player's decrypt index. So the first client of a zone process gets 1, then consecutive values (Z18 §1.3) |

*(captured)* Login seeds 355–368 and WM seeds 264–271 rise by one per connection; zone seeds per process are 1, 2, 3 …
(capture-validation §2.3).

The zone also registers client `0x0806 NC_MISC_SEED_REQ` (`sp_NC_MISC_SEED_REQ`, FUN_00451a30), which answers
`0x0807` from a second counter `newseed` without moving the decrypt index (Z01 §5.1). The 2016 client never sends
`0x0806` *(captured)*, and the zone's session filter lets it through only in a state normal play never reaches, so the
path is dead (Z18 §1.3, original bug Z18-B2).

### 1.5 Heartbeat (observed, *captured*)

`0x0804 NC_MISC_HEARTBEAT_REQ` and `0x0805 NC_MISC_HEARTBEAT_ACK` are both empty. **The server starts them**: every
server session (client and server links alike) runs a check per main-loop pass: no packet received for 30 s → send one
`0x0804` (raw `02 04 08`); nothing at all received in the next 180 s → close the session. Any received packet resets
the timer. A failed `0x0804` send closes the session at once.

| Server | Check | Client-session notes |
|---|---|---|
| Login | `CheckHeartBeat` (FUN_00408f30; L01 §2) | a client before its login request (session mode 0 / 1) is closed for any `0x0804` / `0x0805` it sends, so a pre-login heartbeat cannot be answered (original bug L01-B11). Not reachable with the 2016 client: it opens the Login connection only when the login form is submitted and then polls `0x0C1B` every 10 s, so Login never sends it a heartbeat *(captured, capture-validation §16.2)* |
| WM | `CWMBaseSession::CheckHeartBeat` (FUN_0042fda0), via `ProcHeartBeat` (FUN_00430160; W05 §1.5) | `0x0804` exactly 30.0 s after the last client packet, repeated 30 s after each answer; the client answers within ~1–12 ms; 7 min on the character list without a close *(captured, capture-validation §4.4, §16.2)* |
| Zone | `ClientSession::CheckHeartBeat` (FUN_0045b110) → `ZoneBaseSession::CheckHeartBeat` (FUN_005a67c0; S02 §4.4, Z18 §1.4) | same 30 s / 180 s rule (the 300 the client override passes is ignored). The answer is accepted before `0x1803` too; during the first map load the client answers late (4.9 s), because its loader does not service the zone socket *(captured, capture-validation §5.5)* |

A received `0x0804` is answered with a bare `0x0805` (Login: raw bytes `02 05 08`); a received `0x0805` is accepted and
ignored. The 2016 client answers the server's `0x0804` with `0x0805` (`Net::ProcessNetMsg` FUN_006d2fa0, when its
heartbeat flag is on) and was never seen sending `0x0804` itself *(captured)*. It also sends **unsolicited `0x0805` to
the WM while it loads a map** (`World::LoadMap` FUN_006768c0 → FUN_006d2ef0, name *(pdb2017)*
`NetMgr::SendHeartBeat2WorldMgrServer`), which keeps the WM session alive during long loads (capture-validation §4.4).
Server ↔ server links use the same rule in both directions (capture-validation §7.1; `docs/pseudocode/README.md` §2.3).

---

## 2. Connection flow: which messages are sent when

A sketch of the normal path of a 2016 client, *(captured)* in every instance of P02's captures (message order and
timings: [capture-validation.md](capture-validation.md) §11; the cross-server detail, handler by handler, is in
[`docs/pseudocode/README.md`](../pseudocode/README.md) §3, cited below as **X01 §3.x**). `C` = client, `L` = Login,
`W` = WM, `Z` = zone, `A` = AccountDB, `AL` = AccountLogDB, `D` = CharDB. Heartbeats (§1.5) can come in at any point
and are left out.

```
Client                Login                AccountDB  AccountLog   WM                CharDB   Zone
  |-- TCP connect ----->|   (only when the login form is submitted)
  |<-- 0x0807 seed -----|   (on accept, §1.4)
  |-- 0x0C65 version -->|                                                   (state 0 → 1)
  |<-- 0x0C67 ok / 0x0C66 fail
  |-- 0x0C5A login ---->|-- 0x0C5B -->|                                     (state 1 → 2)
  |-- 0x0C04 XTrap ---->|   (same client tick as 0x0C5A)
  |<-- 0x0C05 ----------|   (at once)
  |                     |<-- 0x0C5C --|
  |<-- 0x0C09 error ----|  (fail; then disconnect)
  |                     |-- 0x0C5D ------------->|
  |                     |<-- 0x0C5E -------------|
  |                     |-- 0x0C16 kick → every WM (§2.5)
  |<-- 0x0C0A worlds ---|  (or 0x0C09 0x51)
  |-- 0x0C1B poll ----->|   (10 ms after 0x0C0A, then every 10.0 s while the list is shown)
  |<-- 0x0C1C ----------|
  |-- 0x0C0B world ---->|-- 0x0C0D ----------------------------->|
  |                     |<-- 0x0C0E -----------------------------|
  |<-- 0x0C0C WM ip, port, 32×u16 validate key
  |
  |== TCP connect to WM ====================================================>|
  |<-- 0x0807 seed ---------------------------------------------------------|
  |-- 0x0C0F world login (user, validate key) -------------------------------->|-- 0x0C60 → AccountDB
  |                                                             ...0x0C61 →  |-- 0x0C12 -->|
  |<-- 0x0C14 avatar list (or 0x0C15 error) --------------------------------|<-- 0x0C13 --|
  |-- 0x080D game time -------------------------------------------------------->|
  |<-- 0x080E {hour, minute, second} ----------------------------------------|
  |-- 0x1001 NC_CHAR_LOGIN_REQ (slot) --------------------------------------->|-- 0x1004 -->|
  |                                                                          |<-- blocks, 0x1005
  |<-- 0x1003 zone ip/port (or 0x1002 error) ------------------------------|-- 0x1036 -->|
  |<-- 0x7032, 0x7033, 0x7034 option data (~53 ms later) ------------------|
  |
  |== TCP connect to Zone =================================================================================>|
  |<-- 0x0807 seed (on accept, §1.4) ------------------------------------------------------------------------|
  |-- 0x1801 NC_MAP_LOGIN_REQ (wm handle, char name, 49 SHN checksums) ------------------------------------->|
  |-- 0x080D game time (same client tick) ------------------------------------>|
  |<-- 0x1804 fail (bad checksum)                                         WM <-- 0x104B ------------------------|
  |                                                                        WM --> 0x104C ---------------------->|
  |                                                                        WM <-- 0x101C -----------------------|
  |                                                                        WM --> blocks …, 0x101D ---------->|
  |<-- 15 blob copies 0x1038 … 0x441E ----------------------------------------------------------------------|
  |<-- 0x1802 NC_MAP_LOGIN_ACK (or 0x1804) -------------------------------------------------------------------|
  |-- 0x7004, 0x700C, 0x7C06 (same tick, on 0x1802) -------------------------->|
  |   … client loads the map …
  |-- 0x1803 NC_MAP_LOGINCOMPLETE_CMD + 0x2001, 0x200B ×3 [+ 0x302C, 0x3020] -------------------------------->|
  |-- 0x581B KQ list (same tick) ---------------------------------------------->|
  |<-- login burst (Z01 §6, one server tick), parameter refresh one tick later -------------------------------|
  |                                                                          |<-- 0x180C link end -----------|
  |<-- 0x180C burst: 0x1097, 0x1012, 0x9414, 0x5826, 0x10D9, 0x0849, 0x182A --|
```

### 2.1 Login server session states (observed, `FUN_00406680`)

| State | Accepted client opcodes | Transition |
|---|---|---|
| 0 (new) | only `0x0C65` | → 1 |
| 1 | only dept 3 with cmd `0x37` (`0x0C37`) or `0x5A` (`0x0C5A`) | → 2 |
| 2 | every opcode registered for `CParserClient` | – |

Anything else closes the session.

### 2.2 Steps of the login → WM → zone chain

| Step | Messages | What the captures show | Detail |
|---|---|---|---|
| Login: version, password | `0x0807`, `C 0x0C65` → `0x0C67`, `C 0x0C5A`, `C 0x0C04 NC_USER_XTRAP_REQ` → `0x0C05 NC_USER_XTRAP_ACK {1}`, A `0x0C5B` / `0x0C5C`, AL `0x0C5D` / `0x0C5E`, W `0x0C16`, `0x0C0A` | *(captured)* The client sends `0x0C04` right **after** its login request, in the same tick (client `On_NC_USER_CLIENT_RIGHTVERSION_CHECK_ACK` FUN_0046f470 calls the login request first); Login answers it at once, so `0x0C05` comes before `0x0C0A` (70–170 ms after `0x0C5A`). The XTrap key is not checked (L00-B5). The TCP connection is opened only when the login form is submitted. Wrong password: `0x0C09 {0x45}` ~50 ms after `0x0C5A`, the next try is a new connection | capture-validation §3.1, §16.1; X01 §3.3; `login-server.md` §4 |
| Login: token login | `0x0807`, `0x0C65` → `0x0C67`, `C 0x0C37 NC_USER_LOGIN_WITH_OTP_REQ {sOTP[32]}`, `C 0x0C04`, `0x0C0A`, `0x0C05` | *(captured)* Used when the client comes back from the WM to the world list (§2.4); the token comes from `0x0C34` (WM ← Login `0x0C36`). No DB round trip, so `0x0C0A` leaves **before** `0x0C05` | capture-validation §3.1; X01 §3.4; `login-server.md` §4, §5.3; L01 §4.3 |
| Login: world list poll | `C 0x0C1B NC_USER_WORLD_STATUS_REQ` → `0x0C1C NC_USER_WORLD_STATUS_ACK` | *(captured)* 10 ms after `0x0C0A`, then every 10.0 s while the world list is shown; keeps the Login session busy, so Login never needs a heartbeat (§1.5) | capture-validation §3.1, §16.2; X01 §3.3 step 8 |
| Login: world select | `C 0x0C0B` → A `0x0C10`, AL `0x0721`, W `0x0C0D` (same ms, this order) / `0x0C0E` → `0x0C0C` | *(captured)* 20–30 ms; the XOR of the 32 validate words is the per-world counter (L01 §2.5); a refused select still carries the WM ip / port, its validate words are stack residue (P02-B23) | capture-validation §3.3, §16.1, §16.3; X01 §3.5 |
| WM: world login | `0x0807`, `C 0x0C0F` → `0x0C16` to every zone, A `0x0C60` / `0x0C61`, D `0x0C12` → `0x0C5F` + `0x0C13` → `0x0C14` | *(captured)* `0x0C14` 50–76 ms after `0x0C0F`; the WM kicks the user from every zone on every world login (§2.5) | capture-validation §4.1; X01 §3.6; W01 §3.2, §3.3 |
| WM: game time | `C 0x080D NC_MISC_GAMETIME_REQ` → `0x080E NC_MISC_GAMETIME_ACK {hour, minute, second}` | *(captured)* 4–8 ms after `0x0C14`, and again in the tick of every zone `0x1801` (map login and map change) | capture-validation §4.1; X01 §3.6 step 6; W01 §5.3 |
| WM: character login | `C 0x1001` → D `0x1004` → blocks → `0x1005` → `0x1003` + D `0x1036` + GameLog `0xC806`, then `0x7032` / `0x7033` / `0x7034` (`NC_CHAR_OPTION_IMPROVE_GET_SHORTCUTDATA_CMD`, `…_GET_KEYMAP_CMD`, `…_GET_GAMEOPTION_CMD`) | *(captured)* `0x1003` ~615 ms after `0x1001`; the option pushes come from `SendToClient_CharOptionData` FUN_00431680 after `0x1003`, 53 ms later, before the zone has answered `0x1801`. `0x1036 NC_CHAR_LOGIN_DB` goes to the CharDB (not to the zone). A character with `nTutorialState` 0 (`TS_PROGRESS`) **and** `nTutorialStep` 0 first gets the `0x1110 NC_CHAR_TUTORIAL_POPUP_REQ` popup (`C 0x1111 {bIsSkip}` → D `0x1112` → `0x1113`, then the same chain); state 0 with a step ≠ 0 gets no popup: the WM sets its login map to "RouT00", sends `0x111D NC_CHAR_TUTORIAL_DOING_CMD` and goes on with the chain (`fc_NC_CHAR_LOGIN_REQ` @ FUN_00422be0). Refusal: `0x1002` (zone down, P02-B33 tutorial skip and every further `0x1001` of that WM session; §2.7) | capture-validation §4.1, §7.4, §18.7, §22.1, §23.6, §28.2; X01 §3.8; W01 §4.2, §6.2; W04 §8 |
| Zone: seed | `0x0807` on accept | *(captured)* The client never sends `0x0806` (§1.4) | capture-validation §2.3; Z18 §1.3 |
| Zone: map login | `C 0x1801` (+ `C 0x080D` to the WM, same tick) → zone → W `0x104B`, W → zone `0x104C`, zone → W `0x101C NC_CHAR_ZONE_CHARDATA_REQ`, W → zone blocks → `0x101D` → 15 client copies of the blocks (`0x1038` BASE … `0x441E` QUEST_RESET_TIME) → `0x1802` | *(captured)* `0x1802` 442–560 ms after `0x1801`; the blob copies come in W01 §6.3 table order, all before `0x1802`. On `0x1802` the client asks the WM for its options in one tick: `0x7004`, `0x700C` (answered from the CharDB, `0x7005`, `0x700D`) and `0x7C06 NC_PRISON_GET_REQ` (`0x7C07`). Refusal: `0x1804 {0x147, index}` + WM `0x0C1A {0, 0, 0x68E}` when an SHN checksum differs (§2.7) | capture-validation §5.1, §4.1, §7.5.2, §28.6; X01 §3.9; Z01 §5.2, §5.3; W01 §7.2 |
| Zone: login complete | `C 0x1803` and, in the same client tick, `0x2001 NC_ACT_CHAT_REQ "&adminlevel"`, `0x200B NC_ACT_ENDOFTRADE_CMD` ×3, on the first map login also `0x302C` / `0x3020`; to the WM `0x581B NC_KQ_LIST_REFRESH_REQ` | *(captured)* The zone answers with the 17-step login burst of Z01 §6 in one server tick (6–18 ms), then the parameter refresh (`0x1035`, `0x240E`, `0x240F`, `0x245F`) one tick later; the zone's `0x180C` makes the WM send `0x1097`, `0x1012`, `0x9414`, `0x5826`, `0x10D9`, `0x0849`, `0x182A` (W01 §7.3 call order; the once-per-character ones only on the first map login). `0x1803` also arms the zone's 10-min auto-save (StoreType 10, §2.4 "Zone process killed") | capture-validation §5.1, §4.1, §23.5; X01 §3.10; Z01 §6, §8.4; W01 §7.3; W04 §17 |

The login request, the world list and the world select also run over the server links (Login ↔ AccountDB /
AccountLogDB / WM, WM ↔ CharDB, zone ↔ WM); their captured order is in capture-validation §7.2, §7.4 and §7.5.2.

### 2.3 Map change

*(captured, town portal and gate)* The old zone ends the stream with `0x180A NC_MAP_LINKOTHER_CMD {mapIndex, x, y,
zoneIp, zonePort, wmHandle}` (zone `so_LinkTo` FUN_0049ad30 → WM `0x180B`, `0x180D` → `0x180E` → `0x180A`, Z01 §7.1).
Town portal: `C 0x2401` → `0x2402`, `C 0x200A` → `0x243D`, `0x201C`; the client's `0x181A NC_MAP_TOWNPORTAL_REQ` (with
`0x200B`) → `0x181B NC_MAP_TOWNPORTAL_ACK` → `0x180A` ~90 ms later (Z01 §7.3). Gate: `C 0x2401`, `C 0x200A` →
`0x3C01` server menu → `C 0x3C02` → `0x180A` (no `0x181B`). The client opens a new zone connection (seed on accept,
`0x1801`, with `0x080D` to the WM in the same tick) and runs §2.2's zone steps again; after the new `0x1803` the WM
repeats only `0x5826` and `0x182A`. A destination on the same zone gets `0x1809 NC_MAP_LINKSAME_CMD {mapIndex, x, y}` instead (no
new connection; *(captured)* with `&linkto`, capture-validation §18.6). The players in sight see a same-zone link as
`0x1805 NC_MAP_LOGOUT_CMD {handle}` (the logout broadcast, Z01 §3.2), not as a sight leave `0x1C0E`, and the handle
stays *(captured: `&linkto`, capture-validation §18.6; a town revive onto the same zone, where the mover gets `0x104F
NC_CHAR_REVIVESAME_CMD` instead of `0x1809`, §27.2)*. Detail: capture-validation §6.1, §4.1, §7.5.4; X01 §3.11; Z01 §7.

### 2.4 Leaving the game: world list, character select, quit

All three ways out start the same *(captured)*: zone `C 0x2012 NC_ACT_STOP_REQ`, `C 0x1071 NC_CHAR_LOGOUTREADY_CMD`
(the zone arms its 13-s logout timer and allows `0x0C18` after 8 s, Z07 §3.3); in the same tick the client saves its
options at the WM (`0x7011`, `0x7015`, `0x7016`, `0x703B`, no answers to the client; the WM writes them to CharDB as
`0x7026` / `0x702A` / `0x702B` / `0x704F` 20–70 ms later, D04 §5.1, W04 §8.2; the CharDB answers `0x7050 {0x2118}` with a
stale `nCharNo`, D04-B13, capture-validation §22.5, §25.9). The client then counts down 10 s
itself and sends `0x0C18 NC_USER_NORMALLOGOUT_CMD {LogoutType}` to the WM **and** the zone in one tick. The zone's
handler reads no `LogoutType`: once the 8 s have passed it runs `sp_Schedule_Logout` at once: one save
(`0x0410 StoreType 9`), `0x0C31 NC_USER_POSSIBLE_NEW_CONNECT_CMD` to the WM, the object freed, nothing to the client
(Z01 §8.1). What the WM does depends on `LogoutType` (W01 §5.1):

- **Back to the world list** (`LogoutType 0` after `0x0C33`): before the `0x0C18`, WM `C 0x0C33
  NC_USER_WILL_WORLD_SELECT_REQ` → (Login `0x0C35` / `0x0C36`) → `0x0C34 NC_USER_WILL_WORLD_SELECT_ACK {nError 0x1E58,
  sOTP[32]}`; then `0x0C18 {0}` closes the WM session as a quit does (below), and the client logs in again with the
  token (§2.2). From the character list the client sends only `0x0C33` → `0x0C34` and closes the WM connection
  without `0x0C18`; the WM's `CWMClientSession::Close` @ FUN_00437030 *(pdb2016)* then sends AccountDB `0x0C11 {playmin 0, 0x780}` and `0x0C19` to every
  zone (capture-validation §23.2).
- **Back to character select** (`LogoutType 1`) *(captured, capture-validation §22.5, §23.1, §23.2)*: the zone saves once
  (StoreType 9) and sends `0x0C31` 3–16 ms after the `0x0C18`. The WM keeps the session (no `0x0C11`, no `0x0C19`); its
  `CWMClientSession::Logout` @ FUN_00436d50 *(pdb2016)* sends CharDB `0x1037 NC_CHAR_LOGOUT_DB`, AccountLogDB `0x081F` and
  GameLogDB `0xC807` in one ms (W01 §5.4). `0x1037` carries the WM's copy of money and position from the character
  login or the last link to another map, not the zone's; the CharDB row is not written from it, but the Character
  server copies it into GameLog `0x040B NC_LOG_GAME_LOGOUT` 4 ms later, so the GameLog gets the stale values
  **(original bug) P02-B36** (capture-validation §23.5, §25.9). The client sends `0x0C1F NC_USER_AVATAR_LIST_REQ` with one
  unset byte (a client quirk; the WM ignores the payload), and the WM reloads the list from CharDB (`0x0C12` →
  `0x0C5F`, `0x0C13`) and sends `0x0C14` (§2.2). The client closes its zone socket 1 s later.
- **Quit to the desktop** (`LogoutType 0`, no `0x0C33`) *(captured, capture-validation §22.5, §25.9)*: the WM
  broadcasts `0x0C19 NC_USER_CONNECTCUT2ZONE_CMD` to every zone from its 0x0C18 handler (with `0x1037` / `0x081F` /
  `0xC807`) and again from `CWMClientSession::Close` (with AccountDB `0x0C11 {playmin, 0x780}`, AccountLogDB `0x0722` /
  `0xC803`), W01 §5.1 / §3.2. Each `0x0C19` makes the zone run `so_banning` (Z01 §8.3). If the zone handles the
  client's own `0x0C18 {0}` first, it saves once (StoreType 9 + `0x0C31`) and the later `0x0C19` find no player
  (`s24` A). If it handles the WM's kick first, it saves four times **(original bug) P02-B35**: StoreType 4
  (`so_banning`), 7 (`zs_disconnect` closing the client socket), 4 (the second `0x0C19`), then 9 + `0x0C31` 13 s after
  the `0x1071` (the `0x1071` timer, about 3 s after the quit), each a full `ws_save2DB` burst. Both orders were
  captured, and the client's `0x0C18` was on the wire first in all three quits.

**The two logout timers** *(captured, capture-validation §23.3)*. `so_banning` saves (`so_Unmark(REMOVE_LOGOUT, 1, 4)`,
FUN_00558900) and arms `sp_Schedule_Kickout` @ FUN_00558080 at +10 s unless the player's timer already holds the
`0x1071` work (`TSCW_LOGOUT`). So the work queued first decides how the zone object ends: after a cut **without**
`0x1071` (lost socket, kick), Kickout at +10 s saves with StoreType 3 and frees the object, **without** `0x0C31`; after a
`0x1071` (quit, exit countdown, also a client killed during it: there the WM broadcasts `0x0C19` only once, from
`CWMClientSession::Close`, as no `0x0C18` arrives, capture-validation §23.7), `sp_Schedule_Logout` at +13 s saves with StoreType 9
and sends `0x0C31` (a late `0x0C31` is harmless: the WM compares the `charNo`, W01 §7.3). Every further kick of the same
user inside that window (`0x0C19`, the next login's `0x0C16`, §2.5) runs `so_banning` and a full save again. Z01
§8.3 does not have the Kickout timer yet (capture-validation §11, "Zone connection lost").

**Zone connection lost** *(captured, capture-validation §23.4)*. When the zone socket closes (server reset, zone
crash), the client does not stay on the WM: 14–27 ms later it sends `0x0C18 {0}` to every open socket
(`NetMgr::SendUserLogOutMsg2AllServer` @ client FUN_006d34e0, name *(pdb2017)*, called from the in-game scene tick
FUN_004cbf30), waits 1 s, closes them all and shows "Disconnected from the server." ("Multiple logins detected, you
have been logged out." when a duplicate-login flag is set; a closed WM socket gives "Disconnected from the world
server."). The WM closes the session as for a quit (`CWMClientSession::Logout`, `0x0C11 {0x780}`, `0x0C19` twice). After a
reset of the socket (zone still running) the zone object saves 4 / 7 / 4 and ends by the Kickout timer (StoreType 3,
no `0x0C31`); after a zone process kill there is no object left and nothing is saved (below).

**Kicked by the zone** *(captured, capture-validation §28.4)*. A zone that drops a logged-in player (GM `&kickout` on
the same zone, reason `0x68B`) runs `ShinePlayer::so_Disconnect` @ FUN_0054f340: WM `0x0C1A
NC_USER_CONNECTCUT2WORLDMANAGER_CMD {usrregnum, wldmanhandle, reason}` with the player's user number and WM handle,
then `so_banning` (one save, StoreType 4, Z01 §8.3), and closes the zone socket, all in one ms. The WM's
`CParserZone::fc_NC_USER_CONNECTCUT2WORLDMANAGER_CMD` @ FUN_00428a40 *(pdb2016)* finds the session by handle and, as
the user number matches, sends the client `0x0C17 NC_USER_CONNECTCUT_CMD {0x68B}` (5 ms later). The client shows
"Disconnected from the server.", sends `0x0C18 {0}` (13 ms) and closes; the WM ends the session as for a quit
(`0x1037`, AccountDB `0x0C11 {0x780}`, `0x0C19` twice, P02-B35's pattern). A `0x0C1A` with user number 0 (the SHN
refusal, §2.7; the name mismatch, §2.6) finds no session, so the client gets no `0x0C17`. The GM's notice reads
" is banned" without the name **(original bug) P02-B41**. A kick of a player on another zone never arrives: the ring
search sends the kick layout under the search opcode and no zone finds the name **(original bug) Z11-B6**
(capture-validation §28.5). Detail: W01 §5.2; Z01 §8.3; Z11 §4.5.

**Zone process killed** *(captured, capture-validation §23.5, §23.6)*. The zone dies without a save. What was committed
through a CharDB transaction survives: `&getmoney` (`so_ply_PickupMoney`) has its `0x3438` → `0x3439` back in 15–22 ms,
before any kill, and the next login has that money. Position (and whatever else only `ws_save2DB` writes) is the
last save's: the last `ws_save2DB`: logout, link or revive (StoreType 2), `&levelup` (8), or the **auto-save**, a full `ws_save2DB` burst with StoreType 10 that
`ShinePlayer::so_Routine` @ FUN_0056c790 runs 600 s after the map login's `0x1803` (deadline from `so_SetAutoSaveTime`
@ FUN_005608c0) and then every 600 s (6000 ticks of 0.1 s; captured 599.94–599.99 s after `0x1803`; Z01 §8.4's "every
6000 ms" is wrong). The WM's `0x1037` still carries its own copy of money and position (P02-B36; the CharDB row is not
written from it). The WM tells nobody that the zone died: its broadcasts go to the remaining zone links, and a
`0x1001` for that zone's maps gets `0x1002 {0x145}` until the restarted zone has registered (§2.7; restarts as
capture-validation §17.4, P02-B25). Detail: capture-validation §4.1, §5.4, §16.1, §22.5, §23.2–§23.6, §25.9; X01
§3.12 a / d; W01 §4.2, §5.1, §5.4; Z01 §8.1, §8.3, §8.4; Z07 §3.3; Z11 §7.4.

### 2.5 Duplicate login

*(captured)* Login sends `0x0C16 NC_USER_KICKOFFFROMWORLD_CMD` to every WM before its `0x0C0A` on **every** successful
login (password and token login, `fc_NC_USER_LOGIN_WITH_OTP_REQ` FUN_00406bb0 too), without checking for an old session;
the body is 10 bytes, `usrregnum` after 6 unwritten header bytes (capture-validation §7.2, P02-B5). The WM's handler
(`CParserLogin::fc_NC_USER_KICKOFFFROMWORLD_CMD` @ FUN_00424880) sends the old client `0x0C17 NC_USER_CONNECTCUT_CMD
{reason 0x683}` ("multiple logins") and closes it only when the account still has a WM session
(`CWMClientSessionManager::Kickoff` @ FUN_00437d50), but passes `0x0C16` on to every zone **unconditionally**
(`CWMZoneSessionManager::Kickoff` @ FUN_00439540); a zone object still in its logout window is kicked and saved again
(StoreType 4; *(captured)* capture-validation §23.3, 518.799; §2.4 "The two logout timers", P02-B35). The WM also sends
its own `0x0C16` to every zone on every `0x0C0F` (§2.2): two zone kicks per login. In the
capture the WM's `0x0C17` left 0.8 ms before Login's `0x0C0A` to the new client. A second `0x0C0F` of the same account
at the WM kicks the old session the same way (not captured). Detail: capture-validation §4.1; X01 §3.12 f;
`login-server.md` §5.1; W01 §3.2, §5.2; Z01 §8.3.

### 2.6 Character create and delete (character list)

*(captured)* Create: `C 0x1401 {slotnum, name, char_shape}` → D `0x1402` (14 ms) → D `0x1405` (85–100 ms,
`p_Char_Create`) → in one WM pass AccountDB `0x140D`, GameLog `0x0411` + `0xC804` and client `0x1406` (`numofavatar 1`,
the new `AVATAR`). Delete (the client checks the typed confirmation itself and sends nothing on a mismatch): `C 0x1407
{slot}` → D `0x1413` / `0x1414 {nGuildNo}` (guild check) → D `0x1408` → `0x140B` → in one ms AccountDB `0x140E`,
GameLog `0x0412` + `0xC805`, client `0x140C`, D `0x9424`, every zone `0x10B2`. Refusals: `0x1404` / `0x140A` (§3.2).
Detail: capture-validation §16.1; X01 §3.7; W01 §4.1; W03 §4.5; W04 §4.3; D02 §3.3, §3.4.

*(captured, capture-validation §22.1)* Create refused by the CharDB: `0x1401` → D `0x1402` (15 ms) → D `0x1403
NC_AVATAR_CREATEDATAFAIL_ACK {err 0x181}` (29 ms) → client `0x1404 {0x181}` (14 ms) "The name is already in use.
Please choose another"; a name with a space never leaves the client.

*(captured, capture-validation §22.1, §22.3)* Free rename (the client opens the rename window itself when the selected
name contains `-`; the unchanged name is refused by the client): `C 0x140F NC_AVATAR_RENAME_REQ {SlotNo, NewName}` → D
`0x1411 {handle, nCharNo, SlotNo, NewName}` → `0x1412 {…, Error}` → client `0x1410 {SlotNo, NewName, Error}` (16–22 ms in all);
`0xD0` = renamed (no message, the list shows the new name, the WM stores it in its avatar copy), `0xD1` = refused, client "The name cannot be used."
(C01, client `0x1410` handler @ FUN_00476c70). The WM answers `0xD1` itself without asking the CharDB
(`fc_NC_AVATAR_RENAME_REQ` @ FUN_0041a640) for a slot > 5 or empty, an empty name or one over 16 characters, a space
in the name, or a name `GetIsBadName` rejects. Nothing refuses a **taken** name *(captured, capture-validation §28.3)*:
the WM checks only slot and name, the Character server's `0x1411` handler @ FUN_00436030 maps `p_Char_Rename`'s
`nRet 0` to `0xD0`, and the 2016 `p_Char_Rename` is a plain `UPDATE tCharacter SET sID`. With no unique index on `sID`
(the test DB has none *(db-backup)*), `0x140F` onto the name of another character answers `0xD0` in 34 ms and two
characters share the name **(original bug) P02-B42** (create refuses a taken name with `0x181`, but that check is
inside `p_Char_Create`). The renamed character's login and map login go through (the WM resolves the zone's `0x104B`
by session handle, not by name). The test DB's newer `p_Char_Rename` answered `0xD0` without renaming: the client then
logged in with a name the CharDB blob did not have, the WM's `0x104B` name check answered `0x104C {−1, −1}` and set its
session to state 3 (closing) at once; the zone's `0x0C1A {0, 0, 0x689}` (`usrregnum` 0) then found no session, so the
client got no `0x0C17`, only "Disconnected" when the WM closed the connection. This is the test DB's
procedure, not a 2016 server path. Detail: W01 §4.1, §7.2, §5.2; D02 §3.5 (its "a duplicate fails on the unique
name" is contradicted); Z01 §5.3.

*(captured, capture-validation §22.1, §22.4)* Rename right (dept 45, avatar `CharIDChangeData.bNeedChangeID` 1): `C
0xB409 NC_USER_CONNECTION_CHANGE_CHAR_ID_REQ {nSlotNo, sNewID}` → D `0xB40A {hWMChar, nRowNo, nUserNo, nCharNo, sNewID,
bInit}` → `0xB40B {hWMChar, nError, …}`. On `0x20C0` the WM sends `0xB40F NC_USER_CONNECTION_ZONE_CHANGE_CHAR_ID_CMD
{nCharNo, bInit, sOldID, sNewID}` to every zone link, then (1 ms later) the client `0xB40C {nError 0x20C0, nSlotNo,
sNewID}` "Character name successfully changed." (30 ms after `0xB409`). Every other CharDB code (`0x20D1` name in
use captured, 48 ms after `0xB409`) carries a stack-garbage slot byte, and the client, finding no avatar in that slot, shows nothing
**(original bug) P02-B34**. Detail: W01 §4.1, §6.2; D02 §14; Z30 §1.2.

### 2.7 Login refusals

*(captured)* Blocked account / login disabled: AccountDB `0x0C5C {nBlock 1}` / `{bLoginAble 0}` → `0x0C09 {0x47}` /
`{0x48}` (AccountLog `0x0720` + `0xC802`, no `0x0C5D`). World closed (WM down): the world stays in the list with
status 0 and a select answers `0x0C0C {0}` at once. World full: Login still runs the AccountDB / AccountLog / WM round
trip and answers `0x0C0C {5}` with a valid address and key; the client shows "Server is full." and does not connect
(L00-B3). For up to 30 s after a WM start the world reports full, because the WM's first `0x0808` carries capacity 0
(P02-B22). Detail: capture-validation §16.1, §16.3; X01 §3.5; `login-server.md` §4, §5.1; L01 §3.

*(captured)* Character login refused: `C 0x1001` → `0x1002 {0x145}` "The Map is under maintenance", the client stays on
the character list. Without a CharDB round trip (2–12 ms) when no zone serves the login map: the zone is stopped or
killed (capture-validation §22.1 step 4, §23.6). The WM tells nobody else that a zone died; the first `0x1001` after the
zone's `0x0803` / `0x180F` succeeds. After a CharDB round trip when a character listed by `0x0C13` (not just created)
skips the tutorial (`0x1110` → `0x1111 {1}` → D `0x1112` → `0x1113 {0x31E8}` → 10 ms → `0x1002 {0x145}`, no `0x1004`):
the WM's list copy maps every tutorial-state-0 avatar to "RouT"; the skip sets the avatar to `TS_SKIP`, and
`TutorialLoginProcess` @ FUN_004371a0 rewrites the login map (to "RouT00") only for `TS_PROGRESS`, so the list's "RouT"
stays, `GetServiceMapZoneNo` finds no zone for it, and the WM refuses **(original bug) P02-B33** (capture-validation §22.2; the skip is saved, the next list shows state 2
and the DB map). Every further `0x1001` of that character in the same WM session gets `0x1002 {0x145}` 4 ms later,
without the tutorial round trip and without a WM log line *(captured, capture-validation §28.2)*: the WM copy now has
`nTutorialState` 2, so `CParserClient::fc_NC_CHAR_LOGIN_REQ` @ FUN_00422be0 goes straight to the map lookup, which
still finds no zone for "RouT". Only a new list clears it, and a new list needs a new WM session (back to the world
list or a new login, §2.4); then `0x1001` → 5 ms → D `0x1004` → `0x1003` as usual, with no tutorial question. Detail:
W01 §4.2, §6.2.

*(captured, capture-validation §28.6)* Map login refused by the SHN check: when one of the 49 `shn_md5` entries of
`0x1801` differs from the zone's checksum of that table, `ShinePlayer::sp_NC_MAP_LOGIN_REQ` @ FUN_00452590 *(pdb2016)*
logs `sp_NC_MAP_LOGIN_REQ : DataFail [CharID=%s]` (no table name, no hashes), sends the client `0x1804
NC_MAP_LOGINFAIL_ACK {0x147, index}` and calls `so_Disconnect(0x68E)` @ FUN_0054f340, which sends the WM `0x0C1A
NC_USER_CONNECTCUT2WORLDMANAGER_CMD {usrregnum 0, wldmanhandle 0, reason 0x68E}` and closes the zone socket. On the
wire both leave 3 ms after `0x1801`, the `0x0C1A` 1 ms before the `0x1804` (two sockets), the FIN 5 ms later.
`index` is the first differing entry (`DataFileCheck` @ FUN_00631350) in the `CShnDataFileCheckSum` table @
FUN_00631450 (… 31 ItemViewInfo, 32 MapViewInfo, 33 MobViewInfo …; captured 32). The `0x0C1A` carries no user
number, so the WM sends no `0x0C17`; the client (`0x1804` handler @ FUN_004778c0) shows "The client has been illegally
manipulated. Please reinstall the client.", closes its WM connection 14 ms after the `0x1804` and goes back to the
login screen, and the WM ends the session as for a lost client (`0x1037`, AccountDB `0x0C11 {playmin, 0x780}`, one
`0x0C19`). The zone hashes the **decrypted** table. A table of another length does not get that far: the zone crashes
at start in `CDataReader::Read` @ FUN_0062a780 **(original bug) P02-B43** (server data only). Detail: Z01 §5.2; W01
§5.2.

---

## 3. Packet layouts

Offsets are payload offsets (just after the opcode). Little-endian. Strings are fixed-size and
NUL-padded unless stated otherwise.

### 3.1 Login server

| Opcode | Dir | Layout | Notes |
|---|---|---|---|
| `0x0807` | S→C | `u16 seed` | sent on accept |
| `0x0C65` | C→S | `char version_key[64]` | `strncmp(..., 64)` against each line of `Login/ClientVersionKeyInfo.txt` |
| `0x0C67` | S→C | `u8 n; char s[n]` | version OK. In this build always `n=1, s=""` (the source field is cleared before the copy) |
| `0x0C66` | S→C | `u8` (value not set by the code) | version rejected |
| `0x0C5A` | C→S | `char user[256]` @0, 4 unread bytes @256, `char password[36]` @260, `u32 extra[5]` @296 | total packet length must equal `0x13E`. `extra` is forwarded to AccountDB without being interpreted |
| `0x0C37` | C→S | `u8 token[32]` | `NC_USER_LOGIN_WITH_OTP_REQ`; total packet length must equal `0x22`. Token login: looked up in a table filled by WM message `0x0C35` (token valid 10 s, L01 §4.3). Unknown token → `0x0C09 {0x52}`; login disabled flag (`gServer.m_isPermitServer` *(pdb2016)*, `DAT_004425f8`, `== 0`) → `{0x45}`; else world list `0x0C0A`, sent before the `0x0C05` of the client's following `0x0C04` *(captured, §2.2)* |
| `0x0C09` | S→C | `u16 error` | login failure, then disconnect. Codes seen: `0x45` (server closed or account error -1; client "Please check ID or Password.", 50 ms after a wrong password *(captured)*), `0x47` (AccountDB `nBlock`: "The ID has been blocked." *(captured)*), `0x48` (AccountDB `bLoginAble 0`: "The World Servers are down for maintenance." *(captured)*), `0x4A` (after `0x0C1D`), `0x4B` (account error -2), `0x4C` (after `0x0C20`), `0x51` (AccountLog block), `0x52` (bad token) |
| `0x0C0A` | S→C | `u8 count; WORLD[count]` | `WORLD` (18 bytes) = `u8 world_no; char name[16]; u8 status`. Status is set to 2 at load, 6–10 while the WM is connected (load band from its `0x0808` user count, L01 §3), 0 once its link is released ("Server is closed."), 5 = full. Login refuses a select of a world with status `< 5`; 5 passes (L00-B3) and the client then shows "Server is full." without connecting; the client connects for 6–10 (`login-server.md` §8). *(captured: 6 normal, 0 after a WM stop, 5 full, capture-validation §16.1)* |
| `0x0C1B` | C→S | – | `NC_USER_WORLD_STATUS_REQ`, world list refresh → `0x0C1C` (same layout as `0x0C0A`). The client polls it 10 ms after `0x0C0A`, then every 10.0 s while the world list is shown *(captured, §2.2)* |
| `0x0C0B` | C→S | `u8 world_no` | world select |
| `0x0C0C` | S→C | `u8 status; char wm_ip[16]; u16 wm_port; u16 validate[32]` (83 bytes) | `NC_USER_WORLDSELECT_ACK`. `wm_ip` / `wm_port` are the WM's client listener from `ServerInfo.txt` (`GetWorldManagerConnectInfo` FUN_0040a020, L01 §2.5; 9110 *(captured)*). On success, `validate` is the 64-byte key that came back from WM `0x0C0E`. On an unknown, closed or refused world only `status` is meaningful: `wm_ip` / `wm_port` are filled anyway and `validate` is uninitialised stack (P02-B23, *captured*) |
| `0x0C04` | C→S | `u8 XTrapClientKeyLength` (29); `char XTrapClientKey[29]` | `NC_USER_XTRAP_REQ`, sent by the client right **after** `0x0C5A` / `0x0C37`, in the same tick *(captured)*. The key is not compared (L00-B5); answered at once with `0x0C05 NC_USER_XTRAP_ACK {u8 bSuccess 1}` |
| `0x0C1D` / `0x0C20` | C→S | – | answered with `0x0C09 {0x4A}` / `{0x4C}`, then disconnect |
| `0x0C06`, `0x0C18` | C→S | –, `u8 LogoutType` | no-op handlers. The client sends `0x0C18 {0}` to Login when the user leaves the world list for the login screen *(captured, capture-validation §16.1)* |

Login → WM `0x0C0D` (internal): carries the login handle, world number, user name and user number, plus
31 random `u16` values and a 32nd `u16` that is the XOR of a world key with all 31. WM keeps this record
until the client presents the same 32 values in `0x0C0F`.

### 3.2 World manager

| Opcode | Dir | Layout | Notes |
|---|---|---|---|
| `0x0807` | S→C | `u16 seed` | sent on accept |
| `0x0C0F` | C→S | `char user[256]` @0, `u16 validate[32]` @256 | must match a pending `0x0C0D` record. No match → `0x0C15 {u16 0x44}` |
| `0x0C15` | S→C | `u16 error` | world login failed (`0x44` bad key, `0x46` avatar DB error) |
| `0x0C14` | S→C | `u16 worldmanager; u8 numofavatar; AVATAR[numofavatar]` | `NC_USER_LOGINWORLD_ACK`. `worldmanager` = the client's WM handle (sent back in `0x1801`). `AVATAR` is 130 bytes (`0x82`), copied from CharDB `0x0C13`, except that the WM sets the login map of every tutorial-state-0 avatar to "RouT" *(captured, capture-validation §22.2)*; its layout is in `annotations.json` (W01 §6.1). The client sends `0x080D` 4–8 ms later *(captured)* |
| `0x1001` | C→S | `u8 slot` (0–5) | `NC_CHAR_LOGIN_REQ`: select a character |
| `0x1002` | S→C | `u16 error` | `NC_CHAR_LOGINFAIL_ACK`. Codes: `0x0143` (slot ≥ 6), `0x0144` (empty slot), `0x0145` "The Map is under maintenance" (no zone serves the map: zone down or a tutorial skip of a listed character and every further `0x1001` of it in the same WM session, all *(captured)*, §2.7, P02-B33; no session for that zone; or the previous character's logout not yet confirmed), `0x31EB` (no selected avatar, W01-B6). W01 §4.2 |
| `0x1003` | S→C | `char zone_ip[16]; u16 zone_port` | `NC_CHAR_LOGIN_ACK`, zone handoff, sent after CharDB `0x1005 NC_CHAR_CHARDATA_ACK`. In the same ms the WM sends `0x1036 NC_CHAR_LOGIN_DB` to the **CharDB** and `0xC806` to the GameLog, then `0x7032`–`0x7034` to the client *(captured, §2.2)* |
| `0x080D` | C→S | – | `NC_MISC_GAMETIME_REQ`: after `0x0C14` and in the tick of every zone `0x1801` *(captured)* → `0x080E NC_MISC_GAMETIME_ACK {u8 hour, u8 minute, u8 second}` (W01 §5.3) |
| `0x7032` / `0x7033` / `0x7034` | S→C | option blobs | `NC_CHAR_OPTION_IMPROVE_GET_SHORTCUTDATA_CMD` / `…_GET_KEYMAP_CMD` / `…_GET_GAMEOPTION_CMD`, pushed after `0x1003` (`SendToClient_CharOptionData` FUN_00431680, W04 §8) |
| `0x0C33` → `0x0C34` | C→S, S→C | – → `u16 nError; char sOTP[32]` | `NC_USER_WILL_WORLD_SELECT_REQ` / `_ACK`: back to the world list; the WM gets a one-time token from Login (`0x0C35` / `0x0C36`), `0x1E58` = OK (§2.4, W01 §5.1) |
| `0x0C18` | C→S | `u8 LogoutType` | `NC_USER_NORMALLOGOUT_CMD`; sent to the WM and the zone together. 0 = quit or back to the world list, 1 = back to character select, both *(captured)* (W01 §5.1); the zone reads no `LogoutType` (§2.4) |
| `0x0C1F` | C→S | – (the client sends 1 unset byte) | `NC_USER_AVATAR_LIST_REQ` *(pdb2016, empty struct)*: after `0x0C18 {1}`, reload the character list; `fc_NC_USER_AVATAR_LIST_REQ` @ FUN_00412ee0 ignores the payload and sends CharDB `0x0C12` → `0x0C14` (§2.4) *(captured, capture-validation §22.5, §22.6)* |
| `0x0C17` | S→C | `u16 reason` | `NC_USER_CONNECTCUT_CMD`, then the WM closes the session; `0x683` = duplicate login (§2.5), zone kick reasons are passed on from zone `0x0C1A NC_USER_CONNECTCUT2WORLDMANAGER_CMD {…, u32 usrregnum @+6, u16 wldmanhandle @+0xa, u16 reason @+0xc}` when the user number matches the session of that handle (W01 §5.2): `0x68B` = `&kickout` *(captured, §2.4 "Kicked by the zone")*; a `0x0C1A` with user number 0 (`0x68E` SHN refusal, `0x689` name mismatch) sends nothing *(captured, §2.6, §2.7)*. On `0x68B` the client shows "Disconnected from the server." and sends `0x0C18 {0}` |
| `0x1401` | C→S | `u8 slotnum; char name[20]; u8 char_shape[4]` (25 bytes; shape byte 0 = `race:2, chrclass:5, gender:1`, then hairtype, haircolor, faceshape) | `NC_AVATAR_CREATE_REQ` *(pdb2016)*: checked by the WM (slot, name, class level rule), then CharDB `0x1402` → `0x1405` (§2.6; W01 §4.1, D02 §3.3) *(captured: `{2, "X37Del", 0x85}` = Fighter)* |
| `0x1406` / `0x1404` | S→C | `u8 numofavatar; AVATAR` (131 bytes) / `u16 err` | `NC_AVATAR_CREATESUCC_ACK` / `NC_AVATAR_CREATEFAIL_ACK`. Every refusal the WM finds itself answers `0x84` "name already taken" (W01-B2); CharDB failures pass on its code (`0x1403`; `0x181` "The name is already in use." *(captured)*, §2.6) |
| `0x1407` | C→S | `u8 slot` | `NC_AVATAR_ERASE_REQ` *(pdb2016)*: the WM asks the CharDB for the guild first (`0x1413` → `0x1414`), then `0x1408` (§2.6; W01 §4.1, W03 §4.5) *(captured)* |
| `0x140F` → `0x1410` | C→S, S→C | `u8 SlotNo; char NewName[20]` → `u8 SlotNo; char NewName[20]; u16 Error` (21 / 23 bytes) | `NC_AVATAR_RENAME_REQ` / `_ACK` *(pdb2016)*: free rename; `0xD0` renamed, also onto a taken name (P02-B42, *captured* §2.6), `0xD1` refused "The name cannot be used." (§2.6; W01 §4.1) *(captured)* |
| `0xB409` → `0xB40C` | C→S, S→C | `u8 nSlotNo; char sNewID[20]` → `u16 nError; u8 nSlotNo; char sNewID[20]` (21 / 23 bytes) | `NC_USER_CONNECTION_CHANGE_CHAR_ID_REQ` / `_ACK` *(pdb2016)*: rename right; `0x20C0` renamed, `nSlotNo` set only then (P02-B34) (§2.6; W01 §4.1, §6.2) *(captured)* |
| `0x140C` / `0x140A` | S→C | `u8 slot` / `u16 err` | `NC_AVATAR_ERASESUCC_ACK` / `NC_AVATAR_ERASEFAIL_ACK`; `0xC7` (199) = guild master; an empty slot answers `0xC6`, which the client also shows as the guild-master text (W01-B3) |

The other 160 WM handlers (party, friends, guild, raid, chat channels, …) are listed in
[opcodes-wm.md](opcodes-wm.md) with their replies and payload-read hints.

### 3.3 Zone

| Opcode | Dir | Layout | Notes |
|---|---|---|---|
| `0x0807` | S→C | `u16 seed` | sent on accept (§1.4) *(captured)* |
| `0x0806` | C→S | – | `NC_MISC_SEED_REQ`: registered, never sent by the 2016 client; dead path (§1.4) |
| `0x1801` | C→S | `u16 wm_handle` @0, `char char_id[20]` @2, `u8 shn_md5[49][32]` @22 | `NC_MAP_LOGIN_REQ`. Each 32-byte entry is compared with the server's checksum of one SHN data file |
| `0x1804` | S→C | `u16 error; u8 index` | `NC_MAP_LOGINFAIL_ACK`, map login failed. `0x0147` = SHN checksum mismatch, `index` = the first differing entry of the `CShnDataFileCheckSum` table (32 = MapViewInfo *(captured)*); the zone then sends WM `0x0C1A {0, 0, 0x68E}` and closes, the client shows "The client has been illegally manipulated. Please reinstall the client." and returns to the login screen (§2.7, Z01 §5.2). Also sent on `0x101E NC_CHAR_ZONE_CHARDATAFAIL_ACK` |
| `0x1802` | S→C | `u16 charhandle; CHAR_PARAMETER_DATA param` (0xE8); `SHINE_XY_TYPE logincoord` (242 bytes) | `NC_MAP_LOGIN_ACK` (struct `PROTO_NC_CHAR_MAPLOGIN_ACK` *(pdb2016)*), sent in `wms_NC_CHAR_ZONE_CHARDATA_ACK` (FUN_005a3590 → FUN_005a3140) once WM delivers the character, after the 15 client blob copies `0x1038` … `0x441E` *(captured, §2.2)*. Field layout: packets-zone.md (Z07 §1.5) |
| `0x1803` | C→S | – | `NC_MAP_LOGINCOMPLETE_CMD`. Zone then pushes the login burst in one server tick (`sp_NC_MAP_LOGINCOMPLETE_CMD` FUN_00443390, Z01 §6; captured order in capture-validation §5.1) and tells the WM `0x180C` |
| `0x180A` | S→C | `u16 mapIndex; u32 x; u32 y; char zoneIp[16]; u16 zonePort; u16 wmHandle` | `NC_MAP_LINKOTHER_CMD`, last packet of a zone stream on a map change to another zone; the client connects to `zoneIp:zonePort` (§2.3, Z01 §7.1) |
| `0x1071`, `0x0C18` | C→S | –, `u8 LogoutType` | `NC_CHAR_LOGOUTREADY_CMD` starts the logout countdown; `0x0C18` 10 s later (accepted after 8 s, any `LogoutType`) ends the session: the zone saves once (StoreType 9), sends the WM `0x0C31`, frees the player and sends the client nothing; a WM kick handled first adds saves (P02-B35, §2.4, Z01 §8.1, Z07 §3.3) |

Zone → WM `0x104B NC_CHAR_REGISTNUMBER_REQ` (internal): `u16 zone_handle, u32 0xFFFFFFFF, u16 wm_handle,
char char_id[20]`.

All 245 zone client handlers carry their original names (from `ShinePlayer::sp_NC_*` profiler strings)
in [opcodes-zone.md](opcodes-zone.md).

---

## 4. How the tables were produced

1. Ghidra headless (the exports were generated with 12.1.4) with `Decompiler Parameter ID` enabled (`tools/protocol-re/EnableParamId.java`).
   `tools/protocol-re/ExportAll.java` dumps every function's C and every string with its references.
   REA (Hopper backend) was used for spot checks. REA's Ghidra provider requires Ghidra 12.1.x
   (now installed as `ghidra@12.1.4`).
2. `extract.py` finds the `pft_Store` function from its "Duplicate protocol set" string. It then reads
   every `pft_Store(dept, cmd, handler)` registration and assigns it to the
   `PROTOCOLFUNCTIONTEMPLETE<Class::*>` table being built. For each handler it collects:
   - **name**: the handler's own `sp_/fc_/gds_/wms_/zls_NC_*` profiler or log string (zone, WM, Character)
   - **sends**: opcodes written by `CSendPacket::ID`, by hand-built raw headers, or into the zone send buffer, in the handler and its direct callees
   - **hints**: packet-length checks and byte offsets read from the packet
3. `catalog.py` merges the 7 binaries. A sent opcode counts as **client-bound** when no server-to-server
   parser in any of the 7 binaries registers a handler for it.

Regenerate:

```bash
export JAVA_HOME=/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home
G=/opt/homebrew/opt/ghidra@12.1.4/libexec/support/analyzeHeadless; T=tools/protocol-re; OUT=/tmp/re/out
$G /tmp/re/proj login -import Files/Server/2016/Login/3LoginServer2.exe -scriptPath $T \
   -preScript EnableParamId.java -postScript ExportAll.java $OUT/login      # repeat per binary
tools/protocol-re/regen.sh                   # rebuilds every generated doc from re-data/exports (preferred)
python3 $T/extract.py $OUT/login            # per server → handlers.json
python3 $T/layouts.py $OUT/zone x Files/Server/2016/w00_Zone00/5ZoneServer2.exe   # per server → layouts.json (exe enables vtable resolution)
python3 $T/catalog.py $OUT docs/protocol    # reads $OUT/<server> (or ${OUT}2/<server> if present)
python3 $T/packets.py $OUT docs/protocol    # → packets-<server>.md (merges annotations.json)
OUT=$OUT $T/fn.sh login 406680              # print one decompiled function
```

## 5. Confidence

| Item | Basis |
|---|---|
| Framing, opcode split, XOR table and index rule, seed packets, heartbeats | observed, cross-checked in 3 binaries, *captured* on all three servers (capture-validation §2) |
| Handler ↔ opcode tables | observed (registration calls). 597/597 zone and 220/223 `sp_` handler names matched |
| Names marked "handler" | the opcode's own handler string in some binary |
| Names marked † | inferred: REQ+1 = ACK, or a log string. Can be wrong (e.g. `0x0C65` is the version check, not `RETURN_CHECK_ACK`) |
| "Sends" columns | regex over decompiled C. Misses sends through virtual calls and helpers deeper than one call. Callee hits (¹) can include unrelated paths |
| Payload layouts in §3 | read manually from the handlers cited |

## 6. Decoding captures

`tools/protocol-re/pcap_decode.py` (stdlib only) decodes `.pcap`/`.pcapng` captures of client traffic with the
rules of §1: TCP reassembly, framing, XOR-499 decryption from the `0x0807` seed (brute-forced when the seed is
missing), field decode from `annotations*.json` then `layouts.json`, and a validation report.

```bash
python3 -I tools/protocol-re/pcap_decode.py re-data/captures/x.pcapng [--port 9010=login] [--show-secrets]
python3 -I tools/protocol-re/pcap_decode.py --selftest
```

Outputs `x.pcapng.decoded.txt`, `.report.md`, `.json`. The `0x0C5A` password is masked by default. The decoder
reads the cipher table from Appendix A below, so keep that heading and hex block intact. Details and limits:
[`docs/knowledge/P01.md`](../knowledge/P01.md).

## Unknowns

- The 130-byte avatar record (`0x0C14`) is decoded in `annotations.json`. Some fields have no name;
  several names are inferred from SQL column types.
- ~~`0x1802` bytes 2–17 and 146–169 unnamed; the burst after `0x1803` has no names~~: `0x1802` is
  `PROTO_NC_CHAR_MAPLOGIN_ACK` with every field named (packets-zone.md, Z07 §1.5); the `0x1803` burst is named and
  ordered in Z01 §6 and *captured* in that order (capture-validation §5.1).
- ~~`0x0C0C` offset 17–18 (probably the WM port) is not written~~: it is `wm_port`, written by
  `GetWorldManagerConnectInfo` FUN_0040a020 (§3.1, *captured* 9110).
- ~~Whether the zone also sends the seed unprompted on accept~~: it does (§1.4, *captured*).
- Session-state gating in WM and Zone is documented in the pseudocode (WM: W01 §2 / §3.2 and W05 §4.3 `m_SessionMode`;
  zone: Z18 §1.3 session filter), not summarised here.
- Which of the client's 8 `0x0805` points in `World::LoadMap` fire for which map (two first loads sent none;
  capture-validation §4.4).
- ~~Names for most WM- and Login-only opcodes. These binaries carry no name strings for them~~: the official
  names come from the opcode enums of the 2016 server PDBs (`Files/Server/NA2016`, work item S01); `opcodes.json`
  names 2,529 of its 2,572 opcodes from them (`name_source: pdb2016`).
- Server → client messages sent from timers or other non-handler code (combat ticks, mob AI, broadcasts)
  are not listed per trigger. They do appear in `opcodes.json` when a handler sends them.

## Appendix A: XOR table

499 bytes, identical in all three servers (Login VA `0x430430`):

```
0759694a941194858c8805cba09ecd583a365b1a6a16febddf9402f82196c8e99ef7bfbdcfcdb27a009f4022fc11f90c2e12fba7740a7d78401e2ca02d06cba8b97eefde49ea4e13161680f43dc29ad486d7942417f4d665bd3fdbe4e10f50f6ec7a9a0c273d2466d322689c9a520be0f9a50b25da80490dfd3e77d156a8b7f40f9be80f5247f56f832022db0f0bb14385c1cba40b0219dff08becdb6c6d66ad45be89147e2f8910b89360d860def6fe6e9bca06c1759533cfc0b2e0cca5ce12f6e5b5b426c5b2184f2a5d261b654df545c98414dc7c124b189cc724e73c64ffd63a2cee8c8149396cb7dcbd94e232f7dd0afc020164ec4c940ab156f5c9a934de0f3827bc81300f7b3825fee83e29ba5543bf6b9f1f8a4952187f8af888245c4fe1a830878e501f2fd10cb4fd0abcdc1285e252ee4a5838abffc63db960640ab450d54089179ad585cfec0d7e817fe3c3040122ec27ccfa3e21a654c8de00b6df279ff625340785bfa7a5a5e0830c3d5d2040af60a36456f305c41c7d3798c3e85a6e5885a49a6b6af4a37b619b09401e604b32d951a4fef95d4e4afb4ad47c330233d59dce5baa5a7cd8f805fa1f2b8c725750ae6c1989ca01fcfc299b61126863654626c45b50aa2bbeef9a790223752c2013fdd95a7623f10bb5b859f99f7ae606e9a53ab450bf165898b39a6e36ee8deb
```
