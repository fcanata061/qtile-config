from libqtile import bar, widget, qtile
from libqtile.config import Screen
import subprocess
import time

# ==========================
# Tema (multi-tema)
# ==========================
THEME = "dracula"  # nord | dracula | gruvbox | solarized-dark | solarized-light

# Paletas por tema
palettes = {
    "nord": {
        "base": "#2e3440", "fg": "#d8dee9",
        "cpu": "#81a1c1", "mem": "#5e81ac", "temp": "#88c0d0",
        "net": "#b48ead", "date": "#a3be8c",
    },
    "dracula": {
        "base": "#282a36", "fg": "#f8f8f2",
        "cpu": "#bd93f9", "mem": "#ff5555", "temp": "#f1fa8c",
        "net": "#6272a4", "date": "#50fa7b",
    },
    "gruvbox": {
        "base": "#282828", "fg": "#ebdbb2",
        "cpu": "#d79921", "mem": "#98971a", "temp": "#d65d0e",
        "net": "#458588", "date": "#b16286",
    },
    "solarized-dark": {
        "base": "#002b36", "fg": "#93a1a1",
        "cpu": "#268bd2", "mem": "#2aa198", "temp": "#b58900",
        "net": "#6c71c4", "date": "#859900",
    },
    "solarized-light": {
        "base": "#eee8d5", "fg": "#073642",
        "cpu": "#2aa198", "mem": "#859900", "temp": "#b58900",
        "net": "#268bd2", "date": "#d33682",
    }
}

colors = palettes.get(THEME, palettes["dracula"])
separator = ""

# ==========================
# Widget personalizado NetSpeed
# ==========================
class NetSpeed(widget.ThreadedPollText):
    defaults = [("update_interval", 1, "Update interval")]
    def __init__(self, **config):
        super().__init__(**config)
        self.last_rx = 0
        self.last_tx = 0
        self.last_time = None

    def poll(self):
        try:
            dev = subprocess.check_output(
                "ip route | awk '/^default/ {print $5; exit}'",
                shell=True).decode().strip()
        except subprocess.CalledProcessError:
            return " Offline"

        if not dev:
            return " Offline"

        rx = int(open(f"/sys/class/net/{dev}/statistics/rx_bytes").read())
        tx = int(open(f"/sys/class/net/{dev}/statistics/tx_bytes").read())
        now = time.time()

        if self.last_time is None:
            self.last_rx = rx
            self.last_tx = tx
            self.last_time = now
            return f" {dev} 0.0↓ 0.0↑"

        interval = now - self.last_time
        if interval <= 0: interval = 1

        rx_rate = (rx - self.last_rx) / interval
        tx_rate = (tx - self.last_tx) / interval

        self.last_rx = rx
        self.last_tx = tx
        self.last_time = now

        def fmt(v):
            if v > 1048576:
                return f"{v/1048576:.1f}MB/s"
            elif v > 1024:
                return f"{v/1024:.1f}KB/s"
            else:
                return f"{v:.0f}B/s"

        return f" {dev} {fmt(rx_rate)}↓ {fmt(tx_rate)}↑"

# ==========================
# Função para criar bloco Powerline clicável
# ==========================
def powerline_block(text, bg, next_bg, click_cmd=None, padding=8):
    """Cria bloco com separador colorido, opcionalmente clicável"""
    widgets = []

    if click_cmd:
        widgets.append(
            widget.TextBox(
                text=f" {text} ",
                background=bg,
                foreground=colors["fg"],
                padding=padding,
                fontsize=14,
                mouse_callbacks={"Button1": lambda: subprocess.Popen(click_cmd, shell=True)}
            )
        )
    else:
        widgets.append(
            widget.TextBox(
                text=f" {text} ",
                background=bg,
                foreground=colors["fg"],
                padding=padding,
                fontsize=14
            )
        )

    widgets.append(
        widget.TextBox(
            text=separator,
            foreground=bg,
            background=next_bg,
            padding=0,
            fontsize=18
        )
    )
    return widgets

# ==========================
# Configuração da barra
# ==========================
screens = [
    Screen(
        top=bar.Bar(
            widgets=sum([
                # CPU (clicável -> htop)
                powerline_block(" CPU", colors["cpu"], colors["mem"], click_cmd="xterm -e htop"),
                [widget.CPU(format="{load_percent}%", background=colors["cpu"], foreground=colors["fg"], padding=6)],
                # Memória (clicável -> htop)
                powerline_block(" MEM", colors["mem"], colors["temp"], click_cmd="xterm -e htop"),
                [widget.Memory(format="{MemUsed:.0f}/{MemTotal:.0f}MB", background=colors["mem"], foreground=colors["fg"], padding=6)],
                # Temperatura (clicável -> sensors)
                powerline_block(" TEMP", colors["temp"], colors["net"], click_cmd="xterm -e sensors"),
                [widget.ThermalSensor(tag_sensor="Package id 0", fmt="{:.0f}°C", background=colors["temp"], foreground=colors["fg"], padding=6)],
                # Rede (clicável -> nmtui)
                powerline_block("", colors["net"], colors["date"], click_cmd="xterm -e nmtui"),
                [NetSpeed(background=colors["net"], foreground=colors["fg"], padding=6)],
                # Data/Hora (não clicável)
                powerline_block("", colors["date"], colors["base"]),
                [widget.Clock(format=" %d/%m/%Y  %H:%M", background=colors["date"], foreground=colors["fg"], padding=6)],
            ], [])
            ,
            26,  # altura da barra
            background=colors["base"]
        )
    )
        ]
