#!/usr/bin/env python3
"""
Bookmark listing screen for SpeakUB.
"""

from datetime import datetime
from pathlib import Path

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Static

from speakub.core.bookmarks import Bookmark, bookmark_manager


class BookmarkScreen(ModalScreen[Bookmark]):
    """Modal screen to display and manage bookmarks."""

    CSS = """
    BookmarkScreen {
        align: center middle;
    }

    #bookmark-dialog {
        width: 80%;
        height: 80%;
        border: solid $accent;
        background: $surface;
        layout: vertical;
        overflow: auto;
    }

    #bookmark-title {
        text-align: center;
        background: $primary;
        color: $text;
        padding: 1;
        text-style: bold;
        height: auto;
    }

    DataTable {
        height: 1fr;
        border-top: solid $secondary;
    }

    /* --- Footer button block layout --- */
    #dialog-footer {
        height: 2;
        background: $surface-darken-1;
        border-top: solid $secondary;
        padding: 0 1;
        layout: horizontal;
    }

    /* Left side: occupies 1/3 space, left-aligned */
    .footer-left {
        width: 1fr;
        align: left middle;
    }

    /* Center: occupies 1/3 space, center-aligned */
    .footer-center {
        width: 1fr;
        align: center middle;
    }

    /* Right side: occupies 1/3 space, placeholder for balance */
    .footer-right {
        width: 1fr;
    }

    /* Button style adjustments */
    #dialog-footer Button {
        min-width: 12;
        height: 1;
        border: none;
    }
    """

    # ✅ Key fix: Add priority=True for enter key
    # This forces the Footer to show this binding and prevents DataTable from intercepting key events
    BINDINGS = [
        Binding("escape", "cancel", "Close"),
        Binding("d", "delete_bookmark", "Delete"),
        Binding("enter", "select_bookmark", "Jump", priority=True),
    ]

    def __init__(self, current_epub_path: str):
        super().__init__()
        self.current_epub_path = current_epub_path
        self.bookmarks = []

    def compose(self) -> ComposeResult:
        with Vertical(id="bookmark-dialog"):
            yield Static("Bookmarks", id="bookmark-title")
            yield DataTable(cursor_type="row")

            # Custom footer button area
            with Horizontal(id="dialog-footer"):
                # 1. Left side: Close button
                with Container(classes="footer-left"):
                    yield Button("Esc Close", id="btn_close", variant="default")

                # 2. Center: Jump and Delete buttons
                with Horizontal(classes="footer-center"):
                    # variant="success" is usually green, suitable for primary actions
                    yield Button("Enter Jump", id="btn_jump", variant="success")
                    # variant="error" is usually red, suitable for dangerous actions
                    yield Button("d Delete", id="btn_delete", variant="error")

                # 3. Right side: Blank placeholder (ensures center is absolutely centered)
                with Container(classes="footer-right"):
                    pass

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("File Name", "Chapter", "Position", "Time")
        self._refresh_bookmarks()

    def _refresh_bookmarks(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        # Only show bookmarks for current book
        self.bookmarks = bookmark_manager.get_bookmarks_for_file(self.current_epub_path)

        for idx, bm in enumerate(self.bookmarks):
            # Add file name processing logic
            file_name = self._format_epub_filename(bm.epub_path)

            # Format timestamp nicely
            try:
                dt = datetime.fromisoformat(bm.created_at)
                time_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception as ex:
                self.app.notify(f"Error formatting date: {ex}", severity="warning")
                time_str = bm.created_at

            # Modify add_row call to add file name column
            table.add_row(
                file_name,  # New: File name
                bm.chapter_title,  # Keep: Chapter title
                bm.display_position,  # Keep: Position info
                time_str,  # Keep: Time
                key=str(idx),  # Use index as key to map back to self.bookmarks
            )

        if self.bookmarks:
            table.focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def _get_selected_index(self) -> int:
        table = self.query_one(DataTable)
        try:
            # Handle case where no row is selected or table is empty
            if not table.row_count:
                return -1

            # Get row ID where DataTable cursor is located
            # Note: In new version of Textual, this is usually coordinate_to_cell_key
            row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key

            if row_key:
                return int(row_key.value)
        except Exception:
            pass
        return -1

    def action_select_bookmark(self) -> None:
        """Handle manual Enter key press (binding)."""
        index = self._get_selected_index()
        if 0 <= index < len(self.bookmarks):
            self.dismiss(self.bookmarks[index])

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Handle row selection from DataTable (e.g. mouse click or internal Enter).
        This ensures 'Jump' works even if DataTable consumes the Enter key event.
        """
        try:
            if event.row_key:
                index = int(event.row_key.value)
                if 0 <= index < len(self.bookmarks):
                    self.dismiss(self.bookmarks[index])
        except Exception:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle footer button click events"""
        button_id = event.button.id

        if button_id == "btn_close":
            self.action_cancel()
        elif button_id == "btn_jump":
            self.action_select_bookmark()
        elif button_id == "btn_delete":
            self._handle_delete_request()

    def action_delete_bookmark(self) -> None:
        index = self._get_selected_index()
        if 0 <= index < len(self.bookmarks):
            bookmark = self.bookmarks[index]
            bookmark_manager.delete_bookmark(bookmark.id)
            self.app.notify("Bookmark deleted", severity="information")
            self._refresh_bookmarks()

            # After refresh, try to keep focus on table and adjust cursor
            table = self.query_one(DataTable)
            if table.row_count > 0:
                new_cursor = min(index, table.row_count - 1)
                table.move_cursor(row=new_cursor)

    def _handle_delete_request(self) -> None:
        """Handle delete request, check if item is selected"""
        if not self.bookmarks:
            # If no bookmarks, show warning message
            self.app.notify("No bookmarks to delete", severity="warning")
            return

        # Check if item is selected
        selected_index = self._get_selected_index()
        if selected_index == -1 or selected_index >= len(self.bookmarks):
            # If no item selected, show warning message
            self.app.notify("Please select a bookmark to delete", severity="warning")
            return

        # If item is selected, show confirmation dialog
        self._show_delete_confirmation()

    def _show_delete_confirmation(self) -> None:
        """Show delete confirmation dialog"""
        confirm_modal = DeleteConfirmationModal()
        self.app.push_screen(confirm_modal, self._on_delete_confirmed)

    def _on_delete_confirmed(self, result: bool | None) -> None:
        """Handle delete confirmation result callback"""
        if result:  # User confirmed deletion
            self._execute_delete()
        # If result is False or None, user cancelled, do nothing

    def _execute_delete(self) -> None:
        """Execute actual deletion operation"""
        index = self._get_selected_index()
        if 0 <= index < len(self.bookmarks):
            bookmark = self.bookmarks[index]
            bookmark_manager.delete_bookmark(bookmark.id)
            self.app.notify("Bookmark deleted", severity="information")
            self._refresh_bookmarks()

            # After refresh, try to keep focus on table and adjust cursor
            table = self.query_one(DataTable)
            if table.row_count > 0:
                new_cursor = min(index, table.row_count - 1)
                table.move_cursor(row=new_cursor)

    def _format_epub_filename(self, epub_path: str) -> str:
        """Format EPUB file path to display name."""
        try:
            path = Path(epub_path)
            # Get filename (without extension)
            file_stem = path.stem

            # Truncate if too long
            if len(file_stem) > 30:
                return file_stem[:27] + "..."

            return file_stem
        except Exception:
            # Fallback: try to extract from full path
            try:
                file_name = Path(epub_path).name
                return file_name[:30] + ("..." if len(file_name) > 30 else "")
            except Exception:
                return "Unknown File"


class DeleteConfirmationModal(ModalScreen[bool]):
    """Delete bookmark confirmation dialog"""

    CSS = """
    DeleteConfirmationModal {
        align: center middle;
    }

    #confirm-dialog {
        width: 46;
        height: auto;
        border: double $error;
        background: $surface;
        layout: vertical;
        padding: 1 2;
    }

    #confirm-title {
        text-align: center;
        color: $error;
        text-style: bold;
        height: 1;
        margin-bottom: 1;
    }

    #confirm-message {
        text-align: center;
        height: auto;
        margin-bottom: 1;
    }

    .button-row {
        layout: horizontal;
        align: center middle;
        height: 1;
        width: 100%;
    }

    /* --- Button style fixes --- */
    .button-row Button {
        height: 1;           /* Force single line height */
        min-height: 1;       /* Override default minimum height */
        border: none;        /* Key: remove border to prevent text clipping */
        padding: 0 2;        /* Top/bottom padding must be 0, left/right can have spacing */
        width: auto;
        min-width: 14;
        content-align: center middle;
    }

    /* Style when mouse hover or keyboard focus */
    .button-row Button:focus, .button-row Button:hover {
        text-style: bold reverse; /* Reverse display to replace border function */
    }
    """

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Static("⚠️  刪除確認", id="confirm-title")
            yield Static("確定要刪除此書籤嗎？\n這個動作無法撤銷。", id="confirm-message")

            with Container(classes="button-row"):
                yield Button("Yes (Y)", id="btn_yes", variant="error")
                yield Button("No (N)", id="btn_no", variant="default")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_yes":
            self.action_confirm()
        elif event.button.id == "btn_no":
            self.action_cancel()

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)
