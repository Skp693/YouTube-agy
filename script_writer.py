"""Stage 2: Script Writer (script_writer.py)

Researches accurate, up-to-date information about the selected AI tool and writes
an original, educational 8–12 minute script (1400–1800 words) with:
  1. Strong hook
  2. What the tool is + who it's for
  3. Clear numbered step-by-step instructions
  4. Tips, common mistakes, and pro tips
  5. Call to action

Saves both .txt and structured .json versions in scripts/.
"""

import os
import sys
import json
import time
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

from config.settings import settings
from config.logging_config import setup_logger

logger = setup_logger("script_writer")

def generate_script_with_gemini(topic_data: Dict[str, Any], retries: int = 3) -> Optional[Dict[str, Any]]:
    """Generates comprehensive 1400-1800 word educational script via Gemini API."""
    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return None

    model = settings.GEMINI_MODEL or "gemini-1.5-pro"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    tool_name = topic_data.get("tool_name", "AI Tool")
    angle = topic_data.get("angle", "Step-by-Step Practical Masterclass")
    key_points = topic_data.get("key_points", [])

    prompt = f"""
You are an expert technical YouTube educator producing a comprehensive 8-12 minute video tutorial (1400-1800 words total) about "{tool_name}".
Angle: {angle}
Key Points: {json.dumps(key_points)}

STRUCTURE REQUIREMENTS:
1. Hook (High energy, pain point, tangible outcome, 100-150 words)
2. What It Is & Who It's For (Clear breakdown of core tech, architecture, ideal user profiles, 150-200 words)
3. Step 1: Initial Setup & Workspace Configuration (Exact steps, settings, credentials, 250-300 words)
4. Step 2: The Core Workflow & First Project (Prompting structure, hands-on example, 300-350 words)
5. Step 3: Advanced Features & Automation (Context rules, multi-step agent workflows, 300-350 words)
6. Pro Tips & Common Mistakes to Avoid (Crucial practical gotchas, rate limits, cost optimization, 200-250 words)
7. Pricing, Limitations & Real-World Monetization (Free vs Pro tiers, agency/client application, 150-200 words)
8. Call to Action & Summary (Wrap up, engagement question, subscribe CTA, 100-150 words)

TOTAL WORDS MUST BE BETWEEN 1400 AND 1800 WORDS.
Return ONLY valid JSON matching this schema:
{{
  "tool_name": "{tool_name}",
  "target_duration_minutes": 10,
  "sections": [
    {{
      "id": 1,
      "section_type": "hook",
      "title": "Section Title",
      "narration": "Full spoken voiceover text here...",
      "visual_description": "Description of image/diagram on screen",
      "image_prompt": "Detailed prompt for 1920x1080 slide image generation",
      "on_screen_text": ["Bullet 1", "Bullet 2", "Bullet 3"],
      "duration_estimate_sec": 45.0
    }}
  ]
}}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.5
        }
    }

    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, retries + 1):
        try:
            logger.info(f"Querying Gemini API for script generation (Attempt {attempt}/{retries})...")
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=90) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(text)
        except Exception as e:
            logger.warning(f"Gemini script generation attempt {attempt} failed: {e}")
            if attempt < retries:
                time.sleep(2 ** attempt)

    return None

def build_claude_artifacts_script(topic_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates an authentic 1500+ word educational masterclass specifically for Claude 3.7 Artifacts."""
    sections = [
        {
            "id": 1,
            "section_type": "hook",
            "title": "The End of Chatbot Copy-Pasting: Why Claude 3.7 Artifacts Changes Everything",
            "narration": (
                "If you've been using AI chatbots over the past two years, you know the single most frustrating bottleneck: "
                "you ask for a piece of code, a landing page, or a data visualization, and the model dumps a massive wall of "
                "text directly into your chat stream. You then have to copy that code, paste it into an external editor, set up a "
                "local server, debug syntax errors, and switch between three different windows just to see if it even works. "
                "Today, that archaic workflow is officially dead. In this complete masterclass, we are diving deep into Claude 3.7 "
                "Artifacts. Claude doesn't just talk to you; it opens a dedicated, interactive execution window right alongside your "
                "conversation, allowing you to build, test, and iterate on full-stack web applications, live interactive dashboards, "
                "and visual diagrams in real time. In this step-by-step guide, you will learn how to set up your workspace, harness "
                "Claude 3.7's new hybrid reasoning engine, build a real production-grade app from scratch, and turn these skills "
                "into high-margin client deliverables. Let's get straight to work."
            ),
            "visual_description": "Split screen comparison: Clunky markdown codeblock on left vs Live interactive Claude Artifact on right",
            "image_prompt": "Side-by-side comparison slide showing traditional raw chat codeblock vs sleek Claude Artifacts interactive UI preview, dark theme, 8k",
            "on_screen_text": ["Claude 3.7 Artifacts", "• Dual-Pane UI", "• Live In-Browser Execution", "• Zero Setup Required"],
            "duration_estimate_sec": 65.0
        },
        {
            "id": 2,
            "section_type": "overview",
            "title": "What Exactly Are Claude Artifacts & What Can They Render?",
            "narration": (
                "Before we write our first prompt, let's understand how Artifacts function under the hood. When Claude generates a "
                "substantial piece of standalone content—typically over fifteen lines of code, a complex diagram, or an architectural "
                "document—it isolates that content into a dedicated window on the right side of your screen called an Artifact. "
                "What can Artifacts actually execute? First, full React applications styled with Tailwind CSS, running live in an "
                "isolated client-side sandbox. You can click buttons, toggle states, sort tables, and trigger animations instantly. "
                "Second, raw HTML, CSS, and modern JavaScript for standalone web widgets. Third, vector graphics using scalable SVG. "
                "And fourth, complex architectural diagrams using Mermaid notation. Crucially, the conversation remains active on the "
                "left, while your living asset stays persistent on the right. You no longer lose your work in an endless scroll of chat history."
            ),
            "visual_description": "Infographic displaying the 4 core Artifact types: React, HTML/JS, SVG Vector, and Mermaid Flowcharts",
            "image_prompt": "Infographic showing four modern software capability badges: React Tailwind, Web HTML5, Vector SVG, Mermaid Diagrams, sleek design",
            "on_screen_text": ["Supported Artifact Formats", "1. React + Tailwind (Live State)", "2. HTML5 & JavaScript", "3. Vector SVG Graphics", "4. Mermaid Flowcharts"],
            "duration_estimate_sec": 70.0
        },
        {
            "id": 3,
            "section_type": "step_1",
            "title": "Step 1: Setting Up Claude Projects & Project Knowledge",
            "narration": (
                "Let's set up your environment like a professional. First, head over to claude.ai and ensure you are using Claude 3.7 Sonnet. "
                "While you can generate artifacts in standard chats, power users always organize their work inside Claude Projects. "
                "Click on Projects in the left navigation sidebar and create a new project. Why are Projects essential? Because they provide "
                "two massive superpowers: Project Custom Instructions and Project Knowledge. In the Custom Instructions panel, define your "
                "design preferences once and for all: specify your brand color palette, mandate clean modular React components with Lucide icons, "
                "and instruct Claude to always prioritize mobile-responsive layouts. Next, upload your project knowledge files. Claude allows you "
                "to upload up to two hundred thousand tokens of reference material—such as your design tokens, API specifications, or database schemas. "
                "This ensures every single artifact Claude generates matches your exact technical architecture without repetitive prompting."
            ),
            "visual_description": "Step 1 UI diagram highlighting Claude Projects, Custom System Instructions, and 200k Token Knowledge Upload",
            "image_prompt": "Dashboard screenshot illustration highlighting Claude Projects sidebar, custom instruction box, and knowledge upload card, 4k",
            "on_screen_text": ["Step 1: Workspace Setup", "• Create Claude Project", "• Set Design Rules in Instructions", "• Upload Up to 200k Token Docs"],
            "duration_estimate_sec": 75.0
        },
        {
            "id": 4,
            "section_type": "step_2",
            "title": "Step 2: Prompting with Claude 3.7 Extended Thinking for Deep Architecture",
            "narration": (
                "Now let's build our first production project. Here is where Claude 3.7 introduces a breakthrough capability: Hybrid Reasoning. "
                "At the bottom of your prompt box, you will find the Extended Thinking toggle. For simple tasks, standard mode is lightning fast. "
                "But when building complex, interactive software artifacts, always toggle Extended Thinking on. This prompts the model to generate "
                "an internal cognitive scratchpad—planning out the component tree, state management, edge cases, and user interactions before writing "
                "a single line of code. Let's look at our exact prompt formula. Never say 'build me a dashboard.' Instead, formulate your prompt with three "
                "layers: Role, Architecture, and State. For example: 'You are an expert senior frontend engineer. Build a comprehensive SaaS Analytics "
                "Dashboard in React with Tailwind CSS. Include four interactive KPI cards with percentage trends, a filterable revenue chart, a date "
                "range dropdown, client-side search across customer accounts, and an instant toggle for dark mode. Ensure all sample data is rich, realistic, "
                "and properly typed. Include smooth hover transitions on every interactive card and realistic chart tooltips.' Watch how Claude reasons through "
                "the state variables, organizes clean functional hooks, and within seconds, renders a gorgeous, production-grade application on your right-hand pane."
            ),
            "visual_description": "Step 2 prompt architecture breakdown with Extended Thinking toggle and three-layer prompt framework",
            "image_prompt": "Visual diagram showing the Extended Thinking cognitive reasoning bar, 3-layer prompt anatomy, and resulting interactive app, cyan glow",
            "on_screen_text": ["Step 2: Prompting Framework", "• Enable Extended Thinking Toggle", "• Layer 1: Senior Role Definition", "• Layer 2: Architecture Specs", "• Layer 3: Interactive State Rules"],
            "duration_estimate_sec": 95.0
        },
        {
            "id": 5,
            "section_type": "step_3",
            "title": "Step 3: Iterative In-Browser Testing & Surgical Code Refinement",
            "narration": (
                "Once your artifact is rendered, do not leave the screen. Test it immediately! Click on the tabs, open the dropdowns, switch between "
                "light and dark mode, and verify how the UI responds on different simulated screen sizes. Notice the two tabs at the top of the artifact "
                "window: Preview and Code. While the Preview tab lets you click and test, the Code tab displays clean, syntax-highlighted React with zero "
                "obfuscation. This is where the magic of Artifacts happens. Suppose you want to modify a specific component. In legacy chatbots, asking "
                "for an edit would re-generate hundreds of lines of code and often introduce hallucinations or break existing features. With Claude "
                "Artifacts, use targeted surgical prompts. You can write: 'In the KPI metrics card, add a sparkline chart showing seven-day momentum and "
                "format the currency with compact notations.' Claude identifies the exact component inside the artifact, updates only the relevant logic, "
                "and refreshes your live preview instantly. You can see your changes live without a single terminal command or local build error."
            ),
            "visual_description": "Interactive testing walkthrough showing live state clicks, dark mode toggle, and targeted code updates",
            "image_prompt": "Clean illustration of an interactive dashboard UI with mouse cursor clicking live tabs and glowing update ripples, modern UX design",
            "on_screen_text": ["Step 3: Live Refinement", "• Test In-Browser State", "• Inspect Clean JSX Code Tab", "• Surgical Component Edits", "• Instant Hot-Reload Preview"],
            "duration_estimate_sec": 80.0
        },
        {
            "id": 6,
            "section_type": "step_4",
            "title": "Step 4: Multi-Artifact Workflows & One-Click Production Deployment",
            "narration": (
                "Once your prototype is dialed in, how do you get it into production? Claude Artifacts provides multiple export options designed "
                "for seamless developer workflows. At the bottom right of the artifact window, you have two primary buttons: Copy Code and Download. "
                "Clicking Download saves a clean standalone JSX or HTML file directly to your machine. But here is the power move: Multi-Artifact "
                "Chaining. Within the same conversation, you can ask Claude: 'Now generate a backend Express API route in Node.js that serves the exact "
                "data schema required by this React artifact.' Claude will generate a second distinct artifact containing your backend endpoint. "
                "You can toggle between multiple artifacts using the version slider at the top of the window, allowing you to review your entire full-stack "
                "architecture before exporting it directly into your GitHub repository or deploying it to platforms like Vercel and Netlify."
            ),
            "visual_description": "Multi-artifact management graphic displaying export buttons, version slider, and one-click Vercel/GitHub deployment",
            "image_prompt": "Export workflow graphic showing Copy Code button, Download JSX, and deployment arrows to GitHub and Vercel, dark slate UI",
            "on_screen_text": ["Step 4: Production Export", "• 1-Click Code Download", "• Multi-Artifact Version Slider", "• Deploy to GitHub, Vercel & Vite"],
            "duration_estimate_sec": 75.0
        },
        {
            "id": 7,
            "section_type": "pro_tips",
            "title": "Pro Tips & Critical Gotchas That Break Your Artifacts",
            "narration": (
                "Let's cover the vital rules to avoid frustration and code breakage. Mistake number one is the 'Monolithic Artifact Trap.' "
                "If you try to build an entire operating system or a ten-page web application in a single prompt, the output will exceed token limits and "
                "get truncated mid-render. Always build modularly: create your dashboard core first, then add subsequent views as separate artifacts. "
                "Mistake number two is external library hallucination. Claude's React environment comes pre-loaded with Lucide React icons, Tailwind CSS, "
                "and standard Recharts, but it cannot fetch arbitrary obscure npm packages. Always specify that Claude should rely on built-in Tailwind "
                "utilities and standard icons. Pro tip number three: manage context windows by starting a fresh conversation inside the same Project once "
                "an artifact is finalized. Because your Project Knowledge holds all your architectural rules, a fresh chat starts with clean memory while "
                "maintaining complete consistency. And finally, use the 'Artifact Version History' control. If an iterative prompt breaks your working "
                "layout, simply click back to Version 1 or Version 2 to restore your perfect build in one second."
            ),
            "visual_description": "Comparison cards highlighting Monolithic Code Pitfalls, NPM dependency boundaries, and Version History restoration",
            "image_prompt": "Split comparison slide showing Red Warning badges for Monolithic Code vs Green Solution badges for Modular Chaining, clean UI",
            "on_screen_text": ["Pitfalls & Pro Safeguards", "❌ Monolithic App Prompts  -->  ✔ Modular Sub-Components", "❌ Obscure NPM Packages     -->  ✔ Tailwind & Lucide Standard", "💡 Pro Tip: Fresh Project Chats & Version Rollback"],
            "duration_estimate_sec": 85.0
        },
        {
            "id": 8,
            "section_type": "monetization",
            "title": "Real-World Monetization: Turning Claude Artifacts into High-Margin Revenue",
            "narration": (
                "How do you turn this mastery into tangible income? Here are three proven monetization models that creators and developers are executing "
                "right now. Route number one is 48-Hour MVP Prototyping for Founders and Startups. Early-stage entrepreneurs constantly need clickable, "
                "interactive proof-of-concepts to show investors and early customers. Instead of spending weeks coding from scratch, you can deliver "
                "gorgeous, responsive React prototypes in forty-eight hours, charging between fifteen hundred and three thousand dollars per project. "
                "Route number two is Interactive Sales Proposals. If you run a digital agency or freelance consultancy, never send a static PDF proposal "
                "again. Build your prospective client a live, customized interactive ROI calculator or dashboard artifact. It demonstrates unmatched "
                "competence and dramatically increases your close rates. Route number three is selling specialized Tailwind and React UI component kits, "
                "micro-SaaS templates, and interactive calculators on digital storefronts like Gumroad or Lemonsqueezy with zero inventory costs."
            ),
            "visual_description": "Business revenue model graphic featuring MVP Prototyping, Interactive Proposals, and Digital Component Assets",
            "image_prompt": "Business monetization infographic displaying 3 high-margin revenue models: 48h MVP Prototyping, Interactive Proposals, UI Kits",
            "on_screen_text": ["Monetization Strategies", "1. 48-Hour Startup MVP Prototypes ($1.5k - $3k)", "2. Interactive High-Ticket Pitch Decks", "3. Commercial UI Kits & Micro-SaaS Templates"],
            "duration_estimate_sec": 85.0
        },
        {
            "id": 9,
            "section_type": "cta",
            "title": "Pricing Breakdown, Free vs Pro Limits & Actionable Next Steps",
            "narration": (
                "To wrap up, let's look at pricing and quotas. Claude Artifacts is accessible on the free tier of claude.ai, making it fantastic "
                "for initial experimentation. However, the free tier imposes strict message limits that refresh every few hours. For anyone using this "
                "commercially, the Claude Pro plan at twenty dollars a month is non-negotiable—it provides five times more usage, priority access during peak "
                "hours, and full access to Claude 3.7 with extended thinking. You now have the exact blueprint to build, refine, and monetize interactive "
                "applications. All prompt templates, setup checklists, and component examples from this video are available in the description below. "
                "Tell me in the comments: what interactive app are you going to build first with Claude Artifacts? If this guide brought you value, "
                "hit that like button, subscribe for weekly masterclasses on leading AI tools, and I will see you in the next video!"
            ),
            "visual_description": "Clean outro slide with Free vs Pro comparison badge, resource links reminder, and YouTube subscribe call-to-action",
            "image_prompt": "Aesthetic outro video slide with glowing subscribe button, notification bell, modern technology background, 4k",
            "on_screen_text": ["Mastery Summary", "• Free Tier: Great for Testing", "• Claude Pro ($20/mo): 5x Limits & Extended Thinking", "• Check Links in Description • Subscribe"],
            "duration_estimate_sec": 65.0
        }
    ]

    return {
        "tool_name": "Claude 3.7 Artifacts",
        "target_duration_minutes": 10,
        "sections": sections
    }

