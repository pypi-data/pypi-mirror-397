
// labels used by ctypes_autogen.py to autogenerate interop code
#define PY_CALL
#define PY_IN
#define PY_OUT
#define PY_LIST_OUT
#define PY_BYTES_OUT

// alloca
#include <stdlib.h>
// strlen and memset
#include <string.h>

#include <stdint.h>
typedef uint8_t u8;
typedef uint16_t u16;
typedef uint32_t u32;
typedef uint64_t u64;
typedef int8_t s8;
typedef int16_t s16;
typedef int32_t s32;
typedef int64_t s64;
typedef uint8_t b8;
typedef uint32_t b32;

#define true 1
#define false 0


typedef struct ComplexCrypt {
    u8 key_size;
    b8 ignore_zero;
    u32 offset;
    u64 starting_key;
    s64 key_increment;
} ComplexCrypt;

typedef struct BasicCrypt {
    u8 deob_key;
    u32 offset;
} BasicCrypt;


PY_CALL void rolling_xor_decrypt(PY_BYTES_OUT u8* output_buffer, PY_IN u8* input_buffer, PY_IN u32 buffer_size, PY_IN u8 start_key) {
    output_buffer[0] = input_buffer[0] ^ start_key;
    for(u32 buffer_index = 1; buffer_index < buffer_size; ++buffer_index) {
        output_buffer[buffer_index] = input_buffer[buffer_index] ^ input_buffer[buffer_index-1];
    }
}

PY_CALL void rolling_xor_find(PY_LIST_OUT u32* offsets, PY_IN u32 offset_count_max, PY_OUT u32* offset_count, 
                              PY_IN u8* buffer, PY_IN u32 buffer_size, 
                              PY_IN u8* pattern, PY_IN u32 pattern_size, PY_IN u32 pattern_offset) {
    *offset_count = 0;
    u32 next_index = 0;
    u32 pattern_index = pattern_size-1;
    for(u32 buffer_index = buffer_size-1; buffer_index > pattern_offset; --buffer_index) {
        if((buffer[buffer_index] ^ buffer[buffer_index-1]) == pattern[pattern_index]) {

            // check if this byte could be the start of another instance of the pattern,
            // so that the next check can start here
            if(next_index == 0 && pattern_index < pattern_size-1 && 
               (buffer[buffer_index] ^ buffer[buffer_index-1]) == pattern[pattern_size-1]) {
                next_index = buffer_index;
            }
            if(pattern_index == 1) {
                // we have found a match, add offset to list
                offsets[*offset_count] = buffer_index-1 - pattern_offset;
                ++*offset_count;
                if(*offset_count == offset_count_max) {
                    // we have filled our results buffer, so break out of everything.
                    break;
                }
                if(next_index) {
                    buffer_index = next_index+1;
                    next_index = 0;
                }
                pattern_index = pattern_size-1;
            }
            else {
                --pattern_index;
            }
        }
        else {
            pattern_index = pattern_size-1;
            if(next_index) {
                buffer_index = next_index+1;
                next_index = 0;
            }
        }
    }
}

PY_CALL void xor_decrypt(PY_BYTES_OUT u8* output_buffer, PY_IN u8* input_buffer, PY_IN u32 buffer_size,
                 PY_IN u64 key, PY_IN u8 key_size, 
                 PY_IN s64 key_increment, PY_IN b8 ignore_zero) {
    u32 zero_count = 0;

    for(u32 buffer_index = 0; buffer_index < buffer_size; ++buffer_index) {
        u32 key_index = buffer_index % key_size;

        if(ignore_zero) {
            // if a keysize worth of bytes are zero and the encryption ignores zeroes, 
            // go back and change them back to zeroes.
            if(key_index == zero_count && input_buffer[buffer_index] == 0 && key != 0) {
                ++zero_count;
                if(zero_count == key_size) {
                    memset(output_buffer + buffer_index - key_size + 1,
                           0, key_size);
                    zero_count = 0;
                    key -= (u64)key_increment;
                    key %= 2uLL << key_size*8-1;
                    continue;
                }
            }
            else {
                zero_count = 0;
            }
        }

        if(key_index == 0 && buffer_index > 0) {
            if(key_increment) {
                key += (u64)key_increment;
                key %= 2uLL << key_size*8-1;
            }
        }

        // do the xor.
        output_buffer[buffer_index] = input_buffer[buffer_index] ^ ((u8*)&key)[key_index];
    }
}

