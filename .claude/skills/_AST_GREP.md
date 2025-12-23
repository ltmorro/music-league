# ABOUTME: ast-grep universal guide for AST-aware code search across all languages
# ABOUTME: ALWAYS use ast-grep instead of grep/ripgrep for code analysis

# ast-grep (sg) - Universal Code Search

## Critical Rule

**ALWAYS use `ast-grep` (sg) via `mcp__acp__Bash` for code analysis. NEVER use grep or ripgrep.**

## Why ast-grep?

- **AST-aware**: Matches code structure, not text
- **No false positives**: Ignores comments, strings, docstrings
- **Language-native**: Understands syntax semantically
- **Refactoring-safe**: Structural matching guarantees correctness

## Installation Check

```bash
sg --version  # Verify ast-grep is installed
```

## Pattern Syntax

```
$VAR        Match single identifier
$$$         Match multiple items (variadic)
$$          Match optional item
$_          Match anything (wildcard)
```

## Universal Flags

```bash
--lang LANG    Specify language (python)
--pattern PAT  Search pattern
-A N           Show N lines after match
-B N           Show N lines before match
-C N           Show N lines before and after
```

## Python Patterns

```bash
# Functions
sg --pattern 'def $NAME($$$): $$$' --lang python

# Async functions
sg --pattern 'async def $NAME($$$): $$$' --lang python

# Classes
sg --pattern 'class $NAME: $$$' --lang python
sg --pattern 'class $NAME($BASE): $$$' --lang python

# Type hints
sg --pattern 'def $NAME($$$) -> $TYPE: $$$' --lang python

# Decorators
sg --pattern '@$DECORATOR\ndef $NAME($$$): $$$' --lang python

# Exception handling
sg --pattern 'try: $$$ except $EXC: $$$' --lang python

# Imports
sg --pattern 'from $MODULE import $$$' --lang python
sg --pattern 'import $MODULE' --lang python
```

## Common Workflows

### Find all TODOs
```bash
sg --pattern '# TODO: $$$' --lang python
```

### Find security issues
```bash
# SQL injection risks (Go)
sg --pattern 'db.Query($QUERY + $VAR)' --lang go

# Eval usage (Python)
sg --pattern 'eval($$$)' --lang python

# Dangerous mass assignment (Rails)
sg --pattern '.create(params)' --lang ruby
```

## Tips

1. **Start specific, broaden if needed**: Specific patterns are faster
2. **Use context flags (-A, -B, -C)**: See surrounding code
3. **Combine with other tools**: Pipe to grep, wc, etc.
4. **Test patterns**: Verify on known matches first
5. **Escape when needed**: Some chars need escaping in shell

## When NOT to use ast-grep

- Searching in non-code files (logs, config, markdown) → use grep
- Searching across file paths → use find or glob
- Full-text search in docs → use grep or ripgrep

---

**For language-specific patterns, see:**
- Python: `python/SKILL.md`