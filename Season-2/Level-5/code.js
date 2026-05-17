// Welcome to Secure Code Game Season-2/Level-5!

// This is the last level of this season, good luck!

var CryptoAPI = (function() {
	var encoding = {
		a2b: function(a) { },
		b2a: function(b) { }
	};

	var API = {
		sha1: {
			name: 'sha1',
			identifier: '2b0e03021a',
			size: 20,
			block: 64,
			hash: function(s) {

				// Fix 1: reject non-string input to prevent malicious toString() exploitation
				if (typeof s !== "string") {
					throw "Error: CryptoAPI.sha1.hash() should be called with a 'normal' parameter (i.e., a string)";
				}

				var len = (s += '\x80').length,
					blocks = len >> 6,
					chunk = len & 63,
					res = "",
					i = 0,
					j = 0,
					H = [0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0],

					// Fix 3: pre-allocate 128 elements so prototype setters on Array cannot fire
					w = [
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
						0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
					];

				while (chunk++ != 56) {
					s += "\x00";
					if (chunk == 64) {
						blocks++;
						chunk = 0;
					}
				}

				for (s += "\x00\x00\x00\x00", chunk = 3, len = 8 * (len - 1); chunk >= 0; chunk--) {
					s += encoding.b2a(len >> (8 * chunk) & 255);
				}

				for (i = 0; i < s.length; i++) {
					j = (j << 8) + encoding.a2b(s[i]);
					if ((i & 3) == 3) {
						w[(i >> 2) & 15] = j;
						j = 0;
					}
					// Fix 2: use local reference so _round cannot be overwritten by external code
					if ((i & 63) == 63) internalRound(H, w);
				}

				for (i = 0; i < H.length; i++)
					for (j = 3; j >= 0; j--)
						res += encoding.b2a(H[i] >> (8 * j) & 255);
				return res;
			}, // End "hash"
			_round: function(H, w) { }
		} // End "sha1"
	}; // End "API"

	// Fix 2: capture local reference to _round before returning API
	var internalRound = API.sha1._round;

	return API; // End body of anonymous function
})(); // End "CryptoAPI"

if (typeof module !== 'undefined') module.exports = CryptoAPI;
