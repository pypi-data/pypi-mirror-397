<h1 align="center">
  <img src="assets/vibe-check-logo.svg" alt="Vibe Check" width="80" style="vertical-align: middle;" />
  Vibe Check
</h1>

<p align="center">
  <strong>Stop design drift when vibe coding with AI</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/vibe-check/"><img src="https://img.shields.io/pypi/v/vibe-check?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/vibe-check/"><img src="https://img.shields.io/pypi/dm/vibe-check" alt="Downloads"></a>
  <a href="https://github.com/ihlamury/vibe-check/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

<p align="center">
  <a href="#the-problem">The Problem</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#ai-integration">AI Integration</a> •
  <a href="#roadmap">Roadmap</a>
</p>

---

<p align="center">
  <img src="assets/demo.gif" alt="Vibe Check Demo" width="700" />
</p>

---

## The Problem

You're **vibe coding** with Cursor, Claude, or Copilot. Shipping fast. Feels great.

But by the 5th feature, your codebase looks like this:
```jsx
// File 1: p-4, rounded-lg, bg-blue-500
// File 2: p-3, rounded-xl, bg-[#3b82f6]
// File 3: p-5, rounded-md, bg-blue-600
// File 4: padding: 18px, border-radius: 10px
```

**No consistent spacing. Random colors. Mixed border radius. Design chaos.**

The AI doesn't know your design system. It just generates *something that works*.

---

## Quick Start

### Install
```bash
pip install vibe-check
```

### Check Your Codebase
```bash
cd your-project
vibe check
```

See what's drifting:
```
🔴 ERRORS — Must fix
  1. colors: Replace arbitrary color `bg-[#ff6b6b]` with a theme color
  2. typography: Move `font-[Comic_Sans]` to tailwind.config.js

🟡 WARNINGS — Should fix
  1. border-radius: Reduce from 4 values to 2-3

🔵 SUGGESTIONS — Consider fixing
  1. colors: Consolidate 6 one-off colors

Summary: 2 errors · 1 warning · 1 suggestion
```

### Lock & Teach Your AI

Once you've fixed the errors, lock your design system:
```bash
vibe init
```

This will:
1. 🔒 Lock your design system to `.vibe/system.json`
2. 📝 Generate `.cursorrules` and `CLAUDE.md`
3. 🔌 Configure MCP server for Claude

**That's it.** Your AI tools now follow your design system.

---

## Features

### 🔍 Scanner

Extracts design tokens from your Tailwind + CSS codebase:

| Category | What It Finds |
|----------|---------------|
| **Spacing** | `p-4`, `m-2`, `gap-6`, `px-[10px]` |
| **Colors** | `bg-blue-500`, `text-gray-900`, `bg-[#ff6b6b]` |
| **Typography** | `text-xl`, `font-bold`, `font-[Comic_Sans]` |
| **Border Radius** | `rounded-lg`, `rounded-[8px]` |
| **Shadows** | `shadow-md`, `shadow-[0_4px_6px_rgba(0,0,0,0.1)]` |

### 🔒 Lock File

Generates `.vibe/system.json` — your source of truth:
```json
{
  "spacing": { "scale": [0, 2, 4, 6, 8, 12, 16] },
  "colors": [
    { "name": "primary", "value": "blue-500", "hex": "#3b82f6" },
    { "name": "neutral", "value": "gray-600" }
  ],
  "typography": {
    "font_sizes": ["sm", "base", "lg", "xl"],
    "font_weights": ["normal", "medium", "bold"]
  },
  "border_radius": { "scale": ["md", "lg", "full"] },
  "shadows": { "scale": ["sm", "md", "lg"] }
}
```

---

## AI Integration

### Cursor

Reads `.cursorrules` automatically. No setup needed.

### Claude Code

Reads `CLAUDE.md` automatically + connects via MCP for live queries:
```
You: Create a Card component
Claude: [uses get_design_system tool]
Claude: Here's a Card using your design system:
        - bg-white (from your palette)
        - p-4 (from your spacing scale)
        - rounded-lg (from your border radius)
```

### Claude Desktop

Connects via MCP server. Ask Claude to validate styles or suggest fixes.

---

## Commands

| Command | Description |
|---------|-------------|
| `vibe check` | Scan for design inconsistencies |
| `vibe init` | Lock design system + configure AI tools |
| `vibe lock` | Lock design system only |
| `vibe serve` | Start MCP server manually |

### Options
```bash
vibe check              # Scan current directory
vibe check ./src        # Scan specific path
vibe check -v           # Verbose output
vibe check -o json      # JSON output (for CI)

vibe init               # Full setup
vibe init -y            # Skip prompts
vibe init --skip-mcp    # Skip MCP configuration
```

---

## Supported Tech

**Frameworks:** React, Next.js, Vue, Nuxt, Svelte, plain HTML

**Styling:** Tailwind CSS, vanilla CSS, SCSS

**AI Tools:** Cursor, Claude Code, Claude Desktop

---

## Roadmap

### Now
- [x] CLI scanner for Tailwind + CSS
- [x] Design system lock
- [x] `.cursorrules` + `CLAUDE.md` generation
- [x] MCP server for Claude

### Next
- [ ] `tailwind.config.js` export
- [ ] GitHub Action for PR checks
- [ ] Figma plugin

---

## Contributing
```bash
git clone https://github.com/ihlamury/vibe-check.git
cd vibe-check
pip install -e ".[dev]"
pytest
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## License

MIT © [Yagiz Ihlamur](https://github.com/ihlamury)

---

<p align="center">
  <strong>Stop the design drift. Start the vibe check.</strong>
</p>

<p align="center">
  <a href="https://github.com/ihlamury/vibe-check">⭐ Star on GitHub</a> •
  <a href="https://x.com/yagizihlamur">𝕏 Follow</a>
</p>