import streamlit as st
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase, WebRtcMode
import av
import openai

# OpenAI API 키 설정 (필요한 경우 secrets로 처리)
client = openai.OpenAI(api_key=st.secrets["openai_api_key"])

# 음성 처리 클래스 정의
class SpeechToTextProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_data = b""

    def recv_audio(self, frames: av.AudioFrame) -> av.AudioFrame:
        # 오디오 데이터를 누적
        self.audio_data += frames.to_ndarray().tobytes()
        return frames

    def get_audio_data(self):
        return self.audio_data

# ChatGPT API 호출
def get_chatgpt_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
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
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

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
        st.audio(str(speech_file_path))  # 음성을 Streamlit에서 재생
    except Exception as e:
        st.error(f"텍스트를 음성으로 변환하는 중 오류가 발생했습니다: {e}")

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

    if len(audio_data) > 0:
        # OpenAI Whisper API를 사용해 음성을 텍스트로 변환
        st.info("음성을 변환 중입니다...")
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_data,
        )

        user_input_text = transcription['text']
        st.write(f"사용자: {user_input_text}")

        # ChatGPT 응답 생성
        response = get_chatgpt_response(user_input_text)
        st.write(f"챗봇: {response}")

        # 응답을 음성으로 변환하여 재생
        text_to_speech_openai(response)


