#!/usr/bin/env python3
"""
FastAPI 웹 서버 테스트 스크립트
"""

import asyncio
import aiohttp
import json
from pathlib import Path

class WebAPITestClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def send_mcp_request(self, method: str, params: dict = None) -> dict:
        """MCP 요청을 웹 API로 전송"""
        request_data = {
            "jsonrpc": "2.0",
            "id": "test-1",
            "method": method,
            "params": params or {}
        }
        
        async with self.session.post(
            f"{self.base_url}/mcp/{method.replace('/', '/')}",
            json=request_data
        ) as response:
            return await response.json()
    
    async def test_initialize(self):
        """초기화 테스트"""
        print("🔧 Testing MCP initialization...")
        response = await self.send_mcp_request("initialize")
        print(f"✅ Initialize response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_list_tools(self):
        """도구 목록 테스트"""
        print("\n📋 Testing tools list...")
        response = await self.send_mcp_request("tools/list")
        print(f"✅ Tools list response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_write_file(self, filepath: str, content: str):
        """파일 쓰기 테스트"""
        print(f"\n✍️ Testing file write: {filepath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "write_file",
            "arguments": {
                "filepath": filepath,
                "content": content
            }
        })
        print(f"✅ Write file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_read_file(self, filepath: str):
        """파일 읽기 테스트"""
        print(f"\n📖 Testing file read: {filepath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "read_file",
            "arguments": {
                "filepath": filepath
            }
        })
        print(f"✅ Read file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_append_file(self, filepath: str, content: str):
        """파일 추가 테스트"""
        print(f"\n➕ Testing file append: {filepath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "append_file",
            "arguments": {
                "filepath": filepath,
                "content": content
            }
        })
        print(f"✅ Append file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_list_files(self, dirpath: str):
        """디렉토리 조회 테스트"""
        print(f"\n📁 Testing directory list: {dirpath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "list_files",
            "arguments": {
                "dirpath": dirpath
            }
        })
        print(f"✅ List files response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_create_directory(self, dirpath: str):
        """디렉토리 생성 테스트"""
        print(f"\n📂 Testing directory creation: {dirpath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "create_directory",
            "arguments": {
                "dirpath": dirpath
            }
        })
        print(f"✅ Create directory response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_update_file(self, filepath: str, find: str, replace: str):
        """파일 수정 테스트"""
        print(f"\n🔄 Testing file update: {filepath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "update_file",
            "arguments": {
                "filepath": filepath,
                "find": find,
                "replace": replace
            }
        })
        print(f"✅ Update file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_delete_file(self, filepath: str):
        """파일 삭제 테스트"""
        print(f"\n🗑️ Testing file deletion: {filepath}")
        response = await self.send_mcp_request("tools/call", {
            "name": "delete_file",
            "arguments": {
                "filepath": filepath
            }
        })
        print(f"✅ Delete file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response

async def run_web_api_test():
    """웹 API 종합 테스트 실행"""
    print("🚀 Starting FastAPI Web API Test")
    print("=" * 50)
    
    # 웹 서버 시작
    import subprocess
    import sys
    import time
    
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py", "--web"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # 서버 시작 대기
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    try:
        async with WebAPITestClient() as client:
            # 1. 초기화 테스트
            await client.test_initialize()
            
            # 2. 도구 목록 테스트
            await client.test_list_tools()
            
            # 3. 디렉토리 생성 테스트
            test_dir = "web_test_files"
            await client.test_create_directory(test_dir)
            
            # 4. 파일 쓰기 테스트
            test_file = f"{test_dir}/web_test.txt"
            test_content = "웹 API 테스트 파일입니다.\nThis is a web API test file."
            await client.test_write_file(test_file, test_content)
            
            # 5. 파일 읽기 테스트
            await client.test_read_file(test_file)
            
            # 6. 파일 추가 테스트
            append_content = "\n웹 API로 추가된 내용입니다.\nContent appended via web API."
            await client.test_append_file(test_file, append_content)
            
            # 7. 수정된 파일 읽기 테스트
            await client.test_read_file(test_file)
            
            # 8. 파일 수정 테스트
            await client.test_update_file(test_file, "웹 API", "Web API")
            
            # 9. 수정된 파일 읽기 테스트
            await client.test_read_file(test_file)
            
            # 10. 디렉토리 조회 테스트
            await client.test_list_files(test_dir)
            
            # 11. 파일 삭제 테스트
            await client.test_delete_file(test_file)
            
            # 12. 삭제 후 디렉토리 조회 테스트
            await client.test_list_files(test_dir)
            
            print("\n" + "=" * 50)
            print("✅ All web API tests completed successfully!")
    
    except Exception as e:
        print(f"\n❌ Web API test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 서버 프로세스 종료
        server_process.terminate()
        server_process.wait()
        print("🔚 Web server process terminated")

if __name__ == "__main__":
    asyncio.run(run_web_api_test()) 