[Setup]
AppName=AI Multimedia Enhancer
AppVersion=1.0.0
DefaultDirName={autopf}\AI Multimedia Enhancer
DefaultGroupName=AI Multimedia Enhancer
UninstallDisplayIcon={app}\AI-Multimedia-Enhancer.exe
Compression=lzma2
SolidCompression=yes
OutputDir=installer_dist
OutputBaseFilename=AI-Multimedia-Enhancer-Installer

[Files]
Source: "dist\AI-Multimedia-Enhancer\*"; DestDir: "{app}"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\AI Multimedia Enhancer"; Filename: "{app}\AI-Multimedia-Enhancer.exe"
Name: "{autodesktop}\AI Multimedia Enhancer"; Filename: "{app}\AI-Multimedia-Enhancer.exe"
