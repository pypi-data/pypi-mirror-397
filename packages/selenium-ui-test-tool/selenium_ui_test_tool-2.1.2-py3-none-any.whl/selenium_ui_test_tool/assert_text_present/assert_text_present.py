"""Assertion helpers for checking text content on the page."""

from selenium_ui_test_tool import wait_for_element


def assert_text_present(driver, by, selector: str, expected_text: str, timeout: int = 10) -> bool:
    element = wait_for_element(driver, by, selector, timeout=timeout)
    if element is None:
        message = f"Element not found for selector '{selector}'."
        print(f"❌ {message}")
        raise AssertionError(message)

    actual_text = element.text.strip()
    if expected_text not in actual_text:
        message = (
            f"Assertion failed: expected '{expected_text}' to be inside '{actual_text}'."
        )
        print(f"❌ {message}")
        raise AssertionError(message)

    print(f"✅ Assertion succeeded: '{expected_text}' is present.")
    return True
