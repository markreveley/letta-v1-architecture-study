# Tour Management with Letta V1 Architecture

**Music industry examples demonstrating Letta's V1 agent architecture**

This directory contains practical examples and documentation for building tour management systems using Letta's simplified V1 architecture. These examples are designed for music industry professionals and developers building business workflow automation.

## 📁 Contents

- **[`../tourlab_email_agent.py`](../tourlab_email_agent.py)** - Complete working example of a tour management email agent
- **[`MEMORY_V1_MIGRATION.md`](MEMORY_V1_MIGRATION.md)** - Comprehensive migration guide from MemGPT to V1
- **[`../tests/test_tourlab_agent.py`](../../tests/test_tourlab_agent.py)** - Full test suite for validation

## 🎯 What You'll Learn

### 1. **Letta V1 Architecture Benefits**
- No heartbeat mechanism (simpler agent loop)
- Natural conversation flow (no forced tool calls)
- Direct responses without wrapper functions
- Native reasoning model support (OpenAI o1, Claude extended thinking)

### 2. **Memory Block Organization**
```python
memory_blocks = [
    {"label": "persona", "value": "I am a tour agent..."},
    {"label": "venue_knowledge", "description": "Venue database", "value": "..."},
    {"label": "artist_requirements", "description": "Tech specs", "value": "..."},
    {"label": "email_workflow", "description": "Current state", "value": "..."}
]
```

### 3. **Business Workflow Tools**
- `search_venue_database()` - Find venues by capacity, location
- `draft_email()` - Generate professional communications
- `check_tour_conflicts()` - Schedule validation
- `log_email_interaction()` - Audit trail tracking

### 4. **Tool Rules for Safety**
- Approval requirements for sending emails
- Workflow constraints (draft before send)
- Multi-step process orchestration

## 🚀 Quick Start

### Prerequisites

```bash
# Install Letta
pip install letta

# Or use the local development version
pip install -e .

# Set up API keys
export LETTA_API_KEY="your-letta-api-key"
export OPENAI_API_KEY="your-openai-key"
```

### Run the Example

```bash
# Start Letta server (in one terminal)
letta server

# Run the tour management agent (in another terminal)
cd examples
python tourlab_email_agent.py
```

### Expected Output

```
======================================================================
TOUR MANAGEMENT AGENT - LETTA V1 ARCHITECTURE EXAMPLE
======================================================================

[1/3] Creating tour management tools...
✓ Created tool: search_venue_database (ID: tool-...)
✓ Created tool: draft_email (ID: tool-...)
✓ Created tool: check_tour_conflicts (ID: tool-...)
✓ Created tool: log_email_interaction (ID: tool-...)

[2/3] Creating tour management agent...
✓ Created agent: Tour Management Email Agent
  ID: agent-...
  Type: letta_v1_agent
  Memory blocks: 5
  Tools attached: 4

[3/3] Running evaluation suite...
======================================================================
TEST: Venue Search Test
======================================================================
User: I need to find venues in New York with capacity around 1500-2000...
```

## 📚 Documentation

### Migration Guide

Read **[`MEMORY_V1_MIGRATION.md`](MEMORY_V1_MIGRATION.md)** for:
- Detailed comparison of MemGPT vs V1 architecture
- Step-by-step migration checklist
- Before/after code examples
- Common pitfalls and solutions
- Music industry-specific best practices

### Code Structure

**`tourlab_email_agent.py`** contains:
1. **Tool Definitions** - Custom functions for tour management
2. **Agent Configuration** - Memory blocks and V1 setup
3. **Evaluation Suite** - Automated testing framework
4. **Interactive Mode** - Command-line chat interface

## 🧪 Running Tests

```bash
# Run all tourlab tests
pytest tests/test_tourlab_agent.py -v

# Run specific test categories
pytest tests/test_tourlab_agent.py::test_tourlab_memory_initialization -v
pytest tests/test_tourlab_agent.py::test_search_venue_database_by_name -v
pytest tests/test_tourlab_agent.py::test_workflow_full_booking_process -v

# Run with coverage
pytest tests/test_tourlab_agent.py --cov=examples --cov-report=html
```

### Test Categories

- **Memory Block Tests** - Validate memory organization and updates
- **Tool Functionality Tests** - Unit tests for each tool
- **Workflow Simulation Tests** - Multi-step process validation
- **V1 Architecture Tests** - Verify V1-specific features
- **Integration Tests** - End-to-end agent behavior (requires server)

## 🎨 Use Cases

### 1. **Tour Booking Automation**
```python
# Agent handles: search → conflict check → draft → send
response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{
        "role": "user",
        "content": "Book CHVRCHES at Brooklyn Steel for December 18th"
    }]
)
```

### 2. **Venue Research**
```python
# Agent searches database and presents options
response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{
        "role": "user",
        "content": "Find venues in California with 5000+ capacity for summer 2025"
    }]
)
```

### 3. **Schedule Management**
```python
# Agent checks conflicts across multiple artists
response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{
        "role": "user",
        "content": "What dates in December are The Midnight available?"
    }]
)
```

### 4. **Email Workflow**
```python
# Agent drafts, reviews, and tracks communications
response = client.agents.messages.create(
    agent_id=agent_id,
    messages=[{
        "role": "user",
        "content": "Draft a follow-up to The Fillmore about our December inquiry"
    }]
)
```

## 🔧 Customization

### Adding Custom Venues

Edit the `search_venue_database()` function:

