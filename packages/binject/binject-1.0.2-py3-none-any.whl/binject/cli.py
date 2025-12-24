import argparse
import sys
from . import patch_apk

def patch(args):
    print(args.apk_path)
    print(args.so_path)

    patch_apk.inject_so(args.apk_path, args.so_path, args.arch)



def main():
    parser = argparse.ArgumentParser(description="Binject: inject shared object to apk")

    parser.add_argument("apk_path", help="path to target apk")
    parser.add_argument("so_path", help="path to target so")
    parser.add_argument(
        "--arch", 
        default="arm64-v8a", 
        help="target architecture (default: arm64-v8a, options: armeabi-v7a, x86, etc)"
    )


    parser.set_defaults(func=patch)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()

    args.func(args)



if __name__ == "__main__":
    main()
