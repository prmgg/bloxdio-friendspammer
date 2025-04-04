# 重要な注意事項 

### 1. 3PSIDMCSP の値 
- `3PSIDMCSP` の値は **動的** であり、定期的に変更されます。
- したがって、420 ​​エラーが発生した場合は、bloxd io にアクセスして最新の値を直接取得し、置き換えてください。

### 2. アカウントの有効期限 
- アカウントには有効期限があります。
- スクリプトを実行する前に、アカウントがアクティブであることを確認してください。定期的にアカウントを更新または切り替える必要がある場合があります。

## インストール 

### 1. Geckodriver のインストール 
このプロジェクトが動作するには、Geckodriver が必要です。以下の手順に従ってください。

#### Windows の場合 
1. [Mozilla Geckodriver Releases](https://github.com/mozilla/geckodriver/releases) から最新の Geckodriver をダウンロードします。

2. ダウンロードしたファイルを解凍します。
 3. システムの `PATH` 環境変数に Geckodriver ディレクトリを追加します。

#### macOS の場合
```bash
brew install geckodriver
