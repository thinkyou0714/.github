# Contributing to thinkyou0714 projects

ようこそ! このガイドは [thinkyou0714](https://github.com/thinkyou0714) アカウントの**全リポジトリ共通**の contribution guideline です。リポジトリ固有の内容は各リポの `CONTRIBUTING.md` を優先してください。

## Quick start

1. **Issues を先に確認** — 既に同じ提案・bug 報告がないかチェック
2. **Discussion で議論** — 大きな変更は PR 前に Discussion で意図を共有
3. **Fork → branch → PR** — `main` への直接 push は避ける
4. **Conventional Commits** — commit message は `feat:` / `fix:` / `docs:` / `chore:` 形式
5. **テスト追加** — code change には対応するテストを必ず追加

## PR ガイドライン

- **小さく、レビューしやすく** — 1 PR = 1 concern (機能追加と refactor は分ける)
- **タイトルは Conventional Commits 形式** — `feat(scope): description`
- **Description には Why** — 何を変えたかではなく、なぜ変えたか
- **Test plan を含める** — どう動作確認したか箇条書きで
- **Draft PR OK** — early feedback が欲しい場合は draft で出す

## Commit message

```
<type>(<scope>): <subject>

<body — optional>

<footer — optional, e.g. "Closes #123">
```

| Type | 用途 |
|---|---|
| `feat` | 新機能 |
| `fix` | bug 修正 |
| `docs` | ドキュメントのみ |
| `style` | フォーマット (機能変更なし) |
| `refactor` | 機能変更なしのコード整理 |
| `perf` | パフォーマンス改善 |
| `test` | テスト追加・修正 |
| `chore` | ビルド・補助ツール |
| `ci` | CI 設定変更 |

## Code style

- **TypeScript / JavaScript**: ESLint + Prettier (各リポの設定を尊重)
- **Python**: ruff (default config)
- **Shell**: shellcheck pass

## Issue を立てる前に

1. [Discussions](https://github.com/thinkyou0714) で類似質問を検索
2. 該当リポの README / docs を確認
3. それでも解決しないなら Issue template に沿って作成

## Code of Conduct

[Contributor Covenant v2.1](./CODE_OF_CONDUCT.md) に準拠します。

## Questions?

- GitHub Discussions (リポ別)
- X: [@thinkyou0714](https://twitter.com/) (TODO: account setup)
- Email: 公開アドレスなし — Issues か Discussions 経由でお願いします
