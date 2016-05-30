import cv2
import time
import os
import requests
import json
from random import randint
import base64


class HeadsUpDataCollector():

    _DRIVE_DATA_FOLDERNAME          = "HUDC"
    _DESIRED_NUMBER_OF_SNAPSHOTS    = 1#30
    _INITIAL_SNAPSHOT_DELAY         = 1#30
    _SNAPSHOT_FAILED                = ""
    _SNAPSHOT_FILETYPE              = ".jpg"
    _SNAPSHOT_FOLDER                = "Heads_Up_data/"
    _SNAPSHOT_INTERVAL              = 1#15
    _SNAPSHOT_TITLE                 = "Heads_Up_data_collection_snapshot"
    _JSON_KEY                       = "image_datauri"
    _UID                            = "uid"
    _URL                            = "http://145.24.222.162:8000/data"

    def __init__(self):
        self._snapshot_count = 0
        self._uid = str(time.time()) + str(randint(0, 999999))

    def collect_data_with_interval(self):
        """
        Handles data collection. Uploads snapshots to Google drive
        if they were taken succesfully, repeats this proces every N
        seconds.
        """
        try:
            os.mkdir("Heads_Up_data", 777)
        except OSError as ose:
            pass
        time.sleep(self._INITIAL_SNAPSHOT_DELAY)
        while self._snapshot_count < self._DESIRED_NUMBER_OF_SNAPSHOTS:
            snapshot_successful, snapshot_filename = self._take_snaphot()
            if snapshot_successful:
                self._upload_snapshot(snapshot_filename)
                #self._delete_old_snapshot(snapshot_filename)
            time.sleep(self._SNAPSHOT_INTERVAL)

    def _take_snaphot(self):
        """
        uses the pc's webcam to take a picture, stores it if the
        picture was taken succesfully.
        :return: succes, filename
        """
        webcam = cv2.VideoCapture(0)
        successful, snapshot = webcam.read()
        if successful:  # frame captured without any errors
            timestamp = str(time.time())
            random_digits = str(randint(11110,99999))
            snapshot_filename = self._SNAPSHOT_FOLDER + timestamp \
                                + self._SNAPSHOT_TITLE \
                                + random_digits + self._SNAPSHOT_FILETYPE
            cv2.imwrite(snapshot_filename, snapshot)
            self._snapshot_count += 1
            return True, snapshot_filename
        return False, self._SNAPSHOT_FAILED

    def _upload_snapshot(self, filename_with_path):
        """
        uploads a snapshot to Heads Up's Google Drive account for
        further processing.
        :param filename: the name of the snapshot file to upload
        """
        with open(filename_with_path, "rb") as f:
            base64_image = base64.b64encode(f.read())
            r = requests.post(self._URL, json={self._JSON_KEY: base64_image, self._UID: self._uid})
            decoded_image = self._decode_datauri(filename_with_path, base64_image)
            self._save_image_in_folder(decoded_image, str(self._snapshot_count))

    def _decode_datauri(self, filename_with_path, base64_image):
        print filename_with_path
        print base64_image
        fh = open("x.jpg", 'wb')
        fh.write(base64_image.decode('base64'))
        fh.close()

        """
        with open(filename_with_path, "rb") as f:
            image = base64.b64encode(f.read()).decode()
            timestamp = time.time()
            image_name = (str(timestamp) + ".jpg")
            return image, image_name"""

    def _save_image_in_folder(self, image, filename):
        with open(filename, 'wb') as image_on_disk:
            try:
                image_on_disk.write(image)
            except Exception as write_exception:
                print str(write_exception) + "_save_image_in_folder"
                pass  # TODO - logging insert

    def _delete_old_snapshot(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            pass


if __name__ == "__main__":
    data_collector = HeadsUpDataCollector()
    data_collector.collect_data_with_interval()

