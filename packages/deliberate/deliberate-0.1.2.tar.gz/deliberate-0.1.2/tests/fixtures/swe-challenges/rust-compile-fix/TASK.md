# Task: Fix Compilation Errors

## Objective
Fix all compilation errors in `src/lib.rs` so that the code compiles and tests pass.

## Current Errors
1. `len()` returns `i32` but `HashMap::len()` returns `usize`
2. `delete()` uses `&self` but `remove()` requires `&mut self`
3. Missing `Default` trait implementation for `Store`

## Success Criteria
- Code compiles: `cargo check`
- All tests pass: `cargo test`

## Constraints
- Keep the public API compatible with the tests
- The `Default::default()` should create an empty store
