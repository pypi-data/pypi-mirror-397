"""
@Author: kang.yang
@Date: 2025/12/9 17:47
"""
from page.web_page import LoginPage


class LoginApi:
    def __init__(self, driver):
        self.lp = LoginPage(driver)

    def pwd_login(self):
        self.lp.goto()
        self.lp.pwd_log.click()
        self.lp.phone.input('13652435335')
        self.lp.pwd.input('wz123456@QZD')
        self.lp.accept.click()
        self.lp.log_now.click()
        self.lp.first_company.click()
