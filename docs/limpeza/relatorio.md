# Remoção autorizada das origens duplicadas

Em 2026-10-29, o usuário autorizou a exclusão da `BASE INICIAL` e dos 53 arquivos auditados do `vault-42`, preservando `arquivo/originais`, `conteudo/Fontes` e `conteudo/Anexos`. A execução foi concluída.

- Removidos os 12 arquivos da `BASE INICIAL` e, depois de conferir que estava vazia, a própria pasta.
- Removidos exatamente os 53 arquivos do vault presentes na [lista auditada](../auditoria-exclusao/candidatos.json).
- As 65 cópias integrais preservadas tiveram seu SHA-256 conferido antes e depois da exclusão.
- Um snapshot de 352 arquivos existentes em originais, fontes e anexos foi conferido após a remoção: nenhum desses arquivos foi alterado. Os índices podem receber novos links da sabatina, e as confirmações são fontes novas.
- Redirecionados 186 links funcionais em 30 notas do vault. A nota `Campanha de Fash e Glim - Base externa`, em `30 Areas/RPG`, oferece uma seção por origem, com acesso ao conteúdo convertido e à cópia integral. Foi criado também o registro de manutenção exigido pelo vault.
- Caminhos escritos como texto e exemplos em código nos registros antigos continuam descrevendo sua época. Os links de consulta do levantamento inicial foram atualizados para os originais preservados.

As outras campanhas, os arquivos do Google Drive, gravações, export ZIP e handoff TXT que não estavam na lista foram mantidos. Os documentos de auditoria anteriores continuam registrando o estado observado naquela etapa.

## Evidências

- [Execução, autorização e lista exata de remoções](execucao.json).
- [Verificação da limpeza](verificacao.json).
- [Hashes dos arquivos protegidos antes da limpeza](protecao-antes.json).
- [Alterações nos links do vault](links-vault.json); as versões anteriores ficam em `antes-links/vault-42/`.
- [Verificação da migração](../migracao/verificacao.json) e [verificação da enciclopédia](../enciclopedia/verificacao.json).

A revisão independente conferiu novamente as cópias e os três verificadores. Em 424 notas ativas do vault, não encontrou links funcionais restantes para os 53 arquivos removidos. As pastas de sistema e os documentos históricos com exemplos de código ficaram fora dessa busca de navegação.

`tools/verificar_limpeza.py` repete a conferência das remoções, das cópias e dos links afetados. `tools/verificar_migracao.py` continua validando a conversão e só aceita origens ausentes quando os hashes e as listas de preservação, auditoria e execução coincidem. As origens históricas dos manifestos foram mantidas como proveniência.

Os arquivos em `patches/` são as saídas exatas preparadas antes da alteração do vault. O script de execução recusa uma segunda execução para evitar repetir a operação.

A manutenção do vault foi registrada no commit `4eefce77b1648b9b6f3bcb4a3ca51adc253932ce`, com exatamente 85 arquivos: 53 remoções, 30 notas com links ajustados e duas novas notas. Após autorização explícita do usuário, o commit foi enviado para `MatosS/vault-42`, na branch `main`; o estado local ficou limpo e sincronizado com `origin/main`. Veja o [registro Git](git-vault.json).
