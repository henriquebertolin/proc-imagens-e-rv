import os
import cv2
import time
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from ultralytics import YOLO
import threading
import platform
from datetime import datetime

MODEL_PATH = "model/best.pt"
RESULTS_DIR = "results"
FILTERS_DIR = os.path.join("runs", "detect", RESULTS_DIR, "filtros_imagem")
VIDEOS_DIR = os.path.join(RESULTS_DIR, "webcam_recordings")
REPORTS_DIR = os.path.join(RESULTS_DIR, "relatorios")

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FILTERS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

model = YOLO(MODEL_PATH)

# Variáveis globais
ultimo_alerta = 0
alerta_cooldown = 2
gravando_webcam = False
video_writer = None
estatisticas_webcam = None


def emitir_alerta_sonoro():
    """Emite um som de alerta SEM dependências externas"""
    global ultimo_alerta
    
    agora = time.time()
    if agora - ultimo_alerta < alerta_cooldown:
        return
    
    ultimo_alerta = agora
    
    sistema = platform.system()
    
    try:
        if sistema == "Windows":
            import winsound
            winsound.Beep(1000, 200)
            time.sleep(0.1)
            winsound.Beep(1000, 200)
            
        elif sistema == "Darwin":
            os.system('afplay /System/Library/Sounds/Alarm.aiff')
            
        elif sistema == "Linux":
            try:
                os.system('echo -e "\a"')
                time.sleep(0.1)
                os.system('echo -e "\a"')
            except:
                pass
    except:
        pass


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
        "no_vest": 0,
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

    epis_detectados = (
        max_contagem["helmet"]
        + max_contagem["vest"]
        + max_contagem["goggles"]
        + max_contagem["gloves"]
        + max_contagem["boots"]
    )

    nao_conformidades = (
        max_contagem["no_helmet"]
        + max_contagem["no_vest"]
        + max_contagem["no_goggle"]
        + max_contagem["no_gloves"]
        + max_contagem["no_boots"]
    )

    if pessoas > 0 and epis_detectados == 0:
        nao_conformidades += pessoas

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
        f"Máximo sem colete: {max_contagem['no_vest']}\n"
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
        "no_vest": 0,
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

    epis_detectados = (
        contagem["helmet"]
        + contagem["vest"]
        + contagem["goggles"]
        + contagem["gloves"]
        + contagem["boots"]
    )

    nao_conformidades = (
        contagem["no_helmet"]
        + contagem["no_vest"]
        + contagem["no_goggle"]
        + contagem["no_gloves"]
        + contagem["no_boots"]
    )

    if pessoas > 0 and epis_detectados == 0:
        nao_conformidades += pessoas

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
        f"Sem colete: {contagem['no_vest']}\n"
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


def mostrar_resultado_imagem(img, resumo):
    win = tk.Toplevel(root)
    win.title("Resultado da Detecção")
    win.geometry("720x720")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Resultado da Detecção de EPIs",
        font=("Arial", 15, "bold")
    ).pack(pady=10)

    foto = cv2_para_tk(img, tamanho_max=500)

    label_img = tk.Label(win, image=foto)
    label_img.image = foto
    label_img.pack(pady=10)

    label_resumo = tk.Label(
        win,
        text=resumo,
        font=("Arial", 10),
        justify="left"
    )
    label_resumo.pack(pady=10)

def process_image():
    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Imagens", "*.jpg *.jpeg *.png")]
    )

    if not file_path:
        return

    img = cv2.imread(file_path)
    if img is None:
        messagebox.showerror("Erro", "Não foi possível abrir a imagem selecionada.")
        return

    results = model.predict(img, conf=0.4, verbose=False)
    annotated = results[0].plot()

    resumo = calcular_conformidade(results)
    mostrar_resultado_imagem(annotated, resumo)

    cv2.imwrite(os.path.join(RESULTS_DIR, "image_prediction.jpg"), annotated)

    messagebox.showinfo(
        "Processamento concluído",
        "Imagem processada com sucesso.\n"
        "Resultado salvo em results/image_prediction.jpg"
    )


def mostrar_resultado_video(resumo, caminho_video):
    win = tk.Toplevel(root)
    win.title("Resultado do Vídeo")
    win.geometry("650x650")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Resultado da Detecção no Vídeo",
        font=("Arial", 15, "bold")
    ).pack(pady=10)

    tk.Label(
        win,
        text=resumo,
        font=("Arial", 10),
        justify="left"
    ).pack(pady=10)

    tk.Label(
        win,
        text=f"Vídeo salvo em:\n{caminho_video}",
        font=("Arial", 9),
        wraplength=480
    ).pack(pady=10)

    tk.Button(
        win,
        text="Abrir vídeo processado",
        width=25,
        command=lambda: os.startfile(caminho_video) if platform.system() == "Windows" else os.system(f'open "{caminho_video}"')
    ).pack(pady=10)

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

    save_dir = str(results[0].save_dir)
    nome_base = os.path.splitext(os.path.basename(file_path))[0]
    caminho_video = os.path.join(save_dir, nome_base + ".avi")

    mostrar_resultado_video(resumo, caminho_video)


