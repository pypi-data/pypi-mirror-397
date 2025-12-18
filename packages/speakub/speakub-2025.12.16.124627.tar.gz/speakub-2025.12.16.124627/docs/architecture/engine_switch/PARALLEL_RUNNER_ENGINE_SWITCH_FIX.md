# Parallel Runner 引擎切换修复备忘录

**日期**: 2025年12月10日  
**补充修复**: Smooth Mode (平行播放) 引擎切换处理  
**状态**: ✅ 已修复

---

## 问题分析

### 发现的缺陷

`tts_runner_parallel_async` (Smooth Mode) 完全缺少引擎切换的处理机制，而 `tts_runner_serial_async` (Standard Mode) 已经有了完整的保护。

**风险场景**：
```
Timeline:
T0: Parallel Runner 在 await asyncio.wait_for(..., timeout=90.0) 中等待合成数据
T1: 用户切换引擎
T2: Engine Manager 设置 _engine_switching = True
T3: Engine Manager 清除 Serial Runner 任务（但 Parallel Runner 还在 await！）
T4: Engine Manager 进行引擎切换：旧引擎 → 新引擎
T5: await 终于完成，Parallel Runner 被唤醒
T6: Parallel Runner 继续执行后续代码
T7: ❌ 问题：app.tts_engine 已经是新引擎，但代码期望的是旧引擎的引用
    导致未定义的行为、崩溃或卡死
```

### 根本原因

**缺少三层检查**：

1. ❌ **主循环检查** - 没有在循环开始检查 `_engine_switching`
2. ❌ **Post-Await 身份验证** - 没有在 `await` 之后重新验证权限
3. ❌ **状态管理** - finally 块没有考虑引擎切换

---

## 修复实现

### 1. 主循环检查（主防线）

```python
# 添加到 while 循环内的最开始
while not tts_integration._async_tts_stop_requested.is_set():
    # [🔥 關鍵：Engine Switch 檢查點]
    if getattr(tts_integration, '_engine_switching', False):
        logger.info("Engine switch detected, stopping runner (STOPPED)")
        stopped_due_to_engine_switch = True
        break
    
    # [🔥 關鍵：Mode Switch 檢查點]
    if not app.tts_smooth_mode:
        logger.info("Mode switched to Serial, self-terminating")
        break
    
    # ... 其他逻辑 ...
```

**目的**：
- ✅ 快速检测引擎切换
- ✅ 如果发生切换，立即退出循环
- ✅ 同时检测 Smooth → Serial 模式切换

### 2. Post-Await 身份验证（关键防线）

```python
# 在 await tts_load_next_chapter_async() 之后
success = await tts_load_next_chapter_async(playlist_manager)

# [🔥 關鍵修復：Post-Await 身分驗證]
# 检查引擎切换
if getattr(tts_integration, '_engine_switching', False):
    logger.info("Engine switch detected after chapter load, aborting")
    stopped_due_to_engine_switch = True
    break

# 检查模式切换
if not app.tts_smooth_mode:
    logger.info("Mode switched to Serial after chapter load, self-terminating")
    break

# 检查停止信号
if tts_integration._async_tts_stop_requested.is_set():
    logger.info("Stop requested after chapter load, aborting")
    break
```

**为什么重要**：
- ✅ 长时间的 `await` 期间，系统可能发生了变化
- ✅ 必须在恢复执行前重新验证
- ✅ 防止"僵尸任务"问题

### 3. 状态管理（最后防线）

```python
finally:
    with tts_integration.tts_lock:
        # 如果因为引擎切换或停止訊號而停止，設置為 STOPPED
        if (
            (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
            and app.tts_status == "PLAYING"
        ):
            app.set_tts_status("STOPPED")
```

**作用**：
- ✅ 确保状态一致性
- ✅ 引擎切换时也设置为 STOPPED
- ✅ 允许新 Runner 正确启动

---

## 修复前后对比

### ❌ 修复前（不安全）

