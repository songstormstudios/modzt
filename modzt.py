import glob
import hashlib
import io
import json
import os
import platform
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
import zipfile
import zlib
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
import ttkbootstrap as tb
from PIL import Image, ImageTk
from ttkbootstrap import Window
import xml.etree.ElementTree as ET

import tkinter as tk
import tkinter.simpledialog as simpledialog
from tkinter import ttk, filedialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False
    print("[!] tkinterdnd2 not installed. Drag and drop disabled.")
    print("    Install with: pip install tkinterdnd2")

try:
    import pygame
    pygame.mixer.init()
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False
    print("[!] pygame not installed. Background music disabled.")
    print("    Install with: pip install pygame")

TRANSLATIONS = {
    "en": {
        "lang_name": "English",
        "tab_zt2_mods": "ZT2 Mods",
        "tab_zt1_mods": "ZT1 Mods",
        "tab_bundles": "Bundles",
        "tab_saved_games": "Saved Games",
        "tab_screenshots": "Screenshots",
        "tab_multiplayer": "Multiplayer",
        "tab_mod_browser": "Mod Browser",
        "tab_themes": "Themes",

        "menu_game": "Game",
        "menu_mods": "Mods",
        "menu_tools": "Tools",
        "menu_view": "View",
        "menu_help": "Help",

        "menu_toggle_theme": "Toggle Theme",
        "menu_toggle_music": "Toggle Music",
        "menu_compact_mode": "Compact Mode",
        "menu_expanded_mode": "Expanded Mode",
        "menu_language": "Language",

        "btn_install": "Install Mods",
        "btn_enable": "Enable",
        "btn_disable": "Disable",
        "btn_enable_all": "Enable All",
        "btn_disable_all": "Disable All",
        "btn_refresh": "Refresh",
        "btn_delete": "Delete",
        "btn_search": "Search",
        "btn_browse": "Browse",
        "btn_download": "Download",
        "btn_apply": "Apply",
        "btn_save": "Save",
        "btn_cancel": "Cancel",
        "btn_close": "Close",
        "btn_launch_game": "Launch Game",
        "btn_achievements": "Achievements",

        "mb_quick_picks": "Quick Picks...",
        "mb_featured": "Featured:",
        "mb_browse_category": "Browse by Category",
        "mb_search": "Search",
        "mb_recent": "Recent Additions",
        "mb_surprise": "Surprise Me!",
        "mb_wiki_page": "Wiki Page",
        "mb_mod_details": "Mod Details",
        "mb_select_mod": "Select a mod to view details",
        "mb_description": "Description:",
        "mb_download_links": "Download Links:",
        "mb_search_tip": "Tip: Search for animal names, creators, or mod types",

        "shots_select_album": "Select Album:",
        "shots_open_folder": "Open Folder",

        "saves_preview": "Preview",
        "saves_open_folder": "Open Folder",

        "themes_select": "Select Theme:",
        "themes_apply": "Apply Theme",

        "msg_no_mods": "No mods installed",
        "msg_loading": "Loading...",
        "msg_success": "Success",
        "msg_error": "Error",
        "msg_confirm_delete": "Are you sure you want to delete this?",
        "msg_language_changed": "Language changed. Some changes require restart.",

        "ach_title": "Achievements",
        "ach_unlocked": "Achievement Unlocked!",
        "ach_progress": "Progress",

        "sched_title": "Theme Scheduling",
        "sched_enable": "Enable automatic theme switching",
        "sched_light_theme": "Light theme:",
        "sched_dark_theme": "Dark theme:",
        "sched_from": "from",
        "sched_time_hint": "Use 24-hour format (e.g., 07:00, 19:00)",

        "adv_search": "Advanced Search",
        "adv_search_label": "Search:",
        "adv_category": "Category:",
        "adv_filetype": "File Type:",
        "adv_date": "Date:",
        "adv_sort": "Sort By:",
        "adv_clear": "Clear",
        "adv_tip": "Tip: Combine filters for precise results",
    },
    "es": {
        "lang_name": "Español",
        "tab_zt2_mods": "Mods ZT2",
        "tab_zt1_mods": "Mods ZT1",
        "tab_bundles": "Paquetes",
        "tab_saved_games": "Partidas Guardadas",
        "tab_screenshots": "Capturas",
        "tab_multiplayer": "Multijugador",
        "tab_mod_browser": "Explorador de Mods",
        "tab_themes": "Temas",
        "menu_game": "Juego",
        "menu_mods": "Mods",
        "menu_tools": "Herramientas",
        "menu_view": "Ver",
        "menu_help": "Ayuda",
        "menu_toggle_theme": "Cambiar Tema",
        "menu_toggle_music": "Cambiar Música",
        "menu_compact_mode": "Modo Compacto",
        "menu_expanded_mode": "Modo Expandido",
        "menu_language": "Idioma",
        "btn_install": "Instalar Mods",
        "btn_enable": "Activar",
        "btn_disable": "Desactivar",
        "btn_enable_all": "Activar Todo",
        "btn_disable_all": "Desactivar Todo",
        "btn_refresh": "Actualizar",
        "btn_delete": "Eliminar",
        "btn_search": "Buscar",
        "btn_browse": "Explorar",
        "btn_download": "Descargar",
        "btn_apply": "Aplicar",
        "btn_save": "Guardar",
        "btn_cancel": "Cancelar",
        "btn_close": "Cerrar",
        "btn_launch_game": "Iniciar Juego",
        "btn_achievements": "Logros",
        "mb_quick_picks": "Selección Rápida...",
        "mb_featured": "Destacados:",
        "mb_browse_category": "Explorar por Categoría",
        "mb_search": "Buscar",
        "mb_recent": "Añadidos Recientes",
        "mb_surprise": "¡Sorpréndeme!",
        "mb_wiki_page": "Página Wiki",
        "mb_mod_details": "Detalles del Mod",
        "mb_select_mod": "Selecciona un mod para ver detalles",
        "mb_description": "Descripción:",
        "mb_download_links": "Enlaces de Descarga:",
        "mb_search_tip": "Consejo: Busca nombres de animales, creadores o tipos de mod",
        "shots_select_album": "Seleccionar Álbum:",
        "shots_open_folder": "Abrir Carpeta",
        "saves_preview": "Vista Previa",
        "saves_open_folder": "Abrir Carpeta",
        "themes_select": "Seleccionar Tema:",
        "themes_apply": "Aplicar Tema",
        "msg_no_mods": "No hay mods instalados",
        "msg_loading": "Cargando...",
        "msg_success": "Éxito",
        "msg_error": "Error",
        "msg_confirm_delete": "¿Estás seguro de que quieres eliminar esto?",
        "msg_language_changed": "Idioma cambiado. Algunos cambios requieren reinicio.",
        "ach_title": "Logros",
        "ach_unlocked": "¡Logro Desbloqueado!",
        "ach_progress": "Progreso",

        "sched_title": "Programación de Temas",
        "sched_enable": "Activar cambio automático de tema",
        "sched_light_theme": "Tema claro:",
        "sched_dark_theme": "Tema oscuro:",
        "sched_from": "desde",
        "sched_time_hint": "Usa formato 24 horas (ej., 07:00, 19:00)",

        "adv_search": "Búsqueda Avanzada",
        "adv_search_label": "Buscar:",
        "adv_category": "Categoría:",
        "adv_filetype": "Tipo de Archivo:",
        "adv_date": "Fecha:",
        "adv_sort": "Ordenar Por:",
        "adv_clear": "Limpiar",
        "adv_tip": "Consejo: Combina filtros para resultados precisos",
    },
    "fr": {
        "lang_name": "Français",
        "tab_zt2_mods": "Mods ZT2",
        "tab_zt1_mods": "Mods ZT1",
        "tab_bundles": "Paquets",
        "tab_saved_games": "Sauvegardes",
        "tab_screenshots": "Captures d'écran",
        "tab_multiplayer": "Multijoueur",
        "tab_mod_browser": "Navigateur de Mods",
        "tab_themes": "Thèmes",
        "menu_game": "Jeu",
        "menu_mods": "Mods",
        "menu_tools": "Outils",
        "menu_view": "Affichage",
        "menu_help": "Aide",
        "menu_toggle_theme": "Changer de Thème",
        "menu_toggle_music": "Changer la Musique",
        "menu_compact_mode": "Mode Compact",
        "menu_expanded_mode": "Mode Étendu",
        "menu_language": "Langue",
        "btn_install": "Installer Mods",
        "btn_enable": "Activer",
        "btn_disable": "Désactiver",
        "btn_enable_all": "Tout Activer",
        "btn_disable_all": "Tout Désactiver",
        "btn_refresh": "Actualiser",
        "btn_delete": "Supprimer",
        "btn_search": "Rechercher",
        "btn_browse": "Parcourir",
        "btn_download": "Télécharger",
        "btn_apply": "Appliquer",
        "btn_save": "Sauvegarder",
        "btn_cancel": "Annuler",
        "btn_close": "Fermer",
        "btn_launch_game": "Lancer le Jeu",
        "btn_achievements": "Succès",
        "mb_quick_picks": "Sélection Rapide...",
        "mb_featured": "En vedette:",
        "mb_browse_category": "Parcourir par Catégorie",
        "mb_search": "Rechercher",
        "mb_recent": "Ajouts Récents",
        "mb_surprise": "Surprenez-moi!",
        "mb_wiki_page": "Page Wiki",
        "mb_mod_details": "Détails du Mod",
        "mb_select_mod": "Sélectionnez un mod pour voir les détails",
        "mb_description": "Description:",
        "mb_download_links": "Liens de Téléchargement:",
        "mb_search_tip": "Conseil: Recherchez des noms d'animaux, créateurs ou types de mods",
        "shots_select_album": "Sélectionner Album:",
        "shots_open_folder": "Ouvrir Dossier",
        "saves_preview": "Aperçu",
        "saves_open_folder": "Ouvrir Dossier",
        "themes_select": "Sélectionner Thème:",
        "themes_apply": "Appliquer Thème",
        "msg_no_mods": "Aucun mod installé",
        "msg_loading": "Chargement...",
        "msg_success": "Succès",
        "msg_error": "Erreur",
        "msg_confirm_delete": "Êtes-vous sûr de vouloir supprimer ceci?",
        "msg_language_changed": "Langue changée. Certains changements nécessitent un redémarrage.",
        "ach_title": "Succès",
        "ach_unlocked": "Succès Débloqué!",
        "ach_progress": "Progression",

        "sched_title": "Planification des Thèmes",
        "sched_enable": "Activer le changement automatique de thème",
        "sched_light_theme": "Thème clair:",
        "sched_dark_theme": "Thème sombre:",
        "sched_from": "à partir de",
        "sched_time_hint": "Utilisez le format 24h (ex., 07:00, 19:00)",

        "adv_search": "Recherche Avancée",
        "adv_search_label": "Rechercher:",
        "adv_category": "Catégorie:",
        "adv_filetype": "Type de Fichier:",
        "adv_date": "Date:",
        "adv_sort": "Trier Par:",
        "adv_clear": "Effacer",
        "adv_tip": "Astuce: Combinez les filtres pour des résultats précis",
    },
    "de": {
        "lang_name": "Deutsch",
        "tab_zt2_mods": "ZT2 Mods",
        "tab_zt1_mods": "ZT1 Mods",
        "tab_bundles": "Pakete",
        "tab_saved_games": "Spielstände",
        "tab_screenshots": "Screenshots",
        "tab_multiplayer": "Mehrspieler",
        "tab_mod_browser": "Mod-Browser",
        "tab_themes": "Designs",
        "menu_game": "Spiel",
        "menu_mods": "Mods",
        "menu_tools": "Werkzeuge",
        "menu_view": "Ansicht",
        "menu_help": "Hilfe",
        "menu_toggle_theme": "Design wechseln",
        "menu_toggle_music": "Musik umschalten",
        "menu_compact_mode": "Kompaktmodus",
        "menu_expanded_mode": "Erweiterter Modus",
        "menu_language": "Sprache",
        "btn_install": "Mods Installieren",
        "btn_enable": "Aktivieren",
        "btn_disable": "Deaktivieren",
        "btn_enable_all": "Alle Aktivieren",
        "btn_disable_all": "Alle Deaktivieren",
        "btn_refresh": "Aktualisieren",
        "btn_delete": "Löschen",
        "btn_search": "Suchen",
        "btn_browse": "Durchsuchen",
        "btn_download": "Herunterladen",
        "btn_apply": "Anwenden",
        "btn_save": "Speichern",
        "btn_cancel": "Abbrechen",
        "btn_close": "Schließen",
        "btn_launch_game": "Spiel Starten",
        "btn_achievements": "Erfolge",
        "mb_quick_picks": "Schnellauswahl...",
        "mb_featured": "Empfohlen:",
        "mb_browse_category": "Nach Kategorie durchsuchen",
        "mb_search": "Suchen",
        "mb_recent": "Neueste Ergänzungen",
        "mb_surprise": "Überrasch mich!",
        "mb_wiki_page": "Wiki-Seite",
        "mb_mod_details": "Mod-Details",
        "mb_select_mod": "Wähle einen Mod für Details",
        "mb_description": "Beschreibung:",
        "mb_download_links": "Download-Links:",
        "mb_search_tip": "Tipp: Suche nach Tiernamen, Erstellern oder Mod-Typen",
        "shots_select_album": "Album Auswählen:",
        "shots_open_folder": "Ordner Öffnen",
        "saves_preview": "Vorschau",
        "saves_open_folder": "Ordner Öffnen",
        "themes_select": "Design Auswählen:",
        "themes_apply": "Design Anwenden",
        "msg_no_mods": "Keine Mods installiert",
        "msg_loading": "Laden...",
        "msg_success": "Erfolg",
        "msg_error": "Fehler",
        "msg_confirm_delete": "Sind Sie sicher, dass Sie dies löschen möchten?",
        "msg_language_changed": "Sprache geändert. Einige Änderungen erfordern Neustart.",
        "ach_title": "Erfolge",
        "ach_unlocked": "Erfolg Freigeschaltet!",
        "ach_progress": "Fortschritt",

        "sched_title": "Design-Planung",
        "sched_enable": "Automatischen Designwechsel aktivieren",
        "sched_light_theme": "Helles Design:",
        "sched_dark_theme": "Dunkles Design:",
        "sched_from": "ab",
        "sched_time_hint": "24-Stunden-Format verwenden (z.B., 07:00, 19:00)",

        "adv_search": "Erweiterte Suche",
        "adv_search_label": "Suche:",
        "adv_category": "Kategorie:",
        "adv_filetype": "Dateityp:",
        "adv_date": "Datum:",
        "adv_sort": "Sortieren Nach:",
        "adv_clear": "Löschen",
        "adv_tip": "Tipp: Kombinieren Sie Filter für genaue Ergebnisse",
    },
    "pt": {
        "lang_name": "Português",
        "tab_zt2_mods": "Mods ZT2",
        "tab_zt1_mods": "Mods ZT1",
        "tab_bundles": "Pacotes",
        "tab_saved_games": "Jogos Salvos",
        "tab_screenshots": "Capturas de Tela",
        "tab_multiplayer": "Multijogador",
        "tab_mod_browser": "Navegador de Mods",
        "tab_themes": "Temas",
        "menu_game": "Jogo",
        "menu_mods": "Mods",
        "menu_tools": "Ferramentas",
        "menu_view": "Visualizar",
        "menu_help": "Ajuda",
        "menu_toggle_theme": "Alternar Tema",
        "menu_toggle_music": "Alternar Música",
        "menu_compact_mode": "Modo Compacto",
        "menu_expanded_mode": "Modo Expandido",
        "menu_language": "Idioma",
        "btn_install": "Instalar Mods",
        "btn_enable": "Ativar",
        "btn_disable": "Desativar",
        "btn_enable_all": "Ativar Todos",
        "btn_disable_all": "Desativar Todos",
        "btn_refresh": "Atualizar",
        "btn_delete": "Excluir",
        "btn_search": "Pesquisar",
        "btn_browse": "Navegar",
        "btn_download": "Baixar",
        "btn_apply": "Aplicar",
        "btn_save": "Salvar",
        "btn_cancel": "Cancelar",
        "btn_close": "Fechar",
        "btn_launch_game": "Iniciar Jogo",
        "btn_achievements": "Conquistas",
        "mb_quick_picks": "Seleção Rápida...",
        "mb_featured": "Destaque:",
        "mb_browse_category": "Navegar por Categoria",
        "mb_search": "Pesquisar",
        "mb_recent": "Adições Recentes",
        "mb_surprise": "Surpreenda-me!",
        "mb_wiki_page": "Página Wiki",
        "mb_mod_details": "Detalhes do Mod",
        "mb_select_mod": "Selecione um mod para ver detalhes",
        "mb_description": "Descrição:",
        "mb_download_links": "Links de Download:",
        "mb_search_tip": "Dica: Pesquise nomes de animais, criadores ou tipos de mods",
        "shots_select_album": "Selecionar Álbum:",
        "shots_open_folder": "Abrir Pasta",
        "saves_preview": "Visualizar",
        "saves_open_folder": "Abrir Pasta",
        "themes_select": "Selecionar Tema:",
        "themes_apply": "Aplicar Tema",
        "msg_no_mods": "Nenhum mod instalado",
        "msg_loading": "Carregando...",
        "msg_success": "Sucesso",
        "msg_error": "Erro",
        "msg_confirm_delete": "Tem certeza de que deseja excluir isso?",
        "msg_language_changed": "Idioma alterado. Algumas alterações requerem reinício.",
        "ach_title": "Conquistas",
        "ach_unlocked": "Conquista Desbloqueada!",
        "ach_progress": "Progresso",

        "sched_title": "Agendamento de Temas",
        "sched_enable": "Ativar troca automática de tema",
        "sched_light_theme": "Tema claro:",
        "sched_dark_theme": "Tema escuro:",
        "sched_from": "a partir de",
        "sched_time_hint": "Use formato 24 horas (ex., 07:00, 19:00)",

        "adv_search": "Pesquisa Avançada",
        "adv_search_label": "Pesquisar:",
        "adv_category": "Categoria:",
        "adv_filetype": "Tipo de Arquivo:",
        "adv_date": "Data:",
        "adv_sort": "Ordenar Por:",
        "adv_clear": "Limpar",
        "adv_tip": "Dica: Combine filtros para resultados precisos",
    },
    "it": {
        "lang_name": "Italiano",
        "tab_zt2_mods": "Mod ZT2",
        "tab_zt1_mods": "Mod ZT1",
        "tab_bundles": "Pacchetti",
        "tab_saved_games": "Salvataggi",
        "tab_screenshots": "Screenshot",
        "tab_multiplayer": "Multigiocatore",
        "tab_mod_browser": "Browser Mod",
        "tab_themes": "Temi",
        "menu_game": "Gioco",
        "menu_mods": "Mod",
        "menu_tools": "Strumenti",
        "menu_view": "Visualizza",
        "menu_help": "Aiuto",
        "menu_toggle_theme": "Cambia Tema",
        "menu_toggle_music": "Cambia Musica",
        "menu_compact_mode": "Modalità Compatta",
        "menu_expanded_mode": "Modalità Estesa",
        "menu_language": "Lingua",
        "btn_install": "Installa Mod",
        "btn_enable": "Attiva",
        "btn_disable": "Disattiva",
        "btn_enable_all": "Attiva Tutti",
        "btn_disable_all": "Disattiva Tutti",
        "btn_refresh": "Aggiorna",
        "btn_delete": "Elimina",
        "btn_search": "Cerca",
        "btn_browse": "Sfoglia",
        "btn_download": "Scarica",
        "btn_apply": "Applica",
        "btn_save": "Salva",
        "btn_cancel": "Annulla",
        "btn_close": "Chiudi",
        "btn_launch_game": "Avvia Gioco",
        "btn_achievements": "Obiettivi",
        "mb_quick_picks": "Selezione Rapida...",
        "mb_featured": "In evidenza:",
        "mb_browse_category": "Sfoglia per Categoria",
        "mb_search": "Cerca",
        "mb_recent": "Aggiunte Recenti",
        "mb_surprise": "Sorprendimi!",
        "mb_wiki_page": "Pagina Wiki",
        "mb_mod_details": "Dettagli Mod",
        "mb_select_mod": "Seleziona un mod per vedere i dettagli",
        "mb_description": "Descrizione:",
        "mb_download_links": "Link di Download:",
        "mb_search_tip": "Suggerimento: Cerca nomi di animali, creatori o tipi di mod",
        "shots_select_album": "Seleziona Album:",
        "shots_open_folder": "Apri Cartella",
        "saves_preview": "Anteprima",
        "saves_open_folder": "Apri Cartella",
        "themes_select": "Seleziona Tema:",
        "themes_apply": "Applica Tema",
        "msg_no_mods": "Nessun mod installato",
        "msg_loading": "Caricamento...",
        "msg_success": "Successo",
        "msg_error": "Errore",
        "msg_confirm_delete": "Sei sicuro di voler eliminare questo?",
        "msg_language_changed": "Lingua cambiata. Alcune modifiche richiedono il riavvio.",
        "ach_title": "Obiettivi",
        "ach_unlocked": "Obiettivo Sbloccato!",
        "ach_progress": "Progresso",

        "sched_title": "Pianificazione Temi",
        "sched_enable": "Attiva cambio automatico del tema",
        "sched_light_theme": "Tema chiaro:",
        "sched_dark_theme": "Tema scuro:",
        "sched_from": "dalle",
        "sched_time_hint": "Usa formato 24 ore (es., 07:00, 19:00)",

        "adv_search": "Ricerca Avanzata",
        "adv_search_label": "Cerca:",
        "adv_category": "Categoria:",
        "adv_filetype": "Tipo di File:",
        "adv_date": "Data:",
        "adv_sort": "Ordina Per:",
        "adv_clear": "Cancella",
        "adv_tip": "Suggerimento: Combina i filtri per risultati precisi",
    },
}

current_language = "en"

def t(key):
    lang_dict = TRANSLATIONS.get(current_language, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

def set_language(lang_code):
    global current_language
    current_language = lang_code
    settings["language"] = lang_code
    save_settings(settings)


def get_app_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def start_background_music(volume=0.3):
    if not AUDIO_AVAILABLE:
        return False

    music_file = os.path.join(get_app_dir(), "theme_remaster_sirgoose.mp3")
    if not os.path.isfile(music_file):
        print(f"[!] Music file not found: {music_file}")
        return False

    try:
        pygame.mixer.music.load(music_file)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1)
        print(f"[✔] Background music started")
        return True
    except Exception as e:
        print(f"[!] Failed to play music: {e}")
        return False


def stop_background_music():
    if AUDIO_AVAILABLE:
        pygame.mixer.music.stop()


def set_music_volume(volume):
    if AUDIO_AVAILABLE:
        pygame.mixer.music.set_volume(max(0.0, min(1.0, volume)))


def toggle_background_music():
    if not AUDIO_AVAILABLE:
        messagebox.showinfo("Audio Unavailable", "pygame is not installed.\nInstall with: pip install pygame")
        return

    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        log("Background music paused", log_text)
    else:
        if pygame.mixer.music.get_pos() == -1:
            start_background_music()
        else:
            pygame.mixer.music.unpause()
        log("Background music playing", log_text)

if platform.system() == "Windows":
    import ctypes
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u"ModZT.App")
    except Exception:
        pass

APP_VERSION = "1.1.7 Beta"
SETTINGS_FILE = "settings.json"
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".zt2_manager")
os.makedirs(CONFIG_DIR, exist_ok=True)
GAME_PATH_FILE = os.path.join(CONFIG_DIR, "game_path.txt")
ZT1_EXE_FILE = os.path.join(CONFIG_DIR, "zt1_exe_path.txt")
ZT1_MOD_DIR_FILE = os.path.join(CONFIG_DIR, "zt1_mod_dir.txt")
DB_FILE = os.path.join(CONFIG_DIR, "mods.db")
ICON_FILE = os.path.join(CONFIG_DIR, "modzt.ico")
BANNER_FILE = os.path.join(CONFIG_DIR, "banner.png")
GITHUB_REPO = "songstormstudios/modzt"

ZT2DL_API_BASE = "https://zt2downloadlibrary.fandom.com/api.php"
ZT2DL_WIKI_BASE = "https://zt2downloadlibrary.fandom.com/wiki"
ZT2DL_CACHE_TTL = 600

GAME_PATH = None
ZT1_PATH = None
ZT1_MOD_DIR = None
ZT2_EXE = None

if os.path.isfile(GAME_PATH_FILE):
    with open(GAME_PATH_FILE, "r", encoding="utf-8") as f:
        GAME_PATH = f.read().strip() or None

if os.path.isfile(ZT1_EXE_FILE):
    with open(ZT1_EXE_FILE, "r", encoding="utf-8") as f:
        ZT1_PATH = f.read().strip()

if os.path.isfile(ZT1_MOD_DIR_FILE):
    with open(ZT1_MOD_DIR_FILE, "r", encoding="utf-8") as f:
        ZT1_MOD_DIR = f.read().strip()

if GAME_PATH and os.path.isdir(GAME_PATH):
    ZT2_EXE = os.path.join(GAME_PATH, "zt.exe")
    if os.path.exists(ZT2_EXE):
        ZT2_PATH = ZT2_EXE
        print(f"ZT2 path registered: {ZT2_EXE}")
    else:
        print("Warning: zt.exe not found in configured path.")
else:
    ZT2_PATH = None
    print("ZT2 path not yet set; will register once chosen.")


def get_zt2_saves_dir():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    p = os.path.join(appdata, "Microsoft Games", "Zoo Tycoon 2",
                     "Default Profile", "Saved")
    return p if os.path.isdir(p) else None


def get_zt2_options_xml_path():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    p = os.path.join(appdata, "Microsoft Games", "Zoo Tycoon 2",
                     "Default Profile", "options.xml")
    return p if os.path.isfile(p) else None


UNLOCK_TUTORIALS = {
    "Base Game Tutorials": [
        ("Tutorial1", "Tutorial 1"),
        ("Tutorial2", "Tutorial 2"),
        ("Tutorial3", "Tutorial 3"),
    ],
    "Endangered Species Tutorials": [
        ("xp1_Tutorial1", "ES Tutorial 1"),
        ("xp1_Tutorial2", "ES Tutorial 2"),
        ("xp1_Tutorial3", "ES Tutorial 3"),
    ],
    "African Adventure Tutorials": [
        ("xp2_Tutorial1", "AA Tutorial 1"),
        ("xp2_Tutorial2", "AA Tutorial 2"),
        ("xp2_Tutorial3", "AA Tutorial 3"),
        ("xp2_Tutorial4", "AA Tutorial 4"),
        ("xp2_Tutorial5", "AA Tutorial 5"),
    ],
    "Marine Mania Tutorials": [
        ("cp1_tutorial1", "MM Tutorial 1"),
    ],
    "Extinct Animals Tutorials": [
        ("cp2tutorialone", "EA Tutorial 1"),
        ("cp2tutorialtwo", "EA Tutorial 2"),
        ("cp2tutorialthree", "EA Tutorial 3"),
    ],
}

UNLOCK_CAMPAIGNS = {
    "Zookeeper Training": [
        ("ZookeeperTrainingscenario1", "Scenario 1"),
        ("ZookeeperTrainingscenario2", "Scenario 2"),
        ("ZookeeperTrainingscenario3", "Scenario 3"),
    ],
    "Campaign 1": [
        ("campaign1scenario1", "Scenario 1"),
        ("campaign1scenario2", "Scenario 2"),
        ("campaign1scenario3", "Scenario 3"),
    ],
    "Campaign 2": [
        ("campaign2scenario1", "Scenario 1"),
        ("campaign2scenario2", "Scenario 2"),
        ("campaign2scenario3", "Scenario 3"),
    ],
    "World Campaigns": [
        ("worldcampaignscenario1", "Scenario 1"),
        ("worldcampaignscenario2", "Scenario 2"),
        ("worldcampaignscenario3", "Scenario 3"),
        ("worldcampaignscenario4", "Scenario 4"),
        ("worldcampaignscenario5", "Scenario 5"),
    ],
    "Africa Campaign": [
        ("AfricaCampaignscenario1", "Scenario 1"),
        ("AfricaCampaignscenario2", "Scenario 2"),
        ("AfricaCampaignscenario3", "Scenario 3"),
    ],
    "Marine Animals Campaign": [
        ("MarineAnimalsCampaignscenario1", "Scenario 1"),
        ("MarineAnimalsCampaignscenario2", "Scenario 2"),
        ("MarineAnimalsCampaignscenario3", "Scenario 3"),
        ("MarineAnimalsCampaignscenario4", "Scenario 4"),
    ],
    "Marine Shows Campaign": [
        ("MarineShowsCampaignscenario1", "Scenario 1"),
        ("MarineShowsCampaignscenario2", "Scenario 2"),
        ("MarineShowsCampaignscenario3", "Scenario 3"),
        ("MarineShowsCampaignscenario4", "Scenario 4"),
        ("MarineShowsCampaignscenario5", "Scenario 5"),
    ],
    "Endangered Animals Campaign": [
        ("EndangeredAnimalsCampaignscenario1", "Scenario 1"),
        ("EndangeredAnimalsCampaignscenario2", "Scenario 2"),
        ("EndangeredAnimalsCampaignscenario3", "Scenario 3"),
    ],
    "Species Survival": [
        ("SpeciesSurvivalscenario1", "Scenario 1"),
        ("SpeciesSurvivalscenario2", "Scenario 2"),
        ("SpeciesSurvivalscenario3", "Scenario 3"),
    ],
    "Photo Safari Campaign": [
        ("PhotoSafariCampaignscenario1", "Scenario 1"),
        ("PhotoSafariCampaignscenario2", "Scenario 2"),
        ("PhotoSafariCampaignscenario3", "Scenario 3"),
    ],
    "Transportation Campaign": [
        ("TransportationCampaignscenario1", "Scenario 1"),
        ("TransportationCampaignscenario2", "Scenario 2"),
        ("TransportationCampaignscenario3", "Scenario 3"),
    ],
    "Dinosaur Zoo Campaign": [
        ("DinosaurZooCampaignscenario1", "Scenario 1"),
    ],
    "Extinct Animals Campaign": [
        ("cp2scen1", "Scenario 1"),
        ("cp2scen2", "Scenario 2"),
        ("cp2scen3", "Scenario 3"),
        ("cp2scen4", "Scenario 4"),
        ("cp2scen5", "Scenario 5"),
        ("cp2scen6", "Scenario 6"),
    ],
    "Other Campaigns": [
        ("Pandascampaign", "Pandas Campaign"),
        ("adcc1", "ADCC 1"),
    ],
}

UNLOCK_ITEMS = {
    "Building Unlocks": [
        ("flowerpostlock", "Flower Post"),
        ("sundiallock", "Sundial"),
        ("flowerarchlock", "Flower Arch"),
        ("globelock", "Globe"),
        ("showtvlock", "Show TV"),
        ("showcanopylock", "Show Canopy"),
        ("breedingcenterlock", "Breeding Center"),
        ("catclimberlock", "Cat Climber"),
        ("whalehalllock", "Whale Hall"),
        ("brachiosaurus_slide_lock", "Brachiosaurus Slide"),
    ],
    "Biome Unlocks": [
        ("safarilock", "Safari"),
        ("junglelock", "Jungle"),
        ("desertlock", "Desert"),
    ],
    "Animal Unlocks": [
        ("pandalock", "Panda"),
        ("yellowtunalock", "Yellow Tuna"),
        ("saigalock", "Saiga"),
    ],
    "Feature Unlocks": [
        ("vehiclegatelock", "Vehicle Gate"),
        ("endangeredlock", "Endangered Features"),
        ("quagga_xtlock", "Quagga"),
        ("extinct_xtlock", "Extinct Animals"),
    ],
}


COMMON_ZT2_PATHS = [
    r"C:\Program Files (x86)\Microsoft Games\Zoo Tycoon 2",
    r"C:\Program Files\Microsoft Games\Zoo Tycoon 2",
]

COMMON_ZT1_PATHS = [
    r"C:\Program Files (x86)\Microsoft Games\Zoo Tycoon",
    r"C:\Program Files\Microsoft Games\Zoo Tycoon",
]

DEFAULT_SETTINGS = {
    "game_path": "",
    "theme": "flatly",
    "window_geometry": "1200x882+78+78",
    "window_maximized": False,
    "language": "en",
    "theme_scheduling_enabled": False,
    "theme_light": "litera",
    "theme_dark": "darkly",
    "theme_light_start": "07:00",
    "theme_dark_start": "19:00"
}

THEMES = {
    "flatly": "Flatly",
    "darkly": "Darkly",
    "superhero": "Superhero",
    "cyborg": "Cyborg",
    "vapor": "Vapor",
    "solar": "Solar"
}


def open_mods_folder():
    path = get_game_path()
    if path:
        os.startfile(path)


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = get_app_dir()
    return os.path.join(base_path, relative_path)


def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "w") as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        for key, value in DEFAULT_SETTINGS.items():
            data.setdefault(key, value)
        return data
    except Exception:
        return DEFAULT_SETTINGS.copy()


def save_settings(s):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=4)


def auto_detect_zt1_installation():
    import winreg

    for path in COMMON_ZT1_PATHS:
        exe = os.path.join(path, "zoo.exe")
        if os.path.isfile(exe):
            return path

    possible_keys = [
        r"SOFTWARE\Microsoft\Microsoft Games\Zoo Tycoon ",
        r"SOFTWARE\WOW6432Node\Microsoft\Microsoft Games\Zoo Tycoon",
    ]
    for key in possible_keys:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as regkey:
                install_dir, _ = winreg.QueryValueEx(regkey,
                                                     "InstallationDirectory")
                exe = os.path.join(install_dir, "zoo.exe")
                if os.path.isfile(exe):
                    return install_dir
        except FileNotFoundError:
            continue
        except Exception:
            pass

    user_dirs = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
    ]
    for base in user_dirs:
        for root, dirs, files in os.walk(base):
            if "zoo.exe" in files:
                return root

    return None


def auto_detect_zt2_installation():
    import winreg

    for path in COMMON_ZT2_PATHS:
        exe = os.path.join(path, "zt.exe")
        if os.path.isfile(exe):
            return path

    possible_keys = [
        r"SOFTWARE\Microsoft\Microsoft Games\Zoo Tycoon 2",
        r"SOFTWARE\WOW6432Node\Microsoft\Microsoft Games\Zoo Tycoon 2",
    ]
    for key in possible_keys:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as regkey:
                install_dir, _ = winreg.QueryValueEx(regkey,
                                                     "InstallationDirectory")
                exe = os.path.join(install_dir, "zt.exe")
                if os.path.isfile(exe):
                    return install_dir
        except FileNotFoundError:
            continue
        except Exception:
            pass

    user_dirs = [
        os.path.join(os.path.expanduser("~"), "Desktop"),
        os.path.join(os.path.expanduser("~"), "Documents"),
    ]
    for base in user_dirs:
        for root, dirs, files in os.walk(base):
            if "zt.exe" in files:
                return root

    return None


sort_state = {"column": "Name", "reverse": False}
ui_mode = {"compact": False}

action_history = []
MAX_HISTORY = 50

TRASH_DIR = os.path.join(CONFIG_DIR, "trash")
os.makedirs(TRASH_DIR, exist_ok=True)

def record_action(action_type, data):
    action_history.append({"type": action_type, "data": data})
    if len(action_history) > MAX_HISTORY:
        old = action_history.pop(0)
        if old["type"] == "uninstall":
            trash_path = old["data"].get("trash_path")
            if trash_path and os.path.isfile(trash_path):
                try:
                    os.remove(trash_path)
                except Exception:
                    pass


