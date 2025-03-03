import gradio as gr
import os
import numpy as np
from pydub import AudioSegment
import hashlib
from sonic import Sonic

pipe = Sonic(0)

def get_md5(content):
    md5hash = hashlib.md5(content)
    md5 = md5hash.hexdigest()
    return md5

def get_video_res(img_path, audio_path, res_video_path, dynamic_scale=1.0):

    expand_ratio = 0.5
    min_resolution = 512
    inference_steps = 25

    face_info = pipe.preprocess(img_path, expand_ratio=expand_ratio)
    print(face_info)
    if face_info['face_num'] > 0:
        crop_image_path = img_path + '.crop.png'
        pipe.crop_image(img_path, crop_image_path, face_info['crop_bbox'])
        img_path = crop_image_path
        os.makedirs(os.path.dirname(res_video_path), exist_ok=True)
        pipe.process(img_path, audio_path, res_video_path, min_resolution=min_resolution, inference_steps=inference_steps, dynamic_scale=dynamic_scale)
    else:
        return -1
tmp_path = './tmp_path/'
res_path = './res_path/'
os.makedirs(tmp_path,exist_ok=1)
os.makedirs(res_path,exist_ok=1)

def process_sonic(image,audio,s0):
    img_md5= get_md5(np.array(image))
    audio_md5 = get_md5(audio[1])
    print(img_md5,audio_md5)
    sampling_rate, arr = audio[:2]
    if len(arr.shape)==1:
        arr = arr[:,None]
    audio = AudioSegment(
        arr.tobytes(),
        frame_rate=sampling_rate,
        sample_width=arr.dtype.itemsize,
        channels=arr.shape[1]
    )
    audio = audio.set_frame_rate(sampling_rate)
    image_path = os.path.abspath(tmp_path+'{0}.png'.format(img_md5))
    audio_path = os.path.abspath(tmp_path+'{0}.wav'.format(audio_md5))
    if not os.path.exists(image_path):
        image.save(image_path)
    if not os.path.exists(audio_path):
        audio.export(audio_path, format="wav")
    res_video_path = os.path.abspath(res_path+f'{img_md5}_{audio_md5}_{s0}.mp4')
    if os.path.exists(res_video_path):
        return res_video_path
    else:
        get_video_res(image_path, audio_path, res_video_path,s0)
    return res_video_path
    
inputs = [
    gr.Image(type='pil',label="上传人像图片"),
    gr.Audio(label="上传音频"),
    gr.Slider(0.5, 2.0, value=1.0, step=0.1, label="动作幅度", info="值越小，动作幅度越小"),
]
outputs = gr.Video(label="output.mp4")

def get_example():
    return [
        ["examples/image/female_diaosu.png", "examples/wav/sing_female_rap_10s.MP3", 1.0],
        ["examples/image/hair.png", "examples/wav/sing_female_10s.wav", 1.0],
        ["examples/image/anime1.png", "examples/wav/talk_female_english_10s.MP3", 1.0],
        ["examples/image/leonnado.jpg", "examples/wav/talk_male_law_10s.wav", 1.0],
        
    ]

css = """footer {visibility: hidden}"""
with gr.Blocks(title="Sonic", css=css, theme="Kasien/ali_theme_custom") as demo:
    gr.Interface(fn=process_sonic, inputs=inputs, outputs=outputs, title="Sonic: 一个音频驱动的数字人生成工具", direction="column", allow_flagging='never')
    gr.Examples(
        examples=get_example(),
        fn=process_sonic,
        inputs=inputs,
        outputs=outputs,
        cache_examples=False,)
    
demo.launch(server_name='0.0.0.0', server_port=8081, share=True, enable_queue=True)