# Publicador Revista Moderninha (@revistamoderninha + Página "Revista Moderninha")

Repositório SÓ da Revista Moderninha (portal teen). Não misturar com o `publicador-revista-moderna` (Itupeva / Alto Uruguai).

## Como funciona
- Posts ficam em `fila/` como par de arquivos: `NOME.json` + `NOME.jpg`.
- O robô (`publicar.py`, workflow "Publicar") publica no Instagram e no Facebook pela API oficial da Meta.
- Janela: publica de `horario - 10 min` até `horario + 3 h`. Fora disso vai para `atrasados/`. Depois de publicar vai para `publicados/` com os links em `resultado`.
- Pausa de emergência: criar um arquivo `PAUSA` na raiz.
- Token da Meta: Secret `META_TOKEN` (GitHub → Settings → Secrets → Actions). Nunca em código ou no chat.
- IDs da conta: `config.json` → `instagram_id` e `pagina_id` (pegar rodando o workflow "Teste de conexao Meta").
- **O repositório precisa ser público**: a Meta baixa a imagem pelo link raw.githubusercontent.com.

## Nome dos arquivos
`AAAA-MM-DD-HHMM-assunto-curto.json` e `.jpg` (mesmo nome).

## Formato do JSON
```json
{
  "tipo": "feed",
  "imagens": ["2026-11-25-1830-estetica-blockette.jpg"],
  "titulo": "Futebol no Look: A Estética Blockette Invadiu o Feed!",
  "legenda": "Siga: @revistamoderninha\n\nTítulo\n\nCorpo...\n\n#a #b #c #d #RevistaModerninha\n\nFonte: VEÍCULO | Texto de Revista Moderninha",
  "fonte": "Jornal Joca",
  "origem": "https://www.instagram.com/p/XXXXXXXX/",
  "foto_credito": "",
  "horario": "2026-11-25T18:30:00-03:00",
  "status": "aprovado"
}
```
- `origem` = link do post de onde veio a matéria. Usado para NUNCA repetir matéria (procurar o link em `publicados/`, `fila/`, `rascunhos/` e `atrasados/` antes de sugerir).
- `tipo`: `feed` (1 imagem) ou `carrossel` (2 a 10). Só JPEG, até 8 MB. Legenda até 2200 caracteres.
- Sem `plataformas`, publica no Instagram e no Facebook. Para só um: `"plataformas": ["instagram"]`.
- Rascunhos ficam em `rascunhos/` (sem `horario`). Só vão para `fila/` depois que o dono aprova vendo arte e legenda.

## Arte
```
python3 -I arte/montar_arte.py FOTO SAIDA.jpg "Título" "Texto de apoio" [crop=x0,y0,x1,y1] [foco=0.5] [focox=0.5]
```
- Saída 1080x1350. A foto entra no buraco da `arte/moldura.png` (624x952, em x 103–727, y 189–1141); a moldura (fundo roxo, enfeites neon e logo) vai por cima.
- Título: fonte More Sugar, branca, centralizada na coluna da direita, 3 a 5 linhas (use "|" para forçar quebra).
- Texto de apoio: Open Sans, branca, menor, embaixo do título (1 frase de ~15 a 25 palavras).
- `foco` / `focox` ajustam o enquadramento (0 = topo/esquerda, 1 = base/direita).

## Legenda
```
Siga: @revistamoderninha

Título

Corpo (2 a 4 parágrafos curtos; eventos com 📅 ⏰ 📍)

#tag1 #tag2 #tag3 #tag4 #RevistaModerninha

Fonte: VEÍCULO | Imagem: ORIGEM | Texto de Revista Moderninha
```
- Exatamente 5 hashtags, a última é `#RevistaModerninha`.
- Omitir "Imagem:" quando a foto é do próprio veículo ou de origem desconhecida. Sem "@" e sem "Foto:". Licença CC exige "Imagem:" com autor e licença.

## Regras
- Conteúdo infanto/juvenil. Reescrever com palavras próprias e fiel aos fatos.
- Pular temas sensíveis (criança vítima ou suspeita, corpos, violência sexual ou doméstica, suicídio, acusação sem confirmação a pessoa privada, facção).
- Foto com criança identificável é permitida.
- Aprovação do dono antes de cada post entrar na fila.
