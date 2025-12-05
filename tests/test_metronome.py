"""Browser tests for TabStash Metronome using Playwright."""

import re

import pytest
from playwright.sync_api import Page, expect


def has_class(page: Page, selector: str, class_name: str) -> bool:
    """Check if an element has a specific class."""
    classes = page.locator(selector).get_attribute("class") or ""
    return class_name in classes.split()


class TestMetronome:
    """Tests for metronome functionality."""

    @pytest.fixture
    def tab_page(self, page: Page, live_server: str) -> Page:
        """Navigate to a tab page."""
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")
        return page

    def test_metronome_button_exists(self, tab_page: Page):
        """Test that metronome button is present."""
        button = tab_page.locator("#metronome-toggle")
        expect(button).to_be_visible()
        expect(button).to_contain_text("Metronome")

    def test_metronome_shows_settings_on_click(self, tab_page: Page):
        """Test that clicking metronome shows settings."""
        button = tab_page.locator("#metronome-toggle")
        settings = tab_page.locator("#metronome-settings")

        # Initially settings hidden
        expect(settings).not_to_be_visible()

        # Click to activate
        button.click()

        # Button active, settings visible
        expect(button).to_have_class(re.compile(r"active"))
        expect(settings).to_be_visible()

    def test_bpm_input_present(self, tab_page: Page):
        """Test that BPM input is present and has valid value."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")
        expect(bpm_input).to_be_visible()

        # Should have a numeric value in valid range
        value = int(bpm_input.input_value())
        assert 20 <= value <= 300

    def test_bpm_input_has_metadata_value(self, tab_page: Page):
        """Test that BPM input is pre-filled with tab metadata."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")
        # Wonderwall has bpm: 87 in its metadata
        value = int(bpm_input.input_value())
        assert value == 87

    def test_bpm_adjustment_buttons(self, tab_page: Page):
        """Test BPM up/down buttons work."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")
        initial_bpm = int(bpm_input.input_value())

        # Click up button
        tab_page.locator("#bpm-up").click()
        new_bpm = int(bpm_input.input_value())
        assert new_bpm == initial_bpm + 5

        # Click down button twice
        tab_page.locator("#bpm-down").click()
        tab_page.locator("#bpm-down").click()
        final_bpm = int(bpm_input.input_value())
        assert final_bpm == initial_bpm - 5

    def test_bpm_input_manual_entry(self, tab_page: Page):
        """Test manual BPM entry."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")
        bpm_input.fill("140")
        bpm_input.blur()  # Trigger change event

        assert int(bpm_input.input_value()) == 140

    def test_bpm_clamped_to_min(self, tab_page: Page):
        """Test BPM is clamped to minimum 20."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")

        # Try setting too low
        bpm_input.fill("5")
        bpm_input.blur()
        assert int(bpm_input.input_value()) >= 20

    def test_bpm_clamped_to_max(self, tab_page: Page):
        """Test BPM is clamped to maximum 300."""
        tab_page.locator("#metronome-toggle").click()

        bpm_input = tab_page.locator("#bpm-input")

        # Try setting too high
        bpm_input.fill("500")
        bpm_input.blur()
        assert int(bpm_input.input_value()) <= 300

    def test_sync_button_present(self, tab_page: Page):
        """Test sync button exists."""
        tab_page.locator("#metronome-toggle").click()

        sync_btn = tab_page.locator("#sync-toggle")
        expect(sync_btn).to_be_visible()

    def test_sync_toggle(self, tab_page: Page):
        """Test sync button toggles state."""
        tab_page.locator("#metronome-toggle").click()

        sync_btn = tab_page.locator("#sync-toggle")

        # Initially not active
        assert not has_class(tab_page, "#sync-toggle", "active")

        # Click to activate
        sync_btn.click()
        expect(sync_btn).to_have_class(re.compile(r"active"))

        # Click to deactivate
        sync_btn.click()
        tab_page.wait_for_timeout(100)
        assert not has_class(tab_page, "#sync-toggle", "active")

    def test_beat_indicator_exists(self, tab_page: Page):
        """Test beat indicator element exists."""
        indicator = tab_page.locator("#beat-indicator")
        # Hidden by default but exists in DOM
        expect(indicator).to_be_attached()

    def test_metronome_toggle_off(self, tab_page: Page):
        """Test metronome can be toggled off."""
        button = tab_page.locator("#metronome-toggle")
        settings = tab_page.locator("#metronome-settings")

        # Turn on
        button.click()
        expect(settings).to_be_visible()

        # Turn off
        button.click()
        tab_page.wait_for_timeout(100)
        assert not has_class(tab_page, "#metronome-toggle", "active")


class TestMetronomeWebKit:
    """WebKit-specific tests for iOS Safari compatibility."""

    def test_webkit_metronome_button_touch(self, browser_type, live_server: str):
        """Test metronome works with touch on WebKit."""
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

        button = page.locator("#metronome-toggle")
        settings = page.locator("#metronome-settings")

        # Tap to activate
        button.tap()
        expect(button).to_have_class(re.compile(r"active"))
        expect(settings).to_be_visible()

        browser.close()

    def test_webkit_bpm_controls_touch_targets(self, browser_type, live_server: str):
        """Test BPM controls have adequate touch targets on mobile."""
        if browser_type.name != "webkit":
            pytest.skip("This test requires WebKit browser")

        browser = browser_type.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")

        page.locator("#metronome-toggle").tap()

        # Check touch target sizes (should be >= 44px)
        bpm_down = page.locator("#bpm-down")
        bpm_up = page.locator("#bpm-up")

        down_box = bpm_down.bounding_box()
        up_box = bpm_up.bounding_box()

        assert down_box["width"] >= 44, "BPM down button too small for touch"
        assert down_box["height"] >= 44, "BPM down button too small for touch"
        assert up_box["width"] >= 44, "BPM up button too small for touch"
        assert up_box["height"] >= 44, "BPM up button too small for touch"

        browser.close()

    def test_webkit_bpm_adjust_with_tap(self, browser_type, live_server: str):
        """Test BPM adjustment buttons work with tap."""
        if browser_type.name != "webkit":
            pytest.skip("This test requires WebKit browser")

        browser = browser_type.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            has_touch=True,
            is_mobile=True,
        )
        page = context.new_page()
        page.goto(f"{live_server}/tabs/oasis/wonderwall.html")

        page.locator("#metronome-toggle").tap()

        bpm_input = page.locator("#bpm-input")
        initial_bpm = int(bpm_input.input_value())

        # Tap up button
        page.locator("#bpm-up").tap()
        new_bpm = int(bpm_input.input_value())

        browser.close()

        assert new_bpm == initial_bpm + 5
