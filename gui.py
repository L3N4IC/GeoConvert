#!/usr/bin/env python3
# Copyright 2026 HOUIZOT Lénaïc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
GeoConvert — Interface graphique Tkinter / CustomTkinter
"""

import sys
import os
import json
import threading
from pathlib import Path
import webbrowser

try:
    from PIL import Image, ImageTk, ImageOps
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    import customtkinter as ctk
    CTK = True
except ImportError:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    CTK = False

if CTK:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox


# ─── Couleurs et style ────────────────────────────────────────────────────────

COLORS_DARK = {
    "bg":       "#0F1113",
    "surface":  "#1A1D21",
    "surface2": "#2D333B",
    "accent":   "#6366F1",
    "accent2":  "#10B981",
    "success":  "#10B981",
    "error":    "#EF4444",
    "warning":  "#F59E0B",
    "text":     "#F1F5F9",
    "text_dim": "#94A3B8",
    "border":   "#334155",
}

COLORS_LIGHT = {
    "bg":       "#F0F2F5",
    "surface":  "#FFFFFF",
    "surface2": "#E2E8F0",
    "accent":   "#4F46E5",
    "accent2":  "#059669",
    "success":  "#059669",
    "error":    "#DC2626",
    "warning":  "#D97706",
    "text":     "#0F172A",
    "text_dim": "#64748B",
    "border":   "#CBD5E1",
}

# ─── Préférences utilisateur ─────────────────────────────────────────────────

_PREFS_PATH = Path.home() / ".config" / "geoconvert" / "preferences.json"

def _load_prefs() -> dict:
    """Loads preferences from the JSON file. Returns default values if absent."""
    defaults = {"theme": "light"}
    try:
        if _PREFS_PATH.exists():
            with open(_PREFS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                defaults.update(data)
    except Exception:
        pass
    return defaults

def _save_prefs(prefs: dict) -> None:
    """Saves preferences to the JSON file."""
    try:
        _PREFS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(_PREFS_PATH, "w", encoding="utf-8") as f:
            json.dump(prefs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Avertissement : impossible de sauvegarder les préférences : {e}")

_prefs = _load_prefs()
_current_theme = _prefs.get("theme", "light")  # Thème clair par défaut
_current_lang  = _prefs.get("lang", "fr")       # Langue française par défaut

def get_colors():
    return COLORS_DARK if _current_theme == "dark" else COLORS_LIGHT

# COLORS n'est plus un alias statique — utiliser get_colors() partout.
# Cette variable est conservée uniquement pour la rétro-compatibilité avec
# les références directes dans les widgets non-registrés (ex: VisualSelector).
# Elle est mise à jour à chaque changement de thème via _apply_theme().
COLORS = get_colors()

def C(key: str) -> str:
    """Raccourci dynamique : retourne toujours la couleur du thème actif.
    
    Usage : C("accent") au lieu de COLORS["accent"]
    Évite les valeurs figées dans les classes popup (VisualSelector, EPSGSelector).
    """
    return get_colors()[key]

# ─── Traductions ─────────────────────────────────────────────────────────────

def t(key: str) -> str:
    """Retourne la traduction de la clé dans la langue courante."""
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(_current_lang, entry.get("fr", key))

TRANSLATIONS: dict[str, dict[str, str]] = {
    # ── En-tête
    "app_version":        {"fr": "v1.0.0",                             "en": "v1.0.0"},
    "tooltip_theme":      {"fr": "Basculer entre le mode sombre et le mode clair", "en": "Toggle dark / light mode"},
    "tooltip_lang":       {"fr": "Changer la langue",                  "en": "Change language"},
    # ── Carte Source
    "card_source":        {"fr": "📂  Sélection Source",               "en": "📂  Source Selection"},
    "radio_single":       {"fr": "Fichier(s) unique(s)",               "en": "Single file(s)"},
    "radio_batch":        {"fr": "Dossier (Batch)",                    "en": "Folder (Batch)"},
    "btn_choose_files":   {"fr": "Choisir fichier(s)",                 "en": "Choose file(s)"},
    "btn_choose_folder":  {"fr": "Choisir dossier",                    "en": "Choose folder"},
    "no_file":            {"fr": "Aucun fichier sélectionné",          "en": "No file selected"},
    # ── Carte Destination
    "card_dest":          {"fr": "💾  Destination et Format",          "en": "💾  Destination & Format"},
    "label_format":       {"fr": "Format :",                           "en": "Format:"},
    "label_epsg":         {"fr": "EPSG :",                             "en": "EPSG:"},
    "tooltip_epsg_search":{"fr": "Rechercher un code EPSG",            "en": "Search for an EPSG code"},
    "placeholder_output": {"fr": "Dossier de sortie (optionnel)",      "en": "Output folder (optional)"},
    "btn_browse":         {"fr": "Parcourir",                          "en": "Browse"},
    # ── Carte Traitement
    "card_proc":          {"fr": "⚙️  Options de Traitement",          "en": "⚙️  Processing Options"},
    "label_depth":        {"fr": "Profondeur :",                       "en": "Depth:"},
    "label_quality":      {"fr": "Qualité :",                          "en": "Quality:"},
    "label_resampling":   {"fr": "Lissage :",                          "en": "Resampling:"},
    "seg_speed":          {"fr": "Vitesse",                            "en": "Speed"},
    "seg_normal":         {"fr": "Normal",                            "en": "Normal"},
    "seg_quality":        {"fr": "Qualité",                           "en": "Quality"},
    "seg_original":       {"fr": "Original",                          "en": "Original"},
    "seg_8bit":           {"fr": "8-bit",                             "en": "8-bit"},
    "seg_16bit":          {"fr": "16-bit",                            "en": "16-bit"},
    "chk_mosaic":         {"fr": "Mosaïque",                          "en": "Mosaic"},
    "chk_multicore":      {"fr": "Multi-cœurs",                       "en": "Multi-core"},
    "chk_tiling":         {"fr": "Tuilage",                           "en": "Tiling"},
    "chk_pyramids":       {"fr": "Pyramides",                         "en": "Pyramids"},
    "chk_nodata":         {"fr": "NoData=0",                          "en": "NoData=0"},
    "tooltip_mosaic":     {"fr": "Fusionne plusieurs fichiers GeoTIFF/JP2 en une seule grande image de sortie.",
                           "en": "Merges multiple GeoTIFF/JP2 files into a single large output image."},
    "tooltip_multicore":  {"fr": "Utilise tous les cœurs du processeur pour accélérer considérablement la conversion.",
                           "en": "Uses all CPU cores to significantly speed up conversion."},
    "tooltip_tiling":     {"fr": "Divise l'image interne en blocs réguliers, accélérant fortement l'affichage sur les logiciels SIG (QGIS/ArcGIS).",
                           "en": "Splits the image into regular tiles, greatly speeding up display in GIS software (QGIS/ArcGIS)."},
    "tooltip_pyramids":   {"fr": "Génère des miniatures internes (Zoom) pour ouvrir les images très lourdes instantanément au dézoom.",
                           "en": "Generates internal thumbnails (overviews) for instant display when zooming out on very large images."},
    "tooltip_nodata":     {"fr": "Considère les pixels de valeur 0 (souvent les bordures noires) comme transparents.",
                           "en": "Treats pixels with value 0 (often black borders) as transparent."},
    "tooltip_depth":      {"fr": "Profondeur des couleurs:\n- 8-bit: Image classique, légère.\n- 16-bit: Haute précision (utile pour MNT ou analyse spectrale).",
                           "en": "Color depth:\n- 8-bit: Standard image, lightweight.\n- 16-bit: High precision (useful for DEM or spectral analysis)."},
    "tooltip_compress":   {"fr": "- LZW: Rapide et sans perte, compression moyenne.\n- DEFLATE: Standard moderne sans perte, compression forte.\n- JPEG: Destruction de données, très forte compression, déconseillé en SIG analytique.",
                           "en": "- LZW: Fast and lossless, medium compression.\n- DEFLATE: Modern lossless standard, strong compression.\n- JPEG: Lossy, very strong compression, not recommended for analytical GIS."},
    "tooltip_resampling": {"fr": "Méthode d'échantillonnage de l'image (si changement de taille) :\n- Vitesse : Plus proche voisin (Garde les pixels bruts)\n- Normal : Bilinéaire (Doux)\n- Qualité : Cubique (Lissage de haute précision)",
                           "en": "Image sampling method (if resizing):\n- Speed: Nearest neighbor (Keeps raw pixels)\n- Normal: Bilinear (Smooth)\n- Quality: Cubic (High precision smoothing)"},
    "tooltip_quality":    {"fr": "Qualité JPEG / J2K (1-100%)\nPlus la qualité est basse, plus l'image sera pixelisée et légère.",
                           "en": "JPEG / J2K Quality (1-100%)\nThe lower the quality, the more pixelated and lightweight the image will be."},
    # ── Outils rapides
    "card_tools":         {"fr": "🛠️  Outils Rapides",                 "en": "🛠️  Quick Tools"},
    "btn_inspect":        {"fr": "🔍  Détails Techniques",             "en": "🔍  Technical Details"},
    "btn_estimate":       {"fr": "⚖️  Estimer la Taille",             "en": "⚖️  Estimate Size"},
    "btn_shapefile":      {"fr": "🗺️  Créer Shapefile",              "en": "🗺️  Create Shapefile"},
    "tooltip_inspect":    {"fr": "Affiche les métadonnées détaillées du fichier sélectionné (EPSG, Emprise, Bandes...)",
                           "en": "Displays detailed metadata for the selected file (EPSG, Extent, Bands...)"},
    "tooltip_estimate":   {"fr": "Estime l'espace disque nécessaire pour la conversion selon vos réglages actuels",
                           "en": "Estimates the disk space required for conversion with your current settings"},
    "tooltip_shapefile":  {"fr": "Crée un fichier Shapefile (.shp) de l'emprise (bounding box) du ou des fichiers sélectionnés",
                           "en": "Creates a Shapefile (.shp) of the bounding box extent of the selected file(s)"},
    "shapefile_title":    {"fr": "Créer un Shapefile d'Emprise",       "en": "Create Extent Shapefile"},
    "shapefile_success":  {"fr": "✅ Shapefile créé avec succès :",    "en": "✅ Shapefile created successfully:"},
    "shapefile_error":    {"fr": "✗ Erreur lors de la création du Shapefile :", "en": "✗ Error creating Shapefile:"},
    "shapefile_no_gdal":  {"fr": "Le module OGR (GDAL) est requis pour créer un Shapefile.", "en": "The OGR (GDAL) module is required to create a Shapefile."},
    "shapefile_save_as":  {"fr": "Enregistrer le Shapefile sous",     "en": "Save Shapefile as"},
    "shapefile_mosaic_lbl":{"fr": "Emprise globale (mosaïque)",       "en": "Global extent (mosaic)"},
    "shapefile_single_lbl":{"fr": "Emprise du fichier",               "en": "File extent"},
    "shapefile_cancelled":{"fr": "Création du Shapefile annulée.",   "en": "Shapefile creation cancelled."},
    # ── Carte À propos
    "card_about":         {"fr": "ℹ️  Informations & Liens",           "en": "ℹ️  Information & Links"},
    "about_desc":         {"fr": "GeoConvert est un utilitaire open-source basé sur GDAL, conçu\npour simplifier la conversion et le traitement d'images géospatiales.",
                           "en": "GeoConvert is an open-source utility based on GDAL, designed\nto simplify the conversion and processing of geospatial images."},
    "btn_license":        {"fr": "📄 Licence",                         "en": "📄 License"},
    "btn_github":         {"fr": "⭐ GitHub",                          "en": "⭐ GitHub"},
    "btn_guide":          {"fr": "📖 Guide",                           "en": "📖 Guide"},
    "btn_bug":            {"fr": "🐛 Signaler un bug",                 "en": "🐛 Report a bug"},
    "btn_gdal_docs":      {"fr": "🌐 Docs GDAL",                      "en": "🌐 GDAL Docs"},
    "btn_sysinfo":        {"fr": "📊 Système",                        "en": "📊 System"},
    "sysinfo_title":      {"fr": "Informations Système",               "en": "System Information"},
    "sysinfo_gdal":       {"fr": "Version GDAL",                       "en": "GDAL Version"},
    "sysinfo_python":     {"fr": "Version Python",                     "en": "Python Version"},
    "sysinfo_platform":   {"fr": "Plateforme",                         "en": "Platform"},
    "sysinfo_drivers":    {"fr": "Drivers raster disponibles",         "en": "Available raster drivers"},
    "sysinfo_pillow":     {"fr": "Pillow (PIL)",                       "en": "Pillow (PIL)"},
    "sysinfo_ctk":        {"fr": "CustomTkinter",                      "en": "CustomTkinter"},
    "sysinfo_numpy":      {"fr": "NumPy",                              "en": "NumPy"},
    "sysinfo_installed":  {"fr": "Installé",                           "en": "Installed"},
    "sysinfo_missing":    {"fr": "Non installé",                       "en": "Not installed"},
    # ── Carte Découpage
    "card_clip":          {"fr": "✂️  Découpage (AOI)",               "en": "✂️  Clipping (AOI)"},
    "chk_clip":           {"fr": "Activer le recadrage",               "en": "Enable clipping"},
    "btn_autoextent":     {"fr": "📐 Auto-emprise",                    "en": "📐 Auto-extent"},
    "btn_visual":         {"fr": "👁️ Sélection Visuelle",             "en": "👁️ Visual Selection"},
    # ── Carte Exécution
    "card_exec":          {"fr": "🚀  Progression et Journal",         "en": "🚀  Progress & Log"},
    "btn_convert":        {"fr": "LANCER LA CONVERSION",               "en": "START CONVERSION"},
    "btn_stop":           {"fr": "ARRÊTER",                            "en": "STOP"},
    "btn_stop_ing":       {"fr": "🛑 Arrêt...",                        "en": "🛑 Stopping..."},
    "status_ready":       {"fr": "Prêt",                               "en": "Ready"},
    # ── Boîtes de dialogue
    "dlg_no_file_title":  {"fr": "Aucun fichier",                      "en": "No file"},
    "dlg_no_file_msg":    {"fr": "Veuillez sélectionner au moins un fichier source.",
                           "en": "Please select at least one source file."},
    "dlg_invalid_coords_title": {"fr": "Coordonnées invalides",        "en": "Invalid coordinates"},
    "dlg_invalid_coords_msg":   {"fr": "Les coordonnées de découpage doivent être des nombres valides.",
                                  "en": "Clipping coordinates must be valid numbers."},
    "dlg_done_title":     {"fr": "Terminé",                            "en": "Done"},
    "dlg_error_title":    {"fr": "Erreur",                             "en": "Error"},
    "dlg_warn_title":     {"fr": "Avertissement",                      "en": "Warning"},
    "dlg_pil_title":      {"fr": "PIL Manquant",                       "en": "PIL Missing"},
    "dlg_pil_msg":        {"fr": "La bibliothèque Pillow est requise pour le sélecteur visuel.\nInstallez-la avec : pip install Pillow",
                           "en": "The Pillow library is required for the visual selector.\nInstall it with: pip install Pillow"},
    "dlg_no_file_extent": {"fr": "Sélectionnez au moins un fichier source pour récupérer l'emprise.",
                           "en": "Select at least one source file to retrieve the extent."},
    "dlg_no_file_visual": {"fr": "Sélectionnez au moins un fichier source pour la sélection visuelle.",
                           "en": "Select at least one source file for visual selection."},
    "dlg_no_valid_files": {"fr": "Aucun fichier image valide trouvé.",  "en": "No valid image file found."},
    "dlg_thumb_error":    {"fr": "Impossible de générer la miniature.", "en": "Unable to generate thumbnail."},
    # ── Journal
    "log_start":          {"fr": "▶  Début de la conversion — format : ", "en": "▶  Starting conversion — format: "},
    "log_files_count":    {"fr": "fichier(s) à traiter",               "en": "file(s) to process"},
    "log_mosaic_mode":    {"fr": "Mode Mosaïque activé : 1 seul fichier de sortie sera généré via VRT",
                           "en": "Mosaic Mode enabled: 1 single output file will be generated via VRT"},
    "log_extent_ok":      {"fr": "📍 Emprise récupérée depuis : ",      "en": "📍 Extent retrieved from: "},
    "log_extent_fail":    {"fr": "⚠️  Impossible de lire l'emprise de : ", "en": "⚠️  Unable to read extent of: "},
    "log_stop_sent":      {"fr": "🛑 Demande d'arrêt envoyée (le fichier en cours se terminera ou sera annulé)...",
                           "en": "🛑 Stop request sent (the current file will complete or be cancelled)..."},
    "log_thumb_gen":      {"fr": "🔍 Génération de la miniature pour : ",  "en": "🔍 Generating thumbnail for: "},
    "log_mosaic_thumb":   {"fr": "🧩 Génération de l'emprise globale pour ",  "en": "🧩 Generating global extent for "},
    "log_mosaic_thumb2":  {"fr": " fichiers...",                         "en": " files..."},
    "log_clip_updated":   {"fr": "🎯 Zone de découpage mise à jour via le sélecteur visuel.",
                           "en": "🎯 Clipping area updated via visual selector."},
    "log_epsg_invalid":   {"fr": "⚠️  Code EPSG invalide ignoré : ",    "en": "⚠️  Invalid EPSG code ignored: "},
    "log_done":           {"fr": "✅  Conversion terminée : ",           "en": "✅  Conversion complete: "},
    "log_done_mosaic":    {"fr": "✅  Mosaïque terminée : ",             "en": "✅  Mosaic complete: "},
    "log_done_suffix":    {"fr": " fichier(s) converti(s)\n",           "en": " file(s) converted\n"},
    "log_done_mosaic_suffix": {"fr": " fichiers fusionnés avec succès\n", "en": " files merged successfully\n"},
    "log_init":           {"fr": "Initialisation…",                     "en": "Initialising…"},
    "log_mosaic_build":   {"fr": "Construction de la mosaïque virtuelle VRT...",
                           "en": "Building virtual VRT mosaic..."},
    "log_mosaic_pct":     {"fr": "Mosaïquage + Conversion — ",          "en": "Mosaicking + Conversion — "},
    "log_success_mosaic": {"fr": "Mosaïque créée : ",                   "en": "Mosaic created: "},
    "log_error_mosaic":   {"fr": "Impossible de créer la mosaïque : ",  "en": "Unable to create mosaic: "},
    "log_success":        {"fr": "   ✓  ",                              "en": "   ✓  "},
    "log_fail":           {"fr": "   ✗  ",                              "en": "   ✗  "},
    "log_time":           {"fr": "   Temps : ",                         "en": "   Time: "},
    "log_error":          {"fr": "\n✗  Erreur : ",                      "en": "\n✗  Error: "},
    # ── Boîtes de dialogue fin de conversion
    "dlg_done_mosaic_msg":{"fr": "Mosaïque créée avec succès !\nSource : ", "en": "Mosaic created successfully!\nSource: "},
    "dlg_done_files":     {"fr": " fichiers\nDestination : ",            "en": " files\nDestination: "},
    "dlg_done_batch_msg": {"fr": " fichier(s) converti(s) vers ",       "en": " file(s) converted to "},
    # ── Fenêtre Inspection
    "inspect_title":      {"fr": "Inspection : ",                       "en": "Inspection: "},
    "inspect_group_title":{"fr": "Résumé de Groupe : ",                 "en": "Group Summary: "},
    "inspect_group_files":{"fr": " fichiers",                          "en": " files"},
    "inspect_general":    {"fr": "📍 Informations générales",           "en": "📍 General Information"},
    "inspect_format":     {"fr": "Format",                              "en": "Format"},
    "inspect_dims":       {"fr": "Dimensions",                          "en": "Dimensions"},
    "inspect_bands":      {"fr": "Bandes",                              "en": "Bands"},
    "inspect_size":       {"fr": "Taille",                              "en": "Size"},
    "inspect_res":        {"fr": "Résolution",                          "en": "Resolution"},
    "inspect_geo":        {"fr": "🌐 Géoréférencement & Emprise",       "en": "🌐 Georef & Extent"},
    "inspect_proj":       {"fr": "Projection",                          "en": "Projection"},
    "inspect_band_n":     {"fr": "🎨 Bande ",                           "en": "🎨 Band "},
    "inspect_dtype":      {"fr": "Type",                                "en": "Type"},
    "inspect_interp":     {"fr": "Interp. Couleur",                     "en": "Color Interp"},
    "inspect_nodata":     {"fr": "NoData",                              "en": "NoData"},
    "inspect_none":       {"fr": "Aucun",                               "en": "None"},
    "inspect_stats":      {"fr": "📊 Statistiques Globales",            "en": "📊 Global Statistics"},
    "inspect_total":      {"fr": "Total Fichiers",                      "en": "Total Files"},
    "inspect_total_size": {"fr": "Poids Total",                         "en": "Total Size"},
    "inspect_main_type":  {"fr": "Type Principal",                      "en": "Main Type"},
    "inspect_coherence":  {"fr": "秤 Cohérence Technique",             "en": "⚖️ Technical Consistency"},
    "inspect_projections":{"fr": "Projections détectées",               "en": "Detected projections"},
    "inspect_status_ok":  {"fr": "✅ Homogène",                         "en": "✅ Homogeneous"},
    "inspect_status_warn":{"fr": "⚠ Hétérogène (Attention)",           "en": "⚠ Heterogeneous (Warning)"},
    "inspect_bbox":       {"fr": "🌍 Emprise combinée (BBox)",          "en": "🌍 Combined Extent (BBox)"},
    # ── Fenêtre Estimation
    "estimate_title":     {"fr": "Estimation de l'Espace Disque",       "en": "Disk Space Estimate"},
    "estimate_header":    {"fr": "⚖️ Prédiction de stockage",           "en": "⚖️ Storage Prediction"},
    "estimate_files":     {"fr": "Fichiers à traiter",                  "en": "Files to process"},
    "estimate_mode":      {"fr": "Mode de traitement",                  "en": "Processing mode"},
    "estimate_mode_mosaic":{"fr": "🧩 Mosaïque (Fusion)",               "en": "🧩 Mosaic (Merge)"},
    "estimate_mode_batch":{"fr": "📦 Batch (Individuel)",               "en": "📦 Batch (Individual)"},
    "estimate_zone":      {"fr": "Zone de sortie",                      "en": "Output area"},
    "estimate_zone_clip": {"fr": "✂️ Découpage (AOI)",                  "en": "✂️ Clipping (AOI)"},
    "estimate_zone_full": {"fr": "🖼️ Image entière",                  "en": "🖼️ Full image"},
    "estimate_format":    {"fr": "Format cible",                        "en": "Target format"},
    "estimate_compress":  {"fr": "Compression",                         "en": "Compression"},
    "estimate_total":     {"fr": "Estimation Totale",                   "en": "Total Estimate"},
    "estimate_warn_10g":  {"fr": "⚠ Traitement lourd détecté (BigTIFF activé)",
                           "en": "⚠ Heavy processing detected (BigTIFF enabled)"},
    "estimate_warn_50g":  {"fr": "🚨 Attention : Volume de données très important !",
                           "en": "🚨 Warning: Very large data volume!"},
    "btn_understood":     {"fr": "Compris",                             "en": "Got it"},
    # ── Fenêtre Sélection Visuelle
    "visual_title":       {"fr": "Sélection visuelle (Rectangle)",      "en": "Visual selection (Rectangle)"},
    "visual_loupe":       {"fr": "🔍 Loupe (x4)",                       "en": "🔍 Zoom (x4)"},
    "visual_actions":     {"fr": "🛠️ Actions",                         "en": "🛠️ Actions"},
    "visual_validate":    {"fr": "✅ Valider",                          "en": "✅ Confirm"},
    "visual_all":         {"fr": "🖼️ Toute l'image",                  "en": "🖼️ Full image"},
    "visual_clear":       {"fr": "🧹 Effacer",                         "en": "🧹 Clear"},
    "visual_cancel":      {"fr": "❌ Annuler",                          "en": "❌ Cancel"},
    "visual_shortcuts":   {"fr": "⌨️ Raccourcis",                      "en": "⌨️ Shortcuts"},
    "visual_hint":        {"fr": "💡 Astuce : Tracez un rectangle pour définir la zone de découpe",
                           "en": "💡 Tip: Draw a rectangle to define the clipping area"},
    "shortcut_drag":      {"fr": "Clic + Glisse",                       "en": "Click + Drag"},
    "shortcut_drag_desc": {"fr": "Tracer zone",                         "en": "Draw area"},
    "shortcut_enter":     {"fr": "Entrée",                              "en": "Enter"},
    "shortcut_enter_desc":{"fr": "Valider",                             "en": "Confirm"},
    "shortcut_esc":       {"fr": "Echap",                               "en": "Esc"},
    "shortcut_esc_desc":  {"fr": "Annuler",                             "en": "Cancel"},
    # ── Fenêtre EPSG
    "epsg_title":         {"fr": "Recherche de code EPSG",              "en": "EPSG code search"},
    "epsg_search_label":  {"fr": "🔍 Rechercher :",                     "en": "🔍 Search:"},
    "epsg_placeholder":   {"fr": "Ex: 2154, France, Lambert...",        "en": "E.g.: 4326, World, WGS84..."},
    "epsg_col_code":      {"fr": "Code EPSG",                           "en": "EPSG Code"},
    "epsg_col_name":      {"fr": "Nom",                                 "en": "Name"},
    "epsg_col_desc":      {"fr": "Description",                         "en": "Description"},
    "epsg_validate":      {"fr": "✅ Valider",                          "en": "✅ Confirm"},
    "epsg_cancel":        {"fr": "❌ Annuler",                          "en": "❌ Cancel"},
    # ── Fenêtre Licence & Guide
    "license_title":      {"fr": "Licence Apache 2.0",                  "en": "Apache 2.0 License"},
    "help_title":         {"fr": "Guide Rapide",                        "en": "Quick Guide"},
    "help_msg":           {"fr": "Bienvenue dans GeoConvert !\n\n1. Sélectionnez un ou plusieurs fichiers sources.\n2. Choisissez un format et un dossier de destination.\n3. Configurez les options de compression et de traitement.\n4. (Optionnel) Découpez votre image avec le recadrage.\n5. Cliquez sur Convertir pour lancer le processus.\n\nPour plus d'informations, consultez le dépôt GitHub.",
                           "en": "Welcome to GeoConvert!\n\n1. Select one or more source files.\n2. Choose a format and a destination folder.\n3. Configure compression and processing options.\n4. (Optional) Clip your image with cropping.\n5. Click Convert to start the process.\n\nFor more information, check the GitHub repository."},
    # ── Compression options labels
    "comp_none":          {"fr": "Sans",                                "en": "None"},
    "comp_lzw":           {"fr": "LZW (Rapide)",                       "en": "LZW (Fast)"},
    "comp_deflate":       {"fr": "DEFLATE (Recommandé)",               "en": "DEFLATE (Recommended)"},
    "comp_jpeg":          {"fr": "JPEG (Avec perte)",                   "en": "JPEG (Lossy)"},
    "comp_auto":          {"fr": "Automatique (Curseur)",               "en": "Automatic (Slider)"},
    "comp_default":       {"fr": "Défaut",                              "en": "Default"},
    "comp_png9":          {"fr": "ZLEVEL=9 (Max)",                     "en": "ZLEVEL=9 (Max)"},
    "comp_png6":          {"fr": "ZLEVEL=6 (Défaut)",                  "en": "ZLEVEL=6 (Default)"},
    "comp_png1":          {"fr": "ZLEVEL=1 (Rapide)",                  "en": "ZLEVEL=1 (Fast)"},
    # ── Progression
    "progress_init":      {"fr": "Initialisation…",                     "en": "Initialising…"},
    "inspect_loading":    {"fr": "⏳ Chargement des métadonnées…",        "en": "⏳ Loading metadata…"},
    "estimate_loading":   {"fr": "⏳ Calcul en cours…",                    "en": "⏳ Computing…"},
    "shapefile_dir_lbl":  {"fr": "📁 Dossier :",                          "en": "📁 Folder:"},
    "shapefile_name_lbl": {"fr": "💾 Nom :",                              "en": "💾 Name:"},
    "btn_save":           {"fr": "✅ Enregistrer",                          "en": "✅ Save"},
    "btn_cancel_action":  {"fr": "❌ Annuler",                              "en": "❌ Cancel"},
    "estimate_pred_title":{"fr": "⚖️ Prédiction de stockage",              "en": "⚖️ Storage Prediction"},
    "label_compress":     {"fr": "Compression :",                          "en": "Compression:"},
    "log_done_summary":   {"fr": "Terminé — ",                             "en": "Done — "},
    "log_done_ok":        {"fr": " réussi(s)",                            "en": " succeeded"},
    "progress_mosaic":    {"fr": "Construction de la mosaïque virtuelle VRT...",
                           "en": "Building virtual VRT mosaic..."},
    "progress_done":      {"fr": "Terminé — ",                          "en": "Done — "},
    "progress_done_ok":   {"fr": " réussi",                             "en": " succeeded"},
}

def _toggle_language() -> None:
    """Bascule la langue et sauvegarde la préférence (appelé depuis GeoConvertApp)."""
    global _current_lang
    _current_lang = "en" if _current_lang == "fr" else "fr"
    _prefs["lang"] = _current_lang
    _save_prefs(_prefs)

# ─── Utilitaire Info-bulle (ToolTip) ──────────────────────────────────────────
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        
        # Sur CustomTkinter, les événements doivent souvent être liés au widget interne (_canvas ou _name)
        # Mais le .bind() standard de CTk gère <Enter> et <Leave>. Certains widgets (CTkSegmentedButton) lèvent NotImplementedError.
        try:
            self.widget.bind("<Enter>", self.schedule_tip, add="+")
            self.widget.bind("<Leave>", self.hide_tip, add="+")
            self.widget.bind("<ButtonPress>", self.hide_tip, add="+")
        except Exception:
            pass

    def schedule_tip(self, event=None):
        """Lance un timer pour afficher l'info-bulle après 500ms."""
        if self.id:
            self.widget.after_cancel(self.id)
        self.id = self.widget.after(500, self.show_tip)

    def show_tip(self):
        if not self.text or self.tip_window: return
        
        # Positionnement intelligent sous le curseur
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(1)
        tw.wm_geometry("+%d+%d" % (x, y))
        tw.attributes("-topmost", True)
        
        # Couleurs dynamiques selon le thème actif
        colors = get_colors()
        bg_color = colors["surface2"]
        accent_color = colors["accent"]
        fg_color = colors["text"]  # Noir en thème clair, blanc en thème sombre
        
        # On crée un cadre pour la bordure
        frame = tk.Frame(tw, background=accent_color, padx=1, pady=1)
        frame.pack()
        
        label = tk.Label(frame, text=self.text, justify=tk.LEFT,
                      background=bg_color, foreground=fg_color,
                      relief=tk.FLAT, borderwidth=0,
                      font=("Helvetica", "9", "normal"), 
                      padx=10, pady=7)
        label.pack()

    def hide_tip(self, event=None):
        if self.id:
            self.widget.after_cancel(self.id)
            self.id = None
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def add_tooltip(widget, text):
    tip = ToolTip(widget, text)
    
    # Patch spécial CustomTkinter : lier les événements du canvas interne
    # au MÊME ToolTip (sans créer un second, pour éviter le doublon)
    if hasattr(widget, "_canvas"):
        try:
            widget._canvas.bind("<Enter>", tip.schedule_tip, add="+")
            widget._canvas.bind("<Leave>", tip.hide_tip, add="+")
            widget._canvas.bind("<ButtonPress>", tip.hide_tip, add="+")
        except Exception:
            pass

