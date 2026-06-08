import os
import base64
import json
import time
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# =====================
# CONFIGURAÇÃO DE MODELOS E APIs
# =====================

# Modelos via OpenRouter
OPENROUTER_MODELS = [
    "qwen/qwen-3-vl-235b", # SOTA Oriental
    "meta-llama/llama-3.2-11b-vision-instruct", # SOTA Ocidental
    "mistralai/ministral-14b-2512" # Eficiência
]

# Modelos via Replicate
REPLICATE_MODELS = [
    # LLaVA v1.6 34B
    "yorickvp/llava-v1.6-34b:41ecfbfb36d247cd4926f50b44128532f8115eb5b23d537f5b8429ab78709f19" 
]

IMAGE_PATH = "ERD (1).png"
OUTPUT_DIR = "results"

# =====================
# DEFINIÇÃO DOS PROMPTS
# =====================

PROMPT_1 = (
    "Analise a imagem contendo um Diagrama Entidade-Relacionamento (ER) e converta-a para um esquema lógico relacional em formato JSON estruturado.\n\n"
    "Instruções:\n"
    "Para cada entidade, gere uma entrada com:\n\n"
    "- \"attributes\": lista com todos os atributos da tabela\n"
    "- \"pk\": chave primária como lista (mesmo que contenha apenas um atributo)\n"
    "- \"fk\": lista de chaves estrangeiras (se existirem)\n\n"
    "Caso não existam chaves estrangeiras, omita o campo \"fk\".\n"
    "Use nomes significativos, mantendo consistência com o diagrama original.\n\n"
    "O modelo de saída deve seguir rigorosamente o seguinte formato:\n"
    "{\n"
    "  \"Entities\": {\n"
    "    \"EntityName\": {\n"
    "      \"attributes\": [\"x\", \"y\", \"z\"],\n"
    "      \"pk\": [\"a\"],\n"
    "      \"fk\": [\"b\", \"c\"]\n"
    "    },\n"
    "    \"AnotherEntity\": {\n"
    "      \"attributes\": [\"m\", \"n\"],\n"
    "      \"pk\": [\"m\"]\n"
    "    }\n"
    "  }\n"
    "}"
)

PROMPT_2 = (
    "Analise a imagem contendo um Diagrama Entidade-Relacionamento (ER) e converta-a para um esquema lógico relacional em formato JSON estruturado.\n\n"
    "Instruções:\n"
    "Para cada entidade ou relacionamento, gere uma entrada com:\n\n"
    "- \"attributes\": lista com todos os atributos da tabela\n"
    "- \"pk\": chave primária como lista (mesmo que contenha apenas um atributo)\n"
    "- \"fk\": lista de chaves estrangeiras (se existirem)\n\n"
    "Caso não existam chaves estrangeiras, omita o campo \"fk\".\n"
    "Use nomes significativos, mantendo consistência com o diagrama original.\n\n"
    "Utilize as regras abaixo para decisão por tabela própria, adição de coluna ou fusão de tabelas:\n\n"
    "Relacionamentos 1:1\n"
    "1. (0,1) — (0,1)\n"
    "Tabela própria: ± (pode ser usada)\n"
    "Adição de coluna: ✔ (preferida)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "2. (0,1) — (1,1)\n"
    "Tabela própria: ✘ (não usar)\n"
    "Adição de coluna: ± (pode ser usada)\n"
    "Fusão de tabelas: ✔ (preferida)\n\n"
    "3. (1,1) — (1,1)\n"
    "Tabela própria: ✘ (não usar)\n"
    "Adição de coluna: ± (pode ser usada)\n"
    "Fusão de tabelas: ✔ (preferida)\n\n"
    "Relacionamentos 1:n\n"
    "1. (0,1) — (0,n)\n"
    "Tabela própria: ± (pode ser usada)\n"
    "Adição de coluna: ✔ (preferida)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "2. (0,1) — (1,n)\n"
    "Tabela própria: ± (pode ser usada)\n"
    "Adição de coluna: ✔ (preferida)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "3. (1,1) — (0,n)\n"
    "Tabela própria: ✘ (não usar)\n"
    "Adição de coluna: ✔ (preferida)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "4. (1,1) — (1,n)\n"
    "Tabela própria: ✘ (não usar)\n"
    "Adição de coluna: ✔ (preferida)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "Relacionamentos n:n\n"
    "1. (0,n) — (0,n)\n"
    "Tabela própria: ✔ (preferida)\n"
    "Adição de coluna: ✘ (não usar)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "2. (0,n) — (1,n)\n"
    "Tabela própria: ✔ (preferida)\n"
    "Adição de coluna: ✘ (não usar)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "3. (1,n) — (1,n)\n"
    "Tabela própria: ✔ (preferida)\n"
    "Adição de coluna: ✘ (não usar)\n"
    "Fusão de tabelas: ✘ (não usar)\n\n"
    "O modelo de saída deve seguir rigorosamente o seguinte formato:\n"
    "{\n"
    "  \"Entities\": {\n"
    "    \"EntityName\": {\n"
    "      \"attributes\": [\"x\", \"y\", \"z\"],\n"
    "      \"pk\": [\"a\"],\n"
    "      \"fk\": [\"b\", \"c\"]\n"
    "    },\n"
    "    \"AnotherEntity\": {\n"
    "      \"attributes\": [\"m\", \"n\"],\n"
    "      \"pk\": [\"m\"]\n"
    "    }\n"
    "  }\n"
    "}"
)

