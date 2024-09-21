from vk_photo_backup import BackupPhotosVK
from dotenv import load_dotenv
import os

def main():
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    ya_token = os.getenv("YA_TOKEN")
    print(f'Добро пожаловать в программу для резервного копирования фотографий\n'
        f'с профиля(аватарок)  или  с  выбранного  альбома  пользователя  vk\n'
        f'в облачное хранилище Яндекс.Диск.\n' + '-' * 70)
    print('Настройки по умолчанию:\n' + '-' * 70)
    print('- Выбранный альбом - "фотографии профиля"')
    print('- Количество фото для копирования - 5')
    print('- Название папки на Яндекс Диск - "profile_photos"\n' + '-' * 70)
    print('Хотите оставить настройки по умолчанию?')
    choice_one = input('(y/n) -> ')
    while choice_one not in ('y', 'n'):
        print('Неверный ввод: введите "y" (да) или "n" (нет)')
        choice_one = input('(y/n) -> ')
    print('-' * 70)
    if choice_one == 'y':
        print('Введите id ВК пользователя состоящий из цифр, у которого нужно\n'
            'выполнить резервное копирование фото на Яндекс.Диск:')
        id_vk = input('-> ')
        print('-' * 70)
        try:
            backup = BackupPhotosVK(vk_token, ya_token, id_vk)
            backup.get_photos_data_vk()
            backup.create_folder_ya_disk()
            backup.upload_photos_disk()
            print('Хотите получить информацию о скопированных фото на Яндекс.Диск?')
            choice_two = input('(y/n) -> ')
            while choice_two not in ('y', 'n'):
                print('Неверный ввод: введите "y" (да) или "n" (нет)')
                choice_two = input('(y/n) -> ')
            print('-' * 70)
            if choice_two == 'y':
                backup.get_information()
            elif choice_two == 'n':
                print('До скорой встречи!')
        except:
            print('Возникла ошибка: неверно введен id пользователя')

    elif choice_one == 'n':
        print('Введите id ВК пользователя состоящий из цифр, у которого нужно\n'
            'выполнить резервное копирование фото на Яндекс.Диск:')
        id_vk = input('-> ')
        print('-' * 70)
        print('Введите что-то из предложенного списка или id (цифрами) альбома:')
        print('-' * 70)
        print(f'- wall — фотографии со стены;\n- profile — фотографии профиля;\n'
            f'- saved — сохраненные фотографии.')
        choice_three = input('-> ')
        print('-' * 70)
        print('Введите желаемое количество фото для резервного копирования (число):')
        choice_four = input('-> ')
        while not choice_four.isdigit():
            print('Ошибка ввода, попробуйте снова:')
            choice_four = input('-> ')
        print('-' * 70)
        print(f'Введите желаемое название для папки на Яндекс.Диск, в которую \n'
            f'будет осуществляться резервного копирования (число):')
        choice_five = input('-> ')
        print('-' * 70)
        try:
            backup = BackupPhotosVK(vk_token, ya_token, id_vk, vk_album_id=choice_three,
            num_photos=int(choice_four), name_folder=choice_five)
            backup.get_photos_data_vk()
            backup.create_folder_ya_disk()
            backup.upload_photos_disk()
            print('Хотите получить информацию о скопированных фото на Яндекс.Диск?')
            choice_two = input('(y/n) -> ')
            while choice_two not in ('y', 'n'):
                print('Неверный ввод: введите "y" (да) или "n" (нет)')
                choice_two = input('(y/n) -> ')
            print('-' * 70)
            if choice_two == 'y':
                backup.get_information()
            elif choice_two == 'n':
                print('До скорой встречи!')
        except:
            print('Возникла ошибка: неверно введен id пользователя или id альбома')

if __name__ == '__main__':
    main()
