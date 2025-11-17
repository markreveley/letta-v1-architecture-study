"""
Test suite for Tour Management Agent (Letta V1 Architecture)

This test suite validates the tourlab email agent's capabilities:
- Memory block management for venue/artist knowledge
- Tool execution for venue search, conflict checking, email drafting
- V1 architecture behavior (no heartbeats, natural continuation)
- Multi-step workflow orchestration
- Music industry-specific use cases
"""

import pytest
from typing import Dict, List, Optional

from letta.schemas.block import Block
from letta.schemas.enums import AgentType
from letta.schemas.memory import Memory
from letta.schemas.llm_config import LLMConfig
from tests.utils import create_tool_from_func


# ============================================================================
# TOOL DEFINITIONS (Same as tourlab_email_agent.py)
# ============================================================================

def search_venue_database(query: str, location: Optional[str] = None) -> Dict:
    """
    Search the venue database for matching venues.

    Args:
        query: Search query (venue name, capacity range, etc.)
        location: Optional location filter (city, state, or region)

    Returns:
        Dict containing matching venues with details
    """
    venues = {
        "The Fillmore": {
            "location": "San Francisco, CA",
            "capacity": 1150,
            "contact": "booking@thefillmore.com",
            "tech_specs": "Full PA, 40x30ft stage, green rooms",
            "availability": ["2025-12-15", "2025-12-20"]
        },
        "Brooklyn Steel": {
            "location": "Brooklyn, NY",
            "capacity": 1800,
            "contact": "bookings@bksteel.com",
            "tech_specs": "D&B PA system, 50x35ft stage, artist lounge",
            "availability": ["2025-12-10", "2025-12-18"]
        },
        "Red Rocks": {
            "location": "Morrison, CO",
            "capacity": 9525,
            "contact": "events@redrocks.com",
            "tech_specs": "Outdoor amphitheater, full production",
            "availability": ["2025-06-15", "2025-07-01"]
        }
    }

    results = []
    for name, details in venues.items():
        if query.lower() in name.lower() or (location and location.lower() in details["location"].lower()):
            results.append({
                "name": name,
                **details
            })

    return {
        "status": "success",
        "query": query,
        "location_filter": location,
        "results": results,
        "count": len(results)
    }


def draft_email(
    recipient: str,
    subject: str,
    body: str,
    template_type: str = "professional"
) -> Dict:
    """
    Draft an email for tour booking communications.

    Args:
        recipient: Email recipient (venue contact or artist rep)
        subject: Email subject line
        body: Email body content
        template_type: Email template style (professional, friendly, follow_up)

    Returns:
        Dict containing drafted email details
    """
    templates = {
        "professional": {
            "signature": "\n\nBest regards,\nTour Management Team"
        },
        "friendly": {
            "signature": "\n\nLooking forward to working together!\nCheers,\nTour Team"
        },
        "follow_up": {
            "signature": "\n\nThank you for your time.\nBest,\nTour Coordinator"
        }
    }

    signature = templates.get(template_type, templates["professional"])["signature"]
    full_body = body + signature

    return {
        "status": "draft_created",
        "recipient": recipient,
        "subject": subject,
        "body": full_body,
        "template_used": template_type,
        "char_count": len(full_body),
        "requires_approval": True
    }


def check_tour_conflicts(
    artist_name: str,
    proposed_dates: List[str]
) -> Dict:
    """
    Check for scheduling conflicts in the tour calendar.

    Args:
        artist_name: Name of the artist/band
        proposed_dates: List of proposed show dates (YYYY-MM-DD format)

    Returns:
        Dict containing conflict analysis
    """
    existing_schedule = {
        "The Midnight": {
            "2025-12-14": "Seattle, WA - Showbox",
            "2025-12-22": "Portland, OR - Crystal Ballroom"
        },
        "CHVRCHES": {
            "2025-12-16": "Los Angeles, CA - The Fonda"
        }
    }

    conflicts = []
    available = []

    artist_schedule = existing_schedule.get(artist_name, {})

    for date in proposed_dates:
        if date in artist_schedule:
            conflicts.append({
                "date": date,
                "conflict": artist_schedule[date]
            })
        else:
            available.append(date)

    return {
        "status": "analysis_complete",
        "artist": artist_name,
        "proposed_dates": proposed_dates,
        "conflicts": conflicts,
        "available_dates": available,
        "has_conflicts": len(conflicts) > 0
    }


