import gpxpy.gpx
import urllib
import geopy.distance
import numpy as np
import requests
import scipy.signal
from scipy.ndimage.filters import uniform_filter1d


ITERATIONS_PER_PRINT = 100      # each N pts we'll update hte graph & display new one
PICKLE_DUMPFILE = "gpxpoints.pick"
url = r'http://localhost:5000/v1/aster30m?'

SLIDING_WINDOW_SIZE = 300
AVERAGING_WINDOWS_SIZE = 500
AVERAGING_WINDOWS_SIZE_ELEVATION = 200

from matplotlib import pyplot as plt


def average_grade_section(gpxpoints):
    """ return the average grade for that section of the course.
        computed by: (elev[0] - elev[1]/distance_meters
    """
    dist = gpxpoints[-1].dist_cumul_meters - gpxpoints[0].dist_cumul_meters 
    elev_change_meters = gpxpoints[-1].elevation - gpxpoints[0].elevation 
    try:
        grade = elev_change_meters / dist
        return grade
    except ZeroDivisionError:
        print("zero div error.")
        return 0

def compute_grade_along_course(gpxpoints):
    """ compute the grade at each pt in course given a list of gpx points"""
   
    averaged_grades = []
    # for i in range(len(gpxpoints) - N + 1):
    for i in range(len(gpxpoints)):
        section_gpxpoints = gpxpoints[i: min(i + SLIDING_WINDOW_SIZE, len(gpxpoints)-1)]         # slice the window. for the last bit we just take whatever window we have left 
        avg_grade = average_grade_section(section_gpxpoints) if len(section_gpxpoints) > SLIDING_WINDOW_SIZE/2 else 0
        averaged_grades.append(avg_grade)

    win_dist_meters = gpxpoints[0].dist_cumul_meters, gpxpoints[AVERAGING_WINDOWS_SIZE].dist_cumul_meters
    print(f"Dist approx. between window ({AVERAGING_WINDOWS_SIZE} pts): {win_dist_meters}")
    averages = uniform_filter1d(averaged_grades, size=AVERAGING_WINDOWS_SIZE)
    return averages
    # return averaged_grades
    
def elevation_function(gpxpoints):
    """Query service using lat, lon. add the elevation values as a new column."""
    print("Adding elevation data to gpxpoints...")
    a=None
    processed_gpxpoints = []
    for idx, gpxpoint in enumerate(gpxpoints, start=1):
        # plot(gpxpoints_list=processed_gpxpoints) if idx%ITERATIONS_PER_PRINT == 0 else a == 1
        print(f"Crunched {idx} of {len(gpxpoints)}") if idx % ITERATIONS_PER_PRINT == 0 else a == 1
        params = {"locations":f"{gpxpoint.latitude},{gpxpoint.longitude}"}
        rqst_url = (url + urllib.parse.urlencode(params))
        result = requests.get(rqst_url)
        json_resp = result.json()
        elevation = json_resp['results'][0]['elevation']
        gpxpoint.elevation = elevation
        processed_gpxpoints.append(gpxpoint)
    return gpxpoints

def get_distance_from_gpxpoint(GPXPoint1, GPXPoint2):
    """ returns a distance given the details of the GPXPoint object, in meters"""
    pt1_coord = (GPXPoint1.latitude, GPXPoint1.longitude)
    pt2_coord = (GPXPoint2.latitude, GPXPoint2.longitude)
    distance =  geopy.distance.geodesic(pt2_coord, pt1_coord)
    return distance.meters


def get_elev_from_gpxpoint(GPXPoint1, GPXPoint2):
    """ returns a distance given the details of the GPXPoint object, in meters"""
    pt1_elev = GPXPoint1.elevation
    pt2_elev = GPXPoint2.elevation
    elev =  pt2_elev - pt1_elev
    return elev


def build_elevation_gpx(filepath):
    """ uses USGC api service to add elevation to a list of gpxpoints. returns a new .gpx file that update/includes elevation for eahc pt """
    print("Building list of gpxpoints object....")
    gpx_file = open(filepath, 'r')
    gpx = gpxpy.parse(gpx_file) 
    # GPXPoints = gpx.tracks[0].segments[0].points
    GPXPoints = gpx.tracks[0].segments[0].points
    gpxpoints_with_elevation = elevation_function(GPXPoints)
    return gpxpoints_with_elevation
    

# 
# def calc_attr_gpxpoints(GPXPoints):
#     """ computes stuff like grade etc... and adds it to gpxpoints for easy plotting"""
#     elevations = []
#     distances = []
#     for idx, pt in enumerate(GPXPoints):
#         gpxpoint1 = pt
#         gpxpoint2 = GPXPoints[idx+1] if idx+1 < len(GPXPoints) else GPXPoints[idx]
#         pt.distance_meters = get_distance_from_gpxpoint(gpxpoint1, gpxpoint2)
#         elev = get_elev_from_gpxpoint(gpxpoint1, gpxpoint2)
#         elevations.append(elev)
#         distances.append(int(pt.distance_meters))
#         
#         # need to compute each, and just + to the previous one, don't resum everything multiple times. 
#         pt.normalized_elev = cumul_elev/max(cumul_elev)
#         pt.normalized_grade = grade / max(grade)

    # 
    # cumul_distance = np.cumsum(np.abs(distances))
    # for idx, pt in enumerate(GPXPoints):
    #     pt.dist_cumul_meters = cumul_distance[idx]
    # cumul_elev = np.cumsum(elevations)
    # grade = compute_grade_along_course(GPXPoints)              # TODO: compute the avg. local grade for each pt so we can plot it as well,like avg(100) pts after? sliding window kind of algo?
    # normalized_elev = cumul_elev/max(cumul_elev)
    # normalized_grade = grade / max(grade)
    # return GPXPoints

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