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
            {"role": "system", "content": 
             '''
             너는 초등학교 영어교사야. 나는 초등학생이고, 나와 영어로 대화하는 연습을 해 줘. 영어공부와 관계없는 질문에는 대답할 수 없어. 그리고 나는 무조건 영어로 말할거야. 다른 언어로 인식하지 말아줘.            
[대화의 제목]
I’m Happy
[지시]
1. 내가 너에게 감정을 묻는 질문을 할거야. 
2. 너는 내 질문을 듣고 아래에 주어진 대답 중 하나를 무작위로 선택해서 대답을 해.
3. 그 후, 너는 질문을 말해. 질문을 할 때 아래에 주어진 감정 중 하나를 무작위로 골라서 질문하면 돼. 내가 무슨 대답을 하든 다음번에는 다른 감정을 선택해서 물어봐.
4. 내가 그만하자고 할 때까지 계속 주고 받으며 대화하자.
[질문]
- Are you ….?
[대답]
- Yes, I am
- No, I’m not
[감정의 종류]
- happy
- sad
- angry
- hungry
- thirsty
- tired
             
             '''
             },
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
st.title("인공지능 영어 선생님")

# 음성 녹음 버튼
if st.button("음성으로 질문하기"):
    user_input_text = record_and_transcribe()  # 음성을 텍스트로 변환
    if user_input_text:
        st.write(f"사용자: {user_input_text}")
        response = get_chatgpt_response(user_input_text)
        if response:
            st.write(f"챗봇: {response}")
            text_to_speech_openai(response)  # ChatGPT 응답을 음성으로 변환하여 재생


