## Baidu Netdisk MCP Server (Python)

一个通过 Model Context Protocol (MCP) 提供百度网盘文件上传功能的服务器。

### 特性

- 支持小文件直接上传
- 支持大文件自动分片上传（>4MB）
- 内置重试机制和错误处理
- 通过 MCP 协议与 AI 助手集成

### 安装

#### 方式一：通过 pip 安装（推荐）

```bash
pip install netdisk-mcp-server
```

#### 方式二：从源码安装

```bash
git clone https://github.com/yourusername/netdisk-mcp-server-stdio.git
cd netdisk-mcp-server-stdio
pip install -e .
```

### 配置

#### 获取百度网盘 Access Token

1. 访问百度开放平台创建应用
2. 获取 Access Token
3. 设置环境变量：`BAIDU_NETDISK_ACCESS_TOKEN`

### 使用方法

#### 方式一：命令行直接运行

```bash
export BAIDU_NETDISK_ACCESS_TOKEN="your_access_token"
netdisk-mcp-server
```

#### 方式二：搭建 Python 虚拟环境

我们推荐通过`uv`构建虚拟环境来运行MCP server，关于`uv`你可以在[这里](https://docs.astral.sh/uv/getting-started/features/)找到一些说明。

按照[官方流程](https://modelcontextprotocol.io/quickstart/server)，你会安装`Python`包管理工具`uv`。除此之外，你也可以尝试其他方法（如`Anaconda`）来创建你的`Python`虚拟环境。

### 在Cursor中使用

打开`Cursor`配置，在MCP中添加MCP Server

![](./img/cursor_setting.png)

在文件中添加如下内容后保存

#### 配置方式一：使用已安装的包

```json
{
  "mcpServers": {
    "baidu-netdisk": {
      "command": "netdisk-mcp-server",
      "env": {
        "BAIDU_NETDISK_ACCESS_TOKEN": "<YOUR_ACCESS_TOKEN>"
      }
    }
  }
}
```

#### 配置方式二：使用 uv 运行

```json
{
  "mcpServers": {
    "baidu-netdisk-local-uploader": {
      "command": "uv的绝对路径，通过which uv命令获取，如/Users/netdisk/.local/bin/uv",
      "args": [
          "--directory",
          "netdisk.py所在的父目录绝对路径，如/Users/netdisk/mcp/netdisk-mcp-server-stdio",
          "run",
          "netdisk.py"
      ],
      "env": {
        "BAIDU_NETDISK_ACCESS_TOKEN": "<YOUR_ACCESS_TOKEN>"
      }
    }
  }
}
```


回到配置，此时百度网盘MCP Server已经启用

![](./img/cursor_run_mcp_success.png)

### 测试

上传文件到网盘测试用例

![](./img/cursor_test_1.png)

![](./img/cursor_test_2.png)

### API 说明

#### upload_file

上传本地文件到百度网盘

参数：
- `local_file_path` (str): 本地文件路径
- `remote_path` (str, 可选): 网盘存储路径，必须以 `/` 开头。如不指定，将默认上传到 `/来自：mcp_server` 目录下

返回：
- `status`: 上传状态（success/error）
- `message`: 状态消息
- `filename`: 文件名
- `size`: 文件大小
- `remote_path`: 远程路径
- `fs_id`: 文件系统 ID

### 开发

#### 构建项目

```bash
# 安装开发依赖
pip install build twine

# 构建包
python -m build

# 检查构建结果
twine check dist/*
```

#### 发布到 PyPI

```bash
# 发布到测试 PyPI
twine upload --repository testpypi dist/*

# 发布到正式 PyPI
twine upload dist/*
```

### 许可证

MIT License

### 贡献

欢迎提交 Issue 和 Pull Request！