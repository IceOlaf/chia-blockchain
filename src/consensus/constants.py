NUMBER_OF_HEADS = 3  # The number of tips each full node keeps track of and propagates
DIFFICULTY_STARTING = 60  # These are in units of 2^32
DIFFICULTY_EPOCH = 10  # The number of blocks per epoch
DIFFICULTY_TARGET = 10  # The target number of seconds per block
DIFFICULTY_FACTOR = 4  # The next difficulty is truncated to range [prev / FACTOR, prev * FACTOR]
DIFFICULTY_WARP_FACTOR = 4  # DELAY divides EPOCH in order to warp efficiently.
DIFFICULTY_DELAY = DIFFICULTY_EPOCH // DIFFICULTY_WARP_FACTOR  # The delay in blocks before the difficulty reset applies
DISCRIMINANT_SIZE_BITS = 1024

# The percentage of the difficulty target that the VDF must be run for, at a minimum
MIN_BLOCK_TIME_PERCENT = 20
MIN_VDF_ITERATIONS = 1  # These are in units of 2^32

MAX_FUTURE_TIME = 7200  # The next block can have a timestamp of at most these many seconds more
NUMBER_OF_TIMESTAMPS = 11  # Than the average of the last NUMBEBR_OF_TIMESTAMPS blocks