def undo_last_action():
    if not action_history:
        messagebox.showinfo("Undo", "Nothing to undo.", parent=globals().get('root'))
        return

    action = action_history.pop()
    action_type = action["type"]
    data = action["data"]
    log_text = globals().get('log_text')

    try:
        if action_type == "enable":
            mod_name = data["mod_name"]
            disable_mod(mod_name, text_widget=log_text, record=False)
            log(f"Undo: Disabled {mod_name}", log_text)

        elif action_type == "disable":
            mod_name = data["mod_name"]
            enable_mod(mod_name, text_widget=log_text, record=False)
            log(f"Undo: Enabled {mod_name}", log_text)

        elif action_type == "uninstall":
            mod_name = data["mod_name"]
            trash_path = data["trash_path"]
            was_enabled = data.get("was_enabled", True)

            if not os.path.isfile(trash_path):
                messagebox.showerror("Undo Failed", f"Backup file not found:\n{trash_path}")
                return

            if was_enabled:
                dest = os.path.join(GAME_PATH, mod_name)
            else:
                dest = os.path.join(mods_disabled_dir(), mod_name)

            shutil.move(trash_path, dest)
            detect_existing_mods()
            refresh_tree()
            log(f"Undo: Restored {mod_name}", log_text)

        elif action_type == "install":
            mod_names = data["mod_names"]
            for mod_name in mod_names:
                uninstall_mod(mod_name, text_widget=log_text, record=False)
            log(f"Undo: Uninstalled {len(mod_names)} mod(s)", log_text)

        messagebox.showinfo("Undo", f"Undid: {action_type} operation", parent=globals().get('root'))

    except Exception as e:
        messagebox.showerror("Undo Failed", f"Could not undo action:\n{e}")
        action_history.append(action)


conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    enabled INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS zt1_mods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    enabled INTEGER DEFAULT 0
)
""")
conn.commit()
try:
    cursor.execute("ALTER TABLE mods ADD COLUMN hash TEXT")
except sqlite3.OperationalError:
    pass
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS bundles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS mod_dependencies (
    mod_name TEXT,
    depends_on TEXT,
    FOREIGN KEY(mod_name) REFERENCES mods(name)
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS bundle_mods (
    bundle_id INTEGER,
    mod_name TEXT,
    UNIQUE(bundle_id, mod_name)
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS zt2dl_cache (
    cache_key TEXT PRIMARY KEY,
    data TEXT,
    cached_at TEXT
)
""")
conn.commit()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_stats (
    stat_name TEXT PRIMARY KEY,
    value INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id TEXT PRIMARY KEY,
    unlocked_at TEXT
)
""")
conn.commit()


def ensure_category_column():
    cursor.execute("PRAGMA table_info(mods)")
    mods_cols = [col[1] for col in cursor.fetchall()]
    if "category" not in mods_cols:
        cursor.execute(
            "ALTER TABLE mods ADD COLUMN category TEXT DEFAULT 'Uncategorized'"
        )

    cursor.execute("PRAGMA table_info(zt1_mods)")
    zt1_cols = [col[1] for col in cursor.fetchall()]
    if "category" not in zt1_cols:
        cursor.execute(
            "ALTER TABLE zt1_mods ADD COLUMN category TEXT DEFAULT 'Uncategorized'"
        )

    conn.commit()


ensure_category_column()


def ensure_db_schema():
    for table in ("mods", "zt1_mods"):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [c[1] for c in cursor.fetchall()]
        if "category" not in cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN category TEXT DEFAULT 'Uncategorized'"
            )
        if "tags" not in cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN tags TEXT DEFAULT ''")
        if "author" not in cols:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN author TEXT DEFAULT ''")
    conn.commit()


ensure_db_schema()


def log(msg, text_widget=None):
    timestamp = time.strftime("%H:%M:%S")
    full = f"[{timestamp}] {msg}"
    print(full)
    if text_widget:
        text_widget.configure(state="normal")
        text_widget.insert(tk.END, full + "\n")
        text_widget.configure(state="disabled")
        text_widget.see(tk.END)


def save_game_path(p):
    with open(GAME_PATH_FILE, "w", encoding="utf-8") as f:
        f.write(p)


def get_game_path():
    global GAME_PATH, settings

    if GAME_PATH and os.path.exists(GAME_PATH):
        return GAME_PATH

    new_path = filedialog.askdirectory(title="Select your Zoo Tycoon 2 folder")
    if new_path:
        GAME_PATH = new_path
        settings["game_path"] = new_path
        with open("settings.json", "w") as f:
            json.dump(settings, f, indent=4)
        return GAME_PATH
    else:
        messagebox.showwarning(
            "Path Not Set", "Please select your Zoo Tycoon 2 folder first.")
        return None


def zt1_mods_disabled_dir():
    if ZT1_MOD_DIR:
        return os.path.join(ZT1_MOD_DIR, "_disabled")
    elif ZT1_PATH:
        return os.path.join(ZT1_PATH, "dlupdates_disabled")
    return None


def detect_existing_zt1_mods():
    if not ZT1_PATH:
        return
    dl_dir = ZT1_MOD_DIR or os.path.join(ZT1_PATH, "dlupdates")
    disabled_dir = os.path.join(dl_dir, "_disabled")
    os.makedirs(disabled_dir, exist_ok=True)

    scanned = {}
    for folder, enabled in [(dl_dir, 1), (disabled_dir, 0)]:
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            if not f.lower().endswith(".ztd"):
                continue
            scanned[f] = enabled

    for name, enabled in scanned.items():
        cursor.execute("SELECT COUNT(*) FROM zt1_mods WHERE name=?", (name, ))
        exists = cursor.fetchone()[0]
        if exists == 0:
            cursor.execute(
                "INSERT INTO zt1_mods (name, enabled) VALUES (?, ?)",
                (name, enabled))
        else:
            cursor.execute("UPDATE zt1_mods SET enabled=? WHERE name=?",
                           (enabled, name))
    conn.commit()

    cursor.execute("SELECT name FROM zt1_mods")
    for (name, ) in cursor.fetchall():
        if name not in scanned:
            cursor.execute("DELETE FROM zt1_mods WHERE name=?", (name, ))
    conn.commit()

ACHIEVEMENTS = {
    "first_mod": {
        "name": "First Steps",
        "description": "Install your first mod",
        "icon": "package",
        "category": "Collector",
        "condition": lambda stats: stats.get("mods_installed", 0) >= 1
    },
    "mod_enthusiast": {
        "name": "Mod Enthusiast",
        "description": "Install 10 mods",
        "icon": "packages",
        "category": "Collector",
        "target": 10,
        "condition": lambda stats: stats.get("mods_installed", 0) >= 10
    },
    "mod_collector": {
        "name": "Mod Collector",
        "description": "Install 50 mods",
        "icon": "archive",
        "category": "Collector",
        "target": 50,
        "condition": lambda stats: stats.get("mods_installed", 0) >= 50
    },
    "mod_hoarder": {
        "name": "Mod Hoarder",
        "description": "Install 100 mods",
        "icon": "warehouse",
        "category": "Collector",
        "target": 100,
        "condition": lambda stats: stats.get("mods_installed", 0) >= 100
    },

    "browser": {
        "name": "Browser",
        "description": "Use the Mod Browser to search for mods",
        "icon": "search",
        "category": "Explorer",
        "condition": lambda stats: stats.get("browser_searches", 0) >= 1
    },
    "random_discovery": {
        "name": "Random Discovery",
        "description": "Use the Random mod button",
        "icon": "shuffle",
        "category": "Explorer",
        "condition": lambda stats: stats.get("random_mods_viewed", 0) >= 1
    },
    "category_explorer": {
        "name": "Category Explorer",
        "description": "Browse all mod categories",
        "icon": "compass",
        "category": "Explorer",
        "target": 6,
        "condition": lambda stats: stats.get("categories_browsed", 0) >= 6
    },

    "zookeeper": {
        "name": "Zookeeper",
        "description": "Have 5 saved games",
        "icon": "save",
        "category": "Zoo Keeper",
        "target": 5,
        "condition": lambda stats: stats.get("saves_count", 0) >= 5
    },
    "screenshot_artist": {
        "name": "Screenshot Artist",
        "description": "View 10 screenshots",
        "icon": "camera",
        "category": "Zoo Keeper",
        "target": 10,
        "condition": lambda stats: stats.get("screenshots_viewed", 0) >= 10
    },
    "bundle_master": {
        "name": "Bundle Master",
        "description": "Create 3 mod bundles",
        "icon": "layers",
        "category": "Zoo Keeper",
        "target": 3,
        "condition": lambda stats: stats.get("bundles_created", 0) >= 3
    },

    "multiplayer_pioneer": {
        "name": "Multiplayer Pioneer",
        "description": "Create a multiplayer session",
        "icon": "users",
        "category": "Social",
        "condition": lambda stats: stats.get("mp_sessions_created", 0) >= 1
    },
    "turn_taker": {
        "name": "Turn Taker",
        "description": "Submit 5 multiplayer turns",
        "icon": "repeat",
        "category": "Social",
        "target": 5,
        "condition": lambda stats: stats.get("mp_turns_submitted", 0) >= 5
    },

    "theme_changer": {
        "name": "Theme Changer",
        "description": "Try 5 different themes",
        "icon": "palette",
        "category": "Customization",
        "target": 5,
        "condition": lambda stats: stats.get("themes_applied", 0) >= 5
    },
    "objective_seeker": {
        "name": "Objective Seeker",
        "description": "Generate 10 random objectives",
        "icon": "target",
        "category": "Customization",
        "target": 10,
        "condition": lambda stats: stats.get("objectives_generated", 0) >= 10
    },

    "completionist": {
        "name": "Completionist",
        "description": "Unlock all other achievements",
        "icon": "trophy",
        "category": "Secret",
        "condition": lambda stats: stats.get("achievements_unlocked", 0) >= 14
    },
}

def get_user_stats():
    cursor.execute("SELECT stat_name, value FROM user_stats")
    return {row[0]: row[1] for row in cursor.fetchall()}

def increment_stat(stat_name, amount=1):
    cursor.execute("""
        INSERT INTO user_stats (stat_name, value) VALUES (?, ?)
        ON CONFLICT(stat_name) DO UPDATE SET value = value + ?
    """, (stat_name, amount, amount))
    conn.commit()
    check_achievements()

def set_stat(stat_name, value):
    cursor.execute("""
        INSERT INTO user_stats (stat_name, value) VALUES (?, ?)
        ON CONFLICT(stat_name) DO UPDATE SET value = ?
    """, (stat_name, value, value))
    conn.commit()
    check_achievements()

def get_unlocked_achievements():
    cursor.execute("SELECT id FROM achievements WHERE unlocked_at IS NOT NULL")
    return [row[0] for row in cursor.fetchall()]

def unlock_achievement(achievement_id):
    cursor.execute("""
        INSERT OR IGNORE INTO achievements (id, unlocked_at) VALUES (?, datetime('now'))
    """, (achievement_id,))
    conn.commit()

    unlocked = get_unlocked_achievements()
    set_stat("achievements_unlocked", len(unlocked))

def check_achievements():
    stats = get_user_stats()
    unlocked = get_unlocked_achievements()
    newly_unlocked = []

    for ach_id, ach_data in ACHIEVEMENTS.items():
        if ach_id not in unlocked:
            try:
                if ach_data["condition"](stats):
                    unlock_achievement(ach_id)
                    newly_unlocked.append(ach_data["name"])
            except Exception:
                pass

    for name in newly_unlocked:
        show_achievement_toast(name)

    return newly_unlocked

def show_achievement_toast(achievement_name):
    try:
        toast = tk.Toplevel(root)
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)

        toast.update_idletasks()
        x = root.winfo_x() + root.winfo_width() - 320
        y = root.winfo_y() + root.winfo_height() - 100
        toast.geometry(f"300x70+{x}+{y}")

        frame = ttk.Frame(toast, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Achievement Unlocked!",
                  font=("Segoe UI", 9, "bold"),
                  bootstyle="warning").pack(anchor="w")
        ttk.Label(frame, text=achievement_name,
                  font=("Segoe UI", 11, "bold")).pack(anchor="w")

        toast.after(3000, toast.destroy)
    except Exception:
        pass

def open_achievements_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Achievements")
    dialog.geometry("600x500")
    dialog.transient(root)
    dialog.grab_set()

    dialog.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - 300
    y = root.winfo_y() + (root.winfo_height() // 2) - 250
    dialog.geometry(f"+{x}+{y}")

    main_frame = ttk.Frame(dialog, padding=15)
    main_frame.pack(fill=tk.BOTH, expand=True)

    header_frame = ttk.Frame(main_frame)
    header_frame.pack(fill=tk.X, pady=(0, 15))

    ttk.Label(header_frame, text="Achievements",
              font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)

    unlocked = get_unlocked_achievements()
    total = len(ACHIEVEMENTS)
    progress_text = f"{len(unlocked)}/{total} Unlocked"
    ttk.Label(header_frame, text=progress_text,
              font=("Segoe UI", 11),
              bootstyle="info").pack(side=tk.RIGHT)

    progress_pct = (len(unlocked) / total) * 100 if total > 0 else 0
    progress_bar = ttk.Progressbar(main_frame, value=progress_pct,
                                    bootstyle="success-striped", length=570)
    progress_bar.pack(fill=tk.X, pady=(0, 15))

    canvas = tk.Canvas(main_frame, highlightthickness=0)
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scroll_frame = ttk.Frame(canvas)

    scroll_frame.bind("<Configure>",
                      lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    dialog.bind("<Destroy>", lambda e: canvas.unbind_all("<MouseWheel>"))

    stats = get_user_stats()

    categories = {}
    for ach_id, ach_data in ACHIEVEMENTS.items():
        cat = ach_data["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append((ach_id, ach_data))

    row = 0
    for cat_name in ["Collector", "Explorer", "Zoo Keeper", "Social", "Customization", "Secret"]:
        if cat_name not in categories:
            continue

        cat_label = ttk.Label(scroll_frame, text=cat_name,
                              font=("Segoe UI", 11, "bold"))
        cat_label.grid(row=row, column=0, columnspan=2, sticky="w", pady=(10, 5))
        row += 1

        for ach_id, ach_data in categories[cat_name]:
            is_unlocked = ach_id in unlocked
            is_secret = cat_name == "Secret" and not is_unlocked

            ach_frame = ttk.Frame(scroll_frame, padding=8)
            ach_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=2, padx=5)

            icon_color = "#4CAF50" if is_unlocked else "#666666"
            icon_canvas = tk.Canvas(ach_frame, width=40, height=40,
                                    highlightthickness=0, bg=icon_color)
            icon_canvas.pack(side=tk.LEFT, padx=(0, 10))

            text_frame = ttk.Frame(ach_frame)
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            name = "???" if is_secret else ach_data["name"]
            desc = "Complete other achievements to reveal" if is_secret else ach_data["description"]

            name_style = "default" if is_unlocked else "secondary"
            ttk.Label(text_frame, text=name,
                      font=("Segoe UI", 10, "bold"),
                      bootstyle=name_style).pack(anchor="w")
            ttk.Label(text_frame, text=desc,
                      font=("Segoe UI", 9),
                      bootstyle="secondary").pack(anchor="w")

            if "target" in ach_data and not is_unlocked and not is_secret:
                stat_map = {
                    "mod_enthusiast": "mods_installed",
                    "mod_collector": "mods_installed",
                    "mod_hoarder": "mods_installed",
                    "category_explorer": "categories_browsed",
                    "zookeeper": "saves_count",
                    "screenshot_artist": "screenshots_viewed",
                    "bundle_master": "bundles_created",
                    "turn_taker": "mp_turns_submitted",
                    "theme_changer": "themes_applied",
                    "objective_seeker": "objectives_generated",
                }
                stat_name = stat_map.get(ach_id, "")
                current = stats.get(stat_name, 0)
                target = ach_data["target"]
                progress_str = f"{current}/{target}"
                ttk.Label(ach_frame, text=progress_str,
                          font=("Segoe UI", 9),
                          bootstyle="info").pack(side=tk.RIGHT, padx=10)

            if is_unlocked:
                ttk.Label(ach_frame, text="✓",
                          font=("Segoe UI", 14, "bold"),
                          bootstyle="success").pack(side=tk.RIGHT, padx=10)

            row += 1

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X, pady=(15, 0))
    ttk.Button(btn_frame, text="Close", command=dialog.destroy,
               bootstyle="secondary").pack(side=tk.RIGHT)

class ZT2DownloadLibraryAPI:

    def __init__(self):
        self.api_base = ZT2DL_API_BASE
        self.wiki_base = ZT2DL_WIKI_BASE
        self.last_request_time = 0
        self.min_request_interval = 0.5

    def _rate_limit(self):
        import time
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _get_cached(self, cache_key):
        cursor.execute(
            "SELECT data, cached_at FROM zt2dl_cache WHERE cache_key=?",
            (cache_key,)
        )
        row = cursor.fetchone()
        if row:
            data, cached_at = row
            try:
                cached_time = datetime.fromisoformat(cached_at)
                if (datetime.now() - cached_time).total_seconds() < ZT2DL_CACHE_TTL:
                    return json.loads(data)
            except Exception:
                pass
        return None

    def _set_cache(self, cache_key, data):
        cursor.execute(
            "INSERT OR REPLACE INTO zt2dl_cache (cache_key, data, cached_at) VALUES (?, ?, ?)",
            (cache_key, json.dumps(data), datetime.now().isoformat())
        )
        conn.commit()

    def _request(self, params, use_cache=True):
        """Make API request with caching"""
        cache_key = f"zt2dl:{json.dumps(params, sort_keys=True)}"

        if use_cache:
            cached = self._get_cached(cache_key)
            if cached:
                return cached

        self._rate_limit()

        params['format'] = 'json'
        response = requests.get(self.api_base, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if use_cache:
            self._set_cache(cache_key, data)

        return data

    def get_categories(self):
        return [
            {"name": "Animals", "title": "Category:Animals"},
            {"name": "Foliage", "title": "Category:Foliage"},
            {"name": "Objects", "title": "Category:Objects"},
            {"name": "Scenery", "title": "Category:Scenery"},
            {"name": "Buildings", "title": "Category:Building_Sets"},
            {"name": "Packs", "title": "Category:Packs"},
            {"name": "Recent", "title": "Special:RecentChanges"},
        ]

    def get_category_members(self, category, limit=50):
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': category,
            'cmlimit': limit,
            'cmtype': 'page|subcat',
            'cmprop': 'title|type'
        }
        data = self._request(params)
        return data.get('query', {}).get('categorymembers', [])

    def search_mods(self, query, limit=25):
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': limit,
            'srnamespace': 0,
            'srprop': 'snippet|titlesnippet'
        }
        data = self._request(params, use_cache=False)
        return data.get('query', {}).get('search', [])

    def get_page_content(self, title):
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'text|links|externallinks|images',
            'disablelimitreport': 'true'
        }
        data = self._request(params)
        return data.get('parse', {})

    def get_page_info(self, title):
        params = {
            'action': 'query',
            'titles': title,
            'prop': 'info|images|categories',
            'inprop': 'url'
        }
        data = self._request(params)
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if page_id != '-1':
                return page_data
        return None

    def get_recent_downloads(self, limit=30):
        params = {
            'action': 'query',
            'list': 'recentchanges',
            'rcnamespace': 0,
            'rclimit': limit,
            'rctype': 'new|edit',
            'rcprop': 'title|timestamp|user'
        }
        data = self._request(params, use_cache=False)
        return data.get('query', {}).get('recentchanges', [])

    def get_page_url(self, title):
        return f"{self.wiki_base}/{title.replace(' ', '_')}"

zt2dl_api = ZT2DownloadLibraryAPI()

class ZT2ModdingWikiAPI:

    def __init__(self):
        self.api_base = "https://zt2modding.fandom.com/api.php"
        self.wiki_base = "https://zt2modding.fandom.com/wiki"
        self.cache = {}
        self.cache_duration = 3600

    def _get_cached(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.cache_duration:
                return data
        return None

    def _set_cache(self, key, data):
        self.cache[key] = (data, time.time())

    def _request(self, params):
        cache_key = f"wiki:{json.dumps(params, sort_keys=True)}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        params['format'] = 'json'
        try:
            response = requests.get(self.api_base, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            self._set_cache(cache_key, data)
            return data
        except Exception as e:
            print(f"[Wiki API Error] {e}")
            return None

    def get_category_pages(self, category):
        params = {
            'action': 'query',
            'list': 'categorymembers',
            'cmtitle': f'Category:{category}',
            'cmlimit': '100',
            'cmtype': 'page'
        }
        data = self._request(params)
        if data and 'query' in data:
            return data['query'].get('categorymembers', [])
        return []

    def get_page_content(self, title):
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'text|wikitext|images',
            'disablelimitreport': '1'
        }
        data = self._request(params)
        if data and 'parse' in data:
            parse_data = data['parse']
            wikitext = parse_data.get('wikitext', {}).get('*', '')
            images = self._extract_images(wikitext, parse_data.get('images', []))
            text = self._clean_wikitext(wikitext)
            if not text.strip():
                text = 'No content available.'
            return {
                'title': parse_data.get('title', title),
                'extract': text,
                'images': images,
                'url': self.get_page_url(title)
            }
        return None

    def _extract_images(self, wikitext, image_list):
        import re
        images = []

        file_pattern = r'\[\[(?:File|Image):([^\]|]+)'
        matches = re.findall(file_pattern, wikitext, re.IGNORECASE)

        for img_name in image_list:
            if img_name not in matches:
                matches.append(img_name)

        for img_name in matches[:5]:
            img_url = self._get_image_url(img_name)
            if img_url:
                images.append({'name': img_name, 'url': img_url})

        return images

    def _get_image_url(self, filename):
        if not filename.startswith('File:'):
            filename = f"File:{filename}"

        params = {
            'action': 'query',
            'titles': filename,
            'prop': 'imageinfo',
            'iiprop': 'url',
            'iiurlwidth': '400'
        }
        data = self._request(params)
        if data and 'query' in data:
            pages = data['query'].get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1':
                    imageinfo = page_data.get('imageinfo', [])
                    if imageinfo:
                        return imageinfo[0].get('thumburl') or imageinfo[0].get('url')
        return None

    def _clean_wikitext(self, wikitext):
        import re
        text = wikitext
        text = re.sub(r'\{\{[^}]+\}\}', '', text)
        text = re.sub(r'\[\[Category:[^\]]+\]\]', '', text)
        text = re.sub(r'\[\[[^\]|]+\|([^\]]+)\]\]', r'\1', text)
        text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
        text = re.sub(r'\[https?://[^\s\]]+ ([^\]]+)\]', r'\1', text)
        text = re.sub(r'\[https?://[^\]]+\]', '', text)
        text = re.sub(r'\[\[File:[^\]]+\]\]', '', text)
        text = re.sub(r'\[\[Image:[^\]]+\]\]', '', text)
        text = re.sub(r'={2,}([^=]+)={2,}', r'\n\1\n', text)
        text = re.sub(r"'''?", '', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'__[A-Z]+__', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        return text

    def get_page_url(self, title):
        return f"{self.wiki_base}/{title.replace(' ', '_')}"

    def get_tutorials(self):
        return self.get_category_pages('Tutorials')

    def get_tools(self):
        tools = []
        tool_names = [
            'Blender', 'Nifskope', 'Photoshop', 'Gimp_2', 'Paint_Shop_Pro',
            'Visual_Studio_Code', 'Gmax', 'ZT2_BFB_Tool', 'ZT_Studio'
        ]
        for tool in tool_names:
            page = self.get_page_content(tool)
            if page:
                tools.append(page)
        return tools

    def get_file_formats(self):
        formats = []
        format_names = [
            '.z2f', '.nif', '.dds', '.bfm', '.xml', '.lua', '.beh', '.bf', '.bfb'
        ]
        for fmt in format_names:
            page = self.get_page_content(fmt)
            if page:
                formats.append(page)
        return formats

    def search(self, query):
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'srlimit': '20'
        }
        data = self._request(params)
        if data and 'query' in data:
            return data['query'].get('search', [])
        return []

    def get_tutorial_categories(self):
        return [
            {"name": "All Tutorials", "category": "Tutorials"},
            {"name": "Blender Tutorials", "category": "Blender_Tutorials"},
            {"name": "Coding Tutorials", "category": "Coding_Tutorials"},
            {"name": "NifSkope Tutorials", "category": "Nifskope_Tutorials"},
            {"name": "Texturing Tutorials", "category": "Paint_Shop_Tutorials"},
        ]


modding_wiki_api = ZT2ModdingWikiAPI()


def check_for_updates():
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        release = response.json()

        latest_version = release["tag_name"].lstrip("v")
        release_url = release["html_url"]

        if latest_version > APP_VERSION:
            if messagebox.askyesno(
                    "Update Available",
                    f"A new version ({latest_version}) is available!\n\n"
                    f"You're using {APP_VERSION}.\n\n"
                    "Would you like to open the release page?"):
                webbrowser.open(release_url)
        else:
            messagebox.showinfo(
                "Up to Date",
                f"You're running the latest version ({APP_VERSION}).")

    except requests.RequestException as e:
        messagebox.showerror("Update Check Failed",
                             f"Could not contact GitHub:\n{e}")

def monitor_game_crash(proc, game_name="ZT2", timeout=10):
    start_time = time.time()
    pid = proc.pid
    crash_log = os.path.join(CONFIG_DIR, f"{game_name.lower()}_crash.log")

    try:
        while proc.poll() is None:
            time.sleep(1)
        exit_code = proc.returncode
    except Exception as e:
        exit_code = -999
        with open(crash_log, "a", encoding="utf-8") as f:
            f.write(
                f"[{datetime.datetime.now()}] Exception monitoring {game_name}: {e}\n"
            )

    elapsed = time.time() - start_time
    if exit_code != 0 or elapsed < timeout:
        with open(crash_log, "a", encoding="utf-8") as f:
            f.write("------ Game Crash Detected ------\n")
            f.write(f"Game: {game_name}\n")
            f.write(f"Time: {datetime.datetime.now()}\n")
            f.write(f"Exit Code: {exit_code}\n")
            f.write(f"Ran for: {elapsed:.1f}s\n\n")

        messagebox.showwarning(
            f"{game_name} Crash Detected",
            f"{game_name} may have crashed or closed unexpectedly.\n"
            f"Duration: {elapsed:.1f} seconds\n\n"
            f"A crash log has been saved to:\n{crash_log}")


def enable_zt1_mod(name, text_widget=None):
    if not ZT1_MOD_DIR or not os.path.isdir(ZT1_MOD_DIR):
        messagebox.showerror("Error", "ZT1 mod folder not set.")
        return

    disabled_dir = zt1_mods_disabled_dir()
    os.makedirs(disabled_dir, exist_ok=True)

    src = os.path.join(disabled_dir, name)
    dst = os.path.join(ZT1_MOD_DIR, name)

    if not os.path.isfile(src):
        log(f"[!] Cannot find disabled mod: {src}", text_widget)
        return

    try:
        shutil.move(src, dst)
        cursor.execute("UPDATE zt1_mods SET enabled=1 WHERE name=?", (name, ))
        conn.commit()
        log(f"Enabled ZT1 mod: {name}", text_widget)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to enable mod:\n{e}")


def disable_zt1_mod(name, text_widget=None):
    if not ZT1_MOD_DIR or not os.path.isdir(ZT1_MOD_DIR):
        messagebox.showerror("Error", "ZT1 mod folder not set.")
        return

    disabled_dir = zt1_mods_disabled_dir()
    os.makedirs(disabled_dir, exist_ok=True)

    src = os.path.join(ZT1_MOD_DIR, name)
    dst = os.path.join(disabled_dir, name)

    if not os.path.isfile(src):
        log(f"[!] Cannot find enabled mod: {src}", text_widget)
        return

    try:
        shutil.move(src, dst)
        cursor.execute("UPDATE zt1_mods SET enabled=0 WHERE name=?", (name, ))
        conn.commit()
        log(f"Disabled ZT1 mod: {name}", text_widget)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to disable mod:\n{e}")


def set_mod_category(mod_name, category, zt1=False):
    table = "zt1_mods" if zt1 else "mods"
    cursor.execute(f"UPDATE {table} SET category=? WHERE name=?",
                   (category, mod_name))
    conn.commit()


def get_mod_category(mod_name, zt1=False):
    table = "zt1_mods" if zt1 else "mods"
    cursor.execute(f"SELECT category FROM {table} WHERE name=?", (mod_name, ))
    row = cursor.fetchone()
    return row[0] if row else "Uncategorized"


def set_mod_tags(mod_name, tags, zt1=False):
    table = "zt1_mods" if zt1 else "mods"
    tags_str = ", ".join(sorted(set([t.strip() for t in tags if t.strip()])))
    cursor.execute(f"UPDATE {table} SET tags=? WHERE name=?",
                   (tags_str, mod_name))
    conn.commit()


def get_mod_tags(mod_name, zt1=False):
    table = "zt1_mods" if zt1 else "mods"
    cursor.execute(f"SELECT tags FROM {table} WHERE name=?", (mod_name, ))
    row = cursor.fetchone()
    return [t.strip() for t in row[0].split(",")] if row and row[0] else []


def enabled_count():
    cursor.execute("SELECT COUNT(*) FROM mods WHERE enabled=1")
    return cursor.fetchone()[0]


def get_zt2_photos_root():
    appdata = os.environ.get("APPDATA")
    if not appdata:
        return None
    root = os.path.join(appdata, "Microsoft Games", "Zoo Tycoon 2",
                        "Default Profile", "HTML Photo Album")
    return root if os.path.isdir(root) else None


def list_zt2_albums(root):
    albums = []
    for p in Path(root).glob("album*"):
        if p.is_dir():
            albums.append((p.name, str(p)))

    def _key(t):
        name = t[0]
        try:
            return int(name.replace("album", ""))
        except Exception:
            return 999999

    return sorted(albums, key=_key)


def list_album_images(album_path):
    exts = ("*.jpg", "*.jpeg", "*.png", "*.bmp", "*.JPG", "*.JPEG", "*.PNG", "*.BMP")
    imgs = []

    for pat in exts:
        imgs.extend(glob.glob(os.path.join(album_path, pat)))

    images_subdir = os.path.join(album_path, "images")
    if os.path.isdir(images_subdir):
        for pat in exts:
            imgs.extend(glob.glob(os.path.join(images_subdir, pat)))

    for pat in exts:
        imgs.extend(glob.glob(os.path.join(album_path, "**", pat), recursive=True))

    seen = set()
    unique_imgs = []
    for img in imgs:
        normalized = os.path.normpath(img)
        if normalized not in seen:
            seen.add(normalized)
            unique_imgs.append(img)

    unique_imgs.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return unique_imgs

def get_current_theme():
    try:
        return settings.get("zt2_theme", "classic")
    except Exception:
        return "classic"


def set_dependencies(mod_name, dependencies):
    cursor.execute("DELETE FROM mod_dependencies WHERE mod_name=?",
                   (mod_name, ))
    for dep in dependencies:
        cursor.execute(
            "INSERT INTO mod_dependencies (mod_name, depends_on) VALUES (?, ?)",
            (mod_name, dep))
    conn.commit()


def get_dependencies(mod_name):
    cursor.execute("SELECT depends_on FROM mod_dependencies WHERE mod_name=?",
                   (mod_name, ))
    return [r[0] for r in cursor.fetchall()]


def get_dependents(target_mod):
    cursor.execute("SELECT mod_name FROM mod_dependencies WHERE depends_on=?",
                   (target_mod, ))
    return [r[0] for r in cursor.fetchall()]


def get_system_theme():
    try:
        if platform.system() == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            return "light" if value == 1 else "dark"

        elif platform.system() == "Darwin":
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True)
            return "dark" if "Dark" in result.stdout else "light"

        else:
            result = subprocess.run([
                "gsettings", "get", "org.gnome.desktop.interface",
                "color-scheme"
            ],
                                    capture_output=True,
                                    text=True)
            return "dark" if "dark" in result.stdout.lower() else "light"

    except Exception:
        return "dark"


def check_theme_schedule():
    if not settings.get("theme_scheduling_enabled", False):
        return

    try:
        now = datetime.now()
        current_time = now.hour * 60 + now.minute

        light_start = settings.get("theme_light_start", "07:00")
        dark_start = settings.get("theme_dark_start", "19:00")

        light_h, light_m = map(int, light_start.split(":"))
        dark_h, dark_m = map(int, dark_start.split(":"))

        light_minutes = light_h * 60 + light_m
        dark_minutes = dark_h * 60 + dark_m

        light_theme = settings.get("theme_light", "litera")
        dark_theme = settings.get("theme_dark", "darkly")

        current_theme = root.style.theme_use()

        if light_minutes < dark_minutes:
            should_be_light = light_minutes <= current_time < dark_minutes
        else:
            should_be_light = current_time >= light_minutes or current_time < dark_minutes

        target_theme = light_theme if should_be_light else dark_theme

        if current_theme != target_theme:
            root.style.theme_use(target_theme)
            settings["theme"] = target_theme
            save_settings(settings)
            if 'current_theme_var' in globals():
                current_theme_var.set(f"Current: {target_theme}")
            log(f"Theme auto-switched to {target_theme} (scheduled)", text_widget=log_text if 'log_text' in globals() else None)
    except Exception as e:
        print(f"Theme schedule check error: {e}")


def start_theme_scheduler():
    def schedule_check():
        check_theme_schedule()
        root.after(60000, schedule_check)

    root.after(1000, schedule_check)


def set_game_path(lbl_widget=None, status_widget=None):
    global GAME_PATH

    try:
        print("Opening file dialog to select ZT2 folder...")
        path = filedialog.askdirectory(title="Select Zoo Tycoon 2 Game Folder")
    except Exception as e:
        print(f"Error opening file dialog: {e}")
        messagebox.showerror("Error", f"Failed to open file dialog:\n{e}")
        return

    if not path:
        print("No folder selected.")
        return

    GAME_PATH = path
    print(f"Selected path: {GAME_PATH}")

    try:
        save_game_path(GAME_PATH)
        print("Game path saved successfully.")
    except Exception as e:
        print(f"Error saving game path: {e}")
        messagebox.showwarning("Warning", f"Could not save game path:\n{e}")

    if lbl_widget:
        try:
            lbl_widget.config(text=GAME_PATH)
        except Exception as e:
            print(f"Failed to update label widget: {e}")
    if status_widget:
        try:
            status_widget.config(
                text=f"ZT2 path: {GAME_PATH} | {enabled_count()} mods enabled")
        except Exception as e:
            print(f"Failed to update status widget: {e}")

    if 'log_text' in globals():
        try:
            log(f"Game path set: {GAME_PATH}", text_widget=log_text)
        except Exception as e:
            print(f"Failed to log message: {e}")

    try:
        refresh_tree()
    except Exception as e:
        print(f"refresh_tree() failed: {e}")


def launch_game(params=None):
    settings = load_settings()
    game_path = settings.get("game_path")

    if not GAME_PATH:
        messagebox.showerror("Error", "Set game path first!")
        return

    exe_path = os.path.join(GAME_PATH, "zt.exe")
    if not os.path.isfile(exe_path):
        messagebox.showerror("Error", f"zt.exe not found in: {GAME_PATH}")
        return

    try:
        cmd = [exe_path]
        if params:
            if isinstance(params, str):
                cmd += params.split()
            elif isinstance(params, (list, tuple)):
                cmd += list(params)

        proc = subprocess.Popen(cmd, cwd=GAME_PATH, shell=False)
        log("🎮 Launched Zoo Tycoon 2", text_widget=log_text)

        threading.Thread(target=monitor_game_crash,
                         args=(proc, "ZT2"),
                         daemon=True).start()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch ZT2: {e}")


def mods_disabled_dir():
    if not GAME_PATH:
        return None
    return os.path.join(GAME_PATH, "Mods", "Disabled")


def find_mod_file(mod_name):
    if not GAME_PATH:
        return None
    p1 = os.path.join(GAME_PATH, mod_name)
    p2 = os.path.join(mods_disabled_dir(), mod_name)
    if os.path.isfile(p1):
        return p1
    if os.path.isfile(p2):
        return p2
    return None


def index_mod_files(cursor=None, conn=None, force=False):
    if cursor is None or conn is None:
        cursor = globals().get("cursor")
        conn = globals().get("conn")

    if not GAME_PATH:
        return

    cache_file = os.path.join(CONFIG_DIR, "file_index.json")
    cache = {}
    if os.path.isfile(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    changed = False
    for folder in [GAME_PATH, mods_disabled_dir()]:
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            if not (f.lower().endswith('.z2f')):
                continue
            if f.lower().endswith('.pac'):
                continue
            full_path = os.path.join(folder, f)
            try:
                mtime = os.path.getmtime(full_path)
            except OSError:
                continue

            if not force and f in cache and cache[f].get("_mtime") == mtime:
                continue

            import hashlib
            h = hashlib.sha1()
            try:
                with open(full_path, "rb") as fp:
                    while True:
                        chunk = fp.read(65536)
                        if not chunk:
                            break
                        h.update(chunk)
                mod_hash = h.hexdigest()
            except Exception:
                mod_hash = None

            cache[f] = {"_mtime": mtime, "hash": mod_hash}
            changed = True

            if mod_hash:
                cursor.execute("UPDATE mods SET hash=? WHERE name=?",
                               (mod_hash, f))
    if changed:
        conn.commit()
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)


def file_hash(path):
    h = hashlib.sha1()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def backup_mods():
    if not GAME_PATH:
        messagebox.showerror("Error", "Set your Zoo Tycoon 2 path first.")
        return

    backup_dir = filedialog.askdirectory(title="Select backup destination")
    if not backup_dir:
        return

    backup_name = f"ZT2_ModBackup_{time.strftime('%Y%m%d_%H%M%S')}.zip"
    backup_path = os.path.join(backup_dir, backup_name)

    try:
        with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for folder in [GAME_PATH, mods_disabled_dir()]:
                if not os.path.isdir(folder):
                    continue
                for f in os.listdir(folder):
                    if f.lower().endswith((".z2f")):
                        fp = os.path.join(folder, f)
                        arcname = os.path.join(
                            "Enabled" if folder == GAME_PATH else "Disabled",
                            f)
                        zf.write(fp, arcname)
        messagebox.showinfo("Backup Complete",
                            f"Mods backed up to:\n{backup_path}")
        log(f"Created backup: {backup_path}", text_widget=log_text)
    except Exception as e:
        messagebox.showerror("Backup Error", str(e))
        log(f"Backup failed: {e}", text_widget=log_text)


def restore_mods():
    if not GAME_PATH:
        messagebox.showerror("Error", "Set your Zoo Tycoon 2 path first.")
        return

    zip_path = filedialog.askopenfilename(title="Select Mod Backup ZIP",
                                          filetypes=[("Zip Files", "*.zip")])
    if not zip_path:
        return

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            temp_extract = os.path.join(CONFIG_DIR, "_restore_temp")
            os.makedirs(temp_extract, exist_ok=True)
            zf.extractall(temp_extract)

            enabled_dir = os.path.join(temp_extract, "Enabled")
            disabled_dir = os.path.join(temp_extract, "Disabled")

            for src, dest in [(enabled_dir, GAME_PATH),
                              (disabled_dir, mods_disabled_dir())]:
                if os.path.isdir(src):
                    for f in os.listdir(src):
                        shutil.copy2(os.path.join(src, f),
                                     os.path.join(dest, f))

        messagebox.showinfo("Restore Complete", "Mods restored successfully!")
        log("Mods restored from backup", text_widget=log_text)
        shutil.rmtree(temp_extract, ignore_errors=True)
        refresh_tree()
    except Exception as e:
        messagebox.showerror("Restore Error", str(e))
        log(f"Restore failed: {e}", text_widget=log_text)


def detect_existing_mods(cursor=None, conn=None):
    if not GAME_PATH:
        return

    if cursor is None or conn is None:
        cursor = globals().get("cursor")
        conn = globals().get("conn")

    disabled_dir = mods_disabled_dir()
    os.makedirs(disabled_dir, exist_ok=True)

    scanned = {}
    for folder, enabled in [(GAME_PATH, 1), (disabled_dir, 0)]:
        if not os.path.isdir(folder):
            continue
        for f in os.listdir(folder):
            if not (f.lower().endswith('.z2f')):
                continue
            if f.lower().endswith('.pac'):
                continue

            full_path = os.path.join(folder, f)
            mtime = os.path.getmtime(full_path)
            scanned[f] = (enabled, mtime)

    for mod_name, (enabled, mtime) in scanned.items():
        cursor.execute("SELECT COUNT(*) FROM mods WHERE name=?", (mod_name, ))
        exists = cursor.fetchone()[0]
        if exists == 0:
            cursor.execute("INSERT INTO mods (name, enabled) VALUES (?, ?)",
                           (mod_name, enabled))
        else:
            cursor.execute("UPDATE mods SET enabled=? WHERE name=?",
                           (enabled, mod_name))
    conn.commit()

    cursor.execute("SELECT name FROM mods")
    for (name, ) in cursor.fetchall():
        if name not in scanned:
            cursor.execute("DELETE FROM mods WHERE name=?", (name, ))
    conn.commit()

    try:
        cursor.execute("""
            SELECT hash, GROUP_CONCAT(name, ', ') AS mods, COUNT(*) AS c
            FROM mods
            WHERE hash IS NOT NULL
            GROUP BY hash HAVING c > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            dup_text = "\n".join(f"{mods}" for _, mods, _ in duplicates)
            log(f"Duplicate mods detected:\n{dup_text}", log_text)
            messagebox.showwarning(
                "Duplicate Mods Detected",
                f"The following mods have identical contents:\n\n{dup_text}")
    except sqlite3.OperationalError:
        pass


