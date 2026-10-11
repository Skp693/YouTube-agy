"""Stage 1: Topic Selector (topic_selector.py)

Researches currently popular or rising AI tools, chooses one clear practical angle,
and outputs a clean JSON file in topics/ with tool_name, angle, suggested_title,
key_points, and reason.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

from config.settings import settings
from config.logging_config import setup_logger

logger = setup_logger("topic_selector")

# Curated pool of high-demand 2026 AI tools for educational explainers
CURATED_AI_TOPICS = [
    {
        "tool_name": "Claude 3.7 & Artifacts",
        "angle": "Complete Beginner to Pro Guide for Interactive Prototyping",
        "suggested_title": "How to Build Full Apps with Claude 3.7 Artifacts (Step-by-Step 2026)",
        "key_points": [
            "Setting up Claude Projects and persistent system instructions",
            "Creating real-time interactive dashboards and React components",
            "Context window optimization and multi-turn iterative prompting",
            "Exporting artifacts to production-ready GitHub and web repositories"
        ],
        "reason": "Massive search volume for practical Claude use-cases beyond standard chat."
    },
    {
        "tool_name": "Google NotebookLM",
        "angle": "How to Turn 50+ Documents into an Interactive Podcast & Knowledge Base",
        "suggested_title": "Google NotebookLM: Master AI Research & Audio Overviews (2026 Guide)",
        "key_points": [
            "Importing PDFs, YouTube links, Google Docs, and web sources into notebooks",
            "Generating grounded citation-backed study guides and FAQ sheets",
            "Configuring conversational Audio Overviews for deep learning",
            "Best practices for preventing hallucinations in academic/technical research"
        ],
        "reason": "High viral interest in Google's audio overview feature and grounded research."
    },
    {
        "tool_name": "Cursor AI IDE",
        "angle": "10x Developer Productivity and Full Codebase Indexing",
        "suggested_title": "How to Code 10x Faster with Cursor AI (Complete Tutorial 2026)",
        "key_points": [
            "Setting up Cursor with local indexing (.cursorrules best practices)",
            "Mastering the Composer multi-file editing agent",
            "Using Cmd+K inline transformations and terminal automation",
            "Security and privacy settings for enterprise codebases"
        ],
        "reason": "Rapid adoption by software engineers, high YouTube audience retention."
    },
    {
        "tool_name": "Bolt.new",
        "angle": "Zero-Setup Full-Stack Web Development in the Browser",
        "suggested_title": "Build & Deploy Full-Stack Web Apps with Bolt.new in 10 Minutes",
        "key_points": [
            "In-browser Node.js WebContainers execution environment",
            "Full-stack prompt scaffolding with Next.js, Vite, and Tailwind",
            "Live debugging, error correction, and instant Supabase database integration",
            "One-click Netlify deployment and GitHub synchronization"
        ],
        "reason": "Great visual appeal for video demonstrations with immediate clickable results."
    },
    {
        "tool_name": "Perplexity AI & Deep Research",
        "angle": "Replacing Traditional Google Search with Grounded Pro Research",
        "suggested_title": "How to Use Perplexity AI for Deep Research (Complete Guide 2026)",
        "key_points": [
            "Focus modes: Academic, Writing, Wolfram, and YouTube filtering",
            "Using Collections to organize ongoing research workflows",
            "Prompt engineering for multi-step reasoning queries with source verification",
            "Exporting formatted reports and sharing collaborative research spaces"
        ],
        "reason": "Massive user transition from traditional search to AI research engines."
    }
]

def query_gemini_topic_research(prompt: str, retries: int = 3) -> Optional[Dict[str, Any]]:
    """Calls Gemini API with retries and exponential backoff to discover trending AI tool topics."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    model = settings.GEMINI_MODEL or "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.4
        }
    }

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=45) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini API attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)

    return None