# Hardcoded genesis block, generated using block tools
GENESIS_BLOCK = b'\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x15N3\xd3\xf9H\xc2K\x96\xfe\xf2f\xa2\xbf\x87\x0e\x0f,\xd0\xd4\x0f6s\xb1".\\\xf5\x8a\xb4\x03\x84\x8e\xf9\xbb\xa1\xca\xdef3:\xe4?\x0c\xe5\xc6\x12\x80\x13\x00\x00\x00\x98\xf9\xeb\x86\x90Kj\x01\x1cZk_\xe1\x9c\x03;Z\xb9V\xe2\xe8\xa5\xc8\n\x0c\xbbU\xa6\xc5\xc5\xbcH\xa3\xb3fd\xcd\xb8\x83\t\xa9\x97\x96\xb5\x91G \xb2\x9e\x05\\\x91\xe1<\xee\xb1\x06\xc3\x18~XuI\xc8\x8a\xb5b\xd7.7\x96Ej\xf3DThs\x18s\xa5\xd4C\x1ea\xfd\xd5\xcf\xb9o\x18\xea6n\xe22*\xb0]%\x15\xd0i\x83\xcb\x9a\xa2.+\x0f1\xcd\x03Z\xf3]\'\xbf|\x8b\xa6\xbcF\x10\xe8Q\x19\xaeZ~\xe5\x1f\xf1)\xa3\xfb\x82\x1a\xb8\x12\xce\x19\xc8\xde\xb9n\x08[\xef\xfd\xf9\x0c\xec\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00/u\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00F\x172\xd9\xb50\x13\xd8\x99\xa7\x88UA)\xec\x0e\xc3//\xb15\n)z\xb6\xf8\x96kTpU\t+Q\xf1\x95\xe8\xd8\x1e\xcd\xe4RrVs\xb8\xee<5^\xf4\xbc\x0bA\x99\xa6\xeb\x95\xf7u\x89G\xd2\xfe\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00$\x01\xf3\x05\x1b&\x8f%m\x15_\x8c\xec\x1f\x038W\xc9\xec\xe5\xf0\xe4Hn\xa6\xe2\x81Yh $?\xb6D\xb1\xa1\xef\x9fP~\x9a\x88\x15s\xb6\xe8\xdd\n\xa5\xb7~\xd7E\xfe\x1c?\xd2@\x87\x97\xf0\'\xf3\x17\x03\x00\x00\x03\x8e\x00\x15\xf0>\x9d\x9ef\x86\x86\xe2\xb4\xe0zt\xee\x86mX+L\xc4\xd7U/\xcc\x12\x8c\x81\x1a(\x17\x05\xcdIc\x066\xe8\xe2\xe1#Z\xb6\xe1\xd4b\xd3\x9b\x17(\x08r\xb0P\x02\xae\xa7>eO\x97-.\xd3X\x00\x00\x9a\xae\x8d\xd5\xcc\xd6\xc5\x80\xcc\xc2}V\xfc\xac\xcdAl\x97\xd0\xc3\x93:\xb6\xeb7t\x17O\xfb$\x01\xea\xa2\x13\xab=bk\x84|\xc4W\xac"\x1f<\x8d\x02@\x94\xa4f~\x89}\xfbsP\xd4\xaaE[\xb1\x00nT\x91\xc2\xd7D\x99f\xb3A\xbc\xdap\xf7\x1b\xd6\x93\xb8\xe8\x81<g\xbaGv"8G.\xfa\xf7\x11\xbc* \xec\xfb\xf3\x9f\x08\xb3\x9b\xc9\x84.G\x98\xff\x93\xba\xb0\xe1\xfd\xa1\x9dz\x99\xba\xb3v\xcc\xad\xfa\xe0\x00\r40\xac.!\x07\xf0\xcaM\x97\xe9\x9c\xb7\x8f\x00m\xed\xfdH\x1e\xb7Q\x89\xf4j\x9a\xc3K$\x01HG$\xbf\x1c\xb6C\x14\xd7\xa9\xa3y\xcc\x92\xa7w\xc9d\xbcQ\x85\xf3\xad\x8a\xd7\x95\xec\x1b\xf6\xe8\x85\xd0\xf1\x00j\x8a\x04\x13\x97\x16W\xb9R\'vQ\x90\xa80\xca\x97C3\xdd\x87\xc6v\xdc\xc7\x0f Zx\x03{\xcb\x06\xce\x88\xb8\x08\xf9\x9e\x1ed!i\xdcG\x1d\x95\x87\x91\xa2\xef\xa2\x9c}\x1c}4\xca\xe7\xa2N|\x9c\xcd\xff\xf2\x07\x90\xc0\x88\xc5Cz\xce\xec\xcc\xd1Q\xa3\xbff\xf7\x8a\x03\xa3\xb4=\x84\xdb[a\xb7\r\xc1\xfb\x89\xd9\xabY\x90\x10+\xd3z\x0b)\x1e\xd7\xdav\xd7\xeb\x84\xa3\xb2X\xf6\xe4\xeeM,\xe6\x02\x8f\r\x13p\xda\x97\x00j\x0e\x805c\xb13\xfb>\x96\x0f\xc1;\x85~\xba\xd5w&7\x17J\xec\xf3\x02\xff\x83\x1aHS\xd9g\xd0\xc1\xcef\xa1\xb6bj\xb1\xc5oR\xf6`\xe7\xe5\x97\xc7\xee\x83\x03\x98\x14\x9f%\x9c\x93\xad\xd8^\x9bx\x00.9T\x1fVo\x98\xb6\xd9\x99x\xc7\x859K\x12\xec\xc3\xe5\xf9\xb5+\xe0\x01\xed\xab\xd6\xcd\x1d[7\xe2\xf5\x11^\xad\xefPl\x8cC7\xd4y\xba\xc1j\x00\x15\x05\xf6K\xac\xfa!\x89\xf0\x88z"t\xc3\x121\x000`s\xaeS\xd0O}\xd9k\xe9\x96jC\xb0,\xfa\x086*Q)\x8f\x1a.\r#h\xb3\xf5T\xc4\xa5l$u\xcd}\xae"\xde\xdbO\xb2{\xdc\x1eQ\x8b\xb5\x9bKp\xa3cO\xf2\xbde\xe91\x16\xdc\x9d\xff\xef\xa6{\x8c\x04\xd1\r\x1d\xc8\xd8\x97\xd0\xee2\xfe\xc0\xfa\x0c\xf5\xb4n\xe6|r\xd8\x88\xee\x8cQ\x9bX\x1f\n\xcf\xb2Yh\x01\'6j\xfd\xe7\x0c\xbc\xb1\xa2dy\t\xf1\xc1\x03 \xcf\xbcX\xfb3H\x9fM2\xa7\x00\x11\x871\xfb\xc1\xd7M]\xfb\xfeo\xb6\xceBt\x9c\xd5\xc7d\xee\xe7\xbf\x0c\x08\x96\xd7S\x056\xf90\xf8\xc4\xf6!\xc1N\xf5\x9e@;\x81\xc6\xca\xe1\xa4*=r\xd0\xd3/U\xc3\x14\x99g\xb5\x96\xa4(\x1ek\xf4\xff\xfb$;\xb7\x134\x19Nmb\xc4\x04\xec\x02\xd0\xc2%\xf5L\xb5N\xc0\n\x8e=R\xdem\xd9%\xa6\xec\x01A\x14-\xdb\xa4Iz.;J\xd4<\xf3\xab\xfd9\x92$\x05\xe9\x1b\xc0\x0b\x13\xcd\xfd[\x9c\xc1\x97\x8f\x00H\xce\x90@s\n\xeb\x90\xd2\xfdtvle\xc2\x19E&K\x8e\xbf\xea\x96\xea6i\xff\x96\x83\xe0\x93\xe3\xa0?\xb5h\xff/\x96\x9f\xdb\xce\xe76\x8df\xe0\x02\xd0\xc9\xfca\xd4\xc2\xd3\xc8\xaf\xe7\xeb<w\xb2_n\xff\xbb\x85\xce\xa8\xa9Q\xe3\xac\x17\xbe\x91\xaf-\xefR\xed(\xbb\x1e\x8fot\xf1\n2pNV\xc6y\x1d9W`\x8b\xad\x9b \x9c\xf6Z\xe75^\x9d\x8f\xf8s\xc1~[)\x97\x89\x19}r\xb5{\xc4\x00\x81\xday\x01~[u\x1f\x81\x7f\x0c)\x05\xe6\xfd\xe5\xd14\\a\n\xc6I\xccJ\x0cXk\xcf,Z\x1c\xdb>\xe0\xc3\xbd;\x13\xc7Lf\x0c"\x1aC?qX\xc3\xd1jY\tZ\x01\x13\x81R\xcb\n\xd3\tv\x8a\x10\xba\xa6\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00<\x00\x00\x00\x00\x00\x00/u\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00]\x89\x94\xda\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~[u\x1f\x81\x7f\x0c)\x05\xe6\xfd\xe5\xd14\\a\n\xc6I\xccJ\x0cXk\xcf,Z\x1c\xdb>\xe0\xc3z!\xc9N\xd5\x03\x8b^\xd9\xe6\xc7I\xba\xb1\x0fm\xd4\xa0=\xb6^s\x94_f\xb5\xc1\\n\xfe\xf9\xd2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00H1V\xdeN\xcc\x8a;\x1a\x8b\xe6v\x9d\x82U\xfc?\xba2K\xdfiE\xfd\x16\xe6t\x90\x86\x14;\x1aT>\xed>u\xe8P\x87\xdf7i|/\xbf\x9a3\x10\x8e\xe0\xa9p\xc3\xdcd\x86\'A\x17:6\xc2\xdc\xe1\xc7b\x9f\xe0\xbe\xd1\xfb\x8eG\xfe?\xde\xee]\xee\x1f711L\t\x0b\xbcG+\xa8b\x0e\\O\xe5\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\xd3tK\xda`\xb5u\xca\x8c\xa2\xf7n\x1d\xd5\x92l\xb13k\xdb\n+\xbe/\x1e\xc0\xfe\xbf\xd9\x83\x88V\x11]~.<\x14\x0f\xce`\x8b\xbf\xb9\xa7\xce"6\x19\xa5\x19|\x81!r\x15V\xa6\x82\x07\x96w\x98F\xce\xb2(G\xcfm\x17@t\xb2\x1b\xba\xcf4I}\x0b\xc4\n\xd4\x9b\xe2E\x9e\x84\x98mY||\xa8[+\x93\xa0\x02\xe4\xc2\x1d\xaa5R\xe5,\xbd\xa5\x15|%}\xa4@\xe5\x11\x00\x80\x1fG\x8aH\x0b\xe7\xe9\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'  # noqa: E501
