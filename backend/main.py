from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import io

app = FastAPI(title="AI Photo Editor API")

# 允许前端访问后端（跨域设置）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Photo Editor API is running"}

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    # 读取上传的图片
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    return {
        "filename": file.filename,
        "format": image.format,
        "size": image.size,        # (宽, 高) 单位px
        "mode": image.mode,        # RGB / RGBA 等
        "file_size_kb": round(len(contents) / 1024, 2)
    }