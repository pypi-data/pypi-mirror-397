## Local Code Review

### 🔍 Code Analysis
The changes address a critical functional defect in the local review workflow where the AI was analyzing file metadata instead of actual code content. The fix involves two key components:
1.  **Data Retrieval**: Switching from `str(diff_item)` (metadata) to `diff_item.diff` (content) in `LocalGitClient`.
2.  **Context Construction**: Manually reconstructing standard unified diff headers (`diff --git`, `---`, `+++`) which are missing from GitPython's `diff` property but are essential for the LLM to understand file context (renames, new files, deletions).
3.  **Prompt Engineering**: Explicitly instructing the LLM on how to interpret unified diff markers (`+`/`-`) to prevent redundant suggestions.

The implementation correctly handles binary data decoding and aligns the local client's output format with what the GitHub/GitLab clients provide, ensuring consistent AI performance across platforms.

### 📂 File Reviews

**📄 `src/ai_code_review/core/local_git_client.py`** - Fix for empty diff content and header construction
- **Review:** Replacing `str(diff_item)` with `diff_item.diff` is the correct fix. The previous implementation only passed the file change summary (SHA/mode), causing the AI to hallucinate reviews.
- **Review:** The manual reconstruction of unified diff headers (`diff --git`, `---`, `+++`) is necessary because `diff_item.diff` only returns the patch hunk. This context is critical for the AI to distinguish between file modifications, creations, and deletions.
- **Review:** Handling bytes-to-string conversion with `decode('utf-8', errors='replace')` is a robust choice to prevent crashes on non-UTF-8 files.
- **Suggestion:** Ensure that `diff_item.a_path` and `diff_item.b_path` are validated before use. In some Git edge cases (like pure mode changes or initial commits), paths might need specific handling to match standard `git diff` output exactly.

**📄 `src/ai_code_review/utils/prompts.py`** - System prompt updates for diff format
- **Review:** Adding explicit instructions that "Lines starting with '+' are NEW code" and "Lines starting with '-' are OLD code" is a high-value improvement. This directly addresses the common LLM failure mode of suggesting "you should add X" when X is already present in the added lines.
- **Review:** The inclusion of a concrete example in the prompt (as mentioned in the commit description) reinforces the instruction and reduces ambiguity for the model.

### ✅ Summary

**Overall Assessment:** Excellent, high-impact fixes. The changes transform the local review feature from broken (reviewing metadata) to functional (reviewing code), while simultaneously improving the AI's ability to interpret the diff syntax correctly.

**Priority Issues:**
- None. The logic described is sound and addresses the root causes effectively.

**Minor Suggestions:**
- In `LocalGitClient`, consider adding a check for `diff_item.diff is None` (e.g., for empty files or binary files where diff is suppressed) to avoid potential runtime errors during concatenation.
