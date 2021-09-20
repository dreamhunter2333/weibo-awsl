# weibo 爬虫

自动爬取某个微博博主转发的微博，根据关键词匹配，记录匹配到的微博的图片

创建 .env 文件

```env
uid=微博博主 id(打开博主主页 url 即可见到)
cookie_alc=删除微博 cookie 中的 SUB，刷新访问 weibo.com 请求记录中搜索 ALC=
keyword=xxx(关键词)
max_page=10(爬取的最大页数)
dbpath=db/data.db(数据库地址)
ttl_time=600(爬取频率)
```
