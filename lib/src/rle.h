#ifndef _RLE_H_
#define _RLE_H_

namespace rle {
	int decode_uint8(char* output, int width, int height, char* input, int size);
	int decode_uint16(char* output, int width, int height, char* input, int size);
	int decode_uint24(char* output, int width, int height, char* input, int size);
}

#endif
