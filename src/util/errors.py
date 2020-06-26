from enum import Enum
from typing import List, Any


class Err(Enum):
    # temporary errors. Don't blacklist
    DOES_NOT_EXTEND = -1
    BAD_HEADER_SIGNATURE = -2
    MISSING_FROM_STORAGE = -3
    INVALID_PROTOCOL_MESSAGE = -4
    SELF_CONNECTION = -5
    INVALID_HANDSHAKE = -6
    INVALID_ACK = -7
    INCOMPATIBLE_PROTOCOL_VERSION = -8
    DUPLICATE_CONNECTION = -9
    BLOCK_NOT_IN_BLOCKCHAIN = -10
    NO_PROOF_OF_SPACE_FOUND = -11
    PEERS_DONT_HAVE_BLOCK = -12

    UNKNOWN = -9999

    # permanent errors. Block is unsalvageable garbage.
    BAD_COINBASE_SIGNATURE = 1
    INVALID_BLOCK_SOLUTION = 2
    INVALID_COIN_SOLUTION = 3
    DUPLICATE_OUTPUT = 4
    DOUBLE_SPEND = 5
    UNKNOWN_UNSPENT = 6
    BAD_AGGREGATE_SIGNATURE = 7
    WRONG_PUZZLE_HASH = 8
    BAD_COINBASE_REWARD = 9
    INVALID_CONDITION = 10
    ASSERT_MY_COIN_ID_FAILED = 11
    ASSERT_COIN_CONSUMED_FAILED = 12
    ASSERT_BLOCK_AGE_EXCEEDS_FAILED = 13
    ASSERT_BLOCK_INDEX_EXCEEDS_FAILED = 14
    ASSERT_TIME_EXCEEDS_FAILED = 15
    COIN_AMOUNT_EXCEEDS_MAXIMUM = 16

    SEXP_ERROR = 17
    INVALID_FEE_LOW_FEE = 18
    MEMPOOL_CONFLICT = 19
    MINTING_COIN = 20
    EXTENDS_UNKNOWN_BLOCK = 21
    COINBASE_NOT_YET_SPENDABLE = 22
    BLOCK_COST_EXCEEDS_MAX = 23
    BAD_ADDITION_ROOT = 24
    BAD_REMOVAL_ROOT = 25

    INVALID_POSPACE_HASH = 26
    INVALID_COINBASE_SIGNATURE = 27
    INVALID_PLOT_SIGNATURE = 28
    TIMESTAMP_TOO_FAR_IN_PAST = 29
    TIMESTAMP_TOO_FAR_IN_FUTURE = 30
    INVALID_TRANSACTIONS_FILTER_HASH = 31
    INVALID_POSPACE_CHALLENGE = 32
    INVALID_POSPACE = 33
    INVALID_HEIGHT = 34
    INVALID_COINBASE_AMOUNT = 35
    INVALID_MERKLE_ROOT = 36
    INVALID_BLOCK_FEE_AMOUNT = 37
    INVALID_WEIGHT = 38
    INVALID_TOTAL_ITERS = 39
    BLOCK_IS_NOT_FINISHED = 40
    INVALID_NUM_ITERATIONS = 41
    INVALID_POT = 42
    INVALID_POT_CHALLENGE = 43
    INVALID_TRANSACTIONS_GENERATOR_HASH = 44
    INVALID_POOL_TARGET = 45

    INVALID_COINBASE_PARENT = 46
    INVALID_FEES_COIN_PARENT = 47
    ASSERT_FEE_CONDITION_FAILED = 48


class ConsensusError(Exception):
    def __init__(self, code: Err, errors: List[Any] = []):
        super(ConsensusError, self).__init__(f"Error code: {code.name}")
        self.errors = errors


class ProtocolError(Exception):
    def __init__(self, code: Err, errors: List[Any] = []):
        super(ProtocolError, self).__init__(f"Error code: {code.name}")
        self.code = code
        self.errors = errors
