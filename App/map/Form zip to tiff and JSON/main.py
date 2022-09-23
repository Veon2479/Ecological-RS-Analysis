#from pyparsing import null_debug_action
from satpy.scene import Scene
from satpy import find_files_and_readers
from glob import glob
from pathlib import Path
#from satpy.utils import debug_on

from datetime import datetime
import config

import print_to_log
print = print_to_log.get_logger(__name__).info

from pyresample.geometry import AreaDefinition
area_BY = AreaDefinition(   
                            area_id = 'Belarus',
                            description = 'The region of Belarus (WGS 84 / UTM zone 35N Projection)', 
                            projection = 'EPSG:32635', 
                            proj_id = 'EPSG:32635', 
                            width = 2800, 
                            height = 2400, 
                            area_extent = (
                                        200000,
                                    5650000,
                                        900000,
                                    6250000, 
                                ))

#debug_on()

zipFiles = Path(config.zipDir).rglob("*_viirs_*.zip")
for zip in zipFiles:

    outTempUnzipDir = Path(config.tempDir + zip.name)
    outTempUnzipDir.mkdir(parents=True, exist_ok=True)
    import zipfile
    zipfile.ZipFile(zip, 'r').extractall(outTempUnzipDir)

    viirsFiles = glob(str(outTempUnzipDir) + "/*.h5")
    scene = Scene(filenames = viirsFiles, reader='viirs_sdr')

    try:

        outResultDir = Path(config.resultTiff + zip.name)
        outResultDir.mkdir(parents=True, exist_ok=True)

        # Yes, hardcode names
        names = ['adaptive_dnb', 'ash', 'cimss_cloud_type', 'cloudtop', 'dust', 'fire_temperature', 'fog', 'green_snow', 'histogram_dnb', 'hncc_dnb', 'natural_color_raw', 'night_fog', 'night_overview', 'overview']
        for name in names:
            print('START ' + name)
            try:
                print("Start load")
                scene.load([name], generate = False)

                print("Start resample")
                ls = scene.resample(area_BY, resampler='nearest')

                # print(name, ls[name].attrs.get("file_units"))

                print("Start save")
                ls.save_dataset(    name, 
                                    writer='geotiff', 
                                    # tiled=False, 
                                    reader_kwargs={'fill_disk': False},
                                    #filename=config.inDir + '/_out_viirs_' + name + '.tif')
                                    filename=str(outResultDir) + "/" + name + '.tif')

                ls = None
                print('DONE  ' + name)
            except:
                print('ERROR ' + name)

    except:
        print('no data: continue')
    
    scene = None
    try:
        print('Delete DIR ' + str(outTempUnzipDir))
        print('\n')
        import shutil
        shutil.rmtree(str(outTempUnzipDir)) # Remove Dir
    except:
        print('ERROR Delete DIR ' + str(outTempUnzipDir))
        print('\n')

