import urllib
import pickle
import gpxpy
import requests
import utils


def build_elevation_gpx(filepath):
    """ uses USGC api service to add elevation to a list of gpxpoints. returns a new .gpx file that update/includes elevation for eahc pt """
    print("Building list of gpxpoints object....")
    gpx_file = open(filepath, 'r')
    gpx = gpxpy.parse(gpx_file) 
    # GPXPoints = gpx.tracks[0].segments[0].points
    GPXPoints = gpx.tracks[0].segments[0].points
    enhanced_gpxpoints = elevation_function(GPXPoints)
    return enhanced_gpxpoints


def elevation_function(gpxpoints):
    """Query service using lat, lon. add the elevation values as a new column."""
    print("Adding elevation data to gpxpoints...")
    a=None
    processed_gpxpoints = []
    for idx, gpxpoint in enumerate(gpxpoints, start=1):
        # plot(gpxpoints_list=processed_gpxpoints) if idx%ITERATIONS_PER_PRINT == 0 else a == 1
        print(f"Crunched {idx} of {len(gpxpoints)}") if idx % utils.CONFIGS["consts"]["ITERATIONS_PER_PRINT"] == 0 else a == 1
        params = {"locations":f"{gpxpoint.latitude},{gpxpoint.longitude}"}
        rqst_url = (utils.CONFIGS["consts"]["url"] + urllib.parse.urlencode(params))
        result = requests.get(rqst_url)
        json_resp = result.json()
        elevation = json_resp['results'][0]['elevation']
        gpxpoint.elevation = elevation
        processed_gpxpoints.append(gpxpoint)
    return gpxpoints


def pickle_new_gpxpoints(gpxpoints_to_pickle):
    print(f"Pickling new gpxpoints. {len(gpxpoints_to_pickle)} pts.")
    with open(f"{utils.CONFIGS['const']['PICKLE_DUMPFILE']}", mode='wb') as jsonfile:
        pickle.dump(gpxpoints_to_pickle, jsonfile)
    print(f"Done. ")