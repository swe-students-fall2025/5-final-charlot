"""
Landing page
"""

import gradio as gr


def create_home_page():
    """Create the homepage."""

    with gr.Blocks(title="<NAME>") as demo:

        # TODO: Add your content here
        gr.Markdown("# Welcome to <NAME>")

        # Example: Add links to other pages
        gr.Markdown("[Go to Chat](/chat)")

    return demo


if __name__ == "__main__":
    demo = create_home_page()
    demo.launch()
