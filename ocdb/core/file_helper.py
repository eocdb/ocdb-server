from pathlib import Path


class FileHelper():

    @staticmethod
    def create_relative_path(archive_root, full_path):
        root_path = Path(full_path)
        rel_path = root_path.relative_to(archive_root)
        return rel_path
