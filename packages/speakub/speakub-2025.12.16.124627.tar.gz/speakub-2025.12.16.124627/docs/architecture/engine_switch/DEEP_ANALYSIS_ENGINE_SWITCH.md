# 引擎切换机制深度分析

**目的**: 详细解答引擎切换相关的四个核心问题

---

## 问题 1: `finally` 块中 `stopped_due_to_engine_switch` 的作用

### 问题描述

在 `finally` 区块中，`stopped_due_to_engine_switch` 旗标是如何被用来确保状态正确设定为 `STOPPED` 的？

### 答案

#### 背景：为什么需要这个旗标？

```python
# ❌ 问题场景：只检查 _async_tts_stop_requested
finally:
    if (
        app.tts_status == "PLAYING"
        and tts_integration._async_tts_stop_requested.is_set()
    ):
        app.set_tts_status("STOPPED")

# 缺陷：
# - 引擎切换时，_async_tts_stop_requested 可能不被设置
# - 所以 finally 块不会执行设置状态的代码
# - 导致状态仍然是 "PLAYING"，但 Runner 已经停止了
# - 新 Runner 启动时状态混乱
```

#### 解决方案：添加本地标记

```python
async def tts_runner_serial_async(tts_integration: "TTSIntegration") -> None:
    # 本地标记：记录本 Runner 停止的原因
    stopped_due_to_engine_switch = False
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # 检测引擎切换
            if getattr(tts_integration, '_engine_switching', False):
                logger.info("Engine switch detected, stopping runner (STOPPED)")
                stopped_due_to_engine_switch = True  # 标记原因
                break
            
            # ... 其他代码 ...
    
    finally:
        with tts_integration.tts_lock:
            # ✅ 现在检查两个条件
            if (
                (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
                and app.tts_status == "PLAYING"
            ):
                app.set_tts_status("STOPPED")
```

#### 工作原理

```
流程 A: 正常停止（用户按 Stop）
  ├─ set _async_tts_stop_requested = True
  ├─ Runner 检测到 → break
  ├─ stopped_due_to_engine_switch = False （未设置）
  └─ finally: 条件 (_async_tts_stop_requested.is_set()) = True → 设置 STOPPED ✅

流程 B: 引擎切换停止
  ├─ set _engine_switching = True
  ├─ Runner 检测到 → set stopped_due_to_engine_switch = True → break
  ├─ _async_tts_stop_requested = False （未设置）
  └─ finally: 条件 (stopped_due_to_engine_switch) = True → 设置 STOPPED ✅

流程 C: 同时停止和引擎切换（边缘情况）
  ├─ set _async_tts_stop_requested = True AND _engine_switching = True
  ├─ Runner 检测到其中一个 → break
  ├─ stopped_due_to_engine_switch = True/False （取决于检测顺序）
  └─ finally: 条件 (stopped_due_to_engine_switch OR _async_tts_stop_requested.is_set()) = True ✅
```

#### 关键优势

```python
# 单一责任原则：
# - _engine_switching: 全局的"引擎在切换"信号
# - stopped_due_to_engine_switch: 本 Runner 的停止原因记录

# 状态一致性保证：
# 无论通过哪个路径停止，finally 块都能正确处理
if (
    (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
    and app.tts_status == "PLAYING"
):
    app.set_tts_status("STOPPED")

# 这是逻辑上的 OR：
# - stopped_due_to_engine_switch OR _async_tts_stop_requested.is_set() 
# = 至少有一个原因导致停止
```

---

## 问题 2: Parallel Runner 的引擎切换处理

### 问题描述

分析 `tts_runner_parallel_async` 中是如何处理引擎切换的，是否存在类似问题？

### 答案

#### 修复前：存在严重问题

```python
# ❌ 修复前的代码
async def tts_runner_parallel_async(tts_integration: "TTSIntegration") -> None:
    """Smooth Mode 的播放 Runner"""
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # ❌ 没有引擎切换检查
            # ❌ 没有 post-await 验证
            # ❌ 只依赖 _async_tts_stop_requested
            
            with tts_integration.tts_lock:
                exhausted = playlist_manager.is_exhausted()

            if exhausted:
                # ⚠️ 长时间 await，期间可能发生引擎切换
                success = await tts_load_next_chapter_async(playlist_manager)
                # ❌ await 完成后，没有重新检查当前状态
                # 可能 app.tts_engine 已经变了！
```

**风险场景**:
```
T0: Parallel Runner 在 await tts_load_next_chapter_async() 中
T1: 用户切换引擎
T2: Engine Manager 设置 _engine_switching = True
T3: Engine Manager 清除任务
T4: Engine Manager 销毁旧引擎，初始化新引擎
T5: await 完成，Runner 继续执行
T6: ❌ Runner 使用 app.tts_engine，但这已经是新引擎了
    可能导致数据不一致、崩溃或死锁
```

