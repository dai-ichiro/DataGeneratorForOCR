from PySide6.QtWidgets import QMainWindow, QApplication, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, Slot, QThread
from trdg.generators import GeneratorFromStrings
import sys
import os
import glob
import json
import random
from PIL import ImageQt, Image
import time
import numpy as np

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--repeat', type=int, default=3, help='count of repeat' )
parser.add_argument('--noise', action='store_true', help="add Gaussian Noise")
parser.add_argument('--trdg', action='store_true', help="use TRDG")
args = parser.parse_args()
repeat_n = args.repeat
noise_true = args.noise
trdg_true = args.trdg

class MakeJson(QThread):
    makingJson_finish_signal = Signal(bool)
    def __init__(self):
        super().__init__()
    def run(self):
        data_list = []
        for i in range(repeat_n):
            for text_i, text in enumerate(texts):
                image_fname = f'{i}_{text_i}.jpg'
        
                data = {
                    'img_path': image_fname,
                    'instances':[{'text':text}]
                    }
                data_list.append(data)
        
        result = {
            'metainfo':{
                'dataset_type':'TextRecogDataset',
                'task_name':'textrecog'
            },
            'data_list':data_list
        }

        with open('train_labels.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        if trdg_true:
            with open('trainTRDG_labels.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        self.makingJson_finish_signal.emit(True)

class MakeImageTRDG(QThread):

    trdg_finish_signal = Signal(int)

    def __init__(self, thread_num):
        super().__init__()
        self.thread_num = thread_num
        self.fonts = random.sample(fontsTRDG, len(fontsTRDG))
        
    def run(self):
        
        generator = GeneratorFromStrings(
            texts,
            fonts = self.fonts,
            count = len(texts),
            # Text blurring
            blur = 1,
            random_blur = True,
            # Text skewing
            skewing_angle = 1,
            random_skew = True,
        )
        
        for i, (img, _) in enumerate(generator):
            image_fname = f'{self.thread_num}_{i}.jpg'
            img.save(os.path.join('trainTRDG', image_fname), quality=95)
        
        self.trdg_finish_signal.emit(self.thread_num)

class MakeImage(QThread):

    finish_signal = Signal(int)

    def __init__(self, thread_num):
        super().__init__()
        self.currentfont = QFont()
        self.thread_num = thread_num
        
    def run(self):
        self.label_1 = QLabel()
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.saveimage()

        self.finish_signal.emit(self.thread_num)
    
    def saveimage(self):
        for i, text in enumerate(texts):
            self.label_1.setText(text)

            # Font 
            random_font = random.randrange(0, len(fonts))
            fontfamily, bold = fonts[random_font].split(',')
            self.currentfont.setFamily(fontfamily)
            self.currentfont.setBold(int(bold))

            # Letter spacing
            random_spacing = random.randrange(start=85, stop=120, step=5)
            self.currentfont.setLetterSpacing(QFont.PercentageSpacing, random_spacing)

            # Font size
            random_font = random.randrange(start=16, stop=22, step=2)
            self.currentfont.setPointSize(random_font)

            self.label_1.setFont(self.currentfont)
            self.label_1.adjustSize()

            # Margin
            random_margin = random.randrange(start=4, stop=16, step=4)
            width = self.label_1.width() + random_margin
            height = self.label_1.height() + random_margin
            self.label_1.resize(width, height)

            image = ImageQt.fromqpixmap(self.label_1.grab()) #RGB

            # Noise
            if noise_true:
                original_img = np.array(image)
                noise = np.random.normal(0, 2, original_img.shape)
                image = Image.fromarray((original_img + noise).astype('uint8'))

            # Quality
            random_quality = random.randrange(start=85, stop=100, step=5)
            image_fname = f'{self.thread_num}_{i}.jpg'
            image.save(os.path.join('train', image_fname), quality = random_quality)

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.thread_count = 0
        self.finish_count = 0
        self.initUI()

    def initUI(self):

        self.thread_list = []

        self.start_time = time.time()

        for i in range(repeat_n):
            self.thread_list.append(MakeImage(i))
            self.thread_count += 1

        for i in range(repeat_n):
            self.thread_list[i].finish_signal.connect(self.pyside_finish)
        for i in range(repeat_n):
            self.thread_list[i].start()

        self.makingJsonThread = MakeJson()
        self.thread_count += 1
        self.makingJsonThread.makingJson_finish_signal.connect(self.makingJson_finish)
        self.makingJsonThread.start()

        if trdg_true:
            self.trdg_thread_list = []
            for i in range(repeat_n):
                self.trdg_thread_list.append(MakeImageTRDG(i))
                self.thread_count += 1
            for i in range(repeat_n):
                self.trdg_thread_list[i].trdg_finish_signal.connect(self.trdg_finish)
            for i in range(repeat_n):
                self.trdg_thread_list[i].start()

    @Slot(int)
    def pyside_finish(self, recieved_signal):
        self.thread_list[recieved_signal].quit()
        self.finish_count += 1
        self.all_finish()
    
    @Slot(int)
    def trdg_finish(self, recieved_signal):
        self.trdg_thread_list[recieved_signal].quit()
        self.finish_count += 1
        self.all_finish()

    @Slot(bool)
    def makingJson_finish(self, recieved_signal):
        if recieved_signal:
            self.makingJsonThread.quit()
            self.finish_count += 1
            self.all_finish()
    
    def all_finish(self):
        if self.finish_count == self.thread_count:
            collapsed = time.time() - self.start_time
            print(f'{collapsed} sec')
            sys.exit()

if __name__ == "__main__":

    os.makedirs('train', exist_ok=True)
    
    with open('fonts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    fonts = [x.strip() for x in lines]

    with open('texts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    texts = [x.strip() for x in lines]

    if trdg_true:
        os.makedirs('trainTRDG', exist_ok=True)
        fontsTRDG = glob.glob('fonts/*.ttf')

    app = QApplication([])
    ex =Window()
    app.exec()