from selenium.webdriver import Chrome, ChromeOptions

if __name__ == "__main__":
    WINDOW_SIZE = "1220,1200"
    options = ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=%s" % WINDOW_SIZE)
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    # options.experimental_options("useAutomationExtension", False)
    driver = Chrome("./webdriver/chromedriver", chrome_options=options)

    driver.get("https://vk.com")
    driver.save_screenshot(f'./static/screenshots/test_screenshot.png')
    driver.close()