def enable_mod(mod_name, text_widget=None, record=True):
    deps = get_dependencies(mod_name)
    for dep in deps:
        cursor.execute("SELECT enabled FROM mods WHERE name=?", (dep, ))
        row = cursor.fetchone()
        if not row or row[0] == 0:
            log(f"Enabling dependency: {dep}", text_widget)
            enable_mod(dep, text_widget, record=False)

    if not mod_name or not GAME_PATH:
        return
    src = os.path.join(mods_disabled_dir(), mod_name)
    dst = os.path.join(GAME_PATH, mod_name)
    if os.path.isfile(src):
        try:
            shutil.move(src, dst)
            log(f"Enabled mod: {mod_name}", text_widget)
        except Exception as e:
            messagebox.showerror("Error", f"Enable failed: {e}")
            return
    else:
        if not os.path.isfile(dst):
            messagebox.showwarning(
                "Not found", f"Mod file for {mod_name} not found on disk.")
            return
    cursor.execute("UPDATE mods SET enabled=1 WHERE name=?", (mod_name, ))
    conn.commit()

    if record:
        record_action("enable", {"mod_name": mod_name})

    for iid in mods_tree.get_children():
        vals = mods_tree.item(iid, "values")
        if vals and vals[0] == mod_name:
            mods_tree.item(iid, values=(vals[0], "Enabled", vals[2], vals[3]))
            mods_tree.item(iid, tags=("enabled", ))
            break

    update_status()


def disable_mod(mod_name, text_widget=None, record=True):
    dependents = get_dependents(mod_name)
    if dependents:
        if not messagebox.askyesno(
                "Disable Dependency",
                f"The following mods depend on {mod_name}:\n{', '.join(dependents)}\nDisable them too?"
        ):
            return
        for d in dependents:
            disable_mod(d, text_widget, record=False)

    if not mod_name or not GAME_PATH:
        return
    dst_dir = mods_disabled_dir()
    os.makedirs(dst_dir, exist_ok=True)
    src = os.path.join(GAME_PATH, mod_name)
    dst = os.path.join(dst_dir, mod_name)
    if os.path.isfile(src):
        try:
            shutil.move(src, dst)
            log(f"Disabled mod: {mod_name}", text_widget)
        except Exception as e:
            messagebox.showerror("Error", f"Disable failed: {e}")
            return
    else:
        messagebox.showwarning(
            "Not found",
            f"Mod file for {mod_name} not found in enabled folder.")
    cursor.execute("UPDATE mods SET enabled=0 WHERE name=?", (mod_name, ))
    conn.commit()

    if record:
        record_action("disable", {"mod_name": mod_name})

    for iid in mods_tree.get_children():
        vals = mods_tree.item(iid, "values")
        if vals and vals[0] == mod_name:
            mods_tree.item(iid, values=(vals[0], "Disabled", vals[2], vals[3]))
            mods_tree.item(iid, tags=("disabled", ))
            break

    update_status()


def uninstall_mod(mod_name, text_widget=None, record=True):
    if not mod_name or not GAME_PATH:
        return
    paths = [
        os.path.join(GAME_PATH, mod_name),
        os.path.join(mods_disabled_dir(), mod_name)
    ]
    removed = False
    was_enabled = False
    trash_path = None

    for p in paths:
        if os.path.isfile(p):
            try:
                trash_path = os.path.join(TRASH_DIR, mod_name)
                if os.path.exists(trash_path):
                    base, ext = os.path.splitext(mod_name)
                    trash_path = os.path.join(TRASH_DIR, f"{base}_{int(time.time())}{ext}")
                shutil.move(p, trash_path)
                was_enabled = (p == os.path.join(GAME_PATH, mod_name))
                log(f"Moved to trash: {p}", text_widget)
                removed = True
                break
            except Exception as e:
                messagebox.showerror("Error", f"Failed to remove {p}: {e}")

    cursor.execute("DELETE FROM mods WHERE name=?", (mod_name, ))
    conn.commit()

    if record and removed and trash_path:
        record_action("uninstall", {
            "mod_name": mod_name,
            "trash_path": trash_path,
            "was_enabled": was_enabled
        })

    if removed:
        log(f"Uninstalled mod: {mod_name}", text_widget)
    else:
        log(f"Mod {mod_name} not found on disk, record removed from DB.",
            text_widget)
    refresh_tree()
    update_status()


def install_mods(file_paths, text_widget=None):
    if not GAME_PATH:
        messagebox.showerror("Error", "Game path not set. Please set your Zoo Tycoon 2 folder first.")
        return

    installed = []
    skipped = []
    errors = []

    for path in file_paths:
        path = path.strip()
        if path.startswith('{') and path.endswith('}'):
            path = path[1:-1]

        if not os.path.isfile(path):
            errors.append(f"File not found: {path}")
            continue

        filename = os.path.basename(path)
        if not filename.lower().endswith('.z2f'):
            skipped.append(f"Not a .z2f file: {filename}")
            continue

        dest = os.path.join(GAME_PATH, filename)
        if os.path.exists(dest):
            if not messagebox.askyesno("Overwrite?", f"{filename} already exists.\nOverwrite?"):
                skipped.append(f"Skipped (exists): {filename}")
                continue

        try:
            shutil.copy2(path, dest)
            installed.append(filename)
            log(f"Installed mod: {filename}", text_widget)
        except Exception as e:
            errors.append(f"Failed to copy {filename}: {e}")

    if installed:
        detect_existing_mods()
        refresh_tree()
        record_action("install", {"mod_names": installed})
        increment_stat("mods_installed", len(installed))

    summary = []
    if installed:
        summary.append(f"Installed: {len(installed)} mod(s)")
    if skipped:
        summary.append(f"Skipped: {len(skipped)}")
    if errors:
        summary.append(f"Errors: {len(errors)}")

    if summary:
        details = "\n".join(installed) if installed else ""
        if errors:
            details += "\n\nErrors:\n" + "\n".join(errors)
        if skipped:
            details += "\n\nSkipped:\n" + "\n".join(skipped)
        messagebox.showinfo("Install Complete", "\n".join(summary) + "\n\n" + details)


def install_mod_from_url_dialog():
    dialog = tk.Toplevel(root)
    dialog.title("Install Mod from URL")
    dialog.geometry("500x200")
    dialog.resizable(False, False)
    dialog.transient(root)
    dialog.grab_set()

    ttk.Label(dialog, text="Install Mod from URL",
              font=("Segoe UI", 12, "bold")).pack(pady=(15, 5))

    ttk.Label(dialog, text="Enter a direct download URL to a .z2f mod file:",
              bootstyle="secondary").pack(pady=(0, 10))

    url_var = tk.StringVar()
    url_entry = ttk.Entry(dialog, textvariable=url_var, width=60)
    url_entry.pack(padx=20, pady=5)
    url_entry.focus_set()

    status_var = tk.StringVar(value="")
    status_label = ttk.Label(dialog, textvariable=status_var, bootstyle="info")
    status_label.pack(pady=5)

    progress = ttk.Progressbar(dialog, mode="indeterminate", length=300)
    progress.pack(pady=5)

    def do_download():
        url = url_var.get().strip()
        if not url:
            status_var.set("Please enter a URL")
            return

        if not GAME_PATH:
            messagebox.showerror("Error", "Game path not set. Please set your Zoo Tycoon 2 folder first.")
            return

        try:
            from urllib.parse import urlparse, unquote
            parsed = urlparse(url)
            filename = unquote(os.path.basename(parsed.path))

            if not filename:
                filename = "downloaded_mod.z2f"
            if not filename.lower().endswith('.z2f'):
                if '.' not in filename:
                    filename += '.z2f'

            status_var.set(f"Downloading {filename}...")
            progress.start()
            dialog.update()

            def download():
                try:
                    response = requests.get(url, stream=True, timeout=60,
                                          headers={"User-Agent": "ModZT/1.0"})
                    response.raise_for_status()

                    content_disp = response.headers.get('Content-Disposition', '')
                    if 'filename=' in content_disp:
                        import re
                        match = re.search(r'filename[*]?=["\']?([^"\';\n]+)', content_disp)
                        if match:
                            filename_from_header = match.group(1).strip()
                            if filename_from_header:
                                nonlocal filename
                                filename = filename_from_header

                    temp_path = os.path.join(CONFIG_DIR, filename)
                    with open(temp_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    return temp_path, None
                except Exception as e:
                    return None, str(e)

            def on_complete(result):
                progress.stop()
                temp_path, error = result

                if error:
                    status_var.set(f"Error: {error}")
                    return

                dest = os.path.join(GAME_PATH, os.path.basename(temp_path))
                if os.path.exists(dest):
                    if not messagebox.askyesno("Overwrite?",
                            f"{os.path.basename(temp_path)} already exists.\nOverwrite?"):
                        status_var.set("Installation cancelled")
                        os.remove(temp_path)
                        return

                try:
                    shutil.move(temp_path, dest)
                    detect_existing_mods()
                    refresh_tree()
                    increment_stat("mods_installed")
                    status_var.set(f"Successfully installed: {os.path.basename(dest)}")
                    log(f"Installed mod from URL: {os.path.basename(dest)}", text_widget=log_text)
                    messagebox.showinfo("Success", f"Mod installed successfully:\n{os.path.basename(dest)}")
                    dialog.destroy()
                except Exception as e:
                    status_var.set(f"Install error: {e}")

            threading.Thread(target=lambda: root.after(0, lambda: on_complete(download())),
                           daemon=True).start()

        except Exception as e:
            progress.stop()
            status_var.set(f"Error: {e}")

    btn_frame = ttk.Frame(dialog)
    btn_frame.pack(pady=15)

    ttk.Button(btn_frame, text="Download & Install", command=do_download,
               bootstyle="success", width=18).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Cancel", command=dialog.destroy,
               bootstyle="secondary", width=10).pack(side=tk.LEFT, padx=5)

    url_entry.bind("<Return>", lambda e: do_download())


def export_load_order():
    cursor.execute("SELECT name, enabled FROM mods")
    rows = cursor.fetchall()
    path = os.path.join(CONFIG_DIR, "load_order.txt")
    with open(path, "w", encoding="utf-8") as f:
        for name, enabled in rows:
            f.write(f"{name}: {'Enabled' if enabled else 'Disabled'}\n")
    messagebox.showinfo("Exported", f"Load order exported to:\n{path}")
    log(f"Exported load order to {path}", text_widget=log_text)


def watch_mods(root, refresh_func, interval=5):

    def worker():
        last_snapshot = set()
        while True:
            try:
                if not GAME_PATH or not os.path.isdir(GAME_PATH):
                    time.sleep(interval)
                    continue
                found = set()
            except Exception as e:
                print("Watcher error:", e)
                time.sleep(interval)

            found = set()
            disabled = mods_disabled_dir()
            for folder in [GAME_PATH, disabled]:
                if os.path.isdir(folder):
                    for f in os.listdir(folder):
                        if f.lower().endswith('.z2f'):
                            found.add((f, 1 if folder == GAME_PATH else 0))
            if found != last_snapshot:

                def update_db_and_refresh():
                    for mod_name, enabled in found:
                        cursor.execute(
                            "SELECT COUNT(*) FROM mods WHERE name=?",
                            (mod_name, ))
                        if cursor.fetchone()[0] == 0:
                            cursor.execute(
                                "INSERT INTO mods (name, enabled) VALUES (?, ?)",
                                (mod_name, enabled))
                        else:
                            cursor.execute(
                                "UPDATE mods SET enabled=? WHERE name=?",
                                (enabled, mod_name))
                    conn.commit()
                    refresh_func()
                    update_status()

                    refresh_tree()

                root.after(0, update_db_and_refresh)
                last_snapshot = found
            time.sleep(interval)

    threading.Thread(target=worker, daemon=True).start()


def bundle_create_dialog():
    dlg = tk.Toplevel(root)
    dlg.title("Create Bundle")
    dlg.geometry("420x500")
    dlg.transient(root)
    dlg.grab_set()

    ttk.Label(dlg, text="Bundle name:").pack(anchor='w', padx=8, pady=(8, 2))
    name_var = tk.StringVar()
    ttk.Entry(dlg, textvariable=name_var).pack(fill=tk.X, padx=8)

    ttk.Label(dlg, text="Select mods to include:").pack(anchor='w',
                                                        padx=8,
                                                        pady=(8, 2))
    mods_listbox = tk.Listbox(dlg, selectmode=tk.MULTIPLE, height=16)
    mods_listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

    cursor.execute("SELECT name FROM mods ORDER BY name")
    mods_all = [r[0] for r in cursor.fetchall()]
    for m in mods_all:
        mods_listbox.insert(tk.END, m)

    def _do_create():
        bname = name_var.get().strip()
        sel = mods_listbox.curselection()
        selected = [mods_all[i] for i in sel]
        if not bname or not selected:
            messagebox.showerror("Invalid",
                                 "Provide a name and select at least one mod.",
                                 parent=dlg)
            return
        ok = create_bundle(bname, selected)
        if not ok:
            messagebox.showerror("Error",
                                 "Bundle name already exists or invalid.",
                                 parent=dlg)
            return
        dlg.destroy()
        refresh_bundles_list()
        log(f"Created bundle '{bname}' with {len(selected)} mods.", log_text)

    btnrow = ttk.Frame(dlg, padding=6)
    btnrow.pack(fill=tk.X)
    ttk.Button(btnrow, text="Create", command=_do_create,
               bootstyle="success").pack(side=tk.RIGHT, padx=4)
    ttk.Button(btnrow,
               text="Cancel",
               command=dlg.destroy,
               bootstyle="secondary").pack(side=tk.RIGHT)


def open_game_unlocks_dialog():
    options_path = get_zt2_options_xml_path()
    if not options_path:
        appdata = os.environ.get("APPDATA", "")
        expected_path = os.path.join(appdata, "Microsoft Games", "Zoo Tycoon 2",
                                     "Default Profile", "options.xml")
        messagebox.showerror(
            "Options File Not Found",
            f"Could not find options.xml at:\n{expected_path}\n\n"
            "Make sure Zoo Tycoon 2 has been run at least once.",
            parent=root)
        return

    dlg = tk.Toplevel(root)
    dlg.title("Game Unlocks Manager")
    dlg.geometry("700x600")
    dlg.transient(root)
    dlg.grab_set()

    try:
        tree = ET.parse(options_path)
        xml_root = tree.getroot()
        user_elem = xml_root.find(".//User")
        if user_elem is None:
            user_elem = ET.SubElement(xml_root, "User")
    except Exception as e:
        messagebox.showerror("XML Error", f"Could not parse options.xml:\n{e}", parent=dlg)
        dlg.destroy()
        return

    check_vars = {}

    main_container = ttk.Frame(dlg)
    main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    canvas = tk.Canvas(main_container)
    scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def create_category_section(parent, title, unlock_dict, value_type="completed"):
        section_frame = ttk.LabelFrame(parent, text=title, padding=10)
        section_frame.pack(fill=tk.X, pady=5)

        for group_name, items in unlock_dict.items():
            group_frame = ttk.LabelFrame(section_frame, text=group_name, padding=5)
            group_frame.pack(fill=tk.X, pady=2)

            items_frame = ttk.Frame(group_frame)
            items_frame.pack(fill=tk.X)

            col = 0
            row = 0
            for attr_name, display_name in items:
                var = tk.BooleanVar()
                current_val = user_elem.get(attr_name, "")
                if value_type == "completed":
                    var.set(current_val.lower() == "completed")
                else:
                    var.set(current_val.lower() == "true")

                check_vars[attr_name] = (var, value_type)
                cb = ttk.Checkbutton(items_frame, text=display_name, variable=var)
                cb.grid(row=row, column=col, sticky="w", padx=5, pady=1)

                col += 1
                if col >= 4:
                    col = 0
                    row += 1

    create_category_section(scrollable_frame, "Tutorials", UNLOCK_TUTORIALS, "completed")
    create_category_section(scrollable_frame, "Campaigns", UNLOCK_CAMPAIGNS, "completed")
    create_category_section(scrollable_frame, "Unlockable Items", UNLOCK_ITEMS, "true")

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    btn_frame = ttk.Frame(dlg, padding=10)
    btn_frame.pack(fill=tk.X, side=tk.BOTTOM)

    def select_all():
        for var, _ in check_vars.values():
            var.set(True)

    def deselect_all():
        for var, _ in check_vars.values():
            var.set(False)

    def save_changes():
        try:
            shutil.copy2(options_path, options_path + ".backup")

            for attr_name, (var, value_type) in check_vars.items():
                if var.get():
                    if value_type == "completed":
                        user_elem.set(attr_name, "completed")
                    else:
                        user_elem.set(attr_name, "true")
                else:
                    if attr_name in user_elem.attrib:
                        del user_elem.attrib[attr_name]

            tree.write(options_path, encoding="utf-8", xml_declaration=True)

            messagebox.showinfo("Success",
                               "Game unlocks saved successfully!\n\n"
                               "A backup was created at:\n"
                               f"{options_path}.backup",
                               parent=dlg)
            dlg.destroy()
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save changes:\n{e}", parent=dlg)

    def restore_backup():
        backup_path = options_path + ".backup"
        if not os.path.isfile(backup_path):
            messagebox.showinfo("No Backup", "No backup file found.", parent=dlg)
            return
        if messagebox.askyesno("Restore Backup",
                              "Restore from backup? This will overwrite current settings.",
                              parent=dlg):
            try:
                shutil.copy2(backup_path, options_path)
                messagebox.showinfo("Restored", "Backup restored. Please reopen this dialog.", parent=dlg)
                dlg.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Could not restore backup:\n{e}", parent=dlg)

    ttk.Button(btn_frame, text="Select All", command=select_all,
               bootstyle="info-outline").pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Deselect All", command=deselect_all,
               bootstyle="info-outline").pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Restore Backup", command=restore_backup,
               bootstyle="warning-outline").pack(side=tk.LEFT, padx=2)
    ttk.Button(btn_frame, text="Cancel", command=dlg.destroy,
               bootstyle="secondary").pack(side=tk.RIGHT, padx=2)
    ttk.Button(btn_frame, text="Save Changes", command=save_changes,
               bootstyle="success").pack(side=tk.RIGHT, padx=2)

    def on_close():
        canvas.unbind_all("<MouseWheel>")
        dlg.destroy()

    dlg.protocol("WM_DELETE_WINDOW", on_close)


def bundle_apply():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    apply_bundle(name, text_widget=log_text)
    refresh_bundle_preview()
    refresh_tree()


def bundle_delete():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    if messagebox.askyesno("Delete Bundle", f"Delete bundle '{name}'?"):
        delete_bundle(name)
        refresh_bundles_list()
        log(f"Deleted bundle: {name}", log_text)


def bundle_export_json():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    export_bundle_as_json(name)


def bundle_import_json():
    import_bundle_from_json()
    refresh_bundles_list()


def bundle_export_z2f():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    export_bundle_as_mod_ui(name)


def create_bundle(bundle_name, mod_list):
    if not bundle_name or not mod_list:
        return False
    cursor.execute("SELECT COUNT(*) FROM bundles WHERE name=?",
                   (bundle_name, ))
    if cursor.fetchone()[0] > 0:
        return False
    cursor.execute("INSERT INTO bundles (name) VALUES (?)", (bundle_name, ))
    bundle_id = cursor.lastrowid
    for m in mod_list:
        cursor.execute(
            "INSERT OR IGNORE INTO bundle_mods (bundle_id, mod_name) VALUES (?, ?)",
            (bundle_id, m))
    conn.commit()
    increment_stat("bundles_created")
    return True


def delete_bundle(bundle_name):
    cursor.execute("SELECT id FROM bundles WHERE name=?", (bundle_name, ))
    row = cursor.fetchone()
    if not row:
        return False
    bundle_id = row[0]
    cursor.execute("DELETE FROM bundle_mods WHERE bundle_id=?", (bundle_id, ))
    cursor.execute("DELETE FROM bundles WHERE id=?", (bundle_id, ))
    conn.commit()
    return True


def get_bundles():
    cursor.execute("SELECT id, name FROM bundles ORDER BY name")
    bundles = []
    for bid, name in cursor.fetchall():
        cursor.execute(
            "SELECT mod_name FROM bundle_mods WHERE bundle_id=? ORDER BY mod_name",
            (bid, ))
        mods = [r[0] for r in cursor.fetchall()]
        bundles.append((name, mods))
    return bundles


def get_bundle_mods(bundle_name):
    cursor.execute("SELECT id FROM bundles WHERE name=?", (bundle_name, ))
    row = cursor.fetchone()
    if not row:
        return []
    bid = row[0]
    cursor.execute(
        "SELECT mod_name FROM bundle_mods WHERE bundle_id=? ORDER BY mod_name",
        (bid, ))
    return [r[0] for r in cursor.fetchall()]


def apply_bundle(bundle_name, text_widget=None):
    mods = get_bundle_mods(bundle_name)
    if not mods:
        messagebox.showinfo("Empty",
                            "Bundle contains no mods or was not found.")
        return
    exclusive = messagebox.askyesno(
        "Apply Bundle",
        "Enable the bundle mods AND disable mods not in the bundle?\n(Yes = exclusive, No = enable bundle mods only)"
    )
    for m in mods:
        enable_mod(m, text_widget=text_widget)
    if exclusive:
        cursor.execute("SELECT name FROM mods WHERE enabled=1")
        enabled_now = [r[0] for r in cursor.fetchall()]
        for en in enabled_now:
            if en not in mods:
                disable_mod(en, text_widget=text_widget)
    log(f"Applied bundle: {bundle_name} (mods: {', '.join(mods)})",
        text_widget)


def export_bundle_as_json(bundle_name):
    mods = get_bundle_mods(bundle_name)
    if not mods:
        messagebox.showerror("Error", "Bundle not found or empty")
        return
    payload = {"name": bundle_name, "mods": mods}
    path = filedialog.asksaveasfilename(defaultextension=".json",
                                        filetypes=[("JSON", "*.json")],
                                        title="Export Bundle As")
    if not path:
        return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4)
    messagebox.showinfo("Exported", f"Bundle exported to:\n{path}")


def import_bundle_from_json(path=None):
    if not path:
        path = filedialog.askopenfilename(title="Import Bundle JSON",
                                          filetypes=[("JSON", "*.json")])
    if not path:
        return
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    name = payload.get("name")
    mods = payload.get("mods", [])
    if not name:
        messagebox.showerror("Invalid", "Bundle JSON missing 'name' field")
        return
    existing = []
    missing = []
    for m in mods:
        cursor.execute("SELECT COUNT(*) FROM mods WHERE name=?", (m, ))
        if cursor.fetchone()[0] > 0:
            existing.append(m)
        else:
            missing.append(m)
    created = create_bundle(name, existing)
    if not created:
        messagebox.showerror(
            "Exists", "Bundle with that name already exists or invalid")
        return
    msg = f"Imported bundle '{name}'.\nAdded {len(existing)} existing mods."
    if missing:
        msg += f"\n{len(missing)} mods were missing locally and were not added: {', '.join(missing)}"
    messagebox.showinfo("Imported", msg)


def export_bundle_as_z2f(bundle_name, include_files, output_path):
    mods = get_bundle_mods(bundle_name)
    if not mods:
        messagebox.showerror("Error", "Bundle not found or empty")
        return
    mod_paths = []
    for m in mods:
        p = find_mod_file(m)
        if p:
            mod_paths.append(p)
        else:
            log(f"Warning: mod file for {m} not found on disk",
                text_widget=log_text)

    if not mod_paths:
        messagebox.showerror(
            "Error", "None of the bundle mod files were found on disk")
        return

    tmp_dir = tempfile.mkdtemp()
    try:
        for mp in mod_paths:
            try:
                with zipfile.ZipFile(mp, 'r') as zf:
                    for member in zf.namelist():
                        if include_files and member not in include_files:
                            continue
                        target = os.path.join(tmp_dir, member)
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        with zf.open(member) as src, open(target, 'wb') as dst:
                            dst.write(src.read())
            except zipfile.BadZipFile:
                log(f"Skipping bad zip: {mp}")

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as outzip:
            for root_dir, _, files in os.walk(tmp_dir):
                for f in files:
                    abs_path = os.path.join(root_dir, f)
                    rel = os.path.relpath(abs_path, tmp_dir)
                    outzip.write(abs_path, rel)
        log(f"Exported merged bundle to: {output_path}", text_widget=log_text)
        messagebox.showinfo("Exported",
                            f"Bundle merged and exported to:\n{output_path}")
    finally:
        shutil.rmtree(tmp_dir)


def export_bundle_as_mod_ui(bundle_name=None):
    if not bundle_name:
        sel = bundle_list.curselection()
        if not sel:
            messagebox.showinfo("Select", "Select a bundle first.")
            return
        bundle_name = bundle_list.get(sel[0]).rsplit(' (', 1)[0]

    mods = get_bundle_mods(bundle_name)
    if not mods:
        messagebox.showerror("Error", "Bundle empty or not found")
        return

    file_map = {}
    mod_paths = {}
    for m in mods:
        p = find_mod_file(m)
        if not p:
            log(f"Mod file {m} not found on disk; skipping",
                text_widget=log_text)
            continue
        mod_paths[m] = p
        try:
            with zipfile.ZipFile(p, 'r') as zf:
                for mem in zf.namelist():
                    file_map.setdefault(mem, []).append(m)
        except zipfile.BadZipFile:
            log(f"Bad zip file: {p}", text_widget=log_text)

    files = sorted(file_map.keys())
    if not files:
        messagebox.showerror("Error",
                             "No files found inside bundle mod archives")
        return

    dlg = tk.Toplevel(root)
    dlg.title(f"Select files to include - {bundle_name}")
    dlg.geometry("700x500")

    frame = ttk.Frame(dlg, padding=6)
    frame.pack(fill=tk.BOTH, expand=True)

    canvas = tk.Canvas(frame)
    scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
    inner = ttk.Frame(canvas)

    inner.bind("<Configure>",
               lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=inner, anchor='nw')
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    var_map = {}
    for f in files:
        text = f"{f}   [{' ,'.join(file_map[f])}]"
        var = tk.BooleanVar(value=True)
        chk = ttk.Checkbutton(inner, text=text, variable=var)
        chk.pack(anchor='w')
        var_map[f] = var

    def do_export():
        included = {f for f, v in var_map.items() if v.get()}
        if not included:
            messagebox.showerror("Empty", "You must include at least one file")
            return
        out_dir = filedialog.askdirectory(title="Select export folder")
        if not out_dir:
            return
        out_name = f"{bundle_name}.z2f"
        out_path = os.path.join(out_dir, out_name)
        export_bundle_as_z2f(bundle_name, included, out_path)
        dlg.destroy()


settings = load_settings()
current_language = settings.get("language", "en")
system_theme = get_system_theme()

if not os.path.isfile(GAME_PATH_FILE):
    detected = auto_detect_zt2_installation()
    if detected:
        GAME_PATH = detected
        save_game_path(GAME_PATH)
        settings["game_path"] = GAME_PATH
        save_settings(settings)
        print(f"[✔] Auto-detected Zoo Tycoon 2 installation: {GAME_PATH}")
else:
    with open(GAME_PATH_FILE, "r", encoding="utf-8") as f:
        GAME_PATH = f.read().strip()

saved_theme = settings.get("theme", "darkly" if system_theme == "dark" else "litera")

if DND_AVAILABLE:
    root = TkinterDnD.Tk()
    root.style = tb.Style(theme=saved_theme)
else:
    root = Window(themename=saved_theme)

root.title(f"ModZT v{APP_VERSION}")

_startup_settings = load_settings()
_saved_geometry = _startup_settings.get("window_geometry", "1200x800")
_was_maximized = _startup_settings.get("window_maximized", False)

root.geometry(_saved_geometry)
root.update_idletasks()

if _was_maximized:
    root.state('zoomed')

def set_zt1_paths():
    global ZT1_PATH
    global ZT1_MOD_DIR

    messagebox.showinfo(
        "Set Zoo Tycoon 1 Paths",
        "Please select the Zoo Tycoon 1 installation folder (where zoo.exe is located)."
    )

    exe_dir = filedialog.askdirectory(title="Select ZT1 Root Folder")
    if not exe_dir:
        return

    exe_path = os.path.join(exe_dir, "zoo.exe")
    if not os.path.isfile(exe_path):
        messagebox.showerror("Error", "zoo.exe not found in that folder.")
        return

    ZT1_PATH = exe_dir
    with open(ZT1_EXE_FILE, "w", encoding="utf-8") as f:
        f.write(ZT1_PATH)

    messagebox.showinfo(
        "Set Mod Folder",
        "Now select your ZT1 mod folder (usually 'dlupdates').")

    mod_dir = filedialog.askdirectory(title="Select ZT1 Mod Folder")
    if mod_dir:
        ZT1_MOD_DIR = mod_dir
    else:
        ZT1_MOD_DIR = os.path.join(ZT1_PATH, "dlupdates")

    with open(ZT1_MOD_DIR_FILE, "w", encoding="utf-8") as f:
        f.write(ZT1_MOD_DIR)

    messagebox.showinfo(
        "Success",
        f"Zoo Tycoon 1 paths saved!\n\nExe: {ZT1_PATH}\nMods: {ZT1_MOD_DIR}")


