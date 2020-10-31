from typing import Dict, Any


def find_fork_point_in_chain(hash_to_block: Dict, block_1: Any, block_2: Any) -> int:
    """Tries to find height where new chain (block_2) diverged from block_1 (assuming prev blocks
    are all included in chain)
    Returns -1 if chains have no common ancestor
    """
    while block_2.height > 0 or block_1.height > 0:
        if block_2.height > block_1.height:
            block_2 = hash_to_block[block_2.prev_header_hash]
        elif block_1.height > block_2.height:
            block_1 = hash_to_block[block_1.prev_header_hash]
        else:
            if block_2.header_hash == block_1.header_hash:
                return block_2.height
            block_2 = hash_to_block[block_2.prev_header_hash]
            block_1 = hash_to_block[block_1.prev_header_hash]
    if block_2 != block_1:
        # All blocks are different
        return -1

    # First block is the same
    return 0
