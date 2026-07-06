# SECS-II Stream 7 — Process Program

Stream 7 handles **Process Program** data transfer and management between Host and Equipment.

Source: [Hume SECS-II Automated Code Generation Tool](http://hume.com/secs/msgsPython.html#S1F2E)

## Function Summary

| Function | Description | Direction |
| --- | --- | --- |
| [S7F1R](s7f1.md) | Process Program Load Inquire | Sent by Host and Equipment |
| [S7F2](s7f2.md) | Process Program Load Grant | Sent by Host and Equipment |
| [S7F3R](s7f3.md) | Process Program Send | Sent by Host and Equipment |
| [S7F4](s7f4.md) | Process Program Send Acknowledge | Sent by Host and Equipment |
| [S7F5R](s7f5.md) | Process Program Request | Sent by Host and Equipment |
| [S7F6](s7f6.md) | Process Program Data | Sent by Host and Equipment |
| [S7F7R](s7f7.md) | Process Program ID Request | Sent by Equipment Only |
| [S7F8](s7f8.md) | Process Program ID Data | Sent by Host Only |
| [S7F9R](s7f9.md) | Matl/Process Matrix Request | Sent by Host and Equipment |
| [S7F10](s7f10.md) | Matl/Process Matrix Data | Sent by Host and Equipment |
| [S7F11[R]](s7f11.md) | Matl/Process Matrix Update Send | Sent by Host Only |
| [S7F12](s7f12.md) | Matl/Process Matrix Update Ack | Sent by Equipment Only |
| [S7F13[R]](s7f13.md) | Matl/Process Matrix Delete Entry Send | Sent by Host Only |
| [S7F14](s7f14.md) | Delete Matl/Process Matrix Entry Acknowledge | Sent by Equipment Only |
| [S7F15R](s7f15.md) | Matrix Mode Select Send | Sent by Host Only |
| [S7F16](s7f16.md) | Matrix Mode Select Ack | Sent by Equipment Only |
| [S7F17R](s7f17.md) | Delete Process Program Send | Sent by Host Only |
| [S7F18](s7f18.md) | Delete Process Program Acknowledge | Sent by Equipment Only |
| [S7F19R](s7f19.md) | Current Process Program Dir Request | Sent by Host Only |
| [S7F20](s7f20.md) | Current Process Program Data | Sent by Equipment Only |
| [S7F21](s7f21.md) | Process Capabilities Request | Sent by Host Only |
| [S7F22](s7f22.md) | Process Capabilities Data | Sent by Equipment Only |
| [S7F23R](s7f23.md) | Formatted Process Program Send | Sent by Host and Equipment |
| [S7F24](s7f24.md) | Formatted Process Program Acknowledge | Sent by Host and Equipment |
| [S7F25R](s7f25.md) | Formatted Process Program Request | Sent by Host and Equipment |
| [S7F26](s7f26.md) | Formatted Process Program Data | Sent by Host and Equipment |
| [S7F27R](s7f27.md) | Process Program Verification Send | Sent by Equipment Only |
| [S7F28](s7f28.md) | Process Program Verification Acknowledge | Sent by Host Only |
| [S7F29R](s7f29.md) | Process Program Verification Inquire | Sent by Equipment Only |
| [S7F30](s7f30.md) | Process Program Verification Grant | Sent by Host Only |
| [S7F31R](s7f31.md) | Verification Request Send | Sent by Host Only |
| [S7F32](s7f32.md) | Verification Request Acknowledge | Sent by Equipment Only |
| [S7F33R](s7f33.md) | Process Program Available Request | Sent by Host and Equipment |
| [S7F34](s7f34.md) | Process Program Availability Data | Sent by Host and Equipment |
| [S7F35R](s7f35.md) | Process Program for MID Request | Sent by Host and Equipment |
| [S7F36](s7f36.md) | Process Program for MID Data | Sent by Host and Equipment |
| [S7F37R](s7f37.md) | Large PP Send | Sent by Host and Equipment |
| [S7F38](s7f38.md) | Large PP Send Ack | Sent by Host and Equipment |
| [S7F39R](s7f39.md) | Large Formatted PP Send | Sent by Host and Equipment |
| [S7F40](s7f40.md) | Large Formatted PP Ack | Sent by Host and Equipment |
| [S7F41R](s7f41.md) | Large PP Req | Sent by Host and Equipment |
| [S7F42](s7f42.md) | Large PP Req Ack | Sent by Host and Equipment |
| [S7F43R](s7f43.md) | Large Formatted PP Req | Sent by Host and Equipment |
| [S7F44](s7f44.md) | Large Formatted PP Req Ack | Sent by Host and Equipment |

## Categories

### Process Program Load (S7F1–S7F6)
Basic process program loading and data transfer.

### Process Program ID (S7F7–S7F8)
Process program identification queries.

### Material/Process Matrix (S7F9–S7F16)
Matrix management: request, update, delete entries, and mode selection.

### Process Program Management (S7F17–S7F22)
Delete process programs, query current directories, and process capabilities.

### Formatted Process Programs (S7F23–S7F26)
Send/request formatted (structured) process programs.

### Process Program Verification (S7F27–S7F32)
Verify process program integrity: send, inquire, grant, and request verification.

### Process Program Availability (S7F33–S7F36)
Query process program availability and mapping to material IDs.

### Large Process Programs (S7F37–S7F44)
Multi-block transfer for large process programs (both raw and formatted).
