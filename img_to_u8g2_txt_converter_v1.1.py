from PIL import Image 
import tkinter as tk
from tkinter import filedialog, messagebox
import os

THRESHOLD = 128
PRESET_SIZES = [8, 16, 32, 64, 128]

def convert():
    mode = size_mode.get()
    invert_gui = invert_var.get()
    invert_default = True  # inversion noir/blanc par défaut

    # --- Détermination de la taille ---
    if mode == "preset":
        width = height = preset_size.get()
    else:
        try:
            width = int(width_entry.get())
            height = int(height_entry.get())
        except ValueError:
            messagebox.showerror("Erreur", "Largeur et hauteur doivent être des entiers")
            return

    if width <= 0 or height <= 0:
        messagebox.showerror("Erreur", "Dimensions invalides")
        return

    if width % 8 != 0:
        messagebox.showerror(
            "Erreur",
            "La largeur doit être un multiple de 8\n(format 8 pixels par octet)"
        )
        return

    # --- Choix fichiers ---
    input_path = filedialog.askopenfilename(
        title="Choisir une image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")]
    )
    if not input_path:
        return

    output_path = filedialog.asksaveasfilename(
        title="Enregistrer le fichier C/PROGMEM",
        defaultextension=".c",
        filetypes=[("Fichier C", "*.c")]
    )
    if not output_path:
        return
    
    name = os.path.splitext(os.path.basename(output_path))[0]

    try:
        # --- Conversion N&B et redimensionnement ---
        img = Image.open(input_path).convert("L")
        img = img.resize((width, height), Image.NEAREST)
        pixels = img.load()

        bytes_out = []
        octets_par_ligne = (width + 7) // 8  # largeur arrondie à l’octet
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
                        byte |= (1 << bit)   # LSB = pixel gauche

                bytes_out.append(byte)


        # --- Écriture du fichier C ---
        with open(output_path, "w") as f:
            f.write(f"// {width}x{height} bitmap for U8g2 drawXBMP\n")
            f.write(f"const uint8_t {name}[] PROGMEM = {{\n")

            for i, b in enumerate(bytes_out):
                f.write(f"0x{b:02X}, ")
                if (i + 1) % octets_par_ligne == 0:
                    f.write("\n")

            f.write("};\n")

        messagebox.showinfo(
            "Conversion terminée",
            f"Bitmap {width}x{height}\n"
            f"{len(bytes_out)} octets générés\n\n"
            f"Usage Arduino:\n"
            f"u8g2.drawXBMP(x, y, {width}, {height}, {name});"
        )


    except Exception as e:
        messagebox.showerror("Erreur", str(e))


# ================= UI =================
root = tk.Tk()
root.title("Bitmap C/PROGMEM – U8g2")
root.geometry("420x450")

size_mode = tk.StringVar(value="preset")
preset_size = tk.IntVar(value=32)
invert_var = tk.BooleanVar(value=False)

tk.Label(root, text="Taille du bitmap", font=("Arial", 10, "bold")).pack(pady=8)

# Preset sizes
tk.Radiobutton(root, text="Tailles prédéfinies", variable=size_mode, value="preset").pack(anchor="w", padx=20)
preset_frame = tk.Frame(root)
preset_frame.pack(anchor="w", padx=40)
for s in PRESET_SIZES:
    tk.Radiobutton(preset_frame, text=f"{s} x {s}", variable=preset_size, value=s).pack(anchor="w")

# Custom size
tk.Radiobutton(root, text="Taille personnalisée", variable=size_mode, value="custom").pack(anchor="w", padx=20, pady=(10, 0))
custom_frame = tk.Frame(root)
custom_frame.pack(anchor="w", padx=40)
tk.Label(custom_frame, text="Largeur").grid(row=0, column=0, padx=5, pady=5)
width_entry = tk.Entry(custom_frame, width=6)
width_entry.insert(0, "32")
width_entry.grid(row=0, column=1)
tk.Label(custom_frame, text="Hauteur").grid(row=1, column=0, padx=5, pady=5)
height_entry = tk.Entry(custom_frame, width=6)
height_entry.insert(0, "32")
height_entry.grid(row=1, column=1)
tk.Label(custom_frame, text="(largeur multiple de 8)", font=("Arial", 8)).grid(row=2, column=0, columnspan=2, pady=2)

# Inversion option
tk.Checkbutton(root, text="Inverser noir/blanc", variable=invert_var).pack(anchor="w", padx=40, pady=5)

# Convert button
tk.Button(root, text="Convertir une image", command=convert, height=2).pack(pady=20, fill="x", padx=20)

root.mainloop()
