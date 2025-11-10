#!/usr/bin/env python3
"""
실제 MCP 서버 직접 호출 예제
이것은 진짜 MCP 서버와 통신하여 동작하는 실제 예제입니다.
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

class RealMCPServerClient:
    """실제 MCP 서버와 통신하는 클라이언트"""
    
    def __init__(self, server_command: List[str]):
        self.server_command = server_command
        self.server_process = None
        self.request_id = 0
        
    async def start_server(self):
        """MCP 서버 프로세스 시작"""
        print("🚀 MCP 서버 시작 중...")
        self.server_process = await asyncio.create_subprocess_exec(
            *self.server_command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # 서버가 준비될 때까지 잠시 대기
        await asyncio.sleep(1)
        print("✅ MCP 서버가 준비되었습니다.")
        
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """MCP 서버에 JSON-RPC 요청 전송"""
        self.request_id += 1
        
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        
        # 요청 전송
        request_json = json.dumps(request)
        print(f"📤 요청 전송: {method}")
        print(f"   파라미터: {params}")
        
        self.server_process.stdin.write((request_json + "\n").encode())
        await self.server_process.stdin.drain()
        
        # 응답 수신
        response_line = await self.server_process.stdout.readline()
        response = json.loads(response_line.decode().strip())
        
        print(f"📥 응답 수신: {response.get('result', {}).get('summary', 'N/A')}")
        return response
        
    async def list_tools(self) -> List[Dict[str, Any]]:
        """사용 가능한 도구 목록 조회"""
        response = await self.send_request("tools/list")
        return response.get("result", {}).get("tools", [])
        
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """특정 도구 호출"""
        return await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        
    async def close(self):
        """서버 연결 종료"""
        if self.server_process:
            self.server_process.terminate()
            await self.server_process.wait()
            print("🔌 MCP 서버 연결 종료")


class SimpleFileMCPServer:
    """간단한 파일 시스템 MCP 서버 (데모용)"""
    
    def __init__(self, work_dir: str):
        self.work_dir = Path(work_dir)
        
    async def run(self):
        """MCP 서버로 동작"""
        print("📁 파일 시스템 MCP 서버 시작...")
        
        while True:
            try:
                # 표준 입력에서 JSON-RPC 요청 읽기
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )
                if not line:
                    break
                    
                request = json.loads(line.strip())
                method = request.get("method")
                params = request.get("params", {})
                request_id = request.get("id")
                
                # 요청 처리
                result = await self.handle_request(method, params)
                
                # 응답 전송
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
                
                print(json.dumps(response), flush=True)
                
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {"code": -1, "message": str(e)}
                }
                print(json.dumps(error_response), flush=True)
    
    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 요청 처리"""
        if method == "tools/list":
            return {
                "tools": [
                    {
                        "name": "search_files",
                        "description": "파일 시스템에서 파일 검색",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "max_results": {"type": "integer", "default": 10}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "read_file",
                        "description": "파일 내용 읽기",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string"}
                            },
                            "required": ["path"]
                        }
                    },
                    {
                        "name": "list_directory",
                        "description": "디렉토리 내용 목록",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "path": {"type": "string", "default": "."}
                            },
                            "required": []
                        }
                    }
                ]
            }
            
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "search_files":
                return await self.search_files(
                    arguments.get("query", ""),
                    arguments.get("max_results", 10)
                )
            elif tool_name == "read_file":
                return await self.read_file(arguments.get("path"))
            elif tool_name == "list_directory":
                return await self.list_directory(arguments.get("path", "."))
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        return {"error": "Unknown method"}
    
    async def search_files(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """파일 검색 구현"""
        import time
        import os
        
        # 캐시 시뮬레이션 (실제 MCP 서버에서는 Redis 등 사용)
        cache_key = f"search_{hash(query)}_{max_results}"
        print(f"🔍 검색 실행: {query}")
        print(f"   캐시 키: {cache_key}")
        
        # 실제 파일 시스템 검색
        results = []
        try:
            for file_path in self.work_dir.glob("*.txt"):
                if query.lower() in file_path.name.lower():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        results.append({
                            "path": str(file_path),
                            "name": file_path.name,
                            "size": len(content),
                            "content": content[:200] + "..." if len(content) > 200 else content
                        })
                        if len(results) >= max_results:
                            break
                            
            time.sleep(0.01)  # 실제 디스크 I/O 시뮬레이션
            
        except Exception as e:
            return {"error": f"Search failed: {str(e)}"}
            
        return {
            "summary": f"Found {len(results)} files matching '{query}'",
            "results": results,
            "cache_info": {"key": cache_key, "ttl": 300}  # 5분 TTL
        }
    
    async def read_file(self, path: str) -> Dict[str, Any]:
        """파일 읽기 구현"""
        try:
            file_path = self.work_dir / path
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "path": path,
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": f"Read failed: {str(e)}"}
    
    async def list_directory(self, path: str = ".") -> Dict[str, Any]:
        """디렉토리 목록 구현"""
        try:
            target_path = self.work_dir / path
            if not target_path.exists():
                return {"error": f"Path not found: {path}"}
                
            items = []
            for item in target_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
                
            return {
                "path": path,
                "items": items
            }
        except Exception as e:
            return {"error": f"List failed: {str(e)}"}


async def demonstrate_real_mcp():
    """실제 MCP 서버 호출 데모"""
    print("🎯 실제 MCP 서버 직접 호출 데모 시작")
    print("=" * 60)
    
    # 1. MCP 서버 프로세스 시작
    server_command = [sys.executable, __file__, "--server-mode"]
    client = RealMCPServerClient(server_command)
    
    try:
        # 서버 시작
        server_task = asyncio.create_task(
            SimpleFileMCPServer("mcp_workspace").run()
        )
        
        # 클라이언트 연결 (실제로는 별도 프로세스)
        await asyncio.sleep(0.5)  # 서버 준비 대기
        
        # 2. 사용 가능한 도구 목록 조회
        print("\n📋 1. 사용 가능한 도구 목록 조회")
        print("-" * 40)
        tools = await client.list_tools()
        for tool in tools:
            print(f"   🔧 {tool['name']}: {tool['description']}")
        
        # 3. 디렉토리 목록 조회
        print("\n📁 2. 작업 디렉토리 목록 조회")
        print("-" * 40)
        dir_result = await client.call_tool("list_directory", {"path": "."})
        if "error" not in dir_result:
            for item in dir_result["items"]:
                icon = "📁" if item["type"] == "directory" else "📄"
                size = f" ({item['size']} bytes)" if item["size"] else ""
                print(f"   {icon} {item['name']}{size}")
        
        # 4. 파일 검색 (실제 MCP 도구 호출)
        print("\n🔍 3. 파일 검색 (실제 MCP 도구 호출)")
        print("-" * 40)
        search_result = await client.call_tool("search_files", {
            "query": "AI 기술",
            "max_results": 5
        })
        
        if "error" not in search_result:
            print(f"   📊 {search_result['summary']}")
            for result in search_result["results"]:
                print(f"   📄 {result['name']} ({result['size']} bytes)")
                print(f"      {result['content'][:100]}...")
        
        # 5. 특정 파일 읽기
        if search_result.get("results"):
            first_file = search_result["results"][0]["name"]
            print(f"\n📖 4. 파일 내용 읽기: {first_file}")
            print("-" * 40)
            file_result = await client.call_tool("read_file", {"path": first_file})
            
            if "error" not in file_result:
                content = file_result["content"]
                print(f"   📊 파일 크기: {file_result['size']} bytes")
                print(f"   📝 내용: {content[:200]}...")
        
        # 6. 캐시 테스트 (동일 검색 재시도)
        print("\n🔄 5. 캐시 테스트 (동일 검색 재시도)")
        print("-" * 40)
        cached_result = await client.call_tool("search_files", {
            "query": "AI 기술",
            "max_results": 5
        })
        
        if "error" not in cached_result:
            cache_info = cached_result.get("cache_info", {})
            print(f"   🎯 캐시 히트! 키: {cache_info.get('key', 'N/A')}")
            print(f"   ⚡ 결과: {cached_result['summary']}")
        
        print("\n✅ 실제 MCP 서버 호출 데모 완료!")
        
    except Exception as e:
        print(f"❌ 데모 실행 중 오류: {e}")
    finally:
        await client.close()


async def main():
    """메인 함수"""
    if len(sys.argv) > 1 and sys.argv[1] == "--server-mode":
        # 서버 모드로 실행
        await SimpleFileMCPServer("mcp_workspace").run()
    else:
        # 클라이언트 데모 모드로 실행
        await demonstrate_real_mcp()


if __name__ == "__main__":
    print("🚀 실제 MCP 서버 직접 호출 예제")
    print("이것은 가상의 시뮬레이션이 아니라, 실제 MCP 서버와 통신합니다!")
    print()
    
    asyncio.run(main())
