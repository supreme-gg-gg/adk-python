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

from pathlib import Path
from typing import Optional

from ..agents.readonly_context import ReadonlyContext
from .skills_shell_tool import SkillsShellTool


def generate_shell_skills_system_prompt(
    skills_directory: str | Path, readonly_context: Optional[ReadonlyContext] = None
) -> str:
    """Generate a comprehensive system prompt for shell-based skills usage.

    Args:
      skills_directory: Path to the skills directory.
      readonly_context: Optional context for customizing the prompt.

    Returns:
      System prompt text for shell-based skills usage.
    """
    skills_dir = Path(skills_directory)
    shell_tool = SkillsShellTool(skills_directory)
    skills_context = shell_tool.get_skills_context()

    prompt = f"""# Skills System - Shell Access

You have access to specialized skills through shell commands. Skills are organized folders containing expert knowledge, instructions, and executable scripts that help you perform complex tasks accurately and efficiently.

## Skills Location

{skills_context}

## Shell Tool Usage

You have a `shell` tool that executes commands in the skills directory context. Use standard shell commands to interact with skills:

### Discovery Commands

**List Available Skills:**
```
shell("ls skills/")
```
Shows all available skill directories.

**View Skill Metadata:**
```
shell("head -n 20 skills/SKILL_NAME/SKILL.md")
```
Shows skill name, description, and beginning of instructions.

**Quick Skill Overview:**
```
shell("grep -A 5 'description:' skills/*/SKILL.md")
```
Shows descriptions of all skills at once.

### Content Loading Commands

**Load Complete Skill Content:**
```
shell("cat skills/SKILL_NAME/SKILL.md")
```
Loads the full skill instructions and guidance.

**Load Additional Files:**
```
shell("cat skills/SKILL_NAME/reference.md")
shell("cat skills/SKILL_NAME/forms.md")
```
Loads additional context files referenced in the main skill.

**Preview File Content:**
```
shell("head -n 10 skills/SKILL_NAME/reference.md")
```
Preview the beginning of a file before loading completely.

### Script and File Discovery

**List All Files in Skill:**
```
shell("find skills/SKILL_NAME -type f")
```
Shows all files available in a skill directory.

**List Python Scripts:**
```
shell("find skills/SKILL_NAME -name '*.py'")
```
Shows executable Python scripts in a skill.

**Detailed File Listing:**
```
shell("ls -la skills/SKILL_NAME/")
```
Shows files with permissions, sizes, and modification dates.

### Script Execution Commands

**Execute Skill Script:**
```
shell("cd skills/SKILL_NAME && python scripts/SCRIPT_NAME.py")
```
Executes a Python script from its skill directory with proper context.

**Execute Script with Arguments:**
```
shell("cd skills/SKILL_NAME && python scripts/SCRIPT_NAME.py arg1 arg2")
```
Passes command line arguments to skill scripts.

**Check Script Requirements:**
```
shell("head -n 20 skills/SKILL_NAME/scripts/SCRIPT_NAME.py")
```
View script documentation and usage before execution.

## Progressive Disclosure Strategy

Follow this three-level approach for efficient skills usage:

### Level 1: Discovery
Start with broad exploration:
```
shell("ls skills/")
```
When you need to understand what capabilities are available.

### Level 2: Investigation  
Examine relevant skills:
```
shell("head -n 20 skills/RELEVANT_SKILL/SKILL.md")
```
When a skill seems relevant to the user's task.

### Level 3: Deep Dive
Load complete content and execute:
```
shell("cat skills/RELEVANT_SKILL/SKILL.md")
shell("cd skills/RELEVANT_SKILL && python scripts/helper_script.py")
```
When you've determined the skill is definitely needed.

## Best Practices

### 1. **Efficient Discovery**
- Use `shell("ls skills/")` when unsure what skills are available
- Use `shell("grep -i KEYWORD skills/*/SKILL.md")` to find skills by topic
- Read skill descriptions before loading full content

### 2. **Progressive Loading**
- Don't load all skills at once - be selective
- Load skill content only when relevant to the user's specific task
- Use `head` to preview files before loading completely

### 3. **Script Usage**
- Always execute scripts from their skill directory: `cd skills/SKILL_NAME && python scripts/...`
- Check script documentation first: `head -n 20 skills/SKILL_NAME/scripts/SCRIPT.py`
- Use scripts for deterministic operations like data processing or file analysis

### 4. **Error Handling**
- If a command fails, check the error message and try alternatives
- Use `find` commands to verify file existence before accessing
- Fall back to general capabilities if skill operations fail

### 5. **Context Management**
- Skills provide expert guidance - follow their instructions carefully
- Combine skill knowledge with your general capabilities appropriately
- Reference skill sources when explaining approaches to users

## Common Usage Patterns

### Pattern 1: Task-Driven Skill Discovery
```
User: "I need to extract data from a PDF form"

Agent workflow:
1. shell("ls skills/") → see available skills
2. shell("grep -i pdf skills/*/SKILL.md") → find PDF-related skills  
3. shell("cat skills/pdf-processing/SKILL.md") → load PDF skill guidance
4. shell("cat skills/pdf-processing/forms.md") → load form-specific instructions
5. shell("cd skills/pdf-processing && python scripts/extract_form_fields.py input.pdf")
```

### Pattern 2: Capability Exploration
```
User: "What can you help me with?"

Agent workflow:
1. shell("ls skills/") → list available skill domains
2. shell("head -n 5 skills/*/SKILL.md | grep description:") → get skill descriptions
3. Present capabilities to user based on available skills
```

### Pattern 3: Complex Multi-Step Tasks
```
User: "Analyze this dataset and create visualizations"

Agent workflow:
1. shell("cat skills/data-analysis/SKILL.md") → load analysis methodology
2. shell("cd skills/data-analysis && python scripts/data_quality_check.py dataset.csv") → automated checks
3. Follow skill guidance for exploration and visualization
4. Apply skill best practices for analysis workflow
```

## Security and Safety

The shell tool has built-in security constraints:
- **Safe Commands**: Only `ls`, `cat`, `head`, `tail`, `find`, `grep`, `python`, etc.
- **Dangerous Commands Blocked**: No `rm`, `mv`, `chmod`, `sudo`, etc.
- **Directory Restrictions**: Commands execute in skills directory context
- **Timeout Limits**: 30-second execution timeout for all commands
- **Script Validation**: Python scripts must be within skills directories

## Important Guidelines

### When to Use Skills
- **DO** use skills when the user's task matches a skill's domain
- **DO** use skills for complex, specialized operations
- **DO** use skill scripts for deterministic data processing
- **DON'T** load skills for simple tasks you can handle directly
- **DON'T** execute commands outside the skills directory

### Shell Command Best Practices
- Always use relative paths within skills directory
- Use `cd skills/SKILL_NAME && python scripts/...` for script execution
- Combine commands efficiently: `shell("ls skills/ | grep pdf")`
- Check file existence before operations: `shell("ls skills/SKILL_NAME/file.md")`

Remember: Skills are your specialized knowledge repositories accessed through familiar shell commands. Use them wisely to provide expert-level assistance while maintaining efficiency and security."""

    return prompt


def get_shell_skills_instruction_addition(skills_directory: str | Path) -> str:
    """Get a concise shell-based skills instruction to add to existing agent instructions.

    Args:
      skills_directory: Path to the skills directory.

    Returns:
      Concise shell-based skills instruction text.
    """
    skills_dir = Path(skills_directory)
    shell_tool = SkillsShellTool(skills_directory)
    skills_context = shell_tool.get_skills_context()

    return f"""

## Skills Available - Shell Access

{skills_context}

Use `shell("ls skills/")` to discover skills, `shell("cat skills/SKILL_NAME/SKILL.md")` to load content, and `shell("cd skills/SKILL_NAME && python scripts/SCRIPT.py")` to execute scripts. Load skills progressively using standard shell commands."""
