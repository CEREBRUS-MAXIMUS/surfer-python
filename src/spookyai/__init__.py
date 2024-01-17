import os as _os
from pydantic import BaseModel, Field
import asyncio
import json
import requests
import time
from langchain.tools import BaseTool
from datetime import datetime


api_key: str | None = _os.environ.get("SPOOKY_API_KEY")

agent_id: str | None = _os.environ.get("SPOOKY_AGENT_ID")

agent_name: str | None = _os.environ.get("SPOOKY_AGENT_NAME")

agent_image: str | None = _os.environ.get("SPOOKY_AGENT_IMAGE")

SPOOKY_URL = "https://cerebrus-prod-eastus.azurewebsites.net/"


def query_human(query: str, metadata: str = "", timeout: int = 86400) -> str:
    """
    Query a human for an answer to a question.
    :param query: The question to ask the human.
    :param metadata: All relevant information about the query, including the context in which it is being asked, and the consequences of the answer. This is what the user will see when they are asked for their consent. This is optional, but highly recommended. It is in Markdown.
    :param timeout: The maximum amount of time to wait for a response from the human, in seconds. Defaults to 24 hours.
    :return: The response from the human.
    """
    
    #get the current unix timestamp
    now = datetime.now()
    current_time = datetime.timestamp(now)
    
    #make a unique ID for the query with the userID and timestamp
    queryID = api_key + "-" + str(current_time)

    data = {
        "apiKey": api_key,
        "query": query,
        "queryID": queryID,
        "agentID": agent_id,
        "agentImage": agent_image, #optional, defaults to spooky logo
        "agentName": agent_name,
        "metadata": metadata,
    }

    headers = {
        "Content-Type": "application/json",
    }

    url = SPOOKY_URL + "queryHuman"
    headers = {'Content-Type': 'application/json'}
    
    start_time = time.time()

    while True:
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=None) #4 Minutes
            if response.status_code == 200:
                print("Success:", response.json())
                return response.json()
            else:
                print("Error:", response.json())
                return response.json()
        except requests.exceptions.RequestException as e:
            print("Request failed:", e)
            
        elapsed_time = time.time() - start_time
        if elapsed_time > timeout:
            print("Timeout occurred")
            return "Timeout occurred: the user was given " + str(timeout) + " seconds to respond, but did not respond in time."

        # Add a sleep to avoid constant retries and reduce server load
        time.sleep(1)


def human_approval(query: str) -> str:
    pass

class _HumanQueryInput(BaseModel):
    query: str = Field()
    metadata: str = Field() #In Markdown: All relevant information about the query, including the context in which it is being asked, and the consequences of the answer. This is what the user will see when they are asked for their consent.

class _HumanQuery(BaseTool):
    name = "QueryHuman"
    description = "useful for when you need to ask your human a question- for permission, to get personal info you can't find elsewhere, and much more. Use sparingly. Arguments: query: the question you want to ask your human. metadata: All relevant information about the query, including the context in which it is being asked, and the consequences of the answer. This is what the user will see when they are asked for their consent. This is optional, but highly recommended. It is in Markdown."
    args_schema: type[BaseModel] = _HumanQueryInput

    def _run(
        self, query: str, metadata: str, run_manager: None
    ) -> str:
        """Use the tool."""
        return query_human(query, metadata)
            

    async def _arun(
        self, query: str, metadata: str, run_manager: None
    ) -> str:
        return self._run(query, metadata, run_manager)
        
        
#Agent Consent Tool: sends a notification to the user asking for consent to use their data
class _HumanApprovalInput(BaseModel):
    query: str = Field()
    
class _HumanApproval(BaseTool):
    name = "HumanApproval"
    description = "useful for when you need to ask your human for confirmation before doing something - for example, using a important tool, or sending a message to someone"
    args_schema: type[BaseModel] = _HumanApprovalInput

    def _run(
        self, query: str, run_manager: None
    ) -> str:
        """Use the tool."""
        return human_approval(query)
            

    async def _arun(
        self, query: str, run_manager: None
    ) -> str:
        return self._run(query, run_manager)



#Agent Stuck in a Loop : sends time sensitive notification to user


#human consent tool: sends a notification to the user asking for consent to use their data    
    
    
HumanQuery = _HumanQuery()
HumanApproval = _HumanApproval()