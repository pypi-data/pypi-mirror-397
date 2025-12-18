# 引擎切换修复 - 快速参考指南

**最后更新**: 2025年12月10日  
**修复版本**: v7  
**涵盖范围**: Serial Runner + Parallel Runner

---

## 🎯 一页纸总结

```
问题：引擎切换导致任务中断、跳章、卡住
根因：缺少引擎切换专用的处理机制
方案：添加 _engine_switching 标记 + 三层检查点
结果：平顺的引擎交接，用户完全控制
```

---

## 📋 核心概念速查

### 三个关键标记

```python
# 1️⃣ 停止信号（用户按停止）
_async_tts_stop_requested: asyncio.Event
  ├─ set by: stop_speaking()
  ├─ checked: while not .is_set()
  └─ result: STOPPED 状态

# 2️⃣ 暂停信号（用户按暂停）
_async_tts_pause_requested: asyncio.Event
  ├─ set by: stop_speaking(is_pause=True)
  ├─ checked: 在 Runner 循环内
  └─ result: PAUSED 状态

# 3️⃣ 引擎切换信号（用户切换引擎）
_engine_switching: bool
  ├─ set by: switch_engine() 开始处
  ├─ checked: 主循环 + post-await
  └─ result: STOPPED 状态，等待新引擎
```

### 三层检查点

```
┌─────────────────────────────────────────────────────┐
│ 第一层：主循环开始检查                                 │
│ if getattr(tts_integration, '_engine_switching', False):
│     break  ← 快速发现大多数情况 ✅                   │
├─────────────────────────────────────────────────────┤
│ 第二层：Post-Await 验证（关键！）                     │
│ success = await tts_load_next_chapter_async()      │
│ if getattr(tts_integration, '_engine_switching', False):
│     break  ← 防止 await 期间的变化 ✅               │
├─────────────────────────────────────────────────────┤
│ 第三层：Finally 块状态管理                            │
│ if (stopped_due_to_engine_switch OR               │
│     _async_tts_stop_requested.is_set()):          │
│     app.set_tts_status("STOPPED")  ← 确保一致 ✅  │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 完整的时间序列

```
时刻    事件                            代码位置
────────────────────────────────────────────────────────
T0      用户点击"切换引擎"
        └─ switch_engine() 开始
           _engine_switching = True      ← SET

T1      Serial Runner 检测
        └─ if getattr(tts_integration, '_engine_switching', False):
           break  ← STOPPED

T2      Parallel Runner 检测
        └─ if getattr(tts_integration, '_engine_switching', False):
           break  ← STOPPED

T3-T4   清除所有活跃任务
        └─ for task in _tts_active_tasks:
              task.cancel()
           _tts_active_tasks.clear()

T5      清理旧引擎
        └─ await _cleanup_engine()

T6      初始化新引擎
        └─ await setup_tts()

T_end   引擎切换完成
        └─ finally:
              _engine_switching = False  ← RESET
              app.notify("Engine switching completed")

T_end+  等待用户
        └─ 用户按 PLAY
           ├─ new Serial/Parallel Runner 启动
           └─ 从停下位置继续播放
```

---

## 💾 代码位置速查

| 功能 | 文件 | 函数 | 行数 |
|-----|------|------|------|
| 引擎切换主逻辑 | `engine_manager.py` | `switch_engine()` | 40-148 |
| SET _engine_switching | `engine_manager.py` | `switch_engine()` | 57 |
| RESET _engine_switching | `engine_manager.py` | `switch_engine()` | 145-149 |
| Serial Runner 检查 | `runners.py` | `tts_runner_serial_async()` | 517-521 |
| Serial Runner post-await | `runners.py` | `tts_runner_serial_async()` | 545-560 |
| Serial Runner finally | `runners.py` | `tts_runner_serial_async()` | 774-780 |
| Parallel Runner 检查 | `runners.py` | `tts_runner_parallel_async()` | 62-69 |
| Parallel Runner post-await | `runners.py` | `tts_runner_parallel_async()` | 87-105 |
| Parallel Runner finally | `runners.py` | `tts_runner_parallel_async()` | 527-532 |

---

## 🚨 问题诊断

### 症状：引擎切换后卡住

**可能原因**：
- [ ] _engine_switching 没有被设置 → 检查 switch_engine() 是否被调用
- [ ] _engine_switching 没有被重置 → 检查 finally 块是否执行
- [ ] Runner 没有检测到标记 → 检查 getattr() 调用
- [ ] await 被中断 → 检查 post-await 是否有异常

**调试步骤**：
```python
# 1. 检查日志中是否有这些信息
"Switching to TTS engine: {name}"
"Engine switch detected, stopping runner (STOPPED)"
"Engine switching completed: ready for user to resume playback"

