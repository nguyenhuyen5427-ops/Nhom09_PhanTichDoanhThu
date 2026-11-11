import os
import pandas as pd


def export_clean_data(df, path):
    """Xuất dữ liệu đã làm sạch ra file CSV."""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        df.to_csv(path, index=False, encoding="utf-8-sig")
        print(f"Đã xuất {len(df)} dòng, {df.shape[1]} cột -> {path}")
    except PermissionError:
        print(f"Không ghi được '{path}'. Hãy đóng file nếu đang mở trong Excel.")


def export_cleaning_log_from_compare(df_raw, df_clean, path):
    # Dán nguyên thân hàm này từ data_loader.py sang (từ dòng "dong = []" đến hết)
    dong = []
    dong.append(f"Số dòng: {len(df_raw)} (gốc) -> {len(df_clean)} (sạch), giảm {len(df_raw) - len(df_clean)} dòng")
    dong.append(f"Số cột: {df_raw.shape[1]} (gốc) -> {df_clean.shape[1]} (sạch)")
    dong.append(f"Dòng trùng lặp: {df_raw.duplicated().sum()} (gốc) -> {df_clean.duplicated().sum()} (sạch)")
    dong.append(f"Tổng ô thiếu: {df_raw.isna().sum().sum()} (gốc) -> {df_clean.isna().sum().sum()} (sạch)")
    
    for cot in df_raw.columns:
        if cot in df_clean.columns:
            t, s = df_raw[cot].isna().sum(), df_clean[cot].isna().sum()
            if t != s:
                dong.append(f"Cột '{cot}': ô thiếu {t} -> {s}")
            if df_raw[cot].dtype != df_clean[cot].dtype:
                dong.append(f"Cột '{cot}': kiểu dữ liệu {df_raw[cot].dtype} -> {df_clean[cot].dtype}")
        else:
            dong.append(f"Cột '{cot}': đã bị xóa")
    for cot in df_clean.columns:
        if cot not in df_raw.columns:
            dong.append(f"Cột '{cot}': cột mới được tạo thêm")
    
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("NHẬT KÝ LÀM SẠCH DỮ LIỆU\n" + "=" * 50 + "\n")
        for i, d in enumerate(dong, start=1):
            f.write(f"{i}. {d}\n")
    print(f"Đã xuất nhật ký -> {path}")


def export_all(data_file, df_clean, base_path):
    """Xuất cả dữ liệu sạch và nhật ký làm sạch bằng một lệnh."""
    export_clean_data(df_clean, base_path / "data" / "processed" / "train_clean.csv")
    df_raw = pd.read_csv(data_file)
    export_cleaning_log_from_compare(df_raw, df_clean, base_path / "output" / "cleaning_log.txt")