# 配置参考

## 加载顺序

程序依次加载以下配置；后加载配置中的 provider 列表替换先加载的列表：

1. `%USERPROFILE%\.Baleen\config.yaml`
2. 当前工作目录下的 `.Baleen\config.yaml`
3. 当前工作目录下的 `.Baleen\config.local.yaml`

不是所有字段都执行简单覆盖：MCP 服务按名称合并，Hook 列表追加，部分布尔选项只在后续层启用。首次使用建议只保留一份项目配置。每份被读取的配置都需要合法的非空 `providers` 列表。

## Provider 字段

| 字段 | 含义 |
| --- | --- |
| `name` | 必填，显示名称；多个 provider 使用不同名称 |
| `protocol` | 必填，只接受下表列出的三种协议 |
| `base_url` | 必填，服务商提供的 API 根地址 |
| `model` | 必填，服务商实际支持的模型 ID |
| `api_key` | 可选，未填写时读取对应的环境变量 |
| `thinking` | 可选布尔值，默认 `false`；是否可用取决于协议与模型 |
| `max_output_tokens` | 输出 token 上限，应使用服务商支持的值 |
| `context_window` | 可选的上下文窗口覆盖值；不确定时可省略 |

API Key 的优先级是：provider 中的非空 `api_key`，然后是对应环境变量。**Provider 的 `api_key` 不支持 `${变量名}` 插值，项目也不会自动加载 `.env` 文件。** 要使用环境变量，请省略 `api_key` 字段。

## 协议区别

| `protocol` | 调用接口 | 环境变量 |
| --- | --- | --- |
| `anthropic` | Anthropic Messages | `ANTHROPIC_API_KEY` |
| `openai` | OpenAI Responses | `OPENAI_API_KEY` |
| `openai-compat` | Chat Completions | `OPENAI_API_KEY` |

协议描述的是服务商的接口格式，而不是模型品牌。通过 Anthropic 兼容服务调用模型时使用 `anthropic`；只提供 Chat Completions 的服务使用 `openai-compat`。

OpenAI 兼容服务示例：

```yaml
providers:
  - name: compatible-api
    protocol: openai-compat
    base_url: https://YOUR_PROVIDER_HOST/v1
    model: YOUR_MODEL_ID
    max_output_tokens: 4096

permission_mode: default
```

将地址与模型替换为服务商提供的值，并在 CMD 中设置 `OPENAI_API_KEY`。不要把 `/messages`、`/responses`、`/chat/completions` 请求路径直接当成 `base_url`。

## 权限模式

默认 `permission_mode: default` 通常允许读取，对写入和命令执行请求确认。

配置校验接受 `default`、`acceptEdits`、`plan`、`bypassPermissions`、`custom`、`dontAsk`。各模式的确认策略不同，首次使用建议保留 `default`，分析或规划时使用 `/plan`。启动参数 `--mode` 可以覆盖配置。

## 扩展配置

可选配置还包括 `mcp_servers`、`hooks`、`enable_fork`、`enable_verification_agent`、`worktree`、`teammate_mode` 和 `enable_coordinator_mode`。MCP 支持 stdio 与 Streamable HTTP；`teammate_mode` 当前只接受空字符串或 `in-process`。

未配置这些项也能使用基本对话和代码工具。字段校验以根目录的 `validator.py` 为准。
