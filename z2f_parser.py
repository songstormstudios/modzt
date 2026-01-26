import os
import zipfile
import json
import shutil
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class Z2FParser:
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.is_valid = self._validate_file()
        
    def _validate_file(self) -> bool:
        """Check if file exists and is a valid zip"""
        if not os.path.exists(self.file_path):
            return False

        if not zipfile.is_zipfile(self.file_path):
            return False

        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                _ = zf.namelist()
            return True
        except (zipfile.BadZipFile, Exception):
            return False
    
    def get_ui_contents(self) -> Optional[Dict[str, str]]:
        if not self.is_valid:
            return None
        
        ui_contents: Dict[str, bytes] = {}
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
            ui_files = [f for f in zf.namelist() if f.lower().startswith('ui/')]
                
                if not ui_files:
                    return None
                
                for file_path in ui_files:
                    if not file_path.endswith('/'):
                        try:
                            ui_contents[file_path] = zf.read(file_path)
                        except Exception:
                            pass
            
            return ui_contents if ui_contents else None
        except Exception as e:
            print(f"Error reading z2f file: {e}")
            return None
    
    def list_ui_files(self) -> List[str]:
        if not self.is_valid:
            return []
        
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                ui_files = [f for f in zf.namelist() if f.lower().startswith('ui/') and not f.endswith('/')]
                return ui_files
        except Exception as e:
            print(f"Error listing z2f files: {e}")
            return []
    
    def extract_ui_to_directory(self, output_dir: str) -> bool:
        if not self.is_valid:
            return False
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                for file_path in zf.namelist():
                    if (file_path.startswith('UI/') or file_path.startswith('ui/')) and not file_path.endswith('/'):
                        extracted = zf.extract(file_path, output_dir)
            
            return True
        except Exception as e:
            print(f"Error extracting UI from z2f: {e}")
            return False
    
    def get_all_contents_flat(self) -> Optional[Dict[str, bytes]]:
        if not self.is_valid:
            return None
        
        contents = {}
        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                for file_info in zf.infolist():
                    if not file_info.is_dir():
                        try:
                            contents[file_info.filename] = zf.read(file_info.filename)
                        except Exception:
                            pass
            return contents
        except Exception as e:
            print(f"Error reading all z2f contents: {e}")
            return None
    
    def replace_ui_folder(self, source_archive: str) -> bool:
        if not self.is_valid:
            return False
        
        source_parser = Z2FParser(source_archive)
        if not source_parser.is_valid:
            return False
        
        try:
            temp_fd, temp_path = tempfile.mkstemp(suffix='.z2f')
            os.close(temp_fd)
            
            with zipfile.ZipFile(self.file_path, 'r') as zf_source:
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zf_temp:
                    for file_info in zf_source.infolist():
                        if not (file_info.filename.startswith('UI/') or file_info.filename.startswith('ui/')):
                            zf_temp.writestr(file_info, zf_source.read(file_info.filename))
            
            with zipfile.ZipFile(source_archive, 'r') as zf_source:
                with zipfile.ZipFile(temp_path, 'a') as zf_temp:
                    for file_info in zf_source.infolist():
                        if (file_info.filename.startswith('UI/') or file_info.filename.startswith('ui/')) and not file_info.is_dir():
                            zf_temp.writestr(file_info, zf_source.read(file_info.filename))
            
            backup_path = self.file_path + '.backup'
            if os.path.exists(backup_path):
                os.remove(backup_path)
            
            shutil.copy2(self.file_path, backup_path)
            shutil.move(temp_path, self.file_path)
            
            return True
        except Exception as e:
            print(f"Error replacing UI in archive: {e}")
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
            return False
    
    def restore_backup(self) -> bool:
        backup_path = self.file_path + '.backup'
        if not os.path.exists(backup_path):
            return False
        
        try:
            shutil.copy2(backup_path, self.file_path)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False


