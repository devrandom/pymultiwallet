#!/usr/bin/env python
import sha3
from optparse import OptionParser
from mnemonic.mnemonic import Mnemonic
import sys
import os
import hashlib
from binascii import hexlify, unhexlify
from pycoin.key.BIP32Node import BIP32Node
from pycoin.networks import full_network_name_for_netcode, network_name_for_netcode
from pycoin.encoding import b2a_hashed_base58, to_bytes_32
from getpass import getpass
from .colorize import colorize
import hashprint

# mw 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about' TREZOR
# > seed c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04
# ku H:$SEED
# > master xprv9s21ZrQH143K3h3fDYiay8mocZ3afhfULfb5GX8kCBdno77K4HiA15Tg23wpbeF1pLfs1c5SPmYHrEpTuuRhxMwvKDwqdKiGJS9XFKzUsAF
# ku -s "44'/0'/0'/0/0" H:$SEED
# > 1PEha8dk5Me5J1rZWpgqSt5F4BroTBLS5y

def btc_to_address(prefix, subkey):
    return b2a_hashed_base58(prefix + subkey.hash160())

def btc_to_private(exponent):
    return b2a_hashed_base58(b'\x80' + to_bytes_32(exponent) + b'\01')

def eth_to_address(prefix, subkey):
    hasher = sha3.keccak_256()
    hasher.update(subkey.sec(True)[1:])
    return hexlify(hasher.digest()[-20:])

def eth_to_private(exponent):
    return hexlify(to_bytes_32(exponent))

coin_map = {
        "btc": (b'\0', "44'/0'/0'/0", btc_to_address, btc_to_private),
        "zcash": (b'\x1c\xb8', "44'/1893'/0'/0", btc_to_address, btc_to_private),
        "eth": (b'', "44'/60'/0'", eth_to_address, eth_to_private)
        }
coins = list(coin_map.keys())

coin_list = ",".join(coins)

def mnemonic_to_master(mnemonic, passphrase):
    seed = Mnemonic.to_seed(mnemonic, passphrase=passphrase)
    master = BIP32Node.from_master_secret(seed)
    return (seed, master)

def compute_address(coin, master, i):
    (address_prefix, coin_derivation, to_address, to_private) = coin_map[coin]
    path = coin_derivation + "/%d"%(i,)
    subkey = next(master.subkeys(path))
    private = to_private(subkey.secret_exponent())
    address = to_address(address_prefix, subkey)
    return (address, private)

def generate(data=None):
    if data is None:
        data = os.urandom(16)
    return Mnemonic('english').to_mnemonic(data)

def hash_entropy(entropy_string):
    ee = hashlib.sha256(entropy_string.encode('utf-8'))
    return ee.digest()[0:16]

def visual(seed):
    return colorize(hashprint.pformat(list(bytearray(seed[0:32]))))

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

    entropy = None
    if (options.entropy):
        sys.stdout.write("Enter entropy string followed by a \\n. ")
        sys.stdout.write("No entropy is added, make sure you provide enough.\n")
        sys.stdout.write(": ")
        entropy_string = raw_input()
        entropy = hash_entropy(entropy_string)
    
    if (options.generate):
        print(generate(entropy))
        exit()

    passphrase = options.passphrase if options.passphrase is not None else getpass('Passphrase: ')
    (seed, master) = mnemonic_to_master(args[0], passphrase)

    if options.show_seed:
        print(hexlify(seed))
        exit()

    if not options.quiet:
        print(visual(seed))

    for i in range(options.count):
        (address, private) = compute_address(options.coin, master, i)
        if options.private:
            print("%s %s"%(address, private))
        else:
            print("%s"%(address))

if __name__ == "__main__":
    main()