```
Parallel Runner 主循环：
  ├─ 检查 exhausted
  ├─ await tts_load_next_chapter_async()  ← 长时间 await！
  │   └─ 在这里引擎切换发生，但 Runner 不知道
  ├─ 获取当前 item
  ├─ 播放音频
  └─ ❌ 可能使用了已销毁的引擎对象

风险：
  - 无引擎切换检查
  - 无 post-await 验证
  - 状态不一致
```

### ✅ 修复后（安全）

```
Parallel Runner 主循环：
  ├─ [🔥 检查] 引擎切换？ → YES → break
  ├─ [🔥 检查] 模式切换？ → YES → break
  ├─ 检查 exhausted
  ├─ await tts_load_next_chapter_async()
  │   └─ 在这里引擎切换发生，但会在恢复后检查
  ├─ [🔥 检查] 引擎切换？ → YES → break
  ├─ [🔥 检查] 模式切换？ → YES → break
  ├─ [🔥 检查] 停止信号？ → YES → break
  ├─ 获取当前 item
  ├─ 播放音频
  └─ ✅ 使用有效的引擎对象

安全特性：
  - ✅ 三层检查点
  - ✅ Post-await 身份验证
  - ✅ 状态管理完善
```

---

## 关键改变总结

| 项目 | 修复前 | 修复后 |
|-----|------|------|
| **主循环检查** | ❌ 无 | ✅ 检查 `_engine_switching` 和模式 |
| **Post-Await 检查** | ❌ 无 | ✅ 3 项检查（引擎、模式、停止） |
| **模式切换处理** | ❌ 无 | ✅ 检查 `tts_smooth_mode` |
| **状态管理** | ⚠️ 不完整 | ✅ 完整处理引擎切换 |
| **可靠性** | 中等 | 高 |

---

## 测试场景

### 场景 1: 在 Smooth Mode 中切换引擎

```
前置：播放中，Smooth Mode (Parallel Runner)
操作：用户快速切换引擎
期望：
  ✅ Parallel Runner 检测到 _engine_switching
  ✅ 立即 break（STOPPED）
  ✅ 状态设为 STOPPED
  ✅ 引擎切换完成
  ✅ 用户按 PLAY 后，新 Runner 启动
```

### 场景 2: 在 await 期间切换引擎

```
前置：播放中，Smooth Mode，正在加载下一章
操作：用户在 await tts_load_next_chapter_async() 期间切换引擎
期望：
  ✅ Post-Await 检查检测到 _engine_switching
  ✅ 立即 break（STOPPED）
  ✅ 避免使用已失效的引擎对象
  ✅ 系统稳定，无崩溃
```

### 场景 3: Smooth → Serial 模式切换

```
前置：播放中，Smooth Mode (Parallel Runner)
操作：用户禁用 Smooth Mode（例如切到 GTTS）
期望：
  ✅ 主循环或 Post-Await 检查检测到模式切换
  ✅ Parallel Runner 自动终止
  ✅ Serial Runner 启动
  ✅ 播放继续
```

### 场景 4: 快速连续切换多个引擎

```
前置：播放中，Smooth Mode
操作：快速切换：GTTS → Edge-TTS → GTTS → Nanmai
期望：
  ✅ 每次切换都被正确处理
  ✅ 没有死锁或卡住
  ✅ 最后引擎启动正常
  ✅ 没有内存泄漏
```

---

## 设计决策说明

### 为什么需要三层检查？

```
问题场景：
T0: Runner 在检查点 A（主循环开始）
T1: 引擎切换发生
T2: Runner 执行长时间 await
T3: 引擎已切换，但 Runner 还在 await
T4: await 完成，Runner 恢复

解决方案：
- 检查点 A（主循环）：快速发现大多数情况 ✅
- 检查点 B（await 之前）：避免进入问题 await ✅
- 检查点 C（await 之后）：即使错过前两个，也能在恢复后检查 ✅

这是"纵深防御"（Defense in Depth）的例子。
```

### 为什么 finally 块需要考虑引擎切换？

