import tables
from telegram.ext import Updater, CommandHandler, Filters,  MessageHandler, BaseFilter
from telegram import ChatMember
from mwt import MWT
import logging

import re

h5f = tables.open_file('database.h5', 'r+')

users = h5f.get_node('/', 'users')
messages = h5f.get_node('/', 'messages')

updater = Updater(token='739574371:AAHeKi0i5H4Q-XFFsr9mJ1345cWJ3Ntt8ak')

dispatcher = updater.dispatcher

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


class NewMember(BaseFilter):
    def filter(self, message):
        if not message.new_chat_members:
            return False
        return True


class allMessages(BaseFilter):
    def filter(self, message):
        return True


def welcome(bot, update):
    for row in messages:
        welcomemess = row['Welcome'].decode('utf-8')
    bot.send_message(chat_id="-1001150510706", text=welcomemess)

def rules(bot, update, chat_data):
    if update.message.from_user.id in get_admin_ids(bot, "-1001150510706"):
        new = update.message.text[12:]
        for row in messages:
            row['Rules'] = new
            row.update()
        message = bot.send_message(chat_id="-1001150510706", text=new)
        bot.pin_chat_message("-1001150510706", message.message_id)

def changeWelcome(bot, update, chat_data):
    if update.message.from_user.id in get_admin_ids(bot, "-1001150510706"):
        if update.message.from_user.id in get_admin_ids(bot, "-1001150510706"):
            new = update.message.text[12:]
            for row in messages:
                row['Welcome'] = new
                row.update()
                messages.flush()
            message = bot.send_message(chat_id=update.message.chat_id, text="Welcome Message Changed")
        else:
            print("Not admin")

def checkUser(memeber):
    username = memeber.username
    images = memeber.get_profile_photos().total_count

    if ((username == "") & (images == 0)):
        return False
    else:
        return True


def addUser(member):
    users.row['Handle'] = member.username
    users.row['UserID'] = member.id
    users.row['Name'] = re.sub(r'\W+', '', member.full_name)
    users.row.append()
    users.flush()

def add_group(bot, update):
    for members in update.message.new_chat_members:
        if members.is_bot:
            bot.send_message(update.message.chat_id, text=members.first_name + " is a bot")
        else:
            welcome(bot, update)
            #addUser(members)

def buildTable(bot, update):
    exists = False
    rowtocheck = 0
    print(update.message.from_user)
    for row in users:
        if row["UserID"].decode('utf-8') == str(update.message.from_user.id):
            exists = True
            username = row['Handle'].decode('utf-8')
            rowtocheck = row
    if not exists:
        addUser(update.message.from_user)
    else:
        if update.message.from_user.username != username:
            rowtocheck["Handle"] = username
            rowtocheck.update()
            users.flush()






@MWT(timeout=60*60)
def get_admin_ids(bot, chat_id):
    """Returns a list of admin IDs for a given chat. Results are cached for 1 hour."""
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

add_group_handle = MessageHandler(callback=add_group, filters=NewMember())
dispatcher.add_handler(add_group_handle)
all_handle = MessageHandler(callback=buildTable, filters=allMessages())

welcome_handle = CommandHandler('welcome', welcome)
dispatcher.add_handler(welcome_handle)

changewelcome_handle = CommandHandler('newWelcome', changeWelcome, pass_chat_data=True)
dispatcher.add_handler(changewelcome_handle)

dispatcher.add_handler(all_handle)

updater.start_polling(clean=True)