import os
import glob

def test_xp_detection(xp_dir_path):
    print(f"Testing XP detection at: {xp_dir_path}")
    print(f"Path exists: {os.path.isdir(xp_dir_path)}")
    
    if not os.path.isdir(xp_dir_path):
        print("❌ XP folder not found!")
        return
    
    print(f"\nContents of {xp_dir_path}:")
    try:
        entries = os.listdir(xp_dir_path)
        for entry in sorted(entries):
            full = os.path.join(xp_dir_path, entry)
            is_dir = os.path.isdir(full)
            print(f"  {'📁' if is_dir else '📄'} {entry}")
            
            if is_dir:
                print(f"    Contents:")
                try:
                    sub_entries = os.listdir(full)
                    for sub in sorted(sub_entries):
                        sub_full = os.path.join(full, sub)
                        sub_is_dir = os.path.isdir(sub_full)
                        print(f"      {'📁' if sub_is_dir else '📄'} {sub}")
                except Exception as e:
                    print(f"      Error reading: {e}")
                
                print(f"    Images in this folder:")
                for ext in ("*.dds", "*.DDS", "*.png", "*.PNG", "*.bmp", "*.BMP", "*.ico", "*.ICO"):
                    found = glob.glob(os.path.join(full, ext))
                    if found:
                        for f in found:
                            print(f"      ✓ {os.path.basename(f)}")
    except Exception as e:
        print(f"Error listing: {e}")

if __name__ == "__main__":
    test_xp_detection("D:/ZT2/xp")
    print("\n" + "="*60)
    test_xp_detection("C:/Program Files (x86)/Microsoft Games/Zoo Tycoon 2/xp")
