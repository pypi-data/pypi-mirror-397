#include "keyedDecrypt.c"
#include <stdio.h>

#define ASSERT(x) if(!(x)) asm("int $3")

u32 get_file_content(u8** output, char* filepath) {
    FILE* file = fopen(filepath, "rb");
    ASSERT(file);
    fseek(file, 0, SEEK_END);
    u32 bufferSize = ftell(file);
    fseek(file, 0, SEEK_SET);

    *output = malloc(bufferSize);
    fread(*output, bufferSize, 1, file);

    fclose(file);

    return bufferSize;
}

int main() {

#if 0
    u8* buffer;
    u32 bufferSize = get_file_content(&buffer, "/tmp/buffer");
    //u32 bufferSize = get_file_content(&buffer, "/tmp/rolling_xor_test");
#else
    u8 buffer[] = "this is not important - this is nffset -\"abcdefgkijklmnotqrstuvw}yz - thos is thb rest on the cogtent";

    u32 bufferSize = sizeof(buffer)-1;
#endif

#if 0
    u8* output_buffer = malloc(bufferSize);
    xor_decrypt(output_buffer, buffer, bufferSize, 27, 3, 1, true);
#elif 0
    u8 pattern[] = "http://";
    u32 patternSize = sizeof(pattern)-1;
    u32 patternOffset = 0;

    ComplexCrypt* results = malloc(10 * sizeof(ComplexCrypt));
    u32 result_count;
    xor_find(results, 10, &result_count, buffer, bufferSize, pattern, patternSize, patternOffset);

#else
    u8 pattern[] = "abcdefghijklmnopqrstuvwxyz";
    u32 patternSize = sizeof(pattern)-1;
    u32 patternOffset = 17;

    u32 result_max = 2;
    ComplexCrypt* results = malloc(result_max * sizeof(BasicCrypt));
    u32 result_count;
    xor_find(results, result_max, &result_count, buffer, bufferSize, pattern, patternSize, patternOffset);
#endif

    return 0;
}