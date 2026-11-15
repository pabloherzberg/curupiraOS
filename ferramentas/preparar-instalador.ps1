# Curupira OS - prepara o boot do instalador SEM pendrive (rodar no Windows, como administrador).
#
# O que faz:
#   1. encolhe o C: em ~2,5 GB;
#   2. cria ali uma particao FAT32 com o conteudo da ISO do Arch Linux;
#   3. ajusta o instalador para carregar inteiro na RAM (copytoram), liberando o NVMe para ser apagado;
#   4. cria a entrada de boot UEFI "Curupira Instalador" (a do Windows continua sendo a primeira).
#
# Uso:
#   .\preparar-instalador.ps1 -Iso C:\caminho\archlinux-x86_64.iso -Sha256 <hash>
#   .\preparar-instalador.ps1 -Desfazer      remove a entrada de boot e a particao, e devolve o espaco ao C:
#
# (sem acentos de proposito: o PowerShell 5.1 le arquivos sem BOM como ANSI)

[CmdletBinding()]
param(
  [string]$Iso,
  [string]$Sha256,
  [switch]$Desfazer,
  [switch]$SuspenderBitLocker
)

$ErrorActionPreference = 'Stop'
$Rotulo = 'CURUPINST'
$Estado = Join-Path $env:ProgramData 'curupira-instalador.txt'
$TamanhoMB = 2560

function Diz($m)   { Write-Host "==> $m" -ForegroundColor Green }
function Avisa($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

$souAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $souAdmin) { throw 'Abra o PowerShell como administrador e rode de novo.' }

# ------------------------------------------------------------------ desfazer
if ($Desfazer) {
  if (Test-Path $Estado) {
    $guid = (Get-Content $Estado -TotalCount 1).Trim()
    if ($guid -match '^\{[0-9a-fA-F-]+\}$') {
      Diz "Removendo a entrada de boot $guid"
      & bcdedit /delete $guid | Out-Null
    }
    Remove-Item $Estado -Force
  }
  $vol = Get-Volume | Where-Object { $_.FileSystemLabel -eq $Rotulo }
  if ($vol) {
    $p = $vol | Get-Partition
    Diz "Removendo a particao $Rotulo (disco $($p.DiskNumber), particao $($p.PartitionNumber))"
    Remove-Partition -DiskNumber $p.DiskNumber -PartitionNumber $p.PartitionNumber -Confirm:$false
  }
  $max = (Get-PartitionSupportedSize -DriveLetter C).SizeMax
  if ($max -gt (Get-Partition -DriveLetter C).Size) {
    Diz 'Devolvendo o espaco ao C:'
    Resize-Partition -DriveLetter C -Size $max
  }
  Diz 'Desfeito.'
  return
}

# ------------------------------------------------------------------ verificacoes
if (-not $Iso -or -not (Test-Path $Iso)) { throw 'Informe a ISO: -Iso C:\caminho\archlinux-x86_64.iso' }
if (-not $Sha256) { throw 'Informe o hash esperado: -Sha256 <hash da pagina de download do Arch>' }
if (Get-Volume | Where-Object { $_.FileSystemLabel -eq $Rotulo }) { throw "Ja existe uma particao $Rotulo. Rode com -Desfazer antes." }

Diz 'Conferindo o SHA256 da ISO (leva um minuto)'
$hash = (Get-FileHash -Algorithm SHA256 -Path $Iso).Hash
if ($hash -ne $Sha256.ToUpper()) { throw "SHA256 nao confere. Esperado $Sha256, obtido $hash. Baixe a ISO de novo." }

$bl = $null
try { $bl = Get-BitLockerVolume -MountPoint 'C:' } catch { Avisa 'Nao foi possivel consultar o BitLocker.' }
if ($bl -and $bl.ProtectionStatus -eq 'On') {
  if (-not $SuspenderBitLocker) {
    throw 'O BitLocker esta ativo no C:. Mudar o boot pode fazer o Windows pedir a chave de recuperacao. Salve a chave (aka.ms/myrecoverykey) e rode de novo com -SuspenderBitLocker.'
  }
  Diz 'Suspendendo o BitLocker por 2 reinicializacoes'
  Suspend-BitLocker -MountPoint 'C:' -RebootCount 2 | Out-Null
}

$c = Get-Partition -DriveLetter C
$disco = $c.DiskNumber
$min = (Get-PartitionSupportedSize -DriveLetter C).SizeMin
$novo = $c.Size - ($TamanhoMB * 1MB)
if ($novo -lt ($min + 5GB)) { throw 'O C: nao tem folga suficiente para encolher. Libere espaco e tente de novo.' }

# ------------------------------------------------------------------ particao
Diz "Encolhendo o C: em $TamanhoMB MB"
Resize-Partition -DriveLetter C -Size $novo

