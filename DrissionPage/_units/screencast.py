# -*- coding:utf-8 -*-
"""
@Author  :   g1879
@Contact :   g1879@qq.com
"""
from base64 import b64decode
from os.path import sep
from pathlib import Path
from threading import Thread
from time import sleep, time

from .._functions.tools import clean_folder


class Screencast(object):
    def __init__(self, page):
        self._page = page
        self._path = None
        self._running = False
        self._enable = False
        self._mode = 'video'

    @property
    def set_mode(self):
        """返回用于设置录屏幕式的对象"""
        return ScreencastMode(self)

    def start(self, save_path=None):
        """开始录屏
        :param save_path: 录屏保存位置
        :return: None
        """
        self.set_save_path(save_path)
        if self._path is None:
            raise ValueError('save_path必须设置。')
        tmp = self._path / 'tmp'
        tmp.mkdir(parents=True, exist_ok=True)
        clean_folder(tmp)
        if self._mode.startswith('frugal'):
            self._page.driver.set_callback('Page.screencastFrame', self._onScreencastFrame)
            self._page.run_cdp('Page.startScreencast', everyNthFrame=1, quality=100)

        elif not self._mode.startswith('js'):
            self._running = True
            self._enable = True
            Thread(target=self._run).start()

        else:
            js = '''
            async function () {
                stream = await navigator.mediaDevices.getDisplayMedia({video: true, audio: true})
                mime = MediaRecorder.isTypeSupported("video/webm; codecs=vp9")
                               ? "video/webm; codecs=vp9"
                               : "video/webm"
                mediaRecorder = new MediaRecorder(stream, {mimeType: mime})
                DrissionPage_Screencast_chunks = []
                mediaRecorder.addEventListener('dataavailable', function(e) {
                    DrissionPage_Screencast_blob_ok = false;
                    DrissionPage_Screencast_chunks.push(e.data);
                    DrissionPage_Screencast_blob_ok = true;
                })
                mediaRecorder.start()

                mediaRecorder.addEventListener('stop', function(){
                    while(DrissionPage_Screencast_blob_ok==false){}
                    DrissionPage_Screencast_blob = new Blob(DrissionPage_Screencast_chunks, 
                                                            {type: DrissionPage_Screencast_chunks[0].type});
                })
              }
            '''
            print('请手动选择要录制的目标。')
            self._page.run_js('var DrissionPage_Screencast_blob;var DrissionPage_Screencast_blob_ok=false;')
            self._page.run_js(js)

    def stop(self, video_name=None):
        """停止录屏
        :param video_name: 视频文件名，为None时以当前时间名命
        :return: 文件路径
        """
        if video_name and not video_name.endswith('mp4'):
            video_name = f'{video_name}.mp4'
        name = f'{time()}.mp4' if not video_name else video_name
        path = f'{self._path}{sep}{name}'

        if self._mode.startswith('js'):
            self._page.run_js('mediaRecorder.stop();', as_expr=True)
            while not self._page.run_js('return DrissionPage_Screencast_blob_ok;'):
                sleep(.1)
            blob = self._page.run_js('return DrissionPage_Screencast_blob;')
            uuid = self._page.run_cdp('IO.resolveBlob', objectId=blob['result']['objectId'])['uuid']
            data = self._page.run_cdp('IO.read', handle=f'blob:{uuid}')['data']
            with open(path, 'wb') as f:
                f.write(b64decode(data))
            return path

        if self._mode.startswith('frugal'):
            self._page.driver.set_callback('Page.screencastFrame', None)
            self._page.run_cdp('Page.stopScreencast')
        else:
            self._enable = False
            while self._running:
                sleep(.1)

        if self._mode.endswith('imgs'):
            return str(Path(self._path).absolute())

        if not str(video_name).isascii() or not str(self._path).isascii():
            raise TypeError('转换成视频仅支持英文路径和文件名。')

        try:
            from cv2 import VideoWriter, imread, VideoWriter_fourcc
            from numpy import fromfile, uint8
        except ModuleNotFoundError:
            raise ModuleNotFoundError('请先安装cv2，pip install opencv-python')

        pic_list = Path(self._path).glob('*.jpg')
        img = imread(str(next(pic_list)))
        imgInfo = img.shape
        size = (imgInfo[1], imgInfo[0])

        videoWrite = VideoWriter(path, VideoWriter_fourcc(*"mp4v"), 5, size)

        for i in pic_list:
            img = imread(str(i))
            videoWrite.write(img)

        clean_folder(self._path, ignore=(name,))
        return f'{self._path}{sep}{name}'

    def set_save_path(self, save_path=None):
        """设置保存路径
        :param save_path: 保存路径
        :return: None
        """
        if save_path:
            save_path = Path(save_path)
            if save_path.exists() and save_path.is_file():
                raise TypeError('save_path必须指定文件夹。')
            save_path.mkdir(parents=True, exist_ok=True)
            self._path = save_path

    def _run(self):
        """非节俭模式运行方法"""
        self._running = True
        while self._enable:
            self._page.get_screenshot(path=self._path, name=f'{time()}.jpg')
            sleep(.04)
        self._running = False

    def _onScreencastFrame(self, **kwargs):
        """节俭模式运行方法"""
        with open(f'{self._path}\\{kwargs["metadata"]["timestamp"]}.jpg', 'wb') as f:
            f.write(b64decode(kwargs['data']))
        self._page.run_cdp('Page.screencastFrameAck', sessionId=kwargs['sessionId'])


class ScreencastMode(object):
    def __init__(self, screencast):
        self._screencast = screencast

    def video_mode(self):
        self._screencast._mode = 'video'

    def frugal_video_mode(self):
        self._screencast._mode = 'frugal_video'

    def js_video_mode(self):
        self._screencast._mode = 'js_video'

    def frugal_imgs_mode(self):
        self._screencast._mode = 'frugal_imgs'

    def imgs_mode(self):
        self._screencast._mode = 'imgs'
