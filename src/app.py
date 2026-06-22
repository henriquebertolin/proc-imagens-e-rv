import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from ultralytics import YOLO

MODEL_PATH = "model/best.pt"
RESULTS_DIR = "results"

os.makedirs(RESULTS_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)


def process_image():
    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
    )

    if not file_path:
        return

    results = model.predict(
        source=file_path,
        conf=0.4,
        save=True,
        project=RESULTS_DIR,
        name="image_prediction",
        exist_ok=True
    )

    messagebox.showinfo(
        "Processamento concluído",
        "Imagem processada com sucesso.\nResultado salvo na pasta results/image_prediction."
    )


def process_video():
    file_path = filedialog.askopenfilename(
        title="Selecione um vídeo",
        filetypes=[("Vídeos", "*.mp4 *.avi *.mov *.mkv")]
    )

    if not file_path:
        return

    results = model.predict(
        source=file_path,
        conf=0.4,
        save=True,
        project=RESULTS_DIR,
        name="video_prediction",
        exist_ok=True
    )

    messagebox.showinfo(
        "Processamento concluído",
        "Vídeo processado com sucesso.\nResultado salvo na pasta results/video_prediction."
    )


def process_webcam():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erro", "Não foi possível acessar a webcam.")
        return

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        results = model.predict(frame, conf=0.4, verbose=False)
        annotated_frame = results[0].plot()

        cv2.imshow("SafeVision - Webcam", annotated_frame)

        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


root = tk.Tk()
root.title("SafeVision - Detector de EPIs")
root.geometry("420x300")
root.resizable(False, False)

title = tk.Label(
    root,
    text="SafeVision",
    font=("Arial", 22, "bold")
)
title.pack(pady=15)

subtitle = tk.Label(
    root,
    text="Detector de EPIs em Ambientes Industriais",
    font=("Arial", 11)
)
subtitle.pack(pady=5)

btn_image = tk.Button(
    root,
    text="Selecionar Imagem",
    width=30,
    height=2,
    command=process_image
)
btn_image.pack(pady=8)

btn_video = tk.Button(
    root,
    text="Selecionar Vídeo",
    width=30,
    height=2,
    command=process_video
)
btn_video.pack(pady=8)

btn_webcam = tk.Button(
    root,
    text="Abrir Webcam",
    width=30,
    height=2,
    command=process_webcam
)
btn_webcam.pack(pady=8)

info = tk.Label(
    root,
    text="Pressione ESC para fechar a webcam.",
    font=("Arial", 9)
)
info.pack(pady=10)

root.mainloop()