def select_topic(
    tool_name: Optional[str] = None,
    angle: Optional[str] = None,
    project_id: Optional[str] = None
) -> Dict[str, Any]:
    """Selects or generates an optimal AI tool topic.
    
    Args:
        tool_name: Optional specific AI tool.
        angle: Optional angle or target audience.
        project_id: Optional unique project identifier.
        
    Returns:
        Dictionary containing topic data.
    """
    settings.ensure_directories()
    project_id = project_id or datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Custom tool explicitly passed
    if tool_name:
        logger.info(f"Using explicitly specified tool: {tool_name}")
        angle = angle or "Comprehensive Step-by-Step 2026 Guide"
        topic_data = {
            "id": project_id,
            "tool_name": tool_name,
            "angle": angle,
            "suggested_title": f"How to Use {tool_name} (Step-by-Step 2026 Guide)",
            "key_points": [
                f"Core overview and setup for {tool_name}",
                "Step-by-step feature breakdown and hands-on workflow",
                "Advanced techniques, common pitfalls, and efficiency tips",
                "Monetization models and real-world practical use cases"
            ],
            "reason": f"Custom user selection for {tool_name}."
        }
        return _persist_topic(topic_data)

    # 2. Check for pending topics in topics/backlog.json
    backlog_file = settings.TOPICS_DIR / "backlog.json"
    if backlog_file.exists():
        try:
            with open(backlog_file, "r", encoding="utf-8") as f:
                items = json.load(f)
            if items:
                raw_item = items.pop(0)
                # Resave remaining backlog
                with open(backlog_file, "w", encoding="utf-8") as f:
                    json.dump(items, f, indent=2)
                
                logger.info(f"Popped topic from backlog: {raw_item.get('tool_name')}")
                topic_data = {
                    "id": project_id,
                    "tool_name": raw_item.get("tool_name", "AI Tool"),
                    "angle": raw_item.get("angle", "Complete Step-by-Step Guide"),
                    "suggested_title": raw_item.get("title") or raw_item.get("suggested_title", f"How to Use {raw_item.get('tool_name')}"),
                    "key_points": raw_item.get("key_points") or raw_item.get("search_keywords", []),
                    "reason": raw_item.get("value_proposition") or raw_item.get("reason", "Queued in topic backlog")
                }
                return _persist_topic(topic_data)
        except Exception as e:
            logger.warning(f"Error reading topics backlog ({e}). Falling back to research.")

    # 3. AI Research via Gemini (if API key available)
    if settings.GEMINI_API_KEY:
        logger.info("Researching trending AI tools via Gemini API...")
        prompt = (
            "Analyze current trending, high-utility AI tools for creators, developers, or professionals. "
            "Select ONE high-demand AI tool with great practical value for an 8-12 minute YouTube educational video. "
            "Return valid JSON matching this exact structure: "
            "{\n"
            '  "tool_name": "Name of AI Tool",\n'
            '  "angle": "Practical angle or focus",\n'
            '  "suggested_title": "High CTR, SEO-friendly YouTube title (under 70 chars)",\n'
            '  "key_points": ["Point 1", "Point 2", "Point 3", "Point 4"],\n'
            '  "reason": "Why this video will attract high viewership and deliver value"\n'
            "}"
        )
        ai_res = query_gemini_topic_research(prompt)
        if ai_res and "tool_name" in ai_res:
            ai_res["id"] = project_id
            logger.info(f"Gemini selected topic: {ai_res['tool_name']}")
            return _persist_topic(ai_res)

    # 4. Deterministic curated selection based on epoch day
    day_index = int(datetime.now().timestamp() // 86400) % len(CURATED_AI_TOPICS)
    selected = dict(CURATED_AI_TOPICS[day_index])
    selected["id"] = project_id
    logger.info(f"Selected curated topic: {selected['tool_name']} ({selected['angle']})")
    return _persist_topic(selected)

def _persist_topic(data: Dict[str, Any]) -> Dict[str, Any]:
    """Saves topic dictionary to topics/<id>_topic.json."""
    output_path = settings.TOPICS_DIR / f"{data['id']}_topic.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    logger.info(f"Topic saved to {output_path}")
    data["saved_path"] = str(output_path)
    return data

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stage 1: Topic Selector")
    parser.add_argument("--tool", type=str, help="Specify AI tool name")
    parser.add_argument("--angle", type=str, help="Specify angle or target use-case")
    parser.add_argument("--project-id", type=str, help="Optional project ID")
    args = parser.parse_args()

    result = select_topic(tool_name=args.tool, angle=args.angle, project_id=args.project_id)
    print("\n--- Topic Selected ---")
    print(f"Tool Name:       {result['tool_name']}")
    print(f"Angle:           {result['angle']}")
    print(f"Suggested Title: {result['suggested_title']}")
    print(f"Saved:           {result['saved_path']}")

if __name__ == "__main__":
    main()
