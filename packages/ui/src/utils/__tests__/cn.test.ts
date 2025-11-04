import { cn } from '../cn';

describe('cn', () => {
  it('should return a string of class names', () => {
    expect(cn('foo', 'bar')).toBe('foo bar');
  });

  it('should remove falsy values', () => {
    expect(cn('foo', false, 'bar', null, undefined, 0, '')).toBe('foo bar');
  });
});
