import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO

def get_stock_info(market_type=None):
  # 1. 마켓 타입에 맞춰 URL 주소 구성하기
  base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"
  method = "download"

  if market_type == 'kospi':
    marketType = "stockMkt"  # 주식 종목이 코스피인 경우
  elif market_type == 'kosdaq':
    marketType = "kosdaqMkt" # 주식 종목이 코스닥인 경우
  elif market_type == None:
    marketType = ""

  url = "{0}?method={1}&marketType={2}".format(base_url, method, marketType)

  # 2. 한국 거래소에서 주식 정보 데이터 가져오기
  df = pd.read_html(url, header=0)[0]

  # 3. 가져온 주식 정보 데이터에서 필요한 데이터만 남기고, 알맞게 가공하기
  # 종목코드 열을 6자리 숫자로 표시된 문자열로 변환
  df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")
    
  # 회사명과 종목코드 열 데이터만 남김
  df = df[['회사명','종목코드']]

  # 4. 주식 정보 데이터 반환
  return df

def get_ticker_symbol(company_name, market_type=None):
  df = get_stock_info(market_type)

  codes = df[df['회사명'] == company_name]['종목코드'].values
  code = codes[0]
  
  if market_type == 'kospi':
    ticker_symbol = code + '.KS'
  elif market_type == 'kosdaq':
    ticker_symbol = code + '.KQ'

  return ticker_symbol

st.title('주식 정보를 가져오는 웹 앱')

radio_options = ['코스피', '코스닥']
radio_selected = st.sidebar.radio('증권시장', radio_options)

stock_name = st.sidebar.text_input('회사 이름', value="NAVER")
date_range = st.sidebar.date_input("시작일과 종료일", [datetime.date(2019, 1, 1), datetime.date(2021, 12, 31)])

clicked = st.sidebar.button("주가 데이터 가져오기")

if clicked:
  market_type = 'kospi'
  if radio_selected == '코스닥':
    market_type = 'kosdaq'

  ticker_symbol = get_ticker_symbol(stock_name, market_type)
  ticker_data = yf.Ticker(ticker_symbol)

  start_p = date_range[0] # 시작일
  end_p = date_range[1] + datetime.timedelta(days=1) # 종료일(지정된 날짜에 하루를 더함)

  df = ticker_data.history(start=start_p, end=end_p)

  # 1) 주식 데이터 표시
  st.subheader(f"[{stock_name}] 주가 데이터")
  st.dataframe(df.head()) # 주가 데이터 표시(앞의 일부만 표시)

  fontprop = fm.FontProperties(fname='NanumGothic.ttf', size=18)
  matplotlib.rcParams['font.family'] = 'Malgun Gothic'
  matplotlib.rcParams['axes.unicode_minus'] = False

  ax = df['Close'].plot(grid=True, figsize=(15, 5))
  ax.set_title("주가(종가) 그래프", fontsize=30) # 그래프 제목을 지정
  ax.set_xlabel("기간", fontsize=20) # x축 라벨을 지정
  ax.set_ylabel("주가(원)", fontsize=20) # y축 라벨을 지정
  plt.xticks(fontsize=15) # X축 눈금값의 폰트 크기 지정
  plt.yticks(fontsize=15) # Y축 눈금값의 폰트 크기 지정
  fig = ax.get_figure() # fig 객체 가져오기
  st.pyplot(fig) # 스트림릿 웹 앱에 그래프 그리기

  st.markdown("**주가 데이터 파일 다운로드**")

  # DataFrame 데이터를 CSV 데이터(csv_data)로 변환
  csv_data = df.to_csv() # DataFrame 데이터를 CSV 데이터로 변환해 반환
  
  # DataFrame 데이터를 엑셀 데이터(excel_data)로 변환
  excel_data = BytesIO() # 메모리 버퍼에 바이너리 객체 생성
  # df['date'] = pd.to_datetime( df['date'], errors='coerce',utc=True)
  df.index = df.index.tz_localize(None)
  df.to_excel(excel_data) # DataFrame 데이터를 엑셀 형식으로 버퍼에 쓰기
  
  columns = st.columns(2) # 2개의 세로단으로 구성
  with columns[0]:
    st.download_button("CSV 파일 다운로드", csv_data, file_name='stock_data.csv')
  with columns[1]:
    st.download_button("엑셀 파일 다운로드", excel_data, file_name='stock_data.xlsx')
