# Phân tích Doanh thu và xu hướng bán hàng 
Dự án phân tích dữ liệu bán hàng nhằm tổng hợp doanh thu theo thời gian, nhận diện xu hướng tăng giảm dài hạn, đo lường tốc độ tăng trưởng (MoM, YoY) và tìm ra tính mùa vụ với các tháng / quý cao điểm và thấp điểm lặp lại qua từng năm. Kết quả được xuất ra dưới dạng biểu đồ và báo cáo để hỗ trợ ra quyết định kinh doanh.
## Yêu cầu hệ thống
- Python 3.10 trở lên
- pip (trình quản lý thư viện)
- Hệ điều hành: Windows / macOS / Linux
## Cài đặt thư viện
## Chạy chương trình
## Cấu trúc thư mục
## Mô tả chức năng chính
 Chuẩn bị dữ liệu
Đọc file CSV/Excel, loại bỏ dòng trùng, xử lý giá trị thiếu, chuẩn hóa kiểu ngày, tính doanh thu revenue = quantity × unit_price, rồi tổng hợp thành chuỗi doanh thu theo tuần / tháng / quý.

 Phân tích xu hướng (trend.py)
Tính đường trung bình động (Moving Average) để làm mượt biến động ngắn hạn.
Ước lượng đường xu hướng dài hạn bằng hồi quy tuyến tính và cho biết doanh thu đang tăng, giảm hay đi ngang.
Xác định các điểm đỉnh, điểm đáy và điểm đảo chiều đáng chú ý.
 Phân tích tăng trưởng (growth.py)
MoM: tăng trưởng so với tháng trước.
YoY: tăng trưởng so với cùng kỳ năm trước.
CAGR: tốc độ tăng trưởng kép hằng năm trong toàn bộ giai đoạn.
Doanh thu lũy kế và đóng góp của từng nhóm sản phẩm vào mức tăng trưởng.
 Phân tích tính mùa vụ (seasonality.py)
Phân rã chuỗi thời gian thành 3 thành phần: xu hướng, mùa vụ và phần dư.
Tính chỉ số mùa vụ cho từng tháng (giá trị > 1 là tháng cao điểm, < 1 là tháng thấp điểm).
Phân tích mẫu hình theo ngày trong tuần và theo quý.
Heatmap doanh thu theo tháng × năm để so sánh các năm với nhau.
 Trực quan hóa và báo cáo

Xuất biểu đồ vào results/charts/ và bảng số liệu tổng hợp vào results/report.xlsx.