PROMPTS = {
    "prompt_1": PROMPT_1,
    "prompt_2": PROMPT_2
}

# =====================
# FUNÇÕES DE INFERÊNCIA
# =====================

def carregar_imagem_base64(caminho):
    with open(caminho, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def infer_openrouter(model_name, prompt_text, image_b64):
    from openai import OpenAI
    
    api_key = os.getenv("OPEN_ROUTER_TOKEN")
    if not api_key:
        raise ValueError("Variável OPEN_ROUTER_TOKEN não encontrada.")
        
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "Você é um assistente especialista em banco de dados relacionais e transformação de diagramas ER para modelo lógico."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt_text
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_b64}"
                        }
                    }
                ]
            }
        ],
        temperature=0,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def infer_replicate(model_name, prompt_text, image_path):
    import replicate
    
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise ValueError("Variável REPLICATE_API_TOKEN não encontrada.")
    
    input_data = {
        "image": open(image_path, "rb"),
        "prompt": prompt_text
    }
    
    output = replicate.run(model_name, input=input_data)
    # Replicate retorna um gerador de strings (stream), então juntamos tudo.
    return "".join(output)

# =====================
# PIPELINE PRINCIPAL
# =====================

def save_result(model_name, prompt_name, content):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    safe_model_name = model_name.split("/")[-1].replace(":", "_")
    filename = f"{safe_model_name}_{prompt_name}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Adicionamos a tag markdown para o JSON ou salvamos o texto raw caso o LLM não resgate perfeitamente formatado.
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[OK] Resultado salvo: {filepath}")

def main():
    if not os.path.exists(IMAGE_PATH):
        print(f"[ERRO] Imagem {IMAGE_PATH} não encontrada.")
        return

    print(f"=== Iniciando Benchmark de Extração ER ({IMAGE_PATH}) ===")
    
    image_b64 = carregar_imagem_base64(IMAGE_PATH)
    
    # 1. Executando Modelos via OpenRouter
    for model in OPENROUTER_MODELS:
        for prompt_name, prompt_text in PROMPTS.items():
            print(f"\n-> Processando [OpenRouter] Modelo: {model} | Prompt: {prompt_name}")
            try:
                resultado = infer_openrouter(model, prompt_text, image_b64)
                save_result(model, prompt_name, resultado)
                time.sleep(2) # Pausa pequena entre requests
            except Exception as e:
                print(f"[ERRO] Falha no OpenRouter ({model}): {e}")

    # 2. Executando Modelos via Replicate
    for model in REPLICATE_MODELS:
        for prompt_name, prompt_text in PROMPTS.items():
            print(f"\n-> Processando [Replicate] Modelo: {model} | Prompt: {prompt_name}")
            try:
                resultado = infer_replicate(model, prompt_text, IMAGE_PATH)
                save_result(model, prompt_name, resultado)
                time.sleep(2)
            except Exception as e:
                print(f"[ERRO] Falha no Replicate ({model}): {e}")
                
    print("\n=== Benchmark Concluído! ===")

if __name__ == "__main__":
    main()
