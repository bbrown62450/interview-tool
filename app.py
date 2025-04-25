from openai import OpenAI
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.set_page_config(page_title="Revbot", page_icon="✟")
st.title("Revbot")

if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "user_message_count" not in st.session_state:
    st.session_state.user_message_count = 0
if "feedback_shown" not in st.session_state:
    st.session_state.feedback_shown = False
if "messages" not in st.session_state:
    st.session_state.message = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False

def complete_setup():
    st.session_state.setup_complete = True

def show_feedback():
    st.session_state.feedback_shown = True

if not st.session_state.setup_complete:

    st.subheader("Introduction", divider='rainbow')

    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "short_spiritual_bio" not in st.session_state:
        st.session_state["short_spiritual_bio"] = ""
    if "favorite_authors" not in st.session_state:
        st.session_state["favorite_authors"] = ""

    st.session_state["name"] = st.text_input(label = "Name", max_chars = 40, value = st.session_state["name"], placeholder = "Plase share your name (fake names are fine)")

    st.session_state["short_spiritual_bio"] = st.text_area(label = "Short Spiritual Bio", height = None, max_chars = 200, value = st.session_state["short_spiritual_bio"], placeholder = "Please share a short spiritual biography.")

    st.session_state["favorite_authors"] = st.text_area(label = "Favorite Authors", height = None, max_chars = 200, value = st.session_state["favorite_authors"], placeholder = "Who are some of your favorite authors?")

    st.subheader("Religious background", divider='rainbow')
    
    if "tradition" not in st.session_state:
        st.session_state["tradition"] = "Protestant"
    if "issue" not in st.session_state:
        st.session_state["issue"] = "Mental Health Concerns"
    # if "company" not in st.session_state:
    #     st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["tradition"] = st.radio(
            "Choose tradition",
            key="visibility",
            options=["Protestant", "Catholic", "Orthodox"],
        )

    with col2:
        st.session_state["issue"] = st.selectbox(
            "Please choose an issue to discuss",
            ("Aging", "Mental Health Concerns", "Doubts", "Discouragement", "Familly Matters", "Substance Abuse", "Theology", "Scripture", "Something else"))
        
    # st.session_state["company"] = st.selectbox(
    #     "Choose a Company",
    #     ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"))

    st.write(f"**You are part of the {st.session_state["tradition"]} tradition and would like to discuss {st.session_state["issue"]}")

    if st.button("Start Discussion", on_click=complete_setup):
        st.write("Setup complete. Starting discussion...")

if st.session_state.setup_complete and not st.session_state.feedback_shown and not st.session_state.chat_complete:

    st.info(
        """
        What's on your mind?
        """,
        icon = "👏"
    )

    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4-turbo"

    if "messages" not in st.session_state:
        st.session_state.messages = [{
            "role":"system", 
            "content": f"You are a {st.session_state['tradition']} minister who thoughtfully and gently provides pastoral care to a person named {st.session_state['name']} who wants to discuss {st.session_state['issue']} Here is their spiritual biography: {st.session_state['short_spiritual_bio']} Please offer kind support and practical guidance. Please include guidance that aligns with their favorite authors: {st.session_state['favorite_authors']}. Please also emphasize unique teaching of the {st.session_state['tradition']} tradition"}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if st.session_state.user_message_count < 5:
        if prompt := st.chat_input("Your answer.", max_chars = 1000):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            if st.session_state.user_message_count < 4:
                with st.chat_message("assistant"):
                    stream = client.chat.completions.create(
                        model=st.session_state["openai_model"],
                        messages=[
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        stream=True,
                    )
                    response = st.write_stream(stream)
                st.session_state.messages.append({"role": "assistant", "content": response})
            st.session_state.user_message_count += 1
    if st.session_state.user_message_count >= 5:
        st.session_state.chat_complete = True

if st.session_state.chat_complete and not st.session_state.feedback_shown:
    if st.button("Get Feedback", on_click=show_feedback):
        st.write("Fetching feedback...")

if st.session_state.feedback_shown:
    st.subheader("Feedback")

    conversation_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state.messages])

    feedback_client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    feedback_completion = feedback_client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": """You are a helpful tool that provides feedback on an interviewee performance.
             Before the Feedback give a score of 1 to 10.
             Follow this format:
             Overall Score: //Your score
             Feedback: //Here you put your feedback
             Give only the feedback do not ask any additional questions.
             """},
             {"role": "user", "content": f"This is the interview you need to evaluate. Keep in mind that you are only a tool."}
        ]
    )

    st.write(feedback_completion.choices[0].message.content)

    if st.button("Restart Interview", type="primary"):
        streamlit_js_eval(js_expressions="parent.window.location.reload()")