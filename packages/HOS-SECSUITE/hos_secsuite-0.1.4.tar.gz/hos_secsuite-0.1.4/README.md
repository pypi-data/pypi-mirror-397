# HOS SecSuite

**HOS SecSuite** 是一个模块化网络安全工具包，采用防御优先的设计理念。它提供了一套全面的网络安全评估、监控和防御工具。

## 功能特性

### 核心功能
- **模块化架构**：可扩展设计，基于基础模块系统
- **多平台支持**：兼容 Windows、Linux 和 macOS
- **异步驱动**：基于 Asyncio 的高性能异步操作
- **CLI 界面**：易于使用的交互式控制台应用
- **Web API**：基于 FastAPI 的 MCP（模块控制面板），支持 WebSocket
- **依赖管理**：自动检查和验证所需工具

### 安全工具集成
- **mitmproxy**：用于流量拦截和分析的中间人代理
- **sqlmap**：SQL 注入检测和利用工具
- **XSStrike**：跨站脚本（XSS）检测和利用工具
- **dirsearch**：Web 目录和文件暴力破解工具
- **proxy.py**：轻量级 HTTP 代理实现

### 实用工具模块
- **输入清理**：全面的输入验证和清理
- **命令执行**：安全执行同步和异步命令
- **日志记录**：可配置的日志系统
- **OS 工具**：平台特定功能检测和管理

## 安装

### 先决条件
- Python 3.8 或更高版本
- pip 包管理器
- Git（可选，用于克隆仓库）

### 安装方法

#### 从 PyPI 安装（推荐）
```bash
pip install hos-secsuite
```

#### 从源代码安装
```bash
git clone https://example.com/hos-secsuite.git
cd hos-secsuite
pip install -e .
```

### 验证安装
```bash
hos-console --version
```

## 使用

### CLI 控制台

HOS SecSuite 控制台提供了一个交互式界面，用于管理和执行安全模块。

```bash
hos-console
```

#### 控制台命令
```
help                    显示帮助信息
exit                    退出控制台
run <module> [options]  运行安全模块
list                    列出所有可用模块
info <module>           显示模块信息
config                  管理配置
scan <target>           快速扫描目标
```

### Web API（MCP 服务）

启动 MCP（模块控制面板）服务以访问 Web API：

```bash
hos-mcp-server
```

#### API 端点
- **GET /docs**：交互式 API 文档（Swagger UI）
- **GET /modules**：列出所有可用模块
- **POST /modules/{module_name}/run**：执行模块
- **GET /modules/{module_name}/info**：获取模块信息
- **WS /ws**：用于实时模块执行的 WebSocket 端点

## 模块开发

### 创建新模块

1. 在 `hos_secsuite/modules` 目录中创建一个新的 Python 文件
2. 继承 `BaseModule` 类
3. 实现所需的属性和方法

```python
from hos_secsuite.core.base_module import BaseModule

class MyModule(BaseModule):
    name = "my.module"
    description = "我的自定义安全模块"
    category = "custom"
    subcategory = "example"
    
    options = {
        "target": {
            "required": True,
            "default": "",
            "description": "要扫描的目标"
        }
    }
    
    async def run(self, **kwargs) -> dict:
        # 在此处实现模块逻辑
        return {
            "status": "success",
            "message": "模块执行成功",
            "result": {}
        }
```

4. 在 `hos_secsuite/modules/__init__.py` 中注册模块

### 模块生命周期
1. **初始化**：使用默认选项创建模块
2. **配置**：用户设置选项
3. **验证**：验证模块选项
4. **执行**：异步调用 `run()` 方法
5. **结果**：返回执行结果

## 配置

配置文件位于 `~/.hos-secsuite` 目录中：

- **config.toml**：主配置文件
- **modules.toml**：模块特定配置
- **logging.toml**：日志配置

## 测试

### 运行测试

```bash
# 运行所有测试
python -m pytest

# 运行特定测试文件
python -m pytest tests/test_utils.py

# 带详细输出运行
python -m pytest -v

# 带覆盖率报告运行
python -m pytest --cov=hos_secsuite
```

### 编写测试

测试位于 `tests` 目录中，使用 pytest 框架。请遵循以下指南：

- 测试函数使用 `test_` 前缀
- 使用描述性的测试名称
- 遵循现有的测试结构
- 尽可能模拟外部依赖

## 开发

### 项目结构
```
hos_secsuite/
├── core/           # 核心功能（BaseModule, Registry, Runner）
├── modules/        # 安全模块
├── utils/          # 实用函数
├── console/        # CLI 控制台应用
├── mcp/            # Web API 服务
└── __init__.py     # 包初始化
```

### 代码风格

- 遵循 PEP 8 指南
- 为所有函数参数和返回值使用类型提示
- 编写全面的文档字符串
- 保持函数小巧且专注
- 在适当的地方使用异步编程

## 贡献

我们欢迎对 HOS SecSuite 的贡献！请遵循以下指南：

1. Fork 仓库
2. 创建功能分支
3. 进行更改
4. 为您的更改编写测试
5. 运行测试套件确保所有测试通过
6. 提交拉取请求

## 安全考虑

- 始终遵守适用的法律法规使用 HOS SecSuite
- 不要在您不拥有或没有明确测试权限的系统上使用此工具
- 了解安全测试对目标系统的潜在影响
- 保持工具更新，使用最新的安全补丁
- 向项目维护者报告任何安全漏洞

## 许可证

HOS SecSuite 采用 Apache License 2.0 许可证。有关更多信息，请参阅 LICENSE 文件。

## 致谢

- [mitmproxy](https://mitmproxy.org/) - 中间人代理
- [sqlmap](https://sqlmap.org/) - SQL 注入工具
- [XSStrike](https://github.com/s0md3v/XSStrike) - XSS 检测工具
- [dirsearch](https://github.com/maurosoria/dirsearch) - Web 目录扫描器
- [proxy.py](https://github.com/abhinavsingh/proxy.py) - HTTP 代理实现
- [FastAPI](https://fastapi.tiangolo.com/) - Web API 框架

## 联系方式

如需问题、反馈或支持：

- 项目网站：[https://example.com/hos-secsuite](https://example.com/hos-secsuite)
- 电子邮件：[security@example.com](mailto:security@example.com)
- GitHub：[https://github.com/example/hos-secsuite](https://github.com/example/hos-secsuite)

## 更新日志

### 版本 0.1.2（当前）
- 修复了 sanitizer.py 函数
- 添加了 pytest-asyncio 依赖
- 修复了异步测试问题
- 创建了全面的 README.md
- 改进了模块架构

### 版本 0.1.1
- 修复了 sanitizer.py 中的正则表达式模式
- 改进了安全清理功能
- 更新了 pyproject.toml 配置

### 版本 0.1.0（初始版本）
- 核心模块系统实现
- CLI 控制台应用
- 基于 FastAPI 的 Web API
- 基本安全工具集成
- 输入清理和命令执行的实用函数

---

**免责声明**：HOS SecSuite 是一个安全测试工具，仅用于教育和授权测试目的。作者和维护者对因使用此工具造成的任何滥用或损害不承担任何责任。