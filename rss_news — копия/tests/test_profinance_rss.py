from __future__ import annotations

from pathlib import Path

import httpx


# =============================================================================
# CONFIGURATION
# =============================================================================

URL = "https://www.profinance.ru/forex.xml"

PROJECT_ROOT = (
    Path(__file__).resolve()
    .parent.parent
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "profinance"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "forex.xml"
)

TIMEOUT = 30.0


# =============================================================================
# MAIN
# =============================================================================

def main() -> None:

    print("=" * 70)
    print("PROFINANCE RSS TEST")
    print("=" * 70)

    print(f"URL: {URL}")
    print(f"OUTPUT: {OUTPUT_FILE}")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/148.0.0.0 Safari/537.36"
        ),
        "Accept": (
            "application/rss+xml, "
            "application/xml, "
            "text/xml, "
            "*/*"
        ),
    }

    try:

        print()
        print("Downloading RSS...")

        with httpx.Client(
            timeout=TIMEOUT,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = client.get(URL)

        print(
            f"HTTP status: {response.status_code}"
        )

        print(
            f"Final URL: {response.url}"
        )

        print(
            f"Content-Type: "
            f"{response.headers.get('content-type')}"
        )

        print(
            f"Size: {len(response.content)} bytes"
        )

        response.raise_for_status()

        # -------------------------------------------------------------
        # SAVE RAW CONTENT
        # -------------------------------------------------------------

        OUTPUT_FILE.write_bytes(
            response.content
        )

        print()
        print("SUCCESS")
        print(
            f"Saved: {OUTPUT_FILE}"
        )

    except httpx.HTTPError as exc:

        print()
        print("HTTP ERROR")
        print(exc)

        raise

    except Exception as exc:

        print()
        print("ERROR")
        print(exc)

        raise

    print()
    print("=" * 70)
    print("TEST FINISHED")
    print("=" * 70)


if __name__ == "__main__":
    main()