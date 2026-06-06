# -*- coding: utf-8 -*-
import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRectF, QTimer, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush


class LogoWidget(QWidget):
    """
    Logo animada do Orbitask.
    - Satelite azul orbita o planeta no anel inclinado
    - Satelite verde orbita no sentido oposto, mais devagar
    - Planeta pulsa levemente
    """

    def __init__(self, size=40, animated=True, parent=None):
        super().__init__(parent)
        self.logo_size = size
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        # Angulos de orbita
        self._angulo_sat1 = 0.0   # satelite azul
        self._angulo_sat2 = 180.0 # satelite verde (oposto)
        self._pulso       = 0.0   # pulso do planeta

        if animated:
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._animar)
            self._timer.start(16)  # ~60fps

    def _animar(self):
        self._angulo_sat1 = (self._angulo_sat1 + 1.8) % 360
        self._angulo_sat2 = (self._angulo_sat2 + 1.1) % 360
        self._pulso = (self._pulso + 0.05) % (2 * math.pi)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx = self.logo_size / 2
        cy = self.logo_size / 2
        s  = self.logo_size / 140

        # --- Anel externo fixo ---
        p.setPen(QPen(QColor("#1a6fd4"), 1.5 * s))
        p.setBrush(Qt.BrushStyle.NoBrush)
        r_ext = 62 * s
        p.drawEllipse(QRectF(cx - r_ext, cy - r_ext, r_ext * 2, r_ext * 2))

        # --- Anel médio inclinado (-30°) ---
        p.save()
        p.translate(cx, cy)
        p.rotate(-30)
        p.setPen(QPen(QColor("#1a6fd4"), 2 * s))
        p.drawEllipse(QRectF(-62 * s, -24 * s, 124 * s, 48 * s))
        p.restore()

        # --- Anel interno tracejado ---
        pen3 = QPen(QColor("#4a9eff"), 1 * s)
        pen3.setStyle(Qt.PenStyle.DashLine)
        p.setPen(pen3)
        r_int = 36 * s
        p.drawEllipse(QRectF(cx - r_int, cy - r_int, r_int * 2, r_int * 2))

        # --- Planeta com pulso ---
        pulso_extra = math.sin(self._pulso) * 1.5 * s
        r_planet = (22 * s) + pulso_extra
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#0d2540")))
        p.drawEllipse(QRectF(cx - r_planet, cy - r_planet, r_planet * 2, r_planet * 2))

        pen_planet = QPen(QColor("#1a6fd4"), 2 * s)
        p.setPen(pen_planet)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.drawEllipse(QRectF(cx - r_planet, cy - r_planet, r_planet * 2, r_planet * 2))

        # Nucleo brilhante
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#1a6fd4")))
        r_core = 14 * s
        p.drawEllipse(QRectF(cx - r_core, cy - r_core, r_core * 2, r_core * 2))

        # Reflexo
        p.setBrush(QBrush(QColor(74, 158, 255, 120)))
        r_refl = 5 * s
        p.drawEllipse(QRectF(cx - 8*s - r_refl, cy - 8*s - r_refl, r_refl*2, r_refl*2))

        # --- Satelite 1 (azul) — orbita no anel inclinado ---
        ang1_rad = math.radians(self._angulo_sat1)
        # Elipse inclinada: a=62s, b=24s, rotacao=-30°
        ex1 = 62 * s * math.cos(ang1_rad)
        ey1 = 24 * s * math.sin(ang1_rad)
        # Rotacao de -30°
        rot = math.radians(-30)
        rx1 = ex1 * math.cos(rot) - ey1 * math.sin(rot)
        ry1 = ex1 * math.sin(rot) + ey1 * math.cos(rot)

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor("#4a9eff")))
        r_s1 = 7 * s
        p.drawEllipse(QRectF(cx + rx1 - r_s1, cy + ry1 - r_s1, r_s1*2, r_s1*2))
        # Brilho
        p.setBrush(QBrush(QColor(255, 255, 255, 210)))
        p.drawEllipse(QRectF(cx + rx1 - 4*s, cy + ry1 - 4*s, 8*s, 8*s))

        # --- Satelite 2 (verde) — orbita no anel externo ---
        ang2_rad = math.radians(self._angulo_sat2)
        rx2 = 62 * s * math.cos(ang2_rad)
        ry2 = 62 * s * math.sin(ang2_rad)

        p.setBrush(QBrush(QColor("#2ab87a")))
        r_s2 = 5 * s
        p.drawEllipse(QRectF(cx + rx2 - r_s2, cy + ry2 - r_s2, r_s2*2, r_s2*2))
        p.setBrush(QBrush(QColor(255, 255, 255, 200)))
        p.drawEllipse(QRectF(cx + rx2 - 3*s, cy + ry2 - 3*s, 6*s, 6*s))

        p.end()