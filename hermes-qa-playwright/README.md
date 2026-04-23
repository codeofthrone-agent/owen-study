# hermes-qa-playwright

> Ported from [gstack/qa](https://github.com/garrytan/gstack/tree/main/qa) by Garry Tan.
> Rewritten for Hermes Agent with Playwright as the browser automation engine.

## What

Systematic web application QA testing using:
- **Hermes native browser tools** (`browser_navigate`, `browser_click`, `browser_snapshot`, `browser_console`, `browser_vision`) for human-in-the-loop interactions
- **Playwright Python** (`scripts/playwright_qa.py`) for programmatic crawls, responsive testing, video recording, and accessibility audits

## Why

gstack's `/qa` skill is one of the best AI-native QA workflows. It enforces:
- Screenshot evidence for every issue
- Health score rubric (0-100) with weighted categories
- Baseline JSON for regression tracking
- Three tiers: Quick / Standard / Exhaustive

This port brings the same discipline to Hermes Agent.

## Install

```bash
# Playwright (required for the Python runner)
pip install playwright
playwright install chromium

# Optional: accessibility audit
pip install axe-playwright-python

# Optional: Hermes browser tools already built-in
```

## Usage

### As a Hermes Skill

Trigger phrases:
- "QA this"
- "test the site"
- "find bugs"
- "does this work?"

The skill uses Hermes browser tools for interactive testing and invokes the Playwright script for scale.

### Direct Playwright Script

```bash
# Quick tier — homepage + top 5 pages
python scripts/playwright_qa.py --url https://example.com --tier quick

# Standard tier — full crawl
python scripts/playwright_qa.py --url https://example.com --tier standard

# Exhaustive tier — all pages + all viewports + video + a11y
python scripts/playwright_qa.py \
  --url https://example.com \
  --tier exhaustive \
  --viewport desktop,mobile,tablet \
  --video \
  --cookies ./cookies.json
```

## Output

```
qa-reports/
├── example-com-20260423/
│   ├── qa-report.md              # Human-readable markdown report
│   ├── screenshots/              # Full-page screenshots per page
│   │   ├── initial.png
│   │   ├── page-_dashboard.png
│   │   └── responsive-mobile.png
│   ├── videos/                   # If --video used
│   │   └── issue-001-repro.webm
│   ├── console-errors.json       # All JS + network errors
│   ├── accessibility-report.json # axe-core results (if installed)
│   ├── performance-metrics.json  # Web Vitals (LCP, FCP, TTFB)
│   └── baseline.json             # For regression diff
```

## Health Score

| Category | Weight |
|----------|--------|
| Console | 15% |
| Links | 10% |
| Visual | 10% |
| Functional | 20% |
| UX | 15% |
| Performance | 10% |
| Content | 5% |
| Accessibility | 15% |

## Differences from gstack/qa

| gstack/qa | hermes-qa-playwright |
|-----------|---------------------|
| Custom `$B` Chromium CDP | Hermes `browser_*` tools + Playwright |
| Tight Claude Code integration | Hermes agent-agnostic |
| Bun/TypeScript runtime | Python + asyncio |
| gstack binary dependency | `pip install playwright` |
| 1695-line SKILL.md | ~400-line focused SKILL.md |

## License

MIT — same as gstack.
