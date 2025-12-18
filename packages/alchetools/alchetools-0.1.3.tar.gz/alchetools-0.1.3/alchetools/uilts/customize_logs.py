import logging
import os
from datetime import datetime
from colorlog import ColoredFormatter
import gzip
import shutil
import threading


class DailyFileHandler(logging.FileHandler):
    """
    每天一个目录，并在日期切换时自动压缩上一天日志。
    """

    def __init__(self, dir_name, mode='a', encoding=None, delay=False, compress_old=True):
        self.dir_name = dir_name
        self.mode = mode
        self.encoding = encoding
        self.delay = delay
        self.compress_old = compress_old

        # 当前日期（yyyy-MM-dd），用于判断是否跨天
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        filename = self.get_filename()
        super().__init__(filename, mode, encoding, delay)

    def get_filename(self):
        """根据当前日期生成日志文件名：dir/YYYY/MM/DD/log.log"""
        date_str = datetime.now().strftime("%Y/%m/%d")
        log_dir = os.path.join(self.dir_name, date_str)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, "log.log")

    def _compress_file(self, filepath: str):
        """把指定日志文件压缩为 .gz，然后删除原始 .log"""
        try:
            if not os.path.exists(filepath):
                return
            gz_path = filepath + ".gz"
            # 已经压缩过就不要重复了
            if os.path.exists(gz_path):
                return

            with open(filepath, "rb") as f_in, gzip.open(gz_path, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

            os.remove(filepath)
        except Exception as e:
            # 压缩失败不要影响主程序，直接写一条错误到控制台即可
            print(f"[DailyFileHandler] 压缩日志失败: {filepath}, err={e}")

    def emit(self, record):
        """在写入日志前检查是否跨天，如果跨天则切换文件并异步压缩旧日志。"""
        new_date = datetime.now().strftime("%Y-%m-%d")

        if new_date != self.current_date:
            # 记录旧文件名，后面压缩
            old_log_file = self.baseFilename

            # 更新当前日期
            self.current_date = new_date

            # 切换到新文件
            self.baseFilename = self.get_filename()
            # 关闭旧文件流，打开新文件流
            if self.stream:
                self.stream.close()
                self.stream = self._open()

            # 异步压缩旧日志，避免阻塞当前线程
            if self.compress_old and old_log_file:
                t = threading.Thread(target=self._compress_file, args=(old_log_file,), daemon=True)
                t.start()

        super().emit(record)


def setup_logger():
    """
    设置日志记录器并返回它。日志文件按年/月/日的层级结构保存。
    """
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        file_handler = DailyFileHandler("./logfile", encoding="utf-8", compress_old=True)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 文件格式
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)

        # 彩色控制台格式
        color_formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(levelname)s - %(filename)s - %(funcName)s - line %(lineno)d - %(message)s",
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            }
        )
        console_handler.setFormatter(color_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.propagate = False

    return logger
