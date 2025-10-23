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

"""Tests for SkillsPlugin functionality."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, AsyncMock

from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.llm_request import LlmRequest
from google.adk.skills.skills_plugin import SkillsPlugin


class TestSkillsPlugin:
    """Test SkillsPlugin functionality."""

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
    def skills_plugin(self, test_skills_dir):
        """Create SkillsPlugin instance for testing."""
        return SkillsPlugin(skills_directory=test_skills_dir)

    @pytest.fixture
    def mock_agent(self):
        """Create mock LLM agent for testing."""
        agent = Mock(spec=LlmAgent)
        agent.name = "test_agent"
        return agent

    @pytest.fixture
    def mock_callback_context(self):
        """Create mock callback context for testing."""
        context = Mock(spec=CallbackContext)
        context.state = {}
        return context

    @pytest.mark.asyncio
    async def test_before_agent_callback_injects_skills_metadata(
        self, skills_plugin, mock_agent, mock_callback_context
    ):
        """Test that skills metadata is injected into agent context."""
        result = await skills_plugin.before_agent_callback(
            agent=mock_agent, callback_context=mock_callback_context
        )

        # Should not return content (no early exit)
        assert result is None

        # Should set skills availability in context
        assert mock_callback_context.state["skills_available"] is True
        assert "skills_summary" in mock_callback_context.state
        assert "test-skill" in mock_callback_context.state["skills_summary"]

    @pytest.mark.asyncio
    async def test_before_model_callback_skill_request(
        self, skills_plugin, mock_callback_context
    ):
        """Test handling of skill content requests."""
        mock_callback_context.state = {"skills_available": True}

        # Create mock LLM request with skill request
        llm_request = Mock(spec=LlmRequest)
        llm_request.contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Please load skill test-skill")],
            )
        ]

        result = await skills_plugin.before_model_callback(
            callback_context=mock_callback_context, llm_request=llm_request
        )

        # Should not return early response
        assert result is None

        # Should have added skill content to the request
        added_parts = [
            part for content in llm_request.contents for part in content.parts
        ]
        skill_parts = [
            part
            for part in added_parts
            if part.text and "SKILL: TEST-SKILL" in part.text
        ]
        assert len(skill_parts) > 0

    @pytest.mark.asyncio
    async def test_before_model_callback_file_request(
        self, skills_plugin, mock_callback_context
    ):
        """Test handling of skill file requests."""
        mock_callback_context.state = {"skills_available": True}

        # Create mock LLM request with file request
        llm_request = Mock(spec=LlmRequest)
        llm_request.contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text="Load file reference.md from skill test-skill"
                    )
                ],
            )
        ]

        result = await skills_plugin.before_model_callback(
            callback_context=mock_callback_context, llm_request=llm_request
        )

        # Should not return early response
        assert result is None

        # Should have added file content to the request
        added_parts = [
            part for content in llm_request.contents for part in content.parts
        ]
        file_parts = [
            part
            for part in added_parts
            if part.text and "FILE: test-skill/reference.md" in part.text
        ]
        assert len(file_parts) > 0

    def test_extract_request_text(self, skills_plugin):
        """Test extraction of text from LLM request."""
        llm_request = Mock(spec=LlmRequest)
        llm_request.contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="Hello"),
                    types.Part.from_text(text="World"),
                ],
            )
        ]

        text = skills_plugin._extract_request_text(llm_request)
        assert text == "hello world"

    def test_handle_skill_requests(self, skills_plugin):
        """Test detection and handling of skill requests."""
        # Test various request patterns
        test_cases = [
            "load skill test-skill",
            "use skill test-skill",
            "activate skill test-skill",
            "skill test-skill content",
        ]

        for request_text in test_cases:
            result = skills_plugin._handle_skill_requests(request_text)
            assert result is not None
            assert "test-skill" in result
            assert "Test Skill" in result["test-skill"]

    def test_handle_file_requests(self, skills_plugin):
        """Test detection and handling of file requests."""
        # Test various file request patterns
        test_cases = [
            "load file reference.md from skill test-skill",
            "skill test-skill file reference.md",
        ]

        for request_text in test_cases:
            result = skills_plugin._handle_file_requests(request_text)
            assert result is not None
            assert "test-skill/reference.md" in result
            assert "Reference content" in result["test-skill/reference.md"]

    @pytest.mark.asyncio
    async def test_handle_script_requests(self, skills_plugin):
        """Test detection and handling of script execution requests."""
        # Test script execution patterns
        test_cases = [
            "execute script test_script.py from skill test-skill",
            "run test_script.py from skill test-skill",
        ]

        for request_text in test_cases:
            result = await skills_plugin._handle_script_requests(request_text)
            assert result is not None
            assert "test-skill/test_script.py" in result
            # Should contain script output
            assert "Hello from test script!" in result["test-skill/test_script.py"]
