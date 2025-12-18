from google.adk.agents.remote_a2a_agent import AGENT_CARD_WELL_KNOWN_PATH
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent


root_agent = RemoteA2aAgent(
    name="hello_world_agent",
    description=(
        "Helpful assistant that can roll dice and check if numbers are prime."
    ),
    agent_card=f"https://ht-adk.yuepa8.com/a2a/remote_a2a{AGENT_CARD_WELL_KNOWN_PATH}",
)
