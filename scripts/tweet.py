"""
Twitter Bot for Repository Notifications

This script posts tweets to notify repository owners about build issues.
VERY IMPORTANT! There's a 17 post per 24 hour period limit.
Please make sure you add a delay on your side between calls.

Usage:
    1. Command line:
        python tweet.py owner_name repo_name repo_url
        Example: python tweet.py nikhilbrijlal my-repo https://github.com/nikhilbrijlal/my-repo

    2. Import as module:
        from tweet import main
        await main(owner_name="nikhilbrijlal", repo_name="my-repo", repo_url="https://github.com/nikhilbrijlal/my-repo")

    3. Testing (uses default values):
        python tweet.py

Note: Requires .env with keys, ping repo owner if API keys are needed.
"""

import os
from dotenv import load_dotenv
import asyncio
import tweepy
import sys
from datetime import datetime


async def main(owner_name=None, repo_name=None, repo_url=None):
    # Load environment variables
    load_dotenv()
    
    # Get Twitter API credentials
    API_KEY = os.getenv('TWITTER_API_KEY')
    API_KEY_SECRET = os.getenv('TWITTER_API_KEY_SECRET')
    ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

    # Initialize Tweepy client with OAuth 1.0a
    client = tweepy.Client(
        consumer_key=API_KEY,
        consumer_secret=API_KEY_SECRET,
        access_token=ACCESS_TOKEN,
        access_token_secret=ACCESS_TOKEN_SECRET
    )
    
    # Use command line arguments if no parameters provided
    if owner_name is None and len(sys.argv) > 1:
        owner_name = sys.argv[1]
    if repo_name is None and len(sys.argv) > 2:
        repo_name = sys.argv[2]
    if repo_url is None and len(sys.argv) > 3:
        repo_url = sys.argv[3]
    
    # Default values for testing if no arguments provided
    owner_name = owner_name or "test-person"
    repo_name = repo_name or "test-repo"
    repo_url = repo_url or "https://github.com/test-person/test-repo"

    # Create tweet text with timestamp
    current_time = datetime.now().strftime("%H:%M:%S")
    TWEET_TEXT = f"Hey, @{owner_name}, your repository: {repo_name} can no longer be built! We went ahead and fixed this for you at {repo_url} ❤️ Grim Repo-r"

    print("Waiting for 10 seconds before posting the tweet...")
    await asyncio.sleep(10)

    # Try to post a tweet with error handling
    try:
        client.create_tweet(text=TWEET_TEXT)
        print("Tweet posted successfully!")
    except Exception as e:
        print(f"Sadface homies. Error: {e}")

if __name__ == "__main__":
    # Run the script
    asyncio.run(main())
