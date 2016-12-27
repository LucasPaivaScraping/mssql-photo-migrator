#!/usr/bin/env python3

"""
usage: python3 main.py
"""

import imghdr
import pymssql
import os
import sys


SERVER = ''
PORT = 1433
USERNAME = ''
PASSWORD = ''
DATABASE = ''

IMAGES_FOLDER = 'images'

IMAGES_DIR = None


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Db:
    def __init__(self, server, port, username, password, database):
        self._conn = pymssql.connect(
            server=server, port=port, user=username, password=password,
            database=database
        )

    def query(self, sql, binds=None):
        cursor = self._conn.cursor(as_dict=True)

        cursor.execute(sql)

        for row in cursor:
            yield row


class AdImagesDao:
    def __init__(self, db):
        self.db = db

    def all(self):
        sql = """
        SELECT TOP 10
            CodAvisoDv, FechaAlta, Plano,
            Foto1, Foto2, Foto3, Foto4, Foto5, Foto6, Foto7, Foto8, Foto9,
            Foto10, Foto11, Foto12, Foto13, Foto14, Foto15
        FROM
            DueAvisosDvFotosNuevoSistema
        """

        for row in self.db.query(sql):
            yield row


class AdImages:
    def __init__(self, row):
        self.row = row

        self.dir_created = False
        self.dir = None

        self.id = row['CodAvisoDv']
        self.dt = row['FechaAlta']

        if self.dt:
            self.dt = self.dt.strftime("%Y%m%d_%H%M%S")

        self.has_floor_plan = (row['Plano'])
        self.has_img_01 = (row['Foto1'])
        self.has_img_02 = (row['Foto2'])
        self.has_img_03 = (row['Foto3'])
        self.has_img_04 = (row['Foto4'])
        self.has_img_05 = (row['Foto5'])
        self.has_img_06 = (row['Foto6'])
        self.has_img_07 = (row['Foto7'])
        self.has_img_08 = (row['Foto8'])
        self.has_img_09 = (row['Foto9'])
        self.has_img_10 = (row['Foto10'])
        self.has_img_11 = (row['Foto11'])
        self.has_img_12 = (row['Foto12'])
        self.has_img_13 = (row['Foto13'])
        self.has_img_14 = (row['Foto14'])
        self.has_img_15 = (row['Foto15'])

    def ensure_dir(self):
        if self.dir_created:
            return

        dir = os.path.join(IMAGES_DIR, str(self.id))
        self.dir = dir

        if os.path.exists(dir):
            self.dir_created = True
            return

        os.makedirs(dir)

        self.dir_created = True

    def save_floor_plan(self):
        if self.has_floor_plan:
            self.ensure_dir()

            filename = "%s_%s_%s" % (self.id, 'plano', self.dt)

            ext = None

            try:
                ext = imghdr.what(None, h=self.row['Plano'])
            except:
                pass

            if ext:
                filename = filename + '.' + ext

            fullpath = os.path.join(self.dir, filename)

            with open(fullpath, 'ab') as f:
                f.write(self.row['Plano'])

    def save_photos(self):
        for n in range(1, 16):
            n_str = "%02d" % n
            attr = 'has_img_' + n_str
            row_idx = 'Foto' + str(n)

            if getattr(self, attr):
                self.ensure_dir()

                filename = "%s_%s_%s" % (self.id, n_str, self.dt)

                ext = None

                try:
                    ext = imghdr.what(None, h=self.row[row_idx])
                except Exception as e:
                    pass

                if ext:
                    filename = filename + '.' + ext

                fullpath = os.path.join(self.dir, filename)

                with open(fullpath, 'ab') as f:
                    f.write(self.row[row_idx])

    def add_extensions(self):
        filenames = os.listdir(self.dir)

        for filename in filenames:
            pass
            #fullpath = os.path.join()

    def save(self):
        self.save_floor_plan()
        self.save_photos()

        if self.dir_created:
            pass
            #self.add_extensions()


if __name__ == '__main__':
    IMAGES_DIR = os.path.join(os.getcwd(), IMAGES_FOLDER)

    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

    try:
        db = Db(SERVER, PORT, USERNAME, PASSWORD, DATABASE)
    except:
        eprint('ERROR: could not connect to database')
        sys.exit(1)

    dao = AdImagesDao(db=db)

    for row in dao.all():
        ad_images = AdImages(row)

        try:
            ad_images.save()
        except Exception as e:
            eprint(
                'ERROR: error saving image from ad %s' % (
                    ad_images.id,
                )
            )
            raise e
            continue
