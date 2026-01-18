# Shadowing Practice App

英語のシャドーイング練習アプリケーション。YouTube動画やPDFを教材として取り込み、AI評価付きで練習できます。

## 機能

- **教材取り込み**
  - YouTube URLから動画/音声をダウンロード
  - PDFの音読機能（TTS生成）
  - ローカルファイル（MP3/MP4/WAV）の読み込み

- **シャドーイング練習**
  - 音声再生（速度調整可能: 0.5x〜1.5x）
  - スクリプト（字幕）表示
  - ユーザー音声の録音
  - 波形表示

- **自動評価・添削**
  - Whisperで録音を文字起こし
  - LLM（Ollama/Claude）で発音・タイミング評価
  - 改善ポイントのフィードバック

## 必要条件

- Python 3.11+
- Node.js 20+
- FFmpeg
- Ollama（オプション、LLM評価用）

## プロジェクト構成

```
ShadowingApp/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPIエントリーポイント
│   │   ├── config.py            # 設定管理
│   │   ├── database.py          # DB接続
│   │   ├── models/              # SQLAlchemyモデル
│   │   ├── routers/             # APIエンドポイント
│   │   └── services/            # ビジネスロジック
│   ├── data/                    # ローカルデータ保存
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── components/          # Reactコンポーネント
│       ├── api/                 # APIクライアント
│       ├── stores/              # Zustand状態管理
│       └── App.tsx
├── scripts/
│   └── setup.ps1                # セットアップスクリプト
└── README.md
```

## セットアップ

### 自動セットアップ（Windows）

```powershell
.\scripts\setup.ps1
```

### 手動セットアップ

#### バックエンド

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### フロントエンド

```powershell
cd frontend
npm install
```

## 起動

### バックエンド

```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

または仮想環境を直接指定:

```powershell
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
```

バックエンドは http://localhost:8000 で起動します。

### フロントエンド

```powershell
cd frontend
npm run dev
```

フロントエンドは http://localhost:5173 で起動します。

## アクセス

| URL | 説明 |
|-----|------|
| http://localhost:5173 | フロントエンド（メインUI） |
| http://localhost:8000 | バックエンドAPI |
| http://localhost:8000/docs | APIドキュメント（Swagger UI） |
| http://localhost:8000/redoc | APIドキュメント（ReDoc） |

## 技術スタック

### バックエンド
| 機能 | ライブラリ |
|-----|-----------|
| Webフレームワーク | FastAPI |
| ORM | SQLAlchemy + SQLite |
| YouTube DL | yt-dlp |
| 音声認識 | faster-whisper |
| TTS | edge-tts |
| PDF処理 | PyMuPDF |

### フロントエンド
| 機能 | ライブラリ |
|-----|-----------|
| UIフレームワーク | React + TypeScript |
| ビルドツール | Vite |
| スタイリング | Tailwind CSS |
| 波形表示 | WaveSurfer.js |
| 状態管理 | Zustand |
| APIクライアント | TanStack Query |

## LLM評価設定

### Ollama（ローカル）

```powershell
winget install Ollama.Ollama
ollama pull llama3.2
```

### Claude API（クラウド）

`backend/.env`ファイルを作成:

```
CLAUDE_API_KEY=your_api_key_here
LLM_PROVIDER=claude
```

## API概要

### 教材管理
- `GET /api/materials` - 教材一覧
- `GET /api/materials/{id}` - 教材詳細
- `POST /api/materials/youtube` - YouTube取込
- `POST /api/materials/pdf` - PDF取込
- `DELETE /api/materials/{id}` - 教材削除

### 練習
- `GET /api/segments/{id}/audio` - セグメント音声取得
- `POST /api/segments/{id}/practice` - 録音アップロード

### 評価
- `POST /api/practice/{id}/evaluate` - AI評価実行

## ライセンス

MIT
