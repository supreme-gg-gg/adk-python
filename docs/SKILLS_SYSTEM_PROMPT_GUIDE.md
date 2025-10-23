# Skills System Prompt Guide

This guide explains how to create effective system prompts for agents using ADK Skills functionality.

## Overview

The Skills system provides comprehensive prompting capabilities to help agents understand and properly use available skills. There are two main approaches:

1. **Comprehensive System Prompt**: Use `generate_skills_system_prompt()` for detailed guidance
2. **Instruction Addition**: Use `get_skills_instruction_addition()` to enhance existing prompts

## Comprehensive System Prompt

### Usage
```python
from google.adk.skills import SkillManager, generate_skills_system_prompt

skill_manager = SkillManager("./skills")
system_prompt = generate_skills_system_prompt(skill_manager)

agent = Agent(
    model="gemini-2.0-flash",
    name="skills_expert",
    instruction=system_prompt
)
```

### What It Provides
- Complete explanation of how skills work
- Detailed tool documentation with examples
- Progressive disclosure best practices
- Usage patterns and error handling guidance
- Specific examples of skill workflows

### When to Use
- New agents that need comprehensive skills understanding
- Complex multi-skill applications
- Training or demonstration scenarios
- When agents need detailed guidance on skill usage

## Instruction Addition

### Usage
```python
from google.adk.skills import SkillManager, get_skills_instruction_addition

skill_manager = SkillManager("./skills")
skills_addition = get_skills_instruction_addition(skill_manager)

agent = Agent(
    instruction=f"""
    You are a helpful assistant specialized in document processing.
    {skills_addition}
    """
)
```

### What It Provides
- Concise list of available skills
- Brief tool usage instructions
- Can be appended to existing instructions

### When to Use
- Agents with existing specialized instructions
- When you want to preserve existing agent personality/role
- Lightweight skills integration
- Production agents where brevity is important

## Automatic Enhancement via Plugin

The `SkillsPlugin` automatically enhances agent instructions:

```python
app = App(
    name="my_app",
    root_agent=agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)
# Plugin automatically adds skills guidance to agent.instruction
```

## Key Components of Skills Prompts

### 1. Progressive Disclosure Education
Teaches agents the three-level approach:
- **Level 1**: Skill metadata and descriptions
- **Level 2**: Full skill content and instructions  
- **Level 3**: Additional files and script execution

### 2. Tool Documentation
Explains each skill tool with:
- Purpose and when to use it
- Parameter requirements
- Expected outputs
- Usage patterns

### 3. Best Practices
- When to load skills vs. handle tasks directly
- How to combine skill knowledge with general capabilities
- Error handling and fallback strategies
- Efficient context management

### 4. Usage Patterns
Provides concrete examples:
- Task-driven skill discovery
- Capability exploration
- Complex multi-step workflows
- Progressive skill loading

## Example Usage Patterns in Prompts

### Pattern 1: Task-Driven Discovery
```
User asks about PDF processing:
1. Call list_available_skills() to check capabilities
2. Call load_skill_content("pdf-processing") for detailed guidance
3. Follow skill instructions for the specific task
```

### Pattern 2: Capability Exploration
```
User asks "What can you do?":
1. Call list_available_skills() to see specialized capabilities
2. Present skills with brief descriptions
3. Load detailed content when user shows interest
```

### Pattern 3: Complex Workflows
```
Multi-step data analysis task:
1. Load data-analysis skill for methodology
2. Use skill scripts for automated processing
3. Follow skill visualization guidance
4. Apply skill reporting templates
```

## Customization Options

### Context-Aware Prompts
```python
def custom_skills_prompt(skill_manager, user_context):
    base_prompt = generate_skills_system_prompt(skill_manager)
    
    if user_context.get("domain") == "finance":
        return base_prompt + "\n\nFocus on financial analysis skills for this user."
    
    return base_prompt
```

### Domain-Specific Additions
```python
def add_domain_context(skill_manager, domain: str):
    skills_addition = get_skills_instruction_addition(skill_manager)
    
    domain_guidance = {
        "research": "Prioritize data analysis and document processing skills.",
        "development": "Focus on code execution and automation skills.",
        "business": "Emphasize document creation and data visualization skills."
    }
    
    return skills_addition + f"\n\n{domain_guidance.get(domain, '')}"
```

## Testing System Prompts

Use the provided demo script to test different prompt approaches:

```bash
cd examples/skills_demo
python run_system_prompt_demo.py
```

This will show how different prompting strategies affect agent behavior with skills.

## Best Practices

### 1. **Match Prompt to Use Case**
- Comprehensive prompts for complex skill usage
- Concise additions for specialized agents
- Let plugin handle basic enhancement automatically

### 2. **Maintain Agent Personality**
- Use instruction additions to preserve existing agent character
- Integrate skills guidance naturally with agent role
- Don't override important domain-specific instructions

### 3. **Progressive Enhancement**
- Start with basic skills awareness
- Add detailed guidance for complex use cases
- Customize based on user feedback and usage patterns

### 4. **Monitor and Iterate**
- Test different prompt approaches
- Monitor how agents use skills in practice
- Refine prompts based on actual usage patterns
- Collect user feedback on skill discovery and usage

The system prompt is crucial for effective skills usage - it teaches agents not just what tools are available, but how to use them wisely and efficiently!
