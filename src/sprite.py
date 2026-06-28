from __future__ import annotations


class Sprite:
    def __init__(self, width, height, frame_count, frames):
        self.width = width
        self.height = height
        self.frame_count = frame_count
        self.frames = frames


def _b(hex_string):
    return bytes.fromhex(hex_string)


# Built-in sprite IDs are stable: 0..127 are SD-card sprites, 128..255 are per-card sprites.
# Frames are packed as 1-bit row-major data, top-to-bottom, left-to-right, padded to whole bytes per row.

# 000
HEART8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("66ffffff7e3c1800"),
        _b("247effff7e3c1800"),
    ],
)

# 001
HEART5 = Sprite(
    width=5,
    height=5,
    frame_count=3,
    frames=[
        _b("50f8f87020"),
        _b("0050f87020"),
        _b("50f8f87020"),
    ],
)

# 002
HEART12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("39c07fe0fff0fff07fe03fc01f800f000600000000000000"),
        _b("000030c07fe0fff0fff07fe03fc01f800f00060000000000"),
        _b("39c07fe0fff0fff07fe03fc01f800f000600000020400000"),
    ],
)

# 003
HEART16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("00001c383e7c7ffeffffffffffff7ffe3ffc1ff80ff007e003c0018000000000"),
        _b("0000000018183c3c7e7e7ffe7ffe3ffc1ff80ff007e003c00180000000000000"),
        _b("00001c383e7c7ffeffffffffffff7ffe3ffc1ff80ff007e003c001800004000a"),

    ],
)

# 004
BROKEN_HEART8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("66ffefdeec683010"),
        _b("66ffdfee74341808"),
        _b("cceedeec68301000"),

    ],
)

# 005
DOUBLE_HEART8 = Sprite(
    width=10,
    height=8,
    frame_count=3,
    frames=[
        _b("028007c057c0fb80f900700020000000"),
        _b("028057c0ffc0fb807100200000000000"),
        _b("0000028057c0ffc0fb80710020000000"),
    ],
)

# 006
HEART_ARROW12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00603ba07fc0ffe0ffe07fc03f805f00ce008400c0000000"),
        _b("00201b603f807fc07fc03f801f004e00c4008000c0000000"),
        _b("00603ba07fc0ffe0ffe07fc03f805f00ce008400c0400050"),

    ],
)

# 007
HEART_LOCK12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("39c07fe0fff0fff07fe03fc01f800f800e800f8000000000"),
        _b("39c07fe0fff0fff07fe03fc01f800f800e8008800f800000"),
    ],
)

# 008
HEART_KEY12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("39c07fe0fff0fff07fe03fc01f801f00262027f018200000"),
        _b("39c07fe0fff0fff07fe03fc01f800f00162013f00c200000"),
    ],
)

# 009
KISS8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("006cfe7c38100000"),
        _b("00006cfe7c381000"),
        _b("016efe7c38100000"),
    ],
)

# 010
RING12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("04000e0015000e0004001f0020804040404020801f000000"),
        _b("24000e0015000e0004001f0020804040404020801f000000"),
        _b("04000e0015000e0004000e0011002080208011000e000000"),

    ],
)

# 011
ROSE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("06000f001f801f800f00060032000e600380020002000200"),
        _b("000006000f001f801f800f0006203ac00700020002000200"),
    ],
)

# 012
FLOWER8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("2070a87020205020"),
        _b("5020f82050202050"),
        _b("2070a87020205020"),

    ],
)

# 013
DAISY8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("284438ee38442810"),
        _b("4428ee38ee284410"),

    ],
)

# 014
SPARKLE4 = Sprite(
    width=4,
    height=4,
    frame_count=2,
    frames=[
        _b("40e04000"),
        _b("a040a000"),
    ],
)

# 015
SPARKLE8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("000000081c080000"),
        _b("0000001408140000"),
        _b("000000081c080000"),
    ],
)

# 016
STAR5 = Sprite(
    width=5,
    height=5,
    frame_count=3,
    frames=[
        _b("007070f820"),
        _b("807070f828"),
        _b("007070f820"),
    ],
)

