# =============================================================================
# local-rag-poc アプリ（Streamlit UI）用イメージ
# ベースは仕様書 §3/§4 の確定構成に合わせて python:3.11-slim
# =============================================================================
FROM python:3.11-slim

# ログを docker compose logs で即時確認できるようにバッファリングを無効化。
# .pyc とホイールキャッシュはイメージ肥大の原因になるだけなので抑止する
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 依存インストールをソースコピーより先に行い、ソース変更時にも
# インストール済みレイヤーのキャッシュが効くようにする
COPY requirements.txt ./

# torch だけ先に CPU 版を明示インストールする。
# 理由: Linux の既定 wheel は CUDA 同梱で数GBイメージが膨らむが、この構成では
# LLM 推論は ollama コンテナが担い、app 側（埋め込み・再ランク）は CPU で
# 受入基準を満たせる想定のため（仕様書 §3: CPU-only 完走を既定とする）。
# app コンテナでも GPU を使いたい場合は下の 1 行目を削除すれば
# requirements.txt 経由で CUDA 版 torch が入る（docker-compose.yml の
# app に GPU の deploy: 節を追加することも忘れないこと）
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install -r requirements.txt

# data/ はイメージへ焼き込まない（docker-compose.yml でバインドマウントする）。
# corpus やベクタDBをイメージに含めると、資料の入れ替えのたびに再ビルドが
# 必要になるうえ、取り込み資料がイメージ配布経路に乗るリスクもあるため
COPY src/ ./src/
COPY eval/ ./eval/

# Streamlit の既定ポート（docker-compose.yml の公開ポートと合わせる）
EXPOSE 8501

# 0.0.0.0 バインドはコンテナ外（ホストのブラウザ）から届くために必須。
# headless はブラウザ自動起動の抑止（コンテナ内にブラウザは無い）
CMD ["streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]
