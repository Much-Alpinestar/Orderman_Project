try:
    from reportlab.lib.pagesizes import A4
    print("Reportlab import successful.")
except ModuleNotFoundError as e:
    print(e)