# 2. 检查状态转换
print(f"Status before switch: {app.tts_status}")  # 应该是 PLAYING
# ... 切换引擎 ...
print(f"Status after switch: {app.tts_status}")   # 应该是 STOPPED

# 3. 检查标记状态
print(f"_engine_switching: {getattr(tts_integration, '_engine_switching', None)}")
# 应该是：开始时 True，完成后 False
```

### 症状：引擎切换后跳章

**可能原因**：
- [ ] Serial Runner 没有 break，使用了 continue → 检查行号 523
- [ ] Parallel Runner 的 post-await 检查缺失 → 检查行号 87-105
- [ ] 新 Runner 启动时状态不对 → 检查 finally 块

**调试步骤**：
```python
# 查看日志顺序
grep "Engine switch" /path/to/log
# 应该看到：
# 1. "Switching to TTS engine"
# 2. "Engine switch detected"
# 3. "Engine switching completed"
# 
# 如果缺少某些，说明检查点没有执行
```

### 症状：引擎切换后双重播放

**可能原因**：
- [ ] Parallel Runner 的 post-await 检查缺失 → 同时启动两个 Runner
- [ ] 旧 Runner 没有真正停止 → 检查 finally 块是否设置 STOPPED

**调试步骤**：
```python
# 检查活跃的 Runner 数量
print(f"Active tasks: {len(tts_integration._tts_active_tasks)}")
# 应该在引擎切换后降到最少

# 检查是否有两个 runner 日志
grep "Async.*runner:" /path/to/log | grep "Engine switch"
# 应该只看到一个，不是两个
```

---

## ✅ 修复检查清单

### Serial Runner (Non-smooth Mode)

- [x] 添加 `stopped_due_to_engine_switch` 标记
- [x] 主循环检查 `_engine_switching`
- [x] Post-Await 验证（3项检查）
- [x] 模式切换检查
- [x] Finally 块状态管理

### Parallel Runner (Smooth Mode)

- [x] 添加 `stopped_due_to_engine_switch` 标记
- [x] 主循环检查 `_engine_switching` 和模式
- [x] Post-Await 验证（3项检查）
- [x] Finally 块状态管理

### Engine Manager

- [x] SET _engine_switching 在开始
- [x] 立即清除任务（不等待）
- [x] RESET _engine_switching 在 finally

---

## 📖 详细文档目录

```
ENGINE_SWITCH_FIX_MEMO.md
├─ 整体修复方案
├─ 车辆交接比喻
├─ 修复前后对比
└─ 设计决策说明

PARALLEL_RUNNER_ENGINE_SWITCH_FIX.md
├─ Parallel Runner 补充修复
├─ Post-Await 身份验证
├─ 与 Serial Runner 的一致性
└─ 测试场景

ENGINE_SWITCHING_FLAG_LIFECYCLE.md
├─ _engine_switching 的完整生命周期
├─ SET 和 RESET 的时机
├─ Runner 的检测流程
├─ 状态转换图
└─ 异常处理流程

DEEP_ANALYSIS_ENGINE_SWITCH.md
├─ stopped_due_to_engine_switch 的作用
├─ Parallel Runner 问题分析
├─ stop_speaking() 的实现
└─ 三个标记的完整对比
```

---

## 🧪 测试用例

### TC-1: 单次引擎切换

```
前置条件：播放中（GTTS）
步骤：
  1. 点击"切换引擎" → Edge-TTS
期望结果：
  ✅ 当前合成停止
  ✅ 状态变为 STOPPED
  ✅ 新引擎初始化
  ✅ 用户按 PLAY 后正常播放
```

### TC-2: 快速连续切换

```
前置条件：播放中
步骤：
  1. 快速点击：GTTS → Edge-TTS → GTTS → Nanmai
期望结果：
  ✅ 每次切换都是干净的
  ✅ 没有卡住或混乱
  ✅ 最后一个引擎启动正常
```

### TC-3: 在合成过程中切换

```
前置条件：播放中，Edge-TTS 正在合成长文本
步骤：
  1. 中途点击"切换引擎" → GTTS
期望结果：
  ✅ 长文本合成被中断
  ✅ 立即切换到 GTTS
  ✅ 不会跳章或重复
```

### TC-4: 在 await 期间切换

```
前置条件：Smooth Mode，正在加载下一章
步骤：
  1. 在 await tts_load_next_chapter_async() 期间点击切换引擎
期望结果：
  ✅ Post-Await 检查检测到切换
  ✅ 立即 break，防止使用失效引擎
  ✅ 系统稳定，无崩溃
