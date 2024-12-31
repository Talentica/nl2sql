import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), '.env'))

from agents.nl2sql import get_nl2sql_agent

from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()
FAILURE_MESSAGE = "Sorry, we are not able to serve you right now. Please try again later."

def get_analytics(user_question, request_id):

    response = get_agent_response(user_question, request_id)

    return response

def get_agent_response(agent_input, request_id):
    try:
        chat_executor = get_nl2sql_agent()

        chat_result = chat_executor.invoke({"input": agent_input})
        print(f"chat_result: {chat_result}")
        api_response = {}
        try:
            # api_response = parser.parse(chat_result['output'])
            api_response = {"message": chat_result['output']}
        except Exception as e:
            print(f"error in response parsing | {e}")
            api_response = {
                'message': FAILURE_MESSAGE,
                'status': "FAILURE",
                'error': e
            }
        
        return api_response
    
    except Exception as e:
        print(f"error in chat agent | {e}")
        return {
            'message': FAILURE_MESSAGE,
            'status': "FAILURE",
            'error': str(e)
        }