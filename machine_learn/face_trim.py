import sys
import cv2

param = sys.argv
argc = len(param)

if argc > 1:
    print("引数を入れろ")
    quit()
    
in_dir_path = ""
out_dir_path = ""
err_dir_path = ""

cascade_path = ""

img_path = in_dir_path + param[1] 

print("img_path")

image = cv2.imread(img_path)
if(image is None):
    print('画像を開けません。')
    quit()


img_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
cascade = cv2.CascadeClassifier(cascade_path)
facerect = cascade.detectMultiScale(img_gray, scaleFactor=1.1, minNeighbors=1, minSize=(1, 1))

## you can see https://colab.research.google.com/drive/1g0h_rXhioeWXzG6zMDHjjKGGUUebcSGQ?hl=ja#scrollTo=ejAZXfW2AVVo here