PY_CALL void xor_find(PY_LIST_OUT ComplexCrypt* results, PY_IN u32 result_count_max, PY_OUT u32* result_count, 
                           PY_IN u8* buffer, PY_IN u32 buffer_size,
                           PY_IN u8* pattern, PY_IN u32 pattern_size, PY_IN u32 pattern_offset) {
    // keep pointer to next result in result list
    ComplexCrypt* next_result = results;
    // check if buffer is big enough to hold pattern
    if(buffer_size >= pattern_size) {
        // the pattern needs to be big enough to hold at least 3 instances of a key, 
        // plus one instance that may be cut off by the pattern not being aligned to the key size.
        u8 max_keysize = sizeof(u64);
        if(max_keysize > pattern_size/4) {
            max_keysize = pattern_size/4;
        }

        // step through whole buffer one byte at a time
        for(u32 offset = pattern_offset; offset < buffer_size-pattern_size+1; ++offset) {
            for(u8 key_size = 1; key_size <= max_keysize; ++key_size) {
                // note: cannot use (1uLL << key_size*8) - 1 to calculate the mask, because the RH operand of a shift
                // is masked to 5 bits, meaning that 1 << 64 == 1, not zero as expected.
                u64 key_mask = (2uLL << key_size*8-1) - 1;
                u32 valid_checked = 0;
                u64 prev_key = 0;
                next_result->ignore_zero = false;

                // any start/end of the pattern that does not align with the key size is ignored.
                for(u32 pattern_index = (key_size - pattern_offset % key_size) * (pattern_offset % key_size != 0);
                    pattern_index < pattern_size; 
                    pattern_index += key_size) {
                    // xor the buffer by the pattern to get the key. 
                    u64 key = *(u64*)(buffer + offset + pattern_index) ^ 
                              *(u64*)(pattern + pattern_index);
                    key &= key_mask;

                    // if there is a zero in both xor'd and unxor'd pattern, then either the encryption 
                    // is ignoring zeroes, or there isn't any encryption at all.
                    if(key == 0 && (*(u64*)(pattern + pattern_index) & key_mask) == 0) {
                        next_result->ignore_zero = true;
                    }
                    else {
                        if(valid_checked == 0) {
                            next_result->starting_key = key;
                        }
                        else if(valid_checked == 1) {
                            // record how much the key has changed by to see if the pattern continues
                            next_result->key_increment = key - prev_key;
                            // need to wrap key differences bigger than the key byte size, 
                            // being careful to avoid a divide-by-zero for an 8 byte key.
                            if((key_mask+1) != 0) {
                                next_result->key_increment %= key_mask + 1;
                            }
                        }
                        else {
                            u64 key_diff = key - prev_key;
                            // need to wrap key differences bigger than the key byte size, 
                            // being careful to avoid a divide-by-zero for an 8 byte key.
                            if((key_mask+1) != 0) {
                                key_diff %= key_mask + 1;
                            }
                            if(key_diff != (u64)next_result->key_increment) {
                                // the key has changed unpredictably, fail
                                break;
                            }
                            if(pattern_size - pattern_index < 2*key_size) {
                                // we have reached the end of the pattern
                                next_result->key_size = key_size;
                                next_result->offset = offset - pattern_offset;
                                
                                if(next_result->key_increment != 0) {
                                    if(next_result->ignore_zero) {
                                        // iterate backwards to calculate the key at the start of the encryption,
                                        // skipping zeros aligned to the key size.
                                        for(u32 key_calc_index = next_result->offset + 
                                            (key_size - pattern_offset % key_size) * (pattern_offset % key_size != 0); 
                                            key_calc_index > next_result->offset - pattern_offset; 
                                            key_calc_index -= key_size) {
                                            
                                            if(*(u64*)(buffer + key_calc_index) % key_mask != 0) {
                                                next_result->starting_key -= next_result->key_increment;
                                            }
                                        }
                                    }
                                    else {
                                        next_result->starting_key -= (pattern_offset + 
                                                                      (key_size - pattern_offset % key_size) * 
                                                                      (pattern_offset % key_size != 0)) /
                                                                     key_size * next_result->key_increment;
                                    }
                                }

                                // convert increment to a negative number if it makes sense to do so
                                if(next_result->key_increment >= (s64)(key_mask+1)/2) {
                                    next_result->key_increment -= (s64)(key_mask+1);
                                }
                                ++next_result;
                                if(next_result-results == result_count_max) {
                                    // we have filled our results buffer, so break out of everything.
                                    goto end_find_xor;
                                }
                                // skip the rest of the checks for this buffer offset
                                goto next_offset;
                            }
                        }
                        prev_key = key;
                        ++valid_checked;
                    }
                }
            }
            next_offset:;
        }
        end_find_xor:;
        *result_count = next_result-results;
    }
}

