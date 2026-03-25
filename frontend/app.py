# frontend/app.py
from nicegui import ui
import requests
import asyncio

API_URL = "http://127.0.0.1:8000"

uploaded_docs = []

# -------------------------------
# Layout: Sidebar + Main Panel
# -------------------------------
with ui.row().style('height: 100vh; width: 100vw; background-color: #f5f6fa;'):

    # -------------------------------
    # Sidebar
    # -------------------------------
    with ui.column().style(
        'width: 300px; padding: 20px; border-right: 1px solid #ddd; '
        'background-color: #fff; gap: 10px; overflow-y: auto;'
    ):

        ui.label("📂 Uploaded Documents").classes("text-lg font-bold")

        ui.label("Upload PDF/Excel files:").classes("text-sm text-gray-600")

        upload_picker = ui.upload(
            on_upload=lambda e: upload_file(e),
            multiple=True,
            auto_upload=True
        ).style('width:100%')

        with ui.row().style("gap:10px;"):

            ui.button(
                "Select All",
                on_click=lambda: [doc["checkbox"].set_value(True) for doc in uploaded_docs]
            ).props("size=small")

            ui.button(
                "Deselect All",
                on_click=lambda: [doc["checkbox"].set_value(False) for doc in uploaded_docs]
            ).props("size=small")

        docs_column = ui.column().style(
            'gap:5px; flex:1; max-height:500px; overflow-y:auto;'
        )

    # -------------------------------
    # Right Panel
    # -------------------------------
    with ui.column().style('flex:1; height:100%; padding: 20px; gap: 10px;'):

        ui.label("📝 Assistant Role / Instructions").classes("text-lg font-bold")

        role_input = ui.textarea(
            placeholder="Define assistant role / rules here...",
            value="You are a helpful financial assistant."
        ).style(
            "width:100%; height:80px; padding:5px; border-radius:5px; border:1px solid #ccc;"
        )

        ui.label("📚 Conversation").classes("text-lg font-bold")

        chat_area = ui.column().style(
            'flex:1; overflow-y:auto; padding:10px; border:1px solid #ddd; '
            'border-radius:5px; background-color:#fff; gap:10px;'
        )

        with ui.column().style("width:100%; gap:5px;"):

            ui.label("💬 Ask a Question").classes("text-lg font-bold")

            with ui.row().style('gap:10px; width:100%;'):

                question_input = ui.input(
                    placeholder="Type your question here..."
                ).style(
                    "flex:1; padding:5px; border-radius:5px; border:1px solid #ccc;"
                )

                ui.button(
                    "Send",
                    on_click=lambda: send_question()
                ).props("color=primary").style("height:35px;")


# -------------------------------
# Upload File
# -------------------------------
async def upload_file(e):

    f = e.file

    try:
        if not f.name.endswith((".pdf", ".xls", ".xlsx")):
            ui.notify("Only PDF/Excel files allowed", type="warning")
            return

        content = await f.read()

        response = await asyncio.to_thread(
            requests.post,
            f"{API_URL}/upload",
            files={"file": (f.name, content)}
        )

        if response.status_code == 200:

            with docs_column:

                with ui.row().classes(
                    "items-center justify-between w-full hover:bg-gray-100 p-2 rounded"
                ):

                    with ui.row().classes("items-center gap-3"):

                        cb = ui.checkbox(value=True)
                        ui.label(f.name).classes("text-sm")

                    ui.button(
                        icon="delete",
                        on_click=lambda name=f.name: delete_document(name)
                    ).props("flat dense color=red")

                ui.separator()

            uploaded_docs.append({
                "name": f.name,
                "checkbox": cb
            })

            ui.notify(f"{f.name} uploaded successfully", type="positive")

        else:
            ui.notify(f"Upload failed for {f.name}", type="negative")

    except Exception as ex:
        print("UPLOAD ERROR:", ex)
        ui.notify(str(ex), type="negative")


# -------------------------------
# Delete Document (UI only)
# -------------------------------
def delete_document(name):

    global uploaded_docs

    uploaded_docs = [doc for doc in uploaded_docs if doc["name"] != name]

    docs_column.clear()

    for doc in uploaded_docs:

        with docs_column:

            with ui.row().classes(
                "items-center justify-between w-full hover:bg-gray-100 p-2 rounded"
            ):

                with ui.row().classes("items-center gap-3"):

                    cb = ui.checkbox(value=doc["checkbox"].value)
                    ui.label(doc["name"]).classes("text-sm")

                ui.button(
                    icon="delete",
                    on_click=lambda name=doc["name"]: delete_document(name)
                ).props("flat dense color=red")

            ui.separator()

        doc["checkbox"] = cb


# -------------------------------
# Ask Question
# -------------------------------
def send_question():

    question = question_input.value.strip()

    if not question:
        ui.notify("Please enter a question", type="warning")
        return

    selected_files = [
        doc["name"] for doc in uploaded_docs if doc["checkbox"].value
    ]

    if not selected_files:
        ui.notify("Please select at least one document", type="warning")
        return

    # User message
    with chat_area:
        ui.label(f"💬 You: {question}") \
            .style("background-color:#e0f7fa; padding:5px; border-radius:5px;")

    question_input.set_value("")

    try:

        response = requests.post(
            f"{API_URL}/ask",
            json={
                "question": question,
                "top_k": 3,
                "documents": selected_files,
                "role": role_input.value
            }
        )

        if response.status_code == 200:

            result = response.json()

            answer_text = result.get("answer", "")
            sources = result.get("sources", [])

            # Assistant response
            with chat_area:
                ui.markdown(f"🤖 Assistant: {answer_text}") \
                    .style("background-color:#fff3e0; padding:5px; border-radius:5px;")

            # Sources
            if sources:

                with chat_area:
                    ui.label("Sources:").classes("text-sm font-semibold")

                for src in sources:

                    snippet = src["text"].replace("\n", " ")

                    if len(snippet) > 150:
                        snippet = snippet[:150] + "..."

                    with chat_area:
                        ui.label(f"- ({src['source']}) {snippet}") \
                            .classes("text-sm text-gray-700")

            chat_area.scroll_to_bottom()

        else:
            ui.notify("Error getting answer", type="negative")

    except Exception as ex:
        print(ex)
        ui.notify("Backend API not running", type="negative")


# -------------------------------
# Run App
# -------------------------------
ui.run()