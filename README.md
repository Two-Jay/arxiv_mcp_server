# ArXiv MCP Server

arXiv Open API를 활용한 Model Context Protocol (MCP) 서버입니다. 논문 검색, 메타데이터 조회, PDF 내용 추출 등의 기능을 제공합니다.

## 기능

- **논문 검색**: 키워드, 저자, 카테고리로 arXiv 논문 검색
- **논문 상세 정보**: arXiv ID로 논문의 상세 메타데이터 조회
- **PDF 내용 추출**: 논문 PDF에서 텍스트 내용 추출
- **논문 요약**: 논문의 핵심 정보와 초록 제공

## 설치

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

2. 서버 실행:
```bash
python arxiv_mcp_server.py
```

## 사용 가능한 도구 (Tools)

### 1. search_papers
논문을 검색합니다.

**파라미터:**
- `query` (필수): 검색 키워드
- `author` (선택): 저자명
- `category` (선택): arXiv 카테고리 (예: cs.AI, math.GT)
- `max_results` (선택): 최대 결과 수 (기본값: 10)
- `sort_by` (선택): 정렬 방식 (relevance, lastUpdatedDate, submittedDate)

**예시:**
```json
{
  "query": "machine learning",
  "category": "cs.LG",
  "max_results": 5
}
```

### 2. get_paper_details
특정 논문의 상세 정보를 조회합니다.

**파라미터:**
- `arxiv_id` (필수): arXiv 논문 ID (예: 2301.07041)

**예시:**
```json
{
  "arxiv_id": "2301.07041"
}
```

### 3. get_paper_content
논문 PDF의 텍스트 내용을 추출합니다.

**파라미터:**
- `arxiv_id` (필수): arXiv 논문 ID
- `max_pages` (선택): 추출할 최대 페이지 수 (기본값: 20)

**예시:**
```json
{
  "arxiv_id": "2301.07041",
  "max_pages": 10
}
```

### 4. summarize_paper
논문의 요약 정보를 제공합니다.

**파라미터:**
- `arxiv_id` (필수): arXiv 논문 ID

**예시:**
```json
{
  "arxiv_id": "2301.07041"
}
```

## 리소스 (Resources)

### 1. arxiv://search
논문 검색 기능에 대한 정보를 제공합니다.

### 2. arxiv://categories
arXiv 주제 카테고리 목록을 제공합니다.

## arXiv 카테고리 예시

### Computer Science
- `cs.AI` - Artificial Intelligence
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision and Pattern Recognition
- `cs.LG` - Machine Learning
- `cs.NE` - Neural and Evolutionary Computing
- `cs.RO` - Robotics

### Mathematics
- `math.AG` - Algebraic Geometry
- `math.GT` - Geometric Topology
- `math.LO` - Logic
- `math.NT` - Number Theory
- `math.ST` - Statistics Theory

### Physics
- `physics.comp-ph` - Computational Physics
- `physics.data-an` - Data Analysis, Statistics and Probability
- `quant-ph` - Quantum Physics

### Statistics
- `stat.AP` - Applications
- `stat.CO` - Computation
- `stat.ML` - Machine Learning
- `stat.TH` - Theory

## 사용 예시

1. **머신러닝 논문 검색:**
   - Tool: `search_papers`
   - 파라미터: `{"query": "machine learning", "category": "cs.LG", "max_results": 5}`

2. **특정 논문 정보 조회:**
   - Tool: `get_paper_details`
   - 파라미터: `{"arxiv_id": "2301.07041"}`

3. **논문 내용 추출:**
   - Tool: `get_paper_content`
   - 파라미터: `{"arxiv_id": "2301.07041", "max_pages": 10}`

## 주의사항

- PDF 텍스트 추출은 텍스트 기반 PDF에서만 제대로 작동합니다.
- 이미지 기반 PDF의 경우 OCR이 필요하므로 추출 결과가 제한적일 수 있습니다.
- arXiv API에는 요청 제한이 있으므로 과도한 요청은 피해주세요.
- PDF 내용은 메모리에 캐시되므로 대용량 PDF를 많이 처리할 경우 메모리 사용량을 주의해주세요.

## 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

## 기여

버그 리포트나 기능 요청은 GitHub Issues를 통해 제출해주세요.