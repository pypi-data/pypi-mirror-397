import yescrypt_hash
from binascii import unhexlify, hexlify

import unittest

# dash block #1
# moo@b1:~/.globalboost$ globalboostd getblockhash 1
# d98cca456363cac31036a33d8e56566e9519943337f8e7b40eea796bb612e011
# moo@b1:~/.globalboost$ globalboostd getblock d98cca456363cac31036a33d8e56566e9519943337f8e7b40eea796bb612e011


#{
#  "hash": "d98cca456363cac31036a33d8e56566e9519943337f8e7b40eea796bb612e011", 11e212b66b79ea0eb4e7f837339419956e56568e3da33610c3ca636345ca8cd9
#  "confirmations": 555870,
#  "height": 1,
#  "version": 2,
#  "versionHex": "00000002", 02000000
#  "merkleroot": "642bb90ace1374f9e07057a7fbdf5885fbd0d3be2284981aacdf319d730039ac", ac3900739d31dfac1a988422bed3d0fb8558dffba75770e0f97413ce0ab92b64
#  "time": 1410223951, 540E4F4F 4F4F0E54
#  "mediantime": 1410223951,
#  "nonce": 96, 00000060 60000000
#  "bits": "1f3fffff", ffff3f1f
#  "difficulty": 2.384149979653205e-07,
#  "chainwork": "0000000000000000000000000000000000000000000000000000000000100410",
#  "nTx": 1,
#  "previousblockhash": "2e28050194ad73f2405394d2f081361a23c2df8904ec7f026a018bbe148d5adf", df5a8d14be8b016a027fec0489dfc2231a3681f0d2945340f273ad940105282e
#  "nextblockhash": "21446f3a6b1656701011ea0baef179f2edfc2ea444cd1b95e347783660298302",
#  "strippedsize": 186,
#  "size": 186,
#  "weight": 744,
#  "tx": [
#   "642bb90ace1374f9e07057a7fbdf5885fbd0d3be2284981aacdf319d730039ac"
#  ]
#}

header_hex = ("02000000" +
    "df5a8d14be8b016a027fec0489dfc2231a3681f0d2945340f273ad940105282e" +
    "ac3900739d31dfac1a988422bed3d0fb8558dffba75770e0f97413ce0ab92b64"
    "4f4f0e54" +
    "ffff3f1f" +
    "60000000")

best_hash = b'1f89267b62241f314a256d4a3a41c74ca099b2ea501586544d6b3bb8539c3800' # This is the Proof Work hash 

class TestSequenceFunctions(unittest.TestCase):

    def setUp(self):
        self.block_header = unhexlify(header_hex)
        self.best_hash = best_hash

    def test_yescrypt_hash(self):
        self.pow_hash = hexlify(yescrypt_hash.getPoWHash(self.block_header))
        self.assertEqual(self.pow_hash, self.best_hash)


if __name__ == '__main__':
    unittest.main()
