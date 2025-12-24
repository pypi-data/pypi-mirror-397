import sys
import shutil
import subprocess
import re
import os
from pathlib import Path
from androguard.core.apk import APK

def run_cmd(cmd_list):
    executable = shutil.which(cmd_list[0])
    if not executable:
        executable = cmd_list[0]
    cmd_list[0] = executable
    is_windows = sys.platform.startswith("win")
    subprocess.check_call(cmd_list, shell=is_windows)

def fix_resource_errors(temp_dir):
    """
    Scans the res folder and removes attributes that commonly cause 
    apktool build failures (like accessibilityPaneTitle).
    """
    print("[*] Cleaning up problematic resource attributes...")
   
    bad_attrs = [
        r'android:accessibilityPaneTitle="[^"]*"',
        r'android:compileSdkVersion="[^"]*"',
        r'android:compileSdkVersionCodename="[^"]*"',
        r'android:appComponentFactory="[^"]*"',
        r'android:allowNativeHeapPointerTagging="[^"]*"'
    ]
    
    res_path = Path(temp_dir) / "res"
    if not res_path.exists():
        return

    for xml_file in res_path.rglob("*.xml"):
        try:
            content = xml_file.read_text(encoding='utf-8')
            original_content = content
            for attr in bad_attrs:
                content = re.sub(attr, '', content)
            
            if content != original_content:
                xml_file.write_text(content, encoding='utf-8')
        except:
            continue

def inject_so(apk, so, arch):
    apk_path = Path(apk).resolve()
    so_path = Path(so).resolve()
    temp_dir = Path("temp_build").resolve()
    output_apk = Path.cwd() / f"{apk_path.stem}_injected.apk"

    if not apk_path.exists():
        raise FileNotFoundError(f"APK not found: {apk_path}")
    if not so_path.exists():
        raise FileNotFoundError(f"SO file not found: {so_path}")

    print(f"[*] Analyzing {apk_path.name}...")
    apk_obj = APK(str(apk_path))
    main_activity = apk_obj.get_main_activity()
    if not main_activity:
        raise Exception("Could not detect Main Activity")

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    
    print("[*] Decompiling...")

    run_cmd(["apktool", "d", "-f", "-o", str(temp_dir), str(apk_path)])


    fix_resource_errors(temp_dir)


    manifest_path = temp_dir / "AndroidManifest.xml"
    if manifest_path.exists():
        try:
            content = manifest_path.read_text(encoding='utf-8')
            

            content = re.sub(r'android:(compileSdkVersion|compileSdkVersionCodename|appComponentFactory)="[^"]*"', '', content)
            

            if 'android.permission.INTERNET' not in content:
                print("[*] Adding Internet permission...")
                content = content.replace('<application', '<uses-permission android:name="android.permission.INTERNET" />\n    <application', 1)
            
            manifest_path.write_text(content, encoding='utf-8')
        except UnicodeDecodeError:
            print("[!] Warning: AndroidManifest.xml is binary. Skipping sanitization.")

    print(f"[*] Copying library to lib/{arch}...")
    lib_dir = temp_dir / "lib" / arch
    lib_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(so_path, lib_dir / so_path.name)

    print(f"[*] Injecting loadLibrary into {main_activity}...")
    smali_path = main_activity.replace('.', '/') + ".smali"
    target_file = next(temp_dir.rglob(smali_path), None)

    if not target_file:
        raise FileNotFoundError(f"Smali file not found: {smali_path}")

    smali_code = target_file.read_text(encoding='utf-8')
    lib_name = so_path.stem.replace("lib", "")
    
    payload = f'\n    const-string v0, "{lib_name}"\n    invoke-static {{v0}}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V'

    if ".locals 0" in smali_code:
        smali_code = smali_code.replace(".locals 0", ".locals 1")

    pattern = r"(\.method.*onCreate.*(?:\n|.)*?\.locals \d+)"
    if not re.search(pattern, smali_code):
         raise Exception("Could not find onCreate method in Main Activity")
         
    smali_code = re.sub(pattern, f"\\1{payload}", smali_code, count=1)
    target_file.write_text(smali_code, encoding='utf-8')

    print("[*] Recompiling...")

    run_cmd(["apktool", "b", "--use-aapt2", "-o", str(output_apk), str(temp_dir)])

    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    print(f"[+] Success: {output_apk}")
    return str(output_apk)