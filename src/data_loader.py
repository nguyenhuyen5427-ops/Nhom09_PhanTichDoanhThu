import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataLoader:
    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self.df = None
        self.log = []  

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

    def clean_data(self):
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
        
"""Chuẩn hóa Order Date và Ship Date cho dự án phân tích doanh thu."""


logger = logging.getLogger(__name__)


class DateCleaner:
    """Chuẩn hóa và kiểm tra hai cột ngày của bộ dữ liệu đơn hàng."""

    DATE_COLUMNS = ("Order Date", "Ship Date")
    START_DATE = pd.Timestamp("2015-01-03")
    END_DATE = pd.Timestamp("2018-12-30")

    def __init__(self, df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df phải là một pandas DataFrame.")

        missing_columns = [
            column for column in self.DATE_COLUMNS if column not in df.columns
        ]

        if missing_columns:
            raise KeyError(
                "Thiếu cột cần chuẩn hóa: " + ", ".join(missing_columns)
            )

        # Tạo bản sao để không làm thay đổi dữ liệu gốc.
        self.df = df.copy()
        self.report: dict[str, int] = {}

    def clean_dates(self) -> pd.DataFrame:
        """Chuẩn hóa ngày tháng và loại bỏ các dòng không hợp lệ."""

        rows_before = len(self.df)

        logger.info("Bắt đầu chuẩn hóa Order Date và Ship Date...")

        # Bước 1: Chuẩn hóa định dạng ngày tháng.
        for column in self.DATE_COLUMNS:
            raw_dates = self.df[column].astype("string").str.strip()

            self.df[column] = pd.to_datetime(
                raw_dates,
                format="mixed",
                dayfirst=True,
                errors="coerce",
            )

        # Bước 2: Loại bỏ những dòng có ngày thiếu hoặc không hợp lệ.
        invalid_date_mask = self.df[
            list(self.DATE_COLUMNS)
        ].isna().any(axis=1)

        invalid_date_rows = int(invalid_date_mask.sum())

        self.df = self.df.loc[~invalid_date_mask].copy()

        # Bước 3: Kiểm tra khoảng thời gian hợp lệ.
        in_range_mask = (
            self.df["Order Date"].between(
                self.START_DATE, self.END_DATE
            )
            & self.df["Ship Date"].between(
                self.START_DATE, self.END_DATE
            )
        )

        out_of_range_rows = int((~in_range_mask).sum())

        self.df = self.df.loc[in_range_mask].copy()

        # Bước 4: Đảm bảo ngày giao hàng không trước ngày đặt hàng.
        wrong_order_mask = (
            self.df["Ship Date"] < self.df["Order Date"]
        )

        ship_before_order_rows = int(wrong_order_mask.sum())

        self.df = self.df.loc[~wrong_order_mask].copy()

        # Bước 5: Đánh lại chỉ số dòng.
        self.df.reset_index(drop=True, inplace=True)

        # Bước 6: Thống kê kết quả làm sạch.
        self.report = {
            "rows_before": rows_before,
            "invalid_date_rows": invalid_date_rows,
            "out_of_range_rows": out_of_range_rows,
            "ship_before_order_rows": ship_before_order_rows,
            "rows_after": len(self.df),
            "rows_removed": rows_before - len(self.df),
        }

        logger.info("Hoàn thành chuẩn hóa ngày tháng.")
        logger.info("Số dòng ban đầu: %s", rows_before)
        logger.info("Dòng có ngày thiếu/không hợp lệ: %s", invalid_date_rows)
        logger.info("Dòng ngoài khoảng thời gian: %s", out_of_range_rows)
        logger.info(
            "Dòng có Ship Date trước Order Date: %s",
            ship_before_order_rows,
        )
        logger.info("Số dòng còn lại: %s", len(self.df))

        return self.df


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    current_dir = Path(__file__).resolve().parent

    if current_dir.name.lower() == "src":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    data_path = project_root / "data" / "train.csv"

    if not data_path.exists():
        raise FileNotFoundError(
            "Không tìm thấy data/train.csv. "
            "Hãy kiểm tra lại đường dẫn dữ liệu."
        )

    original_df = pd.read_csv(data_path)

    cleaner = DateCleaner(original_df)
    cleaned_df = cleaner.clean_dates()

    print("\n--- KẾT QUẢ KIỂM TRA NGÀY THÁNG ---")
    print(cleaner.report)

    print("\nKiểu dữ liệu sau chuẩn hóa:")
    print(cleaned_df[list(DateCleaner.DATE_COLUMNS)].dtypes)

    print("\n5 dòng đầu sau chuẩn hóa:")
    print(cleaned_df[list(DateCleaner.DATE_COLUMNS)].head()) 


    def remove_duplicates(self):

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




