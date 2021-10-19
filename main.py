import os
import youtube_dl
import json
import requests
from auth import token


def get_wall_posts(name_group):
    url = f"https://api.vk.com/method/wall.get?domain={name_group}&count=40&access_token={token}&v=5.131"
    req = requests.get(url)
    src = req.json()

    # Проверяем существует ли директория с именем группы
    if os.path.exists(f"{name_group}"):
        print(f"Директория с именем {name_group} уже существует!")
    else:
        os.mkdir(name_group)

    # Сохраняем данные в json,чтобы видеть структуру
    with open(f"{name_group}/{name_group}.json", "w", encoding="utf-8") as file:
        json.dump(src, file, indent=4, ensure_ascii=False)

    # Собираем ID новых постов
    new_posts_id = []
    posts = src["response"]["items"]

    for new_post_id in posts:
        new_post_id = new_post_id["id"]
        new_posts_id.append(new_post_id)

    """Проверка первый раз ли парсим группу. 
    Иначе начинаем проверку и отправляем только новые посты"""
    if not os.path.exists(f"{name_group}/exist_posts_{name_group}.txt"):
        print("Файла с ID постов не существует, создаем файл!")

        with open(f"{name_group}/exist_posts_{name_group}.txt", "w") as file:
            for item in new_posts_id:
                file.write(str(item) + "\n")

        # Извлекаем данные из постов
        for post in posts:

            #  Функция для сохранения картинок
            def download_image(url, post_id, name_group):
                res = requests.get(url)

                # Создаем папку name_group/files
                if not os.path.exists(f"{name_group}/images"):
                    os.mkdir(f"{name_group}/images")

                with open(f"{name_group}/images/{post_id}.jpg", "wb") as img_file:
                    img_file.write(res.content)

            # Функция для сохранения видео
            def download_video(url, post_id, name_group):
                if not os.path.exists(f"{name_group}/video"):
                    os.mkdir(f"{name_group}/video")

                try:
                    ydl_opts = {"outtmpl": f"{name_group}/video/{post_id}"}
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        video_info = ydl.extract_info(url, download=False)
                        video_duration = video_info["duration"]
                        if video_duration > 300:
                            print("Видео слишком долгое")
                        else:
                            print(f"Видео длится{video_duration} секунд. Сохраняем видео...")
                            ydl.download([url])
                except Exception:
                    print("Не удалось скачать видео!")


            post_id = post["id"]
            print(f"Отправляем пост с ID {post_id}")
            try:
                if "attachments" in post:
                    post = post["attachments"]
                    # Проверка на 1 или несколько фото/видео в посте
                    if len(post) == 1:

                        # Забираем фото
                        if post[0]["type"] == "photo":
                            post_photo = post[0]["photo"]["sizes"][-1]["url"]
                            print(post_photo)
                            download_image(post_photo, post_id, name_group)

                        # Забираем видео
                        elif post[0]["type"] == "video":
                            print("Видео пост")

                            # Формируем данные для составления запроса на получение ссылки на видео
                            video_access_key = post[0]["video"]["access_key"]
                            video_post_id = post[0]["video"]["id"]
                            video_owner_id = post[0]["video"]["owner_id"]

                            video_get_url = f"https://api.vk.   com/method/video.get?videos{video_owner_id}_" \
                                            f"{video_post_id}_{video_access_key}&access_token={token}&v=5.131"
                            req = requests.get(video_get_url)
                            res = req.json()
                            video_url = res["response"]["items"][0]["player"]
                            print(video_url)
                            download_video(video_url, post_id, name_group)
                        else:
                            print("Пост не содержит ни видео,ни фото,либо является репостом")
                    else:
                        photo_count = 0
                        for post_item_photo in post:
                            if post_item_photo["type"] == "photo":
                                pw = post_item_photo["photo"]["sizes"][-1]["width"]
                                ph = post_item_photo["photo"]["sizes"][-1]["height"]
                                post_photo = post_item_photo["photo"]["sizes"][-1]["url"]
                                print(f"Фото с разрешение:{pw}x{ph}")
                                print(post_photo)
                                post_id_counter = str(post_id) + f"_{photo_count}"
                                download_image(post_photo, post_id_counter, name_group)
                                photo_count += 1
                            elif post_item_photo["type"] == "video":
                                print("Видео пост")

                                # Формируем данные для составления запроса на получение ссылки на видео
                                video_access_key = post_item_photo["video"]["access_key"]
                                video_post_id = post_item_photo["video"]["id"]
                                video_owner_id = post_item_photo["video"]["owner_id"]

                                video_get_url = f"https://api.vk.   com/method/video.get?videos{video_owner_id}_" \
                                                f"{video_post_id}_{video_access_key}&access_token={token}&v=5.131"
                                req = requests.get(video_get_url)
                                res = req.json()
                                video_url = res["response"]["items"][0]["player"]
                                print(video_url)
                                post_id_counter = str(post_id) + f"_{photo_count}"
                                download_video(video_url, post_id_counter, name_group)
                                photo_count += 1
                            else:
                                print("Пост не содержит ни видео,ни фото,либо является репостом")

            except Exception:
                print(f"Что-то пошло не так с постом ID {post_id}")
    else:
        print("Файл с ID постов найден,начинаем выборку свежих постов!")


def main():
    name_group = input("Введите название группы: ")
    get_wall_posts(name_group)


if __name__ == '__main__':
    main()
