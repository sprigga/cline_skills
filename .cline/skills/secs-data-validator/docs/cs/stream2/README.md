# Stream 2 - Device Control

SECS-II Stream 2 messages are used for device control, service programs, equipment constants, remote commands, and event/data collection management.

Source: [SECS-II Automated Code Generation Tool](http://hume.com/secs/msgsCS.html)

## Documentation Guides

- **[FORMAT_GUIDE.md](FORMAT_GUIDE.md)** — Comprehensive reference for SECS notation, C# parsing patterns, and the secs4net library conventions
- **[UPDATES_SUMMARY.md](UPDATES_SUMMARY.md)** — Summary of documentation updates for S2F31–S2F42, including explanation of Format vs. Codebase sections

### Enhanced Messages (S2F31–S2F42)

The following messages include detailed explanations of the **Format** section (SECS structure) and the **Codebase** section (C# implementation):

- **S2F31R/S2F32** — Date and Time Set (includes Time synchronization explanation)
- **S2F33R/S2F34** — Define Report (explains three-level nested list structure)
- **S2F35R/S2F36** — Link Event Report (event-to-report linking semantics)
- **S2F37R/S2F38** — Enable/Disable Event Report (boolean control with event list)
- **S2F41R/S2F42** — Host Command Send/Acknowledge (command execution with parameter pairs)

## Functions

| Function | Name | Direction |
|----------|------|-----------|
| [S2F1](S2F1.md) | Service Program Load Inquire | Host and Equipment |
| [S2F2](S2F2.md) | Service Program Load Grant | Host and Equipment |
| [S2F3](S2F3.md) | Service Program Send | Host and Equipment |
| [S2F4](S2F4.md) | Service Program Send Acknowledge | Host and Equipment |
| [S2F5](S2F5.md) | Service Program Load Request | Host and Equipment |
| [S2F6](S2F6.md) | Service Program Load Data | Host and Equipment |
| [S2F7](S2F7.md) | Service Program Run Send | Host and Equipment |
| [S2F8](S2F8.md) | Service Program Run Acknowledge | Host and Equipment |
| [S2F9](S2F9.md) | Service Program Results Request | Host and Equipment |
| [S2F10](S2F10.md) | Service Program Results Data | Host and Equipment |
| [S2F11](S2F11.md) | Service Program Directory Request | Host and Equipment |
| [S2F12](S2F12.md) | Service Program Directory Data | Host and Equipment |
| [S2F13R](S2F13R.md) | Equipment Constant Request | Host Only |
| [S2F14](S2F14.md) | Equipment Constant Data | Equipment Only |
| [S2F15R](S2F15R.md) | New Equipment Constant Send | Host Only |
| [S2F16](S2F16.md) | New Equipment Constant Ack | Equipment Only |
| [S2F17R](S2F17R.md) | Date and Time Request | Host and Equipment |
| [S2F18](S2F18.md) | Date and Time Data | Host and Equipment |
| [S2F19R](S2F19R.md) | Reset/Initialize Send | Host Only |
| [S2F20](S2F20.md) | Reset Acknowledge | Equipment Only |
| [S2F21R](S2F21R.md) | Remote Command Send | Host Only |
| [S2F22](S2F22.md) | Remote Command Acknowledge | Equipment Only |
| [S2F23R](S2F23R.md) | Trace Initialize Send | Host Only |
| [S2F24](S2F24.md) | Trace Initialize Acknowledge | Equipment Only |
| [S2F25R](S2F25R.md) | Loopback Diagnostic Request | Host and Equipment |
| [S2F26](S2F26.md) | Loopback Diagnostic Data | Host and Equipment |
| [S2F27R](S2F27R.md) | Initiate Processing Request | Host Only |
| [S2F28](S2F28.md) | Initiate Processing Acknowledge | Equipment Only |
| [S2F29R](S2F29R.md) | Equipment Constant Namelist Request | Host Only |
| [S2F30](S2F30.md) | Equipment Constant Namelist | Equipment Only |
| [S2F31R](S2F31R.md) | Date and Time Set Request | Host Only |
| [S2F32](S2F32.md) | Date and Time Set Acknowledge | Equipment Only |
| [S2F33R](S2F33R.md) | Define Report | Host Only |
| [S2F34](S2F34.md) | Define Report Acknowledge | Equipment Only |
| [S2F35R](S2F35R.md) | Link Event Report | Host Only |
| [S2F36](S2F36.md) | Link Event Report Acknowledge | Equipment Only |
| [S2F37R](S2F37R.md) | Enable/Disable Event Report | Host Only |
| [S2F38](S2F38.md) | Enable/Disable Event Report Acknowledge | Equipment Only |
| [S2F39R](S2F39R.md) | Multi-block Inquire | Host Only |
| [S2F40](S2F40.md) | Multi-block Grant | Equipment Only |
| [S2F41R](S2F41R.md) | Host Command Send | Host Only |
| [S2F42](S2F42.md) | Host Command Acknowledge | Equipment Only |
| [S2F43R](S2F43R.md) | Configure Spooling | Host Only |
| [S2F44](S2F44.md) | Configure Spooling Acknowledge | Equipment Only |
| [S2F45R](S2F45R.md) | Define Variable Limit Attributes | Host Only |
| [S2F46](S2F46.md) | Define Variable Limit Attributes Acknowledge | Equipment Only |
| [S2F47R](S2F47R.md) | Variable Limit Attribute Request | Host Only |
| [S2F48](S2F48.md) | Variable Limit Attribute Send | Equipment Only |
| [S2F49R](S2F49R.md) | Enhanced Remote Command | Host Only |
| [S2F50](S2F50.md) | Enhanced Remote Command Acknowledge | Equipment Only |
| [S2F51R](S2F51R.md) | Request Report Identifiers | Host Only |
| [S2F52](S2F52.md) | Return Report Identifiers | Equipment Only |
| [S2F53R](S2F53R.md) | Request Report Definitions | Host Only |
| [S2F54](S2F54.md) | Return Report Definitions | Equipment Only |
| [S2F55R](S2F55R.md) | Request Event Report Links | Host Only |
| [S2F56](S2F56.md) | Return Event Report Links | Equipment Only |
| [S2F57R](S2F57R.md) | Request Enabled Events | Host Only |
| [S2F58](S2F58.md) | Return Enabled Events | Equipment Only |
| [S2F59R](S2F59R.md) | Request Spool Streams and Functions | Host Only |
| [S2F60](S2F60.md) | Return Spool Streams and Functions | Equipment Only |
| [S2F61R](S2F61R.md) | Request Trace Identifiers | Host Only |
| [S2F62](S2F62.md) | Return Trace Identifiers | Equipment Only |
| [S2F63R](S2F63R.md) | Request Trace Definitions | Host Only |
| [S2F64](S2F64.md) | Return Trace Definitions | Equipment Only |
