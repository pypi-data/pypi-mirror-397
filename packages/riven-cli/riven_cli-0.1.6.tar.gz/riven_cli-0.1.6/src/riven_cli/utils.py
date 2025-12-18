import os
import shutil
import subprocess

from riven_cli.config import settings


def play_video(item_id: int) -> str:
    try:
        url = f"{settings.api_url}/api/v1/stream/file/{item_id}?api_key={settings.api_key}"

        # Try to detect the best terminal
        terminal, cmd = _get_terminal_command(settings.video_player, url)

        subprocess.Popen(cmd, start_new_session=True)
        return f"Launched {settings.video_player} in {terminal}"
    except Exception as e:
        raise Exception(f"Failed to launch player: {str(e)}")


def _get_terminal_command(player: str, url: str) -> tuple[str, list[str]]:
    # 1. Check for xdg-terminal-exec (modern freedesktop standard)
    if shutil.which("xdg-terminal-exec"):
        return ("xdg-terminal-exec", ["xdg-terminal-exec", player, url])

    # 2. Check $TERMINAL environment variable
    env_terminal = os.environ.get("TERMINAL")
    if env_terminal and shutil.which(env_terminal):
        return (env_terminal, _build_cmd(env_terminal, player, url))

    # 3. Try common terminals in order of preference
    terminals = [
        "kitty",
        "alacritty",
        "wezterm",
        "foot",  # Modern GPU-accelerated
        "gnome-terminal",
        "konsole",
        "xfce4-terminal",
        "tilix",
        "terminator",  # DE-specific
        "x-terminal-emulator",  # Debian/Ubuntu alternative system
        "urxvt",
        "st",
        "xterm",  # Classic/minimal
    ]

    for term in terminals:
        if shutil.which(term):
            return (term, _build_cmd(term, player, url))

    # 4. Fallback: run directly without terminal
    return ("background", [player, url])


def _build_cmd(terminal: str, player: str, url: str) -> list[str]:
    # Terminals that use `--` separator
    if terminal in ("gnome-terminal",):
        return [terminal, "--", player, url]

    # Wezterm uses `start`
    if terminal == "wezterm":
        return [terminal, "start", "--", player, url]

    # Most terminals use `-e`
    return [terminal, "-e", player, url]
