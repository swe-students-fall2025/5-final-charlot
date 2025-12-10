"""
Chat page - main chat interface

This page handles
- Real-time chat with the AI agent
- Saving messages to database
- Running the LangGraph multi-agent system
"""

import gradio as gr


def create_chat_page():
    """Create the chat interface."""

    def chat_handler(message, history, session_id):
        """
        Process user message and return AI response.
        """
        # Dummy response for now
        return f"You said: {message}"

    with gr.Blocks(title="Chat") as demo:

        # Session ID input
        session_id = gr.Textbox(label="Session ID", value="default_session")

        # Chat interface
        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(label="Your question", placeholder="Type here...")
        submit = gr.Button("Send")

        # Wire up chat
        submit.click(chat_handler, inputs=[msg, chatbot, session_id], outputs=[chatbot])
        msg.submit(chat_handler, inputs=[msg, chatbot, session_id], outputs=[chatbot])

    return demo


if __name__ == "__main__":
    demo = create_chat_page()
    demo.launch()
