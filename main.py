import pickle
from argparse import ArgumentParser
# from utils import PICKLE_DUMPFILE
import utils
from plots import plot
import yaml

from api import build_elevation_gpx, pickle_new_gpxpoints

def parse_config_file(cmd_args):
    with open(cmd_args.configfile, 'r') as f:
        confs = yaml.load(f, yaml.FullLoader)
        return confs

if __name__ == '__main__':
    
    # get cmdline args
    parser = ArgumentParser()
    parser.add_argument('--program', default='default', choices=['default', 'foo', 'fetchApiData'])
    parser.add_argument('--configfile', default='configs.yml')
    args = parser.parse_args()
    confs = parse_config_file(args)
    
    # extract current mode confs
    confs = confs[args.program]
    utils.CONFIGS = confs
    
    # run programs selected
    if confs.get("fetchApiData"):
        new_gpxpoints = build_elevation_gpx(confs["consts"]["FILEPATH"])
        pickle_new_gpxpoints(new_gpxpoints)
    elif confs["computeMetrics"]:
        pass    # compute the metrics
    elif confs["plot"]:
        pass    # plot stuff
    
    if args.program == 'build_elevation_pickle':
        gpxpoints =  build_elevation_gpx(args.filepath)
        # pickling it for next time 
        import pickle
        with open(f"{confs['const']['PICKLE_DUMPFILE']}", mode='wb') as jsonfile:
            # test = {"a": 1, "b": 2}
            pickle.dump(gpxpoints, jsonfile)
        print(f"Done. ")

    elif args.program == 'plot':
        with open(confs['const']['PICKLE_DUMPFILE'], 'rb') as f:
            gpxpoints = pickle.load(f)

            # plot(gpxpoints_list=gpxpoints, plotname='plot_normalized')
            plot(gpxpoints_list=gpxpoints, plotname='plot_raw_grade')
    

    elif args.program == 'plot_dev':
        with open(confs['const']['PICKLE_DUMPFILE'], 'rb') as f:
            gpxpoints = pickle.load(f)

            # plot(gpxpoints_list=gpxpoints, plotname='plot_normalized')
            plot(gpxpoints_list=gpxpoints, plotname='plot_dev')
    
    
    else:
        pass
