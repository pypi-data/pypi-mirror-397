import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.wcs import WCS
import astropy.units as u
from scipy.spatial import ConvexHull
from itertools import combinations
from math import atan2, cos, sin
import warnings
from astropy.wcs import FITSFixedWarning

warnings.simplefilter("ignore", FITSFixedWarning)

def analyze(fits_path, distance_mpc, show_plot=True):
    """
    Analyze a FITS file to compute length, breadth, and smart diagonal.

    Parameters
    ----------
    fits_path : str
        Path to FITS file.
    distance_mpc : float
        Distance to source in Mpc.
    show_plot : bool
        Whether to show plot.

    Returns
    -------
    df : pd.DataFrame
        DataFrame with Pixels, Angular, and Physical measurements.
    """
    distance = distance_mpc * u.Mpc

    # Load FITS
    with fits.open(fits_path) as hdul:
        for hdu in hdul:
            if hdu.data is not None:
                data = hdu.data
                header = hdu.header
                break

    ndim = data.ndim
    if ndim not in (2,3):
        raise ValueError("Only 2D images or 3D cubes are supported.")

    if ndim == 3:
        image = np.nanmean(data, axis=0)
    else:
        image = data

    # WCS & pixel scale
    wcs = WCS(header, naxis=2)
    psm = wcs.pixel_scale_matrix
    pix_x = np.sqrt(psm[0,0]**2 + psm[0,1]**2) * u.deg
    pix_y = np.sqrt(psm[1,0]**2 + psm[1,1]**2) * u.deg
    pix_x = pix_x.to(u.arcsec)
    pix_y = pix_y.to(u.arcsec)

    # Data pixels
    mask = np.isfinite(image)
    ys, xs = np.where(mask)
    coords = np.column_stack((xs, ys))
    if len(coords)<2:
        raise ValueError("Not enough valid pixels to measure.")

    # Rotated minimum area rectangle
    def min_area_rectangle(points):
        min_area = np.inf
        best_rect = None
        hull = ConvexHull(points)
        hull_points = points[hull.vertices]
        for i in range(len(hull_points)):
            p1 = hull_points[i]
            p2 = hull_points[(i+1)%len(hull_points)]
            edge = p2 - p1
            angle = -atan2(edge[1], edge[0])
            rot = np.array([[cos(angle), -sin(angle)],
                            [sin(angle), cos(angle)]])
            rot_points = (rot @ hull_points.T).T
            min_x, max_x = rot_points[:,0].min(), rot_points[:,0].max()
            min_y, max_y = rot_points[:,1].min(), rot_points[:,1].max()
            area = (max_x - min_x)*(max_y - min_y)
            if area < min_area:
                min_area = area
                best_rect = {'angle': angle, 'rot': rot,
                             'min_x': min_x, 'max_x': max_x,
                             'min_y': min_y, 'max_y': max_y,
                             'hull_points': hull_points}
        return best_rect

    rect = min_area_rectangle(coords)
    corners_rot = np.array([
        [rect['min_x'], rect['min_y']],
        [rect['max_x'], rect['min_y']],
        [rect['max_x'], rect['max_y']],
        [rect['min_x'], rect['max_y']]
    ])
    corners = (np.linalg.inv(rect['rot']) @ corners_rot.T).T

    # Smart diagonal
    hull_points = rect['hull_points']
    max_dist = 0
    for p1, p2 in combinations(hull_points, 2):
        d = np.linalg.norm(p2-p1)
        if d > max_dist:
            max_dist = d
            diag_p1, diag_p2 = p1, p2
    diag_pix = max_dist

    # Length & breadth
    edges = [np.linalg.norm(corners[i]-corners[(i+1)%4]) for i in range(4)]
    length_pix = max(edges)
    breadth_pix = min(edges)

    length_ang = length_pix * pix_x
    breadth_ang = breadth_pix * pix_y
    diagonal_ang = diag_pix * pix_x

    length_phys = (length_ang*distance).to(u.pc, equivalencies=u.dimensionless_angles())
    breadth_phys = (breadth_ang*distance).to(u.pc, equivalencies=u.dimensionless_angles())
    diagonal_phys = (diagonal_ang*distance).to(u.pc, equivalencies=u.dimensionless_angles())

    df = pd.DataFrame({
        "Quantity": ["Length","Breadth","Diagonal"],
        "Pixels": [length_pix, breadth_pix, diag_pix],
        "Angular": [length_ang, breadth_ang, diagonal_ang],
        "Physical": [length_phys, breadth_phys, diagonal_phys]
    })

    # Plot
    if show_plot:
        fig, ax = plt.subplots(figsize=(8,8))
        ax.imshow(image, origin="lower", cmap="gray")
        rect_x = list(corners[:,0])+[corners[0,0]]
        rect_y = list(corners[:,1])+[corners[0,1]]
        ax.plot(rect_x, rect_y, color="blue", linewidth=2, label="Data footprint")
        ax.plot([diag_p1[0], diag_p2[0]], [diag_p1[1], diag_p2[1]], color="red", linewidth=2, label="Diagonal")
        ax.set_title("Data footprint with smart diagonal")
        ax.set_xlabel("X pixel")
        ax.set_ylabel("Y pixel")
        ax.legend()
        plt.show()

    return df
