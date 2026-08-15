# DiscordBotForOsu
OSUの譜面URLから譜面メタデータを取得し表示するDiscordBot

その他 DiscordBotコマンド

## osu api

1. osu! api を利用するには OAuth のアクセストークンが必要
2. アクセストークンの取得にはマイページから見れるクライアントIDとクライアントシークレットが必要

https://osu.ppy.sh/oauth/token に以下のデータを POST
```
'client_id': クライアントID,
'client_secret': クライアントシークレット,
'grant_type': 'client_credentials',
'scope': 'public'
```
アクセストークンとトークンの有効期限が返ってくる

## Discord bot

3. Discord Bot はサイトでボットを作成してボットトークンを取得して使う

## 機密情報の置き場所
.env ファイルにトークンなどのデータは書いてる

時代遅れらしい