from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

model_choice = "gpt"  # ou "mistral" ou "tinyllama"
adapter_path = "lora_out"

if model_choice == "mistral":
    model_id = "mistralai/Mistral-7B-Instruct-v0.2"
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="bfloat16"
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )
elif model_choice == "tinyllama":
    model_id = "TheBloke/tinyllama-3B-HF"
    from transformers import BitsAndBytesConfig
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype="bfloat16"
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map="auto"
    )
elif model_choice == "gpt":
    model_id = "EleutherAI/gpt-neo-125M"
    base_model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="cpu"  # ou None
    )
else:
    raise ValueError(f"Modelo {model_choice} não suportado.")

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = PeftModel.from_pretrained(base_model, adapter_path)
model.eval()

prompt = """
### Instrução:
Qual a multa prevista?

### Contexto:
A cláusula 9 do contrato estabelece multa de 15% por rescisão.

### Resposta:
"""

inputs = tokenizer(prompt, return_tensors="pt")

if torch.cuda.is_available() and model_choice != "gpt":
    inputs = inputs.to("cuda")
    model = model.to("cuda")
else:
    model = model.to("cpu")

outputs = model.generate(**inputs, max_new_tokens=100, temperature=0.7)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
