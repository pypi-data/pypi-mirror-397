# Debate System Usage Guide

A practical guide to using the debate system for multi-perspective analysis in Sutra.

---

## Quick Start

The debate system provides two complementary templates:

1. **Debate Program** (`get_prompt_program("debate")`) - Executable pseudo-code template
2. **Debate Organ** (`get_organ("debate_council")`) - High-level orchestration pattern

---

## Method 1: Using the Debate Program Template

### Retrieving the Template

```python
from context_engineering_mcp.server import get_prompt_program

debate_program = get_prompt_program("debate")
print(debate_program)
```

### What You Get

A pseudo-code template showing the execution flow:

```javascript
function run_multi_perspective_debate(
    question,
    perspectives = ["Optimistic", "Skeptical", "Pragmatic", "Ethical"],
    rounds = 2
) {
  // Phase 1: Frame the debate
  framing = LLM(frame_debate_question(question, perspectives));

  // Phase 2: Generate initial perspectives
  initial_perspectives = {};
  for (perspective of perspectives) {
    initial_perspectives[perspective] = LLM(generate_perspective(...));
  }

  // Phase 3: Conduct debate rounds
  debate_history = [initial_perspectives];
  for (round = 1; round <= rounds; round++) {
    round_results = LLM(conduct_debate_round(...));
    debate_history.push(round_results);
  }

  // Phase 4: Synthesize all perspectives
  synthesis = LLM(synthesize_debate(...));

  return { ... };
}
```

### How to Use It

**Step 1: Choose your question**
```
"Should we invest in renewable energy infrastructure?"
```

**Step 2: Apply the program structure to your LLM prompt**

```
I need you to analyze this question using a multi-perspective debate approach:

Question: "Should we invest in renewable energy infrastructure?"

Follow this process:

PHASE 1: MODERATOR - Frame the Debate
As the Moderator, please:
1. Clarify the core question and any ambiguities
2. Identify key dimensions of the debate
3. Establish criteria for evaluating different viewpoints
4. Set the scope and constraints for the discussion

[Wait for moderator response]

PHASE 2: GENERATE PERSPECTIVES
Now, analyze from each perspective:

OPTIMISTIC Perspective:
1. State your core position on this question
2. Provide 2-3 key arguments supporting your position
3. Identify assumptions underlying your perspective
4. Acknowledge potential limitations or counterarguments

SKEPTICAL Perspective:
[Same structure]

PRAGMATIC Perspective:
[Same structure]

ETHICAL Perspective:
[Same structure]

[Wait for all perspectives]

PHASE 3: DEBATE ROUND 1
For each perspective, respond to the strongest counterargument from other perspectives:
1. Respond to the strongest counterargument
2. Refine or strengthen your position
3. Find areas of agreement or common ground
4. Raise new considerations

[Wait for round 1]

PHASE 3: DEBATE ROUND 2
[Same structure for round 2]

PHASE 4: SYNTHESIS
Synthesize the multi-perspective debate:
1. Summary of each major perspective and its key arguments
2. Areas of consensus or common ground identified
3. Irreconcilable differences and why they persist
4. Nuanced conclusion that acknowledges complexity
5. Recommendations or implications based on the full discussion
```

### Customizing Perspectives

You can adapt the perspectives to your domain:

**Scientific Debate:**
```javascript
perspectives = ["Theoretical", "Experimental", "Applied", "Critical"]
```

**Business Decision:**
```javascript
perspectives = ["Financial", "Strategic", "Operational", "Risk_Management"]
```

**Ethical Dilemma:**
```javascript
perspectives = ["Utilitarian", "Deontological", "Virtue_Ethics", "Care_Ethics"]
```

### Adjusting Rounds

- **1 round**: Quick initial positions without refinement
- **2 rounds** (default): Balanced - initial + one refinement
- **3+ rounds**: Deep exploration for complex issues

---

## Method 2: Using the Debate Organ Template

### Retrieving the Template

```python
from context_engineering_mcp.server import get_organ

debate_organ = get_organ("debate_council")
print(debate_organ)
```

### What You Get

A protocol shell describing the full orchestration:

```
/organ.debate_council{
    intent="Generate balanced analysis through multi-perspective debate",

    input={
        question="<question_or_topic>",
        perspectives=["Optimistic", "Skeptical", "Pragmatic", "Ethical"],
        rounds=2
    },

    architecture={
        pattern="moderator → perspectives → debate_rounds → synthesis",
        components=[...]
    },

    process=[
        /phase.moderator{...},
        /phase.generate_perspectives{...},
        /phase.debate_rounds{...},
        /phase.synthesis{...}
    ],

    output={
        framing="Debate framing and context",
        perspectives="All perspective positions",
        debate_rounds="Full debate history",
        synthesis="Integrated multi-perspective conclusion",
        ...
    }
}
```

### How to Use It

**Step 1: Understand the architecture**

