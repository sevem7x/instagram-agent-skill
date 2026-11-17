---
name: ig-conta
description: >-
  Gerencia as várias contas de Instagram do pack - cria uma conta nova com a
  própria pasta de voz, troca a conta ativa, lista as contas e mostra onde
  ficam os arquivos de cada uma. Use quando o usuário disser "nova conta",
  "adiciona a conta @x", "troca para a conta y", "quais contas eu tenho",
  "em qual conta estou", ou quando outra skill ig-* não achar conta nenhuma.
---

# ig-conta

Cada conta de Instagram tem a própria pasta. Nada passa de uma conta para
outra: a voz, o swipe file, o log do que foi postado e o plano da semana são
separados.

```
~/.claude/instagram/
  ativa                        apelido da conta em uso
  contas/<apelido>/voice.md    a voz da conta (preencher primeiro)
  contas/<apelido>/swipe.md    escrito pelo /ig-viral
  contas/<apelido>/log.md      o que foi aprovado e postado
  contas/<apelido>/plan.md     escrito pelo /ig-plan
```

A ferramenta fica nesta pasta e roda de verdade. Use, não crie pastas na mão.

```bash
python3 conta.py listar                          # * marca a ativa
python3 conta.py nova <apelido> --handle @usuario
python3 conta.py usar <apelido>
python3 conta.py ativa
python3 conta.py caminho [apelido]               # pasta da conta
```

## Criar uma conta

1. Pergunte, numa pergunta só, o que faltar: o apelido curto (letras,
   números, `.`, `_` ou `-`, ex.: `maps`, `loja-centro`) e o @ da conta.
   Várias contas de uma vez: rode `nova` uma vez para cada.
2. Rode `python3 conta.py nova <apelido> --handle @usuario`. A primeira conta
   criada vira a ativa sozinha.
3. A voz vem em branco. Ofereça os dois caminhos: preencher o `voice.md`, ou
   o usuário manda três reels ou legendas da conta e você escreve o arquivo a
   partir deles. O segundo funciona melhor. Escreva só no `voice.md` daquela
   conta.

## Trocar de conta

`python3 conta.py usar <apelido>`. Depois diga em uma linha qual ficou ativa.
Um pedido que cita a conta ("legenda pra @loja2") vale só para aquele pedido e
não troca a ativa.

## Regras

- Nunca copie a voz, os números ou as histórias de uma conta para outra. Se
  duas contas são da mesma empresa, ainda assim cada uma tem o próprio
  `voice.md`.
- Apagar ou renomear uma conta é decisão do usuário: diga qual pasta seria
  afetada e espere ele confirmar. Esta ferramenta não apaga nada.
- Se houver um MCP de leitura do Instagram que também usa apelidos, use o
  mesmo apelido nos dois, para o `/ig-audit` e o `/ig-viral` acharem os dados
  da conta certa.
