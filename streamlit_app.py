import os
import streamlit as st
from huggingface_hub import InferenceClient

from retrieval_pipeline import (
    load_config,
    get_vector_store,
    run_rag_pipeline,
)


st.set_page_config(
    page_title="CloudDesk AI Support Engineer",
    layout="centered",
)


# Load Streamlit Cloud secrets into environment variables

try:
    for key in [
        "HF_TOKEN",
        "HF_MODEL",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME",
    ]:
        if key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass


@st.cache_resource
def initialise_pipeline():
    cfg = load_config()
    vstore = get_vector_store(cfg)

    client = (
        InferenceClient(api_key=cfg["hf_token"])
        if cfg.get("hf_token")
        else None
    )

    return cfg, vstore, client


st.title("CloudDesk AI Support Engineer")

st.write(
    "Ask a CloudDesk support question and receive a grounded "
    "response based on the available support knowledge base."
)

try:
    cfg, vstore, client = initialise_pipeline()

    question = st.chat_input("Ask a CloudDesk support question...")

    if question:
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching CloudDesk knowledge base..."):
                result = run_rag_pipeline(
                    cfg,
                    vstore,
                    client,
                    question,
                )

            st.markdown(result["answer"])

            st.divider()

            st.write(
                f"**Confidence:** {result['confidence_pct']}"
            )

            if result["requires_escalation"]:
                st.warning(
                    "This question has been escalated to Tier-2 Support "
                    "because the retrieval confidence is below the "
                    "60% threshold."
                )

            if result["citations"]:
                st.markdown("**Sources:**")
                st.markdown(result["citations"])

except Exception as e:
    st.error("The CloudDesk support assistant could not be started.")
    st.exception(e)