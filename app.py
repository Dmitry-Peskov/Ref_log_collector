import os
import re


def is_sys_mailbox(boxname: str) -> bool:
    """
    Проверяет имя папки на соответствие паттерну. Является ли это название - системным ящиком.

    :param boxname: имя папки
    :return: True / False
    """
    check_template = re.search(pattern=r"(\b[\d\w]{7}\b)", string=boxname)
    if check_template is not None:
        return check_template.string == boxname
    else:
        return False


def define_the_root_directory() -> str:
    """
    Предлагает пользователю подтвердить что текущая папка (из которой запущена программа) является корневым каталогом
    ПК "Спринтер" или указать свой путь до данного каталога.

    :return: строка с выбранным путём к корневой папке ПК "Спринтер"
    """
    current_directory = os.getcwd()
    dipost_directory = str()
    while True:
        command = str(
            input(f'Текущая директория: {current_directory}\nЭто корневой каталог ПК "Спринтер"? (y/n): ')).lower()
        if command == 'y':
            dipost_directory += current_directory
            break
        elif command == 'n':
            input_path = str(input('Укажите полный путь до корневого каталога ПК "Спринтер": '))
            if os.path.exists(input_path):
                dipost_directory += input_path
                break
            else:
                print(f'[Ошибка] Каталога: {input_path} не существует! Попробуйте еще раз.\n')
                continue
        else:
            print(f'[Ошибка] Команда не была распознана. Ожидаемые значения: y, n. Попробуйте ещё раз\n')
            continue
    print(f'[Инфо] Выбран каталог: {dipost_directory}')
    return dipost_directory


def find_system_mailboxes(root_directory: str) -> list[str]:
    """
    Анализирует каталог BOXES и собирает из него название системных ящиков

    :param root_directory: путь до корневого каталога ПК "Спринтер"
    :return: список содержащий имена системных ящиков
    """
    system_mailboxes = list()
    boxes_path = root_directory + '\\BOXES' if root_directory[-1] != '\\' else root_directory + 'BOXES'
    print(f'[Инфо] Проверяю существование ящиков в {boxes_path}')
    if os.path.exists(boxes_path):
        boxes = [box for box in os.listdir(boxes_path) if os.path.isdir(os.path.join(boxes_path, box))]
        for box in boxes:
            if is_sys_mailbox(box):
                system_mailboxes.append(box)
        print(f'[Инфо] Обнаружено ящиков: {len(system_mailboxes)} шт.')
    else:
        print(f'[Предупреждение] Каталог {boxes_path} - не существует!')
    return system_mailboxes


if __name__ == "__main__":
    root_dir = define_the_root_directory()
    sys_mailboxes = find_system_mailboxes(root_dir)
