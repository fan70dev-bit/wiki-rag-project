from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import search

app = FastAPI(title="Wiki Pro RAG 后端系统")

# 跨域配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载路由
app.include_router(search.router)

@app.get("/")
async def root():
    return {"message": "Wiki Pro API Server is Running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
