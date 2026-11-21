# Capture guide: recording real traffic for validation (P02)

Captures let us confirm what the decompiled code suggests: exact sizes, real field values, message order.
They are the strongest evidence level in this project ("confirmed by capture").

## Setup (Wireshark on the PC that runs the game)

- Run the 2016 server set (`Files/Server/2016/`) and the 2016 client (`Files/Client/2016`). Client and server versions
  must match, otherwise the version check (`20151116141627`) fails.
- In Wireshark, pick the interface:
  - client and server **on the same Windows PC** → *Adapter for loopback traffic capture* (Npcap loopback;
    install Npcap with loopback support if it is missing)
  - client and server on **different machines** → the network adapter that carries the game traffic
- Capture filter (enter it before starting):
  `tcp portrange 9000-9011 or tcp portrange 9110-9111 or tcp portrange 9210-9221 or tcp port 9311 or tcp port 9411 or tcp port 9511`
  If your server config uses other ports (`9Data/ServerInfo/ServerInfo.txt`), adjust it. Client ports are the
  type-20 rows (Login 9010, WM 9110, zones 9210/9212/9214/9216); the others are server links: Login←WM 9011,
  WM←zone 9111, zone links 9218–9221, AccountDB 9000, AccountLog 9311, Character DB 9411 (`PG_W00_CDB`: item,
  storage, trade writes; D03), GameLog 9511 (the filter also catches the unused OPTool ports 9015/9115/9211–9217).
  Server links run between processes on the server PC, so they show up only on its loopback adapter.
  `fiesta.lua` and the decoder (`pcap_decode.py`) show them as plaintext Fiesta packets named after the listener
  (e.g. `W00_CDB`).
- Save with *File → Save As* (all packets). *Export Specified Packets* with a display filter such as `fiesta` drops
  the TCP handshakes (the decoder then has to resync) and everything the dissector does not mark.
- Start the capture **before** launching the client. The decoder needs each connection's first server
  packet (the seed) to decrypt client→server traffic.
- Save as **pcapng** (Wireshark's default) and copy the file to this repo: `re-data/captures/`.

### Live decoding in Wireshark

1. Copy `tools/wireshark/fiesta.lua` to `%APPDATA%\Wireshark\plugins\` (create the folder if missing; the
   global `C:\Program Files\Wireshark\plugins\` also works). Restart Wireshark, or *Analyze → Reload Lua
   Plugins* (Ctrl+Shift+L). *Help → About → Plugins* should list `fiesta.lua`.
2. Display filter `fiesta`. Each Fiesta packet gets its own `Fiesta Online` subtree (several per TCP segment
   are normal). Client→server bodies are decrypted; the decrypted bytes are in the **Decrypted** tab of the
   bytes pane. Useful filters: `fiesta.name == "NC_MISC_SEED_ACK"`, `fiesta.opcode == 0x0c5a`,
   `fiesta.server == "zone"`, `fiesta.dir == "C->S"`, `_ws.expert && fiesta`.
3. Fields from hand-verified layouts show their names; fields from generated layouts are labelled
   `+offset type (guess)`. Expert info flags unknown opcodes, sizes that differ from the docs, and client
   packets sent before the seed (not decryptable).
4. Ports and password display are in *Edit → Preferences → Protocols → FIESTA*. The `0x0C5A` password shows
   as `********` (also in the Decrypted tab) unless *Show password* is ticked.
5. Start the capture before the client connects: a connection whose seed (`0x0807`) is not in the capture
   stays encrypted. After an update of the docs, copy the regenerated `fiesta.lua` again and press Ctrl+Shift+L.

Test file: `python3 -I tools/protocol-re/pcap_decode.py --selftest` prints a folder holding `synthetic.pcapng`;
open it with the plugin installed and check that the `0x0C65`/`0x0C5A` login packets decrypt.

### Marking what you did (recommended)

Right after an action, select the last packet and add a comment (*Edit → Packet Comment…*, or right-click →
*Packet Comment*). Example: `attack Slime with basic attack`, `equip Iron Sword`, `level up to 13`.
Comments are saved inside the pcapng file, and the decoder uses them as markers for the packets that follow.
Keep a short notes file next to the capture for things comments can't hold (character setup, choices made).

## Privacy

- Use a **test account**. Client→server traffic is only XOR-obfuscated, so the password in `0x0C5A` is
  recoverable from a capture. The decoder masks it by default.
- Captures contain IP addresses. Keep them in `re-data/captures/` and don't share them outside the project.

## File naming and notes

`re-data/captures/<date>_<scenario>.pcapng`, plus a notes file `<same name>.md` with the setup and anything
not covered by packet comments:

```
2026-11-12_combat-basic.md
- char "TestMage" lv 12 mage, map RouN, position near Roumen north gate
- 0:15 attacked Slime x3 with basic attack, killed 2
- 0:40 cast skill "Fire Bolt" lv1 twice
- 1:10 picked up drop (item: Slime Jelly)
```

Values you know (level, money, item names, coordinates shown in the UI) are what let the validator name fields.

## Scenarios (in order of value)

| # | Scenario | Covers |
|---|---|---|
| 1 | Login, world select, character list, logout | Login, WM core |
| 2 | Wrong password; wrong world; second login with the same account while logged in | error codes, kick (0x0C17) |
| 3 | Create a character (note every choice: name, race, class, gender, hair, face); delete one | avatar create/delete, AVATAR struct |
| 4 | Select character → enter map → stand 30 s → logout | map login, login burst, heartbeat |
| 5 | Walk, run, change map through a portal, use a town portal | movement, map link, zone handoff |
| 6 | Chat: normal, shout, whisper (2nd account), party chat | chat routing |
| 7 | Fight mobs: basic attack, 2–3 skills, die once, revive | combat, abstates, exp |
| 8 | Inventory: pick up, drop, equip/unequip, use potion, split a stack, buy/sell at NPC | items, ITEMDB |
| 9 | Upgrade/enchant an item (success and failure if possible) | upgrades |
| 10 | Trade between two accounts; open a booth | economy |
| 11 | Party: invite, accept, leave, kick; guild: create, invite | party, guild |
| 12 | Accept, progress and finish a quest | quests |
| 13 | Level up; spend stat points | progression |

Scenarios 14–54, with the database setups (SQL) and table experiments they need: `docs/plan/capture-scenarios.md` (X02).
Recorded so far: 14, 21 and 37 (capture batch 3), 24, 38 and a second run of 37 (batch 4), 45, 46 and 52 (batch 5); each
has a result line there. What they left open is in scenarios 45–50 (added by X05), 51–52 (X07) and 53–54 (X09: 53 a
stack that may not move back and the logout, 54 shared names, the emote keys, a refused rename), setups S17–S24 and
test-client cases T15–T28; its §2 gives the order and the sessions that fit together.

Two accounts on two clients (or two machines) are needed for 6, 10 and 11.

For scenarios 8–10, keep port 9411 in the filter and, if possible, note the `tItem` / `tItemOptions` rows of the items you use
before and after (SQL). Targeted item checks (account storage, capsules/chests, premium list, pets, dice/gamble/cards, forced
failures): `docs/knowledge/D03.md` "For capture scenarios (X02)".

After adding captures, run work item **P02** ("Execute the work item described in `docs/plan/items/P02.md`").
