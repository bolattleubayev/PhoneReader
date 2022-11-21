# Phone Reader

### Overview
This project is an IoT addition to the existing LibreLinkUp application, or with a little tweaking can be used for any other application.

### Hardware

The code is intended to use on a Linux-based computers and boards such as Raspberry Pi, Beaglebone, Orange Pi etc. In my case it was tested and deployed on Beaglebone Black, so for different hardware a little bit different tweaking might be necessary.

The project consists of several important parts:
 * a LibreLinkUp enabled phone, in my case iPhone 7
 * a web camera, in my case is Logitech (recommended due to drivers)
 * a Lan cable
 * a 5V, 1A charger for Beaglebone (5.5mm OD, 2.1mm ID, center positive)
 * a phone charger

<img src = "/setup01.jpg" width ="200" /> <img src = "/setup02.jpg" width ="200" />

 ### Software
 **Digit recognition training**
 If you are using LibreLinkUp then you can use available *generalresponses.data* and *generalsamples.data* files. The k-Nearest Neighbor algorithm was trained on Source Sans 3 font (implementation taken from https://stackoverflow.com/questions/9413216/simple-digit-recognition-ocr-in-opencv-python).

 If you want to train on your own font, then you will need to upload *train.png* file with the digits that you want to classify and supply a list of those digits to the *chars* variable in *train.ipynb* (read top to bottom, left to right) and run the notebook, this will generate new *generalresponses.data* and *generalsamples.data* files.

 **The main script**
 The main script is main.py, it uses trained model to recognize digits from the camera and send them to the Nightscout API. It does not use loops, contrary to usual OpenCV flow, as I encountered issues with scheduling looped scripts on Beaglebone. So, instead I scheduled to run a single loop every 5 minutes on Beaglebone.

You might want to tweak sizes for filtering contours for your setup as well as morphological operations performed on the input frame. This may vary due to camera positioning, screen brightness, etc.

 ### Beaglebone setup
Assuming that you have a Beaglebone that runs on Linux on the latest available image. It is preferable to use the latest image as it already runs on Python 3.6 and removes the need of installing it manually.

* You will first need to install OpenCV and its dependencies through apt-get.
* Then you will need to put *main.py*, *generalresponses.data*, and *generalsamples.data* files to the Beaglebone with *scp*. In my case it was in */home/debian/*.

```
sudo scp /Users/BigMac/Desktop/filename debian@192.168.7.2:/home/debian/
```
* Install *requests* package with *pip* for API communication
```
pip install requests
```
* Try running the script and test its performance
* Schedule the script run for evey 5 minutes (or any other frequence of your choice) using *crontab*
```
crontab -e
```
 * On the prompt choose *1* nano editor. within the editor add following line to the end of the file. Here instead of python you might need to use the exact location of your preferred python e.g. */usr/bin/python3*

 ```
*/5 * * * * python /home/debian/main.py
```
