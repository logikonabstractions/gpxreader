import gpxpy
import numpy as np
import scipy.signal
from matplotlib import pyplot as plt
from scipy.ndimage.filters import uniform_filter1d

from utils import get_distance_from_gpxpoint, get_elev_from_gpxpoint, compute_grade_along_course


def plot(filepath=None, gpxpoints_list=None, plotname='plot_normalized'):
    print("Plotting data.... ")
    if gpxpoints_list:      # prioritize gpx file over a path 
        GPXPoints = gpxpoints_list
    else:
        gpx_file = open(filepath, 'r')
        gpx = gpxpy.parse(gpx_file)
        GPXPoints = gpx.tracks[0].segments[0].points

    distances = []
    elevations = []
    # GPXPoints = gpxpoints
    print(f"Plotting with {len(gpxpoints_list)} pts...")
    for idx, pt in enumerate(GPXPoints):
        gpxpoint1 = pt
        gpxpoint2 = GPXPoints[idx+1] if idx+1 < len(GPXPoints) else GPXPoints[idx]
        pt.distance_meters = get_distance_from_gpxpoint(gpxpoint1, gpxpoint2)
        elev = get_elev_from_gpxpoint(gpxpoint1, gpxpoint2)
        elevations.append(elev)
        distances.append(int(pt.distance_meters))


    cumul_distance = np.cumsum(np.abs(distances))
    for idx, pt in enumerate(GPXPoints):
        pt.dist_cumul_meters = cumul_distance[idx]
    cumul_elev = np.cumsum(elevations)
    grade = compute_grade_along_course(GPXPoints)              # TODO: compute the avg. local grade for each pt so we can plot it as well,like avg(100) pts after? sliding window kind of algo?
    normalized_elev = cumul_elev/max(cumul_elev)
    normalized_grade = grade / max(grade)
    
    if plotname == 'plot_normalized':
        plot_normalized(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade)
    elif plotname == "plot_raw_grade":
        plot_raw_grade(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade)
    elif plotname == "plot_dev":
        plot_dev(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade, gpxpoints_list)


def plot_raw_grade(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade, gpxpoints_list=None):
    
    # average out elevations changes
    smooth_elev = uniform_filter1d(gpxpoints_list, size=AVERAGING_WINDOWS_SIZE)

    
    plt.plot(cumul_distance , smooth_elev)
    plt.ylabel(f" Grade. Max value: {max(grade) * 100}% \n Max elevation: {max(cumul_elev)}")
    plt.xlabel(f"Distance (km)")
    plt.hlines(0, 0, 100, colors='black')
    plt.show()


def plot_normalized(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade, elevation=None):
    plt.plot(cumul_distance , normalized_elev)

    plt.ylabel(f"Normalized avg grade. Max value: {max(grade) * 100}% \n Max elevation: {max(cumul_elev)}")
    plt.xlabel(f"Distance (km)")
    plt.hlines(0, 0, 100, colors='black')
    plt.show()


def plot_dev(cumul_distance, cumul_elev, grade, normalized_elev, normalized_grade, gpxpoints_list=None):
    elevations = [x.elevation for x in gpxpoints_list]
    # windows = [50, 100, 200, 400, 600]
    windows = [500, 550, 600, 700, 800]
    windows = [500]
    for window in windows:
        smooth_elev = uniform_filter1d(elevations, size=window)
        plt.plot(cumul_distance , smooth_elev)

    # find local grade min/max
    mini = scipy.signal.argrelextrema(smooth_elev, np.less_equal, order=200)
    maxi = scipy.signal.argrelextrema(smooth_elev, np.greater_equal, order=200)
    
    plt.ylabel(f" Grade. Max value: {max(grade) * 100}% \n Max elevation: {max(cumul_elev)}")
    plt.xlabel(f"Distance (km)")
    plt.hlines(0, 0, 100, colors='black')
    
    for idx, idx_min in enumerate(mini):
        plt.scatter(cumul_distance[idx_min], smooth_elev[idx_min], marker='o')
    for idx, idx_max in enumerate(maxi):
        plt.scatter(cumul_distance[idx_max], smooth_elev[idx_max], marker='x')

    plt.show()
    # now let's try to plot our avg. grade betwee each min/max
    minmax_idx = sorted(list(idx_min) + list(idx_max))
    grades = []
    print(f"dist cumul, elev start: {gpxpoints_list[0].dist_cumul_meters} {gpxpoints_list[0].elevation}")
    grades += [0 for i in range(0, minmax_idx[0])]
    for i, idx in enumerate(minmax_idx):
        # get dist
        if i+1<len(minmax_idx):
            dist = get_distance_from_gpxpoint(gpxpoints_list[idx], gpxpoints_list[minmax_idx[i+1]])
            elev_chg = get_elev_from_gpxpoint(gpxpoints_list[idx], gpxpoints_list[minmax_idx[i+1]])
            grade = elev_chg/dist*100
            grade_section = [grade for i in range(idx, minmax_idx[i+1])]
            grades += grade_section
            print(f"dist cumul, elev: {gpxpoints_list[idx].dist_cumul_meters} {gpxpoints_list[idx].elevation}")
            
    print(f"dist cumul, elev last: {gpxpoints_list[-1].dist_cumul_meters} {gpxpoints_list[-1].elevation}")
    grades += [grade for i in range(0, minmax_idx[0])]
    x = [gpxpoints_list[i].dist_cumul_meters if i<len(gpxpoints_list) else gpxpoints_list[-1].dist_cumul_meters for i in range(0, len(grades))]
    grades = [grade if grade<30 else 30 for grade in grades]
    plt.scatter(np.array(x)/1000, grades, marker='.')
    plt.show()
    print(grades)