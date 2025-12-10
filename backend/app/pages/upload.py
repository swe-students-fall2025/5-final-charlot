"""
Upload page - Allow users to upload their documents
"""

import gradio as gr


def create_upload_page():
    """Create the document upload interface."""

    def process_upload(file, session_id, user_id):
        """
        Process uploaded document.

        TODO:
        1. Save file
        2. Process and chunk
        3. Add to vector store
        4. Save to database
        """
        if file is None:
            return "No file selected"

        # Dummy response
        return f"Uploaded: {file.name if hasattr(file, 'name') else 'file'}"

    with gr.Blocks(title="Upload") as demo:

        gr.Markdown("# Upload Documents")

        # User/session info
        user_id = gr.State(value="default_user")
        session_id = gr.Textbox(label="Session ID", value="default_session")

        # File upload
        file_input = gr.File(label="Select file", file_types=[".pdf", ".txt"])
        upload_btn = gr.Button("Upload")
        status = gr.Textbox(label="Status", interactive=False)

        # Wire up upload
        upload_btn.click(
            process_upload,
            inputs=[file_input, session_id, user_id],
            outputs=[status]
        )

    return demo


if __name__ == "__main__":
    demo = create_upload_page()
    demo.launch()
