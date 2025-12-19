"""
Selenium UI Test Tool - Python library that simplifies Selenium WebDriver UI test automation

This library provides utilities and helper classes to simplify the creation and execution
of automated UI tests with Selenium WebDriver.
"""

from selenium_ui_test_tool.base_test.base_test import BaseTest
from selenium_ui_test_tool.driver_builder.driver_builder import create_driver
from selenium_ui_test_tool.get_url.get_url import get_url
from selenium_ui_test_tool.get_env_var.get_env_var import get_env_var
from selenium_ui_test_tool.wait_element.wait_elements import wait_for_element
from selenium_ui_test_tool.config_actions.config_actions import configure_actions
from selenium_ui_test_tool.click_element.click_element import click_element
from selenium_ui_test_tool.click_on.click_on import click_on
from selenium_ui_test_tool.fill_input.fill_input import fill_input
from selenium_ui_test_tool.fill_login_form.fill_login_form import fill_login_form
from selenium_ui_test_tool.fill_login_form_with_confirm_password.fill_login_form_with_confirm_password import fill_login_form_with_confirm_password
from selenium_ui_test_tool.upload_file.upload_file import upload_file
from selenium_ui_test_tool.assert_text_present.assert_text_present import assert_text_present

__version__ = "2.1.2"
__all__ = [
    "BaseTest",
    "create_driver",
    "get_url",
    "get_env_var",
    "wait_for_element",
    "configure_actions",
    "click_element",
    "click_on",
    "fill_input",
    "fill_login_form",
    "fill_login_form_with_confirm_password",
    "upload_file",
    "assert_text_present",
]

