from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from openai import OpenAI
import os
import json

from http import HTTPStatus
from dotenv import load_dotenv

app = Flask(__name__)
CORS(app)

# Load API Key
load_dotenv()
api_key = os.getenv('DASHSCOPE_API_KEY')
base_url = 'https://dashscope-intl.aliyuncs.com/compatible-mode/v1'

@app.route('/api/chat', methods=['POST'])
def query_endpoint():
    try:
        # Parse JSON payload from the request
        payload = request.get_json()
        messages = payload.get('messages', [])
        temperature = payload.get('temperature', 0.4)
        max_output_tokens = payload.get('max_output_tokens', 1000)

        # Format messages (you can replace this with your actual logic)
        data = format_messages(messages)
        messages = data['messages']

        print("Received messages:", messages)

        # Use a generator to stream responses back to the frontend
        def generate_responses():
            yield from inference_loop(messages)

        # Return a streaming response with the correct content type
        return Response(generate_responses(), content_type='text/event-stream')

    except Exception as e:
        # Handle errors gracefully
        return {"error": str(e)}, 400


def inference_loop(messages):

    think_ctr = 0
    think_limit = 3
    think_prompts = [
        "Let me think about this deeply, and then make a plan to address the question...",
        "[llm_thinking]Wait...[/llm_thinking]",
        "[llm_thinking]Let's see if I missed something...[/llm_thinking]",
    ]

    while True:
        if think_ctr == 0:
            think_content = think_prompts[think_ctr]
            messages.append({"role": "assistant", "content": think_content})
            yield json.dumps({'role': 'assistant', 'content': think_content}) + "\n"
            yield json.dumps({'role': 'assistant', 'content': '', 'type': 'done'}) + "\n"
            think_ctr = think_ctr + 1

        client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        response = client.chat.completions.create(
            model="qwen-max-latest",
            messages=messages,
            stream=True
        )

        assistant_response = ""

        # Iterate through the streaming response
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                # Get the text chunk
                content = chunk.choices[0].delta.content
                
                # Accumulate the full response
                assistant_response += content
                
                # Stream the chunk to the frontend
                yield json.dumps({'role': 'assistant', 'content': content, 'type': 'chunk'}) + "\n"

        # After streaming is complete, add the full response to messages
        messages.append({"role": "assistant", "content": assistant_response})

        # Send a completion signal
        yield json.dumps({'role': 'assistant', 'content': '', 'type': 'done'}) + "\n"


        # If no tool call, terminate the loop, unless think_ctr is not yet at think_limit
        if think_ctr == think_limit:
            break
        else:
            think_content = think_prompts[think_ctr]
            messages.append({"role": "assistant", "content": think_content})
            yield json.dumps({'role': 'assistant', 'content': think_content}) + "\n"
            yield json.dumps({'role': 'assistant', 'content': '', 'type': 'done'}) + "\n"

            think_ctr = think_ctr + 1


def format_messages(messages):
    model = ''
    endpoint = ''

    system_prompt = f"""You are Qwen-Max, an advanced AI model. You will assist the user with tasks, using tools available to you.

You are an advanced AI with reasoning capabilities.

Whenever a message starts with [llm_thinking], that means you are thinking and considering something.
Everything inside of the [llm_thinking] and [/llm_thinking] tags are your own thoughts meant to guide you towards better reasoning and action.

"""
    system_message = {"role": "system", "content": system_prompt}
    messages.insert(0, system_message)

    return {'messages': messages, 'model': model, 'endpoint': endpoint } 


if __name__ == '__main__':
    app.run(debug=True, port="5001")