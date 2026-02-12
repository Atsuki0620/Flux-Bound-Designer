import sys
from pathlib import Path

from streamlit.web import cli as stcli


def resolve_app_path() -> Path:
    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", "")
        if not meipass:
            raise RuntimeError("PyInstaller frozen mode detected, but sys._MEIPASS is missing.")
        base_dir = Path(meipass)
    else:
        base_dir = Path(__file__).resolve().parent

    app_path = base_dir / "app.py"
    if not app_path.exists():
        raise FileNotFoundError(f"Streamlit app file was not found: {app_path}")

    return app_path


def main() -> None:
    app_path = resolve_app_path()

    print(f"[FluxBoundDesigner] frozen={getattr(sys, 'frozen', False)}")
    print(f"[FluxBoundDesigner] app_path={app_path}")
    print("[FluxBoundDesigner] launching streamlit on http://localhost:8501")

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        "8501",
        "--server.address",
        "127.0.0.1",
        "--browser.serverAddress",
        "localhost",
        "--browser.serverPort",
        "8501",
        "--server.headless",
        "true",
        "--global.developmentMode",
        "false",
        "--browser.gatherUsageStats",
        "false",
    ]
    raise SystemExit(stcli.main())


if __name__ == "__main__":
    main()
