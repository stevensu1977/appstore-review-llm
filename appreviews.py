import os
import csv
import json
import sys
import chardet 

from datetime import datetime

import boto3
from google_play_scraper import search, Sort, reviews
from app_store_scraper import AppStore


from langchain.agents import tool 
from langchain_community.chat_models import BedrockChat


from crewai import Agent, Task, Crew
from crewai.telemetry import Telemetry

import steam  


#Disable CrewAI Anonymous Telemetry
def noop(*args, **kwargs):
    pass

for attr in dir(Telemetry):
    if callable(getattr(Telemetry, attr)) and not attr.startswith("__"):
        setattr(Telemetry, attr, noop)


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)
    
#Config Amazon Bedrock claude3
def initialize_llm():
    """
    Initialize a Large Language Model (LLM) instance using the Bedrock Runtime service.

    Returns:
        BedrockChat: An instance of the BedrockChat class, which represents the initialized LLM.

    """
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    model_kwargs = {
        "max_tokens": 2048,
        "temperature": 0.0,
        "top_k": 250,
        "top_p": 1,
        "stop_sequences": ["\n\nHuman"],
    }

    # Check if AWS_REGION environment variable is set
    aws_region = os.environ.get("AWS_REGION", "us-west-2")

    bedrock_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name=aws_region,
    )

    bedrock_llm = BedrockChat(
        client=bedrock_runtime,
        model_id=model_id,
        model_kwargs=model_kwargs,
    )

    return bedrock_llm

bedrock_llm = initialize_llm()

def split_data(data, page=1):
    """Tool to split data into pages of 50 items"""
    if isinstance(data, list):
        total_pages = (len(data) + 49) // 50  # Calculate the total number of pages
        if page < 1 or page > total_pages:
            print(f"Invalid page number. Please enter a value between 1 and {total_pages}.")
            return []
        start_index = (page - 1) * 50
        end_index = start_index + 50
        return data[start_index:end_index]
    else:
        print("Input data is not a list.")
        return []
    
def save_review(app_id,data):
    with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
            json.dump(data, file, cls=DateTimeEncoder,ensure_ascii=False, indent=4)

@tool
def get_apple_app_review(app_name:str, country:str, rank:int = -1,page:int=1):
    """Tool to found Apple App Store App reviews by app name ,country ,rank and page"""
    try:
        app = AppStore(country=country, app_name=app_name)
        app.review(how_many=100)
        result = app.reviews

        if rank==-1:
            save_review(app_name, result)
            return result
        else:
            filter_result = [item for item in result if item['rating'] == rank]
            save_review(app_name, filter_result)
            return filter_result
    except Exception as e:
        print(e)
        return []





@tool
def load_local_file(file_name: str,page:int=1):
    """Tool to load local file , page must start from 1"""
    try:
        with open(file_name, "rb") as file:
            result = chardet.detect(file.read())
            encoding = result["encoding"]

        file_extension = file_name.split(".")[-1].lower()

        if file_extension == "csv":
            with open(file_name, "r", encoding=encoding) as file:
                reader = csv.reader(file)
                data = list(reader)
            
            return split_data(data,page)

        elif file_extension == "json":
            with open(file_name, "r", encoding=encoding) as file:
                data = json.load(file)
            return split_data(data,page)

        elif file_extension == "txt":
            with open(file_name, "r", encoding=encoding) as file:
                data = file.read().splitlines()
            return data

        else:
            print(f"Unsupported file extension: {file_extension}")
            return []

    except Exception as e:
        print(f"Error loading file: {e}")
        return []
    
# Tool to found Steam AppID by app name   
@tool
def get_steam_app_id(app_name:str):
    """Tool to found Steam App AppID by app name"""
    try:
        return steam.get_steam_app_id(game_name=app_name)

    except Exception as e:
        print(e)
        return None
    
@tool
def get_steam_app_reviews(app_id:str,country:str, rank:int = -1,page:int=1):
    """Tool to found Steam App Store App reviews by app id , rank , page """
    try:
        review_type = "all"
        if rank == 1:
            review_type = "negative"
        elif rank==5:
            review_type="positive"
        result=steam.get_steam_n_reviews(appid=app_id, review_type=review_type)
        save_review(app_id, result)
        return result
    except Exception as e:
        print(e)
        return None


