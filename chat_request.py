import openai
import requests
from logging_config import logger
from tools import tools
def chatRequest(model_name, client, messages):
    
   try:
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    result= response.choices[0].message
    logger.debug("Model response:", result)
    return result
   except openai.OpenAIError as e:
    logger.error(f"Error while making chat request: {e.message}")
    raise ValueError(f"Error while making chat request: {e.message}")