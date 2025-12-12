import os
import cv2
import numpy as np
from rembg import remove
from tqdm import tqdm

# === 設定區 (相對路徑) ===
INPUT_DIR = 'input_images'
OUTPUT_DIR = 'processed_data'
RESIZE_WIDTH = 600  # 統一縮放寬度，避免圖片太大跑不動


# ========================

def process_images():
    # 1. 檢查目錄
    if not os.path.exists(INPUT_DIR):
        print(f"錯誤：找不到 '{INPUT_DIR}' 資料夾，請先建立並放入圖片。")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"已建立輸出資料夾: {OUTPUT_DIR}")

    # 2. 搜尋圖片
    exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    files = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(exts)]

    print(f"找到 {len(files)} 張圖片，開始去背處理...\n")

    for f in tqdm(files, desc="處理進度"):
        try:
            input_path = os.path.join(INPUT_DIR, f)

            # 讀取圖片
            img = cv2.imread(input_path)
            if img is None: continue

            # 統一縮放 (保持比例)
            h, w = img.shape[:2]
            if w > RESIZE_WIDTH:
                scale = RESIZE_WIDTH / w
                img = cv2.resize(img, (RESIZE_WIDTH, int(h * scale)))

            # --- A. 製作前景  ---
            # rembg 不需要任何參數，直接丟進去就好，效果比 GrabCut 好非常多
            fg_img = remove(img)

            # --- B. 製作背景 (模糊化原圖) ---
            # 模擬相機景深效果
            bg_img = cv2.GaussianBlur(img, (0, 0), sigmaX=15, sigmaY=15)
            bg_img = (bg_img * 0.7).astype(np.uint8)  # 稍微調暗，凸顯前景

            # --- C. 存檔 ---
            filename_no_ext = os.path.splitext(f)[0]

            # 前景存為 PNG (保留透明度)
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"{filename_no_ext}_fg.png"), fg_img)
            # 背景存為 JPG
            cv2.imwrite(os.path.join(OUTPUT_DIR, f"{filename_no_ext}_bg.jpg"), bg_img)

        except Exception as e:
            print(f"處理 {f} 時發生錯誤: {e}")

    print("\n處理完成！請執行 step2_viewer.py 查看水晶球。")


if __name__ == "__main__":
    process_images()