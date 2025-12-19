from AioSpider.orm.fields import ExtensionNameField
from .models import FileModel

__all__ = ['PdfFileModel', 'XlsxFileModel', 'ImageModel']


class PdfFileModel(FileModel):
    """PDF 文件数据结构"""

    class Meta:
        abstract = True

    extension = ExtensionNameField(name='拓展名', default='pdf')

    # def extract_table(self, path):
    #     tables = extract_table_from_pdf(path, pages='all', encoding=self.Meta.charset)
    #
    #     if not tables:
    #         return None
    #
    #     df = self.concat_table(tables)
    #     df = self.process_dataframe(df)
    #
    #     yield from self.yield_dataframe(df)
    #
    # def process_raw_table(self, tables: List[DataFrame]) -> List[DataFrame]:
    #     return tables
    #
    # def concat_table(self, tables: List[DataFrame]) -> DataFrame:
    #     tables = self.process_raw_table(tables)
    #     new_tables = [self.process_raw_dataframe(table) for table in tables]
    #     return concat(new_tables)


class XlsxFileModel(FileModel):
    """XLXS 文件数据结构"""

    class Meta:
        abstract = True

    extension = ExtensionNameField(name='拓展名', default='xlsx')

    # def extract_table(self, path):
    #     df = extract_table_from_xlsx(path)
    #     df = self.process_raw_dataframe(df)
    #     df = self.process_dataframe(df)
    #
    #     yield from self.yield_dataframe(df)


class ImageModel(FileModel):
    """图片文件数据结构"""

    class Meta:
        abstract = True

    extension = ExtensionNameField(name='拓展名', default='png')

    # def extract_table(self, path):
    #     df = ExtractImageTable(path)
    #     df = self.process_raw_dataframe(df)
    #     df = self.process_dataframe(df)
    #
    #     yield from self.yield_dataframe(df)