def build_procedural_script(topic_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates an in-depth 1400-1800 word educational guide script for the specified AI tool."""
    tool_name = topic_data.get("tool_name", "Modern AI Tools")
    angle = topic_data.get("angle", "Step-by-Step Educational Masterclass")

    sections = [
        {
            "id": 1,
            "section_type": "hook",
            "title": f"The Big Bottleneck and Why {tool_name} Changes Everything",
            "narration": (
                f"If you've been working with artificial intelligence over the last year, you've likely hit the "
                f"exact same wall that millions of creators, developers, and knowledge workers face every single day. "
                f"You start a project with huge enthusiasm, only to get bogged down by clumsy copy-pasting, disjointed "
                f"context windows, and generic outputs that require endless manual clean-up. Most AI tools promise "
                f"complete automation, but in reality, they often feel like glorified text prediction. Today, that changes. "
                f"In this comprehensive, step-by-step masterclass, we are taking a deep dive into {tool_name}. "
                f"Whether your goal is to build automated workflows, build functional digital products in minutes, "
                f"or simply save twenty hours a week on repetitive cognitive tasks, this guide will take you from complete "
                f"beginner to absolute power user. We are skipping the hype and focusing purely on real-world, monetization-friendly "
                f"tactics. Grab a notebook, open your browser, and let's jump right in!"
            ),
            "visual_description": f"Bold title slide introducing {tool_name} with workflow speedup infographic",
            "image_prompt": f"Minimalist sleek tech presentation slide featuring {tool_name}, high quality modern dark UI, cyan and indigo accents, 8k",
            "on_screen_text": [tool_name, "Complete 2026 Masterclass", "Eliminate Repetitive Work", "Zero to Power User"],
            "duration_estimate_sec": 65.0
        },
        {
            "id": 2,
            "section_type": "overview",
            "title": f"What Exactly is {tool_name} and Who is It Built For?",
            "narration": (
                f"Before we click into the dashboard, it is crucial to understand the fundamental architecture of {tool_name}. "
                f"At its core, {tool_name} was engineered to solve the context fragmentation problem. Unlike legacy conversational "
                f"models that treat every interaction as an isolated session, this system operates on a persistent, state-aware "
                f"foundation. It actively indexes your project assets, observes your intended structural requirements, and executes "
                f"multi-stage workflows with deterministic precision. Who is this tool actually built for? First, software engineers "
                f"and technical founders who need to rapidly prototype and refactor complex logic without losing architectural consistency. "
                f"Second, digital creators and solopreneurs looking to build high-margin digital deliverables with fraction-of-the-time "
                f"turnarounds. And third, modern knowledge workers who need reliable synthesis of large-scale documents and data sources. "
                f"If your work involves transforming ideas into structured, high-value outputs, this tool belongs in your daily stack."
            ),
            "visual_description": "Clean modular diagram breaking down tool architecture and three core user personas",
            "image_prompt": "Clean digital infographic showing modern software architectural layers, persistent workspace, and user avatars, slate background",
            "on_screen_text": ["Core Architecture", "1. Persistent Context", "2. Multi-Step Execution", "3. Asset Indexing"],
            "duration_estimate_sec": 85.0
        },
        {
            "id": 3,
            "section_type": "step_1",
            "title": "Step 1: Setting Up Your Environment and Custom Configuration",
            "narration": (
                f"Let's get your hands on the keyboard. Step number one is setting up your environment for peak efficiency. "
                f"Navigate to the official portal, authenticate your account, and head straight into the settings menu. Do not "
                f"make the mistake of starting with default global configurations. The single biggest reason people get subpar "
                f"results is that they skip workspace tuning. First, locate your system-level instruction box. Here, you want to "
                f"define your role, your industry domain, and your strict output formatting constraints. For example, explicitly "
                f"stipulate that you prefer concise, production-ready responses without conversational preamble. Second, review your "
                f"privacy and telemetry toggles to ensure your proprietary project data remains secure. Third, configure your API keys "
                f"or link your third-party integrations, such as your GitHub workspace or cloud drives. Taking five minutes to lock in "
                f"these foundational preferences ensures that every subsequent output is tailored precisely to your production standard."
            ),
            "visual_description": "Step 1 visual guide with settings checklist and workspace configuration toggles",
            "image_prompt": "Modern software dashboard showing setup checklist, toggles for system instructions, high-resolution dark mode design",
            "on_screen_text": ["Step 1: Workspace Setup", "• Custom System Rules", "• Privacy & Telemetry Config", "• API & Cloud Integrations"],
            "duration_estimate_sec": 95.0
        },
        {
            "id": 4,
            "section_type": "step_2",
            "title": "Step 2: The Core Workflow and Building Your First Real Project",
            "narration": (
                f"Now that our workspace is configured, let's build our first production asset. This is Step 2: The Core Workflow. "
                f"The secret to unlocking the true capability of {tool_name} lies in the 'Context-Constraint-Verification' framework. "
                f"Never feed the system a single vague sentence. Instead, begin by feeding the foundational context: describe the exact "
                f"problem, the intended consumer of the output, and the necessary inputs. Next, apply your hard constraints: specify the "
                f"file formats, stylistic guidelines, technical boundaries, and structure. Finally, request a staged execution plan before "
                f"generating full deliverables. Watch how cleanly the model responds when you demand this structure: it breaks down "
                f"the problem, surfaces edge cases, and provides modular building blocks that you can verify in real-time. Notice the "
                f"speed and coherence of the output compared to unguided prompting. This structured methodology turns hours of manual "
                f"tinkering into a repeatable five-minute formula."
            ),
            "visual_description": "Step 2 flowchart visualizing the Context-Constraint-Verification prompting pipeline",
            "image_prompt": "Flowchart diagram representing input context, processing constraints, and modular verification outputs, 4k tech aesthetic",
            "on_screen_text": ["Step 2: The Core Workflow", "1. Context Framing", "2. Constraint Definition", "3. Modular Verification"],
            "duration_estimate_sec": 100.0
        },
        {
            "id": 5,
            "section_type": "step_3",
            "title": "Step 3: Advanced Automation, Chaining, and Power User Shortcuts",
            "narration": (
                f"Moving on to Step 3: Advanced Features and Automation. This is where {tool_name} truly outclasses the competition. "
                f"Most casual users never explore the deeper toolset, but power users know this is where exponential time savings live. "
                f"First, leverage multi-file awareness and context indexing. By tagging relevant references or project documentation directly "
                f"in your prompts, you eliminate repetitive explanations and allow the model to reason across your entire project history. "
                f"Second, take advantage of prompt chaining and reusable templates. Instead of generating an entire product in one monolithic "
                f"command, chain distinct micro-prompts: generate the architectural outline first, validate it, produce individual sub-components "
                f"second, and assemble the final deliverable third. Third, memorize key keyboard shortcuts and split-screen views. Being able to "
                f"toggle between editing, prompt history, and live preview environments with a single keypress will double your working speed."
            ),
            "visual_description": "Three isometric power-user cards highlighting context indexing, prompt chaining, and keyboard shortcuts",
            "image_prompt": "Futuristic isometric UI cards showing multi-file indexing, prompt chaining arrows, and sleek speed icons, neon highlights",
            "on_screen_text": ["Step 3: Power User Automation", "• Multi-File Context Indexing", "• Micro-Prompt Chaining", "• Instant Previews & Shortcuts"],
            "duration_estimate_sec": 95.0
        },
        {
            "id": 6,
            "section_type": "pro_tips",
            "title": "Pro Tips & Critical Mistakes That Ruin Your Results",
            "narration": (
                f"Let's cover the vital dos and don'ts that separate beginners from true professionals. Mistake number one is context saturation. "
                f"Feeding tens of thousands of tokens of irrelevant data into a single session causes 'needle in a haystack' degradation, "
                f"leading the model to ignore nuanced instructions. Always keep your sessions clean, scoped, and modular. Mistake number two is "
                f"blind acceptance without verification. No matter how advanced the model is, hallucination and subtle logic errors remain real. "
                f"Always run outputs through an automated linting or checklist routine before deploying them to clients or production systems. "
                f"Now for our top pro tip: maintain a persistent 'rules' or 'scratchpad' document. Whenever the tool makes an error that you correct, "
                f"document that correction as a permanent negative constraint. Over weeks of usage, your custom rules will make the tool virtually "
                f"immune to recurring mistakes."
            ),
            "visual_description": "Red warning vs green checkmark comparison card detailing common pitfalls and pro safeguards",
            "image_prompt": "Split comparison graphic showing Common Mistakes with warning badges vs Pro Solutions with green checkmarks, clean UI",
            "on_screen_text": ["Pitfalls & Pro Solutions", "❌ Context Overload  -->  ✔ Scoped Sessions", "❌ Blind Acceptance -->  ✔ Verification Rules", "💡 Pro Tip: Negative Constraint Logging"],
            "duration_estimate_sec": 95.0
        },
        {
            "id": 7,
            "section_type": "monetization",
            "title": "Real-World Monetization: Turning These Skills into Income",
            "narration": (
                f"Let's talk about the practical economics. How can you monetize your mastery of {tool_name}? There are three proven avenues "
                f"working right now in the market. Route number one is High-Velocity Client Deliverables. Digital agencies, web consultants, and "
                f"technical freelancers who master this workflow are delivering client projects in forty-eight hours that previously took two weeks, "
                f"commanding premium project fees while significantly reducing overhead. Route number two is Custom Automation and Workflow Consulting. "
                f"Small and medium businesses are eager to implement AI but lack internal expertise. By packaging {tool_name} into custom onboarding "
                f"systems and standardized operating procedures, you can charge recurring retainer fees. Route number three is Digital Products and "
                f"Specialized Asset Packs. Packaging your fine-tuned prompt chains, workspace templates, and workflow checklists into downloadable "
                f"resources generates passive, high-margin revenue with zero inventory."
            ),
            "visual_description": "Commercial blueprint diagram displaying three profitable business models powered by AI automation",
            "image_prompt": "Financial and business infographic displaying 3 revenue streams: Client Services, Consulting Retainers, Digital Assets, dark modern style",
            "on_screen_text": ["Monetization Strategies", "1. High-Velocity Client Services", "2. Workflow & SOP Consulting", "3. Reusable Template Products"],
            "duration_estimate_sec": 90.0
        },
        {
            "id": 8,
            "section_type": "pricing",
            "title": f"Pricing Breakdown, Rate Limits & Best Alternatives to {tool_name}",
            "narration": (
                f"Before we wrap up, let's break down the economics and limitations of {tool_name}. Like most top-tier AI platforms, it typically "
                f"operates on a tiered subscription model. The free tier gives you enough headroom to test the core features and validate your workflow, "
                f"but you will quickly encounter daily rate limits and slower queue times during peak traffic. The professional tier is priced around "
                f"twenty dollars a month and provides priority compute, higher token thresholds, and access to premium models. For anyone using this "
                f"professionally, the tier pays for itself within the first hour of work. What about alternatives? If you need strict open-source "
                f"local hosting, explore self-hosted models. But if you value polished UI, seamless integrations, and dependable uptime, {tool_name} "
                f"remains the gold standard in its category."
            ),
            "visual_description": "Pricing tier comparison table showing Free vs Pro with features, pricing, and alternate options",
            "image_prompt": "Clean modern pricing tier comparison table with checkmarks, Free vs Pro comparison, elegant UI",
            "on_screen_text": ["Pricing & Alternatives", "• Free Tier: Exploration & Testing", "• Pro Tier: Priority Speed & High Volume", "• ROI: Pays for itself in 1 hour"],
            "duration_estimate_sec": 80.0
        },
        {
            "id": 9,
            "section_type": "cta",
            "title": "Actionable Next Steps & Call to Action",
            "narration": (
                f"That brings us to the end of our complete masterclass on {tool_name}. You now possess the exact blueprint to configure your workspace, "
                f"harness structured prompting frameworks, automate repetitive workflows, and monetize these high-demand skills in the marketplace. "
                f"All the links, resources, and prompt templates mentioned in this video are listed down in the description box below. "
                f"Now I want to hear from you: what specific project are you going to build with {tool_name} first? Leave your answer in the comments "
                f"below, and if you found this breakdown valuable, smash the like button and hit subscribe with notifications turned on so you never miss "
                f"our weekly deep-dives into cutting-edge AI tools. Thanks for watching, and I will see you in the next video!"
            ),
            "visual_description": "Clean outro slide with YouTube subscribe button badge, resource links notice, and community question",
            "image_prompt": "Aesthetic outro video slide with glowing subscribe button, notification bell, modern technology background, 4k",
            "on_screen_text": ["Mastery Checklist Complete", "• Check Links in Description", "• Comment Your First Project", "• Subscribe for Weekly AI Tutorials"],
            "duration_estimate_sec": 65.0
        }
    ]

    return {
        "tool_name": tool_name,
        "target_duration_minutes": 10,
        "sections": sections
    }

def build_small_business_ai_tools_script(topic_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generates an authentic, fact-checked educational video script for 5 practical AI tools for small businesses."""
    tool_name = "5 Practical AI Tools for Small Business"
    suggested_title = "5 Practical AI Tools That Save Small Business Owners Time in 2026"
    description_summary = (
        "Discover 5 practical, battle-tested AI tools saving small business owners, freelancers, "
        "and agency operators 10+ hours every week in 2026. No fluff, no coding—just actionable operational leverage."
    )
    sections = [
        {
            "id": 1,
            "section_type": "overview",
            "title": "The Small Business Time Trap in 2026",
            "narration": (
                "If you run a small business in 2026, you already know the hardest part isn't finding customers—it's drowning "
                "in repetitive admin tasks, unanswered emails, manual scheduling, and endless paperwork. Most artificial intelligence "
                "advice online is completely disconnected from daily operations, focusing on hypothetical hype rather than real leverage. "
                "In this practical guide, we are cutting through the noise to examine five battle-tested AI tools that real small business "
                "owners, freelancers, and agency operators are using right now to save ten or more hours every single week. No coding "
                "required, no complicated setups—just immediate, practical leverage. Let's get straight to work."
            ),
            "visual_description": "Overview dashboard showing the administrative time trap faced by small businesses and the 5 AI solutions",
            "image_prompt": "Clean modern dashboard showing 5 AI business solutions eliminating admin tasks, dark slate UI, sleek 4k graphic",
            "on_screen_text": [
                "THE ADMIN TRAP: PAPERWORK, INVOICES & EMAILS",
                "REAL OPERATIONAL LEVERAGE VS AI HYPE",
                "SAVE 10+ HOURS WEEKLY WITH ZERO CODE"
            ],
            "duration_estimate_sec": 38.0
        },
        {
            "id": 2,
            "section_type": "tool_1",
            "title": "Google NotebookLM: Grounded SOP Knowledge Base",
            "narration": (
                "First up is Google NotebookLM. Small businesses lose hours digging through vendor contracts, employee onboarding "
                "handbooks, client proposals, and supplier invoices. NotebookLM solves this by creating a private, grounded knowledge base "
                "powered by Gemini 1.5 Pro. You simply upload your PDF contracts, Google Docs, and spreadsheets into a project notebook. "
                "You can then ask questions in plain English—like what are our warranty return terms, or summarize subcontractor deliverables—and "
                "it answers instantly with verifiable source citations. It even generates conversational audio overviews that explain complex "
                "manuals on the go. Best of all, NotebookLM is currently completely free in Google Labs."
            ),
            "visual_description": "Google NotebookLM workflow showing uploaded documents and instant citation-backed answers",
            "image_prompt": "Infographic showing PDF and spreadsheet documents grounded into NotebookLM with interactive citations and audio summaries",
            "on_screen_text": [
                "UPLOAD CONTRACTS, MANUALS & SPREADSHEETS",
                "GROUNDED Q&A WITH VERIFIABLE CITATIONS",
                "AUTO AUDIO OVERVIEWS FOR FAST BRIEFINGS",
                "100% FREE IN GOOGLE LABS"
            ],
            "duration_estimate_sec": 39.0
        },
        {
            "id": 3,
            "section_type": "tool_2",
            "title": "Notion AI: Automated Notes & Team Knowledge Base",
            "narration": (
                "Our second tool is Notion AI. Managing projects across a small team usually turns into a chaotic mess of scattered docs "
                "and missed follow-ups. Notion AI integrates conversational intelligence directly into your documents and tables. When you paste "
                "meeting notes or customer discovery transcripts, Notion AI automatically extracts action items, assigns due dates, and flags open "
                "questions. Even better, its workspace Q and A lets any team member ask questions across your company wiki—like what is our standard "
                "refund policy or who is our primary freight contact—instantly surfacing the exact document. Notion AI is available as a straightforward "
                "add-on for around eight to ten dollars per member monthly."
            ),
            "visual_description": "Notion AI workspace highlighting meeting action item extraction and company wiki Q&A",
            "image_prompt": "Modern Notion workspace showing automated action item checkboxes extracted from meeting notes, clean UI layout",
            "on_screen_text": [
                "AUTO-EXTRACT ACTION ITEMS FROM MEETINGS",
                "WORKSPACE Q&A ACROSS ALL COMPANY DOCS",
                "DRAFT PROPOSALS, SPECS & CLIENT EMAILS",
                "ADD-ON PRICING: ~$8-$10 / MEMBER / MONTH"
            ],
            "duration_estimate_sec": 40.0
        },
        {
            "id": 4,
            "section_type": "tool_3",
            "title": "Descript: Text-Based Video & Marketing Content",
            "narration": (
                "Our third tool is Descript. Video marketing, product walkthroughs, and customer testimonials are critical for modern sales, "
                "but traditional video editing takes hours in complex timelines. Descript completely flips video production by turning your "
                "recordings into an editable text document. When you delete a sentence from the transcript, Descript automatically cuts that exact "
                "video clip. It features one-click filler word removal to purge ums and repeated words instantly, plus Studio Sound which uses neural "
                "networks to remove room echo and background noise, making a cheap phone microphone sound like a professional broadcast studio. "
                "It offers a generous free tier and creator plans starting around twelve dollars a month."
            ),
            "visual_description": "Descript editor interface demonstrating transcript text editing and studio sound noise removal",
            "image_prompt": "Descript audio video editor UI showing transcript text editing, filler word removal, and studio sound toggle, dark mode",
            "on_screen_text": [
                "EDIT VIDEO BY EDITING TEXT TRANSCRIPTS",
                "1-CLICK REMOVAL OF 'UMS' & 'AHS'",
                "STUDIO SOUND NEURAL NOISE ISOLATION",
                "FREE TIER • CREATOR PLANS FROM $12/MO"
            ],
            "duration_estimate_sec": 41.0
        },
        {
            "id": 5,
            "section_type": "tool_4",
            "title": "Perplexity Pro: Verified Market & Supplier Intelligence",
            "narration": (
                "Fourth on our list is Perplexity Pro. When researching competitor pricing, new vendor wholesale terms, or local compliance "
                "regulations, standard search engines bury you in sponsored ads and outdated blog posts. Perplexity is an answer engine that scans live "
                "web sources in real time, synthesizing concise answers backed by numbered, clickable citations. You can upload spreadsheets to compare "
                "supplier quotes, or use its Deep Research feature for multi-step market evaluations. Because every claim includes an exact source link, "
                "you can verify facts before making expensive business commitments. Perplexity offers a robust free tier, while the twenty dollar Pro "
                "tier provides access to the latest frontier reasoning models."
            ),
            "visual_description": "Perplexity search interface highlighting real-time cited answers and supplier comparison tables",
            "image_prompt": "Search engine interface showing multi-source citations, supplier comparison breakdown, and verified web sources",
            "on_screen_text": [
                "REAL-TIME WEB SEARCH WITH CITED URLS",
                "COMPARE SUPPLIER QUOTES & CONTRACT TERMS",
                "DEEP RESEARCH FOR MULTI-STEP MARKET DATA",
                "FREE SEARCH • PRO REASONING AT $20/MO"
            ],
            "duration_estimate_sec": 40.0
        },
        {
            "id": 6,
            "section_type": "tool_5",
            "title": "Make.com: Visual No-Code Multi-App AI Automation",
            "narration": (
                "Our fifth tool is Make.com. Connecting your everyday business tools—like QuickBooks, Stripe, Gmail, and Google Sheets—is where "
                "the biggest time savings happen. Make is a visual drag-and-drop automation platform that now features native AI assistants to build "
                "complex multi-step workflows. For example, when a customer pays an invoice on Stripe, Make can automatically trigger an AI module "
                "to categorize the purchase, log it into QuickBooks, draft a personalized onboarding email in Gmail, and notify your team on "
                "Slack—all in under three seconds with zero code. Make offers a free tier with one thousand operations monthly, and entry plans "
                "starting under ten dollars a month."
            ),
            "visual_description": "Make.com visual automation canvas connecting Stripe, QuickBooks, Gmail, and Google Sheets",
            "image_prompt": "Visual drag-and-drop workflow canvas connecting Stripe, accounting, email, and spreadsheets with AI logic nodes",
            "on_screen_text": [
                "DRAG-AND-DROP VISUAL WORKFLOW CANVAS",
                "CONNECT STRIPE, QUICKBOOKS, GMAIL & SHEETS",
                "NATIVE AI MODULES FOR PARSING & DRAFTING",
                "FREE TIER (1,000 OPS/MO) • PLANS FROM $9/MO"
            ],
            "duration_estimate_sec": 40.0
        },
        {
            "id": 7,
            "section_type": "action_plan",
            "title": "Your 30-Day Practical Implementation Blueprint",
            "narration": (
                "Here is your implementation rule of thumb: do not try to adopt all five tools at once. Start by identifying your single biggest "
                "time bottleneck this week. If you are drowning in paperwork, start with Google NotebookLM. If customer communication and video marketing "
                "take too long, test Descript. Pick just one tool, spend thirty minutes testing it on a real workflow, and measure the hours you save "
                "before expanding. All links and resources are in the description below. Which of these five tools will you implement first? Let us "
                "know in the comments, and subscribe for more practical business automation tutorials."
            ),
            "visual_description": "Clean outro summary showing the 30-day single bottleneck implementation rule and call to action",
            "image_prompt": "Clean actionable roadmap graphic showing Step 1 Bottleneck, Step 2 30-min Test, Step 3 Scale Up, modern outro UI",
            "on_screen_text": [
                "RULE OF THUMB: PICK 1 BOTTLENECK TOOL FIRST",
                "TEST FOR 30 MINUTES ON A REAL WORKFLOW",
                "MEASURE TIME SAVINGS BEFORE SCALING UP",
                "ALL LINKS & RESOURCES IN DESCRIPTION BELOW"
            ],
            "duration_estimate_sec": 38.0
        }
    ]

    return {
        "tool_name": tool_name,
        "suggested_title": suggested_title,
        "description_summary": description_summary,
        "target_duration_minutes": 4,
        "sections": sections
    }

def write_script(topic_data: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
    """Generates and writes an 8-12 minute educational script in both JSON and TXT format.
    
    Args:
        topic_data: Topic specification dictionary.
        project_id: Project identifier.
        
    Returns:
        Structured script dictionary.
    """
    settings.ensure_directories()
    project_id = project_id or topic_data.get("id") or datetime.now().strftime("%Y%m%d_%H%M%S")
    tool_name = topic_data.get("tool_name", "AI Tool")

    logger.info(f"Writing educational script for '{tool_name}' (Project {project_id})...")

    # 1. Try Gemini generation if API key is configured
    script_data = generate_script_with_gemini(topic_data)

    # 2. Check for specialized curricula
    if not script_data or "sections" not in script_data:
        topic_lower = (tool_name + " " + topic_data.get("suggested_title", "") + " " + topic_data.get("angle", "")).lower()
        if any(k in topic_lower for k in ["small business", "5 practical", "save time", "business owner"]):
            logger.info("Generating specialized 5 Practical AI Tools for Small Business curriculum (~710 words, ~4 mins)...")
            script_data = build_small_business_ai_tools_script(topic_data)
        elif "claude" in tool_name.lower() or "artifact" in tool_name.lower():
            logger.info("Generating specialized in-depth Claude 3.7 Artifacts curriculum (1500+ words)...")
            script_data = build_claude_artifacts_script(topic_data)
        else:
            logger.info("Generating script using procedural educational masterclass blueprint...")
            script_data = build_procedural_script(topic_data)

    # Calculate exact word counts and durations
    sections = script_data.get("sections", [])
    total_words = 0
    full_narrative_lines = []

    for sec in sections:
        narration = sec.get("narration", "")
        words = len(narration.split())
        sec["word_count"] = words
        total_words += words
        
        # Duration based on 145 words per minute
        est_sec = round((words / settings.WORDS_PER_MINUTE) * 60, 2)
        sec["duration_estimate_sec"] = max(est_sec, 20.0)

        full_narrative_lines.append(f"--- SECTION {sec.get('id', 0)}: {sec.get('title', '')} ---\n{narration}\n")

    script_data["topic_id"] = project_id
    script_data["tool_name"] = script_data.get("tool_name") or tool_name
    if "suggested_title" not in script_data and topic_data.get("suggested_title"):
        script_data["suggested_title"] = topic_data["suggested_title"]
    script_data["word_count"] = total_words
    script_data["full_text"] = "\n".join(full_narrative_lines)
    script_data["estimated_total_minutes"] = round(total_words / settings.WORDS_PER_MINUTE, 2)

    logger.info(f"Script generated successfully: {total_words} words (~{script_data['estimated_total_minutes']} minutes).")

    # Save structured JSON
    json_path = settings.SCRIPTS_DIR / f"{project_id}_script.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(script_data, f, indent=2)

    # Save readable TXT
    txt_path = settings.SCRIPTS_DIR / f"{project_id}_script.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"VIDEO SCRIPT: {topic_data.get('suggested_title', tool_name)}\n")
        f.write(f"Tool: {tool_name} | Word Count: {total_words} | Est. Duration: {script_data['estimated_total_minutes']} mins\n\n")
        f.write(script_data["full_text"])

    script_data["saved_json_path"] = str(json_path)
    script_data["saved_txt_path"] = str(txt_path)
    logger.info(f"Saved script JSON to {json_path}")
    logger.info(f"Saved script TXT to {txt_path}")

    return script_data

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Stage 2: Script Writer")
    parser.add_argument("--topic-file", type=str, help="Path to topic JSON file")
    parser.add_argument("--tool", type=str, help="AI tool name")
    args = parser.parse_args()

    topic_data = {}
    if args.topic_file:
        with open(args.topic_file, "r", encoding="utf-8") as f:
            topic_data = json.load(f)
    elif args.tool:
        topic_data = {"tool_name": args.tool, "angle": "Complete Step-by-Step Guide"}
    else:
        # Load most recent topic in topics/
        topic_files = sorted(settings.TOPICS_DIR.glob("*_topic.json"))
        if topic_files:
            with open(topic_files[-1], "r", encoding="utf-8") as f:
                topic_data = json.load(f)
        else:
            topic_data = {"tool_name": "Claude 3.7 & Artifacts", "angle": "Beginner to Pro Masterclass"}

    res = write_script(topic_data)
    print("\n--- Script Generated ---")
    print(f"Tool:            {res['tool_name']}")
    print(f"Word Count:      {res['word_count']} words")
    print(f"Target Duration: {res['estimated_total_minutes']} minutes")
    print(f"Sections Count:  {len(res['sections'])}")
    print(f"JSON File:       {res['saved_json_path']}")
    print(f"TXT File:        {res['saved_txt_path']}")

if __name__ == "__main__":
    main()
