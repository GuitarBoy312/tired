import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from openai import OpenAI
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode

# OpenAI API 키 설정
client = OpenAI(api_key=st.secrets["openai_api_key"])

# 음성 인식 및 변환
recognizer = sr.Recognizer()

def recognize_speech(audio_bytes):
    audio = sr.AudioFile(BytesIO(audio_bytes))
    with audio as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language='ko-KR')
        return text
    except sr.UnknownValueError:
        return "음성을 인식할 수 없습니다."
    except sr.RequestError as e:
        return f"음성 인식 서비스에 문제가 발생했습니다: {e}"

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "영어로만 응답해 주세요."}, {"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 텍스트를 음성으로 변환하고 재생
def text_to_speech(text):
    tts = gTTS(text=text, lang='en')
    audio_file = BytesIO()
    tts.write_to_fp(audio_file)
    audio_file.seek(0)
    st.audio(audio_file, format='audio/mp3')

# Streamlit UI
st.title("음성 기반 ChatGPT 챗봇")

# 음성 녹음 위젯
class AudioProcessor(AudioProcessorBase):
    def recv(self, frame):
        audio = frame.to_ndarray()
        # 필요한 경우 여기서 음성을 처리합니다.
        return frame

webrtc_ctx = webrtc_streamer(key="example", mode=WebRtcMode.SENDRECV, audio_processor_factory=AudioProcessor)

if webrtc_ctx and webrtc_ctx.audio_receiver:
    audio_frames = webrtc_ctx.audio_receiver.get_frames(timeout=1)
    if audio_frames:
        audio_bytes = audio_frames[0].data
        user_input = recognize_speech(audio_bytes)
        st.text(f"사용자: {user_input}")
        
        response = get_chatgpt_response(user_input)
        st.text(f"챗봇: {response}")
        
        text_to_speech(response)

