import geopy.distance
CONFIGS = None




def computed_gpxpoints_metrics(GPXPoints):
    """ compute metrics for gpxpoints & adds them as attributes. Metrics:
        * distance_meters
        * cumul_distance_meters
        * cumul_elevation
        * normalized_elev
        * normalized_grade
     """

    current_distance = 0
    current_elevation = 0
    max_relative_elev = get_max_relative_elevation(GPXPoints)
    GPXPoints[0].cumul_distance_meters = 0
    GPXPoints[0].cumul_elevation = 0
    GPXPoints[0].normalized_elevation = 0
    GPXPoints[0].normalized_grade = 0
    for idx, pt in enumerate(GPXPoints, start=1):
        # set points
        gpxpoint1 = pt
        gpxpoint2 = GPXPoints[idx]
        # compute distances
        dist = get_distance_from_gpxpoint(gpxpoint1, gpxpoint2)
        current_distance += dist
        pt.distance_meters = current_distance
        elev = get_elev_from_gpxpoint(gpxpoint1, gpxpoint2)
        pt.normalized_elevation = current_elevation / max_relative_elev
        pt.normalized_elevation = current_elevation / max_relative_elev

    avg_grades = compute_grade_along_course(GPXPoints)
    return GPXPoints

def get_max_relative_elevation(GPXPoints):
    max_abs_elev = max(pt.elevation for pt in GPXPoints)
    min_abs_elev = min(pt.elevation for pt in GPXPoints)
    return  max_abs_elev - min_abs_elev
    

def get_max_relative_grade(GPXPoints):
    max_abs_elev = max(pt.elevation for pt in GPXPoints)
    min_abs_elev = min(pt.elevation for pt in GPXPoints)
    return  max_abs_elev - min_abs_elev
    
    
    
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
    for i, pt in enumerate(gpxpoints):
        section_gpxpoints = gpxpoints[i: min(i + SLIDING_WINDOW_SIZE, len(gpxpoints)-1)]         # slice the window. for the last bit we just take whatever window we have left 
        avg_grade = average_grade_section(section_gpxpoints) if len(section_gpxpoints) > SLIDING_WINDOW_SIZE/2 else 0
        averaged_grades.append(avg_grade)
        pt.grade = avg_grade
    return averaged_grades


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


