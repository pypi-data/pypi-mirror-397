# SpeakUB 鎖定使用規範指南

## 📋 概述

本文檔定義SpeakUB專案中鎖定使用的規範和最佳實踐。基於保守的安全策略，這些規範確保不會重新引入歷史死鎖問題。

**核心原則：鎖定層次結構必須嚴格遵守，任何違規都可能導致死鎖。**

---

## 🏗️ 鎖定層次結構

### 三層架構設計

| 層次 | 鎖定名稱 | 類型 | 用途 | 持有時間限制 | 優先權 |
|------|----------|------|------|--------------|--------|
| **同步層** | `_tts_lock` | `threading.RLock` | 保護TTS引擎操作、播放列表管理、錯誤處理邏輯 | < 100ms | 高 |
| **異步層** | `_async_tts_lock` | `asyncio.Lock` | 保護異步TTS狀態轉換、任務管理 | < 500ms | 中 |
| **狀態層** | `_status_lock` | `threading.Lock` | 保護TTS狀態變更和訪問 | < 10ms | 低 |

### 層次優先權說明

1. **同步層 (最高優先權)**
   - 確保播放核心線性流程的確定性
   - 共享使用，PlaybackManager作為主要持有者
   - 必須謹慎使用，避免長時間阻塞

2. **異步層 (中等優先權)**
   - 處理狀態轉換和協調
   - 僅在異步上下文中使用
   - 與同步鎖無重疊

3. **狀態層 (最低優先權)**
   - 快速狀態訪問
   - 避免與其他鎖競爭
   - 持有時間極短

---

## 🚫 嚴格禁止的鎖定順序

### 死鎖預防規則

1. **永不允許 同步層 → 異步層 的鎖定順序**
   ```python
   # ❌ 嚴格禁止 - 會導致死鎖
   with self._tts_lock:  # 同步層
       # 不要在這裡獲取異步層鎖定
       async with self._async_tts_lock:  # 異步層
           pass
   ```

2. **狀態層鎖定應儘可能短暫，避免嵌套**
   ```python
   # ❌ 不良實踐
   with self._status_lock:
       # 長時間操作
       time.sleep(0.1)

   # ✅ 正確實踐
   with self._status_lock:
       status = self._current_status  # 立即返回
   ```

3. **共享鎖 (_tts_lock) 應謹慎使用**
   - 優先權高，影響範圍廣
   - 必須有明確的業務理由
   - 記錄持有原因和預期時間

---

## 📝 正確的鎖定使用模式

### 1. 同步層鎖定 (PlaybackManager)

```python
class PlaybackManager:
    def stop_playback(self, is_pause: bool = False) -> None:
        """正確的同步層鎖定使用"""
        start_time = time.time()

        with self.tts_integration._tts_lock:  # 同步層鎖定
            # 立即執行，不包含異步操作
            self._do_sync_stop_operations()

        # 鎖定外處理異步任務
        if self.needs_async_cleanup():
            self.tts_integration.async_bridge.run_async_task(
                self._async_cleanup()
            )

        # 驗證持有時間
        duration = time.time() - start_time
        if duration > 0.1:  # 100ms
            logger.warning(f"_tts_lock held for {duration:.3f}s, exceeds 100ms limit")
```

### 2. 異步層鎖定 (TTSIntegration)

```python
async def _async_handle_synthesis_error(self, error: Exception, failed_index: Optional[int] = None) -> None:
    """正確的異步層鎖定使用"""
    async with self._async_tts_lock:  # 異步層鎖定
        # 異步操作安全區
        await self._do_async_error_handling()

    # 鎖定外處理同步UI更新
    self.set_tts_status_safe("PAUSED")
```

### 3. 狀態層鎖定 (UI操作)

```python
def get_tts_status(self) -> str:
    """狀態層鎖定的正確使用"""
    with self._status_lock:  # 狀態層鎖定
        return self._current_status.value  # 立即返回
```

---

## 🔍 代碼審查檢查點

### 新增鎖定操作檢查

新增任何鎖定相關代碼時，必須通過以下檢查：

- [ ] **層次確認**：確定使用哪一層鎖定
- [ ] **持有時間**：確保不會超過層次限制
- [ ] **順序檢查**：確認不會違反鎖定層次規則
- [ ] **必要性**：是否有明確的並發保護需求
- [ ] **文檔記錄**：記錄鎖定用途和持有時間

### 現有代碼修改檢查

修改現有鎖定邏輯時，必須評估：

- [ ] **影響範圍**：哪些組件會受到影響
- [ ] **歷史問題**：是否會重新引入已修復的問題
- [ ] **測試覆蓋**：是否有足夠的測試驗證新行為
- [ ] **回滾計劃**：萬一出問題，如何快速恢復

---

## 📊 性能監控與告警

### 自動監控指標

系統會自動監控以下指標：

1. **鎖定持有時間**
   - 同步層：> 100ms 發出警告
   - 異步層：> 500ms 發出警告
   - 狀態層：> 10ms 發出錯誤

2. **競爭統計**
   - 等待次數比例 > 10% 發出警告
   - 平均競爭時間 > 1ms 記錄日誌

3. **死鎖檢測**
   - 鎖定長時間持有且有等待者
   - 自動記錄線程堆疊追蹤

### 監控工具使用

```bash
# 檢查當前鎖定狀態
python tools/deadlock_monitor.py status

# 健康檢查（用於CI/CD）
python tools/deadlock_monitor.py health

# 持續監控
python tools/deadlock_monitor.py monitor --interval 5

# 匯出統計數據
python tools/deadlock_monitor.py export stats.json
```

---

## 🚨 緊急處理流程

### 發現死鎖時的處理步驟

1. **立即停止**
   - 不要嘗試修復，優先保護數據
   - 使用監控工具確認死鎖情況

2. **收集診斷信息**
   ```bash
   # 匯出完整統計
   python tools/deadlock_monitor.py export deadlock_stats.json

   # 檢查應用日誌
   grep "BRIDGE\|DEADLOCK" speakub.log
   ```

3. **安全重啟**
   - 確保所有鎖定已釋放
   - 使用協調關閉流程
   - 驗證重啟後狀態正常

4. **根本原因分析**
   - 檢查最近的代碼修改
   - 驗證鎖定使用是否符合規範
   - 更新文檔防止重複問題

---

## 📚 相關文檔

- [混合異步架構設計](hybrid_async_architecture.md) - 整體架構設計
- [AsyncBridge操作目錄](async_bridge_operations.md) - 橋接操作詳解
- [Voice Selector引擎切換跳章分析](../../documents/VOICE_SELECTOR_ENGINE_SWITCH_CHAPTER_JUMP_ANALYSIS.md) - 歷史問題案例

## 🔗 開發者責任

**所有開發者必須**：
- 熟悉並遵守這些鎖定規範
- 在代碼審查中檢查鎖定使用
- 遇到鎖定問題時立即報告
- 參與鎖定相關的架構決策

**違反規範的後果**：
- 可能導致死鎖和系統不穩定
- 需要立即修復，不得延遲
- 嚴重違規可能需要代碼回滾

---

## 📝 變更歷史

- **2025-12-13**: 初始版本，建立完整的鎖定使用規範
- **基於**: Voice Selector跳章問題的教訓，強調保守策略

---

**本文檔由SpeakUB架構安全委員會維護。如有疑問，請在代碼審查中提出。**
