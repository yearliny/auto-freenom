# auto-freenom

一个 freenom 域名管理工具，用于自动续期快要过期的域名。目前是写了两个类工具可以方便的管理 Freenom 中的域名，有着 cookies 持久化、日志管理等功能。

## Usage

### Manual Run
```bash
# clone auto-freenom
git clone https://github.com/yearliny/auto-freenom.git
cd auto-freenom

# init venv and install dependencies
python3 -m venv venv
source ./venv/activate
pip install -r requirements.txt

# setup freenom username and password
cp config.example.ini config.ini
vim config.ini

# and run
chmod +x main.py
python3 main.py
```

### Run With Crontab

这里提供一个参考方法每天运行一次任务，检查是否存在待更新的域名并自动更新：

执行 `crontab -e` 命令，添加如下内容：
```bash
30 1 */1 * * cd /path/to/auto-freenom; ./venv/bin/python3 main.py >> runtime.log
```

Okay，大功告成！

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