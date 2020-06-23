import dataclasses


@dataclasses.dataclass(frozen=True)
class ConsensusConstants:
    NUMBER_OF_HEADS: int
    DIFFICULTY_STARTING: int
    DIFFICULTY_FACTOR: int
    DIFFICULTY_EPOCH: int = dataclasses.field(init=False)
    DIFFICULTY_WARP_FACTOR: int
    DIFFICULTY_DELAY: int  # EPOCH / WARP_FACTOR
    SIGNIFICANT_BITS: int  # The number of bits to look at in difficulty and min iters. The rest are zeroed
    DISCRIMINANT_SIZE_BITS: int  # Max is 1024 (based on ClassGroupElement int size)
    BLOCK_TIME_TARGET: int  # The target number of seconds per block
    # The proportion (denominator) of the total time that that the VDF must be run for, at a minimum
    # (1/min_iters_proportion). For example, if this is two, approximately half of the iterations
    # will be contant and required for all blocks.
    MIN_ITERS_PROPORTION: int
    # For the first epoch, since we have no previous blocks, we can't estimate vdf iterations per second
    MIN_ITERS_STARTING: int
    MAX_FUTURE_TIME: int  # The next block can have a timestamp of at most these many seconds more
    NUMBER_OF_TIMESTAMPS: int  # Than the average of the last NUMBEBR_OF_TIMESTAMPS blocks
    # If an unfinished block is more than these many seconds slower than the best unfinished block,
    # don't propagate it.
    PROPAGATION_THRESHOLD: int
    # If the expected time is more than these seconds, slightly delay the propagation of the unfinished
    # block, to allow better leaders to be released first. This is a slow block.
    PROPAGATION_DELAY_THRESHOLD: int
    # Hardcoded genesis block, generated using tests/block_tools.py
    # Replace this any time the constants change.
    GENESIS_BLOCK: bytes
    # Target tx count per sec
    TX_PER_SEC: int
    # Size of mempool = 10x the size of block
    MEMPOOL_BLOCK_BUFFER: int
    # Coinbase rewards are not spendable for 200 blocks
    COINBASE_FREEZE_PERIOD: int
    # Max coin amount uint(1 << 64)
    MAX_COIN_AMOUNT: bytes
    # Raw size per block target = 1,000,000 bytes
    # Rax TX (single in, single out) = 219 bytes (not compressed)
    # TX = 457 vBytes
    # floor(1,000,000 / 219) * 457 = 2086662 (size in vBytes)
    # Max block cost in virtual bytes
    MAX_BLOCK_COST: int
    # MAX block cost in clvm cost units = MAX_BLOCK_COST * CLVM_COST_RATIO_CONSTANT
    # 1 vByte = 108 clvm cost units
    CLVM_COST_RATIO_CONSTANT: int
    # Max block cost in clvm cost units (MAX_BLOCK_COST * CLVM_COST_RATIO_CONSTANT)
    MAX_BLOCK_COST_CLVM: int

    def __post_init__(self):
        # see https://docs.python.org/3/library/dataclasses.html#frozen-instances
        object.__setattr__(self, "DIFFICULTY_EPOCH", self.DIFFICULTY_DELAY * self.DIFFICULTY_WARP_FACTOR)

    def __getitem__(self, key):
        # TODO: remove this
        # temporary, for compatibility
        v = getattr(self, key, None)
        return v

    def copy(self):
        # TODO: remove this
        # temporary, for compatibility
        return dataclasses.asdict(self)


