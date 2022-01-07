# auto-freenom

一个 freenom 域名管理工具，用于自动续期快要过期的域名。目前是写了两个类工具可以方便的管理 Freenom 中的域名，有着 cookies 持久化、日志管理等功能。

## 使用方法




## Example

```python
from freenom import Freenom, MailSender

# 登陆你的 freenom 账户并获取域名
freenom_domains = Freenom('example@yearliny.com', '000000')
# 更新所有可以更新的域名
freenom_domains.renew_all()

# 一个发送邮件提醒的工具类
mail = MailSender('example@yearliny.com', '000000')
mail.send('example@yearliny.com', '您的 Freenom 域名已续期', '请您知晓，这是这次更新的记录', html=False)
```