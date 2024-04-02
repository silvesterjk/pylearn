import openai, os
import gradio as gr
from openai import OpenAI
import os
# import azure.cognitiveservices.speech as speechsdk
from langchain import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI

# openai.api_key = os.environ["OPENAI_API_KEY"]
# TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")

# client = OpenAI(
#   api_key=TOGETHER_API_KEY,
#   base_url='https://api.together.xyz/v1',
# )

# chat_completion = client.chat.completions.create(
#   messages=[
#     {
#       "role": "system",
#       "content": "You are an expert travel guide.",
#     },
#     {
#       "role": "user",
#       "content": "Tell me fun things to do in San Francisco.",
#     }
#   ],
#   model="mistralai/Mixtral-8x7B-Instruct-v0.1"
# )

# print(chat_completion.choices[0].message.content)

memory = ConversationSummaryBufferMemory(llm=ChatOpenAI(), max_token_limit=2048)
conversation = ConversationChain(
    llm=OpenAI(max_tokens=2048, temperature=0.5), 
    memory=memory,
)

def predict(input, history=[]):
    history.append(input)
    response = conversation.predict(input=input)
    history.append(response)
    responses = [(u,b) for u,b in zip(history[::2], history[1::2])]
    return responses, history

def transcribe(audio):
    os.rename(audio, audio + '.wav')
    audio_file = open(audio + '.wav', "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']    

def process_audio(audio, history=[]):
    text = transcribe(audio)
    return predict(text, history)

with gr.Blocks(css="#chatbot{height:350px} .overflow-y-auto{height:500px}") as demo:
    chatbot = gr.Chatbot(elem_id="chatbot")
    state = gr.State([])

    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="Enter text and press enter").style(container=False)
        
    with gr.Row():
        audio = gr.Audio(source="microphone", type="filepath")
        
    txt.submit(predict, [txt, state], [chatbot, state])
    audio.change(process_audio, [audio, state], [chatbot, state])

demo.launch()