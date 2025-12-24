import time
import json
import re
from pathlib import Path
from dataclasses import dataclass

import pytesseract
import pyautogui
from pynput.mouse import Controller, Button
from PIL import ImageGrab, ImageOps


# ======================================================
# 🔹 VisionPattern — representa um padrão aprendido
# ======================================================

@dataclass
class VisionPattern:
    id: str
    type: str               # "text"
    value: str
    state: str
    region: tuple | None
    confidence: float = 1.0
    hits: int = 1


# ======================================================
# 🔹 PatternStore — salva / carrega padrões
# ======================================================

class PatternStore:
    def __init__(self, path=None):
        self.path = path or Path.home() / ".nano-wait" / "vision_patterns.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.patterns: list[VisionPattern] = []
        self._load()

    def _load(self):
        if not self.path.exists():
            self._save()
        with open(self.path, "r") as f:
            data = json.load(f)
            self.patterns = [
                VisionPattern(**p) for p in data.get("patterns", [])
            ]

    def _save(self):
        with open(self.path, "w") as f:
            json.dump(
                {
                    "version": 1,
                    "patterns": [p.__dict__ for p in self.patterns]
                },
                f,
                indent=2
            )

    def match_text(self, text: str, region=None):
        """
        Tenta reconhecer texto usando padrões salvos.
        Retorna state ou None.
        """
        for p in self.patterns:
            if p.type == "text" and p.value.lower() in text.lower():
                if p.region is None or p.region == region:
                    p.hits += 1
                    self._save()
                    return p.state
        return None

    def add_pattern(self, pattern: VisionPattern):
        self.patterns.append(pattern)
        self._save()


# ======================================================
# 🔹 VisionMode — visão computacional + memória
# ======================================================

class VisionMode:
    """
    Modos:
      - observe  → apenas observa e reconhece estados
      - decision → toma ações automáticas
      - learn    → aprende novos padrões
    """

    def __init__(self, mode="observe", load_patterns=False):
        self.mode = mode
        self.mouse = Controller()
        self.store = PatternStore() if load_patterns else None
        print(f"🔍 VisionMode iniciado no modo '{self.mode}'")

    # --------------------------------------------------
    # 📸 OCR / captura
    # --------------------------------------------------

    def capture_text(self, regions=None) -> dict:
        """
        Retorna texto detectado por região.
        """
        results = {}

        if not regions:
            regions = [None]

        for idx, region in enumerate(regions):
            if region:
                x, y, w, h = region
                bbox = (x, y, x + w, y + h)
                img = ImageGrab.grab(bbox=bbox)
            else:
                img = ImageGrab.grab()

            img = ImageOps.grayscale(img)
            text = pytesseract.image_to_string(img)
            clean_text = text.strip()

            results[region or f"full_{idx}"] = clean_text

        return results

    # --------------------------------------------------
    # 🧠 OBSERVE — reconhece estados
    # --------------------------------------------------

    def observe(self, regions=None) -> str:
        texts = self.capture_text(regions)

        full_text = " ".join(texts.values())

        if self.store:
            state = self.store.match_text(full_text)
            if state:
                print(f"🧠 Estado reconhecido: {state}")
                return state

        return "unknown"

    # --------------------------------------------------
    # 📚 LEARN — salva novos padrões
    # --------------------------------------------------

    def learn(self, value: str, state: str, region=None, confidence=1.0):
        if not self.store:
            raise RuntimeError("PatternStore não está ativo")

        pattern = VisionPattern(
            id=f"{state}_{len(self.store.patterns)}",
            type="text",
            value=value,
            state=state,
            region=region,
            confidence=confidence
        )

        self.store.add_pattern(pattern)
        print(f"📚 Padrão aprendido e salvo: {state}")

    # --------------------------------------------------
    # ⚙️ ACTIONS (opcional, mantém compatibilidade)
    # --------------------------------------------------

    def perform_action(self, action):
        if action == "like_post":
            self.mouse.click(Button.left, 2)
            print("❤️ Ação: clique duplo.")
        elif action == "skip_post":
            self.mouse.move(100, 0)
            print("⏭ Ação: pular.")
        else:
            print(f"⚙️ Ação desconhecida: {action}")

    # --------------------------------------------------
    # 📌 MARK REGION (igual ao original)
    # --------------------------------------------------

    @staticmethod
    def mark_region():
        print("📌 Marque a região:")
        input("Clique no canto superior esquerdo e pressione Enter...")
        x1, y1 = pyautogui.position()

        input("Clique no canto inferior direito e pressione Enter...")
        x2, y2 = pyautogui.position()

        x, y = min(x1, x2), min(y1, y2)
        w, h = abs(x2 - x1), abs(y2 - y1)

        if w == 0 or h == 0:
            print("❌ Região inválida")
            return None

        print(f"✅ Região marcada: {x}, {y}, {w}, {h}")
        return (x, y, w, h)