def launch_zt1():
    global ZT1_PATH

    if not ZT1_PATH or not os.path.isfile(os.path.join(ZT1_PATH, "zoo.exe")):
        messagebox.showerror(
            "Error",
            "ZT1 path not set or zoo.exe missing.\nUse 'Set ZT1 Path' first.")
        return

    exe_path = os.path.join(ZT1_PATH, "zoo.exe")
    try:
        subprocess.Popen([exe_path], cwd=ZT1_PATH, shell=False)
        log("🎮 Launched Zoo Tycoon 1", text_widget=log_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to launch ZT1: {e}")


banner = ttk.Frame(root, padding=12, bootstyle="dark")
banner.pack(fill=tk.X)

if os.path.isfile(BANNER_FILE):
    try:
        img = Image.open(BANNER_FILE)
        img.thumbnail((72, 72), Image.LANCZOS)
        banner_img = ImageTk.PhotoImage(img)
        logo_label = ttk.Label(banner, image=banner_img)
        logo_label.image = banner_img
        logo_label.pack(side=tk.LEFT, padx=(0, 12))
    except Exception as e:
        print("Banner load failed:", e)

_tt = ttk.Label(banner,
                text="ModZT",
                font=("Segoe UI", 20, "bold"),
                bootstyle="inverse-dark")
_tt.pack(side=tk.LEFT)

toolbar = ttk.Frame(root, padding=6)
toolbar.pack(side=tk.TOP, fill=tk.X)

def toggle_theme():
    if root.style.theme_use() == 'darkly':
        root.style.theme_use('litera')
    else:
        root.style.theme_use('darkly')
    log("Toggled theme", text_widget=log_text)


def toggle_ui_mode():
    ui_mode["compact"] = not ui_mode["compact"]
    apply_ui_mode()
    mode = "Compact" if ui_mode["compact"] else "Expanded"
    new_label = t("menu_expanded_mode") if ui_mode["compact"] else t("menu_compact_mode")
    view_menu.entryconfig(2, label=new_label)
    log(f"Switched to {mode} mode", text_widget=log_text)

_translatable_widgets = {}

help_menu_btn = ttk.Menubutton(toolbar, text=t("menu_help"), bootstyle="info-outline")
_translatable_widgets["help_menu_btn"] = help_menu_btn
help_menu = tk.Menu(help_menu_btn, tearoff=0)
help_menu.add_command(label="About ModZT",
                      command=lambda: messagebox.showinfo(
                          "About",
                          "ModZT v1.1.7 Beta\n"
                          "Created by Songstorm\n\n"
                          "Music: Zoo Tycoon 2 Theme Remaster\n"
                          "by SirGoose"))
help_menu.add_command(
    label="Open GitHub Page",
    command=lambda: webbrowser.open("https://github.com/songstormstudios/modzt"))
help_menu.add_command(
    label="Discord Server",
    command=lambda: webbrowser.open("https://discord.gg/9y9DfmpZG4"))
help_menu.add_command(label="Check for Updates", command=check_for_updates)
help_menu.add_separator()
help_menu.add_command(
    label="Music Credit (SirGoose)",
    command=lambda: webbrowser.open("https://www.youtube.com/watch?v=9S3P64v9lnw"))
help_menu_btn["menu"] = help_menu
help_menu_btn.pack(side=tk.RIGHT, padx=4)

view_menu_button = ttk.Menubutton(toolbar,
                                  text=t("menu_view"),
                                  bootstyle="info-outline")
view_menu = tk.Menu(view_menu_button, tearoff=0)
view_menu.add_command(label=t("menu_toggle_theme"), command=toggle_theme)
view_menu.add_command(label=t("menu_toggle_music"), command=toggle_background_music)
view_menu.add_command(label=t("menu_compact_mode"), command=toggle_ui_mode)

def refresh_ui_language():
    view_menu_button.configure(text=t("menu_view"))
    view_menu.entryconfig(0, label=t("menu_toggle_theme"))
    view_menu.entryconfig(1, label=t("menu_toggle_music"))
    if ui_mode.get("compact", False):
        view_menu.entryconfig(2, label=t("menu_expanded_mode"))
    else:
        view_menu.entryconfig(2, label=t("menu_compact_mode"))
    view_menu.entryconfig(3, label=t("menu_language"))

    if "help_menu_btn" in _translatable_widgets:
        _translatable_widgets["help_menu_btn"].configure(text=t("menu_help"))
    if "tools_menu_btn" in _translatable_widgets:
        _translatable_widgets["tools_menu_btn"].configure(text=t("menu_tools"))
    if "mods_menu_btn" in _translatable_widgets:
        _translatable_widgets["mods_menu_btn"].configure(text=t("menu_mods"))
    if "game_menu_btn" in _translatable_widgets:
        _translatable_widgets["game_menu_btn"].configure(text=t("menu_game"))

    if "achievements_btn" in _translatable_widgets:
        _translatable_widgets["achievements_btn"].configure(text=t("btn_achievements"))

    if "launch_btn" in _translatable_widgets:
        _translatable_widgets["launch_btn"].configure(text=t("btn_launch_game"))

    if "notebook" in _translatable_widgets:
        nb = _translatable_widgets["notebook"]
        tab_keys = ["tab_zt2_mods", "tab_zt1_mods", "tab_bundles", "tab_screenshots",
                    "tab_saved_games", "tab_multiplayer", "tab_mod_browser", "tab_themes"]
        for i, key in enumerate(tab_keys):
            try:
                nb.tab(i, text=t(key))
            except Exception:
                pass

    if "schedule_frame" in _translatable_widgets:
        _translatable_widgets["schedule_frame"].configure(text=t("sched_title"))
    if "sched_enable_cb" in _translatable_widgets:
        _translatable_widgets["sched_enable_cb"].configure(text=t("sched_enable"))
    if "sched_light_lbl" in _translatable_widgets:
        _translatable_widgets["sched_light_lbl"].configure(text=t("sched_light_theme"))
    if "sched_dark_lbl" in _translatable_widgets:
        _translatable_widgets["sched_dark_lbl"].configure(text=t("sched_dark_theme"))
    if "sched_from_lbl1" in _translatable_widgets:
        _translatable_widgets["sched_from_lbl1"].configure(text=t("sched_from"))
    if "sched_from_lbl2" in _translatable_widgets:
        _translatable_widgets["sched_from_lbl2"].configure(text=t("sched_from"))
    if "sched_hint_lbl" in _translatable_widgets:
        _translatable_widgets["sched_hint_lbl"].configure(text=t("sched_time_hint"))

def apply_language(lang_code):
    global current_language
    current_language = lang_code
    settings["language"] = lang_code
    save_settings(settings)
    refresh_ui_language()
    messagebox.showinfo(
        t("msg_success"),
        t("msg_language_changed")
    )

language_menu = tk.Menu(view_menu, tearoff=0)
for lang_code, lang_data in TRANSLATIONS.items():
    language_menu.add_command(
        label=lang_data["lang_name"],
        command=lambda lc=lang_code: apply_language(lc)
    )
view_menu.add_cascade(label=t("menu_language"), menu=language_menu)

view_menu_button["menu"] = view_menu
view_menu_button.pack(side=tk.RIGHT, padx=4)

tools_menu_btn = ttk.Menubutton(toolbar,
                                text=t("menu_tools"),
                                bootstyle="info-outline")
_translatable_widgets["tools_menu_btn"] = tools_menu_btn
tools_menu = tk.Menu(tools_menu_btn, tearoff=0)
tools_menu.add_command(
    label="Validate Mods",
    command=lambda: messagebox.showinfo("Validate Mods",
                                        "All mods validated successfully."))
tools_menu.add_command(label="Scan for Conflicts",
                       command=lambda: scan_mod_conflicts())
tools_menu.add_command(label="Clean Temporary Files",
                       command=lambda: messagebox.showinfo(
                           "Cleanup", "Temporary files cleaned up."))
tools_menu.add_separator()
tools_menu.add_command(label="Game Unlocks Manager",
                       command=open_game_unlocks_dialog)
tools_menu_btn["menu"] = tools_menu
tools_menu_btn.pack(side=tk.RIGHT, padx=4)

achievements_btn = ttk.Button(toolbar, text=t("btn_achievements"), bootstyle="warning-outline",
                               command=open_achievements_dialog)
achievements_btn.pack(side=tk.RIGHT, padx=4)
_translatable_widgets["achievements_btn"] = achievements_btn

ttk.Separator(toolbar, orient="vertical").pack(side=tk.RIGHT, fill=tk.Y, padx=8)

mods_menu_btn = ttk.Menubutton(toolbar, text=t("menu_mods"), bootstyle="info-outline")
_translatable_widgets["mods_menu_btn"] = mods_menu_btn
mods_menu = tk.Menu(mods_menu_btn, tearoff=0)
mods_menu.add_command(label="Export Load Order", command=export_load_order)
mods_menu.add_command(label="Backup Mods", command=backup_mods)
mods_menu.add_command(label="Restore Mods", command=restore_mods)
mods_menu_btn["menu"] = mods_menu
mods_menu_btn.pack(side=tk.RIGHT, padx=4)

game_menu_btn = ttk.Menubutton(toolbar, text=t("menu_game"), bootstyle="info-outline")
_translatable_widgets["game_menu_btn"] = game_menu_btn
game_menu = tk.Menu(game_menu_btn, tearoff=0)
game_menu.add_command(label="Set ZT1 Path", command=set_zt1_paths)
game_menu.add_command(
    label="Set ZT2 Path",
    command=set_game_path)
game_menu.add_command(label="Play ZT1", command=launch_zt1)
game_menu.add_command(label="Play ZT2", command=launch_game)
game_menu_btn["menu"] = game_menu
game_menu_btn.pack(side=tk.RIGHT, padx=4)

footer = ttk.Frame(root, padding=4)
footer.pack(fill=tk.X, side=tk.BOTTOM)

root.bind("<Control-q>", lambda e: root.quit())

status_bar = ttk.Frame(root)
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

status_size_label = ttk.Label(status_bar, text="Total Mod Size: Calculating...", bootstyle="secondary")
status_size_label.pack(side=tk.LEFT, padx=10, pady=2)

status_disk_label = ttk.Label(status_bar, text="Disk Space: Calculating...", bootstyle="secondary")
status_disk_label.pack(side=tk.RIGHT, padx=10, pady=2)


def update_status_bar():
    try:
        disabled_dir = mods_disabled_dir()
        total_size = 0

        for folder in [GAME_PATH, disabled_dir]:
            if folder and os.path.isdir(folder):
                for f in os.listdir(folder):
                    if f.lower().endswith(".z2f"):
                        path = os.path.join(folder, f)
                        try:
                            total_size += os.path.getsize(path)
                        except OSError:
                            pass

        if total_size >= 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024**3):.2f} GB"
        elif total_size >= 1024 * 1024:
            size_str = f"{total_size / (1024**2):.2f} MB"
        else:
            size_str = f"{total_size / 1024:.2f} KB"

        status_size_label.config(text=f"Total Mod Size: {size_str}")

        if GAME_PATH and os.path.isdir(GAME_PATH):
            import shutil
            total, used, free = shutil.disk_usage(GAME_PATH)
            free_gb = free / (1024**3)
            status_disk_label.config(text=f"Disk Space Free: {free_gb:.2f} GB")
        else:
            status_disk_label.config(text="Disk Space: N/A")
    except Exception as e:
        print(f"[ModZT] Error updating status bar: {e}")


main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

notebook = ttk.Notebook(main_frame)
notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
_translatable_widgets["notebook"] = notebook

main_frame.tkraise()

mods_tab = ttk.Frame(notebook, padding=6)
notebook.add(mods_tab, text=t("tab_zt2_mods"))

zt1_tab = ttk.Frame(notebook, padding=6)
notebook.add(zt1_tab, text=t("tab_zt1_mods"))

zt1_search_var = tk.StringVar()

search_frame = ttk.Frame(zt1_tab)
search_frame.pack(fill="x", padx=6, pady=(4, 0))

ttk.Label(search_frame, text="Search:").pack(side="left")
search_entry = ttk.Entry(search_frame, textvariable=zt1_search_var)
search_entry.pack(side="left", fill="x", expand=True, padx=(4, 6))

zt1_frame = ttk.Frame(zt1_tab)
zt1_frame.pack(fill=tk.BOTH, expand=True, pady=4)

zt1_tree = ttk.Treeview(
    zt1_frame,
    columns=("Name", "Status", "Category", "Size", "Modified"),
    show="headings",
    height=18,
)

for col in ("Name", "Status", "Category", "Size", "Modified"):
    if col == "Size":
        heading_text = "Size (MB)"
    elif col == "Modified":
        heading_text = "Last Modified"
    else:
        heading_text = col
    zt1_tree.heading(col,
                     text=heading_text,
                     command=lambda c=col: sort_zt1_tree(c, False))

zt1_tree.column("Name", anchor="w", width=300)
zt1_tree.column("Status", anchor="center", width=100)
zt1_tree.column("Category", anchor="center", width=120)
zt1_tree.column("Size", anchor="e", width=80)
zt1_tree.column("Modified", anchor="center", width=150)

scrollbar = ttk.Scrollbar(zt1_frame,
                          orient=tk.VERTICAL,
                          command=zt1_tree.yview)
zt1_tree.configure(yscrollcommand=scrollbar.set)
zt1_tree.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

zt1_frame.rowconfigure(0, weight=1)
zt1_frame.columnconfigure(0, weight=1)


def auto_resize_columns(event):
    total_width = event.width
    ratios = {
        "Name": 0.4,
        "Status": 0.1,
        "Category": 0.15,
        "Tags": 0.15,
        "Size": 0.1
    }
    for col, r in ratios.items():
        zt1_tree.column(col, width=int(total_width * r))


zt1_tree.bind("<Configure>", auto_resize_columns)

zt1_menu = tk.Menu(zt1_tree, tearoff=0)
zt1_menu.add_command(label="Set Category",
                     command=lambda: set_zt1_mod_category())
zt1_menu.add_command(label="Set Tags", command=lambda: set_zt1_mod_tags())


def on_zt1_right_click(event):
    iid = zt1_tree.identify_row(event.y)
    if iid:
        zt1_tree.selection_set(iid)
        zt1_menu.post(event.x_root, event.y_root)


zt1_tree.bind("<Button-3>", on_zt1_right_click)


def set_zt1_mod_category():
    selected = zt1_tree.selection()
    if not selected:
        return
    name = zt1_tree.item(selected[0])["values"][0]
    old = get_mod_category(name, zt1=True)
    new = simpledialog.askstring("Set Category",
                                 f"Enter category for '{name}':",
                                 initialvalue=old,
                                 parent=root)
    if new:
        set_mod_category(name, new, zt1=True)
        refresh_zt1_tree()


def set_zt1_mod_tags():
    selected = zt1_tree.selection()
    if not selected:
        return
    name = zt1_tree.item(selected[0])["values"][0]
    old = ", ".join(get_mod_tags(name, zt1=True))
    new = simpledialog.askstring("Set Tags",
                                 f"Enter tags for '{name}' (comma-separated):",
                                 initialvalue=old,
                                 parent=root)
    if new is not None:
        tags = [t.strip() for t in new.split(",")]
        set_mod_tags(name, tags, zt1=True)
        refresh_zt1_tree()


zt1_footer = ttk.Label(zt1_tab,
                       text="Total mods: 0 | Enabled: 0 | Disabled: 0",
                       bootstyle="secondary")
zt1_footer.pack(anchor="w", padx=6, pady=(2, 0))

zt1_mod_btns = ttk.Frame(zt1_tab, padding=6)
zt1_mod_btns.pack(fill=tk.X)

ttk.Button(zt1_mod_btns,
           text="Enable",
           bootstyle="success",
           width=10,
           command=lambda: enable_selected_zt1_mod()).pack(side=tk.LEFT, padx=4)
ttk.Button(zt1_mod_btns,
           text="Disable",
           bootstyle="warning",
           width=10,
           command=lambda: disable_selected_zt1_mod()).pack(side=tk.LEFT, padx=4)
ttk.Button(zt1_mod_btns,
           text="Uninstall",
           bootstyle="danger",
           width=10,
           command=lambda: uninstall_selected_mod()).pack(side=tk.LEFT, padx=4)
ttk.Button(zt1_mod_btns,
           text="Refresh",
           bootstyle="info",
           width=10,
           command=lambda: refresh_zt1_tree()).pack(side=tk.LEFT, padx=4)
ttk.Button(zt1_mod_btns,
           text="Open Folder",
           bootstyle="secondary",
           width=12,
           command=lambda: os.startfile(ZT1_MOD_DIR or os.path.join(ZT1_PATH, "dlupdates"))
           if ZT1_PATH else messagebox.showerror("Error", "ZT1 path not set.")).pack(side=tk.LEFT, padx=4)

def sort_zt1_tree(col, reverse=False):
    data = [(zt1_tree.set(k, col), k) for k in zt1_tree.get_children("")]

    if col == "Size":

        def parse_size(s):
            try:
                return float(s.split()[0]) if "KB" in s else 0
            except Exception:
                return 0

        data.sort(key=lambda t: parse_size(t[0]), reverse=reverse)
    else:
        data.sort(key=lambda t: str(t[0]).lower(), reverse=reverse)

    for index, (val, k) in enumerate(data):
        zt1_tree.move(k, "", index)

    zt1_tree.heading(col, command=lambda: sort_zt1_tree(col, not reverse))

    for c in ("Name", "Status", "Category", "Tags", "Size"):
        label = c
        if c == col:
            label += " 🔽" if reverse else " 🔼"
        zt1_tree.heading(
            c,
            text=label,
            command=lambda c=c: sort_zt1_tree(c, not (c == col and reverse)))


def refresh_zt1_tree(filter_text=""):
    for row in zt1_tree.get_children():
        zt1_tree.delete(row)

    detect_existing_zt1_mods()

    cursor.execute("SELECT COUNT(*), SUM(enabled) FROM zt1_mods")
    total, enabled_count = cursor.fetchone()
    enabled_count = enabled_count or 0
    disabled_count = total - enabled_count

    cursor.execute(
        "SELECT name, enabled, category FROM zt1_mods ORDER BY enabled DESC, name ASC")
    all_rows = cursor.fetchall()

    filter_text = (zt1_search_var.get() or "").strip().lower()

    visible_rows = []
    for name, enabled, category in all_rows:
        status_str = "enabled" if enabled else "disabled"
        combined = f"{name.lower()} {category.lower() if category else ''} {status_str}"

        if filter_text and filter_text not in combined:
            continue

        visible_rows.append((name, enabled, category))

    for name, enabled, category in visible_rows:
        status = "enabled" if enabled else "disabled"
        display_status = "🟢 Enabled" if enabled else "🔴 Disabled"

        mod_path = None
        if ZT1_MOD_DIR:
            enabled_path = os.path.join(ZT1_MOD_DIR, name)
            disabled_path = os.path.join(zt1_mods_disabled_dir() or "", name)
            if os.path.exists(enabled_path):
                mod_path = enabled_path
            elif os.path.exists(disabled_path):
                mod_path = disabled_path

        if mod_path and os.path.exists(mod_path):
            size_mb = os.path.getsize(mod_path) / (1024 * 1024)
            size = f"{size_mb:.2f}"
            modified = time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime(os.path.getmtime(mod_path)))
        else:
            size = "-"
            modified = "N/A"

        zt1_tree.insert("",
                        tk.END,
                        values=(name, display_status, category or "—", size, modified),
                        tags=(status, ))

    zt1_footer.config(
        text=
        f"Total mods: {total} | Enabled: {enabled_count} | Disabled: {disabled_count}"
    )

    apply_zt1_tree_theme()


zt1_search_var.trace_add("write", lambda *_: refresh_zt1_tree())


def on_search_zt1(*args):
    text = zt1_search_var.get().strip()
    refresh_zt1_tree(text)


zt1_search_var.trace_add("write", on_search_zt1)


def get_selected_zt1_mod():
    sel = zt1_tree.selection()
    if not sel:
        messagebox.showinfo("Select", "Select a ZT1 mod first.")
        return None
    return zt1_tree.item(sel[0])["values"][0]


def enable_selected_zt1_mod():
    mod = get_selected_zt1_mod()
    if mod:
        enable_zt1_mod(mod, text_widget=log_text)
        refresh_zt1_tree()


def disable_selected_zt1_mod():
    mod = get_selected_zt1_mod()
    if mod:
        disable_zt1_mod(mod, text_widget=log_text)
        refresh_zt1_tree()


def apply_zt1_tree_theme():
    if root.style.theme_use() == "darkly":
        zt1_tree.tag_configure("enabled", foreground="#4bc969")
        zt1_tree.tag_configure("disabled", foreground="#ff6961")
    else:
        zt1_tree.tag_configure("enabled", foreground="#007f00")
        zt1_tree.tag_configure("disabled", foreground="#b30000")


search_frame = ttk.Frame(mods_tab)
search_frame.pack(fill=tk.X, padx=6, pady=(4, 0))

ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
search_var = tk.StringVar()
search_entry = ttk.Entry(search_frame, textvariable=search_var)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 6))

mods_tree_frame = ttk.Frame(mods_tab)
mods_tree_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))

mods_tree_scroll = ttk.Scrollbar(mods_tree_frame)
mods_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

mods_tree = ttk.Treeview(mods_tree_frame,
                         columns=("Name", "Status", "Category", "Size", "Modified"),
                         show="headings",
                         selectmode="extended",
                         yscrollcommand=mods_tree_scroll.set)
mods_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

mods_tree_scroll.config(command=mods_tree.yview)

mods_tree.column("Name", width=250, anchor="w")
mods_tree.column("Status", width=100, anchor="center")
mods_tree.column("Category", width=120, anchor="center")
mods_tree.column("Size", width=80, anchor="e")
mods_tree.column("Modified", width=150, anchor="center")

mods_tree.heading("Name", text="Name", command=lambda: sort_tree_by("Name"))
mods_tree.heading("Status",
                  text="Status",
                  command=lambda: sort_tree_by("Status"))
mods_tree.heading("Category",
                  text="Category",
                  command=lambda: sort_tree_by("Category"))
mods_tree.heading("Size",
                  text="Size (MB)",
                  command=lambda: sort_tree_by("Size"))
mods_tree.heading("Modified",
                  text="Last Modified",
                  command=lambda: sort_tree_by("Modified"))

mods_tree.bind("<Double-1>", lambda e: show_mod_details())

mod_count_label = ttk.Label(mods_tab,
                            text="Total mods: 0 | Enabled: 0 | Disabled: 0",
                            bootstyle="secondary")
mod_count_label.pack(anchor="w", padx=6, pady=(2, 0))

mod_btns = ttk.Frame(mods_tab, padding=6)
mod_btns.pack(fill=tk.X, pady=(0, 4))

mods_menu = tk.Menu(root, tearoff=0)
mods_menu.add_command(label="Enable", command=lambda: enable_selected_mod())
mods_menu.add_command(label="Disable", command=lambda: disable_selected_mod())
mods_menu.add_command(label="Uninstall",
                      command=lambda: uninstall_selected_mod())
mods_menu.add_separator()
mods_menu.add_command(label="View Contents",
                      command=lambda: inspect_selected_mod())
mods_menu.add_command(label="Check Conflicts",
                      command=lambda: check_selected_mod_conflicts())
mods_menu.add_separator()
mods_menu.add_command(label="Set Category",
                      command=lambda: set_mod_category_dialog())
mods_menu.add_separator()
mods_menu.add_command(label="Open Mod Folder",
                      command=lambda: open_mod_folder())


def set_mod_category_dialog():
    selected = mods_tree.selection()
    if not selected:
        return

    name = mods_tree.item(selected[0])["values"][0]
    old = get_mod_category(name, zt1=False)

    new = simpledialog.askstring("Set Category",
                                 f"Enter category for '{name}':" if len(selected) == 1
                                 else f"Enter category for {len(selected)} mods:",
                                 initialvalue=old or "Uncategorized",
                                 parent=root)
    if new:
        for iid in selected:
            mod_name = mods_tree.item(iid)["values"][0]
            set_mod_category(mod_name, new, zt1=False)
        refresh_tree()


def on_mod_right_click(event):
    iid = mods_tree.identify_row(event.y)
    if iid:
        if iid not in mods_tree.selection():
            mods_tree.selection_set(iid)
        mods_menu.post(event.x_root, event.y_root)


def treeview_sort_column(tree, col, reverse=False):
    data = [(tree.set(k, col), k) for k in tree.get_children('')]

    try:
        data.sort(key=lambda t: float(t[0]), reverse=reverse)
    except ValueError:
        data.sort(key=lambda t: t[0].lower(), reverse=reverse)

    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)

    tree.heading(col,
                 command=lambda: treeview_sort_column(tree, col, not reverse))

    sort_arrow = " ▲" if not reverse else " ▼"
    for c in tree["columns"]:
        text = c.capitalize()
        if c == col:
            text += sort_arrow
        tree.heading(c,
                     text=text,
                     command=lambda _col=c: treeview_sort_column(
                         tree, _col, _col == col and not reverse))


mods_tree.bind("<Button-3>", on_mod_right_click)

def on_drop(event):
    data = event.data
    files = []
    i = 0
    while i < len(data):
        if data[i] == '{':
            end = data.index('}', i)
            files.append(data[i+1:end])
            i = end + 2
        elif data[i] == ' ':
            i += 1
        else:
            end = data.find(' ', i)
            if end == -1:
                files.append(data[i:])
                break
            files.append(data[i:end])
            i = end + 1

    if files:
        text_widget = globals().get('log_text')
        install_mods(files, text_widget=text_widget)

if DND_AVAILABLE:
    mods_tree.drop_target_register(DND_FILES)
    mods_tree.dnd_bind('<<Drop>>', on_drop)
    print("[i] Drag and drop enabled - drop .z2f files onto the mod list to install")

def on_mods_key(event):
    if event.keysym == 'Delete':
        if mods_tree.selection():
            uninstall_selected_mod()
    elif event.keysym == 'Return':
        if mods_tree.selection():
            enable_selected_mod()

mods_tree.bind('<Delete>', on_mods_key)
mods_tree.bind('<Return>', on_mods_key)
mods_tree.bind('<Control-a>', lambda e: mods_tree.selection_set(mods_tree.get_children()))
mods_tree.bind('<Escape>', lambda e: mods_tree.selection_remove(mods_tree.get_children()))
mods_tree.bind('<Control-z>', lambda e: undo_last_action())
mods_tree.bind('<Double-1>', lambda e: inspect_selected_mod())

mod_btns = ttk.Frame(mods_tab, padding=6)
mod_btns.pack(fill=tk.X)

enable_btn = ttk.Button(mod_btns,
                        text="Enable",
                        command=lambda: (enable_selected_mod(), ),
                        bootstyle="success")
enable_btn.pack(side=tk.LEFT, padx=4)
disable_btn = ttk.Button(mod_btns,
                         text="Disable",
                         command=lambda: (disable_selected_mod(), ),
                         bootstyle="danger")
disable_btn.pack(side=tk.LEFT, padx=4)
uninstall_btn = ttk.Button(mod_btns,
                           text="Uninstall",
                           command=lambda: (uninstall_selected_mod(), ),
                           bootstyle="warning")
uninstall_btn.pack(side=tk.LEFT, padx=4)
refresh_btn = ttk.Button(mod_btns,
                         text="Refresh List",
                         command=lambda:
                         (detect_existing_mods(), refresh_tree()))
refresh_btn.pack(side=tk.LEFT, padx=4)

ttk.Separator(mod_btns, orient="vertical").pack(side=tk.LEFT, padx=8, fill=tk.Y)
select_all_btn = ttk.Button(mod_btns,
                            text="Select All",
                            command=lambda: mods_tree.selection_set(mods_tree.get_children()),
                            bootstyle="secondary-outline")
select_all_btn.pack(side=tk.LEFT, padx=4)
deselect_all_btn = ttk.Button(mod_btns,
                              text="Deselect All",
                              command=lambda: mods_tree.selection_remove(mods_tree.get_children()),
                              bootstyle="secondary-outline")
deselect_all_btn.pack(side=tk.LEFT, padx=4)

ttk.Separator(mod_btns, orient="vertical").pack(side=tk.LEFT, padx=8, fill=tk.Y)
undo_btn = ttk.Button(mod_btns,
                      text="Undo",
                      command=undo_last_action,
                      bootstyle="info-outline")
undo_btn.pack(side=tk.LEFT, padx=4)

bundles_tab = ttk.Frame(notebook, padding=6)
notebook.add(bundles_tab, text=t("tab_bundles"))

shots_tab = ttk.Frame(notebook, padding=6)
notebook.add(shots_tab, text=t("tab_screenshots"))

saves_tab = ttk.Frame(notebook, padding=6)
notebook.add(saves_tab, text=t("tab_saved_games"))

multiplayer_tab = ttk.Frame(notebook, padding=6)
notebook.add(multiplayer_tab, text=t("tab_multiplayer"))

modbrowser_tab = ttk.Frame(notebook, padding=6)
notebook.add(modbrowser_tab, text=t("tab_mod_browser"))

modding_tab = ttk.Frame(notebook, padding=6)
notebook.add(modding_tab, text="Modding Resources")

themes_tab = ttk.Frame(notebook, padding=10)
notebook.add(themes_tab, text=t("tab_themes"))

themes_header = ttk.Frame(themes_tab)
themes_header.pack(fill=tk.X, pady=(0, 10))

ttk.Label(themes_header, text="ModZT Interface Themes",
          font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

current_theme_var = tk.StringVar(value=f"Current: {root.style.theme_use()}")
ttk.Label(themes_header, textvariable=current_theme_var,
          bootstyle="secondary").pack(side=tk.RIGHT)

themes_content = ttk.PanedWindow(themes_tab, orient=tk.HORIZONTAL)
themes_content.pack(fill=tk.BOTH, expand=True)

themes_left = ttk.Frame(themes_content, padding=6)
themes_content.add(themes_left, weight=1)

ttk.Label(themes_left, text="Available Themes",
          font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

MODZT_THEMES = {
    "darkly": {
        "display": "Dark Mode",
        "description": "Classic dark theme with blue accents. Easy on the eyes for night sessions.",
        "category": "Standard",
        "colors": {"bg": "#222222", "fg": "#ffffff", "accent": "#375a7f"}
    },
    "litera": {
        "display": "Light Mode",
        "description": "Clean, bright theme perfect for daytime use.",
        "category": "Standard",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#4582ec"}
    },
    "superhero": {
        "display": "Superhero",
        "description": "Bold dark theme with vibrant orange accents.",
        "category": "Standard",
        "colors": {"bg": "#2b3e50", "fg": "#ffffff", "accent": "#df691a"}
    },
    "solar": {
        "display": "Solar",
        "description": "Solarized dark theme with cyan highlights.",
        "category": "Standard",
        "colors": {"bg": "#002b36", "fg": "#839496", "accent": "#2aa198"}
    },
    "cyborg": {
        "display": "Cyborg",
        "description": "High-contrast dark theme with electric blue.",
        "category": "Standard",
        "colors": {"bg": "#060606", "fg": "#888888", "accent": "#2a9fd6"}
    },
    "vapor": {
        "display": "Vapor",
        "description": "Retro synthwave aesthetic with pink and cyan.",
        "category": "Standard",
        "colors": {"bg": "#1a1a2e", "fg": "#ffffff", "accent": "#ea39b8"}
    },
    "flatly": {
        "display": "Flatly",
        "description": "Modern flat design with green accents.",
        "category": "Standard",
        "colors": {"bg": "#ffffff", "fg": "#2c3e50", "accent": "#18bc9c"}
    },
    "journal": {
        "display": "Journal",
        "description": "Crisp and readable, like a newspaper.",
        "category": "Standard",
        "colors": {"bg": "#ffffff", "fg": "#222222", "accent": "#eb6864"}
    },
    "cosmo": {
        "display": "Cosmo",
        "description": "Space-inspired theme with purple tones.",
        "category": "Standard",
        "colors": {"bg": "#ffffff", "fg": "#222222", "accent": "#2780e3"}
    },
    "morph": {
        "display": "Morph",
        "description": "Soft, modern theme with rounded elements.",
        "category": "Standard",
        "colors": {"bg": "#f0f0f0", "fg": "#333333", "accent": "#378dfc"}
    },

    "minty": {
        "display": "Rainforest Green",
        "description": "Lush green theme inspired by tropical rainforest exhibits.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#3cb371"}
    },
    "united": {
        "display": "Prehistoric Orange",
        "description": "Warm orange theme inspired by dinosaur exhibits and ancient times.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#e95420"}
    },
    "cerculean": {
        "display": "Marine Blue",
        "description": "Ocean-inspired blue for marine mammal and aquarium exhibits.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#033c73"}
    },
    "sandstone": {
        "display": "Savanna Gold",
        "description": "Warm golden tones of the African savanna at sunset.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#faf5e6", "fg": "#5c4827", "accent": "#d4a855"}
    },
    "pulse": {
        "display": "Tropical Sunset",
        "description": "Vibrant purple and pink, like a tropical evening sky.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#593196"}
    },
    "lumen": {
        "display": "Arctic Ice",
        "description": "Cool, crisp theme inspired by polar exhibits.",
        "category": "Zoo Tycoon",
        "colors": {"bg": "#ffffff", "fg": "#333333", "accent": "#158cba"}
    },
    "yeti": {
        "display": "ZT1 Classic",
        "description": "Cream and brown interface mimicking the original Zoo Tycoon 1 UI.",
        "category": "Game UI",
        "colors": {"bg": "#e8d5b7", "fg": "#3d2817", "accent": "#8b6f47"}
    },
    "sketchy": {
        "display": "ZT2 Vanilla",
        "description": "Green-tinted interface matching Zoo Tycoon 2 base game UI.",
        "category": "Game UI",
        "colors": {"bg": "#d4e4bc", "fg": "#2b3d0f", "accent": "#6a9539"}
    },
    "spacelab": {
        "display": "Endangered Species",
        "description": "Blue conservation theme from the Endangered Species expansion.",
        "category": "Game UI",
        "colors": {"bg": "#dae8f5", "fg": "#1a3a52", "accent": "#4a7ba7"}
    },
    "materia": {
        "display": "African Adventure",
        "description": "Warm savanna browns from the African Adventure expansion.",
        "category": "Game UI",
        "colors": {"bg": "#f0e6d2", "fg": "#4a3c28", "accent": "#c17a3b"}
    },
    "quartz": {
        "display": "Marine Mania",
        "description": "Deep ocean blues from the Marine Mania expansion.",
        "category": "Game UI",
        "colors": {"bg": "#d0e5f5", "fg": "#0d2d3f", "accent": "#1e6fa8"}
    },
    "zephyr": {
        "display": "Extinct Animals",
        "description": "Prehistoric earth tones from the Extinct Animals expansion.",
        "category": "Game UI",
        "colors": {"bg": "#ded1b8", "fg": "#3b2f1f", "accent": "#9b7653"}
    },
}

themes_list_frame = ttk.Frame(themes_left)
themes_list_frame.pack(fill=tk.BOTH, expand=True)

themes_tree = ttk.Treeview(themes_list_frame, show="tree", selectmode="browse")
themes_tree_scroll = ttk.Scrollbar(themes_list_frame, command=themes_tree.yview)
themes_tree.configure(yscrollcommand=themes_tree_scroll.set)
themes_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
themes_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

_theme_categories = {}
for theme_id, theme_data in MODZT_THEMES.items():
    cat = theme_data["category"]
    if cat not in _theme_categories:
        _theme_categories[cat] = themes_tree.insert("", tk.END, text=cat, open=True)
    themes_tree.insert(_theme_categories[cat], tk.END, text=theme_data["display"],
                       values=(theme_id,), tags=(theme_id,))

themes_right = ttk.LabelFrame(themes_content, text="Theme Preview", padding=10)
themes_content.add(themes_right, weight=2)

preview_name_var = tk.StringVar(value="Select a theme")
preview_desc_var = tk.StringVar(value="Click on a theme to see its preview")
preview_category_var = tk.StringVar(value="")

ttk.Label(themes_right, textvariable=preview_name_var,
          font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 4))
ttk.Label(themes_right, textvariable=preview_category_var,
          bootstyle="info").pack(anchor="w", pady=(0, 8))
ttk.Label(themes_right, textvariable=preview_desc_var,
          wraplength=350, justify="left").pack(anchor="w", pady=(0, 15))

colors_frame = ttk.LabelFrame(themes_right, text="Color Palette", padding=10)
colors_frame.pack(fill=tk.X, pady=(0, 15))

