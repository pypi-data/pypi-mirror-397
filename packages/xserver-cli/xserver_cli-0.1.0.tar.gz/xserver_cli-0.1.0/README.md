# xserver-cli

XServerをコマンドラインから操作するための非公式ツールです。

## インストール

```bash
pip install xserver-cli
```

## 使い方

### ログイン

```bash
xserver login
```

### DNS

```bash
# リスト表示
xserver dns
# 追加
xserver dns add --type A --name www --content 127.0.0.1
# 削除
xserver dns delete --type A --name www
```

### アクセスログ

```bash
# 初期ドメイン
xserver access-log
# 独自ドメイン
xserver access-log --domain <your-domain>
```

### メールアカウント

```bash
# リスト表示
xserver mail
# 追加
xserver mail add --name <your-name> --password <your-password>
# 削除
xserver mail delete --name <your-name>
```

### FTPアカウント

```bash
# リスト表示
xserver ftp
# 追加
xserver ftp add --name <your-name> --password <your-password>
# 削除
xserver ftp delete --name <your-name>
```

### データベース

```bash
# リスト表示
xserver database
# 追加
xserver database create --name <your-name>
# 削除
xserver database drop --name <your-name>
```

### MySQLユーザー

```bash
# リスト表示
xserver mysql-user
# 追加
xserver mysql-user add --name <your-name> --password <your-password>
# 削除
xserver mysql-user delete --name <your-name>
```

### PHPバージョン

```bash
# リスト表示
xserver php-version
# 追加
xserver php-version change --version <your-version>
```

### ドメイン

```bash
# リスト表示
xserver domain
# 追加
xserver domain add --domain <your-domain>
# 削除
xserver domain delete --domain <your-domain>
```

### サブドメイン

```bash
# リスト表示
xserver subdomain
# 追加
xserver subdomain add --subdomain <your-subdomain>
# 削除
xserver subdomain delete --subdomain <your-subdomain>
```

### SSL

```bash
# リスト表示
xserver ssl
# ON
xserver ssl on --domain <your-domain>
# OFF
xserver ssl off --domain <your-domain>
```

### アクセス解析

```bash
# リスト表示
xserver analytics
# ON
xserver analytics on --domain <your-domain>
# OFF
xserver analytics off --domain <your-domain>
```

### エラーログ

```bash
# 初期ドメイン
xserver error-log
# 独自ドメイン
xserver error-log --domain <your-domain>
```

### Xアクセラレータ

```bash
# リスト表示
xserver accelerator
# ON(v1)
xserver accelerator on --domain <your-domain> --v1
# ON(v2)
xserver accelerator on --domain <your-domain> --v2
# OFF
xserver accelerator off --domain <your-domain>
```

### サーバーキャッシュ

```bash
# リスト表示
xserver server-cache
# ON
xserver server-cache on --domain <your-domain>
# OFF
xserver server-cache off --domain <your-domain>
```

### ブラウザキャッシュ

```bash
# リスト表示
xserver browser-cache
# ON(all)
xserver browser-cache on --domain <your-domain> --all
# ON(CSS/JS以外)
xserver browser-cache on --domain <your-domain> --exclude-css-js
# OFF
xserver browser-cache off --domain <your-domain>
```

### WAF

```bash
# リスト表示
xserver waf
# ON
xserver waf xss on --domain <your-domain>
# OFF
xserver waf xss off --domain <your-domain>
# ON
xserver waf sql on --domain <your-domain>
# OFF
xserver waf sql off --domain <your-domain>
# ON
xserver waf file on --domain <your-domain>
# OFF
xserver waf file off --domain <your-domain>
# ON
xserver waf mail on --domain <your-domain>
# OFF
xserver waf mail off --domain <your-domain>
# ON
xserver waf command on --domain <your-domain>
# OFF
xserver waf command off --domain <your-domain>
# ON
xserver waf php on --domain <your-domain>
# OFF
xserver waf php off --domain <your-domain>
```

### SSH鍵

```bash
# リスト表示
xserver ssh-key
# 追加
xserver ssh-key add --key <your-key>
# 削除
xserver ssh-key delete --key <your-key>
```

### Cron

```bash
# リスト表示
xserver cron
# 追加
xserver cron add --command <your-command>
# 削除
xserver cron delete --command <your-command>
```

### 無料VPS

```bash
# リスト表示
xserver free-vps
# 状態表示
xserver free-vps status --name <your-name>
# 作成
xserver free-vps create --name <your-name>
# 削除
xserver free-vps delete --name <your-name>
```

### 静的コンテンツ

```bash
# リスト表示
xserver static
# 追加
xserver static add --name <your-name>
# 削除
xserver static delete --name <your-name>
```

### ゲーム

```bash
# リスト表示
xserver game
# 追加
xserver game add --name <your-name> --game <your-game>
# 削除
xserver game delete --name <your-name>
```

### クラウドストレージ

```bash
# リスト表示
xserver drive
# 追加
xserver drive add --name <your-name>
# 削除
xserver drive delete --name <your-name>
```
