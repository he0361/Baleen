# 常见问题

## Anthropic API key not found

这是本地未读到密钥，不表示服务器已经拒绝了密钥。在运行程序的同一个 CMD 窗口执行：

```cmd
set "ANTHROPIC_API_KEY=YOUR_API_KEY"
if defined ANTHROPIC_API_KEY (echo API key is set) else (echo API key is missing)
start.cmd
```

注意半角等号和英文引号。`set` 随窗口关闭失效；`setx` 对新打开的 CMD 窗口生效。使用 `openai` 或 `openai-compat` 时，变量名是 `OPENAI_API_KEY`。

真实密钥不要截图、发到公开聊天或提交到 Git。

## API 认证、模型或地址错误

- 认证错误：核对密钥属于当前 `base_url` 对应的服务商，且账户有调用权限。
- 模型不存在：将 `YOUR_MODEL_ID` 替换为服务商实际提供的模型 ID。
- 接口不存在：核对协议与接口是否一致，以及 `base_url` 是否为 API 根地址。

这些检查与图标是否正确显示无关。

## 找不到配置文件

将 `config.example.yaml` 复制到 `.Baleen/config.yaml`，替换占位符后重启。配置相对于**当前工作目录**加载；在其他项目中运行时，需要该项目的配置或用户级配置。

## No module named Baleen / MCP 导入异常

确认克隆目录名为 `Baleen`，优先通过 `start.cmd` 启动。不要直接运行 `__main__.py`，也不要把 `PYTHONPATH` 指向 `Baleen` 包内部。

当前采用源码包布局，尚未提供 `pip install -e .` 所需的打包配置。启动脚本通过 `-P` 避免根目录的 `mcp/` 与第三方 MCP 包重名冲突。

## pip 下载失败

当前镜像连接异常时，可以显式尝试官方索引：

```cmd
.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple -r requirements.txt
```

仍失败时检查网络和代理配置，不要关闭 TLS 验证。

## 鲸鱼显示为空心框，或标题区域空白

半尺寸鲸鱼需要支持半格字符的字体。Windows 启动流程先切换备用屏，再配置 UTF-8 和 Consolas，正常退出后恢复原设置。

旧版曾把 CMD 的历史缓冲区高度误作窗口高度，或只对主屏幕配置字体，导致空白和缺块。更新后请完全退出旧进程，再运行 `start.cmd`。不要使用旧的独立预览脚本判断新版显示效果。

字体配置失败时会回退到原尺寸图标。强制终止进程时，退出清理不一定有机会执行。

## 中文输入与换行

当前包含 Windows Unicode 输入兼容处理和输入框回归测试。真实输入法候选词提交仍与终端宿主有关。如仍有问题，请记录终端、字体和输入法，并说明是无法选词、无法插入文字，还是 Enter 误提交。换行可以尝试 `Ctrl+J`。
