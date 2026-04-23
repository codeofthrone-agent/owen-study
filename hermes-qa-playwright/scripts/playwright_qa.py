#!/usr/bin/env python3
"""
Hermes QA Playwright Runner
Advanced browser automation for QA testing.

Usage:
    python playwright_qa.py --url https://example.com --tier standard
    python playwright_qa.py --url https://example.com --tier exhaustive --video --viewport desktop,mobile,tablet
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# Optional dependencies — gracefully degrade
HAVE_PLAYWRIGHT = False
HAVE_AXE = False
Browser = None
BrowserContext = None
Page = None

try:
    from playwright.async_api import async_playwright, Page as _Page, BrowserContext as _BrowserContext, Browser as _Browser
    HAVE_PLAYWRIGHT = True
    Browser = _Browser
    BrowserContext = _BrowserContext
    Page = _Page
except ImportError:
    pass

try:
    from axe_playwright_python.async_playwright import Axe
    HAVE_AXE = True
except ImportError:
    pass


class QARunner:
    def __init__(self, url: str, tier: str, output_dir: str, viewports: list, video: bool, cookies: Optional[str]):
        self.url = url
        self.tier = tier
        self.output_dir = Path(output_dir)
        self.viewports = viewports
        self.video = video
        self.cookies_file = cookies
        self.domain = urlparse(url).netloc.replace(":", "_")
        self.start_time = datetime.now()
        self.issues: list = []
        self.console_errors: list = []
        self.pages_visited: list = []
        self.screenshot_count = 0
        self.baseline = {
            "date": self.start_time.strftime("%Y-%m-%d"),
            "url": url,
            "tier": tier,
            "healthScore": 100,
            "issues": [],
            "categoryScores": {},
        }

        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "screenshots").mkdir(exist_ok=True)
        if video:
            (self.output_dir / "videos").mkdir(exist_ok=True)

    async def run(self):
        if not HAVE_PLAYWRIGHT:
            print("ERROR: playwright is not installed. Install with: pip install playwright && playwright install chromium")
            sys.exit(1)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await self._create_context(browser)
            page = await context.new_page()

            # Collect console errors
            page.on("console", self._on_console)
            page.on("pageerror", self._on_pageerror)
            page.on("response", self._on_response)

            # Phase 3: Orient
            await self._orient(page)

            # Phase 4: Explore
            if self.tier == "quick":
                await self._explore_quick(page)
            elif self.tier == "standard":
                await self._explore_standard(page)
            else:  # exhaustive
                await self._explore_exhaustive(page)

            # Phase 6: Wrap up
            await self._wrap_up(page)

            await context.close()
            await browser.close()

    async def _create_context(self, browser: Browser) -> BrowserContext:
        opts = {
            "viewport": {"width": 1280, "height": 720},
            "user_agent": "HermesQA/1.0 (Automated QA Testing)",
        }
        if self.video:
            opts["record_video_dir"] = str(self.output_dir / "videos")
            opts["record_video_size"] = {"width": 1280, "height": 720}

        context = await browser.new_context(**opts)

        if self.cookies_file and Path(self.cookies_file).exists():
            with open(self.cookies_file) as f:
                cookies = json.load(f)
            await context.add_cookies(cookies)

        return context

    async def _orient(self, page: Page):
        print(f"[Orient] Loading {self.url}")
        await page.goto(self.url, wait_until="networkidle")
        self.pages_visited.append(self.url)

        # Screenshot initial state
        await self._screenshot(page, "initial")

        # Detect framework
        html = await page.content()
        framework = self._detect_framework(html)
        self.baseline["framework"] = framework
        print(f"[Orient] Framework detected: {framework}")

        # Console errors on load
        await asyncio.sleep(0.5)  # let errors accumulate
        self._log_console_summary()

    async def _explore_quick(self, page: Page):
        print("[Explore] Quick mode: homepage + top 5 links")
        links = await page.eval_on_selector_all("a[href]", """
            links => links
                .map(l => ({href: l.href, text: l.innerText.trim()}))
                .filter(l => l.href.startsWith('http') && !l.href.includes('#'))
                .slice(0, 6)
        """)
        for link in links[1:6]:  # skip self
            try:
                await page.goto(link["href"], wait_until="networkidle", timeout=15000)
                self.pages_visited.append(link["href"])
                await self._screenshot(page, f"page-{len(self.pages_visited)}")
            except Exception as e:
                self.issues.append({
                    "id": f"ISSUE-{len(self.issues)+1:03d}",
                    "title": f"Broken link: {link['text'][:40]}",
                    "severity": "high",
                    "category": "functional",
                    "url": link["href"],
                    "description": f"Navigation failed: {e}",
                })

    async def _explore_standard(self, page: Page):
        print("[Explore] Standard mode: full navigation map")
        # Crawl all same-domain links
        visited = set([self.url])
        to_visit = [self.url]
        max_pages = 15 if self.tier == "standard" else 50

        while to_visit and len(visited) < max_pages:
            current = to_visit.pop(0)
            try:
                await page.goto(current, wait_until="networkidle", timeout=15000)
                self.pages_visited.append(current)

                # Screenshot
                safe_name = urlparse(current).path.replace("/", "_") or "root"
                await self._screenshot(page, f"page-{safe_name[:40]}")

                # Find new links
                links = await page.eval_on_selector_all("a[href]", """
                    links => [...new Set(links
                        .map(l => l.href)
                        .filter(h => h.startsWith(location.origin) && !h.includes('#')))]
                """)
                for href in links:
                    if href not in visited:
                        visited.add(href)
                        to_visit.append(href)

                # Check console after page load
                await asyncio.sleep(0.3)
                self._log_console_summary()

            except Exception as e:
                self.issues.append({
                    "id": f"ISSUE-{len(self.issues)+1:03d}",
                    "title": f"Page load error: {current[:60]}",
                    "severity": "medium",
                    "category": "performance",
                    "url": current,
                    "description": str(e),
                })

    async def _explore_exhaustive(self, page: Page):
        print("[Explore] Exhaustive mode: all pages + all viewports")
        await self._explore_standard(page)

        # Responsive testing across viewports
        viewports = {
            "mobile": {"width": 375, "height": 812},
            "tablet": {"width": 768, "height": 1024},
            "desktop": {"width": 1280, "height": 720},
        }

        for vp_name in self.viewports:
            if vp_name not in viewports:
                continue
            print(f"[Responsive] Testing {vp_name}")
            await page.set_viewport_size(viewports[vp_name])
            await page.goto(self.url, wait_until="networkidle")
            await self._screenshot(page, f"responsive-{vp_name}")

        # Accessibility audit
        if HAVE_AXE:
            await self._run_accessibility(page)

        # Performance metrics
        await self._run_performance(page)

    async def _run_accessibility(self, page: Page):
        print("[Accessibility] Running axe-core audit")
        axe = Axe()
        results = await axe.run(page)
        violations = results.get("violations", [])

        for v in violations:
            severity = "high" if v["impact"] in ["critical", "serious"] else "medium"
            self.issues.append({
                "id": f"ISSUE-{len(self.issues)+1:03d}",
                "title": f"A11y: {v['description'][:80]}",
                "severity": severity,
                "category": "accessibility",
                "url": page.url,
                "description": f"{v['help']} — {v['helpUrl']}",
            })

        # Save raw axe results
        with open(self.output_dir / "accessibility-report.json", "w") as f:
            json.dump(results, f, indent=2)

    async def _run_performance(self, page: Page):
        print("[Performance] Collecting Web Vitals")
        metrics = await page.evaluate("""() => {
            const nav = performance.getEntriesByType('navigation')[0];
            const paint = performance.getEntriesByType('paint');
            const lcp = performance.getEntriesByName('largest-contentful-paint');
            return {
                lcp: lcp.length ? lcp[lcp.length-1].startTime : null,
                fcp: paint.find(p => p.name === 'first-contentful-paint')?.startTime || null,
                ttfb: nav?.responseStart || null,
                loadTime: nav?.loadEventEnd || null,
                domContentLoaded: nav?.domContentLoadedEventEnd || null,
            };
        }""")

        # Flag slow pages
        if metrics.get("lcp") and metrics["lcp"] > 2500:
            self.issues.append({
                "id": f"ISSUE-{len(self.issues)+1:03d}",
                "title": f"Slow LCP: {metrics['lcp']:.0f}ms",
                "severity": "medium",
                "category": "performance",
                "url": page.url,
                "description": f"Largest Contentful Paint is {metrics['lcp']:.0f}ms (threshold: 2500ms)",
            })

        with open(self.output_dir / "performance-metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)

    async def _wrap_up(self, page: Page):
        print("[Wrap Up] Computing health score and writing report")
        duration = (datetime.now() - self.start_time).total_seconds()

        # Compute health score
        scores = self._compute_health_scores()
        self.baseline["healthScore"] = scores["total"]
        self.baseline["categoryScores"] = {k: v for k, v in scores.items() if k != "total"}
        self.baseline["issues"] = [{"id": i["id"], "title": i["title"], "severity": i["severity"], "category": i["category"]} for i in self.issues]

        # Save baseline
        with open(self.output_dir / "baseline.json", "w") as f:
            json.dump(self.baseline, f, indent=2)

        # Save console errors
        with open(self.output_dir / "console-errors.json", "w") as f:
            json.dump(self.console_errors, f, indent=2)

        # Generate markdown report
        report = self._generate_report(duration, scores)
        with open(self.output_dir / "qa-report.md", "w") as f:
            f.write(report)

        print(f"\n✅ QA complete: {self.output_dir}/qa-report.md")
        print(f"   Health score: {scores['total']}/100")
        print(f"   Issues found: {len(self.issues)}")
        print(f"   Pages visited: {len(self.pages_visited)}")
        print(f"   Screenshots: {self.screenshot_count}")

    def _detect_framework(self, html: str) -> str:
        h = html.lower()
        if "__next" in h or "_next/data" in h:
            return "Next.js"
        if "csrf-token" in h or "data-turbo" in h:
            return "Rails"
        if "wp-content" in h:
            return "WordPress"
        if h.count("data-reactroot") or h.count("data-reactid"):
            return "React"
        if h.count("ng-app"):
            return "Angular"
        if h.count("vue"):
            return "Vue"
        return "Unknown"

    def _on_console(self, msg):
        if msg.type in ("error", "warning"):
            self.console_errors.append({
                "type": msg.type,
                "text": msg.text,
                "url": msg.page.url if hasattr(msg, "page") else "unknown",
            })

    def _on_pageerror(self, error):
        self.console_errors.append({
            "type": "pageerror",
            "text": str(error),
            "url": "unknown",
        })

    def _on_response(self, response):
        if response.status >= 400:
            self.console_errors.append({
                "type": "network",
                "text": f"{response.status} {response.url}",
                "url": response.url,
            })

    def _log_console_summary(self):
        errors = [e for e in self.console_errors if e["type"] == "error"]
        if errors:
            print(f"   ⚠️  {len(errors)} console errors on this page")

    async def _screenshot(self, page: Page, name: str):
        path = self.output_dir / "screenshots" / f"{name}.png"
        await page.screenshot(path=str(path), full_page=True)
        self.screenshot_count += 1
        print(f"   📸 {path.name}")

    def _compute_health_scores(self) -> dict:
        categories = {"console": 100, "links": 100, "visual": 100, "functional": 100,
                      "ux": 100, "performance": 100, "content": 100, "accessibility": 100}

        for issue in self.issues:
            cat = issue.get("category", "functional")
            sev = issue.get("severity", "medium")
            if cat in categories:
                deduction = {"critical": 25, "high": 15, "medium": 8, "low": 3}.get(sev, 8)
                categories[cat] = max(0, categories[cat] - deduction)

        # Console special scoring
        error_count = len([e for e in self.console_errors if e["type"] == "error"])
        if error_count == 0:
            categories["console"] = 100
        elif error_count <= 3:
            categories["console"] = 70
        elif error_count <= 10:
            categories["console"] = 40
        else:
            categories["console"] = 10

        weights = {"console": 0.15, "links": 0.10, "visual": 0.10, "functional": 0.20,
                   "ux": 0.15, "performance": 0.10, "content": 0.05, "accessibility": 0.15}

        total = int(sum(categories.get(k, 100) * w for k, w in weights.items()))
        categories["total"] = total
        return categories

    def _generate_report(self, duration: float, scores: dict) -> str:
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for i in self.issues:
            severity_counts[i.get("severity", "medium")] += 1

        top3 = sorted(self.issues, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["severity"], 2))[:3]

        lines = [
            f"# QA Report: {self.domain}",
            "",
            "| Field | Value |",
            "|-------|-------|",
            f"| **Date** | {self.start_time.strftime('%Y-%m-%d %H:%M')} |",
            f"| **URL** | {self.url} |",
            f"| **Tier** | {self.tier.title()} |",
            f"| **Duration** | {duration:.0f}s |",
            f"| **Pages visited** | {len(self.pages_visited)} |",
            f"| **Screenshots** | {self.screenshot_count} |",
            f"| **Framework** | {self.baseline.get('framework', 'Unknown')} |",
            "",
            f"## Health Score: {scores['total']}/100",
            "",
            "| Category | Score |",
            "|----------|-------|",
        ]
        for cat in ["console", "links", "visual", "functional", "ux", "performance", "content", "accessibility"]:
            lines.append(f"| {cat.title()} | {scores.get(cat, 100)} |")

        lines.extend([
            "",
            "## Top 3 Things to Fix",
            "",
        ])
        for i, issue in enumerate(top3, 1):
            lines.append(f"{i}. **{issue['id']}: {issue['title']}** — {issue.get('description', '')[:100]}")

        lines.extend([
            "",
            "## Console Health",
            "",
            "| Error | Count |",
            "|-------|-------|",
        ])
        error_types = {}
        for e in self.console_errors:
            key = e["text"][:80]
            error_types[key] = error_types.get(key, 0) + 1
        for text, count in sorted(error_types.items(), key=lambda x: -x[1])[:10]:
            lines.append(f"| {text} | {count} |")

        lines.extend([
            "",
            "## Summary",
            "",
            "| Severity | Count |",
            "|----------|-------|",
            f"| Critical | {severity_counts['critical']} |",
            f"| High | {severity_counts['high']} |",
            f"| Medium | {severity_counts['medium']} |",
            f"| Low | {severity_counts['low']} |",
            f"| **Total** | **{len(self.issues)}** |",
            "",
            "## Issues",
            "",
        ])

        for issue in self.issues:
            lines.extend([
                f"### {issue['id']}: {issue['title']}",
                "",
                "| Field | Value |",
                "|-------|-------|",
                f"| **Severity** | {issue['severity']} |",
                f"| **Category** | {issue['category']} |",
                f"| **URL** | {issue.get('url', 'N/A')} |",
                "",
                f"**Description:** {issue.get('description', 'N/A')}",
                "",
            ])

        lines.extend([
            "",
            "## Ship Readiness",
            "",
            f"**Health score:** {scores['total']}/100",
            f"**Issues found:** {len(self.issues)}",
        ])

        return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Hermes QA Playwright Runner")
    parser.add_argument("--url", required=True, help="Target URL to test")
    parser.add_argument("--tier", choices=["quick", "standard", "exhaustive"], default="standard")
    parser.add_argument("--output", default=None, help="Output directory")
    parser.add_argument("--viewport", default="desktop", help="Comma-separated viewports: desktop,mobile,tablet")
    parser.add_argument("--video", action="store_true", help="Record videos")
    parser.add_argument("--cookies", default=None, help="Path to cookies JSON file")
    args = parser.parse_args()

    output = args.output or f"./qa-reports/{urlparse(args.url).netloc}-{datetime.now().strftime('%Y%m%d')}"
    viewports = [v.strip() for v in args.viewport.split(",")]

    runner = QARunner(
        url=args.url,
        tier=args.tier,
        output_dir=output,
        viewports=viewports,
        video=args.video,
        cookies=args.cookies,
    )
    asyncio.run(runner.run())


if __name__ == "__main__":
    main()
