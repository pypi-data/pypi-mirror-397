def divstep(delta: int, f: int, g: int) -> tuple[int, int, int]:
    if (g & 1) == 0:
        return delta + 2, f, g >> 1
    if delta < 0:
        return delta + 2, f, (g + f) >> 1
    return 2 - delta, g, (g - f) >> 1