testnet_kwargs = {
    "NUMBER_OF_HEADS": 3,  # The number of tips each full node keeps track of and propagates
    "DIFFICULTY_STARTING": 500,  # These are in units of 2^32
    "DIFFICULTY_FACTOR": 3,  # The next difficulty is truncated to range [prev / FACTOR, prev * FACTOR]
    # These 3 constants must be changed at the same time
    # "DIFFICULTY_EPOCH": 128,  # The number of blocks per epoch
    "DIFFICULTY_WARP_FACTOR": 4,  # DELAY divides EPOCH in order to warp efficiently.
    "DIFFICULTY_DELAY": 32,  # EPOCH / WARP_FACTOR
    "SIGNIFICANT_BITS": 12,  # The number of bits to look at in difficulty and min iters. The rest are zeroed
    "DISCRIMINANT_SIZE_BITS": 1024,  # Max is 1024 (based on ClassGroupElement int size)
    "BLOCK_TIME_TARGET": 300,  # The target number of seconds per block
    # The proportion (denominator) of the total time that that the VDF must be run for, at a minimum
    # (1/min_iters_proportion). For example, if this is two, approximately half of the iterations
    # will be contant and required for all blocks.
    "MIN_ITERS_PROPORTION": 10,
    # For the first epoch, since we have no previous blocks, we can't estimate vdf iterations per second
    "MIN_ITERS_STARTING": (2 ** 17),
    "MAX_FUTURE_TIME": 7200,  # The next block can have a timestamp of at most these many seconds more
    "NUMBER_OF_TIMESTAMPS": 11,  # Than the average of the last NUMBEBR_OF_TIMESTAMPS blocks
    # If an unfinished block is more than these many seconds slower than the best unfinished block,
    # don't propagate it.
    "PROPAGATION_THRESHOLD": 300,
    # If the expected time is more than these seconds, slightly delay the propagation of the unfinished
    # block, to allow better leaders to be released first. This is a slow block.
    "PROPAGATION_DELAY_THRESHOLD": 1500,
    # Hardcoded genesis block, generated using tests/block_tools.py
    # Replace this any time the constants change.
    "GENESIS_BLOCK": b'\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x88\xbe_6 X\xf1\x83\xe8\x99\xdf)\xb8\xf6t\xe0;\x82\x17\xc5\xe5\x94\xb7\xef\xc2|\x94\xe6\xfb\x91L\x85\xe4\x00WVV\xefJ\x1e/>\xf6\xc5Gr5n\x13\x00\x00\x00\x98\xe4\xd8(mep\xcf}\xdb\xd7(\x04N"\xd1I\x18g\xae[\xff\xc0#z\xee\xb7\xbd3f\xe4zR3mi-\x89\x88\xbc\xd3\xf0|\xee\x03\x13\xc9}\xbb\x9b\x7f\x7f\xcfj\x08\x01\xe0*\x1e\x9an\xf6\xba\xd5\xb1\xc1\x80\x96\x8a\x99\xe3\x91\x92j\xce\xfdij\xea\xccT\xd0[\xd0\x89\xdc\xb8\xa3 /\xf27\x0f\x9ce\x87\x9dK\xe7\xab\x01\xbb\x1e\x91U\x95\x0f\xc0c\xa3\xa4\x81Um\x80_\xee\x8f3\xc7\xe3?\xf5\xacyF\x941\x90\x9e\xd1\xd0\x0bB\xa4\xa4\xe18\x13\xd5x\xca\xbd\x9b;\xf9B\xa1y\xaasm\x14\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x03\xaf\x99\x00I\x998~\xb9\x8e;\xed:\x19M\xcfp.\xd3A#8a\xb8\x9eee\xda\xfa\xff\xbc\x1ea\xcfN\xda\xde\x02\xe0\xc0\'3\xe41\x8b\xec\xda<@\xb4\x14,\xb5X)\xdbI\xdcS\xe8/\xfa$\n\xaf\xa6\xe0\xce\xff\xd0\x93x`\xb11\xc4\xa2I\xe1-\xd5\x1c\xc7\xef\x88\x05\xa8\x7f\xddp\x8ak\n\xa3\x96\x80L\xefV\xa2\x82\xfa\x92I\x14\x93\xb6\xfbW\n\xcf=W]\xcb\xc5\x0bf\xce4\x1d]\xb6"\t\x07\x82\x9f\xafq{D5\x00\x00\x00\x00\x82\x00\r\xe0\x13\x03bj\x9aPv\xbd{p\x10.#\xcf\xd3P4\x86?\xbawF\x9bS\x0cK\xd6\x0ex;\xd4\xd2\xc4\x90\xd0\x04"t\x1e\x8br\xd9\x8b@"\xb2\xdd\xb1\x11H\xd0s\'"\x1b\xaeeM\xb9\xe6\xe3\x1a\x00\t\x13\xb7\x94\xb6\xd5*\x90,)\x99n\t\x1b\xb4C4\x0fc~\xa7\xf3\x95\x04\xcc]\x17C\x94\x10\x8d\xde`\xc1\xa7\x93\xefb\xf3\xd9\xb9\x8f\x14\xc9\xdc\x18\xd8\xfd\xbd[\xf5\xb7\xaa\xd1\x8e\x01\x1c\x8eZ\x7f\xad\xdb\xc1M\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00^\x86Ch\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00>\x93h\xb0E\x0c\xaa\xda1\x9a\x04\x83 \xedGe\xf1\'\xab\xc7Z\x9d\xaf!\x18D#\t\x0bz\xe2\xc4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xf4\x00\x00\x00\x00\x00\x03\xaf\x99\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8b)\xaa\x96x8\xd76J\xa6\x8b[\x98\t\xe0\\\xe3^7qD\x8c\xf5q\x08\xf2\xa2\xc9\xb03mv\x00\x00\x0c\xbb\xa1\x06\xe0\x00N\x1f\xe8;}6F\xd7\xec\xc7\x83\x16T\x96\x1f\xe6\x88,\xa4\x9b\xa3Lo\xd0\xe6\x89jW\xac\xba\xae)\xe9\x91?\x97\x0fU\xf5\xd8\xdc\x9e\xce\xbf~\xad\xc2\xbc\x17v|\x947N\x0e\xfa\xff\xe6;\xce@|\xe9{\xe2:\xa8H\xb4\xb9\xde;<;-\x9a\x03\xbf\xa3\xff\xed\x81\x0cd\x80|(I\x9e\x8c\xa5\x83\xdf\x8a\x1aX\x8c\xb9\x01%\x17\xc8\x17\xfe\xade\x02\x87\xd6\x1b\xdd\x9ch\x80;k\xf9\xc6A3\xdc\xab>e\xb5\xa5\x0c\xb9\x8b)\xaa\x96x8\xd76J\xa6\x8b[\x98\t\xe0\\\xe3^7qD\x8c\xf5q\x08\xf2\xa2\xc9\xb03mv\x00\x00\x01\xd1\xa9J \x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$)\xcf\x82\xc23&\xedzR\x04\xb8Zz\xe9\x03\x94\xe1\x0f\xc2\xe1TS\xc2\xb6\xd1\xa5\xf2\xd6\xb4\xae\xfb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00H\xb4H>o\xde\x85\x9b\xf7\xc8S\x80\xb1\xfb,\xe6Kb`\xc9\x95p\xf5\x11\xb6\xda7\x071\xe9Wf5\xa2x\xd15r/\x16\x16\x9c\xb9\x9c\xe6\x94\xbe3\x18\xc1n-{\xa9W\xaf\xc6\x17\xc6\xd7\xa5\xf3jCJ\xb1a\xc3U\xb2)\xbc\x04\xa7V\xa43E\x89\x83\xbfw*\x97MQ\x98\xc6!\xb1\xdey"\xa5@%\x00\x00',  # noqa: E501
    # Target tx count per sec
    "TX_PER_SEC": 20,
    # Size of mempool = 10x the size of block
    "MEMPOOL_BLOCK_BUFFER": 10,
    # Coinbase rewards are not spendable for 200 blocks
    "COINBASE_FREEZE_PERIOD": 200,
    # Max coin amount uint(1 << 64)
    "MAX_COIN_AMOUNT": b"\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF",
    # Raw size per block target = 1,000,000 bytes
    # Rax TX (single in, single out) = 219 bytes (not compressed)
    # TX = 457 vBytes
    # floor(1,000,000 / 219) * 457 = 2086662 (size in vBytes)
    # Max block cost in virtual bytes
    "MAX_BLOCK_COST": 2086662,
    # MAX block cost in clvm cost units = MAX_BLOCK_COST * CLVM_COST_RATIO_CONSTANT
    # 1 vByte = 108 clvm cost units
    "CLVM_COST_RATIO_CONSTANT": 108,
    # Max block cost in clvm cost units (MAX_BLOCK_COST * CLVM_COST_RATIO_CONSTANT)
    "MAX_BLOCK_COST_CLVM": 225359496,
}


constants = ConsensusConstants(**testnet_kwargs)  # type: ignore
