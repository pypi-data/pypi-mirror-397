"""
Browser session management using Camoufox for Cloudflare bypass.

Camoufox is an anti-detect browser based on Firefox with C++ level
fingerprint injection, making it effective at bypassing Cloudflare
and other bot detection systems.
"""

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from playwright.async_api import BrowserContext, Page


@dataclass
class BrowserConfig:
    """Configuration for Camoufox browser instance."""

    headless: bool = True
    user_data_dir: Optional[Path] = None  # For persistent sessions
    humanize: bool = True  # Human-like mouse movements
    window_width: int = 1920
    window_height: int = 1080
    timeout: int = 60000  # 60 seconds for Cloudflare challenges
    block_images: bool = False  # Block images for faster loading
    locale: str = "en-US"


class BrowserManager:
    """
    Manages Camoufox browser sessions with Cloudflare bypass capability.

    Key features:
    - Persistent context for cookie storage (survives Cloudflare verification)
    - Humanized interactions to avoid detection
    - Automatic challenge detection and waiting
    """

    def __init__(self, config: Optional[BrowserConfig] = None):
        self.config = config or BrowserConfig()
        self._camoufox: Any = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._is_initialized = False

    async def initialize(self) -> None:
        """
        Initialize Camoufox browser with anti-detection settings.

        Uses persistent context if user_data_dir is specified,
        which preserves Cloudflare verification cookies.
        """
        from camoufox.async_api import AsyncCamoufox

        # Ensure user data directory exists
        if self.config.user_data_dir:
            self.config.user_data_dir.mkdir(parents=True, exist_ok=True)

        # Camoufox configuration - use correct parameter names
        camoufox_kwargs: dict[str, Any] = {
            "headless": self.config.headless,
            "humanize": self.config.humanize,
        }

        # Add persistent context if configured
        if self.config.user_data_dir:
            camoufox_kwargs["persistent_context"] = str(self.config.user_data_dir)

        # Launch Camoufox
        self._camoufox = AsyncCamoufox(**camoufox_kwargs)
        browser_or_context = await self._camoufox.__aenter__()

        # Handle both persistent context and regular browser modes
        if self.config.user_data_dir:
            # In persistent mode, we get a BrowserContext directly
            self._context = browser_or_context
            pages = self._context.pages
            self._page = pages[0] if pages else await self._context.new_page()
        else:
            # In non-persistent mode, we get a Browser
            self._context = browser_or_context
            self._page = await self._context.new_page()

        self._is_initialized = True

    async def navigate(self, url: str, wait_for_cloudflare: bool = True) -> bool:
        """
        Navigate to URL with Cloudflare bypass handling.

        Args:
            url: Target URL
            wait_for_cloudflare: Whether to wait for Cloudflare challenges

        Returns:
            True if navigation successful

        Raises:
            TimeoutError: If Cloudflare challenge doesn't complete in time
            RuntimeError: If browser not initialized
        """
        if not self._is_initialized:
            await self.initialize()

        if not self._page:
            raise RuntimeError("Page not available")

        # Navigate to URL
        await self._page.goto(url, wait_until="domcontentloaded")

        # Wait for Cloudflare challenge if needed
        if wait_for_cloudflare:
            await self._wait_for_cloudflare_challenge()

        return True

    async def _wait_for_cloudflare_challenge(self) -> None:
        """
        Detect and wait for Cloudflare challenges to complete.

        Cloudflare indicators:
        - Page title contains "Just a moment..."
        - Presence of cf-challenge elements
        - Turnstile iframe

        Camoufox's fingerprint spoofing often allows these challenges
        to pass automatically without user interaction.
        """
        if not self._page:
            return

        max_wait_ms = self.config.timeout
        start_time = asyncio.get_event_loop().time()
        check_interval = 0.5  # Check every 500ms

        while True:
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000

            if elapsed_ms >= max_wait_ms:
                raise TimeoutError(
                    f"Cloudflare challenge did not complete within {max_wait_ms}ms. "
                    "The site may be blocking automated access."
                )

            # Check page title for Cloudflare challenge indicators
            title = await self._page.title()

            # Check for various Cloudflare challenge indicators
            is_cloudflare_challenge = False

            if "Just a moment" in title or "Checking your browser" in title:
                is_cloudflare_challenge = True
            else:
                # Check for challenge elements
                challenge_selectors = [
                    "#cf-challenge-running",
                    "#challenge-running",
                    "iframe[src*='challenges.cloudflare.com']",
                    ".cf-browser-verification",
                ]

                for selector in challenge_selectors:
                    try:
                        count = await self._page.locator(selector).count()
                        if count > 0:
                            is_cloudflare_challenge = True
                            break
                    except Exception:
                        pass

            if not is_cloudflare_challenge:
                # Challenge completed or no challenge present
                try:
                    await self._page.wait_for_load_state("networkidle", timeout=5000)
                except Exception:
                    pass  # Timeout is okay, page might have long-polling
                return

            # Wait before checking again
            await asyncio.sleep(check_interval)

    @property
    def page(self) -> Page:
        """Get current page instance."""
        if not self._page:
            raise RuntimeError("Browser not initialized. Call initialize() first.")
        return self._page

    @property
    def is_initialized(self) -> bool:
        """Check if browser is initialized."""
        return self._is_initialized

    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if self._camoufox:
            try:
                await self._camoufox.__aexit__(None, None, None)
            except Exception:
                pass  # Ignore cleanup errors
            self._camoufox = None
            self._context = None
            self._page = None
            self._is_initialized = False

    async def __aenter__(self) -> "BrowserManager":
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
