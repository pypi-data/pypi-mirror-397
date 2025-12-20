"""Configuration management script for FWAuto."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fwauto.config import print_config_info


def main():
    """Main configuration management function."""
    print("FWAuto Configuration Tool")
    print("=" * 40)
    print_config_info()


if __name__ == "__main__":
    main()
