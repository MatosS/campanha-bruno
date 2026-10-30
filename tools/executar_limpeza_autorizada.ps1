$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath('C:\sources\campanha-bruno')
$vaultRoot = [IO.Path]::GetFullPath('C:\sources\vault-42')
$auditPath = Join-Path $taskRoot 'docs\auditoria-exclusao\candidatos.json'
$executionPath = Join-Path $taskRoot 'docs\limpeza\execucao.json'
if (Test-Path -LiteralPath $executionPath) { throw 'A execução já possui registro; não repetir exclusões.' }
$audit = Get-Content -LiteralPath $auditPath -Raw | ConvertFrom-Json
$linkPlan = Get-Content -LiteralPath (Join-Path $taskRoot 'docs\limpeza\links-vault.json') -Raw | ConvertFrom-Json
if (@($audit.arquivos.'BASE INICIAL').Count -ne 12 -or @($audit.arquivos.'vault-42').Count -ne 53) { throw 'Contagens inesperadas.' }

function Assert-ContainedFile([string]$root, [string]$relative, [bool]$mustExist = $true) {
    $full = [IO.Path]::GetFullPath((Join-Path $root $relative))
    $prefix = $root.TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Fora do diretório autorizado: $full" }
    if ($mustExist -and -not (Test-Path -LiteralPath $full -PathType Leaf)) { throw "Arquivo ausente: $full" }
    $current = $full
    while ($current.Length -ge $root.Length) {
        if (Test-Path -LiteralPath $current) {
            $entry = Get-Item -LiteralPath $current -Force
            if (($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Link de filesystem não permitido: $current" }
        }
        if ($current -eq $root) { break }
        $current = Split-Path -Parent $current
    }
    return $full
}

function Assert-Hash([string]$path, [string]$expected) {
    $actual = (Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -ne $expected) { throw "Hash divergente: $path" }
}

$gitExe = 'C:\Users\guilh\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\git\cmd\git.exe'
$branch = & $gitExe -C $vaultRoot branch --show-current
if ($LASTEXITCODE -ne 0 -or $branch -ne 'main') { throw 'O vault precisa estar na branch main.' }
$targets = @()
foreach ($group in @('BASE INICIAL', 'vault-42')) {
    foreach ($item in $audit.arquivos.$group) {
        if ($group -eq 'vault-42') {
            if (-not $item.origem.StartsWith('vault-42/')) { throw 'Origem vault inválida.' }
            $source = Assert-ContainedFile $vaultRoot $item.origem.Substring(9)
        } else {
            if (-not $item.origem.StartsWith('BASE INICIAL/')) { throw 'Origem BASE inválida.' }
            $source = Assert-ContainedFile (Join-Path $taskRoot 'BASE INICIAL') $item.origem.Substring(13)
        }
        if (-not $item.copia_preservada.StartsWith('arquivo/originais/')) { throw 'Cópia fora do arquivo de preservação.' }
        $copy = Assert-ContainedFile (Join-Path $taskRoot 'arquivo\originais') $item.copia_preservada.Substring(18)
        Assert-Hash $source $item.sha256
        Assert-Hash $copy $item.sha256
        $targets += [PSCustomObject]@{ source = $source; record = $item }
    }
}
$baseRoot = [IO.Path]::GetFullPath((Join-Path $taskRoot 'BASE INICIAL'))
if ($baseRoot -ne 'C:\sources\campanha-bruno\BASE INICIAL') { throw 'BASE inesperada.' }
$actualBase = @(Get-ChildItem -LiteralPath $baseRoot -Recurse -Force -File | ForEach-Object { $_.FullName })
$expectedBase = @($targets | Where-Object { $_.record.origem.StartsWith('BASE INICIAL/') } | ForEach-Object { $_.source })
if (@(Compare-Object $actualBase $expectedBase).Count -ne 0) { throw 'BASE contém arquivos fora da lista auditada.' }
if (@(Get-ChildItem -LiteralPath $baseRoot -Force -Directory).Count -ne 0) { throw 'BASE contém subdiretórios não previstos.' }

$patches = @()
foreach ($item in $linkPlan.arquivos) {
    $destination = Assert-ContainedFile $vaultRoot $item.caminho ($null -ne $item.antes_sha256)
    $staged = Assert-ContainedFile (Join-Path $taskRoot 'docs\limpeza\patches\vault-42') $item.caminho
    Assert-Hash $staged $item.depois_sha256
    if ($null -ne $item.antes_sha256) { Assert-Hash $destination $item.antes_sha256 }
    elseif (Test-Path -LiteralPath $destination) { throw "Nova nota já existe: $destination" }
    $patches += [PSCustomObject]@{ source = $staged; destination = $destination; record = $item }
}

# Todas as listas e cópias foram conferidas antes da primeira alteração.
$started = [DateTimeOffset]::Now.ToString('o')
foreach ($patch in $patches) {
    Copy-Item -LiteralPath $patch.source -Destination $patch.destination
    Assert-Hash $patch.destination $patch.record.depois_sha256
}
$removed = @()
foreach ($target in $targets) {
    Assert-Hash $target.source $target.record.sha256
    Remove-Item -LiteralPath $target.source -Force
    if (Test-Path -LiteralPath $target.source) { throw "Remoção falhou: $($target.source)" }
    $removed += $target.record
    [ordered]@{ data = $started; autorizacao = 'Usuário autorizou explicitamente a remoção da BASE INICIAL e dos 53 arquivos auditados do vault-42 em 2026-10-29.'; estado = 'em_execucao'; arquivos = $removed } | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $executionPath -Encoding utf8NoBOM
}
if (@(Get-ChildItem -LiteralPath $baseRoot -Force).Count -ne 0) { throw 'BASE ainda contém itens; não remover diretório.' }
Remove-Item -LiteralPath $baseRoot
foreach ($target in $targets) {
    $copy = Join-Path $taskRoot $target.record.copia_preservada
    Assert-Hash $copy $target.record.sha256
    if (Test-Path -LiteralPath $target.source) { throw 'Origem reapareceu.' }
}
$execution = [ordered]@{
    data = $started
    concluida_em = [DateTimeOffset]::Now.ToString('o')
    autorizacao = 'Usuário autorizou explicitamente a remoção da BASE INICIAL e dos 53 arquivos auditados do vault-42 em 2026-10-29.'
    estado = 'concluida'
    arquivos = $removed
    base_inicial_removida = -not (Test-Path -LiteralPath $baseRoot)
    links_vault = $linkPlan.links_redirecionados
    notas_vault_ajustadas = $linkPlan.arquivos_existentes_alterados
}
$execution | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $executionPath -Encoding utf8NoBOM
$audit.exclusao_executada = $true
$audit | Add-Member -NotePropertyName registro_execucao -NotePropertyValue 'docs/limpeza/execucao.json' -Force
$audit | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $auditPath -Encoding utf8NoBOM
Write-Output "Removidos $($removed.Count) arquivos autorizados; 65 cópias conferidas; BASE INICIAL removida; $($linkPlan.links_redirecionados) links corrigidos."
