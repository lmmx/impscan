import sqlite3
from ..assets import _dir_path as store_path

__all__ = ["PackageDB", "CondaPackageDB"] # TODO: "PyPIPackageDB"


class PackageDB:
    filename = "package_catalogue.db"  # Default value
    directory = store_path

    def __init__(self, dir=directory, filename=filename, create=True, no_touch=False):
        self.directory = dir
        self.filename = filename
        if create:
            self.create(no_touch=no_touch)

    @property
    def path(self):
        return self.directory / self.filename

    def exists(self):
        return self.path.exists()

    def connect(self):
        return sqlite3.connect(self.path)

    # This would also be useful for imported name when supplied
    def has_package(self, package_name):
        peek = self.retrieve_package(package_name, fetch_all=False)
        has_pkg = peek is not None
        return has_pkg

    def __repr__(self):
        return f"{type(self)} '{self.filename}' at {self.directory}"

class CondaPackageDB(PackageDB):
    def create(self, no_touch=False):
        if no_touch and not self.path.exists():
            raise FileNotFoundError(f"No PackageDB at {self.db.path}")
        with self.connect() as conn:
            c = conn.cursor()
            c.execute(
                """
                CREATE TABLE IF NOT EXISTS conda_packages
                (channel tinytext, depends tinytext, filename tinytext, 
                packagename varchar(100), url tinytext, version varchar(100),
                Constraint pk_pid Primary key(channel, filename))
                """
            )

    def insert_entry(
        self,
        channel: str,
        depends: str,
        filename: str, # "fn" key
        packagename: str, # "name" key
        url: str,
        version: str,
    ):
        try:
            with self.connect() as conn:
                c = conn.cursor()
                c.execute(
                    "INSERT INTO conda_packages VALUES (?,?,?,?,?,?)",
                    (channel, depends, filename, packagename, url, version),
                )
                conn.commit()
        except Exception as e:
            print(f"{channel=} {depends=} {filename=} {packagename=} {url=} {version=}")
            raise e

    def retrieve_filename(self, fn, fetch_all=False):
        with self.connect() as conn:
            query_sql = """
            SELECT * FROM conda_packages
            WHERE filename == ?
            """
            c = conn.cursor()
            c.execute(query_sql, (fn,))
            return c.fetchall() if fetch_all else c.fetchone()

    def retrieve_package(self, package_name, fetch_all=True):
        with self.connect() as conn:
            query_sql = """
            SELECT * FROM conda_packages
            WHERE packagename == ?
            """
            c = conn.cursor()
            c.execute(query_sql, (package_name,))
            return c.fetchall() if fetch_all else c.fetchone()