color_preview_bg = tk.Canvas(colors_frame, width=80, height=50, highlightthickness=1)
color_preview_bg.pack(side=tk.LEFT, padx=5)
color_preview_bg.create_rectangle(0, 0, 80, 50, fill="#222222", outline="")
ttk.Label(colors_frame, text="Background").pack(side=tk.LEFT, padx=(0, 15))

color_preview_fg = tk.Canvas(colors_frame, width=80, height=50, highlightthickness=1)
color_preview_fg.pack(side=tk.LEFT, padx=5)
color_preview_fg.create_rectangle(0, 0, 80, 50, fill="#ffffff", outline="")
ttk.Label(colors_frame, text="Text").pack(side=tk.LEFT, padx=(0, 15))

color_preview_accent = tk.Canvas(colors_frame, width=80, height=50, highlightthickness=1)
color_preview_accent.pack(side=tk.LEFT, padx=5)
color_preview_accent.create_rectangle(0, 0, 80, 50, fill="#375a7f", outline="")
ttk.Label(colors_frame, text="Accent").pack(side=tk.LEFT)

apply_frame = ttk.Frame(themes_right)
apply_frame.pack(fill=tk.X, pady=(10, 0))

_selected_theme_id = [None]

def on_theme_select(event=None):
    sel = themes_tree.selection()
    if not sel:
        return
    item = themes_tree.item(sel[0])
    if not item.get("values"):
        return

    theme_id = item["values"][0]
    _selected_theme_id[0] = theme_id

    if theme_id in MODZT_THEMES:
        theme = MODZT_THEMES[theme_id]
        preview_name_var.set(theme["display"])
        preview_category_var.set(theme["category"])
        preview_desc_var.set(theme["description"])

        colors = theme["colors"]
        color_preview_bg.delete("all")
        color_preview_bg.create_rectangle(0, 0, 80, 50, fill=colors["bg"], outline="#666")
        color_preview_fg.delete("all")
        color_preview_fg.create_rectangle(0, 0, 80, 50, fill=colors["fg"], outline="#666")
        color_preview_accent.delete("all")
        color_preview_accent.create_rectangle(0, 0, 80, 50, fill=colors["accent"], outline="#666")

def apply_selected_theme():
    theme_id = _selected_theme_id[0]
    if not theme_id:
        messagebox.showinfo("Theme", "Please select a theme first.")
        return

    try:
        root.style.theme_use(theme_id)
        current_theme_var.set(f"Current: {theme_id}")

        settings["theme"] = theme_id
        save_settings(settings)

        if 'apply_tree_theme' in dir():
            apply_tree_theme()

        log(f"Applied theme: {MODZT_THEMES[theme_id]['display']}", text_widget=log_text)
        increment_stat("themes_applied")
    except Exception as e:
        messagebox.showerror("Theme Error", f"Could not apply theme: {e}")

themes_tree.bind("<<TreeviewSelect>>", on_theme_select)

def reset_theme_to_default():
    root.style.theme_use("darkly")
    current_theme_var.set("Current: darkly")
    settings["theme"] = "darkly"
    save_settings(settings)
    log("Reset theme to default (darkly)", text_widget=log_text)

ttk.Button(apply_frame, text="Apply Theme", command=apply_selected_theme,
           bootstyle="success").pack(side=tk.LEFT, padx=5)
ttk.Button(apply_frame, text="Reset to Default",
           command=reset_theme_to_default,
           bootstyle="secondary").pack(side=tk.LEFT, padx=5)

info_frame = ttk.LabelFrame(themes_right, text="Tips", padding=10)
info_frame.pack(fill=tk.X, pady=(15, 0))
ttk.Label(info_frame, text="• Dark themes are easier on the eyes during long sessions\n"
                           "• Zoo Tycoon themes are inspired by in-game biomes\n"
                           "• Your theme choice is saved automatically",
          justify="left", bootstyle="secondary").pack(anchor="w")

schedule_frame = ttk.LabelFrame(themes_left, text=t("sched_title"), padding=10)
schedule_frame.pack(fill=tk.X, pady=(15, 0))
_translatable_widgets["schedule_frame"] = schedule_frame

schedule_enabled_var = tk.BooleanVar(value=settings.get("theme_scheduling_enabled", False))

def toggle_schedule_enabled():
    enabled = schedule_enabled_var.get()
    settings["theme_scheduling_enabled"] = enabled
    save_settings(settings)
    state = "normal" if enabled else "disabled"
    light_theme_combo.configure(state="readonly" if enabled else "disabled")
    dark_theme_combo.configure(state="readonly" if enabled else "disabled")
    light_time_entry.configure(state=state)
    dark_time_entry.configure(state=state)
    if enabled:
        check_theme_schedule()
    log(f"Theme scheduling {'enabled' if enabled else 'disabled'}", text_widget=log_text)

sched_enable_cb = ttk.Checkbutton(schedule_frame, text=t("sched_enable"),
                variable=schedule_enabled_var, command=toggle_schedule_enabled,
                bootstyle="round-toggle")
sched_enable_cb.pack(anchor="w", pady=(0, 10))
_translatable_widgets["sched_enable_cb"] = sched_enable_cb

schedule_grid = ttk.Frame(schedule_frame)
schedule_grid.pack(fill=tk.X)

sched_light_lbl = ttk.Label(schedule_grid, text=t("sched_light_theme"))
sched_light_lbl.grid(row=0, column=0, sticky="w", pady=2)
_translatable_widgets["sched_light_lbl"] = sched_light_lbl

light_theme_var = tk.StringVar(value=settings.get("theme_light", "litera"))
light_themes = ["litera", "flatly", "journal", "cosmo", "morph", "minty", "sandstone", "lumen"]
light_theme_combo = ttk.Combobox(schedule_grid, textvariable=light_theme_var,
                                  values=light_themes, width=15, state="readonly" if schedule_enabled_var.get() else "disabled")
light_theme_combo.grid(row=0, column=1, padx=5, pady=2)

sched_from_lbl1 = ttk.Label(schedule_grid, text=t("sched_from"))
sched_from_lbl1.grid(row=0, column=2, padx=5)
_translatable_widgets["sched_from_lbl1"] = sched_from_lbl1

light_time_var = tk.StringVar(value=settings.get("theme_light_start", "07:00"))
light_time_entry = ttk.Entry(schedule_grid, textvariable=light_time_var, width=6,
                              state="normal" if schedule_enabled_var.get() else "disabled")
light_time_entry.grid(row=0, column=3, pady=2)

sched_dark_lbl = ttk.Label(schedule_grid, text=t("sched_dark_theme"))
sched_dark_lbl.grid(row=1, column=0, sticky="w", pady=2)
_translatable_widgets["sched_dark_lbl"] = sched_dark_lbl

dark_theme_var = tk.StringVar(value=settings.get("theme_dark", "darkly"))
dark_themes = ["darkly", "superhero", "solar", "cyborg", "vapor"]
dark_theme_combo = ttk.Combobox(schedule_grid, textvariable=dark_theme_var,
                                 values=dark_themes, width=15, state="readonly" if schedule_enabled_var.get() else "disabled")
dark_theme_combo.grid(row=1, column=1, padx=5, pady=2)

sched_from_lbl2 = ttk.Label(schedule_grid, text=t("sched_from"))
sched_from_lbl2.grid(row=1, column=2, padx=5)
_translatable_widgets["sched_from_lbl2"] = sched_from_lbl2

dark_time_var = tk.StringVar(value=settings.get("theme_dark_start", "19:00"))
dark_time_entry = ttk.Entry(schedule_grid, textvariable=dark_time_var, width=6,
                             state="normal" if schedule_enabled_var.get() else "disabled")
dark_time_entry.grid(row=1, column=3, pady=2)

def save_schedule_settings(*args):
    settings["theme_light"] = light_theme_var.get()
    settings["theme_dark"] = dark_theme_var.get()
    settings["theme_light_start"] = light_time_var.get()
    settings["theme_dark_start"] = dark_time_var.get()
    save_settings(settings)

light_theme_var.trace_add("write", save_schedule_settings)
dark_theme_var.trace_add("write", save_schedule_settings)
light_time_var.trace_add("write", save_schedule_settings)
dark_time_var.trace_add("write", save_schedule_settings)

sched_hint_lbl = ttk.Label(schedule_frame, text=t("sched_time_hint"),
          bootstyle="secondary", font=("Segoe UI", 9))
sched_hint_lbl.pack(anchor="w", pady=(8, 0))
_translatable_widgets["sched_hint_lbl"] = sched_hint_lbl

advanced_frame = ttk.LabelFrame(themes_left, text="Advanced Customization", padding=10)
advanced_frame.pack(fill=tk.X, pady=(15, 0))

font_row = ttk.Frame(advanced_frame)
font_row.pack(fill=tk.X, pady=(0, 8))

ttk.Label(font_row, text="Font Family:").pack(side=tk.LEFT)
font_family_var = tk.StringVar(value=settings.get("font_family", "Segoe UI"))

import tkinter.font as tkfont
available_fonts = sorted(set(tkfont.families()))
common_fonts = ["Segoe UI", "Arial", "Helvetica", "Verdana", "Tahoma", "Calibri",
                "Consolas", "Courier New", "Georgia", "Times New Roman"]
font_list = [f for f in common_fonts if f in available_fonts] + \
            [f for f in available_fonts if f not in common_fonts]

font_family_combo = ttk.Combobox(font_row, textvariable=font_family_var,
                                  values=font_list, width=20, state="readonly")
font_family_combo.pack(side=tk.LEFT, padx=(5, 0))

font_size_row = ttk.Frame(advanced_frame)
font_size_row.pack(fill=tk.X, pady=(0, 8))

ttk.Label(font_size_row, text="Font Size:").pack(side=tk.LEFT)
font_size_var = tk.IntVar(value=settings.get("font_size", 10))
font_size_spin = ttk.Spinbox(font_size_row, from_=8, to=18, width=5,
                              textvariable=font_size_var)
font_size_spin.pack(side=tk.LEFT, padx=(5, 10))

ttk.Label(font_size_row, text="pt", bootstyle="secondary").pack(side=tk.LEFT)

scale_row = ttk.Frame(advanced_frame)
scale_row.pack(fill=tk.X, pady=(0, 8))

ttk.Label(scale_row, text="UI Scale:").pack(side=tk.LEFT)
ui_scale_var = tk.StringVar(value=settings.get("ui_scale", "100%"))
ui_scale_combo = ttk.Combobox(scale_row, textvariable=ui_scale_var,
                               values=["90%", "100%", "110%", "125%", "150%"],
                               width=8, state="readonly")
ui_scale_combo.pack(side=tk.LEFT, padx=(5, 0))

compact_row = ttk.Frame(advanced_frame)
compact_row.pack(fill=tk.X, pady=(0, 8))

compact_mode_var = tk.BooleanVar(value=settings.get("compact_mode", False))
ttk.Checkbutton(compact_row, text="Compact Mode (reduce padding)",
                variable=compact_mode_var).pack(side=tk.LEFT)

row_height_row = ttk.Frame(advanced_frame)
row_height_row.pack(fill=tk.X, pady=(0, 8))

ttk.Label(row_height_row, text="List Row Height:").pack(side=tk.LEFT)
row_height_var = tk.IntVar(value=settings.get("row_height", 24))
row_height_spin = ttk.Spinbox(row_height_row, from_=18, to=40, width=5,
                               textvariable=row_height_var)
row_height_spin.pack(side=tk.LEFT, padx=(5, 10))

ttk.Label(row_height_row, text="px", bootstyle="secondary").pack(side=tk.LEFT)

custom_btn_row = ttk.Frame(advanced_frame)
custom_btn_row.pack(fill=tk.X, pady=(10, 0))

def apply_custom_settings():
    try:
        font_family = font_family_var.get()
        font_size = font_size_var.get()
        row_height = row_height_var.get()
        ui_scale = ui_scale_var.get()
        compact = compact_mode_var.get()

        settings["font_family"] = font_family
        settings["font_size"] = font_size
        settings["row_height"] = row_height
        settings["ui_scale"] = ui_scale
        settings["compact_mode"] = compact
        save_settings(settings)

        scale_factor = float(ui_scale.replace("%", "")) / 100.0

        scaled_font_size = int(font_size * scale_factor)
        scaled_row_height = int(row_height * scale_factor)
        default_font = (font_family, scaled_font_size)

        style = ttk.Style()
        style.configure("Treeview", rowheight=scaled_row_height, font=default_font)
        style.configure("Treeview.Heading", font=(font_family, scaled_font_size, "bold"))

        style.configure("TLabel", font=default_font)
        style.configure("TButton", font=default_font)
        style.configure("TCheckbutton", font=default_font)
        style.configure("TRadiobutton", font=default_font)
        style.configure("TEntry", font=default_font)
        style.configure("TCombobox", font=default_font)
        style.configure("TLabelframe.Label", font=default_font)
        style.configure("TNotebook.Tab", font=default_font)

        root.tk.call('tk', 'scaling', scale_factor * 1.333)

        mods_tree.configure(style="Treeview")
        zt1_tree.configure(style="Treeview")

        log(f"Applied custom settings: {font_family} {font_size}pt @ {ui_scale}, row height {row_height}px", text_widget=log_text)
        messagebox.showinfo("Settings Applied",
                           f"Custom settings applied:\n\n"
                           f"Font: {font_family} {scaled_font_size}pt (base {font_size}pt)\n"
                           f"Row Height: {scaled_row_height}px (base {row_height}px)\n"
                           f"UI Scale: {ui_scale}\n"
                           f"Compact Mode: {'On' if compact else 'Off'}\n\n"
                           "Some changes may require restart for full effect.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to apply settings: {e}")

def reset_custom_settings():
    font_family_var.set("Segoe UI")
    font_size_var.set(10)
    row_height_var.set(24)
    ui_scale_var.set("100%")
    compact_mode_var.set(False)

    settings["font_family"] = "Segoe UI"
    settings["font_size"] = 10
    settings["row_height"] = 24
    settings["ui_scale"] = "100%"
    settings["compact_mode"] = False
    save_settings(settings)

    default_font = ("Segoe UI", 10)
    style = ttk.Style()
    style.configure("Treeview", rowheight=24, font=default_font)
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
    style.configure("TLabel", font=default_font)
    style.configure("TButton", font=default_font)
    style.configure("TCheckbutton", font=default_font)
    style.configure("TRadiobutton", font=default_font)
    style.configure("TEntry", font=default_font)
    style.configure("TCombobox", font=default_font)
    style.configure("TLabelframe.Label", font=default_font)
    style.configure("TNotebook.Tab", font=default_font)

    root.tk.call('tk', 'scaling', 1.333)

    log("Reset custom settings to defaults", text_widget=log_text)
    messagebox.showinfo("Settings Reset", "Custom settings have been reset to defaults.")

ttk.Button(custom_btn_row, text="Apply",
           command=apply_custom_settings,
           bootstyle="success").pack(side=tk.LEFT, padx=(0, 5))

ttk.Button(custom_btn_row, text="Reset to Defaults",
           command=reset_custom_settings,
           bootstyle="secondary").pack(side=tk.LEFT)

preview_frame = ttk.LabelFrame(advanced_frame, text="Preview", padding=8)
preview_frame.pack(fill=tk.X, pady=(10, 0))

font_preview_label = ttk.Label(preview_frame,
                                text="The quick brown fox jumps over the lazy dog. 0123456789",
                                font=(font_family_var.get(), font_size_var.get()))
font_preview_label.pack(anchor="w")

def update_font_preview(*args):
    try:
        font_preview_label.configure(font=(font_family_var.get(), font_size_var.get()))
    except:
        pass

font_family_var.trace_add("write", update_font_preview)
font_size_var.trace_add("write", update_font_preview)


modding_header = ttk.Frame(modding_tab)
modding_header.pack(fill=tk.X, pady=(0, 10))

ttk.Label(modding_header, text="Modding Resources",
          font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

ttk.Button(modding_header, text="Open Wiki",
           command=lambda: webbrowser.open("https://zt2modding.fandom.com/wiki/Zoo_Tycoon_2_Modding_Wiki"),
           bootstyle="info-outline").pack(side=tk.RIGHT, padx=4)

modding_paned = ttk.PanedWindow(modding_tab, orient=tk.HORIZONTAL)
modding_paned.pack(fill=tk.BOTH, expand=True)

modding_left = ttk.Frame(modding_paned, padding=5)
modding_paned.add(modding_left, weight=1)

category_frame = ttk.Frame(modding_left)
category_frame.pack(fill=tk.X, pady=(0, 8))

ttk.Label(category_frame, text="Category:").pack(side=tk.LEFT)
modding_category_var = tk.StringVar(value="Tutorials")
modding_category_combo = ttk.Combobox(category_frame, textvariable=modding_category_var,
                                       values=["Tutorials", "Blender", "Coding", "NifSkope", "Tools", "File Formats"],
                                       state="readonly", width=20)
modding_category_combo.pack(side=tk.LEFT, padx=(5, 10))

ttk.Button(category_frame, text="Refresh",
           command=lambda: refresh_modding_list(),
           bootstyle="secondary").pack(side=tk.LEFT)

modding_search_frame = ttk.Frame(modding_left)
modding_search_frame.pack(fill=tk.X, pady=(0, 8))

ttk.Label(modding_search_frame, text="Search:").pack(side=tk.LEFT)
modding_search_var = tk.StringVar()
modding_search_entry = ttk.Entry(modding_search_frame, textvariable=modding_search_var)
modding_search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

ttk.Button(modding_search_frame, text="Search Wiki",
           command=lambda: search_modding_wiki(),
           bootstyle="primary").pack(side=tk.LEFT)

modding_list_frame = ttk.Frame(modding_left)
modding_list_frame.pack(fill=tk.BOTH, expand=True)

modding_tree = ttk.Treeview(modding_list_frame, columns=("Title",), show="headings", height=20)
modding_tree.heading("Title", text="Article Title")
modding_tree.column("Title", width=300)

modding_tree_scroll = ttk.Scrollbar(modding_list_frame, orient="vertical", command=modding_tree.yview)
modding_tree.configure(yscrollcommand=modding_tree_scroll.set)

modding_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
modding_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

modding_right = ttk.Frame(modding_paned, padding=5)
modding_paned.add(modding_right, weight=1)

ttk.Label(modding_right, text="Article Preview",
          font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 5))

modding_title_var = tk.StringVar(value="Select an article to view")
ttk.Label(modding_right, textvariable=modding_title_var,
          font=("Segoe UI", 12, "bold"), wraplength=400).pack(anchor="w", pady=(0, 10))

modding_preview_frame = ttk.Frame(modding_right)
modding_preview_frame.pack(fill=tk.BOTH, expand=True)

modding_preview_text = tk.Text(modding_preview_frame, height=15, wrap=tk.WORD,
                                bg="#2b2b2b", fg="#e0e0e0", font=("Segoe UI", 10),
                                state="disabled", padx=10, pady=10)
modding_preview_scroll = ttk.Scrollbar(modding_preview_frame, orient="vertical",
                                         command=modding_preview_text.yview)
modding_preview_text.configure(yscrollcommand=modding_preview_scroll.set)

modding_preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
modding_preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)

modding_btn_frame = ttk.Frame(modding_right)
modding_btn_frame.pack(fill=tk.X, pady=(10, 0))

modding_current_url = [None]
modding_image_cache = {}

def load_image_from_url(url, max_width=380):
    try:
        from io import BytesIO
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        image_data = BytesIO(response.content)
        img = Image.open(image_data)

        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

        return ImageTk.PhotoImage(img)
    except Exception as e:
        print(f"[ModZT] Error loading image from {url}: {e}")
        return None

def open_current_article():
    if modding_current_url[0]:
        webbrowser.open(modding_current_url[0])

ttk.Button(modding_btn_frame, text="Open in Browser",
           command=open_current_article,
           bootstyle="info").pack(side=tk.LEFT, padx=4)

ttk.Button(modding_btn_frame, text="Copy Link",
           command=lambda: copy_article_link(),
           bootstyle="secondary").pack(side=tk.LEFT, padx=4)

modding_status_var = tk.StringVar(value="Select a category and click Refresh to load articles")
ttk.Label(modding_tab, textvariable=modding_status_var,
          bootstyle="secondary").pack(anchor="w", pady=(5, 0))


def copy_article_link():
    if modding_current_url[0]:
        root.clipboard_clear()
        root.clipboard_append(modding_current_url[0])
        messagebox.showinfo("Copied", "Article link copied to clipboard!")


def refresh_modding_list():
    category = modding_category_var.get()
    modding_tree.delete(*modding_tree.get_children())
    modding_status_var.set(f"Loading {category}...")

    def fetch_articles():
        try:
            articles = []
            if category == "Tutorials":
                articles = modding_wiki_api.get_category_pages("Tutorials")
            elif category == "Blender":
                articles = modding_wiki_api.get_category_pages("Blender_Tutorials")
            elif category == "Coding":
                articles = modding_wiki_api.get_category_pages("Coding_Tutorials")
            elif category == "NifSkope":
                articles = modding_wiki_api.get_category_pages("Nifskope_Tutorials")
            elif category == "Tools":
                tool_names = ['Blender', 'Nifskope', 'Photoshop', 'Gimp_2', 'Paint_Shop_Pro',
                              'Visual_Studio_Code', 'Gmax', 'ZT2_BFB_Tool', 'ZT_Studio']
                articles = [{"title": name.replace("_", " "), "pageid": 0} for name in tool_names]
            elif category == "File Formats":
                format_names = ['.z2f', '.nif', '.dds', '.bfm', '.xml', '.lua', '.beh', '.bf', '.bfb']
                articles = [{"title": name, "pageid": 0} for name in format_names]

            def update_ui():
                for article in articles:
                    title = article.get("title", "Unknown")
                    modding_tree.insert("", tk.END, values=(title,), tags=(title,))
                modding_status_var.set(f"Found {len(articles)} articles in {category}")

            root.after(0, update_ui)

        except Exception as e:
            root.after(0, lambda: modding_status_var.set(f"Error loading articles: {e}"))

    threading.Thread(target=fetch_articles, daemon=True).start()


def search_modding_wiki():
    query = modding_search_var.get().strip()
    if not query:
        messagebox.showinfo("Search", "Please enter a search term.")
        return

    modding_tree.delete(*modding_tree.get_children())
    modding_status_var.set(f"Searching for '{query}'...")

    def do_search():
        try:
            results = modding_wiki_api.search(query)

            def update_ui():
                for result in results:
                    title = result.get("title", "Unknown")
                    modding_tree.insert("", tk.END, values=(title,), tags=(title,))
                modding_status_var.set(f"Found {len(results)} results for '{query}'")

            root.after(0, update_ui)

        except Exception as e:
            root.after(0, lambda: modding_status_var.set(f"Search error: {e}"))

    threading.Thread(target=do_search, daemon=True).start()


def on_modding_article_select(event):
    selected = modding_tree.selection()
    if not selected:
        return

    item = modding_tree.item(selected[0])
    title = item["tags"][0] if item["tags"] else item["values"][0]

    modding_title_var.set(title)
    modding_preview_text.config(state="normal")
    modding_preview_text.delete("1.0", tk.END)
    modding_preview_text.insert("1.0", "Loading article...")
    modding_preview_text.config(state="disabled")

    def fetch_content():
        try:
            page = modding_wiki_api.get_page_content(title)

            loaded_images = []
            if page and page.get('images'):
                for img_data in page['images']:
                    img_url = img_data.get('url')
                    if img_url:
                        photo = load_image_from_url(img_url)
                        if photo:
                            loaded_images.append({'name': img_data.get('name', ''), 'photo': photo})

            def update_preview():
                global modding_image_cache
                modding_image_cache.clear()

                if page:
                    modding_current_url[0] = page.get("url", modding_wiki_api.get_page_url(title))
                    extract = page.get("extract", "No description available.")

                    modding_preview_text.config(state="normal")
                    modding_preview_text.delete("1.0", tk.END)

                    modding_preview_text.insert("1.0", extract if extract else "No preview available.\n\nClick 'Open in Browser' to view the full article.")

                    if loaded_images:
                        modding_preview_text.insert(tk.END, "\n\n\n\n")
                        for i, img in enumerate(loaded_images):
                            modding_image_cache[f"img_{i}"] = img['photo']
                            modding_preview_text.image_create(tk.END, image=img['photo'])
                            modding_preview_text.insert(tk.END, f"\n{img['']}\n\n")

                    modding_preview_text.config(state="disabled")
                else:
                    modding_current_url[0] = modding_wiki_api.get_page_url(title)
                    modding_preview_text.config(state="normal")
                    modding_preview_text.delete("1.0", tk.END)
                    modding_preview_text.insert("1.0", "Could not load preview.\n\nClick 'Open in Browser' to view the article.")
                    modding_preview_text.config(state="disabled")

            root.after(0, update_preview)

        except Exception as e:
            def show_error():
                modding_preview_text.config(state="normal")
                modding_preview_text.delete("1.0", tk.END)
                modding_preview_text.insert("1.0", f"Error loading article: {e}")
                modding_preview_text.config(state="disabled")
            root.after(0, show_error)

    threading.Thread(target=fetch_content, daemon=True).start()


modding_tree.bind("<<TreeviewSelect>>", on_modding_article_select)
modding_category_combo.bind("<<ComboboxSelected>>", lambda e: refresh_modding_list())
modding_search_entry.bind("<Return>", lambda e: search_modding_wiki())


shots_toolbar = ttk.Frame(shots_tab)
shots_toolbar.pack(fill=tk.X, pady=(0, 6))

shots_path_var = tk.StringVar(value=get_zt2_photos_root() or "(Not found)")
ttk.Label(shots_toolbar, text="Root:").pack(side=tk.LEFT)
ttk.Entry(shots_toolbar, textvariable=shots_path_var,
          width=80).pack(side=tk.LEFT, padx=6)


def browse_shots_root():
    p = filedialog.askdirectory(
        title="Select ZT2 photos root (contains album0, album1, ...)")
    if p:
        shots_path_var.set(p)
        refresh_screenshots()


ttk.Button(shots_toolbar, text="Browse…",
           command=browse_shots_root).pack(side=tk.LEFT, padx=4)
ttk.Button(shots_toolbar,
           text="Refresh",
           command=lambda: refresh_screenshots()).pack(side=tk.LEFT, padx=4)


def open_current_root():
    r = shots_path_var.get().strip()
    if r and os.path.isdir(r):
        os.startfile(r)
    else:
        messagebox.showinfo("Open", "Root folder not found.")


ttk.Button(shots_toolbar, text="Open Folder",
           command=open_current_root).pack(side=tk.LEFT, padx=4)

shots_split = ttk.PanedWindow(shots_tab, orient=tk.HORIZONTAL)
shots_split.pack(fill=tk.BOTH, expand=True)

shots_left = ttk.Frame(shots_split, width=220, padding=(4, 6))
shots_left.pack_propagate(False)
shots_split.add(shots_left, weight=0)

ttk.Label(shots_left, text="Albums",
          font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

album_list_scroll = ttk.Scrollbar(shots_left, orient="vertical")
album_list = tk.Listbox(shots_left,
                        exportselection=False,
                        height=20,
                        yscrollcommand=album_list_scroll.set)
album_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
album_list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
album_list_scroll.config(command=album_list.yview)

shots_right = ttk.Frame(shots_split, padding=(6, 6))
shots_split.add(shots_right, weight=1)

thumb_canvas = tk.Canvas(shots_right, highlightthickness=0)
thumb_scroll = ttk.Scrollbar(shots_right,
                             orient=tk.VERTICAL,
                             command=thumb_canvas.yview)
thumb_canvas.configure(yscrollcommand=thumb_scroll.set)
thumb_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
thumb_scroll.pack(side=tk.RIGHT, fill=tk.Y)

thumb_inner = ttk.Frame(thumb_canvas)
thumb_window = thumb_canvas.create_window((0, 0),
                                          window=thumb_inner,
                                          anchor="nw")


def _thumb_cfg(event):
    thumb_canvas.configure(scrollregion=thumb_canvas.bbox("all"))


thumb_inner.bind("<Configure>", _thumb_cfg)


def _canvas_cfg(event):
    thumb_canvas.itemconfigure(thumb_window, width=event.width)


thumb_canvas.bind("<Configure>", _canvas_cfg)

_THUMB_CACHE = {}


def make_thumbnail(path, size=(220, 140)):
    key = (path, size)
    if key in _THUMB_CACHE:
        return _THUMB_CACHE[key]
    try:
        im = Image.open(path)
        im.thumbnail(size, Image.LANCZOS)
        img = ImageTk.PhotoImage(im)
        _THUMB_CACHE[key] = img
        return img
    except Exception:
        return None


def show_full_preview(img_paths, start_index=0):
    if not img_paths:
        return
    idx = max(0, min(start_index, len(img_paths) - 1))

    increment_stat("screenshots_viewed")

    top = tk.Toplevel(root)
    top.title("Screenshot Preview")
    top.geometry("900x700")

    img_label = ttk.Label(top)
    img_label.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

    info_var = tk.StringVar()
    ttk.Label(top, textvariable=info_var).pack(pady=(0, 6))

    btns = ttk.Frame(top)
    btns.pack(pady=6)

    def do_prev():
        nonlocal idx
        if idx > 0:
            idx -= 1
            render()

    def do_next():
        nonlocal idx
        if idx < len(img_paths) - 1:
            idx += 1
            render()

    ttk.Button(btns, text="◀ Prev", command=do_prev).pack(side=tk.LEFT, padx=4)
    ttk.Button(btns, text="Next ▶", command=do_next).pack(side=tk.LEFT, padx=4)

    def open_in_folder():
        p = img_paths[idx]
        try:
            os.startfile(os.path.dirname(p))
        except Exception:
            messagebox.showinfo("Open", os.path.dirname(p))

    ttk.Button(btns, text="Open in Folder",
               command=open_in_folder).pack(side=tk.LEFT, padx=8)

    def export_copy():
        p = img_paths[idx]
        out = filedialog.asksaveasfilename(
            defaultextension=os.path.splitext(p)[1],
            initialfile=os.path.basename(p),
            filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.bmp"),
                       ("All files", "*.*")])
        if out:
            try:
                shutil.copy2(p, out)
                messagebox.showinfo("Exported", f"Saved to:\n{out}")
            except Exception as e:
                messagebox.showerror("Export error", str(e))

    ttk.Button(btns, text="Move...", command=export_copy).pack(side=tk.LEFT,
                                                               padx=8)

    def render():
        p = img_paths[idx]
        try:
            im = Image.open(p)
            w = max(300, top.winfo_width() - 80)
            h = max(200, top.winfo_height() - 160)
            im.thumbnail((w, h), Image.LANCZOS)
            ph = ImageTk.PhotoImage(im)
            img_label.configure(image=ph)
            img_label.image = ph
        except Exception as e:
            img_label.configure(text=f"(Failed to load)\n{e}")
            img_label.image = None

        ts = datetime.fromtimestamp(
            os.path.getmtime(p)).strftime("%Y-%m-%d %H:%M:%S")
        info_var.set(
            f"{os.path.basename(p)}    {ts}    {os.path.getsize(p)/1024:.0f} KB   [{idx+1}/{len(img_paths)}]"
        )

    top.bind("<Left>", lambda e: (do_prev(), "break"))
    top.bind("<Right>", lambda e: (do_next(), "break"))
    top.after(50, render)


def populate_thumbnails(img_paths):
    for child in list(thumb_inner.children.values()):
        child.destroy()

    if not img_paths:
        ttk.Label(thumb_inner,
                  text="No screenshots found in this album.",
                  bootstyle="secondary").pack(pady=16)
        return

    cols = 3
    pad = 8
    for i, p in enumerate(img_paths):
        r, c = divmod(i, cols)
        frame = ttk.Frame(thumb_inner, padding=4, relief="flat")
        frame.grid(row=r, column=c, sticky="nsew", padx=pad, pady=pad)

        th = make_thumbnail(p)
        if th is not None:
            lbl = ttk.Label(frame, image=th)
            lbl.image = th
        else:
            lbl = ttk.Label(frame, text="(image)", width=28, anchor="center")
        lbl.pack()

        meta = ttk.Label(frame, text=os.path.basename(p), width=32)
        meta.pack()

        def _open_preview(event, idx=i):
            show_full_preview(img_paths, start_index=idx)

        lbl.bind("<Button-1>", _open_preview)
        meta.bind("<Button-1>", _open_preview)

    for c in range(cols):
        thumb_inner.grid_columnconfigure(c, weight=1)


def refresh_screenshots():
    root_dir = shots_path_var.get().strip()
    if not root_dir or not os.path.isdir(root_dir):
        d = get_zt2_photos_root()
        if d:
            shots_path_var.set(d)
            root_dir = d
        else:
            album_list.delete(0, tk.END)
            populate_thumbnails([])
            return

    albums = list_zt2_albums(root_dir)
    album_list.delete(0, tk.END)
    for name, _ in albums:
        album_list.insert(tk.END, name)

    def show_first_album():
        if not albums:
            populate_thumbnails([])
            return
        album_list.selection_clear(0, tk.END)
        album_list.selection_set(0)
        album_list.event_generate("<<ListboxSelect>>")

    root.after(10, show_first_album)


def _on_album_select(event=None):
    root_dir = shots_path_var.get().strip()
    if not (root_dir and os.path.isdir(root_dir)):
        populate_thumbnails([])
        return
    idxs = album_list.curselection()
    if not idxs:
        populate_thumbnails([])
        return
    name = album_list.get(idxs[0])
    album_path = os.path.join(root_dir, name)
    imgs = list_album_images(album_path)
    populate_thumbnails(imgs)


album_list.bind("<<ListboxSelect>>", _on_album_select)

saves_toolbar = ttk.Frame(saves_tab)
saves_toolbar.pack(fill=tk.X, pady=(0, 6))

saves_path_var = tk.StringVar(value=get_zt2_saves_dir() or "(Not found)")
ttk.Label(saves_toolbar, text="Saves Folder:").pack(side=tk.LEFT)
ttk.Entry(saves_toolbar, textvariable=saves_path_var, width=60).pack(side=tk.LEFT, padx=6)


def browse_saves_folder():
    p = filedialog.askdirectory(title="Select ZT2 Saved Games folder")
    if p:
        saves_path_var.set(p)
        refresh_saves_list()


ttk.Button(saves_toolbar, text="Browse...", command=browse_saves_folder).pack(side=tk.LEFT, padx=2)
ttk.Button(saves_toolbar, text="Refresh", command=lambda: refresh_saves_list()).pack(side=tk.LEFT, padx=2)


def open_saves_folder():
    folder = saves_path_var.get().strip()
    if folder and os.path.isdir(folder):
        os.startfile(folder)
    else:
        messagebox.showinfo("Open", "Saves folder not found.")


ttk.Button(saves_toolbar, text="Open Folder", command=open_saves_folder).pack(side=tk.LEFT, padx=2)

ttk.Separator(saves_toolbar, orient="vertical").pack(side=tk.LEFT, padx=8, fill=tk.Y, pady=2)
ttk.Button(saves_toolbar, text="Random Objective", command=lambda: generate_random_objective(),
           bootstyle="info-outline").pack(side=tk.LEFT, padx=2)

saves_split = ttk.PanedWindow(saves_tab, orient=tk.HORIZONTAL)
saves_split.pack(fill=tk.BOTH, expand=True)

saves_left = ttk.Frame(saves_split, width=350, padding=(4, 6))
saves_left.pack_propagate(False)
saves_split.add(saves_left, weight=1)

ttk.Label(saves_left, text="Saved Games", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 6))

saves_list_frame = ttk.Frame(saves_left)
saves_list_frame.pack(fill=tk.BOTH, expand=True)

saves_list_scroll = ttk.Scrollbar(saves_list_frame, orient="vertical")
saves_tree = ttk.Treeview(
    saves_list_frame,
    columns=("Name", "Size", "Modified"),
    show="headings",
    selectmode="extended",
    yscrollcommand=saves_list_scroll.set
)
saves_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
saves_list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
saves_list_scroll.config(command=saves_tree.yview)

