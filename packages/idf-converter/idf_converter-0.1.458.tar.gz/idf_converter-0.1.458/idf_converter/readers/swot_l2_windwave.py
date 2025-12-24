# vim: ts=4:sts=4:sw=4
#
# @date 2025-09-15
#
# Copyright (C) 2016-2025 OceanDataLab
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
"""

import os
import numpy
import numpy.typing
import typing
import logging
import netCDF4
import idf_converter.lib
from idf_converter.lib.types import ReaderResult, TransformsList

logger = logging.getLogger(__name__)

DATA_MODEL = 'SWATH'

MASK_BITS = {"suspect_beam_used": 3,
             "suspect_less_than_nine_beams": 4,
             "suspect_rain_likely": 5,
             "suspect_pixel_used": 7,
             "suspect_num_pt_avg": 8,
             "suspect_karin_telem": 9,
             "suspect_orbit_control": 10,
             "suspect_sc_event_flag": 11,
             "suspect_tvp_qual": 12,
             "suspect_volumetric_corr": 13,
             "degraded_beam_used": 17,
             "degraded_large_attitude": 18,
             "degraded_karin_ifft_overflow": 19,
             "bad_karin_telem": 24,
             "bad_very_large_attitude": 25,
             "bad_outside_of_range": 29,
             "degraded": 30
             }


class InputPathMissing(IOError):
    """Error raised when the "path" input option has not been provided by the
    user."""
    pass


def build_gcps(lon: numpy.typing.NDArray,
               lat: numpy.typing.NDArray,
               subsampling: typing.Sequence[int]
               ) -> typing.Dict[str, numpy.typing.NDArray]:
    """"""
    if numpy.ma.is_masked(lon) or numpy.ma.is_masked(lat):
        logger.warn('Some lon and/or lat is masked')

    lon_shape = numpy.array(numpy.shape(lon))  # lat should have the same shape
    x = subsampling[1]
    ngcps_s = numpy.ceil(lon_shape / subsampling).astype('int')
    ngcps_d = numpy.ceil(lon_shape / subsampling).astype('int')

    len_ac = lon_shape[1] - 1
    mid_ac = int(len_ac / 2)
    gcppix = numpy.array([0 * x, 10 * x, 20 * x, 30 * x, mid_ac - 1,
                          mid_ac, mid_ac + 1, mid_ac + 10 * x, mid_ac + 20 * x,
                          mid_ac + 30 * x, len_ac])
    gcppix_s = gcppix
    ngcps_s[1] = len(gcppix_s)
    ngcps_d[1] = len(gcppix)

    gcplin_out = numpy.linspace(0, lon_shape[0] - 1,
                                num=ngcps_d[0]).round().astype('int32')
    gcplin_in = numpy.linspace(0, lon_shape[0] - 1,
                               num=ngcps_s[0]).round().astype('int32')

    gcps = {'geoloc_row': gcplin_in, 'geoloc_cell': gcppix,
            'input_row': gcplin_in, 'input_cell': gcppix,
            'output_row': gcplin_out, 'output_cell': gcppix}
    return gcps


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',)
    out = ''
    return ('\n'.join(inp), '\n'.join(out))


def get_beam_mask(quality_flags: numpy.typing.NDArray,
                  ) -> numpy.typing.NDArray:
    """"""
    list_invalid = ["suspect_rain_likely", "suspect_pixel_used",
                    "suspect_num_pt_avg", "bad_karin_telem",
                    "bad_very_large_attitude",  # "bad_outside_of_range",
                    "degraded",]
    # list_invalid = list_invalid + list_suspect
    # Invalidate if any of these flags is on
    off_flags = numpy.uint(0)
    for invalid in list_invalid:
        off_flags = off_flags + numpy.uint(1 << MASK_BITS[invalid])
    mask = (numpy.bitwise_and(quality_flags, off_flags) > 0)
    return mask


def read_data(input_opts: typing.Dict[str, typing.Any],
              output_opts: typing.Dict[str, typing.Any]
              ) -> typing.Iterator[ReaderResult]:
    """Read input file, extract data and metadata, store them in a Granule
    object then prepare formatting instructions to finalize the conversion to
    IDF format.

    Parameters
    ----------
    input_opts: dict
        Options and information related to input data
    output_opts: dict
        Options and information related to formatting and serialization to IDF
        format

    Returns
    -------
    tuple(dict, dict, idf_converter.lib.Granule, list)
        A tuple which contains four elements:

        - the input_options :obj:dict passed to this method

        - the output_options :obj:dict passed to this method

        - the :obj:`idf_converter.lib.Granule` where the extracted information
          has been stored

        - a :obj:list of :obj:dict describing the formatting operations that
          the converter must perform before serializing the result in IDF
          format
    """
    variables = {'swh_karin': {'name': 'swh_karin',
                               'long_name': ('Significant Wave Height from '
                                             'SWOT'),
                               'units': 'm',
                               'valid_min': 0.0,
                               'valid_max': 8.0,
                               'options': {}},
                 'wind_speed_karin': {'name': 'wind_speed_karin',
                                      'long_name': ('Wind Speed from SWOT'),
                                      'units': 'm.s-1',
                                      'valid_min': 0.0,
                                      'valid_max': 25.4,
                                      'options': {}},
                 'rain_flag': {'name': 'rain_flag',
                               'long_name': 'Rain flag',
                               'units': '',
                               'valid_min': 0,
                               'valid_max': 5,
                               'options': {}},
                 }

    _var_ids = input_opts.get('variables', None)
    if _var_ids is None:
        var_ids = list(variables.keys())
    else:
        var_ids = [x.strip() for x in _var_ids.split(',')
                   if 0 < len(x.strip())]

    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)
    idf_converter.lib.apply_global_overrides(input_opts, granule)
    idf_converter.lib.apply_var_overrides(input_opts, granule)

    maskable_channels = [_ for _ in var_ids if 'flag' not in _]
    granule.vars = {_: variables[_] for _ in var_ids if _ in variables.keys()}
    channels = list(granule.vars.keys())

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    subsampling = [40, 1]
    resolution = 2000

    f_handler = netCDF4.Dataset(input_path, 'r')

    # Extract time coordinates information
    t = f_handler.variables['time'][:]
    t_unit = f_handler.variables['time'].units
    t_mask = numpy.ma.getmaskarray(t)
    if t_mask.all():
        logger.warning(f'No valid time in "{input_path}"')
        f_handler.close()
        raise idf_converter.lib.EarlyExit()

    # Extract geo coordinates information
    lon = f_handler.variables['longitude'][:, :]
    lat = f_handler.variables['latitude'][:, :]

    # Handle longitude continuity
    dlon = lon[1:, :] - lon[:-1, :]
    if 180.0 <= numpy.max(numpy.abs(dlon)):
        lon[numpy.where(lon < 0.0)] = lon[numpy.where(lon < 0.0)] + 360.0

    idf_converter.lib.extract_global_attributes(f_handler, input_opts, granule)

    valid_t_ind = numpy.where(~t_mask)[0]
    time = t[valid_t_ind]
    lon = lon[valid_t_ind, :]
    lat = lat[valid_t_ind, :]
    for var_id in channels:
        idf_converter.lib.extract_variable_attributes(f_handler, var_id,
                                                      granule)
        values = f_handler.variables[var_id][valid_t_ind, :]
        if var_id in ('wind_speed_karin', 'swh_karin'):
            # Apply SWH Qual mask as wind speed mask is not good enough
            # To be reevaluated in future version
            mask = get_beam_mask(f_handler['swh_karin_qual'][valid_t_ind, :])
            values[mask] = numpy.nan
        granule.vars[var_id]['array'] = values

    qf_mask = numpy.full(numpy.shape(lat), numpy.False_, dtype=bool)
    if 'dynamic_ice_flag' in f_handler.variables.keys():
        # "no_ice probable_ice ice no_data": 0UB, 1UB, 2UB, 3UB
        qf = f_handler.variables['dynamic_ice_flag'][valid_t_ind, :]
        ice_mask = (qf > 1)
        qf_mask = (qf_mask | ice_mask)
    if 'rain_flag' in f_handler.variables.keys():
        # "no_rain probable_rain rain no_data": 0UB, 1UB, 2UB, 3UB
        # Do not flag rain as flag is incorrect
        # To be reevaluated in future version
        qf = f_handler.variables['rain_flag'][valid_t_ind, :]
        rain_mask = (qf >= 4)
        qf_mask = (qf_mask | rain_mask)
    if 'ancillary_surface_classification_flag' in f_handler.variables.keys():
        # open_ocean land continental_water aquatic_vegetation
        # continental_ice_snow floating_ice salted_basin
        # 0UB, 1UB, 2UB, 3UB, 4UB, 5UB, 6UB
        flag_name = 'ancillary_surface_classification_flag'
        qf = f_handler.variables[flag_name][valid_t_ind, :]
        surf_mask = ((qf == 1) | (qf == 3) | (qf == 4))
        qf_mask = (qf_mask | surf_mask)
    f_handler.close()

    nrow, ncell = numpy.shape(lon)
    granule.dims['row'] = nrow
    granule.dims['cell'] = ncell

    granule.vars['lat'] = {'array': lat,
                           'units': 'degrees_north',
                           'datatype': lat.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': lon,
                           'units': 'degrees_east',
                           'datatype': lon.dtype,
                           'options': {}}

    # Format time information
    start_dt = netCDF4.num2date(time[0], t_unit)
    stop_dt = netCDF4.num2date(time[-1], t_unit)

    granule_filename = os.path.basename(input_path)
    granule_name, _ = os.path.splitext(granule_filename)

    granule.meta['idf_granule_id'] = f'{granule_name}'
    granule.meta['granule_id'] = f'{granule_name}'
    granule.meta['idf_subsampling_factor'] = 0
    granule.meta['idf_spatial_resolution'] = resolution
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['time_coverage_start'] = start_dt
    granule.meta['time_coverage_end'] = stop_dt

    # Add transforms
    transforms: TransformsList = []

    if qf_mask.any():
        transforms.append(('static_common_mask', {'targets': maskable_channels,
                                                  'mask': qf_mask}))

    output_opts['__export'] = channels
    output_opts['gcp_distribution'] = build_gcps(lon, lat,
                                                 subsampling=subsampling)
    input_opts['geoloc_at_pixel_center'] = 'true'
    yield input_opts, output_opts, granule, transforms
