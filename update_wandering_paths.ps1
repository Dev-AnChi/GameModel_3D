$ErrorActionPreference = 'Stop'
$taskRoot = 'C:\Game\GameModel_3D'
$taskScriptNames = @('phase3_ab.py','download_phase65_assets.py','create_wandering_alchemist_phase1.py','phase6_wood_pass.py','phase65_finalize.py','phase65_reports.py','phase5_stage12.py','phase65_material_trials.py','phase4_pass_a.py','redesign_wandering_alchemist_phase25.py','reference_rework_stage_a.py','upgrade_wandering_alchemist_phase2.py','inspect_tripo_glb.py')
$taskFiles = @($taskScriptNames | ForEach-Object { Get-Item -LiteralPath (Join-Path $taskRoot $_) })
foreach ($taskProject in @('Wandering_Alchemist','Wandering_Alchemist_v2')) {
    $taskFiles += Get-ChildItem -LiteralPath (Join-Path $taskRoot $taskProject) -Recurse -File | Where-Object { $_.Extension -in '.py','.md','.json','.txt' }
}
$taskOldGlb = 'C:\Users\Admin\Downloads\tripo_pbr_model_14d23857-8311-470b-a053-77f7083d4962.glb'
$taskNewGlb = 'C:\Game\GameModel_3D\Wandering_Alchemist_v2\References\Models\tripo_pbr_model_14d23857-8311-470b-a053-77f7083d4962.glb'
foreach ($taskFile in $taskFiles) {
    $taskText = [System.IO.File]::ReadAllText($taskFile.FullName,[System.Text.Encoding]::UTF8)
    $taskUpdated = $taskText.Replace('C:\Game\Commercial_3D\Wandering_Alchemist','C:\Game\GameModel_3D\Wandering_Alchemist').Replace('C:\\Game\\Commercial_3D\\Wandering_Alchemist','C:\\Game\\GameModel_3D\\Wandering_Alchemist').Replace('C:/Game/Commercial_3D/Wandering_Alchemist','C:/Game/GameModel_3D/Wandering_Alchemist').Replace($taskOldGlb,$taskNewGlb)
    if ($taskUpdated -ne $taskText) {
        [System.IO.File]::WriteAllText($taskFile.FullName,$taskUpdated.Normalize([System.Text.NormalizationForm]::FormC),[System.Text.UTF8Encoding]::new($false))
        Write-Output "Updated: $($taskFile.FullName)"
    }
}
