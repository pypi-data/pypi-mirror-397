# `_engine_switching` 旗标生命周期详解

**文档目的**: 追踪 `_engine_switching` 旗标的完整生命周期和时序

---

## 1. 旗标的设定与重置时机

### 🟢 **SET（设定）时机**：引擎切换开始

**位置**: `speakub/tts/engine_manager.py::switch_engine()` 开始处

```python
async def switch_engine(
    self, new_engine_name: str, tts_integration=None, old_engine=None
) -> bool:
    """
    Switch to a new TTS engine, handling complete lifecycle cleanup.
    """
    logger.info(f"Switching to TTS engine: {new_engine_name}")

    # [🔥 關鍵修復] 設置引擎切換標記，防止 Serial Runner 在切換期間跳章
    # ⏰ TIME: T0 - 引擎切換開始
    if tts_integration:
        tts_integration._engine_switching = True  # ← 🟢 SET HERE
        logger.info("Engine switching flag SET")

    try:
        # ... 后续处理 ...
```

**时间点**: `T0` - 当 `switch_engine()` 函数被调用时

**作用**: 通知所有 Runner（Serial 和 Parallel）即将进行引擎切换

---

### 🔴 **RESET（重置）时机**：引擎切换完成

**位置**: `speakub/tts/engine_manager.py::switch_engine()` 的 finally 块

```python
        except Exception as e:
            logger.error(f"Failed to switch TTS engine: {e}")
            if app:
                app.notify(f"Failed to switch engine: {e}", severity="error")
            return False

        finally:
            # [🔥 關鍵修復] 只清除引擎切換標記
            # 車子已停下，乘客已下車，新引擎準備好
            # 等待使用者決定要不要繼續播放（按下 PLAY）
            # 不由腳本自動執行，由使用者控制
            
            # ⏰ TIME: T_end - 引擎切換完成或失敗
            if tts_integration:
                tts_integration._engine_switching = False  # ← 🔴 RESET HERE
                logger.info(
                    "Engine switching completed: ready for user to resume playback if desired.")
```

**时间点**: `T_end` - 无论 `switch_engine()` 成功或失败，finally 块都会执行

**保证**: 即使发生异常，旗标也会被重置（finally 的作用）

---

## 2. 完整的时间序列

```
时间轴：
├─ T0: switch_engine() 开始
│  └─ _engine_switching = True       ← 🟢 SET
│
├─ T1-T2: 等待任务清除
│  ├─ Clearing {n} active TTS tasks
│  └─ All active tasks cleared
│
├─ T3: 执行旧引擎清理
│  ├─ _cleanup_engine(old_engine)
│  └─ Performing comprehensive cleanup
│
├─ T4: GTTS 兼容性检查
│  └─ (if new_engine == "gtts") disable smooth mode
│
├─ T5: 新引擎设置
│  ├─ await tts_integration.setup_tts()
│  └─ Using {engine_name}
│
├─ T_end: Finally 块执行
│  └─ _engine_switching = False      ← 🔴 RESET
│
└─ T_end+: 等待用户按 PLAY
   └─ 新 Serial/Parallel Runner 启动
```

---

## 3. Runner 检测流程

### Serial Runner 的检测点

```python
# speakub/tts/ui/runners.py::tts_runner_serial_async()

async def tts_runner_serial_async(tts_integration: "TTSIntegration") -> None:
    """..."""
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # [🔥 關鍵：Main Loop 檢查點]
            # ⏰ 检测时间: T0 之后的每个循环迭代
            if getattr(tts_integration, '_engine_switching', False):
                logger.info(
                    "Async serial runner: Engine switch detected, stopping runner (STOPPED).")
                stopped_due_to_engine_switch = True
                break  # 🛑 立即停止
            
            # ... 其他逻辑 ...
```

**检测时机**: 
- 🟢 在 T0 (SET) 之后的第一个循环迭代
- 🔴 在 T_end (RESET) 之前的任何循环

### Parallel Runner 的检测点

```python
# speakub/tts/ui/runners.py::tts_runner_parallel_async()

async def tts_runner_parallel_async(tts_integration: "TTSIntegration") -> None:
    """..."""
    
    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # [🔥 關鍵：Engine Switch 檢查點]
            # ⏰ 检测时间: T0 之后的每个循环迭代
            if getattr(tts_integration, '_engine_switching', False):
                logger.info(
                    "Async parallel runner: Engine switch detected, stopping runner (STOPPED).")
                stopped_due_to_engine_switch = True
                break  # 🛑 立即停止
            
            # ... 更多逻辑 ...
            
            success = await tts_load_next_chapter_async(playlist_manager)
            
            # [🔥 關鍵修復：Post-Await 身分驗證]
            # ⏰ 检测时间: await 完成后，立即重新检查
            if getattr(tts_integration, '_engine_switching', False):
                logger.info(
                    "Async parallel runner: Engine switch detected after chapter load, aborting.")
                stopped_due_to_engine_switch = True
                break  # 🛑 立即停止
```

