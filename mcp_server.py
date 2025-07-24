#!/usr/bin/env python3
"""
FastAPI 기반 MCP (Model Context Protocol) 서버
로컬 파일 시스템 CRUD 작업을 지원합니다.
"""

import asyncio
import json
import sys
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import aiofiles

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MCP 메시지 모델들
class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    method: str
    params: Optional[Dict[str, Any]] = None

class MCPResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: Optional[Union[str, int]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    
    class Config:
        extra = "allow"

class MCPNotification(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None

# 파일 작업 모델들
class FileReadRequest(BaseModel):
    filepath: str = Field(..., description="읽을 파일의 경로")

class FileWriteRequest(BaseModel):
    filepath: str = Field(..., description="쓸 파일의 경로")
    content: str = Field(..., description="파일 내용")

class FileAppendRequest(BaseModel):
    filepath: str = Field(..., description="추가할 파일의 경로")
    content: str = Field(..., description="추가할 내용")

class FileUpdateRequest(BaseModel):
    filepath: str = Field(..., description="수정할 파일의 경로")
    find: str = Field(..., description="찾을 문자열")
    replace: str = Field(..., description="바꿀 문자열")

class FileDeleteRequest(BaseModel):
    filepath: str = Field(..., description="삭제할 파일의 경로")

class DirectoryListRequest(BaseModel):
    dirpath: str = Field(..., description="조회할 디렉토리 경로")

class DirectoryCreateRequest(BaseModel):
    dirpath: str = Field(..., description="생성할 디렉토리 경로")

class FileSystemResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class FileSystemItem(BaseModel):
    name: str
    type: str  # "file" or "directory"
    size: Optional[int] = None
    modified: Optional[str] = None

# MCP 서버 클래스
class MCPServer:
    def __init__(self):
        self.app = FastAPI(title="Local File CRUD MCP Server", version="1.0.0")
        self.setup_routes()
        
    def setup_routes(self):
        """FastAPI 라우트 설정"""
        
        @self.app.post("/mcp/initialize")
        async def initialize_mcp(request: MCPRequest):
            """MCP 초기화"""
            try:
                return MCPResponse(
                    id=request.id,
                    result={
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": True
                            }
                        },
                        "serverInfo": {
                            "name": "local-file-crud-mcp",
                            "version": "1.0.0"
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Initialize error: {e}")
                return MCPResponse(
                    id=request.id,
                    error={"code": -1, "message": str(e)}
                )

        @self.app.post("/mcp/tools/list")
        async def list_tools(request: MCPRequest):
            """사용 가능한 도구 목록 반환"""
            try:
                tools = [
                    {
                        "name": "read_file",
                        "description": "파일 내용을 읽어옵니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "읽을 파일의 경로"
                                }
                            },
                            "required": ["filepath"]
                        }
                    },
                    {
                        "name": "write_file",
                        "description": "파일에 내용을 씁니다 (덮어쓰기)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "쓸 파일의 경로"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "파일 내용"
                                }
                            },
                            "required": ["filepath", "content"]
                        }
                    },
                    {
                        "name": "append_file",
                        "description": "파일 끝에 내용을 추가합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "추가할 파일의 경로"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "추가할 내용"
                                }
                            },
                            "required": ["filepath", "content"]
                        }
                    },
                    {
                        "name": "update_file",
                        "description": "파일 내용을 찾아 바꿉니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "수정할 파일의 경로"
                                },
                                "find": {
                                    "type": "string",
                                    "description": "찾을 문자열"
                                },
                                "replace": {
                                    "type": "string",
                                    "description": "바꿀 문자열"
                                }
                            },
                            "required": ["filepath", "find", "replace"]
                        }
                    },
                    {
                        "name": "delete_file",
                        "description": "파일을 삭제합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "삭제할 파일의 경로"
                                }
                            },
                            "required": ["filepath"]
                        }
                    },
                    {
                        "name": "list_files",
                        "description": "디렉토리 내용을 조회합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dirpath": {
                                    "type": "string",
                                    "description": "조회할 디렉토리 경로"
                                }
                            },
                            "required": ["dirpath"]
                        }
                    },
                    {
                        "name": "create_directory",
                        "description": "새 디렉토리를 생성합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dirpath": {
                                    "type": "string",
                                    "description": "생성할 디렉토리 경로"
                                }
                            },
                            "required": ["dirpath"]
                        }
                    }
                ]
                
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    result={"tools": tools}
                )
            except Exception as e:
                logger.error(f"List tools error: {e}")
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    error={"code": -1, "message": str(e)}
                )

        @self.app.post("/mcp/tools/call")
        async def call_tool(request: MCPRequest):
            """도구 호출"""
            try:
                if not request.params or "name" not in request.params:
                    raise ValueError("Tool name is required")
                
                tool_name = request.params["name"]
                arguments = request.params.get("arguments", {})
                
                # 도구별 처리
                if tool_name == "read_file":
                    result = await self.read_file(arguments.get("filepath"))
                elif tool_name == "write_file":
                    result = await self.write_file(
                        arguments.get("filepath"), 
                        arguments.get("content")
                    )
                elif tool_name == "append_file":
                    result = await self.append_file(
                        arguments.get("filepath"), 
                        arguments.get("content")
                    )
                elif tool_name == "update_file":
                    result = await self.update_file(
                        arguments.get("filepath"),
                        arguments.get("find"),
                        arguments.get("replace")
                    )
                elif tool_name == "delete_file":
                    result = await self.delete_file(arguments.get("filepath"))
                elif tool_name == "list_files":
                    result = await self.list_files(arguments.get("dirpath"))
                elif tool_name == "create_directory":
                    result = await self.create_directory(arguments.get("dirpath"))
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    result={"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
                )
                
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    error={"code": -1, "message": str(e)}
                )

    # 파일 시스템 작업 메서드들
    async def read_file(self, filepath: str) -> Dict[str, Any]:
        """파일 읽기"""
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            return {
                "success": True,
                "message": f"File read successfully: {filepath}",
                "data": {
                    "content": content,
                    "size": len(content),
                    "path": str(path.absolute())
                }
            }
        except Exception as e:
            logger.error(f"Read file error: {e}")
            return {
                "success": False,
                "message": f"Failed to read file: {str(e)}",
                "data": None
            }

    async def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """파일 쓰기 (덮어쓰기)"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "success": True,
                "message": f"File written successfully: {filepath}",
                "data": {
                    "path": str(path.absolute()),
                    "size": len(content)
                }
            }
        except Exception as e:
            logger.error(f"Write file error: {e}")
            return {
                "success": False,
                "message": f"Failed to write file: {str(e)}",
                "data": None
            }

    async def append_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """파일 끝에 내용 추가"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(path, 'a', encoding='utf-8') as f:
                await f.write(content)
            
            return {
                "success": True,
                "message": f"Content appended successfully: {filepath}",
                "data": {
                    "path": str(path.absolute()),
                    "appended_size": len(content)
                }
            }
        except Exception as e:
            logger.error(f"Append file error: {e}")
            return {
                "success": False,
                "message": f"Failed to append to file: {str(e)}",
                "data": None
            }

    async def update_file(self, filepath: str, find: str, replace: str) -> Dict[str, Any]:
        """파일 내용 찾아 바꾸기"""
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            async with aiofiles.open(path, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            original_content = content
            content = content.replace(find, replace)
            
            if content == original_content:
                return {
                    "success": True,
                    "message": f"No changes made: '{find}' not found in {filepath}",
                    "data": {"replacements": 0}
                }
            
            async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            replacements = original_content.count(find)
            
            return {
                "success": True,
                "message": f"File updated successfully: {filepath}",
                "data": {
                    "path": str(path.absolute()),
                    "replacements": replacements
                }
            }
        except Exception as e:
            logger.error(f"Update file error: {e}")
            return {
                "success": False,
                "message": f"Failed to update file: {str(e)}",
                "data": None
            }

    async def delete_file(self, filepath: str) -> Dict[str, Any]:
        """파일 삭제"""
        try:
            path = Path(filepath)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {filepath}")
            
            path.unlink()
            
            return {
                "success": True,
                "message": f"File deleted successfully: {filepath}",
                "data": {"path": str(path.absolute())}
            }
        except Exception as e:
            logger.error(f"Delete file error: {e}")
            return {
                "success": False,
                "message": f"Failed to delete file: {str(e)}",
                "data": None
            }

    async def list_files(self, dirpath: str) -> Dict[str, Any]:
        """디렉토리 내용 조회"""
        try:
            path = Path(dirpath)
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {dirpath}")
            
            if not path.is_dir():
                raise NotADirectoryError(f"Not a directory: {dirpath}")
            
            items = []
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": str(stat.st_mtime)
                    })
                except (PermissionError, OSError):
                    # 권한이 없거나 접근할 수 없는 파일은 건너뛰기
                    continue
            
            return {
                "success": True,
                "message": f"Directory listed successfully: {dirpath}",
                "data": {
                    "path": str(path.absolute()),
                    "items": items,
                    "count": len(items)
                }
            }
        except Exception as e:
            logger.error(f"List files error: {e}")
            return {
                "success": False,
                "message": f"Failed to list directory: {str(e)}",
                "data": None
            }

    async def create_directory(self, dirpath: str) -> Dict[str, Any]:
        """디렉토리 생성"""
        try:
            path = Path(dirpath)
            path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "message": f"Directory created successfully: {dirpath}",
                "data": {"path": str(path.absolute())}
            }
        except Exception as e:
            logger.error(f"Create directory error: {e}")
            return {
                "success": False,
                "message": f"Failed to create directory: {str(e)}",
                "data": None
            }

