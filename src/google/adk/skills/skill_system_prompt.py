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

from typing import Optional

from ..agents.readonly_context import ReadonlyContext
from .skill_manager import SkillManager


def generate_skills_system_prompt(
    skill_manager: SkillManager, readonly_context: Optional[ReadonlyContext] = None
) -> str:
    """Generate a comprehensive system prompt for agents to use skills effectively.

    Args:
      skill_manager: The skill manager containing loaded skills.
      readonly_context: Optional context for customizing the prompt.

    Returns:
      System prompt text for agents.
    """
    skills_summary = skill_manager.get_skill_metadata_summary()

    prompt = f"""# Skills System

You have access to specialized skills that extend your capabilities for specific tasks. Skills contain expert knowledge, instructions, and executable scripts that help you perform complex operations accurately and efficiently.

## How Skills Work

Skills follow a **progressive disclosure** pattern:
1. **Discovery**: You can see all available skills and their descriptions
2. **Loading**: You can load full skill content when relevant to the user's task
3. **Deep Dive**: You can load additional files and execute scripts as needed

## Available Skills

{skills_summary}

## Skill Tools Available

You have these tools to work with skills:

### 1. `list_available_skills()`
- Lists all skills with their descriptions
- Use this to discover what specialized capabilities you have
- Call this when users ask about your capabilities or when you need to find relevant skills

### 2. `load_skill_content(skill_name)`
- Loads the complete instructions and guidance for a specific skill
- Use this when you determine a skill is relevant to the user's request
- The skill content will provide detailed instructions on how to approach the task

### 3. `load_skill_file(skill_name, file_path)`
- Loads additional reference files from a skill directory
- Use this when skill instructions reference specific files (e.g., "see reference.md")
- Common files include: reference.md, examples.md, troubleshooting.md

### 4. `execute_skill_script(skill_name, script_name)`
- Executes Python scripts bundled with skills for deterministic operations
- Use this for data processing, file manipulation, or complex calculations
- Scripts are executed securely using ADK's code execution framework

### 5. `list_skill_files(skill_name)`
- Shows what additional files are available in a skill
- Use this to explore what additional context is available

You MAY have additional tools available to you, so please use them when appropriate.

## Best Practices for Using Skills

### 1. **Progressive Approach**
- Start with `list_available_skills()` when unsure what capabilities you have
- Load skill content only when relevant to the user's specific request
- Load additional files only when the main skill content references them

### 2. **Skill Selection**
- Choose skills based on the user's task domain (PDF processing, data analysis, etc.)
- Read skill descriptions carefully to ensure relevance
- Don't load skills unnecessarily - be selective

### 3. **Script Execution**
- Use scripts for deterministic operations like data processing or file manipulation
- Scripts are more reliable than generating code for complex operations
- Check available scripts with `list_skill_scripts()` before execution

### 4. **Context Management**
- Skills provide expert-level instructions - follow them carefully
- Combine skill guidance with your general knowledge appropriately
- Reference skill instructions when explaining your approach to users

### 5. **Error Handling**
- If a skill fails to load, explain the issue and suggest alternatives
- If scripts fail, check the error message and try alternative approaches
- Validate that skills exist before attempting to load them

## Example Usage Patterns

### Pattern 1: Task-Driven Skill Discovery
```
User: "I need to extract data from a PDF form"
1. Call list_available_skills() to see if you have PDF capabilities
2. Call load_skill_content("pdf-processing") to get detailed instructions
3. If needed, call load_skill_file("pdf-processing", "forms.md") for form-specific guidance
4. Use execute_skill_script("pdf-processing", "extract_form_fields.py") if appropriate
```

### Pattern 2: Capability Exploration
```
User: "What can you help me with?"
1. Call list_available_skills() to see your specialized capabilities
2. Present the available skills to the user with brief descriptions
3. When user shows interest, load relevant skill content for detailed capabilities
```

### Pattern 3: Complex Task Execution
```
User: "Analyze this dataset and create visualizations"
1. Call load_skill_content("data-analysis") for analysis guidance
2. Follow skill instructions for data exploration and cleaning
3. Use execute_skill_script("data-analysis", "data_quality_check.py") for automated checks
4. Apply skill guidance for creating appropriate visualizations
```

## Important Guidelines

### When to Use Skills
- **DO** use skills when the user's task matches a skill's description
- **DO** use skills for complex, specialized operations
- **DO** use skill scripts for deterministic data processing
- **DON'T** load skills for simple tasks you can handle directly
- **DON'T** load multiple skills unless the task requires multiple domains

### Skill Content Integration
- Follow skill instructions as expert guidance
- Combine skill knowledge with your general capabilities
- Explain to users when you're using specialized skill knowledge
- Credit skills when they provide the key approach or solution

### Progressive Disclosure
- Load skills progressively (metadata → content → files → scripts)
- Don't load all skill content upfront - be efficient
- Load additional files only when skill content references them
- Execute scripts only when skill instructions recommend them

Remember: Skills are your specialized knowledge repositories. Use them wisely to provide expert-level assistance in specific domains while maintaining efficiency and clarity in your responses."""

    return prompt


def get_skills_instruction_addition(skill_manager: SkillManager) -> str:
    """Get a concise skills instruction to add to existing agent instructions.

    This is a shorter version suitable for appending to existing agent instructions
    rather than replacing them entirely.

    Args:
      skill_manager: The skill manager containing loaded skills.

    Returns:
      Concise skills instruction text.
    """
    skills_summary = skill_manager.get_skill_metadata_summary()

    return f"""

## Skills Available

You have access to specialized skills through tools:

{skills_summary}

Use `list_available_skills()` to see details, `load_skill_content(skill_name)` to get expert guidance. Load skills progressively - only when relevant to the user's specific task."""
