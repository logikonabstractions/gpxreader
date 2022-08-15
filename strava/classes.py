from fitparse import FitFile
import logging
L = logging.getLogger()
L.addHandler(logging.StreamHandler())

class StravaFITS:
    """ opens, save, read, use attrs. of FITS files from strava activities"""
    
    def __init__(self, filepath=None):
        """ """
        self.laps    = None
        self.records = None
        self.fitmessages = self.read_fits(filepath=filepath)
        print(f"Current holding fitsReader file: {self.fitmessages} from filepath: {filepath}")
        self.demo_fits()
            
    def read_fits(self, filepath):
        """ read a.fit.gz file given the filepath"""
        if filepath:
            fitsdata = None
            with FitFile(filepath) as fitfile:
                self.records = list(fitfile.get_messages("records"))
                self.laps = list(fitfile.get_messages("lap"))
            return fitsdata
            
    
    def demo_fits(self):
        """ just to show how to use a fits files quickly """
        
