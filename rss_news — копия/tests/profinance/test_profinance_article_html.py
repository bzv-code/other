
from __future__ import annotations

from pathlib import Path

from playwright.async_api import async_playwright


# =============================================================================
# CONFIGURATION
# =============================================================================

URL = (
    "https://www.profinance.ru/news/2026/08/10/"
    "cjy4-dajmon-utverzhdaet-chto-dollar-mozhet-poteryat-"
    "status-rezervnoj-valyuty-esli-ssh.html"
)

PROJECT_ROOT = (
    Path(__file__).resolve()
    .parent.parent
)

HTML_DIR = (
    PROJECT_ROOT
    / "data"
    / "html_profinance"
)

HTML_FILE = (
    HTML_DIR
    / "profinance_article.html"
)

PROFILE_DIR = (
    PROJECT_ROOT
    / "data"
    / "browser_profiles"
    / "profinance"
)

PAGE_TIMEOUT = 30_000


# =============================================================================
# MAIN
# =============================================================================

async def main() -> None:

    print("=" * 70)
    print("PROFINANCE ARTICLE HTML TEST")
    print("=" * 70)

    print()
    print("URL:")
    print(URL)

    # -------------------------------------------------------------------------
    # CREATE DIRECTORIES
    # -------------------------------------------------------------------------

    HTML_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    PROFILE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print()
    print("HTML directory:")
    print(HTML_DIR)

    print()
    print("Browser profile:")
    print(PROFILE_DIR)

    # -------------------------------------------------------------------------
    # PLAYWRIGHT
    # -------------------------------------------------------------------------

    async with async_playwright() as playwright:

        print()
        print("Starting Chromium...")

        context = (
            await playwright.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),

                headless=False,

                viewport={
                    "width": 1920,
                    "height": 1080,
                },

                locale="ru-RU",

                timezone_id="Europe/Moscow",

                java_script_enabled=True,

                accept_downloads=False,

                args=[
                    "--disable-blink-features=AutomationControlled",
                ],
            )
        )

        try:

            page = await context.new_page()

            print()
            print("Opening page...")

            response = await page.goto(
                URL,
                wait_until="domcontentloaded",
                timeout=PAGE_TIMEOUT,
            )

            # -----------------------------------------------------------------
            # RESPONSE
            # -----------------------------------------------------------------

            if response is not None:

                print()
                print(
                    f"HTTP status: {response.status}"
                )

                print(
                    f"Response URL: {response.url}"
                )

            print()
            print(
                f"Final URL: {page.url}"
            )

            # -----------------------------------------------------------------
            # WAIT FOR PAGE
            # -----------------------------------------------------------------

            print()
            print("Waiting for page rendering...")

            await page.wait_for_timeout(
                3000
            )

            # -----------------------------------------------------------------
            # GET HTML
            # -----------------------------------------------------------------

            print()
            print("Getting page HTML...")

            html = await page.content()

            # -----------------------------------------------------------------
            # SAVE HTML
            # -----------------------------------------------------------------

            HTML_FILE.write_text(
                html,
                encoding="utf-8",
            )

            print()
            print(
                f"HTML saved: {HTML_FILE}"
            )

            print(
                f"HTML size: {len(html)} characters"
            )

            # -----------------------------------------------------------------
            # BASIC SEARCH
            # -----------------------------------------------------------------

            print()
            print("-" * 70)
            print("HTML CHECK")
            print("-" * 70)

            checks = {
                "<html": "<html" in html.lower(),
                "<body": "<body" in html.lower(),
                "profinance": "profinance" in html.lower(),
                "даймон": "даймон" in html.lower(),
                "доллар": "доллар" in html.lower(),
            }

            for name, result in checks.items():

                print(
                    f"{name}: "
                    f"{'FOUND' if result else 'NOT FOUND'}"
                )

            # -----------------------------------------------------------------
            # SAVE SCREENSHOT
            # -----------------------------------------------------------------

            screenshot_file = (
                HTML_DIR
                / "profinance_article.png"
            )

            await page.screenshot(
                path=str(screenshot_file),
                full_page=True,
            )

            print()
            print(
                f"Screenshot saved: {screenshot_file}"
            )

            # -----------------------------------------------------------------
            # PRINT TITLE
            # -----------------------------------------------------------------

            title = await page.title()

            print()
            print(
                f"Page title: {title}"
            )

            # -----------------------------------------------------------------
            # FINISH
            # -----------------------------------------------------------------

            print()
            print("=" * 70)
            print("TEST FINISHED")
            print("=" * 70)

        finally:

            await context.close()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import asyncio

    asyncio.run(
        main()
    )

