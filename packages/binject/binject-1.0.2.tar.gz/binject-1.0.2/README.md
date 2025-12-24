# Binject
inject shared object to an apk

## Install:

```bash
pip install binject 
```

## Usage:


```bash
usage: binject [-h] [--arch ARCH] <apk_path> <so_path>

Binject: inject shared object to apk

positional arguments:
  <apk_path>   path to target apk
  <so_path>    path to target so

options:
  -h, --help   show this help message and exit
  --arch ARCH  target architecture (default: arm64-v8a, options: armeabi-v7a, x86, etc)


```

## Features

- injects loadlibrary() to main activity
- injects internet permissions to AndroidManifest.xml if not present