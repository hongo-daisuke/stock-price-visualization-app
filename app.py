import streamlit as st
import pandas as pd
import yfinance as yf
import altair as alt

@st.cache
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():

        # 会社の株価を取得
        tkr = yf.Ticker(tickers[company])

        # 選択された日数のデータを過去に遡って取得
        hist = tkr.history(period=f'{days}d')

        # インデックスのフォーマットを変更する
        hist.index = hist.index.strftime('%d %B %Y')

        # Closeのみ抽出
        hist = hist[['Close']]

        # カラム名を会社名に変更
        hist.columns = [company]
        hist.head()

        # 行と列を入れ替える
        hist = hist.T

        # インデックス名にNameを入れる
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

st.title('米国株価可視化アプリ')

st.sidebar.write("""
# GAFA株価
株価可視化ツール。以下のオプションから表示日数を指定できます。
""")

try:
    st.sidebar.write("""
    ## 表示日数選択
    """)
    days = st.sidebar.slider('日数', 1, 50, 25)

    st.write(f"""
    ### 過去 **{days}日間** のGAFA株価
    """)

    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    ymin, ymax = st.sidebar.slider('範囲を指定して下さい。', 0.0, 3500.0, (0.0, 3500.0))

    tickers = {
      'apple': 'AAPL',
      'facebook': 'FB',
      'google': 'GOOGL',
      'microsft': 'MSFT',
      'netfilix': 'NFLX',
      'amazon': 'AMZN',
    }
    df = get_data(days, tickers)

    companies = st.multiselect(
        '会社名を選択して下さい。',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )

    if not companies:
        st.error('一社は選択して下さい。')
    else:
        # カラム名で値を取得
        data = df.loc[companies]
        st.write('### 株価 (USD)', data.sort_index())

        # インデックスをリセット
        data = data.T.reset_index()

        # データの整形とインデックスの名前を変更
        data = pd.melt(data, id_vars=['Date']).rename(columns={'value': 'Stock Prices(USD)'})

        # 描画の設定を行う
        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x='Date:T',
                y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[ymin, ymax])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_column_width=True)
except Exception as e:
  st.error(f"""
           エラーが発生しました！\n
           エラー内容 : {e}
           """
  )