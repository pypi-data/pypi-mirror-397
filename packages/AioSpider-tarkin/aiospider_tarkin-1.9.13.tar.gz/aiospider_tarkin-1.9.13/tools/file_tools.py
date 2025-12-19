import os
import filecmp
import shutil
import zipfile
import tarfile
from typing import Union, List
from pathlib import Path

from AioSpider import logger

__all__ = [
    'create_directory',
    'extract_zip',
    'move_folder',
    'rename_file',
    'delete_files',
    'copy_item',
    'find_files',
]


def create_directory(path: Union[Path, str], auto_detect: bool = True) -> None:
    """
    创建目录
    Args:
        path: 文件夹路径
        auto_detect: 
            自动判断 path 参数是文件还是文件夹，默认为 True。
            当 auto_detect 为 True 时，会自动判断 path 路径参数是否有文件后缀，如果有则创建父级文件夹，如果没有则创建当前路径文件夹；
            当 auto_detect 为 False 时，会将当前路径作为文件夹创建
    """
    path = Path(path)
    if path.exists():
        return

    target_path = path.parent if auto_detect and path.suffix else path
    target_path.mkdir(parents=True, exist_ok=True)


def extract_zip(zip_path: Union[str, Path], extract_folder: Union[str, Path], remove_original: bool = True) -> None:
    """
    解压zip文件
    Args:
        zip_path: 要解压的ZIP文件路径
        extract_folder: 解压后的目标文件夹
        remove_original: 解压成功后是否删除该压缩文件
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extract_folder)
        if remove_original:
            os.remove(zip_path)
    except Exception as e:
        logger.warning(f'{zip_path} 文件解压失败！原因：{e}')


def move_folder(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """
    移动文件夹
    Args:
        source: 要剪切的源文件夹路径
        destination: 目标文件夹路径
    """
    try:
        shutil.move(str(source), str(destination))
    except FileExistsError:
        logger.level4(f'{destination} 文件（夹）已存在')
    except FileNotFoundError:
        logger.level4(f'{source} 文件（夹）不存在')
    except shutil.Error as e:
        logger.level4(str(e))


def rename_file(old_name: Union[str, Path], new_name: Union[str, Path]) -> None:
    """
    重命名文件或文件夹
    Args:
        old_name: 要重命名的文件或文件夹路径
        new_name: 新的文件或文件夹名
    """
    try:
        os.rename(str(old_name), str(new_name))
    except FileExistsError:
        logger.level4(f'{new_name} 文件（夹）已存在')
    except FileNotFoundError:
        logger.level4(f'{old_name} 文件（夹）不存在')


def delete_files(path: Union[str, Path]) -> None:
    """
    删除文件或文件夹
    Args:
        path: 文件或文件夹路径
    """
    path = Path(path)
    try:
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
    except FileNotFoundError:
        logger.level4(f'{path} 文件（夹）不存在')


def copy_item(source: Union[str, Path], destination: Union[str, Path]) -> None:
    """
    复制文件或文件夹
    Args:
        source: 源文件或文件夹路径
        destination: 目标文件或文件夹路径
    """
    try:
        if Path(source).is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    except FileNotFoundError:
        logger.level4(f'{source} 文件（夹）不存在')
    except FileExistsError:
        logger.level4(f'{destination} 文件（夹）已存在')
    except Exception as e:
        logger.level4(f'复制失败：{e}')


def find_files(directory: Union[str, Path], pattern: str) -> List[Path]:
    """
    搜索指定目录下的文件
    Args:
        directory: 要搜索的目录
        pattern: 文件名模式（支持通配符）
    Returns:
        匹配的文件路径列表
    """
    return list(Path(directory).rglob(pattern))


def read_text_file(file_path: Union[str, Path]) -> str:
    """
    读取文本文件内容
    Args:
        file_path: 文件路径
    Returns:
        文件内容
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_text_file(file_path: Union[str, Path], content: str) -> None:
    """
    写入内容到文本文件
    Args:
        file_path: 文件路径
        content: 要写入的内容
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)


def compare_file_contents(file1: Union[str, Path], file2: Union[str, Path]) -> bool:
    """
    比较两个文件的内容
    Args:
        file1: 第一个文件路径
        file2: 第二个文件路径
    Returns:
        如果文件内容相同返回 True，否则返回 False
    """
    return filecmp.cmp(file1, file2, shallow=False)


def get_file_metadata(file_path: Union[str, Path]) -> dict:
    """
    获取文件元数据
    Args:
        file_path: 文件路径
    Returns:
        文件元数据字典，包括大小、创建时间、修改时间
    """
    path = Path(file_path)
    return {
        'size': path.stat().st_size,
        'created': path.stat().st_ctime,
        'modified': path.stat().st_mtime
    }


def extract_tar(tar_path: Union[str, Path], extract_folder: Union[str, Path]) -> None:
    """
    解压tar文件
    Args:
        tar_path: 要解压的TAR文件路径
        extract_folder: 解压后的目标文件夹
    """
    try:
        with tarfile.open(tar_path, 'r') as tf:
            tf.extractall(extract_folder)
    except Exception as e:
        logger.warning(f'{tar_path} 文件解压失败！原因：{e}')


def set_file_permissions(file_path: Union[str, Path], mode: int) -> None:
    """
    修改文件权限
    Args:
        file_path: 文件路径
        mode: 权限模式（如 0o755）
    """
    try:
        os.chmod(file_path, mode)
    except Exception as e:
        logger.level4(f'修改权限失败：{e}')


def concatenate_files(file_list: List[Union[str, Path]], output_file: Union[str, Path]) -> None:
    """
    合并多个文件为一个文件
    Args:
        file_list: 要合并的文件路径列表
        output_file: 输出文件路径
    """
    with open(output_file, 'wb') as outfile:
        for file in file_list:
            with open(file, 'rb') as infile:
                shutil.copyfileobj(infile, outfile)
