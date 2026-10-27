# Galería Celi & Fede

Prueba de galería de boda que muestra las fotos de un álbum compartido de Google Photos **sin descargarlas**: cada imagen se carga directo desde `lh3.googleusercontent.com`.

## Cómo funciona

1. `scripts/scrape.py` lee el álbum público (link en `sections.json`), sigue la paginación y escribe `album.js` con la URL, medidas y hora de cada foto.
2. `index.html` arma la página y pide cada foto a Google con un sufijo de tamaño:
   - `=w480` para la grilla
   - `=w1400` para portadas
   - `=w2048` para la vista ampliada

## Secciones

Las secciones son fijas y están en `sections.json`: cada una tiene un rango de índices (`from` / `to`, en el orden por hora del álbum) y tres fotos de portada.

## Actualizar

```bash
python scripts/scrape.py
```

## Limitaciones

- No usa una API oficial: si Google cambia el formato de la página, hay que ajustar el script.
- Si el álbum deja de estar compartido o Google cambia las URLs, las fotos dejan de verse.
