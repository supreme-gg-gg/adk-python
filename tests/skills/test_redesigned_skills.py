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

"""Tests for the redesigned Skills system using tools instead of regex."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from google.genai import types
from google.adk import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.skills import SkillsPlugin, SkillsToolset
from google.adk.skills.skill_tools import create_skill_tools
from google.adk.tools.tool_context import ToolContext


class TestRedesignedSkills:
    """Test the redesigned Skills system."""

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
description: A test skill for unit testing
---
# Test Skill

This is test skill content with instructions for testing."""

            (skill_dir / "SKILL.md").write_text(skill_content)
            (skill_dir / "reference.md").write_text("Reference content for test skill")

            # Create scripts directory with a simple test script
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "test_script.py").write_text("""
print("Hello from test script!")
print("Script executed successfully")
""")

            yield temp_path

    @pytest.fixture
    def mock_tool_context(self):
        """Create mock tool context for testing."""
        context = Mock(spec=ToolContext)
        context.state = {}
        # Mock the invocation context
        context.invocation_context = Mock()
        return context

    def test_create_skill_tools(self, test_skills_dir):
        """Test that skill tools are created properly."""
        tools = create_skill_tools(test_skills_dir)

        # Should create all expected tools
        tool_names = [tool.__name__ for tool in tools]
        expected_tools = [
            "list_available_skills",
            "load_skill_content",
            "load_skill_file",
            "execute_skill_script",
            "list_skill_files",
            "list_skill_scripts",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_list_available_skills_tool(self, test_skills_dir, mock_tool_context):
        """Test the list_available_skills tool."""
        tools = create_skill_tools(test_skills_dir)
        list_skills_tool = next(
            tool for tool in tools if tool.__name__ == "list_available_skills"
        )

        result = await list_skills_tool(mock_tool_context)

        # Should return skills summary
        assert "Available Skills:" in result
        assert "test-skill" in result
        assert "A test skill for unit testing" in result

        # Should store available skills in context
        assert "available_skills" in mock_tool_context.state
        assert "test-skill" in mock_tool_context.state["available_skills"]

    @pytest.mark.asyncio
    async def test_load_skill_content_tool(self, test_skills_dir, mock_tool_context):
        """Test the load_skill_content tool."""
        tools = create_skill_tools(test_skills_dir)
        load_skill_tool = next(
            tool for tool in tools if tool.__name__ == "load_skill_content"
        )

        result = await load_skill_tool("test-skill", mock_tool_context)

        # Should return skill content
        assert "# Skill: test-skill" in result
        assert "Test Skill" in result
        assert "test skill content" in result

        # Should store loaded skill in context
        assert "loaded_skills" in mock_tool_context.state
        assert "test-skill" in mock_tool_context.state["loaded_skills"]

    @pytest.mark.asyncio
    async def test_load_skill_file_tool(self, test_skills_dir, mock_tool_context):
        """Test the load_skill_file tool."""
        tools = create_skill_tools(test_skills_dir)
        load_file_tool = next(
            tool for tool in tools if tool.__name__ == "load_skill_file"
        )

        result = await load_file_tool("test-skill", "reference.md", mock_tool_context)

        # Should return file content
        assert "# File: test-skill/reference.md" in result
        assert "Reference content for test skill" in result

        # Should store loaded file in context
        assert "loaded_skill_files" in mock_tool_context.state
        assert (
            "test-skill/reference.md" in mock_tool_context.state["loaded_skill_files"]
        )

    @pytest.mark.asyncio
    async def test_skills_plugin_adds_tools(self, test_skills_dir):
        """Test that SkillsPlugin automatically adds tools to agents."""
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.agents.llm_agent import LlmAgent

        # Create a simple agent
        agent = Agent(
            model="gemini-2.0-flash",
            name="test_agent",
            description="Test agent",
            instruction="You are a test agent",
        )

        # Create plugin
        plugin = SkillsPlugin(skills_directory=test_skills_dir)

        # Mock callback context
        mock_context = Mock(spec=CallbackContext)
        mock_context.state = {}

        # Get initial tool count
        initial_tool_count = len(agent.tools)

        # Call before_agent_callback
        await plugin.before_agent_callback(agent=agent, callback_context=mock_context)

        # Should have added skill tools
        assert len(agent.tools) > initial_tool_count
        assert mock_context.state["skills_available"] is True
        assert "skills_summary" in mock_context.state

    @pytest.mark.asyncio
    async def test_skills_toolset_integration(self, test_skills_dir):
        """Test SkillsToolset integration with agents."""
        agent = Agent(
            model="gemini-2.0-flash",
            name="skills_agent",
            description="Agent with skills toolset",
            instruction="You have access to skills through tools.",
            tools=[SkillsToolset(skills_directory=test_skills_dir)],
        )

        runner = InMemoryRunner(
            agent=agent, app_name="test_app", session_service=InMemorySessionService()
        )

        session = await runner.session_service.create_session(
            user_id="test_user", app_name="test_app"
        )

        # Test that agent has skill tools
        canonical_tools = await agent.canonical_tools()
        tool_names = [tool.name for tool in canonical_tools]

        # Should include skill management tools
        skill_tool_names = [
            "list_available_skills",
            "load_skill_content",
            "load_skill_file",
            "execute_skill_script",
            "list_skill_files",
            "list_skill_scripts",
        ]

        for skill_tool_name in skill_tool_names:
            assert skill_tool_name in tool_names

        await runner.close()

    def test_error_handling_nonexistent_skill(self, test_skills_dir, mock_tool_context):
        """Test error handling for nonexistent skills."""
        tools = create_skill_tools(test_skills_dir)
        load_skill_tool = next(
            tool for tool in tools if tool.__name__ == "load_skill_content"
        )

        # This should be an async test, but we'll test the error path
        import asyncio

        async def test_async():
            result = await load_skill_tool("nonexistent-skill", mock_tool_context)
            # Should return error message
            assert "Failed to load skill 'nonexistent-skill'" in result

        asyncio.run(test_async())
