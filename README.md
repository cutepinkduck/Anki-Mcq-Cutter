# ANKI MCQ CUTTER 📚✂️

<div align="center">

[🇰🇷 한국어](#kr) | [🇺🇸 English](#en) | [🇨🇳 中文](#zh)

</div>

---

<details open id="kr">
<summary><h2>🇰🇷 한국어 (Korean)</h2></summary>

PDF 문서에서 객관식 문제(MCQ)를 AI로 분석하여 Anki 플래시카드를 자동 생성하는 웹 애플리케이션입니다.

## 📋 주요 기능

- **PDF 분석**: PDF 파일을 업로드하면 AI가 문제(Question)와 해답(Solution)을 자동 감지
- **이미지 크롭**: 감지된 영역을 고화질로 잘라서 저장 (기본 DPI: 300)
- **Batch API 지원**: 대량 페이지를 한 번에 서버로 전송하여 처리
- **다중 AI Provider**: Google Gemini, OpenAI, Anthropic Claude, OpenRouter 지원
- **프로필 관리**: AI 설정과 프롬프트를 프로필로 저장/불러오기
- **자동 저장**: IndexedDB를 통한 자동 저장으로 작업 중 데이터 손실 방지
- **시스템 보호**: Web Worker를 이용한 백그라운드 탭 활성 유지
- **🌐 다국어 지원**: 한국어, English, 中文 UI 언어 선택 가능

## 🛠️ 설치 방법

### 1. 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 2. Python 가상환경 설정 (권장)

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
.\venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install fastapi uvicorn httpx python-multipart pymupdf pillow
```

## 🚀 사용 방법

### 1. 간편 실행 (원클릭)

| OS | 방법 |
|----|------|
| **macOS/Linux** | `start.sh` 더블클릭 |
| **Windows** | `start.bat` 더블클릭 |

> 서버가 자동으로 시작되고, 브라우저에서 앱이 열립니다.

### 2. 수동 실행

서버가 실행되면 `http://localhost:8000`에서 API가 실행됩니다.

### 2. 웹 인터페이스 열기

`anki_batch.html` 파일을 브라우저에서 열어주세요.

```bash
# macOS
open anki_batch.html

# Windows
start anki_batch.html

# Linux
xdg-open anki_batch.html
```

### 3. API 키 설정

1. 좌측 **AI 엔진** 패널에서 Provider 선택 (Gemini, OpenAI, Anthropic 등)
2. API Key 입력
3. 필요시 프로필로 저장하여 재사용

### 4. PDF 분석

1. **PDF 업로드** 버튼 클릭하여 PDF 파일 선택
2. 서버에서 페이지 변환 후 갤러리에 표시됨
3. **실시간 시작** 또는 **Batch API 전송** 버튼 클릭
   - **실시간 시작**: 페이지를 하나씩 분석 (진행 상황 실시간 확인)
   - **Batch API 전송**: 모든 페이지를 한 번에 서버로 전송 후 결과 확인

### 5. 결과 편집

- 결과 아이템의 **가위** 아이콘으로 영역 수정
  - 방향 버튼 **클릭**: 한 번 조정
  - 방향 버튼 **꾹 누르기**: 연속 조정 (빠른 편집)
  - **Shift + 클릭/꾹 누르기**: 5배 속도로 조정
- **휴지통** 아이콘으로 불필요한 항목 삭제
- 결과 선택 후 일괄 삭제 가능
- 고화질 변환 중에도 다른 항목 편집 가능 (비동기 처리)

### 6. Anki 필드 설정

RESULT 패널의 **필드(N)** 버튼을 클릭하여 Anki 카드 필드를 커스터마이징:

- **문제 이미지**: 문제 영역 캡처 (기본 활성)
- **해설 이미지**: 해설 영역 캡처 (기본 활성)
- **태그/단원**: 챕터명 (기본 활성)
- **커스텀 텍스트**: 사용자 정의 필드 (OCR 결과, 힌트 등)

필드 추가/삭제/순서 변경이 가능하며, 설정은 자동 저장됩니다.

### 7. ZIP 다운로드

**ZIP 다운로드** 버튼을 클릭하면:
- 모든 이미지 파일 (.webp)
- Anki 가져오기용 텍스트 파일 (설정된 필드 순서로 탭 구분)
- 챕터별 분리된 텍스트 파일

## 📁 프로젝트 구조

```
├── server.py          # FastAPI 백엔드 서버
├── anki_batch.html    # React 프론트엔드 (단일 HTML)
├── temp_pdfs/         # 업로드된 PDF 임시 저장소
├── venv/              # Python 가상환경
└── README.md          # 이 파일
```

## 🔧 API 엔드포인트

| 엔드포인트 | 메서드 | 설명 |
|-----------|--------|------|
| `/` | GET | 서버 상태 확인 |
| `/upload_pdf` | POST | PDF 파일 업로드 |
| `/check_pdf_job/{job_id}` | GET | PDF 처리 상태 확인 |
| `/process_single` | POST | 단일 페이지 AI 분석 |
| `/crop_batch_items` | POST | 여러 영역 일괄 크롭 |
| `/get_page_image` | POST | 페이지 이미지 요청 |
| `/submit_batch` | POST | Batch 작업 제출 |
| `/check_batch/{batch_id}` | GET | Batch 상태 확인 |
| `/clear_temp_pdfs` | DELETE | 임시 PDF 파일 삭제 |
| `/temp_pdf_count` | GET | 임시 PDF 파일 개수 |

## ⚙️ 설정 옵션

### 공통 설정

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| Batch Size | 한 번에 처리할 페이지 수 | 1 |
| 동시 처리 | 병렬 처리 개수 | 3 |
| 화질 (DPI) | 크롭 이미지 해상도 | 300 |
| 여백 (Padding) | 크롭 영역 추가 여백 | 10 |

### 지원하는 AI Provider

1. **Google Gemini** (기본)
2. **OpenAI**
3. **OpenAI Compatible** (OpenRouter, DeepSeek 등)
   - URL 직접 지정 가능
4. **Anthropic Claude**

## 🗑️ 임시 파일 관리

서버에 업로드된 PDF는 `temp_pdfs/` 폴더에 저장됩니다.  
헤더의 **Temp (N)** 버튼을 클릭하여 임시 파일을 삭제할 수 있습니다.

## 📝 프롬프트 커스터마이징

좌측 **프롬프트** 패널에서 AI에게 전달할 지시문을 수정할 수 있습니다.  
JSON Schema를 수정하여 원하는 필드를 추가하거나 변경 가능합니다.

## 🎛️ UI 버튼 설명

### 헤더 영역

| 버튼 | 설명 |
|------|------|
| **서버 (ON/OFF)** | 서버 연결 상태 표시 (녹색=정상) |
| **Temp (N)** | 임시 PDF 파일 개수 표시, 클릭 시 삭제 |
| **시스템 보호 (ON/OFF)** | 백그라운드 탭 슬립 방지 (장시간 분석 시 사용) |

### 왼쪽 패널 - AI 엔진

| 버튼 | 설명 |
|------|------|
| **⬇️ (Download)** | 프로필 JSON 파일 가져오기 (기존 프로필에 **추가됨**) |
| **ALL ⬆️ (Upload)** | 모든 프로필 내보내기 |
| **저장** | 현재 설정을 새 프로필로 저장 |
| **1개 내보내기** | 현재 프로필만 내보내기 |
| **삭제** | 현재 프로필 삭제 |
| **+추가** (API Keys) | API 키 추가 (여러 키 순환 사용) |

### 왼쪽 패널 - 프롬프트

| 버튼 | 설명 |
|------|------|
| **⬇️ (Download)** | 프롬프트 JSON 파일 가져오기 (기존에 **추가됨**) |
| **ALL ⬆️** | 모든 프롬프트 내보내기 |
| **저장** | 현재 프롬프트 수정사항 저장 |
| **새 이름 저장** | 현재 프롬프트를 새 이름으로 복제 |
| **+ 신규** | 빈 프롬프트 생성 |

### 중앙 패널 - PDF 갤러리

| 버튼 | 설명 |
|------|------|
| **PDF 업로드** | PDF 파일 선택, 서버로 업로드 |
| **실시간 시작** | 선택된 페이지 순차 분석 |
| **중지** | 분석 중지 |
| **Batch API 전송** | 모든 페이지를 한 번에 서버로 전송 |
| **전체 선택/해제** | 갤러리 내 모든 페이지 선택/해제 토글 |

### 중앙 패널 - 설정 슬라이더

| 옵션 | 설명 |
|------|------|
| **Batch Size** | 한 번에 AI에게 전송할 페이지 수 |
| **동시 처리** | 병렬 처리 스레드 수 |
| **Paddle** | 크롭 영역 추가 여백 (상하좌우) |
| **PDF DPI** | PDF 변환 해상도 (높을수록 고화질, 느림) |
| **Crop DPI** | 크롭 이미지 해상도 |
| **Temperature** | AI 창의성 파라미터 (0=정확, 2=창의적) |

### 오른쪽 패널 - RESULT

| 버튼 | 설명 |
|------|------|
| **🔍 검색** | 결과 내 챕터명/문제번호 검색 |
| **정규식(N)** | 챕터명 그룹화용 정규식 설정 |
| **필드(N)** | Anki 필드 설정 모달 열기 |
| **선택 삭제** | 선택된 결과 항목 일괄 삭제 |
| **전체 저장** | 현재까지의 결과를 IndexedDB에 저장 |
| **전체 초기화** | 모든 결과 삭제 |
| **ZIP 다운로드** | 이미지 + 텍스트 파일 ZIP으로 저장 |

### 결과 아이템 내 버튼

| 아이콘 | 설명 |
|--------|------|
| **✂️ (가위)** | 크롭 영역 수정 모드 진입 |
| **🗑️ (휴지통)** | 해당 항목 삭제 |
| **⬆️⬇️⬅️➡️ +/-** | 크롭 영역 확장(+)/축소(-) |
| **완료** | 수정 완료 및 고화질 리크롭 |

## 🐛 문제 해결

### 서버 연결 실패
- `server.py`가 실행 중인지 확인
- 포트 8000이 다른 프로세스에서 사용 중인지 확인

### PDF 업로드 실패
- 서버 콘솔에서 오류 메시지 확인
- PDF 파일이 손상되지 않았는지 확인

### AI 분석 실패
- API 키가 유효한지 확인
- 사용량 제한(Rate Limit)에 걸렸는지 확인

</details>

<details id="en">
<summary><h2>🇺🇸 English</h2></summary>

Web application that automatically generates Anki flashcards by analyzing MCQs from PDF documents using AI.

## 📋 Key Features

- **PDF Analysis**: Automatic detection of Question and Solution from uploaded PDF files using AI
- **Image Crop**: High-quality cropping of detected areas (Default DPI: 300)
- **Batch API Support**: Send large number of pages to the server for processing at once
- **Multi-AI Provider**: Supports Google Gemini, OpenAI, Anthropic Claude, OpenRouter
- **Profile Management**: Save/Load AI settings and prompts as profiles
- **Auto-save**: Prevent data loss with IndexedDB auto-save
- **System Protection**: Prevent background tab sleep using Web Worker
- **🌐 Multi-language**: Supports Korean, English, and Chinese UI

## 🛠️ Installation

### 1. Requirements

- Python 3.8 or higher
- pip (Python package manager)

### 2. Python Virtual Environment (Recommended)

```bash
# Create venv
python -m venv venv

# Activate venv (macOS/Linux)
source venv/bin/activate

# Activate venv (Windows)
.\venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn httpx python-multipart pymupdf pillow
```

## 🚀 Usage

### 1. Easy Start (One-Click)

| OS | Method |
|----|------|
| **macOS/Linux** | Double-click `start.sh` |
| **Windows** | Double-click `start.bat` |

> The server will start automatically, and the app will open in your browser.

### 2. Manual Start

Once the server is running, the API is available at `http://localhost:8000`.

### 3. Open Web Interface

Open `anki_batch.html` in your browser.

```bash
# macOS
open anki_batch.html

# Windows
start anki_batch.html

# Linux
xdg-open anki_batch.html
```

### 4. Setup API Keys

1. Select a Provider (Gemini, OpenAI, Anthropic, etc.) in the **AI Engine** panel on the left.
2. Enter your API Key.
3. Save as a profile for reuse if needed.

### 5. PDF Analysis

1. Click **PDF Upload** to select a PDF file.
2. Pages will be converted and displayed in the gallery.
3. Click **Start Realtime** or **Send Batch API**.
   - **Start Realtime**: Analyze pages one by one (Realtime progress monitoring)
   - **Send Batch API**: Send all pages to server and check results later

### 6. Edit Results

- Use the **Scissors** icon on a result item to edit the crop area.
  - **Click** arrow buttons: Adjust once
  - **Hold** arrow buttons: Continuous adjustment (Fast edit)
  - **Shift + Click/Hold**: Adjust at 5x speed
- Use the **Trash** icon to delete validation items.
- Batch delete selected results.
- Edit other items while high-quality processing is running in background.

### 7. Anki Field Settings

Click the **Fields (N)** button in the RESULT panel to customize Anki card fields:

- **Question Image**: Capture question area (Default: Enabled)
- **Solution Image**: Capture solution area (Default: Enabled)
- **Chapter/Tag**: Chapter name (Default: Enabled)
- **Custom Text**: User-defined field (OCR results, Hints, etc.)

You can Add/Delete/Reorder fields, and settings are auto-saved.

### 8. ZIP Download

Clicking **ZIP Download** button will download:
- All image files (.webp)
- Anki Import Text File (Tab-separated values)
- Chapter-separated text files

## 📁 Project Structure

```
├── server.py          # FastAPI Backend Server
├── anki_batch.html    # React Frontend (Single HTML)
├── temp_pdfs/         # Temporary PDF storage
├── venv/              # Python Virtual Environment
└── README.md          # This file
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|-----------|--------|------|
| `/` | GET | Check Server Status |
| `/upload_pdf` | POST | Upload PDF File |
| `/check_pdf_job/{job_id}` | GET | Check PDF Processing Status |
| `/process_single` | POST | Analyze Single Page |
| `/crop_batch_items` | POST | Batch Crop Items |
| `/get_page_image` | POST | Request Page Image |
| `/submit_batch` | POST | Submit Batch Job |
| `/check_batch/{batch_id}` | GET | Check Batch Status |
| `/clear_temp_pdfs` | DELETE | Delete Temporary PDFs |
| `/temp_pdf_count` | GET | Count Temporary PDFs |

## ⚙️ Configuration

### Common Settings

| Option | Description | Description | Default |
|------|------|--------|
| Batch Size | Pages to process at once | 1 |
| Concurrency | Number of parallel threads | 3 |
| DPI | Crop Image Resolution | 300 |
| Padding | Extra margin for crop area | 10 |

### Supported AI Providers

1. **Google Gemini** (Default)
2. **OpenAI**
3. **OpenAI Compatible** (OpenRouter, DeepSeek, etc.)
   - Custom URL support
4. **Anthropic Claude**

## 🗑️ Temporary File Management

Uploaded PDFs are stored in `temp_pdfs/`.  
Click the **Temp (N)** button in the header to clean up files.

## 📝 Prompt Customization

You can modify instructions sent to AI in the **Prompt** panel on the left.  
Modify JSON Schema to add or change output fields.

## 🎛️ UI Buttons

### Header Area

| Button | Description |
|------|------|
| **Server (ON/OFF)** | Server Status (Green=OK) |
| **Temp (N)** | Temp PDF count, Click to delete |
| **System Protection** | Prevent background tab sleep |

### Left Panel - AI Engine

| Button | Description |
|------|------|
| **⬇️ (Download)** | Import Profile JSON (Adds to existing) |
| **ALL ⬆️ (Upload)** | Export All Profiles |
| **Save** | Save current settings as new profile |
| **Export 1** | Export current profile |
| **Delete** | Delete current profile |
| **+Add** (API Keys) | Add API Key (Round-robin usage) |

### Left Panel - Prompt

| Button | Description |
|------|------|
| **⬇️ (Download)** | Import Prompt JSON |
| **ALL ⬆️** | Export All Prompts |
| **Save** | Save changes |
| **Save As New** | Clone current prompt |
| **+ New** | Create empty prompt |

### Center Panel - PDF Gallery

| Button | Description |
|------|------|
| **PDF Upload** | Select and upload PDF |
| **Start Realtime** | Analyze pages sequentially |
| **Stop** | Stop analysis |
| **Send Batch API** | Send all pages to server |
| **Select All/None** | Toggle selection |

### Center Panel - Sliders

| Option | Description |
|------|------|
| **Batch Size** | Pages per request |
| **Concurrency** | Thread count |
| **Paddle** | Padding (Top/Bottom/Left/Right) |
| **PDF DPI** | PDF conversion resolution |
| **Crop DPI** | Crop image resolution |
| **Temperature** | AI Creativity (0=Precise, 2=Creative) |

### Right Panel - RESULT

| Button | Description |
|------|------|
| **🔍 Search** | Search Chapter/Number |
| **Regex (N)** | Regex for Chapter Grouping |
| **Fields (N)** | Open Anki Field Settings |
| **Delete Selected** | Delete selected items |
| **Reset** | Delete all results |
| **ZIP Download** | Download Images + Text |

</details>

<details id="zh">
<summary><h2>🇨🇳 中文 (Chinese)</h2></summary>

使用AI分析PDF文档中的选择题(MCQ)并自动生成Anki抽认卡的Web应用程序。

## 📋 主要功能

- **PDF分析**：上传PDF文件，AI自动检测问题(Question)和解答(Solution)
- **图像裁剪**：高质量裁剪检测区域（默认DPI：300）
- **Batch API支持**：一次性将大量页面发送到服务器进行处理
- **多AI提供商**：支持Google Gemini, OpenAI, Anthropic Claude, OpenRouter
- **配置文件管理**：保存/加载AI设置和提示词配置
- **自动保存**：通过IndexedDB自动保存，防止数据丢失
- **系统保护**：使用Web Worker防止后台标签页休眠
- **🌐 多语言支持**：支持韩语、英语、中文界面

## 🛠️ 安装方法

### 1. 必需环境

- Python 3.8 或更高版本
- pip (Python 包管理器)

### 2. Python 虚拟环境设置 (推荐)

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境 (macOS/Linux)
source venv/bin/activate

# 激活虚拟环境 (Windows)
.\venv\Scripts\activate
```

### 3. 安装依赖

```bash
pip install fastapi uvicorn httpx python-multipart pymupdf pillow
```

## 🚀 使用方法

### 1. 快速启动 (一键)

| 操作系统 | 方法 |
|----|------|
| **macOS/Linux** | 双击 `start.sh` |
| **Windows** | 双击 `start.bat` |

> 服务器将自动启动，浏览器将打开应用程序。

### 2. 手动启动

服务器运行后，API将在 `http://localhost:8000` 上可用。

### 3. 打开 Web 界面

在浏览器中打开 `anki_batch.html` 文件。

```bash
# macOS
open anki_batch.html

# Windows
start anki_batch.html

# Linux
xdg-open anki_batch.html
```

### 4. 设置 API 密钥

1. 在左侧 **AI 引擎** 面板中选择提供商 (Gemini, OpenAI, Anthropic 等)。
2. 输入 API 密钥。
3. 如果需要，保存为配置文件以便重复使用。

### 5. PDF 分析

1. 点击 **PDF 上传** 按钮选择 PDF 文件。
2. 页面转换后将显示在图库中。
3. 点击 **开始实时** 或 **发送 Batch API** 按钮。
   - **开始实时**：逐页分析（实时监控进度）
   - **发送 Batch API**：将所有页面发送到服务器，稍后查看结果

### 6. 结果编辑

- 使用结果项上的 **剪刀** 图标编辑裁剪区域。
  - **点击** 方向键：调整一次
  - **按住** 方向键：连续调整（快速编辑）
  - **Shift + 点击/按住**：5倍速度调整
- 使用 **垃圾桶** 图标删除不需要的项目。
- 可以批量删除选定的结果。
- 在后台进行高质量转换时，可以编辑其他项目。

### 7. Anki 字段设置

点击结果面板中的 **字段(N)** 按钮自定义 Anki 卡片字段：

- **问题图片**：捕获问题区域（默认：启用）
- **解答图片**：捕获解答区域（默认：启用）
- **章节/标签**：章节名称（默认：启用）
- **自定义文本**：用户定义的字段（OCR结果、提示等）

可以添加/删除/重新排序字段，设置将自动保存。

### 8. ZIP 下载

点击 **ZIP 下载** 按钮将下载：
- 所有图片文件 (.webp)
- Anki 导入文本文件（制表符分隔）
- 按章节分离的文本文件
- 确保正则分组正确应用

## 📁 项目结构

```
├── server.py          # FastAPI 后端服务器
├── anki_batch.html    # React 前端 (单文件 HTML)
├── temp_pdfs/         # 临时 PDF 存储
├── venv/              # Python 虚拟环境
└── README.md          # 本文件
```

## 🔧 API 端点

| 端点 | 方法 | 说明 |
|-----------|--------|------|
| `/` | GET | 检查服务器状态 |
| `/upload_pdf` | POST | 上传 PDF 文件 |
| `/check_pdf_job/{job_id}` | GET | 检查 PDF 处理状态 |
| `/process_single` | POST | 分析单页 |
| `/crop_batch_items` | POST | 批量裁剪项目 |
| `/get_page_image` | POST | 获取页面图像 |
| `/submit_batch` | POST | 提交批处理作业 |
| `/check_batch/{batch_id}` | GET | 检查批处理状态 |
| `/clear_temp_pdfs` | DELETE | 删除临时 PDF 文件 |
| `/temp_pdf_count` | GET | 临时 PDF 文件计数 |

## ⚙️ 配置选项

### 通用设置

| 选项 | 说明 | 默认值 |
|------|------|--------|
| Batch Size | 一次处理的页面数 | 1 |
| 并发处理 | 并行线程数 | 3 |
| DPI | 裁剪图像分辨率 | 300 |
| Padding | 裁剪区域额外边距 | 10 |

### 支持的 AI 提供商

1. **Google Gemini** (默认)
2. **OpenAI**
3. **OpenAI Compatible** (OpenRouter, DeepSeek 等)
   - 支持自定义 URL
4. **Anthropic Claude**

## 🗑️ 临时文件管理

上传的 PDF 存储在 `temp_pdfs/` 中。  
点击标题栏的 **Temp (N)** 按钮可清除文件。

## 📝 提示词自定义

您可以在左侧 **提示词** 面板中修改发送给 AI 的指令。  
修改 JSON Schema 以添加或更改输出字段。

## 🎛️ UI 按钮说明

### 顶部区域

| 按钮 | 说明 |
|------|------|
| **服务器 (ON/OFF)** | 服务器连接状态 (绿色=正常) |
| **Temp (N)** | 临时 PDF 计数，点击删除 |
| **系统保护** | 防止后台标签页休眠 |

### 左侧面板 - AI 引擎

| 按钮 | 说明 |
|------|------|
| **⬇️ (Download)** | 导入配置文件 JSON (添加到现有) |
| **ALL ⬆️ (Upload)** | 导出所有配置 |
| **保存** | 将当前设置保存为新配置 |
| **导出 1** | 仅导出当前配置 |
| **删除** | 删除当前配置 |
| **+添加** (API Keys) | 添加 API 密钥 (轮询使用) |

### 左侧面板 - 提示词

| 按钮 | 说明 |
|------|------|
| **⬇️ (Download)** | 导入提示词 JSON |
| **ALL ⬆️** | 导出所有提示词 |
| **保存** | 保存更改 |
| **另存为新** | 克隆当前提示词 |
| **+ 新建** | 创建空提示词 |

### 中间面板 - PDF 图库

| 按钮 | 说明 |
|------|------|
| **PDF 上传** | 选择并上传 PDF |
| **开始实时** | 顺序分析页面 |
| **停止** | 停止分析 |
| **发送 Batch API** | 将所有页面发送到服务器 |
| **全选/取消** | 切换选择 |

### 中间面板 - 设置滑块

| 选项 | 说明 |
|------|------|
| **Batch Size** | 每次请求的页面数 |
| **并发数** | 线程数 |
| **Paddle** | Padding (上/下/左/右) |
| **PDF DPI** | PDF 转换分辨率 (越高越清晰，越慢) |
| **Crop DPI** | 裁剪图像分辨率 |
| **Temperature** | AI 创造性 (0=精确, 2=创意) |

### 右侧面板 - 结果

| 按钮 | 说明 |
|------|------|
| **🔍 搜索** | 搜索章节/编号 |
| **正则 (N)** | 章节分组正则设置 |
| **字段 (N)** | 打开 Anki 字段设置 |
| **删除选中** | 批量删除选中项 |
| **重置** | 删除所有结果 |
| **ZIP 下载** | 下载图片 + 文本 |

</details>
