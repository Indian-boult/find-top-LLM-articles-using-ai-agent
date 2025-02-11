import autogen
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

print(endpoint, api_key, deployment_name, api_version)

os.environ["AZURE_OPENAI_API_KEY"] = api_key

config_list = [
    {
        "model": deployment_name,  
        "base_url": endpoint, 
        "api_type": "azure", 
        "api_version": api_version, 
        "api_key": api_key
 }
]

llm_config = {
    "cache_seed": None,
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

user_proxy = autogen.UserProxyAgent(
    name="Admin",
    llm_config=llm_config,
    system_message="A human agent. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
    code_execution_config={
        "work_dir": "code",
        "use_docker": False,
    },
    human_input_mode="NEVER",
)

engineer = autogen.AssistantAgent(
    name = "Engineer",
    llm_config=llm_config,
    system_message="""Engineer. You follow as approved plan. Make sure you save the code to disk. You write python
    code to solve tasks. Wrap the code in a code block that specifies the script type and name of the file to save to disk.
    """
)

scientist = autogen.AssistantAgent(
    name="Scientist",
    llm_config=llm_config,
    system_message="""Scientist. You follow as approved plan. You are able to categorize papers after seeing their abstracts
    printed. You don't write the code.""",
)

planner = autogen.AssistantAgent(
    name="Planner",
    llm_config=llm_config,
    system_message="""Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
    The plan may involve an engineer who can write code and a scientist who doesn't write code.
    Explain the plan first. Be clear which step is performed by the engineer, and which step is performed by the scientist.
    """,
)

critic = autogen.AssistantAgent(
    name="Critic",
    llm_config=llm_config,
    system_message="""Critic. Double check plan, claims, code from other agents and provide feedback. Check weather
    the plan includes adding verifiable info such as source url.
    """,
)

group_chat = autogen.GroupChat(
    agents=[user_proxy, engineer, scientist, planner, critic],messages=[],max_round=25
)

manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

user_proxy.initiate_chat(
    manager,
    message="Find papers on LLM applications from arxiv in the last week, then save them in a txt file. First you have to create a file and then write in it."
)