def exportar_relatorio():
    """Exporta as estatísticas da webcam em um arquivo .txt"""
    global estatisticas_webcam
    
    if estatisticas_webcam is None:
        messagebox.showwarning("Aviso", "Execute a webcam primeiro para gerar um relatório.")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_arquivo = f"relatorio_safevision_{timestamp}.txt"
    caminho = os.path.join(REPORTS_DIR, nome_arquivo)
    
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RELATÓRIO DE CONFORMIDADE - SafeVision\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")
        
        f.write(estatisticas_webcam)
        
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("Interpretação:\n")
        f.write("- Conformidade >= 80%: Excelente (OK)\n")
        f.write("- Conformidade 50-79%: Atenção (ATEN)\n")
        f.write("- Conformidade < 50%: Crítico (CRIT)\n")
        f.write("=" * 70 + "\n")
    
    messagebox.showinfo(
        "Relatório exportado",
        f"Relatório salvo em:\n{caminho}"
    )


def process_webcam(gravar=False):
    """Abre webcam com ou sem gravação
    
    Args:
        gravar (bool): Se True, grava vídeo. Se False, apenas monitora.
    """
    global estatisticas_webcam, video_writer
    
    # DESIGN PROFISSIONAL DO PAINEL
    PANEL_W = 320
    PANEL_BG = (20, 20, 30)
    DIVIDER_COLOR = (50, 50, 70)
    TEXT_COLOR = (240, 240, 245)
    OK_COLOR = (76, 175, 80)
    WARN_COLOR = (244, 67, 54)
    ALERT_COLOR = (255, 152, 0)
    TITLE_COLOR = (200, 200, 215)
    ACCENT_COLOR = (66, 165, 245)
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_MONO = cv2.FONT_MONOSPACE

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        messagebox.showerror("Erro", "Não foi possível acessar a webcam.")
        return

    # Setup para gravação (se solicitado)
    video_writer = None
    video_path = None
    
    if gravar:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = os.path.join(VIDEOS_DIR, f"webcam_recording_{timestamp}.mp4")
        
        fps = int(cap.get(cv2.CAP_PROP_FPS)) or 30
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        video_writer = cv2.VideoWriter(video_path, fourcc, fps, 
                                        (frame_width + PANEL_W, frame_height))

    alert_state = False
    alert_timer = 0.0
    ALERT_BLINK_INTERVAL = 0.3
    
    # Para armazenar estatísticas finais
    historico_conformidade = []
    max_pessoas = 0
    total_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = model.predict(frame, conf=0.4, verbose=False)
        annotated = results[0].plot()

        contagem = {
            "Person": 0,
            "helmet": 0,
            "vest": 0,
            "goggles": 0,
            "gloves": 0,
            "boots": 0,
            "no_helmet": 0,
            "no_vest": 0,
            "no_goggle": 0,
            "no_gloves": 0,
            "no_boots": 0,
        }

        for box in results[0].boxes:
            class_id = int(box.cls[0])
            class_name = results[0].names[class_id]
            if class_name in contagem:
                contagem[class_name] += 1

        pessoas = contagem["Person"]
        max_pessoas = max(max_pessoas, pessoas)
        
        epis_detectados = (
            contagem["helmet"]
            + contagem["vest"]
            + contagem["goggles"]
            + contagem["gloves"]
            + contagem["boots"]
        )

        nao_conformidades = (
            contagem["no_helmet"]
            + contagem["no_vest"]
            + contagem["no_goggle"]
            + contagem["no_gloves"]
            + contagem["no_boots"]
        )

        if pessoas > 0 and epis_detectados == 0:
            nao_conformidades += pessoas

        conformidade = (
            max(0.0, 100.0 - (nao_conformidades / pessoas * 100.0))
            if pessoas > 0
            else 0.0
        )
        
        historico_conformidade.append(conformidade)
        total_frames += 1

        tem_alerta = nao_conformidades > 0

        if tem_alerta:
            threading.Thread(target=emitir_alerta_sonoro, daemon=True).start()

        now = time.time()
        if tem_alerta:
            if now - alert_timer >= ALERT_BLINK_INTERVAL:
                alert_state = not alert_state
                alert_timer = now
        else:
            alert_state = False
            alert_timer = now

        h, w = annotated.shape[:2]
        panel = np.full((h, PANEL_W, 3), PANEL_BG, dtype=np.uint8)

        def txt(img, text, x, y, scale=0.45, color=TEXT_COLOR, thickness=1, font=FONT):
            cv2.putText(img, text, (x, y), font, scale, color, thickness, cv2.LINE_AA)

        def linha(img, y, cor=DIVIDER_COLOR):
            cv2.line(img, (15, y), (PANEL_W - 15, y), cor, 1)

        def caixa_titulo(img, title, y, color=ACCENT_COLOR):
            cv2.rectangle(img, (10, y - 20), (PANEL_W - 10, y + 2), color, -1)
            txt(img, title, 15, y - 5, 0.50, (20, 20, 30), 1, FONT)
            return y + 15

        y = 25
        txt(panel, "SafeVision", 15, y, 0.65, ACCENT_COLOR, 2, FONT)
        y += 20
        txt(panel, "Tempo Real", 15, y, 0.38, TITLE_COLOR)
        y += 25

        linha(panel, y)
        y += 10
        y = caixa_titulo(panel, "PESSOAS", y, ACCENT_COLOR)
        txt(panel, str(pessoas).rjust(3), 15, y + 15, 0.80, OK_COLOR if pessoas > 0 else TEXT_COLOR, 2, FONT_MONO)
        y += 35

        linha(panel, y)
        y += 10
        y = caixa_titulo(panel, "EPIS OK", y, OK_COLOR)
        epis_items = [
            ("Cap:", contagem["helmet"]),
            ("Col:", contagem["vest"]),
            ("Ocs:", contagem["goggles"]),
            ("Luv:", contagem["gloves"]),
            ("Bot:", contagem["boots"]),
        ]
        for label, val in epis_items:
            icon = "✓" if val > 0 else "○"
            cor = OK_COLOR if val > 0 else TEXT_COLOR
            txt(panel, f"{icon} {label} {val:2d}", 15, y, 0.38, cor)
            y += 16

        y += 5
        linha(panel, y)
        y += 10
        cor_alerta = WARN_COLOR if tem_alerta else TITLE_COLOR
        y = caixa_titulo(panel, "NAO-CONF", y, cor_alerta)
        
        non_conform_items = [
            ("Cap:", contagem["no_helmet"]),
            ("Col:", contagem["no_vest"]),
            ("Ocs:", contagem["no_goggle"]),
            ("Luv:", contagem["no_gloves"]),
            ("Bot:", contagem["no_boots"]),
        ]
        for label, val in non_conform_items:
            icon = "✗" if val > 0 else "○"
            cor = WARN_COLOR if val > 0 else TEXT_COLOR
            txt(panel, f"{icon} {label} {val:2d}", 15, y, 0.38, cor)
            y += 16

        y += 5
        linha(panel, y)
        y += 12
        txt(panel, "CONFORMIDADE", 15, y, 0.42, TITLE_COLOR, 1, FONT)
        y += 22

        if conformidade >= 80:
            cor_conf = OK_COLOR
            status = "OK"
        elif conformidade >= 50:
            cor_conf = ALERT_COLOR
            status = "ATEN"
        else:
            cor_conf = WARN_COLOR
            status = "CRIT"

        txt(panel, f"{conformidade:5.1f}%", 15, y, 0.75, cor_conf, 2, FONT_MONO)
        txt(panel, status, PANEL_W - 50, y - 5, 0.40, cor_conf, 1)
        y += 32

        barra_h = 8
        barra_w = PANEL_W - 30
        barra_x = 15
        cv2.rectangle(panel, (barra_x, y), (barra_x + barra_w, y + barra_h), (80, 80, 100), -1)
        progresso_px = int((conformidade / 100.0) * barra_w)
        cv2.rectangle(panel, (barra_x, y), (barra_x + progresso_px, y + barra_h), cor_conf, -1)

        # Status de gravação
        y += 20
        if gravar:
            cor_grav = (0, 255, 0)
            status_grav = "● GRAVANDO"
        else:
            cor_grav = (100, 100, 100)
            status_grav = "○ Monitorando"
        txt(panel, status_grav, 15, y, 0.38, cor_grav)

        if tem_alerta and alert_state:
            overlay = annotated.copy()
            cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), -1)
            cv2.addWeighted(overlay, 0.15, annotated, 0.85, 0, annotated)
            
            banner_h = 45
            cv2.rectangle(annotated, (0, h - banner_h), (w, h), (0, 0, 200), -1)
            cv2.putText(
                annotated,
                "!!! ALERTA: NAO-CONFORMIDADE DETECTADA !!!",
                (10, h - 12),
                FONT, 0.70, (255, 255, 255), 2, cv2.LINE_AA
            )

        combined = np.hstack([annotated, panel])
        
        # Grava o frame se solicitado
        if gravar and video_writer:
            video_writer.write(combined)
        
        titulo = "SafeVision - Webcam (ESC para sair)"
        cv2.imshow(titulo, combined)

        if cv2.waitKey(1) == 27:  # ESC
            break

    # Finaliza gravação
    if video_writer:
        video_writer.release()
    
    cap.release()
    cv2.destroyAllWindows()
    
    # Calcula estatísticas finais
    if historico_conformidade:
        conformidade_media = np.mean(historico_conformidade)
        conformidade_min = np.min(historico_conformidade)
        conformidade_max = np.max(historico_conformidade)
        
        if gravar:
            msg_video = f"Vídeo gravado em: {video_path}\n\n"
        else:
            msg_video = ""
        
        estatisticas_webcam = (
            f"Pessoas máximas detectadas: {max_pessoas}\n"
            f"Total de frames processados: {total_frames}\n\n"
            f"Conformidade média: {conformidade_media:.1f}%\n"
            f"Conformidade mínima: {conformidade_min:.1f}%\n"
            f"Conformidade máxima: {conformidade_max:.1f}%\n\n"
            f"{msg_video}"
        )
        
        if gravar:
            messagebox.showinfo(
                "Webcam fechada",
                f"Vídeo gravado com sucesso em:\n{video_path}\n\n"
                f"Conformidade média: {conformidade_media:.1f}%\n"
                f"Clique em 'Exportar Relatório' para salvar as estatísticas."
            )
        else:
            messagebox.showinfo(
                "Webcam fechada",
                f"Monitoramento finalizado.\n\n"
                f"Conformidade média: {conformidade_media:.1f}%\n"
                f"Clique em 'Exportar Relatório' para salvar as estatísticas."
            )


