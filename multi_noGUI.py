from PySide6.QtWidgets import QMainWindow, QApplication, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal, Slot, QThread
import sys
import os
import json
import random
from PIL import ImageQt
import time

from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('--repeat', type=int, default=3, help='count of repeat' )
args = parser.parse_args()
repeat_n = args.repeat

class MyThread(QThread):

    finish_signal = Signal(int)

    def __init__(self, thread_num):
        super().__init__()
        
        self.thread_num = thread_num
        

    def run(self):
        self.label_1 = QLabel()
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.saveimage()

        self.finish_signal.emit(self.thread_num)
    
    def saveimage(self):
        for i, text in enumerate(texts):
            currentfont = QFont()
            self.label_1.setText(text)

            # Font 
            random_font = random.randrange(0, len(fonts))
            fontfamily, bold = fonts[random_font].split(',')
            currentfont.setFamily(fontfamily)
            currentfont.setBold(int(bold))

            # Letter spacing
            random_spacing = random.randrange(start=85, stop=120, step=5)
            currentfont.setLetterSpacing(QFont.PercentageSpacing, random_spacing)

            # Font size
            random_font = random.randrange(start=16, stop=22, step=2)
            currentfont.setPointSize(random_font)

            self.label_1.setFont(currentfont)
            self.label_1.adjustSize()

            # Margin
            random_margin = random.randrange(start=4, stop=28, step=8)
            width = self.label_1.width() + random_margin
            height = self.label_1.height() + random_margin
            self.label_1.resize(width, height)

            image_fname = f'{self.thread_num}_{i}.jpg'
            image = ImageQt.fromqpixmap(self.label_1.grab()) #RGB

            # Quality
            random_quality = random.randrange(start=85, stop=100, step=5)
            image.save(os.path.join('train', image_fname), quality = random_quality)

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.finish_count = 0
        self.initUI()

    def initUI(self):

        self.thread_list = []

        self.start_time = time.time()

        for i in range(repeat_n):
            self.thread_list.append(MyThread(i))

        for i in range(repeat_n):
            self.thread_list[i].finish_signal.connect(self.update_signal)
        for i in range(repeat_n):
            self.thread_list[i].start()

    @Slot(int)
    def update_signal(self, recieved_signal):
        self.thread_list[recieved_signal].quit()
        self.finish_count += 1

        if self.finish_count == repeat_n:
            collapsed = time.time() - self.start_time
            print(f'{collapsed} sec')
            sys.exit()


        '''

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
        
        collapse = time.time() - start_time

        print(f'{collapse} sec')
        '''
if __name__ == "__main__":

    os.makedirs('train', exist_ok=True)
    
    with open('fonts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    fonts = [x.strip() for x in lines]

    with open('texts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    texts = [x.strip() for x in lines]

    app = QApplication([])
    ex =Window()
    app.exec()