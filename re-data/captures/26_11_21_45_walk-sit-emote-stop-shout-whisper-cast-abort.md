Scenario 45 (docs/plan/capture-scenarios.md §3 "45"): second client in sight II, what `s14` left open: walk relay, sit, emote stop, shout out of sight, whisper to an unknown receiver, a mob's hits next to a bystander, cast abort, leaving sight
- recorded on the server PC by tools/capture/45/45-server.ps1 capture-start (dumpcap, loopback + LAN, filter of capture-guide.md)
- account A: "admin", character "X45A" (created as Trickster, made level 40 / GM 100 by 45-server.ps1 prep), world "Enid"
- account B: "testaccountB", character "X45B" (created as Archer, made SharpShooter 40 / GM 100 by prep)
- prep also wrote: B skill 4500 "Distant Shot [01]" (1 399 ms cast); tutorial done for both; A logs in at RouN 6443,9850, B at
  RouN 6843,9850 (400 apart, MapInfo.Sight 1600)
- prep output: X45A level 40 (expected 40); X45B level 40 class 14 (40 / 14)
- server DB readings: 26_11_21_45_walk-sit-emote-stop-shout-whisper-cast-abort-db.txt (snapshots "after prep", "before cleanup")
- server logs: 26_11_21_45_walk-sit-emote-stop-shout-whisper-cast-abort-logs\ (copied by collect)
- clients run on: different PC than server, but both clients on same PC ; setup typed by gmtype.ps1? yes (or by hand)
- no &hide / &dimension in this run (P02-B27)
- write every message text the client shows; "nothing" is an answer too

Start
- capture started; A logged in, then B; tutorial question shown? no (expected no)
- A sees B and B sees A right after login? yes
- typed 45-setupB.txt into B; B equipped the Heavy Bow? yes ; Distant Shot [01] in B's skill list? yes

Step 1: walk relay
- B switched to walking (walk / run toggle), walked five steps -> A saw B walk (slow)? yes
- B switched back to running, ran two steps -> A saw B run? yes

Step 2: sit / stand as an action
- B used the action "Sit" -> A saw B sit? yes ; B's own client showed the sit? yes
- 5 s later B used "Stand" -> A saw B stand? yes

Step 3: emote stop (one dance emote, ended three ways, 10 s apart)
- emote used: dance 2
- way 1: B played the emote, then the same emote again -> emote stopped on A's screen? no ; on B's? no
	- Emote started from the beginning
- way 2: B played the emote, then pressed Esc -> stopped on A? no ; on B? no
- way 3: B played the emote, then took a step -> stopped on A? yes ; on B? yes

Step 4: shout out of sight
- B ran south (towards RouN 6888,7045, the s14 spawn) until A no longer saw B -> B vanished on A's screen? yes ; A vanished on B's? yes
- A shouted "x45 shout A" -> B saw it? yes (expected yes) ; text on B's screen: "[X45A]: x45 shoud A" (in chat window)
- B ran back to A -> A and B see each other again? yes

Step 5: whisper to an unknown receiver
- A whispered X45Nobody (as the receiver, text "x45 whisper") -> message on A's screen: Cannot find the recipient
- B got anything? no (expected no)

Step 6: a mob hits B next to A (A only watches)
- A stands where it logged in; B stands next to it, ~400 away (not closer than ~300: the mob must not pick A)
- typed 45-mob.txt into B (spawns an Archmage Book at B) -> it attacked B by itself? yes (if not within 10 s: &mb Goblin, used: no)
- B let it hit three times without hitting back -> 3 hits seen by B? yes ; by A? yes ;
- the mob ever attacked A? no (expected no)
- B died & ran back to the mob
- B killed it (skill: Distant Shot [1]) -> dead? yes

Step 7: cast abort, then a full cast
- typed 45-slime.txt into B (full SP, a Slime at B)
- B targeted the Slime, started Distant Shot [01] and took a step before the bar was full -> cast bar stopped? yes ;
  message on B: nothing ; A saw B's cast start? yes and stop? yes
- B cast Distant Shot [01] once more to the end (if refused as "cannot use yet", wait 60 s and note it: no) -> A saw the shot? yes ;
  Slime dead? yes

Step 8: leaving sight
- B walked (walk mode on) south until A no longer saw B, then stopped -> B vanished on A's screen? yes
- B switched back to running

End
- both logged out to the login screen, dumpcap stopped (Ctrl+C in its window)
- cleanup output: X45A / X45B p_Char_Delete returned 0 / 0 (expected 0 / 0)
