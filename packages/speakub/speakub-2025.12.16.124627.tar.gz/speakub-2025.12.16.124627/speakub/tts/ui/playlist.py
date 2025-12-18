import asyncio
import logging
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speakub.tts.playlist_manager import PlaylistManager

logger = logging.getLogger(__name__)


def prepare_tts_playlist(
    playlist_manager: "PlaylistManager", from_start: bool = False
) -> None:
    """Prepare TTS playlist from current content."""
    app = playlist_manager.app
    if not app.viewport_content:
        return

    # --- 第一階段：準備數據 (無鎖，耗時) ---
    # 計算 start_idx 和收集 playlist items
    if from_start:
        # Start from the beginning of the chapter
        start_idx = 0
    else:
        cursor_idx = app.viewport_content.get_cursor_global_position()
        para_info = app.viewport_content.line_to_paragraph_map.get(cursor_idx)
        if not para_info:
            for i in range(cursor_idx, len(app.viewport_content.content_lines)):
                if app.viewport_content._is_content_line(
                    app.viewport_content.content_lines[i]
                ):
                    para_info = app.viewport_content.line_to_paragraph_map.get(i)
                    break
            if not para_info:
                # 如果找不到有效的段落，提前返回 (無鎖操作)
                return
        start_idx = para_info["index"]

    # 收集所有有效的文本項 (這是最耗時的部分，無鎖進行)
    new_playlist_items = []
    for p_info in app.viewport_content.paragraphs[start_idx:]:
        text = app.viewport_content.get_paragraph_text(p_info)
        if text.strip():
            new_playlist_items.append((text, p_info["start"]))

    # --- 第二階段：更新狀態 (有鎖，極快) ---
    # 只在這裡獲取引鎖，非常快速的指針交換
    with playlist_manager.tts_integration.tts_lock:
        playlist_manager.reset()
        # 直接附值整個列表，只是一個指針交換，原子性操作
        playlist_manager.playlist = new_playlist_items

    # ✅ v4.0 "Reservoir": Predictive controller will handle initial triggering
    # Removed manual trigger to avoid duplication in smooth mode


def tts_load_next_chapter(playlist_manager: "PlaylistManager") -> bool:
    """Load next chapter for TTS."""
    app = playlist_manager.app
    if not app.epub_manager:
        return False

    # --- 第一階段：準備數據 (無鎖，耗時) ---
    # 檢查下一章節
    try:
        next_chapter = app.epub_manager.get_next_chapter()
        if not next_chapter:
            return False

        logger.debug(f"Loading next chapter: {next_chapter.get('src')}")

        # 非同步載入章節 (這部分不是原子性的，所以無鎖進行)
        app.call_from_thread(
            app.run_worker,
            app.epub_manager.load_chapter(next_chapter, from_start=True),
        )

        # 等待章節載入完成
        chapter_load_start = time.time()
        loaded_chapter_src = None
        while time.time() - chapter_load_start < 10.0:  # Increased timeout
            current_chapter = app.epub_manager.current_chapter
            if current_chapter and current_chapter.get("src") == next_chapter.get(
                "src"
            ):
                loaded_chapter_src = current_chapter.get("src")
                break
            time.sleep(0.1)

        if not loaded_chapter_src:
            logger.error("Chapter loading timeout or failed")
            return False

        logger.debug("Chapter loading completed")

        # 等待 viewport_content 完全更新
        viewport_wait_start = time.time()
        while (
            time.time() - viewport_wait_start < 2.0
        ):  # Wait up to 2 seconds for viewport
            if app.viewport_content and hasattr(app.viewport_content, "paragraphs"):
                break
            time.sleep(0.1)

        # 生成播放列表 (此函數已經優化過，內部只在最後一步鎖定)
        prepare_tts_playlist(playlist_manager, from_start=True)

        # 檢查成功 (透過長度檢查，而非訪問 playlist，因為那可能未同步)
        # 注意：此時 playlist 可能還未完全準備好，所以我們不直接訪問它

    except Exception as e:
        logger.error(f"Error loading next chapter: {e}")
        return False

    # --- 第二階段：最終檢查 (有鎖，極快) ---
    # 只在這裡獲取引鎖來檢查最終狀態
    with playlist_manager.tts_integration.tts_lock:
        success = len(playlist_manager.playlist) > 0

        # 確保 TTS 狀態在平滑模式下的章節轉換期間保持 PLAYING
        if success and app.tts_smooth_mode and app.tts_status == "PLAYING":
            logger.debug(
                "Chapter transition completed, maintaining PLAYING status for smooth mode"
            )
            # Don't change status here - let the runner handle it

        logger.debug(
            f"Next chapter playlist generated: {len(playlist_manager.playlist)} items"
        )
        return success


async def tts_load_next_chapter_async(playlist_manager: "PlaylistManager") -> bool:
    """Load next chapter for TTS (async version for runners)."""
    app = playlist_manager.app
    if not app.epub_manager:
        return False

    try:
        # Check if there's a next chapter
        next_chapter = app.epub_manager.get_next_chapter()
        if next_chapter:
            logger.debug(f"Loading next chapter async: {next_chapter.get('src')}")

            # Load chapter asynchronously (it's already an async method)
            logger.debug("About to call load_chapter async")
            await app.epub_manager.load_chapter(next_chapter, from_start=True)
            logger.debug("load_chapter async call completed")

            # Wait for chapter loading to complete with better verification
            chapter_load_start = time.time()
            loaded_chapter_src = None
            while time.time() - chapter_load_start < 15.0:  # Increased timeout
                current_chapter = app.epub_manager.current_chapter
                logger.debug(
                    f"Checking load status - current_chapter: {current_chapter}"
                )
                if current_chapter and current_chapter.get("src") == next_chapter.get(
                    "src"
                ):
                    loaded_chapter_src = current_chapter.get("src")
                    logger.debug(f"Chapter loaded successfully: {loaded_chapter_src}")
                    break
                await asyncio.sleep(0.1)

            if not loaded_chapter_src:
                logger.error("Chapter loading timeout or failed")
                logger.error(
                    f"Expected chapter: {next_chapter.get('src')}, current: {app.epub_manager.current_chapter}"
                )
                return False

            logger.debug("Chapter loading completed (async)")

            # Additional wait for viewport_content to be fully updated
            viewport_wait_start = time.time()
            while (
                time.time() - viewport_wait_start < 3.0
            ):  # Wait up to 3 seconds for viewport
                if app.viewport_content and hasattr(app.viewport_content, "paragraphs"):
                    break
                await asyncio.sleep(0.1)

            # Generate playlist from the newly loaded chapter
            # prepare_tts_playlist will now automatically decide whether to start preloading based on smooth mode
            await asyncio.get_event_loop().run_in_executor(
                None, prepare_tts_playlist, playlist_manager, True
            )

            success = playlist_manager.has_items()
            logger.debug(
                f"Next chapter playlist generated (async): {playlist_manager.get_playlist_length()} items"
            )

            return success
    except Exception as e:
        logger.error(f"Error loading next chapter (async): {e}")
        return False
