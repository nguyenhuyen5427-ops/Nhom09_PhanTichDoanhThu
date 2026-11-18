import logging
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SalesVisualizer:
    def __init__(self, df=None, output_dir="output/charts"):
        self.df = df
        self.output_dir = Path(output_dir)

    def plot_charts(self):
        try:
            if self.df is None or self.df.empty:
                raise ValueError("Không có dữ liệu để vẽ biểu đồ.")

            # Tạo thư mục lưu ảnh nếu chưa tồn tại
            self.output_dir.mkdir(parents=True, exist_ok=True)
            logging.info("Đang khởi tạo và xuất các biểu đồ trực quan (300 DPI)...")

            # Đảm bảo có cột Year nếu dữ liệu chưa trích xuất sẵn
            if 'Year' not in self.df.columns:
                self.df['Order Date'] = pd.to_datetime(self.df['Order Date'], format='mixed', dayfirst=True)
                self.df['Year'] = self.df['Order Date'].dt.year

            # --- PHẦN CỦA THÀNH (Câu 1, 2, 4) ---
            self._plot_cau1_yearly_sales()
            self._plot_cau2_category_sales()
            self._plot_cau4_top5_subcategory()

            

            logging.info(f"Đã xuất toàn bộ biểu đồ thành công vào thư mục: {self.output_dir}")

        except ValueError as e:
            logging.warning(f"Cảnh báo trực quan: {e}")
        except Exception as e:
            logging.error(f"Lỗi khi vẽ biểu đồ: {e}")

    def _plot_cau1_yearly_sales(self):
        """Câu 1: Line chart tổng doanh thu theo năm (2015-2018)."""
        yearly = self.df.groupby('Year')['Sales'].sum().reset_index()

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(
            yearly['Year'].astype(str),
            yearly['Sales'],
            marker='o',
            linewidth=2.5,
            markersize=8,
            color='#1f77b4',
            label='Tổng doanh thu ($)'
        )

        # Gắn nhãn giá trị trên từng điểm dữ liệu
        for i, row in yearly.iterrows():
            ax.annotate(
                f"${row['Sales']:,.0f}",
                (str(row['Year']), row['Sales']),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=9,
                fontweight='bold'
            )

        ax.set_title('Tổng Doanh Thu Theo Năm (2015 - 2018)', fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Năm', fontsize=11)
        ax.set_ylabel('Doanh thu (USD)', fontsize=11)
        ax.set_ylim(0, yearly['Sales'].max() * 1.18)
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(loc='upper left')

        plt.tight_layout()
        plt.savefig(self.output_dir / "cau1_doanh_thu_theo_nam.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

    def _plot_cau2_category_sales(self):
        """Câu 2: Bar chart so sánh doanh thu 3 danh mục (Category)."""
        cat_sales = self.df.groupby('Category')['Sales'].sum().sort_values(ascending=False).reset_index()
        colors = ['#2b5c8f', '#4a90e2', '#7fb3d5']

        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(cat_sales['Category'], cat_sales['Sales'], color=colors, width=0.5, label='Doanh thu theo danh mục')

        # Gắn nhãn số liệu trên đỉnh mỗi cột
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"${height:,.0f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 5),
                textcoords="offset points",
                ha='center',
                va='bottom',
                fontsize=10,
                fontweight='bold'
            )

        ax.set_title('So Sánh Tổng Doanh Thu Theo Danh Mục Sản Phẩm', fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Danh mục (Category)', fontsize=11)
        ax.set_ylabel('Doanh thu (USD)', fontsize=11)
        ax.set_ylim(0, cat_sales['Sales'].max() * 1.15)
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        ax.legend(loc='upper right')

        plt.tight_layout()
        plt.savefig(self.output_dir / "cau2_doanh_thu_danh_muc.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

    def _plot_cau4_top5_subcategory(self):
        """Câu 4: Bar chart ngang Top 5 Sub-Category có doanh thu cao nhất."""
        top5 = (
            self.df.groupby('Sub-Category')['Sales']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .sort_values(ascending=True)  # Đảo ngược để cột cao nhất nằm trên cùng
            .reset_index()
        )

        fig, ax = plt.subplots(figsize=(9, 5))
        bars = ax.barh(top5['Sub-Category'], top5['Sales'], color='#2e8b57', height=0.55, label='Doanh thu Top 5')

        # Gắn nhãn giá trị bên phải mỗi thanh ngang
        for bar in bars:
            width = bar.get_width()
            ax.annotate(
                f"${width:,.0f}",
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(6, 0),
                textcoords="offset points",
                ha='left',
                va='center',
                fontsize=9.5,
                fontweight='bold'
            )

        ax.set_title('Top 5 Nhóm Sản Phẩm Phụ (Sub-Category) Có Doanh Thu Cao Nhất', fontsize=13, fontweight='bold', pad=15)
        ax.set_xlabel('Doanh thu (USD)', fontsize=11)
        ax.set_ylabel('Nhóm sản phẩm phụ (Sub-Category)', fontsize=11)
        ax.set_xlim(0, top5['Sales'].max() * 1.18)
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        ax.legend(loc='lower right')

        plt.tight_layout()
        plt.savefig(self.output_dir / "cau4_top5_sub_category.png", dpi=300, bbox_inches='tight')
        plt.close(fig)

    def plot_cau3_region_sales(self, result):
        """Câu 3: Biểu đồ doanh thu theo khu vực."""

        if not result or result.get("region_table") is None:
            logging.warning("Không có dữ liệu Câu 3.")
            return

        table = result["region_table"]

        if table.empty or "Tổng" not in table.columns:
            logging.warning("Bảng doanh thu khu vực không hợp lệ.")
            return

        region_sales = table["Tổng"].sort_values(ascending=True)

        fig, ax = plt.subplots(figsize=(9, 5))

        bars = ax.barh(
            region_sales.index,
            region_sales.values,
            color="#4A90E2",
            label="Tổng doanh thu"
        )

        for bar in bars:
            width = bar.get_width()
            ax.annotate(
                f"${width:,.0f}",
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(6, 0),
                textcoords="offset points",
                va="center",
                fontsize=9
            )

        ax.set_title("Tổng Doanh Thu Theo Khu Vực (2015–2018)")
        ax.set_xlabel("Doanh thu (USD)")
        ax.set_ylabel("Khu vực")
        ax.set_xlim(0, region_sales.max() * 1.18)
        ax.grid(axis="x", linestyle="--", alpha=0.5)
        ax.legend()

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "cau3_doanh_thu_theo_khu_vuc.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close(fig)

        logging.info("Đã xuất biểu đồ Câu 3.")

    def plot_cau5_seasonality(self, result):
        """Câu 5: Biểu đồ mùa vụ theo tháng và quý."""

        if not result:
            logging.warning("Không có dữ liệu Câu 5.")
            return

        monthly = result.get("monthly_seasonality")
        quarterly = result.get("quarterly_seasonality")

        if monthly is None or quarterly is None:
            logging.warning("Thiếu dữ liệu mùa vụ.")
            return

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        month_labels = [f"T{int(x)}" for x in monthly.index]
        bars1 = ax1.bar(
            month_labels,
            monthly.values,
            color="#4A90E2"
        )

        ax1.axhline(100, color="red", linestyle="--", label="Mức trung bình (100)")
        ax1.set_title("Chỉ số mùa vụ theo tháng")
        ax1.set_xlabel("Tháng")
        ax1.set_ylabel("Chỉ số mùa vụ")
        ax1.grid(axis="y", linestyle="--", alpha=0.4)
        ax1.legend()

        for bar in bars1:
            height = bar.get_height()
            ax1.annotate(
                f"{height:.1f}",
                (bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                fontsize=8
            )

        quarter_labels = [f"Q{int(x)}" for x in quarterly.index]
        bars2 = ax2.bar(
            quarter_labels,
            quarterly.values,
            color="#2E8B57"
        )

        ax2.axhline(100, color="red", linestyle="--", label="Mức trung bình (100)")
        ax2.set_title("Chỉ số mùa vụ theo quý")
        ax2.set_xlabel("Quý")
        ax2.set_ylabel("Chỉ số mùa vụ")
        ax2.grid(axis="y", linestyle="--", alpha=0.4)
        ax2.legend()

        for bar in bars2:
            height = bar.get_height()
            ax2.annotate(
                f"{height:.1f}",
                (bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                fontsize=9
            )

        fig.suptitle("Phân Tích Tính Mùa Vụ Doanh Thu Theo Tháng Và Quý")
        plt.tight_layout()
        plt.savefig(
            self.output_dir / "cau5_tinh_mua_vu.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close(fig)

        logging.info("Đã xuất biểu đồ Câu 5.")

    def plot_segment_seasonality(self, segment_seasonality):
        """Câu 6: So sánh mùa vụ theo phân khúc khách hàng."""

        if segment_seasonality is None or segment_seasonality.empty:
            logging.warning("Không có dữ liệu Câu 6.")
            return

        required = ["Segment", "Month", "Sales"]

        if not all(col in segment_seasonality.columns for col in required):
            logging.warning("Dữ liệu Câu 6 thiếu cột cần thiết.")
            return

        pivot_df = segment_seasonality.pivot_table(
            index="Month",
            columns="Segment",
            values="Sales",
            aggfunc="sum"
        ).reindex(range(1, 13))

        monthly_mean = pivot_df.mean(axis=0).replace(0, float("nan"))
        seasonal_index = pivot_df.div(monthly_mean, axis=1) * 100

        fig, ax = plt.subplots(figsize=(11, 6))

        for segment in seasonal_index.columns:
            ax.plot(
                seasonal_index.index,
                seasonal_index[segment],
                marker="o",
                linewidth=2,
                label=segment
            )

        ax.axhline(
            100,
            color="red",
            linestyle="--",
            alpha=0.7,
            label="Mức trung bình (100)"
        )

        ax.set_title("So Sánh Tính Mùa Vụ Theo Phân Khúc Khách Hàng")
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Chỉ số mùa vụ")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels([f"Tháng {i}" for i in range(1, 13)])
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Phân khúc khách hàng")

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "cau6_mua_vu_theo_phan_khuc.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close(fig)

        logging.info("Đã xuất biểu đồ Câu 6.")

    def plot_cau7_category_monthly(self, result):
        """Câu 7: Doanh thu theo tháng của danh mục đứng đầu."""

        if not result:
            logging.warning("Không có dữ liệu Câu 7.")
            return

        monthly_index = result.get("monthly_index_by_year")
        average_index = result.get("average_monthly_index")

        if monthly_index is None or average_index is None:
            logging.warning("Thiếu dữ liệu Câu 7.")
            return

        if monthly_index.empty or average_index.empty:
            logging.warning("Dữ liệu Câu 7 trống.")
            return

        months = [f"Tháng {i}" for i in range(1, 13)]

        monthly_index = monthly_index.reindex(columns=months)
        average_index = average_index.reindex(months)

        fig, ax = plt.subplots(figsize=(12, 6))

        for year, row in monthly_index.iterrows():
            ax.plot(
                range(1, 13),
                row.values,
                marker="o",
                linewidth=1.8,
                label=str(year)
            )

        ax.plot(
            range(1, 13),
            average_index.values,
            color="black",
            linestyle="--",
            linewidth=3,
            marker="s",
            label="Trung bình 2015–2018"
        )

        ax.axhline(100, color="red", linestyle=":", label="Mức trung bình (100)")

        category = result.get("category", "Danh mục đứng đầu")

        ax.set_title(f"Phân Tích Chu Kỳ Doanh Thu Theo Tháng - {category}")
        ax.set_xlabel("Tháng")
        ax.set_ylabel("Chỉ số mùa vụ")
        ax.set_xticks(range(1, 13))
        ax.set_xticklabels(months)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend(title="Năm", loc="best")

        plt.tight_layout()
        plt.savefig(
            self.output_dir / "cau7_chu_ky_doanh_thu.png",
            dpi=300,
            bbox_inches="tight"
        )
        plt.close(fig)

        logging.info("Đã xuất biểu đồ Câu 7.")