**检测时机**:
- 🟢 在 T0 (SET) 之后的每个循环迭代（主循环检查）
- 🟢 在任何 await 后立即重新检查（Post-Await 验证）
- 🔴 在 T_end (RESET) 之前的任何检查点

---

## 4. 状态转换图

```
┌──────────────────────────────────────────────────────────────┐
│                     引擎切换的完整状态转换                       │
└──────────────────────────────────────────────────────────────┘

初始状态：
  _engine_switching = False
  Runner: 正常运行中
  ↓
  用户点击"切换引擎"

[T0] switch_engine() 开始
  ├─ _engine_switching = True  ← SET
  └─ Logger: "Switching to TTS engine: {name}"
      ↓
  Runners 检测到变化
  ├─ Serial Runner: break (STOPPED)
  └─ Parallel Runner: break (STOPPED)
      ↓

[T1-T2] 清除活跃任务
  ├─ Cancel all speak_tasks
  ├─ Clear _tts_active_tasks
  └─ Logger: "All active tasks cleared"
      ↓

[T3] 清理旧引擎
  ├─ Stop monitoring
  ├─ Clear resources
  └─ Logger: "Performing comprehensive cleanup"
      ↓

[T4] 检查 GTTS 兼容性
  └─ (if needed) disable smooth mode
      ↓

[T5] 初始化新引擎
  ├─ await setup_tts()
  └─ Logger: "Using {engine_name}"
      ↓

[T_end] Finally 块
  ├─ _engine_switching = False  ← RESET
  └─ Logger: "Engine switching completed: ready for user to resume playback"
      ↓

最终状态：
  _engine_switching = False
  Runner: 已停止，等待新的 PLAY 信号
  新引擎: 已初始化，准备就绪
  ↓
  用户点击"播放"
  ↓
  新的 Serial/Parallel Runner 启动
```

---

## 5. 详细代码片段

### 完整的 switch_engine 函数（相关部分）

```python
async def switch_engine(
    self, new_engine_name: str, tts_integration=None, old_engine=None
) -> bool:
    """
    Switch to a new TTS engine, handling complete lifecycle cleanup.
    """
    logger.info(f"Switching to TTS engine: {new_engine_name}")

    # ⏰ T0: SET 旗标
    if tts_integration:
        tts_integration._engine_switching = True  # 🟢 SET
        logger.debug("Engine switching flag SET")

    try:
        app = tts_integration.app if tts_integration else None

        # ⏰ T1-T2: 清除任务
        if old_engine and app:
            try:
                logger.info("Engine switching: STOPPED - clearing active tasks immediately")

                if hasattr(tts_integration, '_tts_active_tasks') and tts_integration._tts_active_tasks:
                    pending_tasks = list(tts_integration._tts_active_tasks)
                    if pending_tasks:
                        logger.info(f"Clearing {len(pending_tasks)} active TTS tasks immediately")
                        
                        for task in pending_tasks:
                            if not task.done():
                                task.cancel()
                        
                        tts_integration._tts_active_tasks.clear()
                        logger.info("All active tasks cleared")

                logger.info("Tasks cleared: engine switch can proceed")

            except Exception as e:
                logger.warning(f"Error during task clearing: {e}")

        # ⏰ T3: 清理旧引擎
        await self._cleanup_engine(
            old_engine or self._current_engine, tts_integration
        )

        # ⏰ T4: GTTS 兼容性检查
        if new_engine_name == "gtts":
            if hasattr(app, "tts_smooth_mode") and app.tts_smooth_mode:
                logger.warning("GTTS does not support smooth mode, disabling smooth mode")
                app.tts_smooth_mode = False
                self.config_manager.set_override("tts.smooth_mode", False)
                self.config_manager.save_to_file()
                if app:
                    app.notify(
                        "Smooth mode disabled (not supported by GTTS)",
                        severity="information",
                    )

        # ⏰ T5: 新引擎设置
        if tts_integration:
            await tts_integration.setup_tts()
            logger.info(f"TTS engine setup completed for {new_engine_name}")

        return True

    except Exception as e:
        logger.error(f"Failed to switch TTS engine: {e}")
        if app:
            app.notify(f"Failed to switch engine: {e}", severity="error")
        return False

    finally:
        # ⏰ T_end: RESET 旗标（无论成功或失败）
        if tts_integration:
            tts_integration._engine_switching = False  # 🔴 RESET
            logger.info(
                "Engine switching completed: ready for user to resume playback if desired.")
```

