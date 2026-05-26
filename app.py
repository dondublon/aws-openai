import json

import openai

from logging_config import logger 
from chat_request import chatRequest 
from config import MODEL_NAME

from system_prompt import SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS

def _finishProcess():
   print("Chat console exited. Thanks & bye")
def _get_response_from_tool(response, messages):
    responseFromTool = None 
    if response.tool_calls:
        messages.append(response)
        try:
            tool_call = response.tool_calls[0]
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            logger.debug("Tool requested:", function_name)
            logger.debug("Arguments:", arguments)
            responseFromTool = TOOL_FUNCTIONS[function_name](**arguments)
           
        except Exception as e:
            logger.error("Error while executing tool function:", e)
            responseFromTool = f"Error while executing tool function: {e}, please repeat your request with correct some rewording."
        messages.append({"role": "tool", "content": responseFromTool, "tool_call_id": tool_call.id})   
    return responseFromTool
def _get_response(messages, client):
    
    response = chatRequest(MODEL_NAME, client, messages)
    responseFromTool = _get_response_from_tool(response, messages)
    role = "assistant"
    if  responseFromTool:
        response = responseFromTool
        role = "tool"
    else:
       messages.append({"role": "assistant", "content": response.content})
       response = response.content
    return response, role
def main():
    client = openai.OpenAI()
    print(f"{MODEL_NAME} chat console started. Type 'exit' to quit.")
    messages = [
        {"role": "system", 
         "content": SYSTEM_PROMPT
         }
    ]
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == "exit":
                _finishProcess()
                break
            messages.append({"role": "user", "content": user_input})
            response, role = _get_response(messages, client)
            print(f"{role.capitalize()}: {response}")
        except KeyboardInterrupt:
            _finishProcess()
            break   
if __name__ == "__main__":
    main()