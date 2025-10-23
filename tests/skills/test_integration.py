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

"""Integration tests for Skills functionality with ADK agents."""

import pytest
import tempfile
from pathlib import Path

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.skills import SkillsPlugin, SkillsToolset
from google.genai import types


class TestSkillsIntegration:
    """Integration tests for Skills with ADK agents."""

    @pytest.fixture
    def test_skills_dir(self):
        """Create temporary skills directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test skill
            skill_dir = temp_path / "test-skill"
            skill_dir.mkdir()
            skill_content = """---
name: test-skill
description: A test skill that helps with testing tasks
---
# Test Skill

This skill provides testing capabilities:

1. Create test data
2. Run test scenarios  
3. Validate results

Use this skill when you need help with testing tasks."""

            (skill_dir / "SKILL.md").write_text(skill_content)

            yield temp_path

    @pytest.fixture
    def agent_with_toolset(self, test_skills_dir):
        """Create agent with SkillsToolset."""
        return Agent(
            model="gemini-2.0-flash",
            name="skills_toolset_agent",
            description="Agent that uses skills through toolset",
            instruction="""
      You have access to skills through tools. Use discover_skills to see
      available skills, then load_skill when relevant to user requests.
      """,
            tools=[SkillsToolset(skills_directory=test_skills_dir)],
        )

    @pytest.fixture
    def agent_with_plugin(self, test_skills_dir):
        """Create agent with SkillsPlugin."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="skills_plugin_agent",
            description="Agent that uses skills through plugin",
            instruction="""
      You have skills available. When relevant to user requests, you can
      request to "load skill [name]" to get skill content.
      """,
        )

        app = App(
            name="test_app",
            root_agent=agent,
            plugins=[SkillsPlugin(skills_directory=test_skills_dir)],
        )

        return app

    @pytest.mark.asyncio
    async def test_toolset_integration(self, agent_with_toolset):
        """Test skills integration through SkillsToolset."""
        runner = InMemoryRunner(
            agent=agent_with_toolset,
            app_name="test_app",
            session_service=InMemorySessionService(),
        )

        session = await runner.session_service.create_session(
            user_id="test_user", app_name="test_app"
        )

        # Test skill discovery
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="What skills do you have available?")],
            ),
        ):
            events.append(event)

        # Should have discovered and mentioned skills
        response_text = ""
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        # Response should mention the test skill
        assert (
            "test-skill" in response_text.lower() or "testing" in response_text.lower()
        )

        await runner.close()

    @pytest.mark.asyncio
    async def test_plugin_integration(self, agent_with_plugin):
        """Test skills integration through SkillsPlugin."""
        runner = InMemoryRunner(
            app=agent_with_plugin, session_service=InMemorySessionService()
        )

        session = await runner.session_service.create_session(
            user_id="test_user", app_name=agent_with_plugin.name
        )

        # Test asking about available skills
        events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="I need help with testing. Do you have any relevant skills?"
                    )
                ],
            ),
        ):
            events.append(event)

        # Should have skills context and respond appropriately
        response_text = ""
        for event in events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_text += part.text

        # Response should acknowledge skills or testing capabilities
        assert len(response_text) > 0  # Should generate some response

        await runner.close()

    @pytest.mark.asyncio
    async def test_progressive_disclosure(self, agent_with_toolset):
        """Test progressive disclosure pattern with toolset."""
        runner = InMemoryRunner(
            agent=agent_with_toolset,
            app_name="test_app",
            session_service=InMemorySessionService(),
        )

        session = await runner.session_service.create_session(
            user_id="test_user", app_name="test_app"
        )

        # First, discover skills
        discovery_events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Show me available skills")],
            ),
        ):
            discovery_events.append(event)

        # Then, request specific skill content
        skill_events = []
        async for event in runner.run_async(
            user_id="test_user",
            session_id=session.id,
            new_message=types.Content(
                role="user",
                parts=[types.Part.from_text(text="Load the test-skill for me")],
            ),
        ):
            skill_events.append(event)

        # Should have loaded skill content
        skill_response = ""
        for event in skill_events:
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        skill_response += part.text

        # Response should contain skill content or acknowledge loading
        assert len(skill_response) > 0

        await runner.close()
