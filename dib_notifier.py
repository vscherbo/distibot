#!/usr/bin/env python
""" Distibot notification class
"""

import os
import sys
import logging
import telegram
import asyncio
from telegram.request import HTTPXRequest
# ссылка на канал dib-000 https://t.me/joinchat/oJUXFAQZNQwyZGEy

CHAT_ID = -1001566883283
"""
1.  start a chat with BotFather;
type /newbot, select a name (to be shown in chats) and handle for your bot;
note the bot token to access HTTP API - a long string with a colon in the middle

2.visit https://api.telegram.org/bot<token>/getUpdates
answer:
{
    "ok": true,
    "result": [
        {
            "update_id": 129011095,
            "my_chat_member": {
                "chat": {
                    "id": -1001566883283,
                    "title": "dib-000",
                    "type": "channel"
                },
                "from": {
                    "id": 183420637,
                    "is_bot": false,
                    "first_name": "\u0412\u043b\u0430\u0434\u0438\u043c\u0438\u0440",
                    "last_name": "\u0429\u0435\u0440\u0431\u043e",
                    "username": "vscherbo",
                    "language_code": "ru"
                },
                "date": 1627997007,
                "old_chat_member": {
                    "user": {
                        "id": 1434022585,
                        "is_bot": true,
                        "first_name": "distibot",
                        "username": "user_distibot"
                    },
                    "status": "left"
                },
                "new_chat_member": {
                    "user": {
                        "id": 1434022585,
                        "is_bot": true,
                        "first_name": "distibot",
                        "username": "user_distibot"
                    },
                    "status": "administrator",
                    "can_be_edited": false,
                    "can_manage_chat": true,
                    "can_change_info": false,
                    "can_post_messages": true,
                    "can_edit_messages": false,
                    "can_delete_messages": false,
                    "can_invite_users": true,
                    "can_restrict_members": true,
                    "can_promote_members": false,
                    "can_manage_voice_chats": false,
                    "is_anonymous": false
                }
            }
        }
    ]
}


"""


class TGNotifier(telegram.Bot):
    """ A class for notification to Telegram chat
    """
    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        # self.token = os.environ.get('TELEGRAM_DIB_TOKEN')
        try:
            token = os.environ['TELEGRAM_DIB_TOKEN']
        except KeyError as unset:
            raise KeyError('TELEGRAM_DIB_TOKEN is unset') from unset
        except:
            logging.error("Unexpected error:%s", sys.exc_info()[0])
            raise
        else:
            trequest = HTTPXRequest(connection_pool_size=50, pool_timeout=200)
            super().__init__(token, request=trequest)

    def send_msg(self, message):
        """ Send a message to the Telegram chat with CHAT_ID
        """
        try:
            asyncio.run(self.sendMessage(chat_id=CHAT_ID, text=message))
        except TimeoutError:
            logging.error("TimeoutError:%s", sys.exc_info()[0])
        except Exception:
            logging.error("Unexpected error:%s", sys.exc_info()[0])
            raise

def main():
    """ Just main """
    tg_notifier = TGNotifier()
    tg_notifier.send_msg('test')


if __name__ == '__main__':
    main()
