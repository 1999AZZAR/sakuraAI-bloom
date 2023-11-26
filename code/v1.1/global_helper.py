# bot/helper.py

import os
import base64
import requests
import concurrent.futures
import re
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
        except Exception as e:
            print(f"Error in translate_input: {e}")
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
            except Exception as e:
                print(f"Error in translate_output: {e}")
                return response, user_lang
        else:
            return response, user_lang

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

    def generate_image(self, prompt, style="None", size="1:1"):
        api_key = os.getenv('STABILITY_API_KEY')
        common_params = {
            "samples": 1,
            "steps": 45,
            "cfg_scale": 3.7,
            "text_prompts": [
                {
                    "text": prompt, 
                    "weight": 0.9
                },
                {
                    "text": "The artwork showcases excellent anatomy with a clear, complete, and appealing depiction. It has well-proportioned and polished details, presenting a unique and balanced composition. The high-resolution image is undamaged and well-formed, conveying a healthy and natural appearance without mutations or blemishes. The positive aspect of the artwork is highlighted by its skillful framing and realistic features, including a well-drawn face and hands. The absence of signatures contributes to its seamless and authentic quality, and the depiction of straight fingers adds to its overall attractiveness.",
                    "weight": 0.1
                },
                {
                    "text": "2 faces, 2 heads, bad anatomy, blurry, cloned face, cropped image, cut-off, deformed hands, disconnected limbs, disgusting, disfigured, draft, duplicate artifact, extra fingers, extra limb, floating limbs, gloss proportions, grain, gross proportions, long body, long neck, low-res, mangled, malformed, malformed hands, missing arms, missing limb, morbid, mutation, mutated, mutated hands, mutilated, mutilated hands, multiple heads, negative aspect, out of frame, poorly drawn, poorly drawn face, poorly drawn hands, signatures, surreal, tiling, twisted fingers, ugly",
                    "weight": -1
                },
            ],
        }

        size_mapping = {
            "5:4": (1152, 896),
            "11:8": (1216, 832),
            "16:9": (1344, 768),
            "8:3": (1536, 640),
            "1:1": (1024, 1024),
            "3:8": (640, 1536),
            "4:5": (896, 1152),
            "8:11": (832, 1216),
            "9:16": (768, 1344),
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
            for i, image in enumerate(data["artifacts"]):
                with open(f'{output_directory}/txt2img_{image["seed"]}.png', "wb") as f:
                    f.write(base64.b64decode(image["base64"]))
            return f'{output_directory}/txt2img_{data["artifacts"][0]["seed"]}.png'
        except Exception as e:
            print(f"Error in generate_image: {e}")
            return None

helper_code = Helper()
