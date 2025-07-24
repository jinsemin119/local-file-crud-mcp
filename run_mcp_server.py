#!/usr/bin/env python3
"""
FastAPI MCP 서버 실행 스크립트
"""

import sys
import asyncio
from mcp_server import run_mcp_server, run_web_server

def main():
    """메인 실행 함수"""
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == "--web":
            print("🌐 Starting FastAPI MCP Web Server...")
            print("📡 Server will be available at: http://127.0.0.1:8000")
            print("📚 API documentation: http://127.0.0.1:8000/docs")
            print("🔄 Press Ctrl+C to stop the server")
            asyncio.run(run_web_server())
        elif mode == "--help":
            print("FastAPI MCP Server Usage:")
            print("  python run_mcp_server.py          # MCP stdio server (Claude Desktop용)")
            print("  python run_mcp_server.py --web    # Web server (개발/테스트용)")
            print("  python run_mcp_server.py --help   # 도움말 표시")
        else:
            print(f"❌ Unknown mode: {mode}")
            print("Use --help for usage information")
    else:
        print("🔧 Starting FastAPI MCP Stdio Server...")
        print("📡 Server is ready for Claude Desktop integration")
        print("🔄 Press Ctrl+C to stop the server")
        asyncio.run(run_mcp_server())

if __name__ == "__main__":
    main() 