; NSIS Installer Script - Sinav Hazirlama Sistemi v4
Unicode True

!define APP_NAME "Sinav Hazirlama Sistemi"
!define APP_VERSION "4.0"
!define APP_PUBLISHER "DB"
!define APP_EXE "SinavHazirlamaSistemi.exe"
!define INSTALL_DIR "$PROGRAMFILES64\SinavHazirlamaSistemi"
!define REG_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\SinavHazirlamaSistemi"

!include "MUI2.nsh"
!include "LogicLib.nsh"

Name "${APP_NAME}"
OutFile "SinavHazirlamaSistemi_Kurulum.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "${REG_KEY}" "InstallLocation"
RequestExecutionLevel admin
ShowInstDetails show

; Ikonlar
!define MUI_ICON "logo.ico"
!define MUI_UNICON "logo.ico"

; Sayfa baslik ve aciklamalari
!define MUI_WELCOMEPAGE_TITLE "Sinav Hazirlama Sistemi Kurulumu"
!define MUI_WELCOMEPAGE_TEXT "Bu sihirbaz Sinav Hazirlama Sistemi'ni bilgisayariniza kuracaktir.$\r$\n$\r$\nKuruluma baslamak icin Ileri dugmesine tiklayin."

!define MUI_LICENSEPAGE_CHECKBOX
!define MUI_LICENSEPAGE_CHECKBOX_TEXT "Kullanim kosullarini okudum ve kabul ediyorum (Ticari kullanim yasaktir)"
!define MUI_LICENSEPAGE_BUTTON "Kabul Ediyorum"

!define MUI_DIRECTORYPAGE_TEXT_TOP "Sinav Hazirlama Sistemi asagidaki klasore kurulacaktir. Degistirmek icin Goz At'a tiklayin."

!define MUI_INSTFILESPAGE_HEADER_TEXT "Kuruluyor..."
!define MUI_INSTFILESPAGE_HEADER_SUBTEXT "Lutfen bekleyin."

!define MUI_FINISHPAGE_TITLE "Kurulum Tamamlandi"
!define MUI_FINISHPAGE_TEXT "Sinav Hazirlama Sistemi basariyla kuruldu.$\r$\n$\r$\nMasaustundeki kisayolu kullanarak uygulamayi acabilirsiniz."
!define MUI_FINISHPAGE_RUN "$INSTDIR\${APP_EXE}"
!define MUI_FINISHPAGE_RUN_TEXT "Sinav Hazirlama Sistemi'ni su an ac"

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

!insertmacro MUI_LANGUAGE "Turkish"

; Ana kurulum bolumu
Section "Ana Program" SEC_MAIN
    SectionIn RO

    SetOutPath "$INSTDIR"

    ; Uygulama dosyalari
    File /r "dist\SinavHazirlamaSistemi\*.*"

    ; Ikon dosyasini da kopyala (kisayol icin)
    File "logo.ico"

    ; sinav.db artık AppData/Local/SinavHazirlamaSistemi/ altında otomatik oluşur
    ; İlk açılışta uygulama kendi oluşturur — installer müdahale etmez

    ; Registry
    WriteRegStr HKLM "${REG_KEY}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "${REG_KEY}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "${REG_KEY}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "${REG_KEY}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "${REG_KEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
    WriteRegStr HKLM "${REG_KEY}" "DisplayIcon" "$INSTDIR\logo.ico"
    WriteRegDWORD HKLM "${REG_KEY}" "NoModify" 1
    WriteRegDWORD HKLM "${REG_KEY}" "NoRepair" 1

    WriteUninstaller "$INSTDIR\Uninstall.exe"

    ; Masaustu kisayolu - ikon olarak logo.ico kullan
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_EXE}" "" \
        "$INSTDIR\logo.ico" 0 \
        SW_SHOWNORMAL "" "${APP_NAME}"

    ; Baslat menusu
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" \
        "$INSTDIR\${APP_EXE}" "" \
        "$INSTDIR\logo.ico" 0 \
        SW_SHOWNORMAL "" "${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\Kaldir.lnk" \
        "$INSTDIR\Uninstall.exe"

SectionEnd

; Kaldirma bolumu
Section "Uninstall"
    RMDir /r "$INSTDIR"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    RMDir /r "$SMPROGRAMS\${APP_NAME}"
    DeleteRegKey HKLM "${REG_KEY}"
SectionEnd