```python
# ❌ 之前的 finally
if app.tts_status == "PLAYING" and _async_tts_stop_requested.is_set():
    app.set_tts_status("STOPPED")

# 问题：
# - 引擎切换时，_async_tts_stop_requested 可能没设置
# - 所以状态不会变成 STOPPED
# - 导致新 Runner 启动时状态混乱

# ✅ 现在的 finally
if (stopped_due_to_engine_switch or _async_tts_stop_requested.is_set()) \
   and app.tts_status == "PLAYING":
    app.set_tts_status("STOPPED")

# 好处：
# - 无论何种停止原因，都会设置正确的状态
# - 状态始终一致
```

---

## 与 Serial Runner 的一致性

### 检查点对应关系

| Serial Runner | Parallel Runner | 目的 |
|---|---|---|
| 主循环开始检查 `_engine_switching` | ✅ 主循环开始检查 `_engine_switching` | 快速检测 |
| Post-Await 检查（3 项） | ✅ Post-Await 检查（3 项） | 防止僵尸任务 |
| finally 管理 `stopped_due_to_engine_switch` | ✅ finally 管理 `stopped_due_to_engine_switch` | 状态一致性 |

**现在两个 Runner 有相同的保护等级**！

---

## 代码位置

### 修改的文件

**文件**: `speakub/tts/ui/runners.py`  
**函数**: `async def tts_runner_parallel_async()`

### 修改清单

1. **行 48-56**: 添加 `stopped_due_to_engine_switch` 标记和初始检查
2. **行 62-69**: 添加模式切换检查
3. **行 79-105**: 添加 post-await 身份验证（3 项检查）
4. **行 527-532**: 更新 finally 块状态管理

---

## 日志示例

### 正常引擎切换（在主循环检测到）

```
[INFO] Async parallel runner: Engine switch detected, stopping runner (STOPPED)
[DEBUG] Async parallel runner: Playlist exhausted during playback wait, stopping playback
```

### 在 await 期间检测到引擎切换

```
[INFO] Async parallel runner: Engine switch detected after chapter load, aborting.
```

### 模式切换（Smooth → Serial）

```
[INFO] Async parallel runner: Mode switched to Serial at main loop, self-terminating.
```

---

## 常见问题 (FAQ)

### Q: 为什么两个 Runner 需要同样的保护？

**A**: 因为它们都可能在以下情况中运行：
- 长时间的 `await` 中（同步等待、网络请求等）
- 用户随时可能切换引擎或模式
- 系统状态可能随时改变

两个 Runner 都需要在任何时刻能够正确响应这些变化。

### Q: 这个修复会影响性能吗？

**A**: 几乎不会。新增的检查都很轻量级：
- `getattr()` 只是读取一个标记
- `is_set()` 检查一个 Event 的布尔值
- 总共耗时 < 1ms

相比 10ms+ 的网络延迟，这是可以忽略不计的。

### Q: 能否在一个地方集中处理所有检查？

**A**: 可以，但不推荐。原因：
- 当前的分散检查提供了"深度防御"
- 一个集中的检查点容易被 `await` 或其他操作绕过
- 多个检查点确保无论在什么阶段都能捕获问题

### Q: 引擎切换期间 Parallel Runner 中还有其他 await 吗？

**A**: 有多个：
- `tts_load_next_chapter_async()`
- `asyncio.wait_for(..., timeout=90.0)` 等待音频
- `get_event_loop().run_in_executor()`（UI 更新）

每个长时间的 `await` 都是引擎切换的窗口，这就是为什么需要多个检查点。

---

## 修复总结

✅ **问题**: Parallel Runner 缺少引擎切换保护，导致竞态条件  
✅ **根因**: 没有检查机制，依赖单一的外部停止信号  
✅ **解决**: 添加三层检查（主循环、post-await、状态管理）  
✅ **效果**: 与 Serial Runner 同级别的可靠性  

**关键思想**：
> 即使没有"警察"盯着你，你也应该在每个关键点自己检查一下是否该停下来。这就是"Post-Await 身份验证"的核心思想。

---

## 相关文件

- 主修复文档：`ENGINE_SWITCH_FIX_MEMO.md`
- 引擎管理：`speakub/tts/engine_manager.py`
- Serial Runner：`speakub/tts/ui/runners.py::tts_runner_serial_async()`
- Parallel Runner：`speakub/tts/ui/runners.py::tts_runner_parallel_async()` ← 本次修复
