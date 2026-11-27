# pinata-re

Reverse-engineering material for [`pinata`](https://github.com/wbpascal/pinata), the rebuild of the Fiesta Online server:
the original 2016 server and client binaries with their data tables, Ghidra projects and exports, packet captures,
and the behavioural specification reconstructed from them (`docs/protocol/`, `docs/pseudocode/`, `docs/knowledge/`,
work items in `docs/plan/`).

- Clone it next to `pinata` (`../pinata-re` from the server checkout); binaries and data tables are in Git LFS.
- `tools/sync-server.sh [<server-checkout>]` (default `../pinata`) copies `9Data` and `opcodes.json` into the server
  and prints the commit they came from.
- Issues are tracked in `wbpascal/pinata` only.
- Agents and people working here start with [`AGENTS.md`](AGENTS.md).
