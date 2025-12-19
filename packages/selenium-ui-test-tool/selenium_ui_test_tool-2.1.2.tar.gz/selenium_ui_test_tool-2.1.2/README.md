# Selenium UI Test Tool

Python library that simplifies Selenium WebDriver UI test automation.

## 🌐 Languages

- 🇫🇷 [Lire la documentation en français](README.fr.md)

## 📋 Table of Contents

- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [API Reference](#-api-reference)
- [Examples](#-examples)
- [CI/CD Mode](#-cicd-mode)
- [Project Structure](#-project-structure)
- [Contributing](#-contributing)
- [License](#-license)
- [Author](#-author)
- [Report a Bug](#-report-a-bug)
- [Contact](#-contact)

## 🚀 Installation

### Install from PyPI (when published)

```bash
pip install selenium-ui-test-tool
```

### Install from source

```bash
git clone <repository-url>
cd selenium_ui_test_tool
pip install -e .
```

### Dependencies

- Python >= 3.8
- Selenium >= 4.15.0
- python-dotenv >= 1.0.0
- webdriver-manager >= 4.0.1

## ⚙️ Configuration

### Environment variables

Create a `.env` file at the root of your project with the required variables:

```env
# Sample configuration
CHROMEDRIVER_PATH=/path/to/chromedriver  # Optional
HEADLESS=false  # true to run headless
CI=false  # true when running in CI/CD
```

### ChromeDriver setup

The library automatically handles ChromeDriver in several ways:

1. **Environment variable**: if `CHROMEDRIVER_PATH` is set it will be used.
2. **webdriver-manager**: downloads and manages the matching version for you.
3. **Fallback**: uses `/opt/homebrew/bin/chromedriver` (macOS Homebrew) when available.

## 📖 Usage

### Basic example

```python
from selenium_ui_test_tool import BaseTest
from selenium.webdriver.common.by import By

def test_example(driver):
    """Return True when the page title contains 'Example'."""
    title = driver.title
    return "Example" in title

# Create and run the test
test = BaseTest(
    test_function=test_example,
    success_message="✅ Test passed!",
    failure_message="❌ Test failed!",
    url="https://example.com",
    exit_on_failure=True
)

test.run()
```

### Using the utilities

```python
from selenium_ui_test_tool import (
    create_driver,
    get_url,
    wait_for_element,
    configure_actions,
    click_element,
    click_on,
    fill_input,
    fill_login_form,
    fill_login_form_with_confirm_password,
    upload_file,
    assert_text_present,
    get_env_var
)
from selenium.webdriver.common.by import By

# Create a driver
driver = create_driver(headless=False)

# Navigate to a URL
get_url(driver, "https://example.com")

# Wait for an element
element = wait_for_element(driver, By.ID, "my-element", timeout=10)

# Configure and run a scroll+click action
configure_actions(driver, By.CSS_SELECTOR, ".my-button")

# Click with custom messages
click_element(
    driver,
    By.ID,
    "submit-button",
    success_message="Button clicked successfully",
    error_message="Unable to click the button"
)

# Build an action store with click_on
ticket_actions = [
    (By.XPATH, "//span[contains(text(),'Annual')]", "Annual section selected"),
    (By.XPATH, "//span[contains(text(),'Annual Pass')]", "Annual Pass selected"),
]

for by, selector, success_message in ticket_actions:
    click_on(
        driver,
        by,
        selector,
        success_message=success_message,
        error_message=f"Unable to click {selector}"
    )

# Fill a form field
fill_input(driver, By.ID, "username", "my_user")

# Fill a full login form
fill_login_form(
    driver,
    username_env="LOGIN_USERNAME",
    password_env="LOGIN_PASSWORD",
    by=By.ID,
    selector="login-form",
    button="login-button"
)

# Upload a file based on an env var path
upload_file(
    driver,
    file_path="FILE_PATH_ENV",  # Environment variable with the absolute path
    input_selector="file-input",
    by=By.ID,
    success_message="File uploaded",
    error_message="Upload failed"
)

# Assert that text is present on the page
assert_text_present(
    driver,
    By.CSS_SELECTOR,
    ".toast-message",
    expected_text="Order completed",
    timeout=5
)

# Read an environment variable
username = get_env_var("LOGIN_USERNAME", required=True)

# Always quit the driver
driver.quit()
```

## 📚 API Reference

### `BaseTest`

Main class that orchestrates complete UI tests.

```python
BaseTest(
    test_function: Callable[[WebDriver], bool],
    success_message: str,
    failure_message: str,
    url: str,
    exit_on_failure: bool = True
)
```

- `test_function`: callable that receives a `WebDriver` and returns `True`/`False`.
- `success_message`: message printed when the test succeeds.
- `failure_message`: message printed when the test fails.
- `url`: target URL to load.
- `exit_on_failure`: exit the process with code `1` when the test fails.

Methods:

- `setup()` – create the driver and open the URL.
- `teardown()` – close the driver.
- `run()` – run the full flow (setup → trigger → teardown).

### `create_driver(headless: bool = False) -> WebDriver`

Create and configure a Chrome WebDriver instance.

### `get_url(driver: WebDriver, url: str) -> None`

Navigate to a given URL.

### `wait_for_element(driver: WebDriver, by: By, selector: str, timeout: int = 10) -> WebElement | None`

Wait for an element to appear in the DOM.

### `configure_actions(driver: WebDriver, by: By, selector: str) -> bool`

Scroll to an element and click it.

### `click_element(...) -> bool`

Enhanced click helper that adds waits, verification, and custom messages.

### `click_on(...) -> bool`

Thin wrapper above `click_element` that enforces success/error messages.

### `fill_input(...) -> bool`

Scroll to an element, clear the field, and send keys.

### `fill_login_form(...) -> bool`

Automatically fill username/password fields from environment variables and submit.

### `fill_login_form_with_confirm_password(...) -> bool`

Same as `fill_login_form` but also fills a confirmation password field.

### `upload_file(...) -> bool`

Upload a file through an `<input type="file">` element using a path stored in the `.env` file.

### `get_env_var(name: str, required: bool = True) -> str | None`

Retrieve an environment variable and raise a helpful error if it is missing.

### `assert_text_present(driver, by, selector, expected_text, timeout=10) -> bool`

Wait for an element to appear, then assert that its text contains the expected substring. Raises `AssertionError` when the text does not match.

- `driver`: Selenium WebDriver instance.
- `by`: Locator strategy from Selenium's `By`.
- `selector`: Locator used to find the element.
- `expected_text`: Substring that must be present within the element text.
- `timeout`: Seconds to wait for the element before failing (default `10`).

> Refer to the French documentation for the full parameter details or use the inline docstrings shipped with the package.

## 💡 Examples

### Complete login test (with `fill_login_form`)

```python
from selenium_ui_test_tool import BaseTest, fill_login_form, wait_for_element
from selenium.webdriver.common.by import By

def test_login(driver):
    if not fill_login_form(
        driver,
        username_env="LOGIN_USERNAME",
        password_env="LOGIN_PASSWORD",
        by=By.ID,
        selector="login-form",
        button="login-button"
    ):
        return False

    welcome_message = wait_for_element(driver, By.CLASS_NAME, "welcome", timeout=5)
    return welcome_message is not None

test = BaseTest(
    test_function=test_login,
    success_message="✅ Logged in successfully!",
    failure_message="❌ Login failed",
    url="https://example.com/login",
    exit_on_failure=True
)

test.run()
```

### Manual login test (with `fill_input`)

```python
from selenium_ui_test_tool import BaseTest, fill_input, click_element, get_env_var
from selenium.webdriver.common.by import By

def test_login_manual(driver):
    if not fill_input(driver, By.ID, "username", get_env_var("LOGIN_USERNAME")):
        return False

    if not fill_input(driver, By.ID, "password", get_env_var("LOGIN_PASSWORD")):
        return False

    return click_element(
        driver,
        By.ID,
        "login-button",
        success_message="Login successful",
        error_message="Login failed"
    )

test = BaseTest(
    test_function=test_login_manual,
    success_message="✅ Login successful!",
    failure_message="❌ Login failed",
    url="https://example.com/login",
    exit_on_failure=True
)

test.run()
```

### Action store with `click_on`

```python
from selenium_ui_test_tool import BaseTest, click_on
from selenium.webdriver.common.by import By
import time

ACTIONS_MONTHLY = [
    (By.XPATH, "//span[contains(text(),'Monthly')]", "Monthly section opened"),
    (By.XPATH, "//span[contains(text(),'Monthly Pass')]", "Monthly Pass selected"),
]

def monthly_buying(driver):
    for by, selector, success in ACTIONS_MONTHLY:
        click_on(
            driver,
            by,
            selector,
            success_message=success,
            error_message=f"Unable to click {selector}"
        )

def buying_helper_monthly(driver):
    time.sleep(2)
    monthly_buying(driver)
    return True

test = BaseTest(
    test_function=buying_helper_monthly,
    success_message="✅ Monthly purchase completed",
    failure_message="❌ Purchase flow failed",
    url="https://example.com/store"
)

test.run()
```

### Headless mode

```python
from selenium_ui_test_tool import create_driver, get_url
import os

os.environ["HEADLESS"] = "true"

driver = create_driver(headless=True)
get_url(driver, "https://example.com")

# Run your checks...

driver.quit()
```

### Error handling

```python
from selenium_ui_test_tool import BaseTest, wait_for_element
from selenium.webdriver.common.by import By

def test_with_error_handling(driver):
    try:
        element = wait_for_element(driver, By.ID, "my-element", timeout=5)
        if element is None:
            print("⚠️ Element not found")
            return False

        # Your assertions
        return True
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

test = BaseTest(
    test_function=test_with_error_handling,
    success_message="✅ Test passed",
    failure_message="❌ Test failed",
    url="https://example.com",
    exit_on_failure=False
)

test.run()
```

## 🔧 CI/CD Mode

When `CI=true` is detected:

- Chrome automatically runs headless.
- Environment variables are read from GitHub Secrets (or similar).
- No interactive pause happens at the end.

### GitHub Actions sample

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install selenium-ui-test-tool
      - name: Run tests
        env:
          CI: true
          LOGIN_USERNAME: ${{ secrets.LOGIN_USERNAME }}
          LOGIN_PASSWORD: ${{ secrets.LOGIN_PASSWORD }}
        run: |
          python your_test_script.py
```

## 📝 Project Structure

```
selenium_ui_test_tool/
├── selenium_ui_test_tool/
│   ├── __init__.py
│   ├── base_test/
│   ├── click_element/
│   ├── config_actions/
│   ├── driver_builder/
│   ├── get_env_var/
│   ├── get_url/
│   └── wait_element/
├── pyproject.toml
├── setup.py
├── requirements.txt
├── README.md
└── env.example
```

## 🤝 Contributing

1. Fork the project.
2. Create your feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License

MIT License – see `LICENSE` for details.

## 👤 Author

Yann Dipita

## 🐛 Report a Bug

Please open an issue with:

- clear description,
- reproduction steps,
- expected vs. actual behavior,
- your environment (OS, Python, Selenium versions).

## 📧 Contact

For any question: [dipitay@gmail.com](mailto:dipitay@gmail.com).

---

**Note:** This library is under active development. Minor releases may introduce breaking changes.
