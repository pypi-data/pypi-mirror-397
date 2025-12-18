# Async Loop 死锁快速修复清单

## 问题
Edge-TTS → GTTS 切换后卡住 60 秒

## 根本原因
- 每个引擎有独立 async loop
- 引擎切换时，老 loop 被关闭
- 但线程仍在 `future.result(timeout=60)` 中等待
- Loop 已关闭 → RuntimeError → 线程被卡 60 秒

## 三层修复

### 1️⃣ async_manager.py - 快速中断待处理的 futures
```python
# 在 stop_loop() 中添加同步延迟，让 futures 被中断
time.sleep(0.05)

# 在 run_coroutine_threadsafe() 中检测 loop 是否关闭
if self._event_loop and not self._event_loop.is_running():
    raise RuntimeError("Async event loop is not running")
```

### 2️⃣ edge_tts_provider.py - 捕获 async manager 不可用
```python
except RuntimeError as e:
    # Async loop 在等待期间被关闭
    logger.warning(f"Async manager not available (engine switch?): {e}")
    raise TimeoutError("TTS async manager unavailable") from e
```

### 3️⃣ integration.py - 快速失败（不重试）
```python
except TimeoutError as e:
    if "async manager unavailable" in str(e).lower():
        # 引擎已切换，不应该重试
        logger.warning(f"Engine switched - aborting synthesis")
        raise TTSProviderError(f"Engine unavailable: {e}") from e
    else:
        # 普通超时，可以重试
        if attempt < max_retries:
            time.sleep(retry_delay)
```

## 效果

| 场景 | 旧行为 | 新行为 |
|------|--------|--------|
| 合成中切换引擎 | 卡 60 秒 | 立即返回 (< 100ms) |
| 快速连续切换 | 多个超时叠加 | 快速响应 |
| 应用关闭 | 可能卡住 | 快速清理 |

## 测试步骤

1. 启动应用
2. 开始播放（任意引擎）
3. **中途切换引擎**（应立即切换，不卡）
4. 快速连续切换 3-4 次（应全部迅速响应）
5. 关闭应用（应快速退出，无 hang）

✅ 修复完成！
