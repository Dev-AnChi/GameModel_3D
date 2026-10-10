$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$taskWorkspace = 'C:\Game\GameModel_3D'
$taskTransfers = @(
    @{ Source = 'C:\Game\Commercial_3D\Wandering_Alchemist'; Target = 'C:\Game\GameModel_3D\Wandering_Alchemist' },
    @{ Source = 'C:\Game\Commercial_3D\Wandering_Alchemist_v2'; Target = 'C:\Game\GameModel_3D\Wandering_Alchemist_v2' },
    @{ Source = 'C:\Users\Admin\Downloads\tripo_pbr_model_14d23857-8311-470b-a053-77f7083d4962.glb'; Target = 'C:\Game\GameModel_3D\Wandering_Alchemist_v2\References\Models\tripo_pbr_model_14d23857-8311-470b-a053-77f7083d4962.glb' }
)
foreach ($taskTransfer in $taskTransfers) {
    $taskResolved = (Resolve-Path -LiteralPath $taskTransfer.Source).Path
    if ($taskResolved -ne $taskTransfer.Source) { throw 'Source path mismatch' }
    $taskDest = [System.IO.Path]::GetFullPath($taskTransfer.Target)
    if (-not $taskDest.StartsWith($taskWorkspace + '\', [System.StringComparison]::OrdinalIgnoreCase)) { throw 'Destination outside workspace' }
    if (Test-Path -LiteralPath $taskDest) { throw "Destination already exists: $taskDest" }
}
$taskRecords = @()
foreach ($taskTransfer in $taskTransfers) {
    $taskSourceItem = Get-Item -LiteralPath $taskTransfer.Source
    $taskFiles = if ($taskSourceItem.PSIsContainer) { @(Get-ChildItem -LiteralPath $taskTransfer.Source -File -Recurse -Force) } else { @($taskSourceItem) }
    $taskExpected = @($taskFiles | ForEach-Object {
        $taskRelative = if ($taskSourceItem.PSIsContainer) { $_.FullName.Substring($taskTransfer.Source.Length + 1) } else { '' }
        [PSCustomObject]@{ Relative = $taskRelative; Length = $_.Length; SHA256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash }
    })
    $taskParent = Split-Path -Parent $taskTransfer.Target
    if (-not (Test-Path -LiteralPath $taskParent)) { New-Item -ItemType Directory -Path $taskParent | Out-Null }
    Move-Item -LiteralPath $taskTransfer.Source -Destination $taskTransfer.Target
    foreach ($taskEntry in $taskExpected) {
        $taskPath = if ($taskEntry.Relative) { Join-Path $taskTransfer.Target $taskEntry.Relative } else { $taskTransfer.Target }
        $taskActual = Get-Item -LiteralPath $taskPath
        if ($taskActual.Length -ne $taskEntry.Length -or (Get-FileHash -LiteralPath $taskPath -Algorithm SHA256).Hash -ne $taskEntry.SHA256) { throw "Transfer verification failed: $taskPath" }
    }
    $taskRecords += [PSCustomObject]@{ Source = $taskTransfer.Source; Target = $taskTransfer.Target; Count = $taskExpected.Count; Verified = $true; Files = $taskExpected }
    Write-Output "Moved and SHA256 verified: $($taskTransfer.Target) ($($taskExpected.Count) files)"
}
$taskJson = $taskRecords | ConvertTo-Json -Depth 6
[System.IO.File]::WriteAllText((Join-Path $taskWorkspace 'wandering_relocation_manifest.json'), $taskJson, [System.Text.UTF8Encoding]::new($false))
