import cv2
import time
import os
import requests
import json
from random import randint
import base64


class HeadsUpDataCollector():
    """edited constants to take 1 picture every 5 minutes, instead of 4 pics separated by 15 sec per 5 minutes
    The result is 10 images per student, instead of 40. There is no point in taking that many
    pictures of a single student, unless when training to recognize his/her face."""
    _DESIRED_NUMBER_OF_SNAPSHOTS    = 10
    _INITIAL_SNAPSHOT_DELAY         = 60
    _SNAPSHOT_INTERVAL              = 0
    _SNAPSHOT_BURST_INTERVAL        = 300
    _SNAPSHOTS_PER_BURST            = 1
    _SNAPSHOT_FAILED                = ""
    _SNAPSHOT_FILETYPE              = ".jpg"
    _SNAPSHOT_FOLDER                = "Heads_Up_data/"
    _SNAPSHOT_TITLE                 = "Heads_Up_data_collection_snapshot"
    _JSON_KEY                       = "image_datauri"
    _UID                            = "uid"
    _URL                            = "http://145.24.222.162:8000/data"


    def __init__(self):
        self._snapshot_count = 0
        self._uid = str(time.time()) + str(randint(0, 999999))

    def collect_data_with_interval(self):
        """
        Handles data collection. Uploads snapshots to the Heads Up Ubuntu server
        if they were taken successfully, takes x snapshots per burst every y seconds
        """
        try:
            os.mkdir("Heads_Up_data", 777)
        except OSError as ose:
            pass
        time.sleep(self._INITIAL_SNAPSHOT_DELAY)
        while self._snapshot_count < self._DESIRED_NUMBER_OF_SNAPSHOTS:
            for i in range (self._SNAPSHOTS_PER_BURST):
                snapshot_successful, snapshot_filename = self._take_snaphot()
                if snapshot_successful:
                    self._upload_snapshot(snapshot_filename)
                    self._delete_old_snapshot(snapshot_filename)
                time.sleep(self._SNAPSHOT_INTERVAL)
            time.sleep(self._SNAPSHOT_BURST_INTERVAL)

    def _take_snaphot(self):
        """
        uses the pc's webcam to take a picture, stores it if the
        picture was taken succesfully. Images are removed after being uploaded.
        :return: succes, filename
        """
        webcam = cv2.VideoCapture(0)
        successful, snapshot = webcam.read()
        if successful:
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
        uploads a snapshot to Heads Up's ubuntu server for further processing.
        :param filename_with_path: the name of the snapshot file to upload
        """
        with open(filename_with_path, "rb") as f:
            base64_image = base64.b64encode(f.read())
            img_data = json.dumps({self._JSON_KEY: base64_image, self._UID: self._uid})
            r = requests.post(self._URL, data = img_data)

    def _delete_old_snapshot(self, filename):
        try:
            os.remove(filename)
        except OSError as e:
            pass


if __name__ == "__main__":
    '''hs = open("hst.txt", "a")
    hs.write("1")
    hs.close()
    hs = open("hst.txt", "a")
    hs.write("2")
    hs.close()'''

    _ARFF_FILE_RELATION = "@RELATION attention"
    _ARFF_FILE_RX = "@ATTRIBUTE rx	REAL"
    _ARFF_FILE_RY = "@ATTRIBUTE ry	REAL"
    _ARFF_FILE_RZ = "@ATTRIBUTE rz	REAL"
    _ARFF_FILE_CLASS = "@ATTRIBUTE class 	{paying_attention,not_paying_attention}"
    _ARFF_FILE_DATA = "@DATA"
    _ARFF_FILE_NAME = "/original.arff"

    arff_metadata = "%s\n\n%s\n%s\n%s\n%s\n\n%s\n" \
                    % (_ARFF_FILE_RELATION, _ARFF_FILE_RX, _ARFF_FILE_RY, _ARFF_FILE_RZ, _ARFF_FILE_CLASS, _ARFF_FILE_DATA)
    print (arff_metadata)
    #data_collector = HeadsUpDataCollector()
    #data_collector.collect_data_with_interval()

