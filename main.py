import streamlit as st
from streamlit import session_state as ss
from openai import OpenAI
import time

# variables
if 'stream' not in ss:
    ss.stream = None

if "messages" not in ss:
    ss.messages = []

# functions
def data_streamer():
    for response in ss.stream:
        if response.event == 'thread.message.delta':
            value = response.data.delta.content[0].text.value
            yield value
            time.sleep(0.1)

def get_assistant(client):
    assistant_id = st.secrets["ASSISTANT_ID"]
    assistant = client.v2.assistants.retrieve(assistant_id)
    return assistant

def main():
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    assistant = get_assistant(client)

    for message in ss.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        ss.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        msg_history = [{"role": m["role"], "content": m["content"]} for m in ss.messages]

        ss.stream = client.v2.threads.create_and_run(
            assistant_id=assistant.id,        
            thread={"messages": msg_history},
            stream=True
        )
        
        with st.chat_message("assistant"):
            response = st.write_stream(data_streamer)
            ss.messages.append({"role": "assistant", "content": response})

if __name__ == '__main__':
    main()
