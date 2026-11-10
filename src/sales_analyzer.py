import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SalesAnalyzer:
    def __init__(self, df=None):
        self.df = df

    def analyze_data(self):
        try:
            if self.df is None:
                raise ValueError("DataFrame đang trống hoặc chưa được nạp dữ liệu.")
            
            logging.info("Đang thực hiện phân tích dữ liệu...")
            
            # --- TỰ ĐỘNG CHUẨN HÓA VÀ TRÍCH XUẤT NĂM NẾU CỘT 'Year' CHƯA TỒN TẠI ---
            if 'Year' not in self.df.columns:
                self.df['Order Date'] = pd.to_datetime(self.df['Order Date'], format='mixed', dayfirst=True)
                self.df['Year'] = self.df['Order Date'].dt.year
            
            print("\n" + "="*45)
            print("=== BÁO CÁO PHÂN TÍCH DỮ LIỆU (GIAI ĐOẠN 2) ===")
            print("="*45)
            
            print("\n--- PHẦN CỦA THÀNH (Câu 1 & Câu 2) ---")
            
            # --- Câu 1: Tổng doanh thu theo năm & Tăng trưởng YoY ---
            yearly_sales = self.df.groupby('Year')['Sales'].sum().reset_index()
            yearly_sales['YoY (%)'] = yearly_sales['Sales'].pct_change() * 100
            
            print("\n[Câu 1] Tổng doanh thu theo năm và Tăng trưởng YoY:")
            print(yearly_sales.round({'Sales': 2, 'YoY (%)': 2}))

            # --- Câu 2: So sánh doanh thu 3 danh mục (Category) ---
            cat_total = self.df.groupby('Category')['Sales'].sum().reset_index()
            cat_total = cat_total.sort_values(by='Sales', ascending=False)
            
            print("\n[Câu 2a] Tổng doanh thu theo 3 danh mục (2015-2018):")
            print(cat_total.round({'Sales': 2}))

            cat_yearly = self.df.pivot_table(
                values='Sales', 
                index='Year', 
                columns='Category', 
                aggfunc='sum'
            )
            print("\n[Câu 2b] Chi tiết biến động doanh thu 3 danh mục qua các năm:")
            print(cat_yearly.round(2))
            
            print("-" * 45)

        except ValueError as e:
            logging.warning(f"Cảnh báo nghiệp vụ: {e}")
        except Exception as e:
            logging.error(f"Lỗi trong quá trình phân tích: {e}")