# 017
STAR8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("0008087f3e3e3e41"),
        _b("8008087f3e3e3e41"),
        _b("0108087f3e3e3ec1"),
    ],
)

# 018
STAR12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("000002000200020007007ff01fc00f800f800d8018c01040"),
        _b("82000200020007000700fff03fe00f800f800d8018c018d0"),
        _b("001002000200020007007ff01fc00f800f800d8018c09040"),
    ],
)

# 019
MOON12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("000024000c0018003800380038003c001c000e0007200000"),
        _b("0000220006000c001c001c001c001e000e00070003a00000"),
        _b("000024000c0018003800380038003c001c000e0007200000"),
    ],
)

# 020
SUN12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("02000200222012000f000f80ff900f800f00100020200200"),
        _b("020000002020004007800f808ff00f800780024022200200"),
        _b("02000200222012000f000f80ff900f800f00100020200200"),
    ],
)

# 021
CLOUD12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000000000006000f003fe07ff07ff07ff03fe03fe00000"),
        _b("000000000000000006000f003fe07ff07ff07ff03fe03fe0"),
        _b("00000000000006000f003fe07ff07ff07ff03fe03fe00000"),
    ],
)

# 022
RAIN_CLOUD12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000e003f807fc0ffe0ffe07fc03f802480124024800000"),
        _b("00000e003f807fc0ffe0ffe07fc03f801240248012400000"),
        _b("00000e003f807fc0ffe0ffe07fc03f802480124024800000"),

    ],
)

# 023
SNOWFLAKE8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("105438fe38541000"),
        _b("925438fe38549200"),
    ],
)

# 024
SMILEY8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a58181a35e3c"),
        _b("3c42a58181a35e3c"),
        _b("3c4281b781a35e3c"),
    ],
)

# 025
WINK8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a78181a35e3c"),
        _b("3c42a78181a35e3c"),
        _b("3c42a7b781a35e3c"),
    ],
)

# 026
LAUGH8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a581bda57e3c"),
        _b("3c42a581bda57e3c"),
        _b("3c4281b7bda57e3c"),
    ],
)

# 027
BLUSH8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a581c3a35e3c"),
        _b("3c42a581c3a35e3c"),
        _b("3c4281b7c3a35e3c"),
    ],
)

# 028
SAD8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a581819d623c"),
        _b("3c42a581819d623c"),
        _b("3c4281b7819d623c"),
    ],
)

# 029
SURPRISE8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42a5819999423c"),
        _b("3c42a5819999423c"),
        _b("3c4281b79999423c"),
    ],
)

# 030
SLEEPY8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3e42b781819d423c"),
        _b("3d42b781819d423c"),
        _b("3e42b7b7819d423c"),
    ],
)

# 031
COOL8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("3c42f7ff81bd423c"),
        _b("3c42f7ff81817e3c"),
        _b("3c42f7ff81bd423c"),
    ],
)

# 032
CAT12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("108019802f403fc0204029407af0204010800f0010802040"),
        _b("108019802f403fc0204029407af0204010800f0010802040"),
        _b("0000108019802f403fc0204029407af0204010800f0030c0"),
    ],
)

# 033
DOG12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000000f0050a0e070e9706060224017800f0020404020"),
        _b("0000000000000f0050a0e070e9706060224017800f006060"),
    ],
)

# 034
BUNNY12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("088015401540154017400880104015401240088027200000"),
        _b("000008801540154015401740088010401540124008802720"),
        _b("088015401540154017400880104015401240088027200000"),
    ],
)

# 035
BIRD12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("0000000040002000200016000fc07ff01fe00f0007000500"),
        _b("000000000000000006007fc07ff01fe00f00070005000500"),
        _b("0000000040002000200016000fc07ff01fe00f0007000500"),
    ],
)

# 036
FISH12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("0000000000201e60216050a040a02f601e60002000000000"),
        _b("0000000000100f3010b02850205017b00f30001000000000"),
        _b("00000000000007900850142010200bd00790000000000000"),
    ],
)

