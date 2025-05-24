# ArXiv MCP Server 사용 가이드

이 가이드는 ArXiv MCP Server를 설치하고 사용하는 방법을 설명합니다.

## 1. uv 설치

mcp

### macOS

**Homebrew를 사용한 설치:**
```bash
brew install uv
```

**curl을 사용한 설치:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Windows

**PowerShell을 사용한 설치:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Scoop을 사용한 설치:**
```bash
scoop install uv
```

**winget을 사용한 설치:**
```bash
winget install --id=astral-sh.uv  -e
```


## 2. 의존성 설치

uv가 설치되었다면, 프로젝트 디렉토리에서 다음 명령어를 실행하여 의존성을 설치합니다:

```bash
# 프로젝트 디렉토리로 이동
cd arxiv-mcp-server

# 의존성 설치
uv sync
```

또는 개발 의존성까지 포함하여 설치하려면:

```bash
uv sync --dev
```

## 3. MCP 서버 등록

### Claude Desktop에 MCP 서버 등록하기

1. **Claude Desktop 설정 파일 위치 찾기:**

   **macOS:**
   ```
   ~/Library/Application Support/Claude/claude_desktop_config.json
   ```

   **Windows:**
   ```
   %APPDATA%\Claude\claude_desktop_config.json
   ```

2. **설정 파일 편집:**

   설정 파일이 존재하지 않는다면 새로 생성하고, 다음 내용을 추가합니다:

   ```json
   {
     "mcpServers": {
       "arxiv": {
         "command": "uv",
         "args": ["--directory", "/path/to/arxiv-mcp-server", "run", "arxiv-mcp-server"],
         "env": {}
       }
     }
   }
   ```

   **주의:** `/path/to/arxiv-mcp-server`를 실제 프로젝트 경로로 변경해야 합니다. 현재 폴더까지의 경로를 붙여넣으면 됩니다.

   **예시 (macOS):**
   ```json
   {
     "mcpServers": {
       "arxiv": {
         "command": "uv",
         "args": ["--directory", "/Users/username/projects/arxiv-mcp-server", "run", "arxiv-mcp-server"],
         "env": {}
       }
     }
   }
   ```

   **예시 (Windows):**
   ```json
   {
     "mcpServers": {
       "arxiv": {
         "command": "uv",
         "args": ["--directory", "C:\\Users\\username\\projects\\arxiv-mcp-server", "run", "arxiv-mcp-server"],
         "env": {}
       }
     }
   }
   ```

3. **Claude Desktop 재시작:**

   설정 파일을 저장한 후 Claude Desktop을 완전히 종료하고 다시 실행합니다.

## 4. 설치 확인

Claude Desktop을 실행한 후, 새로운 대화에서 다음과 같이 테스트해볼 수 있습니다:

```
"machine learning" 키워드로 arXiv 논문을 검색해줘
```

MCP 서버가 정상적으로 등록되었다면, ArXiv에서 논문을 검색하여 결과를 보여줄 것입니다.

## 문제 해결

### 일반적인 문제들

1. **uv 명령어를 찾을 수 없는 경우:**
   - 터미널을 재시작하거나 PATH를 다시 로드해보세요
   - `source ~/.bashrc` 또는 `source ~/.zshrc` (macOS/Linux)

2. **MCP 서버가 등록되지 않는 경우:**
   - 설정 파일의 JSON 형식이 올바른지 확인하세요
   - 프로젝트 경로가 정확한지 확인하세요
   - Claude Desktop을 완전히 재시작했는지 확인하세요

3. **의존성 설치 오류:**
   - Python 3.8 이상이 설치되어 있는지 확인하세요
   - `uv --version`으로 uv가 제대로 설치되었는지 확인하세요

### 디버깅

MCP 서버의 로그를 확인하려면 다음 명령어로 직접 실행해볼 수 있습니다:

```bash
cd arxiv-mcp-server
uv run arxiv-mcp-server
```

## 추가 정보

- uv 공식 문서: https://docs.astral.sh/uv/
- MCP 공식 문서: https://modelcontextprotocol.io/
- Claude Desktop 다운로드: https://claude.ai/download