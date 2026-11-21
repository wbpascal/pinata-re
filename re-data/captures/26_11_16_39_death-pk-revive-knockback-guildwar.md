Scenario 39 (docs/plan/capture-scenarios.md §3 "39", with the "Added by X05" steps 7–10): combat extras: death penalty, PK, revive item, knock-back, rebirth, guild war kill, boss announcement
- recorded on the server PC by tools/capture/39/39-server.ps1 capture-start (dumpcap, loopback + LAN, filter of capture-guide.md)
- account A: "admin", character "X39A" (created as Archer, made SharpShooter 40 / GM 100 by 39-server.ps1 prep), world "Enid"
- account B: "testaccountB", character "X39B" (created as Cleric, made Guardian 40 / GM 100 by prep)
- prep also wrote: 2 000 000 cen each; A exp 1 509 279 (level 40 runs from 1 389 279 to 1 628 577); A skills 4028 "Power Shot [09]" +
  4500 "Distant Shot [01]"; B skill 2030 "Rebirth [01]"; tutorial done for both; both start in RouN next to the guild NPC (6713,5495)
- prep output: X39A level ___ class ___ exp ___ (expected 40 / 14 / 1509279); X39B level ___ class ___ (40 / 10)
- server DB readings: 26_11_16_39_death-pk-revive-knockback-guildwar-db.txt (snapshots "after prep", "after guilds", "before cleanup")
- clients run on: ___ ; setup typed by gmtype.ps1? ___ (or by hand)
- write every message text the client shows; "nothing" is an answer too
- exp: read it from A's character window before and after each death (the bar's number, or the tooltip). Expected loss per mob
  death on Burning Hill: 2 392 (1 % of level 40, × ExpLostAtDeadByMob 1000 ‰); 2 751 would mean the level table is read one level up
- every death: the death menu appears; write which buttons it shows (town revive / revive item / revive here) and the countdown.
  Do not stay dead longer than 3 minutes (auto revive)

Start
- capture started; A logged in, then B; tutorial question shown? ___ (expected no)
- A: GM commands work? ___ ; Power Shot [09] and Distant Shot [01] in the skill list? ___ ; B: Rebirth [01] in the skill list? ___
- typed 39-setupA.txt into A, 39-setupB.txt into B; A equipped the Heavy Bow, B the Horseman's Hammer? ___ ; Tear of Legel x5 in A's inventory? ___

Guilds (both at the guild NPC RouGuildBrom, RouN)
- A: NPC -> found a guild "X39GuildA", password "1234", the "War" box ticked -> message: ___ ; money left ___ (expected 1 000 000)
- B: the same with "X39GuildB" -> message: ___ ; money left ___
- did the found window have the War / No war boxes? ___
- server: .\39-server.ps1 snapshot -Label "after guilds" -> nType of the two guilds ___ / ___ (must not be 0 for step 4)

Move
- typed 39-moveA.txt into A, 39-moveB.txt into B; both on Burning Hill, in sight of each other? ___

Step 1a: revive item used while alive
- A double-clicked the Tear of Legel in the inventory -> message: ___ (expected "The selected item does not have any effect when used.") ; Tears left ___ (expected 5)

Step 1: die to a mob, revive with the item
- A exp before ___
- typed 39-die.txt into A; A attacked the slime until it killed A -> killed? ___
- death menu buttons: ___ ; countdown ___ s
- A chose the revive item -> revived where? ___ (expected on the spot) ; HP after ___ ; Tears left ___ (expected 4) ; message: ___
- A exp after ___ ; lost ___ (expected 2 392) ; "EXP lost" message: ___

Step 2: die again, town revive
- A exp before ___
- typed 39-die.txt into A, died to the slime -> death menu buttons: ___
- A chose the town revive -> where? ___ (expected Burning Hill regen point, no loading screen) ; message: ___
- A exp after ___ ; lost ___ (expected 2 392)

Step 5: knock-back
- A: &staticdamage 1 still on? ___ (39-die.txt set it); &mb Slime; A cast Power Shot [09] on the slime -> slime pushed back? ___ ; slime alive? ___
- A: &staticdamage 0; after 7 s Power Shot [09] again -> slime dead? ___ ; pushed? ___
- A: &mb Slime, targeted it, typed &knockback -> who moved, A or the slime? ___ (expected A, thrown back from the slime) ; message: ___
- B saw the push(es)? ___