# 037
WHALE16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("0000000000000000000007e10ff33ffd7ffd7fff7ffb3ff107e0000000000000"),
        _b("00000100038001000100010007e10ff33ffd7ffd7fff7ffb3ff107e000000000"),
        _b("0000000000000000000007e10ff33ffd7ffd7fff7ffb3ff107e0000000000000"),
    ],
)

# 038
BUTTERFLY12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("088038e04d10871087104b103ae0472047204720472038c0"),
        _b("0880088035e04b108710bfd04f3077e0472047203ac00000"),
    ],
)

# 039
BEE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000900168016800f009a806a401a800f00000000000000"),
        _b("000004800b400b4007804d4035200d400780000000000000"),
    ],
)

# 040
TURTLE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000000000000000f001fa02f702f601f801f8021002100"),
        _b("000000000000000007800fd017b017b00fc00fc010801080"),
    ],
)

# 041
FROG12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000000108039c02f401080204020402f4010804f200000"),
        _b("000000000000108039c02f401080204020402f4010804f20"),
        _b("00000000108039c02f401080204020402f4010804f200000"),
    ],
)

# 042
DINOSAUR16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("000000f003f006f007f007e01ff83fc07fc0ffe07fc03f201840306000000000"),
        _b("000000f003f006f007f007e01ff83fc07fc0ffe07fc03f2018300c4000000000"),

    ],
)

# 043
GHOST12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000f001080204029403fc03fc03fc03fc03fc03fc01240"),
        _b("000000000f001080204029403fc03fc03fc03fc03fc03fc0"),
        _b("00000f001080204029403fc03fc03fc03fc03fc03fc01240"),
    ],
)

# 044
ROBOT12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0400040004003fc0204029406060a050af5020403fc00000"),
        _b("0400040004003fc0204039c079e0a050af5020403fc00000"),
    ],
)

# 045
ALIEN12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("60601f801080108020402940204020401f8010800f000000"),
        _b("60601f801080108020403fc0204020401f8010800f008010"),
    ],
)

# 046
MONSTER12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0000108018c03fc03fc036c03fc03fc030c03fc03fc00000"),
        _b("0000108018c03fc03fc036c03fc03fc030c030c03fc00000"),
    ],
)

# 047
OCTOPUS12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000006000f001f801f801f800f002ea02aa0111011101110"),
        _b("0000000006000f001f801f801f800f002ea02aa044404440"),
    ],
)

# 048
PENGUIN12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000f001f8036c03fc030c030c030c01f80108030c00000"),
        _b("00000f001f8036c03fc030c030c030c01f80090019800000"),

    ],
)

# 049
DUCK12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000f001f801b801fb03fe07f80ff007e00240000000000"),
        _b("000007000f800d800fb01fe03fc07f003e00120000000000"),

    ],
)

# 050
DRAGON16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("000000000100010002fc82fce4fc5ffc5ffc3ff03ff01ff01ff0049004900490"),
        _b("0000000000800080017e417e727e2ffe2ffe1ff81ff80ff80ff8024802480248"),
        _b("000000000100010002fd82fde4fe5ffc5ffc3ff03ff01ff01ff0049004900490"),
    ],
)

# 051
OWL12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("10801f8034c03fc029403fc029402740128010800f000000"),
        _b("000010801f8034c03fc029403fc029402740128010800f00"),
    ],
)

# 052
FOX12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0880154015402220202024a02020114017c010403fe0c010"),
        _b("00000880154015402220202024a02020114017c01040fff0"),
    ],
)

# 053
BEAR12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000030c07fe07fe03fc03fc03fc03fc01f801f800f000000"),
        _b("0000000030c07fe07fe03fc03fc03fc03fc01f801f800f00"),
    ],
)

# 054
MOUSE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000000306078f07ff038e01240184008c0072000100000"),
        _b("0000000018303c703ff01c7009200c200460039000100000"),
    ],
)