# ─── Menu déroulant CTK maison (sans clignotement) ──────────────────────────

class FlatDropdown:
    """Menu déroulant au design identique au CTkOptionMenu natif.

    Implémentation : un CTkOptionMenu privé inséré dans un tk.Frame natif
    avec pack_propagate(False). Le tk.Frame absorbe tous les reflows CTK
    — le parent ne clignotera plus jamais.
    
    L'API est identique à l'ancien comp_menu :
      - set_values(values)          → change la liste sans flash
      - configure(state=...)        → active/désactive
      - configure(fg_color=..., text_color=..., border_color=...)
      - pack(**kwargs)              → délégué au tk.Frame conteneur
    """

    def __init__(self, parent, variable: tk.StringVar, values: list,
                 width=180, height=30):
        # Le conteneur tk.Frame natif absorbe les reflows de son enfant CTK
        self._frame = tk.Frame(parent, width=width, height=height,
                               bg=COLORS["surface"])  # bg = surface du parent
        self._frame.pack_propagate(False)

        self._var    = variable
        self._values = list(values)
        self._width  = width
        self._height = height

        # CTkOptionMenu intérieur — mêmes paramètres que fmt_menu
        self._menu = ctk.CTkOptionMenu(
            self._frame,
            variable=variable,
            values=values,
            width=width,
            height=height,
            corner_radius=8,
            fg_color=COLORS["surface2"],
            button_color=COLORS["surface2"],
            button_hover_color=COLORS["accent"],
            dropdown_fg_color=COLORS["surface2"],
            text_color=COLORS["text"],
            dropdown_text_color=COLORS["text"],
            dropdown_hover_color=COLORS["surface"],
        )
        self._menu.pack(fill="both", expand=True)

    # —— API publique —————————————————————————————————————

    def set_values(self, values: list):
        """Change la liste d'options sans provoquer de reflow sur le parent."""
        self._values = list(values)
        # configure(values=...) reconstruit le CTkOptionMenu INTERNE,
        # mais le tk.Frame parent a pack_propagate(False) donc le reflow
        # est absorbé et n'affecte pas la carte.
        self._menu.configure(values=values)

    def configure(self, **kwargs):
        """Transmet state/couleurs au CTkOptionMenu interne."""
        state = kwargs.pop("state", None)
        if state == "disabled":
            self._menu.configure(state="disabled",
                                 text_color=COLORS["text_dim"],
                                 button_color=COLORS["surface2"])
        elif state in ("readonly", "normal"):
            self._menu.configure(state="normal",
                                 text_color=COLORS["text"],
                                 button_color=COLORS["surface2"])
        if kwargs:
            # Convertir text_color/fg_color/border_color pour CTkOptionMenu
            menu_kwargs = {}
            if "fg_color"     in kwargs: menu_kwargs["fg_color"]              = kwargs["fg_color"]
            if "text_color"   in kwargs: menu_kwargs["text_color"]            = kwargs["text_color"]
            if "button_color" in kwargs: menu_kwargs["button_color"]          = kwargs["button_color"]
            if "bg" in kwargs:           self._frame.configure(bg=kwargs["bg"])
            if menu_kwargs:
                self._menu.configure(**menu_kwargs)

    def pack(self, **kwargs):
        """Délègue le pack au tk.Frame conteneur."""
        self._frame.pack(**kwargs)

    def pack_forget(self):
        self._frame.pack_forget()



# ─── Sélecteur Visuel ────────────────────────────────────────────────────────

