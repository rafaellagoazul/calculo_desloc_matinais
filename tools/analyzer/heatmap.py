def score_to_color(score, min_s, max_s):
    if max_s == min_s:
        return "#4cc9f0"  # neutro

    norm = (score - min_s) / (max_s - min_s)

    # verde → amarelo → vermelho
    if norm < 0.5:
        r = int(255 * norm * 2)
        g = 255
    else:
        r = 255
        g = int(255 * (1 - (norm - 0.5) * 2))

    return f"#{r:02x}{g:02x}00"
