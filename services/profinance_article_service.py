
from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import (
    BrowserContext,
    Page,
    TimeoutError as PlaywrightTimeoutError,
    async_playwright,
)

from app.models.article_model import Article
from app.utils.logger_utils import get_logger


logger = get_logger(__name__)


class ProFinanceArticleService:
    """
    Сервис получения полного текста статьи ProFinance.

    Использует Playwright и отдельный persistent browser profile.

    Finam profile и FinamArticleService здесь не используются.
    """

    # =========================================================================
    # CONFIGURATION
    # =========================================================================

    PAGE_TIMEOUT = 30_000

    REQUEST_DELAY = 1.0

    # Реальный контейнер статьи ProFinance.
    ARTICLE_SELECTOR = "#article_content"

    # Текст, начиная с которого статья должна обрезаться.
    CUT_OFF_MARKER = "Подготовлено ProFinance.Ru"

    # =========================================================================
    # PATHS
    # =========================================================================

    # __file__:
    #
    # app/services/profinance_article_service.py
    #
    # parent                  -> app/services
    # parent.parent           -> app
    # parent.parent.parent    -> project root

    PROJECT_ROOT = (
        Path(__file__).resolve()
        .parent.parent.parent
    )

    PROFILE_DIR = (
        PROJECT_ROOT
        / "data"
        / "browser_profiles"
        / "profinance"
    )

    # =========================================================================
    # PUBLIC API
    # =========================================================================

    async def enrich_articles(
        self,
        articles: list[Article],
    ) -> list[Article]:
        """
        Получить description_full для списка статей.

        Ошибка одной статьи не останавливает обработку остальных.
        """

        if not articles:

            logger.warning(
                "PROFINANCE ARTICLE: no articles to process"
            )

            return articles

        logger.info(
            "PROFINANCE ARTICLE: "
            "starting full description parsing: %s articles",
            len(articles),
        )

        self.PROFILE_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger.info(
            "PROFINANCE ARTICLE: browser profile: %s",
            self.PROFILE_DIR,
        )

        async with async_playwright() as playwright:

            context = await self._create_browser_context(
                playwright
            )

            try:

                page = await context.new_page()

                for index, article in enumerate(
                    articles,
                    start=1,
                ):

                    logger.info(
                        "PROFINANCE ARTICLE: "
                        "processing %s/%s: %s",
                        index,
                        len(articles),
                        article.url,
                    )

                    try:

                        description_full = (
                            await self._fetch_description_full(
                                page=page,
                                url=article.url,
                            )
                        )

                        if description_full:

                            article.description_full = (
                                description_full
                            )

                            logger.info(
                                "PROFINANCE ARTICLE: "
                                "full description received: "
                                "%s/%s, %s chars",
                                index,
                                len(articles),
                                len(description_full),
                            )

                        else:

                            logger.warning(
                                "PROFINANCE ARTICLE: "
                                "full description not found: "
                                "%s/%s",
                                index,
                                len(articles),
                            )

                    except Exception:

                        logger.exception(
                            "PROFINANCE ARTICLE: "
                            "failed to process article %s/%s: %s",
                            index,
                            len(articles),
                            article.url,
                        )

                    if index < len(articles):

                        await asyncio.sleep(
                            self.REQUEST_DELAY
                        )

            finally:

                await context.close()

        logger.info(
            "PROFINANCE ARTICLE: "
            "full description parsing finished"
        )

        return articles

    # =========================================================================
    # BROWSER
    # =========================================================================

    async def _create_browser_context(
        self,
        playwright,
    ) -> BrowserContext:
        """
        Создать persistent browser context.

        Используется отдельный профиль ProFinance.
        """

        logger.info(
            "PROFINANCE ARTICLE: launching Chromium"
        )

        logger.info(
            "PROFINANCE ARTICLE: profile exists: %s",
            self.PROFILE_DIR.exists(),
        )

        context = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.PROFILE_DIR),

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

        return context

    # =========================================================================
    # ARTICLE
    # =========================================================================

    async def _fetch_description_full(
        self,
        page: Page,
        url: str,
    ) -> str | None:
        """
        Открыть страницу статьи ProFinance
        и получить полный текст.
        """

        logger.debug(
            "PROFINANCE ARTICLE: opening: %s",
            url,
        )

        response = await page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=self.PAGE_TIMEOUT,
        )

        if response is not None:

            logger.info(
                "PROFINANCE ARTICLE: HTTP status: %s",
                response.status,
            )

        logger.info(
            "PROFINANCE ARTICLE: final URL: %s",
            page.url,
        )

        # ---------------------------------------------------------------------
        # CHECK HTTP STATUS
        # ---------------------------------------------------------------------

        if response is not None and response.status == 403:

            logger.warning(
                "PROFINANCE ARTICLE: HTTP 403 received: %s",
                url,
            )

            return None

        if response is not None and response.status >= 400:

            logger.warning(
                "PROFINANCE ARTICLE: HTTP %s received: %s",
                response.status,
                url,
            )

            return None

        # ---------------------------------------------------------------------
        # WAIT FOR ARTICLE
        # ---------------------------------------------------------------------

        try:

            await page.wait_for_selector(
                self.ARTICLE_SELECTOR,
                state="attached",
                timeout=self.PAGE_TIMEOUT,
            )

        except PlaywrightTimeoutError:

            logger.warning(
                "PROFINANCE ARTICLE: "
                "article container not found: %s",
                url,
            )

            return None

        # ---------------------------------------------------------------------
        # WAIT FOR PAGE
        # ---------------------------------------------------------------------

        await page.wait_for_timeout(
            1000
        )

        # ---------------------------------------------------------------------
        # EXTRACT ARTICLE TEXT
        # ---------------------------------------------------------------------

        try:

            description_full = await page.locator(
                self.ARTICLE_SELECTOR
            ).inner_text()

        except Exception:

            logger.exception(
                "PROFINANCE ARTICLE: "
                "failed to get article text: %s",
                url,
            )

            return None

        if not description_full:

            logger.warning(
                "PROFINANCE ARTICLE: "
                "article text is empty: %s",
                url,
            )

            return None

        # ---------------------------------------------------------------------
        # CLEAN TEXT
        # ---------------------------------------------------------------------

        description_full = self._clean_text(
            description_full
        )

        if not description_full:

            return None

        return description_full

    # =========================================================================
    # TEXT CLEANING
    # =========================================================================

    @classmethod
    def _clean_text(
        cls,
        text: str,
    ) -> str:
        """
        Очистить полный текст статьи.

        Правила:

        1. Удалить пробелы и табуляцию в начале/конце строк.
        2. Сжать последовательности пробелов внутри строки.
        3. Удалить пустые строки.
        4. Сохранить абзацы отдельными строками.
        5. Не оставлять пустые строки между абзацами.
        6. Полностью удалить текст начиная с
           "Подготовлено ProFinance.Ru".
        """

        paragraphs: list[str] = []

        for line in text.splitlines():

            line = " ".join(
                line.split()
            ).strip()

            if not line:

                continue

            paragraphs.append(
                line
            )

        # ---------------------------------------------------------------------
        # JOIN PARAGRAPHS
        # ---------------------------------------------------------------------

        cleaned_text = "\n".join(
            paragraphs
        )

        # ---------------------------------------------------------------------
        # CUT PROFINANCE SIGNATURE
        # ---------------------------------------------------------------------

        marker = cls.CUT_OFF_MARKER

        marker_position = cleaned_text.find(
            marker
        )

        if marker_position != -1:

            logger.info(
                "PROFINANCE ARTICLE: "
                "cutting text from marker: %s",
                marker,
            )

            cleaned_text = cleaned_text[
                :marker_position
            ].rstrip()

        return cleaned_text

