from pathlib import Path; 
texto = Path("data/machado_de_assis_obra_completa.txt").read_text(encoding="utf-8")
print("".join(c for c in sorted(set(texto))))
