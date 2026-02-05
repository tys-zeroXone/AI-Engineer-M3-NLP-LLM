import streamlit as st
from agent_humancapital.orchestration.schemas import SupervisorInput, UserContext
from agent_humancapital.agents.supervisor import supervisor_run
from agent_humancapital.config import SETTINGS

# ----------------------------
# Token counting helper
# ----------------------------
def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    """
    Best effort token counter:
    - Uses tiktoken if installed
    - Falls back to rough approximation if not
    """
    if not text:
        return 0

    try:
        import tiktoken  # pip install tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except Exception:
        # fallback: ~4 chars/token heuristic (rough)
        return max(1, len(text) // 4)

st.set_page_config(page_title="Multi-Agent HR Chatbot", layout="wide")
st.markdown("""
## 🧠 HR Multi-Agent RAG Assistant
*Supervisor-Orchestrated Resume Search, Ranking, Skill Intelligence & Interview Prep*
""")


with st.sidebar:
    st.header("User Context")
    role = st.selectbox("Role", ["guest", "manager", "hr", "recruiter", "admin"], index=0)
    user_id = st.text_input("User ID", value="tyson")
    st.caption("RBAC affects which tools/actions can be used.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Render chat history
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask about candidates, ranking, skills, interview prep, governance…")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # prepare history (string)
    recent = st.session_state.messages[-SETTINGS.MAX_HISTORY_MESSAGES:]
    history_str = "\n".join([f"{x['role']}: {x['content']}" for x in recent])

    # --- Token usage estimation (input) ---
    input_text = f"{history_str}\nuser: {prompt}"
    input_tokens = count_tokens(input_text, model=getattr(SETTINGS, "LLM_MODEL", "gpt-4o-mini"))

    payload = SupervisorInput(
        query=prompt,
        history=history_str,
        user=UserContext(user_id=user_id, role=role),
    )

    with st.chat_message("assistant"):
        result = supervisor_run(payload)
        answer = result["answer"]
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

        # --- Token usage estimation (output) ---
        output_tokens = count_tokens(answer, model=getattr(SETTINGS, "LLM_MODEL", "gpt-4o-mini"))

        with st.expander("Tool Traces"):
            st.json(result.get("tool_traces", []))

        with st.expander("Governance"):
            st.json(result.get("governance", {}))

        # ✅ NEW: Usage details
        with st.expander("Usage Details (Token Estimate)"):
            st.code(
                f"model: {getattr(SETTINGS, 'LLM_MODEL', 'gpt-4o-mini')}\n"
                f"input_tokens:  {input_tokens}\n"
                f"output_tokens: {output_tokens}\n"
                f"total_tokens:  {input_tokens + output_tokens}\n"
            )
