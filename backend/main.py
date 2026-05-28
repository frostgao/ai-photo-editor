from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pillow_heif
import io
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

pillow_heif.register_heif_opener()

app = FastAPI(title="AI Photo Editor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化通义千问客户端
client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

@app.get("/")
def root():
    return {"message": "AI Photo Editor API is running"}

@app.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # 读取并转换图片为JPEG
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # 统一转成JPEG（兼容HEIC等格式）
    img_bytes = io.BytesIO()
    image.convert("RGB").save(img_bytes, format="JPEG")
    img_bytes.seek(0)
    
    # 转成base64
    img_base64 = base64.b64encode(img_bytes.read()).decode("utf-8")

    # 调用通义千问视觉模型
    response = client.chat.completions.create(
        model="qwen-vl-max",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{img_base64}"
                        }
                    },
                    {
                        "type": "text",
                        "text": "请分析这张风景照片，描述：1）主要色调和氛围 2）光线情况 3）建议可以调整哪些参数来让照片更好看，比如亮度/对比度/饱和度/色温，给出具体的调整方向"
                    }
                ]
            }
        ]
    )

    return {
        "filename": file.filename,
        "ai_analysis": response.choices[0].message.content
    }