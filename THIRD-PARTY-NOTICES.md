# Third-party notices

This repository vendors agent skills authored by other people. They are **not**
Betterplan skills, they are not part of the `betterplan-*` registry, and they are
redistributed here under their own license.

## mattpocock/skills

Source: <https://github.com/mattpocock/skills> — *"Skills for Real Engineers."*

Installed via the [`skills`](https://www.npmjs.com/package/skills) CLI and pinned
in `skills-lock.json`. Vendored copies live under `.agents/skills/`, with
`.claude/skills/` holding symlinks into them.

| Skill | Upstream path |
|---|---|
| `domain-modeling` | `skills/engineering/domain-modeling/SKILL.md` |
| `grill-me` | `skills/productivity/grill-me/SKILL.md` |
| `grill-with-docs` | `skills/engineering/grill-with-docs/SKILL.md` |
| `grilling` | `skills/productivity/grilling/SKILL.md` |

Their supporting files (`ADR-FORMAT.md`, `GLOSSARY-FORMAT.md`,
`agents/openai.yaml`) are vendored with them and covered by the same license.

These are **not verbatim copies**: the `skills` CLI transforms a skill on
install, so the vendored `SKILL.md` differs from the upstream file it came from.
Treat upstream as the original.

**Do not edit the vendored files** — re-running the `skills` CLI overwrites them,
so edits are silently lost. To change behaviour, fork upstream or write a
Betterplan skill. (`skills-lock.json` also records a `computedHash` per skill;
what it is computed over is not documented, and it matches neither the vendored
nor the upstream bytes, so do not rely on it to notice a local edit.)

### License

```
MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