#### 修复后：三层保护

```python
# ✅ 修复后的代码
async def tts_runner_parallel_async(tts_integration: "TTSIntegration") -> None:
    stopped_due_to_engine_switch = False  # 新增
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # [第一层] 主循环检查
            if getattr(tts_integration, '_engine_switching', False):
                logger.info("Engine switch detected, stopping runner (STOPPED)")
                stopped_due_to_engine_switch = True
                break
            
            # [第一层] 模式检查
            if not app.tts_smooth_mode:
                logger.info("Mode switched to Serial, self-terminating")
                break
            
            with tts_integration.tts_lock:
                exhausted = playlist_manager.is_exhausted()

            if exhausted:
                success = await tts_load_next_chapter_async(playlist_manager)
                
                # [第二层] Post-Await 身份验证（关键！）
                if getattr(tts_integration, '_engine_switching', False):
                    logger.info("Engine switch detected after chapter load, aborting")
                    stopped_due_to_engine_switch = True
                    break
                
                if not app.tts_smooth_mode:
                    logger.info("Mode switched to Serial after chapter load, self-terminating")
                    break
                
                if tts_integration._async_tts_stop_requested.is_set():
                    logger.info("Stop requested after chapter load, aborting")
                    break
```

#### 修复要点对比

| 检查点 | 修复前 | 修复后 | 作用 |
|--------|------|------|------|
| 主循环开始 | ❌ | ✅ | 快速检测大多数情况 |
| Post-await | ❌ | ✅ | 防止 await 期间的变化 |
| 模式切换检查 | ❌ | ✅ | Smooth→Serial 切换 |
| Finally 状态管理 | ⚠️ 部分 | ✅ 完整 | 状态一致性 |

#### 为什么 Post-Await 检查至关重要

```python
# Post-Await 是防守最后一道防线

try:
    # 可能是长时间的 await
    success = await tts_load_next_chapter_async(playlist_manager)  # T0-T5: 5秒+
except:
    pass

# T5 时刻：await 返回
# 系统此刻的状态可能完全不同了
# 必须重新验证所有假设
if getattr(tts_integration, '_engine_switching', False):  # ← 关键防线
    break
```

---

## 问题 3: `stop_speaking()` 方法的实现

### 问题描述

分析 `tts_integration.stop_speaking()` 方法的实现，它如何与 `_async_tts_stop_requested` 事件互动？

### 答案

#### 定位 stop_speaking() 方法

```python
# speakub/tts/integration.py
class TTSIntegration:
    def stop_speaking(self, is_pause: bool = False) -> None:
        """Stop or pause the TTS playback."""
        logger.info(f"Stopping TTS playback (pause={is_pause})")
        
        # 核心动作：设置停止事件
        self._async_tts_stop_requested.set()  # ← 关键行
        
        if is_pause:
            self._async_tts_pause_requested.set()  # 暂停标记
        
        # ... 其他清理 ...
```

#### 与 `_async_tts_stop_requested` 的交互

```
停止流程：
  ├─ 用户点击"停止" 按钮
  ├─ UI 调用 app.stop_speaking()
  │
  ├─ stop_speaking() 执行：
  │  ├─ _async_tts_stop_requested.set()  ← 设置事件
  │  └─ Logger: "Stopping TTS playback"
  │
  ├─ Runner 检测到事件：
  │  ├─ while not _async_tts_stop_requested.is_set():  ← 条件变为 False
  │  └─ 循环终止
  │
  └─ Runner 清理：
     ├─ Finally 块执行
     └─ app.set_tts_status("STOPPED")
```

#### 重要：stop_speaking() 不用于引擎切换

```python
# ❌ 引擎切换时不应该调用 stop_speaking()
# 因为：
# 1. stop_speaking() 设置 _async_tts_stop_requested
# 2. 这会被系统的其他地方解释为"用户停止"
# 3. 而不是"引擎在切换"
# 4. 导致状态不一致

# ✅ 引擎切换使用专门的 _engine_switching 标记
tts_integration._engine_switching = True  # 引擎切换专用

# ✅ 停止使用 stop_speaking()
tts_integration.stop_speaking(is_pause=False)  # 用户停止
```

#### 事件的具体作用

```python
# asyncio.Event 是一个同步原语
self._async_tts_stop_requested = asyncio.Event()

# 三个关键方法：
_async_tts_stop_requested.set()     # 设置事件为 True
_async_tts_stop_requested.is_set()  # 查询是否为 True
_async_tts_stop_requested.clear()   # 重置为 False

# 在 Runner 中的用法
while not self._async_tts_stop_requested.is_set():
    # 循环运行
    # 当 is_set() 返回 True 时，not True = False，循环终止

# await 事件的用法
await self._async_tts_stop_requested.wait()  # 等待直到 set()
```

