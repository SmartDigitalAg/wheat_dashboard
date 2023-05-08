# 익산/남원 NDVI 대시보드, 익산 토양센서 대시보드

****

## 1. 익산/남원 NDVI 대시보드
* 익산 > http://web01.taegon.kr:8505/
* 남원 > http://web01.taegon.kr:8507/

![image](https://user-images.githubusercontent.com/93760723/236784171-4354a3c5-f90b-4c07-b62e-cb3c2fdeab13.png)


### 1-1. 위성영상
| 위성        | 공간해상도 | 촬영주기 | 기간      |
|-----------|-------|------|---------|
| Landsat8  | 30    | 16   | 2013.04.17.~ |
| Landsat9  | 30    | 16   | 2021.10.31.~ |
| Sentinel2 | 10~30 | 10   | 2017.03.28.~ |


### 1-2. 흐름도
![image](https://user-images.githubusercontent.com/93760723/236781084-68d7c1be-6197-440f-a581-91f3bd04a1d8.png)

****

## 2. 익산 토양센서 대시보드
* 익산 > http://web01.taegon.kr:8506/

재배기간을 반영하여 전년도 10 ~ 12월, 당해년도 1 ~ 7월을 1년으로 계산

ex. 2022년: 2021년 10 ~ 12월 + 2022년 1 ~ 7월
![image](https://user-images.githubusercontent.com/93760723/236786628-899793f3-8df6-4bff-8ba5-f02589098df4.png)


### 2-1. 흐름도

![image](https://user-images.githubusercontent.com/93760723/236787274-286e683f-1a30-4b52-8427-b5df2fc71909.png)

### 2-2. 강수량 그래프

* 연도별 누적 강수량 그래프
```python
data["cumulative_rainfall"] = data.groupby(['season_year'])["rainfall"].cumsum()
```
* 연도별 강수량 Anonmaly 그래프
```python
annual_rainfall = data.groupby("season_year")["rainfall"].sum()

mean_rainfall = annual_rainfall.mean()
anomaly_index = annual_rainfall - mean_rainfall
```

-----

# 환경설정


```angular2svg
pip install waitress
pip install streamlit-folium
pip install altair
pip install earthengine-api
pip install pandas
pip install plotly
pip install matplotlib
```

## 1. Google Earth Engine + Streamlit

* 최초 실행 시 ```ee.Authenticate()``` 포함 후 실행. 이후 주석 처리

### 1-1. local

https://developers.google.com/earth-engine/guides/python_install
https://developers.google.com/earth-engine/guides/python_install#expandable-2

1. Google Cloud CLI 설치 프로그램 다운로드

PowerShell 터미널을 열고 다음 PowerShell 명령어 실행
```angular2svg
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```

2. Google 계정 로그인

Google Cloud SDK Shell에서 다음 명령어를 입력하고 Google 계정으로 로그인
````angular2svg
gcloud init
````

-----

Pycharm Interpreter Settings > Plugins > ```Google Cloud Code``` install 

### 1-2. docker

https://developers.google.com/earth-engine/guides/python_install#expandable-3

```angular2html
docker-compose exec #### bash
```

```angular2html
earthengine authenticate --quiet
```

