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
        
            self.analyze_seasonality()

        except ValueError as e:
            logging.warning(f"Cảnh báo nghiệp vụ: {e}")
        except Exception as e:
            logging.error(f"Lỗi trong quá trình phân tích: {e}")




    def analyze_seasonality(self):
        """
        Phân tích tính mùa vụ doanh thu theo tháng và quý.
        Thành viên thực hiện: Trang - GD2.
        Sử dụng bảng Year x Month và Year x Quarter.
        Chuẩn hóa theo từng năm để hạn chế ảnh hưởng của xu hướng tăng trưởng.
        """

        try:
            if self.df is None or self.df.empty:
                logging.warning("Không có dữ liệu để phân tích mùa vụ.")
                return None

            # Kiểm tra các cột cần thiết
            required_columns = ["Order Date", "Sales"]

            missing_columns = [
                column for column in required_columns
                if column not in self.df.columns
            ]

            if missing_columns:
                logging.error(
                    "Thiếu cột cần thiết: %s",
                    ", ".join(missing_columns)
                )
                return None

            # Tạo bản sao để không thay đổi dữ liệu chung của nhóm
            data = self.df[required_columns].copy()

            # Chuẩn hóa dữ liệu ngày và doanh thu
            data["Order Date"] = pd.to_datetime(
                data["Order Date"],
                format="mixed",
                dayfirst=True,
                errors="coerce"
            )

            data["Sales"] = pd.to_numeric(
                data["Sales"],
                errors="coerce"
            )

            data = data.dropna(
                subset=required_columns
            ).copy()

            if data.empty:
                logging.warning("Không có dữ liệu hợp lệ để phân tích.")
                return None

            # Tách năm, tháng và quý
            data["Year"] = data["Order Date"].dt.year
            data["Month"] = data["Order Date"].dt.month
            data["Quarter"] = data["Order Date"].dt.quarter

            month_names = {
                1: "Tháng 1",
                2: "Tháng 2",
                3: "Tháng 3",
                4: "Tháng 4",
                5: "Tháng 5",
                6: "Tháng 6",
                7: "Tháng 7",
                8: "Tháng 8",
                9: "Tháng 9",
                10: "Tháng 10",
                11: "Tháng 11",
                12: "Tháng 12"
            }

            quarter_names = {
                1: "Quý I",
                2: "Quý II",
                3: "Quý III",
                4: "Quý IV"
            }

            # ==========================================
            # PHẦN 1: PHÂN TÍCH TÍNH MÙA VỤ THEO THÁNG
            # ==========================================

            # Tạo bảng Year x Month
            monthly_sales = data.pivot_table(
                index="Year",
                columns="Month",
                values="Sales",
                aggfunc="sum",
                fill_value=0
            ).reindex(
                columns=range(1, 13),
                fill_value=0
            )

            # Tính doanh thu trung bình tháng của từng năm
            monthly_mean = monthly_sales.mean(axis=1)

            # Chuẩn hóa doanh thu theo từng năm
            # Mức trung bình tháng của mỗi năm tương ứng với 100
            monthly_index = monthly_sales.div(
                monthly_mean.where(monthly_mean.ne(0)),
                axis=0
            ) * 100

            # Tính chỉ số mùa vụ trung bình của từng tháng qua các năm
            monthly_seasonality = monthly_index.mean(axis=0)

            # ==========================================
            # PHẦN 2: PHÂN TÍCH TÍNH MÙA VỤ THEO QUÝ
            # ==========================================

            # Tạo bảng Year x Quarter
            quarterly_sales = data.pivot_table(
                index="Year",
                columns="Quarter",
                values="Sales",
                aggfunc="sum",
                fill_value=0
            ).reindex(
                columns=range(1, 5),
                fill_value=0
            )

            # Tính doanh thu trung bình quý của từng năm
            quarterly_mean = quarterly_sales.mean(axis=1)

            # Chuẩn hóa doanh thu theo từng năm
            quarterly_index = quarterly_sales.div(
                quarterly_mean.where(quarterly_mean.ne(0)),
                axis=0
            ) * 100

            # Tính chỉ số mùa vụ trung bình của từng quý qua các năm
            quarterly_seasonality = quarterly_index.mean(axis=0)

            if (
                monthly_seasonality.dropna().empty
                or quarterly_seasonality.dropna().empty
            ):
                logging.warning("Không đủ dữ liệu để tính chỉ số mùa vụ.")
                return None

            # ==========================================
            # PHẦN 3: HIỂN THỊ KẾT QUẢ PHÂN TÍCH
            # ==========================================

            print("\n" + "=" * 55)
            print("--- PHẦN CỦA TRANG: PHÂN TÍCH MÙA VỤ ---")
            print("=" * 55)

            # Kết quả theo tháng
            print("\n[Theo tháng] Bảng doanh thu Year x Month:")

            print(
                monthly_sales.rename(
                    columns=month_names
                ).round(2).to_string()
            )

            print("\nBảng Year x Month sau khi chuẩn hóa:")

            print(
                monthly_index.rename(
                    columns=month_names
                ).round(2).to_string()
            )

            print("\nChỉ số mùa vụ trung bình theo tháng:")

            print(
                monthly_seasonality.rename(
                    index=month_names
                ).round(2).to_string()
            )

            highest_month = int(monthly_seasonality.idxmax())
            lowest_month = int(monthly_seasonality.idxmin())

            print(
                f"\nTháng có chỉ số mùa vụ cao nhất: "
                f"{month_names[highest_month]} "
                f"({monthly_seasonality.max():.2f})."
            )

            print(
                f"Tháng có chỉ số mùa vụ thấp nhất: "
                f"{month_names[lowest_month]} "
                f"({monthly_seasonality.min():.2f})."
            )

            # Kết quả theo quý
            print("\n[Theo quý] Bảng doanh thu Year x Quarter:")

            print(
                quarterly_sales.rename(
                    columns=quarter_names
                ).round(2).to_string()
            )

            print("\nBảng Year x Quarter sau khi chuẩn hóa:")

            print(
                quarterly_index.rename(
                    columns=quarter_names
                ).round(2).to_string()
            )

            print("\nChỉ số mùa vụ trung bình theo quý:")

            print(
                quarterly_seasonality.rename(
                    index=quarter_names
                ).round(2).to_string()
            )

            highest_quarter = int(quarterly_seasonality.idxmax())
            lowest_quarter = int(quarterly_seasonality.idxmin())

            print(
                f"\nQuý có chỉ số mùa vụ cao nhất: "
                f"{quarter_names[highest_quarter]} "
                f"({quarterly_seasonality.max():.2f})."
            )

            print(
                f"Quý có chỉ số mùa vụ thấp nhất: "
                f"{quarter_names[lowest_quarter]} "
                f"({quarterly_seasonality.min():.2f})."
            )

            print(
                "\nCách đọc chỉ số: 100 là mức doanh thu trung bình "
                "trong năm; chỉ số lớn hơn 100 là cao hơn mức trung bình, "
                "nhỏ hơn 100 là thấp hơn."
            )

            # Trả về kết quả để các phần khác có thể sử dụng nếu cần
            return {
                "monthly_sales": monthly_sales,
                "monthly_index_by_year": monthly_index,
                "monthly_seasonality": monthly_seasonality,
                "quarterly_sales": quarterly_sales,
                "quarterly_index_by_year": quarterly_index,
                "quarterly_seasonality": quarterly_seasonality
            }

        except Exception as e:
            logging.error(
                "Lỗi khi phân tích mùa vụ: %s",
                e
            )
            return None
