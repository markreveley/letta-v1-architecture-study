#!/usr/bin/env python3
"""
Tour Management Email Agent - Letta V1 Architecture Example

This example demonstrates the letta_v1_agent architecture for music industry tour management:
- Native reasoning support for complex tour logistics
- Memory blocks for venue/artist knowledge
- Tool rules for email workflow management
- Simplified architecture (no heartbeats, no forced tool calls)

Use case: An agent that manages tour booking emails, tracks venue availability,
and maintains knowledge about artist requirements and venue specifications.
"""

import os
from typing import Dict, List, Optional
from letta_client import Letta


# ============================================================================
# CUSTOM TOOLS FOR TOUR MANAGEMENT
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
    # In production, this would query a real database
    # For demo purposes, we'll return simulated data
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
        "requires_approval": True  # Safety check before sending
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
    # Simulated existing tour dates
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
# TOOL REGISTRATION HELPER
# ============================================================================

def create_tour_management_tools(client: Letta) -> List[str]:
    """
    Create and register all tour management tools with the Letta server.

    Returns:
        List of tool IDs for the created tools
    """
    tools_to_create = [
        search_venue_database,
        draft_email,
        check_tour_conflicts,
        log_email_interaction
    ]

    tool_ids = []

    for tool_func in tools_to_create:
        try:
            # Create tool from function
            tool = client.tools.create(
                func=tool_func,
                tags=["tourlab", "email_workflow"],
                return_char_limit=2000
            )
            tool_ids.append(tool.id)
            print(f"✓ Created tool: {tool.name} (ID: {tool.id})")
        except Exception as e:
            print(f"✗ Error creating tool {tool_func.__name__}: {e}")

    return tool_ids


# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

def create_tourlab_agent(client: Letta, tool_ids: List[str]) -> str:
    """
    Create a tour management agent with v1 architecture.

    Args:
        client: Letta client instance
        tool_ids: List of tool IDs to attach to the agent

    Returns:
        Agent ID
    """
    # Define memory blocks for the agent
    memory_blocks = [
        {
            "label": "persona",
            "value": (
                "I am a professional tour management assistant specializing in booking "
                "and coordinating live music performances. I help with venue research, "
                "email communications, schedule management, and logistics coordination. "
                "I maintain detailed knowledge of venue specifications, artist requirements, "
                "and industry best practices."
            )
        },
        {
            "label": "human",
            "value": "Tour manager for multiple artists in electronic and indie music genres."
        },
        {
            "label": "venue_knowledge",
            "description": "Database of known venues with capacity, tech specs, and booking contacts",
            "value": (
                "Key Venues:\n"
                "- The Fillmore (SF): 1150 cap, full PA, booking@thefillmore.com\n"
                "- Brooklyn Steel (NYC): 1800 cap, D&B PA, bookings@bksteel.com\n"
                "- Red Rocks (CO): 9525 cap, outdoor amphitheater, events@redrocks.com"
            )
        },
        {
            "label": "artist_requirements",
            "description": "Technical and hospitality requirements for managed artists",
            "value": (
                "The Midnight: \n"
                "- Stage: Minimum 30x25ft\n"
                "- Tech: Full lighting rig, video wall capability\n"
                "- Hospitality: Private green room, catering for 8\n\n"
                "CHVRCHES:\n"
                "- Stage: Minimum 40x30ft\n"
                "- Tech: Advanced lighting, synth setup space\n"
                "- Hospitality: Separate dressing rooms, vegan catering"
            )
        },
        {
            "label": "email_workflow",
            "description": "Current state of email communications and pending tasks",
            "value": "No active email threads. Ready to begin outreach for 2025 winter tour."
        }
    ]

    # Create agent with letta_v1_agent architecture
    agent = client.agents.create(
        name="Tour Management Email Agent",
        agent_type="letta_v1_agent",  # Using v1 architecture
        model="openai/gpt-4o",  # Can also use reasoning models like o1
        embedding="openai/text-embedding-3-small",
        memory_blocks=memory_blocks,
        tool_ids=tool_ids,
        system="letta_v1",  # Use v1 system prompt
        description="Tour management agent for handling venue booking and email communications"
    )

    print(f"\n✓ Created agent: {agent.name}")
    print(f"  ID: {agent.id}")
    print(f"  Type: {agent.agent_type}")
    print(f"  Memory blocks: {len(memory_blocks)}")
    print(f"  Tools attached: {len(tool_ids)}")

    return agent.id


# ============================================================================
# EVALUATION SUITE
# ============================================================================

