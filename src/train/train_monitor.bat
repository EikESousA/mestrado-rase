@echo off
set LOG_TREINO=train_output.log
set LOG_VRAM=vram_monitor.log

echo Iniciando treinamento LoRA... > %LOG_TREINO%
echo Iniciando monitor de VRAM... > %LOG_VRAM%

REM Inicia treino Python em background e redireciona saída
start /b python train_lora.py >> %LOG_TREINO% 2>&1

:monitor_loop
REM Pega VRAM usada e total via nvidia-smi
for /f "tokens=1,2 delims=," %%a in ('nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits') do (
    set USED=%%a
    set TOTAL=%%b
)

REM Calcula porcentagem (inteiro simples)
set /a PERC=(%USED% * 100) / %TOTAL%

echo %date% %time% - VRAM usada: %USED% MiB / %TOTAL% MiB (%PERC%%) >> %LOG_VRAM%

if %PERC% GEQ 90 (
    echo ⚠️ VRAM quase cheia! Considere diminuir batch size ou seq length. >> %LOG_VRAM%
) else if %PERC% LEQ 30 (
    echo 👍 VRAM disponível. Pode aumentar batch size para acelerar o treino. >> %LOG_VRAM%
) else (
    echo 🔄 Uso de VRAM dentro do esperado. >> %LOG_VRAM%
)

timeout /t 60 /nobreak > nul
goto monitor_loop
