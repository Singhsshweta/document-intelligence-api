from nicegui import ui
import requests
import asyncio

API_URL = "http://127.0.0.1:8000"

# Plain dict: { filename: is_selected (bool) }
# No widget references stored here — source of truth is Python only.
doc_selection: dict[str, bool] = {}

# -------------------------------
# Global styles
# -------------------------------
ui.add_head_html("""
<style>
  body { background: #f4f4f2 !important; }

  .sidebar {
    width: 260px;
    min-width: 260px;
    height: 100vh;
    background: #ffffff;
    border-right: 1px solid #e8e8e5;
    display: flex;
    flex-direction: column;
  }

  .main-panel {
    flex: 1;
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }

  .chat-scroll {
    flex: 1;
    overflow-y: auto;
    padding: 16px 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .msg-user {
    align-self: flex-end;
    max-width: 68%;
    background: #e8f0fe;
    border-radius: 12px 12px 3px 12px;
    padding: 10px 14px;
    font-size: 13px;
    color: #1a1a18;
    line-height: 1.5;
    word-wrap: break-word;
  }

  .msg-bot { align-self: flex-start; max-width: 78%; }

  .msg-bot-inner {
    background: #ffffff;
    border: 0.5px solid #e2e2de;
    border-radius: 3px 12px 12px 12px;
    padding: 10px 14px;
    font-size: 13px;
    color: #1a1a18;
    line-height: 1.6;
    word-wrap: break-word;
  }

  .msg-error-inner {
    background: #fff5f5;
    border: 0.5px solid #f7c1c1;
    border-radius: 3px 12px 12px 12px;
    padding: 10px 14px;
    font-size: 13px;
    color: #a32d2d;
    line-height: 1.6;
  }

  .source-pills { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 4px; }

  .source-pill {
    font-size: 11px;
    padding: 2px 8px;
    background: #f4f4f2;
    border: 0.5px solid #e2e2de;
    border-radius: 99px;
    color: #888780;
  }

  .doc-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 10px;
    border-radius: 6px;
    transition: background 0.15s;
  }
  .doc-row:hover { background: #f7f7f5; }

  .doc-label {
    flex: 1;
    font-size: 13px;
    color: #2c2c2a;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .nicegui-upload { width: 100% !important; }

  .role-bar {
    background: #f7f7f5;
    border-bottom: 1px solid #e8e8e5;
    padding: 8px 24px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .input-bar {
    background: #ffffff;
    border-top: 1px solid #e8e8e5;
    padding: 12px 24px;
    display: flex;
    gap: 8px;
    align-items: center;
  }
</style>
""")

# -------------------------------
# Layout
# -------------------------------
with ui.row().style("width: 100vw; height: 100vh; overflow: hidden; gap: 0;"):

    # ===========================
    # SIDEBAR
    # ===========================
    with ui.column().classes("sidebar").style("gap: 0;"):

        with ui.row().style(
            "padding: 16px 16px 12px; border-bottom: 1px solid #e8e8e5; "
            "align-items: center; gap: 8px;"
        ):
            ui.label("📂").style("font-size: 16px;")
            ui.label("Documents").style(
                "font-size: 13px; font-weight: 500; color: #5f5e5a; "
                "letter-spacing: 0.05em; text-transform: uppercase;"
            )

        with ui.element("div").style("padding: 10px 12px;"):
            ui.upload(
                on_upload=lambda e: upload_file(e),
                multiple=True,
                auto_upload=True,
                label="Upload PDF or Excel"
            ).classes("nicegui-upload").props(
                "flat accept='.pdf,.xls,.xlsx' color=grey-7"
            ).style(
                "border: 1px dashed #d3d1c7; border-radius: 8px; "
                "width: 100%; font-size: 12px; color: #888780;"
            )

        docs_column = ui.column().style(
            "flex: 1; overflow-y: auto; padding: 6px; gap: 2px;"
        )

        with ui.row().style("padding: 10px 12px; border-top: 1px solid #e8e8e5;"):
            ui.button(
                "Clear all documents",
                on_click=lambda: clear_all_docs()
            ).props("flat size=sm color=negative").style("width: 100%; font-size: 12px;")

    # ===========================
    # MAIN PANEL
    # ===========================
    with ui.column().classes("main-panel").style("gap: 0;"):

        with ui.row().style(
            "background: #ffffff; border-bottom: 1px solid #e8e8e5; "
            "padding: 14px 24px; align-items: center; gap: 12px;"
        ):
            with ui.element("div").style(
                "width: 34px; height: 34px; border-radius: 8px; "
                "background: #e8f0fe; display: flex; align-items: center; "
                "justify-content: center; font-size: 17px;"
            ):
                ui.label("🧠")
            with ui.column().style("gap: 1px;"):
                ui.label("AI Financial Analyst").style(
                    "font-size: 15px; font-weight: 500; color: #1a1a18;"
                )
                ui.label("Ask questions across your uploaded documents").style(
                    "font-size: 12px; color: #888780;"
                )

        with ui.row().classes("role-bar"):
            ui.label("Role").style(
                "font-size: 11px; font-weight: 500; color: #888780; white-space: nowrap;"
            )
            role_input = ui.input(
                value="You are a financial analyst providing concise, data-backed insights."
            ).props("dense outlined").style("flex: 1; font-size: 12px;")

        chat_area = ui.column().classes("chat-scroll")

        with ui.row().classes("input-bar"):
            question_input = ui.input(
                placeholder="Ask about your documents…"
            ).props("outlined dense").style("flex: 1;")
            ui.button("Send", on_click=lambda: send_question()) \
                .props("color=dark unelevated") \
                .style("min-width: 72px; height: 36px; font-size: 13px;")


