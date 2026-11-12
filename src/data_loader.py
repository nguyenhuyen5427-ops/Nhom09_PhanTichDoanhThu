import logging
from pathlib import Path

import pandas as pd

try:
    from date_cleaner import DateCleaner        # chạy từ trong thư mục src
except ModuleNotFoundError:
   from src.date_cleaner import DateCleaner  # type: ignore
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class DataLoader:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.df = None
        self.date_report = {}

    def load_data(self):
        try:
            if not self.file_path.exists():
                raise FileNotFoundError(f"Không tìm thấy file tại đường dẫn: {self.file_path}")

            logging.info(f"Đang tiến hành đọc file từ: {self.file_path}")
            self.df = pd.read_csv(self.file_path)
            logging.info(f"Đọc dữ liệu thành công! Kích thước: {self.df.shape}")
            return self.df

        except FileNotFoundError as e:
            logging.error(f"Lỗi File: {e}")
            return None
        except Exception as e:
            logging.error(f"Đã xảy ra lỗi không mong muốn khi đọc dữ liệu: {e}")
            return None

    def inspect_raw_data(self):
        """Kiểm tra dữ liệu thô (Phân công: Thành)."""
        if self.df is None:
            logging.error("Chưa có dữ liệu để kiểm tra!")
            return

        print("\n--- NHẬT KÝ KIỂM TRA DỮ LIỆU THÔ (Thành) ---")
        print(f"Số dòng và số cột: {self.df.shape}")
        print("\nSố lượng giá trị thiếu (Null) ở mỗi cột:")
        print(self.df.isnull().sum())
        print("\nKiểu dữ liệu của các cột:")
        print(self.df.dtypes)
        print("-" * 45)

    def clean_data(self):
        """Chuẩn hóa Order Date / Ship Date (Phân công: Trang)."""
        if self.df is None:
            logging.error("Chưa có dữ liệu để làm sạch!")
            return None

        cleaner = DateCleaner(self.df)
        self.df = cleaner.clean_dates()
        self.date_report = cleaner.report
        return self.df

    def remove_duplicates(self):
        """Xử lý dữ liệu trùng lặp (Phân công: Ly)."""
        if self.df is None or self.df.empty:
            logging.warning("Chưa có dữ liệu để xử lý trùng lặp.")
            return self.df

        initial_rows = len(self.df)
        logging.info(f"[Ly] Số dòng trước khi xử lý trùng lặp: {initial_rows}")

        cols_to_check = [col for col in self.df.columns if col != 'Row ID']

        dup_mask = self.df.duplicated(subset=cols_to_check, keep='first')
        removed_ids = self.df.loc[dup_mask, 'Row ID'].tolist()

        self.df = self.df[~dup_mask].reset_index(drop=True)

        final_rows = len(self.df)
        removed_rows = initial_rows - final_rows

        if removed_rows > 0:
            logging.info(
                f"[Ly] Quyết định: Phát hiện {removed_rows} bản ghi trùng lặp toàn bộ thông tin đơn hàng "
                f"(trừ Row ID). Row ID bị xóa: {removed_ids}."
            )
            logging.info("[Ly] Quyết định xử lý: Giữ lại bản ghi xuất hiện đầu tiên, xóa các bản ghi sau.")
        else:
            logging.info("[Ly] Không phát hiện bản ghi trùng lặp.")

        logging.info(f"[Ly] Số dòng sau khi xóa trùng lặp: {final_rows}")
        return self.df


if __name__ == "__main__":
    data_path = Path(__file__).resolve().parent.parent / "data" / "train.csv"
    loader = DataLoader(data_path)
    loader.load_data()
    loader.inspect_raw_data()
    loader.clean_data()
    loader.remove_duplicates()