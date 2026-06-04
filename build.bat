@echo off
echo ============================================
echo     Orbitask — Gerando executavel .exe
echo ============================================
echo.

echo [1/3] Limpando builds anteriores...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
echo OK

echo.
echo [2/3] Empacotando com PyInstaller...
pyinstaller orbitask.spec --noconfirm

echo.
echo [3/3] Verificando resultado...
if exist dist\Orbitask.exe (
    echo.
    echo ============================================
    echo  Executavel gerado com sucesso!
    echo  Local: dist\Orbitask.exe
    echo ============================================
    explorer dist
) else (
    echo ERRO: O executavel nao foi gerado.
    echo Verifique os erros acima.
)

pause