# -------------------------------
# Sidebar rebuild
# -------------------------------
def _rebuild_sidebar():
    """Redraw the doc list from doc_selection (the single source of truth)."""
    docs_column.clear()
    for name, selected in doc_selection.items():
        with docs_column:
            with ui.element("div").classes("doc-row"):
                icon = "📊" if name.lower().endswith((".xls", ".xlsx")) else "📄"
                # Capture name in closure correctly
                cb = ui.checkbox(value=selected).props("dense color=primary")
                cb.on("update:model-value", lambda val, n=name: _on_toggle(n, val))
                ui.label(icon).style("font-size: 14px; flex-shrink: 0;")
                ui.label(name).classes("doc-label")
                ui.button(
                    icon="close",
                    on_click=lambda n=name: delete_doc(n)
                ).props("flat round dense size=xs color=negative")


def _on_toggle(name: str, value):
    """Update selection state when a checkbox is toggled."""
    # value arrives as a dict {"args": bool} or directly as bool depending on NiceGUI version
    if isinstance(value, dict):
        value = value.get("args", [True])[0] if isinstance(value.get("args"), list) else value.get("args", True)
    doc_selection[name] = bool(value)


# -------------------------------
# Chat helpers
# -------------------------------
def _add_msg_bot(answer: str, sources: list):
    with chat_area:
        with ui.element("div").classes("msg-bot"):
            with ui.element("div").classes("msg-bot-inner"):
                ui.markdown(answer)
            if sources:
                with ui.element("div").classes("source-pills"):
                    seen = set()
                    for s in sources:
                        src = s.get("source") or "unknown"
                        if src not in seen:
                            seen.add(src)
                            with ui.element("span").classes("source-pill"):
                                ui.label(src)


def _add_msg_error(text: str):
    with chat_area:
        with ui.element("div").classes("msg-bot"):
            with ui.element("div").classes("msg-error-inner"):
                ui.label(text)


# -------------------------------
# Upload
# -------------------------------
async def upload_file(e):
    f = e.file

    if not f.name.lower().endswith((".pdf", ".xls", ".xlsx")):
        ui.notify("Only PDF or Excel files are supported", type="warning")
        return

    content = await f.read()

    try:
        response = await asyncio.to_thread(
            requests.post,
            f"{API_URL}/upload",
            files={"file": (f.name, content)},
            timeout=30
        )

        data = response.json()
        if response.status_code == 200 and data.get("status") == "success":
            doc_selection[f.name] = True   # selected by default
            _rebuild_sidebar()
            ui.notify(f"'{f.name}' indexed", type="positive")
        else:
            ui.notify(f"Upload failed: {data.get('message', 'Unknown error')}", type="negative")

    except Exception as ex:
        ui.notify(f"Upload error: {ex}", type="negative")


# -------------------------------
# Delete
# -------------------------------
def delete_doc(name: str):
    try:
        r = requests.delete(f"{API_URL}/document/{name}", timeout=10)
        if r.status_code != 200:
            ui.notify(f"Backend error deleting '{name}'", type="negative")
            return
    except Exception:
        ui.notify("Backend not reachable", type="negative")
        return

    doc_selection.pop(name, None)
    _rebuild_sidebar()
    ui.notify(f"'{name}' removed", type="info")


# -------------------------------
# Clear all
# -------------------------------
def clear_all_docs():
    try:
        requests.delete(f"{API_URL}/clear", timeout=10)
        doc_selection.clear()
        docs_column.clear()
        ui.notify("All documents cleared", type="positive")
    except Exception:
        ui.notify("Error reaching backend", type="negative")


# -------------------------------
# Send question
# -------------------------------
def send_question():
    question = question_input.value.strip()

    if not question:
        ui.notify("Please enter a question", type="warning")
        return

    if not doc_selection:
        ui.notify("Upload at least one document first", type="warning")
        return

    # Read selection directly from the plain dict — no widget refs needed
    selected = [name for name, is_sel in doc_selection.items() if is_sel]

    if not selected:
        ui.notify("Check at least one document in the sidebar", type="warning")
        return

    with chat_area:
        with ui.element("div").classes("msg-user"):
            ui.label(question)

    question_input.set_value("")

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={
                "question": question,
                "documents": selected,
                "role": role_input.value.strip() or None,
            },
            timeout=60,
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("status") == "error":
                _add_msg_error(result.get("answer", "An error occurred."))
            else:
                _add_msg_bot(
                    result.get("answer", "No answer returned."),
                    result.get("sources", [])
                )
        else:
            _add_msg_error(f"Server error: HTTP {response.status_code}")

    except requests.exceptions.Timeout:
        _add_msg_error("Request timed out — the model may be busy. Try again.")
    except Exception as ex:
        _add_msg_error(f"Could not reach the backend: {ex}")

    chat_area.scroll_to_bottom()


# -------------------------------
# Run
# -------------------------------
ui.run(title="AI Financial Analyst", favicon="🧠")