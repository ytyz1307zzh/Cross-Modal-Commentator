import os
import traceback
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

path = './sina_image/'  # 图片目录名
img_list = os.listdir(path)
cnt = 0
err_file = open('err.txt', 'w', encoding='utf-8')

for img_path in img_list:
    try:
        cnt += 1

        img = Image.open(path+img_path)
        img = img.convert('RGB')
        img = img.resize((224, 224))
        img.save(path+img_path)
        if cnt % 100 == 0:
            print('{} images finished.'.format(cnt))

    except KeyboardInterrupt:
        print('Quiting...')
        quit()

    except:
        traceback.print_exc()
        print(img_path, file=err_file)


print('Final check: {} images finished.'.format(cnt))