```python
def search_venue_database(query: str, location: Optional[str] = None) -> Dict:
    venues = {
        "Your Venue": {
            "location": "City, State",
            "capacity": 2000,
            "contact": "booking@yourvenue.com",
            "tech_specs": "PA system, stage dimensions",
            "availability": ["2025-12-01", "2025-12-15"]
        },
        # Add more venues...
    }
    # ... rest of function
```

### Adding Custom Artists

Edit the memory block:

```python
{
    "label": "artist_requirements",
    "value": (
        "Your Artist:\n"
        "- Stage: 35x30ft minimum\n"
        "- Tech: Full lighting, sound system\n"
        "- Hospitality: Green room, catering for 10\n"
    )
}
```

### Adding New Tools

Create a new function and register it:

```python
def send_contract(venue_name: str, contract_id: str) -> Dict:
    """Send contract to venue for signing."""
    # Your implementation
    return {"status": "sent", "venue": venue_name}

# Register when creating agent
tool = client.tools.create(func=send_contract, tags=["tourlab"])
```

## 🎼 Music Industry Context

### Why Tour Management Needs AI

Tour management involves:
- Coordinating dozens of venues across multiple cities
- Managing complex technical requirements per artist
- Tracking email threads with venue contacts
- Validating schedules across multiple artists
- Maintaining venue relationship history

**Traditional approach:** Manual spreadsheets, email threads, phone calls
**V1 Agent approach:** Automated search, conflict detection, communication drafting

### Real-World Applicability

This example demonstrates patterns for:
- **Festival booking** - Multiple artists, multiple stages
- **Tour routing** - Geographic optimization
- **Contract management** - Document tracking
- **Artist relations** - Requirements management
- **Venue relations** - Communication history

## 🔍 Architecture Deep Dive

### V1 vs MemGPT Comparison

| Feature | MemGPT | Letta V1 |
|---------|---------|----------|
| Loop mechanism | Heartbeat-based | Tool-call-based |
| Response method | `send_message()` required | Direct response |
| Inner thoughts | 50-word limit | Unlimited (reasoning support) |
| Memory management | `core_memory_*()` functions | Memory blocks |
| Continuation | `request_heartbeat()` | Call another tool |
| Complexity | High (many mechanics) | Low (natural flow) |

### Memory Block Strategy

```
┌─────────────────────────────────────────┐
│           Memory Blocks                  │
├─────────────────────────────────────────┤
│ persona      → Agent identity            │
│ human        → User context              │
│ venue_knowledge → Domain data (venues)   │
│ artist_requirements → Domain data (tech) │
│ email_workflow → State tracking          │
└─────────────────────────────────────────┘
```

**Design principle:** Separate identity, user context, domain knowledge, and state.

### Tool Call Flow

```
User: "Book CHVRCHES in Brooklyn"
  ↓
Agent: [analyzes request]
  ↓
Tool: check_tour_conflicts("CHVRCHES", ["2025-12-18"])
  ↓
Tool: search_venue_database(location="Brooklyn")
  ↓
Tool: draft_email(recipient="bookings@bksteel.com", ...)
  ↓
Agent: "I've drafted an email to Brooklyn Steel..."
  ↓
[No tool called → yields control to user]
```

## 🚨 Common Issues

### Issue: Agent calls too many tools

**Solution:** Use tool rules to constrain workflow:
```python
tool_rules = [{
    "type": "MaxCountPerStepToolRule",
    "tool_name": "search_venue_database",
    "max_count": 3
}]
```

### Issue: Agent doesn't remember previous searches

**Solution:** Update workflow state in memory:
```python
# Agent should update email_workflow block after each action
memory.update_block_value(
    "email_workflow",
    "Currently: Negotiating with Brooklyn Steel for Dec 18"
)
```

### Issue: Email drafts lack context

**Solution:** Ensure venue_knowledge and artist_requirements are populated:
```python
# Rich memory blocks = better email content
# Agent can reference specific tech specs from memory
```

## 📖 Additional Resources

### Letta Documentation
- [Agent Types](https://docs.letta.com/agents/types)
- [Memory Blocks](https://docs.letta.com/memory/blocks)
- [Tool Creation](https://docs.letta.com/tools/custom)
- [Tool Rules](https://docs.letta.com/tools/rules)

### Related Examples
- [`examples/streaming/`](../streaming/) - Streaming responses
- [`examples/personal_assistant_demo/`](../personal_assistant_demo/) - Email integration

### Code References
- [`letta/agents/letta_agent_v3.py`](../../letta/agents/letta_agent_v3.py) - V1 agent implementation
- [`letta/prompts/system_prompts/letta_v1.py`](../../letta/prompts/system_prompts/letta_v1.py) - V1 system prompt
- [`letta/schemas/tool_rule.py`](../../letta/schemas/tool_rule.py) - Tool rule types

## 🤝 Contributing

To improve these examples:

1. **Add more venues** - Expand the venue database
2. **Add more tools** - Contract management, rider creation, etc.
3. **Improve tests** - More edge cases and workflows
4. **Documentation** - Industry-specific tips and patterns

## 📝 License

These examples are part of the Letta project and follow the same license.

## 💬 Questions?

- **General Letta questions:** [Letta Discord](https://discord.gg/letta)
- **Music industry use cases:** Check the migration guide or file an issue
- **Bug reports:** [GitHub Issues](https://github.com/letta-ai/letta/issues)

---

**Built with ❤️ for the music industry by the Letta community**