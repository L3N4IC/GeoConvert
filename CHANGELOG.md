# Changelog

All notable changes to GeoConvert are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.0.1] - 2026-03-25

### 🇬🇧 English

#### Fixed
- **UI freeze on conversion start (executable)**: In the compiled version (PyInstaller/Nuitka), the first click on "Start conversion" caused the interface to freeze while GDAL initialized its drivers from the bundle. Resolved by pre-instantiating `ImageConverter` in a daemon thread at app startup (`self.converter`, initialized in `__init__`). A `_get_converter()` accessor is used everywhere instead of direct `ImageConverter()`, with synchronous fallback if the user clicks before the thread finishes (< 1s case).
- **Unnecessary double GDAL import**: `ImageConverter._check_gdal()` performed a second `from osgeo import gdal` even though the import was already done in `__init__`. The method is now a no-op (`pass`), avoiding this superfluous cost at each instantiation.
- **6 redundant instantiations of `ImageConverter`**: The functions for inspection, thumbnail, shapefile, estimation, and conversion each created their own instance. They now all use `self._get_converter()`, ensuring only one GDAL initialization occurs per session.

#### Added
- **Automatic update check**: At startup, GeoConvert silently queries the GitHub Releases API (`/repos/{owner}/{repo}/releases/latest`) in a daemon thread, 2 seconds after the window opens. If a newer version is detected, a compact amber banner appears under the header with a "Download" button (opens the release page in the browser) and a "Dismiss" button to close the banner. No popup, no blocking, no visible error in case of network issue.
- **`APP_VERSION` constant**: The application version is now defined in a single place (`APP_VERSION = "1.0.1"` at the top of `gui.py`). The version badge in the header and the comparison logic both use it.
- **New translation keys** (`gui.py`): `update_available`, `update_download`, `update_dismiss` — available in French and English.
- **End of conversion window**: Replaced the native tkinter `messagebox` with a custom `CTkToplevel` window (`_show_done_dialog`) consistent with the rest of the interface. Displays the logo, a ✅ / ❌ icon depending on the result, the output message, and a "Got it" button (shortcuts `Enter` / `Esc`). Automatically centers on the main window.
- **"📁 Open folder" button**: Added a button in the end of conversion window (success only) to directly access the destination folder in the system file manager (Finder, Explorer, xdg-open). The window closes automatically after opening the folder.
- **`NOTICES` file**: Added a file at the root of the project listing third-party dependencies and their licenses (GDAL, CustomTkinter, Pillow, NumPy, Python Standard Library), following Apache 2.0 best practices.
- **Apache 2.0 license headers**: Added copyright boilerplate to all Python source files that lacked it:
  - `converter/core.py`
  - `converter/formats.py`
  - `converter/utils.py`
  - `converter/epsg_bank.py`
  - `converter/__init__.py`

#### Changed
- **`requirements.txt`**: Added `numpy>=1.24.0`, an implicit dependency now explicitly declared.
- **Theme change (`_apply_theme`)**: Complete rewrite of the color update method. Replaced the simple iteration over the `_ui_registry` with a recursive traversal of the widget tree covering all CTk and native tk types: `CTkLabel`, `CTkFrame`, `CTkScrollableFrame`, `CTkButton`, `CTkCheckBox`, `CTkSegmentedButton`, `CTkSlider`, `CTkOptionMenu`, `CTkEntry`, `CTkTextbox`, `CTkProgressBar`, `tk.Frame`, `tk.Label`. Fixed the CTK compatibility bug where `cget()` sometimes returns a list instead of a string. Added explicit update of the version badge (`lbl_version`) in the header.

#### Removed
- **Unused logo**: Removed `geoconvert_logo_flat_white_1773006660522.png`, a design variant not referenced in the code.

---

### 🇫🇷 Français

