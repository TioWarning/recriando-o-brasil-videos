# Postagem automática pela API do YouTube (sem Zapier)

O vídeo é enviado pelo GitHub Actions direto deste repositório para o YouTube, pela API oficial.
Não usa crédito: a cota padrão do Google é de 100 uploads por dia por projeto.
Você faz os passos abaixo **uma vez só** (uns 15 minutos). Nenhuma senha fica no repositório: ela vai em "Secrets", que só o GitHub vê.

## 1. Criar o projeto no Google Cloud
1. Abra https://console.cloud.google.com/ com a conta Google **dona do canal** Recriando o Brasil.
2. No topo, clique no seletor de projeto → **Novo projeto** → nome `recriando-o-brasil` → **Criar**. Deixe esse projeto selecionado.
3. Menu ☰ → **APIs e serviços** → **Biblioteca** → procure **YouTube Data API v3** → **Ativar**.

## 2. Tela de consentimento (OAuth)
1. ☰ → **APIs e serviços** → **Tela de consentimento OAuth** (ou "Google Auth Platform" → **Branding**).
2. Tipo de usuário: **Externo** → preencha nome do app (`Recriando o Brasil uploader`), seu e-mail de suporte e de contato → salve.
3. Em **Público-alvo** (Audience), clique em **Publicar app** / **Em produção** e confirme.
   Importante: se ficar em "Teste", a autorização expira a cada 7 dias e a postagem para de funcionar.
   Não precisa mandar para verificação do Google: o app é só seu.

## 3. Criar a credencial
1. ☰ → **APIs e serviços** → **Credenciais** → **+ Criar credenciais** → **ID do cliente OAuth**.
2. Tipo de aplicativo: **Aplicativo da Web**. Nome: `uploader`.
3. Em **URIs de redirecionamento autorizados**, adicione exatamente:
   `https://developers.google.com/oauthplayground`
4. **Criar**. Copie o **ID do cliente** e a **Chave secreta do cliente** (guarde num lugar seguro).

## 4. Gerar o token de acesso (refresh token)
1. Abra https://developers.google.com/oauthplayground
2. Clique na engrenagem ⚙️ (canto superior direito) → marque **Use your own OAuth credentials** → cole o ID do cliente e a chave secreta → feche.
3. Na caixa da esquerda, no campo "Input your own scopes", cole (com o espaço no meio):
   `https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube`
   e clique **Authorize APIs**.
4. Entre com a conta do canal. Se aparecer "O Google não verificou este app", clique **Avançado** → **Acessar Recriando o Brasil uploader (não seguro)** — é o seu próprio app. Se pedir para escolher um canal, escolha **Recriando o Brasil**. Permita tudo.
5. De volta ao Playground, clique **Exchange authorization code for tokens**. Copie o **Refresh token** (começa com `1//`).

## 5. Colar os 3 valores no GitHub
1. Abra https://github.com/TioWarning/recriando-o-brasil-videos/settings/secrets/actions
2. **New repository secret**, três vezes:
   - `YT_CLIENT_ID` = ID do cliente
   - `YT_CLIENT_SECRET` = chave secreta do cliente
   - `YT_REFRESH_TOKEN` = refresh token
3. Em https://github.com/TioWarning/recriando-o-brasil-videos/settings/actions confira que **Actions** está permitido e que, em "Workflow permissions", está **Read and write permissions**.

Pronto. Me avise ("configurei a API") que eu confiro e passo a usar esse caminho nas rodadas.

## Como funciona depois
- A rodada gera o vídeo, coloca `epNN.mp4` aqui e um arquivo `queue/epNN.json` com título, descrição, tags e horário (`publish_at`).
- O GitHub Actions espera dar 11:30 / 19:30, sobe o vídeo **público**, marca **conteúdo sintético (IA)**, idioma pt-BR, não é para crianças, categoria Educação, e grava o link em `published/epNN.json`.
- Se der erro temporário (429/5xx), ele tenta de novo sozinho, com intervalos crescentes.
- Para republicar à mão: aba **Actions** → **Publicar no YouTube** → **Run workflow** → `queue/epNN.json`.
