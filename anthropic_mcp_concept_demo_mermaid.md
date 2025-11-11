# Anthropic MCP 개념 데모 동작 원리 다이어그램

## 전체 시스템 아키텍처

```mermaid
graph TB
    subgraph "사용자 인터페이스"
        CLI[명령줄 인터페이스]
        MAIN[main 함수]
    end
    
    subgraph "MCP 데모 클래스"
        DEMO[AnthropicMCPConceptDemo]
        STATE[state_cache]
        HISTORY[execution_history]
    end
    
    subgraph "핵심 기능 모듈"
        PROG[demonstrate_progressive_disclosure]
        STATE_DEMO[demonstrate_state_persistence]
        CONTEXT[demonstrate_context_efficiency]
    end
    
    subgraph "도구 시뮬레이터"
        TOOLS[_call_tool]
        CACHE[_call_tool_with_cache]
        METADATA[_get_tools_list]
    end
    
    subgraph "파일 시스템"
        WORKSPACE[mcp_workspace/]
        FILES[AI_기술_문서_*.txt]
    end
    
    CLI --> MAIN
    MAIN --> DEMO
    DEMO --> STATE
    DEMO --> HISTORY
    
    DEMO --> PROG
    DEMO --> STATE_DEMO
    DEMO --> CONTEXT
    
    PROG --> TOOLS
    PROG --> METADATA
    
    STATE_DEMO --> CACHE
    CONTEXT --> TOOLS
    
    TOOLS --> WORKSPACE
    CACHE --> STATE
    WORKSPACE --> FILES
```

## 1. 점진적 공개 (Progressive Disclosure) 흐름

```mermaid
sequenceDiagram
    participant User as 사용자
    participant Demo as MCP 데모
    participant Tools as 도구 시뮬레이터
    participant Files as 파일 시스템
    
    User->>Demo: "AI 기술 관련 문서 찾아줘"
    
    Note over Demo: 기존 방식 시뮬레이션
    Demo->>Files: 모든 txt 파일 로드
    Files-->>Demo: 전체 파일 내용 (수만 자)
    Demo->>User: 📊 전체 로드: ~X,XXX 토큰
    
    Note over Demo: MCP 방식 실행
    Demo->>Tools: 도구 목록 조회
    Tools-->>Demo: 사용 가능한 도구 목록
    Demo->>User: 🔧 도구 목록: ~XX 토큰
    
    Demo->>Tools: search_files("AI 기술", max_results=3)
    Tools->>Files: AI 관련 파일 검색
    Files-->>Tools: 검색 결과 파일 목록
    Tools-->>Demo: 검색 결과 요약
    Demo->>User: 🔍 검색 결과: ~XX 토큰
    
    Demo->>Tools: read_file(첫 번째 결과 파일)
    Tools->>Files: 특정 파일 읽기
    Files-->>Tools: 파일 내용
    Tools-->>Demo: 파일 내용
    Demo->>User: 📖 파일 읽기: ~XX 토큰
    
    Demo->>User: 🎉 토큰 절약: 90%+
```

## 2. 상태 저장 (State Persistence) 메커니즘

```mermaid
stateDiagram-v2
    [*] --> FirstRequest
    FirstRequest --> GenerateCacheKey: 요청 파라미터로 캐시 키 생성
    GenerateCacheKey --> CheckCache: 캐시 확인
    
    CheckCache --> CacheMiss: 캐시에 없음
    CheckCache --> CacheHit: 캐시에 있음 (5분 내)
    
    CacheMiss --> ExecuteTool: 도구 실제 실행
    ExecuteTool --> StoreResult: 결과를 캐시에 저장
    StoreResult --> ReturnResult: 결과 반환
    ReturnResult --> [*]
    
    CacheHit --> ReturnCached: 캐시된 결과 반환
    ReturnCached --> UpdateHitCount: hit_count 증가
    UpdateHitCount --> [*]
    
    note right of CacheHit: 속도 향상: 10-100배
    note right of ExecuteTool: 첫 실행: O(n) 시간
    note right of ReturnCached: 캐시 히트: O(1) 시간
```

## 3. 컨텍스트 효율성 (Context Efficiency) 필터링

