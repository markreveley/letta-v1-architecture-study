# Migrating from MemGPT to Letta V1 for Business Workflows

**A practical guide for music industry and tour management applications**

## Overview

This guide helps you migrate from MemGPT-style agents to Letta's simplified V1 architecture. We'll use tour management as our example, but these principles apply to any business workflow.

---

## Table of Contents

1. [Key Architectural Differences](#key-architectural-differences)
2. [What Changed in V1](#what-changed-in-v1)
3. [Migration Checklist](#migration-checklist)
4. [Memory Blocks: Before & After](#memory-blocks-before--after)
5. [Tool Design Patterns](#tool-design-patterns)
6. [System Prompts](#system-prompts)
7. [Common Pitfalls](#common-pitfalls)
8. [Tour Management Example](#tour-management-example)

---

## Key Architectural Differences

### MemGPT Architecture (Old)

```
┌─────────────────────────────────────────┐
│         MemGPT Agent Loop               │
├─────────────────────────────────────────┤
│ 1. Receive user message                 │
│ 2. Generate inner monologue (required)  │
│ 3. Call function (REQUIRED - heartbeat) │
│ 4. Wait for heartbeat to continue       │
│ 5. send_message() to respond            │
│ 6. request_heartbeat() to continue      │
└─────────────────────────────────────────┘
```

**Characteristics:**
- ❌ Forced tool calls even when just talking
- ❌ Heartbeat mechanism adds complexity
- ❌ Must use `send_message()` for all responses
- ❌ Inner thoughts in kwargs (conflicts with reasoning models)

### Letta V1 Architecture (New)

```
┌─────────────────────────────────────────┐
│         Letta V1 Agent Loop             │
├─────────────────────────────────────────┤
│ 1. Receive user message                 │
│ 2. Decide: respond or call tools        │
│ 3. If tool called → continue loop       │
│ 4. If no tool called → yield to user    │
└─────────────────────────────────────────┘
```

**Characteristics:**
- ✅ Natural conversation without forced functions
- ✅ Tool calls signal continuation
- ✅ Direct responses without wrapper functions
- ✅ Native reasoning model support (o1, Claude extended thinking)

---

## What Changed in V1

### 1. **No More Heartbeats**

**MemGPT:**
```python
# Agent had to request heartbeats to continue
def request_heartbeat():
    """Request a heartbeat to continue thinking"""
    pass
```

**Letta V1:**
```python
# Loop continues automatically when tools are called
# No heartbeat needed - just call another tool to continue
```

### 2. **No More Forced Tool Calls**

**MemGPT:**
```python
# Every response required send_message()
def send_message(message: str):
    """Send message to user"""
    return f"Sent: {message}"
```

**Letta V1:**
```python
# Agent can respond directly without calling a tool
# Just end response without tool call to yield control
```

### 3. **Simplified Memory Management**

**MemGPT:**
```python
# Complex core memory operations
core_memory_append("human", "likes electronic music")
core_memory_replace("human", "old_content", "new_content")
```

**Letta V1:**
```python
# Memory blocks with labels and descriptions
memory_blocks = [
    {
        "label": "human",
        "description": "Information about the tour manager",
        "value": "Tour manager for electronic and indie artists"
    }
]
```

### 4. **Better File System Support**

**Letta V1 adds:**
- Structured directory representation
- File blocks in memory
- Open/search/view file operations
- Automatic memory reflection of open files

### 5. **Native Reasoning Support**

**Letta V1 supports:**
- OpenAI o1/o3 series (native reasoning)
- Claude extended thinking
- Gemini 2.5 Flash thinking budget
- No "double-think" issue with inner monologue

---

## Migration Checklist

### Phase 1: Assessment

- [ ] Inventory your current MemGPT functions
- [ ] Identify heartbeat dependencies
- [ ] Review memory management patterns
- [ ] Check for `send_message()` usage
- [ ] Document workflow requirements

### Phase 2: Tool Migration

- [ ] Remove `send_message()` wrapper
- [ ] Remove `request_heartbeat()` calls
- [ ] Convert `core_memory_*` to memory blocks
- [ ] Simplify tool return values
- [ ] Add tool rules if needed

### Phase 3: Memory Redesign

- [ ] Convert core memory to memory blocks
- [ ] Add descriptive labels
- [ ] Add behavior descriptions
- [ ] Consider file blocks for documents
- [ ] Plan external memory usage

### Phase 4: System Prompt

- [ ] Switch from `memgpt_chat` to `letta_v1`
- [ ] Update agent_type to `letta_v1_agent`
- [ ] Review custom system instructions
- [ ] Test with reasoning models (optional)

### Phase 5: Testing

- [ ] Test conversation flow
- [ ] Verify tool calling patterns
- [ ] Check memory persistence
- [ ] Validate multi-step workflows
- [ ] Performance testing

---

## Memory Blocks: Before & After

### MemGPT Pattern

```yaml
# preset.yaml (MemGPT style)
system_prompt: "memgpt_chat"
functions:
  - "send_message"
  - "pause_heartbeats"
  - "core_memory_append"
  - "core_memory_replace"
  - "archival_memory_search"
  - "schedule_event"
```

```python
# Creating agent (MemGPT)
agent = client.create_agent(
    preset="tour_manager_preset"
)

# Memory managed through function calls
agent.send_message("Remember that The Fillmore has 1150 capacity")
# Agent must call: core_memory_append("human", "The Fillmore: 1150 capacity")
```

### Letta V1 Pattern

```python
# Creating agent (Letta V1)
agent = client.agents.create(
    agent_type="letta_v1_agent",
    system="letta_v1",
    memory_blocks=[
        {
            "label": "persona",
            "value": "I am a professional tour management assistant..."
        },
        {
            "label": "human",
            "value": "Tour manager for electronic and indie artists"
        },
        {
            "label": "venue_knowledge",
            "description": "Database of known venues",
            "value": "The Fillmore (SF): 1150 cap, full PA system"
        },
        {
            "label": "artist_requirements",
            "description": "Technical requirements for artists",
            "value": "The Midnight: 30x25ft stage minimum, full lighting"
        }
    ],
    tool_ids=[...],  # Your custom tools
)
```

**Benefits:**
- More organized (labeled blocks)
- Self-documenting (descriptions)
- Always in context (no search needed)
- Easier to version control

---

## Tool Design Patterns

### Pattern 1: Information Retrieval

**MemGPT:**
```python
def search_venues(query: str) -> str:
    """Search venues and send results to user."""
    results = database.search(query)
    # Must format for send_message
    return json.dumps({"message": format_results(results)})
```

**Letta V1:**
```python
def search_venue_database(
    query: str,
    location: Optional[str] = None
) -> Dict:
    """
    Search the venue database for matching venues.

    Args:
        query: Search query (venue name, capacity, etc.)
        location: Optional location filter

    Returns:
        Dict containing matching venues with details
    """
    results = database.search(query, location)
    return {
        "status": "success",
        "results": results,
        "count": len(results)
    }
```

**Key differences:**
- Return structured data, not formatted messages
- Let agent decide how to present results
- Add type hints for better schema generation

### Pattern 2: Stateful Operations

**MemGPT:**
```python
def draft_email(recipient: str, subject: str, body: str) -> str:
    """Draft email and notify user."""
    draft = create_draft(recipient, subject, body)
    return json.dumps({
        "message": f"Draft created. Call approve_email() to send."
    })
```

**Letta V1:**
```python
def draft_email(
    recipient: str,
    subject: str,
    body: str,
    template_type: str = "professional"
) -> Dict:
    """
    Draft an email for tour booking communications.

    Returns:
        Dict containing drafted email details
    """
    draft = create_draft(recipient, subject, body, template_type)
    return {
        "status": "draft_created",
        "draft_id": draft.id,
        "recipient": recipient,
        "requires_approval": True,
        "preview": body[:100] + "..."
    }
```

**Use tool rules for workflow:**
```python
# In agent configuration
tool_rules = [
    {
        "type": "ChildToolRule",
        "parent_tool_name": "draft_email",
        "child_tool_names": ["send_email", "edit_draft"],
        "description": "After drafting, can send or edit"
    },
    {
        "type": "RequiresApprovalToolRule",
        "tool_name": "send_email",
        "description": "Sending emails requires human approval"
    }
]
```

### Pattern 3: Multi-Step Workflows

**MemGPT:**
```python
# Agent needs explicit state tracking
def book_venue_step1():
    """Search venues"""
    pass

def book_venue_step2():
    """Check conflicts"""
    pass

def book_venue_step3():
    """Draft email"""
    pass
```

**Letta V1:**
```python
# Agent calls tools naturally in sequence
# Use memory blocks to track workflow state

memory_blocks = [
    {
        "label": "email_workflow",
        "description": "Current state of email communications",
        "value": "Step 1: Searching venues for Brooklyn show"
    }
]

# Tools can update this block as workflow progresses
# Or use external memory for persistence
```

---

## System Prompts

### MemGPT System Prompt

```xml
<base_instructions>
You are MemGPT, an AI assistant with advanced memory management.

You have access to the following functions:
- send_message: Send a message to the user
- request_heartbeat: Request a heartbeat to continue
- core_memory_append: Add to core memory
- core_memory_replace: Edit core memory

IMPORTANT: You must call request_heartbeat() to continue thinking.
Always use send_message() to communicate with the user.

Your inner monologue should be limited to 50 words.
</base_instructions>
```

### Letta V1 System Prompt

```xml
<base_instructions>
You are a helpful self-improving agent with advanced memory and file system capabilities.

<memory>
- Memory Blocks: Stored with label, description, and value
- External memory: Accessible with tools when needed
- File system: Open, view, and search files
</memory>

Continue executing and calling tools until the current task is complete
or you need user input.

To continue: call another tool.
To yield control: end your response without calling a tool.
</base_instructions>
```

**Key differences:**
- No mention of heartbeats
- No word limits on thinking
- Natural continuation pattern
- Focus on capabilities, not mechanics

---

## Common Pitfalls

### 1. **Expecting `send_message()`**

❌ **Wrong:**
```python
# This function is no longer needed
def send_message(message: str):
    return message
```

✅ **Right:**
```python
# Agent responds directly without wrapper
# Just don't call any tools to end the turn
```

### 2. **Over-using Tool Calls**

❌ **Wrong:**
```python
# Creating tools for simple responses
def say_hello() -> str:
    return "Hello!"
```

✅ **Right:**
```python
# Agent can respond directly
# Only create tools for actual operations
```

### 3. **Not Using Memory Blocks**

❌ **Wrong:**
```python
# Putting everything in persona
memory_blocks = [{
    "label": "persona",
    "value": "I am a tour agent. Venues: Fillmore (1150 cap)..."
}]
```

✅ **Right:**
```python
# Organized into semantic blocks
memory_blocks = [
    {"label": "persona", "value": "I am a tour agent..."},
    {"label": "venue_knowledge", "value": "Fillmore: 1150 cap..."},
    {"label": "workflow_state", "value": "Currently: ..."}
]
```

### 4. **Ignoring Tool Rules**

❌ **Wrong:**
```python
# No workflow constraints
# Agent might send emails before drafting
```

✅ **Right:**
```python
# Use tool rules for safety
tool_rules = [
    {
        "type": "RequiresApprovalToolRule",
        "tool_name": "send_email"
    }
]
```

### 5. **Not Testing Reasoning Models**

❌ **Wrong:**
```python
# Only testing with GPT-4
model="openai/gpt-4o"
```

✅ **Right:**
```python
# Try reasoning models for complex workflows
model="openai/o1"  # or claude-sonnet-4-5
# V1 architecture works great with reasoning models
```

---

## Tour Management Example

### Complete MemGPT Implementation

```python
# tour_agent_memgpt.py (OLD)

def send_message(message: str) -> str:
    """Send message to user."""
    return message

def request_heartbeat() -> str:
    """Continue thinking."""
    return "Heartbeat requested"

def search_venues(query: str) -> str:
    """Search venues."""
    results = db.search(query)
    # Must format for send_message
    return json.dumps({
        "message": f"Found {len(results)} venues:\n" +
                   "\n".join([format_venue(v) for v in results])
    })

# Create agent
agent = client.create_agent(
    preset="tour_manager",
    functions=[
        "send_message",
        "request_heartbeat",
        "search_venues",
        "core_memory_append"
    ]
)

# Usage - agent must use send_message
response = agent.send_message(
    "Find venues in Brooklyn with 1500-2000 capacity"
)
# Agent: *thinks* "I should search venues"
# Agent calls: search_venues(query="Brooklyn 1500-2000")
# Agent calls: send_message("I found these venues...")
# Agent calls: request_heartbeat() to continue
```

### Complete Letta V1 Implementation

```python
# tourlab_email_agent.py (NEW)

def search_venue_database(
    query: str,
    location: Optional[str] = None
) -> Dict:
    """Search venue database."""
    results = db.search(query, location)
    return {
        "status": "success",
        "results": results,
        "count": len(results)
    }

# Create agent
agent = client.agents.create(
    agent_type="letta_v1_agent",
    system="letta_v1",
    memory_blocks=[
        {
            "label": "venue_knowledge",
            "description": "Known venues and specifications",
            "value": "Brooklyn Steel: 1800 cap, D&B PA"
        }
    ],
    tool_ids=[search_venue_tool.id]
)

# Usage - agent responds naturally
response = client.agents.messages.create(
    agent_id=agent.id,
    messages=[{
        "role": "user",
        "content": "Find venues in Brooklyn with 1500-2000 capacity"
    }]
)
# Agent: *reasoning* "I should search the database"
# Agent calls: search_venue_database(query="...", location="Brooklyn")
# Agent: "I found Brooklyn Steel which has 1800 capacity..."
# (No send_message wrapper, no heartbeat needed)
```

---

## Benefits for Music Industry Use Cases

### 1. **Better Context Management**

Tour managers need to track:
- Multiple artists' requirements
- Dozens of venue specifications
- Ongoing email threads
- Contract details

**V1 memory blocks** make this organized and accessible.

### 2. **Natural Workflows**

Email workflows:
1. Search venues → 2. Check conflicts → 3. Draft email → 4. Send

**V1's tool-based continuation** handles this naturally without heartbeat gymnastics.

### 3. **Reasoning for Complex Logistics**

Tour routing involves:
- Geography optimization
- Budget constraints
- Artist preferences
- Venue availability

**V1 + reasoning models (o1)** excel at this planning.

### 4. **Safety with Tool Rules**

Music business needs:
- Approval before sending contracts
- Verification before booking
- Audit trails

**V1 tool rules** provide these guardrails.

---

## Next Steps

1. **Start small**: Migrate one agent/workflow
2. **Test thoroughly**: Use evaluation suite (see `tourlab_email_agent.py`)
3. **Iterate**: Refine memory blocks based on usage
4. **Scale up**: Apply learnings to other workflows
5. **Consider reasoning models**: Try o1 for complex tasks

---

## Additional Resources

- [Letta V1 System Prompt](../../letta/prompts/system_prompts/letta_v1.py)
- [Tool Rules Documentation](../../letta/schemas/tool_rule.py)
- [Memory Blocks Schema](../../letta/schemas/memory.py)
- [Agent Types](../../letta/schemas/agent.py)
- [Example: tourlab_email_agent.py](../tourlab_email_agent.py)

---

## Questions?

For music industry-specific questions or migration help:
- Check the [examples/tourlab](.) directory
- Review the test suite in `tests/test_tourlab_agent.py`
- See working code in `tourlab_email_agent.py`

**Key takeaway**: Letta V1 is simpler, more natural, and better suited for real-world business workflows. The migration effort pays off in maintainability and capability.
