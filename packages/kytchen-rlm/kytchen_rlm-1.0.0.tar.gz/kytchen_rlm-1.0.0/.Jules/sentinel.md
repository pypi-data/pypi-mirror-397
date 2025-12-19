## 2024-05-23 - [Sandbox Escape via Format Strings]
**Vulnerability:** The `str.format()` method and `format()` builtin allow accessing object attributes (like `__globals__`) via format specifiers (e.g., `"{0.__globals__}".format(func)`), which bypasses AST-based checks that only look for explicit attribute access nodes.
**Learning:** AST-based sandboxing is insufficient if it doesn't account for dynamic attribute access methods provided by the language standard library (like `format`, `getattr`, etc.). String formatting is a powerful mini-language that can be abused for introspection.
**Prevention:**
1. Forbid usage of `format` and `format_map` methods in the AST validator.
2. Remove `format` from the allowed builtins.
3. Encourage usage of f-strings, which are compiled to AST nodes where attribute access is visible and can be validated.
