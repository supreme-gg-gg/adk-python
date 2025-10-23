# Skills Demo

This example demonstrates how to integrate Anthropic-style Skills with ADK agents using two different approaches.

## Skills Available

### pdf-processing
- Process and manipulate PDF documents
- Extract text, fill forms, merge/split documents
- Includes scripts for form field extraction

### data-analysis  
- Analyze datasets and create visualizations
- Statistical analysis and data quality checks
- Includes data quality checking script

## Two Integration Approaches

### 1. SkillsToolset Approach (Per-Agent Skills)

The agent explicitly uses skill tools to discover and load skills:

```python
from google.adk.skills import SkillsToolset

agent = Agent(
    # ... other config ...
    tools=[SkillsToolset(skills_directory="./skills")]
)
```

**Usage:**
- Agent calls `discover_skills()` to see available skills
- Agent calls `load_skill(skill_name)` to get full skill content
- Agent calls `load_skill_file(skill_name, file_path)` for additional files
- Agent calls `execute_skill_script(skill_name, script_name)` to run scripts

### 2. SkillsPlugin Approach (Global Skills)

Skills are automatically available through a plugin:

```python
from google.adk.skills import SkillsPlugin
from google.adk.apps.app import App

app = App(
    name="my_app",
    root_agent=agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)
```

**Usage:**
- Skills metadata is automatically injected into agent context
- Agent requests "load skill [name]" in natural language
- Agent requests "load file [path] from skill [name]" for additional files
- Agent requests "execute script [name] from skill [name]" to run scripts

## Running the Demo

### Toolset Approach
```bash
cd examples/skills_demo
adk run
```

### Plugin Approach  
```bash
cd examples/skills_demo
python run_with_plugin.py
```

## Example Interactions

### PDF Processing
- "I need to extract text from a PDF file"
- "How do I fill out a PDF form?"
- "Can you help me merge multiple PDFs?"

### Data Analysis
- "I want to analyze a CSV dataset"
- "How do I check data quality?"
- "Help me create visualizations for my data"

The agent will automatically discover relevant skills and load the appropriate content to help with these tasks.
