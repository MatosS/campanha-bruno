# Migração do acervo da campanha — plano de implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Independent format conversions use superpowers:dispatching-parallel-agents.

**Goal:** Transferir o material de Fash/Glim e converter a BASE INICIAL para Markdown navegável sem alterar ou apagar as fontes.

**Architecture:** Conteúdo publicável em `conteudo/`, separado de cópias exatas de preservação e manifestos. Fontes integrais sustentam notas de sessão e entidades com links explícitos. Conversões de PDF, DOCX e XLSX têm saídas distintas e são integradas após conferência.

**Tech Stack:** Markdown/YAML, Python padrão e bibliotecas do runtime de documentos, extração de XML/ZIP e renderização de fontes.

**Spec:** `docs/formato-da-base.md`, `docs/levantamento-inicial.md` e instrução do jogador de 2026-10-29 autorizando o início da transferência.

## Global Constraints

- Não alterar o vault-42 ou a BASE INICIAL; não excluir arquivos.
- Toda a base é pública; limitar o recorte à campanha de Fash/Glim.
- Preservar integralmente as informações relevantes; ajustes de formato não são reescrita narrativa.
- Arquivar originais e registrar hashes para permitir conferência antes de remoções futuras.
- Registrar limites de conversão; não declarar pronto para exclusão aquilo que não estiver verificado.

## Review Focus

- Abas ocultas, células com fórmula, comentários e imagens nas planilhas.
- Páginas de PDF sem camada de texto ou com ordem visual significativa.
- Tabelas, notas, hyperlinks e imagens no DOCX.
- Duplicatas com ordem diferente, metadados e análises que contêm informação além do diário.
- Links para índices pessoais, notas ausentes e colisões de nomes.

## Tarefa 1 — Copiar fontes e importar textos

- [x] Arquivar os 12 arquivos iniciais e as fontes selecionadas do vault com hash idêntico.
- [x] Converter fontes Markdown/TXT e transcrições preservando seus corpos.
- [x] Registrar origem, destino, método e estado de cada conversão em manifesto.

## Tarefa 2 — Converter documentos binários

- [x] Converter os dois PDFs com preservação visual e texto verificável.
- [x] Converter as duas planilhas, cobrindo todas as células com conteúdo, fórmulas, comentários e imagens.
- [x] Converter o DOCX, cobrindo blocos e estruturas adicionais relevantes.
- [x] Integrar os manifestos de conversão e conferir que todas as saídas existem.

## Tarefa 3 — Criar navegação e conferir preservação

- [x] Separar as 27 entradas do diário de Glim em notas de sessão sem reescrever o texto.
- [x] Criar índices e notas de entidades com fontes explícitas; adaptar links do vault ao novo recorte.
- [x] Validar YAML, links, imagens, hashes dos originais e cobertura de todos os arquivos iniciais.
- [x] Produzir relatório final com verificações e eventuais limites de conversão.

Execução já autorizada pelo jogador nesta conversa. Não há commit/push nesta pasta, que ainda não é um repositório Git; nenhuma operação Git será feita no vault-42.
