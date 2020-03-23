from fastvdf import verify
import time

challenge_hash = bytes.fromhex('a4bb1461ade74ac602e9ae511af68bb254dfe65d61b7faf9fab82d0b4364a30b')
a = "2120439809548002603699476515242856052401016261690016272875375071691961393091525387070479560771020084644071207726495978942882631782725802522199105524842492"
b = "-1447745607279856836390430406078195096118390105960950865534703611396791372115445411292284152604500691817421284831093402993306669441174757567119801738100995"
num_iterations = 5728275
witness = bytes([
         0, 66, 83, 222, 194, 35, 255, 62, 48, 148, 1, 100, 235, 199, 156, 156,
         24, 228, 16, 253, 25, 189, 42, 83, 211, 151, 30, 214, 205, 234, 176,
         143, 103, 11, 236, 108, 48, 90, 73, 253, 252, 123, 98, 49, 100, 211,
         134, 126, 122, 253, 197, 214, 156, 104, 29, 235, 77, 255, 37, 110, 150,
         132, 26, 76, 14, 255, 190, 212, 244, 102, 121, 29, 91, 97, 152, 214,
         228, 231, 118, 31, 184, 33, 250, 213, 245, 240, 182, 126, 20, 92, 240,
         178, 227, 83, 39, 7, 84, 122, 138, 82, 188, 99, 80, 63, 141, 215, 155,
         45, 140, 155, 191, 236, 204, 62, 110, 69, 240, 196, 139, 117, 240, 69,
         153, 205, 15, 11, 78, 73, 66, 113, 0, 0, 0, 0, 0, 19, 108, 68, 0, 18,
         56, 13, 141, 27, 60, 129, 110, 67, 132, 125, 163, 147, 28, 132, 246, 13,
         5, 246, 1, 214, 193, 6, 6, 83, 5, 31, 41, 40, 23, 100, 134, 110, 234,
         191, 175, 164, 89, 152, 158, 210, 170, 191, 181, 231, 141, 115, 187,
         188, 117, 13, 16, 118, 57, 14, 200, 9, 38, 155, 56, 207, 29, 199, 184,
         255, 242, 183, 152, 131, 47, 139, 66, 200, 145, 3, 230, 113, 118, 112,
         96, 31, 147, 55, 96, 0, 139, 108, 111, 245, 44, 88, 171, 220, 228, 40,
         255, 245, 85, 110, 163, 132, 156, 190, 217, 61, 224, 83, 141, 162, 183,
         185, 176, 34, 220, 62, 140, 161, 193, 130, 254, 192, 33, 171, 38, 190,
         151, 23, 62, 45, 0, 26, 202, 156, 87, 237, 11, 119, 153, 67, 48, 84,
         126, 74, 210, 174, 20, 26, 114, 242, 211, 158, 56, 88, 206, 124, 247,
         157, 227, 206, 218, 111, 157, 21, 109, 45, 216, 194, 12, 192, 72, 81,
         141, 99, 120, 135, 212, 244, 37, 97, 53, 59, 205, 178, 153, 244, 36,
         173, 68, 79, 191, 22, 150, 104, 243, 0, 6, 67, 238, 203, 215, 17, 96,
         97, 51, 19, 126, 9, 150, 201, 139, 128, 132, 38, 119, 124, 215, 139,
         217, 4, 125, 75, 52, 216, 180, 80, 26, 47, 153, 151, 98, 153, 35, 16,
         158, 184, 185, 84, 136, 248, 61, 227, 105, 149, 46, 157, 207, 36, 132,
         128, 10, 103, 246, 199, 197, 156, 10, 197, 193, 163, 0, 0, 0, 0, 0, 58,
         69, 48, 0, 101, 133, 189, 101, 125, 9, 91, 174, 190, 12, 26, 159, 234,
         224, 17, 36, 112, 170, 14, 206, 164, 160, 20, 140, 144, 250, 67, 81,
         231, 68, 65, 172, 145, 188, 239, 49, 78, 48, 178, 167, 87, 102, 14, 21,
         183, 126, 141, 86, 143, 75, 163, 175, 202, 96, 7, 177, 176, 112, 239,
         41, 178, 222, 118, 225, 255, 219, 166, 43, 222, 69, 28, 31, 16, 187,
         213, 112, 113, 190, 240, 227, 141, 175, 195, 218, 52, 95, 236, 58, 122,
         173, 23, 142, 171, 222, 33, 155, 232, 18, 247, 119, 139, 51, 218, 202,
         37, 181, 50, 60, 78, 214, 164, 89, 244, 30, 190, 11, 115, 56, 153, 170,
         154, 239, 139, 143, 50, 100, 239, 85, 141, 0, 33, 14, 241, 123, 70, 18,
         20, 190, 103, 31, 183, 124, 146, 5, 254, 69, 120, 191, 173, 56, 219,
         126, 111, 177, 223, 13, 181, 75, 155, 121, 84, 163, 110, 185, 145, 245,
         8, 191, 32, 241, 228, 98, 162, 77, 4, 139, 199, 24, 135, 4, 75, 165, 9,
         2, 101, 117, 49, 83, 13, 233, 160, 90, 54, 48, 0, 18, 224, 163, 145, 90,
         8, 46, 176, 190, 175, 151, 24, 190, 8, 238, 94, 208, 74, 164, 186, 90,
         17, 164, 243, 22, 151, 77, 36, 61, 7, 15, 215, 4, 65, 187, 12, 134, 51,
         91, 114, 229, 146, 13, 219, 233, 99, 27, 168, 167, 117, 179, 115, 147,
         119, 118, 154, 147, 143, 186, 148, 218, 207, 108, 221
])

witness_type = 2

t1 = time.time()
result_1 = verify(
    1024,
    challenge_hash,
    a,
    b,
    num_iterations,
    witness,
    witness_type
)
t2 = time.time()

print(f"Result test 1: {result_1}")
print(f"Test time: {t2 - t1}")
assert result_1

result_2 = verify(
    1024,
    challenge_hash,
    a,
    b,
    num_iterations + 1,
    witness,
    witness_type
)

print(f"Result test 2: {result_2}")
assert not result_2