class UIManager:
    
    def __init__(self, zt2_path: str):
        self.zt2_path = zt2_path
        self.ui_base_path = os.path.join(zt2_path, "UI")
        self.ui_backup_path = os.path.join(zt2_path, "UI_Backups")
        self.available_uis: Dict[str, str] = {}
        
        os.makedirs(self.ui_backup_path, exist_ok=True)
        self._scan_available_uis()
    
    def _scan_available_uis(self):
        x300_path = os.path.join(self.zt2_path, "x300_000.z2f")
        
        if os.path.exists(x300_path):
            parser = Z2FParser(x300_path)
            if parser.is_valid:
                ui_files = parser.list_ui_files()
                if ui_files:
                    self.available_uis["Default"] = x300_path
    
    def extract_ui_from_archive(self, archive_path: str, ui_name: str) -> bool:
        parser = Z2FParser(archive_path)
        if not parser.is_valid:
            return False
        
        ui_theme_path = os.path.join(self.ui_base_path, ui_name)
        success = parser.extract_ui_to_directory(ui_theme_path)
        
        if success:
            self.available_uis[ui_name] = archive_path
        
        return success
    
    def backup_current_ui(self, backup_name: str = "backup") -> bool:
        if not os.path.exists(self.ui_base_path):
            return False
        
        backup_path = os.path.join(self.ui_backup_path, backup_name)
        try:
            if os.path.exists(backup_path):
                shutil.rmtree(backup_path)
            shutil.copytree(self.ui_base_path, backup_path)
            return True
        except Exception as e:
            print(f"Error backing up UI: {e}")
            return False
    
    def restore_ui_from_backup(self, backup_name: str = "backup") -> bool:
        backup_path = os.path.join(self.ui_backup_path, backup_name)
        if not os.path.exists(backup_path):
            return False
        
        try:
            self.backup_current_ui("pre_restore")
            
            if os.path.exists(self.ui_base_path):
                shutil.rmtree(self.ui_base_path)
            
            shutil.copytree(backup_path, self.ui_base_path)
            return True
        except Exception as e:
            print(f"Error restoring UI: {e}")
            return False
    
    def switch_ui(self, ui_name: str, source_archive: str = None) -> bool:
        if ui_name not in self.available_uis and not source_archive:
            return False
        
        if source_archive is None:
            source_archive = self.available_uis[ui_name]
        
        x302_path = os.path.join(self.zt2_path, "x302_000.z2f")
        
        if not os.path.exists(x302_path):
            print(f"Error: x302_000.z2f not found at {x302_path}")
            return False
        
        parser = Z2FParser(x302_path)
        if not parser.is_valid:
            print("Error: x302_000.z2f is invalid or corrupted")
            return False
        
        success = parser.replace_ui_folder(source_archive)
        
        return success
    
    def get_available_uis(self) -> List[str]:
        return list(self.available_uis.keys())
    
    def list_all_uis_in_mods(self, mods_path: str) -> Dict[str, str]:
        uis = {}
        
        if not os.path.isdir(mods_path):
            return uis
        
        try:
            for root, dirs, files in os.walk(mods_path):
                for file in files:
                    if file.lower().endswith('.z2f'):
                        file_path = os.path.join(root, file)
                        parser = Z2FParser(file_path)
                        
                        if parser.is_valid:
                            ui_files = parser.list_ui_files()
                            if ui_files:
                                ui_name = os.path.splitext(file)[0]
                                uis[ui_name] = file_path
        except Exception as e:
            print(f"Error scanning mods for UI: {e}")
        
        return uis


class UIThemeExtractor:
    
    @staticmethod
    def extract_x300_ui(x300_path: str, output_dir: str) -> Optional[Dict[str, bytes]]:
        parser = Z2FParser(x300_path)
        if not parser.is_valid:
            return None
        
        success = parser.extract_ui_to_directory(output_dir)
        if success:
            return parser.get_ui_contents()
        
        return None
    
    @staticmethod
    def compare_ui_versions(archive1: str, archive2: str) -> Dict[str, bool]:
        parser1 = Z2FParser(archive1)
        parser2 = Z2FParser(archive2)
        
        if not parser1.is_valid or not parser2.is_valid:
            return {"error": "Invalid archive"}
        
        files1 = set(parser1.list_ui_files())
        files2 = set(parser2.list_ui_files())
        
        return {
            "same_files": files1 == files2,
            "only_in_first": list(files1 - files2),
            "only_in_second": list(files2 - files1),
            "common_files": list(files1 & files2)
        }