class VisualSelector(tk.Toplevel):
    """Fenêtre de sélection visuelle pour le découpage."""
    def __init__(self, parent, thumb_path, extent, callback):
        super().__init__(parent)
        self.title(t("visual_title"))
        self.geometry("1200x850")
        self.configure(bg=C("bg"))  # C() est dynamique : reflète le thème actif
        self.transient(parent)
        self.grab_set()

        # Layout Split: Left (Canvas) | Right (Zoom + Help)
        self.main_frame = tk.Frame(self, bg=C("bg"))
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.left_col = tk.Frame(self.main_frame, bg=C("bg"))
        self.left_col.pack(side="left", fill="both", expand=True)

        self.right_col = tk.Frame(self.main_frame, bg=C("surface"), width=300)
        self.right_col.pack(side="right", fill="y", padx=(20, 0))
        if not CTK: self.right_col.configure(highlightbackground=C("accent"), highlightthickness=1)

        self.extent = extent
        self.callback = callback
        self.thumb_path = thumb_path
        
        # Charger l'image
        self.img = Image.open(thumb_path)
        self.photo = ImageTk.PhotoImage(self.img)
        self.img_w, self.img_h = self.img.size
        
        # Canvas (Left)
        self.canvas = tk.Canvas(self.left_col, width=self.img_w, height=self.img_h, 
                               bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        # Zoom Area (Right)
        tk.Label(self.right_col, text=t("visual_loupe"), bg=C("surface"), 
                 fg=C("accent"), font=("Helvetica", 12, "bold")).pack(pady=(20, 10))
        
        self.zoom_canvas = tk.Canvas(self.right_col, width=280, height=280, 
                                    bg="black", highlightthickness=1, highlightbackground=C("accent"))
        self.zoom_canvas.pack(padx=10)
        
        # Créer l'item image UNE SEULE FOIS — sera mis à jour via itemconfig()
        self._zoom_item = self.zoom_canvas.create_image(0, 0, anchor="nw")
        # Créer les lignes du curseur central UNE SEULE FOIS — seront repositionnées via coords()
        self._cursor_v = self.zoom_canvas.create_line(140, 130, 140, 150, fill=C("accent2"), width=1)
        self._cursor_h = self.zoom_canvas.create_line(130, 140, 150, 140, fill=C("accent2"), width=1)

        self.zoom_photo = None  # Référence forte pour éviter le garbage collection
        
        # --- Actions Panel ---
        tk.Label(self.right_col, text=t("visual_actions"), bg=COLORS["surface"], 
                 fg=COLORS["accent"], font=("Helvetica", 12, "bold")).pack(pady=(20, 10))
        
        if CTK:
            ctk.CTkButton(self.right_col, text=t("visual_validate"), height=40,
                          fg_color=C("accent2"), text_color=C("bg"),
                          font=("Helvetica", 12, "bold"),
                          command=self.confirm).pack(fill="x", padx=20, pady=(0, 15))

            ctk.CTkButton(self.right_col, text=t("visual_all"), height=32,
                          fg_color=C("surface2"), text_color=C("text"),
                          command=self.select_all).pack(fill="x", padx=20, pady=5)
            
            ctk.CTkButton(self.right_col, text=t("visual_clear"), height=32,
                          fg_color=C("surface2"), text_color=C("text"),
                          command=self.clear_selection).pack(fill="x", padx=20, pady=5)
            
            ctk.CTkButton(self.right_col, text=t("visual_cancel"), height=32,
                          fg_color="#CC0000", hover_color="#990000", text_color="white",
                          command=self.destroy).pack(fill="x", padx=20, pady=20)
        else:
            tk.Button(self.right_col, text=t("visual_validate"), command=self.confirm).pack(fill="x", padx=20, pady=(0, 10))
            tk.Button(self.right_col, text=t("visual_all"), command=self.select_all).pack(fill="x", padx=20, pady=5)
            tk.Button(self.right_col, text=t("visual_clear"), command=self.clear_selection).pack(fill="x", padx=20, pady=5)
            tk.Button(self.right_col, text=t("visual_cancel"), command=self.destroy).pack(fill="x", padx=20, pady=5)

        # --- Help / Shortcuts ---
        help_frame = tk.Frame(self.right_col, bg=C("surface"))
        help_frame.pack(fill="x", side="bottom", pady=20)
        
        tk.Label(help_frame, text=t("visual_shortcuts"), bg=C("surface"), 
                 fg=C("text_dim"), font=("Helvetica", 10, "bold")).pack(pady=(0, 5))
        
        shortcuts = [
            (t("shortcut_drag"),  t("shortcut_drag_desc")),
            (t("shortcut_enter"), t("shortcut_enter_desc")),
            (t("shortcut_esc"),   t("shortcut_esc_desc")),
        ]
        for key, desc in shortcuts:
            row = tk.Frame(help_frame, bg=C("surface"))
            row.pack(fill="x", padx=20)
            tk.Label(row, text=key, bg=C("surface"), fg=C("accent2"), font=("Helvetica", 9, "bold")).pack(side="left")
            tk.Label(row, text=f" : {desc}", bg=C("surface"), fg=C("text_dim"), font=("Helvetica", 9)).pack(side="left")
        
        # Rectangle de sélection
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.cur_x = None
        self.cur_y = None
        
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)
        self.canvas.bind("<Motion>", self.update_zoom)
        
        # Raccourcis clavier
        self.bind("<Return>", lambda e: self.confirm())
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Baseline help text
        if CTK:
            ctk.CTkLabel(self.left_col, text=t("visual_hint"),
                        text_color=C("text_dim"), font=("Helvetica", 11, "italic")).pack(pady=10)
        else:
            tk.Label(self.left_col, text=t("visual_hint"), bg=C("bg"), fg=C("text")).pack(pady=10)

    def select_all(self):
        """Sélectionne toute l'image."""
        self.start_x, self.start_y = 0, 0
        self.cur_x, self.cur_y = self.img_w, self.img_h
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(0, 0, self.img_w, self.img_h, 
                                               outline=C("accent"), width=2)
        self.canvas.coords(self.rect, 0, 0, self.img_w, self.img_h)

    def clear_selection(self):
        """Efface la sélection en cours."""
        if self.rect:
            self.canvas.delete(self.rect)
            self.rect = None
            self.start_x = self.start_y = self.cur_x = self.cur_y = None

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, 1, 1, 
                                               outline=C("accent"), width=2)

    def on_move_press(self, event):
        self.cur_x = event.x
        self.cur_y = event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, self.cur_x, self.cur_y)
        self.update_zoom(event)

    def update_zoom(self, event):
        """Met à jour la vue zoomée sous le curseur.
        
        Optimisé : réutilise les items Canvas existants (itemconfig/tag_raise)
        au lieu d'en créer de nouveaux à chaque mouvement de souris.
        """
        x, y = event.x, event.y
        
        # Définir la boîte de crop sur l'image originale (70x70 px → zoom 4x vers 280x280)
        crop_size = 70
        half = crop_size // 2
        
        left = max(0, min(self.img_w - crop_size, x - half))
        top_px = max(0, min(self.img_h - crop_size, y - half))
        
        # Crop et Resize
        cropped = self.img.crop((left, top_px, left + crop_size, top_px + crop_size))
        zoomed = cropped.resize((280, 280), Image.NEAREST)  # NEAREST pour bien voir les pixels
        
        # Réutiliser l'item image existant : évite la fuite mémoire et les empilements
        self.zoom_photo = ImageTk.PhotoImage(zoomed)
        self.zoom_canvas.itemconfig(self._zoom_item, image=self.zoom_photo)
        
        # Remonter le curseur au premier plan (sans le recréer)
        self.zoom_canvas.tag_raise(self._cursor_v)
        self.zoom_canvas.tag_raise(self._cursor_h)

    def on_button_release(self, event):
        pass

    def confirm(self):
        if not self.rect or self.cur_x is None:
            self.destroy()
            return
            
        # Mapper les coordonnées canvas [0, img_w] -> emprise [min, max]
        x1, y1, x2, y2 = self.canvas.coords(self.rect)
        
        # Trier pour avoir min/max
        canv_xmin, canv_xmax = min(x1, x2), max(x1, x2)
        canv_ymin, canv_ymax = min(y1, y2), max(y1, y2)
        
        # Calculer en monde réel
        ext_xmin = self.extent["ulx"]
        ext_xmax = self.extent["lrx"]
        ext_ymin = self.extent["lry"]
        ext_ymax = self.extent["uly"]
        
        res_xmin = ext_xmin + (canv_xmin / self.img_w) * (ext_xmax - ext_xmin)
        res_xmax = ext_xmin + (canv_xmax / self.img_w) * (ext_xmax - ext_xmin)
        # Note Y est souvent inversé en raster (Top -> Bottom)
        res_ymax = ext_ymax - (canv_ymin / self.img_h) * (ext_ymax - ext_ymin)
        res_ymin = ext_ymax - (canv_ymax / self.img_h) * (ext_ymax - ext_ymin)
        
        self.callback(res_xmin, res_ymax, res_xmax, res_ymin)
        self.destroy()
        
        # Supprimer la miniature
        try:
            os.remove(self.thumb_path)
        except:
            pass

# ─── Sélecteur EPSG ──────────────────────────────────────────────────────────