#### 完整的 stop_speaking() 实现

```python
def stop_speaking(self, is_pause: bool = False) -> None:
    """
    Stop the TTS playback.
    
    Args:
        is_pause: If True, also set pause signal (暂停)
                 If False, just stop (停止)
    """
    logger.info(f"Stopping TTS playback (pause={is_pause})")
    
    # 核心：设置停止事件
    # 所有 Runner 都在检查这个事件
    self._async_tts_stop_requested.set()  # ← 通知所有 Runner 停止
    
    # 如果是暂停，还要设置暂停标记
    if is_pause:
        self._async_tts_pause_requested.set()  # 暂停信号
    
    # 尝试停止播放器
    if self.app.tts_engine:
        try:
            if hasattr(self.app.tts_engine, 'stop'):
                self.app.tts_engine.stop()  # 停止引擎播放
        except Exception as e:
            logger.debug(f"Error stopping engine: {e}")
    
    # 取消所有活跃任务
    for task in self._tts_active_tasks:
        if not task.done():
            task.cancel()
    
    # 更新状态（可能）
    if not is_pause:
        self.set_tts_status_safe("STOPPED")
    else:
        self.set_tts_status_safe("PAUSED")
```

#### 恢复暂停

```python
def resume_speaking(self) -> None:
    """Resume paused playback."""
    # 清除暂停和停止信号
    self._async_tts_pause_requested.clear()
    self._async_tts_stop_requested.clear()
    
    # Runner 会继续执行
    # while not _async_tts_stop_requested.is_set():  ← 现在为 True，继续循环
```

#### 与 _engine_switching 的区别

```python
# stop_speaking() vs. 引擎切换

# 使用 stop_speaking() 的场景：
stop_speaking()  # 用户按下停止按钮
stop_speaking(is_pause=True)  # 用户按下暂停按钮

# 使用 _engine_switching 的场景：
_engine_switching = True  # 用户切换引擎
# （不调用 stop_speaking，因为意义不同）
```

---

## 问题 4：三个标记的完整对比

### 标记矩阵

```
┌─────────────────────┬──────────────────┬──────────────────┬──────────────────┐
│ 标记名称             │ _async_tts_stop_requested | _async_tts_pause_requested | _engine_switching |
├─────────────────────┼──────────────────┼──────────────────┼──────────────────┤
│ 类型                │ asyncio.Event    │ asyncio.Event    │ bool           │
│ 范围                │ 全局             │ 全局             │ 全局           │
│ 设置者              │ stop_speaking()  │ stop_speaking()  │ switch_engine()│
│ 清除者              │ resume_speaking()│ resume_speaking()│ finally块      │
│ 含义                │ 用户停止播放     │ 用户暂停播放     │ 引擎在切换     │
│ Runner 检查方式    │ while not .is_set() | 循环内检查   │ if getattr()   │
│ 会导致 STOPPED?    │ ✅ 是           │ ❌ 否（暂停）    │ ✅ 是         │
│ 自动恢复？         │ ❌ 需要 PLAY    │ ❌ 需要 PLAY    │ ❌ 需要 PLAY  │
└─────────────────────┴──────────────────┴──────────────────┴──────────────────┘
```

### 用户交互流程

```
用户按下停止 → stop_speaking()
  ├─ set _async_tts_stop_requested = True
  ├─ set _async_tts_pause_requested = True
  └─ Runner break → STOPPED
       ↓
用户按下播放 → resume_speaking() + start_playback()
  ├─ clear _async_tts_stop_requested = False
  ├─ clear _async_tts_pause_requested = False
  └─ 新 Runner 启动

用户切换引擎 → switch_engine()
  ├─ set _engine_switching = True
  ├─ Runner 检测到 break → STOPPED
  ├─ 清除任务、切换引擎
  └─ finally: reset _engine_switching = False
       ↓
用户按下播放 → start_playback()
  └─ 新 Runner 启动（新引擎）
```

---

## 总结表格

| 问题 | 答案要点 | 关键代码 |
|-----|--------|---------|
| finally 块如何用 stopped_due_to_engine_switch？ | OR 条件：只要有一个原因就设置 STOPPED | `(stopped_due_to_engine_switch OR _async_tts_stop_requested.is_set())` |
| Parallel Runner 有问题吗？ | 有，缺少 post-await 检查，已修复 | 三层检查点：主循环、post-await、状态管理 |
| stop_speaking() 如何工作？ | 设置 _async_tts_stop_requested 事件 | `self._async_tts_stop_requested.set()` |
| 三个标记的区别？ | 不同的停止原因，导致不同的语义 | stop/pause/engine-switch 各有专用标记 |