---

## 6. 关键保证

### ✅ 旗标设定保证

```python
if tts_integration:
    tts_integration._engine_switching = True  # 必定在 try 块前执行
```

**保证**: 旗标一定会在 try 块执行前被设定，即使后续有任何异常

### ✅ 旗标重置保证

```python
finally:
    if tts_integration:
        tts_integration._engine_switching = False  # 必定执行
```

**保证**: 无论成功还是失败，旗标一定会被重置
- ✅ 正常完成 → finally 执行 → RESET
- ✅ 异常失败 → except 捕获 → finally 执行 → RESET
- ✅ 中途 return → finally 执行 → RESET

### ✅ 无死锁保证

```
Timeline:
T0: SET _engine_switching = True
    ↓ (无法被 RESET，因为还在 try 块中)
Tn: 最后一行代码
    ↓
T_end: finally 块必定执行 → RESET
```

**无死锁**: finally 块是 Python 的语言级保证，必定执行

---

## 7. 与 finally 块中的 stopped_due_to_engine_switch 的关联

### runners.py 中的使用

```python
# Serial Runner
async def tts_runner_serial_async(tts_integration: "TTSIntegration") -> None:
    stopped_due_to_engine_switch = False  # 本地标记
    
    try:
        while ...:
            if getattr(tts_integration, '_engine_switching', False):  # 检查全局标记
                stopped_due_to_engine_switch = True  # 设置本地标记
                break
    
    finally:
        # 使用本地标记决定状态
        if (
            (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
            and app.tts_status == "PLAYING"
        ):
            app.set_tts_status("STOPPED")  # 设置状态一致
```

### 两个标记的区别

| 标记 | 范围 | 用途 | 生命周期 |
|-----|------|------|---------|
| `_engine_switching` | 全局（`TTSIntegration`） | 通知所有 Runner 引擎在切换 | T0 → T_end |
| `stopped_due_to_engine_switch` | 本地（Runner 内） | 记录本 Runner 停止的原因 | 函数开始 → finally 块 |

### 工作流程

```
[Engine Manager]
  set _engine_switching = True
         ↓
[Serial Runner]
  检测 _engine_switching
  set stopped_due_to_engine_switch = True
  break
         ↓
[Serial Runner finally]
  检查 stopped_due_to_engine_switch
  执行 app.set_tts_status("STOPPED")
         ↓
[Engine Manager finally]
  reset _engine_switching = False
```

---

## 8. 异常处理流程

### 如果清除任务时出异常

```python
try:
    if tts_integration:
        tts_integration._engine_switching = True  # SET ✅
    
    try:
        # 清除任务时出异常
        for task in pending_tasks:
            task.cancel()  # ← 可能抛出异常
    except Exception as e:
        logger.warning(f"Error during task clearing: {e}")  # 捕获并继续
    
    # ... 继续后续处理 ...

except Exception as e:  # 捕获其他异常
    logger.error(f"Failed to switch TTS engine: {e}")
    return False

finally:
    if tts_integration:
        tts_integration._engine_switching = False  # RESET ✅ 无论如何都执行
```

**保证**: 即使任何步骤出异常，旗标仍会被重置

---

## 9. 调试建议

### 检查旗标状态

```python
# 在 Runner 中
if getattr(tts_integration, '_engine_switching', False):
    print(f"DEBUG: _engine_switching is True")
    print(f"DEBUG: Current status: {app.tts_status}")
    print(f"DEBUG: Runner type: {'Serial' if not app.tts_smooth_mode else 'Parallel'}")
```

### 日志追踪

```
查看日志顺序应该是：
1. "Switching to TTS engine: {name}"
2. "Engine switching: STOPPED - clearing active tasks immediately"
3. "Clearing {n} active TTS tasks immediately"
4. "All active tasks cleared"
5. "Async serial runner: Engine switch detected, stopping runner (STOPPED)"
6. "Performing comprehensive cleanup"
7. "Engine switching completed: ready for user to resume playback"

如果顺序不对或缺少步骤，说明有问题。
```

---

## 总结

| 操作 | 时机 | 位置 | 保证 |
|-----|------|------|------|
| **SET** | 函数开始 | try 块前 | ✅ 必定执行 |
| **检测** | 循环迭代或 await 后 | Runner 中 | ✅ 多个检查点 |
| **RESET** | 函数结束 | finally 块 | ✅ 必定执行（即使异常） |

**核心原则**: `_engine_switching` 旗标的生命周期由 try-finally 严格控制，保证了设定和重置的原子性和可靠性。
