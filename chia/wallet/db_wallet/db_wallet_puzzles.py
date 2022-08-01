from typing import Iterator, Tuple, Union

from chia.types.blockchain_format.program import Program
from chia.types.blockchain_format.sized_bytes import bytes32
from chia.util.ints import uint64
from chia.wallet.nft_wallet.nft_puzzles import NFT_STATE_LAYER_MOD, create_nft_layer_puzzle_with_curry_params
from chia.wallet.puzzles.load_clvm import load_clvm

# from chia.types.condition_opcodes import ConditionOpcode
# from chia.wallet.util.merkle_tree import MerkleTree, TreeType

ACS_MU = Program.to(11)  # returns the third argument a.k.a the full solution
ACS_MU_PH = ACS_MU.get_tree_hash()
SINGLETON_TOP_LAYER_MOD = load_clvm("singleton_top_layer_v1_1.clvm")
# TODO: need new data layer specific clvm
SINGLETON_LAUNCHER = load_clvm("singleton_launcher.clvm")


def create_host_fullpuz(innerpuz: Union[Program, bytes32], current_root: bytes32, genesis_id: bytes32) -> Program:
    db_layer = create_host_layer_puzzle(innerpuz, current_root)
    mod_hash = SINGLETON_TOP_LAYER_MOD.get_tree_hash()
    singleton_struct = Program.to((mod_hash, (genesis_id, SINGLETON_LAUNCHER.get_tree_hash())))
    return SINGLETON_TOP_LAYER_MOD.curry(singleton_struct, db_layer)


def create_host_layer_puzzle(innerpuz: Union[Program, bytes32], current_root: bytes32) -> Program:
    # some hard coded metadata formatting and metadata updater for now
    return create_nft_layer_puzzle_with_curry_params(
        Program.to((current_root, None)),
        ACS_MU_PH,
        # TODO: the nft driver doesn't like the Union yet, but changing that is out of scope for me rn - Quex
        innerpuz,  # type: ignore
    )


def match_dl_singleton(puzzle: Program) -> Tuple[bool, Iterator[Program]]:
    """
    Given a puzzle test if it's a CAT and, if it is, return the curried arguments
    """
    mod, singleton_curried_args = puzzle.uncurry()
    if mod == SINGLETON_TOP_LAYER_MOD:
        mod, dl_curried_args = singleton_curried_args.at("rf").uncurry()
        if mod == NFT_STATE_LAYER_MOD and dl_curried_args.at("rrf") == ACS_MU_PH:
            launcher_id = singleton_curried_args.at("frf")
            root = dl_curried_args.at("rff")
            innerpuz = dl_curried_args.at("rrrf")
            return True, iter((innerpuz, root, launcher_id))

    return False, iter(())


def launch_solution_to_singleton_info(launch_solution: Program) -> Tuple[bytes32, uint64, bytes32, bytes32]:
    solution = launch_solution.as_python()
    try:
        full_puzzle_hash = bytes32(solution[0])
        amount = uint64(int.from_bytes(solution[1], "big"))
        root = bytes32(solution[2][0])
        inner_puzzle_hash = bytes32(solution[2][1])
    except (IndexError, TypeError):
        raise ValueError("Launcher is not a data layer launcher")

    return full_puzzle_hash, amount, root, inner_puzzle_hash
