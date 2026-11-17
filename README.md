# Phân tích Doanh thu và xu hướng bán hàng 
Dự án phân tích dữ liệu bán hàng nhằm tổng hợp doanh thu theo thời gian, nhận diện xu hướng tăng giảm dài hạn, đo lường tốc độ tăng trưởng (MoM, YoY) và tìm ra tính mùa vụ với các tháng / quý cao điểm và thấp điểm lặp lại qua từng năm. Kết quả được xuất ra dưới dạng biểu đồ và báo cáo để hỗ trợ ra quyết định kinh doanh.
## Nguồn dữ liệu
- Tệp gốc: `data/train.csv` (bộ dữ liệu bán hàng Superstore Sales, giai đoạn 2015–2018).
- Nguồn: https://www.kaggle.com/datasets/rohitsahoo/sales-forecasting/data.
- Tệp sau khi làm sạch: `data/processed/train_clean.csv`.
## Cài đặt thư viện
Yêu cầu: Python 3.10 trở lên, pip (Windows / macOS / Linux).

```bash
pip install -r requirements.txt
```

Các thư viện chính: `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl`.

## Chạy chương trình
Mở terminal tại **thư mục gốc** của dự án và chạy:

```bash
python main.py
```

Chương trình lần lượt đọc dữ liệu, làm sạch, loại bỏ dòng trùng, xuất dữ liệu sạch, phân tích 7 câu hỏi và lưu biểu đồ vào `output/charts/`.

## Cấu trúc thư mục
```
Nhom09_PhanTichDoanhThu/
├── main.py                     # Điểm chạy chính
├── requirements.txt            # Danh sách thư viện cần cài
├── README.md
├── data/
│   ├── train.csv               # Dữ liệu gốc
│   └── processed/
│       └── train_clean.csv     # Dữ liệu sau khi làm sạch
├── src/
│   ├── data_loader.py          # Lớp DataLoader: đọc, làm sạch, loại trùng
│   ├── clean_data.py           # Xuất dữ liệu đã làm sạch (export_all)
│   ├── date_cleaner.py         # Chuẩn hóa kiểu ngày
│   ├── sales_analyzer.py       # Lớp SalesAnalyzer: phân tích 7 câu hỏi
│   └── sales_visualizer.py     # Lớp SalesVisualizer: vẽ biểu đồ
└── output/
    ├── cleaning_log.txt        # Nhật ký làm sạch dữ liệu
    └── charts/                 # Biểu đồ xuất ra
```
## Mô tả chức năng chính
### 1.Chuẩn bị dữ liệu
Đọc file CSV/Excel, loại bỏ dòng trùng, xử lý giá trị thiếu, chuẩn hóa kiểu ngày, tính doanh thu revenue = quantity × unit_price, rồi tổng hợp thành chuỗi doanh thu theo tuần / tháng / quý.
### 2.Phân tích xu hướng (trend.py)
Tính đường trung bình động (Moving Average) để làm mượt biến động ngắn hạn.
Ước lượng đường xu hướng dài hạn bằng hồi quy tuyến tính và cho biết doanh thu đang tăng, giảm hay đi ngang.
Xác định các điểm đỉnh, điểm đáy và điểm đảo chiều đáng chú ý.
### 3.Phân tích tăng trưởng (growth.py)
MoM: tăng trưởng so với tháng trước.
YoY: tăng trưởng so với cùng kỳ năm trước.
CAGR: tốc độ tăng trưởng kép hằng năm trong toàn bộ giai đoạn.
Doanh thu lũy kế và đóng góp của từng nhóm sản phẩm vào mức tăng trưởng.
### 4.Phân tích tính mùa vụ (seasonality.py)
Phân rã chuỗi thời gian thành 3 thành phần: xu hướng, mùa vụ và phần dư.
Tính chỉ số mùa vụ cho từng tháng (giá trị > 1 là tháng cao điểm, < 1 là tháng thấp điểm).
Phân tích mẫu hình theo ngày trong tuần và theo quý.
Heatmap doanh thu theo tháng × năm để so sánh các năm với nhau.
### 5.Trực quan hóa 
Xuất biểu đồ vào results/charts/ và bảng số liệu tổng hợp vào results/report.xlsx.
