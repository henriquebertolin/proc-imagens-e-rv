import os
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO

MODEL_PATH = "model/best.pt"
RESULTS_DIR = "results"
FILTERS_DIR = os.path.join("runs", "detect", RESULTS_DIR, "filtros_imagem")


os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FILTERS_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)


def aplicar_escala_cinza(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(cinza, cv2.COLOR_GRAY2BGR)


def aplicar_desfoque(img):
    return cv2.GaussianBlur(img, (15, 15), 0)


def aplicar_deteccao_bordas(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bordas = cv2.Canny(cinza, 100, 200)
    return cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)


def aplicar_segmentacao(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, limiar = cv2.threshold(cinza, 127, 255, cv2.THRESH_BINARY)
    return cv2.cvtColor(limiar, cv2.COLOR_GRAY2BGR)


def aplicar_equalizacao(img):
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    equalizado = cv2.equalizeHist(cinza)
    return cv2.cvtColor(equalizado, cv2.COLOR_GRAY2BGR)


FILTROS_IMAGEM = {
    "Escala de cinza": aplicar_escala_cinza,
    "Desfoque (blur)": aplicar_desfoque,
    "Detecção de bordas": aplicar_deteccao_bordas,
    "Segmentação (limiarização)": aplicar_segmentacao,
    "Equalização de histograma": aplicar_equalizacao,
}

def calcular_conformidade_video(results):
    max_contagem = {
        "Person": 0,
        "helmet": 0,
        "vest": 0,
        "goggles": 0,
        "gloves": 0,
        "boots": 0,
        "no_helmet": 0,
        "no_goggle": 0,
        "no_gloves": 0,
        "no_boots": 0,
    }

    for result in results:
        contagem_frame = {classe: 0 for classe in max_contagem}

        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]

            if class_name in contagem_frame:
                contagem_frame[class_name] += 1

        for classe in max_contagem:
            max_contagem[classe] = max(max_contagem[classe], contagem_frame[classe])

    pessoas = max_contagem["Person"]

    nao_conformidades = (
        max_contagem["no_helmet"]
        + max_contagem["no_goggle"]
        + max_contagem["no_gloves"]
        + max_contagem["no_boots"]
    )

    epis_detectados = (
        max_contagem["helmet"]
        + max_contagem["vest"]
        + max_contagem["goggles"]
        + max_contagem["gloves"]
        + max_contagem["boots"]
    )

    if pessoas > 0:
        conformidade = max(0, 100 - ((nao_conformidades / pessoas) * 100))
    else:
        conformidade = 0

    resumo = (
        f"Resumo do vídeo por máximo em cena:\n\n"
        f"Máximo de pessoas: {pessoas}\n"
        f"Máximo de capacetes: {max_contagem['helmet']}\n"
        f"Máximo de coletes: {max_contagem['vest']}\n"
        f"Máximo de óculos: {max_contagem['goggles']}\n"
        f"Máximo de luvas: {max_contagem['gloves']}\n"
        f"Máximo de botas: {max_contagem['boots']}\n\n"
        f"Máximo sem capacete: {max_contagem['no_helmet']}\n"
        f"Máximo sem óculos: {max_contagem['no_goggle']}\n"
        f"Máximo sem luvas: {max_contagem['no_gloves']}\n"
        f"Máximo sem botas: {max_contagem['no_boots']}\n\n"
        f"EPIs detectados em cena: {epis_detectados}\n"
        f"Não conformidades em cena: {nao_conformidades}\n"
        f"Conformidade estimada: {conformidade:.1f}%"
    )

    return resumo

def calcular_conformidade(results):
    contagem = {
        "Person": 0,
        "helmet": 0,
        "vest": 0,
        "goggles": 0,
        "gloves": 0,
        "boots": 0,
        "no_helmet": 0,
        "no_goggle": 0,
        "no_gloves": 0,
        "no_boots": 0,
    }

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = result.names[class_id]

            if class_name in contagem:
                contagem[class_name] += 1

    pessoas = contagem["Person"]

    nao_conformidades = (
        contagem["no_helmet"]
        + contagem["no_goggle"]
        + contagem["no_gloves"]
        + contagem["no_boots"]
    )

    epis_detectados = (
        contagem["helmet"]
        + contagem["vest"]
        + contagem["goggles"]
        + contagem["gloves"]
        + contagem["boots"]
    )

    if pessoas > 0:
        conformidade = max(0, 100 - ((nao_conformidades / pessoas) * 100))
    else:
        conformidade = 0

    resumo = (
        f"Pessoas detectadas: {pessoas}\n"
        f"Capacetes: {contagem['helmet']}\n"
        f"Coletes: {contagem['vest']}\n"
        f"Óculos: {contagem['goggles']}\n"
        f"Luvas: {contagem['gloves']}\n"
        f"Botas: {contagem['boots']}\n\n"
        f"Sem capacete: {contagem['no_helmet']}\n"
        f"Sem óculos: {contagem['no_goggle']}\n"
        f"Sem luvas: {contagem['no_gloves']}\n"
        f"Sem botas: {contagem['no_boots']}\n\n"
        f"EPIs detectados: {epis_detectados}\n"
        f"Não conformidades: {nao_conformidades}\n"
        f"Conformidade estimada: {conformidade:.1f}%"
    )

    return resumo


def cv2_para_tk(img, tamanho_max=300):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_pil = Image.fromarray(img_rgb)
    img_pil.thumbnail((tamanho_max, tamanho_max))
    return ImageTk.PhotoImage(img_pil)


def open_image_filters_window():

    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
    )
    if not file_path:
        return

    original = cv2.imread(file_path)
    if original is None:
        messagebox.showerror("Erro", "Não foi possível abrir a imagem selecionada.")
        return

    win = tk.Toplevel(root)
    win.title("Filtros de Manipulação de Imagem")
    win.geometry("680x520")
    win.resizable(False, False)

    tk.Label(win, text="Escolha um filtro", font=("Arial", 13, "bold")).pack(pady=10)

    filtro_var = tk.StringVar(value=list(FILTROS_IMAGEM.keys())[0])
    opcoes_frame = tk.Frame(win)
    opcoes_frame.pack(pady=5)
    for nome_filtro in FILTROS_IMAGEM:
        tk.Radiobutton(opcoes_frame, text=nome_filtro, variable=filtro_var, value=nome_filtro, anchor="w").pack(fill="x", anchor="w")

    imagens_frame = tk.Frame(win)
    imagens_frame.pack(pady=15)

    tk.Label(imagens_frame, text="Original").grid(row=0, column=0)
    tk.Label(imagens_frame, text="Com filtro aplicado").grid(row=0, column=1)

    label_original = tk.Label(imagens_frame)
    label_original.grid(row=1, column=0, padx=10)

    label_filtrada = tk.Label(imagens_frame)
    label_filtrada.grid(row=1, column=1, padx=10)

    foto_original = cv2_para_tk(original)
    label_original.configure(image=foto_original)
    label_original.image = foto_original  

    def aplicar():
        nome_escolhido = filtro_var.get()
        resultado = FILTROS_IMAGEM[nome_escolhido](original)

        foto_resultado = cv2_para_tk(resultado)
        label_filtrada.configure(image=foto_resultado)
        label_filtrada.image = foto_resultado

        caminho_saida = os.path.join(FILTERS_DIR, f"{nome_escolhido.replace(' ', '_')}.jpg")

        print("FILTERS_DIR =", FILTERS_DIR)
        print("Salvando em:", caminho_saida)

        salvou = cv2.imwrite(caminho_saida, resultado)

        print("Salvou?", salvou)

    tk.Button(win, text="Aplicar filtro", width=20, command=aplicar).pack(pady=10)


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

    resumo = calcular_conformidade(results)

    messagebox.showinfo(
        "Processamento concluído",
        f"Imagem processada com sucesso.\n"
        f"Resultado salvo em runs/detect/results/image_prediction.\n\n"
        f"{resumo}"
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

    resumo = calcular_conformidade_video(results)

    messagebox.showinfo(
        "Processamento concluído",
        f"Vídeo processado com sucesso.\n"
        f"Resultado salvo em runs/detect/results/video_prediction.\n\n"
        f"{resumo}"
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
root.geometry("420x380")
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

btn_filters = tk.Button(
    root,
    text="Filtros de Imagem",
    width=30,
    height=2,
    command=open_image_filters_window
)
btn_filters.pack(pady=8)

info = tk.Label(
    root,
    text="Pressione ESC para fechar a webcam.",
    font=("Arial", 9)
)
info.pack(pady=10)

root.mainloop()