import itertools
from hashlib import sha256

import pytest

from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.merkle_set import MerkleSet, confirm_included_already_hashed


class TestMerkleSet:
    @pytest.mark.asyncio
    async def test_basics(self, bt):
        num_blocks = 20
        blocks = bt.get_consecutive_blocks(num_blocks)

        merkle_set = MerkleSet()
        merkle_set_reverse = MerkleSet()
        coins = list(itertools.chain.from_iterable(map(lambda block: block.get_included_reward_coins(), blocks)))

        # excluded coin (not present in 'coins' and Merkle sets)
        excl_coin = coins.pop()

        for coin in reversed(coins):
            merkle_set_reverse.add_already_hashed(coin.name())

        for coin in coins:
            merkle_set.add_already_hashed(coin.name())

        for coin in coins:
            result, proof = merkle_set.is_included_already_hashed(coin.name())
            assert result is True
            result_excl, proof_excl = merkle_set.is_included_already_hashed(excl_coin.name())
            assert result_excl is False
            validate_proof = confirm_included_already_hashed(merkle_set.get_root(), coin.name(), proof)
            validate_proof_excl = confirm_included_already_hashed(merkle_set.get_root(), excl_coin.name(), proof_excl)
            assert validate_proof is True
            assert validate_proof_excl is False

        # Test if the order of adding items changes the outcome
        assert merkle_set.get_root() == merkle_set_reverse.get_root()


def hashdown(buf: bytes) -> bytes32:
    return bytes32(sha256(bytes([0] * 30) + buf).digest())


@pytest.mark.asyncio
async def test_merkle_set_invalid_hash_size():
    merkle_set = MerkleSet()

    # this is too large
    with pytest.raises(AssertionError):
        merkle_set.add_already_hashed(bytes([0x80] + [0] * 32))

    # this is too small
    with pytest.raises(AssertionError):
        merkle_set.add_already_hashed(bytes([0x80] + [0] * 30))

    # empty
    with pytest.raises(AssertionError):
        merkle_set.add_already_hashed(b"")


@pytest.mark.asyncio
async def test_merkle_set_1():
    a = bytes32([0x80] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    assert merkle_set.get_root() == sha256(b"\1" + a).digest()


@pytest.mark.asyncio
async def test_merkle_set_duplicate():
    a = bytes32([0x80] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    merkle_set.add_already_hashed(a)
    assert merkle_set.get_root() == sha256(b"\1" + a).digest()


@pytest.mark.asyncio
async def test_merkle_set_0():
    merkle_set = MerkleSet()
    assert merkle_set.get_root() == bytes32([0] * 32)


@pytest.mark.asyncio
async def test_merkle_set_2():
    a = bytes32([0x80] + [0] * 31)
    b = bytes32([0x70] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    merkle_set.add_already_hashed(b)
    assert merkle_set.get_root() == hashdown(b"\1\1" + b + a)


@pytest.mark.asyncio
async def test_merkle_set_2_reverse():
    a = bytes32([0x80] + [0] * 31)
    b = bytes32([0x70] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(b)
    merkle_set.add_already_hashed(a)
    assert merkle_set.get_root() == hashdown(b"\1\1" + b + a)


@pytest.mark.asyncio
async def test_merkle_set_3():
    a = bytes32([0x80] + [0] * 31)
    b = bytes32([0x70] + [0] * 31)
    c = bytes32([0x71] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    merkle_set.add_already_hashed(b)
    merkle_set.add_already_hashed(c)
    assert merkle_set.get_root() == hashdown(b"\2\1" + hashdown(b"\1\1" + b + c) + a)
    # this tree looks like this:
    #
    #        o
    #      /  \
    #     o    a
    #    / \
    #   b   c


@pytest.mark.asyncio
async def test_merkle_set_4():
    a = bytes32([0x80] + [0] * 31)
    b = bytes32([0x70] + [0] * 31)
    c = bytes32([0x71] + [0] * 31)
    d = bytes32([0x81] + [0] * 31)
    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    merkle_set.add_already_hashed(b)
    merkle_set.add_already_hashed(c)
    merkle_set.add_already_hashed(d)
    assert merkle_set.get_root() == hashdown(b"\2\2" + hashdown(b"\1\1" + b + c) + hashdown(b"\1\1" + a + d))
    # this tree looks like this:
    #
    #        o
    #      /   \
    #     o     o
    #    / \   / \
    #   b   c a   d


@pytest.mark.asyncio
async def test_merkle_set_5():
    BLANK = bytes32([0] * 32)

    a = bytes32([0x58] + [0] * 31)
    b = bytes32([0x23] + [0] * 31)
    c = bytes32([0x21] + [0] * 31)
    d = bytes32([0xCA] + [0] * 31)
    e = bytes32([0x20] + [0] * 31)

    merkle_set = MerkleSet()
    merkle_set.add_already_hashed(a)
    merkle_set.add_already_hashed(b)
    merkle_set.add_already_hashed(c)
    merkle_set.add_already_hashed(d)
    merkle_set.add_already_hashed(e)

    # build the expected tree bottom up, since that's simpler
    expected = hashdown(b"\1\1" + e + c)
    expected = hashdown(b"\2\1" + expected + b)
    expected = hashdown(b"\2\0" + expected + BLANK)
    expected = hashdown(b"\2\0" + expected + BLANK)
    expected = hashdown(b"\2\0" + expected + BLANK)
    expected = hashdown(b"\0\2" + BLANK + expected)
    expected = hashdown(b"\2\1" + expected + a)
    expected = hashdown(b"\2\1" + expected + d)

    assert merkle_set.get_root() == expected
    # this tree looks like this:
    #
    #             o
    #            / \
    #           o   d
    #          / \
    #         o   a
    #        / \
    #       E   o
    #          / \
    #         o   E
    #        / \
    #       o   E
    #      / \
    #     o   E
    #    / \
    #   o   b
    #  / \
    # e   c
