# SafeVision - Detector de EPIs em Tempo Real

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.5+-green.svg)](https://opencv.org/)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-orange.svg)](https://github.com/ultralytics/ultralytics)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**SafeVision** é um sistema de detecção de Equipamentos de Proteção Individual (EPIs) em tempo real usando visão computacional e inteligência artificial. Desenvolvido para monitorar conformidade de segurança em ambientes industriais.

---

## 📋 Índice

- [Características](#características)
- [Dataset](#dataset)
- [Tecnologias](#tecnologias)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
  - [Gravação Opcional](#gravação-opcional)
- [Funcionalidades Principais](#funcionalidades-principais)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Critérios de Conformidade](#critérios-de-conformidade)
- [Video Demo](#video-demo)
- [Autores](#autores)

---

## ✨ Características

✅ **Detecção em Tempo Real** - Processa webcam, vídeos e imagens  
✅ **Múltiplos EPIs** - Detecta capacete, colete, óculos, luvas e botas  
✅ **Painel de Monitoramento** - Dashboard com estatísticas em tempo real  
✅ **Som de Alerta** - Notificação sonora quando detecta não-conformidade  
✅ **Gravação Opcional** - Grava webcam com painel integrado (a escolha do usuário)  
✅ **Exportação de Relatório** - Gera arquivo `.txt` com estatísticas  
✅ **Filtros de Imagem** - 5 filtros OpenCV para processamento avançado  
✅ **Interface Gráfica** - GUI intuitiva com Tkinter  
✅ **Multi-plataforma** - Windows, Linux, macOS  

---

## 📊 Dataset

**Dataset utilizado:** Construction-PPE Dataset (Ultralytics)

O modelo foi treinado com o Construction-PPE Dataset, um conjunto de dados especializado para detecção de equipamentos de proteção individual em ambientes de construção e canteiros de obra.

**Dataset info:**
- **Classes detectadas:** Person, helmet, vest, goggles, gloves, boots, no_helmet, no_vest, no_goggle, no_gloves, no_boots
- **Fonte oficial:** https://docs.ultralytics.com/datasets/detect/construction-ppe#dataset-structure
- **Modelo:** YOLOv8 (treinado e otimizado para EPIs)

---

## 🛠️ Tecnologias

| Tecnologia | Versão | Propósito |
|------------|--------|----------|
| **Python** | 3.8+ | Linguagem principal |
| **YOLOv8** | Ultralytics | Modelo de detecção de objetos |
| **OpenCV** | 4.5+ | Processamento de imagens e vídeos |
| **Tkinter** | Nativa | Interface gráfica |
| **NumPy** | 1.19+ | Operações numéricas |
| **Pillow (PIL)** | 8.0+ | Manipulação de imagens |

---

## 📦 Requisitos

### Sistema Operacional
- Windows 10+, Ubuntu 18.04+, macOS 10.14+

### Hardware (recomendado)
- CPU: Intel Core i5 / AMD Ryzen 5 ou superior
- RAM: 8GB mínimo
- GPU: NVIDIA com CUDA (opcional, para melhor performance)

### Software
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

---

## 🚀 Instalação

### 1. Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/safevision.git
cd safevision
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Verificar Modelo Pré-treinado

O modelo YOLOv8 será baixado automaticamente na primeira execução:

```bash
# O modelo será salvo em modelo/best.pt
# Se estiver usando um modelo customizado, coloque em modelo/best.pt
```

---

## 💻 Como Usar

### Iniciar a Aplicação

```bash
python app.py
```

### Interface Principal

A janela principal oferece 6 opções:

#### 1. 📷 **Selecionar Imagem**
- Abre um arquivo de imagem (JPG, PNG)
- Detecta EPIs e exibe resultado com estatísticas

#### 2. 🎥 **Selecionar Vídeo**
- Processa vídeos (MP4, AVI, MOV, MKV)
- Gera vídeo anotado com detecções
- Mostra conformidade máxima do vídeo

#### 3. 📹 **Abrir Webcam (Monitorar)**
- Inicia fluxo ao vivo da câmera
- **NÃO grava vídeo** (apenas monitora)
- Mostra painel lateral com estatísticas em tempo real
- Perfeito para monitorar sem ocupar espaço em disco

**Controles:**
- `ESC` - Fecha webcam
- Sem gravação de vídeo

#### 4. 🔴 **Gravar Webcam**
- Abre um pop-up perguntando: **"Deseja gravar a webcam?"**
- **Opção 1:** Clica "Não" → Apenas monitora (sem gravar)
- **Opção 2:** Clica "Sim" → Abre webcam e **grava em MP4**

**Se escolher "Sim" (gravar):**
```
┌─────────────────────────────────┐
│  Pop-up: Gravar Webcam?         │
│                                 │
│  [Não] - Apenas monitorar       │
│  [Sim] - Gravar em vídeo MP4    │
└─────────────────────────────────┘
        │
        ↓ (se clica Sim)
   Webcam abre
   Painel mostra: "● GRAVANDO"
   Vídeo sendo salvo em:
   results/webcam_recordings/
   webcam_recording_YYYYMMDD_HHMMSS.mp4
```

**Painel mostra em tempo real:**
- ✓ Número de pessoas detectadas
- ✓ EPIs detectados (verde = presente, vermelho = ausente)
- ✓ Não-conformidades
- ✓ Barra de conformidade dinâmica (%)
- ✓ Status: "● GRAVANDO" ou "○ Monitorando"
- ✓ Alertas visuais e sonoros quando não-conformidade

**Controles:**
- `ESC` - Fecha webcam e finaliza gravação (se estiver gravando)

#### 5. 📊 **Exportar Relatório**
- **Disponível após usar a webcam** (qualquer uma das duas opções)
- Salva estatísticas em arquivo `.txt` em `results/relatorios/`
- Arquivo contém:
  - Data e hora
  - Máximo de pessoas detectadas
  - Total de frames processados
  - Conformidade (média, mínima, máxima)
  - Caminho do vídeo (se foi gravado)

#### 6. 🎨 **Filtros de Imagem**
- Aplica filtros OpenCV:
  - Escala de cinza
  - Desfoque (Gaussian Blur)
  - Detecção de bordas (Canny)
  - Segmentação (Thresholding)
  - Equalização de histograma

---

## 🎬 Gravação Opcional

### Quando Gravar?

**Use "Abrir Webcam (Monitorar)" quando:**
- ✓ Quer apenas acompanhar em tempo real
- ✓ Não precisa de registros
- ✓ Quer economizar espaço em disco
- ✓ Melhor performance (sem salvar vídeo)

**Use "Gravar Webcam" quando:**
- ✓ Quer registrar a sessão em vídeo
- ✓ Precisa de evidência para auditoria
- ✓ Vai usar para apresentação/demo
- ✓ Espaço em disco é suficiente

### Exemplo de Uso Prático

**Cenário 1: Monitoramento rápido**
```
1. Clica em "📹 Abrir Webcam (Monitorar)"
2. Webcam abre
3. Painel mostra: "○ Monitorando"
4. Você vê as detecções em tempo real
5. Não está gravando nada
6. Pressiona ESC para sair
7. Pop-up oferece "Exportar Relatório"
```

**Cenário 2: Demo para apresentação**
```
1. Clica em "🔴 Gravar Webcam"
2. Pop-up pergunta: "Deseja gravar?"
3. Você clica "Sim"
4. Webcam abre
5. Painel mostra: "● GRAVANDO"
6. Vídeo sendo salvo em tempo real
7. Você se mexe, faz detecções acontecerem
8. Após 30-60 segundos, pressiona ESC
9. Vídeo salvo em: results/webcam_recordings/
10. Pop-up oferece "Exportar Relatório"
11. Você usa esse vídeo na apresentação!
```

---

## 📂 Estrutura do Projeto

```
safevision/
├── app.py                          # Aplicação principal
├── requirements.txt                # Dependências Python
├── README.md                       # Este arquivo
├── LICENSE                         # Licença MIT
├── .gitignore                      # Arquivos ignorados
├── model/
│   └── best.pt                     # Modelo YOLOv8 treinado
├── results/                        # Saída de processamentos
│   ├── image_prediction.jpg        # Última imagem processada
│   ├── webcam_recordings/          # Vídeos gravados da webcam
│   │   └── webcam_recording_*.mp4
│   ├── relatorios/                 # Relatórios exportados
│   │   └── relatorio_safevision_*.txt
│   ├── filtros_imagem/             # Imagens com filtros aplicados
│   │   ├── Escala_de_cinza.jpg
│   │   ├── Desfoque.jpg
│   │   └── ...
│   └── video_prediction.avi        # Último vídeo processado
```

---

## 🎯 Funcionalidades Principais

### Painel de Monitoramento em Tempo Real

O painel lateral exibe:

```
┌─────────────────────┐
│  SafeVision         │
│  Tempo Real         │
├─────────────────────┤
│ PESSOAS DETECTADAS  │
│     3               │
├─────────────────────┤
│ EPIS OK             │
│ ✓ Cap: 2            │
│ ✓ Col: 3            │
│ ○ Ocs: 0            │
│ ✓ Luv: 2            │
│ ○ Bot: 0            │
├─────────────────────┤
│ NAO-CONFORMIDADES   │
│ ✗ Cap: 1            │
│ ○ Col: 0            │
│ ○ Ocs: 3            │
│ ○ Luv: 1            │
│ ○ Bot: 3            │
├─────────────────────┤
│ CONFORMIDADE        │
│  85.0% OK           │
│ ████████░░          │
│ ● GRAVANDO          │
└─────────────────────┘
```

### Cores Dinâmicas

- 🟢 **Verde (>=80%)** - Conformidade OK
- 🟠 **Laranja (50-79%)** - Atenção
- 🔴 **Vermelho (<50%)** - Crítico

### Som de Alerta

- Toca automaticamente quando detecta não-conformidade
- Compatível com Windows, Linux e macOS
- Sem dependências externas (nativo)
- Cooldown de 2 segundos entre alertas

### Gravação de Vídeo (Opcional)

- Grava apenas se usuário escolher via pop-up
- Inclui painel e relatório integrados
- Salvo em `results/webcam_recordings/`
- Formato: MP4 @ 30 FPS
- Nome do arquivo: `webcam_recording_20260623_143045.mp4`

---

## 📊 Exemplo de Relatório Exportado

```
======================================================================
RELATÓRIO DE CONFORMIDADE - SafeVision
======================================================================

Data/Hora: 23/06/2026 14:30:45

Pessoas máximas detectadas: 5
Total de frames processados: 1200

Conformidade média: 87.3%
Conformidade mínima: 65.2%
Conformidade máxima: 100.0%

Vídeo gravado em: results/webcam_recordings/webcam_recording_20260623_143045.mp4

======================================================================
Interpretação:
- Conformidade >= 80%: Excelente (OK)
- Conformidade 50-79%: Atenção (ATEN)
- Conformidade < 50%: Crítico (CRIT)
======================================================================
```

---

## 🎓 Critérios de Conformidade

### EPIs Detectados

| EPI | Classe | Status |
|-----|--------|--------|
| Capacete | `helmet` / `no_helmet` | Obrigatório |
| Colete | `vest` / `no_vest` | Obrigatório |
| Óculos | `goggles` / `no_goggle` | Obrigatório |
| Luvas | `gloves` / `no_gloves` | Obrigatório |
| Botas | `boots` / `no_boots` | Obrigatório |

### Regras de Validação

1. **Pessoa sem nenhum EPI** → Crítico (RED)
2. **Pessoa faltando qualquer EPI** → Não-conformidade
3. **Conformidade = 100% - (não-conformidades / pessoas) × 100**

### Interpretação

- ✅ **Conformidade ≥ 80%** - Excelente
- ⚠️ **Conformidade 50-79%** - Atenção
- 🚨 **Conformidade < 50%** - Crítico

---

## 🎬 Video Demo

[Clique aqui para assistir à demo](https://seu-link-aqui.com)

*Vídeo de demonstração mostrando:*
- Detecção em tempo real de EPIs
- Painel de monitoramento dinâmico
- Som de alerta automático
- Gravação opcional via pop-up
- Exportação de relatório com estatísticas

---

## 🔧 Configuração Avançada

### Ajustar Confiança de Detecção

Abra `app.py` e procure por:

```python
results = model.predict(frame, conf=0.4, verbose=False)
#                                    ↑
#                          Altere este valor (0.0-1.0)
```

Valores menores = mais detecções (menos precisão)  
Valores maiores = menos detecções (mais precisão)

### Usar Modelo Customizado

```python
MODEL_PATH = "caminho/para/seu/modelo.pt"
model = YOLO(MODEL_PATH)
```

---

## 🐛 Troubleshooting

### Erro: "Não foi possível acessar a webcam"

**Solução:**
1. Verifique se a câmera está conectada
2. Verifique permissões no SO
3. Feche outros aplicativos usando a câmera

### Erro: "Modelo não encontrado"

**Solução:**
1. Verifique se `model/best.pt` existe
2. Faça download do modelo: `python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"`

### Vídeo não foi gravado

**Solução:**
1. Verifique espaço em disco
2. Verifique permissões em `results/webcam_recordings/`
3. Certifique-se de ter clicado "Sim" no pop-up

### Som não funciona

**Solução:**
1. Verifique volume do sistema
2. Windows: reinicie o Windows Sound Service
3. Linux: verifique se `beep` está instalado

---

## 📝 Requisitos de Dependências

```
ultralytics>=8.0.0
opencv-python>=4.5.0
opencv-python-headless>=4.5.0
torch>=1.9.0
torchvision>=0.10.0
numpy>=1.19.0
Pillow>=8.0.0
```

---

## 📄 Licença

Este projeto está sob a licença **MIT**. Veja [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

**SafeVision** foi desenvolvido como trabalho prático da disciplina:

**CCC309 - Processamento de Imagens e Visão Computacional**  
Prof. Dr. Rafael Rieder  
Universidade de Passo Fundo (UPF) - 2026/1

**Equipe:**
- Alan (implementação de WebCam, painel, gravação e integração)
- Colega 1 (modelo de treinamento)
- Colega 2 (funcionalidades adicionais)

---

## 🙏 Agradecimentos

- **Ultralytics** - YOLOv8 e Construction-PPE Dataset
- **OpenCV** - Visão computacional
- **Python Community** - Ferramentas e bibliotecas

---

## 📧 Contato

Para dúvidas ou sugestões sobre o projeto:

- 📧 Email: seu-email@exemplo.com
- 🐙 GitHub: https://github.com/seu-usuario/safevision
- 👥 Orientador: Prof. Dr. Rafael Rieder (rieder@upf.br)

---

**Última atualização:** 23/06/2026  
**Versão:** 2.0.0 (com gravação opcional + documentação completa)