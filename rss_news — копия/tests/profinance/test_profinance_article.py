
from __future__ import annotations

import asyncio
from pathlib import Path

from app.models.article_model import Article
from app.services.profinance_article_service import (
    ProFinanceArticleService,
)


# =============================================================================
# TEST ARTICLE
# =============================================================================

TEST_URL = (
    "https://www.profinance.ru/news/2026/08/10/"
    "cjy4-dajmon-utverzhdaet-chto-dollar-mozhet-poteryat-"
    "status-rezervnoj-valyuty-esli-ssh.html"
)


# =============================================================================
# PATHS
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "profinance"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "profinance_article_test.txt"
)


# =============================================================================
# TEST
# =============================================================================

async def main() -> None:

    print("=" * 70)
    print("PROFINANCE ARTICLE TEST")
    print("=" * 70)

    print()
    print(f"URL:")
    print(TEST_URL)

    # -------------------------------------------------------------------------
    # CREATE ARTICLE
    # -------------------------------------------------------------------------

    article = Article(
        source="profinance",
        source_url="https://www.profinance.ru/forex.xml",
        title="Test ProFinance article",
        url=TEST_URL,
        description="",
        description_full=None,
        author="",
        published_at=None,
    )

    articles = [article]

    # -------------------------------------------------------------------------
    # SERVICE
    # -------------------------------------------------------------------------

    service = ProFinanceArticleService()

    print()
    print("Starting ProFinanceArticleService...")
    print()

    # -------------------------------------------------------------------------
    # ENRICH
    # -------------------------------------------------------------------------

    result = await service.enrich_articles(
        articles
    )

    # -------------------------------------------------------------------------
    # RESULT
    # -------------------------------------------------------------------------

    result_article = result[0]

    print()
    print("=" * 70)
    print("RESULT")
    print("=" * 70)

    if not result_article.description_full:

        print()
        print("ERROR: description_full was not received")
        print()

        return

    description_full = (
        result_article.description_full
    )

    print()
    print(
        f"description_full received: "
        f"{len(description_full)} chars"
    )

    print()
    print("-" * 70)
    print("FIRST 1000 CHARACTERS")
    print("-" * 70)

    print(
        description_full[:1000]
    )

    print()
    print("-" * 70)

    # -------------------------------------------------------------------------
    # SAVE RESULT
    # -------------------------------------------------------------------------

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        description_full,
        encoding="utf-8",
    )

    print()
    print(
        f"FULL ARTICLE SAVED TO:"
    )
    print(
        OUTPUT_FILE
    )

    print()
    print("=" * 70)
    print("TEST FINISHED SUCCESSFULLY")
    print("=" * 70)


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )
