# 想不出名字

## 简介

工作中经常需要使用堡垒机/跳板机来登录生产环境中的服务器，逐级进行不厌其烦的文件拷贝。所以就写了这么个东西。

这是一个简单的脚本，利用配置文件配置好主机信息，以及对应的跳转关系之后，在相关主机中用 screen/tmux 运行该脚本，这一脚本会自动监控 task 文件夹中的任务。一旦发现新的任务，就会根据主机信息，逐级进行上传，并自动回报传输进度。

## 环境依赖

- Python 2.x
- scp
- sshpass

## 用法

### 启动脚本
1. 安装依赖内容
2. 建立工作目录，例如 `mkdir /root/jumper`
3. 填写主机信息文件 `host.json`
	- 主机 ID
	- 其中 path 代表的是各个主机中在步骤 1 建立的工作目录
	- upstream 代表该主机的上级跳板/堡垒机的主机 ID
4. 在各个主机中以 `jumper.py [machin id] [working dir]` 形式运行该脚本

### 传输文件

下面步骤均在第一跳板上完成。

1. 把待传输文件放到工作目录的 `data` 子目录下。
2. 编写任务文件，命名随意，扩展名必须为 `.json`，格式见后，其中 id , position, status 字段值均为 ""
3. 等传输开始，定期查看该任务文件的 log 和 status 字段，获取任务进度

## 配置文件

### host.json

~~~json
{
  "jumper1": {
    "host": "10.211.55.42",
    "user": "root",
    "pass": "ComplexPwd",
    "port": "22",
    "path": "/root/jumper",
    "upstream": ""
  },
  "jumper2": {
    "host": "10.211.55.43",
    "user": "root",
    "pass": "ComplexPwd",
    "port": "22",
    "path": "/root/jumper",
    "upstream": "jumper1"
  },
  "jumper3": {
    "host": "10.211.55.44",
    "user": "root",
    "pass": "ComplexPwd",
    "port": "22",
    "path": "/root/jumper",
    "upstream": "jumper2"
  },
  "web": {
    "host": "10.211.55.45",
    "user": "root",
    "pass": "ComplexPwd",
    "port": "22",
    "path": "/root/jumper",
    "upstream": "jumper3"
  }
}
~~~

### task.json （新任务）

~~~json
{
  "status": "",
  "file": "dm.zip",
  "position": "",
  "id": "",
  "target": "web"
}

~~~


### task.json （任务完成）

~~~json
{
  "status": "finished",
  "log": [
    {
      "host": "jumper1",
      "hash": "55292b6922f34fc1e56b876e8e4dbb5d",
      "time": "2016-02-23 15:39:08"
    },
    {
      "host": "jumper2",
      "hash": "55292b6922f34fc1e56b876e8e4dbb5d",
      "time": "2016-02-23 15:39:39"
    },
    {
      "host": "jumper3",
      "hash": "55292b6922f34fc1e56b876e8e4dbb5d",
      "time": "2016-02-23 15:39:56"
    }
  ],
  "file": "dm.zip",
  "position": "web",
  "id": "86086b9eda0011e5a310001c4268d82a",
  "target": "web"
}

~~~
