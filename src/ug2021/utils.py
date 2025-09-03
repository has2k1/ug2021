from mizani.palettes import gradient_n_pal

# red_green_pal = gradient_n_pal(["#FF0100", "#29850E"])
red_green_pal = gradient_n_pal(["#999999", "#29850E"])


def red_green_pal_pct(value: float) -> list[str]:
    return red_green_pal(value / 100)
