# Django说明

## 结构

https://www.django-rest-framework.org/

- `backend/urls.py`
    - `urlpatterns` 所有的入口路径
        - `backend/user/`
        - `backend/file/`
        - `backend/problem/`
        - `backend/submission/`
        - `backend/news/`
        - `backend/discussion/`
    - `settings` 不同环境的设置

---

- `backend/judge/`
- `backend/utilities/`
- `backend/test/`

---

- `backend/venv/` 临时的Python虚拟环境
- `backend/storage/`

## 手动测试API

用`curl`请求API可以拿到公共的数据

```
$ curl http://166.111.223.67:40000/oj/api/news/
[{"id":1,"title":"来自40000端口的后端测试","create_time":"2022-07-11T11:40:15.501112+08:00","content":"hhhhh","related_files":[]}]
```

或者使用`coreapi`

```
$ pip install coreapi
$ coreapi get http://166.111.223.67:40000/oj/api/docs/

$ coreapi action submission-results read -p id=33
{
    "id": 33,
    "result": "Accepted",
    "status": "DONE",
    "possible_failure": "NONE",
    "submit_time": "2022-07-13T09:42:45.667108+08:00",
    "grade": 10,
    "submission": 30,
    "testcase": 15
}
```

TODO 需要考虑如何在命令行工具中添加csrftoken 以查看特定权限的数据域

## 例子

查看[公告数据结构](./news/README.md)
