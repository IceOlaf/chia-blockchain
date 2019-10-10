constants = {
    "NUMBER_OF_HEADS": 3,  # The number of tips each full node keeps track of and propagates
    "DIFFICULTY_STARTING": 20,  # These are in units of 2^32
    "BLOCK_TIME_TARGET": 10,  # The target number of seconds per block
    "DIFFICULTY_FACTOR": 4,  # The next difficulty is truncated to range [prev / FACTOR, prev * FACTOR]

    # These 3 constants must be changed at the same time
    "DIFFICULTY_EPOCH": 12,  # The number of blocks per epoch
    "DIFFICULTY_WARP_FACTOR": 4,  # DELAY divides EPOCH in order to warp efficiently.
    "DIFFICULTY_DELAY": 3,  # EPOCH / WARP_FACTOR

    "DISCRIMINANT_SIZE_BITS": 1024,

    # The percentage of the difficulty target that the VDF must be run for, at a minimum
    "MIN_BLOCK_TIME_PERCENT": 20,
    "MIN_VDF_ITERATIONS": 1,  # These are in units of 2^32

    "MAX_FUTURE_TIME": 7200,  # The next block can have a timestamp of at most these many seconds more
    "NUMBER_OF_TIMESTAMPS": 11,  # Than the average of the last NUMBEBR_OF_TIMESTAMPS blocks

    # If an unfinished block is more than these many seconds slower than the best unfinished block,
    # don't propagate it.
    "PROPAGATION_THRESHOLD": 1800,
    # If the expected time is more than these seconds, slightly delay the propagation of the unfinished
    # block, to allow better leaders to be released first. This is a slow block.
    "PROPAGATION_DELAY_THRESHOLD": 600,

    # Hardcoded genesis block, generated using block tools
    # GENESIS_BLOCK = b'\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x14\x00\x00\x00\xa0_\x11\x18\x8d3\xa1\x8b\x8b1Q1@Z 6Q\xb4\xba\xafn{\x1c\xb5\xd7\xa4\xd9{\x93\xa1KB \xd2\x9fxK\xd1n\xa0wN\xfd&\nw\xbb7tm$/7\xa0f%\xf6\xd4\xc5\x1c\x98\xef\xb0\xd0\x10D\x10\x1a\x9b\xc3\xf8xd\x9d\xab\xaa>\xff\x7f\x84E\t.\xe5gz\\\x9a|\xdeE\x93\xe1\xba\xb9\xd0E\x1f\x9f\xc6\xb7\x89/\x0e8)\x1f\xdd\xc0\xa7\xa5|\xf0\\\xdf\xf9\xd1\xdbZm\xe6\xcb\xa5|F\xc1\xa3\x89\x87L\x14\xb8\xd9\xe82gIB\xe4\x14\x01q\x15r\xc1"E\x99\xc4\x10+\x0b^\xed?F\x01\x00Cs\x1a\x01\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x00\x00\x00\x00\x00\x00\tH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x035*\x14\xda\xd9\xbbqE\xc6\xa1\x00\\\x8a^&\xc0\xec2\xa1\x16s\x0f\x8b\xe9\xbd\x0c\xe5\xca\x8fO\x06\x10\xfa\x85V!\xe9\xf6S\x97lu\xe6J\xcd\xb6\xfe\xa1F6g\xf2\xa6\xa6-\xa9~\x7f\x80:bGs\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xfe\xf3\xe8G5o&\xb6\x16\xf5\xe7n\xb9-\xebeO-0+\xbe\xc5\x96\xe3\x0f\x1be_<:\xed\xaa\xe8\x80\xbb\xa0Z\x1b>\xa1\x87(\xe9\xba\x08\xdf\xfe\x83n\xe1r\x9aUQ\xe5z9\xd8+D\xd5H\x11\xdd\x03\x00\x00\x03\x8e\x00Cr\xfa\x1c\x06\xb5\xd1\xcd\x8e\xf8\xdc\xbd\x19\xb4 \xb3\x19$\x0fsF\xd1\xbew\xad\x14\xab@\xdf\xc2\x14[\xef\xf0\xd536)\xf5\xfcN\x10\xfbK\xc3\xaeu\x01\xc0\xc8\x1e\x8e\x95:hf\xea?\\MSH\xb8\x88\x00/\x1f[!D\xfc\xb7w\x04\xf8L\xdd\x8b\x06:\xd4\xe7\xf5\xfcR\x11\\Ra}\xa7\x9aH\x9b0\x05\x9f\x80\xf5_3\xfd\xb8\x89R\xa7\xe4\xc0R\x17\xe9B\x1c7S#\xd4\xb1\x8a4zJ\xee\xb1\x01\xce\xd4\x0e\xff\x00EY\x90\x0bV\x8d0\xba\x8d\xf33e8\xe7\x9a\xa5Y~\x08\x19r\xcfP\x88\x8d\xbc\xd3TE\xedWc\x14\xc5-\x1b\xbc\x9e\xbf\xde\xa8\x1b\x90U\xa7\xdc.\xa8\xd6\xe6\'\xf1\x03\x89\xf8\t7\xfez\x02\xda\xae\xc3\xa6\xff\xfc\x07\x9a\xfb\xa6\xcf6\xa7\x8fP\x12\x17\xaa\x1f\xda\xae\xeaS\xac\xd2D\xa5\xe0\xc5\xe3\xab\'\x00\x84_\xabnZ\xf5\xd4\x10\xbd&\x16\xae\x1b{\xa0,%\x1f\xac\x08\x0b\r\xcb\xf7\xb0Ed\xa5h?\xb29^\xe1>\xed\x00O7\xbb\r$\xb5\x03\xaf\r\x0cy\\!_\xa1\xa3\xadE\xd5\x88\xe7\xef\x1d\x8c\x8a\xb0\x8bU\xde\x88\x01\xc0\xe0\xb5h\xe3\x94\x98c,j4\x18j\xe2\xd7\xa2\x05V\xce\xb9=  \x05L\xbb\xcb\x9c\x99\xb6d\xa7\x1f\xff\xbb\xf1\xa3\x99q\xfdg\xc9\x89\xbc\xb8\xbdj\xc5hu\x0bZ\xe3\xa1\x7f\xcc\x0f\xfd\x10\xa1z\xe1\xcd\xb0\xcby=\x93:\xb5\xa7 \x07\xb6.\x07\x9c\xbaR\x97\xb1@\xf4V\xc0Qs\x06\x115x\x82\xb24@\xc4\xa5\x97\x00-\xc220\x85\xfd\x01\xd6\xfb\xe7oM\xa2~\xb8^\xa7\x13\xf5V\xb2\x84ax\x8c\x93H(!\x9a\xbb\xc8\xdb\x01\x0e\xc3l\xc1\xe2E\x92d\xc8B\xfdnt\x11\x11\xd9a\x8bP\x11\x87<Y\xab\xb3:\xa6B\xf6*\x00\n\xd3$b\xd1\xc2\xfd\x8b1\xa6\xc3Vb\x01\xe1\x97\x1e\xad\x127\xe2w\xaf\x1b"\xf2\x03h\xf1\xd24\'\xc2\x00\xb8\xa0\x06J\xba8[\xa7\xedK}SZ\x0b\xe5\xead\xf3\x18\xe6\x07j\xbc$\xb64f\xf0\x98u\x00F\xac\xf3\x92\xe9=\xb2`o~b\xd6\x81/\x05\xb5\xd8\xb1\xd2H\xb5\xe8\x08"4U\x89ykX\xe3\x17\xc1\x19a\xe74\xab\x97\xa1\x8c}\xae\x8c\xea\xd6X\xc9\xe0\xcf\x9f\xe6q]bEi\x0b\xec\x80\xa4\n\xea*\xff\xc0\xaag\x92\xe7\xa1\x9c\x0f[\xd4\xef\x1b\xbd\xf8\xf95\xd0\xc6\xab\xe1\x11\xca\xe9\x14od^,c\x9dm\x1b\x7f1\x07\xad6|\xf9\x01\xa5\xf5\x162\x7fnpu\xde\x8a\x8c\xa5K\xa9[\x1cL\x1cB\xf5\xb9\xdaU\x9b\x00[^:j\x1bH\xe9\xc5\xe4\xe0.\xaf\x00\xaan\xa3\x8a\x12\x85\x00\xdf\xd8\xbe.\xd6\xe3\xcc\xec\xab4\x8b3\xf7 #T;a\xf4\xd4\x05\xb7\xf8B\x08\x1dc\x184\x07\x86MQ?N\x82\xd5t"\xd6\x1dL\xfa\xcf\x00\x15\x1e\xac\x12\xc97`p\x037\xc6\x17_\x81\xc7\x93\x85\x84\x91\xce\xf2_\xe6&\ri\xbcx\xb8T\x06l\x1e\xed\xbeS30T"Dk\xd2\x8e\x1e\xac7\x19Y\x94\x9f\xe8Lb\xd5\x1e%%l\xb7[\xb4A\xc7\x00\x1a\x17\x11\x83.]\x18\x93\xfd\xad\xfb\x98\x0c\x10\x8d\x18M\xe5T\xd2\xf1\xe8)\xccb\xed\x1b\xdf*\x07\xbe\x10\xa1\x84BtA\xa5>\xad\xedQ\xe0_\x1f>aR\x0f\xc5\xa0v\x16\x16\xf6\x94[g\xf6\xb6W\xc3\xc1\xfd\xff\xfc\x05$\x13h\x08\xdd\x97\xf4\xffQdS\xe5\x00\xdd\x9f{`\x91`\x88\xe9\xf5\xed\x8e.\xa4\x81\r\xd4\x80\x81\xc5]\x1b\xb5\xa3\x15\xde\xb9\x86\x9d\xcen&\xd3\xea\xf0SP\x84\xac\x9cqo9)\xcc\x114\xab\x973\x01\xad\xb1SA\x1e\xe5\x1d\x94\xd7\xfb\xb2\xf5:\x82[\xfb7\xfe\x81\x83\x1e\x1bIMT\xb7\nRIk\xb6]O\x97.y\xf5\xf1]\xc1\x89\xbf\x87\xcc\xa9,\x87\xc1\x13\xbcN&\xcc4\xf5h \x8d\xb1\xcd\xcc\xd1;2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x00\x00\x00\x00\tH\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\x8c\x86s\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xad\xb1SA\x1e\xe5\x1d\x94\xd7\xfb\xb2\xf5:\x82[\xfb7\xfe\x81\x83\x1e\x1bIMT\xb7\nRIk\xb6]z!\xc9N\xd5\x03\x8b^\xd9\xe6\xc7I\xba\xb1\x0fm\xd4\xa0=\xb6^s\x94_f\xb5\xc1\\n\xfe\xf9\xd2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xd8.\x1a\xd1\xa9f/B\xa9\xaaO\xe7\xb8O\x87\x9d(\xb0]\xf2r0\xdb]\x03\x81B\xa4\x04\xfc\xc4\xfc~\xcd\xf4\xe5\xb0\xa8{<\xe3.\xc1g\x84Y{V\x06\x1c\x15\xaf\xa47rD\xab\xb1-\xc9\x86\xbf&q\xf4\xc2_\xb3\x05\xa8\xb7\xbf\xb4\x0e\x7f\x85\xfa\xa1\xd3\xc6pS\xc6:\x13\xea2La0\xcf\xe35\xa2\xf1R\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\xd3tK\xda`\xb5u\xca\x8c\xa2\xf7n\x1d\xd5\x92l\xb13k\xdb\n+\xbe/\x1e\xc0\xfe\xbf\xd9\x83\x88V\x11]~.<\x14\x0f\xce`\x8b\xbf\xb9\xa7\xce"6\x19\xa5\x19|\x81!r\x15V\xa6\x82\x07\x96w\x98F\xce\xb2(G\xcfm\x17@t\xb2\x1b\xba\xcf4I}\x0b\xc4\n\xd4\x9b\xe2E\x9e\x84\x98mY||\xa8[+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    # "GENESIS_BLOCK": b'\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x14\x00\x00\x00\xa0_\x11\x18\x8d3\xa1\x8b\x8b1Q1@Z 6Q\xb4\xba\xafn{\x1c\xb5\xd7\xa4\xd9{\x93\xa1KB \xd2\x9fxK\xd1n\xa0wN\xfd&\nw\xbb7tm$/7\xa0f%\xf6\xd4\xc5\x1c\x98\xef\xb0\xd0\x10D\x10\x1a\x9b\xc3\xf8xd\x9d\xab\xaa>\xff\x7f\x84E\t.\xe5gz\\\x9a|\xdeE\x93\xe1\xba\xb9\xd0E\x1f\x9f\xc6\xb7\x89/\x0e8)\x1f\xdd\xc0\xa7\xa5|\xf0\\\xdf\xf9\xd1\xdbZm\xe6\xcb\xa5|F\xc1\xa3\x89\x87L\x14\xb8\xd9\xe82gIB\xe4\x14\x01q\x15r\xc1"E\x99\xc4\x10+\x0b^\xed?F\x01\x00Cs\x1a\x01\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x00\x00\x00\x00\x00\x00\x060\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00[^:j\x1bH\xe9\xc5\xe4\xe0.\xaf\x00\xaan\xa3\x8a\x12\x85\x00\xdf\xd8\xbe.\xd6\xe3\xcc\xec\xab4\x8b3\xf7 #T;a\xf4\xd4\x05\xb7\xf8B\x08\x1dc\x184\x07\x86MQ?N\x82\xd5t"\xd6\x1dL\xfa\xcf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x15\x1e\xac\x12\xc97`p\x037\xc6\x17_\x81\xc7\x93\x85\x84\x91\xce\xf2_\xe6&\ri\xbcx\xb8T\x06l\x1e\xed\xbeS30T"Dk\xd2\x8e\x1e\xac7\x19Y\x94\x9f\xe8Lb\xd5\x1e%%l\xb7[\xb4A\xc7\x03\x00\x00\x03\x8e\x00P\x1e\xce\x92\xbb\x8bcWOopup\xe7"\xfb\xc1\x0e\xfd\x00\xb3U\xef\x07\xa4\x14\xbd\xdaw\xa1h\xd20.\x06\xc8\'\xe3d\x89LU\x1e\xdf\xb7\xeao\x9a\x0eZ@s3[\xc6\x0b\x90\xf5\xb1GKK\\\xfd\x00=\xf4\x9ai\xf6\xf3\n\x8fx\x9d\xf8\x859\x85\x90I\x84\xa8qO\x1d\xdcy\x1f*\x83\xea"\xfc\t\x02\x1cx\xe8\xba\xcf\x15\xbe\x1dM\x8bEU\x03\'d\xf6\xb5b\xc7X\xf2\xfc>G\xfa\xf7I\xd4h<\xa9Y\xc7\x00\t\x1c~\t\xa8\x03R\xf5\t\x83\x99\\T\x02\xf8$\x06\x88\x16\xa2\'\xb1\x95K+"\x9c\x9eU\xe8\x00!\xcbr4\xd8\xc0\xae\xa9\x86\xe0m\xef\x16\xfa\x7f \xdd&(\xe5Rj\xa6x\xab`\xebvQ\x19/\x96\xc1\xff\xfc\xb3\x14\xe6#\xc6\x02\xa8,n\xfd\x92\xfb\x82D\xc7\xe9\x94\xc4\xac\xdc\xf0O\x9d\x15\t\x8f\xa9In%\xe4q\xd3\x1a\r\xe2\x1e7b\x86\xd2\xb0=C\xfe<\xe3&\xa8\x13\xb1vl\x9f\x1f\x9c\x06\xf3\x98zi\xc4\xc3\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\t\x1c~\t\xa8\x03R\xf5\t\x83\x99\\T\x02\xf8$\x06\x88\x16\xa2\'\xb1\x95K+"\x9c\x9eU\xe8\x00!\xcbr4\xd8\xc0\xae\xa9\x86\xe0m\xef\x16\xfa\x7f \xdd&(\xe5Rj\xa6x\xab`\xebvQ\x19/\x96\xc1\xff\xfc\xb3\x14\xe6#\xc6\x02\xa8,n\xfd\x92\xfb\x82D\xc7\xe9\x94\xc4\xac\xdc\xf0O\x9d\x15\t\x8f\xa9In%\xe4q\xd3\x1a\r\xe2\x1e7b\x86\xd2\xb0=C\xfe<\xe3&\xa8\x13\xb1vl\x9f\x1f\x9c\x06\xf3\x98zi\xc4\xc3\x00\x1dP\x98\xaaB\x9fu\x83\xca3\xe1)\xff8\xbc\x92\x19N6\xab\x9dp\xb1E\x99N/}\x9a\xef\xdf\xe1\x8bX\r`>\xc7Y{]\xf09\xd6\x82\t\xb8U\xca\xa4\xc2\x15\xcb\r\xf7@\x1aMM\xe9/q2\xb9\xff\xef\x05\xc1\xfa\xd5\x1c\xf2\'\xc6\xf5\x11\xe7\x12\x11\\\xe6CO?Ii\xff+JB\xfdd]>DS\xf3\x88;\xa4\xa1\xd3ZA\xf5\xf9\x0c\xe3\x9f\x1b\xa8\x99\xebE\x98\xe9T),V\xd3P?N\x85\x04H\xa9\xd1\x000\xae|\xcc\x02\x9f\x86[\x0f\x19\x94vt\x92\xb7\x80\x90\xbd(\xe5\xf8\x95T\xa1)\xb7\x95`?\xb0&\xce\xb3\x10\xaa0\xfe|\\\x0f;z,\xed\x98i\x02\xb7\xde\'9B`RYS\x05q\xfa0g\x81\xca\xf9\x00\x00\xb3\xaf2\xb8\x12\x0f\x7f\x81\xcazE\xda\x82\xa2x\xbaM\xa4\xe9\xfd\xae\x96\x85\xe8\xcdv\xb82d\xc7\xbb\xae!yS\x10\xd1\xb9AU7\x9c\xb9\xf0\x0f\xb2\xb0\x02\xfc(\x1bd\xef\x04\xda\xed.\xfen\x9b!\xbb]\x00^\x99@\xef\xab\x96\xaaDy\xbaB\xde\x96\xae/\xbe\xa4q\xb0xr.\xd2\xcc\xcd4\xaf\x8df\xe5j\x0c\x98\xc8>dz\x04PC{\xa0\xac\xa6\x9f\xc31\xb3j\xfa\x89\xc3u$\x16\x87\xe7\xf3\x9c\xc8D5L$\xff\xfa\xf3u\xcd|\x1a9\x94\xa0\xca\x1acw\xd8\x7f\xb9\xca\x98\xc69Z\x89\xefZ|\xc5K\x96U\xa4\xcb\x8e\x11\xf7M\x14V\xb4\x9d:`g\xd9O\x9c\nt\xbf%\x1c\xad\xfd]\xf7t\xe8~|\x8a\x16\xb5\x89\x98a\x01\xad\xb1SA\x1e\xe5\x1d\x94\xd7\xfb\xb2\xf5:\x82[\xfb7\xfe\x81\x83\x1e\x1bIMT\xb7\nRIk\xb6]\xcf{+\xdd\x80;g\x12\x81%6\xde\tx\x90\xe72\x96\xe8m\xda\xba\xe3@\x01\xd0\xd0#\xbe-\t\xe8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00\x060\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\x8dV4\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xad\xb1SA\x1e\xe5\x1d\x94\xd7\xfb\xb2\xf5:\x82[\xfb7\xfe\x81\x83\x1e\x1bIMT\xb7\nRIk\xb6]z!\xc9N\xd5\x03\x8b^\xd9\xe6\xc7I\xba\xb1\x0fm\xd4\xa0=\xb6^s\x94_f\xb5\xc1\\n\xfe\xf9\xd2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xc2B\x15\xbd\xb4\x02n\x03~\x1fK$\xf7\xe0|\xb1\x9a-Mg\xac\xc4\x8c%R\x08j|\x1d1\x8cB,\xc9\xbd\xe2\xf1\r\x8c\x0c\x0bO{b\xf7\xee\xe6e\x04>\xab\xba8\xde\x1eu\xc6\xae\x0e<I\xd0\xce\xb2\x82\x01\n4\xafh\xa1C\xc4\xf0S\xe7\xe6\xe9\xb2e\xd4\x10F,\x81\xa4\x98Fl\x9d6\xd4k\x0e\x89+\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\xd3tK\xda`\xb5u\xca\x8c\xa2\xf7n\x1d\xd5\x92l\xb13k\xdb\n+\xbe/\x1e\xc0\xfe\xbf\xd9\x83\x88V\x11]~.<\x14\x0f\xce`\x8b\xbf\xb9\xa7\xce"6\x19\xa5\x19|\x81!r\x15V\xa6\x82\x07\x96w\x98F\xce\xb2(G\xcfm\x17@t\xb2\x1b\xba\xcf4I}\x0b\xc4\n\xd4\x9b\xe2E\x9e\x84\x98mY||\xa8[+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
    "GENESIS_BLOCK": b'\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x16\xee\x03\x08\xb2\xb3 l\x95\x14\x1f\xcbx\xdd\x9b\xdd?\x05\xce\xd6T\xbf\xd1\xaf\xc1\xed\x87\x0c\xefk\xf4&\xb3L\xcb\\\x8bJ<S\tri\xad\xd3\x01\x7f\xca\x13\x00\x00\x00\x98\xcb\xe9\xc7Ei\x84u\x8c\x1cP\x1e\x85\x05\xb8\x9b\xee\xcd\xb3\xdajb\xff=z\x1cn\x932\x97\xff\x9e\xea@v"DV\x04cb\x9d\xd3\xee\x9eE\xdcP\xf8D\x8f|\x83B\x06`\x10\xa9\xa9^\xaf\xdb\xd8Via.\xfa\x00\xbe\xc5\xf7i\xce\ti\tBZZ\x83f\x08}\xcf\xb5\x91\xa8\xf7A\xc7.\xca\x9d0lYZ\xe9\x05\xa0~2\x18\xbc\x19\xf1w\xcf^\x96\xd1 \xf6\x18\x10\x05\x81\xfeiV\xd0\xb0\x80\x88\\\xc2\\\xf3\xcb\x9b\xf0\xc8\xfbh\x9e}H\xc1\xa3)\xff_\xf0jy\xafe\xf2\xf66N\xa3\x01\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x04\x00\x00\x00\x00\x00\x00 a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00HC7R\xc6\x01T\xca\x1c*;I\x038\xd1\xce\x91\xd4=\x03\x979\xdfq\xe1\xca"i\xe2\xfbA\xe4\x89\xa6\xa3\xc9,\xeeH>\x10\x85\x1a\xb9\x8c\\\xfcr\x04\x1a\t\x98\x9f\xfc\'S\xef\x16J*\xd8F\xa1\xdc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x000~\x0b5\x7f=\xf6B\xd9\\\xec\x84j\xfc\xcf\x961\x82\x83O >\x9fw\x11\x0e;\xe5@\xa7\xe4BM\x13\xa0\x06\r\x90\xaa\x8c\xdcr\xdc\xa7\x98\xb6\xc2\xd1\xd2ak\x9c\x02*;K\x82{e\xae"\xbd-o\x03\x00\x00\x03\xa6\x00%L\xecf\n] \x1cY\x88\xce\x7f@,\xf9\x03\x04&\xe8\x06(\xd3\xc7\x10\x88\xd2q{1\x98\x13M<\xb8\x1e\x99}\x81\xccJP.\xebg\x84J\x86\x0f\x17\xf0g\x19\xb83\xf3\xd4G\xa3\xa40\xaa\xfd\xa9Q\x00\x11\xdc*\x86\xa5\xd9 =\x07\x87O\\\xfc\xb3\x087\xf2\xe2\x16\x85\xea\xdcS\xdc\xf4\xdd\xd6\xcbc\xb1=\xffh\x8f\xe12\xf6\xa9n\xf5)\x0c\xc8^\x12\x82%\x0c\xf0fR\xf6\\\xed\x8d8OC\xeb\xbf\xf3A\xf3\xb1\x00\x00\x00\x00\x00\x00\x01Y\x00\'\x02\'2bHQc\x9f\xe2\xa7\xadO\r\x9f\x8b\xd1\xcf\x18\x814\'\xcd\xb2L\xb0\xa9\xfbk\xf9\xd0\xe4\xed\xe4p\xa9\x19\xee\xe4\xae8\xbd}\x12\xd4\xef\xd6\xdd\x92\xbcNJ\x00c\xcat{\xf6\xb3\xd5\xf3\x10]\x9d\x00\x0b\xc8\xcf\xebP\xa1 Vt\x18uY\x96\xee\x96\x18\xb4\x8a\x91b\x8d\xa3V\x87{o\xfc\xee\xff\xa0p|\xf1p\xd6\xa9>( \x9d\xf7\xcd\xdc@P\x0c\x14\xc4<L\x04\xdaUj\x18}\x8f\x8c \x12O\xd5\x00\x9f\x00J\xc0\x1f\xe8)q\x7f\xa1,\xda\xd8H\xfd\x8f\xabZb\x8dZ\xc5\xe6\xa7cl\xb4\xfe<\x1dt\xc4\xe1\xebc_?\x89%\xd0z\xd2_\xd9\xde\xb5\xc1I\'`\x9aS\x8e\xd5\x02\x07\x89\x87\x08Ji\xdb\xfd\xa8h\xba\x00(Z1\xbf\xd36\xe1\x06\x0f\x9b\xe2WP\xd7\x9f\xe3T\x7f\x16%%\x072\xcc\xd0\xa8\x17\x86o\x017\xacN\x97\xdf\x01=\x97\xcc\xa9\x8cH\x98\x1c\x82\xaa\xfc\x90\x07\x16\x0e\xb6\xa5\xb7z\xb9\xb1\xed9g\xdc\x94O\x81\x00\x00\x00\x00\x00\x00\x05f\x00_\xf4\xb5\xd7G4Bo,\x18\xa9>\x8cYX\xcd\xf5\xfbU\xfb\x81\x9cT\xa6\xf1\x89\x0f\'\x8a\xf8Y+\xd1\xc7C\xf2\xf8!{\xef,b\xe7\xf8\xfc\x01\xe9^\xbe\xf8\xec\xaes\xce\x8e^\xae\xf2\xf6x\xc1\xfb\xe60\x00M\x1c!k9\x9dbC\xb8\x7fT\xc1-\xdf\xec\xb9\x82X\xaaV\x1a~`\xa5#p\x81\xd9O(O`|\xbdp\xaf\n\xc9\xf4;l\x06\xd4\x110\x0f\xf8K\x13\xdc\xa0\x17\xddR\xd6d\xc5\x86\xfd8\xac\x9f4\xbf\x00\x0c\x84\xb3\x82\xa2\x9a"\x1cdh.-\x19\xee)E\x86\x8b,dN\xbd\xe1\x96\x0b\xdc\x7f\xb3^S\xf7\x9e\xd7\x99`H~\x8a=\xcf\xcacy\xa2\xc50H\xc0~W ^ar\x94l\xac/Q<\xf1k\xa6\x98\x00\x00&\x95\xd9O`\xe4\x90\x9aM2\x1eA&\xd0\x93 \xaa\x9b\x81\xf2\xcc\xfb<\xeeR\x16\xaarQ\x06\xbe\xb7\x82}?\x0e\xbb2\x86]\xb7}cl\xc5/\xd2.\xa7"\xd8\n\xfd\xf8`\xf5;\x00V\x15\x8dbA\x00\x00\x00\x00\x00\x00\x18H\x005{\x16\xf2\x8e\xb1\xee#\x0bG\x9d\xf4WUm\xc7\xa2\xc8\xc5\x99\x10X\x8d"\xd0\x08\xf3\xc2\x06\x03\\\xf9*\xc1\x11\x1f\x06e\x1apdi\xeb\t\x15:l\x02vO\x8eEw2,,\xcf\xf8:\nC\xf8\xf1\xbd\xff\xed\xd3\xc6F,\x0bD\x96\x98\xffv\xbf\xe7\n\xf8\x85\xf7s\xb5\xe0\xa4\x14\x86\x84(u\x8d)\xf9\x15d~]\xdc\xef\x8c\xfb\x83\x97UF\xc3[\xf2*OI\xb9[\xdbQ^\xa0\x7fQ\xa2\x19R~\xb1K9\x9eW\x00\x1fL\x00\xe6!\xba\x9d/l\xc3\xd9IS\xea\x1aF[\nL\xd9\xd8\xc8\x0e8\rA\xeci~j\x85\x0exG.\x00I\xe5n\xa2\xa1\xb38\x05)P\x19\xc0\x1c&_\x02\xc5z>5\xf2\xaa\\V\xe6\x1f\xe1\xf3\x00\x05\x00?\xaeo\xa2&I\x1e\xbc5\xd2?\xb8\xda\xec"8!]!uGV\x03\x8d\x1e\x1e\'\x10\x1cM\xcaq\xa7\x11(\xdc\x8a\xb0P\xa9\x05\x87\xef\rd/X\x7f>\x04\x08\x12\xd9R\xa2\xfdg\x87\x99.\xc3\xd9\x01\xcb\tN\x9d\x1dHq\x14\xe5m\xc1(U!NR\x8ev\xe8L\xfd\xe3Nbj\r\x91n\x1f\xc3\x8d\xa8\xda\x1b*e\x05L\x1ab\xde9aK\xf1E\xac\x80\xd6\x9f\x08\xf2;2\x18\xd2\x86\x17\\\xbdN\xc2x:\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00\x00 a\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\x9e\xad8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xcb\tN\x9d\x1dHq\x14\xe5m\xc1(U!NR\x8ev\xe8L\xfd\xe3Nbj\r\x91n\x1f\xc3\x8d\xa8)\xed\xd8&\xa6\xf4\xf5}h,\x0ch\x95S\x12\x95\x0f\x9c\xac\xbebG\xde\xef\x81\xe0\xeczQ\xc5\xcfk\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00A\xbb\xe5S\xb3\xa9\x9b{\xcd]T\xa3p77\xc7\x96u\xa2l\xc6\x97\nn\xd4\xe8j70Z\x164\xe7\xa8i~\x9b\x9f\x9b(\x1b\x17\x83\xc9\xd4\xc1&\r\x00?iD\x03\xbb\xceGIT\x1d\xcf\x91$\x95\x1b\x92V=\x91\xc5\xa6\x14S\x0bdy\xbc\xf2\x86\xc7\x08\xda\x99\r\xff\xf4\xfe\xdf\xb7\xfc\xa6O\x1d\xbfP4\xde\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x8b)\xaa\x96x8\xd76J\xa6\x8b[\x98\t\xe0\\\xe3^7qD\x8c\xf5q\x08\xf2\xa2\xc9\xb03mvU\x1a\xe2\x181\x88\xfe\t\x03?\x12\xadj\x9d\xe8K\xb8!\xee\xe7e8\x82\xfb$\xf0Y\xfaJ\x10\x1f\x1a\xe5\xe9\xa8\xbb\xea\x87\xfc\xb12y\x94\x8d,\x16\xe4C\x02\xba\xe6\xac\x94{\xc4c\x07(\xb8\xeb\xab\xe3\xcfy{6\x98\t\xf4\x8fm\xd62\x85\x87\xb0\x03f\x01B]\xe3\xc6\x13l6\x8d\x0e\x18\xc64%\x97\x1a\xa6\xf4\x8b)\xaa\x96x8\xd76J\xa6\x8b[\x98\t\xe0\\\xe3^7qD\x8c\xf5q\x08\xf2\xa2\xc9\xb03mv\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
}