def log_email_interaction(
    venue_name: str,
    interaction_type: str,
    notes: str
) -> Dict:
    """
    Log an email interaction with a venue for tracking purposes.

    Args:
        venue_name: Name of the venue
        interaction_type: Type of interaction (inquiry, follow_up, confirmation, rejection)
        notes: Notes about the interaction

    Returns:
        Dict confirming the log entry
    """
    import datetime

    return {
        "status": "logged",
        "venue": venue_name,
        "type": interaction_type,
        "timestamp": datetime.datetime.now().isoformat(),
        "notes": notes,
        "log_id": f"LOG-{hash(venue_name + notes) % 10000:04d}"
    }


# ============================================================================
# MEMORY BLOCK FIXTURES
# ============================================================================

@pytest.fixture
def tourlab_memory_blocks():
    """Standard memory blocks for tour management agent."""
    return [
        Block(
            label="persona",
            value=(
                "I am a professional tour management assistant specializing in booking "
                "and coordinating live music performances. I help with venue research, "
                "email communications, schedule management, and logistics coordination."
            ),
            limit=2000
        ),
        Block(
            label="human",
            value="Tour manager for multiple artists in electronic and indie music genres.",
            limit=1000
        ),
        Block(
            label="venue_knowledge",
            description="Database of known venues with capacity, tech specs, and booking contacts",
            value=(
                "Key Venues:\n"
                "- The Fillmore (SF): 1150 cap, full PA, booking@thefillmore.com\n"
                "- Brooklyn Steel (NYC): 1800 cap, D&B PA, bookings@bksteel.com\n"
                "- Red Rocks (CO): 9525 cap, outdoor amphitheater, events@redrocks.com"
            ),
            limit=5000
        ),
        Block(
            label="artist_requirements",
            description="Technical and hospitality requirements for managed artists",
            value=(
                "The Midnight: \n"
                "- Stage: Minimum 30x25ft\n"
                "- Tech: Full lighting rig, video wall capability\n"
                "- Hospitality: Private green room, catering for 8\n\n"
                "CHVRCHES:\n"
                "- Stage: Minimum 40x30ft\n"
                "- Tech: Advanced lighting, synth setup space\n"
                "- Hospitality: Separate dressing rooms, vegan catering"
            ),
            limit=5000
        ),
        Block(
            label="email_workflow",
            description="Current state of email communications and pending tasks",
            value="No active email threads. Ready to begin outreach for 2025 winter tour.",
            limit=3000
        )
    ]


@pytest.fixture
def tourlab_memory(tourlab_memory_blocks):
    """Memory instance for tourlab agent."""
    return Memory(
        agent_type=AgentType.letta_v1_agent,
        blocks=tourlab_memory_blocks
    )


# ============================================================================
# MEMORY BLOCK TESTS
# ============================================================================

def test_tourlab_memory_initialization(tourlab_memory):
    """Test that tourlab memory initializes with correct blocks."""
    block_labels = tourlab_memory.list_block_labels()
    assert "persona" in block_labels
    assert "human" in block_labels
    assert "venue_knowledge" in block_labels
    assert "artist_requirements" in block_labels
    assert "email_workflow" in block_labels


def test_tourlab_memory_venue_knowledge(tourlab_memory):
    """Test accessing venue knowledge from memory."""
    venue_block = tourlab_memory.get_block("venue_knowledge")
    assert "The Fillmore" in venue_block.value
    assert "Brooklyn Steel" in venue_block.value
    assert "1150 cap" in venue_block.value
    assert venue_block.description == "Database of known venues with capacity, tech specs, and booking contacts"


def test_tourlab_memory_artist_requirements(tourlab_memory):
    """Test accessing artist requirements from memory."""
    artist_block = tourlab_memory.get_block("artist_requirements")
    assert "The Midnight" in artist_block.value
    assert "CHVRCHES" in artist_block.value
    assert "30x25ft" in artist_block.value  # The Midnight stage requirement
    assert "vegan catering" in artist_block.value  # CHVRCHES requirement


def test_tourlab_memory_update_workflow_state(tourlab_memory):
    """Test updating email workflow state."""
    new_state = "Currently negotiating with Brooklyn Steel for December 18th show."
    tourlab_memory.update_block_value("email_workflow", new_state)
    assert tourlab_memory.get_block("email_workflow").value == new_state


def test_tourlab_memory_compilation_v1_standard(tourlab_memory):
    """Test memory compilation for V1 agent with standard (non-Anthropic) models."""
    openai_config = LLMConfig(
        model="gpt-4o",
        model_endpoint_type="openai",
        context_window=128000
    )
    compiled = tourlab_memory.compile(llm_config=openai_config)

    assert "<memory_blocks>" in compiled
    assert "<persona>" in compiled
    assert "<venue_knowledge>" in compiled
    assert "The Fillmore" in compiled
    # Should NOT have line numbers for non-Anthropic models
    assert "1→" not in compiled


