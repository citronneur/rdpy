#include "rle_m.h"

int rle_decode_uint8(char* output, int width, int height, char* input, int size)
{
	char* prevline;
	char* line;
	char* end;
	char color1;
	char color2;
	char mix;
	int code;
	int mixmask;
	int mask;
	int opcode;
	int count;
	int offset;
	int isfillormix;
	int x;
	int lastopcode;
	int insertmix;
	int bicolor;
	int fom_mask;

	end = input + size;
	prevline = 0;
	line = 0;
	x = width;
	lastopcode = -1;
	insertmix = 0;
	bicolor = 0;
	color1 = 0;
	color2 = 0;
	mix = 0xff;
	mask = 0;
	fom_mask = 0;

	while (input < end)
	{
		fom_mask = 0;
		code = CVAL(input);
		opcode = code >> 4;
		/* Handle different opcode forms */
		switch (opcode)
		{
		case 0xc:
		case 0xd:
		case 0xe:
			opcode -= 6;
			count = code & 0xf;
			offset = 16;
			break;
		case 0xf:
			opcode = code & 0xf;
			if (opcode < 9)
			{
				count = CVAL(input);
				count |= CVAL(input) << 8;
			}
			else
			{
				count = (opcode < 0xb) ? 8 : 1;
			}
			offset = 0;
			break;
		default:
			opcode >>= 1;
			count = code & 0x1f;
			offset = 32;
			break;
		}
		/* Handle strange cases for counts */
		if (offset != 0)
		{
			isfillormix = ((opcode == 2) || (opcode == 7));
			if (count == 0)
			{
				if (isfillormix)
				{
					count = CVAL(input) + 1;
				}
				else
				{
					count = CVAL(input) + offset;
				}
			}
			else if (isfillormix)
			{
				count <<= 3;
			}
		}
		/* Read preliminary data */
		switch (opcode)
		{
		case 0: /* Fill */
			if ((lastopcode == opcode) && !((x == width) && (prevline == 0)))
			{
				insertmix = 1;
			}
			break;
		case 8: /* Bicolor */
			color1 = CVAL(input);
		case 3: /* Color */
			color2 = CVAL(input);
			break;
		case 6: /* SetMix/Mix */
		case 7: /* SetMix/FillOrMix */
			mix = CVAL(input);
			opcode -= 5;
			break;
		case 9: /* FillOrMix_1 */
			mask = 0x03;
			opcode = 0x02;
			fom_mask = 3;
			break;
		case 0x0a: /* FillOrMix_2 */
			mask = 0x05;
			opcode = 0x02;
			fom_mask = 5;
			break;
		}
		lastopcode = opcode;
		mixmask = 0;
		/* Output body */
		while (count > 0)
		{
			if (x >= width)
			{
				if (height <= 0)
				{
					return 0;
				}
				x = 0;
				height--;
				prevline = line;
				line = output + height * width;
			}
			switch (opcode)
			{
			case 0: /* Fill */
			if (insertmix)
			{
				if (prevline == 0)
				{
					line[x] = mix;
				}
				else
				{
					line[x] = prevline[x] ^ mix;
				}
				insertmix = 0;
				count--;
				x++;
			}
			if (prevline == 0)
			{
				REPEAT(line[x] = 0)
			}
			else
			{
				REPEAT(line[x] = prevline[x])
			}
			break;
			case 1: /* Mix */
				if (prevline == 0)
				{
					REPEAT(line[x] = mix)
				}
				else
				{
					REPEAT(line[x] = prevline[x] ^ mix)
				}
				break;
			case 2: /* Fill or Mix */
				if (prevline == 0)
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x] = mix;
					}
					else
					{
						line[x] = 0;
					}
					)
				}
				else
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x] = prevline[x] ^ mix;
					}
					else
					{
						line[x] = prevline[x];
					}
					)
				}
				break;
			case 3: /* Color */
				REPEAT(line[x] = color2)
				break;
			case 4: /* Copy */
				REPEAT(line[x] = CVAL(input))
				break;
			case 8: /* Bicolor */
				REPEAT
				(
						if (bicolor)
						{
							line[x] = color2;
							bicolor = 0;
						}
						else
						{
							line[x] = color1;
							bicolor = 1;
							count++;
						}
				)
				break;
			case 0xd: /* White */
				REPEAT(line[x] = 0xff)
				break;
			case 0xe: /* Black */
				REPEAT(line[x] = 0)
				break;
			default:
				return 0;
				break;
			}
		}
	}
	return 1;
}

