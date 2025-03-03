import os
import numpy as np
import hashlib
from PIL import Image
import requests
from io import BytesIO
from pydub import AudioSegment
from sonic import Sonic
from celery_app import celery_app

pipe = Sonic(0)
tmp_path = './tmp_path/'
res_path = './res_path/'
os.makedirs(tmp_path, exist_ok=1)
os.makedirs(res_path, exist_ok=1)

def get_md5(content):
    md5hash = hashlib.md5(content)
    return md5hash.hexdigest()

def download_file(url):
    response = requests.get(url)
    return BytesIO(response.content)

def get_video_res(img_path, audio_path, res_video_path, dynamic_scale=1.0):
    expand_ratio = 0.5
    min_resolution = 512
    inference_steps = 25

    face_info = pipe.preprocess(img_path, expand_ratio=expand_ratio)
    if face_info['face_num'] > 0:
        crop_image_path = img_path + '.crop.png'
        pipe.crop_image(img_path, crop_image_path, face_info['crop_bbox'])
        img_path = crop_image_path
        os.makedirs(os.path.dirname(res_video_path), exist_ok=True)
        pipe.process(img_path, audio_path, res_video_path, 
                    min_resolution=min_resolution, 
                    inference_steps=inference_steps, 
                    dynamic_scale=dynamic_scale)
        return res_video_path
    return None

@celery_app.task(bind=True)
def process_sonic_task(self, image_url, audio_url, dynamic_scale=1.0):
    # 下载图片
    image_content = download_file(image_url)
    image = Image.open(image_content)
    img_md5 = get_md5(np.array(image).tobytes())
    
    # 下载音频
    audio_content = download_file(audio_url)
    audio_md5 = get_md5(audio_content.getvalue())
    
    # 保存文件
    image_path = os.path.abspath(os.path.join(tmp_path, f'{img_md5}.png'))
    audio_path = os.path.abspath(os.path.join(tmp_path, f'{audio_md5}.wav'))
    video_filename = f'{img_md5}_{audio_md5}_{dynamic_scale}.mp4'
    res_video_path = os.path.abspath(os.path.join(res_path, video_filename))
    
    if os.path.exists(res_video_path):
        return video_filename
    
    # 保存图片
    if not os.path.exists(image_path):
        image.save(image_path)
    
    # 保存音频
    if not os.path.exists(audio_path):
        audio = AudioSegment.from_file(audio_content)
        audio.export(audio_path, format="wav")
    
    # 处理视频
    result = get_video_res(image_path, audio_path, res_video_path, dynamic_scale)
    if result:
        return video_filename
    return None