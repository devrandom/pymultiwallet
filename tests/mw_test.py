import unittest
from mw.mw import mnemonic_to_master, compute_address, generate, hash_entropy, visual
from binascii import hexlify, unhexlify

mnemonic1 = 'license diagram pelican spy monitor convince damage script wall hockey goose month popular swamp sugar rose mystery gap regular acquire bottom sea modify eyebrow'
mnemonic2 = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about'
class TestAll(unittest.TestCase):
    def test_eth(self):
        (seed, master) = mnemonic_to_master(mnemonic1, '')
        (a0, p0) = compute_address('eth', master, 0)
        self.assertEqual(a0, b'98cf7199f4e0c977196aafa64c6a240febb7b73e')
        self.assertEqual(p0, b'adc79901d8f7c56ff3ce1ea64ef09b17dcc9c246d5ca4e8cae5aace46471e8ee')
        (a10, p10) = compute_address('eth', master, 10)
        self.assertEqual(a10, b'07384028cc968f0023324661599a234051ad99f9')
        self.assertEqual(p10, b'6d8e2c2a53f5e918565ca9cb000ecacaeb87bddbf60a8fbe450f1f576e5e1b4a')
    def test_seed(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        visual(seed)
    def test_btc(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        self.assertEquals(hexlify(seed), b'c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04')
        (a0, p0) = compute_address('btc', master, 0)
        self.assertEqual(a0, '1PEha8dk5Me5J1rZWpgqSt5F4BroTBLS5y')
        self.assertEqual(p0, 'L47qcNDdda3QMACwfisBm5XHrXvzTLd9H9Cxz3LBH2J8EBPFvMGo')
        (a10, p10) = compute_address('btc', master, 10)
        self.assertEqual(a10, '1LfvmsJpjSc5xh3QpM9cdxxrHSmD63UyVt')
        self.assertEqual(p10, 'Kwq9q38wfkuVZXVDcAruUUvH9xNERaxvMUkrTRu8uJVp25xEnAyg')
    def test_zcash(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        (a0, p0) = compute_address('zcash', master, 0)
        self.assertEqual(a0, 't1WzpZpunHs2jrxMLmASQ22zfgGNWX7yWK9')
        self.assertEqual(p0, 'L2oEutEe8eKcpdeW64KMVihk1PScYZn1Qn1wjtVswL1R7XQDoDfn')
        (a10, p10) = compute_address('zcash', master, 10)
        self.assertEqual(a10, 't1KgukGc7CdKgG87c6yD5E4UkB3rDEv3BXt')
        self.assertEqual(p10, 'KxyEPn1nUukhZFhBb69MSUYay4ojAe7SFGcW6doyqvEEuERQES2G')
    def test_generate(self):
        self.assertEqual(12, len(generate().split(" ")))

    def test_entropy(self):
        self.assertEqual(u"coconut mystery hub satoshi any mandate option alter client column judge diamond", generate(hash_entropy("hello")))
        
if __name__ == '__main__':
    unittest.main()
