# 引擎切换修复备忘录

**日期**: 2025年12月9日  
**问题**: Voice Selector 引擎切换导致当前合成任务被中断、章节跳跃或卡住  
**状态**: ✅ 已修复

---

## 问题背景

### 初始症状
- 执行合成过程中反复切换引擎会发生**卡住**或**跳章节**问题
- 用户选择不同的 TTS 引擎时，当前的语音合成不会平稳处理
- 引擎切换后可能导致播放状态不一致

### 根本原因
之前的引擎切换逻辑使用**硬停** (hard stop) 方式：
```python
# ❌ 错误做法
task.cancel()  # 车子还在开，就直接踢用户下车
tts_integration.stop_speaking()  # 又踢一次
tts_integration._async_tts_stop_requested.set()  # 硬停
```

这相当于：**车子还在开就直接踢用户下车**，导致混乱。

---

## 核心概念：车辆交接的比喻

### 理解 STOPPED 的含义

```
❌ 错误理解：
   - PAUSE = 车子停下来，乘客等待恢复
   - STOPPED = 只是延迟停止，之后还会继续

✅ 正确理解：
   - STOPPED = 车子完全停下来，任务清除，等待用户决定下一步
```

### 正确的引擎切换流程（A车 → B车）

```
┌─────────────────────────────────────────────────────────────┐
│ 1️⃣  A车停车（当前车停止）                                      │
│    └─ 设置 _engine_switching = True                         │
│                                                             │
│ 2️⃣  Serial Runner 停止（STOPPED）                            │
│    └─ 检测到 _engine_switching 标记                          │
│    └─ break（立即退出循环）                                   │
│                                                             │
│ 3️⃣  乘客下车（清除任务）                                      │
│    └─ 立即清除所有 speak_task                               │
│    └─ 清空 _tts_active_tasks 列表                          │
│    └─ finally 块设置状态为 STOPPED                          │
│                                                             │
│ 4️⃣  引擎切换（更换车辆）                                      │
│    └─ A引擎 → B引擎                                        │
│    └─ 初始化 B引擎                                         │
│                                                             │
│ 5️⃣  B车准备好（上车）                                        │
│    └─ 清除 _engine_switching 标记                          │
│    └─ B车也是 STOPPED 状态                                │
│                                                             │
│ 6️⃣  等待用户决定（停着等）                                    │
│    └─ 不由脚本自动执行                                      │
│    └─ 等待用户按下 PLAY 按钮                                │
│                                                             │
│ 7️⃣  用户决定开车（Resume）                                   │
│    └─ 启动新的 Serial Runner（B车）                         │
│    └─ 从停下的位置继续播放                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 修复实现

### 1. 引擎管理器修改 (`speakub/tts/engine_manager.py`)

#### 立即清除任务（不等待）
```python
# 立即清除所有活躍的 speak_task，不等待
if hasattr(tts_integration, '_tts_active_tasks') and tts_integration._tts_active_tasks:
    pending_tasks = list(tts_integration._tts_active_tasks)
    if pending_tasks:
        logger.info(f"Clearing {len(pending_tasks)} active TTS tasks immediately")
        # 強制取消所有任務
        for task in pending_tasks:
            if not task.done():
                task.cancel()
        
        # 清空列表
        tts_integration._tts_active_tasks.clear()
        logger.info("All active tasks cleared")
```

**关键点**：
- ✅ 不使用 `asyncio.wait()` 等待
- ✅ 直接调用 `cancel()` 清除任务
- ✅ 立即清空列表

#### 删除标记设置
```python
# ❌ 不再做这些
# tts_integration._async_tts_stop_requested.set()  # 这会导致混乱
# task.cancel() 然后 await task  # 这样等待太久

# ✅ 现在只做
tts_integration._engine_switching = True  # 标记引擎在切换
# 清除任务（见上面）
```

**原因**：
- `_async_tts_stop_requested` 会打断所有地方的检查
- 导致状态不一致
- 让系统认为要完全停止播放（而不是引擎切换）

### 2. Serial Runner 修改 (`speakub/tts/ui/runners.py`)

#### 添加停止原因标记
```python
async def tts_runner_serial_async(tts_integration: "TTSIntegration") -> None:
    # ... 初始化 ...
    stopped_due_to_engine_switch = False  # 标记引擎切换停止
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # ... 其他检查 ...
```

#### 检测引擎切换并立即停止
```python
# 检测引擎切换
if getattr(tts_integration, '_engine_switching', False):
    logger.info("Engine switch detected, stopping runner (STOPPED)")
    stopped_due_to_engine_switch = True
    break  # 立即停止，不是暂停