```

---

## 🔧 常见操作

### 添加调试日志

```python
# 在 switch_engine() 中
logger.info(f"[DEBUG] _engine_switching before SET: {getattr(tts_integration, '_engine_switching', 'N/A')}")
tts_integration._engine_switching = True
logger.info(f"[DEBUG] _engine_switching after SET: {tts_integration._engine_switching}")

# 在 finally 块中
logger.info(f"[DEBUG] _engine_switching before RESET: {tts_integration._engine_switching}")
tts_integration._engine_switching = False
logger.info(f"[DEBUG] _engine_switching after RESET: {tts_integration._engine_switching}")
```

### 检查状态转换

```python
# 在 Runner finally 块中
logger.info(f"[DEBUG] Runner stopping due to engine_switch={stopped_due_to_engine_switch}")
logger.info(f"[DEBUG] Status before setting: {app.tts_status}")
if (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set()) \
   and app.tts_status == "PLAYING":
    app.set_tts_status("STOPPED")
logger.info(f"[DEBUG] Status after setting: {app.tts_status}")
```

### 验证修复

```bash
# 1. 检查语法
python3 -m py_compile speakub/tts/engine_manager.py speakub/tts/ui/runners.py

# 2. 查看相关日志
grep -i "engine switch" /path/to/log

# 3. 测试引擎切换
# 手动测试切换引擎，观察日志输出
```

---

## 📌 关键代码片段

### Serial Runner 的检查

```python
# 主循环检查
if getattr(tts_integration, '_engine_switching', False):
    logger.info("Engine switch detected, stopping runner (STOPPED)")
    stopped_due_to_engine_switch = True
    break

# Post-Await 检查（示例）
success = await tts_load_next_chapter_async(playlist_manager)

if getattr(tts_integration, '_engine_switching', False):
    logger.info("Engine switch detected after chapter load, aborting")
    stopped_due_to_engine_switch = True
    break
```

### Finally 块的状态管理

```python
finally:
    with tts_integration.tts_lock:
        if (
            (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
            and app.tts_status == "PLAYING"
        ):
            app.set_tts_status("STOPPED")
```

### Engine Manager 的设置

```python
# 开始时
if tts_integration:
    tts_integration._engine_switching = True

# ... 执行切换 ...

# 结束时（finally）
finally:
    if tts_integration:
        tts_integration._engine_switching = False
```

---

## 🎓 学习路径

### 初级（理解基本概念）
1. 阅读本文档的"一页纸总结"和"核心概念"
2. 理解三个关键标记的含义
3. 跟踪一次完整的引擎切换流程

### 中级（理解实现细节）
1. 阅读 `ENGINE_SWITCH_FIX_MEMO.md`
2. 学习"车辆交接"的比喻
3. 理解修复前后的区别

### 高级（深度分析）
1. 阅读 `ENGINE_SWITCHING_FLAG_LIFECYCLE.md`
2. 阅读 `DEEP_ANALYSIS_ENGINE_SWITCH.md`
3. 分析竞态条件和 post-await 验证
4. 理解三层检查点的设计

---

## 📞 问题排查流程

```
问题发生
  ↓
查看日志中是否有"Engine switch"相关信息
  ├─ 没有 → 检查 switch_engine() 是否被调用
  └─ 有 → 继续下一步
  ↓
检查是否有"Engine switch detected"日志
  ├─ 没有 → Runner 没有检测到标记，检查 getattr()
  └─ 有 → 继续下一步
  ↓
检查是否有"Engine switching completed"日志
  ├─ 没有 → Finally 块没有执行，检查异常
  └─ 有 → 继续下一步
  ↓
检查状态是否为 STOPPED
  ├─ 是 → 修复成功，等待用户按 PLAY
  └─ 否 → Finally 块没有设置状态，检查条件
```

---

## 🎯 核心原则

> 引擎切换就像车辆交接。不是"车还在开就踢用户下车"，而是：
> 1. 车缓缓停下（_engine_switching = True）
> 2. 乘客安全下车（Runner break）
> 3. 确认停下（状态设为 STOPPED）
> 4. 更换车辆（引擎切换）
> 5. 上新车（标记清除）
> 6. 乘客决定什么时候开车（等待用户 PLAY）

---

## 版本信息

| 版本 | 日期 | 改动 |
|-----|------|------|
| v6 | 2025-12-09 | Serial Runner 引擎切换修复 |
| v7 | 2025-12-10 | 添加 Parallel Runner 修复 + 详细分析文档 |

---

**最后更新**: 2025年12月10日  
**维护者**: SpeakUB Development Team  
**相关文件**: 参考本文档目录
