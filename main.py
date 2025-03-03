from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from celery.result import AsyncResult
from tasks import process_sonic_task
import os

app = FastAPI()

# 确保res_path目录存在
os.makedirs("res_path", exist_ok=True)

# 挂载静态文件目录
app.mount("/videos", StaticFiles(directory="res_path"), name="videos")

class VideoRequest(BaseModel):
    image_url: str
    audio_url: str
    dynamic_scale: float = 1.0

@app.post("/generate_video")
async def generate_video(request: VideoRequest):
    task = process_sonic_task.delay(
        request.image_url,
        request.audio_url,
        request.dynamic_scale
    )
    return {"task_id": task.id}

@app.get("/task/{task_id}")
async def get_task_status(task_id: str, request: Request):
    task_result = AsyncResult(task_id)
    if task_result.ready():
        if task_result.successful():
            video_filename = task_result.get()
            if video_filename:
                # 使用请求的host信息构建完整URL
                video_url = f"{request.base_url}videos/{video_filename}"
                return {
                    "status": "completed",
                    "video_url": video_url
                }
            return {"status": "failed", "error": "Video generation failed"}
        return {"status": "failed", "error": str(task_result.result)}
    return {"status": "processing"}