Step 7: skill refusals (cast at a slime: &mb Slime first if none is left; type &staticdamage 1 so it lives)
- abort: A started Distant Shot [01] (1.4 s cast) and pressed Esc at once -> cast bar stopped? ___ ; message: ___ ; B saw A's cast stop? ___
- cool-time: A cast Distant Shot to the end, then at once again -> message: ___ (expected "Cannot use the skill yet.") ; or the client refused itself (button greyed): ___
- SP: A typed &setsp 1, cast Power Shot -> message: ___ (expected "Not enough SP.") ; or the client refused itself: ___ ; then &fullpoint
- range: A walked more than ~600 away from the slime, cast Power Shot -> message: ___ (expected "The target is out of casting range.") ; or the client walked A into range: ___

Step 9: rebirth (before the guild war: B can buff A only while they are not enemies)
- B targeted A and cast Rebirth [01] -> buff icon on A? ___ ; message: ___
- A exp before ___ ; typed 39-die.txt, died to the slime -> death menu buttons: ___ (expected a "revive here" choice)
- A accepted the revive here -> revived where? ___ (expected on the spot, no loading screen) ; HP after ___ ; A exp after ___ ; lost ___
- A typed &setabstate StaRebirth (Rebirth has an 80 s cool-time; or B waits 80 s and casts again: which? ___) -> buff icon? ___
- A exp before ___ ; 39-die.txt, died -> "revive here" choice? ___ ; A REFUSED it -> what happened? ___ ; then the town revive -> where? ___
- A exp after ___ ; lost ___

Step 8: in a party
- A invited B, B accepted -> party window shows both? ___
- A exp before ___ ; 39-die.txt, A died to the slime -> B's party window: A's HP bar ___ ; party still there? ___ ; A town revive
- A exp after ___ ; lost ___ (expected 2 392)
- A typed &pvp 1 -> message on A ___ and on B ___ (expected "This area is enabled for PvP.")
- B tried to attack A (party member, free PvP) -> possible? ___
- if yes: A typed &sethp 1, B hit A once -> A dead? ___ ; messages on A ___ and on B ___ ; party still there? ___ ; A town revive
- A exp before ___ after ___ (expected no loss: Burning Hill has ExpLostAtDeadByPly 0)

Step 3: PK without a party
- B left the party -> message: ___
- A typed &sethp 1, B hit A once (free PvP still on) -> A dead? ___ ; messages on A ___ and on B ___ ; A town revive
- A exp before ___ after ___ (expected no loss)
- optional 3b, PK where the player rate is not 0 (Abysmal Cave, ExpLostAtDeadByPly 1000; its mobs are strong, stay at the arrival point):
  A and B: &linkto ValDn02 1159 11349 ; A: &pvp 1 ; A exp before ___ ; A: &sethp 1, B hit A -> A dead? ___ ; killed by a mob instead? ___
  A town revive; A exp after ___ ; lost ___ (expected 1 890 = ExpLostAtPvP of level 40; 2 040 would be the level-41 row)
  A: &pvp 0 -> message ___ ; both back: 39-moveA.txt / 39-moveB.txt
- back on Burning Hill: A typed &pvp 0 -> message on A ___ and on B ___ (expected PvP off)
- B tried to attack A now -> possible? ___ (expected no)

Step 4, part 1: declare the guild war (A is master of X39GuildA)
- A: guild window -> guild war -> request against "X39GuildB" -> message on A ___ ; on B ___ (war starts 5 minutes later)

Step 6: boss announcement (while waiting for the war)
- typed 39-helga.txt into A, A attacked Helga at once -> Helga dead with the first hit? ___ ; A died first? ___
- announcement text on A ___ and on B ___ (expected a world announcement about Helga)
- A typed &staticdamage 0

Step 4, part 2: the guild war kill (Burning Hill, free PvP off)
- war start message on A ___ and on B ___ (about 5 minutes after the request)
- B tried to attack A -> possible? ___ (expected yes: EnemyGuild map, guilds at war)
- A typed &sethp 1, B hit A once -> A dead? ___ ; messages on A ___ and on B ___ ; war score shown anywhere? ___ (expected no: the 2016 client has no handler)
- A exp before ___ after ___ (expected no loss: not a free-PvP kill) ; A town revive

End
- A typed 39-endA.txt (&staticdamage 0, &pvp 0)
- capture stopped; A and B logged out to the login screen; .\39-server.ps1 cleanup -Dest <this folder> done? ___
- anything unexpected: ___
