#!/usr/bin/env python
import hashlib
import os
import sys
from abc import ABC, abstractmethod
from binascii import hexlify
from collections import namedtuple
from getpass import getpass
from optparse import OptionParser

import sha3
from mnemonic.mnemonic import Mnemonic
from pycoin.contrib.segwit_addr import bech32_encode, convertbits
from pycoin.encoding import b2a_hashed_base58, to_bytes_32
from pycoin.key.BIP32Node import BIP32Node

from .ripple import RippleBaseDecoder

# mw 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about' TREZOR
# > seed c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04
# ku H:$SEED
# > master xprv9s21ZrQH143K3h3fDYiay8mocZ3afhfULfb5GX8kCBdno77K4HiA15Tg23wpbeF1pLfs1c5SPmYHrEpTuuRhxMwvKDwqdKiGJS9XFKzUsAF
# ku -s "44'/0'/0'/0/0" H:$SEED
# > 1PEha8dk5Me5J1rZWpgqSt5F4BroTBLS5y
VISUALIZATION_PATH = "9999'/9999'"

ripple_decoder = RippleBaseDecoder()


BaseCoin = namedtuple('Coin', ['address_prefix', 'coin_derivation', 'deposit_path', 'change_path'])


class Coin(BaseCoin, ABC):
    @abstractmethod
    def to_address(self, subkey):
        pass

    @abstractmethod
    def to_private(self, exponent):
        pass

    def address(self, master, i, change=False):
        extra_path = self.change_path if change else self.deposit_path
        path = self.coin_derivation + "%s/%d" % (extra_path, i)
        subkey = next(master.subkeys(path))
        private = self.to_private(subkey.secret_exponent())
        address = self.to_address(subkey)
        return address, private

    def has_change_chain(self):
        return self.change_path is not None


class BTCCoin(Coin):
    def to_address(self, subkey):
        return b2a_hashed_base58(self.address_prefix + subkey.hash160())

    def to_private(self, exponent):
        return b2a_hashed_base58(b'\x80' + to_bytes_32(exponent) + b'\01')


class ETHCoin(Coin):
    def to_address(self, subkey):
        hasher = sha3.keccak_256()
        hasher.update(subkey.sec(True)[1:])
        return hexlify(hasher.digest()[-20:]).decode()

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


class XRPCoin(Coin):
    def to_address(self, subkey):
        return ripple_decoder.encode(subkey.hash160())

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


class CosmosCoin(Coin):
    def to_address(self, subkey):
        return bech32_encode(self.address_prefix.decode(), convertbits(subkey.hash160(), 8, 5))

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


coin_map = {
    "btc": BTCCoin(b'\0', "44'/0'/0'", "/0", "/1"),
    "zcash": BTCCoin(b'\x1c\xb8', "44'/1893'/0'", "/0", "/1"),
    "eth": ETHCoin(b'', "44'/60'/0'", "/0", None),
    "rop": ETHCoin(b'', "44'/1'/0'", "/0", None),
    "xrp": XRPCoin(b'', "44'/144'/0'", "/0", None),
    "txrp": XRPCoin(b'', "44'/1'/0'", "/0", None),
    "cosmos": CosmosCoin(b'cosmos', "44'/118'/0'", "/0", None),
}

coins = list(coin_map.keys())

coin_list = ",".join(coins)


def mnemonic_to_master(mnemonic, passphrase):
    seed = Mnemonic.to_seed(mnemonic, passphrase=passphrase)
    master = BIP32Node.from_master_secret(seed)
    return seed, master


def generate(data=None):
    if data is None:
        data = os.urandom(16)
    return Mnemonic('english').to_mnemonic(data)


def hash_entropy(entropy_string):
    ee = hashlib.sha256(entropy_string.encode('utf-8'))
    return ee.digest()[0:16]


def visual(master):
    import hashprint
    subkey = next(master.subkeys(VISUALIZATION_PATH))
    return hashprint.pformat(list(bytearray(subkey.hash160())))


def main():
    parser = OptionParser()
    parser.add_option("-p", "--passphrase", help="use PASSPHRASE, or prompt if not provided", metavar="PASSPHRASE")
    parser.add_option("-r", "--private", default=False, action="store_true", help="show private keys")
    parser.add_option("-s", "--show-seed", default=False, action="store_true", help="show master seed")
    parser.add_option("-c", "--coin", default="btc", help="use COIN, one of: " + coin_list, choices=coins)
    parser.add_option("-n", "--count", default=20, type="int", help="print out N addresses", metavar="N")
    parser.add_option("-g", "--generate", default=False, action="store_true", help="generate a seed")
    parser.add_option("-e", "--entropy", default=False, action="store_true", help="type some entropy")
    parser.add_option("-q", "--quiet", default=False, action="store_true", help="do not print visual seed")

    (options, args) = parser.parse_args()

    if len(args) > 1:
        sys.stderr.write('too many arguments - did you quote the phrase?\n')
        sys.exit(1)

    entropy = None
    if options.entropy:
        sys.stdout.write("Enter entropy string followed by a \\n. ")
        sys.stdout.write("No entropy is added, make sure you provide enough.\n")
        sys.stdout.write(": ")
        entropy_string = input()
        entropy = hash_entropy(entropy_string)
    
    if options.generate:
        print(generate(entropy))
        exit()

    passphrase = options.passphrase if options.passphrase is not None else getpass('Passphrase: ')
    (seed, master) = mnemonic_to_master(args[0], passphrase)

    if options.show_seed:
        print(hexlify(seed))
        exit()

    if not options.quiet:
        visualization = visual(master)
        if sys.stdout.isatty():
            from .colorize import colorize
            print(colorize(visualization))
        else:
            print(visualization)

    coin = coin_map[options.coin]

    for i in range(options.count):
        (address, private) = coin.address(master, i)
        if options.private:
            print("%s %s" % (address, private))
        else:
            print("%s" % (address,))


if __name__ == "__main__":
    main()