# 055
SNAIL12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000000000000000000c1012502d602df013f00df00000"),
        _b("000000000000000000000610095016d016f009f006f00000"),
    ],
)

# 056
GIFT12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0000000020402d407fe042207fe04220422042207fe00000"),
        _b("00000000462029407fe042207fe04220422042207fe00000"),
    ],
)

# 057
CAKE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("04000e0004000e000a003f807fc055407fc07fc0ffe00000"),
        _b("08001c0004000e000a003f807fc055407fc07fc0ffe00000"),

    ],
)

# 058
CANDLE8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("001c081c1414141c"),
        _b("081c081c1414141c"),
    ],
)

# 059
BALLOON8 = Sprite(
    width=8,
    height=9,
    frame_count=2,
    frames=[
        _b("182442422418101c08"),
        _b("001824424224181c08"),
    ],
)

# 060
CONFETTI12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("080040802000002000102000020000000010401028000040"),
        _b("004008204080004000200000200002000100001040000800"),
        _b("080004400800448000000020000020001200000000104000"),
    ],
)

# 061
FIREWORK12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000000000000000a8007000f8007000a80000000000000"),
        _b("00000020000012400a8007001fc007000a80124040000000"),
        _b("00000000222012400a8007003fe007000a80124022200000"),
    ],
)

# 062
MUSIC_NOTE8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("000c0b0909193f17"),
        _b("00060504040c1f0b"),
    ],
)

# 063
MUSIC_PAIR12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00001c001380108010801080108010803080718023800100"),
        _b("00000e0009c008400840084008400840184038c011c00080"),
        _b("00101c201380108010801080108010803080718023800100"),
    ],
)

# 064
BELL8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("183c7e7e7eff183c"),
        _b("0c1e3f3f3f7f0c1e"),

    ],
)

# 065
CLOCK12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("00000f00108022404220422043e04020204010800f000000"),
        _b("00000f0010802240422042204220412020c010800f000000"),
        _b("00000f00108022404220422042204220224012800f000000"),
        _b("00000f00108022404220422042204c20304010800f000000"),
    ],
)

# 066
HOURGLASS8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("7e4224181824427e"),
        _b("7e7e3c1818247e7e"),
        _b("7e422418183c7e7e"),

    ],
)


# 067
BATTERY12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("000000000000ffe0e020e030e030e020ffe0000000000000"),
        _b("000000000000ffe0f820f830f830f820ffe0000000000000"),
        _b("000000000000ffe0fe20fe30fe30fe20ffe0000000000000"),
        _b("000000000000ffe0ffa0ffb0ffb0ffa0ffe0000000000000"),
    ],
)

# 068
BATTERY_CHARGE12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("000000000200ffe0e420e830ef30e220ffe0040004000000"),
        _b("000000000200ffe0fc20f830ff30fa20ffe0040004000000"),
        _b("000000000200ffe0fe20fe30ff30fe20ffe0040004000000"),
        _b("000000000200ffe0ffa0ffb0ffb0ffa0ffe0040004000000"),
    ],
)

# 069
WIFI12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00000000000000000000000000000000070008800a800000"),
        _b("000000000000000000000000070018c0174028a02aa00000"),
        _b("00000000000000000f801040272058d09740a8a0aaa00000"),
    ],
)

# 070
SIGNAL12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("000000000000000000000000000000000000000060006920"),
        _b("000000000000000000000000000000000c000c006c006d20"),
        _b("000000000000000000000000018001800d800d806d806da0"),
        _b("00000000000000000030003001b001b00db00db06db06db0"),
    ],
)

# 071
NFC12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00003c004400548044404440548044003c00000000000000"),
        _b("00003c004480544044204420544044803c00000000000000"),
        _b("00003c404440542044104410542044403c40000000000000"),

    ],
)

# 072
CHECK8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("0001020444281000"),
        _b("0000010204442810"),
    ],
)

# 073
X8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("0042241818244200"),
        _b("0000422418182442"),
    ],
)

