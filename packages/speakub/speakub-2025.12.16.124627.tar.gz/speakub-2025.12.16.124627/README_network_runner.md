# SpeakUB Network Runner 使用指南

## 📋 **什么是 Network Runner？**

Network Runner 是专门为 SpeakUB 创建的 **TUI 网络测试插件**，参考了 `tools/debug_runner.py` 的设计模式。

就像 debug_runner.py 添加 'x' 鍵來傾印畫面一樣，
**Network Runner 在 SpeakUB TUI 界面添加网络故障注入功能**。

## 🎯 **核心功能**

- ✅ **在合成过程中手动注入网络故障**
- ✅ **观察 SpeakUB 如何处理合成时的网络错误**
- ✅ **记录完整的日志文件供分析**
- ✅ **零干扰原有 SpeakUB 功能**

## 🚀 **如何使用**

### **推薦：專業網路測試系統 (具備Toxiproxy支持)** ⭐⭐⭐⭐⭐

```bash
# 使用Toxiproxy模擬真實網路故障！
python tools/comprehensive_network_tester.py
```

#### **主要特點**
- ✅ **DNS故障**：Python socket mock，100%準確
- ⚡ **網路延遲**：通過Toxiproxy實現真實延遲模擬
- 📡 **封包損失**：使用Toxiproxy的timeout/限速機制
- 🎯 **業界標準**：採用同樣Shopify生產環境使用的技术
- 🛡️ **不影響系統**：只影響SpeakUB的網路調用
- 📊 **專業級測試**：涵蓋所有常見網路故障模式

**💡 安裝提示：**
```bash
# Fedora 安裝 Toxiproxy
curl -L https://github.com/Shopify/toxiproxy/releases/latest/download/toxiproxy_2.5.0_linux_amd64.tar.gz | tar xz
sudo mv toxiproxy-server toxiproxy-cli /usr/bin/
toxiproxy-cli --version  # 驗證安裝
```

#### **額外備選方案**

**輕量級DNS測試：**
```bash
python tests/mock_network_runner.py  # 只測試DNS故障
```

**完整系統級控制 (需要root)：**
```bash
sudo python tests/network_runner.py  # 完整網路控制
```

---

### **第二步：启动网络测试模式**

```bash
# 运行网络测试模式的 SpeakUB
python tests/network_runner.py
```

### **第三步：在 TUI 中测试网络故障**

Network Runner 会启动专门的 SpeakUB TUI，在您正常使用 SpeakUB 时：

```
1. 🎵 选择 EPUB 文件并开始播放
   ↓
2. 🎯 SpeakUB 开始 TTS 合成
   ↓
3. 🚨 在合成过程中按网络控制键：
   - Ctrl+N: DNS解析失败 (bot.n.cn无法解析)
   - Ctrl+L: 高延迟网络 (5秒延迟)
   - Ctrl+P: 包丢失 (20%随机丢失)
   - Ctrl+R: 恢复正常网络
   ↓
4. 📊 观察 SpeakUB 如何响应网络故障
   ↓
5. 💾 查看日志文件分析合成弹性
```

## 📊 **界面显示**

### **终端输出 (stderr)**
```
🔧 [NETWORK] 網路測試按鍵已注入 TUI 介面
   Ctrl+N: DNS故障 | Ctrl+L: 高延遲 | Ctrl+P: 封包損失 | Ctrl+R: 還原
💡 在SpeakUB合成過程中按這些按鍵來測試網路錯誤處理
🚀 網路測試虛擬環境已就緒。
```

### **TUI 界面通知**
- 🔴 **DNS/ZIP损伤性故障已注入** - 显示在屏幕通知区域
- 🟡 **警告信息** - 当注入失败时显示
- 🟢 **网络恢复成功** - 当恢复正常网络时显示

## 📂 **日志文件位置**

SpeakUB 会自动创建带时间戳的日志文件：
```
~/.local/share/speakub/logs/speakub-YYYYMMDD_HHMMSS.log
```

在这些日志中您可以找到：
- TTS 合成的开始和结束
- 网络故障注入的时间点
- Buffer underrun（缓冲区欠载）
- 缓冲区重新填充尝试
- 其他合成错误处理

## 🔍 **测试场景示例**

### **场景1: 测试 DNS 故障恢复**
```
1. 播放 EPUB 内容
2. 等待 SpeakUB 显示 "正在合成..." 或类似信息
3. 按 Ctrl+N 注入 DNS 故障
4. 观察 SpeakUB 是否显示连接错误
5. 等待 SpeakUB 缓冲区耗尽
6. 按 Ctrl+R 恢复网络
7. 观察 SpeakUB 是否重新开始合成
```

### **场景2: 高延迟网络测试**
```
1. 开始播放内容
2. 在合成过程中按 Ctrl+L 注入高延迟
3. 观察连接是否超时
4. 检查日志中的超时错误
```

## 🔧 **技术架构**

Network Runner 采用**分离架构**：

```
┌─────────────────┐    ┌──────────────────────┐
│  network_runner │────│ network_control      │
│   (TUI 插件)    │    │ service (sudo 模式)  │
└─────────────────┘    └──────────────────────┘
         │                       │
         └─────► speakub.cli ───► speaks SpeakUB TTS
```

- **network_runner**: 在普通用户权限下运行 SpeakUB TUI
- **network_control_service**: 在 root 权限下执行网络配置命令

## 🚫 **常见问题**

### **"tc not found" 错误**
```bash
# 解决方案
sudo dnf install iproute-tc  # Fedora
sudo apt install iproute2    # Ubuntu
```

### **网络注入无响应**
- 确保当前在 SpeakUB 的合成阶段
- 检查终端是否有错误提示
- 确认网络控制服务可正常运行

### **日志文件为空**
- SpeakUB 可能还没有开始合成
- 检查是否正确选择了 EPUB 文件

## 📈 **下一步分析**

收集日志文件后，可以：

1. **分析错误模式**：SpeakUB 在网络故障时的响应速度
2. **评估恢复能力**：网络恢复后合成重新开始的时间
3. **优化缓冲策略**：基于 underrun 数据调整缓冲区大小

---

## 🎉 **开始测试！**

现在您有了一个强大的工具来**手动控制 SpeakUB 合成时的网络环境**，观察它如何处理各种网络故障。这将帮助您深入了解和优化 SpeakUB 的网络弹性和用户体验！
