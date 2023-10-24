# FastAPI-TGDiceSQL

A FastAPI Application use to crud `TGBotDiceNodeJS` Mysql.

## Docker deploy

```shell
docker run -d --name=TGDiceAPI \
-v /wfwork/FastAPI-TGMonitor/:/app/ \
-e PORT="80" \
-e APP_MODULE="app.main:app" \
-e DATABASE_URI="mysql+aiomysql://root:lovehyy@mariadb/tgbotdice?charset=utf8mb4" \
-p 9810:80 \
--network frontend \
tgfastapi
```
