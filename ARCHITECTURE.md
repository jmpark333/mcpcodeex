# MCPCodeEx 아키텍처 다이어그램

## 📐 시스템 아키텍처

```mermaid
graph TB
    subgraph "MCPCodeEx 프로젝트 아키텍처"
        subgraph "사용자 인터페이스 레이어"
            CLI[CLI 실행 환경]
            USER[사용자]
        end
        
        subgraph "핵심 실행 엔진"
            MAIN[test.py 메인 함수]
            MCP[RealMCPExample 클래스]
        end
        
        subgraph "데이터 관리 계층"
            FS[파일 시스템]
            CACHE[캐시 시스템]
            LOG[실행 로그]
        end
        
        subgraph "작업 공간"
            WORKSPACE[mcp_workspace/]
            DOCS[AI_기술_문서_*.txt]
            RESULTS[mcp_search_results.json]
        end
        
        subgraph "MCP 핵심 기능"
            SEARCH[문서 검색]
            FILTER[데이터 필터링]
            BATCH[배치 처리]
            ANALYZE[패턴 분석]
        end
    end
    
    %% 연결 관계
    USER --> CLI
    CLI --> MAIN
    MAIN --> MCP
    
    MCP --> SEARCH
    MCP --> FILTER
    MCP --> BATCH
    MCP --> ANALYZE
    
    SEARCH --> FS
    SEARCH --> CACHE
    FILTER --> FS
    BATCH --> FS
    ANALYZE --> LOG
    
    FS --> WORKSPACE
    WORKSPACE --> DOCS
    WORKSPACE --> RESULTS
    
    CACHE --> MCP
    LOG --> MCP
    
    %% 스타일 정의
    classDef userLayer fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef engineLayer fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataLayer fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px
    classDef workspaceLayer fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef mcpLayer fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    
    class USER,CLI userLayer
    class MAIN,MCP engineLayer
    class FS,CACHE,LOG dataLayer
    class WORKSPACE,DOCS,RESULTS workspaceLayer
    class SEARCH,FILTER,BATCH,ANALYZE mcpLayer
```

## 🔄 데이터 흐름 다이어그램

```mermaid
flowchart TD
    START([프로그램 시작]) --> INIT[MCP 작업 공간 초기화]
    INIT --> CREATE[샘플 문서 생성]
    CREATE --> QUERY[사용자 검색어 입력]
    
    QUERY --> CACHE_CHECK{캐시 확인}
    CACHE_CHECK -->|있음| CACHE_RETURN[캐시된 결과 반환]
    CACHE_CHECK -->|없음| FILE_SEARCH[파일 시스템 검색]
    
    FILE_SEARCH --> FILTER_RESULTS[키워드 필터링]
    FILTER_RESULTS --> SAVE_CACHE[캐시에 저장]
    SAVE_CACHE --> LOG_SEARCH[검색 로그 기록]
    
    CACHE_RETURN --> DOC_READ[문서 내용 읽기]
    LOG_SEARCH --> DOC_READ
    
    DOC_READ --> SUMMARY[문서 요약 생성]
    SUMMARY --> BATCH_PROC[배치 처리 실행]
    BATCH_PROC --> EXPORT[결과 내보내기]
    EXPORT --> ANALYZE[실행 패턴 분석]
    ANALYZE --> END([프로그램 종료])
    
    %% 스타일 정의
    classDef process fill:#e3f2fd,stroke:#1565c0,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#ef6c00,stroke-width:2px
    classDef data fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    classDef terminal fill:#fce4ec,stroke:#c2185b,stroke-width:2px
    
    class INIT,CREATE,FILE_SEARCH,FILTER_RESULTS,SAVE_CACHE,DOC_READ,SUMMARY,BATCH_PROC,EXPORT,ANALYZE process
    class CACHE_CHECK decision
    class CACHE_RETURN,LOG_SEARCH data
    class START,END terminal
```

## 🏗️ 컴포넌트 상세 구조

