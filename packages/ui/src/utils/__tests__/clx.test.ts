import { clx } from '../clx';

describe('clx', () => {
  it('should return a string of class names', () => {
    expect(clx('foo', 'bar')).toBe('foo bar');
  });

  it('should remove falsy values', () => {
    expect(clx('foo', false, 'bar', null, undefined, 0, '')).toBe('foo bar');
  });

  it('should handle objects', () => {
    expect(clx({ foo: true, bar: false, baz: true })).toBe('foo baz');
  });
});
