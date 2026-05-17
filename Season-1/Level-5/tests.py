import unittest
import code as c

class TestCrypto(unittest.TestCase):

    # verifies that hash and verification are matching each other for SHA
    def test_1(self):
        rd = c.Random_generator()
        sha256 = c.SHA256_hasher()
        pass_ver = sha256.password_verification("abc", sha256.password_hash("abc", rd.generate_salt()))
        self.assertEqual(pass_ver, True)

    # verifies that hash and verification are matching each other for MD5
    def test_2(self):
        md5 = c.MD5_hasher()
        md5_hash = md5.password_verification("abc", md5.password_hash("abc"))
        self.assertEqual(md5_hash, True)

    # generate_token produces a string of the requested length from the allowed alphabet
    def test_3_generate_token_length(self):
        rd = c.Random_generator()
        token = rd.generate_token(length=16)
        self.assertEqual(len(token), 16)

    # generate_token default length is 8
    def test_4_generate_token_default_length(self):
        rd = c.Random_generator()
        token = rd.generate_token()
        self.assertEqual(len(token), 8)

    # generate_token characters must all belong to the provided alphabet
    def test_5_generate_token_alphabet(self):
        rd = c.Random_generator()
        alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        token = rd.generate_token(length=64, alphabet=alphabet)
        self.assertTrue(all(c in alphabet for c in token))

    # generate_token must produce different values each call (statistically)
    def test_6_generate_token_uniqueness(self):
        rd = c.Random_generator()
        tokens = {rd.generate_token(length=16) for _ in range(100)}
        # With 62^16 possible values, collisions in 100 draws are astronomically unlikely
        self.assertGreater(len(tokens), 95)

    # generate_salt returns a valid bcrypt salt (bytes starting with $2b$)
    def test_7_generate_salt_format(self):
        rd = c.Random_generator()
        salt = rd.generate_salt()
        self.assertIsInstance(salt, bytes)
        self.assertTrue(salt.startswith(b'$2b$'))

    # generate_salt produces different salts each call
    def test_8_generate_salt_uniqueness(self):
        rd = c.Random_generator()
        salts = {rd.generate_salt() for _ in range(10)}
        self.assertGreater(len(salts), 1)

    # PASSWORD_HASHER must point to the strong hasher, not MD5
    def test_9_password_hasher_is_sha256(self):
        self.assertEqual(c.PASSWORD_HASHER, 'SHA256_hasher',
                         "PASSWORD_HASHER must default to SHA256_hasher, not MD5_hasher")

    # SECRET_KEY must come from the environment, not be hardcoded
    def test_10_secret_key_not_hardcoded(self):
        import inspect
        source = inspect.getsource(c)
        self.assertNotIn("SECRET_KEY = '", source,
                         "SECRET_KEY must not be hardcoded in source; use os.environ.get()")

if __name__ == '__main__':
    unittest.main()
