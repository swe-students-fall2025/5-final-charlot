"""
Dashboard page - shows user's chat sessions
"""

import gradio as gr


def create_dashboard_page():
    """Create the dashboard."""

    def load_sessions(user_id):
        """Load sessions from database."""
        # TODO: Connect to database
        # For now, return dummy data
        return [
            ["Session 1", "2025-12-09"],
            ["Session 2", "2025-12-08"],
        ]

    def create_new_session(user_id):
        """Create new chat session."""
        # TODO: Create session in database
        return "New session created!"

    with gr.Blocks(title="Dashboard") as demo:

        gr.Markdown("# Dashboard")

        # User ID (will come from auth)
        user_id = gr.State(value="default_user")

        # TODO: Add new session button
        new_btn = gr.Button("New Session")
        output = gr.Textbox(label="Status")

        # TODO: Add sessions table
        sessions = gr.Dataframe(headers=["Title", "Date"])

        # Wire up events
        new_btn.click(create_new_session, inputs=[user_id], outputs=[output])
        demo.load(load_sessions, inputs=[user_id], outputs=[sessions])

    return demo


if __name__ == "__main__":
    demo = create_dashboard_page()
    demo.launch()
