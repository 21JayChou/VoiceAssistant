import wave
import pyaudio
import whisper
import os
from aip import AipSpeech

# 定义数据流块
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
# 录音时间
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "./output.wav"
# 创建PyAudio对象
p = pyaudio.PyAudio()
# 打开数据流
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)
# 开始录音
print("* recording")
frames = []
for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK)
    frames.append(data)
print("* done recording")
# 停止数据流
stream.stop_stream()
stream.close()
p.terminate()
# 写入录音文件
wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
wf.setnchannels(CHANNELS)
wf.setsampwidth(p.get_sample_size(FORMAT))
wf.setframerate(RATE)
wf.writeframes(b''.join(frames))
wf.close()
#
# # 设置 APPID、API Key 和 Secret Key
# APP_ID = '56463137'
# API_KEY = 'mAgLHm74CTsgpAHQOefcl6gV'
# SECRET_KEY = 'PNyrMPYpksaGCTyV66tUfYd3DSXtDuq8'
#
#
# # 初始化 AipSpeech 对象
# client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# 设置音频文件的位置
audio_file = './output.wav'

# # 读取音频文件
# with open(audio_file, 'rb') as fp:
#     audio_data = fp.read()
#
# # 识别音频文件
# res = client.asr(audio_data, 'wav', 16000, {
#     'dev_pid': 1737,
# })
# print(res)

model = whisper.load_model("base")
result = model.transcribe(os.path.abspath(audio_file))
print(result["text"])