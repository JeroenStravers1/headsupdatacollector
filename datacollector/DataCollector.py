import cv2
import time
import os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from random import randint

class HeadsUpDataCollector():
    _API_KEY                        = "575282054454-5lhuo215eq5b8doe42i9psfbnu3ttfh0.apps.googleusercontent.com"
    _DRIVE_DATA_FOLDERNAME          = "HUDC"
    _DESIRED_NUMBER_OF_SNAPSHOTS    = 30
    _INITIAL_SNAPSHOT_DELAY         = 30
    _SNAPSHOT_FAILED                = ""
    _SNAPSHOT_FILETYPE              = ".jpg"
    _SNAPSHOT_FOLDER                = "Heads_Up_data/"
    _SNAPSHOT_INTERVAL              = 15
    _SNAPSHOT_TITLE                 = "Heads_Up_data_collection_snapshot"



    def __init__(self):
        self._snapshot_count = 0
        '''
        self._gauth = GoogleAuth()
        self._gauth.LoadCredentialsFile("mycreds.txt")
        #self._gauth.credentials = '{"_module": "oauth2client.client", "scopes": ["https://www.googleapis.com/auth/drive"], "token_expiry": "2016-04-27T14:15:08Z", "id_token": null, "access_token": "ya29.CjHRAjA4A1ZedtXQl7lHRemkHQvcXQnAIJ1rqm7TsGHP8EvHrEBmwKkNzenqHFIUY7DL", "token_uri": "https://accounts.google.com/o/oauth2/token", "invalid": false, "token_response": {"access_token": "ya29.CjHRAjA4A1ZedtXQl7lHRemkHQvcXQnAIJ1rqm7TsGHP8EvHrEBmwKkNzenqHFIUY7DL", "token_type": "Bearer", "expires_in": 3599}, "client_id": "1026924012842-2n7oj3euf07qqdqnguf6bup5mndqlmgn.apps.googleusercontent.com", "token_info_uri": "https://www.googleapis.com/oauth2/v3/tokeninfo", "client_secret": "_LZHE0IitzzIZoHD0BMbPo5g", "revoke_uri": "https://accounts.google.com/o/oauth2/revoke", "_class": "OAuth2Credentials", "refresh_token": null, "user_agent": null}'
        if self._gauth.credentials is None:
            self._gauth.LocalWebserverAuth()
        elif self._gauth.access_token_expired:
            self._gauth.Refresh()
        else:
            self._gauth.Authorize()
        self._gauth.SaveCredentialsFile("mycreds.txt")
        self._drive = GoogleDrive(self._gauth)
        self._id = self.getParentFolderId()'''
        pass

    def getParentFolderId(self):
        """
        extracts the id of the parent drive folder for snapshot storage
        :return: id: the folder's id
        """
        file_list = self._drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        for found_file in file_list:
            if found_file['title'] == self._DRIVE_DATA_FOLDERNAME:
                return found_file['id']

    def collectDataWithInterval(self):
        """
        Handles data collection. Uploads snapshots to Google drive
        if they were taken succesfully, repeats this proces every N
        seconds.
        """
        os.mkdir("Heads_Up_data", 777)
        time.sleep(self._INITIAL_SNAPSHOT_DELAY)
        while self._snapshot_count < self._DESIRED_NUMBER_OF_SNAPSHOTS:
            snapshot_successful, snapshot_filename = self.takeSnaphot()
            '''if snapshot_successful:
                self.uploadSnapshot(snapshot_filename)
                self.deleteOldSnapshot(snapshot_filename)'''
            time.sleep(self._SNAPSHOT_INTERVAL)

    def takeSnaphot(self):
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
            snapshot_filename = self._SNAPSHOT_FOLDER+ timestamp \
                                + self._SNAPSHOT_TITLE \
                                + random_digits + self._SNAPSHOT_FILETYPE
            cv2.imwrite(snapshot_filename, snapshot)
            self._snapshot_count += 1
            return True, snapshot_filename
        return False, self._SNAPSHOT_FAILED

    def uploadSnapshot(self, filename):
        """
        uploads a snapshot to Heads Up's Google Drive account for
        further processing.
        :param filename: the name of the snapshot file to upload
        """
        image_file = self._drive.CreateFile({'title': filename, "parents":  [{"kind": "drive#fileLink","id": self._id}]})
        image_file.SetContentFile(filename)
        image_file.Upload()

    def deleteOldSnapshot(self, filename):
        os.remove(filename)


if __name__ == "__main__":
    data_collector = HeadsUpDataCollector()
    data_collector.collectDataWithInterval()