int rle_decode_uint16(char* output, int width, int height, char* input, int size)
{
	char* prevline;
	char* line;
	char* end;
	char color1[2];
	char color2[2];
	char mix[2];
	int code;
	int mixmask;
	int mask;
	int opcode;
	int count;
	int offset;
	int isfillormix;
	int x;
	int lastopcode;
	int insertmix;
	int bicolor;
	int fom_mask;

	end = input + size;
	prevline = 0;
	line = 0;
	x = width;
	lastopcode = -1;
	insertmix = 0;
	bicolor = 0;
	color1[0] = 0;
	color1[1] = 0;
	color2[0] = 0;
	color2[1] = 0;
	mix[0] = 0xff;
	mix[1] = 0xff;
	mask = 0;
	fom_mask = 0;

	while (input < end)
	{
		fom_mask = 0;
		code = CVAL(input);
		opcode = code >> 4;
		/* Handle different opcode forms */
		switch (opcode)
		{
		case 0xc:
		case 0xd:
		case 0xe:
			opcode -= 6;
			count = code & 0xf;
			offset = 16;
			break;
		case 0xf:
			opcode = code & 0xf;
			if (opcode < 9)
			{
				count = CVAL(input);
				count |= CVAL(input) << 8;
			}
			else
			{
				count = (opcode < 0xb) ? 8 : 1;
			}
			offset = 0;
			break;
		default:
			opcode >>= 1;
			count = code & 0x1f;
			offset = 32;
			break;
		}
		/* Handle strange cases for counts */
		if (offset != 0)
		{
			isfillormix = ((opcode == 2) || (opcode == 7));
			if (count == 0)
			{
				if (isfillormix)
				{
					count = CVAL(input) + 1;
				}
				else
				{
					count = CVAL(input) + offset;
				}
			}
			else if (isfillormix)
			{
				count <<= 3;
			}
		}
		/* Read preliminary data */
		switch (opcode)
		{
		case 0: /* Fill */
			if ((lastopcode == opcode) && !((x == width) && (prevline == 0)))
			{
				insertmix = 1;
			}
			break;
		case 8: /* Bicolor */
			color1[EIK0] = CVAL(input);
			color1[EIK1] = CVAL(input);
		case 3: /* Color */
			color2[EIK0] = CVAL(input);
			color2[EIK1] = CVAL(input);
			break;
		case 6: /* SetMix/Mix */
		case 7: /* SetMix/FillOrMix */
			mix[EIK0] = CVAL(input);
			mix[EIK1] = CVAL(input);
			opcode -= 5;
			break;
		case 9: /* FillOrMix_1 */
			mask = 0x03;
			opcode = 0x02;
			fom_mask = 3;
			break;
		case 0x0a: /* FillOrMix_2 */
			mask = 0x05;
			opcode = 0x02;
			fom_mask = 5;
			break;
		}
		lastopcode = opcode;
		mixmask = 0;
		/* Output body */
		while (count > 0)
		{
			if (x >= width)
			{
				if (height <= 0)
				{
					return 0;
				}
				x = 0;
				height--;
				prevline = line;
				line = output + height * (width * 2);
			}
			switch (opcode)
			{
			case 0: /* Fill */
			if (insertmix)
			{
				if (prevline == 0)
				{
					line[x * 2 + 0] = mix[0];
					line[x * 2 + 1] = mix[1];
				}
				else
				{
					line[x * 2 + 0] = prevline[x * 2 + 0] ^ mix[0];
					line[x * 2 + 1] = prevline[x * 2 + 1] ^ mix[1];
				}
				insertmix = 0;
				count--;
				x++;
			}
			if (prevline == 0)
			{
				REPEAT
				(
						line[x * 2 + 0] = 0;
				line[x * 2 + 1] = 0;
				)
			}
			else
			{
				REPEAT
				(
						line[x * 2 + 0] = prevline[x * 2 + 0];
				line[x * 2 + 1] = prevline[x * 2 + 1];
				)
			}
			break;
			case 1: /* Mix */
				if (prevline == 0)
				{
					REPEAT
					(
							line[x * 2 + 0] = mix[0];
					line[x * 2 + 1] = mix[1];
					)
				}
				else
				{
					REPEAT
					(
							line[x * 2 + 0] = prevline[x * 2 + 0] ^ mix[0];
					line[x * 2 + 1] = prevline[x * 2 + 1] ^ mix[1];
					)
				}
				break;
			case 2: /* Fill or Mix */
				if (prevline == 0)
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x * 2 + 0] = mix[0];
						line[x * 2 + 1] = mix[1];
					}
					else
					{
						line[x * 2 + 0] = 0;
						line[x * 2 + 1] = 0;
					}
					)
				}
				else
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x * 2 + 0] = prevline[x * 2 + 0] ^ mix[0];
						line[x * 2 + 1] = prevline[x * 2 + 1] ^ mix[1];
					}
					else
					{
						line[x * 2 + 0] = prevline[x * 2 + 0];
						line[x * 2 + 1] = prevline[x * 2 + 1];
					}
					)
				}
				break;
			case 3: /* Color */
				REPEAT
				(
						line[x * 2 + 0] = color2[0];
				line[x * 2 + 1] = color2[1];
				)
				break;
			case 4: /* Copy */
				REPEAT
				(
						line[x * 2 + EIK0] = CVAL(input);
				line[x * 2 + EIK1] = CVAL(input);
				)
				break;
			case 8: /* Bicolor */
				REPEAT
				(
						if (bicolor)
						{
							line[x * 2 + 0] = color2[0];
							line[x * 2 + 1] = color2[1];
							bicolor = 0;
						}
						else
						{
							line[x * 2 + 0] = color1[0];
							line[x * 2 + 1] = color1[1];
							bicolor = 1;
							count++;
						}
				)
				break;
			case 0xd: /* White */
				REPEAT
				(
						line[x * 2 + 0] = 0xff;
				line[x * 2 + 1] = 0xff;
				)
				break;
			case 0xe: /* Black */
				REPEAT
				(
						line[x * 2 + 0] = 0;
				line[x * 2 + 1] = 0;
				)
				break;
			default:
				return 0;
				break;
			}
		}
	}
	return 1;
}

