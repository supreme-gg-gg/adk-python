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
Example agent demonstrating the recommended Skills integration with ADK.

This agent uses the `SkillsPlugin` to automatically gain access to the shell
and is configured with a comprehensive system prompt for optimal performance.
"""

from pathlib import Path

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.plugins.save_files_as_artifacts_plugin import SaveFilesAsArtifactsPlugin
from google.adk.skills import SkillsPlugin, generate_shell_skills_system_prompt
from google.adk.tools import StageArtifactsTool

# Define the path to the skills directory, relative to this file.
SKILLS_DIR = Path(__file__).parent.parent / "skills"

# 1. Define the Agent
agent = Agent(
    model="gemini-2.5-flash",
    name="skills_expert_agent",
    description="An agent that uses a sandboxed shell to interact with a library of skills.",
    instruction=generate_shell_skills_system_prompt(SKILLS_DIR),
    # This tool allows agent to "stage" files from artifact service to the skills / operating FS.
    tools=[StageArtifactsTool(skills_directory=SKILLS_DIR)],
)

# 2. Define the App
app = App(
    name="skills_demo_app",
    root_agent=agent,
    plugins=[
        SkillsPlugin(skills_directory=SKILLS_DIR),
        # This plugin saves any user-uploaded files as artifacts instead of uploading to the LLM directly.
        SaveFilesAsArtifactsPlugin(),
    ],
)

# 3. Export the app for the runner.
# The `adk run` command will automatically discover and use this `root_agent`.
root_agent = agent