# MCP stdio 서버 (표준 입출력 기반)
class MCPStdioServer:
    def __init__(self):
        self.server = MCPServer()
        self.running = False
    
    async def handle_stdio(self):
        """표준 입출력을 통한 MCP 통신 처리"""
        self.running = True
        print("🔧 MCP Server started - waiting for requests...")
        print("=" * 50)
        
        while self.running:
            try:
                # 표준 입력에서 JSON-RPC 메시지 읽기
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                # JSON 파싱
                try:
                    request_data = json.loads(line)
                    request = MCPRequest(**request_data)
                    
                    # 요청 로그 출력
                    print(f"📥 MCP Request: {request.method} (ID: {request.id})")
                    if request.params:
                        print(f"   Params: {json.dumps(request.params, ensure_ascii=False, indent=2)}")
                    print("-" * 50)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    print(f"❌ JSON Decode Error: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Request parsing error: {e}")
                    print(f"❌ Request Parsing Error: {e}")
                    continue
                
                # 요청 처리
                response = await self.process_request(request)
                
                # 응답 로그 출력
                print(f"📤 MCP Response: {request.method} (ID: {request.id})")
                if hasattr(response, 'result') and response.result is not None:
                    print(f"   Result: {json.dumps(response.result, ensure_ascii=False, indent=2)}")
                elif hasattr(response, 'error') and response.error is not None:
                    print(f"   Error: {json.dumps(response.error, ensure_ascii=False, indent=2)}")
                print("=" * 50)
                
                # 응답 전송
                response_data = {
                    "jsonrpc": "2.0",
                    "id": request.id if request.id is not None else 0
                }
                
                if hasattr(response, 'result') and response.result is not None:
                    response_data["result"] = response.result
                elif hasattr(response, 'error') and response.error is not None:
                    response_data["error"] = response.error
                
                response_json = json.dumps(response_data, ensure_ascii=False)
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: sys.stdout.write(response_json + "\n")
                )
                await asyncio.get_event_loop().run_in_executor(None, sys.stdout.flush)
                
            except Exception as e:
                logger.error(f"Stdio handling error: {e}")
                print(f"❌ Stdio Handling Error: {e}")
                break
    
    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """요청 처리"""
        print(f"🔄 Processing request: {request.method}")
        try:
            if request.method == "initialize":
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    result={
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {
                                "listChanged": True
                            }
                        },
                        "serverInfo": {
                            "name": "local-file-crud-mcp",
                            "version": "1.0.0"
                        }
                    }
                )
            elif request.method == "tools/list":
                tools = [
                    {
                        "name": "read_file",
                        "description": "파일 내용을 읽어옵니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "읽을 파일의 경로"
                                }
                            },
                            "required": ["filepath"]
                        }
                    },
                    {
                        "name": "write_file",
                        "description": "파일에 내용을 씁니다 (덮어쓰기)",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "쓸 파일의 경로"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "파일 내용"
                                }
                            },
                            "required": ["filepath", "content"]
                        }
                    },
                    {
                        "name": "append_file",
                        "description": "파일 끝에 내용을 추가합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "추가할 파일의 경로"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "추가할 내용"
                                }
                            },
                            "required": ["filepath", "content"]
                        }
                    },
                    {
                        "name": "update_file",
                        "description": "파일 내용을 찾아 바꿉니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "수정할 파일의 경로"
                                },
                                "find": {
                                    "type": "string",
                                    "description": "찾을 문자열"
                                },
                                "replace": {
                                    "type": "string",
                                    "description": "바꿀 문자열"
                                }
                            },
                            "required": ["filepath", "find", "replace"]
                        }
                    },
                    {
                        "name": "delete_file",
                        "description": "파일을 삭제합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "filepath": {
                                    "type": "string",
                                    "description": "삭제할 파일의 경로"
                                }
                            },
                            "required": ["filepath"]
                        }
                    },
                    {
                        "name": "list_files",
                        "description": "디렉토리 내용을 조회합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dirpath": {
                                    "type": "string",
                                    "description": "조회할 디렉토리 경로"
                                }
                            },
                            "required": ["dirpath"]
                        }
                    },
                    {
                        "name": "create_directory",
                        "description": "새 디렉토리를 생성합니다",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "dirpath": {
                                    "type": "string",
                                    "description": "생성할 디렉토리 경로"
                                }
                            },
                            "required": ["dirpath"]
                        }
                    }
                ]
                
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    result={"tools": tools}
                )
            elif request.method == "tools/call":
                if not request.params or "name" not in request.params:
                    raise ValueError("Tool name is required")
                
                tool_name = request.params["name"]
                arguments = request.params.get("arguments", {})
                
                # 도구별 처리
                if tool_name == "read_file":
                    result = await self.server.read_file(arguments.get("filepath"))
                elif tool_name == "write_file":
                    result = await self.server.write_file(
                        arguments.get("filepath"), 
                        arguments.get("content")
                    )
                elif tool_name == "append_file":
                    result = await self.server.append_file(
                        arguments.get("filepath"), 
                        arguments.get("content")
                    )
                elif tool_name == "update_file":
                    result = await self.server.update_file(
                        arguments.get("filepath"),
                        arguments.get("find"),
                        arguments.get("replace")
                    )
                elif tool_name == "delete_file":
                    result = await self.server.delete_file(arguments.get("filepath"))
                elif tool_name == "list_files":
                    result = await self.server.list_files(arguments.get("dirpath"))
                elif tool_name == "create_directory":
                    result = await self.server.create_directory(arguments.get("dirpath"))
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    result={"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}
                )
            else:
                return MCPResponse(
                    id=request.id if request.id is not None else 0,
                    error={"code": -32601, "message": f"Method not found: {request.method}"}
                )
        except Exception as e:
            logger.error(f"Request processing error: {e}")
            print(f"❌ Request Processing Error: {e}")
            return MCPResponse(
                id=request.id if request.id is not None else 0,
                error={"code": -1, "message": str(e)}
            )

# 웹 서버 실행 (개발용)
async def run_web_server():
    """FastAPI 웹 서버 실행 (개발 및 테스트용)"""
    server = MCPServer()
    config = uvicorn.Config(
        server.app,
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )
    web_server = uvicorn.Server(config)
    await web_server.serve()

# MCP stdio 서버 실행 (프로덕션용)
async def run_mcp_server():
    """MCP stdio 서버 실행 (Claude Desktop 연동용)"""
    stdio_server = MCPStdioServer()
    await stdio_server.handle_stdio()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        # 웹 서버 모드 (개발용)
        asyncio.run(run_web_server())
    else:
        # MCP stdio 서버 모드 (프로덕션용)
        asyncio.run(run_mcp_server()) 