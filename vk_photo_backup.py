import requests
import vk_api
from pprint import pprint
import datetime
import json
from tqdm import tqdm
from typing import List, Tuple


class BackupPhotosVK:
    """
    Класс для резервного копирования фотографий из ВКонтакте на Яндекс.Диск.

    Атрибуты:
        token_vk (str): Токен доступа к API ВКонтакте.
        token_ya_disk (str): Токен доступа к API Яндекс.Диска.
        vk_user_id (int): ID пользователя ВКонтакте, фотографии которого
        нужно скопировать.
        vk_album_id (str): ID альбома ВКонтакте, фотографии которого нужно
        скопировать (по умолчанию 'profile').
        num_photos (int): Количество фотографий для копирования (по умолчанию 5).
        name_folder (str): Название папки на Яндекс.Диске, куда будут
        скопированы фотографии (по умолчанию 'profile_photos').
        ya_disk_api (str): URL API Яндекс.Диска 
        (по умолчанию 'https://cloud-api.yandex.net/v1/disk/resources').
        file_names (set): Множество имен файлов, которые уже были загружены на Яндекс.Диск.
    """

    def __init__(self, token_vk, token_ya_disk, vk_user_id,
                 vk_album_id='profile', num_photos=5, name_folder='profile_photos'):
        """
        Инициализация объекта класса BackupPhotosVK.
        """
        self.token_vk = token_vk
        self.token_ya_disk = token_ya_disk
        self.vk_user_id = vk_user_id
        self.vk_album_id = vk_album_id
        self.num_photos = num_photos
        self.name_folder = name_folder
        self.ya_disk_api = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.file_names = set()

    def get_photos_data_vk(self) -> List[Tuple[int, str, str]]:
        """
        Получение данных о фотографиях из ВКонтакте.

        Возвращает:
            list: Список кортежей с данными о фотографиях
            (количество лайков, дата, URL фото).
        """
        vk_session = vk_api.VkApi(token=self.token_vk)
        params = {
            'owner_id': self.vk_user_id,
            'album_id': self.vk_album_id,
            'extended': 1
        }
        vk_photos_data = vk_session.method('photos.get', params)
        list_data_photos = list(((x['likes']['count'],
                                  f"{datetime.datetime.fromtimestamp(x['date']).strftime('%Y-%m-%d')}",
                                  x['orig_photo']['url']) for x in sorted(vk_photos_data['items'],
                                                                          key=lambda x: x['orig_photo']['width'] +
                                                                          x['orig_photo']['height'],
                                                                          reverse=True)))
        return list_data_photos[:self.num_photos] if len(list_data_photos) >= \
            self.num_photos else list_data_photos

    def create_folder_ya_disk(self) -> str:
        """
        Создание папки на Яндекс.Диске.

        Возвращает:
            str: Название созданной папки.
        """
        params = {
            'path': self.name_folder
        }
        headers = {
            'Authorization': self.token_ya_disk
        }
        response = requests.put(self.ya_disk_api,
                                headers=headers,
                                params=params)
        status = response.status_code
        if status == 201:
            print(f'Папка {self.name_folder} успешно создана')
            return self.name_folder
        else:
            print(response.json()['message'])
            return self.name_folder

    def upload_photos_disk(self):
        """
        Загрузка фотографий на Яндекс.Диск.

        Использует общий прогресс-бар для отображения прогресса загрузки 
        всех фотографий.
        """
        headers = {
            'Authorization': self.token_ya_disk
        }
        photos_data = self.get_photos_data_vk()
        with tqdm(total=len(photos_data), desc="Загрузка фото на Яндекс.Диск",
                  unit="photo") as pbar_total:
            for data in photos_data:
                like, date, url = data
                params = {
                    'path': f'{self.name_folder}/{like}'
                            if like not in self.file_names
                            else f'{self.name_folder}/{like}_{date}',
                    'url': url
                }
                self.file_names.add(like)
                response = requests.post(f'{self.ya_disk_api}/upload',
                                         headers=headers, params=params)
                if response.status_code == 202:
                    print('\n' + '-' * 22)
                    print('Фото успешно загружено')
                    pbar_total.update(1)
                else:
                    print(f"\n{response.json('message')}")

    def get_information(self):
        """
        Получение информации о загруженных фотографиях и сохранение её в JSON-файл.

        Выводит информацию о загруженных фотографиях и сообщение о том, 
        в какую папку на Яндекс.Диске были скопированы файлы.
        """
        headers = {
            'Authorization': self.token_ya_disk
        }
        list_data_photos = []
        for name in self.file_names:
            params = {
                'path': f'{self.name_folder}/{name}',
                'fields': 'name, size'
            }
            response = requests.get(self.ya_disk_api, headers=headers,
                                    params=params)
            if response.status_code == 200:
                list_data_photos.append(response.json())
            else:
                list_data_photos.append({
                    'message': f'Не удалось получить данные фото с именем {name}'
                })
        with open('info_about_photos.json', 'w', encoding='utf-8') as file:
            json.dump(list_data_photos, file)
        pprint(json.load(open('info_about_photos.json', 'r', encoding='utf-8')))
        print('-' * 70)
        print(f'Файлы скопированы в папку {self.name_folder} на Яндекс Диск')
        print('-' * 70)
