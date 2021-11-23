# weibo 爬虫

本爬虫仅供学习交流，请不要非法使用（后果自负

自动爬取某个微博博主转发的微博，根据关键词匹配，记录匹配到的微博的图片

创建 .env 文件

```env
cookie_sub=xxx
max_page=10(爬取的最大页数)
db_url=mysql+mysqlconnector://xxx:xxx/xxx(数据库地址)
broker=redis://:xxx@localhost:6379/0(数据库地址)
```
