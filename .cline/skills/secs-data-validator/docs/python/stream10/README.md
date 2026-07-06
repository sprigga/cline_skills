# Stream 10 - Terminal Services

SECS-II Stream 10 handles terminal display and keyboard I/O between host and equipment terminals.

Source: http://hume.com/secs/msgsPython.html

## Functions

| Function | Name | Direction | Reply |
|----------|------|-----------|-------|
| [S10F1](S10F1.md) | Terminal Request | Equipment → Host | S10F2 |
| [S10F2](S10F2.md) | Terminal Request Acknowledge | Host → Equipment | — |
| [S10F3](S10F3.md) | Terminal Display, Single | Host → Equipment | S10F4 |
| [S10F4](S10F4.md) | Terminal Display, Single Acknowledge | Equipment → Host | — |
| [S10F5](S10F5.md) | Terminal Display, Multi-Block | Host → Equipment | S10F6 |
| [S10F6](S10F6.md) | Terminal Display, Multi-Block Acknowledge | Equipment → Host | — |
| [S10F7](S10F7.md) | Multi-block Not Allowed | Equipment → Host | S10F8 |
| [S10F9](S10F9.md) | Broadcast | Host → Equipment | S10F10 |
| [S10F10](S10F10.md) | Broadcast Acknowledge | Equipment → Host | — |

## Data Items

- **TID** — Terminal ID, `B:1` (always)
- **TEXT** — Line of text for display, `A:120` (varies), no standard max size
- **ACKC10** — Acknowledge code, `B:1` (always)
