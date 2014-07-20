%Module(name=rle, language="C")

%UnitCode
#include "../../src/rle/rle.h"
%End

int bitmap_decompress(void * output, int width, int height, char * input, int size, int Bpp);

