import pickle
from argparse import ArgumentParser
from utils import build_elevation_gpx, plot, PICKLE_DUMPFILE

if __name__ == '__main__':
    
    # get cmdline args
    parser = ArgumentParser()
    parser.add_argument('program', nargs='?', default='plot', choices=['plot', 'build_elevation_pickle', 'plot_dev'])
    parser.add_argument('filepath', nargs='?', default='utcc_113km.gpx')
    parser.add_argument('--gpxpoints-pickle', nargs='?', default='gpxpoints.pick')
    # parser.add_argument('--gpxpoints-pickle', nargs='?', default='gpxpoints.pick')
    
    args = parser.parse_args()
    
    if args.program == 'build_elevation_pickle':
        gpxpoints =  build_elevation_gpx(args.filepath)
        # pickling it for next time 
        import pickle
        with open(f"{PICKLE_DUMPFILE}", mode='wb') as jsonfile:
            # test = {"a": 1, "b": 2}
            pickle.dump(gpxpoints, jsonfile)
        print(f"Done. ")

    elif args.program == 'plot':
        with open(PICKLE_DUMPFILE, 'rb') as f:
            gpxpoints = pickle.load(f)

            # plot(gpxpoints_list=gpxpoints, plotname='plot_normalized')
            plot(gpxpoints_list=gpxpoints, plotname='plot_raw_grade')
    

    elif args.program == 'plot_dev':
        with open(PICKLE_DUMPFILE, 'rb') as f:
            gpxpoints = pickle.load(f)

            # plot(gpxpoints_list=gpxpoints, plotname='plot_normalized')
            plot(gpxpoints_list=gpxpoints, plotname='plot_dev')
    
    
    else:
        pass
    
    
    # if args.gpxpoints-pickle:
    #     gpxpoints = pickle.load(PICKLE_DUMPFILE)
    #     plot(gpxpoints_list = gpxpoints)
    # else:
    #     filepath = 'utcc_113km.gpx'
    #     
    #     
    #     plot(filepath)

    # if args.program == 'add_elevation_gpx':
    #     gpxpoints =  build_elevation_gpx(filepath)
    #     plot(gpxpoints_list=gpxpoints)
    # elif args.program == 'plot':
    #     plot(filepath)
