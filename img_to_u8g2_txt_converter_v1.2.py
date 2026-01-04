from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox
import os

THRESHOLD = 128

def reverse_bits(byte):
    b = 0
    for i in range(8):
        if byte & (1 << i):
            b |= (1 << (7 - i))
    return b


def convert():
    invert_gui = invert_var.get()
    invert_default = True
    mode_adafruit = adafruit_var.get()

    # --- Choix fichiers (sélection multiple) ---
    input_paths = filedialog.askopenfilenames(
        title="Choisir une ou plusieurs images",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not input_paths:
        return

    try:
        for input_path in input_paths:

            # Nom du fichier de sortie
            name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(os.path.dirname(input_path), name + ".c")

            # --- Charger l'image ---
            img = Image.open(input_path).convert("L")
            width, height = img.size

            # --- Mode U8g2 : largeur multiple de 8 obligatoire ---
            if not mode_adafruit:
                if width % 8 != 0:
                    new_width = (width + 7) // 8 * 8
                    padded = Image.new("L", (new_width, height), color=0)  # padding noir
                    padded.paste(img, (0, 0))
                    img = padded
                    width = new_width

            pixels = img.load()

            # --- Conversion en octets ---
            bytes_out = []
            octets_par_ligne = (width + 7) // 8

            for y in range(height):
                for x_block in range(0, width, 8):
                    byte = 0
                    for bit in range(8):
                        x = x_block + bit
                        if x >= width:
                            continue

                        pixel = pixels[x, y]
                        is_black = pixel < THRESHOLD

                        if invert_default:
                            is_black = not is_black
                        if invert_gui:
                            is_black = not is_black

                        if is_black:
                            byte |= (1 << bit)

                    bytes_out.append(byte)

            # --- Inversion bits ---
            if invert_bits_var.get():
                bytes_out = [reverse_bits(b) for b in bytes_out]

            # --- Inversion octets par ligne ---
            if invert_bytes_var.get():
                bytes_out_inverted = []
                for y in range(height):
                    start = y * octets_par_ligne
                    end = start + octets_par_ligne
                    ligne = bytes_out[start:end]
                    bytes_out_inverted.extend(reversed(ligne))
                bytes_out = bytes_out_inverted

            # --- Écriture du fichier C ---
            with open(output_path, "w") as f:
                f.write(f"// {width}x{height} bitmap\n")
                f.write(f"const uint8_t {name}[] PROGMEM = {{\n")

                for i, b in enumerate(bytes_out):
                    f.write(f"0x{b:02X}, ")
                    if (i + 1) % octets_par_ligne == 0:
                        f.write("\n")

                f.write("};\n")

        messagebox.showinfo("Conversion terminée", "Toutes les images ont été converties.")

    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# ================= UI =================
root = tk.Tk()
root.title("Bitmap C/PROGMEM – U8g2 / Adafruit")
root.geometry("350x300")

invert_bytes_var = tk.BooleanVar(value=False)
invert_bits_var = tk.BooleanVar(value=False)
invert_var = tk.BooleanVar(value=False)
adafruit_var = tk.BooleanVar(value=False)

tk.Label(root, text="Options de conversion", font=("Arial", 10, "bold")).pack(pady=8)

tk.Checkbutton(root, text="Inverser noir/blanc", variable=invert_var).pack(anchor="w", padx=40, pady=5)
tk.Checkbutton(root, text="Inverser les octets (o3 o2 o1 o0)", variable=invert_bytes_var).pack(anchor="w", padx=40, pady=5)
tk.Checkbutton(root, text="Inverser les bits dans chaque octet", variable=invert_bits_var).pack(anchor="w", padx=40, pady=5)

tk.Label(root, text="Mode de sortie", font=("Arial", 10, "bold")).pack(pady=8)
tk.Checkbutton(root, text="Mode Adafruit (pas besoin multiple de 8)", variable=adafruit_var).pack(anchor="w", padx=40, pady=5)

tk.Button(root, text="Convertir image(s)", command=convert, height=2).pack(pady=20, fill="x", padx=20)

root.mainloop()