Diz 'Criando a particao do instalador (FAT32)'
$p = New-Partition -DiskNumber $disco -UseMaximumSize -AssignDriveLetter -GptType '{ebd0a0a2-b9e5-4433-87c0-68b6b72699c7}'
$null = Format-Volume -Partition $p -FileSystem FAT32 -NewFileSystemLabel $Rotulo -Confirm:$false
$p = Get-Partition -DiskNumber $disco -PartitionNumber $p.PartitionNumber
$letra = "$($p.DriveLetter):"

# ------------------------------------------------------------------ copia
Diz 'Copiando o conteudo da ISO'
$img = Mount-DiskImage -ImagePath (Resolve-Path $Iso).Path -PassThru
try {
  $origem = "$(($img | Get-Volume).DriveLetter):"
  & robocopy "$origem\" "$letra\" /E /R:1 /W:1 /NFL /NDL /NJH /NP | Out-Null
  if ($LASTEXITCODE -ge 8) { throw "Falha ao copiar os arquivos (robocopy $LASTEXITCODE)." }
} finally {
  Dismount-DiskImage -ImagePath (Resolve-Path $Iso).Path | Out-Null
}
if (-not (Test-Path "$letra\EFI\BOOT\BOOTx64.EFI")) { throw 'A ISO copiada nao tem EFI\BOOT\BOOTx64.EFI.' }
& attrib -R "$letra\*" /S /D | Out-Null

# ------------------------------------------------------------------ copytoram
# Com copytoram o sistema de instalacao vai inteiro para a RAM e solta o NVMe.
Diz 'Ajustando o boot para carregar na memoria (copytoram)'
$ajustados = 0
$utf8 = New-Object Text.UTF8Encoding $false
$arquivos = @()
if (Test-Path "$letra\loader\entries") { $arquivos += Get-ChildItem "$letra\loader\entries\*.conf" }
foreach ($g in 'boot\grub\grub.cfg', 'boot\grub\loopback.cfg') { if (Test-Path "$letra\$g") { $arquivos += Get-Item "$letra\$g" } }
foreach ($a in $arquivos) {
  $linhas = [IO.File]::ReadAllLines($a.FullName)
  $mudou = $false
  for ($i = 0; $i -lt $linhas.Count; $i++) {
    $l = $linhas[$i]
    if ($l -match 'archisobasedir=' -and $l -notmatch 'copytoram') { $linhas[$i] = $l.TrimEnd() + ' copytoram'; $mudou = $true }
  }
  if ($mudou) { [IO.File]::WriteAllText($a.FullName, ($linhas -join "`n") + "`n", $utf8); $ajustados++ }
}
if ($ajustados -eq 0) { Avisa 'Nao encontrei as linhas de boot para ajustar. No menu do Arch, aperte "e" e acrescente copytoram no fim da linha.' }

# Se a ISO procura a midia pelo rotulo, o rotulo da particao precisa ser o mesmo.
$txt = ($arquivos | ForEach-Object { [IO.File]::ReadAllText($_.FullName) }) -join "`n"
if ($txt -match 'archisolabel=(\S+)') {
  $rot = $Matches[1]
  if ($rot.Length -le 11) { Set-Volume -DriveLetter $p.DriveLetter -NewFileSystemLabel $rot; Avisa "A particao recebeu o rotulo $rot (exigido pela ISO)." }
}

# ------------------------------------------------------------------ entrada de boot
Diz 'Criando a entrada de boot "Curupira Instalador"'
$saida = (& bcdedit /copy '{bootmgr}' /d 'Curupira Instalador') -join ' '
if ($saida -notmatch '\{[0-9a-fA-F-]{36}\}') { throw "bcdedit nao devolveu o identificador: $saida" }
$guid = $Matches[0]
& bcdedit /set $guid device "partition=$letra" | Out-Null
& bcdedit /set $guid path '\EFI\BOOT\BOOTx64.EFI' | Out-Null
& bcdedit /set '{fwbootmgr}' displayorder $guid /addlast | Out-Null
Set-Content -Path $Estado -Value $guid -Encoding ASCII

Write-Host ''
Diz 'Pronto. O Windows continua iniciando normalmente.'
Write-Host "    Particao do instalador: $letra   entrada de boot: $guid"
Write-Host '    Para iniciar o instalador: desligue o Secure Boot no BIOS (F2) e escolha'
Write-Host '    "Curupira Instalador" no menu de boot (F10), ou no Windows em'
Write-Host '    Configuracoes > Sistema > Recuperacao > Inicializacao avancada > Usar um dispositivo.'
Write-Host '    Para desfazer tudo: .\preparar-instalador.ps1 -Desfazer'
