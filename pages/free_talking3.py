import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from audiorecorder import audiorecorder
from pydub import AudioSegment
from pydub.playback import play
from io import BytesIO

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    st.session_state['chat_history'].append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 사용할 모델
        messages=st.session_state['chat_history']
    )
    assistant_response = response.choices[0].message.content
    st.session_state['chat_history'].append({"role": "assistant", "content": assistant_response})
    return assistant_response

# 음성을 녹음하고 텍스트로 변환하는 함수
def record_and_transcribe():
    st.session_state.recording = True
    audio = audiorecorder("녹음 중...", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.session_state.recording = False
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.write("내가 한 말 듣기")
        st.audio(audio.export().read())
        
        audio_file_path = Path("recorded_audio.wav")
        audio.export(str(audio_file_path), format="wav")

        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    
    return None

# 텍스트를 음성으로 변환하고 재생하는 함수
def text_to_speech_openai(text):
    try:
        speech_file_path = Path("speech.mp3")
        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )
        with open(speech_file_path, "wb") as f:
            f.write(response.content)
        st.write("인공지능 선생님의 대답 듣기")    
        st.audio(str(speech_file_path))
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [
        {"role": "system", "content": 
         '''
        너는 초등학교 영어교사이고 이름은 잉글링(engling)이야. 나는 초등학생이야. 나와 영어로 대화하는 연습을 하거나, 영어 표현에 대한 질문에 한국어로 대답을 해줘. 
        영어공부와 관계없는 질문에는 대답할 수 없어.  나의 영어 수준은 CEFR A1 수준이야. 영어로 대화 할 때, 나에게 맞는 수준으로 말해줘.
         '''
        }
    ]

# 녹음 상태 초기화
if 'recording' not in st.session_state:
    st.session_state.recording = False

# Streamlit UI
