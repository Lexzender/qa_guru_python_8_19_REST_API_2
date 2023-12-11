import pytest
from selene import browser


@pytest.fixture(scope="function")
def browser_setup():
    browser.config.window_width = 1920
    browser.config.window_height = 1080
    browser.config.base_url = 'https://demowebshop.tricentis.com'

    yield

    browser.quit()