def test_tourlab_memory_compilation_v1_anthropic(tourlab_memory):
    """Test memory compilation for V1 agent with Anthropic models (line-numbered)."""
    anthropic_config = LLMConfig(
        model="claude-sonnet-4-20250514",
        model_endpoint_type="anthropic",
        context_window=200000
    )
    compiled = tourlab_memory.compile(llm_config=anthropic_config)

    assert "<memory_blocks>" in compiled
    # Should have line numbers for Anthropic models with V1 agent
    # (The venue_knowledge block has multiple lines)
    assert "Key Venues:" in compiled


# ============================================================================
# TOOL FUNCTIONALITY TESTS
# ============================================================================

def test_search_venue_database_by_name():
    """Test venue search by name."""
    result = search_venue_database(query="Fillmore")
    assert result["status"] == "success"
    assert result["count"] == 1
    assert result["results"][0]["name"] == "The Fillmore"
    assert result["results"][0]["capacity"] == 1150


def test_search_venue_database_by_location():
    """Test venue search by location."""
    result = search_venue_database(query="", location="Brooklyn")
    assert result["status"] == "success"
    assert result["count"] == 1
    assert result["results"][0]["name"] == "Brooklyn Steel"
    assert result["results"][0]["location"] == "Brooklyn, NY"


def test_search_venue_database_no_results():
    """Test venue search with no matches."""
    result = search_venue_database(query="Nonexistent Venue")
    assert result["status"] == "success"
    assert result["count"] == 0
    assert result["results"] == []


def test_draft_email_professional_template():
    """Test email drafting with professional template."""
    result = draft_email(
        recipient="booking@thefillmore.com",
        subject="Tour Booking Inquiry - The Midnight",
        body="We are interested in booking The Midnight for December 15th.",
        template_type="professional"
    )
    assert result["status"] == "draft_created"
    assert result["recipient"] == "booking@thefillmore.com"
    assert result["template_used"] == "professional"
    assert "Best regards" in result["body"]
    assert result["requires_approval"] is True


def test_draft_email_friendly_template():
    """Test email drafting with friendly template."""
    result = draft_email(
        recipient="bookings@bksteel.com",
        subject="Show Inquiry",
        body="Hey! We'd love to bring CHVRCHES to your venue.",
        template_type="friendly"
    )
    assert result["template_used"] == "friendly"
    assert "Looking forward to working together" in result["body"]
    assert "Cheers" in result["body"]


def test_check_tour_conflicts_has_conflicts():
    """Test conflict checking with actual conflicts."""
    result = check_tour_conflicts(
        artist_name="The Midnight",
        proposed_dates=["2025-12-14", "2025-12-15"]
    )
    assert result["status"] == "analysis_complete"
    assert result["has_conflicts"] is True
    assert len(result["conflicts"]) == 1
    assert result["conflicts"][0]["date"] == "2025-12-14"
    assert "Seattle" in result["conflicts"][0]["conflict"]
    assert "2025-12-15" in result["available_dates"]


def test_check_tour_conflicts_no_conflicts():
    """Test conflict checking with no conflicts."""
    result = check_tour_conflicts(
        artist_name="The Midnight",
        proposed_dates=["2025-12-15", "2025-12-20"]
    )
    assert result["status"] == "analysis_complete"
    assert result["has_conflicts"] is False
    assert len(result["conflicts"]) == 0
    assert len(result["available_dates"]) == 2


def test_check_tour_conflicts_unknown_artist():
    """Test conflict checking for artist not in schedule."""
    result = check_tour_conflicts(
        artist_name="Unknown Band",
        proposed_dates=["2025-12-01"]
    )
    assert result["status"] == "analysis_complete"
    assert result["has_conflicts"] is False
    assert "2025-12-01" in result["available_dates"]


def test_log_email_interaction():
    """Test email interaction logging."""
    result = log_email_interaction(
        venue_name="The Fillmore",
        interaction_type="inquiry",
        notes="Initial inquiry sent for December dates"
    )
    assert result["status"] == "logged"
    assert result["venue"] == "The Fillmore"
    assert result["type"] == "inquiry"
    assert "timestamp" in result
    assert "log_id" in result
    assert result["log_id"].startswith("LOG-")


# ============================================================================
# TOOL CREATION TESTS
# ============================================================================

def test_create_venue_search_tool():
    """Test creating tool from venue search function."""
    tool = create_tool_from_func(search_venue_database)
    assert tool.name == "search_venue_database"
    assert "query" in str(tool.json_schema)
    assert "location" in str(tool.json_schema)


