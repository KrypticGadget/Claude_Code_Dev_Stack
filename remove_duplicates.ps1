$audioDir = "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\.claude-example\audio"
$files = Get-ChildItem $audioDir -Filter "*.wav"
Write-Host "Total wav files:" $files.Count

# Group by name to find exact duplicates
$grouped = $files | Group-Object Name
$duplicates = $grouped | Where-Object { $_.Count -gt 1 }

if ($duplicates) {
    Write-Host "Found exact duplicates:"
    foreach ($dup in $duplicates) {
        Write-Host "Duplicate: $($dup.Name) ($($dup.Count) copies)"
        # Delete all but the first copy
        for ($i = 1; $i -lt $dup.Group.Count; $i++) {
            Write-Host "Deleting: $($dup.Group[$i].FullName)"
            Remove-Item $dup.Group[$i].FullName -Force
        }
    }
} else {
    Write-Host "No exact duplicates found"
    
    # Look for files with same content (different approach)
    Write-Host "Checking for files with same size..."
    $sizeGroups = $files | Group-Object Length | Where-Object { $_.Count -gt 1 }
    
    if ($sizeGroups) {
        foreach ($sizeGroup in $sizeGroups) {
            Write-Host "Files with same size ($($sizeGroup.Name) bytes):"
            foreach ($file in $sizeGroup.Group) {
                Write-Host "  $($file.Name)"
            }
            # Delete duplicates by size if they have very similar names
            $names = $sizeGroup.Group.Name
            $baseName = $names[0] -replace '\d+|_copy|_duplicate|\s*\(\d+\)', ''
            
            for ($i = 1; $i -lt $sizeGroup.Group.Count; $i++) {
                $currentName = $names[$i] -replace '\d+|_copy|_duplicate|\s*\(\d+\)', ''
                if ($currentName -eq $baseName) {
                    Write-Host "Deleting similar file: $($sizeGroup.Group[$i].FullName)"
                    Remove-Item $sizeGroup.Group[$i].FullName -Force
                }
            }
        }
    }
}

$finalCount = (Get-ChildItem $audioDir -Filter "*.wav").Count
Write-Host "Final count: $finalCount"