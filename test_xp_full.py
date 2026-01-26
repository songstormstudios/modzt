import os
import sys
import glob
from pathlib import Path

sys.path.insert(0, 'D:\\Development\\modzt')

CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".zt2_manager")
os.makedirs(CONFIG_DIR, exist_ok=True)

def detect_installed_xps(game_path):
    xps = []
    try:
        if not game_path:
            print("[XP Detection] game_path is empty or None")
            return []
        xp_dir = os.path.join(game_path, "xp")
        print(f"[XP Detection] Looking for XP folder at: {xp_dir}")
        if not os.path.isdir(xp_dir):
            print(f"[XP Detection] XP folder not found: {xp_dir}")
            return []

        print(f"[XP Detection] Found XP folder, scanning contents...")
        
        loose_icons = {}
        expansion_entries = set()
        
        for filename in os.listdir(xp_dir):
            full = os.path.join(xp_dir, filename)
            if os.path.isfile(full) and filename.lower().endswith('_icon.dds'):
                base = filename.rsplit('_icon.dds', 1)[0]
                loose_icons[base] = full
                expansion_entries.add(base)
                print(f"[XP Detection] Found loose icon: {base} -> {filename}")
            elif os.path.isdir(full):
                expansion_entries.add(filename)
            elif filename.lower().endswith('.xp'):
                expansion_entries.add(filename)
        
        print(f"[XP Detection] Found {len(expansion_entries)} expansion entries")
        
        for entry in sorted(expansion_entries):
            full = os.path.join(xp_dir, entry)
            print(f"[XP Detection] Processing entry: {entry}")
            icon = None
            
            if entry in loose_icons:
                icon = loose_icons[entry]
                print(f"[XP Detection] ✓ Using loose icon for {entry}")

            display_name = entry.replace("_", " ")
            xps.append({"id": entry, "name": display_name, "path": full, "icon": icon})
            print(f"[XP Detection] ✓ Added XP: {display_name} (icon: {icon})")
    except Exception as e:
        print(f"[XP Detection] Error during detection: {e}")
        import traceback
        traceback.print_exc()
        return []
    return xps

def test_load_thumbnail(icon_path):
    print(f"\n[Test Load] Testing thumbnail load for: {icon_path}")
    if not os.path.isfile(icon_path):
        print(f"[Test Load] ✗ File not found: {icon_path}")
        return False
    try:
        from PIL import Image
        try:
            import imageio
        except ModuleNotFoundError:
            print("[Test Load] imageio not installed, skipping thumbnail load.")
            return True
        import hashlib

        size = (48, 48)
        cache_dir = os.path.join(CONFIG_DIR, "exp_icons")
        os.makedirs(cache_dir, exist_ok=True)
        key = hashlib.md5(icon_path.encode('utf-8')).hexdigest() + f"_{size[0]}x{size[1]}.png"
        cached = os.path.join(cache_dir, key)
        
        print(f"[Test Load] Cache path: {cached}")
        print(f"[Test Load] Cache exists: {os.path.isfile(cached)}")
        
        if not os.path.isfile(cached):
            print(f"[Test Load] Loading image via imageio...")
            arr = imageio.imread(icon_path)
            print(f"[Test Load] ✓ imageio loaded array shape: {arr.shape}")
            img = Image.fromarray(arr)
            print(f"[Test Load] ✓ Converted to PIL Image")
            img.thumbnail(size, Image.LANCZOS)
            print(f"[Test Load] ✓ Resized to {size}")
            img.save(cached)
            print(f"[Test Load] ✓ Saved cache to: {cached}")
        else:
            print(f"[Test Load] ✓ Using cached thumbnail")
        
        print(f"[Test Load] ✓ SUCCESS - thumbnail loaded")
        return True
    except Exception as e:
        print(f"[Test Load] ✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("XP Icon Detection & Loading Test")
    print("=" * 70)
    
    game_path = "D:/ZT2"
    print(f"\nTesting with game path: {game_path}\n")
    
    xps = detect_installed_xps(game_path)
    print(f"\n✓ Detected {len(xps)} expansions:")
    for xp in xps:
        print(f"  - {xp['name']} (icon: {xp['icon']})")
    
    if xps and xps[0]['icon']:
        print()
        test_load_thumbnail(xps[0]['icon'])
    
    print("\n" + "=" * 70)
