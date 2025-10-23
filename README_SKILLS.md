# ADK Skills Integration

This implementation adds Anthropic-style Skills functionality to ADK, providing agents with the ability to dynamically load specialized knowledge and capabilities.

## Overview

Skills are structured folders containing instructions, scripts, and resources that agents can load progressively to improve performance on specialized tasks. This implementation provides two integration approaches while maintaining ADK's code-first philosophy.

## Features

### Progressive Disclosure
- **Level 1**: Skill metadata (name, description) loaded at startup
- **Level 2**: Full skill content loaded when relevant to tasks
- **Level 3**: Additional files and scripts loaded as needed

### Two Integration Approaches

#### 1. SkillsPlugin (Recommended)
Global skills available to all agents through plugin callbacks:
```python
from google.adk.skills import SkillsPlugin
from google.adk.apps.app import App

app = App(
    name="my_app",
    root_agent=my_agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)
```

#### 2. SkillsToolset
Per-agent skills through explicit tool calls:
```python
from google.adk.skills import SkillsToolset

agent = Agent(
    # ... other config ...
    tools=[SkillsToolset(skills_directory="./skills")]
)
```

## Skill Structure

Each skill is a directory with a `SKILL.md` file:

```
skills/
├── pdf-processing/
│   ├── SKILL.md          # Main skill file with YAML frontmatter
│   ├── forms.md          # Additional context files
│   ├── reference.md
│   └── scripts/          # Python scripts for execution
│       └── extract_form_fields.py
└── data-analysis/
    ├── SKILL.md
    └── scripts/
        └── data_quality_check.py
```

### SKILL.md Format
```yaml
---
name: skill-name
description: Description of what the skill does and when to use it
license: Optional license information
---

# Skill Content

Markdown instructions and examples for the skill.
```

## Usage Examples

### With SkillsPlugin
Agents can request skills naturally:
- "Load skill pdf-processing"
- "Load file forms.md from skill pdf-processing"  
- "Execute script extract_form_fields.py from skill pdf-processing"

### With SkillsToolset
Agents use explicit tools:
- `discover_skills()` - List available skills
- `load_skill(skill_name)` - Load full skill content
- `load_skill_file(skill_name, file_path)` - Load specific files
- `execute_skill_script(skill_name, script_name)` - Run scripts

## Implementation Details

### Core Components

- **Skill**: Represents a skill with metadata and content
- **SkillLoader**: Discovers and parses skill directories  
- **SkillManager**: Manages loaded skills and progressive disclosure
- **SkillsPlugin**: Plugin providing global skills access
- **SkillsToolset**: Toolset providing per-agent skills access

### Security Considerations

- Scripts execute in subprocess with timeout limits
- Only Python scripts are supported
- Scripts run in their skill directory context
- No network access restrictions (implement as needed)

## Dependencies

Skills functionality requires:
- `pyyaml` for YAML frontmatter parsing
- `pydantic` for data models (included with ADK)

## Examples

See `examples/skills_demo/` for complete working examples including:
- PDF processing skill with form extraction
- Data analysis skill with quality checking
- Agent configurations for both approaches
- Interactive demo scripts

## Testing

Comprehensive test suite covers:
- Skill loading and parsing
- Progressive disclosure mechanisms
- Plugin and toolset integrations
- Error handling and edge cases
- End-to-end agent interactions

Run tests with:
```bash
pytest tests/skills/
```

## Architecture Benefits

- **Zero Core Changes**: Uses existing ADK extension points
- **Progressive Loading**: Efficient context management
- **Flexible Integration**: Choose plugin or toolset approach
- **Code-First**: Maintains ADK's development philosophy
- **Extensible**: Easy to add new skill types and capabilities
