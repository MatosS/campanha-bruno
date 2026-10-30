# Formato da base da campanha

Esta primeira migração foi autorizada pelo jogador em 2026-10-29: copiar o material de Fash/Glim sem alterar o vault-42 e converter toda a BASE INICIAL sem perder informação relevante. A publicação e a exclusão das fontes ficam para etapas posteriores.

## Organização

- `conteudo/Inicio.md`: entrada da base.
- `conteudo/Campanhas/`: campanhas de Fash e Glim e continuidade entre elas.
- `conteudo/Sessoes/`: uma nota por sessão de Glim, preservando integralmente a voz do diário.
- `conteudo/Personagens/`, `Lugares/`, `Faccoes/`, `Itens/`, `Eventos/`: notas de navegação e informação documentada, com fontes. Uma menção ainda não pesquisada permanece uma menção, nunca uma biografia inventada.
- `conteudo/Cronologia/`: cronologia com datas de mesa e tempo ficcional separados.
- `conteudo/Fontes/Documentos/`, `Vault/`, `Transcricoes/`, `Planilhas/`: documentos integrais e dados extraídos; as fontes não são descartadas após a síntese.
- `conteudo/Anexos/`: imagens e representações visuais necessárias para preservar os documentos.
- `arquivo/originais/BASE INICIAL/` e `arquivo/originais/vault-42/`: cópias exatas e verificadas, fora da pasta de publicação.
- `docs/migracao/`: manifestos, métricas e pendências de conversão, fora do conteúdo da wiki.

## Notas e links

Markdown UTF-8, com frontmatter YAML e links Obsidian. Preferir links explícitos desde a raiz de `conteudo`, como `[[Personagens/Glim Sombrasselva|Glim]]`, para eliminar ambiguidades. Imagens e downloads usam links Markdown relativos.

Metadados mínimos: `tipo`, `titulo`, `campanhas` (lista de `fash`, `glim` ou ambas), `publico: true`, `status`, `origens` (lista) e `aliases` (lista). As datas de jogo só são preenchidas quando sustentadas pela fonte. `importado` significa transferência de formato, não validação factual.

Nas notas de sessão, usar `sessao` e `data_mesa` quando documentada. A solo de 22/04 é uma entrada própria e não renumera as outras sessões. A separação de 70 anos descreve as duas épocas; não cria calendário absoluto para todos os eventos.

## Preservação

Preservar conteúdo integral, ordem de leitura, tabelas, notas, fórmulas, valores disponíveis, imagens e lacunas. Não corrigir silenciosamente diários nem reconciliar versões por mera preferência editorial. Correções confirmadas ficam em notas separadas com referência.

PDFs com conteúdo visual mantêm imagens legíveis das páginas, além do texto extraído ou transcrito. As planilhas mantêm todas as abas com conteúdo, inclusive ocultas, e apresentam fórmulas e valores em cache separadamente. O arquivo binário original acompanha a conversão quando o Markdown não representa todos os recursos do formato.

Cada origem deve ter destino e hash registrados. Duplicatas podem compartilhar uma apresentação quando a equivalência foi verificada; todas as variantes originais ficam preservadas. Conteúdo com continuidade duvidosa recebe indicação de revisão em vez de ser misturado ao cânone.

## Limites desta etapa

O foco é a migração íntegra e navegável. Ainda não inclui criar ou hospedar o site, excluir fontes, alterar o vault-42, atualizar documentos no Drive ou afirmar que todas as interpretações das fontes estão corretas.

## Organização enciclopédica posterior

A etapa seguinte, autorizada em 2026-10-29, está descrita em `docs/enciclopedia/criterios.md`. As entidades usam `status: documentado_parcial`, citações próximas das afirmações e `atualizado`. Lugares e facções podem ser aspectos distintos do mesmo núcleo; os links explícitos evitam ambiguidade. `Criaturas/` separa espécies e categorias de organizações ou indivíduos.

`Pendencias/` reúne perguntas para uma sabatina futura. Cada registro tem ID estável, categoria, prioridade, pergunta, fontes e entidades afetadas. As respostas já confirmadas não voltam a ser perguntas de identidade; dúvidas sobre mecanismos, destinos ou consequências continuam separadas. `Visoes/` contém sínteses de relações e fios abertos, com fontes e limites.
