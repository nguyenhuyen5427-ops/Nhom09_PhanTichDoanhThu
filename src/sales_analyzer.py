import logging
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SalesAnalyzer:
    def __init__(self, df=None):
        self.df = df

    @staticmethod
    def _parse_dates(dates):
        """Chuyển cột ngày về datetime mà không đảo tháng/ngày.

        - Đã là datetime (dữ liệu sạch trong bộ nhớ): giữ nguyên.
        - Chuỗi dd/mm/yyyy (dữ liệu thô) hoặc yyyy-mm-dd (CSV sạch): đọc đúng từng loại.
        Không dùng dayfirst=True với chuỗi ISO vì sẽ đảo tháng/ngày.
        """
        if pd.api.types.is_datetime64_any_dtype(dates):
            return dates
        parsed = pd.to_datetime(dates, format='%d/%m/%Y', errors='coerce')
        return parsed.fillna(pd.to_datetime(dates, format='%Y-%m-%d', errors='coerce'))

    def analyze_data(self):
        try:
            if self.df is None:
                raise ValueError("DataFrame đang trống hoặc chưa được nạp dữ liệu.")
            
            logging.info("Đang thực hiện phân tích dữ liệu...")
            
            # --- TỰ ĐỘNG CHUẨN HÓA VÀ TRÍCH XUẤT NĂM NẾU CỘT 'Year' CHƯA TỒN TẠI ---
            if 'Year' not in self.df.columns:
                self.df['Order Date'] = self._parse_dates(self.df['Order Date'])
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
            data["Order Date"] = self._parse_dates(data["Order Date"])

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

    # ==================================================================
    # PHẦN CỦA LY (Giai đoạn 2): Câu 3 & Câu 4
    # ==================================================================

    def _get_order_year(self):
        """Lấy năm đặt hàng mà không sửa self.df (dùng cột Year nếu đã có)."""
        if 'Year' in self.df.columns:
            return self.df['Year']

        dates = self.df['Order Date']
        if not pd.api.types.is_datetime64_any_dtype(dates):
            # Dữ liệu thô là dd/mm/yyyy; dữ liệu sạch xuất ra CSV là yyyy-mm-dd.
            # Không dùng dayfirst=True với chuỗi ISO vì sẽ đảo tháng/ngày.
            parsed = pd.to_datetime(dates, format='%d/%m/%Y', errors='coerce')
            dates = parsed.fillna(pd.to_datetime(dates, format='%Y-%m-%d', errors='coerce'))
        return dates.dt.year

    @staticmethod
    def _add_growth(yearly):
        """Thêm mức tăng tuyệt đối và % giữa năm đầu và năm cuối của bảng Nhóm x Năm."""
        first_year, last_year = yearly.columns.min(), yearly.columns.max()
        table = yearly.copy()
        table['Tổng'] = yearly.sum(axis=1)
        table['Tăng tuyệt đối'] = yearly[last_year] - yearly[first_year]
        # Năm đầu = 0 thì không tính được % (tránh chia cho 0)
        table['Tăng (%)'] = (
            table['Tăng tuyệt đối'] / yearly[first_year].where(yearly[first_year].ne(0)) * 100
        )
        return table, first_year, last_year

    def analyze_region(self):
        """Câu 3: Doanh thu theo khu vực (Region). Phân công: Ly."""
        try:
            if self.df is None or self.df.empty:
                logging.warning("Không có dữ liệu để phân tích khu vực.")
                return None

            missing = [c for c in ('Region', 'Sales') if c not in self.df.columns]
            if missing:
                logging.error("Thiếu cột cần thiết: %s", ", ".join(missing))
                return None

            data = self.df[['Region', 'Sales']].copy()
            data['Year'] = self._get_order_year()
            data = data.dropna(subset=['Region', 'Sales', 'Year'])
            data['Year'] = data['Year'].astype(int)

            yearly = data.pivot_table(
                index='Region', columns='Year', values='Sales',
                aggfunc='sum', fill_value=0
            )
            table, first_year, last_year = self._add_growth(yearly)
            table['Tỷ trọng (%)'] = table['Tổng'] / table['Tổng'].sum() * 100
            table = table.sort_values('Tổng', ascending=False)

            print("\n" + "=" * 55)
            print("--- PHẦN CỦA LY: CÂU 3 - DOANH THU THEO KHU VỰC ---")
            print("=" * 55)
            print(f"\nBảng doanh thu theo khu vực qua các năm "
                  f"(tăng trưởng tính từ {first_year} đến {last_year}):")
            print(table.round(2).to_string())

            best, worst = table.index[0], table.index[-1]
            fastest = table['Tăng (%)'].idxmax()
            print(
                f"\nKhu vực doanh thu cao nhất: {best} "
                f"({table.loc[best, 'Tổng']:,.2f}, {table.loc[best, 'Tỷ trọng (%)']:.2f}%)."
            )
            print(
                f"Khu vực doanh thu thấp nhất: {worst} "
                f"({table.loc[worst, 'Tổng']:,.2f}, {table.loc[worst, 'Tỷ trọng (%)']:.2f}%)."
            )
            print(
                f"Khu vực tăng nhanh nhất {first_year}-{last_year}: {fastest} "
                f"(+{table.loc[fastest, 'Tăng tuyệt đối']:,.2f}, "
                f"{table.loc[fastest, 'Tăng (%)']:.2f}%)."
            )

            return {"region_table": table, "region_by_year": yearly}

        except Exception as e:
            logging.error("Lỗi khi phân tích doanh thu theo khu vực: %s", e)
            return None

    def analyze_top_subcategory(self, top_n=5):
        """Câu 4: Top 5 Sub-Category tăng trưởng mạnh nhất. Phân công: Ly.

        Xếp hạng theo MỨC TĂNG TUYỆT ĐỐI (năm đầu -> năm cuối) và hiển thị kèm
        % tăng, vì chỉ xếp theo % sẽ bị nhiễu bởi các nhóm có doanh thu gốc nhỏ.
        """
        try:
            if self.df is None or self.df.empty:
                logging.warning("Không có dữ liệu để phân tích Sub-Category.")
                return None

            missing = [c for c in ('Sub-Category', 'Sales') if c not in self.df.columns]
            if missing:
                logging.error("Thiếu cột cần thiết: %s", ", ".join(missing))
                return None

            data = self.df[['Sub-Category', 'Sales']].copy()
            data['Year'] = self._get_order_year()
            data = data.dropna(subset=['Sub-Category', 'Sales', 'Year'])
            data['Year'] = data['Year'].astype(int)

            yearly = data.pivot_table(
                index='Sub-Category', columns='Year', values='Sales',
                aggfunc='sum', fill_value=0
            )
            table, first_year, last_year = self._add_growth(yearly)

            top_abs = table.sort_values('Tăng tuyệt đối', ascending=False).head(top_n)
            top_pct = table.sort_values('Tăng (%)', ascending=False).head(top_n)
            top_total = table.sort_values('Tổng', ascending=False).head(top_n)

            print("\n" + "=" * 55)
            print(f"--- PHẦN CỦA LY: CÂU 4 - TOP {top_n} SUB-CATEGORY ---")
            print("=" * 55)
            print(f"\n[Bảng chính] Top {top_n} theo mức tăng tuyệt đối "
                  f"{first_year} -> {last_year} (kèm % tăng):")
            print(top_abs.round(2).to_string())

            print(f"\n[Đối chiếu] Top {top_n} nếu chỉ xếp theo % tăng "
                  f"(dễ bị nhiễu bởi nhóm có doanh thu gốc nhỏ):")
            print(top_pct.round(2).to_string())

            print(f"\n[Tham khảo] Top {top_n} theo tổng doanh thu cả giai đoạn:")
            print(top_total.round(2).to_string())

            leader = top_abs.index[0]
            pct_leader = top_pct.index[0]
            print(
                f"\nNhận xét: {leader} tăng nhiều nhất về giá trị tuyệt đối "
                f"(+{top_abs.loc[leader, 'Tăng tuyệt đối']:,.2f}, "
                f"{top_abs.loc[leader, 'Tăng (%)']:.2f}%)."
            )
            base = table.loc[pct_leader, first_year]
            if pct_leader == leader:
                print(
                    f"{pct_leader} cũng dẫn đầu về % tăng ({top_pct.loc[pct_leader, 'Tăng (%)']:.2f}%), "
                    f"nhưng doanh thu năm {first_year} chỉ {base:,.2f} nên % lớn một phần do mức gốc thấp; "
                    f"nên đọc cùng mức tăng tuyệt đối."
                )
            else:
                print(
                    f"{pct_leader} có % tăng cao nhất ({top_pct.loc[pct_leader, 'Tăng (%)']:.2f}%) "
                    f"nhưng doanh thu năm {first_year} chỉ {base:,.2f}, nên % bị phóng đại bởi mức gốc thấp."
                )
            decliners = table[table['Tăng tuyệt đối'] < 0]
            if not decliners.empty:
                print("Nhóm giảm doanh thu: " + ", ".join(
                    f"{name} ({row['Tăng tuyệt đối']:,.2f})"
                    for name, row in decliners.iterrows()
                ) + ".")

            return {
                "subcategory_table": table,
                "top_by_absolute_growth": top_abs,
                "top_by_percent_growth": top_pct,
                "top_by_total": top_total,
            }

        except Exception as e:
            logging.error("Lỗi khi phân tích Top Sub-Category: %s", e)
            return None

    def analyze_region_and_subcategory(self):
        """Chạy Câu 3 và Câu 4 (phần của Ly)."""
        return {
            "cau3": self.analyze_region(),
            "cau4": self.analyze_top_subcategory(),
        }