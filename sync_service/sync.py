import os
from loguru import logger
from datetime import datetime as dt

from cloud_connector.yandex_disk_connector import YandexDiskConnector


def sync_files(connector: YandexDiskConnector, local_dir: str, log: logger) -> None:
    """
    Синхронизирует файлы между локальной директорией и облачным хранилищем.

    Args:
        connector (YandexDiskConnector): Объект для работы с Яндекс Диском.
        local_dir (str): Путь к локальной директории.
        log (logger): Логгер для записи информации о процессе синхронизации.
    Raises:
        Exception: В случае ошибки при синхронизации файлов.
    """
    try:
        cloud_files = connector.get_cloud_files()
        local_files = os.listdir(local_dir)

        for cloud_file in cloud_files:
            if cloud_file not in local_files:
                connector.delete_file(cloud_file)
                log.info(f"Удалён файл из облака: {cloud_file}")

        for local_file in local_files:
            if local_file not in cloud_files:
                connector.upload_file(file_path=os.path.join(local_dir, local_file))
                log.info(f"Загружен новый файл в облако: {local_file}")

            else:
                local_file_modified_time = dt.fromtimestamp(os.path.getmtime(os.path.join(local_dir, local_file))).strftime("%Y-%m-%dT%H:%M:%S")
                if local_file_modified_time > cloud_files[local_file]:
                    connector.reupload_file(file_path=os.path.join(local_dir, local_file))
                    log.info(f"Перезаписан файл в облаке: {local_file}")

    except Exception as exc:
        log.error(f"Ошибка синхронизации: {str(exc)}")