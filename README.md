Random maritime demos in Ignition Gazebo.

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

### Example

An example pair of input and output files are in `models/Monterey_Bay_130x142_n37s36w-122e-122/materials/textures/`.
The input is `gebco/gebco_2021_n37.07611083984375_s36.48284912109375_w-122.24212646484376_e-121.69830322265626.asc`.
The output is `heightmap_shifted.png`.

To satisfy the 2^n + 1 square dimensions requirement, the PNG image is then cropped in any image editing software, e.g. GIMP, to obtain `heightmap_shifted_square.png`.
In this case, it was resized to 129 x 129 pixels.

The true heights outputted from `shift_negative_elevation.py` were
```
$ python scripts/shift_negative_elevation.py models/Monterey_Bay_130x142_n37s36w-122e-122/materials/textures/gebco/gebco_2021_n37.07611083984375_s36.48284912109375_w-122.24212646484376_e-121.69830322265626.asc models/Monterey_Bay_130x142_n37s36w-122e-122/materials/textures/heightmap_shifted.png
Loading models/Monterey_Bay_130x142_n37s36w-122e-122/materials/textures/gebco/gebco_2021_n37.07611083984375_s36.48284912109375_w-122.24212646484376_e-121.69830322265626.asc
Read matrix of size 142 x 130
Minimum value: -6313 (shift by this value to retrieve true heights)
Shifting everything up by the minimum value.
New minimum value: 0
Scaling factor: 7146 (stretch RGB values by this factor to retrieve true heights)
Min value after normalizing: 0
Max value after normalizing: 255
```

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

### Example

Continuing from the example above, the z is computed as follows.

For simplicity, x and y in `<heightmap><size>` are set to the grid size of 129 x 129.
z needs to be computed such that it is proportional to x and y in terms of meters.

The data was obtained from latitude boundaries of north 37.07611083984375 to south 36.48284912109375.

Giving the mean latitude of 36.77945 and the GEBCO 2021 grid cell resolution of 15 arc-seconds to OpenDEM Arc2Meters, it computes the result of 370.8380759437494 m.
That is the approximate distance per grid cell.
It is approximate because only an average latitude is used to compute it.

z shift in `<pos>` is obtained by dividing the minimum height by the distance in meters:
```
-6313 / 370.8380759437494 = -17.023602508814623
```

z size in `<size>` is obtained by dividing the range in height (i.e. scaling factor used for normalization) by the distance in meters:
```
7146 / 370.8380759437494 = 19.26986591604456
```

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

For an exaggerated effect, scale up z in both `<pos>` and `<size>`.

z proportional to x and y:

![xyzProportional_1.png](https://github.com/mabelzhang/ign_maritime_demos/blob/master/models/Monterey_Bay_130x142_n37s36w-122e-122/thumbnails/xyzProportional_1.png)

![xyzProportional_2.png](https://github.com/mabelzhang/ign_maritime_demos/blob/master/models/Monterey_Bay_130x142_n37s36w-122e-122/thumbnails/xyzProportional_2.png)

z exaggerated 10 times:

Now I never want to be there.

![zExaggerated10x_1.png](https://github.com/mabelzhang/ign_maritime_demos/blob/master/models/Monterey_Bay_130x142_n37s36w-122e-122/thumbnails/zExaggerated10x_1.png)

![zExaggerated10x_2.png](https://github.com/mabelzhang/ign_maritime_demos/blob/master/models/Monterey_Bay_130x142_n37s36w-122e-122/thumbnails/zExaggerated10x_2.png)
