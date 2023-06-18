import streamlit as st
import re
import requests
from github import Github
from urllib.parse import urlparse
import openai

# Set up your OpenAI API credentials
openai.api_key = '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'
# Authenticate with GitHub API using a personal access token
g = Github("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")

def extract_username(github_url):
    # Extract the username from the GitHub URL
    pattern = r"(?:http[s]?://)?(?:www\.)?(?:github\.com/)?([a-zA-Z0-9_-]+)(?:/.*)?"
    match = re.match(pattern, github_url)

    if match:
        return match.group(1)

    # If the URL format is not recognized, raise an exception
    raise ValueError("Invalid GitHub URL or username not found")


def fetch_user_repositories(github_url):
    # Extract the username from the GitHub URL
    username = extract_username(github_url)

    if not is_valid_username(username):
        raise ValueError("Invalid GitHub username")

    try:
        # Make a GET request to the GitHub API to fetch the user's repositories
        api_url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(api_url)

        if response.status_code == 200:
            repositories = [repo['name'] for repo in response.json()]
            return repositories
        else:
            # Return None when failed to fetch repositories
            return None
    except requests.exceptions.RequestException:
        # Return None when failed to fetch repositories
        return None


def is_valid_username(username):
    # Check if the username is not empty and contains only alphanumeric characters and hyphens
    if username and re.match("^[a-zA-Z0-9-]+$", username):
        # Check if the username length is within a valid range
        if 1 <= len(username) <= 39:
            return True

    return False


    try:
        # Make a GET request to the GitHub API to fetch the user's repositories
        api_url = f"https://api.github.com/users/{username}/repos"
        response = requests.get(api_url)

        if response.status_code == 200:
            repositories = [repo['name'] for repo in response.json()]
            return repositories
        else:
            raise ValueError("Failed to fetch repositories from GitHub API")
    except requests.exceptions.RequestException:
        raise ValueError("Failed to fetch repositories from GitHub API")


def assess_code_complexity(code):
    # Preprocess the code as needed before passing it to GPT
    preprocessed_code = preprocess_code(code)

    # Format the GPT prompt by replacing the {code} placeholder with the preprocessed code
    formatted_prompt = generate_prompt(preprocessed_code)

    # Generate response from GPT
    response = openai.Completion.create(
        engine='text-davinci-003',  # Use the appropriate GPT model
        prompt=formatted_prompt,
        max_tokens=1000,  # Adjust the token limit as needed
        temperature=0.7,  # Adjust the temperature to control response randomness
        n=1,  # Generate a single response
        stop=None,  # Let GPT generate the full response
        timeout=30,  # Set an appropriate timeout value
    )

    # Extract the generated response from GPT
    generated_response = response.choices[0].text.strip()

    # Analyze the generated response to determine the technical complexity of the code
    complexity_score = analyze_generated_response(generated_response)

    return complexity_score


def fetch_code_from_repository(repository, username):
    # Parse the repository URL to extract the repository name
    url_parts = urlparse(repository)
    path_parts = url_parts.path.strip("/").split("/")

    if len(path_parts) == 1:
        # Only repository name provided
        repository_name = path_parts[0]
    else:
        raise ValueError("Invalid repository URL or name.")

    # Make a GET request to the GitHub API to fetch the repository contents
    api_url = f"https://api.github.com/repos/{username}/{repository_name}/contents"
    response = requests.get(api_url)

    if response.status_code == 200:
        # Extract the file paths from the API response
        files = response.json()
        file_paths = [file['path'] for file in files if file['type'] == 'file']

        # Fetch the code from each file
        code = ""
        for file_path in file_paths:
            file_url = f"https://raw.githubusercontent.com/{username}/{repository_name}/master/{file_path}"
            file_response = requests.get(file_url)
            code += file_response.text

        return code
    else:
        raise ValueError("Failed to fetch code from the repository. Please check the repository URL or name.")


def preprocess_code(code):
    # Remove comments from the code
    code = remove_comments(code)

    # Remove blank lines from the code
    code = remove_blank_lines(code)

    # Remove trailing whitespaces
    code = remove_trailing_whitespaces(code)

    # Exclude specific file types if needed
    excluded_file_types = ['.txt', '.csv']
    if any(file_type in code for file_type in excluded_file_types):
        return ""

    return code


def remove_comments(code):
    # Remove single-line comments
    code = re.sub(r"\/\/.*", "", code)

    # Remove multi-line comments
    code = re.sub(r"\/\*.*?\*\/", "", code, flags=re.DOTALL)

    return code


def remove_blank_lines(code):
    code_lines = code.split('\n')
    code_lines = [line for line in code_lines if line.strip() != '']
    code = '\n'.join(code_lines)
    return code


def remove_trailing_whitespaces(code):
    code_lines = code.split('\n')
    code_lines = [line.rstrip() for line in code_lines]
    code = '\n'.join(code_lines)
    return code


def generate_prompt(code):
    # Implement your prompt engineering logic here
    # Generate a prompt that incorporates code characteristics or specific questions for code evaluation

    # Extract code characteristics or relevant information
    code_lines = code.split('\n')
    num_lines = len(code_lines)
    # You can add more code characteristics as per your requirements

    # Generate a prompt using the extracted code characteristics
    prompt = f"Please evaluate the technical complexity of the following code:\n\n"
    prompt += f"Code:\n{code}\n\n"
    prompt += f"Code Characteristics:\n"
    prompt += f"- Number of lines: {num_lines}\n"
    # Add more code characteristics if needed

    # Add specific questions for code evaluation
    prompt += f"\nQuestions for Evaluation:\n"
    prompt += "- How would you describe the code structure and organization?\n"
    prompt += "- Are there any advanced techniques or algorithms used in the code?\n"
    prompt += "- Can you identify any potential performance bottlenecks or areas for optimization?\n"
    # Add more evaluation questions as per your requirements

    return prompt


def generate_justification(repository):
    # Implement your prompt engineering logic here
    # Generate a prompt that justifies the selection of the most complex repository

    # Generate a prompt using the selected repository
    prompt = f"Justification for selecting the most complex repository:\n\n"
    prompt += f"The repository '{repository}' has been identified as the most technically complex based on its complexity score. "
    prompt += "The complexity score is determined by evaluating the technical aspects and characteristics of the code, such as code structure, "
    prompt += "organization, advanced techniques or algorithms used, potential performance bottlenecks, and areas for optimization.\n"
    prompt += "Please provide a detailed explanation to justify the selection of this repository as the most complex."

    return prompt


# ...

# Conversation flow
st.title("Code Complexity Evaluator")
st.write("I can help you evaluate the technical complexity of code in a GitHub repository.")
github_user_url = st.text_input("Enter the GitHub UserName:")

if st.button("Evaluate"):
    try:
        user_repositories = fetch_user_repositories(github_user_url)
        
        if user_repositories is None:
            st.write("No repositories found for the provided GitHub user.")
        else:
            st.write(f"Found {len(user_repositories)} repositories for the provided GitHub user:")
            for repository in user_repositories:
                st.write(f"- {repository}")

            selected_repository = st.selectbox("Select a repository:", user_repositories)
            code = fetch_code_from_repository(selected_repository, extract_username(github_user_url))
            complexity_score = assess_code_complexity(code)
            st.write(f"The technical complexity score for the selected code is: {complexity_score}")

            justification_prompt = generate_justification(selected_repository)
            justification = generate_justification(justification_prompt)
            st.write("Justification for selecting the most complex repository:")
            st.write(justification)

    except ValueError as e:
        st.error(str(e))
