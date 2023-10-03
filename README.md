## Chat-Meow-ESP32

| Python | v3.10                                              |
|--------|----------------------------------------------------|
| 逆向库    | [revchatgpt](https://github.com/acheong08/ChatGPT) |

> pyopenjtalk库似乎只能在Python3.10上安装成功，此库只影响日语生成

### 环境安装

```commandline
pip install -r requirements.txt 
```

如果不存在配置文件的话，第一次运行会生成配置文件

```commandline
python server.py
```

### 配置参数

需要先配置OpenAI登录信息，在文件`openai.ini`中

配置access_token

- 这是实际用于身份验证的内容喵，可以在https://chat.openai.com/api/auth/session找到
- 2周后失效
- 推荐的身份验证方法
- 如果您登录到https://chat.openai.com/，然后转到https://chat.openai.com/api/auth/session，就可以找到

或者配置email(邮箱) password(密码)字段
> 只需配置access_token(推荐)或者是email&password, 如果都配置了，优先使用access_token

你需要准备一个Vits模型文件，测试用模型可以在Release处下载，仅供参考
模型文件(*.pth config.json)放入根目录model(可改)文件夹里面，同时需要在config.ini中填入对应的文件名称

### 启动测试服务器

```commandline
python main.py
```

### 开始测试服务器

- 开始运行后，将启动默认端口8000的服务器
- /upload接口支持POST方法，和ESP32配置项目`Server URL to send data`对应
- 完成tts，vits后在static目录生成out.wav文件，和ESP32配置项目`Server FILE URL to play voice`对应

### 即将支持

- 一个网页界面来配置参数
- 支持RockChinQ大佬的free-one-api接口

