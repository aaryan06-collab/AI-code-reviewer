import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

REVIEW_PROMPT = """You are a senior software engineer conducting a thorough code review.
You have deep expertise in security, performance, clean architecture, complexity analysis, and language-specific best practices.

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
7. Complexity — What is the time and space complexity?

For EACH issue found, use this exact format. You MUST include the exact line number(s):
### [Critical/Major/Minor] Issue Title
- **Line(s)**: Exact line number(s) where the issue occurs (e.g., "Line 5", "Lines 12-15")
- **Category**: Correctness | Security | Performance | Maintainability | Best Practice | Error Handling
- **Confidence**: High | Medium | Low
- **Problem**: Clear explanation of what is wrong and why it matters
- **Fix**: Provide a complete, working code snippet that fixes the issue. Show the exact corrected code — not vague advice. The fix should be copy-pasteable and ready to use.

If there are no issues in a category, skip it — do NOT invent problems.
If the code is clean with no real issues, state "No significant issues found" and move to the next sections.

After the issues, provide:

## Top 3 Issues
List the 3 most critical issues (if any exist), sorted by severity. Use format:
1. **[Severity]** Issue title — Line X
2. **[Severity]** Issue title — Line X
3. **[Severity]** Issue title — Line X

If fewer than 3 issues exist, list only those.

## Complexity Analysis
For EACH function or method in the code, provide:
- **Function**: function_name()
- **Time Complexity**: O(...) with brief explanation of why
- **Space Complexity**: O(...) with brief explanation of why
- **Line(s)**: Line numbers of the function

If the code has no functions (e.g., a script), analyze the overall algorithm.

## Positive Aspects
What the code does well. Be specific — mention function names, patterns, or techniques done right.

## Score Card
- Correctness: X/10
- Security: X/10
- Performance: X/10
- Maintainability: X/10
- Complexity: X/10
- **Overall: X/10**

## Summary
2-3 sentence verdict. State the most critical action needed and whether the code is production-ready.

Rules:
- Be specific. Reference exact line numbers, variable names, and function names.
- Only report real issues — zero false positives.
- Prioritize issues by real-world impact, not style preferences.
- The Fix section MUST contain actual working code, not just descriptions.
- If the code is good, say so honestly. Do not pad the review to look busy.
- Always include line numbers for every issue — this is mandatory."""

def review_code(code: str, filename: str, review_lang: str = "English") -> str:
    if not code.strip():
        return "Error: File is empty."

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("GROQ_API_KEY not set. Add it to your .env file.")

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    ext = os.path.splitext(filename)[1].lstrip(".") or "text"

    prompt = REVIEW_PROMPT.format(language=ext, code=code, review_lang=review_lang)
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=4000,
    )
    return response.choices[0].message.content
