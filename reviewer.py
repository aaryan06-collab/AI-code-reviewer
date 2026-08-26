import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

REVIEW_PROMPT = """You are a senior software engineer conducting a thorough code review.
You have deep expertise in security, performance, clean architecture, and language-specific best practices.

Review the following {language} code:

```{language}
{code}
```

Write the entire review in {review_lang}.

Evaluate the code across these dimensions:
1. Correctness — Are there bugs, logic errors, or edge cases?
2. Security — Are there vulnerabilities (injection, auth issues, data exposure)?
3. Performance — Are there inefficiencies, unnecessary computations, or memory issues?
4. Maintainability — Is the code readable, well-structured, and DRY?
5. Best Practices — Does it follow {language} conventions and idioms?
6. Error Handling — Are errors caught and handled properly?

For EACH issue found, use this exact format:
### [Critical/Major/Minor] Issue Title
- **Location**: Exact line number(s) or function name
- **Category**: Correctness | Security | Performance | Maintainability | Best Practice | Error Handling
- **Confidence**: High | Medium | Low
- **Problem**: Clear explanation of what is wrong and why it matters
- **Fix**: Provide a complete, working code snippet that fixes the issue. Show the exact corrected code — not vague advice. The fix should be copy-pasteable and ready to use.

If there are no issues in a category, skip it — do NOT invent problems.

After the issues, provide:

## Positive Aspects
What the code does well. Be specific — mention function names, patterns, or techniques done right.

## Score Card
- Correctness: X/10
- Security: X/10
- Performance: X/10
- Maintainability: X/10
- **Overall: X/10**

## Summary
2-3 sentence verdict. State the most critical action needed and whether the code is production-ready.

Rules:
- Be specific. Reference exact lines, variable names, and function names.
- Only report real issues — zero false positives.
- Prioritize issues by real-world impact, not style preferences.
- The Fix section MUST contain actual working code, not just descriptions.
- If the code is good, say so honestly. Do not pad the review to look busy."""

def review_code(code: str, filename: str, review_lang: str = "English") -> str:
    if not code.strip():
        return "Error: File is empty."

    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY not set. Add it to your .env file.")

    ext = os.path.splitext(filename)[1].lstrip(".") or "text"

    prompt = REVIEW_PROMPT.format(language=ext, code=code, review_lang=review_lang)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3,
            max_output_tokens=4000,
        ),
    )
    return response.text
