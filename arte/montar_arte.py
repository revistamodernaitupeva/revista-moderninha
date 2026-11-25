#!/usr/bin/env python3
"""Monta a arte da Revista Moderninha (1080x1350).

Uso:
  python3 -I arte/montar_arte.py FOTO SAIDA.jpg "Título" "Texto de apoio" [opções]

Título: use "|" para forçar quebras (3 a 5 linhas); sem "|", quebra automática.
Opções:
  crop=x0,y0,x1,y1   recorte da foto original antes de encaixar
  foco=0.5           posição vertical do enquadramento (0 = topo, 1 = base)
  focox=0.5          posição horizontal do enquadramento
  titulo=36          tamanho da fonte do título (padrão: ajusta sozinho)
  apoio=25           tamanho da fonte do texto de apoio (padrão: ajusta sozinho)
"""
import sys
from pathlib import Path

from PIL import Image, ImageFont, ImageDraw

AQUI = Path(__file__).resolve().parent
MOLDURA = AQUI / "moldura.png"            # fundo + enfeites + logo, com o buraco da foto
FONTE_TITULO = AQUI / "MoreSugar-Regular.ttf"
FONTE_APOIO = AQUI / "OpenSans.ttf"

FOTO_CAIXA = (103, 189, 727, 1141)        # área transparente da moldura
COLUNA_X0, COLUNA_X1 = 745, 1065          # coluna roxa da direita
CENTRO_X = (COLUNA_X0 + COLUNA_X1) // 2
TOPO_TEXTO = 548                           # logo abaixo da seta neon
LIMITE_BASE = 1205                         # acima da faixa branca de baixo
BRANCO = (255, 255, 255)


def opcoes(args):
    o = {}
    for a in args:
        k, _, v = a.partition("=")
        o[k] = v
    return o


def encaixar(foto, caixa, foco=0.5, focox=0.5):
    x0, y0, x1, y1 = caixa
    w, h = x1 - x0, y1 - y0
    escala = max(w / foto.width, h / foto.height)
    nova = foto.resize((round(foto.width * escala), round(foto.height * escala)),
                       Image.LANCZOS)
    sobra_x, sobra_y = nova.width - w, nova.height - h
    left = round(sobra_x * focox)
    top = round(sobra_y * foco)
    return nova.crop((left, top, left + w, top + h))


def quebrar(texto, fonte, largura, draw):
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = (atual + " " + palavra).strip()
        if draw.textlength(teste, font=fonte) <= largura or not atual:
            atual = teste
        else:
            linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def fonte_apoio(tamanho):
    f = ImageFont.truetype(str(FONTE_APOIO), tamanho)
    try:
        f.set_variation_by_axes([100, 400])   # largura normal, peso Regular
    except Exception:
        pass
    return f


def bloco_titulo(titulo, draw, tamanho=None):
    largura = COLUNA_X1 - COLUNA_X0
    for t in ([tamanho] if tamanho else range(38, 25, -1)):
        f = ImageFont.truetype(str(FONTE_TITULO), t)
        if "|" in titulo:
            linhas = [l.strip() for l in titulo.split("|") if l.strip()]
        else:
            linhas = quebrar(titulo, f, largura, draw)
        if tamanho or (len(linhas) <= 5 and
                       all(draw.textlength(l, font=f) <= largura for l in linhas)):
            return f, linhas, round(t * 1.33)
    return f, linhas, round(t * 1.33)


def bloco_apoio(texto, draw, espaco, tamanho=None):
    largura = COLUNA_X1 - COLUNA_X0 + 5
    for t in ([tamanho] if tamanho else range(25, 17, -1)):
        f = fonte_apoio(t)
        linhas = quebrar(texto, f, largura, draw)
        alt = round(t * 1.48)
        if tamanho or len(linhas) * alt <= espaco:
            return f, linhas, alt
    return f, linhas, alt


TIL = {"ã": "a", "õ": "o", "ñ": "n", "Ã": "A", "Õ": "O", "Ñ": "N"}


def escrever(draw, linhas, fonte, y, altura, til_manual=False):
    """Escreve linhas centralizadas, alinhadas pela linha de base (espaçamento
    igual mesmo com acentos). Com til_manual, desenha o til à parte
    (a More Sugar tem ã/õ sem o til no desenho)."""
    import math
    s = fonte.size
    asc = round(s * 0.78)                      # topo da linha -> linha de base
    for l in linhas:
        yb_linha = y + asc
        if not til_manual or not any(c in TIL for c in l):
            draw.text((CENTRO_X, yb_linha), l, font=fonte, fill=BRANCO, anchor="ms")
            y += altura
            continue
        base = "".join(TIL.get(c, c) for c in l)
        x0 = round(CENTRO_X - draw.textlength(base, font=fonte) / 2)
        draw.text((x0, yb_linha), base, font=fonte, fill=BRANCO, anchor="ls")
        mascara = Image.new("L", (round(draw.textlength(base, font=fonte)) + s, s * 3), 0)
        ImageDraw.Draw(mascara).text((0, s * 2), base, font=fonte, fill=255, anchor="ls")
        for i, c in enumerate(l):
            if c not in TIL:
                continue
            ia = round(draw.textlength(base[:i], font=fonte))
            ib = round(draw.textlength(base[:i + 1], font=fonte))
            bx0, by0, bx1, _ = mascara.crop((ia, 0, ib, s * 3)).getbbox()
            cx = x0 + ia + (bx0 + bx1) / 2
            w, h = s * 0.42, s * 0.11
            yb = yb_linha + (by0 - s * 2) - s * 0.10   # base do til, acima da letra
            pts = [(cx - w / 2 + w * k / 24,
                    yb - h / 2 - (h / 2) * math.sin(k / 24 * 2 * math.pi))
                   for k in range(25)]
            draw.line(pts, fill=BRANCO, width=max(3, round(s * 0.09)), joint="curve")
        y += altura
    return y


def main():
    if len(sys.argv) < 5:
        print(__doc__)
        return 1
    foto_p, saida, titulo, apoio = sys.argv[1:5]
    o = opcoes(sys.argv[5:])

    foto = Image.open(foto_p).convert("RGB")
    if "crop" in o:
        foto = foto.crop(tuple(int(v) for v in o["crop"].split(",")))
    moldura = Image.open(MOLDURA).convert("RGBA")

    arte = Image.new("RGBA", moldura.size, (255, 255, 255, 255))
    arte.paste(encaixar(foto, FOTO_CAIXA, float(o.get("foco", 0.5)),
                        float(o.get("focox", 0.5))), FOTO_CAIXA[:2])
    arte.alpha_composite(moldura)

    d = ImageDraw.Draw(arte)
    ft, lt, at = bloco_titulo(titulo, d, int(o["titulo"]) if "titulo" in o else None)
    y = escrever(d, lt, ft, TOPO_TEXTO, at, til_manual=True)
    y += 38
    fa, la, aa = bloco_apoio(apoio, d, LIMITE_BASE - y,
                             int(o["apoio"]) if "apoio" in o else None)
    fim = escrever(d, la, fa, y, aa)
    if fim > LIMITE_BASE + 5:
        print(f"AVISO: o texto de apoio passou do limite ({fim}px). Encurte o texto.")

    arte.convert("RGB").save(saida, "JPEG", quality=92, optimize=True)
    print(f"Arte salva em {saida} | título {len(lt)} linhas, apoio {len(la)} linhas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
