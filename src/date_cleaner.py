"""Chuẩn hóa Order Date và Ship Date cho dự án phân tích doanh thu (Trang)."""

import logging

import pandas as pd

logger = logging.getLogger(__name__)


class DateCleaner:
    """Chuẩn hóa và kiểm tra hai cột ngày của bộ dữ liệu đơn hàng."""

    DATE_COLUMNS = ("Order Date", "Ship Date")
    DATE_FORMAT = "%d/%m/%Y"  # định dạng chính của train.csv
    ISO_FORMAT = "%Y-%m-%d"   # định dạng dự phòng (ví dụ CSV đã làm sạch)
    START_DATE = pd.Timestamp("2015-01-03")
    END_DATE = pd.Timestamp("2018-12-30")

    def __init__(self, df: pd.DataFrame, check_ship_date_range: bool = True) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df phải là một pandas DataFrame.")

        missing_columns = [c for c in self.DATE_COLUMNS if c not in df.columns]
        if missing_columns:
            raise KeyError("Thiếu cột cần chuẩn hóa: " + ", ".join(missing_columns))

        self.df = df.copy()
        # True: lọc khoảng ngày cho cả Ship Date (theo bảng phân công).
        # False: chỉ lọc theo Order Date (giữ thêm 48 đơn đặt cuối 12/2018).
        self.check_ship_date_range = check_ship_date_range
        self.report: dict[str, int] = {}

    def clean_dates(self) -> pd.DataFrame:
        """Chuẩn hóa ngày tháng và loại bỏ các dòng không hợp lệ."""
        rows_before = len(self.df)
        logger.info("Bắt đầu chuẩn hóa Order Date và Ship Date...")

        # Bước 1: Parse ngày. Cột đã là datetime thì bỏ qua (tránh parse lại sai
        # khi dữ liệu đã sạch được chuyển thành chuỗi ISO yyyy-mm-dd).
        for column in self.DATE_COLUMNS:
            if pd.api.types.is_datetime64_any_dtype(self.df[column]):
                continue
            raw_dates = self.df[column].astype("string").str.strip()
            parsed = pd.to_datetime(
                raw_dates, format=self.DATE_FORMAT, errors="coerce"
            )
            # Dòng không khớp dd/mm/yyyy thì thử yyyy-mm-dd (định dạng thứ 2).
            # Không dùng dayfirst=True với chuỗi ISO vì sẽ đảo tháng/ngày.
            iso = pd.to_datetime(raw_dates, format=self.ISO_FORMAT, errors="coerce")
            self.df[column] = parsed.fillna(iso)

        # Bước 2: Loại dòng có ngày thiếu/không hợp lệ.
        invalid_mask = self.df[list(self.DATE_COLUMNS)].isna().any(axis=1)
        invalid_date_rows = int(invalid_mask.sum())
        self.df = self.df.loc[~invalid_mask].copy()

        # Bước 3: Khoảng thời gian hợp lệ.
        in_range = self.df["Order Date"].between(self.START_DATE, self.END_DATE)
        if self.check_ship_date_range:
            in_range &= self.df["Ship Date"].between(self.START_DATE, self.END_DATE)
        out_of_range_rows = int((~in_range).sum())
        self.df = self.df.loc[in_range].copy()

        # Bước 4: Ship Date không được trước Order Date.
        wrong_order = self.df["Ship Date"] < self.df["Order Date"]
        ship_before_order_rows = int(wrong_order.sum())
        self.df = self.df.loc[~wrong_order].reset_index(drop=True)

        self.report = {
            "rows_before": rows_before,
            "invalid_date_rows": invalid_date_rows,
            "out_of_range_rows": out_of_range_rows,
            "ship_before_order_rows": ship_before_order_rows,
            "rows_after": len(self.df),
            "rows_removed": rows_before - len(self.df),
        }

        logger.info("Số dòng ban đầu: %s", rows_before)
        logger.info("Dòng có ngày thiếu/không hợp lệ: %s", invalid_date_rows)
        logger.info("Dòng ngoài khoảng thời gian: %s", out_of_range_rows)
        logger.info("Dòng có Ship Date trước Order Date: %s", ship_before_order_rows)
        logger.info("Số dòng còn lại: %s", len(self.df))
        return self.df