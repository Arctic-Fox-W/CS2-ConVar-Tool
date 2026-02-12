# CS2 RCON GUI 工具

一个用于连接与控制 CS2 服务器的图形化 RCON 工具。使用 Python + PyQt5 构建，集成常用比赛控制、Bot 管理、游戏速度调整、状态显示以及 ConVar 配置管理等功能。可一键打包为独立 exe，并支持版本化压缩包发布。

## [必读]服务器配置

- 确保服务器开启 RCON 功能：
  - 在 `server.cfg` 中添加 `rcon_password "your_password"`
  - 重启服务器使配置生效
- 检查服务器端口：
  - 默认端口为 27015，可在 `server.cfg` 中修改 `rcon_port` 项

## 功能特性

- RCON 连接与命令执行：输入命令、查看返回日志，使用 Source RCON 协议。
- 控制台左侧功能区（双列）：
  - 常用快捷：重启回合、开关作弊、热身开始/结束、暂停/继续、获取地图信息
  - Bot 管理：增加 Bot、踢出 Bot、停止开枪、停止移动、冻结（自动处理 sv_cheats）
  - 游戏速度：- / 数值 / + / 加速 / 恢复（host_timescale，步长 0.5）
- 状态栏信息：显示 IP、端口、在线人数与当前地图名，并每 5 秒自动刷新。
- ConVar 管理：导入 JSON 分组显示，一键获取当前值并记录初始值，支持保存/加载配置。
- 资源与打包适配：包含图标与资源文件，兼容 PyInstaller（sys.\_MEIPASS）。

## 运行环境

- Python 3.11+（已在 3.11/3.13 下测试）
- 依赖：PyQt5、rcon（`pip install PyQt5 rcon`）
- Windows（开发与打包在 Windows 上进行）

## 快速开始

- 运行源码：
  - 在项目目录执行：`py cs2_rcon_tool.py`
- 连接服务器：
  - 输入服务器 IP/端口/密码后连接；连接成功后左侧功能区与速度控制可用。
  - 部分功能（例如 host*timescale、bot*\* 行为）需要 `sv_cheats 1`。可用“开关作弊”按钮或脚本自动尝试开启。

## 配置文件

- 示例与官方配置：
  - 官方 ConVar 配置（host 留空）：[cs2_official_convars_config.json](file:///d:/Program/CSGO/Bot/ConVar_Tool/cs2_official_convars_config.json)
  - 示例配置（含自定义/插件项）：[zero_convars_config.json](file:///d:/Program/CSGO/Bot/ConVar_Tool/zero_convars_config.json)
- 结构说明：
  - `connection`: 包含 `host` 与 `port`（可留空以手动填写）
  - `groups`: 分组下包含 `convars` 或 `weapons`，每项含 `name`、`zh`、`initial`
- 导入行为：
  - 支持 `{"convars": [...]}` 的对象结构或顶层 `[...]` 列表结构

## 界面说明

- 控制台页：
  - 左侧功能区（双列）放置常用按钮与 Bot 管理、底部为速度控制行
  - 右侧包含命令输入框与日志输出
- ConVar 页：
  - 展示配置分组与项，一键获取当前值，保存/加载配置

## 关键文件

- 主程序：[cs2_rcon_tool.py](file:///d:/Program/CSGO/Bot/ConVar_Tool/cs2_rcon_tool.py)
- 打包脚本：[package.ps1](file:///d:/Program/CSGO/Bot/ConVar_Tool/package.ps1)
- 打包配置：[cs2_rcon_tool.spec](file:///d:/Program/CSGO/Bot/ConVar_Tool/cs2_rcon_tool.spec)

## 常见问题

- 运行时出现 `Hidden import "sip" not found!`：这是 PyInstaller 的警告，实际运行不受影响。
- 调整游戏速度无效：请确认已启用 `sv_cheats 1`，或通过“开关作弊”按钮启用。
- 导入 ConVar 报结构错误：请确保 JSON 为对象含 `convars` 列表或顶层列表，两种结构都被支持。
