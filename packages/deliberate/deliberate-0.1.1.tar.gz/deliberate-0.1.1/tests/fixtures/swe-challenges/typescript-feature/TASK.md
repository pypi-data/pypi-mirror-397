# Task: Add Email Validation Function

## Objective
Add an `isValidEmail(email: string): boolean` function to `src/utils.ts`.

## Requirements
1. Return `true` for valid email addresses like:
   - `user@example.com`
   - `test.user@sub.domain.com`

2. Return `false` for invalid emails:
   - Empty string
   - Missing @ symbol
   - Nothing before @ (like `@example.com`)
   - Nothing after @ (like `user@`)

## Success Criteria
- Uncomment the tests in `src/utils.test.ts`
- All tests pass with: `npm test`

## Setup
```bash
npm install
```

## Constraints
- Export the function from utils.ts
- Use a reasonable regex or validation logic
