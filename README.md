# PC Hardware Monitor MCP-Server 

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-green.svg)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20WSL2-blue.svg)](https://github.com/Iwamoto-Ai/pc-system-info-mcp)
[![MCP](https://img.shields.io/badge/MCP-Compatible-purple.svg)](https://modelcontextprotocol.io/)


AIチャットアプリ Claude Desktop から自然言語でPCの CPU・メモリ・ディスク・ネットの状態を確認できるMCP-Serverです。

例、「CPUの状態を教えて」 「メモリの使用状況はどうなってる？」 など



> **⚠️ 注意**
- Claude Desktop は Windows版アプリ、macOS版アプリ でのみ使用できます。 その他のブラウザ版・スマホ版などでは使えません。
　 (https://claude.com/ja/download)
  
- Copilot Desktop は Windows11pro付属 ローカル動作版でのみMCPが使用できるようですが非推奨。廃止になるらしいです。　
  以前は Windows11Home付属 ローカル動作版があったが廃止されたようです。

- Windowsの WMIC コマンド は間もなく廃止されるようです。


- 1から作り直しました！！　（こちらはシンプル版として置いておきます。。。）
  Claude Desktopだけでなく、🦞OpenClawでも使えるようにし、　
  外出先からLineやDiscodeを使い自然言語でPCの状況を確認できます。　　
　 https://github.com/Iwamoto-Ai/pc-system-info-mcp


---

## インストール

```bash
pip install mcp psutil

# Windowsの場合（CPU温度取得に必要）
pip install wmi

# macOSの場合（CPU温度取得に必要）
brew install osx-cpu-temp

# server.py をローカルディスクへコピー

```

---

## 設定ファイルへの登録

- `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS版 Claude Desktop の場合）  
- `%APPDATA%\Claude\claude_desktop_config.json`（Windows版 Claude Desktop の場合）
- `$env:USERPROFILE\.copilot\servers.json`（Windows11pro付属のローカル動作版 Copilot Desktop の場合（非推奨））

```json
{
  "mcpServers": {
    "system-monitor": {
      "command": "python",
      "args": ["/path/to/server.py"]
    }
  }
}
```

※ パスは `server.py` の実際の絶対パスに変更してください。
※ 設定を反映にするため、アプリの再起動が必要です。


---

## 利用できるツール

| ツール名 | 説明 |
|---|---|
| `get_cpu_info` | CPU使用率・コア別・周波数・温度 |
| `get_memory_info` | RAM・スワップ使用状況 |
| `get_disk_info` | ディスク使用量・I/O統計 |
| `get_network_info` | ネットワーク送受信統計 |
| `get_top_processes` | CPU/メモリ使用率上位プロセス |
| `get_system_summary` | システム全体のサマリー |
| `get_cpu_temperature` | CPU温度のみ |

---

## プロンプトの例

- 「今のCPUの状況を教えて」
- 「メモリの使用状況はどうなってる？」
- 「CPU使用率が高いプロセスTOP5を見せて」
- 「ディスクの空き容量はどれくらい？」
- 「システム全体のサマリーを教えて」

---

## CPU温度について

| OS | 必要なもの |
|---|---|
| Linux | `lm-sensors`（`sudo apt install lm-sensors && sudo sensors-detect`） |
| macOS | `osx-cpu-temp`（`brew install osx-cpu-temp`） |
| Windows | `wmi`（`pip install wmi`） |

温度センサーが利用できない環境では、温度以外のメトリクスは正常に取得できます。

---

📄 ライセンス

Apache License Version 2.0 - 詳細は LICENSE を参照

Copyright 2026　岩本 剛　All rights reserved.

---

---

