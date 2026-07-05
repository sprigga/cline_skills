# Stream 5 — Alarm Handling

SECS-II Stream 5 messages handle alarm reporting, enabling/disabling alarms, and exception management.

Source: http://hume.com/secs/msgsPython.html

## Functions

| Function | Name | Direction |
|----------|------|-----------|
| [S5F1](S5F1.md) | Alarm Report Send | Equipment → Host |
| [S5F2](S5F2.md) | Alarm Report Ack | Host → Equipment |
| [S5F3](S5F3.md) | Enable/Disable Alarm Send | Host → Equipment |
| [S5F4](S5F4.md) | Enable/Disable Alarm Ack | Equipment → Host |
| [S5F5](S5F5.md) | List Alarms Request | Host → Equipment |
| [S5F6](S5F6.md) | List Alarm Data | Equipment → Host |
| [S5F7](S5F7.md) | List Enabled Alarm Request | Host → Equipment |
| [S5F8](S5F8.md) | List Enabled Alarm Data | Equipment → Host |
| [S5F9](S5F9.md) | Exception Post Notify | Equipment → Host |
| [S5F10](S5F10.md) | Exception Post Confirm | Host → Equipment |
| [S5F11](S5F11.md) | Exception Clear Notify | Equipment → Host |
| [S5F12](S5F12.md) | Exception Clear Confirm | Host → Equipment |
| [S5F13](S5F13.md) | Exception Recover Request | Host → Equipment |
| [S5F14](S5F14.md) | Exception Recover Acknowledge | Equipment → Host |
| [S5F15](S5F15.md) | Exception Recovery Complete Notify | Equipment → Host |
| [S5F16](S5F16.md) | Exception Recovery Complete Confirm | Host → Equipment |
| [S5F17](S5F17.md) | Exception Recovery Abort Request | Host → Equipment |
| [S5F18](S5F18.md) | Exception Recovery Abort Ack | Equipment → Host |

## Message Pairs

- **S5F1/S5F2** — Alarm report and acknowledgment
- **S5F3/S5F4** — Enable or disable a specific alarm
- **S5F5R/S5F6** — List all alarms (request/response)
- **S5F7R/S5F8** — List enabled alarms (request/response)
- **S5F9/S5F10** — Exception post notification and confirmation
- **S5F11/S5F12** — Exception clear notification and confirmation
- **S5F13R/S5F14** — Exception recovery request and acknowledge
- **S5F15/S5F16** — Exception recovery complete notification and confirmation
- **S5F17R/S5F18** — Exception recovery abort request and ack
