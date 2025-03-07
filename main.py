from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from openai import OpenAI
import os
app = FastAPI()

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=os.getenv("DS_KEY"),
    base_url="https://api.deepseek.com/v1",
)

def generate_stream(prompt: str):
    """流式生成器函数"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=True,
            temperature=0.7,
        )
        
        # 逐块返回数据
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield f"data: {content}\n\n"
                
    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/post")
def read_root(request: Request):
    data = request.json()
    return {data: request}

@app.post("/stream_chat")
async def stream_chat(request: Request):
    """流式对话接口"""
    data = await request.json()
    prompt = data.get("content", "")
    
    return StreamingResponse(
        generate_stream(prompt),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
    

#     # 服务启动配置（开发环境使用）
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",  # 允许外部访问
        port=8100,
        reload=True,     # 开发时自动重载
        workers=1,       # 生产环境建议增加
        access_log=False # 生产环境可关闭访问日志
    )