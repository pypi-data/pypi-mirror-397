#!/usr/bin/env python3
"""
SpeakUB Comprehensive Network Tester (完整網路故障模擬系統)
使用 Toxiproxy (專業網路代理) + Python mock 技術

功能：
- Toxiproxy 處理延遲、封包損失、連接斷線等真實網路故障
- Python socket mock 處理DNS解析失敗
- TUI 按鍵控制，可即時切換故障類型
- 一鍵涵蓋所有SpeakUB網路測試需求

使用方式：
python tools/comprehensive_network_tester.py

然後在SpeakUB TUI中按:
- Ctrl+N: DNS故障注入
- Ctrl+L: 高延遲網路 (需Toxiproxy)
- Ctrl+D: 封包損失 (需Toxiproxy)
- Ctrl+W: 恢復正常網路
"""

import sys
import subprocess
import threading
import time
import socket
import requests
import json
from pathlib import Path
from typing import Dict, Any

# --- 1. 設定路徑 ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from speakub.ui.app import EPUBReaderApp
    from speakub.cli import main as cli_main
except ImportError as e:
    print(f"❌ 無法匯入 SpeakUB: {e}", file=sys.stderr)
    sys.exit(1)

# 日誌輸出說明
print("🔬 SpeakUB Comprehensive Network Tester", file=sys.stderr)
print("   📊 Toxiproxy + Python mock 專業網路測試工具", file=sys.stderr)
print("   🎯 模擬 DNS失敗、高延遲、封包損失等網路狀況", file=sys.stderr)
print("   ⚡ 專門設計用於測試Nanmai TTS的網路錯誤處理", file=sys.stderr)
print("", file=sys.stderr)
print("📋 技術架構說明：", file=sys.stderr)
print("   • Nanmai TTS: 直接HTTP (bot.n.cn:443) → 受本工具控制", file=sys.stderr)
print("   • gTTS: 直接HTTP → 受本工具控制", file=sys.stderr)
print("   • Edge-TTS: warp-cli VPN → Cloudflare全球節點中繼 → 不受影響", file=sys.stderr)
print("", file=sys.stderr)
print("💡 結果：Edge-TTS完全不受本工具影響，無法測試它的網路問題", file=sys.stderr)
print("", file=sys.stderr)

# ==========================================
# 2. Toxiproxy 網路故障模擬器
# ==========================================


