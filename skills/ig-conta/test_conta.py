"""Testes do conta.py. Rodar: python3 -m unittest skills/ig-conta/test_conta.py"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conta  # noqa: E402


def rodar(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = conta.main(list(args))
    return code, out.getvalue().strip(), err.getvalue().strip()


class ContaTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        os.environ["IG_HOME"] = self.tmp.name
        self.base = Path(self.tmp.name)

    def tearDown(self):
        os.environ.pop("IG_HOME", None)
        self.tmp.cleanup()

    def test_nova_cria_pasta_com_voice_e_handle_preenchido(self):
        code, out, _ = rodar("nova", "MapsRent", "--handle", "maps.rentacar")
        self.assertEqual(code, 0)
        voice = self.base / "contas" / "mapsrent" / "voice.md"
        self.assertTrue(voice.exists())
        self.assertIn("**Handle:** @maps.rentacar", voice.read_text())

    def test_primeira_conta_vira_ativa(self):
        rodar("nova", "loja1")
        rodar("nova", "loja2")
        self.assertEqual(rodar("ativa")[1], "loja1")

    def test_nova_recusa_conta_que_ja_existe(self):
        rodar("nova", "loja1")
        code, _, err = rodar("nova", "@loja1")
        self.assertEqual(code, 1)
        self.assertIn("já existe", err)

    def test_apelido_invalido_e_recusado(self):
        code, _, err = rodar("nova", "../fora")
        self.assertEqual(code, 1)
        self.assertIn("apelido inválido", err)
        self.assertFalse((self.base / "fora").exists())

    def test_usar_troca_a_ativa(self):
        rodar("nova", "loja1")
        rodar("nova", "loja2")
        self.assertEqual(rodar("usar", "loja2")[0], 0)
        self.assertEqual(rodar("ativa")[1], "loja2")

    def test_usar_conta_inexistente_falha(self):
        code, _, err = rodar("usar", "nada")
        self.assertEqual(code, 1)
        self.assertIn("não existe", err)

    def test_caminho_usa_a_ativa_ou_a_informada(self):
        rodar("nova", "loja1")
        rodar("nova", "loja2")
        self.assertEqual(rodar("caminho")[1], str(self.base / "contas" / "loja1"))
        self.assertEqual(rodar("caminho", "@loja2")[1], str(self.base / "contas" / "loja2"))

    def test_caminho_sem_conta_nenhuma_falha(self):
        code, _, err = rodar("caminho")
        self.assertEqual(code, 1)
        self.assertIn("nenhuma conta", err)

    def test_listar_marca_a_ativa(self):
        rodar("nova", "loja1", "--handle", "@loja.um")
        rodar("nova", "loja2")
        out = rodar("listar")[1]
        self.assertIn("* loja1", out)
        self.assertIn("@loja.um", out)
        self.assertIn("  loja2", out)


if __name__ == "__main__":
    unittest.main()