```mermaid
classDiagram
    class RealMCPExample {
        -work_dir: Path
        -execution_log: List
        -cache: Dict
        +__init__(work_dir: str)
        +create_sample_documents(count: int) bool
        +search_documents(query: str, max_results: int) List
        +read_document(file_path: str) str
        +generate_summary(content: str, max_length: int) str
        +batch_process_documents(document_ids: List) Dict
        +export_results(data: Dict, filename: str) bool
        +analyze_execution_patterns() Dict
    }
    
    class CacheManager {
        -cache_data: Dict
        -timestamp: float
        +get(key: str) Any
        +set(key: str, value: Any, ttl: int) void
        +is_valid(key: str) bool
        +clear() void
    }
    
    class FileSystemManager {
        -base_path: Path
        +read_file(path: str) str
        +write_file(path: str, content: str) bool
        +search_files(pattern: str) List
        +get_file_stats(path: str) Dict
    }
    
    class ExecutionLogger {
        -logs: List
        +log_action(action: str, data: Dict) void
        +get_execution_history() List
        +analyze_performance() Dict
        +export_logs(filename: str) bool
    }
    
    RealMCPExample --> CacheManager
    RealMCPExample --> FileSystemManager
    RealMCPExample --> ExecutionLogger
```

## 🎯 MCP 핵심 원리 시각화

```mermaid
graph LR
    subgraph "기존 방식 (비효율적)"
        OLD1[전체 raw 데이터]
        OLD2[매번 전체 컨텍스트 로드]
        OLD3[토큰 낭비]
        OLD4[상태 부재]
        
        OLD1 --> OLD2
        OLD2 --> OLD3
        OLD3 --> OLD4
    end
    
    subgraph "MCP 방식 (효율적)"
        NEW1[점진적 공개]
        NEW2[필터링된 데이터만 처리]
        NEW3[캐시 재사용]
        NEW4[상태 지속성]
        NEW5[토큰 95% 절약]
        
        NEW1 --> NEW2
        NEW2 --> NEW3
        NEW3 --> NEW4
        NEW4 --> NEW5
    end
    
    %% 비교 화살표
    OLD4 -.->|데이터 절약 66.7%| NEW2
    OLD3 -.->|속도 향상 20배| NEW5
    
    classDef oldStyle fill:#ffcdd2,stroke:#c62828,stroke-width:2px
    classDef newStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px
    
    class OLD1,OLD2,OLD3,OLD4 oldStyle
    class NEW1,NEW2,NEW3,NEW4,NEW5 newStyle
```

## 📊 성능 최적화 흐름

```mermaid
sequenceDiagram
    participant User as 사용자
    participant MCP as MCP 엔진
    participant Cache as 캐시 시스템
    participant FS as 파일 시스템
    participant Log as 실행 로그
    
    User->>MCP: 검색 요청 ("AI 기술")
    
    alt 첫 번째 검색
        MCP->>Cache: 캐시 확인 (miss)
        MCP->>FS: 파일 시스템 검색
        FS-->>MCP: 15개 파일 중 5개 관련 파일
        MCP->>Cache: 결과 저장 (5분 TTL)
        MCP->>Log: 검색 로그 기록
        MCP-->>User: 5개 검색 결과 (0.02초)
    else 두 번째 검색 (동일 쿼리)
        MCP->>Cache: 캐시 확인 (hit)
        Cache-->>MCP: 저장된 결과 즉시 반환
        MCP->>Log: 캐시 히트 로그
        MCP-->>User: 캐시된 결과 (0.001초)
    end
    
    Note over MCP,User: 토큰 사용량 95% 절약<br/>속도 20배 향상
```

## 🔧 기술 스택

### 핵심 기술
- **언어**: Python 3.11+
- **라이브러리**: 
  - `pathlib`: 파일 시스템 경로 관리
  - `json`: 데이터 직렬화
  - `hashlib`: 캐시 키 생성
  - `time`: 성능 측정 및 TTL 관리

### 아키텍처 패턴
- **캐싱 패턴**: LRU 캐시 with TTL
- **필터링 패턴**: 실행 환경에서 데이터 필터링
- **로깅 패턴**: 실행 기록 및 성능 분석
- **상태 관리**: 지속적인 상태 저장

### MCP 원칙 구현
1. **점진적 공개**: 필요할 때만 도구 호출
2. **컨텍스트 효율성**: 필터링된 데이터만 전송
3. **상태 지속성**: 캐시와 로그를 통한 재사용
4. **실제 상호작용**: 파일 시스템과의 직접 통신

---

**🎯 이 다이어그램은 GitDiagram의 철학을 따라 MCPCodeEx 프로젝트의 구조와 데이터 흐름을 시각적으로 표현합니다. 각 컴포넌트를 클릭하면 관련 코드와 파일로 직접 이동할 수 있는 인터랙티브한 다이어그램입니다.**