def confirmacao_gravacao():
    """Abre um pop-up perguntando se deseja gravar a webcam"""
    resposta = messagebox.askyesno(
        "Gravar Webcam?",
        "Deseja gravar a webcam em vídeo MP4?\n\n"
        "Sim → Abre webcam COM gravação\n"
        "Não → Abre webcam SEM gravação\n\n"
        "(Apenas monitorar)"
    )
    
    if resposta:
        process_webcam(gravar=True)
    else:
        process_webcam(gravar=False)


root = tk.Tk()
root.title("SafeVision - Detector de EPIs")
root.geometry("450x520")
root.resizable(False, False)

title = tk.Label(
    root,
    text="SafeVision",
    font=("Arial", 24, "bold"),
    fg="#4285F4"
)
title.pack(pady=15)

subtitle = tk.Label(
    root,
    text="Detector de EPIs em Ambientes Industriais",
    font=("Arial", 11),
    fg="#666"
)
subtitle.pack(pady=5)

info_box = tk.Frame(root, bg="#f5f5f5", height=50)
info_box.pack(fill="x", padx=10, pady=10)
info_text = tk.Label(
    info_box,
    text="✓ Som de alerta nativo\n✓ Gravação opcional de webcam\n✓ Exportação de relatório",
    font=("Arial", 9),
    bg="#f5f5f5",
    justify="left"
)
info_text.pack(padx=10, pady=5)

