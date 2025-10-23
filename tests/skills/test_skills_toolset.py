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

"""Tests for SkillsToolset functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from google.adk.skills.skills_toolset import SkillsToolset
from google.adk.tools.tool_context import ToolContext


class TestSkillsToolset:
    """Test SkillsToolset functionality."""

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

This is test skill content with instructions."""

            (skill_dir / "SKILL.md").write_text(skill_content)
            (skill_dir / "reference.md").write_text("Reference content for test skill")

            # Create scripts directory
            scripts_dir = skill_dir / "scripts"
            scripts_dir.mkdir()
            (scripts_dir / "test_script.py").write_text("""
import sys
print("Hello from test script!")
print(f"Arguments: {sys.argv[1:]}")
""")

            yield temp_path

    @pytest.fixture
    def skills_toolset(self, test_skills_dir):
        """Create SkillsToolset instance for testing."""
        return SkillsToolset(skills_directory=test_skills_dir)

    @pytest.fixture
    def mock_tool_context(self):
        """Create mock tool context for testing."""
        context = Mock(spec=ToolContext)
        context.state = {}
        return context

    @pytest.mark.asyncio
    async def test_get_tools(self, skills_toolset):
        """Test that toolset provides expected tools."""
        tools = await skills_toolset.get_tools()

        # Should provide all expected skill tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "discover_skills",
            "load_skill",
            "load_skill_file",
            "execute_skill_script",
            "list_skill_files",
            "list_skill_scripts",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    @pytest.mark.asyncio
    async def test_discover_skills(self, skills_toolset, mock_tool_context):
        """Test skills discovery functionality."""
        result = await skills_toolset.discover_skills(mock_tool_context)

        # Should return formatted skills summary
        assert "Available Skills:" in result
        assert "test-skill" in result
        assert "A test skill for unit testing" in result

        # Should store available skills in context
        assert "available_skills" in mock_tool_context.state
        assert "test-skill" in mock_tool_context.state["available_skills"]

    @pytest.mark.asyncio
    async def test_load_skill(self, skills_toolset, mock_tool_context):
        """Test skill loading functionality."""
        result = await skills_toolset.load_skill("test-skill", mock_tool_context)

        # Should return skill content
        assert "# Skill: test-skill" in result
        assert "Test Skill" in result
        assert "test skill content" in result

        # Should store loaded skill in context
        assert "loaded_skills" in mock_tool_context.state
        assert "test-skill" in mock_tool_context.state["loaded_skills"]

    @pytest.mark.asyncio
    async def test_load_skill_file(self, skills_toolset, mock_tool_context):
        """Test skill file loading functionality."""
        result = await skills_toolset.load_skill_file(
            "test-skill", "reference.md", mock_tool_context
        )

        # Should return file content
        assert "# File: test-skill/reference.md" in result
        assert "Reference content for test skill" in result

        # Should store loaded file in context
        assert "loaded_skill_files" in mock_tool_context.state
        assert (
            "test-skill/reference.md" in mock_tool_context.state["loaded_skill_files"]
        )

    @pytest.mark.asyncio
    async def test_execute_skill_script(self, skills_toolset, mock_tool_context):
        """Test skill script execution functionality."""
        result = await skills_toolset.execute_skill_script(
            "test-skill", "test_script.py", mock_tool_context
        )

        # Should return script output
        assert "# Script Output: test-skill/test_script.py" in result
        assert "Hello from test script!" in result

        # Should store executed script in context
        assert "executed_scripts" in mock_tool_context.state
        assert (
            "test-skill/test_script.py" in mock_tool_context.state["executed_scripts"]
        )

    @pytest.mark.asyncio
    async def test_execute_skill_script_with_args(
        self, skills_toolset, mock_tool_context
    ):
        """Test skill script execution with arguments."""
        result = await skills_toolset.execute_skill_script(
            "test-skill",
            "test_script.py",
            mock_tool_context,
            script_args=["arg1", "arg2"],
        )

        # Should pass arguments to script
        assert "Arguments: ['arg1', 'arg2']" in result

    @pytest.mark.asyncio
    async def test_list_skill_files(self, skills_toolset, mock_tool_context):
        """Test listing skill files functionality."""
        result = await skills_toolset.list_skill_files("test-skill", mock_tool_context)

        # Should list available files
        assert "Available files in skill 'test-skill':" in result
        assert "reference.md" in result
        assert "scripts/test_script.py" in result

    @pytest.mark.asyncio
    async def test_list_skill_scripts(self, skills_toolset, mock_tool_context):
        """Test listing skill scripts functionality."""
        result = await skills_toolset.list_skill_scripts(
            "test-skill", mock_tool_context
        )

        # Should list available scripts
        assert "Available scripts in skill 'test-skill':" in result
        assert "scripts/test_script.py" in result

    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_skill(
        self, skills_toolset, mock_tool_context
    ):
        """Test error handling for nonexistent skills."""
        result = await skills_toolset.load_skill("nonexistent-skill", mock_tool_context)

        # Should return error message
        assert "Failed to load skill 'nonexistent-skill'" in result

    @pytest.mark.asyncio
    async def test_error_handling_nonexistent_file(
        self, skills_toolset, mock_tool_context
    ):
        """Test error handling for nonexistent files."""
        result = await skills_toolset.load_skill_file(
            "test-skill", "nonexistent.md", mock_tool_context
        )

        # Should return error message
        assert "Failed to load file 'nonexistent.md'" in result
