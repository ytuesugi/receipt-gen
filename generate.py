from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).parent / "src"))


if __name__ == "__main__":
    from receipt_gen.cli import main

    raise SystemExit(main())
