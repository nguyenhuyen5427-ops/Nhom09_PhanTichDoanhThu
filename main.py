
from pathlib import Path

from src.data_loader import DataLoader
from src.clean_data import export_all
from src.sales_analyzer import SalesAnalyzer
from src.sales_visualizer import SalesVisualizer


def main():
    try:
        print("=== BẮT ĐẦU CHƯƠNG TRÌNH PHÂN TÍCH DOANH THU ===")

        # 1. Thiết lập đường dẫn
        base_path = Path(__file__).parent
        data_file = base_path / "data" / "train.csv"
        output_dir = base_path / "output" / "charts"

        # 2. Đọc và làm sạch dữ liệu
        loader = DataLoader(data_file)
        loader.load_data()
        loader.clean_data()
        loader.remove_duplicates()

        # Xuất dữ liệu đã làm sạch
        export_all(data_file, loader.df, base_path)

        # 3. Khởi tạo bộ phân tích
        analyzer = SalesAnalyzer(loader.df)

        # Chạy phân tích chung của nhóm
        analyzer.analyze_data()

        # 4. Lấy kết quả phân tích của Ly

        print("\n=== PHÂN TÍCH CÂU 3 ===")
        cau3 = analyzer.analyze_region()

        print("\n=== PHÂN TÍCH CÂU 5 ===")
        cau5 = analyzer.analyze_seasonality()

        print("\n=== PHÂN TÍCH CÂU 6 ===")
        cau6 = analyzer.analyze_segment_seasonality()

        print("\n=== PHÂN TÍCH CÂU 7 ===")

        top_category = (
            loader.df.groupby("Category")["Sales"]
            .sum()
            .idxmax()
        )

        print(f"Danh mục có doanh thu cao nhất: {top_category}")

        cau7 = analyzer.analyze_top_category_monthly(top_category)

        # 5. Kiểm tra kết quả phân tích
        results = {
            "Câu 3": cau3,
            "Câu 5": cau5,
            "Câu 6": cau6,
            "Câu 7": cau7
        }

        failed = [
            name for name, result in results.items()
            if result is None
        ]

        if failed:
            raise ValueError(
                "Không có kết quả phân tích cho: "
                + ", ".join(failed)
            )

        # 6. Khởi tạo bộ trực quan hóa
        visualizer = SalesVisualizer(
            loader.df,
            output_dir=output_dir
        )

        # 7. Vẽ biểu đồ của Thành
        print("\n=== TRỰC QUAN HÓA CỦA THÀNH ===")
        visualizer.plot_charts()

        # 8. Vẽ biểu đồ của Ly
        print("\n=== TRỰC QUAN HÓA CỦA LY ===")

        visualizer.plot_cau3_region_sales(cau3)
        visualizer.plot_cau5_seasonality(cau5)
        visualizer.plot_segment_seasonality(cau6)
        visualizer.plot_cau7_category_monthly(cau7)

        # 9. Kiểm tra ảnh biểu đồ của Ly
        expected_files = [
            "cau3_doanh_thu_theo_khu_vuc.png",
            "cau5_tinh_mua_vu.png",
            "cau6_mua_vu_theo_phan_khuc.png",
            "cau7_chu_ky_doanh_thu.png"
        ]

        missing_files = [
            name for name in expected_files
            if not (output_dir / name).exists()
        ]

        if missing_files:
            raise FileNotFoundError(
                "Chưa tạo được các biểu đồ: "
                + ", ".join(missing_files)
            )

        print("\n=== KIỂM TRA HOÀN TẤT ===")
        print("Đã tạo đủ 4 biểu đồ của Ly:")
        for name in expected_files:
            print(f"- {name}")

        print("\n=== CHƯƠNG TRÌNH KẾT THÚC THÀNH CÔNG ===")

    except Exception as e:
        print(f"Lỗi nghiêm trọng tại luồng chính: {e}")


if __name__ == "__main__":
    main()
