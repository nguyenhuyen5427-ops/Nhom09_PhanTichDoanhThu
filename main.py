from pathlib import Path
from src.data_loader import DataLoader
from src.clean_data import export_all
from src.sales_analyzer import SalesAnalyzer
from src.sales_visualizer import SalesVisualizer

def main():
    try:
        print("=== BẮT ĐẦU CHƯƠNG TRÌNH PHÂN TÍCH DOANH THU ===")
        
        # Thiết lập đường dẫn tương đối từ vị trí file main.py
        base_path = Path(__file__).parent
        data_file = base_path / "data" / "train.csv"
        
        # Khởi tạo lần lượt 3 lớp theo đúng yêu cầu
        loader = DataLoader(data_file)
        loader.load_data()
        loader.clean_data()
        # Xuất dữ liệu đã làm sạch
        export_all(data_file, loader.df, base_path)
        analyzer = SalesAnalyzer(loader.df)
        analyzer.analyze_data()
        
        visualizer = SalesVisualizer(loader.df)
        visualizer.plot_charts()
        
        print("=== CHƯƠNG TRÌNH KẾT THÚC THÀNH CÔNG ===")
        
    except Exception as e:
        print(f"Lỗi nghiêm trọng tại luồng chính: {e}")

if __name__ == "__main__":
    main()

