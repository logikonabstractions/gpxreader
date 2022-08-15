TOL = 4     # ±TOL for what variation is acccepted to be considered within a given interval type 
import numpy as np
import matplotlib.pyplot as plt
from utils import FITS_FILEPATH, DILL_FILEPATH
import os
import json
import dill

class Program:
    def run(self):
        raise NotImplemented("implt. this func. ")


class LapsAnalyzer:
    ''' reads a bunch of fit files & extracts stats about laps - avg/stdev/min/max etc. on laps from activities '''
    
    def __init__(self,stavafits=None, dill_filepath=None):
        self.laps = []
        self.init_data(stravafits=stavafits)
        self.relevent_lap_fields = ["start_time", "avg_speed", "avg_heart_rate", "max_heart_rate", "total_elapsed_time" ]
        self.laps_dict = {x:[] for x in range(30,301, 30)}      # interested laps of 30s, 60s.... 5 minutes
        self.stats = {x:[] for x in self.laps_dict.keys()}
        
    def run(self):
        """ executes this program """
        print(f"Running LapAnalyzer...")
        self.extract_laps()
        self.calc_stats()
        # self.plot_stats()
        
        
        
        
    def init_data(self, stravafits=None, dill_filepath=None, **kwargs):
        """ inits the laps based on data provided. if fits list, then xtacts all the laps from the files """
        laps = []
        print(f"Init data ....")
        if stravafits:
            print(f"Datasouce: fitfiles")
            for stravafit in stravafits:
                laps += stravafit.laps
            self.laps = laps

        elif dill_filepath:
            print(f"Datasouce: dill file: {dill_filepath}")
            with open(dill_filepath, 'rb') as dillfile:
                self.laps = dill.load(dillfile)
        else:
            raise NotImplemented("only stravafits support for now, implt other formats")
        
    def extract_laps(self):
        """ takes laps in self.laps & extract them to self.laps_dict """
        print(f"Sort the laps we have by 30±4 seconds slots ")
        for lap in self.laps:
            # round to secondes the lap
            lap_details = lap.get_values()
            laptime = int(lap_details["total_elapsed_time"])
            if laptime >= min(self.laps_dict.keys()) and laptime <= max(self.laps_dict.keys()):     # e.g. that's a relevent duration lap
                for key in self.laps_dict.keys():
                    if laptime in range(key-TOL, key+TOL):
                        self.laps_dict[key].append(lap_details["avg_speed"])
        # TODO: ouput that dictionnary to file so I don't need to recompute it every single time
    
    def calc_stats(self):
        """ based on laps_dict """
        for inttime, avg_speed_ms in self.laps_dict.items():
            if len(avg_speed_ms)>0:
                print(f"Time: {inttime}, avg speed (m/s): {self.ms_to_mink(avg_speed_ms)}")
                self.stats[inttime] = self.ms_to_mink(avg_speed_ms)
                
                
                
    def plot_stats(self):
        """ """
        for inttime, avg_speed in self.stats.items():
            x = []
            y = []
            for lap in avg_speed:
                x.append(inttime)
                y.append(lap)
            plt.scatter(x, y)
            plt.show()
        
    def ms_to_mink(self, ms_speeds):
        """ converts meter/seconds speeds to min/km values """
        return  [1/(x*60/1000) for x in ms_speeds]
    
    def save_laps_to_file(self, filepath):
        """ saves the laps to a file """
        print(f"saving {len(self.laps)} laps to file.... ")
        with open(filepath, 'wb') as outfile:
            # json.dump({"laps":self.laps_dict}, outfile)
            # json.dump({"laps":self.laps}, outfile)
            dill.dump(self.laps, outfile)
        print(f"File saved...")


