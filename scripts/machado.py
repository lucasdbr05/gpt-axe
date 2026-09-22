from __future__ import annotations

import argparse
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path


DATASET_URL = (
    "https://www.kaggle.com/api/v1/datasets/download/luxedo/machado-de-assis"
)
PASTA_DADOS = Path(__file__).resolve().parents[1] / "data"
ARQUIVO_FINAL = PASTA_DADOS / "machado_de_assis_obra_completa.txt"
PASTA_OBRAS = PASTA_DADOS / "obras"

CATEGORIAS = (
    ("romance", "Romance", 10),
    ("conto", "Conto", 7),
    ("poesia", "Poesia", 7),
    ("cronica", "Crônica", 24),
    ("teatro", "Teatro", 10),
    ("critica", "Crítica", 45),
    ("traducao", "Tradução", 3),
    ("miscelanea", "Miscelânea", 10),
)


def argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera um TXT por obra e um TXT consolidado do acervo."
    )
    parser.add_argument(
        "--saida", type=Path, default=ARQUIVO_FINAL,
        help=f"arquivo consolidado (padrão: {ARQUIVO_FINAL})",
    )
    parser.add_argument(
        "--obras-dir", type=Path, default=PASTA_OBRAS,
        help=f"diretório dos TXTs individuais (padrão: {PASTA_OBRAS})",
    )
    parser.add_argument(
        "--zip", dest="arquivo_zip", type=Path,
        help="usa um ZIP já baixado em vez de baixar o acervo",
    )
    return parser.parse_args()


def baixar_dataset(destino: Path) -> None:
    print(f"Baixando o acervo: {DATASET_URL}")
    requisicao = urllib.request.Request(
        DATASET_URL,
        headers={"User-Agent": "Mozilla/5.0 (Machado TXT Builder)"},
    )

    with urllib.request.urlopen(requisicao, timeout=120) as resposta:
        with destino.open("wb") as arquivo:
            shutil.copyfileobj(resposta, arquivo)


def corrigir_nome_zip(nome: str) -> str:
    """Corrige os nomes UTF-8 gravados no ZIP sem a flag de codificacao."""
    try:
        return nome.encode("cp437").decode("utf-8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        return nome


def chave_categoria(nome: str) -> str | None:
    partes = nome.split("/")
    if len(partes) != 4 or partes[0:2] != ["raw", "txt"]:
        return None
    pasta = partes[2]
    pasta_sem_acentos = str.maketrans("áâãàéêíóôõúç", "aaaaeeiooouc")
    pasta = pasta.lower().translate(pasta_sem_acentos)

    categorias_validas = {categoria[0] for categoria in CATEGORIAS}
    return pasta if pasta in categorias_validas else None


def listar_obras(
    arquivo_zip: zipfile.ZipFile,
) -> dict[str, list[tuple[str, str]]]:
    obras = {categoria[0]: [] for categoria in CATEGORIAS}

    for nome_original in arquivo_zip.namelist():
        nome = corrigir_nome_zip(nome_original)
        if not nome.startswith("raw/txt/") or not nome.endswith(".txt"):
            continue

        categoria = chave_categoria(nome)
        if categoria is not None:
            obras[categoria].append((nome, nome_original))

    for categoria, _, quantidade_esperada in CATEGORIAS:
        obras[categoria].sort(key=lambda item: Path(item[0]).name)
        quantidade = len(obras[categoria])
        if quantidade != quantidade_esperada:
            raise RuntimeError(
                f"A categoria {categoria!r} deveria conter "
                f"{quantidade_esperada} obras, mas contem {quantidade}."
            )

    return obras


def gerar_txt(arquivo_zip: Path, saida: Path, pasta_obras: Path = PASTA_OBRAS) -> int:
    if pasta_obras.resolve() in saida.resolve().parents:
        raise ValueError("O arquivo consolidado deve ficar fora do diretório das obras.")

    with zipfile.ZipFile(arquivo_zip) as pacote:
        obras = listar_obras(pacote)
        nomes = [Path(nome).name for categoria, _, _ in CATEGORIAS
                 for nome, _ in obras[categoria]]
        if len(nomes) != len(set(nomes)):
            raise ValueError("Há obras com nomes de arquivo repetidos entre categorias.")

        saida.parent.mkdir(parents=True, exist_ok=True)
        pasta_obras.mkdir(parents=True, exist_ok=True)

        with saida.open("w", encoding="utf-8", newline="\n") as consolidado:
            total = 0
            for categoria, rotulo, _ in CATEGORIAS:
                for nome, nome_original in obras[categoria]:
                    conteudo = pacote.read(nome_original).decode("utf-8-sig")
                    conteudo = conteudo.replace("\r\n", "\n").replace("\r", "\n")
                    nome_arquivo = Path(nome).name
                    titulo = next(
                        (linha.strip() for linha in conteudo.splitlines() if linha.strip()),
                        Path(nome).stem,
                    )
                    texto_obra = conteudo if conteudo.endswith("\n") else conteudo + "\n"

                    (pasta_obras / nome_arquivo).write_text(
                        texto_obra, encoding="utf-8", newline="\n"
                    )

                    if total:
                        consolidado.write("\n")
                    # consolidado.write(
                    #     "=" * 80
                    #     + f"\nINÍCIO DA OBRA\nCATEGORIA: {rotulo}\n"
                    #     + f"TÍTULO: {titulo}\n"
                    #     + f"ARQUIVO DE ORIGEM: {nome_arquivo}\n"
                    #     + "=" * 80
                    #     + "\n\n"
                    # )
                    consolidado.write(texto_obra)
                    # consolidado.write("\n" + "=" * 80 + "\nFIM DA OBRA\n" + "=" * 80 + "\n")
                    total += 1

    return total


if __name__ == "__main__":
    args = argumentos()

    if args.arquivo_zip is None:
        with tempfile.TemporaryDirectory(prefix="machado-") as pasta_temporaria:
            arquivo_zip = Path(pasta_temporaria) / "machado-de-assis.zip"
            baixar_dataset(arquivo_zip)
            total = gerar_txt(arquivo_zip, args.saida, args.obras_dir)
    else:
        total = gerar_txt(args.arquivo_zip, args.saida, args.obras_dir)

    tamanho = args.saida.stat().st_size
    print(f"Concluído: {args.saida.resolve()}")
    print(f"Obras reunidas: {total}")
    print(f"TXTs individuais: {args.obras_dir.resolve()}")
    print(f"Tamanho: {tamanho:,} bytes")
