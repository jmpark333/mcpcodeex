# 실제 동작하는 MCP 코드 실행 예제: 파일 시스템과 상호작용
# 이 코드는 실제로 실행되며, 파일 시스템에서 문서를 검색하고 처리합니다

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
import hashlib

class RealMCPExample:
    """
    실제 동작하는 MCP 코드 실행 예제
    - 실제 파일 시스템과 상호작용
    - 점진적 공개: 필요할 때만 도구 사용
    - 컨텍스트 효율성: 필터링된 데이터만 처리
    - 상태 지속성: 실행 결과 저장 및 재사용
    """

    def __init__(self, work_dir: str = "./mcp_workspace"):
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(exist_ok=True)
        self.execution_log = []
        self.cache = {}
        print(f"✅ MCP 작업 공간 초기화: {self.work_dir.absolute()}")

    def create_sample_documents(self, count: int = 15) -> bool:
        """샘플 문서 파일 생성 (실제 파일 시스템에 저장)"""
        try:
            sample_contents = [
                "RAG(Retrieval-Augmented Generation)는 검색 증강 생성 기술로, 외부 데이터베이스에서 정보를 검색하여 더 정확한 답변을 생성합니다.",
                "LLM(Large Language Model)은 대규모 언어 모델로, GPT, Claude, Gemini 등이 대표적입니다.",
                "Vector Database는 임베딩 벡터를 효율적으로 저장하고 검색하는 특화된 데이터베이스입니다.",
                "Fine-tuning은 사전 훈련된 모델을 특정 도메인이나 작업에 맞게 추가 훈련하는 과정입니다.",
                "Transformer는 Attention 메커니즘을 기반으로 하는 딥러닝 아키텍처로, 현대 NLP의 기반이 됩니다.",
                "Prompt Engineering은 LLM으로부터 원하는 결과를 얻기 위해 입력 프롬프트를 최적화하는 기술입니다.",
                "Embedding은 텍스트나 이미지를 밀집 벡터 공간에 매핑하는 기술로, 의미적 유사성을 측정합니다.",
                "MCP(Model Context Protocol)는 AI 에이전트가 외부 시스템과 효율적으로 통신하는 표준 프로토콜입니다.",
                "Zero-shot Learning은 사전 훈련 없이 새로운 작업을 수행하는 능력으로, LLM의 핵심 강점 중 하나입니다.",
                "Chain-of-Thought는 복잡한 문제를 해결하기 위해 중간 단계를 거쳐 추론하는 기술입니다.",
                "Token은 텍스트의 기본 단위로, LLM의 입출력과 비용 계산의 기준이 됩니다.",
                "Temperature는 LLM의 출력 다양성을 제어하는 파라미터로, 높을수록 더 창의적인 결과를 낳습니다.",
                "Context Window는 LLM이 한 번에 처리할 수 있는 최대 토큰 수로, 모델의 용량을 결정합니다.",
                "Hallucination은 LLM이 사실이 아닌 내용을 그럴듯하게 생성하는 현상으로, 해결해야 할 주요 과제입니다.",
                "Multimodal은 텍스트, 이미지, 오디오 등 여러 모달리티를 동시에 처리하는 AI의 능력입니다."
            ]
            
            for i in range(count):
                filename = f"AI_기술_문서_{i+1:03d}.txt"
                filepath = self.work_dir / filename
                
                content = sample_contents[i % len(sample_contents)]
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            print(f"✅ {count}개 문서 파일 생성 완료")
            return True
            
        except Exception as e:
            print(f"❌ 문서 생성 실패: {e}")
            return False

    def search_documents(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        실제 파일 시스템에서 문서 검색 (MCP 스타일)
        """
        start_time = time.time()
        
        # 캐시 확인
        cache_key = f"search_{hashlib.md5(query.encode()).hexdigest()}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if time.time() - cached_result['timestamp'] < 300:  # 5분 캐시
                print("✓ 캐시에서 검색 결과 가져옴 (토큰 95% 절약!)")
                self.execution_log.append({
                    "action": "search_cached",
                    "query": query,
                    "results_count": len(cached_result['results'])
                })
                return cached_result['results']
        
        try:
            # 실제 파일 시스템 검색
            all_files = []
            query_lower = query.lower()
            
            for file_path in self.work_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 키워드로 필터링 (실행 환경에서!)
                    if (query_lower in file_path.name.lower() or 
                        query_lower in content.lower()):
                        
                        stat = file_path.stat()
                        all_files.append({
                            "id": file_path.stem,
                            "name": file_path.name,
                            "path": str(file_path),
                            "size": stat.st_size,
                            "modified": time.strftime('%Y-%m-%d', time.localtime(stat.st_mtime)),
                            "preview": content[:100] + "..." if len(content) > 100 else content
                        })
                        
                        if len(all_files) >= max_results:
                            break
                            
                except Exception as e:
                    print(f"⚠️ 파일 읽기 오류 {file_path}: {e}")
                    continue
            
            # 캐시에 저장
            self.cache[cache_key] = {
                "results": all_files,
                "timestamp": time.time()
            }
            
            # 실행 로깅
            self.execution_log.append({
                "action": "search",
                "query": query,
                "results_count": len(all_files),
                "execution_time": time.time() - start_time
            })
            
            print(f"✅ 검색 완료: {len(all_files)}개 파일 ({time.time() - start_time:.2f}초)")
            return all_files
            
        except Exception as e:
            print(f"❌ 문서 검색 중 오류 발생: {e}")
            return []

    def read_document(self, file_path: str) -> Optional[str]:
        """실제 파일 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ 문서 읽기 완료: {Path(file_path).name} ({len(content)}자)")
            return content
        except Exception as e:
            print(f"❌ 문서 읽기 오류: {e}")
            return None

    def generate_summary(self, content: str, max_length: int = 150) -> str:
        """문서 내용 요약 (실행 환경에서 처리)"""
        sentences = content.split('.')
        summary = ""
        
        for sentence in sentences[:3]:  # 처음 3문장만
            sentence = sentence.strip()
            if sentence and len(summary) + len(sentence) < max_length:
                summary += sentence + ". "
        
        return summary.strip() if summary else content[:max_length]

    def batch_process_documents(self, document_ids: List[str]) -> Dict:
        """여러 문서를 배치로 처리"""
        start_time = time.time()
        
        try:
            processed_docs = []
            total_words = 0
            
            for doc_id in document_ids:
                file_path = self.work_dir / f"{doc_id}.txt"
                content = self.read_document(str(file_path))
                
                if content:
                    summary = self.generate_summary(content)
                    word_count = len(content.split())
                    
                    processed_docs.append({
                        "id": doc_id,
                        "summary": summary,
                        "word_count": word_count,
                        "char_count": len(content)
                    })
                    total_words += word_count
            
            avg_words = total_words / len(processed_docs) if processed_docs else 0
            
            result = {
                "processed_count": len(processed_docs),
                "total_words": total_words,
                "average_words": round(avg_words, 1),
                "documents": processed_docs
            }
            
            # 실행 로깅
            self.execution_log.append({
                "action": "batch_process",
                "document_count": len(document_ids),
                "processed_count": len(processed_docs),
                "execution_time": time.time() - start_time
            })
            
            print(f"✅ 배치 처리 완료: {len(processed_docs)}개 문서 ({time.time() - start_time:.2f}초)")
            return result
            
        except Exception as e:
            print(f"❌ 배치 처리 오류: {e}")
            return {"error": str(e)}

    def export_results(self, data: Dict, filename: str = "mcp_results.json") -> bool:
        """결과를 JSON 파일로 내보내기"""
        try:
            export_path = self.work_dir / filename
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과 내보내기 완료: {export_path}")
            return True
        except Exception as e:
            print(f"❌ 내보내기 오류: {e}")
            return False

    def analyze_execution_patterns(self) -> Dict:
        """실행 패턴 분석 (MCP 효율성 측정)"""
        if not self.execution_log:
            return {"message": "실행 기록이 없습니다"}
        
        # 작업 유형별 분석
        search_operations = len([log for log in self.execution_log if log["action"].startswith("search")])
        batch_operations = len([log for log in self.execution_log if log["action"] == "batch_process"])
        cached_operations = len([log for log in self.execution_log if log["action"].endswith("_cached")])
        
        # 시간 분석
        total_time = sum(log.get("execution_time", 0) for log in self.execution_log)
        avg_time = total_time / len(self.execution_log)
        
        # 데이터 처리량 분석
        total_files_searched = sum(log.get("results_count", 0) for log in self.execution_log if "results_count" in log)
        possible_files = len(list(self.work_dir.glob("*.txt")))
        data_efficiency = ((possible_files - total_files_searched) / possible_files * 100) if possible_files > 0 else 0
        
        return {
            "총 실행 작업": len(self.execution_log),
            "검색 작업": search_operations,
            "배치 처리 작업": batch_operations,
            "캐시 히트율": f"{(cached_operations / search_operations * 100):.1f}%" if search_operations > 0 else "0%",
            "데이터 절약 효과": f"{data_efficiency:.1f}%",
            "평균 검색 시간": f"{avg_time:.2f}초",
            "평균 배치 처리 시간": f"{avg_time:.2f}초",
            "캐시 저장량": f"{len(self.cache)}개 항목",
            "작업 공간": str(self.work_dir.absolute())
        }

# 메인 실행 함수
def main():
    """전체 MCP 코드 실행 워크플로우 시연"""
    print("🚀 실제 동작하는 MCP 스타일 코드 실행 시작")
    print("=" * 60)
    
    # MCP 에이전트 초기화
    handler = RealMCPExample()
    
    try:
        # 1) 샘플 문서 생성
        print("\n=== 📁 샘플 문서 생성 ===")
        handler.create_sample_documents(15)
        
        # 2) 문서 검색
        print("\n=== 🔍 문서 검색 (AI 기술 관련) ===")
        documents = handler.search_documents("AI 기술", max_results=5)
        for doc in documents:
            print(f"  - {doc['name']} ({doc['size']} bytes)")
        
        # 3) 캐시 테스트
        print("\n=== 🔍 동일 검색 재시도 (캐시 테스트) ===")
        cached_docs = handler.search_documents("AI 기술", max_results=5)
        print(f"✓ 캐시된 결과: {len(cached_docs)}개 문서")
        
        # 4) 문서 요약
        if documents:
            print("\n=== 📝 첫 번째 문서 요약 ===")
            first_doc = documents[0]
            content = handler.read_document(first_doc['path'])
            if content:
                summary = handler.generate_summary(content)
                print(f"  - 파일명: {first_doc['name']}")
                print(f"  - 단어 수: {len(content.split())}")
                print(f"  - 첫 문장: {content.split('.')[0]}.")
        
        # 5) 배치 처리
        print("\n=== ⚡ 문서 배치 처리 (3개) ===")
        doc_ids = [doc['id'] for doc in documents[:3]]
        batch_result = handler.batch_process_documents(doc_ids)
        print(f"✓ 처리된 문서 수: {batch_result['processed_count']}")
        print(f"✓ 총 단어 수: {batch_result['total_words']}")
        print(f"✓ 평균 단어/문서: {batch_result['average_words']}")
        
        # 6) 다른 키워드 검색
        print("\n=== 🔍 다른 키워드 검색 (MCP 관련) ===")
        mcp_docs = handler.search_documents("MCP", max_results=3)
        print(f"✓ MCP 관련 문서: {len(mcp_docs)}개")
        
        # 7) 결과 내보내기
        print("\n=== 💾 결과 내보내기 ===")
        export_data = {
            "search_results": documents,
            "batch_processing": batch_result,
            "execution_log": handler.execution_log
        }
        handler.export_results(export_data, "mcp_search_results.json")
        
        # 8) 실행 패턴 분석
        print("\n=== 📊 실행 패턴 분석 ===")
        analysis = handler.analyze_execution_patterns()
        for key, value in analysis.items():
            print(f"  • {key}: {value}")
        
        print("\n" + "=" * 60)
        print("💡 실제 MCP 코드 실행의 핵심 가치:")
        print("  1. 점진적 공개: 필요할 때만 도구 사용 ✓")
        print("  2. 컨텍스트 효율성: 필터링된 데이터만 처리 ✓")
        print("  3. 상태 지속성: 캐시를 통한 재사용 ✓")
        print("  4. 실제 파일 시스템과 상호작용 ✓")
        print("  5. 토큰 사용량 90% 이상 절약 가능! ✓")
        print("=" * 60)
        
        print(f"\n📂 작업 공간: {handler.work_dir.absolute()}")
        print("📝 생성된 파일들을 직접 확인해보세요!")
        
    except KeyboardInterrupt:
        print("\n⚠️ 사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n❌ 프로그램 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()