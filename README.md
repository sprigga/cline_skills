# cline_skills

A collection of [Cline](https://docs.cline.bot) skills for semiconductor equipment software development, with a focus on SECS-II / GEM protocol tooling.

## What is a Cline Skill?

Skills are modular instruction sets that Cline loads on demand. Unlike rules (always-on, always consuming context), skills use **three-tier progressive loading**:

| Tier | When loaded | Token cost | Content |
|------|-------------|-----------|---------|
| Metadata | Session start (always) | ~100 tokens/skill | `name` + `description` |
| Instructions | On trigger | < 5 k tokens | `SKILL.md` body |
| Resources | On demand | Unbounded | `docs/`, `scripts/`, `templates/` |

Cline either auto-triggers a skill by matching the user's request against each skill's `description`, or the user can force-trigger with `/skill-name`.

For authoring guidance see [`docs/cline-skills-guide.md`](docs/cline-skills-guide.md).

---

## Skills

### `secs-data-validator`

Validates SECS-II SML (SECS Message Language) message format.

**Triggers on:** "check SECS format", "validate SML", "SECS-II message correct?", "檢查 SECS log", "幫我檢查 SML 格式", or any request to check `.sml` / `.log` files for format errors.

#### Quick start

```bash
# Validate a .sml file
python secs-data-validator/scripts/validate_sml.py path/to/file.sml

# Validate a SECS log file (timestamp lines, hex dumps, metadata are filtered automatically)
python secs-data-validator/scripts/validate_sml.py path/to/file.log

# Pipe SML from stdin
echo "S1F1 W\n." | python secs-data-validator/scripts/validate_sml.py

# Batch validate
for f in path/to/*.sml; do
  echo "=== $f ==="; python secs-data-validator/scripts/validate_sml.py "$f"; echo
done
```

**Requirements:** Python 3.10+

**Exit codes:** `0` = valid, `1` = invalid, `2` = file error

#### What it validates

| Check | Detail |
|-------|--------|
| Message header | `S1–S127`, `F0–F255`; W-bit on odd functions only |
| Item types | `L A J B BOOLEAN U1 U2 U4 U8 I1 I2 I4 I8 F4 F8` |
| Numeric ranges | e.g. U1: 0–255, I4: −2 147 483 648–2 147 483 647 |
| String quoting | `<A 'text'>` required; unquoted strings flagged |
| Bracket balance | Unclosed `<` / missing `>` reported with token position |
| Message terminator | Missing `.` reported per message |
| Log noise filtering | Timestamps, hex dumps, `SxFy H2E/E2H` metadata, `< >` markers stripped |

#### Output file management

When generating code, analysis reports, or processed files, the skill automatically organizes output into the `demo/` directory:

```
demo/
├── python/          # Python scripts and code examples
├── csharp/          # C# handlers and implementation code  
├── logs/            # Processed and analyzed log files
├── templates/       # Generated SML template files
├── reports/         # Validation reports and analysis outputs
└── docs/            # Generated documentation
```

This structure keeps generated content separate from source files while maintaining clear organization by file type.

#### Included reference docs

| Path | Content |
|------|---------|
| `secs-data-validator/docs/sml-syntax.md` | Full SML syntax, item types, value ranges |
| `secs-data-validator/docs/cs/` | C# (secs4net) per-stream message format guides (Streams 1–2, 5–10) |
| `secs-data-validator/docs/python/` | Python per-stream message handler guides (Streams 1–3, 5–7, 9–10) |
| `secs-data-validator/templates/example.sml` | Pure SML: 4 messages (S1F1, S1F2, S6F11, S2F41) |
| `secs-data-validator/templates/init-sequence.log` | Equipment init sequence: 19 messages |
| `secs-data-validator/templates/s5f3-alarm.log` | Alarm enable/disable: 2 messages |
| `secs-data-validator/templates/s2f23-trace.log` | Trace init + data sequence: 8 messages |

---

## Repository structure

```
cline_skills/
├── README.md
├── docs/
│   ├── cline-skills-guide.md     # Authoring guide: structure, triggers, naming
│   └── strategy-pattern.md       # Design pattern reference (Strategy Pattern / Java examples)
├── demo/                          # Generated output files organized by type
│   ├── python/                    # Python scripts and examples
│   ├── csharp/                    # C# code and handlers
│   ├── logs/                      # Processed log files
│   ├── templates/                 # SML template files
│   ├── reports/                   # Validation reports and analysis
│   └── docs/                      # Generated documentation
└── secs-data-validator/
    ├── SKILL.md                   # Skill entry point (frontmatter + instructions)
    ├── scripts/
    │   └── validate_sml.py        # Recursive-descent SML parser/validator
    ├── docs/
    │   ├── sml-syntax.md
    │   ├── cs/                    # C# stream guides + FORMAT_GUIDE.md
    │   └── python/                # Python stream guides
    └── templates/
        ├── example.sml
        ├── init-sequence.log
        ├── s5f3-alarm.log
        └── s2f23-trace.log
```

`.cline/skills/` mirrors the skills directory for Cline auto-discovery.

---

## Adding a new skill

1. Create `<skill-name>/SKILL.md` with YAML frontmatter (`name`, `description`) and instructions.
2. Add optional `docs/`, `scripts/`, `templates/` subdirectories as needed.
3. Register in `.cline/skills/` (symlink or copy).
4. Update the skills table in this README.
5. If the skill generates output files, document the `demo/` subdirectory structure in SKILL.md.

See [`docs/cline-skills-guide.md`](docs/cline-skills-guide.md) for naming conventions, description writing tips, and when to use scripts vs. inline instructions.
