#!/usr/bin/env python
import hashlib
import os
import sys
from abc import ABC, abstractmethod
from binascii import hexlify
from getpass import getpass
from optparse import OptionParser

import sha3
from mnemonic.mnemonic import Mnemonic
from pycoin.contrib.segwit_addr import bech32_encode, convertbits
from pycoin.encoding import b2a_hashed_base58, to_bytes_32
from pycoin.key.BIP32Node import BIP32Node

from .ripple import RippleBaseDecoder

# mw -p TREZOR 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about'
# > seed c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04
# ku H:$SEED
# > master xprv9s21ZrQH143K3h3fDYiay8mocZ3afhfULfb5GX8kCBdno77K4HiA15Tg23wpbeF1pLfs1c5SPmYHrEpTuuRhxMwvKDwqdKiGJS9XFKzUsAF
# ku -s "44'/0'/0'/0/0" H:$SEED
# > 1PEha8dk5Me5J1rZWpgqSt5F4BroTBLS5y
VISUALIZATION_PATH = "9999'/9999'"

ripple_decoder = RippleBaseDecoder()


class Coin(ABC):
    def __init__(self, address_prefix, coin_derivation, deposit_path, change_path):
        self.address_prefix = address_prefix
        self.coin_derivation = coin_derivation
        self.deposit_path = deposit_path
        self.change_path = change_path

    @abstractmethod
    def to_address(self, subkey, purpose):
        pass

    @abstractmethod
    def to_private(self, exponent):
        pass

    def path(self, i, change, purpose):
        extra_path = self.change_path if change else self.deposit_path
        return self.base_derivation(purpose) + "%s/%d" % (extra_path, i)

    def address(self, master, i, change=False, purpose=None):
        path = self.path(i, change, purpose)
        subkey = next(master.subkeys(path))
        private = self.to_private(subkey.secret_exponent())
        address = self.to_address(subkey, purpose)
        return address, private

    def has_change_chain(self):
        return self.change_path is not None

    def can_generate_addresses(self, purpose):
        return True

    def xpub(self, master, purpose):
        raise NotImplementedError()

    def base_derivation(self, purpose):
        return self.coin_derivation


class BTCCoin(Coin):
    def __init__(self, *args, bech_prefix):
        super().__init__(*args)
        self.bech_prefix = bech_prefix

    def can_generate_addresses(self, purpose):
        if purpose == 'p2wsh':
            return False
        return True

    def path(self, i, change, purpose):
        base_derivation = self.base_derivation(purpose)
        extra_path = self.change_path if change else self.deposit_path
        return base_derivation + "%s/%d" % (extra_path, i)

    def base_derivation(self, purpose):
        if purpose is None or purpose == 'p2pkh':
            purpose_path = "44"
        elif purpose == 'p2wpkh' or purpose == 'p2wsh':
            purpose_path = "84"
        else:
            raise RuntimeError('invalid purpose ' + purpose)
        return self.coin_derivation % purpose_path

    def to_address(self, subkey, purpose):
        if purpose == 'p2wpkh':
            return bech32_encode(self.bech_prefix, [0] + convertbits(subkey.hash160(), 8, 5))
        elif purpose == 'p2wsh':
            raise RuntimeError('no addresses can be generated for p2wsh')
        else:
            return b2a_hashed_base58(self.address_prefix + subkey.hash160())

    def to_private(self, exponent):
        return b2a_hashed_base58(b'\x80' + to_bytes_32(exponent) + b'\01')

    def xpub(self, master, purpose):
        base_derivation = self.base_derivation(purpose)
        subkey = next(master.subkeys(base_derivation))
        return subkey.as_text()


class ETHCoin(Coin):
    def to_address(self, subkey, _purpose):
        hasher = sha3.keccak_256()
        hasher.update(subkey.sec(True)[1:])
        return hexlify(hasher.digest()[-20:]).decode()

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


class XRPCoin(Coin):
    def to_address(self, subkey, _purpose):
        return ripple_decoder.encode(subkey.hash160())

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


class CosmosCoin(Coin):
    def to_address(self, subkey, _purpose):
        return bech32_encode(self.address_prefix.decode(), convertbits(subkey.hash160(), 8, 5))

    def to_private(self, exponent):
        return hexlify(to_bytes_32(exponent)).decode()


coin_map = {
    "btc": BTCCoin(b'\0', "%s'/0'/0'", "/0", "/1", bech_prefix='bc'),
    "tbtc": BTCCoin(b'\x6f', "%s'/1'/0'", "/0", "/1", bech_prefix='tb'),
    "zcash": BTCCoin(b'\x1c\xb8', "%s'/1893'/0'", "/0", "/1", bech_prefix=None),
    "eth": ETHCoin(b'', "44'/60'/0'", "/0", None),
    "rop": ETHCoin(b'', "44'/1'/0'", "/0", None),
    "xrp": XRPCoin(b'', "44'/144'/0'", "/0", None),
    "txrp": XRPCoin(b'', "44'/1'/0'", "/0", None),
    "cosmos": CosmosCoin(b'cosmos', "44'/118'/0'", "/0", None),
}

coins = list(coin_map.keys())

coin_list = ', '.join(coins)

purposes = ['p2pkh', 'p2wpkh', 'p2wsh']

purpose_list = ', '.join(purposes)


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
    parser = OptionParser(usage="""Usage: %prog [options] [MNEMONIC_PHRASE]
    Note that the mnemonic phrase is required if --generate is not supplied. 
    """)
    parser.add_option("-p", "--passphrase", help="use an additional wallet passphrase, will prompt if not provided."
                                                 " Pass an empty string to not have a passphrase.", metavar="PASSPHRASE")
    parser.add_option("-r", "--show-private", default=False, action="store_true", help="show private keys")
    parser.add_option("-s", "--show-seed", default=False, action="store_true", help="show master seed")
    parser.add_option("-x", "--show-xpub", default=False, action="store_true", help="show xpub")
    parser.add_option("-c", "--coin", default="btc", help="use COIN, one of: " + coin_list, choices=coins)
    parser.add_option("-n", "--count", default=20, type="int", help="print out N addresses", metavar="N")
    parser.add_option("-g", "--generate", default=False, action="store_true", help="generate a seed")
    parser.add_option("-e", "--entropy", default=False, action="store_true", help="type some entropy")
    parser.add_option("-q", "--quiet", default=False, action="store_true", help="do not print visual seed")
    parser.add_option("-u", "--purpose", default=None, help="one of: " + purpose_list, choices=purposes)
    parser.add_option("-a", "--change", default=False, action="store_true", help="show change addresses")

    (options, args) = parser.parse_args()

    if len(args) > 1:
        sys.stderr.write('too many arguments - did you quote the mnemonic phrase?\n')
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

    print("base derivation path: %s" % coin.base_derivation(options.purpose))

    if options.show_xpub:
        print("xpub: %s" % coin.xpub(master, options.purpose))

    if coin.can_generate_addresses(options.purpose):
        for i in range(options.count):
            (address, private) = coin.address(master, i, change=options.change, purpose=options.purpose)
            if options.show_private:
                print("%s %s" % (address, private))
            else:
                print("%s" % (address,))
    else:
        if not options.show_xpub:
            print("no addresses can be shown for %s, try --show-xpub" % options.purpose)


if __name__ == "__main__":
    main()
