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

"""Tests for the shell-based Skills system."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from google.adk import Agent
from google.adk.apps.app import App
from google.adk.runners import InMemoryRunner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.skills import SkillsPlugin, SkillsToolset
from google.adk.skills.skills_shell_tool import SkillsShellTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types


class TestShellBasedSkills:
    """Test the shell-based Skills system."""

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
description: A test skill for shell-based testing
---
# Test Skill

This skill provides testing capabilities through shell commands."""

            (skill_dir / "SKILL.md").write_text(skill_content)
            (skill_dir / "reference.md").write_text(
                "Reference content for shell testing"
            )

            # Create scripts directory with test script
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "test_script.py").write_text("""
print("Hello from shell-executed script!")
print("Script working directory:", __import__('os').getcwd())
""")

            yield temp_path

    @pytest.fixture
    def mock_tool_context(self):
        """Create mock tool context for testing."""
        context = Mock(spec=ToolContext)
        context.state = {}
        context._invocation_context = Mock()
        return context

    def test_skills_shell_tool_creation(self, test_skills_dir):
        """Test SkillsShellTool creation and basic properties."""
        shell_tool = SkillsShellTool(test_skills_dir)

        assert shell_tool.name == "shell"
        assert "shell commands" in shell_tool.description
        assert shell_tool.skills_directory == Path(test_skills_dir).resolve()

    def test_command_validation_safe_commands(self, test_skills_dir):
        """Test that safe commands are allowed."""
        shell_tool = SkillsShellTool(test_skills_dir)

        safe_commands = [
            "ls skills/",
            "cat skills/test-skill/SKILL.md",
            "head -n 20 skills/test-skill/SKILL.md",
            "find skills/test-skill -type f",
            "cd skills/test-skill && python scripts/test_script.py",
        ]

        for command in safe_commands:
            result = shell_tool._parse_and_validate_command(command)
            assert isinstance(result, list), f"Safe command rejected: {command}"

    def test_command_validation_dangerous_commands(self, test_skills_dir):
        """Test that dangerous commands are blocked."""
        shell_tool = SkillsShellTool(test_skills_dir)

        dangerous_commands = [
            "rm -rf skills/",
            "sudo cat /etc/passwd",
            "chmod 777 skills/",
            "mv skills/ /tmp/",
            "kill -9 $$",
        ]

        for command in dangerous_commands:
            result = shell_tool._parse_and_validate_command(command)
            assert isinstance(result, str), f"Dangerous command allowed: {command}"
            assert "not allowed" in result or "not in the allowed" in result

    @pytest.mark.asyncio
    async def test_shell_tool_ls_command(self, test_skills_dir, mock_tool_context):
        """Test shell tool execution of ls command."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "ls skills/"}, tool_context=mock_tool_context
        )

        # Should list the test skill directory
        assert "test-skill" in result

    @pytest.mark.asyncio
    async def test_shell_tool_cat_command(self, test_skills_dir, mock_tool_context):
        """Test shell tool execution of cat command."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "cat skills/test-skill/SKILL.md"},
            tool_context=mock_tool_context,
        )

        # Should return skill content
        assert "Test Skill" in result
        assert "shell commands" in result

    @pytest.mark.asyncio
    async def test_shell_tool_python_execution(
        self, test_skills_dir, mock_tool_context
    ):
        """Test shell tool execution of Python scripts."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "cd skills/test-skill && python scripts/test_script.py"},
            tool_context=mock_tool_context,
        )

        # Should execute script and return output
        assert "Hello from shell-executed script!" in result
        assert "Script working directory:" in result

    @pytest.mark.asyncio
    async def test_shell_tool_find_command(self, test_skills_dir, mock_tool_context):
        """Test shell tool execution of find command."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "find skills/test-skill -name '*.py'"},
            tool_context=mock_tool_context,
        )

        # Should find the test script
        assert "test_script.py" in result

    def test_get_skills_context(self, test_skills_dir):
        """Test skills context generation."""
        shell_tool = SkillsShellTool(test_skills_dir)

        context = shell_tool.get_skills_context()

        assert "Available skills" in context
        assert "test-skill" in context
        assert "shell-based testing" in context

    @pytest.mark.asyncio
    async def test_skills_plugin_with_shell_tool(self, test_skills_dir):
        """Test SkillsPlugin integration with shell tool."""
        from google.adk.agents.callback_context import CallbackContext

        # Create agent
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

        # Get initial state
        initial_tool_count = len(agent.tools)
        initial_instruction = agent.instruction

        # Call before_agent_callback
        await plugin.before_agent_callback(agent=agent, callback_context=mock_context)

        # Should have added shell tool
        assert len(agent.tools) > initial_tool_count

        # Should have enhanced instruction
        assert len(agent.instruction) > len(initial_instruction)
        assert "shell" in agent.instruction.lower()
        assert "skills/" in agent.instruction

        # Should have set context state
        assert mock_context.state["skills_available"] is True
        assert "skills_directory" in mock_context.state

    @pytest.mark.asyncio
    async def test_skills_toolset_with_shell_tool(self, test_skills_dir):
        """Test SkillsToolset integration with shell tool."""
        # Create agent with skills toolset
        agent = Agent(
            model="gemini-2.0-flash",
            name="shell_skills_agent",
            description="Agent with shell-based skills",
            instruction="You have access to skills through shell commands.",
            tools=[SkillsToolset(skills_directory=test_skills_dir)],
        )

        # Test that agent has shell tool
        canonical_tools = await agent.canonical_tools()
        tool_names = [tool.name for tool in canonical_tools]

        assert "shell" in tool_names

        # Find the shell tool
        shell_tool = next(tool for tool in canonical_tools if tool.name == "shell")
        assert isinstance(shell_tool, SkillsShellTool)

    @pytest.mark.asyncio
    async def test_error_handling_invalid_command(
        self, test_skills_dir, mock_tool_context
    ):
        """Test error handling for invalid commands."""
        shell_tool = SkillsShellTool(test_skills_dir)

        # Test dangerous command
        result = await shell_tool.run_async(
            args={"command": "rm -rf skills/"}, tool_context=mock_tool_context
        )

        assert "not allowed" in result

    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_file(
        self, test_skills_dir, mock_tool_context
    ):
        """Test error handling for nonexistent files."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "cat skills/nonexistent-skill/SKILL.md"},
            tool_context=mock_tool_context,
        )

        # Should return error message about file not found
        assert "failed" in result.lower() or "no such file" in result.lower()

    @pytest.mark.asyncio
    async def test_compound_command_execution(self, test_skills_dir, mock_tool_context):
        """Test execution of compound commands with &&."""
        shell_tool = SkillsShellTool(test_skills_dir)

        result = await shell_tool.run_async(
            args={"command": "cd skills/test-skill && ls"},
            tool_context=mock_tool_context,
        )

        # Should show contents of test-skill directory
        assert "SKILL.md" in result
        assert "scripts" in result

