# ADK Skills Redesign Plan: Generic Shell Tool Approach

## Overview

Redesign the Skills system to use a single generic `shell_tool` instead of multiple specialized skill tools. This approach is cleaner, more flexible, and leverages standard shell commands for skill operations.

## Current Architecture Issues

### Current State
- 6 specialized skill tools: `list_available_skills`, `load_skill_content`, `load_skill_file`, `execute_skill_script`, `list_skill_files`, `list_skill_scripts`
- Custom tool creation and management
- Specialized error handling for each operation
- Complex tool injection logic

### Problems
1. **Tool Proliferation**: Too many specialized tools for what are essentially file operations
2. **Complexity**: Custom tool creation and management overhead
3. **Inflexibility**: Hard to extend for new skill operations
4. **Non-Standard**: Doesn't leverage standard shell/filesystem paradigms

## Proposed Shell Tool Approach

### Core Concept
Replace specialized skill tools with a single `shell_tool` that agents can use for:
- File system navigation and reading
- Script execution
- Standard shell commands
- Skill directory operations

### Benefits
1. **Simplicity**: One tool instead of six
2. **Flexibility**: Agents can use any shell command for skill operations
3. **Familiarity**: Standard shell paradigms that agents understand
4. **Extensibility**: Easy to add new operations without creating new tools
5. **Consistency**: Uses standard file operations and command execution

## Implementation Plan

### Phase 1: Create Generic Shell Tool

#### 1.1 Create `SkillsShellTool`
**File**: `src/google/adk/skills/skills_shell_tool.py`

```python
class SkillsShellTool(BaseTool):
    """Generic shell tool for skills operations.
    
    Provides shell command execution with skills context and safety constraints.
    """
    
    def __init__(self, skills_directory: str | Path):
        super().__init__(
            name="shell",
            description="Execute shell commands for skills operations and file access"
        )
        self.skills_directory = Path(skills_directory)
    
    async def run_async(self, *, args: dict[str, Any], tool_context: ToolContext) -> str:
        command = args.get("command", "")
        # Execute shell command with skills context
        # Handle skill-specific operations
```

#### 1.2 Define Shell Commands for Skills
Create standard shell commands that agents can use:

```bash
# List available skills
ls skills/

# View skill metadata  
head -n 20 skills/pdf-processing/SKILL.md

# Load skill content (skip YAML frontmatter)
tail -n +$(grep -n "^---$" skills/pdf-processing/SKILL.md | tail -1 | cut -d: -f1) skills/pdf-processing/SKILL.md

# Load skill file
cat skills/pdf-processing/forms.md

# List skill files
find skills/pdf-processing -type f

# List skill scripts
find skills/pdf-processing -name "*.py"

# Execute skill script
cd skills/pdf-processing && python scripts/extract_form_fields.py input.pdf
```

### Phase 2: Update Skills System

#### 2.1 Simplify SkillsPlugin
**File**: `src/google/adk/skills/skills_plugin.py`

```python
class SkillsPlugin(BasePlugin):
    """Simplified plugin that only provides shell tool and skills context."""
    
    def __init__(self, skills_directory: str | Path):
        super().__init__("skills_plugin")
        self.skills_directory = Path(skills_directory)
        self.shell_tool = SkillsShellTool(skills_directory)
    
    async def before_agent_callback(self, *, agent: BaseAgent, callback_context: CallbackContext):
        # Add shell tool to agent
        agent.tools.append(self.shell_tool)
        
        # Add skills context to agent instruction
        skills_summary = self._get_skills_summary()
        agent.instruction += f"\n\nSkills available in: {self.skills_directory}\n{skills_summary}"
```

#### 2.2 Update SkillsToolset
**File**: `src/google/adk/skills/skills_toolset.py`

```python
class SkillsToolset(BaseToolset):
    """Toolset providing shell access to skills directory."""
    
    def __init__(self, skills_directory: str | Path):
        super().__init__()
        self.shell_tool = SkillsShellTool(skills_directory)
    
    async def get_tools(self, readonly_context=None) -> List[BaseTool]:
        return [self.shell_tool]
```

### Phase 3: Update System Prompt

#### 3.1 Shell-Based Skills Instructions
**File**: `src/google/adk/skills/skill_system_prompt.py`

