#!/usr/bin/env python3
"""
Kalkulator GUI sederhana menggunakan Tkinter.
Simpan sebagai `kalkulator.py` lalu jalankan:
    python kalkulator.py

Fitur:
- Tampilan seperti kalkulator biasa
- Operasi: + - × ÷ * / % **
- Tombol Clear (C), Backspace (⌫), tanda +/-
- Dukungan keyboard (angka, + - * / Enter Backspace Esc)
- Evaluasi ekspresi yang aman menggunakan ast (hanya angka dan operator dasar)
"""
import tkinter as tk
from tkinter import ttk
import ast
import operator

# Evaluator aman menggunakan AST
ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.FloorDiv: operator.floordiv,
}


def safe_eval(expr: str):
    """Evaluasi ekspresi matematika sederhana secara aman.
    Mendukung + - * / % // dan pangkat (**). Mengizinkan angka float dan integer.
    """
    # Ganti simbol kalkulator umum ke operator Python
    expr = expr.replace('×', '*').replace('÷', '/').replace('^', '**')

    try:
        node = ast.parse(expr, mode='eval')
    except SyntaxError:
        raise ValueError('Sintaks salah')

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Num):  # < Py3.8
            return node.n
        if isinstance(node, ast.Constant):  # Py3.8+
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError('Tipe konstanta tidak diizinkan')
        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_OPERATORS:
                raise ValueError('Operator tidak diizinkan')
            left = _eval(node.left)
            right = _eval(node.right)
            return ALLOWED_OPERATORS[op_type](left, right)
        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in ALLOWED_OPERATORS:
                raise ValueError('Operator unary tidak diizinkan')
            operand = _eval(node.operand)
            return ALLOWED_OPERATORS[op_type](operand)
        if isinstance(node, ast.Call):
            raise ValueError('Pemanggilan fungsi tidak diizinkan')
        raise ValueError('Ekspresi tidak diizinkan')

    return _eval(node)


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Kalkulator')
        self.resizable(False, False)
        self.configure(bg='#222')

        self.expr = ''

        self._create_widgets()
        self._bind_keys()

    def _create_widgets(self):
        style = ttk.Style(self)
        style.theme_use('default')

        # Tampilan (entry-like label)
        self.display_var = tk.StringVar()
        self.display = ttk.Label(self, textvariable=self.display_var, anchor='e', font=('Segoe UI', 28), background='#222', foreground='white')
        self.display.grid(row=0, column=0, columnspan=4, sticky='nsew', padx=10, pady=(10, 0))

        btn_specs = [
            ('C', 1, 0, self.clear), ('+/-', 1, 1, self.negate), ('%', 1, 2, self.percent), ('⌫', 1, 3, self.backspace),
            ('7', 2, 0, lambda: self.append('7')), ('8', 2, 1, lambda: self.append('8')), ('9', 2, 2, lambda: self.append('9')), ('÷', 2, 3, lambda: self.append('÷')),
            ('4', 3, 0, lambda: self.append('4')), ('5', 3, 1, lambda: self.append('5')), ('6', 3, 2, lambda: self.append('6')), ('×', 3, 3, lambda: self.append('×')),
            ('1', 4, 0, lambda: self.append('1')), ('2', 4, 1, lambda: self.append('2')), ('3', 4, 2, lambda: self.append('3')), ('-', 4, 3, lambda: self.append('-')),
            ('0', 5, 0, lambda: self.append('0')), ('.', 5, 1, lambda: self.append('.')), ('=', 5, 2, self.evaluate), ('+', 5, 3, lambda: self.append('+')),
        ]

        for (text, r, c, cmd) in btn_specs:
            btn = ttk.Button(self, text=text, command=cmd)
            btn.grid(row=r, column=c, sticky='nsew', padx=6, pady=6)

        # Grid weight
        for i in range(6):
            self.rowconfigure(i, weight=1)
        for j in range(4):
            self.columnconfigure(j, weight=1)

        self._update_display()

    def _bind_keys(self):
        self.bind('<Key>', self._on_key)
        self.bind('<Return>', lambda e: self.evaluate())
        self.bind('<KP_Enter>', lambda e: self.evaluate())
        self.bind('<BackSpace>', lambda e: self.backspace())
        self.bind('<Escape>', lambda e: self.clear())

    def _on_key(self, event):
        key = event.char
        if key.isdigit() or key in '.+-*/()%':
            # Map keyboard '/' '*' to ÷ × for display consistency
            if key == '/':
                self.append('÷')
            elif key == '*':
                self.append('×')
            else:
                self.append(key)
        elif key == '\r':
            self.evaluate()

    def append(self, char: str):
        # Hindari beberapa karakter berulang yang tidak masuk akal di input
        if char in '÷×+-' and (not self.expr or self.expr[-1] in '÷×+-'):
            # jika pengguna menekan operator berturut-turut, ganti operator terakhir
            if self.expr:
                self.expr = self.expr[:-1] + char
                self._update_display()
                return
            # jangan tambahkan operator saat kosong
            return

        self.expr += char
        self._update_display()

    def clear(self):
        self.expr = ''
        self._update_display()

    def backspace(self):
        self.expr = self.expr[:-1]
        self._update_display()

    def negate(self):
        # toggle sign pada nilai saat ini (bekerja pada angka terakhir)
        if not self.expr:
            return
        # coba evaluasi bagian terakhir jika mungkin
        try:
            # cari batas angka terakhir
            i = len(self.expr) - 1
            while i >= 0 and (self.expr[i].isdigit() or self.expr[i] == '.' or self.expr[i] in 'eE'):
                i -= 1
            # bagian angka
            num = self.expr[i+1:]
            if not num:
                return
            val = float(num)
            val = -val
            # pasang kembali
            self.expr = self.expr[:i+1] + (str(int(val)) if val.is_integer() else str(val))
            self._update_display()
        except Exception:
            return

    def percent(self):
        # ubah angka terakhir menjadi persen (angka/100)
        if not self.expr:
            return
        try:
            i = len(self.expr) - 1
            while i >= 0 and (self.expr[i].isdigit() or self.expr[i] == '.' or self.expr[i] in 'eE'):
                i -= 1
            num = self.expr[i+1:]
            if not num:
                return
            val = float(num) / 100.0
            self.expr = self.expr[:i+1] + (str(int(val)) if val.is_integer() else str(val))
            self._update_display()
        except Exception:
            return

    def evaluate(self):
        if not self.expr:
            return
        try:
            # ubah simbol dan evaluasi secara aman
            py_expr = self.expr.replace('÷', '/').replace('×', '*')
            result = safe_eval(py_expr)
            # format hasil: jika integer tampilkan tanpa .0
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            self.expr = str(result)
            self._update_display()
        except Exception as e:
            self.display_var.set('Error')
            self.after(1200, self._update_display)

    def _update_display(self):
        text = self.expr if self.expr else '0'
        # batasi panjang tampilan
        if len(text) > 30:
            text = text[-30:]
        self.display_var.set(text)


if __name__ == '__main__':
    app = Calculator()
    app.mainloop()
