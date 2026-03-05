# NovaPaw Installer for Windows
# Usage: irm <url>/install.ps1 | iex
#    or: .\install.ps1 [-Version X.Y.Z] [-FromSource [DIR]] [-Extras "llamacpp,mlx"]
#
# Installs NovaPaw into ~/.novapaw with a uv-managed Python environment.
# Users do NOT need Python pre-installed — uv handles everything.
#
# The entire script is wrapped in & { ... } @args so that `irm | iex` works
# correctly (param() is only valid inside a scriptblock/function/file scope).

& {
param(
    [string]$Version = "",
    [switch]$FromSource,
    [string]$SourceDir = "",
    [string]$Extras = "",
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# ── Defaults ──────────────────────────────────────────────────────────────────
$NovapawHome = if ($env:NOVAPAW_HOME) { $env:NOVAPAW_HOME } else { Join-Path $HOME ".novapaw" }
$NovapawVenv = Join-Path $NovapawHome "venv"
$NovapawBin = Join-Path $NovapawHome "bin"
$PythonVersion = "3.12"
$NovapawRepo = "https://github.com/agentscope-ai/NovaPaw.git"

# ── Colors ────────────────────────────────────────────────────────────────────
function Write-Info { param([string]$Message) Write-Host "[novapaw] " -ForegroundColor Green -NoNewline; Write-Host $Message }
function Write-Warn { param([string]$Message) Write-Host "[novapaw] " -ForegroundColor Yellow -NoNewline; Write-Host $Message }
function Write-Err  { param([string]$Message) Write-Host "[novapaw] " -ForegroundColor Red -NoNewline; Write-Host $Message }
function Stop-WithError { param([string]$Message) Write-Err $Message; exit 1 }

# ── Help ──────────────────────────────────────────────────────────────────────
if ($Help) {
    @"
NovaPaw Installer for Windows

Usage: .\install.ps1 [OPTIONS]

Options:
  -Version <VER>        Install a specific version (e.g. 0.0.2)
  -FromSource [DIR]     Install from source. If DIR is given, use that local
                        directory; otherwise clone from GitHub.
  -Extras <EXTRAS>      Comma-separated optional extras to install
                        (e.g. llamacpp, mlx, llamacpp,mlx)
  -Help                 Show this help

Environment:
  NOVAPAW_HOME            Installation directory (default: ~/.novapaw)
"@
    exit 0
}

Write-Host "[novapaw] " -ForegroundColor Green -NoNewline
Write-Host "Installing NovaPaw into " -NoNewline
Write-Host "$NovapawHome" -ForegroundColor White

# ── Execution Policy Check ────────────────────────────────────────────────────
$policy = Get-ExecutionPolicy
if ($policy -eq "Restricted") {
    Write-Info "Execution policy is 'Restricted', setting to RemoteSigned for current user..."
    try {
        Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Info "Execution policy updated to RemoteSigned"
    } catch {
        Write-Err "PowerShell execution policy is set to 'Restricted' which prevents script execution."
        Write-Err "Please run the following command and retry:"
        Write-Err ""
        Write-Err "  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser"
        Write-Err ""
        exit 1
    }
}

# ── Step 1: Ensure uv is available ───────────────────────────────────────────
function Ensure-Uv {
    if (Get-Command uv -ErrorAction SilentlyContinue) {
        Write-Info "uv found: $((Get-Command uv).Source)"
        return
    }

    # Check common install locations not yet on PATH
    $candidates = @(
        (Join-Path $HOME ".local\bin\uv.exe"),
        (Join-Path $HOME ".cargo\bin\uv.exe"),
        (Join-Path $env:LOCALAPPDATA "uv\uv.exe")
    )
    foreach ($candidate in $candidates) {
        if (Test-Path $candidate) {
            $dir = Split-Path $candidate -Parent
            $env:PATH = "$dir;$env:PATH"
            Write-Info "uv found: $candidate"
            return
        }
    }

    Write-Info "Installing uv..."
    try {
        irm https://astral.sh/uv/install.ps1 | iex
    } catch {
        Stop-WithError "Failed to install uv. Please install it manually: https://docs.astral.sh/uv/"
    }

    # Refresh PATH after uv install
    $uvPaths = @(
        (Join-Path $HOME ".local\bin"),
        (Join-Path $HOME ".cargo\bin"),
        (Join-Path $env:LOCALAPPDATA "uv")
    )
    foreach ($p in $uvPaths) {
        if ((Test-Path $p) -and ($env:PATH -notlike "*$p*")) {
            $env:PATH = "$p;$env:PATH"
        }
    }

    if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Stop-WithError "Failed to install uv. Please install it manually: https://docs.astral.sh/uv/"
    }
    Write-Info "uv installed successfully"
}

Ensure-Uv

# ── Step 2: Create / update virtual environment ──────────────────────────────
if (Test-Path $NovapawVenv) {
    Write-Info "Existing environment found, upgrading..."
} else {
    Write-Info "Creating Python $PythonVersion environment..."
}

uv venv $NovapawVenv --python $PythonVersion --quiet
if ($LASTEXITCODE -ne 0) { Stop-WithError "Failed to create virtual environment" }

$VenvPython = Join-Path $NovapawVenv "Scripts\python.exe"
if (-not (Test-Path $VenvPython)) { Stop-WithError "Failed to create virtual environment" }

$pyVersion = & $VenvPython --version 2>&1
Write-Info "Python environment ready ($pyVersion)"

# ── Step 3: Install NovaPaw ────────────────────────────────────────────────────
# Build extras suffix: "" or "[llamacpp,mlx]"
$ExtrasSuffix = ""
if ($Extras) {
    $ExtrasSuffix = "[$Extras]"
}

$script:ConsoleCopied = $false
$script:ConsoleAvailable = $false

function Prepare-Console {
    param([string]$RepoDir)

    $consoleSrc = Join-Path $RepoDir "console\dist"
    $consoleDest = Join-Path $RepoDir "src\novapaw\console"

    # Already populated
    if (Test-Path (Join-Path $consoleDest "index.html")) { $script:ConsoleAvailable = $true; return }

    # Copy pre-built assets if available
    if ((Test-Path $consoleSrc) -and (Test-Path (Join-Path $consoleSrc "index.html"))) {
        Write-Info "Copying console frontend assets..."
        New-Item -ItemType Directory -Path $consoleDest -Force | Out-Null
        Copy-Item -Path "$consoleSrc\*" -Destination $consoleDest -Recurse -Force
        $script:ConsoleCopied = $true
        $script:ConsoleAvailable = $true
        return
    }

    # Try to build if npm is available
    $packageJson = Join-Path $RepoDir "console\package.json"
    if (-not (Test-Path $packageJson)) {
        Write-Warn "Console source not found - the web UI won't be available."
        return
    }

    if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
        Write-Warn "npm not found - skipping console frontend build."
        Write-Warn "Install Node.js from https://nodejs.org/ then re-run this installer,"
        Write-Warn "or run 'cd console && npm ci && npm run build' manually."
        return
    }

    Write-Info "Building console frontend (npm ci && npm run build)..."
    Push-Location (Join-Path $RepoDir "console")
    try {
        npm ci
        if ($LASTEXITCODE -ne 0) { Write-Warn "npm ci failed - the web UI won't be available."; return }
        npm run build
        if ($LASTEXITCODE -ne 0) { Write-Warn "npm run build failed - the web UI won't be available."; return }
    } finally {
        Pop-Location
    }
    if (Test-Path (Join-Path $consoleSrc "index.html")) {
        New-Item -ItemType Directory -Path $consoleDest -Force | Out-Null
        Copy-Item -Path "$consoleSrc\*" -Destination $consoleDest -Recurse -Force
        $script:ConsoleCopied = $true
        $script:ConsoleAvailable = $true
        Write-Info "Console frontend built successfully"
        return
    }

    Write-Warn "Console build completed but index.html not found - the web UI won't be available."
}