btn_image = tk.Button(
    root,
    text="📷 Selecionar Imagem",
    width=35,
    height=2,
    command=process_image,
    bg="#4285F4",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_image.pack(pady=6)

btn_video = tk.Button(
    root,
    text="🎥 Selecionar Vídeo",
    width=35,
    height=2,
    command=process_video,
    bg="#34A853",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_video.pack(pady=6)

btn_webcam = tk.Button(
    root,
    text="📹 Abrir Webcam (Monitorar)",
    width=35,
    height=2,
    command=lambda: process_webcam(gravar=False),
    bg="#EA4335",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_webcam.pack(pady=6)

btn_gravar = tk.Button(
    root,
    text="🔴 Gravar Webcam",
    width=35,
    height=2,
    command=confirmacao_gravacao,
    bg="#9C27B0",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_gravar.pack(pady=6)

btn_export = tk.Button(
    root,
    text="📊 Exportar Relatório",
    width=35,
    height=2,
    command=exportar_relatorio,
    bg="#FF6F00",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_export.pack(pady=6)

btn_filters = tk.Button(
    root,
    text="🎨 Filtros de Imagem",
    width=35,
    height=2,
    command=open_image_filters_window,
    bg="#FBBC04",
    fg="white",
    font=("Arial", 10, "bold"),
    relief="flat",
    cursor="hand2"
)
btn_filters.pack(pady=6)

info = tk.Label(
    root,
    text="Webcam: ESC = sair | Gravação: opcional com pop-up",
    font=("Arial", 8),
    fg="#999"
)
info.pack(pady=8)

root.mainloop()