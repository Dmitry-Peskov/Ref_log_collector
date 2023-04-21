import os
import re
from datetime import datetime
import shutil


class ThisDirectoryIsNotTheRoot(Exception):
    """Исключение 'Этот каталог не является корневой папкой ПК "Спринтер"'"""

    def __init__(self, message):
        super().__init__(message)


class ErrorInProgressCopy(Exception):
    """Исключение 'В процессе копирования log-файлов произошли ошибки'"""

    def __init__(self, message):
        super().__init__(message)


class ErrorInProgressPacking(Exception):
    """Исключение 'В процессе упаковки в zip произошла ошибка'"""

    def __init__(self, message):
        super().__init__(message)


def is_sys_mailbox(boxname: str) -> bool:
    """
    Проверить имя папки на соответствие паттерну. Является ли это название - системным ящиком.

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
    Предложить пользователю подтвердить что текущая папка (из которой запущена программа) является корневым каталогом
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
    Проанализировать каталог BOXES и собрать из него название системных ящиков

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


def build_paths_to_log_files(root_directory: str, boxes_list: list[str]) -> list[str]:
    """
    Построить пути к log-файлам и проверить их существование.
    Если не будет найдено ни одного log-файла, будет возбуждено исключение, говорящее о том что root_directory не является
    корневым каталогом ПК "Спринтер"

    :param root_directory: путь к корневому каталогу ПК "Спринтер"
    :param boxes_list:  список системных ящиков (для сбора файлов protocol_{box}.log и ref_crypto_{box}.log)
    :return: список валидных путей к log-файлам
    """
    print('[Инфо] Идёт построение путей к log-файлам и проверка их существования')
    log_paths = list()
    base_path = root_directory + '\\' if root_directory[-1] != '\\' else root_directory
    logs = (r'log\Referent\Referent.log',
            r'CPCrypto.ini',
            r'Referent0.ini',
            r'referent.ini',
            r'Referent_Setup.ini',
            r'log\Referent\Reftransport.log',
            r'log\FormatCheck\FormatCheck.log',
            r'DocEngineError.log',
            r'dbconnection.ini',
            r'log\ManagedApp\WebModuleSystemConverter.log',
            r'log\ManagedApp\WebModuleSystem.log',
            r'log\ManagedApp\MkOnlineProxyNew.log',)
    for log in logs:
        log_p = base_path + log
        if os.path.exists(log_p):
            log_paths.append(log_p)
    if len(boxes_list) != 0:
        for box in boxes_list:
            box_logs = (fr'log\Referent\protocol_{box}.log',
                        fr'log\Referent\ref_crypto_{box}.log')
            for box_log_path in box_logs:
                if os.path.exists(box_log_path):
                    log_paths.append(box_log_path)
    cnt_log = len(log_paths)
    if cnt_log == 0:
        raise ThisDirectoryIsNotTheRoot(f'[Ошибка] Каталог {root_directory} не является корневой папкой ПК "Спринтер"')
    else:
        print(f'[Инфо] Обнаружено {cnt_log} log-файлов')
    return log_paths


def create_an_output_folder(root_directory: str) -> tuple[str, str]:
    """
    Создать папку для сохранения копий log-файлов и вернуть имя и ссылку на нее.
    Папка будет создана в директории ПК "Спринтер"

    :param root_directory: директория ПК "Спринтер"
    :return: имя созданной папки и путь к ней
    """
    date = datetime.now()
    directory_name = f'{date.day}-{date.month}-{date.year}_{date.hour}-{date.minute}_LOG файлы'
    root = root_directory + '\\' if root_directory[-1] != '\\' else root_directory
    output_path = root + directory_name
    if not os.path.exists(output_path):
        os.mkdir(output_path)
    else:
        shutil.rmtree(output_path, ignore_errors=True)
        os.mkdir(output_path)
    print(f'[Инфо] По пути {root} создана папка "{directory_name}", в которую будут скопированы файлы')
    return directory_name, output_path


def make_copies_of_files(output_dir: str, file_paths: list[str]) -> None:
    """
    Скопировать найденные log-файлы в специально созданную директорию.
    Если размер файла с расширением .log превышает 2 Мб и количество строк в файле больше 5000
    , копируются последние 5000 строк из файла.

    :param output_dir: путь к каталогу, в который будут скопированы файлы
    :param file_paths: список путей к копируемым log-файлам
    :return: None
    """
    cnt_log = len(file_paths)
    cnt_copy = 0
    print('[Инфо] Начата процедура копирования')
    try:
        for file in file_paths:
            if file[-4:] != '.log':
                shutil.copy(file, output_dir)
                cnt_copy += 1
            else:
                size = os.path.getsize(file)
                if size <= 2_097_152:  # меньше или равно 2 Мб
                    shutil.copy(file, output_dir)
                    cnt_copy += 1
                else:
                    log_name = file.rsplit('\\')[-1]
                    copy_file = f'{output_dir}\\{log_name}'
                    with open(file, 'r') as origin, open(copy_file, 'w') as copy_f:
                        data = origin.readlines()
                        cnt_row = len(data)
                        if cnt_row > 5000:
                            print(
                                f'[Инфо] Файл {log_name} более 2 Мб и имеет более 5000 строк. Копирую последние 5000 строк из файла')
                            end_row = cnt_row - 5000
                            for row in data[end_row:]:
                                copy_f.write(row)
                        else:
                            shutil.copy(file, output_dir)
                    cnt_copy += 1
            print(f'[Инфо] Скопировано {cnt_copy} из {cnt_log} файлов.')
    except Exception as errors_text:
        raise ErrorInProgressCopy(f'[Ошибка] в процессе копирования произошли ошибки:\n"{errors_text}"')


def pack_in_zip(packaged_catalog: str, archive_name: str, output_calatalog: str) -> None:
    """
    Производит упаковку собранных log-файлов в zip архив. Если упаковка прошла успешно, удаляет промежуточную папку,
    в которую собирались log-файлы. В ином случае предалагет пользователю упаковать папку вручную

    :param packaged_catalog: ссылка на каталог, который будет упакован в архив
    :param archive_name: имя будущего архива
    :param output_calatalog: каталог, в который будет произведена запись архива
    :return: None
    """
    try:
        os.chdir(output_calatalog)
        shutil.make_archive(base_name=archive_name, format='zip', root_dir=output_calatalog, base_dir=packaged_catalog)
        shutil.rmtree(path_out_folder, ignore_errors=True)
        print(f'[Инфо] В директории "{output_calatalog}" создан архив {archive_name}.zip')
        os.chdir(os.getcwd())
    except Exception as errors_t:
        raise ErrorInProgressPacking(f'[Ошибка] В процессе упаковки в zip:\n{errors_t}\nПроизведите упаковку каталога "{packaged_catalog}" вручную.')


# точка входа (запуск программы)
if __name__ == "__main__":
    while True:
        # получаем путь к каталогу ПК "Спринтер"
        root_dir = define_the_root_directory()
        # получаем имена системных ящиков
        sys_mailboxes = find_system_mailboxes(root_directory=root_dir)
        # строим пути и проверяем существование log-файлов. Если ни один файл не найден, перезапускаем сессию
        try:
            logfile_path = build_paths_to_log_files(root_directory=root_dir, boxes_list=sys_mailboxes)
        except ThisDirectoryIsNotTheRoot as err:
            print(err)
            print('[Инфо] Сеанс был перезапущен. Попробуйте снова.\n')
            continue
        # создать папку для копируемых файлов, получить её название и путь к ней
        name_out_folder, path_out_folder = create_an_output_folder(root_directory=root_dir)
        # копируем файлы в созданную папку, если файл .log более 2 Мб и 5000 строк, копируем последние 5000 строк из файла
        try:
            make_copies_of_files(output_dir=path_out_folder, file_paths=logfile_path)
        except ErrorInProgressCopy as error:
            print(error)
            shutil.rmtree(path_out_folder, ignore_errors=True)  # удаляем ранее созданную папку под log-файлы
            print('[Инфо] Сеанс был перезапущен. Попробуйте снова либо осуществите сбор файлов вручную\n')
            continue
        # производим упаковку собранных log-файлов в архив zip и удаление служебной папки, в которую собирали копии файлов
        try:
            pack_in_zip(packaged_catalog=path_out_folder, archive_name=name_out_folder, output_calatalog=root_dir)
        except ErrorInProgressPacking as errors:
            print(errors)
        finally:
            input('[Работа завершена] Нажмите Enter что бы завершить работу программы')
            break
