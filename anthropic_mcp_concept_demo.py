#!/usr/bin/env python3
"""
Anthropic 공식 MCP 개념 설명 데모
https://www.anthropic.com/engineering/code-execution-with-mcp

이 코드는 Anthropic이 설명하는 MCP의 핵심 개념을 실제로 보여줍니다:
1. 점진적 공개 (Progressive Disclosure)
2. 상태 저장 (State Persistence) 
3. 컨텍스트 효율성 (Context Efficiency)
"""

import asyncio
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

class AnthropicMCPConceptDemo:
    """Anthropic MCP 개념 실제 데모"""
    
    def __init__(self, work_dir: str):
        self.work_dir = Path(work_dir)
        self.state_cache = {}  # MCP의 핵심: 상태 저장
        self.execution_history = []  # 실행 기록
        
    async def demonstrate_progressive_disclosure(self):
        """1. 점진적 공개 (Progressive Disclosure) 데모"""
        print("🎯 1. 점진적 공개 (Progressive Disclosure)")
        print("=" * 60)
        print("MCP의 핵심: 필요할 때만 도구를 호출하여 토큰 절약")
        print()
        
        # 시나리오: 사용자가 문서를 찾고 싶어함
        user_query = "AI 기술 관련 문서 찾아줘"
        
        # ❌ 기존 방식: 전체 문서를 한 번에 로드
        print("❌ 기존 방식 (비효율적):")
        all_files = list(self.work_dir.glob("*.txt"))
        total_content = ""
        for file_path in all_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                total_content += f"\n\n=== {file_path.name} ===\n{content}"
        
        print(f"   📊 전체 {len(all_files)}개 파일 로드")
        print(f"   📏 총 {len(total_content):,} 자")
        print(f"   💰 토큰 사용량: ~{len(total_content) // 4:,} 토큰 (1토큰=4자)")
        print()
        
        # ✅ MCP 방식: 점진적으로 필요한 것만 요청
        print("✅ MCP 방식 (효율적):")
        
        # 1단계: 도구 목록만 먼저 확인
        tools_response = await self._get_tools_list()
        print(f"   🔧 사용 가능한 도구: {len(tools_response['tools'])}개")
        print(f"   💰 토큰 사용량: ~{len(json.dumps(tools_response)) // 4} 토큰")
        print()
        
        # 2단계: 실제로 필요한 도구만 호출
        search_response = await self._call_tool("search_files", {
            "query": "AI 기술",
            "max_results": 3
        })
        print(f"   🔍 검색 결과: {search_response['summary']}")
        print(f"   💰 토큰 사용량: ~{len(json.dumps(search_response)) // 4} 토큰")
        print()
        
        # 3단계: 결과 분석
        read_response = None  # 변수 초기화
        if search_response.get("results"):
            first_file = search_response["results"][0]
            read_response = await self._call_tool("read_file", {
                "path": first_file["name"]
            })
            print(f"   📖 파일 읽기: {first_file['name']}")
            print(f"   💰 토큰 사용량: ~{len(json.dumps(read_response)) // 4} 토큰")
        
        print("\n📊 효율성 비교:")
        print(f"   기존 방식: ~{len(total_content) // 4:,} 토큰")
        
        # read_response가 None인 경우 처리
        read_tokens = len(json.dumps(read_response)) // 4 if read_response else 0
        mcp_tokens = (len(json.dumps(tools_response)) + len(json.dumps(search_response)) + read_tokens) // 4
        print(f"   MCP 방식: ~{mcp_tokens:,} 토큰")
        print(f"   🎉 토큰 절약: {((len(total_content) // 4) - mcp_tokens) / (len(total_content) // 4) * 100:.1f}%")
        
    async def demonstrate_state_persistence(self):
        """2. 상태 저장 (State Persistence) 데모"""
        print("\n🔄 2. 상태 저장 (State Persistence)")
        print("=" * 60)
        print("MCP의 핵심: 이전 실행 결과를 저장하여 재사용")
        print()
        
        # 첫 번째 요청
        print("🔍 첫 번째 요청:")
        start_time = time.time()
        result1 = await self._call_tool_with_cache("search_files", {
            "query": "머신러닝",
            "max_results": 5
        })
        first_time = time.time() - start_time
        print(f"   ⏱️  실행 시간: {first_time:.3f}초")
        print(f"   📊 결과: {result1['summary']}")
        print(f"   💾 상태 저장: {len(self.state_cache)}개 항목")
        print()
        
        # 두 번째 동일 요청 (캐시 히트)
        print("🔄 두 번째 동일 요청 (캐시 테스트):")
        start_time = time.time()
        result2 = await self._call_tool_with_cache("search_files", {
            "query": "머신러닝", 
            "max_results": 5
        })
        second_time = time.time() - start_time
        print(f"   ⚡ 실행 시간: {second_time:.3f}초")
        print(f"   📊 결과: {result2['summary']}")
        print(f"   🎯 캐시 히트: 동일 결과 반환")
        print()
        
        print("📈 성능 향상:")
        print(f"   속도 향상: {(first_time / second_time):.1f}배 빠름")
        print(f"   처리량 절약: 100% (데이터베이스 조회 불필요)")
        
    async def demonstrate_context_efficiency(self):
        """3. 컨텍스트 효율성 (Context Efficiency) 데모"""
        print("\n🎯 3. 컨텍스트 효율성 (Context Efficiency)")
        print("=" * 60)
        print("MCP의 핵심: 필터링된 데이터만 컨텍스트에 포함")
        print()
        
        # 대용량 데이터 시뮬레이션
        large_dataset = []
        for i in range(100):  # 100개의 대용량 문서
            doc = {
                "id": f"doc_{i:03d}",
                "title": f"기술 문서 {i}",
                "content": f"이것은 {i}번째 기술 문서입니다. " + "A" * 1000,
                "category": ["AI", "ML", "DL", "NLP", "CV"][i % 5],
                "size": 1000 + i * 10
            }
            large_dataset.append(doc)
        
        print(f"📚 대용량 데이터셋: {len(large_dataset)}개 문서")
        print(f"   📏 총 크기: {sum(doc['size'] for doc in large_dataset):,} 바이트")
        print()
        
        # ❌ 기존 방식: 전체 데이터를 컨텍스트에 포함
        print("❌ 기존 방식:")
        context_size_old = len(json.dumps(large_dataset))
        print(f"   📏 컨텍스트 크기: {context_size_old:,} 자")
        print(f"   💰 토큰 사용량: ~{context_size_old // 4:,} 토큰")
        print(f"   ⚠️  문제: 컨텍스트 윈도우 초과 가능성")
        print()
        
        # ✅ MCP 방식: 필터링 후 관련 데이터만 포함
        print("✅ MCP 방식:")
        
        # 1단계: 메타데이터만 먼저 조회
        metadata_response = await self._call_tool("get_metadata", {
            "category": "AI",
            "limit": 10
        })
        
        # 2단계: 관련 문서 ID만 확보
        if metadata_response.get("document_ids"):
            doc_ids = metadata_response["document_ids"]
            filtered_response = await self._call_tool("get_documents", {
                "document_ids": doc_ids,
                "fields": ["title", "summary"]  # 필요한 필드만
            })
            
            context_size_new = len(json.dumps(filtered_response))
            print(f"   📏 컨텍스트 크기: {context_size_new:,} 자")
            print(f"   💰 토큰 사용량: ~{context_size_new // 4:,} 토큰")
            print(f"   🎯 필터링: {len(doc_ids)}개 문서만 선택")
            print()
            
            print("📊 효율성 비교:")
            reduction = ((context_size_old - context_size_new) / context_size_old) * 100
            print(f"   컨텍스트 감소: {reduction:.1f}%")
            print(f"   토큰 절약: {(context_size_old // 4) - (context_size_new // 4):,} 토큰")
            print(f"   🎯 목표 달성: 관련 정보만 정확히 전달")
        
    async def _get_tools_list(self) -> Dict[str, Any]:
        """도구 목록 조회 (MCP 표준)"""
        return {
            "tools": [
                {
                    "name": "search_files",
                    "description": "파일 검색",
                    "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}}
                },
                {
                    "name": "read_file", 
                    "description": "파일 읽기",
                    "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}}
                },
                {
                    "name": "get_metadata",
                    "description": "문서 메타데이터 조회",
                    "inputSchema": {"type": "object", "properties": {"category": {"type": "string"}}}
                },
                {
                    "name": "get_documents",
                    "description": "특정 문서 조회",
                    "inputSchema": {"type": "object", "properties": {"document_ids": {"type": "array"}}}
                }
            ]
        }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """도구 호출 시뮬레이션"""
        print(f"   🔧 도구 호출: {tool_name}")
        print(f"   📥 파라미터: {arguments}")
        
        if tool_name == "search_files":
            # 실제 파일 검색
            results = []
            query = arguments.get("query", "").lower()
            max_results = arguments.get("max_results", 10)
            
            for file_path in self.work_dir.glob("*.txt"):
                if query in file_path.name.lower():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        results.append({
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": len(content),
                            "preview": content[:100] + "..." if len(content) > 100 else content
                        })
                        if len(results) >= max_results:
                            break
            
            return {
                "summary": f"Found {len(results)} files matching '{query}'",
                "results": results
            }
            
        elif tool_name == "read_file":
            path = self.work_dir / arguments["path"]
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "path": arguments["path"],
                "content": content,
                "size": len(content)
            }
            
        elif tool_name == "get_metadata":
            # 메타데이터 시뮬레이션
            category = arguments.get("category", "")
            return {
                "document_ids": [f"doc_{i:03d}" for i in range(10)],
                "category": category,
                "total_count": 100
            }
            
        elif tool_name == "get_documents":
            # 필터링된 문서 시뮬레이션
            doc_ids = arguments.get("document_ids", [])
            fields = arguments.get("fields", ["title", "summary"])
            
            documents = []
            for doc_id in doc_ids:
                doc_data = {field: f"{doc_id}_{field}" for field in fields}
                documents.append(doc_data)
                
            return {
                "documents": documents,
                "fields": fields,
                "count": len(documents)
            }
        
        return {"error": f"Unknown tool: {tool_name}"}
    
    async def _call_tool_with_cache(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """캐시를 포함한 도구 호출"""
        # 캐시 키 생성
        cache_key = f"{tool_name}_{hashlib.md5(json.dumps(arguments, sort_keys=True).encode()).hexdigest()}"
        
        # 캐시 확인
        if cache_key in self.state_cache:
            cached_entry = self.state_cache[cache_key]
            if time.time() - cached_entry["timestamp"] < 300:  # 5분 TTL
                print(f"   🎯 캐시 히트: {tool_name}")
                cached_entry["hit_count"] += 1
                return cached_entry["result"]
        
        # 캐시 미스 - 실제 실행
        print(f"   🔍 캐시 미스: {tool_name} 실행")
        result = await self._call_tool(tool_name, arguments)
        
        # 결과 저장
        self.state_cache[cache_key] = {
            "result": result,
            "timestamp": time.time(),
            "hit_count": 0,
            "tool_name": tool_name,
            "arguments": arguments
        }
        
        return result


async def main():
    """Anthropic MCP 개념 데모 실행"""
    print("🤖 Anthropic 공식 MCP 개념 데모")
    print("https://www.anthropic.com/engineering/code-execution-with-mcp")
    print("=" * 80)
    
    demo = AnthropicMCPConceptDemo("mcp_workspace")
    
    try:
        # 1. 점진적 공개 데모
        await demo.demonstrate_progressive_disclosure()
        
        # 2. 상태 저장 데모
        await demo.demonstrate_state_persistence()
        
        # 3. 컨텍스트 효율성 데모
        await demo.demonstrate_context_efficiency()
        
        print("\n🎉 Anthropic MCP 개념 데모 완료!")
        print("=" * 60)
        print("💡 MCP의 핵심 가치:")
        print("   1. 점진적 공개: 필요할 때만 도구 호출")
        print("   2. 상태 저장: 이전 결과 재사용")
        print("   3. 컨텍스트 효율성: 필터링된 데이터만 처리")
        print("   4. 실제 상호작용: 파일 시스템과 직접 통신")
        print("   5. 토큰 효율성: 90% 이상 절약 가능")
        
    except Exception as e:
        print(f"❌ 데모 실행 중 오류: {e}")


if __name__ == "__main__":
    print("🚀 Anthropic MCP 개념 실제 데모")
    print("이것은 Anthropic이 설명하는 MCP의 핵심 원리를 보여줍니다!")
    print()
    
    asyncio.run(main())
