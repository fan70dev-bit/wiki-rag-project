from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search, ai_agent

app = FastAPI(title="Wiki Pro RAG 后端系统")

# 跨域配置 (允许前端访问)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由模块
app.include_router(search.router)
app.include_router(ai_agent.router)  # 🚀 解决 404 的关键：把 AI 路由注册进来

@app.get("/")
async def root():
    return {"message": "Wiki Pro API Server is Running!"}

if __name__ == "__main__":
    import uvicorn
    # 从 settings 读取配置，如果没引入 settings 就写死 0.0.0.0
    uvicorn.run(app, host="0.0.0.0", port=8000)
