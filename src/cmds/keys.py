from pathlib import Path
from blspy import PrivateKey, ExtendedPrivateKey
from src.cmds.init import check_keys
from src.util.keychain import (
    generate_mnemonic,
    bytes_to_mnemonic,
    Keychain,
    seed_from_mnemonic,
)


def make_parser(parser):
    parser.add_argument(
        "-m",
        "--mnemonic",
        type=str,
        nargs=24,
        default=None,
        help="Enter mnemonic you want to use",
    )
    parser.add_argument(
        "-k", "--key", type=str, default=None, help="Enter the raw private key in hex",
    )
    parser.add_argument(
        "-f",
        "--fingerprint",
        type=int,
        default=None,
        help="Enter the fingerprint of the key you want to delete",
    )

    parser.add_argument(
        "command", help="", type=str, nargs=1,
    )
    parser.set_defaults(function=handler)


keychain: Keychain = Keychain()


def generate_and_print():
    """
    Generates a seed for a private key, and prints the mnemonic to the terminal.
    """

    mnemonic = generate_mnemonic()
    mnemonics_string = mnemonic_to_string(mnemonic)
    print("Generating private key. Mnemonic:")
    print(mnemonics_string)
    print(
        "Note that this key has not been added to the keychain. Run chia keys add_seed -m [MNEMONICS] to add"
    )
    return mnemonic


def generate_and_add():
    """
    Generates a seed for a private key, prints the mnemonic to the terminal, and adds the key to the keyring.
    """

    mnemonic = generate_mnemonic()
    print("Generating private key.")
    add_private_key_seed(mnemonic)


def add_private_key_seed(mnemonic):
    """
    Add a private key seed to the keyring, with the given mnemonic.
    """

    try:
        seed = seed_from_mnemonic(mnemonic)
        fingerprint = (
            ExtendedPrivateKey.from_seed(seed).get_public_key().get_fingerprint()
        )
        print(
            f"Adding private key with public key fingerprint {fingerprint} and mnemonic"
        )
        print(f"{mnemonic_to_string(mnemonic)}")

        keychain.add_private_key_seed(seed)
    except ValueError as e:
        print(e)
        return


def add_private_key(args):
    """
    Adds a private key to the keyring, without a seed (with the raw private key bytes).
    """

    key_hex = args.key
    extended_key = ExtendedPrivateKey.from_bytes(bytes.fromhex(key_hex))
    print(
        f"Adding private_key: {extended_key} with fingerprint {extended_key.get_public_key().get_fingerprint()}"
    )
    keychain.add_private_key(extended_key)


def add_private_key_not_extended(args):
    """
    Adds a not extended private key to the keyring. This can be used for migrating old pool sks from keys.yaml.
    """

    key_hex = args.key
    private_key = PrivateKey.from_bytes(bytes.fromhex(key_hex))
    print(
        f"Adding private_key: {private_key} with fingerprint {private_key.get_public_key().get_fingerprint()}"
    )
    keychain.add_private_key_not_extended(private_key)


def mnemonic_to_string(mnemonic):
    """
    Converts a menmonic to a user readable string in the terminal.
    """
    mnemonics_string = ""

    for i in range(0, 24):
        mnemonics_string += f"{i + 1}) {mnemonic[i]}"
        if i != 23:
            mnemonics_string += ", "
        if (i + 1) % 6 == 0:
            mnemonics_string += "\n"

    return mnemonics_string


def show_all_keys():
    """
    Prints all keys and mnemonics (if available).
    """

    private_keys = keychain.get_all_private_keys()
    if len(private_keys) == 0:
        print("There are no saved private keys.")
        return
    print("Showing all private keys:")
    for sk, seed in private_keys:
        print("")
        print("Fingerprint:", sk.get_public_key().get_fingerprint())
        print("Extended private key:", bytes(sk).hex())
        if seed is not None:
            mnemonic = bytes_to_mnemonic(seed)
            mnemonic_string = mnemonic_to_string(mnemonic)
            print("Mnemonic seed:")
            print(mnemonic_string)
        else:
            print(
                "There is no mnemonic for this key, since it was imported without a seed. (Or migrated from keys.yaml)."
            )


def delete(args):
    """
    Delete a key by it's public key fingerprint (which is an int).
    """

    fingerprint = args.fingerprint
    print(f"Deleting private_key with fingerprint {fingerprint}")
    keychain.delete_key_by_fingerprint(fingerprint)


def handler(args, parser):
    root_path: Path = args.root_path
    if not root_path.is_dir():
        raise RuntimeError(
            "Please initialize (or migrate) your config directory with chia init."
        )

    command_list = [
        "generate",
        "generate_and_add",
        "show",
        "add_seed",
        "add",
        "add_not_extended",
        "delete",
        "delete_all",
    ]

    command = args.command[0]
    if command not in command_list:
        print(f"Available commands: {command_list}")
        return 1

    if command == "generate":
        generate_and_print()
    if command == "generate_and_add":
        generate_and_add()
        check_keys(root_path)
    elif command == "show":
        show_all_keys()
    elif command == "add_seed":
        add_private_key_seed(args.mnemonic)
        check_keys(root_path)
    elif command == "add":
        add_private_key(args)
        check_keys(root_path)
    elif command == "add_not_extended":
        add_private_key_not_extended(args)
        check_keys(root_path)
    elif command == "delete":
        delete(args)
        check_keys(root_path)
    elif command == "delete_all":
        keychain.delete_all_keys()
