import streamlit as st
import pandas as pd
import re

# Cấu hình giao diện
st.set_page_config(page_title="Tool Dự Đoán Dữ Liệu", layout="wide")
st.title("📊 Tool Dự Đoán Độ Phình To Dữ Liệu & Thời Gian Truy Vấn")

# Khu vực upload file
uploaded_file = st.file_uploader("📂 Chọn file dữ liệu (.xlsx, .xls, .csv)", type=["csv", "xlsx", "xls"])


# Hàm lọc lấy số từ chuỗi (ví dụ: chuyển "50 ms" thành 50.0)
def clean_time_value(val):
    if pd.isna(val):
        return 0.0
    match = re.search(r"([\d\.]+)", str(val))
    return float(match.group(1)) if match else 0.0


if uploaded_file is not None:
    try:
        # Đọc file
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # ⚠️ QUAN TRỌNG: Xóa các dòng trống (blank rows) có trong file Excel của bạn
        df.dropna(how='all', inplace=True)

        st.success("Tải file thành công!")

        # Thanh điều khiển
        st.sidebar.header("⚙️ Thiết lập dự đoán")
        years_to_predict = st.sidebar.slider("Chọn số năm:", min_value=1, max_value=10, value=5)
        months = years_to_predict * 12

        if st.sidebar.button("🚀 Chạy dự đoán"):
            # Chuyển tên cột về chữ thường để dễ tìm kiếm
            cols = df.columns.astype(str).str.lower()

            # Tự động nhận diện các cột cần thiết
            col_table = df.columns[cols.str.contains('table')].tolist()[0]
            col_curr = df.columns[cols.str.contains('tổng số bản ghi')].tolist()[0]
            col_growth = df.columns[cols.str.contains('tăng trung bình')].tolist()[0]

            # Kiểm tra xem file có cột time_query_now không
            col_time_now = df.columns[cols.str.contains('time_query_now')].tolist()
            col_time_now = col_time_now[0] if col_time_now else None

            if not col_time_now:
                st.warning("⚠️ File của bạn đang thiếu cột 'time_query_now'. Tool sẽ chỉ dự đoán số lượng bản ghi.")

            # Tạo DataFrame mới chứa kết quả với các cột y hệt form bạn muốn
            result_df = pd.DataFrame()
            result_df['Table'] = df[col_table]
            result_df['Tổng số bản ghi hiện tại'] = df[col_curr]

            col_pred_rows = f"Sau {years_to_predict} năm"
            col_pred_time = f"time_query_{years_to_predict}"

            pred_rows_list = []
            time_now_list = []
            pred_time_list = []

            # Duyệt qua từng dòng để tính toán
            for index, row in df.iterrows():
                # Xử lý các giá trị NaN (nếu có)
                curr = float(row[col_curr]) if pd.notna(row[col_curr]) else 0
                growth = float(row[col_growth]) if pd.notna(row[col_growth]) else 0

                # Tính số bản ghi tương lai
                pred_rows = curr + (growth * months)
                pred_rows_list.append(int(pred_rows))

                # Tính thời gian truy vấn tương lai
                if col_time_now:
                    time_now_val = clean_time_value(row[col_time_now])
                    # Lưu lại thời gian hiện tại có chữ "ms"
                    time_now_list.append(
                        f"{int(time_now_val)} ms" if time_now_val.is_integer() else f"{time_now_val:.2f} ms")

                    # Tính thời gian dự kiến (giả định tỷ lệ thuận O(N))
                    ratio = pred_rows / curr if curr > 0 else 1
                    pred_time = time_now_val * ratio
                    pred_time_list.append(f"{int(pred_time)} ms" if pred_time.is_integer() else f"{pred_time:.2f} ms")

            # Gắn dữ liệu đã tính toán vào bảng kết quả
            result_df[col_pred_rows] = pred_rows_list
            if col_time_now:
                result_df['time_query_now'] = time_now_list
                result_df[col_pred_time] = pred_time_list

            st.subheader(f"📈 Kết quả dự đoán")
            # Hiển thị bảng kết quả ra màn hình
            st.dataframe(result_df, width="stretch", hide_index=True)

            # Nút tải file Excel/CSV về máy
            csv_data = result_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Tải xuống bảng kết quả (CSV)",
                data=csv_data,
                file_name=f"ket_qua_du_doan_{years_to_predict}_nam.csv",
                mime="text/csv",
            )

    except Exception as e:
        st.error(f"Đã xảy ra lỗi khi đọc file: Hãy đảm bảo file của bạn có đủ các cột cần thiết. Chi tiết lỗi: {e}")