# 074
ALERT8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("08081414363e7f7f"),
        _b("ff899595b7bfffff"),
    ],
)

# 075
INFO8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("3c42898199894a3c"),
        _b("3c42858199894a3c"),
    ],
)

# 076
LOCK8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("003c247e4252427e"),
        _b("003c247e424a427e"),
    ],
)

# 077
UNLOCK8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("0619207e4252427e"),
        _b("0619217e424a427e"),
    ],
)

# 078
KEY12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0000000000000000700088408ff088207000000000000000"),
        _b("00000000000000003800444047f044203800000000000000"),
    ],
)

# 079
GEAR12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("00000200222017000a8016407f5016400880170020200200"),
        _b("00000200202007400880134057f013400a80074022200200"),
        _b("00000200222017000a8016407f5016400880170020200200"),
        _b("00000200202007400880134057f013400a80074022200200"),
    ],
)

# 080
WRENCH12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000060009000d000e00100020004000800700070007000"),
        _b("000000300040006000700080010002000400380038003800"),
    ],
)

# 081
MAGNIFIER12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("00001c00220041004100410022001d000080004000200010"),
        _b("00000e00110020802080208011000e800040004000200010"),
        _b("00001c00220041004900410022001d000080004000200010"),
    ],
)

# 082
MAIL12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0000000000007fe0606058a045205aa060607fe000000000"),
        _b("0000000000407fe0606058a045205aa060607fe000000000"),
    ],
)

# 083
ENVELOPE_HEART12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("0000000000007fe06a605fa05f205ea064607fe000000000"),
        _b("0000000000007fe060605aa05f205ea064607fe000000000"),
        _b("0000000000007fe06a605fa05f205ea064607fe000000000"),
    ],
)

# 084
BOOK12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00007fe0462046204620462046204620462046207fe00000"),
        _b("00007fe046207fe04620462046204620462046207fe00000"),
    ],
)

# 085
CAMERA12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000001e007fe0476048a048a048a047207fe000000000"),
        _b("000000001e007fe047e049e048a048a047207fe000000000"),
    ],
)

# 086
GAMEPAD16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("000007e0181820044e528a029f2a8a024e042004181807e00000000000000000"),
        _b("000007e0181820044e228a0a9f228a0a4e042004181807e00000000000000000"),

    ],
)

# 087
DICE8 = Sprite(
    width=8,
    height=8,
    frame_count=4,
    frames=[
        # 1
        _b("ff818181899181ff"),

        # 2
        _b("ff819181818981ff"),

        # 3
        _b("ff819189818981ff"),

        # 4
        _b("ff819191919181ff"),
    ],
)

# 088
COIN8 = Sprite(
    width=8,
    height=8,
    frame_count=4,
    frames=[
        _b("00182c4a4a2c1800"),
        _b("0018181818181800"),
        _b("00182c4a4a2c1800"),
        _b("0018181818181800"),
    ],
)

# 089
GEM8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("081c2a7f2a2c1c08"),
        _b("0a1f2a7f2a2c1c08"),
    ],
)

# 090
CROWN12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000000100219032902a502c60442040207fe000000000"),
        _b("001080000100219032902a502c60442040207fe000000000"),
    ],
)

# 091
TROPHY12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00001f8070e050a050a070e01f800600060006001f800000"),
        _b("00001f8070e056a050a070e01f800600060006001f800000"),
    ],
)

# 092
MEDAL12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("108009000900060006000900168010800900060000000000"),
        _b("108009000900060006000900168010800d00060000000000"),
    ],
)

# 093
SHIELD12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000006001b802260222022201240124012400a8007000200"),
        _b("000006001b80226022202fa01240124012400a8007000200"),
    ],
)

# 094
MAGIC_WAND12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("0000004000e0004000800100020004000800700070007000"),
        _b("000000a0004000e000800100020004000800700070007000"),
        _b("0100004000e0004000800110020004000800700070007000"),
    ],
)

# 095
CURSOR8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("006058464f546a44"),
        _b("00302c23272a3522"),
    ],
)

