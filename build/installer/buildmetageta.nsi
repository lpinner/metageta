
    ######################################################################
    #      NSIS Installation Script
    #
    #       This install script requires the following symbols to be
    #       defined via the /D commandline switch. It is usually run
    #       by the buildmetageta.py script:
    #
    #       EXCLUDE           Relative path to the MetaGETA code
    #       APP_DIR           Relative path to the MetaGETA code
    #       BIN_DIR           Relative path to the GDAL & Python directory
    #       VERSION           N.N.N.N format version number
    #       DISPLAY_VERSION   Version text string
    #       OUTPATH           Output installer filepath
    #
    #       Example:
    #       makensis /DVERSION=1.2.0.123 /DDISPLAY_VERSION=1.2 RC1 /DOUTPATH=..\downloads\metageta-1.2-setup.exe /DBIN_DIR=..\bin /DAPP_DIR=tmp buildmetageta.nsi
    #
    ######################################################################
    !define /date YEAR "%Y"

    !define APP_NAME "MetaGETA"
    !define COMP_NAME "Department of Environment"
    !define WEB_SITE "http://environment.gov.au"
    !define COPYRIGHT "${COMP_NAME} © ${YEAR}"
    !define DESCRIPTION "MetaGETA installer (Metadata Gathering, Extraction and Transformation Application)"
    !define LICENSE_TXT "licenses\license.rtf"
    !define MUI_WELCOMEFINISHPAGE_BITMAP "graphics\installer.bmp"
    !define REG_START_MENU "Start Menu Folder"
    !define MUI_ICON "graphics\metageta.ico"

    var /GLOBAL StartMenuFolder
    var /GLOBAL ConfigFile

    ######################################################################

    SetCompressor LZMA
    Name "${APP_NAME}"
    Caption "${APP_NAME}"
    OutFile "${OUTPATH}"
    BrandingText "${APP_NAME}"
    XPStyle on

    ######################################################################

    !define INSTALL_PATH "Software\${APP_NAME}"
    !define UNINSTALL_PATH "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    !define MULTIUSER_EXECUTIONLEVEL Highest
    !define MULTIUSER_MUI
    !define MULTIUSER_INSTALLMODE_COMMANDLINE
    !define MULTIUSER_INSTALLMODE_INSTDIR "${APP_NAME}"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_KEY "${UNINSTALL_PATH}"
    !define MULTIUSER_INSTALLMODE_DEFAULT_REGISTRY_VALUENAME "UninstallString"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_KEY "${INSTALL_PATH}"
    !define MULTIUSER_INSTALLMODE_INSTDIR_REGISTRY_VALUENAME "InstallLocation"
    !define REG_ROOT "SHCTX"

    !include "FileFunc.nsh"
    !include "MultiUser.nsh"
    !include "MUI.nsh"

    !define MUI_ABORTWARNING
    !define MUI_UNABORTWARNING

    !define MUI_STARTMENUPAGE_DEFAULTFOLDER "${APP_NAME}"
    !define MUI_STARTMENUPAGE_REGISTRY_ROOT "${REG_ROOT}"
    !define MUI_STARTMENUPAGE_REGISTRY_KEY "${UNINSTALL_PATH}"
    !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${REG_START_MENU}"
    ######################################################################

    !ifdef VERSION
        VIProductVersion  "${VERSION}"
        VIAddVersionKey "FileVersion"  "${VERSION}"
        VIAddVersionKey "ProductName"  "${APP_NAME}"
        VIAddVersionKey "CompanyName"  "${COMP_NAME}"
        VIAddVersionKey "LegalCopyright"  "${COPYRIGHT}"
        VIAddVersionKey "FileDescription"  "${DESCRIPTION}"
    !endif

    ######################################################################

    !insertmacro MUI_PAGE_WELCOME
    !insertmacro MUI_PAGE_LICENSE "${LICENSE_TXT}"
    !insertmacro MULTIUSER_PAGE_INSTALLMODE
    !insertmacro MUI_PAGE_DIRECTORY

    ; Optional components
    !define MUI_PAGE_CUSTOMFUNCTION_SHOW components_show
    !insertmacro MUI_PAGE_COMPONENTS
    !define MUI_PAGE_CUSTOMFUNCTION_PRE startmenu_pre
    !insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

    !define MUI_PAGE_CUSTOMFUNCTION_PRE UninstallPrevious
    !insertmacro MUI_PAGE_INSTFILES
    !define MUI_FINISHPAGE_NOAUTOCLOSE
    !define MUI_PAGE_CUSTOMFUNCTION_PRE ExistingConfig
    !insertmacro MUI_PAGE_FINISH
    !insertmacro MUI_UNPAGE_CONFIRM
    !insertmacro MUI_UNPAGE_INSTFILES
    !insertmacro MUI_UNPAGE_FINISH
    !insertmacro MUI_LANGUAGE "English"

    ######################################################################
    Section "MetaGETA Application" sec_main
        ;${INSTALL_TYPE}
        SetOverwrite ifnewer
        SetOutPath $INSTDIR
        File /r ${EXCLUDE} "${APP_DIR}\*"
        File "${MUI_ICON}"
        ${GetFileName} "${BIN_DIR}" $R0
        SetOutPath $INSTDIR\$R0
        File /r  ${EXCLUDE} "${BIN_DIR}\Python27"
        SetOutPath "$INSTDIR"
        WriteUninstaller "$INSTDIR\Uninstall.exe"
        WriteRegStr ${REG_ROOT} "${INSTALL_PATH}"  "InstallPath" "$INSTDIR"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayName" "${APP_NAME}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "UninstallString" "$INSTDIR\uninstall.exe"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayIcon" "$INSTDIR\${APP_NAME}\lib\wm_icon.ico"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "DisplayVersion" "${DISPLAY_VERSION}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "Publisher" "${COMP_NAME}"
        WriteRegStr ${REG_ROOT} "${UNINSTALL_PATH}"  "URLInfoAbout" "${WEB_SITE}"
    SectionEnd


    ######################################################################
    # Optional sections
    section "Explorer Integration" sec_shell
        WriteRegStr ${REG_ROOT} "Software\Classes\Folder\shell\metageta" "" "MetaGETA Crawler..."
        WriteRegStr ${REG_ROOT} "Software\Classes\Folder\shell\metageta\command" "" 'cmd.exe /s /c ""$INSTDIR\metageta\runcrawler.bat" -d "%1""'
        WriteRegStr ${REG_ROOT} "Software\Classes\Excel.Sheet.8\shell\metageta" "" "MetaGETA Transform..."
        WriteRegStr ${REG_ROOT} "Software\Classes\Excel.Sheet.8\shell\metageta\command" "" 'cmd.exe /s /c ""$INSTDIR\metageta\runtransform.bat" -x "%1""'
    sectionEnd
    
    Section "Start Menu shortcuts" sec_startmenu
        !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
            CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\Run Crawler (${DISPLAY_VERSION}).lnk" "$INSTDIR\metageta\runcrawler.bat" "" "$INSTDIR\metageta.ico" 0 SW_SHOWMINIMIZED
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\Run Transform (${DISPLAY_VERSION}).lnk" "$INSTDIR\metageta\runtransform.bat" "" "$INSTDIR\metageta.ico" 0 SW_SHOWMINIMIZED
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\MetaGETA Shell (${DISPLAY_VERSION}).lnk" "$INSTDIR\metageta\metageta-shell.bat" "" "$SYSDIR\cmd.exe" 0 SW_SHOWNORMAL
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\${APP_NAME} API Documentation (${DISPLAY_VERSION}).lnk" "$INSTDIR\${APP_NAME}\doc\index.html" "" "$SYSDIR\SHELL32.dll" 23 SW_SHOWMAXIMIZED
            CreateShortCut  "$SMPROGRAMS\$StartMenuFolder\Uninstall ${APP_NAME} (${DISPLAY_VERSION}).lnk" "$INSTDIR\uninstall.exe"
            WriteIniStr "$INSTDIR\${APP_NAME} website.url" "InternetShortcut" "URL" "${WEB_SITE}"
            CreateShortCut "$SMPROGRAMS\$StartMenuFolder\${APP_NAME} (${DISPLAY_VERSION}) Website.lnk" "$INSTDIR\${APP_NAME} website.url" "" "$SYSDIR\SHELL32.dll" 13 SW_SHOWMAXIMIZED
        !insertmacro MUI_STARTMENU_WRITE_END
    SectionEnd

    ######################################################################
    ;Section decriptions
    !insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
      !insertmacro MUI_DESCRIPTION_TEXT ${sec_shell} "Add MetaGETA functions to Windows Explorer folder and spreadsheet context menus"
      !insertmacro MUI_DESCRIPTION_TEXT ${sec_startmenu} "Add MetaGETA shortcuts to your Windows Start Menu"
    !insertmacro MUI_FUNCTION_DESCRIPTION_END

    ######################################################################

    Section Uninstall sec_uninstall
        RMDir /r "$INSTDIR"
        !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
        RMDir /r "$SMPROGRAMS\$StartMenuFolder"
        DeleteRegKey ${REG_ROOT} "${UNINSTALL_PATH}"
        DeleteRegKey ${REG_ROOT} "${INSTALL_PATH}"
        DeleteRegKey ${REG_ROOT} "Software\Classes\Folder\shell\metageta"
        DeleteRegKey ${REG_ROOT} "Software\Classes\Excel.Sheet.8\shell\metageta"
    SectionEnd

    ######################################################################

    ;Installer Functions
    Function .onInit
      !insertmacro MULTIUSER_INIT
    FunctionEnd

    ;Uninstaller Functions
    Function un.onInit
      !insertmacro MULTIUSER_UNINIT
    FunctionEnd

    Function UninstallPrevious
        ; Check for uninstaller.
        ReadRegStr $R0 ${REG_ROOT} "${UNINSTALL_PATH}" "UninstallString"
        ${If} $R0 != ""
            IfFileExists $INSTDIR\metageta\metageta\config.xml uninstallit_config uninstallit
            uninstallit_config:
                MessageBox MB_YESNO "An existing ${APP_NAME} has been detected and will be uninstalled.$\r$\nYour config.xml file will be backed up to $INSTDIR\metageta\metageta\config-previous.xml.$\r$\nDo you wish to continue?" IDYES +2
                    Quit
                DetailPrint "Removing previous installation and backing up config file."
                GetTempFileName $ConfigFile
                ;CreateDirectory $ConfigFile
                CopyFiles /SILENT $INSTDIR\metageta\metageta\config.xml $ConfigFile
                Goto rununinstaller
                
            uninstallit:
                MessageBox MB_YESNO "An existing ${APP_NAME} has been detected and will be uninstalled.$\r$\nDo you wish to continue?" IDYES +2
                    Quit
                DetailPrint "Removing previous installation."
                Goto rununinstaller
                
            rununinstaller:
                ; Run the uninstaller silently.
                ExecWait '"$R0" /S _?=$INSTDIR'
        ${EndIf}
    FunctionEnd

    Function ExistingConfig
        ${If} $ConfigFile != ""
                CopyFiles /SILENT $ConfigFile $INSTDIR\metageta\metageta\config-previous.xml
                Delete $ConfigFile
        ${EndIf}
    FunctionEnd

    Function components_show
        SectionSetFlags ${sec_main} 17 ;SF_SELECTED+SF_RO
    FunctionEnd
    
    Function startmenu_pre
        ${Unless} ${SectionIsSelected} ${sec_startmenu}
          Abort
        ${EndUnless}
    FunctionEnd
