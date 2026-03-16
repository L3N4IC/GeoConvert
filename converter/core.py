"""
GDAL conversion logic: ImageConverter class.
"""

import os
import time
import tempfile
from pathlib import Path
from typing import Optional, Callable, Union, Tuple

from .formats import SUPPORTED_FORMATS
from .utils import setup_logger, build_output_path, get_human_size

logger = setup_logger()


class ConversionResult:
    """Result of a conversion."""

    def __init__(
        self,
        src: Path,
        dst: Path,
        success: bool,
        elapsed: float,
        error: Optional[str] = None,
    ):
        self.src = src
        self.dst = dst
        self.success = success
        self.elapsed = elapsed
        self.error = error

    def __repr__(self):
        status = "✓" if self.success else "✗"
        return f"[{status}] {self.src.name} → {self.dst.name} ({self.elapsed:.2f}s)"


class ImageConverter:
    """
    Raster image converter via GDAL.

    Supports: JPEG2000 → GeoTIFF, COG, PNG, JPEG, NetCDF, HFA, ENVI, VRT, GPKG, BMP
    and any (input_format, output_format) pair supported by GDAL.
    """

    def __init__(self):
        from osgeo import gdal
        gdal.UseExceptions()
        self._check_gdal()

    @staticmethod
    def _check_gdal():
        """Verifies that GDAL is available."""
        try:
            from osgeo import gdal  # noqa
        except ImportError:
            raise ImportError(
                "GDAL is not installed.\n"
                "Install it with:\n"
                "  conda install -c conda-forge gdal\n"
                "or:\n"
                "  pip install GDAL==$(gdal-config --version)"
            )

    def get_info(self, filepath: str) -> dict:
        """
        Retrieves geospatial metadata from a raster file.
        Returns a dictionary with key information.
        """
        from osgeo import gdal

        ds = gdal.Open(str(filepath))
        if ds is None:
            raise ValueError(f"GDAL cannot open: {filepath}")

        gt = ds.GetGeoTransform()
        proj = ds.GetProjection()
        driver = ds.GetDriver().LongName

        # Geographical extent
        xmin = gt[0]
        ymax = gt[3]
        xmax = xmin + gt[1] * ds.RasterXSize
        ymin = ymax + gt[5] * ds.RasterYSize

        # Per-band info
        bands_info = []
        for i in range(1, ds.RasterCount + 1):
            band = ds.GetRasterBand(i)
            bands_info.append({
                "index": i,
                "dtype": gdal.GetDataTypeName(band.DataType),
                "nodata": band.GetNoDataValue(),
                "color_interp": gdal.GetColorInterpretationName(band.GetColorInterpretation()),
            })

        info = {
            "driver": driver,
            "width": ds.RasterXSize,
            "height": ds.RasterYSize,
            "bands": ds.RasterCount,
            "bands_info": bands_info,
            "projection": proj[:80] + "…" if proj and len(proj) > 80 else (proj or "Not defined"),
            "geotransform": gt,
            "bbox": {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax},
            "pixel_size": (abs(gt[1]), abs(gt[5])),
            "file_size": os.path.getsize(filepath),
            "metadata": ds.GetMetadata(),
        }

        ds = None  # Explicit closure
        return info

    def get_extent(self, src_path: Union[str, Path]) -> Optional[dict]:
        """
        Retrieves the spatial extent (bounding box) of a raster.
        
        Returns:
            dict: {ulx, uly, lrx, lry} or None if error
        """
        from osgeo import gdal
        try:
            ds = gdal.Open(str(src_path))
            if not ds:
                return None
            
            gt = ds.GetGeoTransform()
            if not gt:
                return None
            
            width = ds.RasterXSize
            height = ds.RasterYSize
            
            ulx = gt[0]
            uly = gt[3]
            lrx = ulx + width * gt[1] + height * gt[2]
            lry = uly + width * gt[4] + height * gt[5]
            
            ds = None
            return {
                "ulx": round(ulx, 6),
                "uly": round(uly, 6),
                "lrx": round(lrx, 6),
                "lry": round(lry, 6)
            }
        except Exception:
            return None

    def get_thumbnail(self, src_path: Union[str, Path], max_size: int = 800) -> Optional[Tuple[str, dict]]:
        """
        Generates a thumbnail (JPEG) of the raster for visual selection.
        
        Returns:
            Tuple[str, dict]: (Temporary file path, extent info)
        """
        from osgeo import gdal
        try:
            ds = gdal.Open(str(src_path))
            if not ds:
                return None
            
            # Calculate dimensions to fit in max_size
            w, h = ds.RasterXSize, ds.RasterYSize
            scale = min(max_size / w, max_size / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Create a temporary file
            fd, tmp_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            
            # Extract a thumbnail with GDAL
            # Force JPEG format and resize
            opts = gdal.TranslateOptions(
                format="JPEG",
                width=new_w,
                height=new_h,
                resampleAlg=gdal.GRIORA_Bilinear
            )
            
            gdal.Translate(tmp_path, ds, options=opts)
            
            extent = self.get_extent(src_path)
            ds = None
            
            return tmp_path, extent
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None

    def get_mosaic_thumbnail(self, file_paths: list[Union[str, Path]], max_size: int = 800) -> Optional[Tuple[str, dict]]:
        """
        Generates a thumbnail (JPEG) of the global extent of multiple rasters via a VRT.
        """
        from osgeo import gdal
        vrt_path = None
        try:
            # Create a temporary VRT
            fd_vrt, vrt_path = tempfile.mkstemp(suffix=".vrt")
            os.close(fd_vrt)
            
            vrt_ds = gdal.BuildVRT(vrt_path, [str(f) for f in file_paths])
            if not vrt_ds:
                return None
                
            # Calculate dimensions
            w, h = vrt_ds.RasterXSize, vrt_ds.RasterYSize
            scale = min(max_size / w, max_size / h)
            new_w, new_h = int(w * scale), int(h * scale)
            
            # Create the final JPEG
            fd_jpg, tmp_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd_jpg)
            
            opts = gdal.TranslateOptions(
                format="JPEG",
                width=new_w,
                height=new_h,
                resampleAlg=gdal.GRIORA_Bilinear
            )
            
            gdal.Translate(tmp_path, vrt_ds, options=opts)
            
            # Global extent
            geo = vrt_ds.GetGeoTransform()
            extent = {
                "ulx": geo[0],
                "uly": geo[3],
                "lrx": geo[0] + geo[1] * vrt_ds.RasterXSize,
                "lry": geo[3] + geo[5] * vrt_ds.RasterYSize
            }
            
            vrt_ds = None
            if vrt_path and os.path.exists(vrt_path):
                os.remove(vrt_path)
                
            return tmp_path, extent
        except Exception as e:
            logger.error(f"Error generating mosaic thumbnail: {e}")
            if vrt_path and os.path.exists(vrt_path):
                try: os.remove(vrt_path)
                except: pass
            return None

    def convert(
        self,
        src: Union[str, list[str]],
        dst: Optional[str] = None,
        format_name: str = "GeoTIFF",
        output_dir: Optional[str] = None,
        epsg: Optional[int] = None,
        creation_options: Optional[list] = None,
        progress_callback: Optional[Callable] = None,
        build_overviews: bool = False,
        nodata: Optional[float] = None,
        output_type: Optional[str] = None,
        use_multithread: bool = False,
        quality: int = 85,
        resampling: str = "Nearest (Speed)",
        clip_box: Optional[list[float]] = None,
    ) -> ConversionResult:
        """
        Converts a raster file to the specified format.
        """
        from osgeo import gdal

        gdal.UseExceptions()

        # Output path construction
        if isinstance(src, list):
            # Mosaic Mode: src is a list of paths
            first_src = Path(src[0])
            src_path = first_src.parent / (first_src.stem + "_mosaic")
        else:
            # Single File Mode: src is a path
            src_path = Path(src)
            
        t0 = time.time()

        # Format check
        if format_name not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Format '{format_name}' not supported.\n"
                f"Available formats: {', '.join(SUPPORTED_FORMATS.keys())}"
            )

        fmt = SUPPORTED_FORMATS[format_name]
        is_cog = fmt.get("cog", False)

        # Final path construction
        if dst:
            dst_path = Path(dst)
            dst_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            if isinstance(src, list):
                # Uses the pseudo src_path (1st file name + _mosaic)
                dst_path = build_output_path(src_path, output_dir, fmt["extension"])
            else:
                dst_path = build_output_path(src_path, output_dir, fmt["extension"])

        # Options GDAL
        opts = list(creation_options) if creation_options is not None else list(fmt["creation_options"])
        
        # Multithreading pour GTiff/COG
        if use_multithread and fmt["driver"] == "GTiff":
            if not any("NUM_THREADS" in opt for opt in opts):
                opts.append("NUM_THREADS=ALL_CPUS")
        
        # BigTIFF optimization: default block size 512x512
        if fmt["driver"] == "GTiff":
            if not any("BLOCKXSIZE" in opt for opt in opts):
                opts.append("BLOCKXSIZE=512")
            if not any("BLOCKYSIZE" in opt for opt in opts):
                opts.append("BLOCKYSIZE=512")

        # BigTIFF safety for mosaics (forced as often > 4GB)
        if isinstance(src, list) and fmt["driver"] == "GTiff":
            if not any("BIGTIFF" in opt for opt in opts):
                opts.append("BIGTIFF=YES")

        # Quality management
        if fmt["driver"] == "GTiff":
            if any("COMPRESS=JPEG" in opt for opt in opts):
                if not any("JPEG_QUALITY" in opt for opt in opts):
                    opts.append(f"JPEG_QUALITY={quality}")
        elif fmt["driver"] in ["JPEG", "JP2OpenJPEG", "WEBP"]:
            # Replace eventual default quality
            opts = [o for o in opts if not o.startswith("QUALITY=")]
            opts.append(f"QUALITY={quality}")

        # Resampling mapping
        res_map = {
            "Nearest (Speed)": "near",
            "Bilinear": "bilinear",
            "Cubic": "cubic",
            "Lanczos (Quality)": "lanczos"
        }
        res_alg = res_map.get(resampling, "near")

        try:
            # 1. Open source (or VRT)
            if isinstance(src, list):
                vrt_kwargs = {}
                if nodata is not None:
                    vrt_kwargs["srcNodata"] = nodata
                    vrt_kwargs["VRTNodata"] = nodata
                vrt_opts = gdal.BuildVRTOptions(**vrt_kwargs)
                src_ds = gdal.BuildVRT("", src, options=vrt_opts)
                if src_ds is None:
                    raise ValueError(f"VRT construction failed ({len(src)} files)")
            else:
                src_ds = gdal.Open(str(src_path))
                if src_ds is None:
                    raise ValueError(f"Cannot open: {src_path}")

            # 2. Prepare transformation options
            warp_kwargs = {}
            translate_kwargs = {}
            
            # Output type
            if output_type:
                gdal_type = gdal.GetDataTypeByName(output_type)
                warp_kwargs["outputType"] = gdal_type
                translate_kwargs["outputType"] = gdal_type
                if output_type == "Byte":
                    first_band = src_ds.GetRasterBand(1)
                    if first_band and first_band.DataType != gdal.GDT_Byte:
                        translate_kwargs["scaleParams"] = [[]]
                        warp_kwargs["extraOptions"] = ["-scale"]

            # 3. Working path
            # If several steps are needed (e.g., Warp + COG), use a temporary file
            current_ds = src_ds
            temp_files = []

            # --- STEP A: Reprojection (Warp) ---
            if epsg:
                from osgeo import osr
                warped_clip = None
                if clip_box:
                    try:
                        src_wkt = current_ds.GetProjection()
                        if src_wkt:
                            s_srs = osr.SpatialReference()
                            s_srs.ImportFromWkt(src_wkt)
                            s_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                            d_srs = osr.SpatialReference()
                            d_srs.ImportFromEPSG(epsg)
                            d_srs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
                            
                            if not s_srs.IsSame(d_srs):
                                ct = osr.CoordinateTransformation(s_srs, d_srs)
                                ul = ct.TransformPoint(clip_box[0], clip_box[1])
                                lr = ct.TransformPoint(clip_box[2], clip_box[3])
                                warped_clip = [ul[0], ul[1], lr[0], lr[1]]
                                logger.info(f"   Transformed clip (EPSG:{epsg}): {warped_clip}")
                            else:
                                warped_clip = clip_box
                        else:
                            warped_clip = clip_box
                    except Exception as e:
                        logger.warning(f"   Error transforming clip: {e}")
                        warped_clip = clip_box

                # If it's the only step and not COG, write directly to dst_path
                inter_warp_path = str(dst_path) + ".warp.tmp.tif" if is_cog or (not is_cog and build_overviews and fmt["driver"] != "GTiff") else str(dst_path)
                
                warp_opts = gdal.WarpOptions(
                    dstSRS=f"EPSG:{epsg}",
                    format="GTiff" if is_cog else fmt["driver"],
                    creationOptions=opts if not is_cog else ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512"],
                    callback=progress_callback if not is_cog else None,
                    multithread=use_multithread,
                    resampleAlg=res_alg,
                    outputBounds=[warped_clip[0], warped_clip[3], warped_clip[2], warped_clip[1]] if warped_clip else None,
                    **warp_kwargs
                )
                
                logger.info(f"   Warping... -> {os.path.basename(inter_warp_path)}")
                warp_ds = gdal.Warp(inter_warp_path, current_ds, options=warp_opts)
                if warp_ds is None:
                    raise RuntimeError("Warp failed")
                
                if inter_warp_path != str(dst_path):
                    temp_files.append(inter_warp_path)
                    current_ds = warp_ds
                else:
                    # Finished
                    warp_ds.FlushCache()
                    if build_overviews:
                        warp_ds.BuildOverviews(res_alg.upper(), [2, 4, 8, 16, 32, 64])
                    warp_ds = None
                    elapsed = time.time() - t0
                    return ConversionResult(src_path, dst_path, True, elapsed)

            # --- STEP B: COG or Standard Translation ---
            if is_cog:
                # 1. Intermediate copy with overviews
                cog_tmp = str(dst_path) + ".cog.tmp.tif"
                temp_files.append(cog_tmp)
                
                cog_creation = ["COMPRESS=LZW", "TILED=YES", "BIGTIFF=YES", "BLOCKXSIZE=512", "BLOCKYSIZE=512"]
                if use_multithread:
                    cog_creation.append("NUM_THREADS=ALL_CPUS")
                
                trans_opts = gdal.TranslateOptions(
                    format="GTiff",
                    creationOptions=cog_creation,
                    callback=progress_callback,
                    resampleAlg=res_alg,
                    projWin=clip_box if not epsg else None, # Already clipped by Warp if epsg
                    **translate_kwargs
                )
                logger.info("   Generating COG structure...")
                tmp_ds = gdal.Translate(cog_tmp, current_ds, options=trans_opts)
                if tmp_ds is None:
                    raise RuntimeError("COG structure failed")
                
                tmp_ds.BuildOverviews(res_alg.upper(), [2, 4, 8, 16, 32])
                tmp_ds.FlushCache()
                tmp_ds = None
                
                # 2. Final COG copy
                final_ds_in = gdal.Open(cog_tmp)
                trans_opts_final = gdal.TranslateOptions(
                    format="GTiff",
                    creationOptions=opts,
                    callback=progress_callback,
                    resampleAlg=res_alg
                )
                result_ds = gdal.Translate(str(dst_path), final_ds_in, options=trans_opts_final)
                final_ds_in = None
                
            else:
                # Translation Standard
                trans_opts = gdal.TranslateOptions(
                    format=fmt["driver"],
                    creationOptions=opts,
                    callback=progress_callback,
                    resampleAlg=res_alg,
                    projWin=clip_box if not epsg else None,
                    **translate_kwargs
                )
                logger.info(f"   Writing to {dst_path.name}...")
                result_ds = gdal.Translate(str(dst_path), current_ds, options=trans_opts)
                if result_ds and build_overviews:
                    result_ds.BuildOverviews(res_alg.upper(), [2, 4, 8, 16, 32, 64])

            if result_ds is None:
                raise RuntimeError("Final operation failed")

            result_ds.FlushCache()
            result_ds = None
            
            # Cleanup
            src_ds = None
            current_ds = None
            for tmp in temp_files:
                try:
                    if os.path.exists(tmp):
                        os.remove(tmp)
                except:
                    pass

            elapsed = time.time() - t0
            return ConversionResult(src_path, dst_path, True, elapsed)

        except Exception as exc:
            elapsed = time.time() - t0
            logger.error(f"Fatal conversion error: {exc}")
            return ConversionResult(src_path, dst_path, False, elapsed, error=str(exc))

    def batch_convert(
        self,
        files: list,
        format_name: str = "GeoTIFF",
        output_dir: Optional[str] = None,
        epsg: Optional[int] = None,
        creation_options: Optional[list] = None,
        on_progress: Optional[Callable] = None,
    ) -> list[ConversionResult]:
        """
        Converts a list of raster files.

        Args:
            files:            List of source paths (str or Path)
            format_name:      Output format
            output_dir:       Output directory
            epsg:             Target EPSG for reprojection
            creation_options: GDAL options
            on_progress:      Callback(index, total, result) called after each file

        Returns:
            List of ConversionResult
        """
        results = []
        total = len(files)

        for i, f in enumerate(files):
            result = self.convert(
                src=str(f),
                format_name=format_name,
                output_dir=output_dir,
                epsg=epsg,
                creation_options=creation_options,
            )
            results.append(result)
            if on_progress:
                on_progress(i + 1, total, result)

        return results
