---
name: hermes-qa-playwright
description: |
  Systematically QA test a web application using Hermes browser tools + Playwright.
  Runs browser-based testing, produces structured reports with screenshots,
  health scores, and baseline tracking. Inspired by gstack/qa but rewritten
  for Hermes Agent with Playwright as the automation engine.
triggers:
  - qa test this
  - find bugs on site
  - test the site
  - run qa
  - playwright qa
---

# Hermes QA with Playwright

> Ported from gstack/qa skill. Uses Hermes native browser tools as primary
> interaction layer, with Playwright Python scripts for advanced automation
> (multi-viewport responsive testing, video recording, programmatic crawls).

## When to Use

- User says: "QA this", "test the site", "find bugs", "does this work?"
- Before shipping a feature — run /qa for a sanity check
- After a refactor — run regression mode to catch new issues
- When reviewing a PR with UI changes

## Three Tiers

| Tier | Scope | Time |
|------|-------|------|
| **Quick** | Critical + High severity only. Homepage + top 5 pages. | ~5 min |
| **Standard** | + Medium severity. Full navigation map. | ~15 min |
| **Exhaustive** | + Low/cosmetic. All viewports, all states. | ~30 min |

Default tier: **Standard**.

---

## Tools

### Primary: Hermes Browser Tools
Use these for all human-in-the-loop interactions:

- `browser_navigate` — load a URL
- `browser_click` — click elements by ref ID
- `browser_type` — fill forms
- `browser_snapshot` — get page structure + ref IDs
- `browser_console` — read JS errors and logs
- `browser_scroll` — scroll for lazy-loaded content
- `browser_vision` — visual analysis of screenshots

### Advanced: Playwright Python Runner
Use `scripts/playwright_qa.py` for:

- Programmatic multi-page crawls
- Responsive testing across multiple viewports
- Video recording of bug reproductions
- Console error aggregation across pages
- Accessibility audit (axe-core)
- Performance metrics (LCP, FCP, CLS)

```bash
python scripts/playwright_qa.py \
  --url https://example.com \
  --tier standard \
  --output ./qa-reports/example-com-2026-04-23 \
  --viewport desktop,mobile,tablet \
  --video
```

---

## Phase-Based Workflow

### Phase 1: Initialize

1. Determine tier from user request (default: standard)
2. Create output directory: `./qa-reports/{domain}-{date}/`
3. Copy report template to output dir
4. Start timer

### Phase 2: Authenticate (if needed)

- If login required: use `browser_navigate` → `browser_type` → `browser_click`
- If cookie file provided: load via Playwright script (`--cookies path`)
- If 2FA/CAPTCHA: ask user, wait for confirmation

### Phase 3: Orient

1. `browser_navigate` to target URL
2. `browser_snapshot` to get page map
3. `browser_console` to check for JS errors on load
4. Detect framework:
   - `__next` in HTML → Next.js
   - `csrf-token` meta → Rails
   - `wp-content` in URLs → WordPress
   - Client-side routing, no reloads → SPA

### Phase 4: Explore

Systematically visit pages. For each page:

```
1. browser_navigate → browser_snapshot (full=true)
2. browser_console (check errors)
3. browser_vision (visual scan for layout issues)
4. Click interactive elements, fill forms
5. browser_console again (post-interaction errors)
6. browser_scroll down to trigger lazy load
7. browser_vision again
```

**Per-page checklist** (from issue taxonomy):
1. Visual scan — layout, images, alignment
2. Interactive elements — buttons, links, controls
3. Forms — empty, invalid, edge cases
4. Navigation — paths in/out, back button, deep links
5. States — empty, loading, error, overflow
6. Console — JS errors after interactions
7. Responsiveness — use Playwright script for mobile/tablet
8. Auth boundaries — logged-out behavior, role differences

**Depth judgment:**
- More time on: homepage, dashboard, checkout, search
- Less time on: about, terms, privacy

**Quick mode:** Only homepage + top 5 nav targets. Skip per-page checklist.

### Phase 5: Document

Document each issue **immediately** when found. Two evidence tiers:

