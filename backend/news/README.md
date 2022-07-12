# 快速上手开发

## 结构

- `urls.py`
    - 指定在`backend/urls.py`的总url`api/`下继续延伸的url`news`
- `models.py`
    - 定义数据结构
- `views.py`
    - 定义如何获取/修改数据
- `serializers.py`
    - https://www.django-rest-framework.org/
    - 

---

- `admin.py`
    - 将该数据放入`admin-django`的后台管理中
- `apps.py`

## 部署之后本地测试

```
$ curl http://166.111.223.67:40000/oj/api/news/
[{"id":1,"title":"来自40000端口的后端测试","create_time":"2022-07-11T11:40:15.501112+08:00","content":"hhhhh","related_files":[]}]
```
