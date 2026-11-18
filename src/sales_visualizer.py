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
    def plot_segment_seasonality(self, segment_seasonality):
        """
        Vẽ biểu đồ so sánh tính mùa vụ (tháng) giữa các phân khúc khách hàng (Câu 6)
        """
        try:
            if segment_seasonality is None or segment_seasonality.empty:
                print("Không có dữ liệu để vẽ biểu đồ tính mùa vụ.")
                return
            
            plt.figure(figsize=(12, 6))
            
            # Dùng pivot để vẽ biểu đường biểu diễn theo từng Segment
            pivot_df = segment_seasonality.pivot(index='Month', columns='Segment', values='Sales')
            pivot_df.plot(kind='line', marker='o', figsize=(12, 6))
            
            plt.title('So sánh tính mùa vụ theo tháng giữa các phân khúc khách hàng', fontsize=14)
            plt.xlabel('Tháng (Month)', fontsize=12)
            plt.ylabel('Tổng doanh thu (Sales)', fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            plt.legend(title='Phân khúc khách hàng')
            plt.xticks(range(1, 13))
            plt.tight_layout()
            
            plt.show()
            
        except Exception as e:
            print(f"Lỗi khi vẽ biểu đồ tính mùa vụ: {e}"