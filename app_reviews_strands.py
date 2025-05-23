import os
import json
import sys
from datetime import datetime

import boto3
from google_play_scraper import search, Sort, reviews
from app_store_scraper import AppStore

# 导入Strands Agents
from strands import Agent, tool
import logging

# 启用Strands调试日志
logging.getLogger("strands").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

# 定义工具函数
@tool
def get_google_app_id(app_name: str) -> str:
    """
    Find Google Play Store AppID by app name.
    
    Args:
        app_name (str): The name of the app to search for
        
    Returns:
        str: The app ID if found, None otherwise
    """
    try:
        result = search(
            app_name,
            lang="en",
            country="us",
            n_hits=1
        )
        if len(result) > 0:
            return result[0]['appId']
        else:
            return None
    except Exception as e:
        print(e)
        return None

@tool
def get_google_play_app_review(app_id: str, country: str = "us", rank: int = -1, page: int = 1) -> list:
    """
    Get app reviews from Google Play Store.
    
    Args:
        app_id (str): The app ID to get reviews for
        country (str): The country code to get reviews from
        rank (int): Filter reviews by this score (-1 for all scores)
        page (int): The page number of reviews to get
        
    Returns:
        list: A list of reviews with username, content, and score
    """
    try:
        filter_score = None
        if rank > 0 and rank < 6:
            filter_score = rank
        
        result, continuation_token = reviews(
            app_id,
            lang='en',
            country="us" if country == "" else country,
            sort=Sort.NEWEST,
            count=100,
            filter_score_with=filter_score
        )
        
        save_review(app_id, result)
        
        return [{"username": review["userName"], "content": review["content"], "score": review["score"]} for review in result]
    except Exception as e:
        print(e)
        return []

def save_review(app_id, data):
    """Save reviews to a JSON file."""
    os.makedirs("output", exist_ok=True)
    with open(f"output/{app_id}.json", "w", encoding="utf-8") as file:
        json.dump(data, file, cls=DateTimeEncoder, ensure_ascii=False, indent=4)

def analyze_app_reviews(store: str, app_name: str, country: str = "us", rank: int = -1):
    """
    Main function to analyze app reviews using Strands Agents.
    
    Args:
        store (str): The app store to get reviews from ('Google Play', 'Apple', 'Steam')
        app_name (str): The name of the app to analyze
        country (str): The country code to get reviews from
        rank (int): Filter reviews by this score (-1 for all scores)
        
    Returns:
        tuple: (app_id, analysis_result)
    """
    # 创建Strands Agent
    agent = Agent(
        tools=[get_google_app_id, get_google_play_app_review],
        model="us.anthropic.claude-3-7-sonnet-20250219-v1:0"
    )
    
    print(f"Agent model: {agent.model.config}")
    
    # 获取app ID
    if store == 'Google Play':
        app_id_message = f"Find the Google Play Store app ID for the app named '{app_name}'."
        app_id_result = agent(app_id_message)
        
        # 修复：直接使用返回结果作为字符串，而不是尝试访问.message属性
        app_id = str(app_id_result).strip()
        
        # 如果返回的不是有效的app ID，尝试直接调用工具
        if not app_id or "I'll help you find" in app_id:
            app_id = get_google_app_id(app_name)
    else:
        app_id = app_name  # 简化处理，其他商店直接使用app_name作为ID
    
    print(f"App ID: {app_id}")
    
    # 获取应用评论
    reviews_message = f"""
    Get app reviews from {store} for the app with ID '{app_id}' in country '{country}'.
    If rank is specified ({rank}), filter reviews by that score.
    """
    
    reviews_result = agent(reviews_message)
    
    # 分析评论
    analysis_message = f"""
    Analyze the following app reviews from {store}, app_id: {app_id}, country: {country}.
    
    {reviews_result}
    
    Your task:
    1. Identify common issues mentioned in the reviews (e.g., price issues, network issues, game content issues)
    2. Calculate the percentage for each review score (1-5 stars)
    3. Summarize the overall sentiment
    4. Format your response in markdown
    5. Translate your analysis to Chinese
    """
    
    analysis_result = agent(analysis_message)
    
    # 修复：直接返回结果字符串，而不是尝试访问.message属性
    return app_id, str(analysis_result)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process app name and get reviews summary.")
    parser.add_argument("app_name", nargs="?", help="The name of the app to analyze")
    parser.add_argument("-i", "--interaction", action="store_true", help="Enable interactive mode")
    
    args = parser.parse_args()
    
    if args.interaction:
        print("Interactive mode enabled")
        store = input("Enter store (Google Play, Apple, Steam): ")
        app_name = input("Enter app name: ")
        country = input("Enter country code (default: us): ") or "us"
        rank_input = input("Enter rank filter (1-5, default: all): ")
        rank = int(rank_input) if rank_input.isdigit() else -1
    else:
        store = "Google Play"
        app_name = args.app_name or "Genshin Impact"
        country = "us"
        rank = -1
    
    app_id, result = analyze_app_reviews(store, app_name, country, rank)
    print("\n--- Analysis Result ---\n")
    print(result)