class TourAgentEvaluator:
    """Evaluation suite for tour management agent capabilities."""

    def __init__(self, client: Letta, agent_id: str):
        self.client = client
        self.agent_id = agent_id
        self.test_results = []

    def send_message(self, message: str, description: str = "") -> Dict:
        """Send a message and capture the response."""
        print(f"\n{'='*70}")
        print(f"TEST: {description}")
        print(f"{'='*70}")
        print(f"User: {message}\n")

        response = self.client.agents.messages.create(
            agent_id=self.agent_id,
            messages=[{"role": "user", "content": message}]
        )

        # Extract assistant messages
        assistant_messages = [
            msg for msg in response.messages
            if hasattr(msg, 'message_type') and msg.message_type == 'assistant_message'
        ]

        # Extract tool calls
        tool_calls = [
            msg for msg in response.messages
            if hasattr(msg, 'message_type') and msg.message_type == 'tool_call_message'
        ]

        for msg in assistant_messages:
            if hasattr(msg, 'content'):
                print(f"Assistant: {msg.content}\n")

        if tool_calls:
            print(f"Tools called: {len(tool_calls)}")
            for tc in tool_calls:
                if hasattr(tc, 'tool_call'):
                    print(f"  - {tc.tool_call.name}")

        return {
            "description": description,
            "message": message,
            "assistant_messages": assistant_messages,
            "tool_calls": tool_calls,
            "success": len(assistant_messages) > 0
        }

    def test_venue_search(self):
        """Test venue search capabilities."""
        result = self.send_message(
            "I need to find venues in New York with capacity around 1500-2000 for a show in December.",
            "Venue Search Test"
        )
        self.test_results.append(result)

    def test_conflict_checking(self):
        """Test tour schedule conflict detection."""
        result = self.send_message(
            "Check if The Midnight has any conflicts with shows on December 15th and 20th, 2025.",
            "Conflict Checking Test"
        )
        self.test_results.append(result)

    def test_email_drafting(self):
        """Test email drafting capabilities."""
        result = self.send_message(
            "Draft a professional email to Brooklyn Steel asking about availability for "
            "The Midnight on December 18th, 2025. Mention their technical requirements.",
            "Email Drafting Test"
        )
        self.test_results.append(result)

    def test_memory_recall(self):
        """Test memory block recall."""
        result = self.send_message(
            "What are CHVRCHES' technical requirements?",
            "Memory Recall Test"
        )
        self.test_results.append(result)

    def test_multi_step_workflow(self):
        """Test complex multi-step workflow."""
        result = self.send_message(
            "I need to book a show for CHVRCHES in Brooklyn in December. "
            "Find suitable venues, check for conflicts, and draft an inquiry email.",
            "Multi-Step Workflow Test"
        )
        self.test_results.append(result)

    def run_all_tests(self):
        """Run the complete evaluation suite."""
        print("\n" + "="*70)
        print("TOUR MANAGEMENT AGENT - EVALUATION SUITE")
        print("="*70)

        self.test_venue_search()
        self.test_conflict_checking()
        self.test_email_drafting()
        self.test_memory_recall()
        self.test_multi_step_workflow()

        # Summary
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)
        total = len(self.test_results)
        successful = sum(1 for r in self.test_results if r["success"])
        print(f"Total tests: {total}")
        print(f"Successful: {successful}")
        print(f"Failed: {total - successful}")
        print(f"Success rate: {(successful/total)*100:.1f}%")

        return self.test_results


# ============================================================================
# MAIN EXAMPLE
# ============================================================================

def main():
    """Main example demonstrating tour management agent with v1 architecture."""

    # Check for API key
    api_key = os.environ.get("LETTA_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: Please set LETTA_API_KEY or OPENAI_API_KEY environment variable")
        return

    # Initialize Letta client
    # For hosted Letta: client = Letta(token=api_key)
    # For local server: client = Letta(base_url="http://localhost:8283")
    client = Letta(base_url="http://localhost:8283")

    print("="*70)
    print("TOUR MANAGEMENT AGENT - LETTA V1 ARCHITECTURE EXAMPLE")
    print("="*70)

    try:
        # Step 1: Create tour management tools
        print("\n[1/3] Creating tour management tools...")
        tool_ids = create_tour_management_tools(client)

        # Step 2: Create the agent
        print("\n[2/3] Creating tour management agent...")
        agent_id = create_tourlab_agent(client, tool_ids)

        # Step 3: Run evaluation suite
        print("\n[3/3] Running evaluation suite...")
        evaluator = TourAgentEvaluator(client, agent_id)
        results = evaluator.run_all_tests()

        # Interactive mode (optional)
        print("\n" + "="*70)
        print("INTERACTIVE MODE")
        print("="*70)
        print("You can now interact with the agent. Type 'exit' to quit.\n")

        while True:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                break

            response = client.agents.messages.create(
                agent_id=agent_id,
                messages=[{"role": "user", "content": user_input}]
            )

            for msg in response.messages:
                if hasattr(msg, 'message_type') and msg.message_type == 'assistant_message':
                    if hasattr(msg, 'content'):
                        print(f"\nAssistant: {msg.content}\n")

    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup (optional - comment out if you want to keep the agent)
        # print(f"\nCleaning up agent {agent_id}...")
        # client.agents.delete(agent_id)
        print("\nDone!")


if __name__ == "__main__":
    main()
