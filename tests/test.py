import json
import logging

import allure
import requests
from allure_commons.types import AttachmentType
from selene import browser, have

LOGIN = "TestAQA@mail.ru"
PASSWORD = "test123"
API_URL = "https://demowebshop.tricentis.com"
WEB_URL = "https://demowebshop.tricentis.com"


def demowebshop_api(url, **kwargs):
    with allure.step("API Request"):
        result = requests.post(url=API_URL + url, **kwargs)

        allure.attach(body=result.request.url, name="Request url",
                      attachment_type=AttachmentType.TEXT)
        allure.attach(body=json.dumps(result.request.body, indent=4, ensure_ascii=True), name="Request body",
                      attachment_type=AttachmentType.JSON, extension="json")

        # allure.attach(body=json.dumps(result.json(), indent=4, ensure_ascii=True), name="Response",
        #               attachment_type=AttachmentType.JSON, extension="json")

        logging.info("Request: " + result.request.url)
        if result.request.body:
            logging.info("INFO Request body: " + result.request.body)
        logging.info("Request headers: " + str(result.request.headers))
        logging.info("Response code " + str(result.status_code))
        logging.info("Response: " + result.text)
    return result


def test_login_though_api(browser_setup):
    with allure.step('Authorization though api'):
        results = demowebshop_api('/login',
                                  data={"Email": LOGIN, "Password": PASSWORD, 'RememberMe': False},
                                  allow_redirects=False)

    with allure.step('Saving authorization cookies'):
        cookie = results.cookies.get("NOPCOMMERCE.AUTH")

    with allure.step('Opening the browser'):
        browser.open('/')
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": cookie})
        browser.open('/')

    with allure.step('Verify successful authorization'):
        browser.element(".account").should(have.text(LOGIN))


def test_guest_add_to_cart_from_catalog_with_api(browser_setup):
    with allure.step('add_item_to_cart'):
        results = demowebshop_api('/addproducttocart/catalog/31/1/1')
    with allure.step('Saving  cookies'):
        cookie = results.cookies.get("Nop.customer")

    with allure.step('Opening the browser'):
        browser.open('/')
        browser.driver.add_cookie({"name": "Nop.customer", "value": cookie})
        browser.open("/cart")

    with allure.step('Verify successful add item to cart'):
        browser.all('.cart-item-row').should(have.size(1))
        browser.all('.cart-item-row').element_by(have.text('14.1-inch Laptop')).element('[name^="itemquantity"]') \
            .should(have.value("1"))


def test_user_add_to_cart_from_catalog_with_api(browser_setup):
    with allure.step('Authorization though api'):
        results = demowebshop_api('/login',
                                  data={"Email": LOGIN, "Password": PASSWORD, 'RememberMe': False},
                                  allow_redirects=False)

    with allure.step('Saving authorization cookies'):
        cookie = results.cookies.get("NOPCOMMERCE.AUTH")
        headers = {'Cookie': f'NOPCOMMERCE.AUTH={cookie}'}
        requests.post(url=API_URL + "/addproducttocart/catalog/31/1/1", headers=headers)

    with allure.step('Opening the browser'):
        browser.open('/')
        browser.driver.add_cookie({"name": "NOPCOMMERCE.AUTH", "value": cookie})
        browser.open("/cart")

    browser.element(".account").should(have.text(LOGIN))
    browser.all('.cart-item-row').element_by(have.text('14.1-inch Laptop'))
