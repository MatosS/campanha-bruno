# Publicação no GitHub Pages

O jogador autorizou publicar o atlas como site público em 30/10/2026. O repositório de destino é `MatosS/campanha-bruno`, com a branch `main`.

A rotina `.github/workflows/pages.yml` instala as dependências fixadas pelo lockfile, confere os tipos, gera o site a partir de `conteudo/`, verifica os links e publica apenas `site/public/` no Pages. Novos envios à `main` atualizam o site automaticamente. A configuração pública usa `matoss.github.io/campanha-bruno` como endereço base.

O código do Quartz foi incorporado ao projeto com sua licença MIT. Os metadados Git do download inicial foram preservados localmente em `.quartz-upstream.git/`, fora da publicação. As rotinas de publicação do projeto original do Quartz não são executadas por este repositório.

`.gitattributes` desativa conversão automática de finais de linha para preservar os bytes das fontes e dos originais arquivados ao transportar o acervo entre Windows e Linux.

O servidor local continua disponível em `http://127.0.0.1:8080/`. Para publicar alterações locais da base, envie um novo commit para `main`; a rotina de publicação faz o restante.
