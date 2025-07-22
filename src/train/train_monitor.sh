#!/bin/bash

LOG_TREINO="train_output.log"
LOG_VRAM="vram_monitor.log"

echo "Iniciando treinamento LoRA..." | tee $LOG_TREINO $LOG_VRAM

# Executa o treino em background e salva saída em train_output.log
python train_lora.py > $LOG_TREINO 2>&1 &

PID_TREINO=$!

echo "Treinamento rodando com PID $PID_TREINO"

# Função para monitorar VRAM com nvidia-smi e dar dicas, salvando no log
while kill -0 $PID_TREINO 2> /dev/null; do
    USADA=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
    TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)
    PERC=$(( USADA * 100 / TOTAL ))

    echo "$(date '+%Y-%m-%d %H:%M:%S') - VRAM usada: ${USADA}MiB / ${TOTAL}MiB (${PERC}%)" | tee -a $LOG_VRAM

    if [ $PERC -gt 90 ]; then
        echo "⚠️ VRAM quase cheia! Considere diminuir o batch size ou seq length." | tee -a $LOG_VRAM
    elif [ $PERC -lt 30 ]; then
        echo "👍 VRAM disponível. Pode aumentar o batch size para acelerar o treino." | tee -a $LOG_VRAM
    else
        echo "🔄 Uso de VRAM dentro do esperado." | tee -a $LOG_VRAM
    fi

    sleep 60  # checa a cada 60 segundos
done

echo "Treinamento finalizado, monitor de VRAM encerrado." | tee -a $LOG_VRAM
