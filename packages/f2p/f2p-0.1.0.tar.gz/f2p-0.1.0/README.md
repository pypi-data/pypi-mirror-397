# fits2physical

FITS 2D/3D physical size analyzer with smart diagonal measurement.

## Installation

```bash
pip install git+https://github.com/siwakotiutsav/fits2physical.git

```

#Usage

import f2p
df = f2p.analyze("path/to/fits/file.fits", distance_mpc=give your distance in Mpc)

print(df)
