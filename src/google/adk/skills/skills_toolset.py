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

from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Optional

try:
    from typing_extensions import override
except ImportError:
    from typing import override

from ..agents.readonly_context import ReadonlyContext
from ..tools.base_tool import BaseTool
from ..tools.base_toolset import BaseToolset
from ..tools.function_tool import FunctionTool
from .skill_tools import create_skill_tools

logger = logging.getLogger("google_adk." + __name__)


class SkillsToolset(BaseToolset):
    """Toolset that provides Anthropic-style Skills functionality through tools.

    This toolset implements skills as a set of tools that agents can call to:
    1. Discover available skills
    2. Load skill content progressively
    3. Load specific skill files
    4. Execute skill scripts

    This approach provides more granular control over skill access and integrates
    naturally with ADK's existing tool system.
    """

    def __init__(self, skills_directory: str | Path):
        """Initialize the skills toolset.

        Args:
          skills_directory: Path to directory containing skill folders.
        """
        super().__init__()
        self.skills_directory = Path(skills_directory)

        # Create skill tools
        self.skill_functions = create_skill_tools(skills_directory)

    @override
    async def get_tools(
        self, readonly_context: Optional[ReadonlyContext] = None
    ) -> List[BaseTool]:
        """Get all skill-related tools.

        Returns:
          List of skill management tools.
        """
        return [FunctionTool(func=func) for func in self.skill_functions]