```

**关键点**：
- ✅ 使用 `break` 而不是 `continue`（STOPPED 而不是 PAUSE）
- ✅ 记录停止原因
- ✅ 不等待任何东西

#### Finally 块处理状态
```python
finally:
    with tts_integration.tts_lock:
        # 如果因为引擎切换而停止，设置为 STOPPED
        if (
            (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
            and app.tts_status == "PLAYING"
        ):
            app.set_tts_status("STOPPED")
```

**关键点**：
- ✅ 确保状态一致性
- ✅ 引擎切换时设置为 STOPPED
- ✅ 停止请求时也设置为 STOPPED

---

## 修复前后对比

### ❌ 修复前的流程（有问题）

```
1. 用户切换引擎
   ↓
2. 硬停：task.cancel() + stop_speaking()
   ↓
3. 当前合成任务被中断（车还在开就踢下来）
   ↓
4. Serial Runner 继续运行
   ↓
5. 加载下一章（跳章了！）
   ↓
6. 状态混乱（UI显示 "PLAYING" 但实际已切换）
```

### ✅ 修复后的流程（正确）

```
1. 用户切换引擎
   ↓
2. 设置 _engine_switching = True
   ↓
3. Serial Runner 检测到标记 → break（STOPPED）
   ↓
4. 立即清除所有任务（乘客下车）
   ↓
5. 状态设为 STOPPED（车子停好了）
   ↓
6. 引擎切换（更换车辆）
   ↓
7. 清除标记，B引擎准备
   ↓
8. 等待用户按 PLAY（乘客决定什么时候开车）
   ↓
9. 启动新 Serial Runner（从停下位置继续）
```

---

## 主要改变总结

| 项目 | 修复前 | 修复后 |
|-----|------|------|
| **停止方式** | `task.cancel()` + `stop_speaking()` | 清除 `_tts_active_tasks` |
| **标记使用** | `_async_tts_stop_requested.set()` | 只用 `_engine_switching = True` |
| **等待逻辑** | 等待任务完成（3-5秒） | 立即清除（不等待） |
| **Serial Runner** | `continue`（暂停后继续） | `break`（完全停止） |
| **状态管理** | 状态不一致 | finally 块确保 STOPPED |
| **用户体验** | 跳章、混乱 | 平顺交接、用户控制 |

---

## 关键设计决策

### 1. 为什么不使用 `_async_tts_stop_requested`？

```python
# ❌ 错误
tts_integration._async_tts_stop_requested.set()

# 问题：
# - 这会影响整个系统的所有地方
# - 会导致其他地方认为用户要停止播放（而不是切换引擎）
# - 状态转换不明确
```

### 2. 为什么用 `break` 而不是 `continue`？

```python
# ❌ 暂停（PAUSE）
if _engine_switching:
    await asyncio.sleep(0.1)
    continue  # 还会继续循环

# ✅ 停止（STOPPED）
if _engine_switching:
    break  # 完全退出循环
```

**原因**：
- 引擎切换时，当前 Serial Runner 应该完全停止
- 新 Serial Runner 会在用户按 PLAY 时启动
- 不应该继续原 Runner 的循环

### 3. 为什么要立即清除任务？

```python
# ❌ 等待
await asyncio.wait(pending_tasks, timeout=3.0)

# ✅ 立即清除
tts_integration._tts_active_tasks.clear()

# 原因：
# - STOPPED 就是立即停止，不等待
# - 等待可能导致超时
# - 清除后新 Serial Runner 可以立即启动
```

---

## 测试验证

### 场景 1: 单次引擎切换
```
1. 播放 GTTS
2. 切换到 Edge-TTS
   ✅ 当前合成停止
   ✅ 状态变为 STOPPED
   ✅ 系统准备好
   
3. 用户按 PLAY
   ✅ 新 Serial Runner 启动
   ✅ 从停下位置继续
```

### 场景 2: 快速反复切换
```
1. 播放 GTTS
2. 快速切换：GTTS → Edge-TTS → GTTS
   ✅ 每次切换都是干净的
   ✅ 没有卡住或混乱
   ✅ 状态始终一致
   
3. 最后按 PLAY
   ✅ 最后一个引擎启动正常
```

### 场景 3: 在合成过程中切换
```
1. Edge-TTS 正在合成 "长文本..."
2. 用户切换到 GTTS
   ✅ 立即清除合成任务
   ✅ 不会继续合成长文本
   ✅ 不会跳章
   
3. 用户按 PLAY
   ✅ 从停下位置继续（还是原来的位置）
```

---

## 文件修改清单

### 修改的文件

#### 1. `speakub/tts/engine_manager.py`
- **函数**: `async def switch_engine()`
- **改动**:
  - 移除 `asyncio.wait()` 等待逻辑
  - 改为立即 `task.cancel()` 和 `clear()`
  - 移除 `_async_tts_stop_requested.set()` 调用
  - 只使用 `_engine_switching = True`
  
#### 2. `speakub/tts/ui/runners.py`
- **函数**: `async def tts_runner_serial_async()`
- **改动**:
  - 添加 `stopped_due_to_engine_switch` 标记变量
  - 修改引擎切换检查：`continue` → `break`
  - 更新 finally 块处理引擎切换停止
  - 添加详细日志记录

---

## 关键变量说明

| 变量 | 位置 | 用途 |
|-----|------|------|
| `_engine_switching` | `TTSIntegration` | 标记引擎正在切换 |
| `_tts_active_tasks` | `TTSIntegration` | 活跃的 speak_task 集合 |
| `_async_tts_stop_requested` | `TTSIntegration` | 停止请求事件（不在引擎切换时使用） |
| `stopped_due_to_engine_switch` | Serial Runner 本地 | 本次停止是否因为引擎切换 |

---

## 日志示例

### 正常引擎切换的日志
```
[INFO] Switching to TTS engine: edge-tts
[INFO] Engine switching: STOPPED - clearing active tasks immediately
[INFO] Clearing 1 active TTS tasks immediately
[INFO] All active tasks cleared
[INFO] Tasks cleared: engine switch can proceed
[INFO] Async serial runner: Engine switch detected, stopping runner (STOPPED). Next engine will continue from this point.
[INFO] Engine switching completed: ready for user to resume playback if desired.
```

### 用户恢复播放的日志
```
[DEBUG] Using async serial runner for standard mode
[INFO] Async serial runner: Mode switched to Smooth at main loop, self-terminating.
```

---

## 常见问题 (FAQ)

### Q1: 为什么不自动恢复播放？
**A**: 因为用户切换了引擎，系统不知道用户接下来想做什么。可能用户想：
- 继续播放（新引擎）
- 调整引擎参数
- 进行其他操作

所以应该**等待用户决定**，而不是自动恢复。

### Q2: 如果任务没有正确清除会怎样？
**A**: 可能导致：
- 新 Serial Runner 启动失败（旧 task 还在运行）
- 双重合成（两个引擎同时合成）
- 声音混乱、卡住

这就是为什么 `finally` 块很重要。

### Q3: 能否优化切换速度？
**A**: 当前实现已经是最快的了：
- 不等待（立即清除）
- 立即停止（不暂停）
- 立即清除标记

只能通过优化引擎初始化来加快整体速度。

### Q4: GTTS 和 Edge-TTS 切换有特殊处理吗？
**A**: 有！有个约束：
```python
# GTTS 不支持 Smooth Mode
if new_engine_name == "gtts":
    if app.tts_smooth_mode:
        app.tts_smooth_mode = False  # 自动禁用
        logger.warning("GTTS does not support smooth mode, disabling smooth mode")
```

---

## 相关代码位置

### 核心文件
- `speakub/tts/engine_manager.py` - 引擎切换逻辑
- `speakub/tts/ui/runners.py` - Serial Runner 实现
- `speakub/tts/integration.py` - TTS 集成（初始化 _engine_switching）

### 相关概念
- Serial Runner: 标准非平滑模式的播放循环
- Smooth Mode: 预读模式（Parallel Runner）
- speak_task: 单个文本的合成任务
- Playlist Manager: 播放列表管理

---

## 修复总结

✅ **问题**: 引擎切换导致任务中断、跳章、卡住  
✅ **根因**: 使用硬停（task.cancel + stop_speaking）  
✅ **解决**: 使用标记驱动的清缘方式  
✅ **效果**: 平顺引擎交接，用户完全控制  

**关键思想**：
> 引擎切换就像车辆交接。不是"车还在开就踢用户下车"，而是"车缓缓停下，乘客安全下车，上新车后，乘客决定什么时候开车"。
