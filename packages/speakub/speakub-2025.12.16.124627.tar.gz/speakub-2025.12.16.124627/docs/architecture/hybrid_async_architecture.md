# Hybrid Async Architecture: Async預載 + Threading播放

## 架構總覽

SpeakUB採用混合並發架構，將專案分為兩個截然不同的領域，各適用完全不同的並發模型：

### 🏭 後勤補給區（Synthesis / Network） - 適用Asyncio
**任務特性：**
- 下載文字、請求API、合成音檔、寫入快取
- 適合並行處理，可以亂序執行
- **技術選擇：`asyncio`, `aiohttp`**

**核心邏輯：**
```python
# 預載可以並行執行
async def batch_preload():
    tasks = [synthesize_text(text) for text in batch]
    results = await asyncio.gather(*tasks)
```

### 🎭 前台演出區（Playback / Playlist） - 必須保留Threading
**任務特性：**
- `python-mpv` / `pygame` 播放音檔
- `playlist` 切換下一句、控制暫停/繼續
- **必須阻塞（Blocking）** - 因為人類耳朵是線性接收器官

**核心邏輯：**
```python
# 播放必須線性等待
def play_audio_blocking():
    player.play()
    while player.is_playing():  # 阻塞等待
        time.sleep(0.1)
    next_track()  # 然後播放下一首
```

## 為何不能純Async播放？

### 生物限制（Human Constraints）
人類耳朵是**線性（Linear）**接收資訊的器官：
- 無法像眼睛瀏覽網頁一樣「並行下載」聲音
- 必須「說完這句，再說下一句」
- Asyncio的設計初衷是「消滅等待」，但朗讀的等待是核心功能

### 技術問題
```python
# ❌ 錯誤的Async播放
async def wrong_async_playback():
    await player.play_async()  # 這會讓整個應用程式凍結
    next_track()  # 永遠不會執行

# ✅ 正確的混合模式
async def correct_hybrid_playback():
    # 在thread中阻塞播放
    await asyncio.to_thread(player.play_blocking)
    await next_track_async()
```

## 現有實現分析

### PlaybackManager
- 使用`asyncio.create_task`啟動播放任務
- 播放邏輯本身仍為線性阻塞

### Backends (MPV/Pygame)
- MPVBackend: `_wait_for_completion()`使用`threading.Event`
- PygameBackend: `AudioPlayer.play_and_wait()`使用`time.sleep`

### PlaylistManager
- 預載邏輯完全async: `asyncio.Queue`, `asyncio.Lock`
- 播放推進邏輯保持線性

## 架構原則

### 1. 播放器核心 (The Player Core) 是神聖的
- `speakub/tts/backends/` 和 `speakub/tts/playback_manager.py` **必須保持同步/Threaded邏輯**
- 它們代表了「時間的流逝」和「語音的輸出」，這必須是線性且穩定的

### 2. Playlist 是劇本 (The Script)
- Playlist 的推進邏輯必須是嚴格的序列化（Sequential）
- 不應該讓 Asyncio 的併發特性干擾到 Playlist 的 `current_index` 指針移動

### 3. 預載是背景服務
- 使用Async進行預載，提高效率
- 結果靜靜放進Queue，讓播放執行緒單純地從Queue拿東西

## 開發者指南

### ✅ 正確模式
```python
# 預載使用async
async def preload_batch():
    await synthesize_parallel(batch)

# 播放使用threading/blocking
def play_sequence():
    while has_next():
        play_current_blocking()
        advance_to_next()
```

### ❌ 避免的模式
```python
# 不要嘗試async播放
async def bad_async_play():
    await player.play_async()  # 會破壞線性節奏
    await asyncio.sleep(0)     # 無法解決問題
```

## 風險預防

### 未來開發注意事項
1. **永遠不要**將播放邏輯async化
2. **永遠保留**blocking等待作為播放的核心
3. **區分清楚**預載（可以async）和播放（必須blocking）

### 程式碼審查檢查點
- [ ] 播放相關程式碼是否包含`time.sleep`或`threading.Event`？
- [ ] 是否有嘗試使用`await`在播放等待上？
- [ ] 預載邏輯是否正確使用async而非blocking？

## 結論

這個混合架構是SpeakUB的核心競爭力：
- **效能**：預載使用async獲得最大並行度
- **體驗**：播放使用threading維持人類友好的線性節奏
- **穩定**：避免async帶來的不確定性複雜度

**記住**：這個專案的核心價值在於「給耳朵聽」。為了服務這個目的，保留threading來控制線性的播放流程是絕對正確且必要的設計選擇。