PY_CALL void add_decrypt(PY_BYTES_OUT u8* output_buffer, PY_IN u8* input_buffer, PY_IN u32 buffer_size, PY_IN u8 key) {
    for(u32 buffer_index = 0; buffer_index < buffer_size; ++buffer_index) {
        output_buffer[buffer_index] = input_buffer[buffer_index] + key;
    }
}

PY_CALL void add_find(PY_LIST_OUT BasicCrypt* results, PY_IN u32 result_count_max, PY_OUT u32* result_count, 
                           PY_IN u8* buffer, PY_IN u32 buffer_size,
                           PY_IN u8* pattern, PY_IN u32 pattern_size, PY_IN u32 pattern_offset) {
    *result_count = 0;

    if(buffer_size >= pattern_size) {
        // get the difference between each byte in the target pattern
        u8* pattern_diffs = alloca(pattern_size-1);
        pattern_diffs[0] = 0;
        for(u32 diff_index = 0; diff_index < pattern_size-1; ++diff_index) {
            pattern_diffs[diff_index] = pattern[diff_index+1] - pattern[diff_index];
        }

        u32 next_index = 0;
        u32 diff_index = 0;
        for(u32 buffer_index = pattern_offset; buffer_index < buffer_size-1; ++buffer_index) {
            // this has to be cast, since apparently u8 - u8 = s32?? apparently an issue on all compilers
            if((u8)(buffer[buffer_index+1] - buffer[buffer_index]) == pattern_diffs[diff_index]) {
                // don't skip over another occurence of the start of the pattern
                if(next_index == 0 && diff_index > 0 && 
                   (u8)(buffer[buffer_index+1] - buffer[buffer_index]) == pattern_diffs[0]) {
                    next_index = buffer_index;
                }
                ++diff_index;
                if(diff_index == pattern_size-1) {
                    results[*result_count].offset = buffer_index - pattern_offset - diff_index + 1;
                    results[*result_count].deob_key = pattern[0] - buffer[results[*result_count].offset];
                    ++*result_count;
                    if(*result_count == result_count_max) {
                        // we have filled our results buffer, so break out of everything.
                        break;
                    }
                    diff_index = 0;
                    if(next_index > 0) {
                        buffer_index = next_index - 1;
                        next_index = 0;
                    }
                }
            }
            else {
                diff_index = 0;
                if(next_index > 0) {
                    buffer_index = next_index - 1;
                    next_index = 0;
                }
            }
        }
    }
}

u8 rol(u8 byte, u8 rotate_bits) {
    return (byte << rotate_bits) | (byte >> (8 - rotate_bits));
}

PY_CALL void rol_decrypt(PY_BYTES_OUT u8* output_buffer, PY_IN u8* input_buffer, PY_IN u32 buffer_size, PY_IN u8 key) {
    for(u32 buffer_index = 0; buffer_index < buffer_size; ++buffer_index) {
        output_buffer[buffer_index] = rol(input_buffer[buffer_index], key);
    }
}

PY_CALL void rol_find(PY_LIST_OUT BasicCrypt* results, PY_IN u32 result_count_max, PY_OUT u32* result_count, 
                           PY_IN u8* buffer, PY_IN u32 buffer_size,
                           PY_IN u8* pattern, PY_IN u32 pattern_size, PY_IN u32 pattern_offset) {
    *result_count = 0;

    if(buffer_size >= pattern_size) {
        for(u32 buffer_index = pattern_offset; buffer_index < buffer_size; ++buffer_index) {
            for(u8 rotate_bits = 1; rotate_bits < 8; ++rotate_bits) {
                for(u32 pattern_index = 0; pattern_index < pattern_size; ++pattern_index) {
                    if(rol(buffer[buffer_index + pattern_index], rotate_bits) == pattern[pattern_index]) {
                        if(pattern_index == pattern_size-1) {
                            results[*result_count].deob_key = rotate_bits;
                            results[*result_count].offset = buffer_index - pattern_offset;
                            ++*result_count;
                            if(*result_count == result_count_max) {
                                // we have filled our results buffer, so break out of everything.
                                goto end_find_rol;
                            }
                        }
                    }
                    else {
                        break;
                    }
                }
            }
        }
        end_find_rol:;
    }
}
