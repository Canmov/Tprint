import os
def get_name_photo_in_folder(folder_path):
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
    files = os.listdir(folder_path)
    for f in files:
        if f.lower().endswith(image_extensions):
            return f
    return None

file_name = get_name_photo_in_folder('./')
if file_name:
    print("Найден файл:", file_name)
else:
    print("Фото в папке не найдено")
