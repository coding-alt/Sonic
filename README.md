## 🎥 Demo
| Input                | Output                | Input                | Output                |
|----------------------|-----------------------|----------------------|-----------------------|
|<img src="examples/image/anime1.png" width="360">|<video src="https://github.com/user-attachments/assets/636c3ff5-210e-44b8-b901-acf828071133" width="360"> </video>|<img src="examples/image/female_diaosu.png" width="360">|<video src="https://github.com/user-attachments/assets/e8207300-2569-47d1-9ad4-4b4c9b0f0bd4" width="360"> </video>|
|<img src="examples/image/hair.png" width="360">|<video src="https://github.com/user-attachments/assets/dcb755c1-de01-4afe-8b4f-0e0b2c2439c1" width="360"> </video>|<img src="examples/image/leonnado.jpg" width="360">|<video src="https://github.com/user-attachments/assets/b50e61bb-62d4-469d-b402-b37cda3fbd27" width="360"> </video>|


For more visual demos, please visit our [**Page**](https://jixiaozhong.github.io/Sonic/).

## 🧩 Community Contributions
If you develop/use Sonic in your projects, welcome to let us know.

- ComfyUI version of Sonic: [**ComfyUI_Sonic**](https://github.com/smthemex/ComfyUI_Sonic)


## 📜 Requirements
* An NVIDIA GPU with CUDA support is required. 
  * The model is tested on a single 32G GPU.
* Tested operating system: Linux

## 🔑 Inference

### Installtion

- install pytorch
```shell
  pip install -r requirements.txt
```
- All models are stored in `checkpoints` by default, and the file structure is as follows
```shell
Sonic
  ├──checkpoints
  │  ├──Sonic
  │  │  ├──audio2bucket.pth
  │  │  ├──audio2token.pth
  │  │  ├──unet.pth
  │  ├──stable-video-diffusion-img2vid-xt
  │  │  ├──...
  │  ├──whisper-tiny
  │  │  ├──...
  │  ├──RIFE
  │  │  ├──flownet.pkl
  │  ├──yoloface_v5m.pt
  ├──...
```
Download by `huggingface-cli` follow
```shell
  python3 -m pip install "huggingface_hub[cli]"
  huggingface-cli download LeonJoe13/Sonic --local-dir  checkpoints
  huggingface-cli download stabilityai/stable-video-diffusion-img2vid-xt --local-dir  checkpoints/stable-video-diffusion-img2vid-xt
  huggingface-cli download openai/whisper-tiny --local-dir checkpoints/whisper-tiny
```

or manully download [pretrain model](https://drive.google.com/drive/folders/1oe8VTPUy0-MHHW2a_NJ1F8xL-0VN5G7W?usp=drive_link), [svd-xt](https://huggingface.co/stabilityai/stable-video-diffusion-img2vid-xt) and [whisper-tiny](https://huggingface.co/openai/whisper-tiny) to checkpoints/ 

## 🎬 Inference API

### Celery配置
```
celery_app.py
```

### 启动Celery worker：
```
celery -A tasks worker --loglevel=info
```

### 启动FastAPI服务：
```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 创建视频生成任务：
```
curl -X POST "http://localhost:8000/generate_video" \
-H "Content-Type: application/json" \
-d '{"image_url":"https://example.com/image.jpg","audio_url":"https://example.com/audio.wav","dynamic_scale":1.0}'
```
### 查看视频生成结果：
```
curl "http://localhost:8000/task/{task_id}"
```


### Supervisord配置
```
[program:sonic_api]
command=bash -c "cd /data/Sonic && /home/work/data/miniconda3/envs/Sonic/bin/uvicorn main:app --host 0.0.0.0 --port 8005 --reload"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/sonic_api.err.log
stdout_logfile=/var/log/supervisor/sonic_api.out.log

[program:sonic_celery]
command=bash -c "cd /data/Sonic && /home/work/data/miniconda3/envs/Sonic/bin/celery -A tasks worker --loglevel=info --pool=threads"
autostart=true
autorestart=true
stderr_logfile=/var/log/supervisor/sonic_celery.err.log
stdout_logfile=/var/log/supervisor/sonic_celery.out.log
```