**Interactive bugs** (broken flows, dead buttons, form failures):
1. `browser_vision` before the action
2. Perform the action (`browser_click`, `browser_type`)
3. `browser_vision` showing the result
4. `browser_console` for JS errors
5. Write repro steps referencing screenshots

**Static bugs** (typos, layout issues, missing images):
1. `browser_vision` showing the problem
2. Describe what's wrong

**Write each issue to the report immediately.** Use the template format.

### Phase 6: Wrap Up

1. Compute health score (see rubric below)
2. Write "Top 3 Things to Fix"
3. Write console health summary
4. Update severity counts
5. Fill report metadata
6. Save baseline JSON for regression tracking

### Phase 7: Triage (for /qa with fixes)

Sort issues by severity. Fix based on tier:
- Quick: fix critical + high only
- Standard: fix critical + high + medium
- Exhaustive: fix all including low/cosmetic

After each fix: re-verify with `browser_navigate` + `browser_vision`.

---

## Health Score Rubric

Compute each category (0-100), then weighted average.

### Console (weight: 15%)
- 0 errors → 100
- 1-3 errors → 70
- 4-10 errors → 40
- 10+ errors → 10

### Links (weight: 10%)
- 0 broken → 100
- Each broken link → -15 (min 0)

### Per-Category Deductions
Each category starts at 100. Deduct per finding:
- Critical → -25
- High → -15
- Medium → -8
- Low → -3

### Weights
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

### Final Score
`score = Σ (category_score × weight)`

---

## Important Rules

1. **Repro is everything.** Every issue needs at least one screenshot via `browser_vision`. No exceptions.
2. **Verify before documenting.** Retry the issue once to confirm it's reproducible.
3. **Never include credentials.** Write `[REDACTED]` for passwords in repro steps.
4. **Write incrementally.** Append each issue to the report as you find it. Don't batch.
5. **Never read source code.** Test as a user, not a developer.
6. **Check console after every interaction.** JS errors that don't surface visually are still bugs.
7. **Test like a user.** Use realistic data. Walk through complete workflows end-to-end.
8. **Depth over breadth.** 5-10 well-documented issues with evidence > 20 vague descriptions.
9. **Never delete output files.** Screenshots and reports accumulate — that's intentional.
10. **Show screenshots to the user.** After every `browser_vision`, describe what you see.
11. **Never refuse to use the browser.** When user invokes QA, they are requesting browser-based testing. Never suggest unit tests as a substitute.
12. **Use Playwright for scale.** When you need to test 10+ pages or 3+ viewports, use the Playwright script instead of manual browser tools.

---

## Output Structure

```
qa-reports/
├── {domain}-{date}/
│   ├── qa-report.md              # Structured report
│   ├── screenshots/
│   │   ├── initial.png
│   │   ├── issue-001-step-1.png
│   │   ├── issue-001-result.png
│   │   ├── issue-001-before.png  # if fixed
│   │   ├── issue-001-after.png   # if fixed
│   │   └── ...
│   ├── videos/                   # if --video flag used
│   │   └── issue-001-repro.webm
│   ├── console-errors.json       # aggregated console errors
│   ├── accessibility-report.json # axe-core results
│   └── baseline.json             # for regression tracking
└── index.md                      # index of all QA runs
```

---

## Framework-Specific Guidance

### Next.js
- Check console for hydration errors (`Hydration failed`)
- Monitor `_next/data` requests — 404s indicate broken data fetching
- Test client-side navigation (click links, don't just navigate)
- Check for CLS on pages with dynamic content

### Rails
- Check for N+1 query warnings in console
- Verify CSRF token presence in forms
- Test Turbo/Stimulus integration
- Check flash messages appear and dismiss correctly

### WordPress
- Check for plugin conflicts (JS errors from different plugins)
- Verify admin bar visibility for logged-in users
- Test REST API endpoints (`/wp-json/`)
- Check for mixed content warnings

### General SPA (React, Vue, Angular)
- Use `browser_snapshot` for navigation — links may be client-side
- Check for stale state (navigate away and back)
- Test browser back/forward — history handling
- Check for memory leaks (monitor console after extended use)
