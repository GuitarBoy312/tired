import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from audiorecorder import audiorecorder

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 사용할 모델
        messages=[
            {"role": "system", "content": 
             '''
             너는 초등학교 영어교사야. 나는 초등학생이고, 나와 영어로 대화하는 연습을 해 줘. 영어공부와 관계없는 질문에는 대답할 수 없어. 그리고 나는 무조건 영어로 말할거야. 다른 언어로 인식하지 말아줘.            
[대화의 제목]
I'm Happy
[지시]
1. 내가 너에게 감정을 묻는 질문을 할거야. 
2. 너는 내 질문을 듣고 아래에 주어진 대답 중 하나를 무작위로 선택해서 대답을 해.
3. 그 후, 너는 질문을 말해. 질문을 할 때 아래에 주어진 감정 중 하나를 무작위로 골라서 질문하면 돼. 내가 무슨 대답을 하든 다음번에는 다른 감정을 선택해서 물어봐.
4. 내가 그만하자고 할 때까지 계속 주고 받으며 대화하자.
[질문]
- Are you ….?
[대답]
- Yes, I am
- No, I'm not
[감정의 종류]
- happy
- sad
- angry
- hungry
- thirsty
- tired
             '''
             },
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# Streamlit UI

# 메인 화면 구성
st.title("✨인공지능 영어 선생님👱🏾‍♂️")
st.subheader("감정에 대한 대화하기")
st.divider()

# 채팅 히스토리 초기화
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# 메시지 출력 함수
def display_messages():
    for message in st.session_state['chat_history']:
        if message['role'] == 'user':
            st.chat_message("user").write(message['content'])
        else:
            st.chat_message("assistant").write(message['content'])

# 오디오 녹음
audio_bytes = audiorecoder()

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    # 오디오 파일을 저장
    audio_file_path = Path("recorded_audio.wav")
    with open(audio_file_path, "wb") as f:
        f.write(audio_bytes)

    # Whisper API를 사용해 음성을 텍스트로 변환
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    user_input_text = transcription.text
    st.session_state['chat_history'].append({"role": "user", "content": user_input_text})
    response = get_chatgpt_response(user_input_text)
    if response:
        st.session_state['chat_history'].append({"role": "chatbot", "content": response})

# 메시지 표시
display_messages()

# 사이드바 구성
with st.sidebar:
    st.header(
        '''
사용방법
1. '음성으로 질문하기' 버튼을 눌러 파란색이 활성화되면 인공지능 선생님에게 질문하기
2. 재생버튼(세모)를 눌러 선생님의 대답을 듣기
3. '음성으로 질문하기' 버튼을 눌러 파란색이 활성화되면 대답하고 바로 질문하기
'''
    )
    st.divider()

    st.subheader("다음 보기 중 골라서 질문해 보세요")
    st.markdown("1️⃣ Are you happy?<br>2️⃣ Are you sad?<br>3️⃣ Are you angry?<br>4️⃣ Are you hungry?<br>5️⃣ Are you thirsty?<br>6️⃣ Are you tired?", unsafe_allow_html=True)

    st.divider()

    st.subheader("선생님의 질문을 듣고, 다음 보기 중 골라서 대답해 보세요.")
    st.markdown("1️⃣ Yes, I am.<br>2️⃣ No, I'm not.", unsafe_allow_html=True)
