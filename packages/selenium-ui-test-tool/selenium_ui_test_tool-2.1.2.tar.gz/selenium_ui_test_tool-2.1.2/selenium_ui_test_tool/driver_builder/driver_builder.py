from selenium import webdriver


def create_driver(headless=False):
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")


    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(2)
    return driver
