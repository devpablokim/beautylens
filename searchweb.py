import streamlit as st
import pandas as pd
import requests
import os
from urllib.parse import quote
import io

st.set_page_config(page_title="Beauty Lens", layout="wide")

st.markdown("<h1 style='text-align: left; color: #FF69B4;'>Beauty Lens</h1>", unsafe_allow_html=True)

query = st.text_input("검색어를 입력하세요:", "")

def fetch_all_product_data(query):
    encoded_query = quote(query)
    base_url = "https://www.hwahae.co.kr/_next/data/MgkRfo8mFXRFxum_el3Tb/search.json"

    headers = {
        "accept": "*/*",
        "referer": f"https://www.hwahae.co.kr/search?q={encoded_query}",
        "user-agent": "Mozilla/5.0",
        "x-nextjs-data": "1",
    }

    cookies = {
        "_tt_enable_cookie": "1",
        "_ttp": "01JN5J6H0VYVFQY17YEXJCQF65_.tt.2",
        "_ga": "GA1.1.1064689440.1740722358",
    }

    all_products = []
    offset = 0
    limit = 20
    total_count = 1

    while offset < total_count:
        params = {"q": query, "type": "products", "offset": offset, "limit": limit}
        response = requests.get(base_url, headers=headers, cookies=cookies, params=params)

        if response.status_code != 200:
            return []

        data = response.json()
        
        try:
            products_data = data["pageProps"]["products"]
            products = products_data["products"]
            pagination_info = products_data["meta"]["pagination"]
            total_count = pagination_info["total_count"]
        except KeyError:
            return []

        if not products:
            break

        all_products.extend(products)
        offset += limit

    return all_products

def convert_df_to_csv(df):
    """
    데이터프레임을 CSV 바이너리 파일로 변환하여 다운로드 가능하게 함
    """
    output = io.BytesIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)
    return output

if query:
    products = fetch_all_product_data(query)

    if products:
        st.subheader(f"🔎 '{query}' 검색 결과")

        df = pd.DataFrame(products)

        df = df.drop(columns=["uid"], errors="ignore")

        df.rename(columns={
            "reviewCount": "리뷰 수",
            "avgRatings": "별점",
            "buyInfo": "구매정보",
            "product_capacity": "용량",
            "product_price": "가격"
        }, inplace=True)

        # 📥 CSV 다운로드 버튼 (위쪽으로 배치)
        csv_file = convert_df_to_csv(df)
        st.download_button(
            label="📥 CSV로 저장",
            data=csv_file,
            file_name=f"{query}.csv",
            mime="text/csv",
        )

        # ✅ 검색 결과 리스트 표시
        for index, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([2, 5])

                with col1:
                    st.image(row["imageUrl"], width=200)

                with col2:
                    st.write(f"### {row['productName']}")
                    st.write(f"⭐ **별점 {row['별점']}** | 📝 리뷰 {row['리뷰 수']}개")
                    st.write(f"💰 **가격**: {row['가격']}원 | 📦 **용량**: {row['용량']}")
                    st.write(f"🛒 **구매정보**: {row['구매정보']}")

                    if "id" in row:
                        product_link = f"https://www.hwahae.co.kr/products/{row['id']}"
                        st.markdown(f"[🔗 제품 상세페이지 바로가기]({product_link})", unsafe_allow_html=True)
                    else:
                        st.warning("⚠ 제품 ID가 없어 상세페이지 링크를 생성할 수 없습니다.")
                    
                    st.write("---")

    else:
        st.warning("❌ 검색 결과가 없습니다.")
