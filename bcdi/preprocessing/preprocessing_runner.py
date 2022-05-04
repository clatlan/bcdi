# -*- coding: utf-8 -*-

# BCDI: tools for pre(post)-processing Bragg coherent X-ray diffraction imaging data
#   (c) 07/2017-06/2019 : CNRS UMR 7344 IM2NP
#   (c) 07/2019-05/2021 : DESY PHOTON SCIENCE
#       authors:
#         Jerome Carnis, jerome.carnis@esrf.fr
"""Main runner for BCDI data preprocessing, before phase retrieval."""

try:
    import hdf5plugin  # for P10, should be imported before h5py or PyTables
except ModuleNotFoundError:
    pass

import logging
from typing import Any, Dict

from bcdi.preprocessing.process_scan import process_scan
from bcdi.utils.parameters import PreprocessingChecker
import bcdi.utils.utilities as util

logger = logging.getLogger(__name__)


def run(prm: Dict[str, Any]) -> None:
    """
    Run the postprocessing.

    :param prm: the parsed parameters
    """
    prm = PreprocessingChecker(
        initial_params=prm,
        default_values={
            "actuators": None,
            "align_q": True,
            "backend": "Qt5Agg",
            "background_file": None,
            "background_plot": 0.5,
            "beam_direction": [1, 0, 0],
            "bin_during_loading": False,
            "bragg_peak": None,
            "center_fft": "skip",
            "centering_method": "max_com",
            "colormap": "turbo",
            "comment": "",
            "custom_monitor": None,
            "custom_motors": None,
            "custom_images": None,
            "custom_scan": False,
            "data_dir": None,
            "debug": False,
            "detector_distance": None,
            "direct_beam": None,
            "dirbeam_detector_angles": None,
            "energy": None,
            "fill_value_mask": 0,
            "fix_size": None,
            "flag_interact": True,
            "flatfield_file": None,
            "frames_pattern": None,
            "hotpixels_file": None,
            "inplane_angle": None,
            "interpolation_method": "linearization",
            "is_series": False,
            "linearity_func": None,
            "mask_zero_event": False,
            "median_filter": "skip",
            "median_filter_order": 7,
            "normalize_flux": False,
            "offset_inplane": 0,
            "outofplane_angle": None,
            "pad_size": None,
            "photon_filter": "loading",
            "photon_threshold": 0,
            "preprocessing_binning": [1, 1, 1],
            "ref_axis_q": "y",
            "reload_orthogonal": False,
            "reload_previous": False,
            "sample_inplane": [1, 0, 0],
            "sample_offsets": None,
            "sample_outofplane": [0, 0, 1],
            "save_as_int": False,
            "save_rawdata": False,
            "save_to_mat": False,
            "save_to_npz": True,
            "save_to_vti": False,
        },
        match_length_params=(
            "data_dir",
            "sample_name",
            "save_dir",
            "specfile_name",
            "template_imagefile",
        ),
        required_params=(
            "beamline",
            "detector",
            "phasing_binning",
            "rocking_angle",
            "root_folder",
            "sample_name",
            "scans",
            "use_rawdata",
        ),
    ).check_config()

    ############################
    # start looping over scans #
    ############################
    nb_scans = len(prm["scans"])
    for scan_idx in range(nb_scans):
        result = process_scan(scan_idx=scan_idx, prm=prm)
        util.move_log(result)