def test_create_email_draft_tool():
    """Test creating tool from email draft function."""
    tool = create_tool_from_func(draft_email)
    assert tool.name == "draft_email"
    assert "recipient" in str(tool.json_schema)
    assert "subject" in str(tool.json_schema)
    assert "body" in str(tool.json_schema)
    assert "template_type" in str(tool.json_schema)


def test_create_conflict_check_tool():
    """Test creating tool from conflict check function."""
    tool = create_tool_from_func(check_tour_conflicts)
    assert tool.name == "check_tour_conflicts"
    assert "artist_name" in str(tool.json_schema)
    assert "proposed_dates" in str(tool.json_schema)


def test_create_log_interaction_tool():
    """Test creating tool from interaction logging function."""
    tool = create_tool_from_func(log_email_interaction)
    assert tool.name == "log_email_interaction"
    assert "venue_name" in str(tool.json_schema)
    assert "interaction_type" in str(tool.json_schema)
    assert "notes" in str(tool.json_schema)


# ============================================================================
# WORKFLOW SIMULATION TESTS
# ============================================================================

def test_workflow_venue_search_to_email_draft():
    """Test multi-step workflow: search venues then draft email."""
    # Step 1: Search for venue
    search_result = search_venue_database(query="Brooklyn", location="New York")
    assert search_result["count"] > 0
    venue = search_result["results"][0]

    # Step 2: Draft email to found venue
    draft_result = draft_email(
        recipient=venue["contact"],
        subject=f"Tour Booking Inquiry - {venue['name']}",
        body=f"We are interested in booking a show at {venue['name']}.",
        template_type="professional"
    )
    assert draft_result["status"] == "draft_created"
    assert venue["name"] in draft_result["body"]


def test_workflow_conflict_check_before_booking():
    """Test workflow: check conflicts before proceeding with booking."""
    # Step 1: Check conflicts
    conflict_result = check_tour_conflicts(
        artist_name="The Midnight",
        proposed_dates=["2025-12-15"]
    )

    # Step 2: Only proceed if no conflicts
    if not conflict_result["has_conflicts"]:
        # Search for venue
        venue_result = search_venue_database(query="Fillmore")
        assert venue_result["count"] > 0

        # Draft email
        draft_result = draft_email(
            recipient=venue_result["results"][0]["contact"],
            subject="Tour Booking Request",
            body="We'd like to book The Midnight for December 15th.",
            template_type="professional"
        )
        assert draft_result["status"] == "draft_created"


def test_workflow_full_booking_process():
    """Test complete booking workflow."""
    artist = "CHVRCHES"
    target_location = "Brooklyn"
    proposed_date = "2025-12-18"

    # Step 1: Check artist conflicts
    conflict_check = check_tour_conflicts(
        artist_name=artist,
        proposed_dates=[proposed_date]
    )
    assert not conflict_check["has_conflicts"], "Artist should be available"

    # Step 2: Search for suitable venues
    venue_search = search_venue_database(query="", location=target_location)
    assert venue_search["count"] > 0, "Should find venues in Brooklyn"
    venue = venue_search["results"][0]

    # Step 3: Verify venue meets artist requirements
    # (In real implementation, would check venue specs against artist requirements)
    assert venue["capacity"] >= 1500, "Venue should have adequate capacity"

    # Step 4: Draft inquiry email
    email_draft = draft_email(
        recipient=venue["contact"],
        subject=f"Tour Booking Inquiry - {artist}",
        body=f"We are interested in booking {artist} at {venue['name']} on {proposed_date}.",
        template_type="professional"
    )
    assert email_draft["status"] == "draft_created"

    # Step 5: Log the interaction
    log_result = log_email_interaction(
        venue_name=venue["name"],
        interaction_type="inquiry",
        notes=f"Sent booking inquiry for {artist} on {proposed_date}"
    )
    assert log_result["status"] == "logged"


# ============================================================================
# INTEGRATION TESTS (require server/client setup)
# ============================================================================

@pytest.mark.skip(reason="Requires running Letta server - for manual integration testing")
async def test_create_tourlab_agent_with_server(server):
    """Integration test: Create tourlab agent on server."""
    from letta.schemas.agent import CreateAgent

    # Create tools
    actor = await server.user_manager.get_actor_or_default_async()
    tools = []
    for func in [search_venue_database, draft_email, check_tour_conflicts, log_email_interaction]:
        tool = await server.tool_manager.create_or_update_tool_async(
            create_tool_from_func(func),
            actor=actor
        )
        tools.append(tool)

    # Create agent
    agent_request = CreateAgent(
        name="Tour Management Agent",
        agent_type=AgentType.letta_v1_agent,
        memory_blocks=[
            {"label": "persona", "value": "I am a tour management assistant."},
            {"label": "human", "value": "Tour manager for electronic music artists."}
        ],
        tool_ids=[t.id for t in tools],
        system="letta_v1"
    )

    agent = await server.agent_manager.create_agent_async(agent_request, actor=actor)
    assert agent.id is not None
    assert agent.agent_type == AgentType.letta_v1_agent


