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

# Bank of commonly used EPSG codes
# Format: list of dictionaries

EPSG_BANK = [
    # ---- Global Systems ----
    {"code": 4326, "name": "WGS 84", "desc": "WGS 84 GPS System (Lat/Lon)"},
    {"code": 3857, "name": "WGS 84 / Pseudo-Mercator", "desc": "Web Mercator (Google Maps, OSM)"},
    {"code": 3395, "name": "WGS 84 / World Mercator", "desc": "World Mercator (naval/general use)"},
    {"code": 3785, "name": "Popular Visualisation CRS", "desc": "Old Web Mercator (Deprecated, equiv. 3857)"},
    {"code": 900913, "name": "Google Maps Global Mercator", "desc": "Old Web Mercator code (non-standard)"},

    # ---- Ellipsoids / Basic Geographics ----
    {"code": 4258, "name": "ETRS89", "desc": "Geographical Europe (Lat/Lon)"},
    {"code": 4269, "name": "NAD83", "desc": "Geographical North America (Lat/Lon)"},
    {"code": 4267, "name": "NAD27", "desc": "North America (Old system Lat/Lon)"},
    {"code": 4152, "name": "NAD83(HARN)", "desc": "Geographical North America (High precision)"},
    {"code": 4618, "name": "SAD69", "desc": "Geographical South America (Lat/Lon)"},
    {"code": 4674, "name": "SIRGAS 2000", "desc": "Geographical Latin America (Lat/Lon)"},
    {"code": 4283, "name": "GDA94", "desc": "Geographical Australia (Lat/Lon)"},
    {"code": 4008, "name": "Clarke 1866", "desc": "Clarke 1866 Ellipsoid"},
    {"code": 4978, "name": "WGS 84 (Geocentric)", "desc": "WGS 84 Geocentric (internal X, Y, Z)"},

    # ---- Trans-national European Systems ----
    {"code": 3035, "name": "ETRS89 / LAEA Europe", "desc": "Europe (Lambert Azimuthal Equal Area - Statistics)"},
    {"code": 3034, "name": "ETRS89 / LCC Europe", "desc": "Europe (Lambert Conformal Conic)"},
    {"code": 25830, "name": "ETRS89 / UTM zone 30N", "desc": "Western Europe (Spain, UK, West France)"},
    {"code": 25831, "name": "ETRS89 / UTM zone 31N", "desc": "Central Western Europe (France, Benelux)"},
    {"code": 25832, "name": "ETRS89 / UTM zone 32N", "desc": "Central Europe (East France, Germany, Italy)"},
    {"code": 25833, "name": "ETRS89 / UTM zone 33N", "desc": "Eastern Europe (Scandinavia, East Italy)"},

    # ---- France (Mainland and Overseas) ----
    {"code": 2154, "name": "RGF93 / Lambert-93", "desc": "Mainland France (official national)"},
    {"code": 27572, "name": "NTF (Paris) / Lambert zone II", "desc": "Old Mainland France system (Extended Lambert 2)"},
    {"code": 27571, "name": "NTF (Paris) / Lambert zone I", "desc": "Old North France system"},
    {"code": 27573, "name": "NTF (Paris) / Lambert zone III", "desc": "Old South France system"},
    {"code": 27574, "name": "NTF (Paris) / Lambert zone IV", "desc": "Old Corsica system"},

    # Conic Conformal (9 French zones)
    {"code": 3942, "name": "RGF93 / CC42", "desc": "Conic Conformal zone 1 (Corsica/Extreme South, Lat=42)"},
    {"code": 3943, "name": "RGF93 / CC43", "desc": "Conic Conformal zone 2 (South, Lat=43)"},
    {"code": 3944, "name": "RGF93 / CC44", "desc": "Conic Conformal zone 3 (Toulouse/Marseille, Lat=44)"},
    {"code": 3945, "name": "RGF93 / CC45", "desc": "Conic Conformal zone 4 (Bordeaux/Grenoble, Lat=45)"},
    {"code": 3946, "name": "RGF93 / CC46", "desc": "Conic Conformal zone 5 (La Rochelle/Lyon, Lat=46)"},
    {"code": 3947, "name": "RGF93 / CC47", "desc": "Conic Conformal zone 6 (Nantes/Dijon, Lat=47)"},
    {"code": 3948, "name": "RGF93 / CC48", "desc": "Conic Conformal zone 7 (Paris/Rennes, Lat=48)"},
    {"code": 3949, "name": "RGF93 / CC49", "desc": "Conic Conformal zone 8 (Rouen/Metz, Lat=49)"},
    {"code": 3950, "name": "RGF93 / CC50", "desc": "Conic Conformal zone 9 (Lille/North, Lat=50)"},

    # Other French geographic zones
    {"code": 2972, "name": "RGAF09 / UTM zone 20N", "desc": "French Antilles (Guadeloupe, Martinique)"},
    {"code": 2975, "name": "RGR92 / UTM zone 40S", "desc": "La Réunion"},
    {"code": 2970, "name": "CSG67 / UTM zone 11N", "desc": "French Guiana"},
    {"code": 2980, "name": "RGSPM06 / UTM zone 21N", "desc": "Saint-Pierre-et-Miquelon"},
    {"code": 3296, "name": "RGPF / UTM zone 5S", "desc": "Polynesia (Marquesas)"},
    {"code": 3297, "name": "RGPF / UTM zone 6S", "desc": "Polynesia (Tahiti/Society)"},

    # ---- United Kingdom & Ireland ----
    {"code": 27700, "name": "OSGB36 / British National Grid", "desc": "UK / Great Britain"},
    {"code": 29902, "name": "TM65 / Irish Grid", "desc": "Ireland (Old system)"},
    {"code": 2157, "name": "IRENET95 / Irish Transverse Mercator", "desc": "Ireland (Modern system)"},

    # ---- Switzerland & Benelux ----
    {"code": 2056, "name": "CH1903+ / LV95", "desc": "Switzerland (New official system)"},
    {"code": 21781, "name": "CH1903 / LV03", "desc": "Switzerland (Old system)"},
    {"code": 31370, "name": "Belge 1972 / Belgian Lambert 72", "desc": "Belgium"},
    {"code": 28992, "name": "Amersfoort / RD New", "desc": "Netherlands (Rijksdriehoekstelsel)"},

    # ---- Global UTM (WGS 84 North Band) ----
    {"code": 32601, "name": "WGS 84 / UTM zone 1N", "desc": "UTM Zone 1 North"},
    {"code": 32610, "name": "WGS 84 / UTM zone 10N", "desc": "UTM Zone 10 North (USA West Coast)"},
    {"code": 32618, "name": "WGS 84 / UTM zone 18N", "desc": "UTM Zone 18 North (USA East Coast)"},
    {"code": 32630, "name": "WGS 84 / UTM zone 30N", "desc": "UTM Zone 30 North (Spain/UK/West France)"},
    {"code": 32631, "name": "WGS 84 / UTM zone 31N", "desc": "UTM Zone 31 North (France/North Sea)"},
    {"code": 32632, "name": "WGS 84 / UTM zone 32N", "desc": "UTM Zone 32 North (Germany/Italy)"},
    {"code": 32633, "name": "WGS 84 / UTM zone 33N", "desc": "UTM Zone 33 North (Scandinavia/Eastern Europe)"},
    {"code": 32640, "name": "WGS 84 / UTM zone 40N", "desc": "UTM Zone 40 North (Middle East)"},
    {"code": 32650, "name": "WGS 84 / UTM zone 50N", "desc": "UTM Zone 50 North (China/East Asia)"},

    # ---- Global UTM (WGS 84 South Band) ----
    {"code": 32719, "name": "WGS 84 / UTM zone 19S", "desc": "UTM Zone 19 South (Chile/Argentina)"},
    {"code": 32720, "name": "WGS 84 / UTM zone 20S", "desc": "UTM Zone 20 South (Brazil, Bolivia)"},
    {"code": 32722, "name": "WGS 84 / UTM zone 22S", "desc": "UTM Zone 22 South (South Brazil)"},
    {"code": 32736, "name": "WGS 84 / UTM zone 36S", "desc": "UTM Zone 36 South (Madagascar, South Africa)"},
    {"code": 32740, "name": "WGS 84 / UTM zone 40S", "desc": "UTM Zone 40 South (Indian Ocean/La Réunion WGS84)"},
    {"code": 32750, "name": "WGS 84 / UTM zone 50S", "desc": "UTM Zone 50 South (West Australia)"},
    {"code": 32755, "name": "WGS 84 / UTM zone 55S", "desc": "UTM Zone 55 South (East Australia)"},

    # ---- Additional Spherical Systems (Pseudo) ----
    {"code": 102100, "name": "Web Mercator Auxiliary Sphere", "desc": "Web Mercator variant (Esri ArcGIS systems)"},
    {"code": 3413, "name": "WGS 84 / NSIDC Sea Ice Polar Stereographic North", "desc": "Arctic North Pole (Glaciology)"},
    {"code": 3976, "name": "WGS 84 / NSIDC Sea Ice Polar Stereographic South", "desc": "Antarctic South Pole (Glaciology)"},

    # ---- Other National Specific Systems ----
    {"code": 31467, "name": "DHDN / 3-degree Gauss-Kruger zone 3", "desc": "Germany (Historic Gauss-Kruger system)"},
    {"code": 3006, "name": "SWEREF99 TM", "desc": "Sweden"},
    {"code": 3395, "name": "WGS 84 / World Mercator", "desc": "Standard Mercator for global navigation"},
    {"code": 5650, "name": "DGN95 / Indonesia TM zone 50", "desc": "Indonesia"},
    {"code": 6668, "name": "JGD2011", "desc": "Geographical Japan (Lat/Lon)"},
]

def search_epsg(query: str) -> list[dict]:
    """Search the EPSG bank by code, name, or keyword."""
    query = query.lower()
    results = []
    for item in EPSG_BANK:
        if query in str(item["code"]) or query in item["name"].lower() or query in item["desc"].lower():
            results.append(item)
    return results