function Cleanup-Console {
    param([string]$RepoDir)
    if ($script:ConsoleCopied) {
        $consoleDest = Join-Path $RepoDir "src\novapaw\console"
        if (Test-Path $consoleDest) {
            Remove-Item -Path "$consoleDest\*" -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

$VenvNovapaw = Join-Path $NovapawVenv "Scripts\novapaw.exe"

if ($FromSource) {
    if ($SourceDir) {
        $SourceDir = (Resolve-Path $SourceDir).Path
        Write-Info "Installing NovaPaw from local source: $SourceDir"
        Prepare-Console $SourceDir
        Write-Info "Installing package from source..."
        uv pip install "${SourceDir}${ExtrasSuffix}" --python $VenvPython --prerelease=allow
        if ($LASTEXITCODE -ne 0) { Stop-WithError "Installation from source failed" }
        Cleanup-Console $SourceDir
    } else {
        if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
            Stop-WithError "git is required for -FromSource without a local directory. Please install Git from https://git-scm.com/ or pass a local path: .\install.ps1 -FromSource -SourceDir C:\path\to\NovaPaw"
        }
        Write-Info "Installing NovaPaw from source (GitHub)..."
        $cloneDir = Join-Path $env:TEMP "novapaw-install-$(Get-Random)"
        try {
            git clone --depth 1 $NovapawRepo $cloneDir
            if ($LASTEXITCODE -ne 0) { Stop-WithError "Failed to clone repository" }
            Prepare-Console $cloneDir
            Write-Info "Installing package from source..."
            uv pip install "${cloneDir}${ExtrasSuffix}" --python $VenvPython --prerelease=allow
            if ($LASTEXITCODE -ne 0) { Stop-WithError "Installation from source failed" }
        } finally {
            if (Test-Path $cloneDir) {
                Remove-Item -Path $cloneDir -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
} else {
    $package = "novapaw"
    if ($Version) {
        $package = "novapaw==$Version"
    }

    Write-Info "Installing ${package}${ExtrasSuffix} from PyPI..."
    uv pip install "${package}${ExtrasSuffix}" --python $VenvPython --prerelease=allow --quiet
    if ($LASTEXITCODE -ne 0) { Stop-WithError "Installation failed" }
}

# Verify the CLI entry point exists
if (-not (Test-Path $VenvNovapaw)) { Stop-WithError "Installation failed: novapaw CLI not found in venv" }

Write-Info "NovaPaw installed successfully"

# Check console availability (for PyPI installs, check the installed package)
if (-not $script:ConsoleAvailable) {
    $consoleCheck = & $VenvPython -c "import importlib.resources, novapaw; p=importlib.resources.files('novapaw')/'console'/'index.html'; print('yes' if p.is_file() else 'no')" 2>&1
    if ($consoleCheck -eq "yes") { $script:ConsoleAvailable = $true }
}

# ── Step 4: Create wrapper script ────────────────────────────────────────────
New-Item -ItemType Directory -Path $NovapawBin -Force | Out-Null

$wrapperPath = Join-Path $NovapawBin "novapaw.ps1"
$wrapperContent = @'
# NovaPaw CLI wrapper — delegates to the uv-managed environment.
$ErrorActionPreference = "Stop"

$NovapawHome = if ($env:NOVAPAW_HOME) { $env:NOVAPAW_HOME } else { Join-Path $HOME ".novapaw" }
$RealBin = Join-Path $NovapawHome "venv\Scripts\novapaw.exe"

if (-not (Test-Path $RealBin)) {
    Write-Error "NovaPaw environment not found at $NovapawHome\venv"
    Write-Error "Please reinstall: irm <install-url> | iex"
    exit 1
}

& $RealBin @args
'@

Set-Content -Path $wrapperPath -Value $wrapperContent -Encoding UTF8
Write-Info "Wrapper created at $wrapperPath"

# Also create a .cmd wrapper for use from cmd.exe
$cmdWrapperPath = Join-Path $NovapawBin "novapaw.cmd"
$cmdWrapperContent = @"
@echo off
REM NovaPaw CLI wrapper — delegates to the uv-managed environment.
set "NOVAPAW_HOME=%NOVAPAW_HOME%"
if "%NOVAPAW_HOME%"=="" set "NOVAPAW_HOME=%USERPROFILE%\.novapaw"
set "REAL_BIN=%NOVAPAW_HOME%\venv\Scripts\novapaw.exe"
if not exist "%REAL_BIN%" (
    echo Error: NovaPaw environment not found at %NOVAPAW_HOME%\venv >&2
    echo Please reinstall: irm ^<install-url^> ^| iex >&2
    exit /b 1
)
"%REAL_BIN%" %*
"@

Set-Content -Path $cmdWrapperPath -Value $cmdWrapperContent -Encoding UTF8
Write-Info "CMD wrapper created at $cmdWrapperPath"

# ── Step 5: Update PATH via User Environment Variable ────────────────────────
$currentUserPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentUserPath -notlike "*$NovapawBin*") {
    [Environment]::SetEnvironmentVariable("Path", "$NovapawBin;$currentUserPath", "User")
    $env:PATH = "$NovapawBin;$env:PATH"
    Write-Info "Added $NovapawBin to user PATH"
} else {
    Write-Info "$NovapawBin already in PATH"
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "NovaPaw installed successfully!" -ForegroundColor Green
Write-Host ""

# Install summary
Write-Host "  Install location:  " -NoNewline; Write-Host "$NovapawHome" -ForegroundColor White
Write-Host "  Python:            " -NoNewline; Write-Host "$pyVersion" -ForegroundColor White
if ($script:ConsoleAvailable) {
    Write-Host "  Console (web UI):  " -NoNewline; Write-Host "available" -ForegroundColor Green
} else {
    Write-Host "  Console (web UI):  " -NoNewline; Write-Host "not available" -ForegroundColor Yellow
    Write-Host "                     Install Node.js and re-run to enable the web UI."
}
Write-Host ""

Write-Host "To get started, open a new terminal and run:"
Write-Host ""
Write-Host "  novapaw init" -ForegroundColor White -NoNewline; Write-Host "       # first-time setup"
Write-Host "  novapaw app" -ForegroundColor White -NoNewline; Write-Host "        # start NovaPaw"
Write-Host ""
Write-Host "To upgrade later, re-run this installer."
Write-Host "To uninstall, run: " -NoNewline
Write-Host "novapaw uninstall" -ForegroundColor White

} @args
