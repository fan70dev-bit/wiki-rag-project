from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import json
from core.config import settings

router = APIRouter(prefix="/api/ai", tags=["AI 智能分析"])

class AskRequest(BaseModel):
    query: str
    context: str

@router.post("/ask")
async def ask_qianwen_stream(req: AskRequest):
    system_prompt = "你是一个严谨的学术助手。请严格基于【参考文本】回答。严禁胡编乱造。"
    user_prompt = f"【参考文本】:\n{req.context[:1500]}\n\n【指令】:针对以上内容，回答：{req.query}"

    url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.3,
        "stream": True  # 🚀 开启通义千问的流式输出
    }

    # 构建流式生成器
    def generate():
        try:
            # 使用 requests 的 stream 模式持续读取
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=30) as response:
                for line in response.iter_lines():
                    if line:
                        # 原封不动地把阿里云的流式数据推给前端
                        yield f"{line.decode('utf-8')}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    # 使用 FastAPI 的 StreamingResponse 返回事件流
    return StreamingResponse(generate(), media_type="text/event-stream")
