#!/usr/bin/env python3
"""
conta.py - gerencia as contas de Instagram do pack. Só biblioteca padrão.

Cada conta tem a própria pasta, com a própria voz, swipe file, log e plano:

  ~/.claude/instagram/
    ativa                      apelido da conta em uso
    contas/<apelido>/voice.md  voz da conta (preencher)
    contas/<apelido>/swipe.md  escrito pelo /ig-viral
    contas/<apelido>/log.md    o que foi aprovado e postado
    contas/<apelido>/plan.md   escrito pelo /ig-plan

Uso:
  python3 conta.py listar
  python3 conta.py nova <apelido> [--handle @usuario]
  python3 conta.py usar <apelido>
  python3 conta.py ativa
  python3 conta.py caminho [apelido]

IG_HOME troca a pasta base (usado nos testes).
"""
import argparse
import os
import re
import sys
from pathlib import Path

APELIDO_VALIDO = re.compile(r"^[a-z0-9][a-z0-9._-]{0,39}$")
LINHA_HANDLE = "- **Handle:**"
VOICE_MINIMO = "# voice.md\n\n## Who I am\n\n- **Name:**\n- **Handle:**\n"


class ErroConta(Exception):
    pass


def base():
    return Path(os.environ.get("IG_HOME") or Path.home() / ".claude" / "instagram")


def pasta_contas():
    return base() / "contas"


def arquivo_ativa():
    return base() / "ativa"


def normalizar(apelido):
    limpo = apelido.strip().lstrip("@").lower()
    if not APELIDO_VALIDO.match(limpo):
        raise ErroConta(f"apelido inválido: {apelido!r} (use letras, números, ponto, _ ou -)")
    return limpo


def contas_existentes():
    if not pasta_contas().is_dir():
        return []
    return sorted(p.name for p in pasta_contas().iterdir() if p.is_dir())


def ler_ativa():
    try:
        apelido = arquivo_ativa().read_text().strip()
    except FileNotFoundError:
        return None
    return apelido if apelido in contas_existentes() else None


def ler_handle(apelido):
    voice = pasta_contas() / apelido / "voice.md"
    if not voice.exists():
        return ""
    for linha in voice.read_text().splitlines():
        if linha.startswith(LINHA_HANDLE):
            return linha[len(LINHA_HANDLE):].strip()
    return ""


def modelo_voice():
    aqui = Path(__file__).resolve().parent
    for candidato in (aqui.parent.parent / "templates" / "voice.md", aqui / "voice.md"):
        if candidato.exists():
            return candidato.read_text()
    return VOICE_MINIMO


def com_handle(texto, handle):
    if not handle:
        return texto
    arroba = "@" + handle.strip().lstrip("@")
    return texto.replace(LINHA_HANDLE + "\n", f"{LINHA_HANDLE} {arroba}\n", 1)


def cmd_nova(apelido, handle):
    nome = normalizar(apelido)
    pasta = pasta_contas() / nome
    if pasta.exists():
        raise ErroConta(f"a conta {nome} já existe em {pasta}")
    pasta.mkdir(parents=True)
    (pasta / "voice.md").write_text(com_handle(modelo_voice(), handle))
    if ler_ativa() is None:
        arquivo_ativa().write_text(nome + "\n")
    print(f"conta criada: {nome}")
    print(f"preencha a voz em: {pasta / 'voice.md'}")
    return 0


def cmd_usar(apelido):
    nome = normalizar(apelido)
    if nome not in contas_existentes():
        raise ErroConta(f"a conta {nome} não existe. Crie com: conta.py nova {nome}")
    arquivo_ativa().write_text(nome + "\n")
    print(f"conta ativa: {nome}")
    return 0


def cmd_ativa():
    atual = ler_ativa()
    if atual is None:
        raise ErroConta("nenhuma conta ativa. Crie com: conta.py nova <apelido>")
    print(atual)
    return 0


def cmd_caminho(apelido):
    nome = normalizar(apelido) if apelido else ler_ativa()
    if nome is None:
        raise ErroConta("nenhuma conta ativa e nenhuma conta informada")
    if nome not in contas_existentes():
        raise ErroConta(f"a conta {nome} não existe")
    print(pasta_contas() / nome)
    return 0


def cmd_listar():
    contas = contas_existentes()
    if not contas:
        print("nenhuma conta ainda. Crie com: conta.py nova <apelido> --handle @usuario")
        return 0
    atual = ler_ativa()
    for nome in contas:
        marca = "*" if nome == atual else " "
        print(f"{marca} {nome}  {ler_handle(nome)}".rstrip())
    return 0


def parser():
    ap = argparse.ArgumentParser(description="Contas de Instagram do pack")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    nova = sub.add_parser("nova")
    nova.add_argument("apelido")
    nova.add_argument("--handle", default="")
    usar = sub.add_parser("usar")
    usar.add_argument("apelido")
    sub.add_parser("ativa")
    caminho = sub.add_parser("caminho")
    caminho.add_argument("apelido", nargs="?")
    return ap


def main(argv=None):
    args = parser().parse_args(argv)
    acoes = {
        "listar": lambda: cmd_listar(),
        "nova": lambda: cmd_nova(args.apelido, args.handle),
        "usar": lambda: cmd_usar(args.apelido),
        "ativa": lambda: cmd_ativa(),
        "caminho": lambda: cmd_caminho(args.apelido),
    }
    try:
        return acoes[args.cmd]()
    except ErroConta as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
