#!/usr/bin/env python

# Shifts negative elevations in ESRI ASCII files, as downloaded from GEBCO
# (General Bathymetric Chart of the Oceans) https://www.gebco.net/ , to positive
# values, so that they can be represented in PNG format (RGB image values are
# positive only) to be read by Ignition Gazebo heightmaps. Ignition Gazebo
# heightmaps currently only support PNG files, not DEM / GeoTIFF.
#
# Usage:
#   $ python shift_negative_elevation.py <infile.asc> <outfile.png>
#

import sys

import numpy as np

from PIL import Image


def parse_esri_ascii(path):

  print('Loading %s' % (path))

  data = np.zeros(0)
  next_row = 0

  # Read file line by line
  with open(path, 'ro') as asc:

    nrows = 0
    ncols = 0

    # Read header lines
    # First line tells us number of columns
    line = asc.readline()
    line_sp = line.split()

    # Technically, we don't need such tight assumptions and constraints. Size of
    # data need not to be known, if we reallocate the space for the numpy array
    # after reading every row, but that is very inefficient.
    if line.startswith('ncols') and len(line_sp) > 0:
      try:
        ncols = int(line_sp[1])
      except ValueError:
        print('ncols %s is an invalid integer' % line_sp[1])
        return data
    else:
      print('First row in header does not start with ncols. Unexpected data format.')
      return data

    # Second line tells us number of rows
    line = asc.readline()
    line_sp = line.split()
    if line.startswith('nrows') and len(line_sp) > 0:
      try:
        nrows = int(line_sp[1])
      except ValueError:
        print('nrows %s is an invalid integer' % line_sp[1])
        return data
    else:
      print('First row in header does not start with ncols. Unexpected data format.')
      return data

    # Reallocate to the right size
    data = np.zeros((nrows, ncols))

    # Read the remaining lines
    while line:

      # A data line starts with a space
      if line.startswith(' '):
        try:
          # Tokenize row into cells, convert each cell to an integer
          line_numeric = [int(word) for word in line.split()]
        except ValueError:
          print('Could not convert %s to an integer. Skipping line' % word)
          continue

        # Populate matrix
        data[next_row] = np.array(line_numeric)
        next_row += 1

      # Read the next line
      line = asc.readline()

  return data


def shift_negative_values(data):

  min_val = data.flatten().min()
  print('Minimum value: %g (shift by this value to retrieve true heights)' % min_val)
  print('Maximum value: %g' % data.flatten().max())

  if min_val < 0:
    print ('Shifting everything up by the minimum value.')

    # Shift everything by the minimum value
    data -= min_val

  min_val = data.flatten().min()
  print('New minimum value: %g' % min_val)

  return data


# Normalize values to be between [0, 255] for outputting to RGB image
def normalize_to_rgb(data):

  scaling_factor = data.flatten().max() - data.flatten().min()

  if scaling_factor == 0:
    print('Max value in data is 0. Did you shift negative values to non-negative? Doing nothing.')
    return data, scaling_factor
  else:
    data = data / scaling_factor * 255

    print('Scaling factor: %g (stretch RGB values by this factor to retrieve true heights)' % (
      scaling_factor))

    print('Min value after normalizing: %g' % data.flatten().min())
    print('Max value after normalizing: %g' % data.flatten().max())

    return data, scaling_factor


def write_png(data, path):

  # Round to nearest integer
  data_rounded = data.round().astype(np.uint8)

  im = Image.fromarray(data_rounded)
  im.save(path, 'png')


def main():

  if len(sys.argv) < 3:
    print('Usage: python shift_negative_elevation.py <infile.asc> <outfile.png>')
    return

  # Read ESRI ASCII file
  data = parse_esri_ascii(sys.argv[1])
  if data.shape[0] == 0:
    print('Error in reading. Aborting.')
    return
  else:
    print('Read matrix of size %d x %d' % (data.shape[0], data.shape[1]))

  # Shift negative values in the data to non-negative
  data = shift_negative_values(data)

  # Normalize to [0, 255] for RGB image output
  data, scaling_factor = normalize_to_rgb(data)

  # Write the new data to file
  write_png(data, sys.argv[2])


if __name__ == '__main__':
  main()
