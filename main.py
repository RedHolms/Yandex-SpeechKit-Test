import requests as req
import json

from config import *

def bytes_to_str(b: bytes):
   result = ''
   for byte in b:
      result = result + "%" + hex(byte)[2:]
   return result

def cond_input(text: str):
   while True:
      answer = input(text)
      if answer.lower()[0] == 'y': return True
      elif answer.lower()[0] == 'n': return False

def uri_format(data: dict):
   result = ''

   temp = ''
   for k, v in data.items():
      result = result + temp + k + "=" + str(v)
      temp = '&'

   return result

class YandexSpeechKitTest:
   def __init__(self, token: str, folder_id: str, api_ver: int = 1) -> None:
      self._ya_token = token
      self._folder_id = folder_id
      self._api_ver = api_ver
      self.receive_iam_token()

   def receive_iam_token(self):
      response = req.post("https://iam.api.cloud.yandex.net/iam/v1/tokens", data=json.dumps({ "yandexPassportOauthToken": self._ya_token }))

      if not (response.status_code >= 200 and response.status_code <= 299):
         print("failed to receive IAM token: request failed (" + str(response.status_code) + ")")
         print("content: ", response.content)
         exit(1)

      json_response = response.json()

      self._iam_token = json_response["iamToken"]
      self._iam_session = req.Session()
      self._iam_session.headers = {
         "Authorization": "Bearer " + self._iam_token,
         "x-folder-id": self._folder_id
      }

   def speech_synthesis(self, text: str, out: str, voice: str = "zahar", emotion: str = "neutral", speed: float = 1.0, format: str = None):
      if format is None:
         # determine format
         if out.endswith(".ogg"):
            format = "oggopus"
         elif out.endswith(".wav"):
            format = "lpcm"
         elif out.endswith(".mp3"):
            format = "mp3"
         else:
            format = "oggopus" # by default

      request_body = {
         "text": bytes_to_str(text.encode('utf-8')),
         "lang": "ru-RU",
         "voice": voice,
         "emotion": emotion,
         "speed": speed,
         "format": format,
         "folderId": self._folder_id
      }

      print('request body ', uri_format(request_body))

      response = self._iam_session.post("https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize", data=uri_format(request_body))

      if not (response.status_code >= 200 and response.status_code <= 299):
         print("failed to speech_synthesis(): request failed (" + str(response.status_code) + ")")
         print("content: ", response.content)
         exit(1)

      with open(out, "wb+") as f:
         f.write(response.content)
         f.close()

def main():
   if cond_input("do you want to see token?[y/n] "):
      print("token: '" + CFG_YA_TOKEN + "'")
   
   app = YandexSpeechKitTest(CFG_YA_TOKEN, CFG_YA_FOLDER)

   text = input("Enter text: ")

   out_filename = "output.ogg"
   app.speech_synthesis(text, out_filename)

   print('writen to ' + out_filename)

   return 0

if __name__ == "__main__":
   exit(main())