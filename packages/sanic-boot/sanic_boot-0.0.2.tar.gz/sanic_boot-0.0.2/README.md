![sanic-framework-boot-logo-400x93.png](sanic-framework-boot-logo-400x93.png)

# Sanic Boot

Sanic Boot 基于 Sanic 框架，为开发者提供与 Spring Boot 类似的装饰器，便于路由系统、模型类的自动装配与配置。

## Sanic | Build fast. Run fast.

Sanic is a Python 3.9+ web server and web framework that's written to go fast. It allows the usage of the `async/await` syntax added in
Python
3.5, which makes your code non-blocking and speedy.

## 安装

``pip install sanic-boot``

## Hello World Example

```python
from sanic_boot import sanicBoot
import sanic

app = sanicBoot(__name__)


# 使用 sanic 自带的装饰器仍然有效
@app.get("/")
def index(request):
    return sanic.response.text("hello")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088, debug=True, auto_reload=True)

```

### 1. Create NORMAL route by common function (which can be with `async`)

```python
from sanic import Request, text
from sanic_boot import GetMapping


# 面向函数
@GetMapping('/index')
async def index(request: Request):
    return text('Hello')
```

### 2. Create Router View from class, which just collect the route -- A simple method instead of blueprint

```python
from sanic import Request, text, json
from sanic_boot import Controller, GetMapping, RequestMapping


# 面向类
@Controller('/person')
class PersonController:
    # 使用 Views 装饰器后，若发现目标未继承自 HTTPMethodView、BaseView 中的任何一个，将会修改基类为 BaseView
    @RequestMapping('/login')
    class Login:
        async def get(self, request: Request):
            return text('the route is /person/login')

    # 除视图外，还可以使用普通方法构造路由
    @GetMapping('/logout')
    async def logout(self, request: Request):
        return json({
            'code': 200,
            'data': '退出登录'
        })
```

### 3. Create Task by decorator `Task`, which can get a parameter named `name` or `taskName`. The only parameter is `None` as value.

```python
import asyncio
from sanic import Sanic
from sanic_boot import Task


@Task(name='')  # name 或 taskName 默认为 None
async def gen(app: Sanic):
    while True:
        print([item for item in range(10)])
        await asyncio.sleep(5000)
```

## Decorator Description

+ `@Controller (uri : str)`
  > 装饰器 `Controller` 意在收集目标注解对象内部注册的路由，是 `sanic` 框架中 `blueprint` 蓝图系统的自动化实现。
  >
  > `@Controller`允许不带任何参数，此时将自动分配路由，分配的路由与目标注解的类名有关，故类名推荐的格式为 `^[A-Z][A-Za-z0-9*]Controller$`
  ，（即大写字母开头的有意义单词，并以 Controller
  > 结尾），分配所得路由为全小写且不带 `Controller`。如 `TestController` 的路由为 `test`，`TestTest2Controller` 的路由为 `test-test2`
  >
  > _注意_: 若最终注册的路由存在重复将会造成**路由冲突**。

+ `@RequestMapping(uri : str, methods: list[RequestMethod] | RequestMethod | None = None)`
  > 使用 `RequestMapping` 时若注解对象是一个视图类，则第二个参数可不必填写，`sanic` 路由系统将会根据视图类的方法自动分配路由方法。装饰器
  `RequestMapping` 是 `sanic` 框架中类视图注册方法 `app.add_route (Class.as_view, routeString)` 的自动化实现。
+ `@[Get|Post|Head|Put|Delete|Patch|Options]Mapping(uri : str)`
  > `@GetMapping (uri : str)` 等装饰器是 `@RequestMapping ('/login', RequestMethod.GET)` 的简便写法。
+ `@Task(name : str = None)`
  > 在 Tasks 目录下注册任务事件。