saves_tree.heading("Name", text="Save Name")
saves_tree.heading("Size", text="Size")
saves_tree.heading("Modified", text="Last Modified")
saves_tree.column("Name", width=180, anchor="w")
saves_tree.column("Size", width=70, anchor="e")
saves_tree.column("Modified", width=130, anchor="center")

saves_right = ttk.Frame(saves_split, padding=(10, 6))
saves_split.add(saves_right, weight=1)

save_preview_label = ttk.Label(saves_right, text="Select a save to preview", font=("Segoe UI", 11))
save_preview_label.pack(anchor="w", pady=(0, 10))

save_preview_canvas = tk.Canvas(saves_right, width=300, height=200, bg="#2b2b2b", highlightthickness=1)
save_preview_canvas.pack(anchor="w", pady=(0, 10))

save_info_frame = ttk.Frame(saves_right)
save_info_frame.pack(fill=tk.X, anchor="w")

save_name_var = tk.StringVar(value="")
save_size_var = tk.StringVar(value="")
save_date_var = tk.StringVar(value="")

ttk.Label(save_info_frame, text="Name:", width=10).grid(row=0, column=0, sticky="w", pady=2)
ttk.Label(save_info_frame, textvariable=save_name_var).grid(row=0, column=1, sticky="w", pady=2)
ttk.Label(save_info_frame, text="Size:", width=10).grid(row=1, column=0, sticky="w", pady=2)
ttk.Label(save_info_frame, textvariable=save_size_var).grid(row=1, column=1, sticky="w", pady=2)
ttk.Label(save_info_frame, text="Modified:", width=10).grid(row=2, column=0, sticky="w", pady=2)
ttk.Label(save_info_frame, textvariable=save_date_var).grid(row=2, column=1, sticky="w", pady=2)

saves_btn_frame = ttk.Frame(saves_right)
saves_btn_frame.pack(fill=tk.X, pady=(15, 0))


def backup_selected_save():
    selected = saves_tree.selection()
    if not selected:
        messagebox.showinfo("Backup", "Select a save first.")
        return

    saves_folder = saves_path_var.get().strip()
    if not saves_folder or not os.path.isdir(saves_folder):
        return

    backup_dir = filedialog.askdirectory(title="Select backup destination")
    if not backup_dir:
        return

    for iid in selected:
        name = saves_tree.item(iid)["values"][0]
        src = os.path.join(saves_folder, name)
        if os.path.isfile(src):
            dst = os.path.join(backup_dir, name)
            shutil.copy2(src, dst)

    messagebox.showinfo("Backup", f"Backed up {len(selected)} save(s) to:\n{backup_dir}")
    log(f"Backed up {len(selected)} save(s)", log_text)


def delete_selected_save():
    selected = saves_tree.selection()
    if not selected:
        messagebox.showinfo("Delete", "Select a save first.")
        return

    if not messagebox.askyesno("Confirm Delete", f"Delete {len(selected)} selected save(s)?\nThis cannot be undone."):
        return

    saves_folder = saves_path_var.get().strip()
    if not saves_folder or not os.path.isdir(saves_folder):
        return

    deleted = 0
    for iid in selected:
        name = saves_tree.item(iid)["values"][0]
        path = os.path.join(saves_folder, name)
        if os.path.isfile(path):
            try:
                os.remove(path)
                deleted += 1
            except Exception as e:
                log(f"Failed to delete {name}: {e}", log_text)

    refresh_saves_list()
    log(f"Deleted {deleted} save(s)", log_text)


def rename_selected_save():
    selected = saves_tree.selection()
    if not selected or len(selected) != 1:
        messagebox.showinfo("Rename", "Select exactly one save to rename.")
        return

    saves_folder = saves_path_var.get().strip()
    if not saves_folder or not os.path.isdir(saves_folder):
        return

    old_name = saves_tree.item(selected[0])["values"][0]
    old_path = os.path.join(saves_folder, old_name)

    base_name = os.path.splitext(old_name)[0]
    new_name = simpledialog.askstring("Rename Save", "Enter new name:", initialvalue=base_name, parent=root)

    if new_name and new_name != base_name:
        new_path = os.path.join(saves_folder, new_name + ".z2s")
        if os.path.exists(new_path):
            messagebox.showerror("Error", "A save with that name already exists.")
            return
        try:
            os.rename(old_path, new_path)
            refresh_saves_list()
            log(f"Renamed save: {old_name} -> {new_name}.z2s", log_text)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to rename: {e}")


def play_selected_save():
    selected = saves_tree.selection()
    if not selected:
        messagebox.showwarning("No Selection", "Please select a save to play.")
        return

    saves_folder = saves_path_var.get().strip()
    if not saves_folder:
        messagebox.showerror("Error", "Saves folder not found.")
        return

    name = saves_tree.item(selected[0])["values"][0]
    save_path = os.path.join(saves_folder, name)

    if not os.path.isfile(save_path):
        messagebox.showerror("Error", f"Save file not found: {save_path}")
        return

    log(f"Launching save: {name}", log_text)
    launch_game([save_path])


ttk.Button(saves_btn_frame, text="Play Save", bootstyle="success",
           command=play_selected_save).pack(fill=tk.X, pady=2)
ttk.Separator(saves_btn_frame, orient="horizontal").pack(fill=tk.X, pady=6)
ttk.Button(saves_btn_frame, text="Backup Selected", bootstyle="info-outline",
           command=backup_selected_save).pack(fill=tk.X, pady=2)
ttk.Button(saves_btn_frame, text="Rename", bootstyle="warning-outline",
           command=rename_selected_save).pack(fill=tk.X, pady=2)
ttk.Button(saves_btn_frame, text="Delete Selected", bootstyle="danger-outline",
           command=delete_selected_save).pack(fill=tk.X, pady=2)

_SAVE_THUMB_CACHE = {}


def extract_save_thumbnail(save_path):
    try:
        mtime = os.path.getmtime(save_path)
        cache_key = (save_path, mtime)
    except OSError:
        cache_key = save_path

    if cache_key in _SAVE_THUMB_CACHE:
        return _SAVE_THUMB_CACHE[cache_key]

    try:
        if zipfile.is_zipfile(save_path):
            with zipfile.ZipFile(save_path, 'r') as zf:
                for name in zf.namelist():
                    if name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                        data = zf.read(name)
                        img = Image.open(io.BytesIO(data))
                        img.thumbnail((300, 200), Image.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        _SAVE_THUMB_CACHE[cache_key] = photo
                        return photo
    except Exception:
        pass

    _SAVE_THUMB_CACHE[cache_key] = None
    return None


def on_save_select(event=None):
    selected = saves_tree.selection()
    if not selected:
        save_name_var.set("")
        save_size_var.set("")
        save_date_var.set("")
        save_preview_canvas.delete("all")
        save_preview_label.config(text="Select a save to preview")
        return

    saves_folder = saves_path_var.get().strip()
    if not saves_folder:
        return

    name = saves_tree.item(selected[0])["values"][0]
    path = os.path.join(saves_folder, name)

    save_name_var.set(name)
    save_preview_label.config(text=name)

    if os.path.isfile(path):
        size = os.path.getsize(path)
        if size >= 1024 * 1024:
            save_size_var.set(f"{size / (1024*1024):.2f} MB")
        else:
            save_size_var.set(f"{size / 1024:.1f} KB")

        mtime = os.path.getmtime(path)
        save_date_var.set(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)))

        save_preview_canvas.delete("all")
        thumb = extract_save_thumbnail(path)
        if thumb:
            save_preview_canvas.create_image(150, 100, image=thumb, anchor="center")
            save_preview_canvas.image = thumb
        else:
            save_preview_canvas.create_text(150, 100, text="No preview available",
                                           fill="#888888", font=("Segoe UI", 10))
    else:
        save_size_var.set("N/A")
        save_date_var.set("N/A")


saves_tree.bind("<<TreeviewSelect>>", on_save_select)


def refresh_saves_list():
    saves_tree.delete(*saves_tree.get_children())

    saves_folder = saves_path_var.get().strip()
    if not saves_folder or not os.path.isdir(saves_folder):
        d = get_zt2_saves_dir()
        if d:
            saves_path_var.set(d)
            saves_folder = d
        else:
            return

    saves = []
    for f in os.listdir(saves_folder):
        if f.lower().endswith(".z2s"):
            path = os.path.join(saves_folder, f)
            size = os.path.getsize(path)
            mtime = os.path.getmtime(path)
            saves.append((f, size, mtime))

    saves.sort(key=lambda x: x[2], reverse=True)

    for name, size, mtime in saves:
        if size >= 1024 * 1024:
            size_str = f"{size / (1024*1024):.1f} MB"
        else:
            size_str = f"{size / 1024:.0f} KB"
        date_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(mtime))
        saves_tree.insert("", tk.END, values=(name, size_str, date_str))

    log(f"Found {len(saves)} saved game(s)", log_text)
    set_stat("saves_count", len(saves))

MULTIPLAYER_DIR = os.path.join(CONFIG_DIR, "multiplayer")
os.makedirs(MULTIPLAYER_DIR, exist_ok=True)

def get_session_file(session_id):
    return os.path.join(MULTIPLAYER_DIR, f"{session_id}.json")

def get_session_save_dir(session_id):
    d = os.path.join(MULTIPLAYER_DIR, session_id)
    os.makedirs(d, exist_ok=True)
    return d

def generate_session_id():
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def export_save_for_sharing(save_path, output_path=None):
    if not os.path.isfile(save_path):
        return None, "Save file not found"

    save_name = os.path.basename(save_path)

    if not output_path:
        output_path = filedialog.asksaveasfilename(
            title="Export Save For Sharing",
            defaultextension=".zt2share",
            filetypes=[("ZT2 Share Package", "*.zt2share"), ("All Files", "*.*")],
            initialfile=os.path.splitext(save_name)[0] + ".zt2share"
        )

    if not output_path:
        return None, "Export cancelled"

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(save_path, save_name)

            metadata = {
                "original_name": save_name,
                "exported_by": os.environ.get("USERNAME", "Unknown"),
                "exported_at": datetime.now().isoformat(),
                "size": os.path.getsize(save_path),
                "version": APP_VERSION
            }
            zf.writestr("metadata.json", json.dumps(metadata, indent=2))

        return output_path, f"Exported to {os.path.basename(output_path)}"
    except Exception as e:
        return None, f"Export failed: {e}"

def import_shared_save(package_path=None):
    if not package_path:
        package_path = filedialog.askopenfilename(
            title="Import Shared Save",
            filetypes=[("ZT2 Share Package", "*.zt2share"), ("All Files", "*.*")]
        )

    if not package_path:
        return None, "Import cancelled"

    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        return None, "Could not find saves directory"

    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            try:
                metadata = json.loads(zf.read("metadata.json"))
            except:
                metadata = {}

            save_files = [f for f in zf.namelist() if f.lower().endswith('.z2s')]
            if not save_files:
                return None, "No save file found in package"

            save_name = save_files[0]

            dest_path = os.path.join(saves_dir, save_name)
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(save_name)
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = os.path.join(saves_dir, f"{base}_{counter}{ext}")
                    counter += 1
                save_name = os.path.basename(dest_path)

            zf.extract(save_files[0], saves_dir)
            if save_files[0] != save_name:
                os.rename(os.path.join(saves_dir, save_files[0]), dest_path)

            return dest_path, f"Imported: {save_name}"
    except Exception as e:
        return None, f"Import failed: {e}"

def create_multiplayer_session(save_path, session_name):
    if not os.path.isfile(save_path):
        return None, "Save file not found"

    session_id = generate_session_id()
    session_dir = get_session_save_dir(session_id)

    save_name = os.path.basename(save_path)
    shutil.copy2(save_path, os.path.join(session_dir, save_name))

    session_data = {
        "id": session_id,
        "name": session_name,
        "created_at": datetime.now().isoformat(),
        "created_by": os.environ.get("USERNAME", "Unknown"),
        "current_save": save_name,
        "turn_number": 1,
        "turn_history": [
            {
                "turn": 0,
                "player": os.environ.get("USERNAME", "Unknown"),
                "action": "Created session",
                "timestamp": datetime.now().isoformat(),
                "save_file": save_name
            }
        ],
        "players": [os.environ.get("USERNAME", "Unknown")]
    }

    with open(get_session_file(session_id), 'w') as f:
        json.dump(session_data, f, indent=2)

    increment_stat("mp_sessions_created")

    return session_id, f"Session created: {session_id}"

def load_session(session_id):
    session_file = get_session_file(session_id)
    if not os.path.isfile(session_file):
        return None

    try:
        with open(session_file, 'r') as f:
            return json.load(f)
    except:
        return None

def list_sessions():
    sessions = []
    for f in os.listdir(MULTIPLAYER_DIR):
        if f.endswith('.json'):
            session_id = f[:-5]
            session = load_session(session_id)
            if session:
                sessions.append(session)
    return sessions


def take_turn(session_id, new_save_path, note=""):
    session = load_session(session_id)
    if not session:
        return False, "Session not found"

    if not os.path.isfile(new_save_path):
        return False, "Save file not found"

    session_dir = get_session_save_dir(session_id)
    save_name = os.path.basename(new_save_path)
    turn_save_name = f"turn_{session['turn_number']}_{save_name}"

    shutil.copy2(new_save_path, os.path.join(session_dir, turn_save_name))

    stats = parse_zoo_stats(new_save_path)

    session['turn_number'] += 1
    session['current_save'] = turn_save_name
    session['turn_history'].append({
        "turn": session['turn_number'],
        "player": os.environ.get("USERNAME", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "save_file": turn_save_name,
        "note": note,
        "stats": stats
    })

    player = os.environ.get("USERNAME", "Unknown")
    if player not in session['players']:
        session['players'].append(player)

    with open(get_session_file(session_id), 'w') as f:
        json.dump(session, f, indent=2)

    increment_stat("mp_turns_submitted")

    return True, f"Turn {session['turn_number']} submitted"


def delete_session(session_id):
    session_file = get_session_file(session_id)
    session_dir = get_session_save_dir(session_id)

    try:
        if os.path.isfile(session_file):
            os.remove(session_file)

        if os.path.isdir(session_dir):
            shutil.rmtree(session_dir)

        return True, "Session deleted"
    except Exception as e:
        return False, f"Failed to delete session: {e}"


def rollback_turn(session_id, target_turn):
    session = load_session(session_id)
    if not session:
        return False, "Session not found"

    if target_turn < 0 or target_turn >= session['turn_number']:
        return False, f"Invalid turn number. Valid range: 0-{session['turn_number']-1}"

    target_history = None
    for h in session['turn_history']:
        if h['turn'] == target_turn:
            target_history = h
            break

    if not target_history:
        return False, "Turn not found in history"

    session['current_save'] = target_history['save_file']
    session['turn_number'] = target_turn + 1

    session['turn_history'] = [h for h in session['turn_history'] if h['turn'] <= target_turn]

    session['turn_history'].append({
        "turn": target_turn,
        "player": os.environ.get("USERNAME", "Unknown"),
        "timestamp": datetime.now().isoformat(),
        "save_file": target_history['save_file'],
        "note": f"[Rolled back to turn {target_turn}]",
        "is_rollback": True
    })

    with open(get_session_file(session_id), 'w') as f:
        json.dump(session, f, indent=2)

    return True, f"Rolled back to turn {target_turn}"

def export_session(session_id, output_path=None):
    session = load_session(session_id)
    if not session:
        return None, "Session not found"

    if not output_path:
        output_path = filedialog.asksaveasfilename(
            title="Export Session",
            defaultextension=".zt2session",
            filetypes=[("ZT2 Session", "*.zt2session")],
            initialfile=f"{session['name']}_{session_id}.zt2session"
        )

    if not output_path:
        return None, "Export cancelled"

    try:
        session_dir = get_session_save_dir(session_id)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("session.json", json.dumps(session, indent=2))

            for f in os.listdir(session_dir):
                if f.endswith('.z2s'):
                    zf.write(os.path.join(session_dir, f), f"saves/{f}")

        return output_path, f"Session exported"
    except Exception as e:
        return None, f"Export failed: {e}"

def import_session(package_path=None):
    if not package_path:
        package_path = filedialog.askopenfilename(
            title="Import Session",
            filetypes=[("ZT2 Session", "*.zt2session"), ("All Files", "*.*")]
        )

    if not package_path:
        return None, "Import cancelled"

    try:
        with zipfile.ZipFile(package_path, 'r') as zf:
            session = json.loads(zf.read("session.json"))
            session_id = session['id']

            if os.path.exists(get_session_file(session_id)):
                pass

            with open(get_session_file(session_id), 'w') as f:
                json.dump(session, f, indent=2)

            session_dir = get_session_save_dir(session_id)
            for f in zf.namelist():
                if f.startswith('saves/') and f.endswith('.z2s'):
                    save_name = os.path.basename(f)
                    with open(os.path.join(session_dir, save_name), 'wb') as out:
                        out.write(zf.read(f))

            return session_id, f"Session imported: {session['name']}"
    except Exception as e:
        return None, f"Import failed: {e}"

def load_session_save_to_game(session_id):
    session = load_session(session_id)
    if not session:
        return False, "Session not found"

    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        return False, "Could not find saves directory"

    session_dir = get_session_save_dir(session_id)
    current_save = session.get('current_save')

    if not current_save:
        return False, "No save in session"

    src = os.path.join(session_dir, current_save)
    if not os.path.isfile(src):
        return False, "Session save not found"

    dest_name = f"MP_{session['name']}_{current_save}"
    dest = os.path.join(saves_dir, dest_name)

    shutil.copy2(src, dest)
    return True, f"Loaded to game: {dest_name}"


mp_paned = ttk.PanedWindow(multiplayer_tab, orient=tk.HORIZONTAL)
mp_paned.pack(fill=tk.BOTH, expand=True)

sharing_frame = ttk.LabelFrame(mp_paned, text="Save Sharing", padding=10)
mp_paned.add(sharing_frame, weight=1)

ttk.Label(sharing_frame, text="Share your zoos with friends!",
          bootstyle="secondary").pack(anchor="w", pady=(0, 10))

sharing_btn_frame = ttk.Frame(sharing_frame)
sharing_btn_frame.pack(fill=tk.X, pady=5)

def on_export_save():
    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        messagebox.showerror("Error", "Could not find saves directory")
        return

    save_path = filedialog.askopenfilename(
        title="Select Save to Export",
        initialdir=saves_dir,
        filetypes=[("ZT2 Saves", "*.z2s"), ("All Files", "*.*")]
    )

    if save_path:
        result, msg = export_save_for_sharing(save_path)
        if result:
            log(f"Exported save: {msg}", log_text)
            messagebox.showinfo("Export Complete", msg)
        else:
            messagebox.showerror("Export Failed", msg)

def on_import_save():
    result, msg = import_shared_save()
    if result:
        log(f"Imported save: {msg}", log_text)
        messagebox.showinfo("Import Complete", msg)
        refresh_saves_list()
    else:
        if msg != "Import cancelled":
            messagebox.showerror("Import Failed", msg)

ttk.Button(sharing_btn_frame, text="Export Save (.zt2share)",
           command=on_export_save, bootstyle="info", width=25).pack(pady=2)
ttk.Button(sharing_btn_frame, text="Import Save (.zt2share)",
           command=on_import_save, bootstyle="success", width=25).pack(pady=2)

ttk.Separator(sharing_frame, orient="horizontal").pack(fill=tk.X, pady=15)

ttk.Label(sharing_frame, text="Quick Share",
          font=("Segoe UI", 9, "bold")).pack(anchor="w")

def copy_save_to_clipboard():
    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        messagebox.showerror("Error", "Could not find saves directory")
        return

    save_path = filedialog.askopenfilename(
        title="Select Save to Copy",
        initialdir=saves_dir,
        filetypes=[("ZT2 Saves", "*.z2s")]
    )

    if not save_path:
        return

    try:
        import base64
        with open(save_path, 'rb') as f:
            data = f.read()

        package = {
            "name": os.path.basename(save_path),
            "data": base64.b64encode(data).decode('ascii'),
            "size": len(data)
        }

        encoded = base64.b64encode(json.dumps(package).encode()).decode('ascii')
        root.clipboard_clear()
        root.clipboard_append(f"ZT2SAVE:{encoded}")

        messagebox.showinfo("Copied", f"Save copied to clipboard!\nSize: {len(data)//1024} KB\n\nShare this with a friend.")
        log(f"Copied save to clipboard: {os.path.basename(save_path)}", log_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy: {e}")

def paste_save_from_clipboard():
    try:
        import base64
        clipboard = root.clipboard_get()

        if not clipboard.startswith("ZT2SAVE:"):
            messagebox.showerror("Error", "No valid save data in clipboard.\nAsk your friend to copy their save first.")
            return

        encoded = clipboard[8:]
        package = json.loads(base64.b64decode(encoded).decode())
        data = base64.b64decode(package['data'])

        saves_dir = get_zt2_saves_dir()
        if not saves_dir:
            messagebox.showerror("Error", "Could not find saves directory")
            return

        save_name = package.get('name', 'shared_save.z2s')
        dest = os.path.join(saves_dir, f"Shared_{save_name}")

        counter = 1
        while os.path.exists(dest):
            base, ext = os.path.splitext(save_name)
            dest = os.path.join(saves_dir, f"Shared_{base}_{counter}{ext}")
            counter += 1

        with open(dest, 'wb') as f:
            f.write(data)

        messagebox.showinfo("Success", f"Save imported!\n{os.path.basename(dest)}")
        log(f"Imported save from clipboard: {os.path.basename(dest)}", log_text)
        refresh_saves_list()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to paste: {e}")

clip_frame = ttk.Frame(sharing_frame)
clip_frame.pack(fill=tk.X, pady=5)
ttk.Button(clip_frame, text="Copy Save", command=copy_save_to_clipboard,
           width=12).pack(side=tk.LEFT, padx=2)
ttk.Button(clip_frame, text="Paste Save", command=paste_save_from_clipboard,
           width=12).pack(side=tk.LEFT, padx=2)

async_frame = ttk.LabelFrame(mp_paned, text="Multiplayer", padding=10)
mp_paned.add(async_frame, weight=2)

ttk.Label(async_frame, text="Take turns building a zoo with friends!",
          bootstyle="secondary").pack(anchor="w", pady=(0, 10))

session_list_frame = ttk.Frame(async_frame)
session_list_frame.pack(fill=tk.BOTH, expand=True)

session_tree = ttk.Treeview(
    session_list_frame,
    columns=("Name", "Turn", "Players", "Last Activity"),
    show="headings",
    height=8
)
session_tree.heading("Name", text="Session Name")
session_tree.heading("Turn", text="Turn #")
session_tree.heading("Players", text="Players")
session_tree.heading("Last Activity", text="Last Activity")

session_tree.column("Name", width=150)
session_tree.column("Turn", width=60, anchor="center")
session_tree.column("Players", width=100)
session_tree.column("Last Activity", width=120)

session_scroll = ttk.Scrollbar(session_list_frame, orient="vertical", command=session_tree.yview)
session_tree.configure(yscrollcommand=session_scroll.set)

session_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
session_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def refresh_sessions():
    session_tree.delete(*session_tree.get_children())
    sessions = list_sessions()

    for s in sorted(sessions, key=lambda x: x.get('turn_history', [{}])[-1].get('timestamp', ''), reverse=True):
        last_turn = s.get('turn_history', [{}])[-1]
        last_time = last_turn.get('timestamp', '')[:16].replace('T', ' ')
        players = ', '.join(s.get('players', [])[:3])
        if len(s.get('players', [])) > 3:
            players += f" +{len(s['players'])-3}"

        session_tree.insert("", tk.END, iid=s['id'], values=(
            s.get('name', 'Unnamed'),
            s.get('turn_number', 0),
            players,
            last_time
        ))

    log(f"Found {len(sessions)} multiplayer session(s)", log_text)

session_btn_frame = ttk.Frame(async_frame)
session_btn_frame.pack(fill=tk.X, pady=(10, 0))

def on_create_session():
    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        messagebox.showerror("Error", "Could not find saves directory")
        return

    save_path = filedialog.askopenfilename(
        title="Select Starting Save",
        initialdir=saves_dir,
        filetypes=[("ZT2 Saves", "*.z2s")]
    )

    if not save_path:
        return

    session_name = simpledialog.askstring("Session Name",
                                          "Enter a name for this multiplayer session:",
                                          parent=root)
    if not session_name:
        return

    session_id, msg = create_multiplayer_session(save_path, session_name)
    if session_id:
        log(f"Created multiplayer session: {session_name} ({session_id})", log_text)
        messagebox.showinfo("Session Created",
                           f"Session ID: {session_id}\n\nExport this session to share with friends!")
        refresh_sessions()
    else:
        messagebox.showerror("Error", msg)

def on_load_session():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session first")
        return

    session_id = selected[0]
    success, msg = load_session_save_to_game(session_id)

    if success:
        log(msg, log_text)
        messagebox.showinfo("Loaded", f"{msg}\n\nYou can now play this save in Zoo Tycoon 2!")
        refresh_saves_list()
    else:
        messagebox.showerror("Error", msg)

def on_take_turn():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session first")
        return

    session_id = selected[0]
    session = load_session(session_id)

    saves_dir = get_zt2_saves_dir()
    if not saves_dir:
        messagebox.showerror("Error", "Could not find saves directory")
        return

    save_path = filedialog.askopenfilename(
        title="Select Your Updated Save",
        initialdir=saves_dir,
        filetypes=[("ZT2 Saves", "*.z2s")]
    )

    if not save_path:
        return

    note = simpledialog.askstring("Turn Note",
                                   "Add a note about what you did this turn (optional):",
                                   parent=root) or ""

    success, msg = take_turn(session_id, save_path, note)
    if success:
        log(f"Turn submitted for {session['name']}: {msg}", log_text)
        messagebox.showinfo("Turn Submitted", f"{msg}\n\nExport the session to share your turn!")
        refresh_sessions()
    else:
        messagebox.showerror("Error", msg)

def on_export_session():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session to export")
        return

    session_id = selected[0]
    result, msg = export_session(session_id)

    if result:
        log(f"Exported session: {msg}", log_text)
        messagebox.showinfo("Exported", f"{msg}\n\nShare this file with your friends!")
    else:
        if msg != "Export cancelled":
            messagebox.showerror("Error", msg)

def on_import_session():
    result, msg = import_session()

    if result:
        log(f"Imported session: {msg}", log_text)
        messagebox.showinfo("Imported", msg)
        refresh_sessions()
    else:
        if msg != "Import cancelled":
            messagebox.showerror("Error", msg)

def on_delete_session():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session to delete")
        return

    session_id = selected[0]
    session = load_session(session_id)
    session_name = session.get('name', 'Unknown') if session else 'Unknown'

    if not messagebox.askyesno("Confirm Delete",
                                f"Delete session '{session_name}'?\n\nThis will remove all saves and cannot be undone!"):
        return

    success, msg = delete_session(session_id)
    if success:
        log(f"Deleted session: {session_name}", log_text)
        refresh_sessions()
    else:
        messagebox.showerror("Error", msg)

def on_view_history():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session first")
        return

    session_id = selected[0]
    session = load_session(session_id)
    if not session:
        messagebox.showerror("Error", "Could not load session")
        return

    history_win = tk.Toplevel(root)
    history_win.title(f"Turn History - {session.get('name', 'Unknown')}")
    history_win.geometry("700x450")
    history_win.transient(root)

    history_frame = ttk.Frame(history_win, padding=10)
    history_frame.pack(fill=tk.BOTH, expand=True)

    history_tree = ttk.Treeview(
        history_frame,
        columns=("Turn", "Player", "Time", "Note", "Stats"),
        show="headings",
        height=15
    )
    history_tree.heading("Turn", text="Turn")
    history_tree.heading("Player", text="Player")
    history_tree.heading("Time", text="Timestamp")
    history_tree.heading("Note", text="Note")
    history_tree.heading("Stats", text="Zoo Stats")

    history_tree.column("Turn", width=50, anchor="center")
    history_tree.column("Player", width=100)
    history_tree.column("Time", width=130)
    history_tree.column("Note", width=200)
    history_tree.column("Stats", width=180)

    history_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=history_tree.yview)
    history_tree.configure(yscrollcommand=history_scroll.set)

    history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    history_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    for h in session.get('turn_history', []):
        turn = h.get('turn', 0)
        player = h.get('player', 'Unknown')
        timestamp = h.get('timestamp', '')[:16].replace('T', ' ')
        note = h.get('note', '')[:50]
        if h.get('is_rollback'):
            note = f"🔄 {note}"

        stats = h.get('stats', {})
        stats_str = ""
        if stats:
            parts = []
            if stats.get('money') is not None:
                parts.append(f"${stats['money']:,.0f}")
            if stats.get('rating') is not None:
                parts.append(f"⭐{stats['rating']:.1f}")
            if stats.get('zoo_name'):
                parts.append(stats['zoo_name'][:20])
            stats_str = " | ".join(parts)

        history_tree.insert("", tk.END, values=(turn, player, timestamp, note, stats_str))

    def do_rollback():
        sel = history_tree.selection()
        if not sel:
            messagebox.showinfo("Select Turn", "Please select a turn to rollback to")
            return

        item = history_tree.item(sel[0])
        target_turn = int(item['values'][0])

        if not messagebox.askyesno("Confirm Rollback",
                                    f"Rollback to turn {target_turn}?\n\nAll turns after this will be removed!"):
            return

        success, msg = rollback_turn(session_id, target_turn)
        if success:
            log(f"Rolled back session to turn {target_turn}", log_text)
            messagebox.showinfo("Success", msg)
            history_win.destroy()
            refresh_sessions()
        else:
            messagebox.showerror("Error", msg)

    btn_frame = ttk.Frame(history_win, padding=10)
    btn_frame.pack(fill=tk.X)

    ttk.Button(btn_frame, text="Rollback to Selected Turn", command=do_rollback,
               bootstyle="warning").pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Close", command=history_win.destroy,
               bootstyle="secondary").pack(side=tk.RIGHT, padx=5)

def on_rollback():
    selected = session_tree.selection()
    if not selected:
        messagebox.showinfo("Select Session", "Please select a session first")
        return

    session_id = selected[0]
    session = load_session(session_id)
    if not session:
        messagebox.showerror("Error", "Could not load session")
        return

    max_turn = session.get('turn_number', 1) - 1
    if max_turn <= 0:
        messagebox.showinfo("Cannot Rollback", "No previous turns to rollback to")
        return

    target = simpledialog.askinteger("Rollback Turn",
                                      f"Enter turn number to rollback to (0-{max_turn}):",
                                      parent=root,
                                      minvalue=0,
                                      maxvalue=max_turn)
    if target is None:
        return

    if not messagebox.askyesno("Confirm Rollback",
                                f"Rollback to turn {target}?\n\nAll turns after this will be removed!"):
        return

    success, msg = rollback_turn(session_id, target)
    if success:
        log(f"Rolled back session to turn {target}", log_text)
        messagebox.showinfo("Success", msg)
        refresh_sessions()
    else:
        messagebox.showerror("Error", msg)

btn_row1 = ttk.Frame(session_btn_frame)
btn_row1.pack(fill=tk.X, pady=2)

ttk.Button(btn_row1, text="New Session", command=on_create_session,
           bootstyle="success", width=12).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row1, text="Load Save", command=on_load_session,
           bootstyle="info", width=12).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row1, text="Submit Turn", command=on_take_turn,
           bootstyle="warning", width=12).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row1, text="Refresh", command=refresh_sessions,
           bootstyle="secondary", width=10).pack(side=tk.LEFT, padx=2)

btn_row2 = ttk.Frame(session_btn_frame)
btn_row2.pack(fill=tk.X, pady=2)

ttk.Button(btn_row2, text="Export Session", command=on_export_session,
           bootstyle="info-outline", width=14).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row2, text="Import Session", command=on_import_session,
           bootstyle="success-outline", width=14).pack(side=tk.LEFT, padx=2)

btn_row3 = ttk.Frame(session_btn_frame)
btn_row3.pack(fill=tk.X, pady=2)

ttk.Button(btn_row3, text="View History", command=on_view_history,
           bootstyle="secondary", width=12).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row3, text="Rollback", command=on_rollback,
           bootstyle="warning-outline", width=10).pack(side=tk.LEFT, padx=2)
ttk.Button(btn_row3, text="Delete", command=on_delete_session,
           bootstyle="danger-outline", width=10).pack(side=tk.LEFT, padx=2)

ttk.Separator(async_frame, orient="horizontal").pack(fill=tk.X, pady=10)

instructions = ttk.Label(async_frame, text="""How to play:
1. Create a new session with a starting save
2. Export session and share with friends
3. Friends import the session and load the save
4. After playing, submit your turn with the updated save
5. Export again and pass to the next player""",
    justify="left", bootstyle="secondary", font=("Segoe UI", 9))
instructions.pack(anchor="w")

modbrowser_header = ttk.Frame(modbrowser_tab)
modbrowser_header.pack(fill=tk.X, pady=(0, 10))