The organ template shows you the components:
- **Moderator Cell**: Frames the question
- **Perspective Cells**: Multiple viewpoints (default: 4)
- **Debate Rounds**: Iterative refinement
- **Synthesis Cell**: Final integration

**Step 2: Apply the process phases**

Each phase in the `process` array describes what should happen:

```python
# Phase 1: Moderator
"""
Role: Frame the debate
Actions:
- Clarify the core question and any ambiguities
- Identify key dimensions of debate
- Establish evaluation criteria
- Set scope and constraints
Output: framing_context
"""

# Phase 2: Generate Perspectives (for each perspective)
"""
Role: Generate initial positions
Actions:
- State core position on the question
- Provide 2-3 key supporting arguments
- Identify underlying assumptions
- Acknowledge limitations or counterarguments
Output: initial_perspectives[]
"""

# Phase 3: Debate Rounds (iterate for each round)
"""
Role: Conduct multi-round debate
Actions:
- Each perspective responds to strongest counterarguments
- Refine or strengthen position based on discussion
- Find areas of agreement or common ground
- Raise new considerations not yet addressed
Output: debate_history[]
"""

# Phase 4: Synthesis
"""
Role: Synthesize all perspectives
Actions:
- Summarize each major perspective and key arguments
- Identify areas of consensus or common ground
- Acknowledge irreconcilable differences and why
- Provide nuanced conclusion acknowledging complexity
- Generate recommendations or implications
Output: final_synthesis
"""
```

**Step 3: Structure your prompt based on the organ**

```
I need you to act as a debate organ orchestrator.

INPUT:
Question: "Should we adopt AI-assisted coding tools in our development workflow?"
Perspectives: ["Developer_Experience", "Code_Quality", "Security_Risk", "Business_Value"]
Rounds: 2

ARCHITECTURE:
You will coordinate 4 perspective cells through 2 rounds of debate, then synthesize.

PROCESS:

[PHASE 1: MODERATOR]
Role: Frame the debate
Output: Framing context for the question

[PHASE 2: GENERATE PERSPECTIVES]
For each perspective (Developer_Experience, Code_Quality, Security_Risk, Business_Value):
- State core position
- Provide 2-3 key arguments
- Identify assumptions
- Acknowledge limitations
Output: Initial positions for all 4 perspectives

[PHASE 3: DEBATE ROUNDS - Round 1]
Each perspective responds to counterarguments and refines position
Output: Refined positions after round 1

[PHASE 3: DEBATE ROUNDS - Round 2]
Each perspective continues refinement
Output: Refined positions after round 2

[PHASE 4: SYNTHESIS]
Integrate all perspectives into coherent conclusion
Output: Final synthesis with recommendations

Please execute this debate organ process.
```

---

## Practical Examples

### Example 1: Policy Decision

**Question**: "Should we implement a 4-day work week?"

**Perspectives**: ["Employee_Wellbeing", "Productivity", "Competitive_Advantage", "Implementation_Cost"]

**Process**:
1. Moderator frames the question with key dimensions (work-life balance, output, talent retention, transition costs)
2. Each perspective presents initial position
3. Round 1: Perspectives respond to each other (e.g., Productivity addresses Employee_Wellbeing concerns)
4. Round 2: Further refinement and finding common ground
5. Synthesis: Balanced recommendation considering all factors

**Expected Output**:
- Summary of all 4 positions
- Areas of agreement (e.g., pilot program approach)
- Key trade-offs (short-term costs vs. long-term benefits)
- Nuanced recommendation with conditions

---

### Example 2: Technical Architecture Decision

**Question**: "Should we migrate from monolith to microservices?"

**Perspectives**: ["Scalability", "Development_Velocity", "Operational_Complexity", "Cost"]

**Process**:
1. Moderator clarifies: current pain points, team size, traffic patterns, budget
2. Scalability advocates for distributed architecture
3. Development_Velocity warns about coordination overhead
4. Operational_Complexity highlights monitoring challenges
5. Cost analyzes infrastructure and staffing implications
6. Debate rounds refine positions based on specific context
7. Synthesis provides decision framework (e.g., "Microservices if X, monolith if Y")

---

### Example 3: Ethical Analysis

**Question**: "Should we use facial recognition in public spaces for security?"

**Perspectives**: ["Public_Safety", "Privacy_Rights", "Social_Equity", "Legal_Framework"]

**Process**:
1. Moderator defines scope (what technology, what spaces, what purposes)
2. Public_Safety emphasizes crime prevention and emergency response
3. Privacy_Rights raises surveillance concerns and chilling effects
4. Social_Equity addresses bias and discriminatory impacts
5. Legal_Framework examines regulations and oversight
6. Debate explores trade-offs and safeguards
7. Synthesis acknowledges tension between values, proposes conditions

---

## Comparison: Program vs. Organ

| Aspect | Debate Program | Debate Organ |
|--------|----------------|--------------|
| **Format** | Pseudo-code (executable template) | Protocol shell (orchestration pattern) |
| **Level** | Implementation details | Architecture overview |
| **Best For** | Direct LLM prompting | System design, documentation |
| **Shows** | Step-by-step execution flow | Components and their roles |
| **Use When** | You need a prompt template | You need to understand the pattern |

