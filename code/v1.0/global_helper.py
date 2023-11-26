# bot/helper.py

import os
import base64
import requests
import re

from pydub import AudioSegment
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv('.env')

class Helper:
    def is_user(self, user_id):
        allowed_users = os.getenv('USER_ID').split(',')
        return '*' in allowed_users or str(user_id) in allowed_users

    def is_admin(self, user_id):
        allowed_users = os.getenv('ADMIN_ID').split(',')
        return '*' in allowed_users or str(user_id) in allowed_users

    def translate_input(self, user_input):
        url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=auto&tl=en&q={user_input}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        }
        try:
            request_result = requests.get(url, headers=headers).json()
            user_input = request_result[0][0]
            user_lang = request_result[0][1]
            return user_input, user_lang
        except:
            return user_input, 'en'

    def translate_output(self, response, user_lang):
        if user_lang != 'en':
            url = f"https://clients5.google.com/translate_a/t?client=dict-chrome-ex&sl=en&tl={user_lang}&q={response}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
            }
            try:
                request_result = requests.get(url, headers=headers).json()
                response = request_result[0]
                return response, user_lang
            except:
                return response, user_lang
        else:
            return response, user_lang

    def tts(self, last_response):
        if last_response is not None:
            if last_response[1] is not None:
                user_lang = last_response[1]
                text = last_response[0]
            if last_response[1] is None:
                user_lang = 'en'
                text = last_response[0]
        if last_response is None:
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
        tts.save(f'voice_raw.mp3')

        audio = AudioSegment.from_file(f"voice_raw.mp3", format="mp3")
        audio = audio.speedup(playback_speed=1.22)
        audio.export(f'voice.mp3', format="mp3")
        os.remove(f'voice_raw.mp3')

    def generate_image(self, prompt, style="None"):
        api_key = os.getenv('STABILITY_API_KEY')
        common_params = {
            "samples": 1,
            "height": 1024,
            "width": 1024,
            "steps": 45,
            "cfg_scale": 6,
            "text_prompts": [
                {"text": prompt, "weight": 0.85},
                {
                    "text": "2 faces, 2 heads, bad anatomy, blurry, cloned face, cropped image, cut-off, deformed hands, disconnected limbs, disgusting, disfigured, draft, duplicate artifact, extra fingers, extra limb, floating limbs, gloss proportions, grain, gross proportions, long body, long neck, low-res, mangled, malformed, malformed hands, missing arms, missing limb, morbid, mutation, mutated, mutated hands, mutilated, mutilated hands, multiple heads, negative aspect, out of frame, poorly drawn, poorly drawn face, poorly drawn hands, signatures, surreal, tiling, twisted fingers, ugly",
                    "weight": -1,
                },
            ],
        }

        if style != "None":
            common_params["style_preset"] = style
        body = common_params.copy()
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
        if not os.path.exists("./out"):
            os.makedirs("./out")
        for i, image in enumerate(data["artifacts"]):
            with open(f'./out/txt2img_{image["seed"]}.png', "wb") as f:
                f.write(base64.b64decode(image["base64"]))
        return f'./out/txt2img_{data["artifacts"][0]["seed"]}.png'

helper_code = Helper()
