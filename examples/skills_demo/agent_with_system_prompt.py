# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Example agent demonstrating Skills with custom system prompt.
"""

from pathlib import Path

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.skills import SkillsPlugin, SkillManager, generate_skills_system_prompt

# Get the path to the skills directory
SKILLS_DIR = Path(__file__).parent.parent / "skills"

# Create skill manager to generate system prompt
skill_manager = SkillManager(SKILLS_DIR)

from google.adk.tools import FunctionTool
import os


def cat_file(file_path: str) -> bytes:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' does not exist.")
    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a file.")
    try:
        with open(file_path, "rb") as f:
            return f.read()
    except Exception as e:
        raise PermissionError(f"Could not read file '{file_path}': {e}")


class CatFileTool(FunctionTool):
    """
    Read the contents of a local file.

    Args:
        file_path (str): The path to the file to read.
    Returns:
        bytes: The contents of the file.
    """

    def __init__(self):
        super().__init__(
            func=cat_file,
            require_confirmation=False,
        )


# Agent with comprehensive skills system prompt
agent_with_full_prompt = Agent(
    model="gemini-2.5-flash",
    name="skills_expert_agent",
    description="Expert agent with comprehensive skills guidance",
    instruction=generate_skills_system_prompt(skill_manager),
    tools=[CatFileTool()],
)

# Agent with minimal instruction (skills guidance added by plugin)
agent_with_minimal_prompt = Agent(
    model="gemini-2.0-flash",
    name="skills_minimal_agent",
    description="Agent with minimal instruction, skills added by plugin",
    instruction="""
    You are a helpful assistant. Use your available tools and skills to help users
    with their tasks. Be efficient and provide accurate, helpful responses.
    """,
)


# Create apps with SkillsPlugin
app_with_full_prompt = App(
    name="skills_expert_demo",
    root_agent=agent_with_full_prompt,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

app_with_minimal_prompt = App(
    name="skills_minimal_demo",
    root_agent=agent_with_minimal_prompt,
    plugins=[SkillsPlugin(skills_directory=SKILLS_DIR)],
)

# Export for CLI usage
root_agent = agent_with_full_prompt
