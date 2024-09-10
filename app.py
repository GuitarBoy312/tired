import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from openai import OpenAI

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
            {"role": "system", "content": '''
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
             '''},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 텍스트를 음성으로 변환하고 Streamlit에서 재생
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')  # ChatGPT는 영어로 응답하므로 lang='en'
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    
    # Streamlit 오디오 위젯을 사용하여 음성 재생
    st.audio(audio_file, format='audio/mp3')

# Streamlit UI
st.title("음성 기반 ChatGPT 챗봇")

# 음성 입력 버튼
if st.button("음성으로 질문하기"):
    user_input = recognize_speech()  # 음성 인식
    if user_input:
        st.text(f"사용자: {user_input}")
        response = get_chatgpt_response(user_input)  # ChatGPT 응답 받기
        st.text(f"챗봇: {response}")
        
        # 응답을 음성으로 변환하여 재생
        text_to_speech(response)
