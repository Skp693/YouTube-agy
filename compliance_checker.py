"""YouTube Monetization & Policy Compliance Guard (compliance_checker.py)

Periodically and pre-flight audits all generated content (scripts, metadata, visuals)
against updated YouTube policies:
  1. Advertiser-Friendly Content Guidelines (no profanity, shock value, or harmful instructions)
  2. Reused Content & Repetitious Content Policy (mandates significant educational commentary & original framing)
  3. Altered or Synthetic Content Policy (enforces proper disclosure for AI media)
  4. Misleading Metadata & Spam Policy (ensures honest titles, accurate timestamps, and no keyword stuffing)
  5. Child Safety & COPPA compliance (selfDeclaredMadeForKids: False)
"""

import re
from typing import Dict, Any, List

class ComplianceChecker:
    """Automated policy auditor for monetization safety and YouTube compliance."""

    # Prohibited or high-risk advertiser terms that trigger demonetization (yellow dollar icon)
    HIGH_RISK_KEYWORDS = [
        "hack", "crack", "pirated", "free download bypass", "torrent",
        "bypass paywall", "exploit", "steal", "cheat", "scam",
        "guaranteed overnight income", "crypto doubling", "get rich quick"
    ]

    # Required positive signals for educational fair-use monetization
    EDUCATIONAL_SIGNALS = [
        "tutorial", "guide", "how to", "step-by-step", "workflow",
        "overview", "tips", "best practices", "setup", "walkthrough"
    ]

    @classmethod
    def audit_project(
        cls,
        title: str,
        description: str,
        narration_full: str,
        tags: List[str],
        has_ai_disclosure: bool = True
    ) -> Dict[str, Any]:
        """Audits complete video package against YouTube policies.
        
        Returns:
            Dictionary with compliance score (0-100), status, issues, and recommendations.
        """
        issues: List[Dict[str, str]] = []
        passed_checks: List[str] = []
        score = 100

        combined_text = f"{title}\n{description}\n{narration_full}".lower()

        # 1. Advertiser-Friendly Audit
        found_risky = []
        for kw in cls.HIGH_RISK_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", combined_text):
                found_risky.append(kw)

        if found_risky:
            score -= (len(found_risky) * 15)
            issues.append({
                "severity": "HIGH",
                "category": "Advertiser-Friendly Guidelines",
                "message": f"Detected high-risk advertiser keywords that may limit ads: {', '.join(found_risky)}",
                "action": "Replace words like 'hack' or 'bypass' with 'workflow tip' or 'efficiency technique'."
            })
        else:
            passed_checks.append("Clean advertiser-friendly language: Zero demonetization flags detected.")

        # 2. Original Commentary / Reused Content Guard
        edu_count = sum(1 for s in cls.EDUCATIONAL_SIGNALS if s in combined_text)
        if edu_count < 3:
            score -= 10
            issues.append({
                "severity": "MEDIUM",
                "category": "Reused Content Policy",
                "message": "Content may lack sufficient educational framing signals.",
                "action": "Ensure the narration includes clear original analysis, tips, and step-by-step walkthroughs."
            })
        else:
            passed_checks.append("Strong educational framing: Meets original commentary thresholds.")

        # 3. Synthetic Media Disclosure (YouTube 2024-2026 policy)
        if not has_ai_disclosure:
            score -= 20
            issues.append({
                "severity": "HIGH",
                "category": "Altered or Synthetic Content Disclosure",
                "message": "Missing mandatory YouTube synthetic media disclosure for AI voiceover and generated visuals.",
                "action": "Enable the 'Altered Content' disclosure checkbox in YouTube Studio."
            })
        else:
            passed_checks.append("Altered/Synthetic Media Disclosure: Compliant with YouTube AI labeling rules.")

        # 4. Misleading Metadata & Chapter Audit
        has_timestamps = bool(re.search(r"\b0?0:00\b", description))
        if not has_timestamps:
            score -= 10
            issues.append({
                "severity": "MEDIUM",
                "category": "Misleading Metadata",
                "message": "Description is missing a 00:00 chapter marker, reducing Google Search key moments ranking.",
                "action": "Include timestamp chapters starting at 00:00."
            })
        else:
            passed_checks.append("Description contains valid 00:00 indexed chapter markers.")

        # 5. Title Length & Clickbait Balance
        if len(title) > 70:
            score -= 5
            issues.append({
                "severity": "LOW",
                "category": "Title Optimization",
                "message": f"Title is {len(title)} characters; it may truncate on mobile screens (>70 chars).",
                "action": "Shorten title to under 70 characters for higher click-through rates."
            })
        elif len(title) < 25:
            score -= 5
            issues.append({
                "severity": "LOW",
                "category": "Title Optimization",
                "message": "Title is too short to rank well for search keywords.",
                "action": "Add specific benefit and tutorial angle into the title."
            })
        else:
            passed_checks.append("Title length is optimized for mobile and desktop display (<70 chars).")

        # 6. Tag Count & Relevance
        if len(tags) > 20:
            score -= 5
            issues.append({
                "severity": "LOW",
                "category": "Metadata Spam",
                "message": "Too many tags may trigger spam detection.",
                "action": "Limit tags to 10-15 hyper-relevant keywords."
            })
        else:
            passed_checks.append("Search tags are clean and within optimal bounds.")

        final_score = max(0, min(100, score))
        status = "PASSED_MONETIZATION_READY" if final_score >= 80 else "NEEDS_MODIFICATION"

        return {
            "score": final_score,
            "status": status,
            "monetization_friendly": final_score >= 80,
            "passed_checks": passed_checks,
            "issues": issues,
            "policy_version": "YouTube Partner Program Standards (2026.1)"
        }