# Tool to found Google App Store AppID by app name   
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

# Tool to found Google App Store App reviews by app id
@tool
def get_google_play_app_review(app_id:str,country:str,rank:int = -1,page:int=1 ):
    """Tool to found Google App Store App reviews by app id ,country ,rank and page"""
    try:
        
        filter_score = None
        if rank > 0 and rank <6:
            filter_score = rank
        print(f"{country=}")
        result, continuation_token = reviews(
        app_id,
        lang='en', # defaults to 'en'
        country="us" if country=="" else country , # defaults to 'us'
        sort=Sort.NEWEST, # defaults to Sort.NEWEST
        count=100, # defaults to 100
        filter_score_with= filter_score
        )
        
        if continuation_token:
            print(f'Have continuation token: {continuation_token}')

        # if len(result) > 0:
        #     process_app_review_with_llm(result)
        save_review(app_id, result)
        # with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
        #     json.dump(result, file, cls=DateTimeEncoder,ensure_ascii=False, indent=4)

        return [{"username":review["userName"],"content":review["content"],"score":review["score"]} for review in result]
    except Exception as e:
        print(e)
        return []



review_loader = Agent(
    role='App Review Research Analyst',
    goal='If user input is app id and store type google or apple ,you load App review  from a app id',
    backstory='Specializes in handling and interpreting app reviews documents',
    verbose=True,
    tools=[get_google_play_app_review,get_apple_app_review,get_steam_app_reviews,load_local_file],
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
    if store =='Google Play':
        app_id = get_google_app_id(app_name)
    elif store =='Steam':
        app_id = get_steam_app_id(app_name)
    else:
        app_id=""
        
    # Create a task for the review_reader agent to fetch reviews for the given app ID and rank
    review_loading_task = Task(
        description=f"""Use store: {store} ,app_name:{app_name} app_id: {app_id} and country:{country}, rank: {rank}, page: {page}, if store is Custom File , please load local "upload/{file}", if result more than 50, you need every time process 50 result, return reviews""",
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



def interactive_mode():
    """
    This function provides an interactive mode for the user to enter the app name and review rank.
    It runs in a loop until the user enters 'q' to quit.
    """
    while True:
        app_store = input("Enter the app store [Google|Apple] (or 'q' to quit): ")
        app_name = input("Enter the app name (or 'q' to quit): ")
        if app_name.lower() == 'q':
            # If the user enters 'q', exit the loop and the interactive mode
            break
        rank = input("Enter the review rank (1-5, or -1 for all reviews): ")
        try:
            rank = int(rank)
            if rank < -1 or rank > 5:
                # If the rank is not between 1 and 5, or -1 for all reviews, print an error message
                print("Invalid rank. Please enter a value between 1 and 5, or -1 for all reviews.")
                continue
        except ValueError:
            # If the user enters a non-integer value for the rank, print an error message
            print("Invalid rank. Please enter a valid integer.")
            continue
        _,app_crew=init_app_crew(app_store, app_name, "us", rank)
        result = app_crew.kickoff()
        print(result)

def main(app_store,app_name):
    """
    This function calls the kickoff function with the provided app name and a rank of -1 (for all reviews).
    It prints the result returned by the kickoff function.
    """
    _,app_crew=init_app_crew(app_store, app_name, "us", -1)
    result = app_crew.kickoff()
    print(result)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Process app name and get reviews summary.')
    parser.add_argument('--app_store',default='Google', nargs='?', type=str, help='Google|Apple')
    parser.add_argument('--app_name',default='Minecraft', nargs='?', type=str, help='The name of the app to analyze')
    parser.add_argument('-i', '--interaction', action='store_true', help='Enable interactive mode')
    args = parser.parse_args()
    if args.interaction:
        interactive_mode()
    elif args.app_name:
        main(args.app_store,args.app_name)
    else:
        parser.print_help()

