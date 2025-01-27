# Upstage Agent Chat

이 프로젝트는 Upstage의 다양한 AI 모델들을 활용한 RAG 대화형 에이전트 시스템입니다.

## 주요 기능

- **Upstage 모델 활용**
  - ChatUpstage: 대화형 AI 모델
  - UpstageEmbeddings: 문서 임베딩 모델
  - UpstageGroundednessCheck: AI 응답의 신뢰성 검증 기능

- **통합 검색 기능**
  - Google 검색 (SerpAPI 활용)
  - Tavily AI 특화 검색
  - PDF 문서 내용 검색 및 분석(RAG)

- **Streamlit 웹 인터페이스**
  - 채팅 인터페이스
  - 대화 기록 자동 관리

## 설치 방법

1. 저장소 복제
```bash
git clone https://github.com/your-username/Upstage_agent_chat.git
cd Upstage_agent_chat
```

2. 가상환경 생성
```bash
python -m venv venv
source venv/Scripts/activate
```

3. 필수 패키지 설치
```bash
pip install -r requirements.txt
```

4. 환경 변수 설정
프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 입력하세요:
```bash
UPSTAGE_API_KEY=your_upstage_api_key
SERPAPI_API_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_key
```

## 실행 방법

1. PDF 파일 설정
- `agent_chat.py` 파일에서 `file_path` 변수를 분석하고자 하는 PDF 파일 경로로 수정하세요.

2. 애플리케이션 실행
```bash
streamlit run agent_chat.py
```

## 기능 설명

- **문서 분석**: PDF 문서를 자동으로 분석하고 벡터화하여 검색 가능한 형태로 변환
- **멀티 소스 검색**: Google 검색, Tavily 검색, 문서 내용 검색을 통합적으로 제공
- **대화 관리**: 최근 대화 내용을 자동으로 관리하고 컨텍스트 유지
- **신뢰성 검증**: AI 응답에 대한 Groundedness Check를 통해 신뢰성 확인