from libqtile import bar, widget
from libqtile.config import Screen
from libqtile import qtile
import psutil
import subprocess

# ===============================
# Função para mostrar taxa de rede
# ===============================
class NetSpeed(widget.ThreadedPollText):
    """Widget personalizado para upload/download da interface padrão"""
    defaults = [
        ("update_interval", 1, "Update interval"),
    ]

    def __init__(self, **config):
        super().__init__(**config)
        self.last_rx = 0
        self.last_tx = 0
        self.last_time = None

    def poll(self):
        # interface padrão
        try:
            dev = subprocess.check_output("ip route | awk '/^default/ {print $5; exit}'", shell=True).decode().strip()
        except subprocess.CalledProcessError:
            return " Offline"

        if not dev:
            return " Offline"

        rx = int(open(f"/sys/class/net/{dev}/statistics/rx_bytes").read())
        tx = int(open(f"/sys/class/net/{dev}/statistics/tx_bytes").read())
        import time
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

        def format_rate(val):
            if val > 1048576:
                return f"{val/1048576:.1f}MB/s"
            elif val > 1024:
                return f"{val/1024:.1f}KB/s"
            else:
                return f"{val:.0f}B/s"

        return f" {dev} {format_rate(rx_rate)}↓ {format_rate(tx_rate)}↑"

# ===============================
# Paleta de cores Powerline
# ===============================
colors = {
    "base": "#282c34",
    "fg": "#ffffff",
    "cpu": "#bd93f9",
    "mem": "#ff5555",
    "temp": "#f1fa8c",
    "net": "#6272a4",
    "date": "#50fa7b",
}

separator = ""  # Powerline separator

# ===============================
# Widgets com Powerline
# ===============================
def powerline_widget(text, bg_color, next_bg=None):
    """Cria um bloco Powerline simples"""
    if next_bg:
        sep = f'{separator}'
    else:
        sep = ''
    return f' {text} {sep}'

# ===============================
# Configuração da barra Qtile
# ===============================
screens = [
    Screen(
        top=bar.Bar(
            [
                widget.Spacer(length=5),
                widget.CPU(
                    format=" {load_percent}%",
                    background=colors["cpu"],
                    foreground=colors["fg"],
                ),
                widget.TextBox(text=separator, foreground=colors["cpu"], background=colors["mem"], fontsize=16),
                widget.Memory(
                    format=" {MemUsed:.0f}/{MemTotal:.0f}MB",
                    background=colors["mem"],
                    foreground=colors["fg"],
                ),
                widget.TextBox(text=separator, foreground=colors["mem"], background=colors["temp"], fontsize=16),
                widget.ThermalSensor(
                    tag_sensor="Package id 0",
                    fmt=" {}°C",
                    background=colors["temp"],
                    foreground=colors["fg"],
                ),
                widget.TextBox(text=separator, foreground=colors["temp"], background=colors["net"], fontsize=16),
                NetSpeed(
                    background=colors["net"],
                    foreground=colors["fg"],
                ),
                widget.TextBox(text=separator, foreground=colors["net"], background=colors["date"], fontsize=16),
                widget.Clock(
                    format=" %d/%m/%Y  %H:%M",
                    background=colors["date"],
                    foreground=colors["fg"],
                ),
                widget.Spacer(length=5),
            ],
            24,  # altura da barra
            background=colors["base"],
        )
    )
]
