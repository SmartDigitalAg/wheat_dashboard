import ee
import pandas as pd
import altair as alt
import streamlit as st
from streamlit_folium import st_folium
import folium
import datetime

# ee.Authenticate()
ee.Initialize()

def load_collection(roi, earth_engine_snippet, start_date, end_date, band):
    collection= ee.ImageCollection(earth_engine_snippet) \
        .filterBounds(roi) \
        .filterDate(start_date, end_date) \
        .select(band)

    return collection.map(lambda image: addNDVI(image, band))
def addNDVI(image, band):
    return image.addBands(image.normalizedDifference(band).rename('NDVI'))

def reduceToMean(image, roi):
    mean = image.reduceRegion(reducer=ee.Reducer.mean(), geometry=roi, scale=30)
    ndvi_mean = mean.get('NDVI')
    return ee.Image(image.select('NDVI').set('NDVI_mean', ndvi_mean))

def ndvi_values_list(roi1, roi2, collection):
    ndvi_collection = []
    for roi in [roi1, roi2]:
        ndvi_collection.append(collection.map(lambda image: reduceToMean(image, roi)))

    ndvi_list1 = ndvi_collection[0].reduceColumns(ee.Reducer.toList(2), ['system:time_start', 'NDVI_mean']) \
        .get('list') \
        .getInfo()

    ndvi_list2 = ndvi_collection[1].reduceColumns(ee.Reducer.toList(2), ['system:time_start', 'NDVI_mean']) \
        .get('list') \
        .getInfo()

    df1 = pd.DataFrame(ndvi_list1, columns=['date', 'ndvi'])
    df1['date'] = pd.to_datetime(df1['date'], unit='ms')
    df1['date'] = df1['date'].astype(str).str.split(' ').str[0]
    df1['index'] = 1

    df2 = pd.DataFrame(ndvi_list2, columns=['date', 'ndvi'])
    df2['date'] = pd.to_datetime(df2['date'], unit='ms')
    df2['date'] = df2['date'].astype(str).str.split(' ').str[0]
    df2['index'] = 2

    return df1, df2

def extract_ndvi(roi1, roi2):

    today = datetime.date.today()
    year = today.year
    month = today.month
    day = today.day

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            datetime.date(2013, 3, 18), key="1")
    with col2:
        end_date = st.date_input(
            "End Date",
            datetime.date(year, month, day), key="2")

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")


    l8_collection = load_collection(roi1, 'LANDSAT/LC08/C02/T1', start_date, end_date, ['B5', 'B4'])
    l9_collection = load_collection(roi1, 'LANDSAT/LC09/C02/T1_L2', start_date, end_date, ['SR_B5', 'SR_B4'])
    s2_collection = load_collection(roi1, 'COPERNICUS/S2_SR', start_date, end_date, ['B8', 'B4'])


    collections = [l8_collection, l9_collection, s2_collection]

    values_list = []
    for collection in collections:
        dfs = ndvi_values_list(roi1, roi2, collection)
        values_list.append(dfs[0])
        values_list.append(dfs[1])

    return values_list

def draw_chart(df, color):

    chart = alt.Chart(df).mark_line().encode(
        y=alt.Y('ndvi', title='NDVI values'),
        x=alt.X('date', title='Date(YYYY-mm-dd)'),
        color=alt.value(color))

    return chart

def chart_ndvi(roi1, roi2):
    st.header("TimeSeries NDVI Values Chart")

    st.subheader("Landsat8 & Landsat9")

    df = extract_ndvi(roi1, roi2)
    l8_field1 = df[0]
    l8_field2 = df[1]
    l9_field1 = df[2]
    l9_field2 = df[3]
    s2_field1 = df[4]
    s2_field2 = df[5]

    c_l8_field1 = draw_chart(l8_field1, "blue")
    c_l8_field2 = draw_chart(l8_field2, "orange")
    c_l9_field1 = draw_chart(l9_field1, "skyblue")
    c_l9_field2 = draw_chart(l9_field2, "blue")

    st.altair_chart((c_l8_field1 + c_l8_field2 + c_l9_field1 + c_l9_field2).interactive(), use_container_width=True)

    st.subheader("Sentinel2")

    c_s2_field1 = draw_chart(s2_field1, "blue")
    c_s2_field2 = draw_chart(s2_field2, "orange")

    st.altair_chart((c_s2_field1 + c_s2_field2).interactive(), use_container_width=True)

def get_ndvi_image(collection, roi):
    vis_paramsNDVI = {
        'min': 0,
        'max': 1,
        'palette': ['brown', 'yellow', 'green', 'blue']
    }

    ndvi_values = collection.select('NDVI').limit(1, 'system:time_start', False).first().clip(roi)
    map_dict = ee.Image(ndvi_values).getMapId(vis_paramsNDVI)

    return map_dict

def load_background():
    tiles = "http://mt0.google.com/vt/lyrs=s&hl=ko&x={x}&y={y}&z={z}"
    attr = "Google"

    m = folium.Map(
        location=[35.43890642346706, 127.52977233306779],
        zoom_start=18,
        tiles=tiles,
        attr=attr)
    return m

def draw_map(m, map_id_dict):
    color_map = folium.raster_layers.TileLayer(
                    tiles=map_id_dict['tile_fetcher'].url_format,
                    attr='Google Earth Engine',
                    name='NDVI',
                    overlay=True,
                    control=True
                ).add_to(m)

    return color_map

def draw_ndvi_map(roi1, roi2, earth_engine_snippet, band, key, title):
    st.subheader(title)
    with st.spinner(text="Loading map..."):
        today = datetime.date.today()

        start_date = '2018-01-01'
        end_date = today.strftime("%Y-%m-%d")

        figure = folium.Figure()
        m = load_background()
        m.add_to(figure)

        collection = load_collection(roi1, earth_engine_snippet, start_date, end_date, band)

        map_id_dict1 = get_ndvi_image(collection, roi1)
        map_id_dict2 = get_ndvi_image(collection, roi2)

        draw_map(m, map_id_dict1)
        draw_map(m, map_id_dict2)

        st_data = st_folium(m, width=700, height=400, key=key)

def mapping_ndvi(roi1, roi2):
    st.header("NDVI Map")
    col1, col2, col3 = st.columns(3)
    with col1:
            draw_ndvi_map(roi1, roi2, 'LANDSAT/LC08/C01/T1_SR', ['B5', 'B4'], "1", 'Landsat8')
    with col2:
            draw_ndvi_map(roi1, roi2, 'LANDSAT/LC09/C02/T1_L2', ['SR_B5', 'SR_B4'], "2", 'Landsat9')
    with col3:
            draw_ndvi_map(roi1, roi2, 'COPERNICUS/S2_SR', ['B8', 'B4'], "3", 'Sentinel2')

def main():
    roi1 = ee.Geometry.MultiPolygon(
        [[[[127.52903233306779, 35.43925642346706],
           [127.52839396732224, 35.43833204554555],
           [127.52882580297364, 35.43811570024398],
           [127.52948830860032, 35.4389570398177],
           [127.52903233306779, 35.43925642346706]]]])

    roi2 = ee.Geometry.MultiPolygon(
        [[[[127.52903233306779, 35.43925642346706],
           [127.52839396732224, 35.43833204554555],
           [127.52882580297364, 35.43811570024398],
           [127.52948830860032, 35.4389570398177],
           [127.52903233306779, 35.43925642346706]]]])

    st.set_page_config(layout="wide")

    chart_ndvi(roi1, roi2)
    mapping_ndvi(roi1, roi2)


if __name__ == '__main__':
    main()