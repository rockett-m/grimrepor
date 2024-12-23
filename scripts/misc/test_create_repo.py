import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com/user/repos"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def create_new_github_repo(new_repo_name):
    """
    Creates a new GitHub repository using the GitHub API.
    
    Args:
        new_repo_name (str): Name for the new repository
        
    Returns:
        dict: Response from GitHub API including repository details if successful
    """
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "name": new_repo_name,
        "description": "Test repository created via GitHub API",
        "private": False,
        "auto_init": True,
        "gitignore_template": "Python",  # Adds Python .gitignore
        "license_template": "mit"  # Adds MIT license
    }

    try:
        response = requests.post(GITHUB_API_URL, json=data, headers=headers)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        print(f"Repository created successfully!")
        print(f"URL: {response.json().get('html_url')}")
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating repository: {e}")
        if hasattr(e.response, 'json'):
            print(f"GitHub API response: {e.response.json()}")
        return None

def main():
    # Check if GitHub token is available
    if not GITHUB_TOKEN:
        print("Error: GitHub token not found. Please set GITHUB_TOKEN in your .env file")
        return

    # Get repository name from user
    repo_name = input("Enter the name for your new repository: ")
    
    # Create the repository
    result = create_new_github_repo(repo_name)
    
    if result:
        print("\nRepository details:")
        print(f"Name: {result.get('name')}")
        print(f"Description: {result.get('description')}")
        print(f"Clone URL: {result.get('clone_url')}")
        print(f"SSH URL: {result.get('ssh_url')}")

if __name__ == "__main__":
    main() 