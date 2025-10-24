# Skills Demo - Shell-Based Approach

This example demonstrates how to integrate Anthropic-style Skills with ADK agents using a shell-based approach with a single, flexible shell tool.

## Skills Available

### pdf-processing
- Process and manipulate PDF documents
- Extract text, fill forms, merge/split documents
- Includes scripts for form field extraction

### data-analysis  
- Analyze datasets and create visualizations
- Statistical analysis and data quality checks
- Includes data quality checking script

## Shell-Based Skills Integration

### Single Shell Tool Approach
Instead of multiple specialized tools, agents use one `shell` tool for all skills operations:

```python
from google.adk.skills import SkillsPlugin, SkillsToolset

# Plugin approach - automatic shell tool for all agents
app = App(
    name="my_app",
    root_agent=agent,
    plugins=[SkillsPlugin(skills_directory="./skills")]
)

# Toolset approach - explicit shell tool per agent
agent = Agent(
    tools=[SkillsToolset(skills_directory="./skills")]
)
```

## Shell Commands for Skills

### Discovery
```bash
shell("ls skills/")                           # List available skills
shell("head -n 20 skills/pdf-processing/SKILL.md")  # View skill description
shell("grep -i 'data' skills/*/SKILL.md")     # Find skills by keyword
```

### Content Loading
```bash
shell("cat skills/pdf-processing/SKILL.md")   # Load full skill content
shell("cat skills/pdf-processing/forms.md")   # Load additional files
shell("find skills/pdf-processing -type f")   # List all skill files
```

### Script Execution
```bash
shell("find skills/pdf-processing -name '*.py'")                    # List scripts
shell("cd skills/pdf-processing && python scripts/extract_form_fields.py input.pdf")  # Execute script
```

## Running the Demo

### Shell-Based Approach
```bash
cd examples/skills_demo
adk run  # Uses agent.py with shell tool
```

### Plugin Approach  
```bash
cd examples/skills_demo
python run_with_plugin.py  # Uses shell-enhanced plugin
```

### System Prompt Comparison
```bash
cd examples/skills_demo
python run_system_prompt_demo.py  # Compare different prompting approaches
```

## Example Interactions

### PDF Processing
**User**: "I need to extract text from a PDF file"

**Agent**:
1. `shell("ls skills/")` → discovers pdf-processing skill
2. `shell("head -n 20 skills/pdf-processing/SKILL.md")` → reads description
3. `shell("cat skills/pdf-processing/SKILL.md")` → loads full guidance
4. Provides PDF processing help based on skill instructions

### Data Analysis
**User**: "I want to analyze a CSV dataset"

**Agent**:
1. `shell("ls skills/")` → discovers data-analysis skill
2. `shell("cat skills/data-analysis/SKILL.md")` → loads analysis guidance
3. `shell("cd skills/data-analysis && python scripts/data_quality_check.py dataset.csv")` → runs quality check
4. Provides analysis recommendations based on skill methodology

### Skill Discovery
**User**: "What can you help me with?"

**Agent**:
1. `shell("ls skills/")` → lists available skill domains
2. `shell("head -n 5 skills/*/SKILL.md | grep description:")` → gets descriptions
3. Presents capabilities organized by skill domains

## Benefits of Shell Approach

### 1. **Simplicity**
- One tool instead of six specialized tools
- Standard shell commands agents understand
- No complex tool injection logic

### 2. **Flexibility**  
- Any shell operation possible (grep, find, awk, etc.)
- Easy to combine commands: `shell("ls skills/ | grep analysis")`
- Natural file system navigation

### 3. **Familiarity**
- Standard shell paradigms
- Commands agents already understand
- Follows Unix philosophy of small, composable tools

### 4. **Security**
- Built-in command whitelisting
- Directory access restrictions
- Timeout and resource limits

### 5. **Extensibility**
- No new tools needed for new operations
- Just use appropriate shell commands
- Easy to add new skills without code changes

The shell-based approach makes skills feel like a natural extension of the agent's capabilities rather than a separate system!