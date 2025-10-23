# ADK Skills System Prompt

## Overview

I've created a comprehensive system prompt system to help agents properly understand and use Skills functionality. This addresses the critical need for agents to know how to interact with skills effectively.

## Components Created

### 1. **Comprehensive System Prompt Generator**
**File**: `src/google/adk/skills/skill_system_prompt.py`

```python
from google.adk.skills import generate_skills_system_prompt, SkillManager

skill_manager = SkillManager("./skills")
full_prompt = generate_skills_system_prompt(skill_manager)
```

**Provides**:
- Complete explanation of how skills work
- Detailed documentation of all skill tools
- Progressive disclosure best practices
- Usage patterns with concrete examples
- Error handling guidelines
- When to use skills vs. general capabilities

### 2. **Instruction Addition Helper**
```python
from google.adk.skills import get_skills_instruction_addition

# Concise addition to existing instructions
skills_addition = get_skills_instruction_addition(skill_manager)
agent.instruction += skills_addition
```

**Provides**:
- Concise skills overview
- Available skills list
- Brief tool usage instructions
- Perfect for appending to existing agent instructions

### 3. **Automatic Plugin Enhancement**
The `SkillsPlugin` now automatically enhances agent instructions:
- Detects if skills guidance is already present
- Adds concise skills instruction if missing
- Preserves existing agent personality and role

## Key Features of the System Prompt

### 🎯 **Progressive Disclosure Education**
Teaches agents the three-level approach:
1. **Discovery**: `list_available_skills()` to see what's available
2. **Loading**: `load_skill_content(skill_name)` when relevant
3. **Deep Dive**: `load_skill_file()` and `execute_skill_script()` as needed

### 🛠️ **Tool Documentation**
Each skill tool is documented with:
- Clear purpose and when to use it
- Parameter requirements and examples
- Expected outputs and behavior
- Integration with other tools

### 📋 **Best Practices**
- **Skill Selection**: Choose skills based on task relevance
- **Context Management**: Load skills progressively, not all at once
- **Script Usage**: Use scripts for deterministic operations
- **Error Handling**: Graceful fallbacks when skills fail

### 💡 **Usage Patterns**
Concrete examples for common scenarios:
- Task-driven skill discovery
- Capability exploration  
- Complex multi-step workflows
- Progressive skill loading

## Example System Prompt Output

```
# Skills System

You have access to specialized skills that extend your capabilities for specific tasks...

## Available Skills

- pdf-processing: Process and manipulate PDF documents, including form filling and data extraction
- data-analysis: Analyze datasets, create visualizations, and perform statistical analysis

## Skill Tools Available

### 1. `list_available_skills()`
- Lists all skills with their descriptions
- Use this to discover what specialized capabilities you have

### 2. `load_skill_content(skill_name)`
- Loads the complete instructions and guidance for a specific skill
- Use this when you determine a skill is relevant to the user's request

[... detailed documentation continues ...]

## Best Practices for Using Skills

### 1. **Progressive Approach**
- Start with `list_available_skills()` when unsure what capabilities you have
- Load skill content only when relevant to the user's specific request

[... best practices continue ...]
```

## Integration Examples

### Option 1: Comprehensive Prompt
```python
from google.adk.skills import SkillsPlugin, SkillManager, generate_skills_system_prompt

skill_manager = SkillManager("./skills")

agent = Agent(
    model="gemini-2.0-flash",
    name="skills_expert",
    instruction=generate_skills_system_prompt(skill_manager)
)

app = App(
    name="expert_app",
    root_agent=agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)
```

### Option 2: Enhanced Existing Instructions
```python
agent = Agent(
    model="gemini-2.0-flash",
    name="document_processor", 
    instruction="""
    You are a document processing specialist with expertise in various file formats.
    Help users with document analysis, conversion, and manipulation tasks.
    """,
)

app = App(
    name="doc_app",
    root_agent=agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)
# Plugin automatically adds skills guidance to existing instruction
```

### Option 3: Manual Enhancement
```python
from google.adk.skills import get_skills_instruction_addition, SkillManager

skill_manager = SkillManager("./skills")
skills_addition = get_skills_instruction_addition(skill_manager)

agent = Agent(
    instruction=f"""
    You are a data scientist specializing in statistical analysis.
    {skills_addition}
    
    Always validate your analysis methodology and explain your reasoning.
    """
)
```

## Testing Different Approaches

Use the provided demo to compare approaches:

```bash
cd examples/skills_demo
python run_system_prompt_demo.py
```

This demonstrates:
- Agent with comprehensive skills system prompt
- Agent with minimal prompt enhanced by plugin
- Side-by-side comparison of responses
- How prompting affects skill discovery and usage

## Customization Guidelines

### 1. **Domain-Specific Customization**
```python
def create_domain_prompt(skill_manager, domain: str):
    base_prompt = generate_skills_system_prompt(skill_manager)
    
    domain_additions = {
        "research": "\n\nPrioritize data analysis and document processing skills for research tasks.",
        "business": "\n\nFocus on document creation and data visualization for business contexts.",
        "development": "\n\nEmphasize code execution and automation skills for development work."
    }
    
    return base_prompt + domain_additions.get(domain, "")
```

### 2. **User Experience Levels**
```python
def create_user_level_prompt(skill_manager, user_level: str):
    if user_level == "beginner":
        return get_skills_instruction_addition(skill_manager)  # Concise
    else:
        return generate_skills_system_prompt(skill_manager)  # Comprehensive
```

### 3. **Task-Specific Focus**
```python
def create_task_focused_prompt(skill_manager, task_type: str):
    base = generate_skills_system_prompt(skill_manager)
    
    if task_type == "analysis":
        return base + "\n\nFor analysis tasks, always start with data-analysis skills."
    
    return base
```

## Benefits

### 🎓 **Agent Education**
- Agents understand progressive disclosure concept
- Clear guidance on when and how to use skills
- Reduces trial-and-error in skill usage

### 🔧 **Proper Tool Usage**
- Detailed documentation of each skill tool
- Examples of correct usage patterns
- Error handling and fallback strategies

### ⚡ **Efficiency**
- Agents load skills progressively, not all at once
- Selective skill usage based on task relevance
- Optimized context management

### 🎯 **Task Success**
- Higher success rates for complex tasks
- Better skill discovery and selection
- More effective use of specialized capabilities

The system prompt is essential for unlocking the full potential of the Skills system - it transforms raw capability into intelligent, efficient skill usage!
