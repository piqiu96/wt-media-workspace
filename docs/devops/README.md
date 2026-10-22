<!-- governance: class=stable default_load=task -->

# DevOps

This directory contains the port and deployment ledger: which components listen where, how local and online environments connect, and where each value is changed.

## Index

- [Service deployment](服务部署.md): local startup, the port table, the online architecture, release steps, and troubleshooting.

## Boundary

- Numeric values (ports, addresses, credentials, timeouts) are owned by the configuration or provider file named in the document; this directory only indexes them.
- Release procedure details stay in the owning repository's deployment guide. This directory links to them instead of copying commands.