int rle_decode_uint24(char* output, int width, int height, char* input, int size)
{
	char* prevline;
	char* line;
	char* end;
	char color1[3];
	char color2[3];
	char mix[3];
	int code;
	int mixmask;
	int mask;
	int opcode;
	int count;
	int offset;
	int isfillormix;
	int x;
	int lastopcode;
	int insertmix;
	int bicolor;
	int fom_mask;

	end = input + size;
	prevline = 0;
	line = 0;
	x = width;
	lastopcode = -1;
	insertmix = 0;
	bicolor = 0;
	color1[0] = 0;
	color1[1] = 0;
	color1[2] = 0;
	color2[0] = 0;
	color2[1] = 0;
	color2[2] = 0;
	mix[0] = 0xff;
	mix[1] = 0xff;
	mix[2] = 0xff;
	mask = 0;
	fom_mask = 0;

	while (input < end)
	{
		fom_mask = 0;
		code = CVAL(input);
		opcode = code >> 4;
		/* Handle different opcode forms */
		switch (opcode)
		{
		case 0xc:
		case 0xd:
		case 0xe:
			opcode -= 6;
			count = code & 0xf;
			offset = 16;
			break;
		case 0xf:
			opcode = code & 0xf;
			if (opcode < 9)
			{
				count = CVAL(input);
				count |= CVAL(input) << 8;
			}
			else
			{
				count = (opcode < 0xb) ? 8 : 1;
			}
			offset = 0;
			break;
		default:
			opcode >>= 1;
			count = code & 0x1f;
			offset = 32;
			break;
		}
		/* Handle strange cases for counts */
		if (offset != 0)
		{
			isfillormix = ((opcode == 2) || (opcode == 7));
			if (count == 0)
			{
				if (isfillormix)
				{
					count = CVAL(input) + 1;
				}
				else
				{
					count = CVAL(input) + offset;
				}
			}
			else if (isfillormix)
			{
				count <<= 3;
			}
		}
		/* Read preliminary data */
		switch (opcode)
		{
		case 0: /* Fill */
			if ((lastopcode == opcode) && !((x == width) && (prevline == 0)))
			{
				insertmix = 1;
			}
			break;
		case 8: /* Bicolor */
			color1[0] = CVAL(input);
			color1[1] = CVAL(input);
			color1[2] = CVAL(input);
		case 3: /* Color */
			color2[0] = CVAL(input);
			color2[1] = CVAL(input);
			color2[2] = CVAL(input);
			break;
		case 6: /* SetMix/Mix */
		case 7: /* SetMix/FillOrMix */
			mix[0] = CVAL(input);
			mix[1] = CVAL(input);
			mix[2] = CVAL(input);
			opcode -= 5;
			break;
		case 9: /* FillOrMix_1 */
			mask = 0x03;
			opcode = 0x02;
			fom_mask = 3;
			break;
		case 0x0a: /* FillOrMix_2 */
			mask = 0x05;
			opcode = 0x02;
			fom_mask = 5;
			break;
		}
		lastopcode = opcode;
		mixmask = 0;
		/* Output body */
		while (count > 0)
		{
			if (x >= width)
			{
				if (height <= 0)
				{
					return 0;
				}
				x = 0;
				height--;
				prevline = line;
				line = output + height * (width * 3);
			}
			switch (opcode)
			{
			case 0: /* Fill */
			if (insertmix)
			{
				if (prevline == 0)
				{
					line[x * 3 + 0] = mix[0];
					line[x * 3 + 1] = mix[1];
					line[x * 3 + 2] = mix[2];
				}
				else
				{
					line[x * 3 + 0] = prevline[x * 3 + 0] ^ mix[0];
					line[x * 3 + 1] = prevline[x * 3 + 1] ^ mix[1];
					line[x * 3 + 2] = prevline[x * 3 + 2] ^ mix[2];
				}
				insertmix = 0;
				count--;
				x++;
			}
			if (prevline == 0)
			{
				REPEAT
				(
						line[x * 3 + 0] = 0;
				line[x * 3 + 1] = 0;
				line[x * 3 + 2] = 0;
				)
			}
			else
			{
				REPEAT
				(
						line[x * 3 + 0] = prevline[x * 3 + 0];
				line[x * 3 + 1] = prevline[x * 3 + 1];
				line[x * 3 + 2] = prevline[x * 3 + 2];
				)
			}
			break;
			case 1: /* Mix */
				if (prevline == 0)
				{
					REPEAT
					(
							line[x * 3 + 0] = mix[0];
					line[x * 3 + 1] = mix[1];
					line[x * 3 + 2] = mix[2];
					)
				}
				else
				{
					REPEAT
					(
							line[x * 3 + 0] = prevline[x * 3 + 0] ^ mix[0];
					line[x * 3 + 1] = prevline[x * 3 + 1] ^ mix[1];
					line[x * 3 + 2] = prevline[x * 3 + 2] ^ mix[2];
					)
				}
				break;
			case 2: /* Fill or Mix */
				if (prevline == 0)
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x * 3 + 0] = mix[0];
						line[x * 3 + 1] = mix[1];
						line[x * 3 + 2] = mix[2];
					}
					else
					{
						line[x * 3 + 0] = 0;
						line[x * 3 + 1] = 0;
						line[x * 3 + 2] = 0;
					}
					)
				}
				else
				{
					REPEAT
					(
							MASK_UPDATE;
					if (mask & mixmask)
					{
						line[x * 3 + 0] = prevline[x * 3 + 0] ^ mix[0];
						line[x * 3 + 1] = prevline[x * 3 + 1] ^ mix[1];
						line[x * 3 + 2] = prevline[x * 3 + 2] ^ mix[2];
					}
					else
					{
						line[x * 3 + 0] = prevline[x * 3 + 0];
						line[x * 3 + 1] = prevline[x * 3 + 1];
						line[x * 3 + 2] = prevline[x * 3 + 2];
					}
					)
				}
				break;
			case 3: /* Color */
				REPEAT
				(
						line[x * 3 + 0] = color2[0];
				line[x * 3 + 1] = color2[1];
				line[x * 3 + 2] = color2[2];
				)
				break;
			case 4: /* Copy */
				REPEAT
				(
						line[x * 3 + 0] = CVAL(input);
				line[x * 3 + 1] = CVAL(input);
				line[x * 3 + 2] = CVAL(input);
				)
				break;
			case 8: /* Bicolor */
				REPEAT
				(
						if (bicolor)
						{
							line[x * 3 + 0] = color2[0];
							line[x * 3 + 1] = color2[1];
							line[x * 3 + 2] = color2[2];
							bicolor = 0;
						}
						else
						{
							line[x * 3 + 0] = color1[0];
							line[x * 3 + 1] = color1[1];
							line[x * 3 + 2] = color1[2];
							bicolor = 1;
							count++;
						}
				)
				break;
			case 0xd: /* White */
				REPEAT
				(
						line[x * 3 + 0] = 0xff;
				line[x * 3 + 1] = 0xff;
				line[x * 3 + 2] = 0xff;
				)
				break;
			case 0xe: /* Black */
				REPEAT
				(
						line[x * 3 + 0] = 0;
				line[x * 3 + 1] = 0;
				line[x * 3 + 2] = 0;
				)
				break;
			default:
				return 0;
				break;
			}
		}
	}
	return 1;
}
