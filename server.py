#!/usr/bin/env python3
"""
PC hardware MCP-Server     by.Iwamoto
CPU温度・負荷率・メモリ・ディスク・ネットワークをモニタリングするMCPサーバー

依存ライブラリ:
  pip install mcp psutil
  # macOSの場合: pip install mcp psutil
  # Windowsの場合: pip install mcp psutil wmi
"""

import json
import platform
import sys
from datetime import datetime

import psutil
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("system-monitor")


# ──────────────────────────────────────────────────────────
# ヘルパー関数
# ──────────────────────────────────────────────────────────

def bytes_to_human(n: int) -> str:
    """バイト数を人間が読みやすい形式に変換"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def get_cpu_temperature() -> dict:
    """CPU温度を取得（プラットフォーム別）"""
    temps = {}
    system = platform.system()

    # psutil の sensors_temperatures (Linux / macOS 一部対応)
    if hasattr(psutil, "sensors_temperatures"):
        raw = psutil.sensors_temperatures()
        if raw:
            for chip, entries in raw.items():
                chip_temps = []
                for entry in entries:
                    chip_temps.append({
                        "label": entry.label or chip,
                        "current": entry.current,
                        "high": entry.high,
                        "critical": entry.critical,
                    })
                temps[chip] = chip_temps
            return {"available": True, "data": temps}

    # Windows: WMI 経由
    if system == "Windows":
        try:
            import wmi
            w = wmi.WMI(namespace=r"root\wmi")
            sensors = w.MSAcpi_ThermalZoneTemperature()
            win_temps = []
            for s in sensors:
                celsius = (s.CurrentTemperature / 10) - 273.15
                win_temps.append({
                    "label": s.InstanceName,
                    "current": round(celsius, 1),
                })
            if win_temps:
                return {"available": True, "data": {"WMI": win_temps}}
        except Exception:
            pass

    # macOS: osx-cpu-temp / powermetrics (フォールバック)
    if system == "Darwin":
        try:
            import subprocess
            result = subprocess.run(
                ["osx-cpu-temp"],
                capture_output=True, text=True, timeout=3
            )
            if result.returncode == 0:
                temp_str = result.stdout.strip().replace("°C", "").strip()
                return {
                    "available": True,
                    "data": {"CPU": [{"label": "CPU", "current": float(temp_str)}]},
                }
        except Exception:
            pass

    return {
        "available": False,
        "message": (
            "温度センサーが利用できません。"
            "Linux: lm-sensors をインストール / macOS: osx-cpu-temp をインストール"
            " / Windows: WMI が必要です。"
        ),
    }


# ──────────────────────────────────────────────────────────
# ツール定義
# ──────────────────────────────────────────────────────────

@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_cpu_info",
            description="CPU使用率（全体・コア別）、周波数、コア数、温度を取得します",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_memory_info",
            description="RAM・スワップのメモリ使用状況を取得します",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_disk_info",
            description="ディスクの使用状況とI/O統計を取得します",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_network_info",
            description="ネットワークインターフェースの送受信統計を取得します",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_top_processes",
            description="CPU・メモリ使用率上位のプロセスを取得します",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "取得するプロセス数（デフォルト: 10）",
                        "default": 10,
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "ソート基準: 'cpu' または 'memory'（デフォルト: 'cpu'）",
                        "enum": ["cpu", "memory"],
                        "default": "cpu",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_system_summary",
            description="システム全体のサマリー（CPU・メモリ・ディスク・温度）をまとめて取得します",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="get_cpu_temperature",
            description="CPU温度のみを取得します（利用可能な場合）",
            inputSchema={"type": "object", "properties": {}, "required": []},
        ),
    ]


# ──────────────────────────────────────────────────────────
# ツール実装
# ──────────────────────────────────────────────────────────

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    result = {}

    # ── CPU情報 ──────────────────────────────────────────
    if name == "get_cpu_info":
        cpu_percent_total = psutil.cpu_percent(interval=1)
        cpu_percent_per_core = psutil.cpu_percent(interval=0, percpu=True)
        freq = psutil.cpu_freq()
        load = psutil.getloadavg() if hasattr(psutil, "getloadavg") else None

        result = {
            "cpu_name": platform.processor() or "不明",
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "usage_total_percent": cpu_percent_total,
            "usage_per_core_percent": cpu_percent_per_core,
            "frequency_mhz": {
                "current": round(freq.current, 1) if freq else None,
                "min": round(freq.min, 1) if freq and freq.min else None,
                "max": round(freq.max, 1) if freq and freq.max else None,
            },
            "load_average_1_5_15min": (
                [round(x, 2) for x in load] if load else None
            ),
            "temperature": get_cpu_temperature(),
        }

    # ── メモリ情報 ────────────────────────────────────────
    elif name == "get_memory_info":
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()
        result = {
            "ram": {
                "total": bytes_to_human(vm.total),
                "used": bytes_to_human(vm.used),
                "available": bytes_to_human(vm.available),
                "percent": vm.percent,
            },
            "swap": {
                "total": bytes_to_human(swap.total),
                "used": bytes_to_human(swap.used),
                "free": bytes_to_human(swap.free),
                "percent": swap.percent,
            },
        }

    # ── ディスク情報 ──────────────────────────────────────
    elif name == "get_disk_info":
        partitions = []
        for part in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(part.mountpoint)
                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total": bytes_to_human(usage.total),
                    "used": bytes_to_human(usage.used),
                    "free": bytes_to_human(usage.free),
                    "percent": usage.percent,
                })
            except PermissionError:
                continue

        io = psutil.disk_io_counters()
        result = {
            "partitions": partitions,
            "io_counters": {
                "read_bytes": bytes_to_human(io.read_bytes) if io else None,
                "write_bytes": bytes_to_human(io.write_bytes) if io else None,
                "read_count": io.read_count if io else None,
                "write_count": io.write_count if io else None,
            },
        }

    # ── ネットワーク情報 ──────────────────────────────────
    elif name == "get_network_info":
        net_io = psutil.net_io_counters(pernic=True)
        interfaces = []
        for iface, stats in net_io.items():
            interfaces.append({
                "interface": iface,
                "bytes_sent": bytes_to_human(stats.bytes_sent),
                "bytes_recv": bytes_to_human(stats.bytes_recv),
                "packets_sent": stats.packets_sent,
                "packets_recv": stats.packets_recv,
                "errors_out": stats.errout,
                "errors_in": stats.errin,
            })
        result = {"interfaces": interfaces}

    # ── トッププロセス ────────────────────────────────────
    elif name == "get_top_processes":
        limit = arguments.get("limit", 10)
        sort_by = arguments.get("sort_by", "cpu")
        attr = "cpu_percent" if sort_by == "cpu" else "memory_percent"

        procs = []
        for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
            try:
                procs.append(p.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        procs.sort(key=lambda x: x.get(attr, 0) or 0, reverse=True)
        result = {
            "sorted_by": sort_by,
            "processes": [
                {
                    "pid": p["pid"],
                    "name": p["name"],
                    "cpu_percent": round(p.get("cpu_percent") or 0, 1),
                    "memory_percent": round(p.get("memory_percent") or 0, 2),
                    "status": p.get("status"),
                }
                for p in procs[:limit]
            ],
        }

    # ── システムサマリー ──────────────────────────────────
    elif name == "get_system_summary":
        vm = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        cpu_pct = psutil.cpu_percent(interval=1)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = (datetime.now() - boot_time).total_seconds()
        uptime_str = (
            f"{int(uptime_seconds // 3600)}時間"
            f"{int((uptime_seconds % 3600) // 60)}分"
        )

        result = {
            "timestamp": datetime.now().isoformat(),
            "os": f"{platform.system()} {platform.release()}",
            "hostname": platform.node(),
            "uptime": uptime_str,
            "cpu": {
                "usage_percent": cpu_pct,
                "cores_logical": psutil.cpu_count(),
                "temperature": get_cpu_temperature(),
            },
            "memory": {
                "usage_percent": vm.percent,
                "used": bytes_to_human(vm.used),
                "total": bytes_to_human(vm.total),
            },
            "disk_root": {
                "usage_percent": disk.percent,
                "used": bytes_to_human(disk.used),
                "total": bytes_to_human(disk.total),
            },
        }

    # ── CPU温度のみ ───────────────────────────────────────
    elif name == "get_cpu_temperature":
        result = get_cpu_temperature()

    else:
        result = {"error": f"未知のツール: {name}"}

    return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]


# ──────────────────────────────────────────────────────────
# エントリポイント
# ──────────────────────────────────────────────────────────

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