# 096
COFFEE8 = Sprite(
    width=8,
    height=9,
    frame_count=2,
    frames=[
        _b("2a2a2a7e4342437e3f"),
        _b("0000007e4342437e3f"),
    ],
)

# 097
TEA8 = Sprite(
    width=8,
    height=9,
    frame_count=2,
    frames=[
        _b("000102027e43427f7f"),
        _b("001112127e43427f7f"),
    ],
)

# 098
PIZZA12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000030002c002380166016c010c0130011000a000c000800"),
        _b("000030002c002380146010c01080130013000e000c000800"),
    ],
)

# 099
ICECREAM8 = Sprite(
    width=8,
    height=9,
    frame_count=2,
    frames=[
        _b("1c3e3e3e1c3e141408"),
        _b("1c3a3e2e1c3e141408"),
    ],
)

# 100
APPLE8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("060408247e7e3c18"),
        _b("040608247e7e3c18"),
    ],
)

# 101
DONUT8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("0018245a5a241800"),
        _b("8018245a5a241801"),
    ],
)

# 102
TOAST8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("1824427e6e5a427e"),
        _b("1824427e665e427e"),
    ],
)

# 103
FIRE8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("081c1c3677223614"),
        _b("00081c1c36772236"),
    ],
)

# 104
WATER_DROP8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("081c1c3e7f3e1c08"),
        _b("00081c1c3e7f1c08"),
    ],
)

# 105
LIGHTNING8 = Sprite(
    width=8,
    height=8,
    frame_count=3,
    frames=[
        _b("0818183f7e0c1810"),
        _b("040c0c1f3f060c08"),
        _b("0898183f7e0c1910"),
    ],
)

# 106
RAINBOW12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000000f001f8036c059a070e030c01080000000000000"),
        _b("000000000f001f8036c059a070e030c01080000040200000"),
    ],
)

# 107
WAVE12 = Sprite(
    width=12,
    height=12,
    frame_count=3,
    frames=[
        _b("000000000000004000000000606098900500050022000000"),
        _b("000000000000004000002020505050508980060020000000"),
        _b("000000000000004000000000606098900500050022000000"),
    ],
)

# 108
MOUNTAIN16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000000000002000300050005c8099808541064106220a220917fff00000000"),
        _b("00000000200002040300050005c8099808541064106220a220917fff00000000"),
    ],
)

# 109
TREE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("0200070007000f801fc01fc03fe01fc03fe07ff007000700"),
        _b("00000200070007000f801fc01fc03fe01fc03fe07ff00700"),
    ],
)

# 110
MUSHROOM8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("3c7effdbff3c3c7e"),
        _b("3c7effe7ff3c3c7e"),

    ],
)

# 111
LEAF8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("001d224d51225c80"),
        _b("000e112628112e40"),
    ],
)

# 112
HOUSE12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("00000200050018c020207ff020202720252025203fe00000"),
        _b("00000200050018c020207ff020202760256025203fe00000"),
    ],
)

# 113
CITY16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000000000003c003c003c07bc05ac07bde7bde5ad27bde7bde5ad27bde7bde"),
        _b("00000000000003c003c003c07bc05b447bde7bde5b567bde7bde5b567bde7bde"),
    ],
)

# 114
TENT12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("000000000200070007000a800a4012c0232023207ff00000"),
        _b("000000000200070007000a800a401a40262026207ff00000"),
    ],
)

# 115
MAP_PIN8 = Sprite(
    width=8,
    height=8,
    frame_count=2,
    frames=[
        _b("387c6c7c38381010"),
        _b("00387c6c7c383810"),

    ],
)

# 116
COMPASS12 = Sprite(
    width=12,
    height=12,
    frame_count=4,
    frames=[
        _b("00000f0012802240472047204f2043a020c010800f000000"),
        _b("00000f0010802040422043a047e04720284010800f000000"),
        _b("00000f001080204048204e2047a04720274012800f000000"),
        _b("00000f001080204040a047207f204e20224010800f000000"),
    ],
)

