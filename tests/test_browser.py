"""Browser tests for TabStash using Playwright."""

import re

import pytest
from playwright.sync_api import Page, expect


def has_class(page: Page, selector: str, class_name: str) -> bool:
    """Check if an element has a specific class."""
    classes = page.locator(selector).get_attribute("class") or ""
    return class_name in classes.split()


class TestAutoScroll:
    """Tests for auto-scroll functionality."""

    @pytest.fixture
    def tab_page(self, page: Page, live_server: str) -> Page:
        """Navigate to a tab page."""
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")
        return page

    def test_auto_scroll_button_exists(self, tab_page: Page):
        """Test that auto-scroll button is present."""
        button = tab_page.locator("#auto-scroll-toggle")
        expect(button).to_be_visible()
        expect(button).to_contain_text("Auto-scroll")

    def test_auto_scroll_activates_on_click(self, tab_page: Page):
        """Test that clicking auto-scroll button activates scrolling."""
        button = tab_page.locator("#auto-scroll-toggle")
        speed_control = tab_page.locator("#speed-control")

        # Initially speed control is hidden
        expect(speed_control).not_to_be_visible()

        # Click the button
        button.click()

        # Button should be active and speed control visible
        expect(button).to_have_class(re.compile(r"active"))
        expect(speed_control).to_be_visible()

    def test_auto_scroll_shows_indicator(self, tab_page: Page):
        """Test that scrolling indicator appears."""
        button = tab_page.locator("#auto-scroll-toggle")
        indicator = tab_page.locator(".scroll-indicator")

        button.click()

        expect(indicator).to_have_class(re.compile(r"visible"))

    def test_auto_scroll_actually_scrolls(self, tab_page: Page):
        """Test that the page actually scrolls when auto-scroll is active."""
        button = tab_page.locator("#auto-scroll-toggle")

        # Get initial scroll position
        initial_scroll = tab_page.evaluate("window.pageYOffset")

        # Start auto-scroll
        button.click()

        # Wait for scrolling to happen (1 second at 40px/sec = 40px)
        tab_page.wait_for_timeout(1000)

        # Get new scroll position
        new_scroll = tab_page.evaluate("window.pageYOffset")

        # Should have scrolled down
        assert new_scroll > initial_scroll, (
            f"Page should have scrolled. Initial: {initial_scroll}, New: {new_scroll}"
        )

    def test_auto_scroll_stops_on_second_click(self, tab_page: Page):
        """Test that auto-scroll stops when button clicked again."""
        button = tab_page.locator("#auto-scroll-toggle")

        # Start scrolling
        button.click()
        expect(button).to_have_class(re.compile(r"active"))

        # Stop scrolling
        button.click()
        # After stopping, button should not have active class
        tab_page.wait_for_timeout(100)  # Small wait for state to update
        assert not has_class(tab_page, "#auto-scroll-toggle", "active")
        assert not has_class(tab_page, ".scroll-indicator", "visible")

    def test_auto_scroll_speed_control(self, tab_page: Page):
        """Test that speed control buttons work."""
        button = tab_page.locator("#auto-scroll-toggle")
        slow_btn = tab_page.locator(".speed-btn[data-speed='slow']")
        fast_btn = tab_page.locator(".speed-btn[data-speed='fast']")

        # Start scrolling
        button.click()

        # Click slow
        slow_btn.click()
        expect(slow_btn).to_have_class(re.compile(r"active"))

        # Click fast
        fast_btn.click()
        expect(fast_btn).to_have_class(re.compile(r"active"))
        tab_page.wait_for_timeout(100)
        assert not has_class(tab_page, ".speed-btn[data-speed='slow']", "active")

    def test_content_tap_toggles_scroll(self, tab_page: Page):
        """Test that tapping on content toggles auto-scroll."""
        content = tab_page.locator("#tab-content")
        button = tab_page.locator("#auto-scroll-toggle")

        # Click on content to start scrolling
        content.click()
        expect(button).to_have_class(re.compile(r"active"))

        # Click again to stop
        content.click()
        tab_page.wait_for_timeout(100)
        assert not has_class(tab_page, "#auto-scroll-toggle", "active")


class TestAutoScrollWebKit:
    """WebKit-specific tests to validate iOS Safari compatibility."""

    def test_webkit_auto_scroll_works(self, browser_type, live_server: str):
        """Test that auto-scroll works on WebKit (Safari engine)."""
        if browser_type.name != "webkit":
            pytest.skip("This test requires WebKit browser")

        browser = browser_type.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},  # iPhone 16 dimensions
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
                "AppleWebKit/605.1.15"
            ),
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")

        button = page.locator("#auto-scroll-toggle")

        initial_scroll = page.evaluate("window.pageYOffset")
        button.click()
        page.wait_for_timeout(1500)  # 1.5 seconds
        new_scroll = page.evaluate("window.pageYOffset")

        browser.close()

        assert new_scroll > initial_scroll, (
            f"WebKit should scroll. Initial: {initial_scroll}, New: {new_scroll}"
        )

    def test_webkit_touch_to_toggle(self, browser_type, live_server: str):
        """Test that tapping content toggles auto-scroll on touch devices."""
        if browser_type.name != "webkit":
            pytest.skip("This test requires WebKit browser")

        browser = browser_type.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent=(
                "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) "
                "AppleWebKit/605.1.15"
            ),
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")

        content = page.locator("#tab-content")
        button = page.locator("#auto-scroll-toggle")

        # Tap content to start scrolling
        content.tap()
        expect(button).to_have_class(re.compile(r"active"))

        # Tap again to stop
        content.tap()
        page.wait_for_timeout(100)
        classes = button.get_attribute("class") or ""
        assert "active" not in classes.split()

        browser.close()
