PyMultiWallet
=============

A python tool for creating mnemonic HD wallets with multiple coin support.


Currently supported coins:

- Bitcoin
- Zcash
- Ethereum

Features:

- Additional passphrase

Usage
======

```
pip install -e .
mnemonic='abandon abandon abandon abandon abandon\
 abandon abandon abandon abandon abandon abandon about'
mw -p TREZOR -r -c zcash $mnemonic
```

results in:

```
t1WzpZpunHs2jrxMLmASQ22zfgGNWX7yWK9 L2oEutEe8eKcpdeW64KMVihk1PScYZn1Qn1wjtVswL1R7XQDoDfn
t1McxjZf1AEwnR6ztb8QsbhDVHvAJ2ZmiJD L59gGcB5RmoWewCden8aJcSZ7moADx6wrPcP8KddnwnmGbKYXYWn
t1J3Nc3HAnCMndPr7ouyQoGeC86ZUYVLMSF L4hQ4LSjtwibfWcRqYv9W3P2MaNn4VqWXzL97uhZXYmWM7CJLCns
...
```
