from typing import Union, List
from pathlib import Path

import numpy as np
import pandas as pd
from AioSpider import logger

from .ocr_tools import recognize_from_image

__all__ = [
    'extract_table_from_pdf',
    'extract_table_from_xlsx',
    'concat_dataframes',
    'ImageTableExtractor',
    'merge_tables',
    'table_to_html',
    'table_statistics',
]

def import_tabula():
    global tabula
    if tabula is None:
        try:
            import tabula
        except:
            logger.warning("未安装tabula库，请使用pip安装[pip install tabula-py]")


def import_cv2():
    global cv2
    if cv2 is None:
        try:
            import cv2
        except:
            logger.warning("未安装cv2库, 请使用pip安装[pip install opencv-python]")


def import_PIL():
    global Image
    if Image is None:
        try:
            from PIL import Image
        except:
            logger.warning("未安装PIL库, 请使用pip安装[pip install pillow]")


def extract_table_from_pdf(file_path: Union[str, Path], pages: Union[int, str] = 'all', encoding: str = 'utf-8') -> List[pd.DataFrame]:
    import_tabula()

    if tabula is None:
        return []

    file_path = str(file_path) if isinstance(file_path, Path) else file_path

    try:
        tables = tabula.read_pdf(file_path, pages=pages, encoding=encoding)
    except UnicodeDecodeError:
        tables = tabula.read_pdf(file_path, pages=pages, encoding='gbk')
    except Exception as e:
        logger.error(f"从PDF提取表格失败: {e}")
        return []

    return tables


def extract_table_from_xlsx(file_path: Union[str, Path]) -> pd.DataFrame:
    file_path = str(file_path) if isinstance(file_path, Path) else file_path

    try:
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception as e:
        logger.error(f"{file_path} 未解析到文件中的表格，原因：{e}")
        df = pd.DataFrame()

    return df


def concat_dataframes(dataframes: List[pd.DataFrame], axis: int = 0) -> pd.DataFrame:
    if not dataframes:
        return pd.DataFrame()

    df = pd.concat(dataframes, axis=axis)
    return df.reset_index(drop=True)


class ImageTableExtractor:

    def __init__(self, image_path: Union[str, Path], col_scale: int = 40, row_scale: int = 20, coord_threshold: int = 10):
        self.image = self._read_image(image_path)
        self.col_scale = col_scale
        self.row_scale = row_scale
        self.coord_threshold = coord_threshold

    def extract(self) -> pd.DataFrame:

        import_cv2()

        if self.image is None or cv2 is None or Image is None:
            return pd.DataFrame()

        gray_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        binary_image = cv2.adaptiveThreshold(~gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 35, -5)

        rows, cols = binary_image.shape
        kernel_col = cv2.getStructuringElement(cv2.MORPH_RECT, (cols // self.col_scale, 1))
        kernel_row = cv2.getStructuringElement(cv2.MORPH_RECT, (1, rows // self.row_scale))

        eroded_col = cv2.erode(binary_image, kernel_col, iterations=1)
        dilated_col = cv2.dilate(eroded_col, kernel_col, iterations=1)

        eroded_row = cv2.erode(binary_image, kernel_row, iterations=1)
        dilated_row = cv2.dilate(eroded_row, kernel_row, iterations=1)

        intersections = cv2.bitwise_and(dilated_col, dilated_row)
        intersections_x, intersections_y = np.where(intersections > 0)

        x_coords, y_coords = self._filter_coordinates(intersections_x, intersections_y)
        x_coords, y_coords = self._filter_coordinates(intersections_x, intersections_y)

        data = [
            [self._extract_cell_text((x_coords[j], y_coords[i]), (x_coords[j+1], y_coords[i+1]))
             for j in range(len(x_coords) - 1)]
            for i in range(len(y_coords) - 1)
        ]

        return pd.DataFrame(data)

    def _read_image(self, path: Union[str, Path]):
        import_PIL()
        return np.array(Image.open(path))

    def _filter_coordinates(self, x, y):
        sorted_x = np.sort(x)
        sorted_y = np.sort(y)

        x_coords = self._filter_and_extend_coords(sorted_x)
        y_coords = self._filter_and_extend_coords(sorted_y)

        return x_coords, y_coords

    def _filter_and_extend_coords(self, coords):
        filtered_coords = [coords[0]]
        for coord in coords[1:]:
            if coord - filtered_coords[-1] > self.coord_threshold:
                filtered_coords.append(coord)

        avg_diff = np.mean(np.diff(filtered_coords))
        extended_coords = []
        for i in range(int(filtered_coords[0] // avg_diff) + 1):
            new_coord = int(filtered_coords[0] - avg_diff * i)
            if new_coord > 0:
                extended_coords.insert(0, new_coord)
        
        return extended_coords + filtered_coords[1:]

    def _extract_cell_text(self, pos1, pos2):
        import_PIL()
        x1, y1 = pos1
        x2, y2 = pos2
        cell = self.image[y1:y2, x1:x2]
        return recognize_from_image(Image.fromarray(cell))


def merge_tables(tables: List[pd.DataFrame], axis: int = 0) -> pd.DataFrame:
    """合并多个表格，可以选择按行或列合并"""
    return pd.concat(tables, axis=axis, ignore_index=True)


def table_to_html(df: pd.DataFrame, output_path: str):
    """将DataFrame转换为HTML表格并保存"""
    html_content = df.to_html(index=False)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def table_statistics(df: pd.DataFrame) -> dict:
    """计算表格的基本统计信息"""
    return {
        'row_count': len(df),
        'column_count': len(df.columns),
        'null_count': df.isnull().sum().sum(),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist()
    }


def filter_table(df: pd.DataFrame, conditions: dict) -> pd.DataFrame:
    """根据给定条件筛选表格数据"""
    query = ' & '.join([f"{k} == '{v}'" if isinstance(v, str) else f"{k} == {v}" for k, v in conditions.items()])
    return df.query(query)


def pivot_table(df: pd.DataFrame, index: str, columns: str, values: str, aggfunc: str = 'mean') -> pd.DataFrame:
    """创建数据透视表"""
    return pd.pivot_table(df, values=values, index=index, columns=columns, aggfunc=aggfunc)
