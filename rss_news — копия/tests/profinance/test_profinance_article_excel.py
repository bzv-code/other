
from __future__ import annotations

import asyncio
from pathlib import Path

from openpyxl import Workbook

from app.models.article_model import Article
from app.services.profinance_article_service import (
    ProFinanceArticleService,
)


# =============================================================================
# CONFIGURATION
# =============================================================================

URLS = [
    "https://www.profinance.ru/news/2026/08/10/cjy7-kursy-valyut-tsb-rf-kurs-rublya-k-dollaru-evro-yuanyu-bel-rublyu-somoni-somu-i-s.html",
    "https://www.profinance.ru/news/2026/08/10/cjy4-dajmon-utverzhdaet-chto-dollar-mozhet-poteryat-status-rezervnoj-valyuty-esli-ssh.html",
    "https://www.profinance.ru/news/2026/08/10/cjxz-dollar-stabilizirovalsya-posle-novostej-o-snizhenii-chisla-rabochikh-mest-i-v-oz.html",
    "https://www.profinance.ru/news/2026/08/07/cjxh-kursy-valyut-tsb-rf-kurs-rublya-k-dollaru-evro-yuanyu-bel-rublyu-somoni-somu-i-s.html",
    "https://www.profinance.ru/news/2026/08/07/cjxg-po-mneniyu-blackrock-prodazha-ssha-evro-za-ienu-uvelichivaet-geopoliticheskie-ri.html",

    # -------------------------------------------------------------------------
    # Добавь сюда ещё 5 URL для полного теста 10 статей.
    # -------------------------------------------------------------------------
]


# =============================================================================
# CONSTANTS
# =============================================================================

SOURCE = "ProFinance"

SOURCE_URL = "https://www.profinance.ru/"


# =============================================================================
# PATHS
# =============================================================================

# __file__:
#
# tests/profinance/test/test_profinance_article_excel.py
#
# parent                  -> test
# parent.parent          -> profinance
# parent.parent.parent   -> tests
# parent.parent.parent.parent -> project root

PROJECT_ROOT = (
    Path(__file__).resolve()
    .parent.parent.parent.parent
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "test"
    / "profinance"
)

OUTPUT_FILE = (
    OUTPUT_DIR
    / "profinance_articles_test.xlsx"
)


# =============================================================================
# CREATE ARTICLES
# =============================================================================

def create_articles() -> list[Article]:
    """
    Создать тестовые Article из списка URL.
    """

    articles: list[Article] = []

    for index, url in enumerate(
        URLS,
        start=1,
    ):

        article = Article(
            source=SOURCE,
            source_url=SOURCE_URL,
            title=f"ProFinance test article {index}",
            url=url,
        )

        articles.append(article)

    return articles


# =============================================================================
# SAVE EXCEL
# =============================================================================

