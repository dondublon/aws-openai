import openai
from logging_config import logger
def chatRequestRag(model_name, client, question, retrieved_doc):
    
   try:
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You answer question only based on provided context\
                If context is empty, say 'I don't know'"},
            {"role": "user", "content": f'''
             Context: {retrieved_doc}
             Question: {question}
             '''}],
        
    )
    result= response.choices[0].message.content
    logger.debug("Model response:", result)
    return result
   except openai.OpenAIError as e:
    logger.error(f"Error while making chat request: {e.message}")
    raise ValueError(f"Error while making chat request: {e.message}")