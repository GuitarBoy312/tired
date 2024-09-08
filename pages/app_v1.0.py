import streamlit as st
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import os
from pydub import AudioSegment
from pydub.playback import play
from langdetect import detect

# OpenAI API 키 설정 (OpenAI 계정에서 발급받은 API 키를 넣어주세요)
client = OpenAI(
  api_key=st.secrets["openai_api_key"], 
)
# 음성 인식 및 변환
recognizer = sr.Recognizer()

def recognize_speech():
    with sr.Microphone() as source:
        st.info("음성 입력을 기다리고 있습니다...")
        audio = recognizer.listen(source)
        st.success("음성 입력이 완료되었습니다.")
        try:
            text = recognizer.recognize_google(audio, language='ko-KR')
            return text
        except sr.UnknownValueError:
            return "음성을 인식할 수 없습니다."
        except sr.RequestError as e:
            return f"음성 인식 서비스에 문제가 발생했습니다: {e}"

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 사용할 모델
        messages=[
            {"role": "system", "content": "너는 초등학교 영어교사야. 나는 초등학생이야 내 영어공부를 도와줘."},
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content

# 음성을 텍스트로 변환하고, 텍스트를 다시 음성으로 변환
def text_to_speech(text):
    tts = gTTS(text=text, lang='en' or 'ko')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    
    # pydub을 사용하여 재생
    sound = AudioSegment.from_file(audio_file, format="mp3")
    play(sound)

# Streamlit UI
st.title("음성 기반 ChatGPT 챗봇")

# 음성 입력 버튼
if st.button("음성으로 질문하기"):
    user_input = recognize_speech()
    if user_input:
        st.text(f"사용자: {user_input}")
        response = get_chatgpt_response(user_input)
        st.text(f"챗봇: {response}")
        
        # 응답을 음성으로 변환하여 재생
        text_to_speech(response)
