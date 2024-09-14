import streamlit as st
from openai import OpenAI
import os
from pathlib import Path
from datetime import datetime
from audiorecorder import audiorecorder
from pydub import AudioSegment
import io

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai_api_key"])

# ChatGPT API 호출
def get_chatgpt_response(question):
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
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content
# 음성을 녹음하는 함수
def record_and_transcribe():
    audio = audiorecorder("클릭하여 녹음하기", "녹음중...클릭하여 저장하기")
    if len(audio) > 0:
        audio.export("recorded_audio.wav", format="wav")

    
    #recognizer = sr.Recognizer()
    #with sr.Microphone() as source:
        #st.info("음성을 녹음 중입니다. 말을 시작하세요...")
        #audio = recognizer.listen(source)
        #st.success("녹음이 완료되었습니다. 변환 중입니다...")
        #audio_bytes = io.BytesIO(audio.export().read())
        #audio_segment = AudioSegment.from_file(audio_bytes, format="mp3")
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
# STT 함수
#def STT(audio):
    # 파일 저장
    #filename = 'input.mp3'
    #audio.export(filename, format="mp3")
    
    # 음원 파일 열기
    #with open(filename, "rb") as audio_file:
        # Whisper 모델을 활용해 텍스트 얻기
        #transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
    
    # 파일 삭제
    #os.remove(filename)
    
    #return transcript.text

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
# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    if st.button("목소리로 대화하기", use_container_width=True): 
        user_input_text = record_and_transcribe()
        if user_input_text:
            st.session_state['chat_history'].append({"role": "user", "content": user_input_text})
            response = get_chatgpt_response(user_input_text)
            if response:
                text_to_speech_openai(response)
                st.session_state['chat_history'].append({"role": "chatbot", "content": response})    
   
with col2:
    if st.button("처음부터 다시하기",type="primary"):
        st.session_state['chat_history'] = []
        st.rerun()
        
# 기능 구현 공간
#col1, col2 = st.columns(2)
#with col1:
    # 왼쪽 영역 작성
    #st.subheader("질문하기")
    # 음성 녹음 아이콘 추가
    #audio = audiorecorder("클릭하여 녹음하기", "녹음중...클릭하여 저장하기")
    #if (audio.duration_seconds > 0) and (st.session_state.get("check_reset", False) == False):
        # 음성 재생 
        #st.audio(audio.export().read())
        # 음원 파일에서 텍스트 추출
        #audio_bytes = io.BytesIO(audio.export().read())
        #audio_segment = AudioSegment.from_file(audio_bytes, format="mp3")
        #question = STT(audio_segment)

        # 채팅을 시각화하기 위해 질문 내용 저장
        #now = datetime.now().strftime("%H:%M")
        #st.session_state["chat"] = st.session_state.get("chat", []) + [("user", now, question)]
        # GPT 모델에 넣을 프롬프트를 위해 질문 내용 저장
        #st.session_state["messages"] = st.session_state.get("messages", []) + [{"role": "user", "content": question}]
        #response = get_chatgpt_response(question)
        #if response:
            #st.session_state["chat"] = st.session_state["chat"] + [("chatbot", now, response)]
            #st.session_state["messages"] = st.session_state["messages"] + [{"role": "assistant", "content": response}]

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
