# PC Hardware Monitor MCP-Server 

AIチャットアプリ Claude Desktop, Copilot Desktop から自然言語でPCの CPU温度・負荷率・メモリ・ディスク・ネットの状態を確認できるMCP-Serverです。　by.Iwamoto

例、「今のCPU温度と使用率を教えて」 「メモリの使用状況はどうなってる？」 など


- Claude Desktop は Windows版アプリ、macOS版アプリ でのみ使用できます。 その他のブラウザ版・スマホ版などは使えません。
　 (https://claude.com/ja/download)
  
- Copilot Desktop は Windows11付属のローカル動作版でのみ使用できます。　その他のブラウザ版・スマホ版・クラウド版は使えません。
　　(https://apps.microsoft.com/detail/xp9cxngppj97xx?hl=ja-JP&gl=JP)

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

`~/Library/Application Support/Claude/claude_desktop_config.json`（macOS版 Claude Desktop の場合）  
`%APPDATA%\Claude\claude_desktop_config.json`（Windows版 Claude Desktop の場合）
`$env:USERPROFILE\.copilot\servers.json`（Windows11付属のローカル動作版 Copilot Desktop の場合）

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

- 「今のCPU温度と使用率を教えて」
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