#### Fixed
- **Gel de l'UI au démarrage de la conversion (exécutable)** : dans la version compilée (PyInstaller/Nuitka), le premier clic sur « Lancer la conversion » provoquait un gel de l'interface le temps que GDAL initialise ses drivers depuis le bundle. Résolu en pré-instanciant `ImageConverter` dans un thread daemon dès le démarrage de l'app (`self.converter`, initialisé dans `__init__`). Un accesseur `_get_converter()` est utilisé partout à la place de `ImageConverter()` direct, avec fallback synchrone si l'utilisateur clique avant la fin du thread (cas < 1s).
- **Double import GDAL inutile** : `ImageConverter._check_gdal()` effectuait un second `from osgeo import gdal` alors que l'import était déjà réalisé dans `__init__`. La méthode est désormais un no-op (`pass`), évitant ce coût superflu à chaque instanciation.
- **6 instanciations redondantes de `ImageConverter`** : les fonctions d'inspection, de miniature, de shapefile, d'estimation et de conversion recréaient chacune leur propre instance. Elles utilisent désormais toutes `self._get_converter()`, ce qui garantit qu'une seule initialisation GDAL a lieu par session.

#### Added
- **Vérification automatique des mises à jour** : au démarrage, GeoConvert interroge silencieusement l'API GitHub Releases (`/repos/{owner}/{repo}/releases/latest`) dans un thread daemon, 2 secondes après l'ouverture de la fenêtre. Si une version plus récente est détectée, un bandeau amber compact s'affiche sous le header avec un bouton « Télécharger » (ouvre la release page dans le navigateur) et un bouton « Ignorer » pour fermer le bandeau. Aucune popup, aucun blocage, aucune erreur visible en cas de problème réseau.
- **Constante `APP_VERSION`** : la version de l'application est désormais définie en un seul endroit (`APP_VERSION = "1.0.1"` en haut de `gui.py`). Le badge de version dans le header et la logique de comparaison l'utilisent tous les deux.
- **Nouvelles clés de traduction** (`gui.py`) : `update_available`, `update_download`, `update_dismiss` — disponibles en français et en anglais.
- **Fenêtre de fin de conversion** : remplacement du `messagebox` natif tkinter par une fenêtre `CTkToplevel` custom (`_show_done_dialog`) cohérente avec le reste de l'interface. Affiche le logo, une icône ✅ / ❌ selon le résultat, le message de sortie, et un bouton "Compris" (raccourcis `Entrée` / `Échap`). Se centre automatiquement sur la fenêtre principale.
- **Bouton "📁 Ouvrir le dossier"** : ajout d'un bouton dans la fenêtre de fin de conversion (succès uniquement) permettant d'accéder directement au dossier de destination dans le gestionnaire de fichiers système (Finder, Explorateur, xdg-open). La fenêtre se ferme automatiquement après l'ouverture du dossier.
- **Fichier `NOTICES`** : ajout à la racine du projet d'un fichier listant les dépendances tierces et leurs licences (GDAL, CustomTkinter, Pillow, NumPy, Python Standard Library), conformément aux bonnes pratiques Apache 2.0.
- **En-têtes de licence Apache 2.0** : ajout du boilerplate de copyright dans tous les fichiers source Python qui en étaient dépourvus :
  - `converter/core.py`
  - `converter/formats.py`
  - `converter/utils.py`
  - `converter/epsg_bank.py`
  - `converter/__init__.py`

#### Changed
- **`requirements.txt`** : ajout de `numpy>=1.24.0`, dépendance implicite désormais déclarée explicitement.
- **Changement de thème (`_apply_theme`)** : refonte complète de la méthode de mise à jour des couleurs. Remplacement du simple parcours du registre `_ui_registry` par un parcours récursif de l'arbre de widgets couvrant tous les types CTk et tk natifs : `CTkLabel`, `CTkFrame`, `CTkScrollableFrame`, `CTkButton`, `CTkCheckBox`, `CTkSegmentedButton`, `CTkSlider`, `CTkOptionMenu`, `CTkEntry`, `CTkTextbox`, `CTkProgressBar`, `tk.Frame`, `tk.Label`. Correction du bug de compatibilité CTK où `cget()` retourne parfois une liste au lieu d'une string. Ajout de la mise à jour explicite du badge de version (`lbl_version`) dans le header.

#### Removed
- **Logo inutilisé** : suppression de `geoconvert_logo_flat_white_1773006660522.png`, variante de design non référencée dans le code.

---

## [1.0.0] - 2026-01-01

### 🇬🇧 English
- Initial release of GeoConvert.

### 🇫🇷 Français
- Version initiale de GeoConvert.
