# =========================
# COLOR PRINT FUNCTION
# =========================
# Usage: ANSI("colorname", "text")
# This prints colored text directly (no return)

def ANSI(subcolor, text):
    COLORS = {
        "black": "\033[38;5;0m",
        "white": "\033[38;5;15m",
        "gray": "\033[38;5;8m",
        "lightgray": "\033[38;5;7m",
        "darkgray": "\033[38;5;240m",

        "red": "\033[38;5;1m",
        "brightred": "\033[38;5;9m",
        "darkred": "\033[38;5;88m",
        "maroon": "\033[38;5;52m",
        "crimson": "\033[38;5;160m",

        "yellow": "\033[38;5;3m",
        "brightyellow": "\033[38;5;11m",
        "orange": "\033[38;5;208m",
        "darkorange": "\033[38;5;166m",
        "gold": "\033[38;5;220m",
        "amber": "\033[38;5;214m",
        "mustard": "\033[38;5;178m",

        "green": "\033[38;5;2m",
        "brightgreen": "\033[38;5;10m",
        "lime": "\033[38;5;118m",
        "lightgreen": "\033[38;5;120m",
        "darkgreen": "\033[38;5;22m",
        "olive": "\033[38;5;58m",
        "mint": "\033[38;5;121m",

        "blue": "\033[38;5;4m",
        "brightblue": "\033[38;5;12m",
        "lightblue": "\033[38;5;117m",
        "skyblue": "\033[38;5;111m",
        "cyan": "\033[38;5;6m",
        "aqua": "\033[38;5;14m",
        "teal": "\033[38;5;30m",
        "navy": "\033[38;5;17m",

        "magenta": "\033[38;5;5m",
        "brightmagenta": "\033[38;5;13m",
        "purple": "\033[38;5;93m",
        "violet": "\033[38;5;177m",
        "lavender": "\033[38;5;183m",
        "pink": "\033[38;5;218m",
        "hotpink": "\033[38;5;205m",

        "brown": "\033[38;5;94m",
        "darkbrown": "\033[38;5;52m",
        "tan": "\033[38;5;180m",
        "beige": "\033[38;5;223m",
    }

    RESET = "\033[0m"

    color = COLORS.get(subcolor.lower())
    if color is None:
        raise ValueError(f"Unknown color: {subcolor}")

    print(color + text + RESET)