# 117
FOOTSTEP12 = Sprite(
    width=12,
    height=12,
    frame_count=2,
    frames=[
        _b("10004400180024002440251024c0192001200120012000c0"),
        _b("080022000c0012001280122013800e400240024002400180"),
    ],
)

# 118
ROCKET16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("0000008001400140022002a0055004900410041004100c1817f41c1c30060000"),
        _b("00000000008001400140022002a0055004900410041004100c1817f43c1e0000"),
        _b("0000008001400140022002a0055004900410041004100c1817f41ddc30860080"),
    ],
)

# 119
CAR16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("000000000000000003e0041004103ffc2004200424143ffc0410000000000000"),
        _b("000000000000000001f0020802081ffe10021002120a1ffe0208000000000000"),
    ],
)

# 120
TRAIN16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000000000000003ff83dc83dc83dc8200c200a3ffc0a5a0424000000000000"),
        _b("00000000000000001ffc1ee41ee41ee4100610061ffe052d0212000000000000"),
    ],
)

# 121
BOAT16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000000010001800360051005f809001f0001003ffc1008081007e000000000"),
        _b("00000000010001800360051005f809001f00010000003ffc1008081007e00000"),
    ],
)

# 122
PLANE16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000800040007000286027803c01f4060e00030000800000000000000000000"),
        _b("00000400020003800143013c01e00fa030700018000400000000000000000000"),
    ],
)

# 123
BICYCLE16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("0000000000000000010001380100038005403cbc4cba5ffa4422381c00000000"),
        _b("0000000000000000010001380100038005403cbc5cb25ffe4422381c00000000"),
    ],
)

# 124
PLANET16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("00000000000001c006300413083e09f81fc86e10363001c00000000000000000"),
        _b("00000000000001c006300410080f0ffe7fe83c10063001c00000000000000000"),
    ],
)

# 125
UFO16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("000000000180024007e0099010087ffe0fe80000000000000000000000000000"),
        _b("0000000000000180024007e0099010087ffe0fe8000000000000000000000000"),
        _b("000000000180024007e0099010087ffe0fe80240042004200810081000000000"),
    ],
)

# 126
SATELLITE16 = Sprite(
    width=16,
    height=16,
    frame_count=2,
    frames=[
        _b("0000f0009000b000f000080007c00240024003e00010000f000d0009000f0000"),
        _b("0001f0029004b008f010082007c00240024003e00010000f000d0009000f0000"),
    ],
)

# 127
COMET16 = Sprite(
    width=16,
    height=16,
    frame_count=3,
    frames=[
        _b("000060001800061c01be007efffe003c00c003000c0030000000000000000000"),
        _b("0000400030001c00023801fcf87c07fc04f803000c0030000000000000000000"),
        _b("00004000200010000c000270e1f81ef801f801f00e0030000000000000000000"),
    ],
)


