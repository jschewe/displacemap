import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
import os
import csv
import pickle
import geopy.geocoders
from geopy.geocoders import Nominatim, GoogleV3

#####################

### Specify data directories: 
indir = os.path.abspath("C:\/data\/Migration")
localbasedir = os.path.abspath("C:\/Documents and Settings\/schewe\/My Documents\/localcopy")
outdir = os.path.abspath(localbasedir + "\/own_papers\/Migration")

### Read displacement data: 

# IDMCfilename = "idmc-disaster-displacement-dataset-2013-2015-2016-05-11.csv"
# IDMCfilename = "idmc-disaster-displacement-dataset-2013-2015-2016-05-11_test100.csv"
IDMCfilename = "idmc-disaster-displacement-dataset-2013-2015-2016-05-11_test500.csv"

IDMCfile = os.path.abspath(indir + "//" + IDMCfilename)

def readCSVinput(inputfile):
  with open(inputfile, 'rb') as infile:
    indat = csv.reader(infile, delimiter=';')
    indatlist = list()
    for column in indat: 
      indatlist.append(column)
    indatarray = np.array(indatlist)
  # return indatlist
  return indatarray

IDMCdata = readCSVinput(IDMCfile)
  
# os.sys.exit(0)

### Set up map: 

degsouth = -90
degnorth = 90
degwest = -180
degeast = 180
from mpl_toolkits.basemap import Basemap, cm
bm = Basemap(projection='cyl',llcrnrlat=degsouth,urcrnrlat=degnorth,llcrnrlon=degwest,urcrnrlon=degeast,resolution='c')
fig = plt.figure()
plt.clf()
ax1 = fig.add_subplot(111)
plt.ion()
plt.show()


### If there's already a file with coordinates, read them; else, create empty dicts:
# Coords_filename = str(IDMCfilename.split('.')[0] + '_coordinates.pkl')
Coords_filename = 'idmc-disaster-displacement-dataset-2013-2015-2016-05-11_coordinates.pkl'
Coords_errors_filename = 'idmc-disaster-displacement-dataset-2013-2015-2016-05-11_coordinates_errors.csv'
try: 
  with open(Coords_filename, 'rb') as Coords_file:
    Lats_dict, Lons_dict, Flags_dict = pickle.load(Coords_file)
except IOError: 
  Lats_dict = {}
  Lons_dict = {}
  Flags_dict = {}

  
### Locate places, and flag places where exact location cannot be found: 
IDMCdata_dict = {}
newCoordsSwitch = 0
for i,locID in enumerate(np.ravel(IDMCdata[1:,IDMCdata[0,:]=="ID"])): 
  IDMCdata_dict[locID] = dict(zip(IDMCdata[0,:], IDMCdata[i+1,:]))
  IDMCevent_dict = dict(zip(IDMCdata[0,:], IDMCdata[i+1,:]))
  # locID = IDMCevent_dict['ID']
  locName = IDMCevent_dict['Locations']
  print locID, locName
  try: 
    locLat = Lats_dict[locID]
    locLon = Lons_dict[locID]
    print 'Taking coordinates out of pickle file.'
  except KeyError: 
    print 'Locating coordinates...'
    newCoordsSwitch = 1
    geolocator = Nominatim()
    # geolocator = GoogleV3()
    try: 
      # location = geolocator.geocode(locName)
      location = geolocator.geocode(locName, timeout=10)
      # print(location.address)
      print((location.latitude, location.longitude))
    except (AttributeError, geopy.exc.GeocoderQueryError) as e: 
      print 'NOTE: Location(s) not found; using Country or Territory as a proxy:'
      locCountry = IDMCevent_dict['Country or Territory']
      print locCountry
      location = geolocator.geocode(locCountry, timeout=10)
      print((location.latitude, location.longitude))
      Flags_dict[locID] = 1
    Lats_dict[locID] = location.latitude
    Lons_dict[locID] = location.longitude
    locLat = Lats_dict[locID]
    locLon = Lons_dict[locID]
  
  ### Plot events on map, indicating event type and size of affected population: 
  popAffected = int(IDMCevent_dict["New Displacement"])
  # msize = np.ceil(popAffected*1e-3)*0.05
  msize = np.ceil(np.log(popAffected))
  # msizes = {100: 2, 1000: 4, 1000: 6}
  disasterType = IDMCevent_dict["Type"]
  mcolors = {'Flood': 'b', 'Extreme temperature': 'r', 'Storm': 'g', 'Severe winter condition': 'y'}
  if disasterType in mcolors.keys():
    mcolor = mcolors[disasterType]
  else:
    mcolor = 'k'
  bm.plot(locLon, locLat, 'o', latlon=True, markersize=msize, color=mcolor, alpha=0.3)

bm.drawcoastlines(linewidth=0.75)   
bm.drawcountries(linewidth=0.75)   
# bm.drawmeridians(np.arange(-50,60,10), labels=[0,0,0,0])
# bm.drawparallels(np.arange(-20,60,10), labels=[0,0,0,0])
# plt.text(-42,-15,str(model),size=16, backgroundcolor='w')
xx, locs = plt.xticks()
ll = ['%.1f' % a for a in xx]
plt.xticks(xx, ll)

with open(Coords_errors_filename, 'wb') as errorf: 
  wr = csv.writer(errorf, delimiter=';')
  for locID in Flags_dict.keys():
    wr.writerow((IDMCdata_dict[locID]['ID'], IDMCdata_dict[locID]['Country or Territory'], IDMCdata_dict[locID]['Locations']))

### Print map to file
# outfname = str(outdir + '//IDMC_displacement_map.pdf') 
# print "Save data to %s" % outfname
# if os.path.exists(outfname): 
  # print "File exists, will be overwritten. "
# raw_input("Print figure? Press key to continue...")
# savefig(outfname)

### If coordinates have been newly located, add them to coordinate file: 
if newCoordsSwitch == 1: 
  with open(Coords_filename, 'wb') as Coords_file:
    pickle.dump((Lats_dict, Lons_dict, Flags_dict), Coords_file)
