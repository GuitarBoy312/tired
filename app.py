import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import openai
import numpy as np

# OpenAI API 키 설정 (필요한 경우 secrets로 처리)
client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# 음성 처리 클래스 정의
class SpeechToTextProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_frames = []

    def recv_audio(self, frame: av.AudioFrame) -> av.AudioFrame:
        # 오디오 프레임을 numpy 배열로 변환하고 저장
        audio_data = frame.to_ndarray()
        self.audio_frames.append(audio_data)
        return frame

    def get_audio_data(self):
        # 누적된 오디오 데이터를 하나의 배열로 결합
        if len(self.audio_frames) > 0:
            return np.concatenate(self.audio_frames)
        return None

# Streamlit UI
st.title("🎤 인공지능 영어 선생님과 대화")
st.write("마이크로 말을 하고 결과를 확인하세요.")

# WebRTC 스트리머 (음성 녹음)
webrtc_ctx = webrtc_streamer(
    key="speech-to-text",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=SpeechToTextProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# 음성 녹음 및 변환 처리
if webrtc_ctx.audio_processor:
    audio_data = webrtc_ctx.audio_processor.get_audio_data()

    if audio_data is not None:
        st.info("음성을 변환 중입니다...")
        
        # Whisper API를 사용해 변환할 수 있도록 오디오 데이터를 처리
        audio_bytes = audio_data.tobytes()
        audio_file = open("audio.wav", "wb")
        audio_file.write(audio_bytes)
        audio_file.close()

        with open("audio.wav", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )

        user_input_text = transcription['text']
        st.write(f"사용자: {user_input_text}")

        # ChatGPT 응답 생성
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an English teacher for a child."},
                {"role": "user", "content": user_input_text},
            ]
        )
        st.write(f"챗봇: {response['choices'][0]['message']['content']}")
