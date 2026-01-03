Ce projet contient un script Python pour convertir des images en **bitmaps monochromes** prêts à être utilisés avec la fonction `u8g2.drawXBMP()` sur Arduino.

Le script est compatible avec **toutes les tailles** de bitmap, qu'elles soient multiples de 8 ou non, et gère l’inversion noir/blanc.

---

## Fonctionnalités

- Conversion d’images PNG, JPG, BMP en **bitmap C/PROGMEM**.
- Supporte des tailles prédéfinies : 8x8, 16x16, 32x32, 64x64, 128x128.
- Taille personnalisée possible, largeur et hauteur arbitraires.
- Option pour inverser le noir et le blanc.
- Génère un fichier `.c` prêt à copier dans Arduino IDE pour `u8g2.drawXBMP(x, y, width, height, bitmap)`.

---

## Prérequis

- Python 3.x
- Bibliothèque [Pillow](https://pillow.readthedocs.io/) :
  ```bash
  pip install pillow
