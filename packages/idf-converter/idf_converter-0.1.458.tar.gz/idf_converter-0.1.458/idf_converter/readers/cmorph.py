# vim: ts=4:sts=4:sw=4
#
# @date 2020-01-07
#
# This file is part of IDF converter, a set of tools to convert satellite,
# in-situ and numerical model data into Intermediary Data Format, making them
# compatible with the SEAScope application.
#
# Copyright (C) 2014-2022 OceanDataLab
#
# IDF converter is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# IDF converter is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IDF converter. If not, see <https://www.gnu.org/licenses/>.

"""
"""

import os
import gzip
import numpy
import struct
import typing
import logging
import datetime
import idf_converter.lib
from idf_converter.lib.types import InputOptions, OutputOptions, ReaderResult

logger = logging.getLogger(__name__)

DATA_MODEL = 'GRID_LATLON'


class InputPathMissing(Exception):
    """Error raised when the "path" input option has not been specified by the
    user."""
    pass


class InvalidRateThreshold(ValueError):
    """Error raised when the "mask-if-rate-below" output option is set to a
    value that cannot be converted to a float number."""
    def __init__(self, value: str) -> None:
        """"""
        self.value = value


class SpatioTemporalResolutionNotSupported(Exception):
    """Error raised when the size of the input file does not match any of the
    supported combination of dimensions/resolutions."""
    pass


def help() -> typing.Tuple[str, str]:
    """Describe options supported by this reader.

    Returns
    -------
    str
        Description of the supported options
    """
    inp = ('    path\tPath of the input file',
           )
    out = ('    include-mean-precipitation\tSet to yes|true|1 if the mean '
           'amount of precipitation (i.e. precipitation rate × temporal '
           'extent) must be included in the output IDF file as the "rain" '
           'variable',
           '    mask-if-rate-below\tPixels with a precipitation rate strictly '
           'below this value will be masked (default: 0.00001)'
           )
    return ('\n'.join(inp), '\t'.join(out))


def read_data(input_opts: InputOptions,
              output_opts: OutputOptions
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
    idf_version = output_opts.get('idf_version', '1.0')
    granule = idf_converter.lib.create_granule(idf_version, DATA_MODEL)

    _input_path = input_opts.get('path', None)
    if _input_path is None:
        raise InputPathMissing()
    input_path = os.path.normpath(_input_path)

    include_amount = False
    _include_amount = output_opts.get('include-mean-precipitation', False)
    if _include_amount is not False:
        include_amount = _include_amount.lower() in ('yes', 'true', '1')

    _rate_threshold = output_opts.get('mask-if-rate-below', '0.00001')
    try:
        rate_threshold = float(_rate_threshold)
    except ValueError:
        logger.error('The "mask-if-rate-below" option expects a float value,'
                     f'but "{_rate_threshold}" cannot be converted to float')
        raise InvalidRateThreshold(_rate_threshold)

    granule_fname = os.path.basename(input_path)

    # Read variables
    if input_path.endswith('.gz'):
        _granule_name, _ = os.path.splitext(granule_fname)
        with gzip.open(input_path, 'rb') as f:
            file_content = f.read()
    else:
        # decompressed binary data have no extension
        _granule_name = granule_fname
        with open(input_path, 'rb') as f:
            file_content = f.read()

    _, granule_date = _granule_name.rsplit('_', 1)  # %Y%m%d
    _, version, process, _ = _granule_name.split('_', 3)

    content_length = len(file_content)
    if (4948 * 1649 * 2 * 4) == content_length:
        # 8km, 30min, hourly files
        lon_size = 4948
        lat_size = 1649
        time_size = 2
        temporal_extent = datetime.timedelta(minutes=30)
        spatial_res_m = 8000
        dlon = 0.072756669
        dlat = 0.072771376
        dtime_base = datetime.datetime.strptime(granule_date, '%Y%m%d%H')
        amount_factor = 0.5
    elif (1440 * 480 * 8 * 4) == content_length:
        # 0.25deg, 3h, daily files
        lon_size = 1440
        lat_size = 480
        time_size = 8
        temporal_extent = datetime.timedelta(hours=3)
        spatial_res_m = 27500  # approx. 0.25deg
        dlon = 0.25
        dlat = 0.25
        dtime_base = datetime.datetime.strptime(granule_date, '%Y%m%d')
        amount_factor = 3
    else:
        raise SpatioTemporalResolutionNotSupported

    fmt = '<{}f'.format(lon_size * lat_size * time_size)
    _all_data = struct.unpack(fmt, file_content)
    all_data = numpy.reshape(_all_data, (time_size, lat_size, lon_size,))
    all_data = numpy.roll(all_data, numpy.floor(lon_size / 2).astype(int),
                          axis=2)

    input_opts['geoloc_at_pixel_center'] = 'no'
    dim1 = numpy.array([-60.0 + i * dlat for i in range(0, lat_size)])
    dim2 = numpy.array([-180.0 + i * dlon for i in range(0, lon_size)])

    granule.vars['lat'] = {'array': dim1,
                           'units': 'degrees_north',
                           'datatype': dim1.dtype,
                           'options': {}}
    granule.vars['lon'] = {'array': dim2,
                           'units': 'degrees_east',
                           'datatype': dim2.dtype,
                           'options': {}}

    granule.dims['lat'] = dim1.size
    granule.dims['lon'] = dim2.size

    granule.vars['rain_rate'] = {'name': 'rain_rate',
                                 'units': 'mm/hr',
                                 'valid_min': 0.0,
                                 'valid_max': 1.0,
                                 'options': {}}
    if include_amount is True:
        granule.vars['rain'] = {'name': 'rain',
                                'units': 'mm',
                                'valid_min': 0.0,
                                'valid_max': 1.0,
                                'options': {}}

    granule.meta['idf_spatial_resolution'] = spatial_res_m
    granule.meta['idf_spatial_resolution_units'] = 'm'
    granule.meta['institution'] = 'NOAA CPC'

    for i in range(0, time_size):
        start_dt = dtime_base + i * temporal_extent
        stop_dt = start_dt + temporal_extent

        granule_name = '{}_{:02d}{:02d}'.format(_granule_name, start_dt.hour,
                                                start_dt.minute)

        granule.meta['idf_granule_id'] = granule_name
        granule.meta['time_coverage_start'] = start_dt
        granule.meta['time_coverage_end'] = stop_dt

        _data = all_data[i, :, :]
        mask = (_data < rate_threshold)  # nodata is -999
        if mask.all():
            logger.warning(f'No valid data found for {granule_name}')
            continue

        valid_data = _data[numpy.where(~mask)]
        vmin: float = numpy.nanmin(valid_data)
        vmax: float = numpy.nanmax(valid_data)

        granule.vars['rain_rate']['array'] = _data
        granule.vars['rain_rate']['valid_min'] = vmin
        granule.vars['rain_rate']['valid_max'] = vmax

        if include_amount is True:
            # input contains 3-hourly rate, we want the amount of precipitation
            # during these 3 hours
            granule.vars['rain']['array'] = _data * amount_factor
            granule.vars['rain']['valid_min'] = vmin * amount_factor
            granule.vars['rain']['valid_max'] = vmax * amount_factor

        transforms = []

        # Mask where there are no precipitations
        targets = ['rain_rate']
        if include_amount is True:
            targets.append('rain')
        transforms.append(('static_common_mask', {'targets': targets,
                                                  'mask': mask}))

        output_opts['__export'] = targets

        yield input_opts, output_opts, granule, transforms
