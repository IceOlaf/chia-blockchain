from typing import List, Union, Dict

from src.consensus.constants import ConsensusConstants
from src.full_node.sub_block_record import SubBlockRecord
from src.types.full_block import FullBlock
from src.types.header_block import HeaderBlock
from src.types.sized_bytes import bytes32
from src.types.unfinished_block import UnfinishedBlock
from src.types.unfinished_header_block import UnfinishedHeaderBlock


def get_block_challenge(
    constants: ConsensusConstants,
    genesis_block: bool,
    header_block: Union[UnfinishedHeaderBlock, UnfinishedBlock, HeaderBlock, FullBlock],
    overflow: bool,
    prev_sb: SubBlockRecord,
    sub_blocks: Dict[bytes32, SubBlockRecord],
    skip_overflow_last_ss_validation: bool,
):
    if len(header_block.finished_sub_slots) > 0:
        if overflow:
            # New sub-slot with overflow block
            if skip_overflow_last_ss_validation:
                # In this case, we are missing the final sub-slot bundle (it's not finished yet)
                challenge: bytes32 = header_block.finished_sub_slots[-1].challenge_chain.get_hash()
            else:
                challenge: bytes32 = header_block.finished_sub_slots[
                    -1
                ].challenge_chain.challenge_chain_end_of_slot_vdf.challenge
        else:
            # No overflow, new slot with a new challenge
            challenge: bytes32 = header_block.finished_sub_slots[-1].challenge_chain.get_hash()
    else:
        if genesis_block:
            challenge = constants.FIRST_CC_CHALLENGE
        else:
            if overflow:
                # Overflow infusion, so get the second to last challenge
                challenges_to_look_for = 2
            else:
                challenges_to_look_for = 1
            reversed_challenge_hashes: List[bytes32] = []
            curr: SubBlockRecord = prev_sb
            while len(reversed_challenge_hashes) < challenges_to_look_for:
                if curr.first_in_sub_slot:
                    reversed_challenge_hashes += reversed(curr.finished_challenge_slot_hashes)
                if curr.height == 0:
                    break
                curr = sub_blocks[curr.prev_hash]
            challenge = reversed_challenge_hashes[challenges_to_look_for - 1]
    return challenge
