import tkinter as tk
from controllers import AppBebidasContabil

if __name__ == "__main__":
    root = tk.Tk()
    app = AppBebidasContabil(root)
    root.protocol("WM_DELETE_WINDOW", app.fechar)
    root.mainloop()