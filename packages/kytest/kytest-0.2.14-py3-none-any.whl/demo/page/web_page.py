"""
@Author: kang.yang
@Date: 2024/9/14 09:48
"""
import kytest
from kytest.core.web import Elem


class LoginPage(kytest.Page):
    url = "https://www.qizhidao.com/login?redirect=https%3A%2F%2Fwww.qizhidao.com%2F&businessSource" \
          "=PC%E7%BB%BC%E5%90%88-%E9%A1%B6%E9%83%A8%E6%A8%A1%E5%9D%97-%E7%AB%8B%E5%8D%B3%E7%99%BB%E5%BD%95&" \
          "registerPage=https%3A%2F%2Fwww.qizhidao.com%2F&fromPage=home"
    log_reg = Elem(
        tag='登录注册按钮',
        text="登录/注册",
        exact=True
    )
    pwd_log = Elem(
        tag='密码登录按钮',
        text='密码登录'
    )
    phone = Elem(
        tag='手机号输入框',
        placeholder='请输入手机号码'
    )
    pwd = Elem(
        tag='密码输入框',
        placeholder='请输入密码'
    )
    accept = Elem(
        tag='接受选择框',
        locator='//div[@class="agreeCheckbox el-popover__reference"]'
    )
    log_now = Elem(
        tag='立即登录按钮',
        role='button',
        name='立即登录'
    )
    first_company = Elem(
        tag='第一个公司',
        locator="(//div[@class='company-msg__name'])[1]"
    )

