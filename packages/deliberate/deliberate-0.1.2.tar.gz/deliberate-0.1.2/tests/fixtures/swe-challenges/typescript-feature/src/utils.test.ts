import { capitalize, truncate, slugify } from './utils';
// TODO: Import and test isValidEmail when implemented

describe('capitalize', () => {
  it('capitalizes first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('handles empty string', () => {
    expect(capitalize('')).toBe('');
  });
});

describe('truncate', () => {
  it('truncates long strings', () => {
    expect(truncate('hello world', 8)).toBe('hello...');
  });

  it('returns short strings unchanged', () => {
    expect(truncate('hi', 10)).toBe('hi');
  });
});

describe('slugify', () => {
  it('creates URL-safe slugs', () => {
    expect(slugify('Hello World!')).toBe('hello-world');
  });
});

// TODO: Add tests for isValidEmail
// describe('isValidEmail', () => {
//   it('validates correct emails', () => {
//     expect(isValidEmail('user@example.com')).toBe(true);
//     expect(isValidEmail('test.user@sub.domain.com')).toBe(true);
//   });
//
//   it('rejects invalid emails', () => {
//     expect(isValidEmail('')).toBe(false);
//     expect(isValidEmail('user@')).toBe(false);
//     expect(isValidEmail('@example.com')).toBe(false);
//     expect(isValidEmail('userexample.com')).toBe(false);
//   });
// });