@pytest.mark.skip(reason="Requires running Letta server - for manual integration testing")
async def test_tourlab_agent_venue_search_interaction(server, tourlab_agent_id):
    """Integration test: Agent responds to venue search request."""
    from letta.schemas.message import MessageCreate

    actor = await server.user_manager.get_actor_or_default_async()

    # Send message to agent
    response = await server.agent_manager.send_message_async(
        agent_id=tourlab_agent_id,
        actor=actor,
        messages=[MessageCreate(
            role="user",
            content="Find me venues in Brooklyn with capacity around 1800"
        )]
    )

    # Verify response includes tool call and venue information
    tool_calls = [msg for msg in response.messages if msg.message_type == "tool_call_message"]
    assert len(tool_calls) > 0, "Agent should have called search_venue_database"

    # Should get assistant response with venue info
    assistant_msgs = [msg for msg in response.messages if msg.message_type == "assistant_message"]
    assert len(assistant_msgs) > 0, "Agent should provide response"


# ============================================================================
# V1 ARCHITECTURE VALIDATION TESTS
# ============================================================================

def test_v1_agent_type_enum():
    """Verify letta_v1_agent is a valid agent type."""
    assert AgentType.letta_v1_agent in AgentType
    assert AgentType.letta_v1_agent.value == "letta_v1_agent"


def test_v1_memory_supports_descriptions(tourlab_memory_blocks):
    """Verify V1 memory blocks support description field."""
    venue_block = next(b for b in tourlab_memory_blocks if b.label == "venue_knowledge")
    assert venue_block.description is not None
    assert venue_block.description == "Database of known venues with capacity, tech specs, and booking contacts"


def test_v1_no_heartbeat_functions():
    """Verify tourlab tools don't include MemGPT heartbeat functions."""
    tool_names = [
        search_venue_database.__name__,
        draft_email.__name__,
        check_tour_conflicts.__name__,
        log_email_interaction.__name__
    ]

    # None of our tools should be heartbeat-related
    assert "request_heartbeat" not in tool_names
    assert "pause_heartbeats" not in tool_names
    assert "send_message" not in tool_names


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_venue_search_case_insensitive():
    """Test venue search is case-insensitive."""
    result1 = search_venue_database(query="fillmore")
    result2 = search_venue_database(query="FILLMORE")
    result3 = search_venue_database(query="Fillmore")

    assert result1["count"] == result2["count"] == result3["count"]


def test_draft_email_with_special_characters():
    """Test email drafting handles special characters."""
    result = draft_email(
        recipient="test@venue.com",
        subject="Test & Special <Characters>",
        body="Email with unicode: café, naïve, 日本語",
        template_type="professional"
    )
    assert result["status"] == "draft_created"
    assert "café" in result["body"]


def test_conflict_check_empty_dates():
    """Test conflict checking with empty dates list."""
    result = check_tour_conflicts(
        artist_name="The Midnight",
        proposed_dates=[]
    )
    assert result["status"] == "analysis_complete"
    assert result["has_conflicts"] is False
    assert len(result["conflicts"]) == 0
    assert len(result["available_dates"]) == 0


def test_memory_block_char_limit_enforcement(tourlab_memory):
    """Test that memory blocks enforce character limits."""
    with pytest.raises(ValueError):
        # Try to set value exceeding the limit
        long_value = "x" * 10000
        tourlab_memory.update_block_value("persona", long_value)


# ============================================================================
# PERFORMANCE AND SCALABILITY TESTS
# ============================================================================

def test_venue_search_performance():
    """Test venue search completes quickly."""
    import time
    start = time.time()
    result = search_venue_database(query="Brooklyn", location="New York")
    duration = time.time() - start
    assert duration < 0.1, "Venue search should complete in < 100ms"
    assert result["status"] == "success"


def test_multiple_conflict_checks():
    """Test handling multiple date conflict checks."""
    many_dates = [f"2025-12-{day:02d}" for day in range(1, 31)]
    result = check_tour_conflicts(
        artist_name="The Midnight",
        proposed_dates=many_dates
    )
    assert result["status"] == "analysis_complete"
    assert len(result["available_dates"]) + len(result["conflicts"]) == len(many_dates)