**Recommendation**: Use both together!
- Start with the **organ** to understand the architecture
- Use the **program** to construct your actual prompts

---

## Advanced Usage

### Composing with Other Tools

**Combine with `understand_question` (thinking model)**:
```python
# Step 1: Decompose the question first
from context_engineering_mcp.server import ...
clarification = understand_question("Should we...", context="...", constraints="...")

# Step 2: Use clarified question in debate
debate_result = run_debate(clarified_question, perspectives=[...])
```

**Combine with `verify_logic` (thinking model)**:
```python
# After debate synthesis, verify the reasoning
verification = verify_logic(
    claim=synthesis["conclusion"],
    reasoning_trace=synthesis["full_debate"],
    constraints="Must address all perspectives"
)
```

### Integrating with RAG

```python
# 1. Retrieve relevant context
context = retrieve_documents(question)

# 2. Run debate with context
debate_prompt = f"""
Context: {context}

Now conduct debate using this evidence:
[Insert debate program template]
"""
```

### Chaining Multiple Organs

```python
# Use debate to narrow options, then use another organ for detailed analysis
initial_debate = run_debate_council(broad_question)
top_options = extract_top_3(initial_debate)

for option in top_options:
    detailed_analysis = run_research_synthesis_organ(option)
```

---

## Best Practices

### 1. Question Formulation

✅ **Good**: "Should we adopt TypeScript for our backend services?"
- Clear, specific, actionable
- Has clear stakeholders and trade-offs

❌ **Bad**: "Is TypeScript good?"
- Too vague, not actionable
- Lacks context for meaningful debate

### 2. Perspective Selection

✅ **Good**: Domain-appropriate perspectives
- Technical decision → Use relevant technical aspects
- Ethical question → Use ethical frameworks
- Business decision → Use business dimensions

❌ **Bad**: Generic perspectives for specialized questions
- Don't use "Optimistic/Pessimistic" for technical architecture

### 3. Round Configuration

- **1 round**: Simple yes/no decisions with clear criteria
- **2 rounds**: Most use cases (balanced depth vs. efficiency)
- **3+ rounds**: Complex, high-stakes decisions needing deep exploration

### 4. Synthesis Quality

Ensure synthesis includes:
- ✅ Summary of each perspective's key points
- ✅ Areas of agreement identified
- ✅ Acknowledged uncertainties or gaps
- ✅ Actionable recommendations
- ✅ Conditions or caveats

---

## Troubleshooting

### Issue: Perspectives are too similar

**Solution**: Make perspectives more distinct
- Instead of: ["Positive", "Negative", "Neutral"]
- Use: ["Cost_Efficiency", "User_Experience", "Technical_Debt", "Security"]

### Issue: Debate doesn't converge

**Solution**:
- Check if question is actually decidable
- Ensure moderator phase properly frames the question
- Consider if you need more rounds
- May indicate genuine unresolvable trade-off (this is valuable!)

### Issue: Synthesis is shallow

**Solution**:
- Ensure debate rounds actually engaged with counterarguments
- Check that all perspectives provided substantive initial positions
- May need more specific prompt instructions in synthesis phase

---

## MCP Integration

### Via MCP Protocol

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_prompt_program",
    "arguments": {
      "program_type": "debate"
    }
  }
}
```

```json
{
  "method": "tools/call",
  "params": {
    "name": "get_organ",
    "arguments": {
      "name": "debate_council"
    }
  }
}
```

### From Claude Desktop MCP

If Sutra is configured as an MCP server in Claude Desktop:

```
Please help me analyze whether we should migrate to microservices.

Use the debate_council organ approach with these perspectives:
- Scalability
- Development_Velocity
- Operational_Complexity
- Cost

Run 2 rounds of debate and provide a synthesis.
```

---

## Summary

**To use the debate system**:

1. **Retrieve** the template: `get_prompt_program("debate")` or `get_organ("debate_council")`
2. **Customize** perspectives for your domain
3. **Structure** your prompt following the phase pattern
4. **Execute** with your LLM
5. **Extract** the synthesis for your decision

**When to use debate**:
- ✅ Complex decisions with multiple stakeholders
- ✅ Trade-offs between competing values
- ✅ Questions where multiple valid perspectives exist
- ✅ Need for balanced, nuanced analysis

**When NOT to use debate**:
- ❌ Simple factual questions
- ❌ Questions with objectively correct answers
- ❌ Time-sensitive decisions needing quick resolution
- ❌ Questions where perspectives would be nearly identical

---

For more details, see:
- `design_docs/debate_system_implementation_report.md` - Full technical documentation
- `.context/00_foundations/04_organs_applications.md` - Architectural specification
- `src/context_engineering_mcp/core/programs.py` - Implementation source
- `src/context_engineering_mcp/systems/organs.py` - Organ source
