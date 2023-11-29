# bot/main.py

import os
import logging
import telegram
import threading
import time
import html
import re

from datetime import datetime
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, ConversationHandler
from telegram import ChatAction, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.error import NetworkError
from global_helper import helper_code, translate, image_gen, audio, wikip
from palmai_helper import palm_instance
from datamanager import DatabaseManager

class BotHandler:
    connection_alive = True 

    def __init__(self):
        load_dotenv('.env')
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
        self.bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.updater = Updater(self.bot_token, use_context=True)
        self.dispatcher = self.updater.dispatcher
        self._add_CallbackQueryHandler()
        self.MAX_MESSAGE_LENGTH = 3000 # 4096 max
        self.palm_instance = palm_instance
        self.db_manager = DatabaseManager()
        self.helper = helper_code
        self.translate = translate
        self.user_last_responses = {}
        self.audio = audio
        
        self.wikip =wikip
        self.SEARCH = range(1)
        self.wiki_conv_handler = ConversationHandler(
            entry_points=[CommandHandler('wiki', self.start_search)],
            states={
                self.SEARCH: [MessageHandler(Filters.text, self.search)],
            },
            fallbacks=[],
        )
        
        self.image_gen = image_gen
        self.WAITING_FOR_PROMPT,self.WAITING_FOR_SIZE, self.WAITING_FOR_STYLE, self.PROCESSING = range(4)
        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('image', self.image)],
            states={
                self.WAITING_FOR_PROMPT: [MessageHandler(Filters.text & ~Filters.command, self.handle_image_prompt)],
                self.WAITING_FOR_SIZE: [MessageHandler(Filters.text & ~Filters.command, self.handle_image_size)],
                self.WAITING_FOR_STYLE: [MessageHandler(Filters.text & ~Filters.command, self.handle_image_style)],
            },
            fallbacks=[],
        )

    def _add_command_handlers(self):
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        self.dispatcher.add_handler(CommandHandler("start", self.start))
        self.dispatcher.add_handler(CommandHandler("reset", self.reset))
        self.dispatcher.add_handler(CommandHandler("detailed", self.detailed))
        self.dispatcher.add_handler(CommandHandler("simple", self.simple))
        self.dispatcher.add_handler(CommandHandler("paraphrase", self.paraphrase))
        self.dispatcher.add_handler(CommandHandler("summarize", self.summarize))
        self.dispatcher.add_handler(CommandHandler("elaborate", self.elaborate))
        self.dispatcher.add_handler(CommandHandler("generalize", self.generalize))
        self.dispatcher.add_handler(self.conv_handler)
        self.dispatcher.add_handler(self.wiki_conv_handler)

    def _add_CallbackQueryHandler(self):
        self.dispatcher.add_handler(CallbackQueryHandler(self.button_click))

    def _add_message_handler(self):
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.process_input))

    def _add_error_handler(self):
        self.dispatcher.add_error_handler(self.error_handler)

    def error_handler(self, update, context):
        logging.error(f"Error occurred: {context.error}")
        if update.message:
            update.message.reply_text("Sorry, something went wrong. Please try again later.")
        else:
            logging.warning("Update message is None. Unable to send error message to the user.")

    def connection_watchdog(self):
        while True:
            try:
                self.updater.bot.get_me()
                if not self.connection_alive:
                    logging.info("Connection reestablished.")
                    self.connection_alive = True
            except NetworkError:
                if self.connection_alive:
                    logging.error("Connection lost. Attempting to reconnect...")
                    self.connection_alive = False
                    self.updater.start_polling(drop_pending_updates=True)
            time.sleep(10)

    def process_input(self, update, context):
        user_id = update.message.from_user.id
        self.send_chat_action(update, context, ChatAction.TYPING)
        if self.helper.is_user(user_id):
            user_input = html.escape(update.message.text)
            logging.info(f"got {update.message.from_user.first_name} as user with id {user_id}, input: {user_input}")
            translated_input = self.translate.translate_input(user_input)
            user_input = translated_input[0]
            response = self.palm_instance.generate_chat(user_input)
            if response is not None:
                response = re.sub(r"\bI am a large language model\b", "my name is Sakura", response, flags=re.IGNORECASE)
                message = self.translate.translate_output(response, f"{translated_input[1]}")
            else:
                message = [f"I'm sorry, but an unexpected problem has occurred. If you wish, you can try again later."]
        else:
            message = [f"Apologies, you lack the necessary authorization to utilize my services."]
        self.send_message(update, context, message)

    def send_chat_action(self, update, context, action):
        try:
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action=action)
        except telegram.error.TimedOut:
            logging.error("Timed out while sending chat action. Ignoring and continuing.")

    def send_message(self, update, context, message):
        self.send_chat_action(update, context, ChatAction.TYPING)
        user_id = self.get_user_id_from_update(update)
        response = message[0]
        lang = message[1]
        data_id = self.get_data_id()
        logging.info("Storing user data")
        self.db_manager.store_user_data(user_id, data_id, response, lang)
        logging.info(f"Sending response: {message}")
        try:
            if response is not None:
                chunks = [response[i:i + self.MAX_MESSAGE_LENGTH] for i in range(0, len(response), self.MAX_MESSAGE_LENGTH)]
                for index, chunk in enumerate(chunks):
                    reply_markup = self.get_inline_keyboard(data_id, index, len(chunks))
                    chunk = re.sub(r'\] \(', '](', chunk, flags=re.IGNORECASE)
                    try:
                        context.bot.send_message(chat_id=update.effective_chat.id, text=chunk, parse_mode="MARKDOWN", reply_markup=reply_markup, disable_web_page_preview=False)
                    except telegram.error.BadRequest:
                        # chunk = html.escape(chunk)
                        context.bot.send_message(chat_id=update.effective_chat.id, text=chunk, reply_markup=reply_markup, disable_web_page_preview=False)
            if response is None:
                message = ("I'm sorry, but an unexpected problem has occurred. If you wish, you can try again later.", 'en')
                self.send_message(update, context, message)
        except:
            message = ("there has been no response at the moment", 'en')
            self.send_message(update, context, message)

    def button_click(self, update, context):
        query = update.callback_query
        user_id = query.from_user.id if query.from_user else None
        if user_id is not None:
            callback_data_parts = query.data.split("_")
            if len(callback_data_parts) == 2:
                data_id = int(callback_data_parts[1])
                logging.info(f"User {user_id} clicked the button for data_id {data_id}")
                response_text = self.db_manager.retrieve_user_data_by_data_id(user_id, data_id)
                self.user_last_responses[user_id] = response_text
                if callback_data_parts[0] == 'tts':
                    self.handle_tts(update, context, response_text)
                elif callback_data_parts[0] in ['summarize', 'paraphrase', 'elaborate']:
                    self.handle_text_generation(update, context, callback_data_parts[0])
            else:
                self.handle_user_info_not_available(update, context)
        else:
            self.handle_user_info_not_available(update, context)

    def get_user_id_from_update(self, update):
        return (update.callback_query.from_user.id if update.callback_query and update.callback_query.from_user else None) or \
            (update.message.from_user.id if update.message and update.message.from_user else None)

    def get_data_id(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%d%m%y%H%M%S")
        return int(formatted_time)

    def get_inline_keyboard(self, data_id, index, total_chunks):
        if index == total_chunks - 1:
            return InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔊 voice", callback_data=f"tts_{data_id}"),
                        InlineKeyboardButton("📝 elaborate", callback_data=f"elaborate_{data_id}"),
                    ],
                    [
                        InlineKeyboardButton("🗞️ summary", callback_data=f"summarize_{data_id}"),
                        InlineKeyboardButton("✍🏻 paraphrase", callback_data=f"paraphrase_{data_id}"),
                    ],
                ]
            )
        else:
            return None

    def handle_tts(self, update, context, response_text):
        if response_text:
            logging.info(f"asking for TTS")
            self.send_chat_action(update, context, ChatAction.RECORD_AUDIO)
            self.audio.tts(response_text)
            self.send_chat_action(update, context, ChatAction.UPLOAD_AUDIO)
            context.bot.send_voice(chat_id=update.callback_query.message.chat_id, voice=open('voice.mp3', 'rb'))
            os.remove('voice.mp3')
            logging.info("TTS done")
        else:
            message = ("Could not find response for data_id {data_id}", 'en')
            self.send_chat_action(update, context, ChatAction.TYPING)
            time.sleep(1)
            self.send_message(update, context, message)

    def handle_text_generation(self, update, context, action):
        logging.info(f"asking for {action} answer")
        user_id = self.get_user_id_from_update(update)
        self.send_chat_action(update, context, ChatAction.TYPING)

        if self.helper.is_user(user_id):
            user_input = context.args
            translated_input = self.get_translated_input(user_input, user_id)

            if translated_input:
                command = self.get_command(action)
                response = self.palm_instance.generate_text(f"{command} + {translated_input[0]}")
                message = self.translate.translate_output(response, f"{translated_input[1]}")
            else:
                message = ("An unexpected problem has occurred. If you wish, you can try again later.", 'en')
        else:
            message = ("Sorry, you are not authorized to use this feature", 'en')

        self.send_message(update, context, message)

    def get_translated_input(self, user_input, user_id):
        if user_input:
            user_input = ' '.join(user_input)
            logging.info(f"User selected the command with input: {user_input}")
            message = f"{user_input}"
            translated_input = self.translate.translate_input(message)
        else:
            message = self.user_last_responses[user_id]
            translated_input = self.translate.translate_input({message})

        return translated_input

    def get_command(self, action):
        commands = {
            'summarize' : "summarize this for me make it more simple and shorter but understandable: \n",
            'paraphrase': "paraphrase the following text by proofreading, rewording, and/or rephrasing it. I'm looking for a refined version that maintains clarity and coherence.: \n",
            'elaborate' : "Elaborate this make it longer by providing more details, but ensure it remains understandable.: \n",
            'generalize': "generalize this statement, eliminate the specifics and make it more organized and comprehensible.: \n",
        }
        return commands.get(action, "")

    def summarize(self, update, context):
        self.handle_text_generation(update, context, 'summarize')

    def paraphrase(self, update, context):
        self.handle_text_generation(update, context, 'paraphrase')

    def elaborate(self, update, context):
        self.handle_text_generation(update, context, 'elaborate')

    def generalize(self, update, context):
        self.handle_text_generation(update, context, 'generalize')

    def handle_user_info_not_available(self, update, context):
        message = ("User information not available.", 'en')
        self.send_chat_action(update, context, ChatAction.TYPING)
        time.sleep(1)
        self.send_message(update, context, message)

    def help_command(self, update, context):
        user_id = update.message.from_user.id
        self.send_chat_action(update, context, ChatAction.TYPING)
        if self.helper.is_user(user_id):
            logging.info(f"User selected the /help command")
            commands = [
                "🌸 Explore the blossoming possibilities with SakuraAI Bloom! Here are the commands at your service: 😊",
                "\n1. Operation mode 📳",
                "- /paraphrase - Transform your input or my latest response.",
                "- /summarize  - Condense your input or my latest response.",
                "- /elaborate  - Expand on your input or my latest response.",
                "- /image - Generate an image from text.",
                "\n2. Question And Answer 🤓",
                "- /detailed - Seek a detailed answer.",
                "- /simple   - Request a straightforward answer.",
                "- /wiki - Search for wikipedia."
                "\n3. System Set ⚙️",
                "- /start - Initiate a conversation with me.",
                "- /help  - Reveal this helpful menu.",
                "- /reset - Reset me for re-initialization.",
                "\nHow may I assist you further on this blooming journey? 💬🌸"
            ]
            self.send_chat_action(update, context, ChatAction.TYPING)
            message = ("\n".join(commands))
        else:
            message = (f"Apologies, you lack the necessary authorization to utilize my services.")
        update.message.reply_text(text=message, parse_mode="MARKDOWN")

    def start(self, update, context):
        user_id = update.message.from_user.id
        self.send_chat_action(update, context, ChatAction.TYPING)
        if self.helper.is_user(user_id):
            logging.info(f"User selected the /start command")
            message = (f"🌸 Greetings {update.message.from_user.first_name}, I'm SakuraAI, \nyour savvy companion. How may I assist you today? 💬 \nUse \"/help\" to unveil my command prowess. Let's dive into the world of possibilities together! 🚀✨")         
        else:
            message = (f"Apologies, you lack the necessary authorization to utilize my services.",'en')
        update.message.reply_text(text=message, parse_mode="MARKDOWN")

    def reset(self, update, context):
        user_id = update.message.from_user.id
        self.send_chat_action(update, context, ChatAction.TYPING)
        if self.helper.is_admin(user_id):
            logging.info(f"User selected the /reset command")
            self.palm_instance.reset()
            message = (f"Sakura has been reset. You can now use \"/start\" to re-initialize me for a new conversation.")
        else:
            message = (f"Apologies, but access to this command is restricted to administrators only.")
        update.message.reply_text(text=message, parse_mode="MARKDOWN")

    def generate_chat_response(self, update, context, command_template):
        user_id = update.message.from_user.id
        self.send_chat_action(update, context, ChatAction.TYPING)

        if self.helper.is_user(user_id):
            user_input = context.args
            if user_input:
                user_input = ' '.join(user_input)
                logging.info(f"User selected the command with input: {user_input}")
                command = f"{command_template} + {user_input}"
                translated_input = self.translate.translate_input(user_input)
                response = self.palm_instance.generate_chat(command)
                message = self.translate.translate_output(response, translated_input[1])
            else:
                message = (f"Please pass your argument directly after the command.", 'en')
        else:
            message = (f"Apologies, you lack the necessary authorization to utilize my services.", 'en')

        self.send_message(update, context, message)

    def detailed(self, update, context):
        command_template = "give me a detailed possible answer or explanation about"
        self.generate_chat_response(update, context, command_template)

    def simple(self, update, context):
        command_template = "give me one simple possible answer or explanation (35 word max) about"
        self.generate_chat_response(update, context, command_template)

    def image(self, update, context):
        user_id = update.message.from_user.id
        logging.info(f"image generation from {update.message.from_user.first_name}")
        chat_id = update.message.chat_id
        if self.helper.is_user(user_id):
            update.message.reply_text("Please enter a prompt for the image generation:")
            context.user_data['state'] = self.WAITING_FOR_PROMPT
            return self.WAITING_FOR_PROMPT
        else:
            update.message.reply_text("Apologies, you lack the necessary authorization to utilize my services.")
            return ConversationHandler.END

    def handle_image_prompt(self, update, context):
        chat_id = update.message.chat_id
        if 'state' in context.user_data and context.user_data['state'] == self.WAITING_FOR_PROMPT:
            prompt = update.message.text
            context.user_data['prompt'] = prompt
            size_keyboard = [
                ["landscape", "widescreen", "panorama"],
                ["square-l","square","square-p"],
                ["portrait", "highscreen", "panorama-p"]
            ]
            reply_markup = ReplyKeyboardMarkup(size_keyboard, one_time_keyboard=True)
            update.message.reply_text("Please select the preferred size for the image:", reply_markup=reply_markup)
            context.user_data['state'] = self.WAITING_FOR_SIZE
            return self.WAITING_FOR_SIZE

    def handle_image_size(self, update, context):
        chat_id = update.message.chat_id
        if 'state' in context.user_data and context.user_data['state'] == self.WAITING_FOR_SIZE:
            size = update.message.text
            context.user_data['size'] = size
            style_keyboard = [
                ["photographic", "enhance", "anime"],
                ["digital-art", "comic-book", "fantasy-art"],
                ["line-art", "analog-film", "neon-punk"],
                ["isometric", "low-poly", "origami"],
                ["modeling-compound", "cinematic", "3d-model"],
                ["pixel-art", "tile-texture", "None"]
            ]
            reply_markup = ReplyKeyboardMarkup(style_keyboard, one_time_keyboard=True)
            update.message.reply_text("Please select a style for the image:", reply_markup=reply_markup)
            context.user_data['state'] = self.WAITING_FOR_STYLE
            return self.WAITING_FOR_STYLE

    def handle_image_style(self, update, context):
        chat_id = update.message.chat_id
        if 'state' in context.user_data and context.user_data['state'] == self.WAITING_FOR_STYLE:
            style = update.message.text
            prompt = context.user_data.get('prompt', '')
            size = context.user_data.get('size', 'square')
            context.user_data['state'] = self.PROCESSING
            reply_markup = ReplyKeyboardRemove()
            logging.info(f"generating image")
            message = update.message.reply_text("Processing...", reply_markup=reply_markup)
            generated_image_path = self.image_gen.generate_image(prompt, style, size)
            if generated_image_path:
                self.send_chat_action(update, context, ChatAction.UPLOAD_PHOTO)
                with open(generated_image_path, "rb") as f:
                    context.bot.send_photo(chat_id, photo=f)
                context.bot.delete_message(chat_id=chat_id, message_id=message.message_id)
                os.remove(generated_image_path)
                logging.info(f"Image successfully generated and sent to user {chat_id}")
            else:
                logging.error(f"Error generating image for user {chat_id}")
                context.bot.send_message(chat_id, "Sorry, there was an error generating the image. Please try again using another prompt.")
            return ConversationHandler.END
        return context.user_data.get('state', self.WAITING_FOR_PROMPT)

    def start_search(self, update, context):
        update.message.reply_text("Please enter your search query:")
        return self.SEARCH

    def search(self, update, context):
        user_id = update.message.from_user.id
        if self.helper.is_user(user_id):
            user_input = html.escape(update.message.text)
            translated_input = self.translate.translate_input(user_input)
            self.send_chat_action(update, context, ChatAction.TYPING)
            results = self.wikip.search(translated_input[0])
            message = self.translate.translate_output(results, translated_input[1])
        else:
            message = (f"Apologies, you lack the necessary authorization to utilize my services.")
        self.send_message(update, context, message)
        return ConversationHandler.END

    def run(self):
        self._add_command_handlers()
        self._add_message_handler()
        self._add_error_handler()
        self.updater.start_polling()
        logging.info("The bot has started")
        logging.info("The bot is listening for messages")
        threading.Thread(target=self.connection_watchdog, daemon=True).start()
        self.updater.idle()

if __name__ == "__main__":
    bot_handler = BotHandler()
    bot_handler.run()
