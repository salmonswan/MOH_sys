[Setup]
AppName=MOH Intern Placement System
AppVersion=1.0
AppPublisher=Ministry of Health Uganda
DefaultDirName={autopf}\MOH Intern Placement
DefaultGroupName=MOH Intern Placement
OutputBaseFilename=MOH_Intern_Placement_Setup
OutputDir=installer_output
Compression=lzma
SolidCompression=yes
SetupIconFile=
PrivilegesRequired=lowest
UninstallDisplayName=MOH Intern Placement System

[Files]
Source: "dist\MOH_Intern_Placement.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\MOH Intern Placement"; Filename: "{app}\MOH_Intern_Placement.exe"
Name: "{group}\Uninstall MOH Intern Placement"; Filename: "{uninstallexe}"
Name: "{commondesktop}\MOH Intern Placement"; Filename: "{app}\MOH_Intern_Placement.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional icons:"

[Run]
Filename: "{app}\MOH_Intern_Placement.exe"; Description: "Launch MOH Intern Placement"; Flags: nowait postinstall skipifsilent