```mermaid
flowchart TD
    A[대용량 데이터셋<br/>100개 문서, 100KB+] --> B{기존 방식 vs MCP 방식}
    
    B --> C[기존 방식]
    B --> D[MCP 방식]
    
    C --> E[전체 데이터를<br/>컨텍스트에 포함]
    E --> F[컨텍스트 크기:<br/>~100,000+ 자]
    F --> G[토큰 사용량:<br/>~25,000+ 토큰]
    G --> H[⚠️ 컨텍스트 윈도우<br/>초과 위험]
    
    D --> I[1단계: 메타데이터 조회]
    I --> J[2단계: 관련 문서 ID 필터링]
    J --> K[3단계: 필요한 필드만 선택]
    K --> L[컨텍스트 크기:<br/>~1,000 자]
    L --> M[토큰 사용량:<br/>~250 토큰]
    M --> N[✅ 관련 정보만<br/>정확히 전달]
    
    style C fill:#ffcccc
    style D fill:#ccffcc
    style H fill:#ff9999
    style N fill:#99ff99
```

## 4. 도구 호출 시뮬레이션 상세 흐름

```mermaid
graph LR
    subgraph "도구 호출 프로세스"
        START[도구 호출 요청] --> VALIDATE[파라미터 검증]
        VALIDATE --> CACHE_CHECK[캐시 확인]
        
        CACHE_CHECK -->|캐시 히트| RETURN_CACHE[캐시된 결과 반환]
        CACHE_CHECK -->|캐시 미스| EXECUTE[실제 도구 실행]
        
        EXECUTE --> SEARCH_FILES[search_files]
        EXECUTE --> READ_FILE[read_file]
        EXECUTE --> GET_METADATA[get_metadata]
        EXECUTE --> GET_DOCUMENTS[get_documents]
        
        SEARCH_FILES --> FILE_SYSTEM[파일 시스템 조회]
        READ_FILE --> FILE_SYSTEM
        GET_METADATA --> SIMULATE[데이터 시뮬레이션]
        GET_DOCUMENTS --> SIMULATE
        
        FILE_SYSTEM --> STORE[결과 저장]
        SIMULATE --> STORE
        STORE --> RETURN_NEW[새로운 결과 반환]
        
        RETURN_CACHE --> UPDATE_CACHE[캐시 통계 업데이트]
        RETURN_NEW --> UPDATE_CACHE
        UPDATE_CACHE --> END[완료]
    end
    
    style START fill:#e1f5fe
    style END fill:#e8f5e8
    style RETURN_CACHE fill:#fff3e0
    style RETURN_NEW fill:#e8f5e8
```

## 5. 캐시 데이터 구조

```mermaid
classDiagram
    class StateCache {
        -Dict[str, CacheEntry] state_cache
        -List[ExecutionRecord] execution_history
        +get_cache_key(tool_name, arguments) str
        +check_cache(cache_key) Optional[CacheEntry]
        +store_result(cache_key, result) void
        +get_cache_stats() Dict[str, Any]
    }
    
    class CacheEntry {
        +Dict[str, Any] result
        +float timestamp
        +int hit_count
        +str tool_name
        +Dict[str, Any] arguments
        +is_expired() bool
    }
    
    class ExecutionRecord {
        +str tool_name
        +Dict[str, Any] arguments
        +float execution_time
        +bool cache_hit
        +datetime timestamp
    }
    
    StateCache --> CacheEntry
    StateCache --> ExecutionRecord
    
    note for CacheEntry "TTL: 5분<br/>키: tool_name + MD5(arguments)"
    note for ExecutionRecord "성능 모니터링용"
```

## 6. 성능 비교 메트릭스

```mermaid
gantt
    title MCP vs 기존 방식 성능 비교
    dateFormat X
    axisFormat %s
    
    section 기존 방식
    전체 파일 로드     :0, 3
    전체 데이터 처리    :3, 5
    컨텍스트 구성     :5, 6
    
    section MCP 방식
    도구 목록 조회     :0, 0.5
    필요한 도구만 호출   :0.5, 1.5
    필터링된 결과 처리  :1.5, 2
    컨텍스트 구성     :2, 2.2
    
    section 성능 향상
    토큰 절약율       :milestone, 6, 90%+
    속도 향상         :milestone, 6.2, 2-5배
    컨텍스트 효율     :milestone, 6.4, 95%+ 감소
```

## 핵심 통찰 요약

이 다이어그램들은 Anthropic MCP의 핵심 가치를 시각적으로 보여줍니다:

1. **점진적 공개**: 필요할 때만 도구를 호출하여 불필요한 토큰 소비 방지
2. **상태 저장**: 캐시를 통해 이전 실행 결과를 재사용하여 성능 극대화
3. **컨텍스트 효율성**: 필터링된 데이터만 처리하여 컨텍스트 윈도우 최적화

이러한 원리들을 통해 MCP는 **90% 이상의 토큰 절약**과 **2-100배의 속도 향상**을 달성할 수 있습니다.
