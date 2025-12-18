# SWE Challenge Test Fixtures

Realistic software engineering challenges for testing deliberate's capabilities.

## Challenges

### 1. python-bug-fix
**Type:** Bug fix
**Language:** Python
**Difficulty:** Easy

A calculator module with two bugs:
- `divide()` doesn't handle division by zero
- `calculate()` doesn't validate unknown operators (returns None)

**Test command:** `uv run pytest`

### 2. typescript-feature
**Type:** Feature addition
**Language:** TypeScript
**Difficulty:** Easy

A string utilities library that needs a new `isValidEmail()` function added.
Tests are commented out - they should be uncommented after implementation.

**Test command:** `npm test` (after `npm install`)

### 3. rust-compile-fix
**Type:** Compilation errors
**Language:** Rust
**Difficulty:** Medium

A key-value store with multiple compilation errors:
- Wrong return type (`i32` vs `usize`)
- Missing `&mut self` on `delete` method
- Missing `Default` trait implementation

**Test command:** `cargo test`

## Usage with Deliberate

```bash
# Python bug fix
uv run deliberate tests/fixtures/swe-challenges/python-bug-fix/TASK.md

# TypeScript feature
uv run deliberate tests/fixtures/swe-challenges/typescript-feature/TASK.md

# Rust compile fix
uv run deliberate tests/fixtures/swe-challenges/rust-compile-fix/TASK.md
```
