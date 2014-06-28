%Module(name=rle, language="C")

%UnitCode
#include "rle.h"
%End

int rle_decode_uint8(void* output, int width, int height, char* input, int size);
int rle_decode_uint16(void* output, int width, int height, char* input, int size);
int rle_decode_uint24(void* output, int width, int height, char* input, int size);
