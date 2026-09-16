# Step 5b - Add Power Query queries, load them to tables, recalculate in Excel, scan for errors.
$ErrorActionPreference = "Stop"
# Project root: the folder that contains scripts/, build/ and outputs/.
# Resolved from this script's own location; override with $env:VAN311_ROOT.
$root  = if ($env:VAN311_ROOT) { $env:VAN311_ROOT } else { Split-Path -Parent $PSScriptRoot }
$stage = "$root\build\workbook_stage1.xlsx"
$final = "$root\outputs\Vancouver311_Closure_Outcomes_Workbook.xlsx"
Copy-Item $stage $final -Force
$missing = [System.Reflection.Missing]::Value
$xl = New-Object -ComObject Excel.Application
$xl.DisplayAlerts = $false; $xl.Visible = $false; $xl.ScreenUpdating = $false
try {
    $wb = $xl.Workbooks.Open($final)
    $xl.CalculateFull()
    "DataFile resolves to: " + $wb.Worksheets.Item("README").Range("DataFile").Text
    # Both sources are local files / this workbook; ignore privacy levels to avoid the Formula.Firewall.
    $wb.Queries.FastCombine = $true
    $defs = @(
        @{ Name = "Source_Data";      File = "$root\scripts\pq_source_data.m";      Sheet = "Source_Data" },
        @{ Name = "Source_Durations"; File = "$root\scripts\pq_source_durations.m"; Sheet = "Source_Durations" }
    )
    foreach ($d in $defs) {
        $m = Get-Content $d.File -Raw
        $null = $wb.Queries.Add($d.Name, $m, "3-1-1 case study Power Query step")
        $ws = $wb.Worksheets.Item($d.Sheet)
        $conn = "OLEDB;Provider=Microsoft.Mashup.OleDb.1;Data Source=`$Workbook`$;Location=$($d.Name);Extended Properties=`"`""
        $lo = $ws.ListObjects.Add(0, $conn, $missing, 1, $ws.Range("A3"))
        $lo.Name = "tbl" + ($d.Name -replace "_", "")
        $qt = $lo.QueryTable
        $qt.CommandType = 2
        $qt.CommandText = "SELECT * FROM [$($d.Name)]"
        $qt.BackgroundQuery = $false
        $qt.RefreshStyle = 1
        $qt.PreserveColumnInfo = $true
        $qt.AdjustColumnWidth = $true
        $qt.RefreshOnFileOpen = $false
        try { $null = $qt.Refresh($false) } catch { "REFRESH FAILED for $($d.Name): " + $_.Exception.Message; throw }
        $hdr = @(); foreach ($c in $lo.ListColumns) { $hdr += $c.Name }
        "$($d.Name): rows=$($lo.ListRows.Count) | " + ($hdr -join ",")
    }
    $xl.CalculateFullRebuild()
    $total = 0
    foreach ($ws in $wb.Worksheets) {
        try { $rng = $ws.UsedRange.SpecialCells(-4123, 16); $total += $rng.Count; "ERROR CELLS on $($ws.Name): $($rng.Address($false, $false))" } catch { }
    }
    "Formula error cells: $total"
    "Analysis all-checks cell: " + $wb.Worksheets.Item("Dashboard").Range("T6").Text
    $wb.Worksheets.Item("README").Activate()
    $wb.Save()
    $wb.Close($false)
} finally {
    $xl.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
}
