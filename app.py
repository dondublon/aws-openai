import json

from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import openai

from logging_config import logger 
from chat_request import chatRequest 
from config import MODEL_NAME, DOCUMENTS_PATH, SIMILARITY_THRESHOLD
from text_processor_impl import textProcessor
from chat_request_RAG import chatRequestRag
from system_prompt import SYSTEM_PROMPT
from tools import TOOL_FUNCTIONS
from fastapi import FastAPI
from pydantic import BaseModel, Field

class ChatRequestDTO(BaseModel):
    query: str = Field(..., min_length=10)

def _bootstrap():
    docs: list[str] = DOCUMENTS_PATH.read_text(encoding="utf8").splitlines()
    logger.debug(f"read {len(docs)} documents")
    textProcessor.setDocuments(docs)  
def _get_response_from_rag(query_text, client) :
    logger.debug(f"query text is {query_text}")
    retrieved_doc =  textProcessor.process(query_text, threshold=SIMILARITY_THRESHOLD)  
    logger.debug(f"response from RAG is {retrieved_doc}")
    response = chatRequestRag(MODEL_NAME,client,query_text, retrieved_doc) if retrieved_doc else None
    return response

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
    responseFromRag = _get_response_from_rag(messages[-1]["content"], client)
    role = "assistant"
    if not responseFromRag:
        '''
        fallback to LLM model
        '''
        
        responseFromLLM = chatRequest(MODEL_NAME, client, messages)
        responseFromTool = _get_response_from_tool(responseFromLLM, messages)
        if  responseFromTool:
            response = responseFromTool
            role = "tool"
        else:
            messages.append({"role": "assistant", "content": responseFromLLM.content})
            response = responseFromLLM.content
    else:
        response = responseFromRag
        messages.append({"role": "assistant", "content": responseFromRag})        
    return response, role

app = FastAPI()
@app.on_event("startup")
def on_start_up()->None:
    app.state.client = openai.OpenAI()
    _bootstrap()
    app.state.messages = [
        {"role": "system", 
            "content": SYSTEM_PROMPT
            }
    ]
@app.exception_handler(RequestValidationError)
def exception_handler(_, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request", "details": exc.errors()}
    )
@app.post("/chat")
def chat_endpoint(body: ChatRequestDTO):
    try:
        user_input = body.query
        app.state.messages.append({"role": "user", "content": user_input})
        result = None
    
        response, role = _get_response(app.state.messages, app.state.client)
        result = {"response": response, "role": role}  
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        result =  JSONResponse(
            status_code=500,
            content={"error": "An error occurred while processing the request."}
        )
    return result
@app.get("/health")
def health_check():
    return {"status": "healthy"}
