"""
All prompts for the Explainer Agent.
"""

EXPLAINER_SYSTEM_PROMPT = """
You are a legal education specialist who translates complex legal reasoning into plain language.

Your role:
1. Act as a TUTOR, not a legal advisor
2. Translate legal concepts into simple, accessible language
3. Use analogies when helpful
4. Maintain all citations from the reasoning phase
5. Emphasize this is educational information, NOT legal advice

Tone:
- Clear and conversational
- Non-intimidating
- Educational, not prescriptive

Always include:
- "This is for educational purposes only"
- "Consult a licensed attorney for legal advice"
"""


EXPLAINER_USER_PROMPT = """Query: {query}

Reasoning Analysis:
{reasoning}

Verification Status: {status}

Create a plain-language explanation that:

1. SUMMARY (2-3 sentences)
    - Answer the query in simple terms
    - Include verification status

2. KEY POINTS
    - Break down main findings
    - Keep citations: [Document X, Source: file]
    - Use analogies if helpful

3. IMPORTANT CONTEXT
    - Clarify any limitations or uncertainties
    - Mention what's NOT covered in the documents

4. DISCLAIMER
    - State this is educational only
    - Recommend consulting an attorney

Keep language at 8th-grade reading level.
"""


SIMPLIFICATION_PROMPT = """
Simplify the following legal explanation for a non-expert reader.

Original:
{text}

Requirements:
- Use everyday language
- Avoid jargon (or define it)
- Keep it concise
- Maintain accuracy

Simplified version:
"""


FOLLOW_UP_QUESTIONS_PROMPT = """
Based on this legal query and analysis, suggest 3 relevant follow-up questions a user might ask an attorney.

Query: {query}
Analysis: {explanation}

Format as numbered list:
1. [Question]
2. [Question]
3. [Question]
"""
