import cv2
import cv2.aruco as aruco  # type: ignore

# 設定與你偵測程式相同的字典
aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_4X4_50)

# 標籤解析度 (例如 200x200 像素)
marker_size_px = 200 

# 生成 ID 17 標籤
print("正在生成標籤 ID 17...")
marker_img_17 = aruco.generateImageMarker(aruco_dict, 17, marker_size_px)
# 加入一個簡單的白色外框，確保辨識率
padded_17 = cv2.copyMakeBorder(marker_img_17, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])
cv2.imwrite("marker_17.png", padded_17)

# 生成 ID 37 標籤
print("正在生成標籤 ID 37...")
marker_img_37 = aruco.generateImageMarker(aruco_dict, 37, marker_size_px)
padded_37 = cv2.copyMakeBorder(marker_img_37, 20, 20, 20, 20, cv2.BORDER_CONSTANT, value=[255, 255, 255])
cv2.imwrite("marker_37.png", padded_37)

print("生成完成！請將生成的 marker_17.png 與 marker_37.png 列印出來使用。")

