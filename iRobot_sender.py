from wxpy import *
from wechat_sender import *

bot = Bot()
log_group = ensure_one(bot.groups().search('机器人'))
listen(bot,[log_group])