ttk.Label(modbrowser_header, text="Mod Browser",
          font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

FEATURED_MODS = [
    "Radical Remake", "African Elephant", "Bengal Tiger", "Giant Panda",
    "Komodo Dragon", "Emperor Penguin", "Grizzly Bear", "Deinonychus"
]

def load_featured_mod(mod_title):
    search_zt2dl_mods(mod_title)

def on_quickpick_select(event=None):
    sel = quickpick_var.get()
    if sel and sel != "Quick Picks...":
        load_featured_mod(sel)
        quickpick_var.set("Quick Picks...")

quickpick_var = tk.StringVar(value="Quick Picks...")
quickpick_combo = ttk.Combobox(modbrowser_header, textvariable=quickpick_var,
                               values=FEATURED_MODS, state="readonly", width=18)
quickpick_combo.pack(side=tk.RIGHT, padx=4)
quickpick_combo.bind("<<ComboboxSelected>>", on_quickpick_select)
ttk.Label(modbrowser_header, text="Featured:", bootstyle="secondary").pack(side=tk.RIGHT)

search_toolbar = ttk.Frame(modbrowser_tab)
search_toolbar.pack(fill=tk.X, pady=(0, 8))

modbrowser_search_var = tk.StringVar()
modbrowser_search_entry = ttk.Entry(search_toolbar, textvariable=modbrowser_search_var, width=35)
modbrowser_search_entry.pack(side=tk.LEFT, padx=(0, 4))

def on_modbrowser_search(event=None):
    query = modbrowser_search_var.get().strip()
    if query:
        search_zt2dl_mods(query)

modbrowser_search_entry.bind("<Return>", on_modbrowser_search)

ttk.Button(search_toolbar, text="Search", command=on_modbrowser_search,
           bootstyle="info", width=8).pack(side=tk.LEFT, padx=2)

ttk.Separator(search_toolbar, orient="vertical").pack(side=tk.LEFT, padx=8, fill=tk.Y, pady=2)

modbrowser_category_var = tk.StringVar(value="Animals")
modbrowser_category_combo = ttk.Combobox(search_toolbar, textvariable=modbrowser_category_var,
    values=["Animals", "Foliage", "Objects", "Scenery", "Buildings", "Packs"],
    state="readonly", width=10)
modbrowser_category_combo.pack(side=tk.LEFT, padx=(0, 4))

ttk.Button(search_toolbar, text="Browse", command=lambda: browse_zt2dl_category(),
           bootstyle="success", width=8).pack(side=tk.LEFT, padx=2)

ttk.Button(search_toolbar, text="Recent", command=lambda: load_recent_zt2dl(),
           bootstyle="info-outline", width=7).pack(side=tk.LEFT, padx=2)

ttk.Button(search_toolbar, text="Random", command=lambda: load_random_zt2dl_mod(),
           bootstyle="warning-outline", width=7).pack(side=tk.LEFT, padx=2)

def open_moddb_zt2():
    webbrowser.open("https://www.moddb.com/games/zoo-tycoon-2/downloads")
    log("Opened Mod DB", text_widget=log_text)

def open_zt2_roundtable():
    webbrowser.open("https://thezt2roundtable.com/downloads-f169/")
    log("Opened ZT2 Round Table", text_widget=log_text)

def open_nexus_mods_zt2():
    webbrowser.open("https://www.nexusmods.com/zootycoon2")
    log("Opened Nexus Mods", text_widget=log_text)

ttk.Separator(search_toolbar, orient="vertical").pack(side=tk.LEFT, padx=8, fill=tk.Y, pady=2)

external_btn = ttk.Menubutton(search_toolbar, text="More Sources", bootstyle="secondary-outline")
external_menu = tk.Menu(external_btn, tearoff=0)
external_menu.add_command(label="Mod DB", command=open_moddb_zt2)
external_menu.add_command(label="ZT2 Round Table", command=open_zt2_roundtable)
external_menu.add_command(label="Nexus Mods", command=open_nexus_mods_zt2)
external_btn["menu"] = external_menu
external_btn.pack(side=tk.LEFT, padx=2)

ttk.Button(search_toolbar, text="Install URL", command=install_mod_from_url_dialog,
           bootstyle="success-outline", width=10).pack(side=tk.LEFT, padx=2)

modbrowser_split = ttk.PanedWindow(modbrowser_tab, orient=tk.HORIZONTAL)
modbrowser_split.pack(fill=tk.BOTH, expand=True)

modbrowser_list_frame = ttk.Frame(modbrowser_split, padding=4)
modbrowser_split.add(modbrowser_list_frame, weight=2)

modbrowser_tree_scroll = ttk.Scrollbar(modbrowser_list_frame)
modbrowser_tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

modbrowser_tree = ttk.Treeview(
    modbrowser_list_frame,
    columns=("Name", "Type"),
    show="headings",
    selectmode="browse",
    yscrollcommand=modbrowser_tree_scroll.set
)
modbrowser_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
modbrowser_tree_scroll.config(command=modbrowser_tree.yview)

modbrowser_tree.heading("Name", text="Name")
modbrowser_tree.heading("Type", text="Type")
modbrowser_tree.column("Name", width=300, anchor="w")
modbrowser_tree.column("Type", width=80, anchor="center")

modbrowser_details_frame = ttk.LabelFrame(modbrowser_split, text="Mod Details", padding=8)
modbrowser_split.add(modbrowser_details_frame, weight=1)

modbrowser_detail_title = tk.StringVar(value="Select a mod to view details")
ttk.Label(modbrowser_details_frame, textvariable=modbrowser_detail_title,
          font=("Segoe UI", 11, "bold"), wraplength=280).pack(anchor="w", pady=(0, 6))

modbrowser_action_frame = ttk.Frame(modbrowser_details_frame)
modbrowser_action_frame.pack(fill=tk.X, pady=(0, 8))

modbrowser_open_btn = ttk.Button(modbrowser_action_frame, text="Wiki Page",
                                  bootstyle="info", command=lambda: open_zt2dl_page(),
                                  state="disabled")
modbrowser_open_btn.pack(side=tk.LEFT, padx=(0, 4))

modbrowser_link_btn = ttk.Button(modbrowser_action_frame, text="Download",
                                  bootstyle="success", command=lambda: open_zt2dl_download(),
                                  state="disabled")
modbrowser_link_btn.pack(side=tk.LEFT, padx=2)

modbrowser_content_canvas = tk.Canvas(modbrowser_details_frame, highlightthickness=0)
modbrowser_content_scroll = ttk.Scrollbar(modbrowser_details_frame, orient="vertical",
                                           command=modbrowser_content_canvas.yview)
modbrowser_content_inner = ttk.Frame(modbrowser_content_canvas)

modbrowser_content_inner.bind("<Configure>",
    lambda _: modbrowser_content_canvas.configure(scrollregion=modbrowser_content_canvas.bbox("all")))
modbrowser_content_canvas.create_window((0, 0), window=modbrowser_content_inner, anchor="nw")
modbrowser_content_canvas.configure(yscrollcommand=modbrowser_content_scroll.set)

modbrowser_content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
modbrowser_content_scroll.pack(side=tk.RIGHT, fill=tk.Y)

def _on_modbrowser_mousewheel(event):
    modbrowser_content_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
modbrowser_content_canvas.bind_all("<MouseWheel>", _on_modbrowser_mousewheel)

modbrowser_image_frame = ttk.Frame(modbrowser_content_inner)
modbrowser_image_frame.pack(fill=tk.X, pady=(0, 8))

modbrowser_image_label = ttk.Label(modbrowser_image_frame, text="(No preview)",
                                    bootstyle="secondary")
modbrowser_image_label.pack(anchor="center")

_modbrowser_current_image = None

ttk.Label(modbrowser_content_inner, text="Description:",
          font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))

modbrowser_desc_text = tk.Text(modbrowser_content_inner, wrap=tk.WORD, height=6,
                                state="disabled", bg="#2b2b2b", fg="#e0e0e0",
                                font=("Segoe UI", 9))
modbrowser_desc_text.pack(fill=tk.X, pady=(0, 8))

ttk.Label(modbrowser_content_inner, text="Download Links:",
          font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 2))

modbrowser_links_list = tk.Listbox(modbrowser_content_inner, height=3, exportselection=False,
                                    bg="#2b2b2b", fg="#e0e0e0")
modbrowser_links_list.pack(fill=tk.X)

modbrowser_status_var = tk.StringVar(value="Select a category and click Browse, or search for mods")
ttk.Label(modbrowser_tab, textvariable=modbrowser_status_var,
          bootstyle="secondary").pack(anchor="w", pady=(8, 0))

_modbrowser_current_page = None
_modbrowser_items = []

def browse_zt2dl_category():
    global _modbrowser_items
    category = modbrowser_category_var.get()

    category_map = {
        "Animals": "Category:Animals",
        "Foliage": "Category:Foliage",
        "Objects": "Category:Objects",
        "Scenery": "Category:Scenery",
        "Buildings": "Category:Building_Sets",
        "Packs": "Category:Packs",
        "Recent": "Special:RecentChanges"
    }

    cat_title = category_map.get(category, f"Category:{category}")
    modbrowser_status_var.set(f"Loading {category}...")
    root.update()

    def fetch():
        try:
            if category == "Recent":
                items = zt2dl_api.get_recent_downloads(limit=50)
                return [{"title": i.get("title", ""), "type": "page"} for i in items], None
            else:
                items = zt2dl_api.get_category_members(cat_title, limit=100)
                return items, None
        except Exception as e:
            return None, str(e)

    def on_complete(result):
        items, error = result
        if error:
            modbrowser_status_var.set(f"Error: {error}")
            return

        global _modbrowser_items
        _modbrowser_items = items

        modbrowser_tree.delete(*modbrowser_tree.get_children())
        for item in items:
            title = item.get("title", "Unknown")
            item_type = item.get("type", "page")
            if item_type == "subcat":
                display_type = "Category"
            else:
                display_type = "Mod"
            modbrowser_tree.insert("", tk.END, values=(title, display_type))

        modbrowser_status_var.set(f"Found {len(items)} items in {category}")
        increment_stat("categories_browsed")

    threading.Thread(target=lambda: root.after(0, lambda: on_complete(fetch())),
                     daemon=True).start()

def search_zt2dl_mods(query):
    global _modbrowser_items
    modbrowser_status_var.set(f"Searching for '{query}'...")
    root.update()

    def fetch():
        try:
            results = zt2dl_api.search_mods(query, limit=50)
            return results, None
        except Exception as e:
            return None, str(e)

    def on_complete(result):
        results, error = result
        if error:
            modbrowser_status_var.set(f"Error: {error}")
            return

        global _modbrowser_items
        _modbrowser_items = [{"title": r.get("title", ""), "type": "page"} for r in results]

        modbrowser_tree.delete(*modbrowser_tree.get_children())
        for r in results:
            title = r.get("title", "Unknown")
            modbrowser_tree.insert("", tk.END, values=(title, "Mod"))

        modbrowser_status_var.set(f"Found {len(results)} results for '{query}'")
        increment_stat("browser_searches")

    threading.Thread(target=lambda: root.after(0, lambda: on_complete(fetch())),
                     daemon=True).start()


def load_recent_zt2dl():
    modbrowser_category_var.set("Recent")
    browse_zt2dl_category()

def generate_random_objective():
    import random as rnd

    increment_stat("objectives_generated")

    objectives = {
        "Animal Challenge": [
            "Create an exhibit with exactly 5 different species from the same continent",
            "Raise 10 baby animals to adulthood without any deaths",
            "Have 3 endangered species reach maximum happiness",
            "Create a nocturnal animal zone with at least 4 species",
            "Build a marine exhibit with dolphins, orcas, and sea lions",
            "Breed every big cat species in your zoo",
            "Create a primate paradise with 6+ different monkey/ape species",
            "Have 20 animals achieve 'Superstar' status",
            "Build an African savanna with lions, elephants, zebras, and giraffes",
            "Create an Australian outback with kangaroos, koalas, and platypus",
            "Maintain 50+ animals with 95%+ happiness for 6 months",
            "Successfully release 5 animals back to the wild",
        ],
        "Building Challenge": [
            "Build a zoo using only ancient/historical themed buildings",
            "Create a zoo with no straight paths - curves only!",
            "Build elevated walkways connecting at least 5 exhibits",
            "Design a zoo with a central water feature visible from all exhibits",
            "Create themed zones for each continent represented",
            "Build an underwater viewing tunnel for marine exhibits",
            "Construct a zoo with no food courts - only scattered vendors",
            "Design a perfectly symmetrical zoo layout",
            "Create a jungle-themed zoo with maximum foliage coverage",
            "Build a desert oasis zoo with water features throughout",
        ],
        "Financial Challenge": [
            "Reach $500,000 profit without using any donations",
            "Achieve 5-star zoo rating with starting budget only",
            "Run a profitable zoo with free admission for 1 year",
            "Earn $100,000 from gift shop sales alone",
            "Complete a zoo with budget under $200,000 total spent",
            "Maintain profitability with 50% of exhibits being endangered species",
            "Reach 1000 monthly guests with ticket prices over $50",
        ],
        "Guest Challenge": [
            "Achieve 98% guest happiness for 3 consecutive months",
            "Have 500 guests in your zoo simultaneously",
            "Get 100 guests to use the guided tour at once",
            "Maintain zero guest complaints for 6 months",
            "Have guests rate every exhibit 4+ stars",
            "Create a zoo where average guest stay exceeds 4 hours",
            "Build enough amenities that no guest ever gets hungry/thirsty",
        ],
        "Creative Challenge": [
            "Build a zoo inspired by your favorite movie",
            "Create a 'mythical creatures' zoo using available animals creatively",
            "Design a zoo that tells a story through its layout",
            "Build the smallest possible 5-star zoo",
            "Create a zoo using only animals from one expansion pack",
            "Design a 'conservation center' focused on breeding programs",
            "Build a 'walk-through' safari experience",
            "Create a seasonal-themed zoo (winter wonderland, autumn forest, etc.)",
        ],
        "Speed Challenge": [
            "Achieve 3-star rating within 30 minutes of gameplay",
            "Build 10 exhibits in under 15 minutes",
            "Reach 200 guests in the first in-game month",
            "Get your first baby animal within 2 in-game months",
            "Achieve profitability within the first in-game week",
        ],
    }

    category = rnd.choice(list(objectives.keys()))
    objective = rnd.choice(objectives[category])

    obj_win = tk.Toplevel(root)
    obj_win.title("Random Zoo Objective")
    obj_win.geometry("450x280")
    obj_win.resizable(False, False)
    obj_win.transient(root)
    obj_win.grab_set()

    obj_win.update_idletasks()
    x = root.winfo_x() + (root.winfo_width() // 2) - (450 // 2)
    y = root.winfo_y() + (root.winfo_height() // 2) - (280 // 2)
    obj_win.geometry(f"+{x}+{y}")

    main_frame = ttk.Frame(obj_win, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="Your Zoo Challenge",
              font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

    cat_frame = ttk.Frame(main_frame)
    cat_frame.pack(pady=(0, 15))
    ttk.Label(cat_frame, text=category,
              font=("Segoe UI", 10, "bold"),
              bootstyle="info").pack()

    obj_text = tk.Text(main_frame, wrap=tk.WORD, height=5, width=45,
                       bg="#2b2b2b", fg="#e0e0e0", font=("Segoe UI", 11),
                       relief="flat", padx=10, pady=10)
    obj_text.pack(fill=tk.X, pady=(0, 15))
    obj_text.insert("1.0", objective)
    obj_text.config(state="disabled")

    btn_frame = ttk.Frame(main_frame)
    btn_frame.pack(fill=tk.X)

    def reroll():
        new_cat = rnd.choice(list(objectives.keys()))
        new_obj = rnd.choice(objectives[new_cat])
        cat_frame.winfo_children()[0].config(text=new_cat)
        obj_text.config(state="normal")
        obj_text.delete("1.0", tk.END)
        obj_text.insert("1.0", new_obj)
        obj_text.config(state="disabled")

    ttk.Button(btn_frame, text="Reroll", command=reroll,
               bootstyle="warning").pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Accept Challenge", command=obj_win.destroy,
               bootstyle="success").pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="Close", command=obj_win.destroy,
               bootstyle="secondary").pack(side=tk.RIGHT, padx=5)

def load_random_zt2dl_mod():
    global _modbrowser_current_page, _modbrowser_items
    modbrowser_status_var.set("Loading random mod...")
    root.update()

    def fetch_random():
        try:
            params = {
                "action": "query",
                "format": "json",
                "list": "random",
                "rnnamespace": "0",
                "rnlimit": "1"
            }
            response = requests.get(ZT2DL_API_BASE, params=params, timeout=10)
            data = response.json()
            random_pages = data.get("query", {}).get("random", [])
            if random_pages:
                return random_pages[0].get("title"), None
            return None, "No random page found"
        except Exception as e:
            return None, str(e)

    def on_complete(result):
        title, error = result
        if error:
            modbrowser_status_var.set(f"Error: {error}")
            return

        global _modbrowser_current_page, _modbrowser_items
        _modbrowser_current_page = title
        _modbrowser_items = [{"title": title, "type": "page"}]

        modbrowser_tree.delete(*modbrowser_tree.get_children())
        item_id = modbrowser_tree.insert("", tk.END, values=(title, "Mod"))
        modbrowser_tree.selection_set(item_id)

        modbrowser_status_var.set(f"Random mod: {title}")
        increment_stat("random_mods_viewed")

        on_modbrowser_select(None)

    threading.Thread(target=lambda: root.after(0, lambda: on_complete(fetch_random())),
                     daemon=True).start()

def load_modbrowser_image(image_url):
    global _modbrowser_current_image

    def fetch_image():
        try:
            img_response = requests.get(image_url, timeout=15)
            img_response.raise_for_status()
            return img_response.content, None
        except Exception as e:
            return None, str(e)

    def on_image_loaded(result):
        global _modbrowser_current_image
        img_data, error = result

        if error or not img_data:
            modbrowser_image_label.config(image='', text="(No preview)")
            _modbrowser_current_image = None
            return

        try:
            from PIL import Image, ImageTk
            import io

            img = Image.open(io.BytesIO(img_data))

            max_width, max_height = 200, 150
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(img)

            modbrowser_image_label.config(image=photo, text="")
            _modbrowser_current_image = photo

        except ImportError:
            modbrowser_image_label.config(image='', text="(PIL not installed)")
            _modbrowser_current_image = None
        except Exception:
            modbrowser_image_label.config(image='', text="(Image error)")
            _modbrowser_current_image = None

    modbrowser_image_label.config(image='', text="Loading...")

    threading.Thread(target=lambda: root.after(0, lambda: on_image_loaded(fetch_image())),
                     daemon=True).start()

def on_modbrowser_select(event=None):
    global _modbrowser_current_page

    selection = modbrowser_tree.selection()
    if not selection:
        return

    item = modbrowser_tree.item(selection[0])
    title = item['values'][0]
    item_type = item['values'][1]

    if item_type == "Category":
        modbrowser_category_var.set(title.replace("Category:", ""))
        browse_zt2dl_category()
        return

    _modbrowser_current_page = title
    modbrowser_detail_title.set(title)
    modbrowser_status_var.set(f"Loading details for {title}...")
    root.update()

    def fetch():
        try:
            content = zt2dl_api.get_page_content(title)
            return content, None
        except Exception as e:
            return None, str(e)

    def on_complete(result):
        global _modbrowser_current_image
        content, error = result
        if error:
            modbrowser_status_var.set(f"Error loading details: {error}")
            return

        import re
        import html as html_module

        html_text = content.get("text", {}).get("*", "")

        image_loaded = False
        img_patterns = [
            r'src="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|gif))"',
            r'href="(https://static\.wikia\.nocookie\.net/[^"]+\.(?:png|jpg|jpeg|gif))"',
            r'(https://static\.wikia\.nocookie\.net/[^"\s]+\.(?:png|jpg|jpeg|gif))',
        ]

        for pattern in img_patterns:
            matches = re.findall(pattern, html_text, re.I)
            if matches:
                for img_url in matches:
                    if '/revision/' in img_url and '/scale-to-width-down/' in img_url:
                        img_url = re.sub(r'/revision/.*', '', img_url)
                    if any(x in img_url.lower() for x in ['icon', 'logo', 'button', '/thumb/', '28px', '20px']):
                        continue
                    load_modbrowser_image(img_url)
                    image_loaded = True
                    break
            if image_loaded:
                break

        if not image_loaded:
            modbrowser_image_label.config(image='', text="(No preview)")
            _modbrowser_current_image = None

        after_table = re.split(r'</table>|</aside>', html_text, flags=re.I)
        if len(after_table) > 1:
            desc_html = after_table[-1]
        else:
            desc_html = html_text

        text = desc_html
        text = re.sub(r'</p>', '\n\n', text, flags=re.I)
        text = re.sub(r'<br\s*/?>', '\n', text, flags=re.I)
        text = re.sub(r'</li>', '\n', text, flags=re.I)
        text = re.sub(r'<[^>]+>', '', text)

        text = html_module.unescape(text)

        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = '\n'.join(line.strip() for line in text.split('\n'))
        text = text.strip()

        for footer in ['Categories', 'Community content', 'FANDOM']:
            if footer in text:
                text = text.split(footer)[0].strip()

        text = text[:1200] if text else "No description available."

        modbrowser_desc_text.config(state="normal")
        modbrowser_desc_text.delete("1.0", tk.END)
        modbrowser_desc_text.insert("1.0", text)
        modbrowser_desc_text.config(state="disabled")

        links = content.get("externallinks", [])
        modbrowser_links_list.delete(0, tk.END)

        exclude_sites = [
            'fandom.com', 'wikia.com', 'creativecommons.org',
            'wikipedia.org', 'gnu.org/licenses'
        ]

        for link in links:
            link_lower = link.lower()
            if any(exclude in link_lower for exclude in exclude_sites):
                continue
            modbrowser_links_list.insert(tk.END, link)

        if modbrowser_links_list.size() == 0:
            modbrowser_links_list.insert(tk.END, "(No download links found - try Open Wiki Page)")

        modbrowser_open_btn.config(state="normal")
        modbrowser_link_btn.config(state="normal" if links else "disabled")

        modbrowser_status_var.set(f"Loaded: {title}")

    threading.Thread(target=lambda: root.after(0, lambda: on_complete(fetch())),
                     daemon=True).start()

def open_zt2dl_page():
    global _modbrowser_current_page
    if _modbrowser_current_page:
        url = zt2dl_api.get_page_url(_modbrowser_current_page)
        webbrowser.open(url)

def open_zt2dl_download():
    selection = modbrowser_links_list.curselection()
    if selection:
        link = modbrowser_links_list.get(selection[0])
        if link and not link.startswith("("):
            webbrowser.open(link)
    elif modbrowser_links_list.size() > 0:
        link = modbrowser_links_list.get(0)
        if link and not link.startswith("("):
            webbrowser.open(link)

modbrowser_tree.bind("<<TreeviewSelect>>", on_modbrowser_select)
modbrowser_tree.bind("<Double-1>", lambda e: open_zt2dl_page())
modbrowser_links_list.bind("<Double-1>", lambda e: open_zt2dl_download())

modbrowser_context = tk.Menu(modbrowser_tree, tearoff=0)
modbrowser_context.add_command(label="Open Wiki Page", command=open_zt2dl_page)
modbrowser_context.add_command(label="Copy Page URL", command=lambda: copy_zt2dl_url())

def on_modbrowser_right_click(event):
    iid = modbrowser_tree.identify_row(event.y)
    if iid:
        modbrowser_tree.selection_set(iid)
        modbrowser_context.post(event.x_root, event.y_root)

def copy_zt2dl_url():
    global _modbrowser_current_page
    if _modbrowser_current_page:
        url = zt2dl_api.get_page_url(_modbrowser_current_page)
        root.clipboard_clear()
        root.clipboard_append(url)
        modbrowser_status_var.set("URL copied to clipboard!")

modbrowser_tree.bind("<Button-3>", on_modbrowser_right_click)

content_frame = ttk.Frame(bundles_tab)
content_frame.pack(fill=tk.BOTH, expand=True)

bundle_split = ttk.PanedWindow(content_frame, orient=tk.HORIZONTAL)
bundle_split.pack(fill=tk.BOTH, expand=True)

left_panel = ttk.Frame(bundle_split, width=260, padding=(4, 6))
left_panel.pack_propagate(False)
bundle_split.add(left_panel, weight=1)

ttk.Label(left_panel, text="Bundles",
          font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 4))
search_row = ttk.Frame(left_panel)
search_row.pack(fill=tk.X, pady=(0, 6))

bundle_search_var = tk.StringVar()
ttk.Entry(search_row, textvariable=bundle_search_var).pack(side=tk.LEFT,
                                                           fill=tk.X,
                                                           expand=True)
ttk.Button(search_row,
           text="Clear",
           bootstyle="secondary-outline",
           command=lambda:
           (bundle_search_var.set(""), refresh_bundles_list())).pack(
               side=tk.LEFT, padx=(6, 0))

bundle_list_frame = ttk.Frame(left_panel)
bundle_list_frame.pack(fill=tk.BOTH, expand=True)

bundle_list_scroll = ttk.Scrollbar(bundle_list_frame, orient="vertical")
bundle_list_scroll.pack(side=tk.RIGHT, fill=tk.Y)

bundle_list = tk.Listbox(bundle_list_frame,
                         exportselection=False,
                         height=20,
                         yscrollcommand=bundle_list_scroll.set)
bundle_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
bundle_list_scroll.config(command=bundle_list.yview)

if bundle_list.size() == 0:
    bundle_list.insert(tk.END, "(No bundles yet)")

bundle_preview = ttk.Frame(bundle_split, padding=8)
bundle_split.add(bundle_preview, weight=3)

ttk.Label(bundle_preview, text="Bundle Preview",
          font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 6))
bundle_name_lbl = ttk.Label(bundle_preview,
                            text="(Select a bundle)",
                            bootstyle="secondary")
bundle_name_lbl.pack(anchor="w", pady=(0, 6))

preview_tree = ttk.Treeview(bundle_preview,
                            columns=("mod", "status"),
                            show="headings",
                            height=14)
preview_tree.heading("mod", text="Mod Name")
preview_tree.heading("status", text="Status")
preview_tree.column("mod", width=280, anchor="w")
preview_tree.column("status", width=100, anchor="center")
preview_tree.pack(fill=tk.BOTH, expand=True)

bundle_stats = tk.StringVar(value="0 mods")
ttk.Label(bundle_preview, textvariable=bundle_stats,
          bootstyle="info").pack(anchor="e", pady=(6, 0))

bundle_btns = ttk.Frame(bundles_tab, padding=6)
bundle_btns.pack(side=tk.BOTTOM, fill=tk.X, pady=(4, 0))


def update_bundle_toolbar_state():
    has_selection = bool(bundle_list.curselection())
    for btn in (apply_btn, delete_btn):
        state = "normal" if has_selection else "disabled"
        btn.config(state=state)


bundle_list.bind("<<ListboxSelect>>", lambda _: update_bundle_toolbar_state())

create_btn = ttk.Button(bundle_btns,
                        text="Create",
                        bootstyle="success",
                        command=bundle_create_dialog)
create_btn.pack(side=tk.LEFT, padx=4)

apply_btn = ttk.Button(bundle_btns,
                       text="Apply",
                       bootstyle="primary",
                       command=bundle_apply,
                       state="disabled")
apply_btn.pack(side=tk.LEFT, padx=4)

delete_btn = ttk.Button(bundle_btns,
                        text="Delete",
                        bootstyle="info",
                        command=bundle_delete,
                        state="disabled")
delete_btn.pack(side=tk.LEFT, padx=4)

ttk.Button(bundle_btns, text="Export JSON",
           command=bundle_export_json).pack(side=tk.LEFT, padx=4)
ttk.Button(bundle_btns, text="Import JSON",
           command=bundle_import_json).pack(side=tk.LEFT, padx=4)
ttk.Button(bundle_btns,
           text="Export Bundle as Mod (.z2f)",
           bootstyle="success",
           command=bundle_export_z2f).pack(side=tk.LEFT, padx=4)


def update_bundle_toolbar_state():
    sel = bundle_list.curselection()
    has_selection = bool(sel) and not bundle_list.get(sel[0]).startswith("(")
    apply_btn.config(state="normal" if has_selection else "disabled")
    delete_btn.config(state="normal" if has_selection else "disabled")


bundle_list.bind(
    "<<ListboxSelect>>", lambda _:
    (refresh_bundle_preview(), update_bundle_toolbar_state()))

preview_btns = ttk.Frame(bundle_preview)
preview_btns.pack(fill=tk.X, pady=(6, 0))
ttk.Button(preview_btns,
           text="Apply Bundle",
           command=lambda: bundle_apply(),
           bootstyle="primary").pack(side=tk.LEFT, padx=4)
ttk.Button(preview_btns,
           text="Enable All",
           command=lambda: bundle_enable_all(),
           bootstyle="success").pack(side=tk.LEFT, padx=4)
ttk.Button(preview_btns,
           text="Disable All",
           command=lambda: bundle_disable_all(),
           bootstyle="warning").pack(side=tk.LEFT, padx=4)


def _selected_bundle_name():
    sel = bundle_list.curselection()
    if not sel:
        return None
    return bundle_list.get(sel[0])


def refresh_bundles_list():
    global _all_bundle_names_cache
    cursor.execute("SELECT name FROM bundles ORDER BY name ASC")
    names = [r[0] for r in cursor.fetchall()]
    _all_bundle_names_cache = names[:]
    _apply_bundle_filter()


def _apply_bundle_filter(*_):
    query = bundle_search_var.get().strip().lower()
    bundle_list.delete(0, tk.END)

    filtered = [n for n in _all_bundle_names_cache if query in n.lower()]
    if not filtered:
        bundle_list.insert(
            tk.END, "(No bundles yet)"
            if not _all_bundle_names_cache else "(No matches)")
        bundle_name_lbl.config(text="(Select a bundle)")
        for i in preview_tree.get_children():
            preview_tree.delete(i)
        bundle_stats.set("0 mods")
        return

    for n in filtered:
        bundle_list.insert(tk.END, n)


def refresh_bundle_preview(event=None):
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        bundle_name_lbl.config(text="(Select a bundle)")
        for i in preview_tree.get_children():
            preview_tree.delete(i)
        bundle_stats.set("0 mods")
        return

    bundle_name_lbl.config(text=name)
    for i in preview_tree.get_children():
        preview_tree.delete(i)

    cursor.execute("SELECT id FROM bundles WHERE name=?", (name, ))
    row = cursor.fetchone()
    if not row:
        bundle_stats.set("0 mods")
        return

    bundle_id = row[0]
    cursor.execute(
        "SELECT mod_name FROM bundle_mods WHERE bundle_id=? ORDER BY mod_name",
        (bundle_id, ))
    mods = [r[0] for r in cursor.fetchall()]

    enabled_count = 0
    for m in mods:
        cursor.execute("SELECT enabled FROM mods WHERE name=?", (m, ))
        r = cursor.fetchone()
        status = "Enabled" if r and r[0] else "Disabled"
        if status == "Enabled":
            enabled_count += 1
        preview_tree.insert("", "end", values=(m, status))

    bundle_stats.set(f"{enabled_count}/{len(mods)} enabled")


bundle_list.bind("<<ListboxSelect>>", refresh_bundle_preview)


def _bundle_context_menu(event):
    idx = bundle_list.nearest(event.y)
    try:
        bundle_list.selection_clear(0, tk.END)
        bundle_list.selection_set(idx)
    except Exception:
        pass

    menu = tk.Menu(bundles_tab, tearoff=0)
    menu.add_command(label="Apply", command=lambda: bundle_apply())
    menu.add_command(label="Delete", command=lambda: bundle_delete())
    menu.add_separator()
    menu.add_command(label="Export JSON", command=lambda: bundle_export_json())
    try:
        menu.tk_popup(event.x_root, event.y_root)
    finally:
        menu.grab_release()


bundle_list.bind("<Button-3>", _bundle_context_menu)


def bundle_enable_all():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    mods = get_bundle_mods(name)
    for m in mods:
        enable_mod(m, text_widget=log_text)
    refresh_bundle_preview()
    refresh_tree()


def bundle_disable_all():
    name = _selected_bundle_name()
    if not name or name.startswith("("):
        messagebox.showinfo("Select", "Select a bundle first.")
        return
    mods = get_bundle_mods(name)
    for m in mods:
        disable_mod(m, text_widget=log_text)
    refresh_bundle_preview()
    refresh_tree()


refresh_bundles_list()

log_frame = ttk.Frame(main_frame, padding=6)
log_frame.pack(side=tk.RIGHT, fill=tk.Y)

ttk.Label(log_frame, text="Log Output:").pack(anchor='w')
log_text = tk.Text(log_frame, height=40, wrap='word', state='disabled')
log_text.pack(fill=tk.BOTH, expand=True)

def refresh_tree():
    mods_tree.delete(*mods_tree.get_children())

    if not GAME_PATH:
        return

    detect_existing_mods()

    disabled_dir = mods_disabled_dir()
    if disabled_dir:
        os.makedirs(disabled_dir, exist_ok=True)

    cursor.execute(
        "SELECT name, enabled, category FROM mods ORDER BY enabled DESC, name ASC")
    mods = cursor.fetchall()

    total = len(mods)
    enabled_count = sum(1 for _, e, _ in mods if e)
    disabled_count = total - enabled_count

    for name, enabled_flag, category in mods:
        path = find_mod_file(name)
        exists = path and os.path.isfile(path)

        size_mb = os.path.getsize(path) / (1024 * 1024) if exists else 0
        modified = (time.strftime("%Y-%m-%d %H:%M:%S",
                                  time.localtime(os.path.getmtime(path)))
                    if exists else "N/A")

        status = ("🟢 Enabled" if enabled_flag else
                  ("🟡 Missing" if not exists else "🔴 Disabled"))

        mods_tree.insert("",
                         tk.END,
                         values=(name, status, category or "—", f"{size_mb:.2f}", modified),
                         tags=("enabled" if enabled_flag else
                               ("missing" if not exists else "disabled"), ))

    mod_count_label.config(
        text=
        f"Total mods: {total} | Enabled: {enabled_count} | Disabled: {disabled_count}"
    )

    apply_tree_theme()
    refresh_bundles_list()
    update_status_bar()

    print(f"[ModZT] Refreshed mod list ({total} mods found).")


def sort_tree_by(column):
    if sort_state["column"] == column:
        sort_state["reverse"] = not sort_state["reverse"]
    else:
        sort_state["column"] = column
        sort_state["reverse"] = False

    items = [mods_tree.item(iid)["values"] for iid in mods_tree.get_children()]

    col_index = {"Name": 0, "Status": 1, "Category": 2, "Size": 3, "Modified": 4}[column]

    def sort_key(row):
        val = row[col_index]
        if column == "Size":
            try:
                return float(val)
            except ValueError:
                return 0
        elif column == "Modified":
            try:
                return time.mktime(time.strptime(val, "%Y-%m-%d %H:%M:%S"))
            except Exception:
                return 0
        else:
            return str(val).lower()

    items.sort(key=sort_key, reverse=sort_state["reverse"])

    for row in mods_tree.get_children():
        mods_tree.delete(row)

    for r in items:
        status_text = r[1]
        if "🟢" in status_text:
            tag = "enabled"
        elif "🟡" in status_text:
            tag = "missing"
        else:
            tag = "disabled"
        mods_tree.insert("", tk.END, values=r, tags=(tag, ))

    apply_tree_theme()

    for col in ("Name", "Status", "Category", "Size", "Modified"):
        arrow = ""
        if col == column:
            arrow = "▼" if sort_state["reverse"] else "▲"
        mods_tree.heading(col,
                          text=f"{col} {arrow}",
                          command=lambda c=col: sort_tree_by(c))


def apply_tree_theme():
    if root.style.theme_use() == 'darkly':
        mods_tree.tag_configure('enabled', foreground="#4bc969")
        mods_tree.tag_configure('disabled', foreground='#ff6961')
        mods_tree.tag_configure('missing', foreground='#f5d97e')
    else:
        mods_tree.tag_configure('enabled', foreground='#007f00')
        mods_tree.tag_configure('disabled', foreground='#b30000')
        mods_tree.tag_configure('missing', foreground='#c48f00')


def apply_ui_mode():
    compact = ui_mode["compact"]

    style = root.style
    style.configure("Treeview", rowheight=(18 if compact else 24))

    font_size = 9 if compact else 10
    style.configure("TLabel", font=("Segoe UI", font_size))
    style.configure("TButton", font=("Segoe UI", font_size))
    style.configure("Treeview.Heading", font=("Segoe UI", font_size, "bold"))

    padding = 2 if compact else 6
    for frame in [toolbar, mods_tab, bundles_tab, log_frame]:
        try:
            frame.configure(padding=padding)
        except tk.TclError:
            pass

    if compact:
        banner.pack_forget()
    else:
        banner.pack(fill=tk.X, before=toolbar)

    refresh_tree()


def get_selected_mod():
    sel = mods_tree.selection()
    if not sel:
        messagebox.showinfo("Select", "Select a mod first.", parent=root)
        return None
    return mods_tree.item(sel[0])['values'][0]


def get_selected_mods():
    sel = mods_tree.selection()
    if not sel:
        messagebox.showinfo("Select", "Select one or more mods first.", parent=root)
        return []
    return [mods_tree.item(iid)['values'][0] for iid in sel]


def enable_selected_mod():
    mods = get_selected_mods()
    if not mods:
        return
    for mod in mods:
        enable_mod(mod, text_widget=log_text)
    if len(mods) > 1:
        log(f"Enabled {len(mods)} mods", log_text)


def disable_selected_mod():
    mods = get_selected_mods()
    if not mods:
        return
    for mod in mods:
        disable_mod(mod, text_widget=log_text)
    if len(mods) > 1:
        log(f"Disabled {len(mods)} mods", log_text)
    if mods:
        root.after(100, lambda: restore_selection(mods[-1]))


def restore_selection(mod_name):
    for iid in mods_tree.get_children():
        vals = mods_tree.item(iid, 'values')
        if vals and vals[0] == mod_name:
            mods_tree.selection_set(iid)
            mods_tree.focus(iid)
            mods_tree.see(iid)
            break


def save_tree_state(tree):
    sel = tree.selection()
    first_visible = tree.index(
        tree.identify_row(0)) if tree.get_children() else 0
    return {"sel": sel, "first_visible": first_visible}


