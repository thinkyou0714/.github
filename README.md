# .github — thinkyou0714 community health files

このリポジトリは [thinkyou0714](https://github.com/thinkyou0714) アカウントの**全リポジトリに適用される community health files** を集約する特別なリポジトリです。

GitHub の `.github` リポジトリ機構により、各リポジトリで該当ファイルが定義されていない場合、ここに置かれたファイルが**フォールバックとして自動適用**されます。

## 提供している default files

| File | 目的 |
|---|---|
| `FUNDING.yml` | リポ右上の Sponsor ボタンに表示される funding link |
| `CONTRIBUTING.md` | コントリビューションガイドライン |
| `CODE_OF_CONDUCT.md` | Contributor Covenant v2.1 |
| `SECURITY.md` | 脆弱性報告先 |
| `SUPPORT.md` | ユーザサポート窓口 |
| `ISSUE_TEMPLATE/` | Issue テンプレ (bug / feature / question) と contact links の fallback |
| `PULL_REQUEST_TEMPLATE.md` | PR テンプレ |

## 上書き

個別リポジトリで同名ファイルを定義すると、そちらが優先されます。
たとえば `thinkyou0714/ccmux/CONTRIBUTING.md` があれば、`ccmux` ではそれが使われ、本リポの `CONTRIBUTING.md` は無視されます。

## ライセンス

ドキュメント類は [CC0 1.0 Universal](https://creativecommons.org/publicdomain/zero/1.0/) 相当 — 自由に流用してください。

## 参考

- [GitHub Docs — Creating a default community health file](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/creating-a-default-community-health-file)


## 運用メモ

この default ファイル群は汎用のフォールバックです。
対象リポジトリで要件（例: セキュリティ連絡先、サポート窓口、テンプレ項目）が異なる場合は、必要に応じて各リポジトリで上書きしてください。
