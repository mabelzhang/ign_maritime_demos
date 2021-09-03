## Dependencies
```
pip install Pillow
pip install numpy
```

## To generate a negative-shifted and normalized PNG from ESRI ASCII

At the time of writing, Ignition only supports heightmaps by PNG, and the
heightmap dimensions must be a square sized 2^n + 1.
Since PNG files can only contain values in the range of [0, 255], two issues
need to be worked around.
- True heights are lost in the RGB image format
- Negative heights in ocean bathymetry cannot be represented

To work around that, the following script shifts negative heights to
non-negative, and outputs the scaling factor used to normalize all values to the
range of [0, 255].
Two values are printed:
1. The minimum height, which is a negative depth, in the original bathymetry data. This is needed to compute the z in `<heightmap><pos>`
2. The scaling factor. This is needed to compute the z in `<heightmap><size>`

Generate a shifted and normalized PNG from an ESRI ASCII file:
```
python shift_negative_elevation.py <infile.asc> <outfile.png>
```
where the ESRI ASCII file is downloaded from GEBCO https://www.gebco.net/ .

An example pair of input and output files are in `models/Monterey_Bay_130x142_n37s36w-122e-122/materials/textures/`.
The input is `gebco/gebco_2021_n37.07611083984375_s36.48284912109375_w-122.24212646484376_e-121.69830322265626.asc`.
The output is `heightmap_shifted.png`.

## To compute values in the SDF model file

To compute the full `<heightmap><size>` in meters, x and y need to be derived
from the grid cell resolution (15 arc-degrees for GEBCO 2021 data) and the
latitutde of the data.
A tool such as [OpenDEM Arc2Meters](https://www.opendem.info/arc2meters.html) can help you do that.
That will give you the approximate grid cell size in meters.

To derive a proportional z for `<pos>` and `<size>`, divide the grid cell size
in meters by the true heights printed from `shift_negative_elevation.py`.

For `<pos>`, use the minimum height, which is the value by which the data has
been shifted by the script.

For `<size>`, use the scaling factor, which is the full (max - min) range of
original heights, by which the data was normalized to [0, 255].

## To try out the world

Run from the root of this repository, so that `models` path is in the Ignition
environment variable, for Ignition to find the model:
```
export IGN_GAZEBO_RESOURCE_PATH=`pwd`/models
```

The computations outlined above have been done in this SDF file so that x, y,
and z are approximately proportional:
```
ign gazebo models/montereyBay130x142.sdf 
```
