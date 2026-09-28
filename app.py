"""
CloudDesk AI Support Engineer — Gradio Web UI
Entry point for local runs and Hugging Face Spaces deployment.
"""

import gradio as gr
import os
from huggingface_hub import InferenceClient
from retrieval_pipeline import load_config, get_vector_store, run_rag_pipeline

cfg = load_config()
vstore = get_vector_store(cfg)
client = InferenceClient(api_key=cfg["hf_token"]) if cfg.get("hf_token") else None


def answer_question(question: str, history):
    result = run_rag_pipeline(cfg, vstore, client, question)

    reply = f"{result['answer']}\n\n**Confidence:** {result['confidence_pct']}"
    if result["requires_escalation"]:
        reply += "\n\n⚠️ **Escalated to Tier-2 Support** (confidence below threshold)."
    if result["citations"]:
        reply += f"\n\n**Sources:**\n{result['citations']}"
    return reply


demo = gr.ChatInterface(
    fn=answer_question,
    title="CloudDesk AI Support Engineer",
    description="Ask a CloudDesk support question and get a grounded, cited answer.",
    examples=[
        "How do I integrate Slack with CloudDesk?",
        "My SAML login stopped working after adding a new domain",
        "Why are webhook deliveries failing?",
    ],
)

if __name__ == "__main__":
    demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))
)
