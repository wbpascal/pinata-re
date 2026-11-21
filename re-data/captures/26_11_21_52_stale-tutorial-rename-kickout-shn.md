Scenario 52 (docs/plan/capture-scenarios.md §3 "52"): character select and session II: the stale tutorial copy (P02-B33), the 2016 p_Char_Rename (S20), &kickout with a real user number, the SHN checksum refusal
- recorded on the server PC by tools/capture/52/52-server.ps1 capture-start (dumpcap, loopback + LAN, filter of capture-guide.md; the zone ring ports 9211-9217 are inside it)
- account A: "admin", characters before prep: Test1235, Test2, X37Del ; world "Enid"
- account B: "testaccountB", character "X52B" (created in the client for this run: yes)
- prep (52-server.ps1 prep): X37Del renamed "X52-Dash" (GM 100, RouN, tutorial state 2); X52B to RouN (tutorial state 2); S20 installed (2016 p_Char_Rename)
- prep output: see output files
- server DB readings: 26_11_21_52_stale-tutorial-rename-kickout-shn-db.txt ; server logs: 26_11_21_52_stale-tutorial-rename-kickout-shn-logs\ (copied by collect)
- clients run on: different PC than server (both clients on same PC)
- write every message text the client shows; "nothing" is an answer too

Step 1: second start with the stale "RouT" copy (P02-B33)
- admin logged in, world "Enid"
- "Create", any class, name "X52Tut" -> created? yes ; message: nothing
- back to the server list (or login screen: which? server list), world "Enid" again -> X52Tut in the list? yes
- selected X52Tut, Start -> tutorial question shown? yes ; its text: Would you like to start the tutorial?
- answered No / skip -> message: The Map is under maintenance. Please try again later. (expected "The Map is under maintenance") ; still on the character list? yes
- Start again at once (same character, nothing else in between) -> message: The Map is under maintenance. Please try again later. (expected the same, at once) ; tutorial question again? no (expected no)
- back to the server list, world "Enid" again, selected X52Tut, Start -> tutorial question? no (expected no) ; in game? yes ; map: Roumen (RouN) (expected Roumen)
- menu -> character select

Step 2: the 2016 p_Char_Rename (S20)
- selected X52-Dash -> rename window opened? yes ; its text: Character name must be changed.
- entered "Test1235" (a name in use) -> message: nothing (expected "The name cannot be used.") ; name shown in the list: Test1235 (expected X52-Dash)
- select new Test1235 (former X52-Dash) -> Start -> Loads successfully
	- For some reason starts next to town portal in RouN (maybe position of old Test1235?). However, stats and inventory are those of X52-Dash (level 1, inventory empty)
- server: .\52-server.ps1 snapshot -Label "after taken name" -> X52-Dash renamed in the DB? yes (expected no) ; duplicate_name rows: yes (expected none)
  (if the rename went through and two characters are now "Test1235": note it, it is the finding; skip the next two lines)
- selected X52Ren, Start -> in game? yes ; map: Roumen (RouN) (expected Roumen) ; GM commands work (e.g. &fullpoint)? yes
	- Regarding the GM commands: There is an option that automatically makes all character GM level 100  if they are created by a GM account.

Step 3: &kickout with a real user number
- B: testaccountB logged in, X52B started -> in game on Roumen? yes ; tutorial question? no (expected no)
- A typed "&kickout X52B" -> message on A: "[Notice]  is banned" (expected "X52B is banned")
- B's client: Disconnected from the server. (expected "Disconnected from the server.", client closes) ; B left the game? yes.
- server: .\52-server.ps1 move-b (B at the login screen) -> done? yes
- B logged in again, X52B started -> in game on Forest of Mist? yes (expected RouVal01, another zone)
- A typed "&kickout X52B" again -> message on A: [Notice] #X52B is not in game (the # is an unprintable character) (expected "… is not in game", the name read one byte early: write exactly what it shows)
- B's client: nothing, stays in game (expected nothing, B stays in game)
- B: menu -> exit game (B saved on Forest of Mist; client to the login screen or closed) -> done? yes

Step 4: SHN mismatch (zone 1, port 9212, hosts Forest of Mist)
- server: .\52-server.ps1 shn-break -> md5 before / after: B6FCFBD3005D25F5539FE07F63C125E1 / 7A01298C392B74D7EC30911E3A74D437 ; READY? yes
- B logged in, X52B started (loads Forest of Mist) -> message: The client has been illegally manipulated. Please reinstall the client. (expected "The client has been illegally manipulated. Please reinstall the client.") ; screen afterwards: login screen
- server: .\52-server.ps1 shn-restore -> restored, READY? yes
- B logged in again -> in game on Forest of Mist? yes ; message: nothing
- B: menu -> exit game ; A: menu -> exit game (both at the login screen or closed)

End
- capture stopped (Ctrl+C in the dumpcap window)
- server: .\52-server.ps1 cleanup -Dest <folder of this file>
