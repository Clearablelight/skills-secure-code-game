// Run tests.js by following the instructions below:

// Run file by opening a terminal and running the following:
// $ npm install Season-2/Level-5/ && mocha Season-2/Level-5/tests.js

const { expect } = require('chai');
const CryptoAPI = require('./code');

describe('CryptoAPI.sha1.hash', () => {

  // Fix 1: non-string argument must throw, not silently invoke attacker-controlled toString()
  it('should throw when called with a non-string (object with malicious toString)', () => {
    const malicious = {
      toString: function() { return 'injected'; }
    };
    expect(() => CryptoAPI.sha1.hash(malicious)).to.throw();
  });

  it('should throw when called with a number', () => {
    expect(() => CryptoAPI.sha1.hash(42)).to.throw();
  });

  it('should throw when called with null', () => {
    expect(() => CryptoAPI.sha1.hash(null)).to.throw();
  });

  it('should throw when called with undefined', () => {
    expect(() => CryptoAPI.sha1.hash(undefined)).to.throw();
  });

  // Fix 2: overwriting _round externally must not affect hash behaviour
  it('should not be affected by external overwrite of CryptoAPI.sha1._round', () => {
    let exploitFired = false;
    CryptoAPI.sha1._round = function() { exploitFired = true; };

    // Call hash — it must use the local internalRound, not the overwritten one
    try {
      CryptoAPI.sha1.hash("abc");
    } catch (e) {
      // hash may throw for other reasons (encoding stubs are empty), that is fine
    }

    expect(exploitFired).to.equal(false,
      '_round overwrite must not be called inside hash() — use a local reference');
  });

  // Fix 3: prototype poisoning of Array must not affect hash behaviour
  it('should not be affected by Array.prototype setter poisoning', () => {
    let exploitFired = false;
    const originalDescriptor = Object.getOwnPropertyDescriptor(Array.prototype, '0');

    Object.defineProperty(Array.prototype, '0', {
      set: function() { exploitFired = true; },
      configurable: true,
    });

    try {
      CryptoAPI.sha1.hash("abc");
    } catch (e) {
      // encoding stubs may throw, that is acceptable
    } finally {
      // Restore Array.prototype to avoid polluting other tests
      if (originalDescriptor) {
        Object.defineProperty(Array.prototype, '0', originalDescriptor);
      } else {
        delete Array.prototype['0'];
      }
    }

    expect(exploitFired).to.equal(false,
      'Array.prototype setter poisoning must not fire inside hash() — w must be pre-allocated');
  });

  // Valid string input must not throw (encoding stubs may return undefined, that is OK)
  it('should accept a plain string without throwing a type error', () => {
    expect(() => CryptoAPI.sha1.hash("hello")).to.not.throw(
      /should be called with a 'normal' parameter/
    );
  });
});
