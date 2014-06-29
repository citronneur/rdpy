#ifndef _RLE_M_H_
#define _RLE_M_H_

#include "rle.h"

#define CVAL(p) ((unsigned char)(*(p++)))

#if defined(B_ENDIAN)
#define EIK0 1
#define EIK1 0
#else
#define EIK0 0
#define EIK1 1
#endif

#define REPEAT(statement) \
{ \
  while ((count > 0) && (x < width)) \
  { \
    statement; \
    count--; \
    x++; \
  } \
}

#define MASK_UPDATE \
{ \
  mixmask <<= 1; \
  if ((mixmask & 0xff) == 0) \
  { \
    mask = fom_mask ? fom_mask : CVAL(input); \
    mixmask = 1; \
  } \
}
#endif
