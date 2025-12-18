# 為什麼純 Asyncio 架構失敗

## 問題描述

嘗試將 SpeakUB 純化為完全 Asyncio 架構時，遇到系統性問題。

## 症狀

**配置**：
- Smooth Mode 啟用
- 跨引擎切換（Edge-TTS ↔ Nanmai）

**現象**：
1. 切換引擎後開始播放
2. 只處理一個批次
3. 停止，不再觸發新批次
4. 需要手動停止並重新播放

**可重現性**：
100%（在上述配置下）

## 根本原因

### 直接原因

Predictive Controller 使用了舊引擎的預測參數：
- 合成速度估計
- 批次大小預測
- 觸發閾值

### 深層原因

純異步架構中，引擎切換時的狀態清理有延遲：

```python
# 純異步的問題時間線
T0: switch_engine() 開始
T1: await stop_async()        # 開始停止
T2: await cleanup_async()     # 開始清理
T3: await reset_async()       # 開始重置
T4: _async_stop_flag.clear()  # 清除標誌
T5: await setup_new_engine()  # 設置新引擎
T6: await start_playback()    # 開始播放

問題：T6 可能在 T4 之前執行
結果：新播放看到舊的停止標誌
```

### 根本原因

缺少同步屏障機制：
- Asyncio 的 `await` 會讓出控制權
- 無法保證清理操作的完成時機
- 狀態變更不是立即生效的

## 為什麼混合架構能解決

混合架構使用同步屏障：

```python
# 混合架構的正確時間線
T0: switch_engine() 開始
T1: stop_speaking()           # 同步屏障
    ├─ 停止播放（同步等待）
    ├─ 重置狀態（立即生效）
    └─ 清除標誌（立即生效）
T2: ✅ 此時狀態已確定清理完成
T3: await cleanup_engine()    # 安全：在乾淨狀態
T4: await setup_new_engine()  # 安全：在乾淨狀態
T5: await start_playback()    # 安全：一定是乾淨狀態
```

## 實驗數據

### 測試場景

1. 使用 Edge-TTS 播放 5 個批次
2. 切換到 Nanmai
3. 觀察播放行為

### 結果

| 架構 | 批次處理數 | 狀態 |
|------|------------|------|
| 純 Asyncio | 1 | ❌ 失敗 |
| 混合架構 | 5+ | ✅ 正常 |

### 日誌分析

**純 Asyncio（失敗）**：
```
[INFO] Starting playback with Nanmai
[DEBUG] Batch 1 triggered
[DEBUG] Batch 1 completed
[DEBUG] Checking stop flag: True  ← ❌ 舊標誌未清除
[INFO] Playback stopped
```

**混合架構（成功）**：
```
[INFO] Starting playback with Nanmai
[DEBUG] Batch 1 triggered
[DEBUG] Batch 1 completed
[DEBUG] Checking stop flag: False  ← ✅ 標誌已清除
[DEBUG] Batch 2 triggered
[DEBUG] Batch 2 completed
...
```

## 結論

### 技術結論

純 Asyncio 架構不適合 SpeakUB，因為：
1. 底層庫是同步的（Pygame, MPV）
2. 引擎切換需要確定性的狀態清理
3. 異步操作無法提供這種確定性

### 架構決策

保留混合異步架構：
- ✅ 同步屏障確保狀態清理
- ✅ 異步工作流不阻塞 UI
- ✅ 橋接層協調兩者

### 遷移計劃狀態

**Stage 4 遷移計劃：已取消**

理由：實驗證明純 Asyncio 不可行

## 相關文檔

- [混合異步架構設計](./hybrid_async_architecture.md)
- [引擎切換設計](./engine_switching.md)
