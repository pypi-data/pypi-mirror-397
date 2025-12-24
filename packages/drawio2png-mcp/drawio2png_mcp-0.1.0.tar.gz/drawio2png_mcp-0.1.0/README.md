# drawio2png-mcp

将 Draw.io 图表转换为 PNG 图片的 MCP 服务。

## 安装

```bash
uvx drawio2png-mcp
```

## 配置

在 MCP 客户端配置中添加：

```json
{
  "mcpServers": {
    "drawio": {
      "command": "uvx",
      "args": ["drawio2png-mcp"]
    }
  }
}
```

## 前置要求

需要安装 [draw.io 桌面版](https://github.com/jgraph/drawio-desktop/releases)。

如果 draw.io 不在默认路径，可通过 `DRAWIO_PATH` 环境变量指定：

```json
{
  "mcpServers": {
    "drawio": {
      "command": "uvx",
      "args": ["drawio2png-mcp"],
      "env": {
        "DRAWIO_PATH": "/path/to/drawio"
      }
    }
  }
}
```
