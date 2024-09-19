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
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 사용할 모델
        messages=[
            {"role": "system", "content": 
             '''
             너는 초등학교 영어교사야. 나는 초등학생이고, 나와 영어로 대화하는 연습을 해 줘. 영어공부와 관계없는 질문에는 대답할 수 없어. 그리고 나는 무조건 영어로 말할거야. 내 발음이 좋지 않더라도 영어로 인식하도록 노력해 봐.            
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

# Streamlit UI

# 메인 화면 구성
st.header("✨인공지능 영어대화 선생님 잉글링👩‍🏫")
st.markdown("**💕감정이나 느낌에 대한 대화하기**")
st.divider()

#확장 설명
with st.expander("❗❗ 글상자를 펼쳐 사용방법을 읽어보세요 👆✅", expanded=False):
    st.markdown(
    """     
    1️⃣ [녹음 시작] 버튼을 눌러 잉글링에게 말하기.<br>
    2️⃣ [녹음 완료] 버튼을 누르고 내가 한 말과 잉글링의 대답 들어보기.<br> 
    3️⃣ 재생 막대의 버튼으로 재생▶ 및 정지⏸,<br>
       재생 막대의 오른쪽 스노우맨 버튼(점 세개)을 눌러 재생 속도를 조절할 수 있습니다.<br> 
    4️⃣ [녹음 시작] 버튼을 다시 눌러 대답하고 이어서 바로 질문하기.<br>
    5️⃣ 1~3번을 반복하기. 말문이 막힐 땐 [잠깐 멈춤] 버튼을 누르기.<br>
    <br>
    🙏 잉글링은 완벽하게 이해하거나 제대로 대답하지 않을 수 있어요.<br> 
    🙏 그럴 때에는 [처음부터 다시하기] 버튼을 눌러주세요.
    """
    ,  unsafe_allow_html=True)
    st.divider()
    st.write("다음 보기 중 골라서 잉글링에게 질문해 보세요.")
    st.markdown('''
    🔸 Are you happy? (아 유 해피?)<br>
    🔸 Are you sad? (아 유 새드?)<br>
    🔸 Are you angry? (아 유 앵그리?)<br>
    🔸 Are you hungry? (아 유 헝그리?)<br>
    🔸 Are you thirsty? (아 유 떨스티?)<br>
    🔸 Are you tired? (아 유 다이얼드?)
    ''', unsafe_allow_html=True)
    st.divider()
    st.write("잉글링의 질문을 듣고, 다음 보기 중 골라서 대답해 보세요.")
    st.markdown('''
    🔸 Yes, I am.(예스 아이 앰.)<br>
    🔸 No, I'm not.(노 아임 낫.)
    ''', unsafe_allow_html=True)
    
# 버튼 배치
col1, col2 = st.columns([1,1])

with col1:
    user_input_text = record_and_transcribe()
    if user_input_text:
        st.session_state['chat_history'].append({"role": "user", "content": user_input_text})
        response = get_chatgpt_response(user_input_text)
        if response:
            text_to_speech_openai(response)
            st.session_state['chat_history'].append({"role": "chatbot", "content": response})    

with col2:
    if st.button("처음부터 다시하기", type="primary"):
        st.session_state['chat_history'] = []
        st.rerun()

# 사이드바 구성
with st.sidebar:
    # 메시지 표시
    display_messages()
    
    #st.header(
        #'''

#'''
    #)
    #st.divider()