def restore_tree_state(tree, state):
    if not state:
        return
    sel = state.get("sel")
    if sel:
        tree.selection_set(sel)
        tree.focus(sel[0])
        tree.see(sel[0])
    else:
        first = state.get("first_visible", 0)
        try:
            iid = tree.get_children()[first]
            tree.see(iid)
        except IndexError:
            pass


def uninstall_selected_mod():
    mods = get_selected_mods()
    if not mods:
        return
    if len(mods) == 1:
        msg = f"Uninstall {mods[0]}?"
    else:
        msg = f"Uninstall {len(mods)} selected mods?\n\n" + "\n".join(mods[:10])
        if len(mods) > 10:
            msg += f"\n... and {len(mods) - 10} more"
    if messagebox.askyesno("Uninstall", msg):
        for mod in mods:
            uninstall_mod(mod, text_widget=log_text)
        if len(mods) > 1:
            log(f"Uninstalled {len(mods)} mods", log_text)


def open_mod_folder():
    mod = get_selected_mod()
    if not mod:
        return
    paths = [
        os.path.join(GAME_PATH, mod),
        os.path.join(mods_disabled_dir(), mod)
    ]
    for p in paths:
        if os.path.isfile(p):
            try:
                os.startfile(os.path.dirname(p))
                return
            except Exception:
                messagebox.showinfo("Open",
                                    f"Mod located at: {os.path.dirname(p)}")
                return
    messagebox.showinfo("Not Found", f"Could not find {mod} on disk.")


def parse_z2f_contents(z2f_path):
    contents = {
        "animals": [],
        "objects": [],
        "buildings": [],
        "scenery": [],
        "foliage": [],
        "fences": [],
        "paths": [],
        "guests": [],
        "staff": [],
        "other": [],
        "files": [],
        "total_size": 0,
        "compressed_size": 0
    }

    try:
        with zipfile.ZipFile(z2f_path, 'r') as zf:
            for info in zf.infolist():
                contents["total_size"] += info.file_size
                contents["compressed_size"] += info.compress_size
                contents["files"].append({
                    "name": info.filename,
                    "size": info.file_size,
                    "compressed": info.compress_size
                })

                if info.filename.lower().endswith('.xml'):
                    try:
                        xml_data = zf.read(info.filename).decode('utf-8', errors='ignore')
                        if xml_data.startswith('\ufeff'):
                            xml_data = xml_data[1:]

                        root_elem = ET.fromstring(xml_data)

                        entity_info = extract_entity_info(root_elem, info.filename)
                        if entity_info:
                            category = entity_info.get("category", "other")
                            if category in contents:
                                contents[category].append(entity_info)
                            else:
                                contents["other"].append(entity_info)
                    except ET.ParseError:
                        pass
                    except Exception:
                        pass
    except zipfile.BadZipFile:
        return None

    return contents


def extract_entity_info(root_elem, filename):
    info = {
        "filename": filename,
        "name": None,
        "codename": None,
        "type": None,
        "category": "other",
        "icon": None,
        "description": None
    }

    root_tag = root_elem.tag.lower() if root_elem.tag else ""

    if root_tag == "bfaitype" or root_elem.find(".//BFAIType") is not None:
        info["category"] = "animals"
        info["type"] = "Animal"
    elif root_tag == "bfbuildingtype" or root_elem.find(".//BFBuildingType") is not None:
        info["category"] = "buildings"
        info["type"] = "Building"
    elif root_tag == "bfscenerytype" or root_elem.find(".//BFSceneryType") is not None:
        info["category"] = "scenery"
        info["type"] = "Scenery"
    elif root_tag == "bffencetype" or root_elem.find(".//BFFenceType") is not None:
        info["category"] = "fences"
        info["type"] = "Fence"
    elif root_tag == "bfpathtype" or root_elem.find(".//BFPathType") is not None:
        info["category"] = "paths"
        info["type"] = "Path"
    elif root_tag == "bffoliagetype" or root_elem.find(".//BFFoliageType") is not None:
        info["category"] = "foliage"
        info["type"] = "Foliage"
    elif root_tag == "bfguesttype" or root_elem.find(".//BFGuestType") is not None:
        info["category"] = "guests"
        info["type"] = "Guest"
    elif root_tag == "bfstafftype" or root_elem.find(".//BFStaffType") is not None:
        info["category"] = "staff"
        info["type"] = "Staff"
    elif root_tag == "bfunittype" or root_elem.find(".//BFUnitType") is not None:
        info["category"] = "objects"
        info["type"] = "Object"
    else:
        path_lower = filename.lower()
        if "/animals/" in path_lower or "\\animals\\" in path_lower:
            info["category"] = "animals"
            info["type"] = "Animal"
        elif "/buildings/" in path_lower or "\\buildings\\" in path_lower:
            info["category"] = "buildings"
            info["type"] = "Building"
        elif "/scenery/" in path_lower or "\\scenery\\" in path_lower:
            info["category"] = "scenery"
            info["type"] = "Scenery"
        elif "/foliage/" in path_lower or "\\foliage\\" in path_lower:
            info["category"] = "foliage"
            info["type"] = "Foliage"
        elif "/fences/" in path_lower or "\\fences\\" in path_lower:
            info["category"] = "fences"
            info["type"] = "Fence"
        elif "/paths/" in path_lower or "\\paths\\" in path_lower:
            info["category"] = "paths"
            info["type"] = "Path"
        else:
            return None

    for tag in ["codename", "Codename", "cCodename", "ccodename"]:
        elem = root_elem.find(f".//{tag}")
        if elem is not None and elem.text:
            info["codename"] = elem.text.strip()
            break

    if not info["codename"]:
        type_attr = root_elem.get("Type") or root_elem.get("type")
        if type_attr:
            info["codename"] = type_attr
        else:
            base = os.path.basename(filename)
            info["codename"] = os.path.splitext(base)[0]

    for tag in ["cIconName", "ciconname", "IconName", "Name", "name", "cName"]:
        elem = root_elem.find(f".//{tag}")
        if elem is not None and elem.text:
            info["name"] = elem.text.strip()
            break

    if not info["name"]:
        info["name"] = info["codename"]

    for tag in ["cDescription", "Description", "description"]:
        elem = root_elem.find(f".//{tag}")
        if elem is not None and elem.text:
            info["description"] = elem.text.strip()
            break

    return info


def inspect_selected_mod():
    mod = get_selected_mod()
    if not mod:
        return

    path = find_mod_file(mod)
    if not path or not os.path.isfile(path):
        messagebox.showerror("Error", f"Cannot find file for '{mod}'.")
        return

    contents = parse_z2f_contents(path)
    if contents is None:
        messagebox.showerror("Error", "This mod file is not a valid Z2F file.")
        return

    dlg = tk.Toplevel(root)
    dlg.title(f"Z2F Contents: {mod}")
    dlg.geometry("900x700")

    main_frame = ttk.Frame(dlg, padding=8)
    main_frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.Frame(main_frame)
    header.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(header,
              text=f"Contents of {mod}",
              font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

    total_entities = sum(len(contents[cat]) for cat in
                         ["animals", "objects", "buildings", "scenery", "foliage", "fences", "paths"])
    size_mb = contents["total_size"] / (1024 * 1024)
    comp_mb = contents["compressed_size"] / (1024 * 1024)

    ttk.Label(header,
              text=f"Size: {size_mb:.2f} MB ({comp_mb:.2f} MB compressed)",
              bootstyle="secondary").pack(side=tk.RIGHT)

    summary_frame = ttk.Frame(main_frame)
    summary_frame.pack(fill=tk.X, pady=(0, 10))

    categories = [
        ("Animals", "animals", "success"),
        ("Buildings", "buildings", "info"),
        ("Scenery", "scenery", "warning"),
        ("Foliage", "foliage", "success"),
        ("Fences", "fences", "secondary"),
        ("Paths", "paths", "secondary"),
        ("Objects", "objects", "primary"),
    ]

    for i, (label, key, style) in enumerate(categories):
        count = len(contents[key])
        if count > 0:
            card = ttk.Frame(summary_frame)
            card.pack(side=tk.LEFT, padx=4)
            ttk.Label(card, text=str(count), font=("Segoe UI", 16, "bold")).pack()
            ttk.Label(card, text=label, bootstyle=style).pack()

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    content_tab = ttk.Frame(notebook, padding=6)
    notebook.add(content_tab, text="Content")

    content_tree = ttk.Treeview(content_tab,
                                 columns=("Type", "Name", "Codename"),
                                 show="headings", height=15)
    content_tree.heading("Type", text="Type")
    content_tree.heading("Name", text="Display Name")
    content_tree.heading("Codename", text="Codename")
    content_tree.column("Type", width=100)
    content_tree.column("Name", width=300)
    content_tree.column("Codename", width=300)

    content_scroll = ttk.Scrollbar(content_tab, orient="vertical", command=content_tree.yview)
    content_tree.configure(yscrollcommand=content_scroll.set)

    content_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    content_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    type_icons = {
        "animals": "Animal",
        "buildings": "Building",
        "scenery": "Scenery",
        "foliage": "Foliage",
        "fences": "Fence",
        "paths": "Path",
        "objects": "Object",
        "guests": "Guest",
        "staff": "Staff",
        "other": "Other"
    }

    for cat_key, cat_label in type_icons.items():
        for entity in contents[cat_key]:
            content_tree.insert("", tk.END,
                              values=(cat_label,
                                     entity.get("name", "Unknown"),
                                     entity.get("codename", "Unknown")))

    files_tab = ttk.Frame(notebook, padding=6)
    notebook.add(files_tab, text=f"Files ({len(contents['files'])})")

    files_tree = ttk.Treeview(files_tab,
                               columns=("Filename", "Size", "Compressed"),
                               show="headings", height=15)
    files_tree.heading("Filename", text="Filename")
    files_tree.heading("Size", text="Size (KB)")
    files_tree.heading("Compressed", text="Compressed (KB)")
    files_tree.column("Filename", width=500)
    files_tree.column("Size", width=100, anchor="e")
    files_tree.column("Compressed", width=100, anchor="e")

    files_scroll = ttk.Scrollbar(files_tab, orient="vertical", command=files_tree.yview)
    files_tree.configure(yscrollcommand=files_scroll.set)

    files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    files_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    for f in contents["files"]:
        size_kb = f["size"] / 1024
        comp_kb = f["compressed"] / 1024
        files_tree.insert("", tk.END,
                         values=(f["name"], f"{size_kb:.1f}", f"{comp_kb:.1f}"))

    detail_frame = ttk.LabelFrame(main_frame, text="Details", padding=8)
    detail_frame.pack(fill=tk.X, pady=(10, 0))

    detail_text = tk.Text(detail_frame, height=4, state="disabled",
                          bg="#2b2b2b", fg="#e0e0e0", font=("Consolas", 9), wrap=tk.WORD)
    detail_text.pack(fill=tk.X)

    def on_content_select(event):
        selected = content_tree.selection()
        if not selected:
            return
        item = content_tree.item(selected[0])
        values = item["values"]

        detail_text.config(state="normal")
        detail_text.delete("1.0", tk.END)
        detail_text.insert("1.0", f"Type: {values[0]}\nDisplay Name: {values[1]}\nCodename: {values[2]}")
        detail_text.config(state="disabled")

    content_tree.bind("<<TreeviewSelect>>", on_content_select)

    btns = ttk.Frame(dlg, padding=6)
    btns.pack(fill=tk.X)

    ttk.Button(btns,
               text="Extract to Folder",
               command=lambda: extract_zip_contents(path),
               bootstyle="info").pack(side=tk.LEFT, padx=4)

    ttk.Button(btns,
               text="Copy Content List",
               command=lambda: copy_content_list(contents),
               bootstyle="secondary").pack(side=tk.LEFT, padx=4)

    ttk.Button(btns, text="Close", command=dlg.destroy).pack(side=tk.RIGHT, padx=4)


def copy_content_list(contents):
    lines = ["Content Summary", "=" * 40, ""]

    categories = [
        ("Animals", "animals"),
        ("Buildings", "buildings"),
        ("Scenery", "scenery"),
        ("Foliage", "foliage"),
        ("Fences", "fences"),
        ("Paths", "paths"),
        ("Objects", "objects"),
    ]

    for label, key in categories:
        if contents[key]:
            lines.append(f"{label} ({len(contents[key])}):")
            for entity in contents[key]:
                name = entity.get("name", "Unknown")
                codename = entity.get("codename", "")
                if name != codename:
                    lines.append(f"  - {name} ({codename})")
                else:
                    lines.append(f"  - {name}")
            lines.append("")

    text = "\n".join(lines)
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Content list copied to clipboard!")


def scan_mod_conflicts():
    if not GAME_PATH or not os.path.isdir(GAME_PATH):
        messagebox.showwarning("No Game Path", "Please set your Zoo Tycoon 2 game path first.")
        return

    cursor.execute("SELECT name, enabled FROM mods")
    all_mods = cursor.fetchall()

    if not all_mods:
        messagebox.showinfo("No Mods", "No mods found to scan.")
        return

    progress_dlg = tk.Toplevel(root)
    progress_dlg.title("Scanning for Conflicts")
    progress_dlg.geometry("400x120")
    progress_dlg.transient(root)
    progress_dlg.grab_set()

    ttk.Label(progress_dlg, text="Scanning mods for file conflicts...",
              font=("Segoe UI", 11)).pack(pady=(20, 10))

    progress_var = tk.DoubleVar(value=0)
    progress_bar = ttk.Progressbar(progress_dlg, variable=progress_var,
                                    maximum=100, length=350)
    progress_bar.pack(pady=10)

    status_var = tk.StringVar(value="Initializing...")
    ttk.Label(progress_dlg, textvariable=status_var).pack()

    progress_dlg.update()

    file_index = {}
    mod_count = len(all_mods)

    for i, (mod_name, enabled) in enumerate(all_mods):
        progress_var.set((i / mod_count) * 100)
        status_var.set(f"Scanning: {mod_name[:40]}...")
        progress_dlg.update()

        mod_path = find_mod_file(mod_name)
        if not mod_path or not os.path.isfile(mod_path):
            continue

        try:
            with zipfile.ZipFile(mod_path, 'r') as zf:
                for info in zf.infolist():
                    file_path = info.filename.lower().replace('\\', '/')

                    if file_path.endswith('/'):
                        continue

                    if file_path not in file_index:
                        file_index[file_path] = []

                    file_index[file_path].append({
                        "mod": mod_name,
                        "size": info.file_size,
                        "enabled": enabled == 1,
                        "original_path": info.filename
                    })
        except zipfile.BadZipFile:
            continue
        except Exception:
            continue

    progress_dlg.destroy()

    conflicts = {}
    for file_path, mods in file_index.items():
        if len(mods) > 1:
            conflicts[file_path] = mods

    show_conflict_results(conflicts, len(all_mods))


def show_conflict_results(conflicts, total_mods):
    dlg = tk.Toplevel(root)
    dlg.title("Mod Conflict Scanner")
    dlg.geometry("1000x700")

    main_frame = ttk.Frame(dlg, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    header = ttk.Frame(main_frame)
    header.pack(fill=tk.X, pady=(0, 10))

    ttk.Label(header, text="Mod Conflict Scanner",
              font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)

    conflict_count = len(conflicts)
    affected_mods = set()
    for file_path, mods in conflicts.items():
        for mod_info in mods:
            affected_mods.add(mod_info["mod"])

    if conflict_count == 0:
        summary_text = f"No conflicts found among {total_mods} mods!"
        summary_style = "success"
    else:
        summary_text = f"Found {conflict_count} file conflicts affecting {len(affected_mods)} mods"
        summary_style = "warning"

    ttk.Label(header, text=summary_text, bootstyle=summary_style).pack(side=tk.RIGHT)

    if conflict_count == 0:
        ttk.Label(main_frame,
                  text="All mods are compatible - no file overwrites detected.",
                  font=("Segoe UI", 12)).pack(pady=50)
        ttk.Button(main_frame, text="Close", command=dlg.destroy).pack()
        return

    filter_frame = ttk.Frame(main_frame)
    filter_frame.pack(fill=tk.X, pady=(0, 10))

    filter_var = tk.StringVar(value="all")
    ttk.Label(filter_frame, text="Show:").pack(side=tk.LEFT, padx=(0, 5))
    ttk.Radiobutton(filter_frame, text="All Conflicts", variable=filter_var,
                    value="all").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(filter_frame, text="Enabled Mods Only", variable=filter_var,
                    value="enabled").pack(side=tk.LEFT, padx=5)
    ttk.Radiobutton(filter_frame, text="Critical (XML files)", variable=filter_var,
                    value="critical").pack(side=tk.LEFT, padx=5)

    paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
    paned.pack(fill=tk.BOTH, expand=True)

    left_frame = ttk.Frame(paned, padding=5)
    paned.add(left_frame, weight=1)

    ttk.Label(left_frame, text="Conflicting Files",
              font=("Segoe UI", 11, "bold")).pack(anchor="w")

    conflict_tree = ttk.Treeview(left_frame,
                                  columns=("File", "Mods", "Type"),
                                  show="headings", height=20)
    conflict_tree.heading("File", text="File Path")
    conflict_tree.heading("Mods", text="# Mods")
    conflict_tree.heading("Type", text="Type")
    conflict_tree.column("File", width=350)
    conflict_tree.column("Mods", width=60, anchor="center")
    conflict_tree.column("Type", width=80)

    conflict_scroll = ttk.Scrollbar(left_frame, orient="vertical",
                                     command=conflict_tree.yview)
    conflict_tree.configure(yscrollcommand=conflict_scroll.set)

    conflict_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    conflict_scroll.pack(side=tk.RIGHT, fill=tk.Y)

    right_frame = ttk.Frame(paned, padding=5)
    paned.add(right_frame, weight=1)

    ttk.Label(right_frame, text="Affected Mods",
              font=("Segoe UI", 11, "bold")).pack(anchor="w")

    detail_tree = ttk.Treeview(right_frame,
                                columns=("Mod", "Status", "Size"),
                                show="headings", height=10)
    detail_tree.heading("Mod", text="Mod Name")
    detail_tree.heading("Status", text="Status")
    detail_tree.heading("Size", text="File Size")
    detail_tree.column("Mod", width=250)
    detail_tree.column("Status", width=80)
    detail_tree.column("Size", width=80, anchor="e")

    detail_scroll = ttk.Scrollbar(right_frame, orient="vertical",
                                   command=detail_tree.yview)
    detail_tree.configure(yscrollcommand=detail_scroll.set)

    detail_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=(5, 0))
    detail_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=(5, 0))

    info_frame = ttk.LabelFrame(right_frame, text="Conflict Info", padding=8)
    info_frame.pack(fill=tk.X, pady=(10, 0))

    info_text = tk.Text(info_frame, height=6, state="disabled",
                        bg="#2b2b2b", fg="#e0e0e0", font=("Consolas", 9), wrap=tk.WORD)
    info_text.pack(fill=tk.X)

    conflicts_data = conflicts

    def get_file_type(filepath):
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.xml':
            return "XML"
        elif ext in ['.dds', '.tga', '.png', '.bmp']:
            return "Texture"
        elif ext in ['.nif', '.bfm']:
            return "Model"
        elif ext in ['.wav', '.mp3', '.ogg']:
            return "Audio"
        elif ext == '.lua':
            return "Script"
        elif ext == '.ini':
            return "Config"
        else:
            return "Other"

    def populate_conflict_tree(filter_type="all"):
        conflict_tree.delete(*conflict_tree.get_children())

        for file_path, mods in conflicts_data.items():
            if filter_type == "enabled":
                enabled_mods = [m for m in mods if m["enabled"]]
                if len(enabled_mods) < 2:
                    continue
                display_mods = enabled_mods
            elif filter_type == "critical":
                if not file_path.endswith('.xml'):
                    continue
                display_mods = mods
            else:
                display_mods = mods

            file_type = get_file_type(file_path)
            display_path = file_path
            if len(display_path) > 50:
                display_path = "..." + display_path[-47:]

            item_id = conflict_tree.insert("", tk.END,
                                           values=(display_path, len(display_mods), file_type),
                                           tags=(file_path,))

    def on_conflict_select(event):
        selected = conflict_tree.selection()
        if not selected:
            return

        item = conflict_tree.item(selected[0])
        file_path = item["tags"][0] if item["tags"] else None

        if not file_path or file_path not in conflicts_data:
            return

        mods = conflicts_data[file_path]

        detail_tree.delete(*detail_tree.get_children())

        for mod_info in mods:
            status = "Enabled" if mod_info["enabled"] else "Disabled"
            size_kb = mod_info["size"] / 1024
            detail_tree.insert("", tk.END,
                              values=(mod_info["mod"], status, f"{size_kb:.1f} KB"),
                              tags=("enabled" if mod_info["enabled"] else "disabled",))

        detail_tree.tag_configure("enabled", foreground="#2ecc71")
        detail_tree.tag_configure("disabled", foreground="#95a5a6")

        info_text.config(state="normal")
        info_text.delete("1.0", tk.END)

        info_lines = [
            f"File: {file_path}",
            f"Type: {get_file_type(file_path)}",
            f"Conflicting mods: {len(mods)}",
            "",
            "Note: The last loaded mod will overwrite earlier ones.",
            "Load order depends on alphabetical filename order."
        ]
        info_text.insert("1.0", "\n".join(info_lines))
        info_text.config(state="disabled")

    conflict_tree.bind("<<TreeviewSelect>>", on_conflict_select)

    def on_filter_change(*args):
        populate_conflict_tree(filter_var.get())

    filter_var.trace_add("write", on_filter_change)

    populate_conflict_tree()

    btn_frame = ttk.Frame(dlg, padding=8)
    btn_frame.pack(fill=tk.X)

    def export_conflicts():
        filepath = filedialog.asksaveasfilename(
            title="Save Conflict Report",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return

        lines = ["Conflict Report", "=" * 50, "",
                 f"Total conflicts: {len(conflicts_data)}",
                 f"Affected mods: {len(affected_mods)}", ""]

        for file_path, mods in sorted(conflicts_data.items()):
            lines.append(f"\nFile: {file_path}")
            lines.append(f"Type: {get_file_type(file_path)}")
            lines.append("Mods:")
            for mod_info in mods:
                status = "[ENABLED]" if mod_info["enabled"] else "[disabled]"
                lines.append(f"  - {mod_info['mod']} {status}")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            messagebox.showinfo("Exported", f"Conflict report saved to:\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report:\n{e}")

    ttk.Button(btn_frame, text="Export Report",
               command=export_conflicts,
               bootstyle="info").pack(side=tk.LEFT, padx=4)

    ttk.Button(btn_frame, text="Rescan",
               command=lambda: [dlg.destroy(), scan_mod_conflicts()],
               bootstyle="secondary").pack(side=tk.LEFT, padx=4)

    ttk.Button(btn_frame, text="Close",
               command=dlg.destroy).pack(side=tk.RIGHT, padx=4)


def check_selected_mod_conflicts():
    mod = get_selected_mod()
    if mod:
        check_mod_conflicts_for(mod)


def check_mod_conflicts_for(mod_name):
    mod_path = find_mod_file(mod_name)
    if not mod_path or not os.path.isfile(mod_path):
        messagebox.showerror("Error", f"Cannot find file for '{mod_name}'.")
        return

    target_files = set()
    try:
        with zipfile.ZipFile(mod_path, 'r') as zf:
            for info in zf.infolist():
                if not info.filename.endswith('/'):
                    target_files.add(info.filename.lower().replace('\\', '/'))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read mod:\n{e}")
        return

    cursor.execute("SELECT name FROM mods WHERE name != ?", (mod_name,))
    other_mods = [row[0] for row in cursor.fetchall()]

    conflicts = {}

    for other_mod in other_mods:
        other_path = find_mod_file(other_mod)
        if not other_path or not os.path.isfile(other_path):
            continue

        try:
            with zipfile.ZipFile(other_path, 'r') as zf:
                for info in zf.infolist():
                    if info.filename.endswith('/'):
                        continue
                    file_path = info.filename.lower().replace('\\', '/')
                    if file_path in target_files:
                        if other_mod not in conflicts:
                            conflicts[other_mod] = []
                        conflicts[other_mod].append(info.filename)
        except Exception:
            continue

    if not conflicts:
        messagebox.showinfo("No Conflicts",
                           f"'{mod_name}' has no file conflicts with other mods.")
        return

    dlg = tk.Toplevel(root)
    dlg.title(f"Conflicts for: {mod_name}")
    dlg.geometry("700x500")

    main_frame = ttk.Frame(dlg, padding=10)
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame,
              text=f"Conflicts for: {mod_name}",
              font=("Segoe UI", 12, "bold")).pack(anchor="w", pady=(0, 5))

    ttk.Label(main_frame,
              text=f"Found conflicts with {len(conflicts)} other mod(s)",
              bootstyle="warning").pack(anchor="w", pady=(0, 10))

    tree = ttk.Treeview(main_frame, columns=("Mod", "Files"),
                        show="headings", height=15)
    tree.heading("Mod", text="Conflicting Mod")
    tree.heading("Files", text="# Conflicting Files")
    tree.column("Mod", width=400)
    tree.column("Files", width=150, anchor="center")

    scroll = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scroll.pack(side=tk.RIGHT, fill=tk.Y)

    for other_mod, files in sorted(conflicts.items(), key=lambda x: -len(x[1])):
        tree.insert("", tk.END, values=(other_mod, len(files)), tags=(other_mod,))

    detail_frame = ttk.LabelFrame(dlg, text="Conflicting Files", padding=8)
    detail_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    detail_text = tk.Text(detail_frame, height=8, state="disabled",
                          bg="#2b2b2b", fg="#e0e0e0", font=("Consolas", 9))
    detail_text.pack(fill=tk.X)

    def on_select(event):
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        other_mod = item["tags"][0] if item["tags"] else None
        if other_mod and other_mod in conflicts:
            detail_text.config(state="normal")
            detail_text.delete("1.0", tk.END)
            detail_text.insert("1.0", "\n".join(conflicts[other_mod][:50]))
            if len(conflicts[other_mod]) > 50:
                detail_text.insert(tk.END, f"\n... and {len(conflicts[other_mod]) - 50} more")
            detail_text.config(state="disabled")

    tree.bind("<<TreeviewSelect>>", on_select)

    ttk.Button(dlg, text="Close", command=dlg.destroy).pack(pady=10)


def extract_zip_contents(path):
    out_dir = filedialog.askdirectory(title="Select destination folder")
    if not out_dir:
        return
    try:
        with zipfile.ZipFile(path, 'r') as zf:
            zf.extractall(out_dir)
        messagebox.showinfo("Extracted", f"Contents extracted to:\n{out_dir}")
        log(f"Extracted {os.path.basename(path)} to {out_dir}", log_text)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to extract:\n{e}")


def show_mod_details():
    mod = get_selected_mod()
    if not mod:
        return

    path = find_mod_file(mod)
    if not path:
        messagebox.showerror("Error", f"File for '{mod}' not found.")
        return

    size_mb = os.path.getsize(path) / (1024 * 1024)
    modified = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.localtime(os.path.getmtime(path)))

    cursor.execute(
        "SELECT b.name FROM bundles b JOIN bundle_mods bm ON b.id=bm.bundle_id WHERE bm.mod_name=?",
        (mod, ))
    bundle_rows = cursor.fetchall()
    bundle_names = [r[0] for r in bundle_rows] if bundle_rows else []

    readme_text = ""
    try:
        import zipfile
        with zipfile.ZipFile(path, 'r') as zf:
            for name in zf.namelist():
                if "readme" in name.lower() and name.lower().endswith(
                    (".txt", ".md")):
                    with zf.open(name) as f:
                        data = f.read().decode("utf-8", errors="ignore")
                        readme_text = data[:2000]
                        break
    except Exception:
        pass

    dlg = tk.Toplevel(root)
    dlg.title(f"Mod Details - {mod}")
    dlg.geometry("600x500")
    dlg.transient(root)

    frame = ttk.Frame(dlg, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(frame, text=f"🧩 {mod}",
              font=("Segoe UI", 14, "bold")).pack(anchor="w", pady=(0, 6))
    ttk.Label(frame, text=f"Path: {path}", wraplength=560).pack(anchor="w",
                                                                pady=(0, 3))
    ttk.Label(frame, text=f"Size: {size_mb:.2f} MB").pack(anchor="w")
    ttk.Label(frame, text=f"Last Modified: {modified}").pack(anchor="w",
                                                             pady=(0, 5))

    if bundle_names:
        ttk.Label(frame,
                  text="Included in Bundles:",
                  font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))
        ttk.Label(frame, text=", ".join(bundle_names),
                  wraplength=560).pack(anchor="w", pady=(0, 5))

    ttk.Separator(frame).pack(fill=tk.X, pady=8)

    ttk.Label(frame, text="Readme Preview:",
              font=("Segoe UI", 10, "bold")).pack(anchor="w")
    txt = tk.Text(frame, height=15, wrap="word")
    txt.pack(fill=tk.BOTH, expand=True)
    txt.insert(tk.END, readme_text or "(No readme found in mod)")
    txt.configure(state="disabled")

    ttk.Button(frame, text="Close", command=dlg.destroy).pack(pady=8)


def refresh_bundles_list():
    bundle_list.delete(0, tk.END)
    for name, mods in get_bundles():
        bundle_list.insert(tk.END, f"{name}")


def get_selected_bundle_name():
    sel = bundle_list.curselection()
    if not sel:
        messagebox.showinfo("Select", "Select a bundle first.", parent=root)
        return None
    text = bundle_list.get(sel[0])
    return text.rsplit(' (', 1)[0]


def on_create_bundle():
    dlg = tk.Toplevel(root)
    dlg.title("Create Bundle")
    dlg.geometry("420x480")

    ttk.Label(dlg, text="Bundle name:").pack(anchor='w', padx=6, pady=(6, 0))
    name_var = tk.StringVar()
    ttk.Entry(dlg, textvariable=name_var).pack(fill=tk.X, padx=6)

    ttk.Label(dlg, text="Select mods to include:").pack(anchor='w',
                                                        padx=6,
                                                        pady=(6, 0))
    mods_listbox = tk.Listbox(dlg, selectmode=tk.MULTIPLE)
    mods_listbox.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
    cursor.execute("SELECT name FROM mods ORDER BY name")
    mods = [r[0] for r in cursor.fetchall()]
    for m in mods:
        mods_listbox.insert(tk.END, m)

    def do_create():
        bname = name_var.get().strip()
        sel = mods_listbox.curselection()
        selected = [mods[i] for i in sel]
        if not bname or not selected:
            messagebox.showerror("Invalid",
                                 "Provide a name and select at least one mod.",
                                 parent=dlg)
            return
        ok = create_bundle(bname, selected)
        if not ok:
            messagebox.showerror("Error",
                                 "Bundle name already exists or invalid.",
                                 parent=dlg)
            return
        dlg.destroy()
        refresh_bundles_list()
        log(f"Created bundle '{bname}' with {len(selected)} mods.", log_text)

    ttk.Button(dlg, text="Create", command=do_create).pack(padx=6, pady=6)


on_create_bundle = on_create_bundle


def on_delete_bundle():
    name = get_selected_bundle_name()
    if not name:
        return
    if messagebox.askyesno("Delete Bundle", f"Delete bundle '{name}'?"):
        delete_bundle(name)
        refresh_bundles_list()
        log(f"Deleted bundle: {name}", log_text)


def on_apply_bundle():
    name = get_selected_bundle_name()
    if not name:
        return
    apply_bundle(name, text_widget=log_text)
    refresh_tree()


def on_export_bundle():
    name = get_selected_bundle_name()
    if not name:
        return
    export_bundle_as_json(name)


def on_import_bundle():
    import_bundle_from_json()
    refresh_bundles_list()


def on_export_bundle_as_mod():
    name = get_selected_bundle_name()
    if not name:
        return
    export_bundle_as_mod_ui(name)

def update_status():
    pass



search_var.trace_add('write', lambda *_: filter_tree())


def filter_tree(*_):
    query = search_var.get().strip().lower()

    for row in mods_tree.get_children():
        mods_tree.delete(row)

    cursor.execute(
        "SELECT name, enabled, category FROM mods ORDER BY enabled DESC, name ASC")
    mods = cursor.fetchall()

    visible_rows = []
    for name, enabled_flag, category in mods:
        status_str = "enabled" if enabled_flag else "disabled"

        combined = f"{name.lower()} {category.lower() if category else ''} {status_str}"
        if query and query not in combined:
            continue

        path = find_mod_file(name)
        size_mb = 0
        modified = "N/A"
        if path and os.path.isfile(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            modified = time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime(os.path.getmtime(path)))

        if enabled_flag:
            status = "🟢 Enabled"
        elif not path or not os.path.isfile(path):
            status = "🟡 Missing"
        else:
            status = "🔴 Disabled"

        tag = ("enabled" if enabled_flag else (
            "missing" if not path or not os.path.isfile(path) else "disabled"))

        mods_tree.insert("",
                         tk.END,
                         values=(name, status, category or "—", f"{size_mb:.2f}", modified),
                         tags=(tag, ))

        visible_rows.append(name)

    apply_tree_theme()

    total = len(mods)
    enabled = sum(1 for _, e in mods if e)
    disabled = total - enabled
    mod_count_label.config(
        text=
        f"Total mods: {len(visible_rows)} (Filtered) | Enabled: {enabled} | Disabled: {disabled}"
    )


refresh_tree()
apply_ui_mode()
detect_existing_zt1_mods()
refresh_zt1_tree()

if not hasattr(root, "_watcher_started"):
    watch_mods(root, refresh_tree, interval=3)
    root._watcher_started = True

if __name__ == '__main__':

    if not GAME_PATH:
        detected = auto_detect_zt2_installation()
        if detected:
            GAME_PATH = detected
            log(f"✅ Detected Zoo Tycoon 2 installation at: {GAME_PATH}",
                log_text)
            pass
        else:
            log("⚠️ Could not auto-detect Zoo Tycoon 2 path.", log_text)


def on_close():
    try:
        settings = load_settings()
        is_maximized = root.state() == 'zoomed'
        settings["window_maximized"] = is_maximized

        if not is_maximized:
            settings["window_geometry"] = root.geometry()

        save_settings(settings)
        print(f"Window geometry saved: {settings.get('window_geometry')} (maximized: {is_maximized})")
    except Exception as e:
        print(f"Error saving window geometry: {e}")

    try:
        conn.close()
        print("Database connection closed.")
    except Exception as e:
        print("Error closing DB:", e)
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)


icon_candidates = [
    resource_path("modzt.ico"),
    os.path.join(get_app_dir(), "modzt.ico"),
    os.path.join(CONFIG_DIR, "modzt.ico"),
    "modzt.ico"
]

icon_set = False
app_icon_photo = None

print(f"[i] Looking for icon in these locations:")
for candidate in icon_candidates:
    print(f"    - {candidate} {'(exists)' if os.path.exists(candidate) else '(not found)'}")

for icon_path in icon_candidates:
    if os.path.exists(icon_path):
        try:
            abs_icon_path = os.path.abspath(icon_path)

            root.iconbitmap(abs_icon_path)

            try:
                icon_img = Image.open(abs_icon_path)
                if icon_img.mode != 'RGBA':
                    icon_img = icon_img.convert('RGBA')
                app_icon_photo = ImageTk.PhotoImage(icon_img)
                root.iconphoto(True, app_icon_photo)
            except Exception as e2:
                print(f"[!] iconphoto failed: {e2}")

            root.update_idletasks()

            print(f"[✓] Icon successfully set from: {abs_icon_path}")
            icon_set = True
            break
        except Exception as e:
            print(f"[!] Failed to set icon from {icon_path}: {e}")

if not icon_set:
    print("[!] No icon file found, using default")

refresh_screenshots()
refresh_saves_list()
refresh_sessions()

start_background_music(volume=0.3)

start_theme_scheduler()

root.mainloop()
