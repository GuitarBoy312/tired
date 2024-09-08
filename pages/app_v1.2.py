import streamlit as st
from openai import OpenAI
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import os
from pydub import AudioSegment
from pydub.playback import play
from langdetect import detect
from pathlib import Path

# OpenAI API 키 설정 (OpenAI 계정에서 발급받은 API 키를 넣어주세요)
client = OpenAI(
  api_key=st.secrets["openai_api_key"], 
)

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 사용할 모델
        messages=[
            {"role": "system", "content": "너는 초등학교 영어교사야. 나는 초등학생이야 내 영어공부를 도와줘."},
            {"role": "user", "content": user_input_text}
        ]
    )
    return response.choices[0].message.content


# 음성을 녹음하고 텍스트로 변환하는 함수 (Whisper API 사용)
def record_and_transcribe():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("음성을 녹음 중입니다. 말을 시작하세요...")
        audio = recognizer.listen(source)
        st.success("녹음이 완료되었습니다. 변환 중입니다...")

        # 녹음한 오디오를 파일로 저장
        audio_file_path = Path("recorded_audio.wav")
        with open(audio_file_path, "wb") as f:
            f.write(audio.get_wav_data())

        # Whisper API를 사용해 음성을 텍스트로 변환
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    try:
        speech_file_path = Path("speech.mp3")
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # OpenAI TTS 모델에서 사용할 음성
            input=text
        )
        with open(speech_file_path, "wb") as f:
            f.write(response.content)  # 음성 파일을 저장
        st.audio(str(speech_file_path))  # 음성을 Streamlit에서 재생
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")


# Streamlit UI
st.title("음성 기반 ChatGPT 챗봇 (OpenAI Whisper + TTS)")

# 음성 녹음 버튼
if st.button("음성으로 질문하기"):
    user_input_text = record_and_transcribe()  # 음성을 텍스트로 변환
    if user_input_text:
        st.write(f"사용자: {user_input_text}")
        response = get_chatgpt_response(user_input_text)
        if response:
            st.write(f"챗봇: {response}")
            text_to_speech_openai(response)  # ChatGPT 응답을 음성으로 변환하여 재생


