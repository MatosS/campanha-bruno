# Importação dos diários de Firael e do prelúdio de Ryld

Recebidos em 30/10/2026. Os quatro arquivos da Área de Trabalho foram somente lidos e copiados. Nenhuma alteração foi feita no Google Doc compartilhado.

- `manifesto.json`: caminhos, hashes SHA-256 dos quatro originais, de todas as partes dos pacotes DOCX, das conversões e das auditorias por parágrafo.
- `* - paragrafos.json`: texto integral, Markdown, ordem, listas e separadores de cada parágrafo, inclusive vazios e repetições.
- `comparacao.json`: diferenças entre as versões de Firael e repetição do capítulo 6 de Ryld.
- `verificacao.json`: resultado da conferência independente de originais, partes OOXML, texto, ordem e representação em Markdown.

As quatro cópias ficam em `arquivo/originais/importacoes-2026-10-30`. Somam-se aos 65 originais da migração anterior, cujo manifesto histórico não foi reescrito. As contagens do verificador antigo continuam referentes àquela migração; esta importação possui sua própria auditoria.

Conversões integrais em `conteudo/Fontes/Documentos`. Notas curadas e visão de integração em `conteudo/Visoes/Novas fontes - Firael e Ryld.md`. Datas dos cabeçalhos são rótulos documentais, sem equivalência automática com o calendário do mundo. Afirmações, crenças, planos e fala atribuída a NPC conservam essas condições.

Foram complementadas PC-008, FC-002, PC-039, LG-005, LG-008, FC-015, EV-002, IT-002 e PC-014. Nenhuma foi encerrada integralmente, pois restam perguntas de outro alcance ou época. As respostas preservadas no Google Doc e o espelho histórico de compartilhamento não foram editados.

Verificação desta importação: executar `tools/verificar_importacao_firael_ryld.py` com o Python bundled do Codex. Os verificadores gerais são `tools/verificar_enciclopedia.py` e `tools/verificar_migracao.py`; a navegação é atualizada com `tools/indexar_enciclopedia.py --somente-indices`.

A verificação compara os 2.904 parágrafos das quatro fontes e também retira as marcações da conversão para conferir o texto visível. Não declara equivalência de paginação entre DOCX e Markdown. As figuras VML encontradas são somente réguas horizontais; não há imagens, tabelas, notas, comentários, cabeçalhos ou rodapés adicionais com conteúdo nesses arquivos.
