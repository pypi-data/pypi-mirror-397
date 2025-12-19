"""Streamlit components for PraisonAI."""

from typing import Optional
import streamlit as st
from streamlit_praisonai.client import PraisonAIClient


def praisonai_chat(
    api_url: str = "http://localhost:8080",
    agent: Optional[str] = None,
    title: str = "🤖 PraisonAI Chat",
    placeholder: str = "Ask PraisonAI agents...",
    key: str = "praisonai_chat",
) -> None:
    """Render a PraisonAI chat interface in Streamlit.

    Args:
        api_url: PraisonAI API server URL.
        agent: Optional specific agent to use.
        title: Title for the chat interface.
        placeholder: Placeholder text for input.
        key: Unique key for the component.
    """
    st.subheader(title)

    # Initialize session state
    if f"{key}_messages" not in st.session_state:
        st.session_state[f"{key}_messages"] = []

    # Display chat history
    for message in st.session_state[f"{key}_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input(placeholder, key=f"{key}_input"):
        # Add user message
        st.session_state[f"{key}_messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    client = PraisonAIClient(api_url=api_url)
                    if agent:
                        response = client.run_agent(prompt, agent)
                    else:
                        response = client.run_workflow(prompt)
                    st.markdown(response)
                    st.session_state[f"{key}_messages"].append(
                        {"role": "assistant", "content": response}
                    )
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state[f"{key}_messages"].append(
                        {"role": "assistant", "content": error_msg}
                    )


def praisonai_sidebar(
    api_url: str = "http://localhost:8080",
) -> Optional[str]:
    """Render PraisonAI agent selector in sidebar.

    Returns:
        Selected agent name or None for full workflow.
    """
    with st.sidebar:
        st.subheader("🤖 PraisonAI")

        try:
            client = PraisonAIClient(api_url=api_url)
            agents = client.list_agents()
            agent_names = ["Full Workflow"] + [a.get("name", a.get("id")) for a in agents]
            selected = st.selectbox("Select Agent", agent_names)
            if selected == "Full Workflow":
                return None
            # Find agent id
            for a in agents:
                if a.get("name") == selected or a.get("id") == selected:
                    return a.get("id")
            return None
        except Exception:
            st.warning("Could not connect to PraisonAI")
            return None
