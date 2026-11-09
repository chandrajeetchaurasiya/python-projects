import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from core.engine import CalculatorEngine
from core.parser import CalculationError
from core.converter import FACTORS, convert
from database.history_db import HistoryDatabase
from utils.formatter import format_result
from ui import theme as T


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class QuantumCalcApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuantumCalc — Scientific Calculator")
        self.geometry("1040x760")
        self.minsize(820, 650)
        self.configure(fg_color=T.BG)
        self.engine = CalculatorEngine()
        self.history = HistoryDatabase()
        self.expression = tk.StringVar()
        self.result = tk.StringVar(value="0")
        self.status = tk.StringVar(value="Ready")
        self.memory = 0.0
        self.mode = tk.StringVar(value="Scientific")
        self._build()
        self.bind("<Key>", self._on_key)

    def _build(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(22, 12))
        brand = ctk.CTkFrame(header, fg_color="transparent")
        brand.pack(side="left")
        ctk.CTkLabel(brand, text="◈", text_color="#42B9FF", font=("Segoe UI", 30, "bold")).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(brand, text="QuantumCalc", text_color=T.TEXT, font=("Segoe UI", 25, "bold")).pack(side="left")
        ctk.CTkLabel(brand, text="  PRECISION IN EVERY CALCULATION", text_color=T.MUTED, font=("Segoe UI", 9, "bold")).pack(side="left", padx=12, pady=(10, 0))
        ctk.CTkLabel(header, text="●  READY", text_color="#65D6A0", font=("Segoe UI", 11, "bold")).pack(side="right", pady=10)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(4, 24))
        self.left = ctk.CTkFrame(body, fg_color="transparent")
        self.left.pack(side="left", fill="both", expand=True)
        self.right = ctk.CTkFrame(body, fg_color=T.PANEL, corner_radius=18, width=270)
        self.right.pack(side="right", fill="y", padx=(18, 0))
        self.right.pack_propagate(False)

        top = ctk.CTkFrame(self.left, fg_color="transparent")
        top.pack(fill="x", pady=(0, 12))
        ctk.CTkSegmentedButton(top, values=["Standard", "Scientific"], variable=self.mode,
                               command=self._mode_changed, selected_color=T.BLUE,
                               fg_color=T.BUTTON, text_color=T.TEXT).pack(side="left")
        self.angle_button = ctk.CTkButton(top, text="DEG", width=72, height=34, fg_color=T.SCI,
                                          hover_color=T.BLUE_HOVER, command=self._toggle_angle)
        self.angle_button.pack(side="right")

        display = ctk.CTkFrame(self.left, fg_color=T.PANEL, corner_radius=18)
        display.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(display, text="EXPRESSION", text_color=T.MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="e", padx=20, pady=(15, 0))
        ctk.CTkLabel(display, textvariable=self.expression, text_color="#B8D1E9",
                     font=("Segoe UI", 18), anchor="e", justify="right", wraplength=650).pack(fill="x", padx=20, pady=(6, 2))
        ctk.CTkFrame(display, height=1, fg_color="#263C55").pack(fill="x", padx=18, pady=8)
        ctk.CTkLabel(display, text="RESULT", text_color=T.MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="e", padx=20)
        ctk.CTkLabel(display, textvariable=self.result, text_color="#46B9FF",
                     font=("Segoe UI", 34, "bold"), anchor="e").pack(fill="x", padx=20, pady=(0, 15))

        controls = ctk.CTkFrame(self.left, fg_color="transparent")
        controls.pack(fill="x", pady=(0, 8))
        for label, command in [("MC", self._memory_clear), ("MR", self._memory_recall),
                               ("M+", self._memory_add), ("M−", self._memory_subtract),
                               ("HISTORY", self._show_history)]:
            ctk.CTkButton(controls, text=label, height=30, fg_color=T.SCI, hover_color=T.BLUE_HOVER,
                          font=("Segoe UI", 11, "bold"), command=command).pack(side="left", expand=True, fill="x", padx=3)

        self.keypad = ctk.CTkFrame(self.left, fg_color="transparent")
        self.keypad.pack(fill="both", expand=True)
        self._render_keypad()

        ctk.CTkLabel(self.right, text="QUICK TOOLS", text_color=T.TEXT,
                     font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=18, pady=(20, 4))
        ctk.CTkLabel(self.right, text="UNIT CONVERTER", text_color=T.MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(14, 5))
        self.category = ctk.CTkOptionMenu(self.right, values=["Length", "Mass", "Temperature", "Area", "Volume"],
                                          command=self._category_changed, fg_color=T.BUTTON, button_color=T.BLUE)
        self.category.pack(fill="x", padx=16)
        self.value_entry = ctk.CTkEntry(self.right, placeholder_text="Enter value", height=38)
        self.value_entry.pack(fill="x", padx=16, pady=(12, 8))
        self.from_unit = ctk.CTkOptionMenu(self.right, values=list(FACTORS["Length"]), fg_color=T.BUTTON, button_color=T.BLUE)
        self.from_unit.pack(fill="x", padx=16, pady=5)
        self.to_unit = ctk.CTkOptionMenu(self.right, values=list(FACTORS["Length"]), fg_color=T.BUTTON, button_color=T.BLUE)
        self.to_unit.pack(fill="x", padx=16, pady=5)
        ctk.CTkButton(self.right, text="Convert", command=self._convert, fg_color=T.BLUE,
                      hover_color=T.BLUE_HOVER).pack(fill="x", padx=16, pady=10)
        self.convert_result = ctk.CTkLabel(self.right, text="Conversion result appears here",
                                           text_color=T.MUTED, wraplength=220, justify="left")
        self.convert_result.pack(fill="x", padx=18, pady=(2, 8))
        ctk.CTkFrame(self.right, height=1, fg_color="#263C55").pack(fill="x", padx=16, pady=12)
        ctk.CTkLabel(self.right, text="KEYBOARD", text_color=T.MUTED,
                     font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18)
        ctk.CTkLabel(self.right, text="Enter  Calculate\nBackspace  Delete\nEsc  Clear\nUse * / + - and brackets", text_color="#A8C0D8",
                     justify="left", font=("Segoe UI", 11),).pack(anchor="w", padx=18, pady=8)
        ctk.CTkLabel(self, textvariable=self.status, text_color=T.MUTED,
                     font=("Segoe UI", 10)).pack(anchor="w", padx=30, pady=(0, 10))

    def _render_keypad(self):
        for child in self.keypad.winfo_children():
            child.destroy()
        scientific = self.mode.get() == "Scientific"
        rows = []
        if scientific:
            rows += [
                [("2nd", "2nd"), ("π", "pi"), ("e", "e"), ("(", "("), (")", ")")],
                [("sin", "sin("), ("cos", "cos("), ("tan", "tan("), ("√", "sqrt("), ("x²", "**2")],
                [("ln", "ln("), ("log", "log("), ("xʸ", "**"), ("n!", "factorial("), ("÷", "/")],
            ]
        rows += [
            [("7", "7"), ("8", "8"), ("9", "9"), ("×", "*"), ("AC", "AC")],
            [("4", "4"), ("5", "5"), ("6", "6"), ("−", "-"), ("⌫", "BACK")],
            [("1", "1"), ("2", "2"), ("3", "3"), ("+", "+"), ("%", "%")],
            [("±", "SIGN"), ("0", "0"), (".", "."), ("Ans", "ans"), ("=", "EQUAL")],
        ]
        for r, row in enumerate(rows):
            self.keypad.grid_rowconfigure(r, weight=1)
            for c, (label, value) in enumerate(row):
                self.keypad.grid_columnconfigure(c, weight=1)
                is_action = value in ("AC", "BACK", "EQUAL")
                is_operator = value in ("/", "*", "-", "+", "%", "**")
                color = T.BLUE if value == "EQUAL" else T.DANGER if value == "AC" else T.SCI if is_operator or label in ("sin","cos","tan","√","ln","log","xʸ","n!","x²") else T.BUTTON
                btn = ctk.CTkButton(self.keypad, text=label, command=lambda v=value: self._press(v),
                                    fg_color=color, hover_color=T.BLUE_HOVER, text_color=T.TEXT,
                                    corner_radius=11, font=("Segoe UI", 14, "bold"))
                btn.grid(row=r, column=c, sticky="nsew", padx=4, pady=4)

    def _press(self, value):
        current = self.expression.get()
        if value == "AC":
            self.expression.set("")
            self.result.set("0")
            self.status.set("Cleared")
        elif value == "BACK":
            self.expression.set(current[:-1])
        elif value == "EQUAL":
            self._calculate()
        elif value == "SIGN":
            if current.startswith("-"):
                self.expression.set(current[1:])
            elif current:
                self.expression.set("-(" + current + ")")
            else:
                self.expression.set("-")
        elif value == "2nd":
            self.status.set("Use asin(, acos( and atan( for inverse functions.")
        elif value == "%":
            self.expression.set(current + "/100")
        else:
            self.expression.set(current + value)
        self.focus_set()

    def _calculate(self):
        try:
            expr = self.expression.get()
            value = self.engine.calculate(expr)
            shown = format_result(value)
            self.result.set(shown)
            self.history.add(expr, shown)
            self.status.set("Calculation completed")
        except (CalculationError, ArithmeticError) as exc:
            self.result.set("—")
            self.status.set(str(exc))

    def _mode_changed(self, _value=None):
        self._render_keypad()

    def _toggle_angle(self):
        new_mode = "RAD" if self.engine.angle_mode == "DEG" else "DEG"
        self.engine.set_angle_mode(new_mode)
        self.angle_button.configure(text=new_mode)
        self.status.set(f"Angle mode: {new_mode}")

    def _memory_clear(self):
        self.memory = 0.0
        self.status.set("Memory cleared")

    def _memory_recall(self):
        self.expression.set(self.expression.get() + "ans" if False else self.expression.get() + str(self.memory))
        self.status.set("Memory recalled")

    def _memory_add(self):
        self.memory += float(self.engine.answer)
        self.status.set("Added current answer to memory")

    def _memory_subtract(self):
        self.memory -= float(self.engine.answer)
        self.status.set("Subtracted current answer from memory")

    def _show_history(self):
        win = ctk.CTkToplevel(self)
        win.title("Calculation History")
        win.geometry("560x500")
        win.configure(fg_color=T.BG)
        ctk.CTkLabel(win, text="Calculation History", font=("Segoe UI", 20, "bold"),
                     text_color=T.TEXT).pack(anchor="w", padx=20, pady=18)
        scroll = ctk.CTkScrollableFrame(win, fg_color=T.PANEL)
        scroll.pack(fill="both", expand=True, padx=18, pady=(0, 12))
        rows = self.history.latest()
        if not rows:
            ctk.CTkLabel(scroll, text="No calculations yet.", text_color=T.MUTED).pack(pady=20)
        for expr, result, stamp in rows:
            card = ctk.CTkFrame(scroll, fg_color=T.BUTTON, corner_radius=10)
            card.pack(fill="x", padx=6, pady=5)
            ctk.CTkLabel(card, text=expr, text_color="#B8D1E9", anchor="w").pack(fill="x", padx=12, pady=(8, 0))
            ctk.CTkLabel(card, text=result, text_color="#46B9FF", font=("Segoe UI", 17, "bold"),
                         anchor="w").pack(fill="x", padx=12)
            ctk.CTkLabel(card, text=stamp, text_color=T.MUTED, font=("Segoe UI", 9),
                         anchor="w").pack(fill="x", padx=12, pady=(0, 8))
            card.bind("<Button-1>", lambda _e, ex=expr: self._reuse_history(ex, win))
        ctk.CTkButton(win, text="Clear history", fg_color=T.DANGER, command=self._clear_history).pack(pady=(0, 14))

    def _reuse_history(self, expr, win):
        self.expression.set(expr)
        win.destroy()

    def _clear_history(self):
        if messagebox.askyesno("Clear history", "Delete all saved calculations?"):
            self.history.clear()
            self.status.set("History cleared")

    def _category_changed(self, category):
        units = ["°C", "°F", "K"] if category == "Temperature" else list(FACTORS[category])
        self.from_unit.configure(values=units)
        self.to_unit.configure(values=units)
        self.from_unit.set(units[0])
        self.to_unit.set(units[1] if len(units) > 1 else units[0])

    def _convert(self):
        try:
            category = self.category.get()
            value = float(self.value_entry.get())
            result = convert(category, value, self.from_unit.get(), self.to_unit.get())
            self.convert_result.configure(text=f"{format_result(value)} {self.from_unit.get()} =\n{format_result(result)} {self.to_unit.get()}",
                                          text_color="#46B9FF")
        except (ValueError, KeyError) as exc:
            self.convert_result.configure(text="Enter a valid value and unit.", text_color=T.DANGER)

    def _on_key(self, event):
        if event.keysym in ("Return", "KP_Enter"):
            self._calculate()
            return "break"
        if event.keysym == "Escape":
            self._press("AC")
            return "break"
        if event.keysym == "BackSpace":
            self._press("BACK")
            return "break"
        if event.char and event.char in "0123456789.+-*/()%":
            self.expression.set(self.expression.get() + event.char)
            return "break"