def save_to_excel(
    articles: list[Article],
) -> None:
    """
    Сохранить результаты обработки в Excel.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    workbook = Workbook()

    worksheet = workbook.active

    worksheet.title = "ProFinance"

    # -------------------------------------------------------------------------
    # HEADERS
    # -------------------------------------------------------------------------

    headers = [
        "№",
        "source",
        "source_url",
        "title",
        "URL",
        "description",
        "description_full",
        "Длина description_full",
        "Статус",
    ]

    worksheet.append(
        headers
    )

    # -------------------------------------------------------------------------
    # DATA
    # -------------------------------------------------------------------------

    for index, article in enumerate(
        articles,
        start=1,
    ):

        description_full = (
            getattr(
                article,
                "description_full",
                None,
            )
            or ""
        )

        description = (
            getattr(
                article,
                "description",
                None,
            )
            or ""
        )

        status = (
            "OK"
            if description_full
            else "ERROR"
        )

        worksheet.append(
            [
                index,
                getattr(
                    article,
                    "source",
                    "",
                ),
                getattr(
                    article,
                    "source_url",
                    "",
                ),
                getattr(
                    article,
                    "title",
                    "",
                ),
                getattr(
                    article,
                    "url",
                    "",
                ),
                description,
                description_full,
                len(description_full),
                status,
            ]
        )

    # -------------------------------------------------------------------------
    # COLUMN WIDTH
    # -------------------------------------------------------------------------

    worksheet.column_dimensions["A"].width = 7
    worksheet.column_dimensions["B"].width = 15
    worksheet.column_dimensions["C"].width = 40
    worksheet.column_dimensions["D"].width = 35
    worksheet.column_dimensions["E"].width = 90
    worksheet.column_dimensions["F"].width = 80
    worksheet.column_dimensions["G"].width = 120
    worksheet.column_dimensions["H"].width = 22
    worksheet.column_dimensions["I"].width = 12

    # -------------------------------------------------------------------------
    # TEXT WRAPPING
    # -------------------------------------------------------------------------

    for row in worksheet.iter_rows():

        for cell in row:

            cell.alignment = cell.alignment.copy(
                vertical="top",
                wrap_text=True,
            )

    # -------------------------------------------------------------------------
    # FREEZE HEADER
    # -------------------------------------------------------------------------

    worksheet.freeze_panes = "A2"

    # -------------------------------------------------------------------------
    # AUTO FILTER
    # -------------------------------------------------------------------------

    worksheet.auto_filter.ref = (
        worksheet.dimensions
    )

    # -------------------------------------------------------------------------
    # SAVE
    # -------------------------------------------------------------------------

    workbook.save(
        OUTPUT_FILE
    )

    print()
    print("=" * 70)
    print("EXCEL SAVED")
    print("=" * 70)
    print()
    print(
        f"File: {OUTPUT_FILE}"
    )
    print()


# =============================================================================
# MAIN
# =============================================================================

async def main() -> None:

    print("=" * 70)
    print("PROFINANCE ARTICLE EXCEL TEST")
    print("=" * 70)
    print()

    print(
        f"Articles to process: {len(URLS)}"
    )

    print(
        f"Output file: {OUTPUT_FILE}"
    )

    print()

    # -------------------------------------------------------------------------
    # CHECK URL COUNT
    # -------------------------------------------------------------------------

    if len(URLS) != 10:

        print(
            "WARNING:"
        )

        print(
            f"Expected 10 URLs, but configured: {len(URLS)}"
        )

        print(
            "Add the remaining URLs to URLS."
        )

        print()

    # -------------------------------------------------------------------------
    # CREATE ARTICLES
    # -------------------------------------------------------------------------

    articles = create_articles()

    # -------------------------------------------------------------------------
    # START SERVICE
    # -------------------------------------------------------------------------

    print(
        "Starting ProFinanceArticleService..."
    )

    print()

    service = ProFinanceArticleService()

    # -------------------------------------------------------------------------
    # PARSE ARTICLES
    # -------------------------------------------------------------------------

    articles = await service.enrich_articles(
        articles
    )

    # -------------------------------------------------------------------------
    # STATISTICS
    # -------------------------------------------------------------------------

    success_count = 0
    error_count = 0

    print()
    print("=" * 70)
    print("PROCESSING RESULT")
    print("=" * 70)
    print()

    for index, article in enumerate(
        articles,
        start=1,
    ):

        description_full = (
            getattr(
                article,
                "description_full",
                None,
            )
            or ""
        )

        if description_full:

            success_count += 1

            print(
                f"{index:02d}. OK    "
                f"{len(description_full):6d} chars    "
                f"{article.url}"
            )

        else:

            error_count += 1

            print(
                f"{index:02d}. ERROR "
                f"               "
                f"{article.url}"
            )

    print()

    print(
        f"Total:   {len(articles)}"
    )

    print(
        f"Success: {success_count}"
    )

    print(
        f"Errors:  {error_count}"
    )

    # -------------------------------------------------------------------------
    # SAVE EXCEL
    # -------------------------------------------------------------------------

    save_to_excel(
        articles
    )


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":

    asyncio.run(
        main()
    )

