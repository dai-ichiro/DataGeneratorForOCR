from PySide6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
import os
import json
import random
from PIL import ImageQt, Image

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.currentfont = QFont()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("pyQt6 sample")

        self.button1 = QPushButton('save as image')
        self.button1.clicked.connect(self.saveimage)

        self.label_1 = QLabel(self)
        self.label_1.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        self.setCentralWidget(self.button1)
    
    def saveimage(self):
        
        data_list = []
        
        for r in range(repeat_n):
            for i, text in enumerate(texts):
                
                self.label_1.setText(text)

                # Font 
                random_font = random.randrange(0, len(fonts))
                fontfamily, bold = fonts[random_font].split(',')
                self.currentfont.setFamily(fontfamily)
                self.currentfont.setBold(int(bold))

                # Letter spacing
                if len(text) < 15:
                    random_spacing = random.randrange(start=100, stop=120, step=5)
                else:
                    random_spacing = random.randrange(start=85, stop=105, step=5)
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

                image_fname = f'{r}_{i}.jpg'
                image = ImageQt.fromqpixmap(self.label_1.grab()) #RGBA
                background = Image.new("RGB", image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3]) # 3 is the alpha channel

                # Quality
                random_quality = random.randrange(start=85, stop=100, step=5)
                background.save(os.path.join('train', image_fname), quality = random_quality)

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

if __name__ == "__main__":

    repeat_n = 2

    os.makedirs('train', exist_ok=True)
    
    with open('fonts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    fonts = [x.strip() for x in lines]

    with open('texts.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    texts = [x.strip() for x in lines]

    app = QApplication([])
    ex =Window()
    ex.show()
    app.exec()