class EPSGSelector(tk.Toplevel):
    """Fenêtre modale pour rechercher et sélectionner un code EPSG."""
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title(t("epsg_title"))
        self.geometry("600x500")
        self.configure(bg=C("bg"))  # C() est dynamique : reflète le thème actif
        self.transient(parent)
        self.grab_set()

        self.callback = callback

        # --- Layout ---
        # Search bar
        search_frame = tk.Frame(self, bg=C("bg"))
        search_frame.pack(fill="x", padx=20, pady=20)
        
        if CTK:
            ctk.CTkLabel(search_frame, text=t("epsg_search_label"), text_color=C("text")).pack(side="left", padx=(0, 10))
            self.search_var = tk.StringVar()
            self.search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var, width=300, 
                                            placeholder_text=t("epsg_placeholder"),
                                            fg_color=C("surface"), border_color=C("border"))
            self.search_entry.pack(side="left", fill="x", expand=True)
        else:
            tk.Label(search_frame, text=t("epsg_search_label"), bg=C("bg"), fg=C("text")).pack(side="left", padx=(0, 10))
            self.search_var = tk.StringVar()
            self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, bg=C("surface"), fg=C("text"))
            self.search_entry.pack(side="left", fill="x", expand=True)

        # Results List
        list_frame = tk.Frame(self, bg=C("bg"))
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Utiliser un Treeview pour l'affichage en colonnes
        columns = ("Code", "Nom", "Description")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Custom.Treeview")
        self.tree.heading("Code", text=t("epsg_col_code"))
        self.tree.heading("Nom", text=t("epsg_col_name"))
        self.tree.heading("Description", text=t("epsg_col_desc"))
        
        self.tree.column("Code", width=80, anchor="center")
        self.tree.column("Nom", width=150)
        self.tree.column("Description", width=300)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind("<Double-1>", self.on_double_click)

        # Style pour le Treeview — C() assure les couleurs du thème actif
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except:
            pass
        style.configure("Custom.Treeview", background=C("surface"), fieldbackground=C("surface"), foreground=C("text"))
        style.configure("Custom.Treeview.Heading", background=C("surface2"), foreground=C("text"))
        style.map("Custom.Treeview", background=[('selected', C("accent"))])

        # Buttons
        btn_frame = tk.Frame(self, bg=C("bg"))
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        if CTK:
            ctk.CTkButton(btn_frame, text=t("epsg_validate"), command=self.confirm,
                          fg_color=C("accent2"), hover_color="#059669", text_color="white").pack(side="right", padx=(10, 0))
            ctk.CTkButton(btn_frame, text=t("epsg_cancel"), command=self.destroy,
                          fg_color=C("surface2"), hover_color="#CC0000", text_color=C("text")).pack(side="right")
        else:
            tk.Button(btn_frame, text=t("epsg_validate"), command=self.confirm).pack(side="right", padx=(10, 0))
            tk.Button(btn_frame, text=t("epsg_cancel"), command=self.destroy).pack(side="right")

        # Load initial data
        try:
            from converter.epsg_bank import EPSG_BANK
            self.full_bank = EPSG_BANK
        except Exception as e:
            print(f"Error loading EPSG bank: {e}")
            self.full_bank = [{"code": 4326, "name": "WGS 84", "desc": "GPS"}]
        
        self.populate_list(self.full_bank)
        
        # Add trace here to avoid triggering during initialization before full_bank exists
        self.search_var.trace_add("write", self.on_search)
        
        self.after(100, self.search_entry.focus_set)

    def populate_list(self, data):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for entry in data:
            self.tree.insert("", "end", values=(entry["code"], entry["name"], entry["desc"]))

    def on_search(self, *args):
        """Déclenche la recherche avec un debounce de 150ms.
        
        Sans debounce, chaque frappe rebuilde tout le Treeview immédiatement.
        Avec debounce, on attend que l'utilisateur ait fini de taper.
        """
        if not hasattr(self, 'full_bank'):
            return
        # Annuler le timer précédent s'il existe
        if hasattr(self, '_search_after_id'):
            self.after_cancel(self._search_after_id)
        # Replanifier dans 150ms
        self._search_after_id = self.after(150, self._do_search)

    def _do_search(self):
        """Exécute la recherche et met à jour le Treeview (appelé après debounce)."""
        query = self.search_var.get().lower()
        if not query:
            self.populate_list(self.full_bank)
            return
        results = [
            item for item in self.full_bank
            if query in str(item["code"])
            or query in item["name"].lower()
            or query in item["desc"].lower()
        ]
        # Limiter l'affichage à 200 résultats pour éviter de saturar le Treeview
        self.populate_list(results[:200])

    def on_double_click(self, event):
        self.confirm()

    def confirm(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            code = item["values"][0]
            self.callback(str(code))
        self.destroy()

# ─── Application principale ───────────────────────────────────────────────────

class GeoConvertApp:
    def __init__(self):
        if CTK:
            ctk.set_appearance_mode("light" if _current_theme == "light" else "dark")
            ctk.set_default_color_theme("blue")
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()

        self.root.title("GeoConvert — GDAL")
        self.root.geometry("1100x850")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(1100, 750)
        self.root.resizable(True, True)
        
        # État conversion
        self.is_cancelled = False
        self._cached_file_count: int = 0  # Cache du nombre de fichiers (mis à jour en thread)
        self._bit_seg_active: bool = True  # État du widget profondeur (évite les redraws inutiles)

        # Variables
        self.source_files: list[Path] = []
        self.output_dir = tk.StringVar()
        self.format_var = tk.StringVar(value="GeoTIFF")
        self.epsg_var = tk.StringVar(value="")
        
        # Liste des EPSG courants pour aider l'utilisateur
        self.epsg_common = [
            "",
            "4326 - WGS84 (Monde GPS | Lat/Lon)",
            "3857 - Web Mercator (Google Maps)",
            "2154 - Lambert 93 (France métrop.)",
            "3946 - CC46 (France Zone 6)",
            "3947 - CC47 (France Zone 7)",
            "3948 - CC48 (France Zone 8)",
            "3949 - CC49 (France Zone 9)",
        ]
        # Variables avancées très utiles
        self.overviews_var = tk.BooleanVar(value=False)
        self.nodata_var = tk.BooleanVar(value=False)
        
        self.compress_var = tk.StringVar(value=t("comp_deflate")) # Options: Sans, LZW, DEFLATE, JPEG
        self.tiled_var = tk.BooleanVar(value=True)
        # Variable avancée cachée/optionnelle
        self.options_var = tk.StringVar()
        
        self.multithread_var = tk.BooleanVar(value=True)
        self.mosaic_var = tk.BooleanVar(value=False)
        self.mosaic_var.trace_add("write", lambda *a: self._update_mosaic_state())
        
        self.quality_var = tk.IntVar(value=85)
        self.resampling_var = tk.StringVar(value="Normal")
        self.mode_var = tk.StringVar(value="single")
        self.bit_depth_var = tk.StringVar(value="Original")
        
        # Découpage (Clipping)
        self.clip_var = tk.BooleanVar(value=False)
        self.clip_var.trace_add("write", lambda *a: self._toggle_clip_ui())
        self.ulx_var = tk.StringVar(value="")
        self.uly_var = tk.StringVar(value="")
        self.lrx_var = tk.StringVar(value="")
        self.lry_var = tk.StringVar(value="")

        self._build_ui()
        self.root.mainloop()

    # ── Construction de l'interface ───────────────────────────────────────────

    def _open_epsg_bank(self):
        def set_epsg(code):
            match = ""
            for common in self.epsg_common:
                if common.startswith(f"{code} -"):
                    match = common
                    break
            if match:
                self.epsg_var.set(match)
            else:
                try:
                    from converter.epsg_bank import EPSG_BANK
                    name_desc = ""
                    for item in EPSG_BANK:
                        if str(item["code"]) == str(code):
                            name_desc = item["name"]
                            break
                    if name_desc:
                        self.epsg_var.set(f"{code} - {name_desc}")
                    else:
                        self.epsg_var.set(f"{code}")
                except Exception:
                    self.epsg_var.set(f"{code}")
        
        EPSGSelector(self.root, set_epsg)

    def _build_ui(self):
        if CTK:
            self._build_ctk_ui()
        else:
            self._build_tk_ui()
        
        # Charger le logo si disponible
        self._load_branding()

    def _load_branding(self):
        """Charge le logo de l'application et définit l'icône de la fenêtre."""
        logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geoconvert_logo_final.png")
        if os.path.exists(logo_path) and HAS_PIL:
            try:
                img = Image.open(logo_path)
                
                # Créer une version sombre du logo pour le mode clair (en coloriant le blanc transparent en gris foncé)
                try:
                    dark_img = img.copy()
                    if dark_img.mode in ('RGBA', 'LA'):
                        # Remplacer les pixels RGB par la couleur du texte mode clair (#1E293B) tout en gardant l'alpha
                        r, g, b, a = dark_img.convert('RGBA').split()
                        color_img = Image.new("RGB", dark_img.size, (30, 41, 59)) # #1E293B
                        dark_img = Image.merge("RGBA", (*color_img.split(), a))
                    else:
                        dark_img = ImageOps.invert(dark_img.convert('RGB'))
                except Exception as e:
                    print(f"Avertissement conversion logo: {e}")
                    dark_img = img
                
                # 1. Image pour le header (DPI aware pour CTK)
                if CTK:
                    self.logo_image = ctk.CTkImage(light_image=dark_img, dark_image=img, size=(40, 40))
                else:
                    header_img = img.resize((40, 40), Image.LANCZOS)
                    self.logo_photo = ImageTk.PhotoImage(header_img)
                
                # 2. Icône de la fenêtre (Doit être un PhotoImage pour wm_iconphoto)
                # On garde une référence forte pour éviter le garbage collection
                self._window_icon = ImageTk.PhotoImage(img)
                self.root.wm_iconphoto(True, self._window_icon)
                
                if hasattr(self, 'lbl_logo'):
                    self.lbl_logo.configure(image=self.logo_image if CTK else self.logo_photo)
            except Exception as e:
                print(f"Error loading logo: {e}")

    def _build_ctk_ui(self):
        """Interface moderne Premium avec CustomTkinter."""

        # ── En-tête (Branding)
        header = ctk.CTkFrame(self.root, fg_color="transparent", height=80)
        header.pack(fill="x", padx=30, pady=(20, 10))

        logo_img = None
        if CTK and hasattr(self, "logo_image"):
            logo_img = self.logo_image
        elif hasattr(self, "logo_photo"):
            logo_img = self.logo_photo

        self.lbl_logo = ctk.CTkLabel(header, text="", image=logo_img, width=40, height=40)
        self.lbl_logo.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(
            header,
            text="GeoConvert",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=t("app_version"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=COLORS["surface2"],
            corner_radius=6,
            padx=10,
            pady=2,
            text_color=COLORS["text_dim"],
        ).pack(side="left", padx=15)

        # ── Bouton bascule Thème (à droite de l'en-tête)
        self.btn_theme = ctk.CTkButton(
            header,
            text="☀️",
            width=38, height=38,
            corner_radius=19,
            fg_color=COLORS["surface2"],
            hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=16),
            command=self._toggle_theme,
        )
        self.btn_theme.pack(side="right")
        add_tooltip(self.btn_theme, t("tooltip_theme"))

        # ── Bouton bascule Langue
        lang_icon = "🇬🇧" if _current_lang == "fr" else "🇫🇷"
        self.btn_lang = ctk.CTkButton(
            header,
            text=lang_icon,
            width=38, height=38,
            corner_radius=19,
            fg_color=COLORS["surface2"],
            hover_color=COLORS["accent"],
            font=ctk.CTkFont(size=16),
            command=self._toggle_lang,
        )
        self.btn_lang.pack(side="right", padx=(0, 8))
        add_tooltip(self.btn_lang, t("tooltip_lang"))

        # ── Corps principal (Deux colonnes de cartes)
        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=25, pady=0)

        # Left Column (Files + Settings)
        left_col = ctk.CTkFrame(body, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=(0, 12))

        # Colonne Droite (Découpage + Logs)
        right_col = ctk.CTkFrame(body, fg_color="transparent")
        right_col.pack(side="left", fill="both", expand=True, padx=(12, 0))

        # --- CARTE 1 : SOURCE & MODE (Gauche Haut) ---
        card_src = ctk.CTkFrame(left_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        card_src.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_src, text=t("card_source"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(15, 10))

        row_mode = ctk.CTkFrame(card_src, fg_color="transparent")
        row_mode.pack(fill="x", padx=20, pady=(0, 10))
        
        self.radio_single = ctk.CTkRadioButton(row_mode, text=t("radio_single"), variable=self.mode_var, value="single",
                           command=self._update_mode, text_color=COLORS["text"])
        self.radio_single.pack(side="left", padx=(0, 20))
        self.radio_batch = ctk.CTkRadioButton(row_mode, text=t("radio_batch"), variable=self.mode_var, value="batch",
                           command=self._update_mode, text_color=COLORS["text"])
        self.radio_batch.pack(side="left")

        btn_row = ctk.CTkFrame(card_src, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_select = ctk.CTkButton(btn_row, text=t("btn_choose_files"),
                                        command=self._select_files,
                                        fg_color=COLORS["accent"], hover_color="#4F46E5",
                                        text_color="white", font=ctk.CTkFont(weight="bold"),
                                        corner_radius=8, height=35)
        self.btn_select.pack(side="left", padx=(0, 15))
        
        self.lbl_files = ctk.CTkLabel(btn_row, text=t("no_file"),
                                      text_color=COLORS["text_dim"], font=ctk.CTkFont(size=12))
        self.lbl_files.pack(side="left", fill="x")

        # --- CARTE 2 : DESTINATION (Gauche Milieu) ---
        card_out = ctk.CTkFrame(left_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        card_out.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_out, text=t("card_dest"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(15, 10))

        # Format & EPSG
        row_fmt = ctk.CTkFrame(card_out, fg_color="transparent")
        row_fmt.pack(fill="x", padx=20, pady=(0, 10))

        from converter.formats import SUPPORTED_FORMATS
        fmt_names = list(SUPPORTED_FORMATS.keys())
        
        ctk.CTkLabel(row_fmt, text=t("label_format"), text_color=COLORS["text"]).pack(side="left", padx=(0, 5))
        fmt_menu = ctk.CTkOptionMenu(row_fmt, variable=self.format_var, values=fmt_names,
                                     width=120, height=30, corner_radius=8, text_color=COLORS["text"],
                                     fg_color=COLORS["surface2"], button_color=COLORS["accent"],
                                     dropdown_fg_color=COLORS["surface2"], command=self._on_format_change)
        fmt_menu.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(row_fmt, text=t("label_epsg"), text_color=COLORS["text"]).pack(side="left", padx=(0, 5))
        self.epsg_combo = ctk.CTkComboBox(row_fmt, variable=self.epsg_var, values=self.epsg_common,
                                          width=200, height=30, corner_radius=8, text_color=COLORS["text"],
                                          fg_color=COLORS["surface2"], border_color=COLORS["border"],
                                          button_color=COLORS["surface2"], dropdown_fg_color=COLORS["surface2"])
        self.epsg_combo.pack(side="left")

        btn_search_epsg = ctk.CTkButton(row_fmt, text="🔍", width=30, height=30, corner_radius=8,
                                        fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                        text_color=COLORS["text"], command=self._open_epsg_bank)
        btn_search_epsg.pack(side="left", padx=(5, 0))
        add_tooltip(btn_search_epsg, t("tooltip_epsg_search"))

        # Output Folder
        out_row = ctk.CTkFrame(card_out, fg_color="transparent")
        out_row.pack(fill="x", padx=20, pady=(0, 15))

        self.ent_out = ctk.CTkEntry(out_row, textvariable=self.output_dir, 
                                    placeholder_text=t("placeholder_output"),
                                    height=35, corner_radius=8, border_color=COLORS["border"])
        self.ent_out.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(out_row, text=t("btn_browse"), command=self._browse_output,
                      width=90, height=35, corner_radius=8, text_color=COLORS["text"],
                      fg_color=COLORS["surface2"], hover_color=COLORS["accent"]).pack(side="left")

        # --- CARTE 3 : TRAITEMENT (Gauche Milieu) ---
        card_proc = ctk.CTkFrame(left_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        card_proc.pack(fill="x")

        ctk.CTkLabel(card_proc, text=t("card_proc"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(15, 10))

        # Profondeur & Compression
        # NOTE: on utilise un frame avec grid() pour figer totalement le layout
        # et éviter tout reflow quand les widgets enfants changent d'état.
        row_depth = tk.Frame(card_proc, bg=COLORS["surface"], height=36)
        row_depth.pack(fill="x", padx=20, pady=(0, 10))
        row_depth.pack_propagate(False)
        self._row_depth_frame = row_depth  # référence pour mise à jour thème

        self._lbl_depth = tk.Label(row_depth, text=t("label_depth"), bg=COLORS["surface"],
                                   fg=COLORS["text"], font=("Helvetica", 12))
        self._lbl_depth.pack(side="left", padx=(0, 10))
        self.bit_seg = ctk.CTkSegmentedButton(row_depth, values=[t("seg_original"), t("seg_8bit"), t("seg_16bit")],
                                              variable=self.bit_depth_var,
                                              selected_color=COLORS["accent"],
                                              unselected_color=COLORS["surface2"],
                                              text_color=COLORS["text"])
        self.bit_seg.pack(side="left", padx=(0, 15))

        # Compression — FlatDropdown : widget CTK maison, zéro clignotement
        self.comp_menu = FlatDropdown(
            row_depth, variable=self.compress_var,
            values=[t("comp_none"), t("comp_lzw"), t("comp_deflate"), t("comp_jpeg")],
            width=200, height=30,
        )
        self.comp_menu.pack(side="left")

        # Quality & Resampling
        row_qual_res = ctk.CTkFrame(card_proc, fg_color="transparent", height=36)
        row_qual_res.pack(fill="x", padx=20, pady=(0, 10))
        row_qual_res.pack_propagate(False)

        ctk.CTkLabel(row_qual_res, text=t("label_quality"), text_color=COLORS["text"]).pack(side="left", padx=(0, 10))
        slider_qual = ctk.CTkSlider(row_qual_res, from_=1, to=100, variable=self.quality_var,
                                   width=150, button_color=COLORS["accent"], progress_color=COLORS["accent"])
        slider_qual.pack(side="left", padx=(0, 5))
        
        lbl_q_val = ctk.CTkLabel(row_qual_res, text="85%", text_color=COLORS["accent"], font=ctk.CTkFont(weight="bold"), width=42, anchor="w")
        lbl_q_val.pack(side="left", padx=(0, 20))
        self.quality_var.trace_add("write", lambda *a: lbl_q_val.configure(text=f"{int(self.quality_var.get())}%"))

        ctk.CTkLabel(row_qual_res, text=t("label_resampling"), text_color=COLORS["text"]).pack(side="left", padx=(0, 10))
        self.res_seg = ctk.CTkSegmentedButton(row_qual_res, values=[t("seg_speed"), t("seg_normal"), t("seg_quality")],
                                             variable=self.resampling_var,
                                             selected_color=COLORS["accent"],
                                             unselected_color=COLORS["surface2"],
                                             text_color=COLORS["text"])
        self.res_seg.pack(side="left")
        self.res_seg.set(t("seg_normal")) # Force la sélection visuelle initiale

        # Checkboxes (Mosaic, Multi-core, etc.)
        row_checks = ctk.CTkFrame(card_proc, fg_color="transparent")
        row_checks.pack(fill="x", padx=20, pady=(0, 15))

        checkboxes = [
            (t("chk_mosaic"),    self.mosaic_var,     COLORS["accent"], t("tooltip_mosaic")),
            (t("chk_multicore"), self.multithread_var, COLORS["accent"], t("tooltip_multicore")),
            (t("chk_tiling"),    self.tiled_var,       COLORS["accent"], t("tooltip_tiling")),
            (t("chk_pyramids"),  self.overviews_var,   COLORS["accent"], t("tooltip_pyramids")),
            (t("chk_nodata"),    self.nodata_var,       COLORS["accent"], t("tooltip_nodata")),
        ]
        for txt, var, color, ttip in checkboxes:
            cb = ctk.CTkCheckBox(row_checks, text=txt, variable=var,
                                 text_color=COLORS["text"], font=ctk.CTkFont(size=12),
                                 fg_color=color, checkbox_width=18, checkbox_height=18)
            cb.pack(side="left", padx=(0, 15))
            
            # Ajout info-bulle sur la checkbox texte ET composant
            add_tooltip(cb, ttip)
            
            # Affectation des attributs pour contrôle ultérieur
            if txt == t("chk_mosaic"): self.chk_mosaic = cb
            elif txt == t("chk_multicore"): self.chk_mt = cb
            elif txt == t("chk_tiling"): self.chk_tiled = cb
            elif txt == t("chk_pyramids"): self.chk_ovr = cb
            elif txt == t("chk_nodata"): self.chk_nodata = cb
            
        # Tooltips supplémentaires sur les autres composants de traitement
        add_tooltip(self.bit_seg, t("tooltip_depth"))
        add_tooltip(self.comp_menu, t("tooltip_compress"))
        add_tooltip(self.res_seg, t("tooltip_resampling"))
        add_tooltip(slider_qual, t("tooltip_quality"))

        # --- NOUVEAU : OUTILS RAPIDES (Espace vide) ---
        ctk.CTkLabel(card_proc, text=t("card_tools"), font=ctk.CTkFont(size=12, weight="bold"),
                     text_color=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(0, 5))
        
        row_tools = ctk.CTkFrame(card_proc, fg_color="transparent")
        row_tools.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_inspect = ctk.CTkButton(row_tools, text=t("btn_inspect"), command=self._inspect_metadata,
                                         width=160, height=32, corner_radius=8,
                                         fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                         text_color=COLORS["text"])
        self.btn_inspect.pack(side="left", padx=(0, 10))
        
        self.btn_estimate = ctk.CTkButton(row_tools, text=t("btn_estimate"), command=self._estimate_output_size,
                                          width=160, height=32, corner_radius=8,
                                          fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                          text_color=COLORS["text"])
        self.btn_estimate.pack(side="left", padx=(0, 10))

        self.btn_shapefile = ctk.CTkButton(row_tools, text=t("btn_shapefile"), command=self._create_shapefile,
                                           width=160, height=32, corner_radius=8,
                                           fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                           text_color=COLORS["text"])
        self.btn_shapefile.pack(side="left")
        
        # Tooltips pour les boutons
        add_tooltip(self.btn_inspect, t("tooltip_inspect"))
        add_tooltip(self.btn_estimate, t("tooltip_estimate"))
        add_tooltip(self.btn_shapefile, t("tooltip_shapefile"))

        # --- CARTE 4 : À PROPOS & LIENS (Gauche Bas) ---
        self.card_about = ctk.CTkFrame(left_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        self.card_about.pack(fill="both", expand=True, pady=(20, 0))

        self.lbl_card_about = ctk.CTkLabel(self.card_about, text=t("card_about"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"])
        self.lbl_card_about.pack(anchor="w", padx=20, pady=(15, 5))

        self.lbl_about_desc = ctk.CTkLabel(self.card_about, text=t("about_desc"),
                     text_color=COLORS["text_dim"], font=ctk.CTkFont(size=12), justify="left")
        self.lbl_about_desc.pack(anchor="w", padx=20, pady=(0, 15))

        # Ligne 1 : Licence, GitHub, Guide
        row_links = ctk.CTkFrame(self.card_about, fg_color="transparent")
        row_links.pack(fill="x", padx=20, pady=(0, 8))

        self.btn_license = ctk.CTkButton(row_links, text=t("btn_license"), command=self._show_license,
                                         width=90, height=32, corner_radius=8,
                                         fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                         text_color=COLORS["text"])
        self.btn_license.pack(side="left", padx=(0, 10))

        self.btn_github = ctk.CTkButton(row_links, text=t("btn_github"), command=self._open_github,
                                        width=90, height=32, corner_radius=8,
                                        fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                        text_color=COLORS["text"])
        self.btn_github.pack(side="left", padx=(0, 10))

        self.btn_help = ctk.CTkButton(row_links, text=t("btn_guide"), command=self._show_help,
                                      width=90, height=32, corner_radius=8,
                                      fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                      text_color=COLORS["text"])
        self.btn_help.pack(side="left")

        # Ligne 2 : Bug, Docs GDAL, Système
        row_links2 = ctk.CTkFrame(self.card_about, fg_color="transparent")
        row_links2.pack(fill="x", padx=20, pady=(0, 15))

        self.btn_bug = ctk.CTkButton(row_links2, text=t("btn_bug"), command=self._open_bug_report,
                                     width=130, height=32, corner_radius=8,
                                     fg_color=COLORS["surface2"], hover_color="#EF4444",
                                     text_color=COLORS["text"])
        self.btn_bug.pack(side="left", padx=(0, 10))

        self.btn_gdal_docs = ctk.CTkButton(row_links2, text=t("btn_gdal_docs"), command=self._open_gdal_docs,
                                           width=110, height=32, corner_radius=8,
                                           fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                           text_color=COLORS["text"])
        self.btn_gdal_docs.pack(side="left", padx=(0, 10))

        self.btn_sysinfo = ctk.CTkButton(row_links2, text=t("btn_sysinfo"), command=self._show_sysinfo,
                                         width=100, height=32, corner_radius=8,
                                         fg_color=COLORS["surface2"], hover_color=COLORS["accent"],
                                         text_color=COLORS["text"])
        self.btn_sysinfo.pack(side="left")

        # --- CARTE 4 : DÉCOUPAGE (Droite Haut) ---
        card_clip = ctk.CTkFrame(right_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        card_clip.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_clip, text=t("card_clip"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(15, 10))

        self.chk_clip = ctk.CTkCheckBox(card_clip, text=t("chk_clip"), variable=self.clip_var,
                                        text_color=COLORS["accent"], checkbox_height=18, checkbox_width=18,
                                        fg_color=COLORS["accent2"], command=self._toggle_clip_ui)
        self.chk_clip.pack(anchor="w", padx=20, pady=(0, 5))

        grid_clip = ctk.CTkFrame(card_clip, fg_color="transparent")
        grid_clip.pack(fill="x", padx=20, pady=5)

        def add_clip_entry(label, var, r, c):
            ctk.CTkLabel(grid_clip, text=label, text_color=COLORS["text_dim"], font=ctk.CTkFont(size=11)).grid(row=r, column=c*2, padx=(0, 5), pady=2, sticky="e")
            e = ctk.CTkEntry(grid_clip, textvariable=var, width=120, height=28, corner_radius=6, border_color=COLORS["border"], fg_color=COLORS["surface2"])
            e.grid(row=r, column=c*2+1, padx=(0, 10), pady=2, sticky="w")
            return e

        self.entries_clip = [
            add_clip_entry("X Min :", self.ulx_var, 0, 0),
            add_clip_entry("Y Max :", self.uly_var, 0, 1),
            add_clip_entry("X Max :", self.lrx_var, 1, 0),
            add_clip_entry("Y Min :", self.lry_var, 1, 1)
        ]

        row_btn_clip = ctk.CTkFrame(card_clip, fg_color="transparent")
        row_btn_clip.pack(fill="x", padx=20, pady=(10, 15))

        self.btn_get_extent = ctk.CTkButton(row_btn_clip, text=t("btn_autoextent"), command=self._on_get_extent,
                                            width=120, height=32, corner_radius=8, text_color=COLORS["text"],
                                            fg_color=COLORS["surface2"], hover_color=COLORS["accent"])
        self.btn_get_extent.pack(side="left", padx=(0, 10))

        self.btn_visual = ctk.CTkButton(row_btn_clip, text=t("btn_visual"), command=self._on_visual_select,
                                         width=150, height=32, corner_radius=8,
                                         fg_color=COLORS["surface2"], hover_color=COLORS["accent"], text_color=COLORS["text"])
        self.btn_visual.pack(side="left")
        
        self.entries_clip.extend([self.btn_get_extent, self.btn_visual])
        self.clip_frame = card_clip # Compatibilité
        self._toggle_clip_ui()

        # --- CARTE 5 : EXÉCUTION & LOGS (Droite Bas) ---
        card_exec = ctk.CTkFrame(right_col, corner_radius=16, border_width=1, border_color=COLORS["border"], fg_color=COLORS["surface"])
        card_exec.pack(fill="both", expand=True)

        ctk.CTkLabel(card_exec, text=t("card_exec"), font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["accent"]).pack(anchor="w", padx=20, pady=(15, 10))

        row_actions = ctk.CTkFrame(card_exec, fg_color="transparent")
        row_actions.pack(fill="x", padx=20, pady=(0, 10))

        self.btn_convert = ctk.CTkButton(row_actions, text=t("btn_convert"), command=self._start_conversion,
                                        width=200, height=45, corner_radius=10,
                                        fg_color=COLORS["accent"], hover_color="#4F46E5",
                                        text_color="white", font=ctk.CTkFont(size=14, weight="bold"))
        self.btn_convert.pack(side="left", padx=(0, 15))

        self.btn_stop = ctk.CTkButton(row_actions, text=t("btn_stop"), command=self._on_stop,
                                     width=120, height=45, corner_radius=10,
                                     fg_color="#CC0000", hover_color="#990000",
                                     text_color="white", font=ctk.CTkFont(size=14, weight="bold"),
                                     state="disabled")
        self.btn_stop.pack(side="left")

        self.progress_bar = ctk.CTkProgressBar(card_exec, height=10, corner_radius=5,
                                               progress_color=COLORS["accent"], fg_color=COLORS["bg"])
        self.progress_bar.pack(fill="x", padx=20, pady=(10, 5))
        self.progress_bar.set(0)

        self.lbl_progress = ctk.CTkLabel(card_exec, text=t("status_ready"), text_color=COLORS["text_dim"], font=ctk.CTkFont(size=11))
        self.lbl_progress.pack(anchor="w", padx=22)

        self.log_text = ctk.CTkTextbox(card_exec, fg_color=COLORS["bg"], corner_radius=12,
                                       border_width=1, border_color=COLORS["border"],
                                       font=ctk.CTkFont(family="Courier", size=12),
                                       text_color=COLORS["text"])
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        # Placeholder label to satisfy existing references
        self.lbl_fmt_desc = ctk.CTkLabel(self.root, text="")

        # ───────────────────────────────────────────────────────────────────────
        # Registre des widgets pour mise à jour thème/langue sans reconstruction.
        # Chaque entrée : {"widget": w, "theme": {prop: color_key}, "lang": "t_key"}
        # ───────────────────────────────────────────────────────────────────────
        self._ui_registry = [
            # ── Cartes (frames) ──
            {"widget": card_src,        "theme": {"fg_color": "surface", "border_color": "border"}},
            {"widget": card_out,        "theme": {"fg_color": "surface", "border_color": "border"}},
            {"widget": card_proc,       "theme": {"fg_color": "surface", "border_color": "border"}},
            {"widget": self.card_about, "theme": {"fg_color": "surface", "border_color": "border"}},
            {"widget": card_clip,       "theme": {"fg_color": "surface", "border_color": "border"}},
            {"widget": card_exec,       "theme": {"fg_color": "surface", "border_color": "border"}},
            # ── Boutons Header ──
            {"widget": self.btn_lang,    "theme": {"fg_color": "surface2", "hover_color": "accent"}},
            # ── Bouton sélection fichiers ──
            {"widget": self.btn_select,  "theme": {"fg_color": "accent"}, "lang": "_select_mode"},
            # ── Boutons Source ──
            {"widget": self.radio_single, "theme": {"text_color": "text"}, "lang": "radio_single"},
            {"widget": self.radio_batch,  "theme": {"text_color": "text"}, "lang": "radio_batch"},
            {"widget": self.lbl_files,    "theme": {"text_color": "text_dim"}, "lang": "_lbl_files"},
            # ── Boutons Destination ──
            {"widget": self.epsg_combo,  "theme": {"fg_color": "surface2", "border_color": "border",
                                                   "button_color": "surface2", "dropdown_fg_color": "surface2",
                                                   "text_color": "text"}},
            {"widget": self.ent_out,     "theme": {"border_color": "border"}},
            # ── Boutons Traitement ──
            # comp_menu est un ttk.Combobox natif — mis à jour via _apply_theme directement

            {"widget": self.bit_seg,     "theme": {"selected_color": "accent", "unselected_color": "surface2",
                                                   "text_color": "text"}},
            {"widget": self.res_seg,     "theme": {"selected_color": "accent", "unselected_color": "surface2",
                                                   "text_color": "text"}},
            # ── Checkboxes ──
            {"widget": self.chk_mosaic,  "theme": {"text_color": "accent"}, "lang": "chk_mosaic"},
            {"widget": self.chk_mt,      "theme": {"text_color": "text"},   "lang": "chk_multicore"},
            {"widget": self.chk_tiled,   "theme": {"text_color": "text", "fg_color": "accent"},   "lang": "chk_tiling"},
            {"widget": self.chk_ovr,     "theme": {"text_color": "text", "fg_color": "accent"},   "lang": "chk_pyramids"},
            {"widget": self.chk_nodata,  "theme": {"text_color": "text", "fg_color": "accent"},   "lang": "chk_nodata"},
            # ── Checkbox Clip ──
            {"widget": self.chk_clip,    "theme": {"text_color": "accent"}, "lang": "chk_clip"},
            # ── Boutons Outils ──
            {"widget": self.btn_inspect,  "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_inspect"},
            {"widget": self.btn_estimate, "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_estimate"},
            {"widget": self.btn_shapefile,"theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_shapefile"},
            # ── Boutons AOI ──
            {"widget": self.btn_get_extent, "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_autoextent"},
            {"widget": self.btn_visual,     "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_visual"},
            # ── Carte À-propos (titre + description) ──
            {"widget": self.lbl_card_about, "theme": {"text_color": "accent"}, "lang": "card_about"},
            {"widget": self.lbl_about_desc, "theme": {"text_color": "text_dim"}, "lang": "about_desc"},
            # ── Boutons À-propos ──
            {"widget": self.btn_license, "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_license"},
            {"widget": self.btn_github,  "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_github"},
            {"widget": self.btn_help,    "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_guide"},
            {"widget": self.btn_bug,     "theme": {"fg_color": "surface2", "text_color": "text"},
             "lang": "btn_bug"},
            {"widget": self.btn_gdal_docs, "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_gdal_docs"},
            {"widget": self.btn_sysinfo, "theme": {"fg_color": "surface2", "hover_color": "accent", "text_color": "text"},
             "lang": "btn_sysinfo"},
            # ── Boutons Conversion ──
            {"widget": self.btn_convert, "theme": {"fg_color": "accent"}, "lang": "btn_convert"},
            {"widget": self.btn_stop,    "theme": {"fg_color": "#CC0000"}, "lang": "btn_stop"},
            # ── Zone de log ──
            {"widget": self.log_text,    "theme": {"fg_color": "bg", "border_color": "border",
                                                   "text_color": "text"}},
            # ── Barre de progression ──
            {"widget": self.progress_bar, "theme": {"progress_color": "accent", "fg_color": "bg"}},
            {"widget": self.lbl_progress, "theme": {"text_color": "text_dim"}},
        ]

        self._on_format_change(self.format_var.get())
        self._update_mosaic_state()


    def _build_tk_ui(self):
        """Interface de repli avec Tkinter standard (si customtkinter absent)."""
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=COLORS["bg"], foreground=COLORS["text"])
        style.configure("TButton", background=COLORS["accent2"], foreground="white")
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("TCombobox", background=COLORS["surface"])

        self.root.configure(bg=COLORS["bg"])

        # En-tête
        header = tk.Frame(self.root, bg=COLORS["surface"], pady=10)
        header.pack(fill="x")
        tk.Label(header, text="🗺  GeoConvert — GDAL",
                 bg=COLORS["surface"], fg=COLORS["accent"],
                 font=("Helvetica", 20, "bold")).pack(side="left", padx=20)

        body = tk.Frame(self.root, bg=COLORS["bg"], padx=15, pady=10)
        body.pack(fill="both", expand=True)

        # ── Sélection Source ──
        src_frame = tk.LabelFrame(body, text="📂 Fichier(s) source", bg=COLORS["bg"], fg=COLORS["accent"],
                                  font=("Helvetica", 11, "bold"), padx=10, pady=10)
        src_frame.pack(fill="x", pady=(0, 10))
        
        self.btn_select = tk.Button(src_frame, text="Choisir", command=self._select_files,
                  bg=COLORS["accent2"], fg="white")
        self.btn_select.pack(side="left", padx=(0, 10))
        self.lbl_files = tk.Label(src_frame, text="Aucun fichier", bg=COLORS["bg"], fg=COLORS["text_dim"])
        self.lbl_files.pack(side="left", fill="x", expand=True)

        # ── Destination ──
        out_frame = tk.LabelFrame(body, text="💾 Dossier de sortie", bg=COLORS["bg"], fg=COLORS["accent"],
                                  font=("Helvetica", 11, "bold"), padx=10, pady=10)
        out_frame.pack(fill="x", pady=(0, 10))
        
        tk.Button(out_frame, text="Parcourir", command=self._browse_output,
                  bg=COLORS["surface2"], fg="white").pack(side="left", padx=(0, 10))
        tk.Entry(out_frame, textvariable=self.output_dir, bg=COLORS["surface"],
                 fg=COLORS["text"]).pack(side="left", fill="x", expand=True)

        # ── Paramètres de Conversion ──
        opts_frame = tk.LabelFrame(body, text="⚙️ Paramètres de conversion", bg=COLORS["bg"], fg=COLORS["accent"],
                                   font=("Helvetica", 11, "bold"), padx=10, pady=10)
        opts_frame.pack(fill="x", pady=(0, 10))
        
        # Sous-ligne 1: Format & EPSG
        row1 = tk.Frame(opts_frame, bg=COLORS["bg"])
        row1.pack(fill="x", pady=(0, 5))
        tk.Label(row1, text="Format :", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        from converter.formats import SUPPORTED_FORMATS
        self.fmt_combo = ttk.Combobox(row1, textvariable=self.format_var,
                                      values=list(SUPPORTED_FORMATS.keys()), state="readonly", width=15)
        self.fmt_combo.pack(side="left", padx=(5, 15))

        tk.Label(row1, text="EPSG :", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        ttk.Combobox(row1, textvariable=self.epsg_var, values=self.epsg_common, 
                     width=30).pack(side="left", padx=5)
        tk.Button(row1, text="🔍", command=self._open_epsg_bank, bg=COLORS["surface2"], fg="white").pack(side="left")

        # Sous-ligne 2: Avancé
        row2 = tk.Frame(opts_frame, bg=COLORS["bg"])
        row2.pack(fill="x", pady=(5, 0))
        tk.Label(row2, text="Compression :", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        self.comp_menu = ttk.Combobox(row2, textvariable=self.compress_var, 
                                      values=[t("comp_none"), t("comp_lzw"), t("comp_deflate"), t("comp_jpeg")], 
                                      state="readonly", width=18)
        self.comp_menu.pack(side="left", padx=(5, 15))
                     
        self.chk_tiled = tk.Checkbutton(row2, text="Tuilage", variable=self.tiled_var, 
                                        bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["surface"])
        self.chk_tiled.pack(side="left", padx=5)
        
        self.chk_ovr = tk.Checkbutton(row2, text="Pyramides", variable=self.overviews_var, 
                                      bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["surface"])
        self.chk_ovr.pack(side="left", padx=5)

        self.chk_nodata = tk.Checkbutton(row2, text="NoData=0", variable=self.nodata_var, 
                                         bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["surface"])
        self.chk_nodata.pack(side="left", padx=5)

        self.chk_mosaic = tk.Checkbutton(row2, text="Mosaïque", variable=self.mosaic_var, 
                                         bg=COLORS["bg"], fg=COLORS["accent2"], selectcolor=COLORS["surface"])
        self.chk_mosaic.pack(side="left", padx=5)

        self.chk_mt = tk.Checkbutton(row2, text="Multi-cœurs", variable=self.multithread_var, 
                                      bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["surface"])
        self.chk_mt.pack(side="left", padx=5)

        # Sous-ligne 4: Qualité & Ré-éch (TK)
        row4 = tk.Frame(opts_frame, bg=COLORS["bg"])
        row4.pack(fill="x", pady=5)
        tk.Label(row4, text="Qualité (1-100) :", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left", padx=5)
        tk.Entry(row4, textvariable=self.quality_var, width=5).pack(side="left", padx=(0, 15))
        
        tk.Label(row4, text="Lissage :", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left", padx=5)
        from tkinter import ttk
        ttk.Combobox(row4, textvariable=self.resampling_var, values=["Plus proche (Vitesse)", "Bilinéaire", "Cubique", "Lanczos (Qualité)"], state="readonly").pack(side="left")

        # Sous-ligne 5 : Découpage (TK)
        row5 = tk.Frame(opts_frame, bg=COLORS["bg"])
        row5.pack(fill="x", pady=5)
        tk.Checkbutton(row5, text="Découper (Décimal)", variable=self.clip_var, bg=COLORS["bg"], fg=COLORS["text"], selectcolor=COLORS["surface"]).pack(side="left", padx=5)
        tk.Label(row5, text="Xmin:", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        tk.Entry(row5, textvariable=self.ulx_var, width=8).pack(side="left", padx=2)
        tk.Label(row5, text="Ymax:", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        tk.Entry(row5, textvariable=self.uly_var, width=8).pack(side="left", padx=2)
        tk.Label(row5, text="Xmax:", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        tk.Entry(row5, textvariable=self.lrx_var, width=8).pack(side="left", padx=2)
        tk.Label(row5, text="Ymin:", bg=COLORS["bg"], fg=COLORS["text"]).pack(side="left")
        tk.Entry(row5, textvariable=self.lry_var, width=8).pack(side="left", padx=2)
        tk.Button(row5, text="Emprise", command=self._on_get_extent, bg=COLORS["surface"], fg=COLORS["accent"]).pack(side="left", padx=5)
        tk.Button(row5, text="Sélection", command=self._on_visual_select, bg=COLORS["surface"], fg=COLORS["success"]).pack(side="left", padx=5)

        # Sous-ligne 3: Profondeur (TK)
        row3 = tk.Frame(opts_frame, bg=COLORS["bg"])
        row3.pack(fill="x", pady=(5, 0))
        tk.Label(row3, text="Profondeur :", bg=COLORS["bg"], fg=COLORS["accent"], font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 5))
        self.bit_combo = ttk.Combobox(row3, textvariable=self.bit_depth_var, 
                                      values=["Original", "8-bit (Visualisation)", "16-bit (Données)"], 
                                      state="readonly", width=25)
        self.bit_combo.pack(side="left", padx=5)

        # ── Panneau Exécution ──
        run_frame = tk.Frame(body, bg=COLORS["bg"])
        run_frame.pack(fill="x", pady=10)

        self.btn_convert = tk.Button(run_frame, text="🚀 Convertir", command=self._start_conversion,
                                     bg=COLORS["accent"], fg=COLORS["bg"],
                                     font=("Helvetica", 13, "bold"), pady=8, padx=20)
        self.btn_convert.pack(side="left", expand=True, padx=5)

        self.btn_stop = tk.Button(run_frame, text="🛑 Arrêter", command=self._on_stop,
                                  bg=COLORS["surface"], fg=COLORS["warning"],
                                  font=("Helvetica", 13, "bold"), pady=8, padx=20,
                                  state="disabled")
        self.btn_stop.pack(side="left", expand=True, padx=5)

        # Progress
        self.progress_bar = ttk.Progressbar(body, mode="determinate", length=600)
        self.progress_bar.pack(fill="x", pady=5)

        self.lbl_progress = tk.Label(body, text="", bg=COLORS["bg"], fg=COLORS["text_dim"])
        self.lbl_progress.pack(anchor="w")

        # Log
        tk.Label(body, text="📋 Journal :", bg=COLORS["bg"], fg=COLORS["accent"],
                 font=("Helvetica", 11, "bold")).pack(anchor="w", pady=(10, 2))
        self.log_text = tk.Text(body, height=15, bg=COLORS["surface"], fg=COLORS["text"],
                                font=("Courier", 11))
        self.log_text.pack(fill="both", expand=True)
        self._update_mosaic_state()

    # ── Interactions ──────────────────────────────────────────────────────────

    def _update_mode(self):
        if self.mode_var.get() == "batch":
            self.btn_select.configure(text=t("btn_choose_folder"))
        else:
            self.btn_select.configure(text=t("btn_choose_files"))
        self._update_mosaic_state()

    # ── Thème ─────────────────────────────────────────────────────────────────

    def _toggle_lang(self):
        """Bascule la langue et met à jour les textes sans reconstruire l'UI."""
        _toggle_language()
        if CTK:
            self._apply_lang()
        else:
            # Fallback léger pour tk pur (non-CTK, cas rare)
            for child in self.root.winfo_children():
                child.destroy()
            self._build_ui()

    def _toggle_theme(self):
        """Bascule entre mode sombre et mode clair sans reconstruire l'UI.

        Met à jour uniquement les couleurs de chaque widget enregistré
        dans self._ui_registry. Le contenu du journal et toutes les variables
        sont conservés tels quels.
        """
        global _current_theme, COLORS

        # ── 1. Basculer le thème global ─────────────────────────────────────
        _current_theme = "light" if _current_theme == "dark" else "dark"
        COLORS = get_colors()
        _prefs["theme"] = _current_theme
        _save_prefs(_prefs)

        if CTK:
            ctk.set_appearance_mode("light" if _current_theme == "light" else "dark")
            # ── 2. Mettre à jour les couleurs de tous les widgets enregistrés
            self._apply_theme()
        else:
            # Fallback léger pour tk pur
            for child in self.root.winfo_children():
                child.destroy()
            self._build_ui()



    # ── Mise à jour thème / langue sans reconstruction ────────────────────────

    def _apply_theme(self):
        """Met à jour les couleurs de tous les widgets CTk enregistrés."""
        global COLORS
        c = get_colors()
        COLORS = c  # Synchronise l'alias global pour les classes popup non-registrées

        # Fenêtre principale
        self.root.configure(fg_color=c["bg"])

        # Icone du bouton thème
        if hasattr(self, "btn_theme"):
            self.btn_theme.configure(
                text="🌙" if _current_theme == "light" else "☀️",
                fg_color=c["surface2"], hover_color=c["accent"]
            )

        # Parcourir le registre et appliquer chaque règle
        for entry in getattr(self, "_ui_registry", []):
            widget = entry.get("widget")
            if widget is None:
                continue
            try:
                props = {}
                for prop, color_key in entry.get("theme", {}).items():
                    if color_key is not None:
                        props[prop] = c[color_key]
                if props:
                    # tk natifs (Frame, Label) utilisent configure() standard
                    widget.configure(**props)
            except Exception:
                pass
        # Mettre à jour les widgets tk/ttk natifs (non-CTK)
        try:
            if hasattr(self, "_lbl_depth"):
                self._lbl_depth.configure(bg=c["surface"], fg=c["text"])
            if hasattr(self, "_row_depth_frame"):
                self._row_depth_frame.configure(bg=c["surface"])
            if hasattr(self, "comp_menu"):
                self.comp_menu.configure(
                    bg=c["surface"],
                    fg_color=c["surface2"],
                    button_color=c["surface2"],
                    text_color=c["text"],
                )
        except Exception:
            pass

    def _apply_lang(self):
        """Met à jour les textes de tous les widgets CTk enregistrés."""
        # Icône de la langue
        if hasattr(self, "btn_lang"):
            self.btn_lang.configure(text="🇬🇧" if _current_lang == "fr" else "🇫🇷")

        # Segments dont les valeurs doivent changer avec la langue
        if hasattr(self, "bit_seg"):
            current_val = self.bit_depth_var.get()
            self.bit_seg.configure(values=[t("seg_original"), t("seg_8bit"), t("seg_16bit")])
            # Conserver la valeur sélectionnée
            if "8" in current_val:
                self.bit_depth_var.set(t("seg_8bit"))
            elif "16" in current_val:
                self.bit_depth_var.set(t("seg_16bit"))
            else:
                self.bit_depth_var.set(t("seg_original"))

        if hasattr(self, "res_seg"):
            current_res = self.resampling_var.get()
            self.res_seg.configure(values=[t("seg_speed"), t("seg_normal"), t("seg_quality")])
            if any(k in current_res.lower() for k in ["speed", "vitesse", "proche"]):
                self.resampling_var.set(t("seg_speed"))
            elif any(k in current_res.lower() for k in ["qualit", "cubic"]):
                self.resampling_var.set(t("seg_quality"))
            else:
                self.resampling_var.set(t("seg_normal"))

        # Mettre à jour le label Profondeur (tk.Label natif)
        if hasattr(self, "_lbl_depth"):
            try:
                self._lbl_depth.configure(text=t("label_depth"))
            except Exception:
                pass

        # Mettre à jour les valeurs du comp_menu (FlatDropdown) selon le format actif
        if hasattr(self, "comp_menu") and hasattr(self, "format_var"):
            try:
                fmt = self.format_var.get()
                if fmt in ["GeoTIFF", "COG"]:
                    self.comp_menu.set_values([t("comp_none"), t("comp_lzw"), t("comp_deflate"), t("comp_jpeg")])
                elif fmt == "PNG":
                    self.comp_menu.set_values([t("comp_png9"), t("comp_png6"), t("comp_png1")])
                else:
                    self.comp_menu.set_values([t("comp_auto")])
                # Retranscrire la valeur courante dans la nouvelle langue
                self.root.after(0, lambda: self._on_format_change(self.format_var.get()))
            except Exception:
                pass

        # Parcourir le registre et appliquer le texte traduit
        for entry in getattr(self, "_ui_registry", []):
            widget = entry.get("widget")
            lang_key = entry.get("lang")
            if widget is None or not lang_key:
                continue
            try:
                # Cas spécial : le mode_var détermine le texte du bouton de sélection
                if lang_key == "_select_mode":
                    text = t("btn_choose_folder") if self.mode_var.get() == "batch" else t("btn_choose_files")
                elif lang_key == "_lbl_files":
                    # Traduire seulement si aucun fichier n'est sélectionné
                    if not self.source_files:
                        widget.configure(text=t("no_file"))
                    continue
                elif lang_key == "btn_stop":
                    # Ne mettre à jour que si pas en cours d'arrêt (pas en état btn_stop_ing)
                    if not self.is_cancelled:
                        widget.configure(text=t("btn_stop"))
                    continue
                else:
                    text = t(lang_key)
                widget.configure(text=text)
            except Exception:
                pass

    def _select_files(self):

        if self.mode_var.get() == "batch":
            folder = filedialog.askdirectory(title=t("btn_choose_folder"))
            if folder:
                self.source_files = [Path(folder)]
                self._set_lbl_files(f"📁 {folder}")
        else:
            files = filedialog.askopenfilenames(
                title="Choose source file(s)",
                filetypes=[
                    ("All supported rasters" if _current_lang == "en" else "Tous les rasters supportés", "*.jp2 *.j2k *.j2c *.jpx *.tif *.tiff *.ecw *.img *.nc *.png *.jpg *.jpeg *.ntf *.nitf *.hdf *.h5 *.vrt *.dem *.asc"),
                    ("JPEG2000", "*.jp2 *.j2k *.j2c *.jpx"),
                    ("GeoTIFF", "*.tif *.tiff"),
                    ("ECW", "*.ecw"),
                    ("PNG / JPEG", "*.png *.jpg *.jpeg"),
                    ("All files" if _current_lang == "en" else "Tous les fichiers", "*.*"),
                ],
            )
            if files:
                self.source_files = [Path(f) for f in files]
                label = f"{len(files)} file(s) : {', '.join(Path(f).name for f in files[:3])}"
                if len(files) > 3:
                    label += f"… (+{len(files) - 3})"
                self._set_lbl_files(label)
            
        self._refresh_file_count_async()

    def _set_lbl_files(self, text: str):
        if CTK:
            self.lbl_files.configure(text=text, text_color=COLORS["text"])
        else:
            self.lbl_files.configure(text=text, fg=COLORS["text"])

    def _browse_output(self):
        folder = filedialog.askdirectory(title="Choose output folder")
        if folder:
            self.output_dir.set(folder)

    def _update_mosaic_state(self):
        """Met à jour les widgets mosaïque/clip depuis le cache — ne touche jamais au disque.
        
        Appelée par : mosaic_var.trace, _update_mode(), et _apply_mosaic_state().
        Pour déclencher un rescan disque, utiliser _refresh_file_count_async().
        """
        self._apply_mosaic_state(self._cached_file_count)

    def _apply_mosaic_state(self, total_count: int):
        """Configure les widgets mosaïque et clip selon le nombre de fichiers.
        
        Thread-safe : peut être appelée depuis root.after() depuis n'importe quel thread.
        """
        self._cached_file_count = total_count
        can_mosaic = total_count > 1
        state = "normal" if can_mosaic else "disabled"

        if not can_mosaic:
            self.mosaic_var.set(False)

        if CTK:
            self.chk_mosaic.configure(state=state)
            self.chk_mosaic.configure(
                text_color=COLORS["accent"] if can_mosaic else COLORS["text_dim"]
            )
        else:
            self.chk_mosaic.configure(state=state)

        # Clipping autorisé : 1 seul fichier OU plusieurs fichiers en mode mosaïque
        can_clip = total_count == 1 or self.mosaic_var.get()
        clip_state = "normal" if can_clip else "disabled"
        if not can_clip:
            self.clip_var.set(False)

        if CTK:
            self.chk_clip.configure(state=clip_state)
            self.chk_clip.configure(
                text_color=COLORS["accent"] if can_clip else COLORS["text_dim"]
            )
        else:
            self.chk_clip.configure(state=clip_state)

    def _refresh_file_count_async(self):
        """Scanne le disque en thread puis applique l'état mosaïque/clip.
        
        Appelée uniquement après une sélection de fichiers (scan potentiellement long).
        L'UI n'est jamais bloquée : _apply_mosaic_state est planifiée via root.after().
        """
        snapshot = list(self.source_files)  # Copie thread-safe de la liste courante

        def _scan():
            total = 0
            from converter.utils import collect_input_files
            for p in snapshot:
                if p.is_dir():
                    try:
                        total += len(collect_input_files(str(p)))
                    except Exception:
                        pass
                else:
                    total += 1
            # Planifier la mise à jour UI depuis le thread principal
            self.root.after(0, self._apply_mosaic_state, total)

        threading.Thread(target=_scan, daemon=True).start()

    def _toggle_clip_ui(self):
        """Enables/disables coordinate entry fields based on the checkbox."""
        state = "normal" if self.clip_var.get() else "disabled"
        if CTK:
            for e in self.entries_clip:
                e.configure(state=state)
        # For standard TK, we don't manage the state here to simplify compared to the priority user need CTK

    def _on_get_extent(self):
        """Retrieves the extent of the first selected file."""
        if not self.source_files:
            messagebox.showwarning(t("dlg_warn_title"), t("dlg_no_file_extent"))
            return
            
        src = self.source_files[0]
        try:
            from converter.core import ImageConverter
            conv = ImageConverter()
            extent = conv.get_extent(src)
        except Exception as e:
            self._log(f"⚠️ Error : {e}", COLORS["error"])
            return
        
        if extent:
            self.ulx_var.set(str(extent["ulx"]))
            self.uly_var.set(str(extent["uly"]))
            self.lrx_var.set(str(extent["lrx"]))
            self.lry_var.set(str(extent["lry"]))
            self._log(t("log_extent_ok") + os.path.basename(str(src)))
        else:
            self._log(t("log_extent_fail") + os.path.basename(str(src)), COLORS["warning"])

    def _on_stop(self):
        """Stop button action."""
        if not self.is_cancelled:
            self.is_cancelled = True
            self._log(t("log_stop_sent"), COLORS["warning"])
            if CTK:
                self.btn_stop.configure(state="disabled", text=t("btn_stop_ing"))
            else:
                self.btn_stop.configure(state="disabled", text=t("btn_stop_ing"))

    def _on_visual_select(self):
        """Opens the visual selector (individual thumbnail or global for mosaic)."""
        if not HAS_PIL:
            messagebox.showerror("PIL Missing", "The Pillow library is required for the visual selector.\nInstall it with: pip install Pillow")
            return
            
        if not self.source_files:
            messagebox.showwarning(t("dlg_warn_title"), t("dlg_no_file_visual"))
            return

        from converter.utils import collect_input_files
        all_files = []
        for p in self.source_files:
            if p.is_dir():
                all_files.extend(collect_input_files(str(p)))
            else:
                all_files.append(p)

        if not all_files:
            messagebox.showerror(t("dlg_error_title"), t("dlg_no_valid_files"))
            return

        mosaic_mode = self.mosaic_var.get() and len(all_files) > 1
        
        if mosaic_mode:
            self._log(t("log_mosaic_thumb") + str(len(all_files)) + t("log_mosaic_thumb2"))
        else:
            self._log(t("log_thumb_gen") + os.path.basename(str(all_files[0])))
        
        def task():
            try:
                from converter.core import ImageConverter
                conv = ImageConverter()
                
                if mosaic_mode:
                    thumb_data = conv.get_mosaic_thumbnail(all_files)
                else:
                    thumb_data = conv.get_thumbnail(all_files[0])
                
                if thumb_data:
                    thumb_path, extent = thumb_data
                    self.root.after(0, lambda: VisualSelector(self.root, thumb_path, extent, self._apply_visual_clip))
                else:
                    self.root.after(0, lambda: messagebox.showerror(t("dlg_error_title"), t("dlg_thumb_error")))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror(t("dlg_error_title"), str(e)))

        threading.Thread(target=task, daemon=True).start()

    def _apply_visual_clip(self, xmin, ymax, xmax, ymin):
        """Applies the coordinates chosen in the selector."""
        self.ulx_var.set(str(round(xmin, 6)))
        self.uly_var.set(str(round(ymax, 6)))
        self.lrx_var.set(str(round(xmax, 6)))
        self.lry_var.set(str(round(ymin, 6)))
        self._log(t("log_clip_updated"))

    def _on_format_change(self, value):
        """Met à jour les contrôles selon le format choisi.
        
        Tous les configure() sont groupés puis appliqués en une seule passe
        via after(0) pour éviter les redraws successifs (clignotement).
        """
        def _apply():
            # 1. Description du format
            try:
                from converter.formats import SUPPORTED_FORMATS
                desc = SUPPORTED_FORMATS[value]["description"]
                if CTK:
                    self.lbl_fmt_desc.configure(text=desc)
            except Exception:
                pass

            # 2. Compression + état des checkboxes selon le format
            if value in ["GeoTIFF", "COG"]:
                self._update_comp_menu(
                    [t("comp_none"), t("comp_lzw"), t("comp_deflate"), t("comp_jpeg")],
                    t("comp_deflate"), normal_state=True)
                self._set_widget_state(self.chk_tiled,  "normal")
                self._set_widget_state(self.chk_ovr,    "normal")
                self._set_widget_state(self.chk_nodata, "normal")

            elif value == "PNG":
                self._update_comp_menu(
                    [t("comp_png9"), t("comp_png6"), t("comp_png1")],
                    t("comp_png6"), normal_state=True)
                self._set_widget_state(self.chk_tiled,  "disabled")
                self._set_widget_state(self.chk_ovr,    "disabled")
                self._set_widget_state(self.chk_nodata, "disabled")

            elif value in ["WebP", "JPEG", "JPEG2000", "PDF"]:
                self._update_comp_menu(
                    [t("comp_auto")],
                    t("comp_auto"), normal_state=False)
                self._set_widget_state(self.chk_tiled,  "disabled")
                self._set_widget_state(self.chk_ovr,    "disabled")
                self._set_widget_state(self.chk_nodata, "disabled")

            else:
                self._update_comp_menu(
                    [t("comp_default")],
                    t("comp_default"), normal_state=False)
                self._set_widget_state(self.chk_tiled,  "disabled")
                self._set_widget_state(self.chk_ovr,    "disabled")
                self._set_widget_state(self.chk_nodata, "disabled")

            # 3. Profondeur de bits : bloquer sans aucun clignotement
            bit_active = value in ["GeoTIFF", "COG", "PNG", "JPEG", "WebP", "PDF", "JPEG2000"]
            if CTK:
                # Ne reconfigurer que si l'état a vraiment changé
                if bit_active != self._bit_seg_active:
                    self._bit_seg_active = bit_active
                    dim = COLORS["text"] if bit_active else COLORS["text_dim"]
                    if hasattr(self.bit_seg, "_buttons_dict"):
                        for btn in self.bit_seg._buttons_dict.values():
                            # Bloquer/débloquer la command (sans redraw)
                            if bit_active:
                                if hasattr(btn, "_seg_original_command"):
                                    btn._command = btn._seg_original_command
                            else:
                                if not hasattr(btn, "_seg_original_command"):
                                    btn._seg_original_command = btn._command
                                btn._command = None
                            # Griser le label texte directement (sans passer par configure → pas de _draw())
                            if btn._text_label is not None:
                                btn._text_label.configure(fg=dim)
            else:
                self._set_widget_state(self.bit_combo, "normal" if bit_active else "disabled")

        # Planifier tous les configure() en une seule passe de rendu
        self.root.after(0, _apply)

    def _inspect_metadata(self):
        """Opens a pop-up window with metadata (1 file) or a summary (N files).
        
        Les lectures GDAL sont faites dans un thread séparé pour ne pas bloquer l'UI.
        Un spinner est affiché pendant le chargement.
        """
        if not self.source_files:
            self._log("⚠ Please select a source file first.", "error")
            return

        from converter.utils import collect_input_files
        all_files = []
        for p in self.source_files:
            if p.is_dir():
                all_files.extend(collect_input_files(str(p)))
            else:
                all_files.append(p)

        if not all_files:
            self._log("⚠ No valid image file found.", "error")
            return

        # ── Créer la fenêtre immédiatement avec un spinner ──
        top = ctk.CTkToplevel(self.root)
        top.configure(fg_color=C("bg"))
        top.geometry("600x650" if len(all_files) == 1 else "600x600")
        top.after(100, lambda: top.focus_force())

        spinner = ctk.CTkLabel(top, text=t("inspect_loading"),
                               font=ctk.CTkFont(size=14), text_color=C("text_dim"))
        spinner.pack(expand=True)

        def _load_and_render():
            """Exécuté dans un thread : lit les métadonnées GDAL puis schedule l'affichage UI."""
            try:
                from converter.core import ImageConverter
                from converter.utils import get_human_size
                conv = ImageConverter()

                if len(all_files) == 1:
                    src = all_files[0]
                    info = conv.get_info(src)  # ← lecture GDAL (potentiellement lente)
                    self.root.after(0, lambda: _render_single(src, info, get_human_size))
                else:
                    # Lire les infos de tous les fichiers
                    total_size = 0
                    projections = set()
                    min_x, max_x = float('inf'), float('-inf')
                    min_y, max_y = float('inf'), float('-inf')
                    for src in all_files:
                        total_size += src.stat().st_size
                        try:
                            info = conv.get_info(src)  # ← lecture GDAL
                            p_name = info["projection"].split('[')[-1].split('"')[1] if '"' in info["projection"] else "Unknown"
                            projections.add(p_name)
                            min_x = min(min_x, info["bbox"]["xmin"])
                            max_x = max(max_x, info["bbox"]["xmax"])
                            min_y = min(min_y, info["bbox"]["ymin"])
                            max_y = max(max_y, info["bbox"]["ymax"])
                        except: pass
                    self.root.after(0, lambda: _render_group(
                        all_files, total_size, projections, min_x, max_x, min_y, max_y, get_human_size
                    ))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"✗ Inspection error : {e}", "error"))
                self.root.after(0, top.destroy)

        def _build_scroll():
            """Supprime le spinner et retourne un CTkScrollableFrame prêt."""
            spinner.destroy()
            scroll = ctk.CTkScrollableFrame(top, fg_color="transparent", corner_radius=0)
            scroll.pack(fill="both", expand=True, padx=20, pady=20)
            return scroll

        def _add_section(target, title, data_dict, accent_color=None):
            section = ctk.CTkFrame(target, fg_color=C("surface"), corner_radius=12,
                                   border_width=1, border_color=C("border"))
            section.pack(fill="x", pady=(0, 15))
            ctk.CTkLabel(section, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                         text_color=accent_color or C("accent2")).pack(anchor="w", padx=15, pady=(10, 5))
            for k, v in data_dict.items():
                row = ctk.CTkFrame(section, fg_color="transparent")
                row.pack(fill="x", padx=15, pady=2)
                ctk.CTkLabel(row, text=f"{k} :", text_color=C("text_dim"), width=130, anchor="w").pack(side="left")
                ctk.CTkLabel(row, text=str(v), text_color=C("text"), wraplength=400, justify="left").pack(side="left", fill="x", expand=True)

        def _render_single(src, info, get_human_size):
            """Construit l'UI mode fichier unique — appelé depuis le thread principal."""
            top.title(t("inspect_title") + src.name)
            scroll = _build_scroll()
            header = ctk.CTkFrame(top, fg_color=C("surface"), height=60, corner_radius=0)
            header.pack(fill="x", side="top")
            header.lift()  # S'assurer que le header est au-dessus du scroll
            ctk.CTkLabel(header, text=t("inspect_title") + src.name,
                         font=ctk.CTkFont(size=16, weight="bold"), text_color=C("accent")).pack(pady=15)
            _add_section(scroll, t("inspect_general"), {
                t("inspect_format"):     info["driver"],
                t("inspect_dims"):       f"{info['width']} x {info['height']} px",
                t("inspect_bands"):      info["bands"],
                t("inspect_size"):       get_human_size(info["file_size"]),
                t("inspect_res"):        f"{abs(info['pixel_size'][0]):.4f} m/px"
            })
            _add_section(scroll, t("inspect_geo"), {
                t("inspect_proj"):       info["projection"][:100] + "...",
                "X Min (ULX)":          f"{info['bbox']['xmin']:.2f}",
                "Y Max (ULY)":          f"{info['bbox']['ymax']:.2f}",
                "X Max (LRX)":          f"{info['bbox']['xmax']:.2f}",
                "Y Min (LRY)":          f"{info['bbox']['ymin']:.2f}"
            })
            for b in info["bands_info"]:
                _add_section(scroll, t("inspect_band_n") + str(b["index"]), {
                    t("inspect_dtype"):      b["dtype"],
                    t("inspect_interp"):     b["color_interp"],
                    t("inspect_nodata"):     b["nodata"] if b["nodata"] is not None else t("inspect_none")
                })

        def _render_group(all_files, total_size, projections, min_x, max_x, min_y, max_y, get_human_size):
            """Construit l'UI mode groupe — appelée depuis le thread principal."""
            top.title(t("inspect_group_title") + str(len(all_files)) + t("inspect_group_files"))
            scroll = _build_scroll()
            header = ctk.CTkFrame(top, fg_color=C("surface2"), height=60, corner_radius=0)
            header.pack(fill="x", side="top")
            header.lift()
            ctk.CTkLabel(header, text=t("inspect_group_title") + str(len(all_files)) + t("inspect_group_files"),
                         font=ctk.CTkFont(size=16, weight="bold"), text_color=C("accent")).pack(pady=15)
            _add_section(scroll, t("inspect_stats"), {
                t("inspect_total"):      len(self.source_files),
                t("inspect_total_size"): get_human_size(total_size),
                t("inspect_main_type"): self.source_files[0].suffix.upper()
            })
            proj_color = C("accent") if len(projections) <= 1 else "#ff5555"
            _add_section(scroll, t("inspect_coherence"), {
                t("inspect_projections"): ", ".join(projections),
                "Status": t("inspect_status_ok") if len(projections) <= 1 else t("inspect_status_warn")
            }, accent_color=proj_color)
            if min_x != float('inf'):
                _add_section(scroll, t("inspect_bbox"), {
                    "Global X Min": f"{min_x:.2f}",
                    "Global Y Max": f"{max_y:.2f}",
                    "Global X Max": f"{max_x:.2f}",
                    "Global Y Min": f"{min_y:.2f}"
                })

        threading.Thread(target=_load_and_render, daemon=True).start()

    def _create_shapefile(self):
        """Crée un Shapefile (.shp) représentant l'emprise du ou des fichiers sélectionnés."""
        if not self.source_files:
            messagebox.showwarning(t("dlg_warn_title"), t("dlg_no_file_extent"))
            return

        try:
            from osgeo import ogr, osr, gdal
        except ImportError:
            messagebox.showerror(t("dlg_error_title"), t("shapefile_no_gdal"))
            return

        try:
            from converter.core import ImageConverter
            from converter.utils import collect_input_files
            conv = ImageConverter()

            # Collecter tous les fichiers
            all_files = []
            for p in self.source_files:
                if p.is_dir():
                    all_files.extend(collect_input_files(str(p)))
                else:
                    all_files.append(p)

            if not all_files:
                messagebox.showerror(t("dlg_error_title"), t("dlg_no_valid_files"))
                return

            # Lire l'emprise de chaque fichier individuellement
            from osgeo import gdal as _gdal
            import os
            extents = []       # liste de (Path, xmin, ymin, xmax, ymax)
            projection_wkt = None

            for f in all_files:
                try:
                    ds = _gdal.Open(str(f))
                    if ds is None:
                        continue
                    gt = ds.GetGeoTransform()
                    xmin = gt[0]
                    ymax = gt[3]
                    xmax = xmin + gt[1] * ds.RasterXSize
                    ymin = ymax + gt[5] * ds.RasterYSize
                    extents.append((f, xmin, ymin, xmax, ymax))
                    if projection_wkt is None:
                        projection_wkt = ds.GetProjection()  # WKT complet, non tronqué
                    ds = None
                except Exception as e:
                    self._log(f"⚠️ Impossible de lire l'emprise de {f.name} : {e}", C("warning"))

            if not extents:
                messagebox.showerror(t("dlg_error_title"), "Impossible de déterminer l'emprise des fichiers.")
                return

            # Demander où sauvegarder via une fenêtre personnalisée
            default_name = all_files[0].stem + "_extent" if len(all_files) == 1 else "extents"
            suggested_dir = str(all_files[0].parent)

            out_path = self._ask_shapefile_path(default_name, suggested_dir)

            if not out_path:
                self._log(t("shapefile_cancelled"), C("text_dim"))
                return

            # Création du Shapefile avec OGR
            driver = ogr.GetDriverByName("ESRI Shapefile")
            if not driver:
                messagebox.showerror(t("dlg_error_title"), "Driver ESRI Shapefile non disponible dans GDAL.")
                return

            # Supprimer si le fichier existe déjà
            if os.path.exists(out_path):
                driver.DeleteDataSource(out_path)

            ds = driver.CreateDataSource(out_path)
            if ds is None:
                messagebox.showerror(t("dlg_error_title"), f"Impossible de créer le fichier : {out_path}")
                return

            # Système de coordonnées
            srs = osr.SpatialReference()
            if projection_wkt:
                srs.ImportFromWkt(projection_wkt)
            else:
                srs.ImportFromEPSG(4326)

            layer = ds.CreateLayer("extent", srs, ogr.wkbPolygon)

            # Champs attributaires
            layer.CreateField(ogr.FieldDefn("filename", ogr.OFTString))
            layer.CreateField(ogr.FieldDefn("xmin", ogr.OFTReal))
            layer.CreateField(ogr.FieldDefn("ymin", ogr.OFTReal))
            layer.CreateField(ogr.FieldDefn("xmax", ogr.OFTReal))
            layer.CreateField(ogr.FieldDefn("ymax", ogr.OFTReal))

            # Créer UN polygone par image
            for (f, xmin, ymin, xmax, ymax) in extents:
                ring = ogr.Geometry(ogr.wkbLinearRing)
                ring.AddPoint(xmin, ymin)
                ring.AddPoint(xmax, ymin)
                ring.AddPoint(xmax, ymax)
                ring.AddPoint(xmin, ymax)
                ring.AddPoint(xmin, ymin)  # Fermer le polygone

                poly = ogr.Geometry(ogr.wkbPolygon)
                poly.AddGeometry(ring)

                feature = ogr.Feature(layer.GetLayerDefn())
                feature.SetGeometry(poly)
                feature.SetField("filename", f.name)
                feature.SetField("xmin",     round(xmin, 6))
                feature.SetField("ymin",     round(ymin, 6))
                feature.SetField("xmax",     round(xmax, 6))
                feature.SetField("ymax",     round(ymax, 6))
                layer.CreateFeature(feature)
                feature = None

            # Libérer les ressources
            ds = None

            shp_name = os.path.basename(out_path)
            self._log(f"{t('shapefile_success')} {shp_name}  ({len(extents)} polygone(s))")
            messagebox.showinfo(t("dlg_done_title"),
                                f"{t('shapefile_success')}\n{out_path}")

        except Exception as e:
            self._log(f"{t('shapefile_error')} {e}", C("error"))
            messagebox.showerror(t("dlg_error_title"), f"{t('shapefile_error')}\n{e}")

    def _ask_shapefile_path(self, default_name: str, suggested_dir: str) -> str:
        """Fenêtre CTk personnalisée pour choisir le nom et l'emplacement du Shapefile."""
        result = [None]

        dlg = ctk.CTkToplevel(self.root)
        dlg.title(t("shapefile_save_as"))
        dlg.geometry("620x260")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C("bg"))
        dlg.transient(self.root)
        dlg.grab_set()
        dlg.after(50, dlg.focus_force)

        # ── En-tête
        ctk.CTkLabel(dlg, text=t("shapefile_title"),
                     font=ctk.CTkFont(size=15, weight="bold"),
                     text_color=C("accent")).pack(anchor="w", padx=25, pady=(20, 15))

        # ── Dossier de destination
        dir_var = tk.StringVar(value=suggested_dir)

        row_dir = ctk.CTkFrame(dlg, fg_color="transparent")
        row_dir.pack(fill="x", padx=25, pady=(0, 10))
        ctk.CTkLabel(row_dir, text=t("shapefile_dir_lbl"), text_color=C("text_dim"),
                     width=90, anchor="w").pack(side="left")
        dir_entry = ctk.CTkEntry(row_dir, textvariable=dir_var, height=32,
                                 corner_radius=8, border_color=C("border"),
                                 fg_color=C("surface2"))
        dir_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        ctk.CTkButton(row_dir, text="…", width=36, height=32, corner_radius=8,
                      fg_color=C("surface2"), hover_color=C("accent"),
                      text_color=C("text"),
                      command=lambda: dir_var.set(
                          filedialog.askdirectory(title="Choisir un dossier",
                                                  initialdir=dir_var.get(),
                                                  parent=dlg) or dir_var.get()
                      )).pack(side="left")

        # ── Nom du fichier
        name_var = tk.StringVar(value=default_name)

        row_name = ctk.CTkFrame(dlg, fg_color="transparent")
        row_name.pack(fill="x", padx=25, pady=(0, 20))
        ctk.CTkLabel(row_name, text=t("shapefile_name_lbl"), text_color=C("text_dim"),
                     width=90, anchor="w").pack(side="left")
        name_entry = ctk.CTkEntry(row_name, textvariable=name_var, height=32,
                                  corner_radius=8, border_color=C("border"),
                                  fg_color=C("surface2"))
        name_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        ctk.CTkLabel(row_name, text=".shp", text_color=C("text_dim"),
                     font=ctk.CTkFont(size=12)).pack(side="left")

        # ── Boutons
        def on_confirm():
            folder = dir_var.get().strip()
            name = name_var.get().strip()
            if not folder or not name:
                return
            if not name.endswith(".shp"):
                name += ".shp"
            result[0] = os.path.join(folder, name)
            dlg.destroy()

        def on_cancel():
            dlg.destroy()

        row_btns = ctk.CTkFrame(dlg, fg_color="transparent")
        row_btns.pack(fill="x", padx=25, pady=(0, 20))
        ctk.CTkButton(row_btns, text=t("btn_save"), command=on_confirm,
                      width=140, height=36, corner_radius=8,
                      fg_color=C("accent2"), hover_color="#059669",
                      text_color="white", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=(0, 10))
        ctk.CTkButton(row_btns, text=t("btn_cancel_action"), command=on_cancel,
                      width=110, height=36, corner_radius=8,
                      fg_color=C("surface2"), hover_color="#CC0000",
                      text_color=C("text")).pack(side="left")

        dlg.bind("<Return>", lambda e: on_confirm())
        dlg.bind("<Escape>", lambda e: on_cancel())

        dlg.wait_window()
        return result[0]

    def _estimate_output_size(self):
        """Prédit la taille de sortie selon les réglages actuels.
        
        Les lectures GDAL sont faites dans un thread séparé pour ne pas bloquer l'UI.
        Un spinner est affiché pendant le chargement.
        """
        if not self.source_files:
            self._log("⚠ Please select a source file first.", "error")
            return

        from converter.utils import collect_input_files
        all_files = []
        for p in self.source_files:
            if p.is_dir():
                all_files.extend(collect_input_files(str(p)))
            else:
                all_files.append(p)

        # Capturer les paramètres UI maintenant, avant de passer au thread
        fmt          = self.format_var.get()
        comp         = self.compress_var.get()
        depth        = self.bit_depth_var.get()
        mosaic_mode  = self.mosaic_var.get() and len(all_files) > 1
        build_ovr    = self.overviews_var.get()
        clipping_active = self.clip_var.get()
        clip_geo = None
        if clipping_active:
            try:
                clip_geo = (
                    float(self.ulx_var.get()), float(self.uly_var.get()),
                    float(self.lrx_var.get()), float(self.lry_var.get())
                )
            except:
                clipping_active = False

        # ── Fenêtre immédiate avec spinner ──
        top = ctk.CTkToplevel(self.root)
        top.title(t("estimate_title"))
        top.geometry("450x350")
        top.configure(fg_color=C("bg"))
        top.after(100, lambda: top.focus_force())

        spinner = ctk.CTkLabel(top, text=t("estimate_loading"),
                               font=ctk.CTkFont(size=14), text_color=C("text_dim"))
        spinner.pack(expand=True)

        def _compute():
            """Exécuté dans un thread : lit les métadonnées et calcule la taille."""
            try:
                from converter.core import ImageConverter
                from converter.utils import get_human_size
                conv = ImageConverter()

                comp_ratio = 1.0
                if "LZW" in comp:    comp_ratio = 0.5
                elif "DEFLATE" in comp: comp_ratio = 0.4
                elif "JPEG" in comp:  comp_ratio = 0.12
                bpp = 2.0 if "16" in depth else 1.0

                total_est_size = 0
                file_count = len(all_files)

                if mosaic_mode:
                    min_x, max_x = float('inf'), float('-inf')
                    min_y, max_y = float('inf'), float('-inf')
                    pix_x, pix_y, bands = 0, 0, 0
                    for f in all_files:
                        try:
                            info = conv.get_info(f)  # ← lecture GDAL
                            min_x = min(min_x, info["bbox"]["xmin"])
                            max_x = max(max_x, info["bbox"]["xmax"])
                            min_y = min(min_y, info["bbox"]["ymin"])
                            max_y = max(max_y, info["bbox"]["ymax"])
                            pix_x, pix_y = abs(info["pixel_size"][0]), abs(info["pixel_size"][1])
                            bands = info["bands"]
                        except: pass
                    if pix_x > 0 and pix_y > 0:
                        if clipping_active and clip_geo:
                            win_w = abs(clip_geo[2] - clip_geo[0]) / pix_x
                            win_h = abs(clip_geo[1] - clip_geo[3]) / pix_y
                        else:
                            win_w = (max_x - min_x) / pix_x
                            win_h = (max_y - min_y) / pix_y
                        total_est_size = win_w * win_h * bands * bpp * comp_ratio
                else:
                    for f in all_files:
                        try:
                            info = conv.get_info(f)  # ← lecture GDAL
                            if clipping_active and clip_geo:
                                px, py = abs(info["pixel_size"][0]), abs(info["pixel_size"][1])
                                win_w = abs(clip_geo[2] - clip_geo[0]) / px
                                win_h = abs(clip_geo[1] - clip_geo[3]) / py
                                raw_bytes = win_w * win_h * info["bands"] * bpp
                            else:
                                raw_bytes = info["width"] * info["height"] * info["bands"] * bpp
                            total_est_size += raw_bytes * comp_ratio
                        except:
                            total_est_size += f.stat().st_size * 1.5

                total_est_size *= 1.33 if build_ovr else 1.1

                self.root.after(0, lambda: _render(
                    file_count, mosaic_mode, clipping_active, fmt, comp,
                    total_est_size, get_human_size
                ))
            except Exception as e:
                self.root.after(0, lambda: self._log(f"✗ Erreur d'estimation : {e}", "error"))
                self.root.after(0, top.destroy)

        def _render(file_count, mosaic_mode, clipping_active, fmt, comp, total_est_size, get_human_size):
            """Construit l'UI du résultat — appelée depuis le thread principal."""
            spinner.destroy()

            header = ctk.CTkFrame(top, fg_color=C("surface"), height=60, corner_radius=0)
            header.pack(fill="x", pady=(0, 20))
            ctk.CTkLabel(header, text=t("estimate_pred_title"),
                         font=ctk.CTkFont(size=15, weight="bold"), text_color=C("accent")).pack(pady=15)

            card = ctk.CTkFrame(top, fg_color=C("surface"), corner_radius=16,
                                border_width=1, border_color=C("border"))
            card.pack(fill="both", expand=True, padx=30, pady=(0, 20))

            def add_line(label, value, color=None):
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=5)
                ctk.CTkLabel(row, text=label, text_color=C("text_dim")).pack(side="left")
                ctk.CTkLabel(row, text=value, text_color=color or C("text"),
                             font=ctk.CTkFont(weight="bold")).pack(side="right")

            add_line(t("estimate_files"),  str(file_count))
            add_line(t("estimate_mode"),    t("estimate_mode_mosaic") if mosaic_mode else t("estimate_mode_batch"))
            add_line(t("estimate_zone"),    t("estimate_zone_clip") if clipping_active else t("estimate_zone_full"))
            add_line(t("estimate_format"),  fmt)
            add_line(t("estimate_compress"), comp.split('(')[0].strip())
            ctk.CTkFrame(card, height=1, fg_color=C("border")).pack(fill="x", padx=20, pady=10)
            add_line(t("estimate_total"),   get_human_size(int(total_est_size)), C("accent"))

            warning = ""
            if total_est_size > 50 * 1024**3:
                warning = t("estimate_warn_50g")
            elif total_est_size > 10 * 1024**3:
                warning = t("estimate_warn_10g")
            if warning:
                ctk.CTkLabel(card, text=warning, text_color="#ff5555",
                             font=ctk.CTkFont(slant="italic")).pack(pady=5)

            ctk.CTkButton(top, text=t("btn_understood"), command=top.destroy,
                          fg_color=C("surface2"), hover_color=C("accent")).pack(pady=(0, 20))

        threading.Thread(target=_compute, daemon=True).start()

    def _update_comp_menu(self, values: list, default: str, normal_state: bool):
        """Met à jour la liste et la valeur du menu de compression.
        
        FlatDropdown.set_values() ne redessine jamais le widget parent.
        """
        if values:
            self.comp_menu.set_values(values)
        self.compress_var.set(default)
        self.comp_menu.configure(state="readonly" if normal_state else "disabled")
            
    def _set_widget_state(self, widget, state: str):
        """Met à jour l'état (normal/disabled) d'un widget selon l'UI active."""
        if CTK:
            widget.configure(state=state)
        else:
            widget.configure(state=state)

    def _clear_log(self):
        if CTK:
            self.log_text.delete("1.0", "end")
        else:
            self.log_text.delete("1.0", tk.END)

    def _show_license(self):
        """Affiche la licence Apache 2.0 dans une fenêtre brandée."""
        top = ctk.CTkToplevel(self.root) if CTK else tk.Toplevel(self.root)
        top.title(t("license_title"))
        top.geometry("700x600")
        top.configure(bg=C("bg"))
        if CTK: top.configure(fg_color=C("bg"))
        top.after(100, lambda: top.focus_force())

        # Header branding
        header = ctk.CTkFrame(top, fg_color=C("surface"), height=70, corner_radius=0)
        header.pack(fill="x", pady=(0, 20))
        
        logo_img = None
        if CTK and hasattr(self, "logo_image"):
            logo_img = self.logo_image
        elif hasattr(self, "logo_photo"):
            logo_img = self.logo_photo
            
        lbl_logo = ctk.CTkLabel(header, text="", image=logo_img, width=40, height=40)
        lbl_logo.pack(side="left", padx=(20, 15), pady=10)
        
        ctk.CTkLabel(header, text="GeoConvert", font=ctk.CTkFont(size=18, weight="bold"), 
                      text_color=C("accent")).pack(side="left")
        ctk.CTkLabel(header, text=f" — {t('license_title')}", font=ctk.CTkFont(size=14), 
                      text_color=C("text_dim")).pack(side="left", padx=5)

        license_text = """Copyright 2026 HOUIZOT Lénaïc

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
        if CTK:
            textbox = ctk.CTkTextbox(top, wrap="word", fg_color=C("surface"), text_color=C("text"), font=ctk.CTkFont(family="Courier", size=12))
            textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))
            textbox.insert("1.0", license_text)
            textbox.configure(state="disabled")
        else:
            textbox = tk.Text(top, wrap="word", bg=C("surface"), fg=C("text"), font=("Courier", 12))
            textbox.pack(fill="both", expand=True, padx=20, pady=20)
            textbox.insert("1.0", license_text)
            textbox.config(state="disabled")

    def _open_github(self):
        """Ouvre le dépôt GitHub du projet."""
        try:
            webbrowser.open("https://github.com/L3N4IC/GeoConvert") # Adaptez si besoin
        except:
            self._log("⚠  Impossible d'ouvrir le navigateur web.", COLORS["warning"])

    def _show_help(self):
        """Affiche une fenêtre d'aide brandée et détaillée."""
        top = ctk.CTkToplevel(self.root) if CTK else tk.Toplevel(self.root)
        top.title(t("help_title"))
        top.geometry("700x550")
        top.configure(bg=C("bg"))
        if CTK: top.configure(fg_color=C("bg"))
        top.after(100, lambda: top.focus_force())

        # Header branding
        header = ctk.CTkFrame(top, fg_color=C("surface"), height=70, corner_radius=0)
        header.pack(fill="x", pady=(0, 20))
        
        logo_img = None
        if CTK and hasattr(self, "logo_image"):
            logo_img = self.logo_image
        elif hasattr(self, "logo_photo"):
            logo_img = self.logo_photo
            
        lbl_logo = ctk.CTkLabel(header, text="", image=logo_img, width=40, height=40)
        lbl_logo.pack(side="left", padx=(20, 15), pady=10)
        
        ctk.CTkLabel(header, text="GeoConvert", font=ctk.CTkFont(size=18, weight="bold"), 
                      text_color=C("accent")).pack(side="left")
        ctk.CTkLabel(header, text=f" — {t('help_title')}", font=ctk.CTkFont(size=14), 
                      text_color=C("text_dim")).pack(side="left", padx=5)

        if CTK:
            scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
            scroll.pack(fill="both", expand=True, padx=30, pady=(0, 30))
            
            help_text = t("help_msg")
            label = ctk.CTkLabel(scroll, text=help_text, justify="left", wraplength=600, 
                                 font=ctk.CTkFont(size=13), text_color=C("text"))
            label.pack(fill="x", padx=10, pady=10)
            
            ctk.CTkButton(top, text=t("btn_understood"), width=120, 
                          fg_color=C("accent"), text_color="white",
                          command=top.destroy).pack(pady=(0, 20))
        else:
            messagebox.showinfo(t("help_title"), t("help_msg"))

    def _open_bug_report(self):
        """Ouvre directement la page de création d'issue GitHub."""
        try:
            webbrowser.open("https://github.com/L3N4IC/GeoConvert/issues/new")
        except Exception:
            self._log("⚠  Impossible d'ouvrir le navigateur web.", COLORS["warning"])

    def _open_gdal_docs(self):
        """Ouvre la documentation des drivers raster GDAL."""
        try:
            webbrowser.open("https://gdal.org/en/stable/drivers/raster/index.html")
        except Exception:
            self._log("⚠  Impossible d'ouvrir le navigateur web.", COLORS["warning"])

    def _show_sysinfo(self):
        """Affiche les informations système : versions GDAL, Python, librairies."""
        import sys
        import platform

        # Collecte des infos
        python_ver = sys.version.split(" ")[0]
        plat = platform.platform()

        try:
            from osgeo import gdal
            gdal_ver = gdal.VersionInfo("RELEASE_NAME")
            driver_count = gdal.GetDriverCount()
        except Exception:
            gdal_ver = "Non disponible"
            driver_count = "?"

        try:
            import PIL
            pil_ver = PIL.__version__
            pil_status = f"v{pil_ver}"
            pil_color = C("accent2")
        except ImportError:
            pil_status = t("sysinfo_missing")
            pil_color = C("error")

        try:
            import customtkinter
            ctk_ver = customtkinter.__version__
            ctk_status = f"v{ctk_ver}"
            ctk_color = C("accent2")
        except ImportError:
            ctk_status = t("sysinfo_missing")
            ctk_color = C("error")

        try:
            import numpy
            np_ver = numpy.__version__
            np_status = f"v{np_ver}"
            np_color = C("accent2")
        except ImportError:
            np_status = t("sysinfo_missing")
            np_color = C("error")

        # Fenêtre
        top = ctk.CTkToplevel(self.root)
        top.title(t("sysinfo_title"))
        top.geometry("520x420")
        top.configure(fg_color=C("bg"))
        top.transient(self.root)
        top.after(100, lambda: top.focus_force())

        # Header
        header = ctk.CTkFrame(top, fg_color=C("surface"), height=60, corner_radius=0)
        header.pack(fill="x")

        logo_img = getattr(self, "logo_image", None)
        if logo_img:
            ctk.CTkLabel(header, text="", image=logo_img, width=36, height=36).pack(side="left", padx=(20, 12), pady=12)

        ctk.CTkLabel(header, text="GeoConvert", font=ctk.CTkFont(size=17, weight="bold"),
                     text_color=C("accent")).pack(side="left")
        ctk.CTkLabel(header, text=f" — {t('sysinfo_title')}", font=ctk.CTkFont(size=13),
                     text_color=C("text_dim")).pack(side="left", padx=5)

        # Contenu
        scroll = ctk.CTkScrollableFrame(top, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=20)

        def add_row(label, value, value_color=None):
            row = ctk.CTkFrame(scroll, fg_color=C("surface"), corner_radius=10)
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=label, text_color=C("text_dim"),
                         width=200, anchor="w", font=ctk.CTkFont(size=12)).pack(side="left", padx=15, pady=8)
            ctk.CTkLabel(row, text=value, text_color=value_color or C("text"),
                         font=ctk.CTkFont(size=12, weight="bold"), anchor="w").pack(side="left", padx=5)

        add_row(t("sysinfo_gdal"),    gdal_ver,               C("accent"))
        add_row(t("sysinfo_python"),  python_ver,             C("accent"))
        add_row(t("sysinfo_drivers"), str(driver_count),      C("accent2"))
        add_row(t("sysinfo_pillow"),  pil_status,             pil_color)
        add_row(t("sysinfo_ctk"),     ctk_status,             ctk_color)
        add_row(t("sysinfo_numpy"),   np_status,              np_color)
        add_row(t("sysinfo_platform"), plat,                  C("text_dim"))

        ctk.CTkButton(top, text=t("btn_understood"), command=top.destroy,
                      fg_color=C("surface2"), hover_color=C("accent"),
                      text_color=C("text")).pack(pady=(0, 20))

    # ── Conversion ────────────────────────────────────────────────────────────

    # Nombre maximum de lignes conservées dans le journal.
    # Au-delà, les lignes les plus anciennes sont supprimées pour éviter
    # le ralentissement progressif de CTkTextbox sur les longues sessions.
    _LOG_MAX_LINES = 500

    def _log(self, msg: str, color: str = ""):
        if CTK:
            self.log_text.insert("end", msg + "\n")
            # Élaguer si le journal dépasse la limite
            line_count = int(self.log_text.index("end-1c").split(".")[0])
            if line_count > self._LOG_MAX_LINES:
                excess = line_count - self._LOG_MAX_LINES
                self.log_text.delete("1.0", f"{excess + 1}.0")
            self.log_text.see("end")
        else:
            self.log_text.insert(tk.END, msg + "\n")
            # Même limite pour le widget tk.Text standard
            line_count = int(self.log_text.index(tk.END).split(".")[0])
            if line_count > self._LOG_MAX_LINES:
                excess = line_count - self._LOG_MAX_LINES
                self.log_text.delete("1.0", f"{excess + 1}.0")
            self.log_text.see(tk.END)

    def _set_progress(self, value: float, label: str = ""):
        """Met à jour la barre de progression (0.0 - 1.0)."""
        if CTK:
            self.progress_bar.set(value)
            self.lbl_progress.configure(text=label)
        else:
            self.progress_bar["value"] = int(value * 100)
            self.lbl_progress.configure(text=label)

    def _start_conversion(self):
        if not self.source_files:
            messagebox.showwarning(t("dlg_no_file_title"), t("dlg_no_file_msg"))
            return

        fmt = self.format_var.get()
        out_dir = self.output_dir.get() or None
        
        # Extraction intelligente du code EPSG (tolère "4326 - WGS84" ou juste "4326")
        epsg_str = self.epsg_var.get().strip()
        epsg = None
        if epsg_str:
            # Récupère le premier mot qui devrait être le nombre
            first_part = epsg_str.split("-")[0].strip()
            if first_part.isdigit():
                epsg = int(first_part)
            else:
                self._log(t("log_epsg_invalid") + f"'{epsg_str}'", C("warning"))
        
        # Découpage ( Clipping )
        clip_box = None
        if self.clip_var.get():
            try:
                ulx = float(self.ulx_var.get())
                uly = float(self.uly_var.get())
                lrx = float(self.lrx_var.get())
                lry = float(self.lry_var.get())
                clip_box = [ulx, uly, lrx, lry]
            except ValueError:
                messagebox.showerror(t("dlg_invalid_coords_title"), t("dlg_invalid_coords_msg"))
                return
        
        # Construction dynamique des options GDAL en fonction du format et des choix simples
        opts = []
        comp_choice = self.compress_var.get()
        
        # === GeoTIFF / COG ===
        if fmt in ["GeoTIFF", "COG"]:
            # Baseline for very large files (force BIGTIFF for safety)
            opts.append("BIGTIFF=YES")
            
            if self.tiled_var.get():
                opts.append("TILED=YES")
                
            if "LZW" in comp_choice:
                opts.append("COMPRESS=LZW")
                opts.append("PREDICTOR=2")
            elif "DEFLATE" in comp_choice:
                opts.append("COMPRESS=DEFLATE")
                opts.append("PREDICTOR=2")
            elif "JPEG" in comp_choice:
                opts.append("COMPRESS=JPEG")
                
        # === PNG / WebP ===
        elif fmt in ["PNG", "WebP"]:
            if fmt == "PNG":
                if "9" in comp_choice:
                    opts.append("ZLEVEL=9")
                elif "1" in comp_choice:
                    opts.append("ZLEVEL=1")
                elif "6" in comp_choice:
                    opts.append("ZLEVEL=6")
                
        # === JPEG / JPEG2000 / PDF ===
        elif fmt in ["JPEG", "JPEG2000", "PDF"]:
            if fmt == "PDF":
                opts.append("GEO_ENCODING=ISO32000")
                
        # Repli si aucune option
        if not opts:
            opts = None

        build_ovr = self.overviews_var.get() and fmt in ["GeoTIFF", "COG"]
        nodata_val = 0 if self.nodata_var.get() and fmt in ["GeoTIFF", "COG"] else None
        
        # Bit depth
        bit_choice = self.bit_depth_var.get()
        out_type = None
        if "8-bit" in bit_choice:
            out_type = "Byte"
        elif "16-bit" in bit_choice:
            out_type = "UInt16"
            
        use_mt = self.multithread_var.get()
        quality_val = self.quality_var.get()
        res_choice = self.resampling_var.get()

        if CTK:
            self.btn_convert.configure(state="disabled", text="⏳…")
            self.btn_stop.configure(state="normal")
        else:
            self.btn_convert.configure(state="disabled", text="⏳…")
            self.btn_stop.configure(state="normal")

        self.is_cancelled = False

        self._set_progress(0, t("progress_init"))
        self._log(t("log_start") + fmt)

        def run():
            try:
                from converter.core import ImageConverter
                from converter.utils import collect_input_files, get_human_size
                conv = ImageConverter()

                # Collecte des fichiers
                all_files = []
                for src in self.source_files:
                    all_files.extend(collect_input_files(str(src)))

                total = len(all_files)
                self._log(f"   {total} " + t("log_files_count"))
                ok = 0

                if self.mosaic_var.get() and len(all_files) > 1:
                    # -- Mode Mosaïque --
                    self._log(t("log_mosaic_mode"))
                    self.root.after(0, self._set_progress, 0.1, "Construction de la mosaïque virtuelle VRT...")
                    
                    def progress_cb(pct, msg, data):
                        if self.is_cancelled:
                            return 0 # Arrêt demandé à GDAL
                        label = f"Mosaïquage + Conversion — {int(pct*100)}%"
                        self.root.after(0, self._set_progress, pct, label)
                        return 1
                        
                    # On passe la liste de STR au module core
                    str_files = [str(f) for f in all_files]
                    result = conv.convert(
                        str_files, 
                        format_name=fmt, 
                        output_dir=out_dir,
                        epsg=epsg, 
                        creation_options=opts,
                        progress_callback=progress_cb,
                        build_overviews=build_ovr,
                        nodata=nodata_val,
                        output_type=out_type,
                        use_multithread=use_mt,
                        quality=quality_val,
                        resampling=res_choice,
                        clip_box=clip_box
                    )
                    if result.success:
                        ok = total # On considère l'opération comme réussie pour tous les fichiers
                        self.root.after(0, self._log, t("log_success_mosaic") + f"{result.dst.name} ({get_human_size(result.dst.stat().st_size)})", C("success"))
                        self.root.after(0, self._log, f"   Temps : {result.elapsed:.1f}s", C("text_dim"))
                    else:
                        self.root.after(0, self._log, t("log_error_mosaic") + str(result.error), C("error"))

                else:
                    # -- Mode classique (fichier par fichier) --
                    for i, f in enumerate(all_files):
                        self.root.after(0, self._set_progress, i / total, f"({i+1}/{total}) {f.name}…")
                        
                        def progress_cb(pct, msg, data):
                            if self.is_cancelled:
                                return 0
                            global_pct = (i + pct) / total
                            label = f"({i+1}/{total}) {f.name} — {int(pct*100)}%"
                            self.root.after(0, self._set_progress, global_pct, label)
                            return 1
                        
                        result = conv.convert(
                            str(f), 
                            format_name=fmt, 
                            output_dir=out_dir,
                            epsg=epsg, 
                            creation_options=opts,
                            progress_callback=progress_cb,
                            build_overviews=build_ovr,
                            nodata=nodata_val,
                            output_type=out_type,
                            use_multithread=use_mt,
                            quality=quality_val,
                            resampling=res_choice,
                            clip_box=clip_box
                        )
                        
                        if result.success:
                            ok += 1
                            size = get_human_size(result.dst.stat().st_size)
                            self.root.after(0, self._log, f"   ✓  {result.src.name} → {result.dst.name}  ({result.elapsed:.2f}s, {size})")
                        else:
                            self.root.after(0, self._log, f"   ✗  {result.src.name} : {result.error}")

                self.root.after(0, self._set_progress, 1.0, t("log_done_summary") + f"{ok}/{total}" + t("log_done_ok"))
                
                if self.mosaic_var.get() and len(all_files) > 1:
                    log_msg = "\n" + t("log_done_mosaic") + str(total) + t("log_done_mosaic_suffix")
                else:
                    log_msg = "\n" + t("log_done") + f"{ok}/{total}" + t("log_done_suffix")
                
                self.root.after(0, self._log, log_msg)
                
                if ok > 0:
                    out_path = out_dir or str(all_files[0].parent)
                    if self.mosaic_var.get() and len(all_files) > 1:
                        msg = t("dlg_done_mosaic_msg") + str(total) + t("dlg_done_files") + out_path
                    else:
                        msg = f"{ok}/{total}" + t("dlg_done_batch_msg") + out_path
                    
                    self.root.after(0, messagebox.showinfo, t("dlg_done_title"), msg)

            except Exception as e:
                self.root.after(0, self._log, f"\n✗  Erreur : {e}")
                self.root.after(0, messagebox.showerror, t("dlg_error_title"), str(e))
            finally:
                def restore_btn():
                    if CTK:
                        self.btn_convert.configure(state="normal", text=t("btn_convert"))
                        self.btn_stop.configure(state="disabled", text=t("btn_stop"))
                    else:
                        self.btn_convert.configure(state="normal", text=t("btn_convert"))
                        self.btn_stop.configure(state="disabled", text=t("btn_stop"))
                
                self.root.after(0, restore_btn)

        threading.Thread(target=run, daemon=True).start()


# ─── Point d'entrée ──────────────────────────────────────────────────────────

def main():
    GeoConvertApp()


if __name__ == "__main__":
    main()
