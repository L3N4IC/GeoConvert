# GeoConvert

**GeoConvert** is a desktop application for converting geospatial raster images using GDAL, with a modern GUI built with CustomTkinter.

> 🇫🇷 [Version française ci-dessous](#version-française)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-Apache%202.0-green)
![GDAL](https://img.shields.io/badge/GDAL-3.x-orange)

---

## Features

- Convert geospatial rasters between 13+ formats (GeoTIFF, COG, PNG, JPEG, NetCDF, GPKG, WebP, PDF, JPEG2000, and more)
- Batch processing — convert entire folders at once
- Light / Dark theme toggle with persistent preference
- French 🇫🇷 / English 🇬🇧 interface with persistent language preference
- Built on GDAL for reliable, high-fidelity geospatial conversions

## Supported Input Formats

`.jp2` `.j2k` `.tif` `.tiff` `.ecw` `.img` `.nc` `.png` `.jpg` `.ntf` `.nitf` `.hdf` `.h5` `.vrt` `.dem` `.asc`

## Supported Output Formats

| Format | Driver | Notes |
|---|---|---|
| GeoTIFF | GTiff | Standard universal raster |
| COG | GTiff | Cloud-Optimized GeoTIFF |
| PNG | PNG | Lossless, visualization |
| JPEG | JPEG | Lossy, small file size |
| NetCDF | netCDF | Scientific multidimensional |
| HFA | HFA | Erdas Imagine |
| ENVI | ENVI | Hyperspectral remote sensing |
| VRT | VRT | GDAL Virtual Format |
| GeoPackage | GPKG | OGC raster/vector container |
| WebP | WEBP | Modern high-compression |
| Geospatial PDF | PDF | Georeferenced PDF |
| JPEG2000 | JP2OpenJPEG | Wavelet compression |
| BMP | BMP | Windows Bitmap |

---

## Download & Install

GeoConvert is distributed as a standalone installer — **no Python or GDAL installation required**.

Head to the [Releases](../../releases) page and download the package for your OS:

| Platform | File | Notes |
|---|---|---|
| Windows | `GeoConvert-x.x.x-setup.exe` | Windows 10/11 64-bit |
| macOS | `GeoConvert-x.x.x.dmg` | macOS 12 Monterey+ (Apple Silicon & Intel) |
| Debian / Ubuntu | `geoconvert_x.x.x_amd64.deb` | Ubuntu 22.04+, Debian 11+ |
| Fedora / RHEL | `geoconvert-x.x.x.x86_64.rpm` | Fedora 38+, RHEL 8+ |

### Windows
Double-click the `.exe` installer and follow the setup wizard.

### macOS
Open the `.dmg` file, drag **GeoConvert** into your **Applications** folder, then launch it from there.

> **Note:** On first launch, macOS may warn that the app is from an unidentified developer. Go to **System Settings → Privacy & Security** and click **Open Anyway**.

### Debian / Ubuntu
```bash
sudo dpkg -i geoconvert_x.x.x_amd64.deb
```

### Fedora / RHEL
```bash
sudo rpm -i geoconvert-x.x.x.x86_64.rpm
# or with dnf:
sudo dnf install geoconvert-x.x.x.x86_64.rpm
```

---

## For Developers

If you want to run GeoConvert from source or contribute to the project:

### Requirements

- Python 3.10+
- GDAL 3.x (system library — see below)

### Installing GDAL

**macOS (Homebrew):**
```bash
brew install gdal
pip install gdal==$(gdal-config --version)
```

**Ubuntu / Debian:**
```bash
sudo apt-get install gdal-bin libgdal-dev
pip install gdal==$(gdal-config --version)
```

**Windows:**
Download the GDAL wheel from [GIS Internals](https://www.gisinternals.com/) or use [OSGeo4W](https://trac.osgeo.org/osgeo4w/).

### Running from source

```bash
git clone https://github.com/your-username/geoconvert.git
cd geoconvert
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python gui.py
```

---

## Project Structure

```
geoconvert/
├── gui.py              # Main application entry point
├── converter/
│   ├── __init__.py
│   ├── core.py         # GDAL conversion logic
│   ├── formats.py      # Supported format definitions
│   └── utils.py        # Validation and helpers
├── requirements.txt
└── LICENSE
```

---

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

Copyright 2026 HOUIZOT Lénaïc

---

---

# Version française

**GeoConvert** est une application de bureau pour convertir des images raster géospatiales via GDAL, avec une interface moderne construite avec CustomTkinter.

> 🇬🇧 [English version above](#geoconvert)

---

## Fonctionnalités

- Conversion de rasters géospatiaux vers plus de 13 formats (GeoTIFF, COG, PNG, JPEG, NetCDF, GPKG, WebP, PDF, JPEG2000, et plus)
- Traitement par lot — conversion de dossiers entiers en une seule fois
- Bascule thème clair / sombre avec mémorisation de la préférence
- Interface en français 🇫🇷 / anglais 🇬🇧 avec mémorisation de la langue
- Basé sur GDAL pour des conversions géospatiales fiables et précises

## Formats d'entrée supportés

`.jp2` `.j2k` `.tif` `.tiff` `.ecw` `.img` `.nc` `.png` `.jpg` `.ntf` `.nitf` `.hdf` `.h5` `.vrt` `.dem` `.asc`

## Formats de sortie supportés

| Format | Driver | Notes |
|---|---|---|
| GeoTIFF | GTiff | Raster universel standard |
| COG | GTiff | GeoTIFF optimisé pour le cloud |
| PNG | PNG | Sans perte, visualisation |
| JPEG | JPEG | Compression avec perte, léger |
| NetCDF | netCDF | Format scientifique multidimensionnel |
| HFA | HFA | Erdas Imagine |
| ENVI | ENVI | Télédétection hyperspectrale |
| VRT | VRT | Format virtuel GDAL |
| GeoPackage | GPKG | Conteneur OGC raster/vecteur |
| WebP | WEBP | Compression moderne haute performance |
| PDF géospatial | PDF | PDF géoréférencé |
| JPEG2000 | JP2OpenJPEG | Compression par ondelettes |
| BMP | BMP | Windows Bitmap |

---

## Téléchargement & Installation

GeoConvert est distribué sous forme d'installeur autonome — **aucune installation de Python ou GDAL requise**.

Rendez-vous sur la page [Releases](../../releases) et téléchargez le paquet correspondant à votre système :

| Plateforme | Fichier | Notes |
|---|---|---|
| Windows | `GeoConvert-x.x.x-setup.exe` | Windows 10/11 64-bit |
| macOS | `GeoConvert-x.x.x.dmg` | macOS 12 Monterey+ (Apple Silicon & Intel) |
| Debian / Ubuntu | `geoconvert_x.x.x_amd64.deb` | Ubuntu 22.04+, Debian 11+ |
| Fedora / RHEL | `geoconvert-x.x.x.x86_64.rpm` | Fedora 38+, RHEL 8+ |

### Windows
Double-cliquer sur l'installeur `.exe` et suivre l'assistant.

### macOS
Ouvrir le fichier `.dmg`, glisser **GeoConvert** dans le dossier **Applications**, puis le lancer depuis là.

> **Note :** Au premier lancement, macOS peut afficher un avertissement sur un développeur non identifié. Aller dans **Réglages Système → Confidentialité & Sécurité** et cliquer sur **Ouvrir quand même**.

### Debian / Ubuntu
```bash
sudo dpkg -i geoconvert_x.x.x_amd64.deb
```

### Fedora / RHEL
```bash
sudo rpm -i geoconvert-x.x.x.x86_64.rpm
# ou avec dnf :
sudo dnf install geoconvert-x.x.x.x86_64.rpm
```

---

## Pour les développeurs

Pour lancer GeoConvert depuis les sources ou contribuer au projet :

### Prérequis

- Python 3.10+
- GDAL 3.x (bibliothèque système — voir ci-dessous)

### Installer GDAL

**macOS (Homebrew) :**
```bash
brew install gdal
pip install gdal==$(gdal-config --version)
```

**Ubuntu / Debian :**
```bash
sudo apt-get install gdal-bin libgdal-dev
pip install gdal==$(gdal-config --version)
```

**Windows :**
Télécharger le wheel GDAL depuis [GIS Internals](https://www.gisinternals.com/) ou utiliser [OSGeo4W](https://trac.osgeo.org/osgeo4w/).

### Lancer depuis les sources

```bash
git clone https://github.com/your-username/geoconvert.git
cd geoconvert
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
pip install -r requirements.txt
python gui.py
```

---

## Structure du projet

```
geoconvert/
├── gui.py              # Point d'entrée de l'application
├── converter/
│   ├── __init__.py
│   ├── core.py         # Logique de conversion GDAL
│   ├── formats.py      # Définition des formats supportés
│   └── utils.py        # Validation et utilitaires
├── requirements.txt
└── LICENSE
```

---

## Licence

Apache License 2.0 — voir [LICENSE](LICENSE) pour les détails.

Copyright 2026 HOUIZOT Lénaïc
