#!/usr/bin/env python3
"""
FastAPI MCP 서버 테스트 스크립트
"""

import asyncio
import json
import sys
from pathlib import Path

# 테스트용 MCP 클라이언트 클래스
class MCPTestClient:
    def __init__(self, server_process):
        self.server_process = server_process
        self.request_id = 1
    
    async def send_request(self, method: str, params: dict = None) -> dict:
        """MCP 요청 전송"""
        request = {
            "jsonrpc": "2.0",
            "id": str(self.request_id),
            "method": method,
            "params": params or {}
        }
        
        # 서버에 요청 전송
        request_json = json.dumps(request) + "\n"
        self.server_process.stdin.write(request_json)
        self.server_process.stdin.flush()
        
        # 응답 읽기
        response_line = self.server_process.stdout.readline().strip()
        response = json.loads(response_line)
        
        self.request_id += 1
        return response
    
    async def test_initialize(self):
        """초기화 테스트"""
        print("🔧 Testing MCP initialization...")
        response = await self.send_request("initialize")
        print(f"✅ Initialize response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_list_tools(self):
        """도구 목록 테스트"""
        print("\n📋 Testing tools list...")
        response = await self.send_request("tools/list")
        print(f"✅ Tools list response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response
    
    async def test_write_file(self, filepath: str, content: str):
        """파일 쓰기 테스트"""
        print(f"\n✍️ Testing file write: {filepath}")
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
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
        response = await self.send_request("tools/call", {
            "name": "delete_file",
            "arguments": {
                "filepath": filepath
            }
        })
        print(f"✅ Delete file response: {json.dumps(response, indent=2, ensure_ascii=False)}")
        return response

async def run_comprehensive_test():
    """종합 테스트 실행"""
    print("🚀 Starting FastAPI MCP Server Test")
    print("=" * 50)
    
    # MCP 서버 프로세스 시작
    import subprocess
    server_process = subprocess.Popen(
        [sys.executable, "mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    try:
        # 테스트 클라이언트 생성
        client = MCPTestClient(server_process)
        
        # 1. 초기화 테스트
        await client.test_initialize()
        
        # 2. 도구 목록 테스트
        await client.test_list_tools()
        
        # 3. 디렉토리 생성 테스트
        test_dir = "test_files"
        await client.test_create_directory(test_dir)
        
        # 4. 파일 쓰기 테스트
        test_file = f"{test_dir}/test.txt"
        test_content = "안녕하세요! 이것은 테스트 파일입니다.\nHello! This is a test file."
        await client.test_write_file(test_file, test_content)
        
        # 5. 파일 읽기 테스트
        await client.test_read_file(test_file)
        
        # 6. 파일 추가 테스트
        append_content = "\n이것은 추가된 내용입니다.\nThis is appended content."
        await client.test_append_file(test_file, append_content)
        
        # 7. 수정된 파일 읽기 테스트
        await client.test_read_file(test_file)
        
        # 8. 파일 수정 테스트
        await client.test_update_file(test_file, "테스트", "TEST")
        
        # 9. 수정된 파일 읽기 테스트
        await client.test_read_file(test_file)
        
        # 10. 디렉토리 조회 테스트
        await client.test_list_files(test_dir)
        
        # 11. 파일 삭제 테스트
        await client.test_delete_file(test_file)
        
        # 12. 삭제 후 디렉토리 조회 테스트
        await client.test_list_files(test_dir)
        
        print("\n" + "=" * 50)
        print("✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 서버 프로세스 종료
        server_process.terminate()
        server_process.wait()
        print("🔚 MCP server process terminated")

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test()) 