import torch
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    Trainer,
    TrainingArguments,
    DataCollatorForLanguageModeling,
    BitsAndBytesConfig
)
from datasets import load_dataset
import sys

def get_gpu_name():
    if torch.cuda.is_available():
        return torch.cuda.get_device_name(0).lower()
    return None

def get_train_config(gpu_name, model_choice):
    if model_choice == "gpt":
        return {
            "batch_size": 8,
            "gradient_accumulation_steps": 2,
            "max_steps": 300,
            "learning_rate": 2e-4,
            "fp16": False,
            "device_map": None
        }

    if gpu_name is None:
        return {
            "batch_size": 1,
            "gradient_accumulation_steps": 16,
            "max_steps": 100,
            "learning_rate": 2e-4,
            "fp16": False,
            "device_map": None
        }
    elif "4080" in gpu_name:
        return {
            "batch_size": 4,
            "gradient_accumulation_steps": 4,
            "max_steps": 400,
            "learning_rate": 2e-4,
            "fp16": True,
            "device_map": "auto"
        }
    elif "4070" in gpu_name:
        return {
            "batch_size": 2,
            "gradient_accumulation_steps": 4,
            "max_steps": 300,
            "learning_rate": 2e-4,
            "fp16": True,
            "device_map": "auto"
        }
    elif "3060" in gpu_name:
        return {
            "batch_size": 1,
            "gradient_accumulation_steps": 8,
            "max_steps": 200,
            "learning_rate": 2e-4,
            "fp16": True,
            "device_map": "auto"
        }
    else:
        return {
            "batch_size": 1,
            "gradient_accumulation_steps": 8,
            "max_steps": 150,
            "learning_rate": 2e-4,
            "fp16": True,
            "device_map": "auto"
        }

def main():
    model_choice = "mistral"
    if len(sys.argv) > 1:
        model_choice = sys.argv[1].lower()

    if model_choice == "mistral":
        model_id = "mistralai/Mistral-7B-Instruct-v0.2"
    elif model_choice == "tinyllama":
        model_id = "TheBloke/tinyllama-3B-HF"
    elif model_choice == "gpt":
        model_id = "EleutherAI/gpt-neo-125M"
    else:
        print(f"Modelo {model_choice} não suportado. Use 'mistral', 'tinyllama' ou 'gpt'.")
        return

    gpu_name = get_gpu_name()
    if gpu_name:
        print(f"GPU detectada: {gpu_name}")
    else:
        print("GPU não detectada, rodando em CPU (muito lento para modelos grandes).")

    cfg = get_train_config(gpu_name, model_choice)

    print(f"Configurações de treino:\n"
          f"Batch size: {cfg['batch_size']}\n"
          f"Gradient Accumulation Steps: {cfg['gradient_accumulation_steps']}\n"
          f"Max Steps: {cfg['max_steps']}\n"
          f"FP16: {cfg['fp16']}\n"
          f"Device map: {cfg['device_map']}")

    bnb_config = None
    if gpu_name and cfg["device_map"] == "auto" and model_choice != "gpt":
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

    print("\nCarregando tokenizer e modelo...")
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=True)

    model_kwargs = {}
    if bnb_config:
        model_kwargs["quantization_config"] = bnb_config
    if cfg["device_map"]:
        model_kwargs["device_map"] = cfg["device_map"]

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        **model_kwargs
    )

    print("Aplicando LoRA...")
    config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(model, config)
    model.print_trainable_parameters()

    print("Carregando datasets...")
    dataset_pira = load_dataset("json", data_files="data/pira.jsonl")["train"]
    dataset_squad = load_dataset("json", data_files="data/squad_br.jsonl")["train"]

    dataset = dataset_pira.concatenate(dataset_squad).shuffle(seed=42).select(range(2000))

    def format_sample(e):
        return {
            "text": f"### Instrução:\n{e['instruction']}\n\n### Contexto:\n{e['input']}\n\n### Resposta:\n{e['output']}"
        }

    dataset = dataset.map(format_sample)

    training_args = TrainingArguments(
        output_dir="lora_out",
        per_device_train_batch_size=cfg["batch_size"],
        gradient_accumulation_steps=cfg["gradient_accumulation_steps"],
        max_steps=cfg["max_steps"],
        learning_rate=cfg["learning_rate"],
        fp16=cfg["fp16"],
        logging_steps=10,
        save_steps=100,
        save_total_limit=1,
        report_to=[]
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False)
    )

    print("Iniciando treino...")
    trainer.train()
    model.save_pretrained("lora_out")
    print("Treinamento finalizado e modelo salvo em lora_out/")

if __name__ == "__main__":
    main()