```python
def generate_shell_skills_system_prompt(skills_directory: Path) -> str:
    """Generate system prompt for shell-based skills usage."""
    
    return f"""
# Skills System - Shell Access

You have access to specialized skills through shell commands in: {skills_directory}

## Available Operations

### Discovery
- `ls skills/` - List all available skills
- `head -n 20 skills/SKILL_NAME/SKILL.md` - View skill metadata and description

### Loading Content
- `cat skills/SKILL_NAME/SKILL.md` - Load complete skill content
- `cat skills/SKILL_NAME/reference.md` - Load additional skill files

### Script Execution  
- `cd skills/SKILL_NAME && python scripts/SCRIPT_NAME.py` - Execute skill scripts
- `find skills/SKILL_NAME -name "*.py"` - List available scripts

### File Operations
- `find skills/SKILL_NAME -type f` - List all files in a skill
- `ls -la skills/SKILL_NAME/` - Detailed file listing

## Usage Patterns

1. **Skill Discovery**: Start with `ls skills/` to see available skills
2. **Skill Investigation**: Use `head -n 20 skills/SKILL_NAME/SKILL.md` to read descriptions
3. **Content Loading**: Use `cat skills/SKILL_NAME/SKILL.md` when skill is relevant
4. **Script Execution**: Use `cd skills/SKILL_NAME && python scripts/SCRIPT.py` for automation

## Best Practices

- Always start with skill discovery: `ls skills/`
- Read skill metadata before loading full content
- Use appropriate shell commands for file operations
- Execute scripts from their skill directory for proper context
"""
```

### Phase 4: Remove Obsolete Components

#### 4.1 Files to Remove
- `src/google/adk/skills/skill_tools.py` (replaced by shell commands)
- `src/google/adk/skills/skill_code_executor.py` (shell handles execution)
- Complex tool injection logic in plugins

#### 4.2 Files to Simplify
- `src/google/adk/skills/skills_plugin.py` (much simpler)
- `src/google/adk/skills/skills_toolset.py` (just provides shell tool)
- `src/google/adk/skills/__init__.py` (fewer exports)

### Phase 5: Update Examples and Tests

#### 5.1 Update Agent Instructions
**File**: `examples/skills_demo/agent.py`

```python
agent_with_toolset = Agent(
    instruction="""
    You have access to skills through shell commands.
    
    Use `ls skills/` to discover available skills.
    Use `cat skills/SKILL_NAME/SKILL.md` to load skill content when relevant.
    Use `cd skills/SKILL_NAME && python scripts/SCRIPT.py` to execute scripts.
    
    Always explore skills directory structure before attempting operations.
    """,
    tools=[SkillsToolset(skills_directory=SKILLS_DIR)]
)
```

#### 5.2 Update Tests
- Test shell command execution for skill operations
- Test skills directory access and navigation
- Test script execution via shell commands

## Implementation Benefits

### 1. **Simplicity**
- **Before**: 6 specialized tools + complex injection logic
- **After**: 1 shell tool + simple directory access

### 2. **Flexibility** 
- **Before**: Fixed set of operations (list, load, execute)
- **After**: Any shell command for skills operations

### 3. **Familiarity**
- **Before**: Custom tool API that agents need to learn
- **After**: Standard shell commands that agents understand

### 4. **Extensibility**
- **Before**: Need to create new tools for new operations
- **After**: Just use appropriate shell commands

### 5. **Maintainability**
- **Before**: Complex tool management and injection
- **After**: Simple shell tool with directory context

## Security Considerations

### Command Restrictions
- Restrict shell commands to skills directory and subdirectories
- Whitelist safe commands: `ls`, `cat`, `head`, `tail`, `find`, `python`
- Blacklist dangerous commands: `rm`, `mv`, `chmod`, `sudo`, etc.

### Execution Context
- Set working directory to skills directory by default
- Limit script execution to skill script directories
- Maintain timeout and resource limits

## Example Usage After Redesign

### Agent Workflow
```
User: "I need help with PDF processing"

Agent: 
1. shell("ls skills/") -> sees "pdf-processing" directory
2. shell("head -n 20 skills/pdf-processing/SKILL.md") -> reads description
3. shell("cat skills/pdf-processing/SKILL.md") -> loads full content
4. shell("find skills/pdf-processing -name '*.py'") -> lists scripts
5. shell("cd skills/pdf-processing && python scripts/extract_form_fields.py input.pdf")
```

### Comparison with Current Approach
```
Current: load_skill_content("pdf-processing")
New:     shell("cat skills/pdf-processing/SKILL.md")

Current: execute_skill_script("pdf-processing", "extract_forms.py")  
New:     shell("cd skills/pdf-processing && python scripts/extract_forms.py")

Current: list_skill_files("pdf-processing")
New:     shell("find skills/pdf-processing -type f")
```

## Migration Strategy

1. **Implement SkillsShellTool** with security constraints
2. **Update SkillsPlugin** to use shell tool instead of specialized tools
3. **Update SkillsToolset** to provide shell tool
4. **Update system prompts** for shell-based operations
5. **Update examples** to demonstrate shell usage
6. **Update tests** for shell-based approach
7. **Remove obsolete** specialized tool files

This approach significantly simplifies the Skills system while making it more flexible and familiar to agents!

