# ----- IMPORTS ---------#
from tkinter import *
import _thread
from tkinter import messagebox
import cv2
from openalpr import Alpr
import sys
from PIL import Image, ImageTk
import pymysql

pymysql.install_as_MySQLdb()

# ----- PRE CONFIG ------#
alpr = Alpr("br", "openalpr.conf", "runtime_data")

if not alpr.is_loaded():
    print("Erro ao carregar OpenALPR")
    sys.exit(1)

alpr.set_top_n(20)
alpr.set_default_region("br")

conn = None

lastPlate = ""


# ----- FUNCTIONS -------#
def connect_mysql():
    global conn
    conn = pymysql.Connection(
        host=mysqlHostEntry.get(),
        user=mysqlUserEntry.get(),
        passwd=mysqlPassEntry.get(),
        port=int(mysqlPortEntry.get()),
        db=mysqlDbEntry.get()
    )
    if conn.open:
        messagebox.showinfo("Alpr", "Conectado!")


def save_plate(plate):
    global conn
    conn.query(f"INSERT INTO plates (placa) VALUES ('{plate}')")
    conn.commit()


def detect(img):
    global lastPlate
    try:
        img_str = cv2.imencode('.jpg', img)[1].tostring()
        results = alpr.recognize_array(img_str)
        for plate in results['results']:
            if plate['matches_template']:

                x = plate['coordinates'][0]['x']
                y = plate['coordinates'][0]['y']
                w = plate['coordinates'][0]['x'] + plate['coordinates'][1]['x']
                h = plate['coordinates'][0]['y'] + plate['coordinates'][2]['y']

                crop = img[y:y + h, x:x + w]

                cv2.putText(img, plate['plate'], (x, y - 5), 0, 2, (0, 255, 0), 3)
                cv2.rectangle(img, (x, y), (plate['coordinates'][2]['x'], h), (0, 255, 0), 2)

                cv2.imshow('crop', crop)

                if saveplate.get():

                    if lastPlate != plate['plate']:
                        save_plate(plate['plate'])
                        lastPlate = plate['plate']

                plateTxtLabel.configure(text=plate['plate'])

                cv2.image = cv2.cvtColor(crop, cv2.COLOR_BGR2RGBA)
                img2 = Image.fromarray(cv2.image)
                imgtk = ImageTk.PhotoImage(image=img2)
                lastLabel.imgtk = imgtk
                lastLabel.configure(image=imgtk)
    except:
        pass
    return img


def show_frame():
    th = _thread.start_new(video_stream, ())


def video_stream():
    cap = cv2.VideoCapture(streamSrc.get())
    streamName = streamSrc.get()
    while True:
        ret, frame = cap.read()
        frame = detect(frame)
        cv2.imshow(streamName, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break


# ----- MAIN FRAME ------#
root = Tk()  # tkinter

root.geometry('600x600+200+200')  # Definindo tamanho da tela
root.wm_title("Detector de placas")

saveplate = IntVar()

# ----- DETECTS FRAME ------#
detectsFrame = LabelFrame(root, text="Detecções")
detectsFrame.place(relwidth=1, relheight=0.4)

plateTxtFrame = LabelFrame(detectsFrame, text="Placa detectada")
plateTxtFrame.place(relwidth=0.5, relheight=1)

plateTxtLabel = Label(plateTxtFrame, text="AAA0000", font=("Helvetica", 14))
plateTxtLabel.place(relx=0.5, rely=0.5, anchor="center")

plateImgFrame = LabelFrame(detectsFrame, text="Imagem Placa")
plateImgFrame.place(relx=0.5, relwidth=0.5, relheight=1)

lastLabel = Label(plateImgFrame, text="Imagem Final")
lastLabel.place(relx=0.5, rely=0.5, anchor="center")

# ----- CONFIG FRAME ------#
configFrame = LabelFrame(root, text="Configurações")
configFrame.place(relwidth=1, relheight=0.6, rely=0.4)

streamFrame = LabelFrame(configFrame, text="Stream")
streamFrame.place(relwidth=1, relheight=0.2)

streamSrc = Entry(streamFrame)
streamSrc.place(relwidth=0.75, relheight=0.6, relx=0.025, rely=0.15)
streamSrc.insert(0, "C:\\Users\\jfna\\Documents\\plate-detection-openalpr\\videos\\output5.avi")

streamStartBtn = Button(streamFrame, text="Iniciar", command=show_frame)
streamStartBtn.place(relwidth=0.25, relheight=0.6, relx=0.75, rely=0.15)

# ----- MYSQL FRAME ------#
mysqlFrame = LabelFrame(configFrame, text="MySql")
mysqlFrame.place(relwidth=1, relheight=0.8, rely=0.2)

mysqlHostTxt = Label(mysqlFrame, text="Host:", font=("Helvetica", 14))
mysqlHostTxt.place(relwidth=0.3, relheight=0.15)

mysqlHostEntry = Entry(mysqlFrame)
mysqlHostEntry.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.025)
mysqlHostEntry.insert(0, 'localhost')

mysqlPortTxt = Label(mysqlFrame, text="Port:", font=("Helvetica", 14))
mysqlPortTxt.place(rely=0.15, relwidth=0.3, relheight=0.15)

mysqlPortEntry = Entry(mysqlFrame)
mysqlPortEntry.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.175)
mysqlPortEntry.insert(0, '3307')

mysqlUserTxt = Label(mysqlFrame, text="Usuário:", font=("Helvetica", 14))
mysqlUserTxt.place(rely=0.3, relwidth=0.3, relheight=0.15)

mysqlUserEntry = Entry(mysqlFrame)
mysqlUserEntry.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.325)
mysqlUserEntry.insert(0, 'root')

mysqlPassTxt = Label(mysqlFrame, text="Senha:", font=("Helvetica", 14))
mysqlPassTxt.place(rely=0.45, relwidth=0.3, relheight=0.15)

mysqlPassEntry = Entry(mysqlFrame)
mysqlPassEntry.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.475)
mysqlPassEntry.insert(0, 'usbw')

mysqlDbTxt = Label(mysqlFrame, text="DB:", font=("Helvetica", 14))
mysqlDbTxt.place(rely=0.6, relwidth=0.3, relheight=0.15)

mysqlDbEntry = Entry(mysqlFrame)
mysqlDbEntry.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.625)
mysqlDbEntry.insert(0, 'plates')

mysqlConnectBtn = Button(mysqlFrame, text="Conectar", command=connect_mysql)
mysqlConnectBtn.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.9)

mysqlCheckBox = Checkbutton(mysqlFrame, text="Salvar placas", variable=saveplate)
mysqlCheckBox.place(relx=0.25, relwidth=0.65, relheight=0.1, rely=0.7)
# ----- START APP -------#
root.mainloop()
