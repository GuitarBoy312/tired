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

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [
        {"role": "system", "content": 
         '''
        너는 초등학교 영어교사이고 이름은 잉글링(engling)이야. 나는 초등학생이야. 나와 영어로 대화하는 연습을 하거나, 영어 표현에 대한 질문에 한국어로 대답을 해줘. 
        영어공부와 관계없는 질문에는 대답할 수 없어. 나의 영어 수준은 CEFR A1 수준이야. 영어로 대화 할 때, 나에게 맞는 수준으로 말해줘.
         '''
        }
    ]

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
    audio = audiorecorder("녹음 시작", "녹음 완료", pause_prompt="잠깐 멈춤")
    
    if len(audio) > 0:
        st.success("녹음이 완료되었습니다. 변환 중입니다...")
        st.write("내가 한 말 듣기")
        # To play audio in frontend:
        st.audio(audio.export().read()) 
        
        # 녹음한 오디오를 파일로 저장
        audio_file_path = Path("recorded_audio.wav")
        audio.export(str(audio_file_path), format="wav")

        # Whisper API를 사용해 음성을 텍스트로 변환
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
            voice="shimmer",  # OpenAI TTS 모델에서 사용할 음성
            input=text
        )
        with open(speech_file_path, "wb") as f:
            f.write(response.content)  # 음성 파일을 저장
        st.write("인공지능 선생님의 대답 듣기")    
        st.audio(str(speech_file_path))  # 음성을 Streamlit에서 재생
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

# 메시지 출력 함수
def display_messages():
    for message in st.session_state['chat_history']:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        elif message['role'] == 'assistant':
            st.chat_message("assistant").write(message['content'])

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어대화 선생님 잉글링👱🏾‍♂️")
st.markdown("**😃자유롭게 대화하기.**")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요. 👆✅", expanded=False):
    st.markdown(
    """ 
    1️⃣ [녹음 시작] 버튼을 눌러 잉글링에게 말하기.<br>
    2️⃣ [녹음 완료] 버튼을 누르고 내가 한 말과 잉글링의 대답 들어보기.<br> 
    3️⃣ [녹음 시작] 버튼을 다시 눌러 대답하고 이어서 바로 질문하기.<br>
    4️⃣ 1~3번을 반복하기. 말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르기.<br>
    <br>
    🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)
    st.divider()
    st.write("🔸이번 단원과 관련하여 궁금한 점을 물어볼 수 있어요.") 
    st.write("🔸영어에 대해 전반적으로 궁금한 점을 한국어나 영어 중 원하는 말로 질문해도 돼요.")
    st.write("🔸영어로 잉글링과 자유롭게 대화할 수도 있어요.")

# 대화 기록 표시
display_messages()
    
# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)

with col2:
    user_input = st.text_input("영어로 대화를 입력하세요:")
    if user_input:
        response = get_chatgpt_response(user_input)
        if response:
            text_to_speech_openai(response)

# 대화 초기화 버튼
if st.button("처음부터 다시하기"):
    st.session_state['chat_history'] = [st.session_state['chat_history'][0]]  # 시스템 메시지만 유지
    st.experimental_rerun()