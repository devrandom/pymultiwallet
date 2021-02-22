import unittest
from binascii import hexlify

from mw.mw import generate, hash_entropy, mnemonic_to_master, visual, coin_map

mnemonic1 = 'license diagram pelican spy monitor convince damage script wall hockey goose month popular swamp sugar rose mystery gap regular acquire bottom sea modify eyebrow'
mnemonic2 = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about'


class TestAll(unittest.TestCase):
    def test_cosmos(self):
        (seed, master) = mnemonic_to_master(mnemonic2, '')
        coin = coin_map['cosmos']
        (a0, p0) = coin.address(master, 0)
        self.assertEqual(a0, 'cosmos19rl4cm2hmr8afy4kldpxz3fka4jguq0auqdal4')
        self.assertEqual(p0, 'c4a48e2fce1481cd3294b4490f6678090ea98d3d0e5cd984558ab0968741b104')

    def test_ripple(self):
        (seed, master) = mnemonic_to_master(mnemonic1, '')
        coin = coin_map['xrp']
        (a0, p0) = coin.address(master, 0)
        self.assertEqual(a0, 'r4keqeEf57QZnLeiKr5f4twBoH5Mr9S824')
        self.assertEqual(p0, 'f730f2c7a79fabe94465b2d86f6c7f108d56810d89965f99c6bf193cfc7b0730')

    def test_eth(self):
        (seed, master) = mnemonic_to_master(mnemonic1, '')
        coin = coin_map['eth']
        (a0, p0) = coin.address(master, 0)
        self.assertEqual(a0, '363aa60f6f5b5fc97e6874c6419c5421762dabf8')
        self.assertEqual(p0, '6177745c12c1483cf83bca94e10a0fee4ee5d58a2c0f09b2162a5c3f8a07a27c')
        (a10, p10) = coin.address(master, 10)
        self.assertEqual(a10, 'a6c572a1e51b377fd610861da4b64e6df987bea6')
        self.assertEqual(p10, 'de77e2f9b063355d6e1b98af2717a21020cca03bb3749d86155ded10f2abd775')

    def test_visual(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        self.assertEqual(visual(master), '+-----------------+\n'
                                         '|                 |\n'
                                         '|                 |\n'
                                         '|                 |\n'
                                         '|                 |\n'
                                         '|       .S       =|\n'
                                         '|*.    o=*=     +B|\n'
                                         '|@*     o.*+     .|\n'
                                         '|.      .*+.      |\n'
                                         '|o ...        .E  |\n'
                                         '+-----------------+')

    def test_btc(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        coin = coin_map['btc']
        self.assertEqual(hexlify(seed), b'c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04')
        (a0, p0) = coin.address(master, 0)
        self.assertEqual(a0, '1PEha8dk5Me5J1rZWpgqSt5F4BroTBLS5y')
        self.assertEqual(p0, 'L47qcNDdda3QMACwfisBm5XHrXvzTLd9H9Cxz3LBH2J8EBPFvMGo')
        (a10, p10) = coin.address(master, 10)
        self.assertEqual(a10, '1LfvmsJpjSc5xh3QpM9cdxxrHSmD63UyVt')
        self.assertEqual(p10, 'Kwq9q38wfkuVZXVDcAruUUvH9xNERaxvMUkrTRu8uJVp25xEnAyg')
        (ca0, cp0) = coin.address(master, 0, change=True)
        self.assertEqual(ca0, '1MVkh45Zn9A7ZBga697r34DBiRFLXD4UKG')
        self.assertEqual(cp0, 'L2CWaV2UFB7bUqWA3tjaqtu4opBzCw5ZdDwEwFxUjxj4yr4Lqq8g')

    def test_zcash(self):
        (seed, master) = mnemonic_to_master(mnemonic2, 'TREZOR')
        coin = coin_map['zcash']
        (a0, p0) = coin.address(master, 0)
        self.assertEqual(a0, 't1WzpZpunHs2jrxMLmASQ22zfgGNWX7yWK9')
        self.assertEqual(p0, 'L2oEutEe8eKcpdeW64KMVihk1PScYZn1Qn1wjtVswL1R7XQDoDfn')
        (a10, p10) = coin.address(master, 10)
        self.assertEqual(a10, 't1KgukGc7CdKgG87c6yD5E4UkB3rDEv3BXt')
        self.assertEqual(p10, 'KxyEPn1nUukhZFhBb69MSUYay4ojAe7SFGcW6doyqvEEuERQES2G')

    def test_generate(self):
        self.assertEqual(12, len(generate().split(" ")))

    def test_entropy(self):
        self.assertEqual(u"coconut mystery hub satoshi any mandate option alter client column judge diamond",
                         generate(hash_entropy("hello")))

    def test_btc_bech32(self):
        (_, master) = mnemonic_to_master(mnemonic2, '')
        coin = coin_map['btc']
        (a0, _) = coin.address(master, 0, purpose='p2wpkh')
        self.assertEqual(a0, 'bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu')

    def test_btc_xpub(self):
        (seed, master) = mnemonic_to_master(mnemonic2, '')
        self.assertEqual(hexlify(seed), b'5eb00bbddcf069084889a8ab9155568165f5c453ccb85e70811aaed6f6da5fc19a5ac40b389cd370d086206dec8aa6c43daea6690f20ad3d8d48b2d2ce9e38e4')
        coin = coin_map['btc']
        xpub = coin.xpub(master, None)
        self.assertEqual(xpub, 'xpub6BosfCnifzxcFwrSzQiqu2DBVTshkCXacvNsWGYJVVhhawA7d4R5WSWGFNbi8Aw6ZRc1brxMyWMzG3DSSSSoekkudhUd9yLb6qx39T9nMdj')

        # this one is from https://bip39calculator.com/ + conversion from https://jlopp.github.io/xpub-converter/
        xpub = coin.xpub(master, 'p2wsh')
        self.assertEqual(xpub, 'xpub6CatWdiZiodmUeTDp8LT5or8nmbKNcuyvz7WyksVFkKB4RHwCD3XyuvPEbvqAQY3rAPshWcMLoP2fMFMKHPJ4ZeZXYVUhLv1VMrjPC7PW6V')


if __name__ == '__main__':
    unittest.main()
