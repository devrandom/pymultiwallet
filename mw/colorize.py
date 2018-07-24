colors = [
    '\033[38;5;21m', # blue (cold)
    '\033[38;5;39m',
    '\033[38;5;50m',
    '\033[38;5;48m',
    '\033[38;5;46m', # green
    '\033[38;5;118m',
    '\033[38;5;190m',
    '\033[38;5;226m', # yellow
    '\033[38;5;220m',
    '\033[38;5;214m', # orange
    '\033[38;5;208m',
    '\033[38;5;202m',
    '\033[38;5;196m', # red
    '\033[38;5;203m',
    '\033[38;5;210m',
    '\033[38;5;217m', # pink
    '\033[38;5;224m',
    '\033[38;5;231m'  # white (hot)
]
reset = '\033[0m'
mapping = 'SE .o+=*BOX@%&#/^'

def colorize_char(c):
    ind = mapping.find(c)
    if (ind < 0 or ind >= len(colors)):
        return c
    return "%s%s%s"%(colors[ind], c, reset)

def colorize(visualization):
    return ''.join(colorize_char(c) for c in visualization)
