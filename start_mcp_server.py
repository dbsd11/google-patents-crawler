#!/usr/bin/env python3
"""
Google Patents Crawler MCP Server 启动脚本

基于 Starlette、uvicorn 和 MCP SSE 传输方式实现
"""

import argparse
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, WebSocket
from mcp.server.sse import SseServerTransport
from mcp.server.websocket import websocket_server

from logger import logger
from mcp_server import server, run_stdio

# SSE 传输实例
sse = SseServerTransport("/messages/")

async def handle_websocket(websocket: WebSocket):
    """处理 WebSocket 连接"""
    await websocket.accept()
    
    # 创建 ASGI scope, receive, send 函数
    scope = {
        "type": "websocket",
        "path": "/ws",
        "query_string": b"",
        "headers": [],
    }
    
    async def receive():
        """接收 WebSocket 消息"""
        message = await websocket.receive()
        if message["type"] == "websocket.receive":
            return {
                "type": "websocket.receive",
                "bytes": message.get("bytes"),
                "text": message.get("text"),
            }
        return message
    
    async def send(message):
        """发送 WebSocket 消息"""
        if message["type"] == "websocket.send":
            if "bytes" in message:
                await websocket.send_bytes(message["bytes"])
            elif "text" in message:
                await websocket.send_text(message["text"])
        elif message["type"] == "websocket.close":
            await websocket.close(code=message.get("code", 1000))
    
    # 使用 MCP WebSocket 服务器处理连接
    await websocket_server(scope, receive, send)

async def handle_sse(request: Request):
    """处理 SSE 连接"""
    async with sse.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as streams:
        await server.run(
            streams[0], streams[1], server.create_initialization_options()
        )

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="Google Patents Crawler MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "websocket"],
        default="stdio",
        help="传输方式 (默认: stdio)"
    )
    parser.add_argument(
        "--host",
        default="localhost",
        help="SSE 服务器主机 (默认: localhost)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="SSE 服务器端口 (默认: 8000)"
    )
    
    args = parser.parse_args()
    
    if args.transport == "stdio":
        logger.info("启动 stdio 传输...")
        asyncio.run(run_stdio())
    elif args.transport == "websocket":
        logger.info(f"启动 WebSocket 传输在 {args.host}:{args.port}...")
        import uvicorn

        # FastAPI 应用
        app = FastAPI(title="Google Patents Crawler MCP Server", debug=True)

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket 端点"""
            await handle_websocket(websocket)

        uvicorn.run(app, host=args.host, port=args.port)
    else:  # SSE
        logger.info(f"启动 SSE 传输在 {args.host}:{args.port}...")
        import uvicorn

        # FastAPI 应用
        app = FastAPI(title="Google Patents Crawler MCP Server", debug=True)

        @app.get("/")
        async def health_check():
            """健康检查端点，用于心跳检查"""
            return {"status": "ok", "service": "Google Patents Crawler MCP Server", "transport": "sse"}

        @app.get("/sse")
        async def sse_endpoint(request: Request):
            """SSE 端点"""
            return await handle_sse(request)

        # 挂载 SSE 消息处理
        app.mount("/messages/", sse.handle_post_message)
        uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()