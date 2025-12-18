# 混合異步架構開發指南

## 快速開始

如果你是新開發者，需要理解 SpeakUB 的混合異步架構。

### 核心概念

```
UI 層（同步）
   ↓ [橋接]
異步核心（async/await）
   ↓ [Thread Pool]
底層庫（同步）
```

### 何時使用什麼

| 場景 | 使用方法 | 原因 |
|------|----------|------|
| UI 事件處理 | 同步方法 + 橋接 | UI 調用是同步的 |
| TTS 工作流 | 異步方法 | 不阻塞 UI |
| 關鍵清理 | 同步屏障 | 需要確定性 |
| 資源釋放 | 異步方法 | 可以延遲 |

## 常見任務

### 添加新的 UI 事件處理器

```python
# Step 1: 在 TTSIntegration 添加處理方法
class TTSIntegration:
    def handle_my_ui_event(self) -> None:
        """UI 事件處理器 [同步調用]"""
        # 1. 處理同步邏輯
        self._sync_ui_signal.set()

        # 2. 橋接到異步核心
        self._bridge_to_async_core(
            self._async_my_event,
            "set"
        )

        # 3. 更新狀態
        self.update_status()

# Step 2: 在 Runner 中處理異步事件
async def my_runner(tts_integration):
    while not tts_integration._async_tts_stop_requested.is_set():
        # 檢查你的事件
        if tts_integration._async_my_event.is_set():
            await handle_event()
            tts_integration._async_my_event.clear()
```

### 添加需要確定性清理的操作

```python
class MyComponent:
    def critical_cleanup(self) -> None:
        """關鍵清理 [同步屏障方法]"""
        # ✅ 使用同步操作
        self.stop_workers()
        self.clear_cache()
        self.reset_state()

        # ✅ 函數返回 = 清理完成

    async def optional_cleanup(self) -> None:
        """可選清理 [異步方法]"""
        # ✅ 可以使用異步操作
        await self.release_resources_async()
```

### 切換引擎或重大狀態變更

```python
async def major_state_change(self):
    """重大狀態變更"""
    # Step 1: 同步屏障確保當前狀態清理
    self.stop_current_operation()  # 同步

    # Step 2: 異步清理資源
    await self.cleanup_resources()

    # Step 3: 設置新狀態
    await self.setup_new_state()
```

## 調試技巧

### 檢查事件狀態

```python
def debug_event_state(self):
    """調試事件狀態"""
    logger.debug("Event State Dump:")
    logger.debug(f"  Async stop: {self._async_tts_stop_requested.is_set()}")
    logger.debug(f"  Sync stop: {self._sync_ui_stop_signal.is_set()}")
    logger.debug(f"  Async pause: {self._async_tts_pause_requested.is_set()}")
```

### 驗證同步屏障

```python
def test_sync_barrier():
    """測試同步屏障"""
    # 設置初始狀態
    component.state = "dirty"

    # 調用屏障方法
    component.critical_cleanup()

    # ✅ 立即檢查（屏障保證已完成）
    assert component.state == "clean"
```

### 追蹤橋接調用

```python
def _bridge_to_async_core(self, event, action):
    """橋接機制（帶日誌）"""
    logger.debug(
        f"Bridge: {action} event {event.__class__.__name__} "
        f"from thread {threading.current_thread().name}"
    )

    self._loop.call_soon_threadsafe(
        event.set if action == "set" else event.clear
    )
```

## 常見陷阱

### ❌ 陷阱 1：在異步上下文中使用 threading.Event

```python
# ❌ 錯誤
async def my_worker():
    self.threading_event.wait()  # 會阻塞 event loop!

# ✅ 正確
async def my_worker():
    # 使用異步事件或橋接
    await self._async_event.wait()
```

### ❌ 陷阱 2：假設異步清理立即完成

```python
# ❌ 錯誤
await cleanup_async()
# 清理可能還沒完成
start_new_operation()

# ✅ 正確
cleanup_sync()  # 同步屏障
start_new_operation()  # 安全
```

### ❌ 陷阱 3：在同步方法中使用 await

```python
# ❌ 錯誤
def handle_ui_event(self):
    await some_async_operation()  # SyntaxError!

# ✅ 正確
def handle_ui_event(self):
    # 創建異步任務
    loop = self._get_event_loop()
    loop.create_task(some_async_operation())
```

## 性能考量

### 何時使用線程池

```python
# ✅ 好：I/O 密集型操作
await asyncio.to_thread(synthesize_audio)

# ❌ 不好：CPU 密集型操作（考慮 ProcessPoolExecutor）
await asyncio.to_thread(complex_calculation)

# ✅ 好：阻塞的第三方庫
await asyncio.to_thread(pygame.mixer.play)
```

### 避免過度橋接

```python
# ❌ 不好：頻繁橋接
for i in range(1000):
    self._bridge_to_async_core(event, "set")

# ✅ 好：批量操作
events_to_set = [...]
self._bridge_batch_to_async_core(events_to_set, "set")
```

## 測試策略

### 測試同步方法

```python
def test_sync_method(tts_integration):
    """同步方法可以直接測試"""
    tts_integration.stop_speaking()
    assert tts_integration.playlist_manager.playlist == []
```

### 測試異步方法

```python
@pytest.mark.asyncio
async def test_async_method(tts_integration):
    """異步方法需要 asyncio 測試"""
    await tts_integration.start_playback_async()
    assert tts_integration.get_tts_status() == "PLAYING"
```

### 測試橋接機制

```python
@pytest.mark.asyncio
async def test_bridge(tts_integration):
    """測試同步到異步的橋接"""
    # 同步調用
    tts_integration.handle_tts_play_pause()

    # 等待橋接生效
    await asyncio.sleep(0.1)

    # 驗證異步事件
    assert tts_integration._async_tts_pause_requested.is_set()
```

## 獲取幫助

如果遇到問題：
1. 檢查 [混合異步架構設計](../architecture/hybrid_async_architecture.md)
2. 查看 [已知問題](../known_issues/)
3. 搜索類似的代碼模式
4. 在 Issues 中提問

## 相關文檔

- [架構設計](../architecture/)
- [API 文檔](../api/)
- [測試指南](./testing.md)
