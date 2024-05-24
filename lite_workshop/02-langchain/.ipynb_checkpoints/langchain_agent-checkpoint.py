import os
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError

import requests


from langchain.agents import AgentType, initialize_agent
from langchain.embeddings import BedrockEmbeddings
from langchain.llms import Bedrock
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import AIMessage, HumanMessage
from langchain.tools import StructuredTool


# Define the Chrome user agent string
chrome_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
# Set the headers with the Chrome user agent
headers = {"User-Agent": chrome_user_agent}


# Initialize AWS clients

def setup_bedrock():
    """Initialize the Bedrock runtime."""
    return boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
    )


def initialize_llm(client):
    """Initialize the language model."""
    llm = Bedrock(client=client, model_id="anthropic.claude-v2")
    llm.model_kwargs = {"temperature": 0.0, "max_tokens_to_sample": 4096}
    return llm


# Setup bedrock
bedrock_runtime = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1",
)


#Tools define
def get_lat_long(place:str):
        """Returns the latitude and longitude for a given place name."""
        url = "https://nominatim.openstreetmap.org/search"
        params = {'q': place, 'format': 'json', 'limit': 1}
        response = requests.get(url, headers=headers,params=params).json()
        if response:
            lat = response[0]["lat"]
            lon = response[0]["lon"]
            return {"latitude": lat, "longitude": lon}
        else:
            return None

#Tools define
def get_weather(latitude: str, longitude: str):
  """Returns weather data for a given latitude and longitude."""
  url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
  response = requests.get(url,headers=headers)
  return response.json()




def interact_with_agent(agent_executor, input_query, chat_history):
    """Interact with the agent and store chat history. Return the response."""
    result = agent_executor.invoke(
        {
            "input": input_query,
            "chat_history": chat_history,
        }
    )
    chat_history.append(HumanMessage(content=input_query))
    chat_history.append(AIMessage(content="Assistant: " + result["output"]))
    return result


def setup_full_agent():
    # Initialize bedrock and llm
    bedrock_runtime = setup_bedrock()
    llm = initialize_llm(bedrock_runtime)

    # Initialize LangChain tools
    aws_get_lat_long = StructuredTool.from_function(get_lat_long)
    aws_get_weather =StructuredTool.from_function(get_weather)
   

    custom_suffix=""""""

    custom_prefix = """
    1.  First need to find latitude and longitude from place name 
    2.  Second, if you use latitude and longitude get weatcher data
    Your final answer should be of the form 'The current temperature in <location> is <temp> degrees, windspeed is km/h' 
Your final answer should use Chinese
    """

    chat_message_int = MessagesPlaceholder(variable_name="chat_history")
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_executor = initialize_agent(
        [aws_get_lat_long,aws_get_weather],
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        agent_kwargs={
            "prefix": custom_prefix,
            "suffix": custom_suffix,
            "memory_prompts": [chat_message_int],
            "input_variables": ["input", "agent_scratchpad", "chat_history"],
        },
        memory=memory,
        verbose=True,
    )

    return agent_executor


def main():
    # Initialize agent
    agent_executor = setup_full_agent()

    # Initialize chat history
    chat_history = []

    
    input1 ="Can you check the weather for me in Paris, France"
    response1 = interact_with_agent(agent_executor, input1, chat_history)
    print(response1)



if __name__ == "__main__":
    main()
