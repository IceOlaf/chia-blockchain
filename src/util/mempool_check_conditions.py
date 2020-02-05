from typing import Optional, List, Dict, Tuple

import clvm
from clvm import EvalError
from clvm.casts import int_from_bytes

from src.types.ConditionVarPair import ConditionVarPair
from src.types.hashable.Coin import CoinName
from src.types.hashable.Program import Program, ProgramHash
from src.types.hashable.SpendBundle import SpendBundle
from src.types.hashable.Unspent import Unspent
from src.types.name_puzzle_condition import NPC
from src.types.pool import Pool
from src.util.Conditions import ConditionOpcode
from src.util.ConsensusError import Err
from src.util.consensus import conditions_dict_for_solution
import time

from src.util.ints import uint64
from src.util.run_program import run_program


def mempool_assert_coin_consumed(
    condition: ConditionVarPair, spend_bundle: SpendBundle, mempool: Pool
) -> Optional[Err]:
    """
    Checks coin consumed conditions
    Returns None if conditions are met, if not returns the reason why it failed
    """
    bundle_removals = spend_bundle.removals_dict()
    coin_name = condition.var1
    if coin_name not in bundle_removals:
        return Err.ASSERT_COIN_CONSUMED_FAILED
    return None


def mempool_assert_my_coin_id(
    condition: ConditionVarPair, unspent: Unspent
) -> Optional[Err]:
    """
    Checks if CoinID matches the id from the condition
    """
    if unspent.coin.name() != condition.var1:
        return Err.ASSERT_MY_COIN_ID_FAILED
    return None


def mempool_assert_block_index_exceeds(
    condition: ConditionVarPair, unspent: Unspent, mempool: Pool
) -> Optional[Err]:
    """
    Checks if the next block index exceeds the block index from the condition
    """
    try:
        expected_block_index = int_from_bytes(condition.var1)
    except ValueError:
        return Err.INVALID_CONDITION
    # + 1 because min block it can be included is +1 from current
    if mempool.header_block.height + 1 <= expected_block_index:
        return Err.ASSERT_BLOCK_INDEX_EXCEEDS_FAILED
    return None


def mempool_assert_block_age_exceeds(
    condition: ConditionVarPair, unspent: Unspent, mempool: Pool
) -> Optional[Err]:
    """
    Checks if the coin age exceeds the age from the condition
    """
    try:
        expected_block_age = int_from_bytes(condition.var1)
        expected_block_index = expected_block_age + unspent.confirmed_block_index
    except ValueError:
        return Err.INVALID_CONDITION
    if mempool.header_block.height + 1 <= expected_block_index:
        return Err.ASSERT_BLOCK_AGE_EXCEEDS_FAILED
    return None


def mempool_assert_time_exceeds(condition: ConditionVarPair):
    """
    Check if the current time in millis exceeds the time specified by condition
    """
    try:
        expected_mili_time = int_from_bytes(condition.var1)
    except ValueError:
        return Err.INVALID_CONDITION

    current_time = uint64(int(time.time() * 1000))
    if current_time < expected_mili_time:
        return Err.ASSERT_TIME_EXCEEDS_FAILED
    return None


async def get_name_puzzle_conditions(
    block_program: Program,
) -> Tuple[Optional[Err], List[NPC], int]:
    """
    Returns an error if it's unable to evaluate, otherwise
    returns a list of NPC (coin_name, solved_puzzle_hash, conditions_dict)
    """

    try:
        cost, sexp = run_program(block_program, [])
    except EvalError:
        breakpoint()
        return Err.INVALID_COIN_SOLUTION, [], 0

    npc_list = []
    for name_solution in sexp.as_iter():
        _ = name_solution.as_python()
        if len(_) != 2:
            return Err.INVALID_COIN_SOLUTION, [], cost
        if not isinstance(_[0], bytes) or len(_[0]) != 32:
            return Err.INVALID_COIN_SOLUTION, [], cost
        coin_name = CoinName(_[0])
        if not isinstance(_[1], list) or len(_[1]) != 2:
            return Err.INVALID_COIN_SOLUTION, [], cost
        puzzle_solution_program = name_solution.rest().first()
        puzzle_program = puzzle_solution_program.first()
        puzzle_hash = ProgramHash(Program(puzzle_program))
        try:
            error, conditions_dict = conditions_dict_for_solution(
                puzzle_solution_program
            )
            if error:
                return error, [], cost
        except clvm.EvalError:
            return Err.INVALID_COIN_SOLUTION, [], cost
        if conditions_dict is None:
            conditions_dict = {}
        npc: NPC = NPC(coin_name, puzzle_hash, conditions_dict)
        npc_list.append(npc)

    return None, npc_list, cost


def mempool_check_conditions_dict(
    unspent: Unspent,
    spend_bundle: SpendBundle,
    conditions_dict: Dict[ConditionOpcode, List[ConditionVarPair]],
    mempool: Pool,
) -> Optional[Err]:
    """
    Check all conditions against current state.
    """
    for con_list in conditions_dict.values():
        cvp: ConditionVarPair
        for cvp in con_list:
            error = None
            if cvp.opcode is ConditionOpcode.ASSERT_COIN_CONSUMED:
                error = mempool_assert_coin_consumed(cvp, spend_bundle, mempool)
            elif cvp.opcode is ConditionOpcode.ASSERT_MY_COIN_ID:
                error = mempool_assert_my_coin_id(cvp, unspent)
            elif cvp.opcode is ConditionOpcode.ASSERT_BLOCK_INDEX_EXCEEDS:
                error = mempool_assert_block_index_exceeds(cvp, unspent, mempool)
            elif cvp.opcode is ConditionOpcode.ASSERT_BLOCK_AGE_EXCEEDS:
                error = mempool_assert_block_age_exceeds(cvp, unspent, mempool)
            elif cvp.opcode is ConditionOpcode.ASSERT_TIME_EXCEEDS:
                error = mempool_assert_time_exceeds(cvp)

            if error:
                return error

    return None