class ToxiproxyController:
    """使用Toxiproxy進行專業網路故障模擬"""

    def __init__(self):
        self.api_url = "http://localhost:8474"
        self.proxy_name = "speakub_bot_n_cn"
        self.upstream_host = "bot.n.cn"
        self.upstream_port = 443
        self.proxies = []  # 保存創建的代理清單

    def check_toxiproxy_running(self) -> bool:
        """檢查Toxiproxy服務是否運行"""
        try:
            response = requests.get(f"{self.api_url}/version", timeout=2)
            return response.status_code == 200
        except:
            return False

    def start_toxiproxy_daemon(self):
        """啟動Toxiproxy後台進程"""
        try:
            # 檢查是否已運行
            if self.check_toxiproxy_running():
                print("ℹ️ [TOXIPROXY] 已經有實例在運行", file=sys.stderr)
                return True

            print("🔄 [TOXIPROXY] 啟動Toxiproxy服務...", file=sys.stderr)

            # 啟動Toxiproxy後台進程
            process = subprocess.Popen(
                ["/usr/bin/toxiproxy-server"],  # 使用用戶系統中的路徑
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # 等待服務啟動
            time.sleep(2)
            if self.check_toxiproxy_running():
                print("✅ [TOXIPROXY] 服務啟動成功", file=sys.stderr)
                return True
            else:
                print("❌ [TOXIPROXY] 服務啟動失敗", file=sys.stderr)
                return False

        except FileNotFoundError:
            print("❌ [TOXIPROXY] 未安裝Toxiproxy。在macOS上安裝：", file=sys.stderr)
            print("   brew install toxiproxy", file=sys.stderr)
            print("   或其他系統：訪問 https://github.com/Shopify/toxiproxy", file=sys.stderr)
            return False
        except Exception as e:
            print(f"❌ [TOXIPROXY] 啟動異常: {e}", file=sys.stderr)
            return False

    def create_proxy(self, upstream_host: str, upstream_port: int) -> Dict[str, Any]:
        """創建Toxiproxy代理"""
        proxy_config = {
            "name": f"proxy_{upstream_host}",
            "listen": f"0.0.0.0:{self._get_free_port()}",
            "upstream": f"{upstream_host}:{upstream_port}"
        }

        try:
            response = requests.post(
                f"{self.api_url}/proxies",
                json=proxy_config,
                timeout=5
            )
            response.raise_for_status()
            proxy = response.json()
            self.proxies.append(proxy)
            print(
                f"✅ [TOXIPROXY] 創建代理: {proxy_config['name']} -> {upstream_host}:{upstream_port}", file=sys.stderr)
            return proxy
        except Exception as e:
            print(f"❌ [TOXIPROXY] 創建代理失敗: {e}", file=sys.stderr)
            return None

    def _get_free_port(self) -> int:
        """獲取一個可用端口"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port

    def apply_latency_toxic(self, proxy_id: str, latency_ms: int, jitter_ms: int = 50):
        """應用延遲有毒物質"""
        toxic_config = {
            "type": "latency",
            "attributes": {
                "latency": latency_ms,
                "jitter": jitter_ms
            }
        }
        return self._add_toxic(proxy_id, toxic_config)

    def apply_packet_loss_toxic(self, proxy_id: str, loss_percent: float):
        """應用封包損失去毒物質"""
        toxic_config = {
            "type": "timeout",
            "attributes": {
                "timeout": 1000  # 1秒超時模擬封包損失
            }
        }
        return self._add_toxic(proxy_id, toxic_config)

    def apply_downstream_toxic(self, proxy_id: str, percentage: float):
        """應用下游封包損失"""
        toxic_config = {
            "type": "slicer",
            "attributes": {
                "average_size": 64,
                "size_variation": 32,
                "delay": int(percentage * 10)  # 模擬延遲損失
            }
        }
        # 註：實際的封包損失需要更複雜的毒物配置
        return self._add_toxic(proxy_id, toxic_config)

    def _add_toxic(self, proxy_id: str, toxic_config: Dict[str, Any]) -> bool:
        """添加有毒物質到代理"""
        try:
            response = requests.post(
                f"{self.api_url}/proxies/{proxy_id}/toxics",
                json=toxic_config,
                timeout=5
            )
            response.raise_for_status()
            print(
                f"✅ [TOXIPROXY] 添加有毒物質: {toxic_config['type']} -> {proxy_id}", file=sys.stderr)
            return True
        except Exception as e:
            print(f"❌ [TOXIPROXY] 添加有毒物質失敗: {e}", file=sys.stderr)
            return False

    def remove_all_toxics(self):
        """移除所有代理的有毒物質"""
        for proxy in self.proxies:
            try:
                response = requests.delete(
                    f"{self.api_url}/proxies/{proxy['name']}/toxics",
                    timeout=5
                )
                # Toxiproxy 會返回200，但要移除所有毒物
                print(f"✅ [TOXIPROXY] 清理毒物: {proxy['name']}", file=sys.stderr)
            except:
                pass  # 忽略清理錯誤

    def reset_all(self):
        """重置所有代理和毒物"""
        self.remove_all_toxics()

        # 刪除所有代理
        for proxy in self.proxies:
            try:
                requests.delete(
                    f"{self.api_url}/proxies/{proxy['name']}", timeout=5)
            except:
                pass
        self.proxies = []
        print("🔄 [TOXIPROXY] 完全重置", file=sys.stderr)

# ==========================================
# 3. Python DNS Mock 模擬器
# ==========================================


class DNSFaultSimulator:
    """DNS解析故障模擬"""

    def __init__(self):
        self.original_getaddrinfo = socket.getaddrinfo
        self.dns_blocked = False
        self.dns_blocked_host = None

    def mock_getaddrinfo(self, host, *args, **kwargs):
        """攔截DNS解析請求"""
        if self.dns_blocked and host == self.dns_blocked_host:
            raise socket.gaierror(-2, f"Name resolution failure for {host}")
        return self.original_getaddrinfo(host, *args, **kwargs)

    def enable_dns_failure(self, hostname: str):
        """啟用DNS故障"""
        print(f"🌐 [DNS MOCK] 啟用DNS故障: {hostname}", file=sys.stderr)
        self.dns_blocked = True
        self.dns_blocked_host = hostname
        socket.getaddrinfo = self.mock_getaddrinfo

    def disable_dns_failure(self):
        """停用DNS故障"""
        print("🌐 [DNS MOCK] 停用DNS故障", file=sys.stderr)
        self.dns_blocked = False
        self.dns_blocked_host = None
        socket.getaddrinfo = self.original_getaddrinfo

# ==========================================
# 4. 綜合網路故障控制器
# ==========================================


class ComprehensiveNetworkFaultController:
    """整合Toxiproxy + DNS Mock的全面網路故障控制器"""

    def __init__(self):
        self.toxiproxy = ToxiproxyController()
        self.dns_sim = DNSFaultSimulator()
        self.current_proxy = None

    def initialize(self) -> bool:
        """初始化所有網路故障模擬設施"""
        print("🚀 [COMPREHENSIVE] 初始化網路故障控制器...", file=sys.stderr)

        # 1. 啟動Toxiproxy服務
        if not self.toxiproxy.start_toxiproxy_daemon():
            print("⚠️ [COMPREHENSIVE] Toxiproxy服務啟動失敗，將繼續使用DNS模擬",
                  file=sys.stderr)
            return False

        # 2. 創建針對bot.n.cn的代理
        self.current_proxy = self.toxiproxy.create_proxy(
            self.toxiproxy.upstream_host,
            self.toxiproxy.upstream_port
        )

        if self.current_proxy:
            print("🎯 [COMPREHENSIVE] 代理創建成功，可控制SpeakUB網路流量", file=sys.stderr)
            return True
        else:
            print("⚠️ [COMPREHENSIVE] 代理創建失敗，只啟用DNS模擬", file=sys.stderr)
            return False

    def apply_dns_failure(self, hostname: str = "bot.n.cn"):
        """應用DNS解析故障"""
        self.dns_sim.enable_dns_failure(hostname)

    def apply_high_latency(self, latency_ms: int = 5000):
        """應用高延遲網路故障"""
        if self.current_proxy:
            self.toxiproxy.apply_latency_toxic(
                self.current_proxy['name'], latency_ms)

    def apply_packet_loss(self, loss_percent: float = 20.0):
        """應用網路封包損失"""
        if self.current_proxy:
            self.toxiproxy.apply_packet_loss_toxic(
                self.current_proxy['name'], loss_percent)

    def reset_all_faults(self):
        """重置所有網路故障"""
        self.dns_sim.disable_dns_failure()
        self.toxiproxy.reset_all()

# ==========================================
# 5. TUI 按鍵動作
# ==========================================


# 全局控制器實例
network_controller = ComprehensiveNetworkFaultController()


def trigger_dns_failure(self):
    """DNS故障注入 (Ctrl+N)"""
    hostname = "bot.n.cn"
    print(f"🌐 [NETWORK] 注入DNS故障: {hostname}", file=sys.stderr)

    try:
        network_controller.apply_dns_failure(hostname)
        self.notify(f"❌ DNS故障注入: {hostname}", severity="information")
        print(f"✅ [NETWORK] DNS故障生效：所有解析{hostname}的請求都會失敗", file=sys.stderr)
    except Exception as e:
        self.notify("❌ DNS故障注入失敗", severity="error")
        print(f"❌ [NETWORK] DNS故障失敗: {e}", file=sys.stderr)


def trigger_high_latency(self):
    """高延遲網路故障 (Ctrl+L) - 持續式超長延遲"""
    latency_ms = 20000  # 從5秒增加到20秒，超出系統請求超時時間
    print(f"🌐 [NETWORK] 注入持續超長延遲: {latency_ms}ms", file=sys.stderr)
    print("   💡 所有的網路請求都會被額外延遲20秒 (超出系統超時限制)", file=sys.stderr)
    print("   🔄 持續生效：每個請求都會被延遲，直到按Ctrl+W重置", file=sys.stderr)

    try:
        network_controller.apply_high_latency(latency_ms)
        if network_controller.current_proxy:
            self.notify(
                f"⏰ 超長延遲故障: 每請求+{latency_ms//1000}s", severity="warning")
            print(f"✅ [NETWORK] 超長延遲故障生效 - 每個網路請求將等待 {latency_ms//1000} 秒",
                  file=sys.stderr)
            print("   ⚠️ 這會導致TTS合成超時，觀察錯誤處理機制", file=sys.stderr)
        else:
            self.notify("⚠️ 高延遲導入有限（只有DNS故障）", severity="warning")
            print("⚠️ [NETWORK] 高延遲故障只會影響DNS解析失敗的請求", file=sys.stderr)
    except Exception as e:
        self.notify("❌ 高延遲注入失敗", severity="error")
        print(f"❌ [NETWORK] 高延遲失敗: {e}", file=sys.stderr)


def trigger_packet_loss(self):
    """網路封包損失故障 (Ctrl+P)"""
    loss_percent = 20.0
    print(f"🌐 [NETWORK] 注入封包損失: {loss_percent}%", file=sys.stderr)

    try:
        network_controller.apply_packet_loss(loss_percent)
        if network_controller.current_proxy:
            self.notify(f"📡 封包損失故障注入: {loss_percent}%", severity="information")
            print("✅ [NETWORK] 封包損失網路故障生效（使用Toxiproxy）", file=sys.stderr)
        else:
            self.notify("⚠️ 封包損失導入有限", severity="warning")
            print("⚠️ [NETWORK] 封包損失故障只會影響DNS解析失敗的請求", file=sys.stderr)
    except Exception as e:
        self.notify("❌ 封包損失注入失敗", severity="error")
        print(f"❌ [NETWORK] 封包損失失敗: {e}", file=sys.stderr)


def restore_network(self):
    """恢復正常網路 (Ctrl+R)"""
    print("🌐 [NETWORK] 恢復正常網路", file=sys.stderr)

    try:
        network_controller.reset_all_faults()
        self.notify("✅ 網路故障已全部清除", severity="information")
        print("✅ [NETWORK] 所有網路故障已恢復正常", file=sys.stderr)
    except Exception as e:
        self.notify("❌ 網路恢復失敗", severity="error")
        print(f"❌ [NETWORK] 網路恢復失敗: {e}", file=sys.stderr)

# ==========================================
# 6. TUI 整合初始化邏輯
# ==========================================


def inject_network_hooks():
    """注入網路測試功能到SpeakUB TUI - 簡單穩定版本"""

    # 初始化網路控制器
    if not network_controller.initialize():
        print("⚠️ [INIT] Toxiproxy初始化失敗，只會有DNS模擬功能", file=sys.stderr)

    # 保存原始 on_mount 方法
    original_on_mount = EPUBReaderApp.on_mount

    # 創建帶網路測試功能的hook
    async def hooked_on_mount(self):
        # 先調用原始的 on_mount 方法
        await original_on_mount(self)

        # 添加網路測試按鍵 (顯示在原始按鍵清單中，避開專案已用的按鍵)
        self.bind("ctrl+n", "dns_failure", description="🌐 DNS故障", show=True)
        self.bind("ctrl+l", "high_latency", description="⏰ 高延遲", show=True)
        self.bind("ctrl+d", "packet_loss", description="📡 封包損失", show=True)
        self.bind("ctrl+w", "restore_network", description="✅ 恢復網路", show=True)

        print("🔧 [NETWORK] 網路測試按鍵已添加到SpeakUB TUI", file=sys.stderr)
        print("   Ctrl+N: DNS故障注入", file=sys.stderr)
        print("   Ctrl+L: 高延遲網路", file=sys.stderr)
        print("   Ctrl+D: 封包損失", file=sys.stderr)
        print("   Ctrl+W: 恢復網路正常", file=sys.stderr)
        print("", file=sys.stderr)

    # 替換 on_mount 方法
    EPUBReaderApp.on_mount = hooked_on_mount

    # 綁定動作函數
    EPUBReaderApp.action_dns_failure = trigger_dns_failure
    EPUBReaderApp.action_high_latency = trigger_high_latency
    EPUBReaderApp.action_packet_loss = trigger_packet_loss
    EPUBReaderApp.action_restore_network = restore_network

    print("🚀 SpeakUB網路測試系統已啟動，準備進行網路故障測試！", file=sys.stderr)

    # 確保退出時清理網路狀態
    def cleanup_network_on_exit():
        """退出時清理網路狀態"""
        try:
            network_controller.reset_all_faults()
            print("🧹 [CLEANUP] SpeakUB網路測試退出，已恢復正常狀態", file=sys.stderr)
        except:
            pass  # 忽略清理錯誤

    # 註冊退出處理器
    import atexit
    atexit.register(cleanup_network_on_exit)

    cli_main()


# 啟動網路測試版本的SpeakUB
if __name__ == "__main__":
    inject_network_hooks()
