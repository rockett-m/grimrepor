import subprocess
import os
import sys

def get_all_contributor_emails(repo_path):
    try:
        # Verify the path exists and is a directory
        if not os.path.isdir(repo_path):
            raise ValueError(f"The path '{repo_path}' is not a valid directory")
            
        # Verify it's a git repository
        if not os.path.isdir(os.path.join(repo_path, '.git')):
            raise ValueError(f"The directory '{repo_path}' is not a git repository")
        
        # Change to the repository directory
        original_dir = os.getcwd()
        os.chdir(repo_path)
        
        try:
            # Run git log command to get all commit emails
            command = ["git", "log", "--pretty=format:%ae"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            
            # Split output into lines and convert to set to remove duplicates
            emails = set(result.stdout.split('\n'))
            
            # Write emails to file in the repository directory
            output_file = os.path.join(repo_path, 'contributor_emails.txt')
            with open(output_file, 'w') as f:
                for email in sorted(emails):
                    f.write(f"{email}\n")
            
            print(f"Successfully extracted {len(emails)} unique contributor emails to {output_file}")
            
        finally:
            # Always change back to original directory
            os.chdir(original_dir)
            
    except subprocess.CalledProcessError:
        print("Error: Failed to execute git command")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_contributor_emails.py <path_to_git_repo>")
        sys.exit(1)
        
    repo_path = os.path.abspath(sys.argv[1])
    get_all_contributor_emails(repo_path) 