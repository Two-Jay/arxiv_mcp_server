# ArXiv MCP Server 사용 가이드

이 가이드는 ArXiv MCP Server를 설치하고 사용하는 방법을 설명합니다. 코딩 경험이 없어도 따라할 수 있도록 자세히 설명되어 있습니다.

## 1. uv 설치

uv는 Python 프로젝트를 관리하는 도구입니다. 우리가 만든 ArXiv 서버를 실행하기 위해 필요합니다.

### macOS (맥)

**방법 1: Homebrew 사용 (가장 쉬운 방법)**

먼저 Homebrew가 설치되어 있는지 확인하세요. 터미널(Applications > Utilities > Terminal)을 열고 다음을 입력:

```bash
brew --version
```

Homebrew가 설치되어 있다면 버전이 나타납니다. 설치되어 있지 않다면 [brew.sh](https://brew.sh)에서 설치하세요.

Homebrew가 있다면 다음 명령어로 uv를 설치:
```bash
brew install uv
```

**방법 2: 자동 설치 스크립트 사용**

터미널에서 다음 명령어를 실행하세요:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows (윈도우)

**방법 1: PowerShell 사용 (가장 쉬운 방법)**

1. 윈도우 검색창에서 "PowerShell"을 검색
2. "Windows PowerShell"을 **관리자 권한으로** 실행 (우클릭 > "관리자 권한으로 실행")
3. 다음 명령어를 복사해서 붙여넣고 Enter:

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**방법 2: Scoop 사용**

Scoop이 설치되어 있다면:
```bash
scoop install uv
```

**방법 3: winget 사용**

윈도우 10/11에서 사용할 수 있는 기본 패키지 관리자:
```bash
winget install --id=astral-sh.uv  -e
```

**설치 확인하기**

설치가 완료되었는지 확인하려면 터미널(맥) 또는 명령 프롬프트(윈도우)를 새로 열고 다음을 입력:

```bash
uv --version
```

버전 번호가 나타나면 성공적으로 설치된 것입니다.

## 2. 의존성 설치

"의존성"이란 우리 프로그램이 작동하기 위해 필요한 다른 프로그램들을 말합니다. 마치 요리를 하기 위해 재료들이 필요한 것과 같습니다.

**단계별 진행:**

1. **터미널/명령 프롬프트 열기**
   - **맥**: Applications > Utilities > Terminal
   - **윈도우**: 시작 메뉴에서 "cmd" 검색 후 "명령 프롬프트" 실행

2. **프로젝트 폴더로 이동**
   
   ArXiv MCP Server 폴더가 저장된 위치로 이동해야 합니다. 예를 들어:
   
   **맥의 경우:**
   ```bash
   cd /Users/사용자이름/Downloads/arxiv-mcp-server
   ```
   
   **윈도우의 경우:**
   ```bash
   cd C:\Users\사용자이름\Downloads\arxiv-mcp-server
   ```
   
   💡 **팁**: 폴더를 터미널/명령 프롬프트로 드래그하면 경로가 자동으로 입력됩니다!

3. **의존성 설치하기**
   
   다음 명령어를 입력하고 Enter를 누르세요:
   ```bash
   uv sync
   ```
   
   이 과정은 몇 분 정도 걸� 수 있습니다. 화면에 여러 메시지가 나타나는 것은 정상입니다.

## 3. MCP 서버 등록

MCP 서버를 Claude Desktop에 등록하면, Claude가 ArXiv에서 논문을 검색할 수 있게 됩니다. 마치 Claude에게 새로운 기능을 추가해주는 것입니다.

### Claude Desktop에 MCP 서버 등록하기

**1단계: 설정 파일 찾기**

Claude Desktop의 설정 파일을 찾아야 합니다. 이 파일은 숨겨진 폴더에 있을 수 있습니다.

**맥 사용자:**
1. Finder를 엽니다
2. 메뉴에서 "이동" > "폴더로 이동..." 클릭
3. 다음 경로를 입력하고 이동: `~/Library/Application Support/Claude/`
4. `claude_desktop_config.json` 파일을 찾습니다

**윈도우 사용자:**
1. 윈도우 키 + R을 누릅니다
2. `%APPDATA%\Claude` 를 입력하고 Enter
3. `claude_desktop_config.json` 파일을 찾습니다

**2단계: 설정 파일 편집하기**

파일이 없다면 새로 만들어야 합니다:

1. 메모장(윈도우) 또는 텍스트 편집기(맥)를 엽니다
2. 다음 내용을 복사해서 붙여넣습니다:

   ```json
   {
     "mcpServers": {
       "arxiv": {
         "command": "uv",
         "args": ["--directory", "여기에_실제_폴더_경로_입력", "run", "arxiv-mcp-server"],
         "env": {}
       }
     }
   }
   ```

3. **중요**: `여기에_실제_폴더_경로_입력` 부분을 ArXiv MCP Server 폴더의 실제 경로로 바꿔야 합니다.

**경로 찾는 방법:**
- **맥**: Finder에서 arxiv-mcp-server 폴더를 우클릭 > "정보 보기" > "위치" 확인
- **윈도우**: 파일 탐색기에서 arxiv-mcp-server 폴더의 주소창 내용 복사

**실제 예시:**

**맥의 경우:**
```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uv",
      "args": ["--directory", "/Users/홍길동/Downloads/arxiv-mcp-server", "run", "arxiv-mcp-server"],
      "env": {}
    }
  }
}
```

**윈도우의 경우:**
```json
{
  "mcpServers": {
    "arxiv": {
      "command": "uv",
      "args": ["--directory", "C:\\Users\\홍길동\\Downloads\\arxiv-mcp-server", "run", "arxiv-mcp-server"],
      "env": {}
    }
  }
}
```

**3단계: 파일 저장하기**

1. 파일을 `claude_desktop_config.json` 이름으로 저장합니다
2. 파일 형식은 "모든 파일" 또는 "JSON"으로 선택하세요
3. 저장 위치는 앞서 찾은 Claude 폴더입니다

**4단계: Claude Desktop 재시작**

1. Claude Desktop을 완전히 종료합니다 (맥: Cmd+Q, 윈도우: Alt+F4 또는 X 버튼)
2. Claude Desktop을 다시 실행합니다

## 4. 설치 확인

모든 설정이 완료되었는지 확인해보겠습니다.

**1단계: Claude Desktop 실행**
Claude Desktop을 열고 새로운 대화를 시작합니다.

**2단계: 테스트해보기**
Claude에게 다음과 같이 물어보세요:

```
"machine learning" 키워드로 arXiv 논문을 검색해줘
```

또는

```
arXiv에서 인공지능 관련 최신 논문 5개를 찾아줘
```

**성공한 경우:** Claude가 실제로 arXiv에서 논문들을 검색해서 제목, 저자, 요약 등을 보여줍니다.

**실패한 경우:** Claude가 "arXiv에 접근할 수 없다" 또는 "검색 기능을 사용할 수 없다"고 답합니다. 이 경우 아래 문제 해결 섹션을 참고하세요.

## 문제 해결

설치 과정에서 문제가 발생했을 때 해결 방법입니다.

### 일반적인 문제들

**1. "uv 명령어를 찾을 수 없습니다" 오류**

**원인:** uv가 제대로 설치되지 않았거나, 시스템이 uv를 찾을 수 없습니다.

**해결 방법:**
- 터미널/명령 프롬프트를 완전히 닫고 새로 열어보세요
- 맥 사용자: 터미널에서 `source ~/.zshrc` 또는 `source ~/.bashrc` 입력
- 그래도 안 되면 uv를 다시 설치해보세요

**2. MCP 서버가 작동하지 않는 경우**

**원인:** 설정 파일에 오타가 있거나 경로가 잘못되었습니다.

**해결 방법:**
1. `claude_desktop_config.json` 파일을 다시 열어보세요
2. JSON 형식이 올바른지 확인하세요 (중괄호, 쉼표, 따옴표 등)
3. 폴더 경로가 정확한지 다시 확인하세요
4. Claude Desktop을 완전히 재시작했는지 확인하세요

**JSON 형식 확인 방법:**
- 온라인 JSON 검증 도구를 사용하세요: jsonlint.com
- 설정 파일 내용을 복사해서 붙여넣고 오류가 있는지 확인

**3. "의존성을 설치할 수 없습니다" 오류**

**원인:** Python이 설치되지 않았거나 버전이 너무 낮습니다.

**해결 방법:**
- Python 3.8 이상이 설치되어 있는지 확인: `python --version` 또는 `python3 --version`
- Python이 없다면 python.org에서 다운로드해서 설치
- `uv --version`으로 uv가 제대로 설치되었는지 확인

**4. 경로를 찾을 수 없는 경우**

**해결 방법:**
- 맥: Finder에서 arxiv-mcp-server 폴더를 터미널로 드래그하면 경로가 자동 입력됩니다
- 윈도우: 파일 탐색기에서 Shift + 우클릭 > "경로로 복사" 선택

### 고급 디버깅

문제를 더 자세히 알아보려면 MCP 서버를 직접 실행해볼 수 있습니다:

**1단계: 터미널/명령 프롬프트에서 프로젝트 폴더로 이동**
```bash
cd /path/to/arxiv-mcp-server
```

**2단계: 서버 직접 실행**
```bash
uv run arxiv-mcp-server
```

오류 메시지가 나타나면 그 내용을 바탕으로 문제를 해결할 수 있습니다.

### 도움이 필요한 경우

위 방법들로도 해결되지 않으면:
1. 오류 메시지를 정확히 복사해두세요
2. 어떤 단계에서 문제가 발생했는지 기록해두세요
3. 사용하는 운영체제(맥/윈도우)와 버전을 확인해두세요

## 추가 정보

- uv 공식 문서: https://docs.astral.sh/uv/
- MCP 공식 문서: https://modelcontextprotocol.io/
- Claude Desktop 다운로드: https://claude.ai/download