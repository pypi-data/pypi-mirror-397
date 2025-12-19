"""Gradio interface for PraisonAI."""

from typing import Optional, List, Tuple
import gradio as gr
from gradio_praisonai.client import PraisonAIClient


def create_chat_interface(
    api_url: str = "http://localhost:8080",
    agent: Optional[str] = None,
    title: str = "🤖 PraisonAI Chat",
    description: str = "Chat with PraisonAI multi-agent framework",
) -> gr.Blocks:
    """Create a Gradio chat interface for PraisonAI.

    Args:
        api_url: PraisonAI API server URL.
        agent: Optional specific agent to use.
        title: Title for the interface.
        description: Description for the interface.

    Returns:
        A Gradio Blocks interface.
    """
    client = PraisonAIClient(api_url=api_url)

    def respond(message: str, history: List[Tuple[str, str]]) -> str:
        """Handle chat messages."""
        try:
            if agent:
                response = client.run_agent(message, agent)
            else:
                response = client.run_workflow(message)
            return response or "No response received."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    with gr.Blocks(title=title) as demo:
        gr.Markdown(f"# {title}")
        gr.Markdown(description)

        chatbot = gr.Chatbot(height=400)
        msg = gr.Textbox(
            placeholder="Ask PraisonAI agents...",
            show_label=False,
            container=False,
        )
        clear = gr.Button("Clear")

        def user_message(user_msg: str, history: List):
            return "", history + [[user_msg, None]]

        def bot_response(history: List):
            user_msg = history[-1][0]
            bot_msg = respond(user_msg, history[:-1])
            history[-1][1] = bot_msg
            return history

        msg.submit(user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
            bot_response, chatbot, chatbot
        )
        clear.click(lambda: None, None, chatbot, queue=False)

    return demo


def launch_chat(
    api_url: str = "http://localhost:8080",
    agent: Optional[str] = None,
    share: bool = False,
    **kwargs,
) -> None:
    """Launch a PraisonAI chat interface.

    Args:
        api_url: PraisonAI API server URL.
        agent: Optional specific agent to use.
        share: Whether to create a public link.
        **kwargs: Additional arguments for gr.Blocks.launch().
    """
    demo = create_chat_interface(api_url=api_url, agent=agent)
    demo.launch(share=share, **kwargs)
