# Audio cleanup script to remove 6 extra files to get exactly 96
# Based on installer list vs current directory

$audioDir = "C:\Users\Zach\Desktop\Master Code\Claude_Code_Agents\Claude_Code_Dev_Stack\.claude-example\audio"

# Expected 96 files from installer
$expectedFiles = @(
    "agent_activated.wav", "agent_delegating.wav", "analyzing.wav", "analyzing_code.wav",
    "auto_accepting.wav", "auto_mode_active.wav", "awaiting_confirmation.wav", "awaiting_input.wav",
    "backend_agent.wav", "build_successful.wav", "cargo_build.wav", "changing_directory.wav",
    "checking_files.wav", "command_execution_pending.wav", "command_failed.wav", "command_successful.wav",
    "confirm_required.wav", "connection_error.wav", "context_loaded.wav", "context_saved.wav",
    "copy_operation.wav", "dashboard_started.wav", "database_agent.wav", "decision_required.wav",
    "delete_operation.wav", "dependency_installing.wav", "dependency_missing.wav", "docker_building.wav",
    "docker_running.wav", "documentation_generating.wav", "downloading_file.wav", "file_exists.wav",
    "file_not_found.wav", "file_operation_complete.wav", "file_operation_pending.wav", "formatting_code.wav",
    "frontend_agent.wav", "generating_code.wav", "git_commit.wav", "git_pull.wav",
    "git_push.wav", "git_status.wav", "handoff_generated.wav", "http_request.wav",
    "installing_packages.wav", "linting_complete.wav", "linting_issues.wav", "linting_started.wav",
    "make_build.wav", "master_orchestrator.wav", "milestone_complete.wav", "mkdir_operation.wav",
    "move_operation.wav", "notification_sent.wav", "no_venv_warning.wav", "npm_build.wav",
    "npm_install.wav", "obsidian_notes.wav", "operation_complete.wav", "optimizing_performance.wav",
    "orchestration_complete.wav", "orchestration_started.wav", "parallel_execution.wav", "performance_warning.wav",
    "permission_denied.wav", "permission_required.wav", "phase_complete.wav", "phase_deployment.wav",
    "phase_implementation.wav", "phase_planning.wav", "phase_testing.wav", "pipeline_complete.wav",
    "pipeline_initiated.wav", "pip_install.wav", "planning_complete.wav", "playwright_automation.wav",
    "processing.wav", "project_created.wav", "quality_gate_passed.wav", "ready_for_input.wav",
    "resource_warning.wav", "reviewing_changes.wav", "risky_command.wav", "running_tests.wav",
    "searching_files.wav", "security_scanning.wav", "smart_routing.wav", "ssh_connection.wav",
    "startup.wav", "status_update.wav", "tests_failed.wav", "tests_passed.wav",
    "token_critical.wav", "token_warning.wav", "touch_operation.wav", "tunnel_connected.wav",
    "tunnel_disconnected.wav", "v3_feature_activated.wav", "venv_activated.wav", "venv_required.wav",
    "web_search.wav", "working.wav"
)

# Get current files
$currentFiles = Get-ChildItem $audioDir -Filter "*.wav" | Select-Object -ExpandProperty Name

Write-Host "Expected files: $($expectedFiles.Count)"
Write-Host "Current files: $($currentFiles.Count)"

# Find extra files
$extraFiles = $currentFiles | Where-Object { $_ -notin $expectedFiles }

Write-Host "`nExtra files to remove:"
foreach ($file in $extraFiles) {
    Write-Host "  $file"
}

Write-Host "`nTo delete these files, run:"
foreach ($file in $extraFiles) {
    Write-Host "Remove-Item '$audioDir\$file' -Force"
}