SPRITE_NAMES = {
    0: "HEART8",
    1: "HEART5",
    2: "HEART12",
    3: "HEART16",
    4: "BROKEN_HEART8",
    5: "DOUBLE_HEART8",
    6: "HEART_ARROW12",
    7: "HEART_LOCK12",
    8: "HEART_KEY12",
    9: "KISS8",
    10: "RING12",
    11: "ROSE12",
    12: "FLOWER8",
    13: "DAISY8",
    14: "SPARKLE4",
    15: "SPARKLE8",
    16: "STAR5",
    17: "STAR8",
    18: "STAR12",
    19: "MOON12",
    20: "SUN12",
    21: "CLOUD12",
    22: "RAIN_CLOUD12",
    23: "SNOWFLAKE8",
    24: "SMILEY8",
    25: "WINK8",
    26: "LAUGH8",
    27: "BLUSH8",
    28: "SAD8",
    29: "SURPRISE8",
    30: "SLEEPY8",
    31: "COOL8",
    32: "CAT12",
    33: "DOG12",
    34: "BUNNY12",
    35: "BIRD12",
    36: "FISH12",
    37: "WHALE16",
    38: "BUTTERFLY12",
    39: "BEE12",
    40: "TURTLE12",
    41: "FROG12",
    42: "DINOSAUR16",
    43: "GHOST12",
    44: "ROBOT12",
    45: "ALIEN12",
    46: "MONSTER12",
    47: "OCTOPUS12",
    48: "PENGUIN12",
    49: "DUCK12",
    50: "DRAGON16",
    51: "OWL12",
    52: "FOX12",
    53: "BEAR12",
    54: "MOUSE12",
    55: "SNAIL12",
    56: "GIFT12",
    57: "CAKE12",
    58: "CANDLE8",
    59: "BALLOON8",
    60: "CONFETTI12",
    61: "FIREWORK12",
    62: "MUSIC_NOTE8",
    63: "MUSIC_PAIR12",
    64: "BELL8",
    65: "CLOCK12",
    66: "HOURGLASS8",
    67: "BATTERY12",
    68: "BATTERY_CHARGE12",
    69: "WIFI12",
    70: "SIGNAL12",
    71: "NFC12",
    72: "CHECK8",
    73: "X8",
    74: "ALERT8",
    75: "INFO8",
    76: "LOCK8",
    77: "UNLOCK8",
    78: "KEY12",
    79: "GEAR12",
    80: "WRENCH12",
    81: "MAGNIFIER12",
    82: "MAIL12",
    83: "ENVELOPE_HEART12",
    84: "BOOK12",
    85: "CAMERA12",
    86: "GAMEPAD16",
    87: "DICE8",
    88: "COIN8",
    89: "GEM8",
    90: "CROWN12",
    91: "TROPHY12",
    92: "MEDAL12",
    93: "SHIELD12",
    94: "MAGIC_WAND12",
    95: "CURSOR8",
    96: "COFFEE8",
    97: "TEA8",
    98: "PIZZA12",
    99: "ICECREAM8",
    100: "APPLE8",
    101: "DONUT8",
    102: "TOAST8",
    103: "FIRE8",
    104: "WATER_DROP8",
    105: "LIGHTNING8",
    106: "RAINBOW12",
    107: "WAVE12",
    108: "MOUNTAIN16",
    109: "TREE12",
    110: "MUSHROOM8",
    111: "LEAF8",
    112: "HOUSE12",
    113: "CITY16",
    114: "TENT12",
    115: "MAP_PIN8",
    116: "COMPASS12",
    117: "FOOTSTEP12",
    118: "ROCKET16",
    119: "CAR16",
    120: "TRAIN16",
    121: "BOAT16",
    122: "PLANE16",
    123: "BICYCLE16",
    124: "PLANET16",
    125: "UFO16",
    126: "SATELLITE16",
    127: "COMET16",
}

BUILTIN_SPRITES = [globals()[SPRITE_NAMES[index]] for index in range(len(SPRITE_NAMES))]

SPRITE_IDS = {name: index for index, name in SPRITE_NAMES.items()}

# Friendly aliases for the names most likely to be typed by hand in .pxla files.
SPRITE_IDS.update({
    "HEART": SPRITE_IDS["HEART8"],
    "BROKEN_HEART": SPRITE_IDS["BROKEN_HEART8"],
    "DOUBLE_HEART": SPRITE_IDS["DOUBLE_HEART8"],
    "SPARKLE": SPRITE_IDS["SPARKLE8"],
    "STAR": SPRITE_IDS["STAR8"],
    "SMILEY": SPRITE_IDS["SMILEY8"],
    "WINK": SPRITE_IDS["WINK8"],
    "KISS": SPRITE_IDS["KISS8"],
    "CHECK": SPRITE_IDS["CHECK8"],
    "X": SPRITE_IDS["X8"],
    "LOCK": SPRITE_IDS["LOCK8"],
    "UNLOCK": SPRITE_IDS["UNLOCK8"],
    "COIN": SPRITE_IDS["COIN8"],
    "GEM": SPRITE_IDS["GEM8"],
    "CURSOR": SPRITE_IDS["CURSOR8"],
})