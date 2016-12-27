#!/usr/bin/env python3

"""
usage: python3 main.py
"""

import imghdr
import pymssql
import os
import sys


###############################################################################
# Configure the next variables
###############################################################################

DB_SERVER = ''
DB_PORT = 1433
DB_USERNAME = ''
DB_PASSWORD = ''
DB_DATABASE = ''

IMAGES_FOLDER = 'images'

ADS_SQL = """
SELECT TOP 100
    CodAvisoDv, FechaAlta, Plano,
    Foto1, Foto2, Foto3, Foto4, Foto5, Foto6, Foto7, Foto8, Foto9,
    Foto10, Foto11, Foto12, Foto13, Foto14, Foto15
FROM
    DueAvisosDvFotosNuevoSistema
"""


def eprint(*args, **kwargs):
    """Like print(), but writes to stderr"""
    print(*args, file=sys.stderr, **kwargs)


class Db:
    """Database connection abstraction"""
    def __init__(self, server, port, username, password, database):
        self._conn = pymssql.connect(
            server=server, port=port, user=username, password=password,
            database=database
        )

    def query(self, sql, binds=None):
        """Yields the files obtained in the query"""
        cursor = self._conn.cursor(as_dict=True)

        cursor.execute(sql)

        for row in cursor:
            yield row


class AdImagesDao:
    """Data access object"""
    def __init__(self, db, ads_sql):
        self.db = db
        self.ads_sql = ads_sql

    def all(self):
        for row in self.db.query(self.ads_sql):
            yield row


class AdImage:
    """Abstraction of an image and the info that need to be saved"""
    def __init__(self, dir, filename, bytes_):
        self.dir = dir
        self.filename = filename
        self.bytes_ = bytes_

    def add_extension(self):
        """
        Try to get the image type. If succeed, adds the extension to the
        filename.
        """
        ext = None

        try:
            ext = imghdr.what(None, h=self.bytes_)
        except:
            pass

        if ext:
            self.filename += '.' + ext


    def save(self):
        """
        Saves the image to disk. If the image existed previously, keeps the
        original file.
        """
        self.add_extension()

        fullpath = os.path.join(self.dir, self.filename)

        if os.path.isfile(fullpath):
            return

        with open(fullpath, 'ab') as f:
            f.write(self.bytes_)


class AdImages:
    """
    Abstraction of the list of images of and ad, and other info needed to save
    them.
    """
    def __init__(self, row):
        self.row = row

        self.dir_created = False
        self.dir = None

        self.id = row['CodAvisoDv']
        self.dt = row['FechaAlta']

        if self.dt:
            self.dt = self.dt.strftime("%Y%m%d_%H%M%S")

        self.has_floor_plan = bool(row['Plano'])
        self.has_img_01 = bool(row['Foto1'])
        self.has_img_02 = bool(row['Foto2'])
        self.has_img_03 = bool(row['Foto3'])
        self.has_img_04 = bool(row['Foto4'])
        self.has_img_05 = bool(row['Foto5'])
        self.has_img_06 = bool(row['Foto6'])
        self.has_img_07 = bool(row['Foto7'])
        self.has_img_08 = bool(row['Foto8'])
        self.has_img_09 = bool(row['Foto9'])
        self.has_img_10 = bool(row['Foto10'])
        self.has_img_11 = bool(row['Foto11'])
        self.has_img_12 = bool(row['Foto12'])
        self.has_img_13 = bool(row['Foto13'])
        self.has_img_14 = bool(row['Foto14'])
        self.has_img_15 = bool(row['Foto15'])

    def ensure_dir(self):
        if self.dir_created:
            return

        dir = os.path.join(os.getcwd(), IMAGES_FOLDER, str(self.id))
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

            try:
                ad_image = AdImage(
                    dir=self.dir,
                    filename=filename,
                    bytes_=self.row['Plano']
                )
                ad_image.save()
            except Exception as e:
                eprint(
                    'ERROR: could not save image from ad %s, exception: %s (%s)' % (
                        self.id, type(e).__name__, e
                    )
                )


    def save_photos(self):
        for n in range(1, 16):
            n_str = "%02d" % n
            attr = 'has_img_' + n_str
            row_idx = 'Foto' + str(n)

            if getattr(self, attr):
                self.ensure_dir()

                filename = "%s_%s_%s" % (self.id, n_str, self.dt)

                try:
                    ad_image = AdImage(
                        dir=self.dir,
                        filename=filename,
                        bytes_=self.row[row_idx]
                    )
                    ad_image.save()
                except Exception as e:
                    eprint(
                        'ERROR: could not save image from ad %s, exception: %s (%s)' % (
                            self.id, type(e).__name__, e
                        )
                    )
                    continue

    def save(self):
        self.save_floor_plan()
        self.save_photos()


if __name__ == '__main__':
    images_dir = os.path.join(os.getcwd(), IMAGES_FOLDER)

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    try:
        db = Db(DB_SERVER, DB_PORT, DB_USERNAME, DB_PASSWORD, DB_DATABASE)
    except:
        eprint('ERROR: could not connect to database')
        sys.exit(1)

    dao = AdImagesDao(db=db, ads_sql=ADS_SQL)

    for row in dao.all():
        ad_images = AdImages(row)

        try:
            ad_images.save()
        except Exception as e:
            eprint(
                'ERROR: could not save image from ad %s, exception: %s (%s)' % (
                    ad_images.id, type(e).__name__, e
                )
            )
            continue
