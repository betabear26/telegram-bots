from flask import Flask, request
from config import Config, TeleConfig, AppConfig
import telebot
from constants import Constants
import telebot.types as types
import commandsHandler
import inlineHandler
import apiCalls

butlerBot = telebot.TeleBot(TeleConfig.BOT_TOKEN)

server = Flask(__name__)
server.config.from_object(Config)

@server.route('/', methods=['POST'])
def webhook():
    print(request)
    return "WTF do you want?",401
    
@server.route('/'+TeleConfig.BOT_TOKEN, methods=['POST'])
def getMessage():
    requestString = request.stream.read().decode("utf-8")
    server.logger.debug(f"Incoming message -> {requestString}")
    butlerBot.process_new_updates([telebot.types.Update.de_json(requestString)])
    
    return "!", 200

@butlerBot.message_handler(commands=['start'])
def start(message):
    server.logger.debug(f"start message -> from {message.from_user.username} and chat_id -> {message.chat.id}")
    butlerBot.send_message(message.chat.id, Constants.greeting.format(message.from_user.first_name))

@butlerBot.message_handler(commands=['help'])
def help(message):
    server.logger.debug(f"start message -> from {message.from_user.username} and chat_id -> {message.chat.id}")
    returnMessage = Constants.help
    butlerBot.send_message(message.chat.id, returnMessage)

@butlerBot.message_handler(commands=['sendnoodz'])
@butlerBot.message_handler(func=lambda message: message.text.lower()=="send noodz" if isinstance(message.text, str) else ' ')
def sendNoodz(message):
    server.logger.debug(f"start message -> from {message.from_user.username} and chat_id -> {message.chat.id}")
    pic = apiCalls.getRandomImage("Noodles")
    butlerBot.send_photo(message.chat.id, pic, reply_to_message_id=message.message_id)

@butlerBot.message_handler(commands=['roast'])
def roast(message):
    server.logger.debug(f"start message -> from {message.from_user.username} and chat_id -> {message.chat.id}")
    insult = apiCalls.generateRoast()
    if(message.reply_to_message != None):
        butlerBot.send_message(message.chat.id, insult, reply_to_message_id=message.reply_to_message.message_id)
    else:
        butlerBot.send_message(message.chat.id, insult)

@butlerBot.inline_handler(func=lambda query: query.query == "roast")
def roast_inline(query):
    server.logger.debug(f"inline query insult -> from {query.from_user.username}")
    insult = apiCalls.generateRoast()
    result = types.InlineQueryResultArticle('1', "Roast", types.InputTextMessageContent(insult))
    butlerBot.answer_inline_query(query.id, [result])



if __name__ == "__main__":
    server.debug=True
    server.run(host='0.0.0.0', port=AppConfig.PORT)
