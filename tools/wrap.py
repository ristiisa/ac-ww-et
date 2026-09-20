"""Wrap text to the pixel width of the game's font (see check.width)."""
import check


def wrap(text, maxpx):
    lines = []
    for para in text.split('\n'):
        cur = ''
        for word in para.split():
            trial = f'{cur} {word}'.strip()
            if cur and check.width(trial) > maxpx:
                lines.append(cur)
                cur = word
            else:
                cur = trial
        lines.append(cur)
    return lines


def too_wide(text, maxpx):
    """Words that cannot fit on a line by themselves."""
    return [w for w in text.split() if check.width(w) > maxpx]
