# Model character abilities in deterministic sim

- STATUS: OPEN
- PRIORITY: 75
- TAGS: wasm, security

The sim core covers universal mechanics (spawn queue, chops, stamina deadlines, death). The 8 heroes' abilities (fargol flame/phoenix, ali flurry, ahmad shield, parsa sacrifice, fateme/erfan/amirhossein/nima specifics) are not modeled, so ability-affected rounds cannot replay-verify yet. Design ability declarations as trace inputs, port each ability's rules to integer-only Rust with goldens, and extend server replay to apply them. Follow-up of the sim-alignment work.
