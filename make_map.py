#!/usr/bin/env python
# GPL v3 Brian Ballsun-Stanton
# Taken from https://automating-gis-processes.github.io/2016/Lesson5-static-maps.html


import geopandas
import matplotlib.pyplot as plt
from frictionless import extract
from pathlib import Path
from pprint import pprint
import pandas
import os
import subprocess
import geoplot
# https://geopandas.org/reference/geopandas.GeoDataFrame.html#geopandas.GeoDataFrame
from shapely.geometry import Point
# https://geopandas.org/gallery/plotting_basemap_background.html#sphx-glr-gallery-plotting-basemap-background-py
import contextily as ctx
#https://geopython.github.io/OWSLib/#wms
from owslib.wms import WebMapService
from owslib.wfs import WebFeatureService

# TO DISABLE SSL CHECKING 
# $ export CURL_CA_BUNDLE=""; ./make_map.py




DATA_DIR = Path("data")
DATA_FILENAME = "2020-08-18-term1_petra-249.tsv"
DATA_FILE = DATA_DIR / DATA_FILENAME
DEBUG = False
ROMAN_ROADS = Path("Roman-Road-Network")
ROMAN_ROADS_SHP = ROMAN_ROADS / "roads" / "roman_roads_v2008.shp"

WMS_LAYERS={"Roman Roads":{"name":'Roman Roads', "zorder":"0"},
			"Provinces (ca. AD117)":{"name":'Provinces (ca. AD117)', "zorder":"1"},
			"Cities and Settlements":{"name":'Cities and Settlements', "zorder":"2"},
}
layers_list = list(WMS_LAYERS.keys())
# https://stackoverflow.com/a/15445989
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)



wms = WebMapService('https://ags.cga.harvard.edu/arcgis/services/darmc/roman/MapServer/WMSServer?', version='1.1.1')
for content in wms.contents:
	if wms[content].title in WMS_LAYERS:
		pprint((content, wms[content], wms[content].title, wms[content].crsOptions, wms[content].styles, wms[content].boundingBoxWGS84))

		WMS_LAYERS[wms[content].title]['wms'] = wms[content]
#https://geopandas.org/install.html
geopandas.options.use_pygeos = True
pprint(WMS_LAYERS)
pprint([op.name for op in wms.operations])

# https://frictionlessdata.io/tooling/python/extracting-data/
# Handles multiline columns cleanly.
import_rows = extract(DATA_FILE)
import_dataframe = pandas.DataFrame(import_rows)

#https://cmdlinetips.com/2018/02/how-to-subset-pandas-dataframe-based-on-values-of-a-column/

roads = geopandas.read_file(ROMAN_ROADS_SHP)
point_geodataframe = geopandas.GeoDataFrame(
  import_dataframe[import_dataframe.Longitude.notnull()],
  geometry=geopandas.points_from_xy(
    import_dataframe[import_dataframe.Longitude.notnull()].Longitude,
    import_dataframe[import_dataframe.Longitude.notnull()].Latitude),
  crs="EPSG:4326")
if DEBUG:
	pprint(point_geodataframe)

point_geodataframe_3857 = point_geodataframe.to_crs(epsg=3857)



pprint(wms.getOperationByName('GetCapabilities').methods)
pprint(wms.getOperationByName('GetCapabilities').formatOptions)

# pprint(point_geodataframe_3857.total_bounds)
# img = wms.getmap(layers=['92'],
#                  src='EPSG:3857',
#                  size=(900,900),
#                  bbox=point_geodataframe_3857.total_bounds,
#                  format='image/png',
#                  transparent=True
#                  )


# out = open('roman-map.png', 'wb')
# out.write(img.read())
# out.close()

# https://geopandas.org/gallery/create_geopandas_from_pandas.html#sphx-glr-gallery-create-geopandas-from-pandas-py
#world = geopandas.read_file(geopandas.datasets.get_path('naturalearth_lowres'))

# ax = world.plot(
#   color='white', 
#   edgecolor='black')

# https://geopandas.org/gallery/plotting_with_geoplot.html
# geoplot.polyplot(world, figsize=(8, 4))
# ax = geoplot.polyplot(
#     world, projection=geoplot.crs.Orthographic(), figsize=(10, 10)
# )
# ax.outline_patch.set_visible(True)

fig, ax = plt.subplots()
plt.title(DATA_FILENAME)
roads_3857 = roads.to_crs(epsg=3857)
roads_3857.plot(ax=ax, linewidth=0.1, alpha=1,  color='gray', zorder=1)
point_geodataframe_3857.plot(ax=ax, linewidth=0.1, markersize=1, alpha=0.5, color='red', edgecolor='k', zorder=2)
ctx.add_basemap(ax, source=ctx.providers.Stamen.TerrainBackground)

# for layer in WMS_LAYERS:
# 	print("foo")
# 	current_layer = WMS_LAYERS[layer]['wms']
# 	pprint(layer)
# 	pprint(current_layer.getOperationByName('GetMap').methods)
# 	pprint(current_layer.getOperationByName('GetMap').formatOptions)

#layermap_3857 = wms.getmap(layers=WMS_LAYERS.keys(),
#                      		  srs="EPSG:3857",
#                      		  )


plt.axis('off')

#point_geodataframe.plot(ax=ax, color='red')
MAP_FILENAME="testdata.png"
plt.savefig(MAP_FILENAME, dpi=600)
subprocess.call(["xdg-open", MAP_FILENAME])

#pre_geo_data = {'objects':[], 'geometry':[]}

# for row in import_rows:
# 	if DEBUG:
# 		print(row)
# #	objects.append(row)
# #	geometry.append(Point())
