![Baleen 蓝色像素鲸鱼与白色标题](docs/assets/banner.svg)

# Baleen

Baleen 是一个基于 Python 与 [Textual](https://github.com/Textualize/textual) 构建的终端 AI 编程助手：它运行在你的 CMD / 终端里，可以读取项目、搜索代码、编辑文件、执行命令，并通过大语言模型 API 与你协作完成编程任务。

项目以**蓝色像素鲸鱼**为标识。当前维护重点为 **Windows CMD 下的启动、中文（IME）输入与终端显示体验**，主要测试与启动脚本面向 Windows。

## 功能

**终端交互（Textual TUI）**
- 多行输入与历史输入、Tab 补全、斜杠命令。
- 内嵌的计划模式、权限确认与 AskUser 对话框，以及子 Agent / 团队 / Skill / Worktree 等面板。

**模型接入（多协议）**
- `anthropic`：Anthropic Messages API，支持流式、扩展思考、prompt caching，并可通过 `/v1/models` 自动探测上下文窗口。
- `openai`：OpenAI Responses API。
- `openai-compat`：OpenAI 兼容的 Chat Completions API（可用于 vLLM、Ollama、Together、Azure 等兼容服务）。
- 每个提供方都有独立的 `base_url`，因此也可接入 Anthropic 兼容的第三方服务。

**代码工具与权限**
- 工具：文件读 / 写 / 编辑、文件与内容搜索（Glob / Grep）、本地 Shell 命令等。
- 权限：按权限模式决定「读 / 写 / 命令」是否需要确认；支持 YAML 权限规则、危险命令检测与路径沙箱。
- 计划模式：只开放规划所需的少量工具，先出方案再执行。

**会话、上下文与记忆**
- 会话保存 / 恢复（每会话 JSONL 记录，自动生成标题），支持按需恢复。
- 上下文自动 / 手动压缩（`/compact`）；被截断的大工具结果会落盘保存。
- 记忆：自动提取并写入 `memories.md`，也支持带 frontmatter 的记忆文件与基于模型的相关性召回。
- 指令：读取项目级 / 用户级 `BALEEN.md`（支持 `@include` 引用其它文件）。
- 文件历史：每次助手回复后生成快照，可用 `/rewind` 回退到任意检查点。

**Agent 协作**
- 用 Markdown（frontmatter）定义子 Agent 类型；内置 Explore、Plan、general-purpose 与可选的 Verification。
- 后台任务与完成通知、父会话 fork、Git Worktree 独立工作目录、进程内团队协作（任务、进度与消息）。

**扩展机制**
- Skill：`SKILL.md` 定义技能，支持 inline / fork 两种执行方式，并自动注册为命令。
- Hook：生命周期钩子（会话 / 轮次 / 工具调用前后 / 收发消息等），动作支持命令、HTTP、提示与子 Agent。
- MCP：支持 stdio 与 Streamable HTTP 两种传输；远端工具以 `mcp_<server>_<tool>` 形式接入并按需加载。

**Windows 体验与品牌**
- 启动时切换 UTF-8 代码页、设置 Consolas 字体与备用屏幕，退出后恢复原设置。
- 通过 Win32 控制台输入归一化中文合成输入（IME），避免重复 / 丢失字符。
- 蓝色像素鲸鱼标识与 `Baleen` 像素标题由 `branding.py` 渲染，样式位于 `styles.tcss`。

## 快速开始（Windows CMD）

需要 **Python 3.11+**、Git，以及可用的模型 API 服务。以下命令在 **CMD** 中运行。

### 1. 获取源码并安装依赖

```cmd
git clone https://github.com/he0361/Baleen.git Baleen
cd Baleen
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

克隆目录名请保留为 `Baleen`：项目根目录本身就是 Python 包 `Baleen`，导入时依赖目录名（`python -m Baleen`）。依赖安装完成后无需再 `pip install -e .`，直接就地运行即可。

### 2. 创建模型配置

```cmd
mkdir .Baleen
copy config.example.yaml .Baleen\config.yaml
notepad .Baleen\config.yaml
```

根据服务商提供的信息填写 `base_url` 与 `model`。最小示例（默认使用 Anthropic 协议）：

```yaml
providers:
  - name: my-anthropic
    protocol: anthropic
    base_url: https://api.anthropic.com
    model: YOUR_MODEL_ID
    thinking: false
    max_output_tokens: 4096

permission_mode: default
```

`YOUR_MODEL_ID` 必须替换为服务商支持且你的账户有权使用的模型 ID；若使用 Anthropic 兼容服务，还需把 `base_url` 改为该服务商给出的接口根地址。完整配置字段见下节「配置」。

### 3. 设置 API Key 并启动

在**同一个 CMD 窗口**执行，把占位符换成你自己的有效密钥：

```cmd
set "ANTHROPIC_API_KEY=YOUR_API_KEY"
start.cmd
```

`set` 只对当前窗口生效。希望保存为当前用户的持久环境变量时：

```cmd
setx ANTHROPIC_API_KEY "YOUR_API_KEY"
```

`setx` 对新打开的 CMD 窗口生效。**真实密钥不要提交到仓库**（`.gitignore` 已忽略 `.env`、`.Baleen/` 等）。

### 4. 开始使用

可以先输入：

```text
请阅读当前项目，介绍目录结构和启动入口，不要修改文件。
```

`start.cmd` 默认把 Baleen 源码目录作为工作目录。需要操作其它项目时，见下一节。

## 在其它项目中使用

例如工具位于 `E:\Baleen`，要分析的代码位于 `E:\my-project`：

```cmd
cd /d E:\my-project
set "PYTHONPATH=E:\"
set "PYTHONUTF8=1"
set "TEXTUAL_COLOR_SYSTEM=truecolor"
set "ANTHROPIC_API_KEY=YOUR_API_KEY"
E:\Baleen\.venv\Scripts\python.exe -P -m Baleen
```

- `PYTHONPATH` 指向工具目录的**上一级目录**，使 `Baleen` 作为包被导入。
- `-P` 是 Python 的「安全路径」模式：避免当前项目内（或工作目录下）的 `mcp` 文件夹遮蔽第三方 `mcp` 包——本项目自带的 `mcp/` 子包正是需要这种隔离的原因。
- 目标项目需要自己的 `.Baleen\config.yaml`，或把通用 provider 放在用户级 `%USERPROFILE%\.Baleen\config.yaml`。

## 配置

配置从以下路径加载（按需合并）：

1. 用户级：`~/.Baleen/config.yaml`
2. 项目级：`.Baleen/config.yaml`
3. 本地覆盖：`.Baleen/config.local.yaml`

合并规则：后加载配置中的 `providers` 列表整体替换先前列表，`mcp_servers` 按名称合并，`hooks` 追加。没有任何配置文件时启动会报错。`config.example.yaml` 为不含密钥的参考示例。

| 配置键 | 说明 |
| --- | --- |
| `providers[]` | 模型提供方列表。必填字段：`name`、`protocol`（`anthropic` / `openai` / `openai-compat`）、`base_url`、`model`；可选字段：`api_key`（省略时读环境变量）、`thinking`、`max_output_tokens`、`context_window` |
| `permission_mode` | `default` / `acceptEdits` / `plan` / `bypassPermissions` / `custom` / `dontAsk` |
| `mcp_servers[]` | MCP 服务器：stdio（`command`+`args`+`env`）或 Streamable HTTP（`url`+`headers`）；env/headers 支持 `${ENV_VAR}` 插值 |
| `hooks[]` | 生命周期钩子配置 |
| `enable_fork` | 是否允许子 Agent fork 父会话 |
| `enable_verification_agent` | 是否加载 Verification 验证子 Agent |
| `worktree` | Git worktree 配置（`symlink_directories`、过期清理间隔与时限） |
| `teammate_mode` | 团队后端，当前支持 `""` 与 `"in-process"` |
| `enable_coordinator_mode` | 协调者模式（也可用环境变量 `BALEEN_COORDINATOR_MODE` 控制） |

环境变量：`ANTHROPIC_API_KEY`（anthropic）、`OPENAI_API_KEY`（openai / openai-compat）。

## 常用操作

详细说明：[模型与 API Key 配置](docs/configuration.md) · [启动、中文输入与图标显示排错](docs/troubleshooting.md)。

| 操作 | 用法 |
| --- | --- |
| 发送消息 | `Enter` |
| 插入换行 | `Shift+Enter` 或 `Ctrl+J`（视终端支持而定） |
| 历史 / 补全候选 | 上下方向键 / `Tab` |
| 退出 | `Ctrl+C` |
| 取消当前操作 | `Esc` |
| 切换权限模式 | `Shift+Tab` |
| 展开 / 收起工具调用块 | `Ctrl+O` |

斜杠命令：`/help`、`/status`、`/clear`、`/compact`、`/plan`、`/session`、`/memory`、`/permission`、`/rewind`、`/mcp`、`/skill`、`/worktree`、`/tasks`、`/trace`。更多参数用 `/help <命令名>` 查看。

也支持命令行单次执行：

```cmd
start.cmd -p "请介绍当前项目结构，不要修改文件"
start.cmd --mode plan
start.cmd --help
```

- `-p PROMPT`：非交互模式，运行一次提示并打印结果到 stdout（使用配置中第一个 provider）。
- `--mode`：临时覆盖权限模式。

## 目录结构

| 目录 / 文件 | 用途 |
| --- | --- |
| `__main__.py`、`start.cmd` | 命令行与 Windows 启动入口（`python -m Baleen`） |
| `app.py`、`styles.tcss`、`branding.py` | Textual 终端界面、样式与像素鲸鱼标识 |
| `agent.py`、`prompts.py`、`conversation.py`、`serialization.py` | Agent 循环、系统提示、会话消息与协议序列化 |
| `client.py`、`config.py`、`validator.py` | 模型 API 客户端、配置加载与校验 |
| `driver.py`、`console_setup.py`、`windows_input.py` | 控制台、UTF-8 / 字体设置与 Windows 输入归一化 |
| `tools/` | 本地工具库（文件、Shell、AskUser、计划、子 Agent、团队、Skill、Worktree 等） |
| `permissions/` | 权限模式、检查器、规则、危险命令检测与路径沙箱 |
| `agents/` | 子 Agent：frontmatter 解析、加载、fork、后台任务与追踪 |
| `teams/` | 进程内团队协作（消息、共享任务、进度、协调者） |
| `worktree/` | Git worktree 隔离与清理 |
| `commands/` | 斜杠命令解析、注册与各命令处理器 |
| `skills/` | Skill 解析、加载与执行（含内置 commit / review / test / backend-interview） |
| `hooks/` | 生命周期钩子（事件、条件、动作、引擎） |
| `mcp/` | MCP 客户端（stdio 与 Streamable HTTP）、管理器与工具包装 |
| `context/`、`memory/`、`filehistory/` | 上下文压缩、会话/记忆/指令、文件历史与回退 |
| `config.example.yaml` | 不含密钥的配置示例 |
| `test_baleen.py` | 面向 Windows 的回归测试 |

## 开发与验证

从仓库根目录在 CMD 中运行：

```cmd
set "PYTHONPATH=%CD%\.."
.venv\Scripts\python.exe -P -m unittest Baleen.test_baleen -v
.venv\Scripts\python.exe -m pip check
```

回归测试面向 Windows，覆盖：驱动对备用屏幕的处理顺序、IME 合成输入 / 修饰键 Unicode 提交、像素配色保留（半尺寸鲸鱼不丢像素）、缺少 API Key 时的标题显示，以及中文输入 / 粘贴 / 提交等场景。代码含非 Windows 驱动分支（回退 `LinuxDriver`），但其它平台的同等验证尚未完成，`start.cmd` 与当前测试集均面向 Windows。
