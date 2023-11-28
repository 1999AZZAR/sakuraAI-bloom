# bot/helper.py

import os
import base64
import requests
import wikipediaapi
import concurrent.futures
import re
import html

from PIL import Image, ImageEnhance
from pydub import AudioSegment
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv('.env')

class Helper:
    def __init__(self):
        self.allowed_users = os.getenv('USER_ID').split(',')
        self.allowed_admins = os.getenv('ADMIN_ID').split(',')

    def is_user(self, user_id):
        return '*' in self.allowed_users or str(user_id) in self.allowed_users

    def is_admin(self, user_id):
        return '*' in self.allowed_admins or str(user_id) in self.allowed_admins

class Audio:

    def tts(self, last_response):
        if last_response is not None:
            user_lang = last_response[1] if last_response[1] is not None else 'en'
            text = last_response[0] if last_response[1] is not None else "There has been no response at the moment."
        else:
            user_lang = 'en'
            text = "There has been no response at the moment."

        dev_pattern = r'\[\d+\]:\s+https?://\S+\s+""\n'
        text = re.sub(dev_pattern, '', text)
        url_pattern = r"https?://\S+|www\.\S+|http?://\S+"
        text = re.sub(url_pattern, '', text)
        pattern = r'\[\^\d+\^\] \[\d+\]'
        text = re.sub(pattern, '', text)
        excluded_characters = "`#$^<>*_/\\{}[]|~"
        text = text.translate(str.maketrans('', '', excluded_characters))
        text = re.sub(r'\s+', ' ', text)

        if user_lang != 'en':
            tts = gTTS(text=text, lang=user_lang, slow=False)
        elif user_lang != 'ja':
            text = re.sub(r'[^\x00-\x7F]+', '', text)
            tts = gTTS(text=text, lang=user_lang, slow=False)
        else:
            tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
        tts.save('voice_raw.mp3')
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.submit(self.process_audio)

    def process_audio(self):
        try:
            audio = AudioSegment.from_file("voice_raw.mp3", format="mp3")
            audio = audio.speedup(playback_speed=1.22)
            audio.export('voice.mp3', format="mp3")
            os.remove('voice_raw.mp3')
        except Exception as e:
            print(f"Error in process_audio: {e}")

class Image_gen:

    def add_watermark(self, input_image_path, output_image_path, watermark_image_path, transparency=25):
        if watermark_image_path is None:
            original_image = Image.open(input_image_path)
            original_image.save(output_image_path)
            return

        original_image = Image.open(input_image_path)
        watermark = Image.open(watermark_image_path)
        min_dimension = min(original_image.width, original_image.height)
        watermark_size = (int(min_dimension * 0.14), int(min_dimension * 0.14))
        watermark = watermark.resize(watermark_size)
        if watermark.mode != 'RGBA':
            watermark = watermark.convert('RGBA')
        image_with_watermark = original_image.copy()
        position = (0, original_image.size[1] - watermark.size[1])
        image_with_watermark.paste(watermark, position, watermark)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(transparency / 100.0)
        watermark.putalpha(alpha)
        image_with_watermark.save(output_image_path)

    def generate_image(self, prompt, style="None", size="square"):
        api_key = os.getenv('STABILITY_API_KEY')
        common_params = {
            "samples": 1,
            "steps": 45,
            "cfg_scale": 3.7,
            "text_prompts": [
                {
                    "text"  : prompt, 
                    "weight": 0.9
                },
                {
                    "text"  : "The artwork showcases excellent anatomy with a clear, complete, and appealing depiction. It has well-proportioned and polished details, presenting a unique and balanced composition. The high-resolution image is undamaged and well-formed, conveying a healthy and natural appearance without mutations or blemishes. The positive aspect of the artwork is highlighted by its skillful framing and realistic features, including a well-drawn face and hands. The absence of signatures contributes to its seamless and authentic quality, and the depiction of straight fingers adds to its overall attractiveness.",
                    "weight": 0.1
                },
                {
                    "text"  : "2 faces, 2 heads, bad anatomy, blurry, cloned face, cropped image, cut-off, deformed hands, disconnected limbs, disgusting, disfigured, draft, duplicate artifact, extra fingers, extra limb, floating limbs, gloss proportions, grain, gross proportions, long body, long neck, low-res, mangled, malformed, malformed hands, missing arms, missing limb, morbid, mutation, mutated, mutated hands, mutilated, mutilated hands, multiple heads, negative aspect, out of frame, poorly drawn, poorly drawn face, poorly drawn hands, signatures, surreal, tiling, twisted fingers, ugly",
                    "weight": -1
                },
            ],
        }

        size_mapping = {
            "square-p"  : (1152, 896),
            "portrait"  : (1216, 832),
            "highscreen": (1344, 768),
            "panorama-p": (1536, 640),
            "square"    : (1024, 1024),
            "panorama"  : (640, 1536),
            "square-l"  : (896, 1152),
            "landscape" : (832, 1216),
            "widescreen": (768, 1344),
        }

        if size in size_mapping:
            common_params["height"], common_params["width"] = size_mapping[size]
        if style != "None":
            common_params["style_preset"] = style
        body = common_params.copy()

        try:
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {api_key}",
                },
                json=body,
            )

            if response.status_code != 200:
                raise Exception("Non-200 response: " + str(response.text))
            data = response.json()
            output_directory = "./out"
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            generated_image_path = f'{output_directory}/txt2img_{data["artifacts"][0]["seed"]}.png'
            with open(generated_image_path, "wb") as f:
                f.write(base64.b64decode(data["artifacts"][0]["base64"]))
            
            watermark_image_path = '/media/azzar/Betha/Download/project/telegram bot/sakuraAI-Bloom/logo.png' 
            output_with_watermark_path = generated_image_path
            self.add_watermark(generated_image_path, output_with_watermark_path, watermark_image_path, transparency=25)
            
            return f'{output_directory}/txt2img_{data["artifacts"][0]["seed"]}.png'
        except Exception as e:
            print(f"Error in generate_image: {e}")
            return None

class Translator:

    def translate_input(self, user_input):
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=en&q={user_input}"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

        try:
            request_result = requests.get(url, headers=headers).json()
            user_input = request_result[0][0]
            user_lang = request_result[0][1]
        except Exception as e:
            print(f"Error in translate_input: {e}")
            user_input, user_lang = user_input, 'en'

        return user_input, user_lang

    def translate_output(self, response, user_lang):
        if user_lang != 'en':
            response = html.escape(response)
            url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl={user_lang}&q={response}"
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}

            try:
                request_result = requests.get(url, headers=headers).json()
                response = request_result[0]
            except Exception as e:
                print(f"Error in translate_output: {e}")
                response = response

        return response, user_lang

class Wikip:
    def __init__(self):
        self.user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        self.wikipedia = wikipediaapi.Wikipedia('en', headers={'User-Agent': self.user_agent})

    def search(self, user_input):
        raw_query = user_input
        page = self.wikipedia.page(raw_query)

        if page.exists():
            summary = page.summary[0:500]
            link = f"\n\nRead more: [Wikipedia]({page.fullurl})"
            full_response = summary + link
        else:
            full_response = f"No results found for that search."

        return full_response

helper_code = Helper()
translate = Translator()
image_gen = Image_gen()
audio = Audio()
wikip = Wikip()
