import streamlit as st
import pandas as pd
import altair as alt
import datetime
import os
import matplotlib.pyplot as plt
import plotly.express as px
from PIL import Image


def get_weather():
    stn_Ids = 247
    sy = 1961
    ey = 2023
    URL = f"https://api.taegon.kr/stations/{stn_Ids}/?sy={sy}&ey={ey}&format=csv"
    df = pd.read_csv(URL, sep='\\s*,\\s*', engine="python")
    df.to_csv("weather_namwon.csv", index=False)

def preprocess_wheather():
    df = pd.read_csv("weather_namwon.csv")
    df['season_year'] = df['year']
    df = df[~df['month'].isin([8, 9])]
    df.loc[df['month'].isin([10, 11, 12]), 'season_year'] += 1
    # df = df[(df['month'] != 2) | (df['day'] != 29)]

    df = df.sort_values(['month'], ascending=[False])
    df['month'] = pd.Categorical(df['month'], categories=[10, 11, 12, 1, 2, 3, 4, 5, 6, 7], ordered=True)
    df = df.sort_values(['month', 'year', 'day'], ascending=[True, True, True]).reset_index(drop=True)
    df['date'] = df.groupby("season_year").cumcount() + 1

    return df

def draw_temp_chart(df, item, color):
    chart = alt.Chart(df).mark_line().encode(
        y=alt.Y(item, title='Temperature'),
        x=alt.X('date', title='Date'),
        color=alt.value(color))

    return chart


def draw_seasonyear(df, item, color):
    c = df[df["month"].isin([10, 11, 12])]
    l = df[~df["month"].isin([10, 11, 12])]

    line1 = draw_temp_chart(l, item, color)
    line2 = draw_temp_chart(c, item, color)

    combined_line = alt.layer(line2, line1)

    return combined_line

def chart_temp_commonyear():
    op_year = st.selectbox("평년",
              ["1991~2020", "1981~2010", "1971~2000", "1961~1990"])

    sy = int(op_year.split("~")[0])
    ey = int(op_year.split("~")[1])

    df = preprocess_wheather()

    #------ 선택 30년
    df_common = df[(df["season_year"] >= sy) & (df["season_year"] <= ey)]
    df_common_mean = df_common.groupby(["month", "day"]).mean()[['date','tmax', 'tavg', 'tmin', 'humid', 'wind', 'sunshine', 'rainfall', 'snow', 'cloud', 'season_year']]
    df_common_mean.reset_index(inplace=True)
    df_common_mean = df_common_mean.rename(columns={'month': 'month', 'day': 'day'})

    # ------ 현재
    df_current = df[df['season_year'] == 2023]


    tavg_chart = draw_seasonyear(df_common_mean, "tavg", "green")
    tmax_chart = draw_seasonyear(df_common_mean, "tmax", "red")
    tmin_chart = draw_seasonyear(df_common_mean, "tmin", "blue")
    current_chart = draw_seasonyear(df_current, "tavg", "black")

    st.altair_chart(tavg_chart + tmax_chart + tmin_chart + current_chart, use_container_width=True)



def chart_rainfall_cumulative():
    st.subheader("")
    data = preprocess_wheather()
    data = data[data['year'] != 1961]

    data["cumulative_rainfall"] = data.groupby(['season_year'])["rainfall"].cumsum()
    df = data[['season_year', 'date', 'cumulative_rainfall']]

    # ------- px
    line_fig = px.line(df, x='date', y='cumulative_rainfall', color='season_year', height=700)

    line_fig.update_yaxes(title_text='Cumulative Rainfall(mm)')
    line_fig.update_traces(line_color='gray', line_width=0.5)
    line_fig.update_traces(line_color='red', selector={'name': '2023'}, line_width=3)
    line_fig.update_layout(showlegend=False)

    st.plotly_chart(line_fig, use_container_width=True)

def chart_rainfall_anomaly():

    data = preprocess_wheather()

    annual_rainfall = data.groupby("season_year")["rainfall"].sum()

    mean_rainfall = annual_rainfall.mean()
    anomaly_index = annual_rainfall - mean_rainfall

    fig = px.bar(
        anomaly_index,
        x=anomaly_index.index,
        y=anomaly_index.values,
        color=anomaly_index.values > 0,
        color_discrete_sequence=['red', 'blue'], height=700
    )
    fig.update_layout(
        # title="Annual Rainfall Anomaly Index",
        xaxis_title="Year",
        yaxis_title="Rainfall Anomaly Index",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def draw_soilwater_chart(df, port, color):
    chart = alt.Chart(df).mark_line().encode(
        y=alt.Y(port, title='Matric Potential(kPa)', scale=alt.Scale(reverse=True)),
        x=alt.X('date', title='Date'),
        color=alt.value(color))

    return chart

def chart_soil_water():
    sheets = ['60(plot3,4_상)', '62(plot1,2_상)', '63(plot1,2_하)',
              '56(plot3,4_하)', '51(plot5,6_상)', '54(plot5,6_하)',
              '55(plot7,8_상)', '58(plot7,8_하)']

    op_sheet = st.selectbox(
        '구역', sheets
    )
    df = pd.read_excel("익산포텐셜.xlsx", sheet_name=op_sheet)
    title = df.columns[0]
    df = df.rename(columns={title: 'date'})

    port1 = draw_soilwater_chart(df, 'Port1', 'blue')
    port2 = draw_soilwater_chart(df, 'Port2', 'orange')
    port3 = draw_soilwater_chart(df, 'Port3', 'green')
    port4 = draw_soilwater_chart(df, 'Port4', 'navy')
    port5 = draw_soilwater_chart(df, 'Port5', 'yellow')
    port6 = draw_soilwater_chart(df, 'Port6', 'grey')

    st.altair_chart(port1 + port2 + port3 + port4 + port5 + port6, use_container_width=True)


def main():
    st.set_page_config(layout="wide")
    # get_weather()
    # st.title("토양 수분")
    # chart_soil_water()
    st.title("기후평년 일별평년값")
    chart_temp_commonyear()
    st.title("연도별 누적 강수량")
    chart_rainfall_cumulative()
    st.title("연도별 강수량 anomaly")
    chart_rainfall_anomaly()
    # get_weather()

if __name__ == '__main__':
    main()