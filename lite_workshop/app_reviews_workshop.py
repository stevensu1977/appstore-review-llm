from langchain_aws import ChatBedrock
from langchain.agents import tool 
from google_play_scraper import search, Sort, reviews
import json
from datetime import datetime
from langchain.agents import tool
from google_play_scraper import Sort, reviews
from crewai import Agent
import sys
from crewai import Task, Crew
import re

def init_bedrock_chat(model_id='anthropic.claude-3-sonnet-20240229-v1:0', region_name='us-west-2'):

    model_kwargs =  { 
        "max_tokens": 4096,
        "temperature": 0.0
    }
    bedrock_chat = ChatBedrock(model_id=model_id, model_kwargs=model_kwargs, region_name=region_name)
    print("boto3 Bedrock client successfully created!")
    return bedrock_chat


bedrock_llm = init_bedrock_chat()


@tool
def get_google_app_id(app_name:str):
    """Tool to found Google App Store AppID by app name"""
    try:
        result = search(
            app_name,
            lang="en",  # defaults to 'en'
            country="us",  # defaults to 'us'
            n_hits=1  # defaults to 30 (= Google's maximum)
        )
        if len(result)>0:
            return result[0]['appId']
        else:
            return None

    except Exception as e:
        print(e)
        return None



class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def save_review(app_id, data):
    with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, cls=DateTimeEncoder,
                  ensure_ascii=False, indent=4)


@tool
def get_google_play_app_review(app_id: str, country: str = 'us', rank: int = -1, page: int = 1):
    """Tool to found Google App Store App reviews by app id ,country ,rank and page"""
    try:

        filter_score = None
        if rank > 0 and rank < 6:
            filter_score = rank
        print(f"{country=}")
        result, continuation_token = reviews(
            app_id,
            lang='en',  # defaults to 'en'
            country="us" if country == "" else country,  # defaults to 'us'
            sort=Sort.NEWEST,  # defaults to Sort.NEWEST
            count=100,  # defaults to 100
            filter_score_with=filter_score
        )

        if continuation_token:
            print(f'Have continuation token: {continuation_token}')

        # if len(result) > 0:
        #     process_app_review_with_llm(result)
        save_review(app_id, result)
        # with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
        #     json.dump(result, file, cls=DateTimeEncoder,ensure_ascii=False, indent=4)

        return [{"username": review["userName"], "content": review["content"], "score": review["score"]} for review in result]
    except Exception as e:
        print(e)
        return []
    

review_loader = Agent(
    role='App Review Research Analyst',
    goal='If user input is app id, you load App review  from a app id',
    backstory='Specializes in handling and interpreting app reviews documents',
    verbose=True,
    tools=[get_google_play_app_review],
    allow_delegation=False,
    llm=bedrock_llm,
    memory=True,
)

researcher = Agent(
  role='Expert App Store reviews summarizer',
  goal='Found prices issue , network issue, game content issue in every user\'s reviews content, you need keep username',
  backstory="""You are a renowned expert summarizer of AI related 
  Google App Store User reviews, known for your insightful 
  and engaging articles. You transform complex concepts into 
  compelling narratives.""",
  verbose=True,
  allow_delegation=True,
  llm=bedrock_llm
  
)



def init_app_crew(store:str,app_name:str,country:str, rank:int=-1,page:int=1, file:str="",output_stream=None):
    """
    This function is the main entry point for the application.
    It takes an app name and a review rank , page as input, and returns the result of processing the app reviews.
    """
    
    if output_stream is not None:
            sys.stdout = output_stream
    

    # Get the app ID from the app name using the get_google_app_id tool
    app_id = get_google_app_id(app_name)
        
    # Create a task for the review_reader agent to fetch reviews for the given app ID and rank
    review_loading_task = Task(
        description=f"""Use store: {store} ,app_name:{app_name} app_id: {app_id} and country:{country}, rank: {rank}, page: {page}""",
        agent=review_loader,
        expected_output='A refined finalized version of the blog post in markdown format'
    )

    content_creation_task = Task(
        description="""Using the insights provided by the research Analyst agent, if have different score , please calculate every score the percentage
        develop an engaging  content, you need use markdown format and translate to chinese. """,
        agent=researcher,
        expected_output=f'A refined finalized version of the blog post in markdown format,need include store: {store} , app_id: {app_id} and country:{country},translate to chinese.'
    )

    # Instantiate a Crew with the review_reader and researcher agents, and the tasks to be performed
    # Set the logging level to 2 (more verbose)
    crew = Crew(
        agents=[review_loader, researcher],
        tasks=[review_loading_task, content_creation_task],
        verbose=2, 
    )

    return app_id,crew

# app_id, crew=init_app_crew('Google Play', 'genshin', "us", -1)
# crew.kickoff()