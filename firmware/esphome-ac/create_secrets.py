"""Create local device keys without asking for or printing home Wi-Fi credentials."""
from pathlib import Path
import secrets


def main():
    path = Path(__file__).with_name("secrets.yaml")
    # Exclusive creation preserves credentials used by an already provisioned device.
    with path.open("x", encoding="utf-8") as out:
        out.write(f'setup_password: "{secrets.token_hex(12)}"\n')
        out.write(f'control_password: "{secrets.token_hex(16)}"\n')
    print("Created ignored secrets.yaml. Open it locally; do not publish it.")


if __name__ == "__main__":
    main()
