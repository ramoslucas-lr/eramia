import os
import base64
import json
import time
import argparse
import replicate
from openai import OpenAI
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# =====================
# CONFIGURAÇÃO DE MODELOS E APIs
# =====================

# Modelos via OpenRouter
OPENROUTER_MODELS = [
    "qwen/qwen3-vl-235b-a22b-instruct", # SOTA Oriental
    "meta-llama/llama-3.2-11b-vision-instruct", # SOTA Ocidental
    "mistralai/ministral-14b-2512", # Eficiência
    "mistralai/mistral-large-2512",
    "google/gemini-3.5-flash",
    "anthropic/claude-opus-4.8",
    "anthropic/claude-opus-4.1",
    "openai/gpt-5.5",
    "openai/gpt-4o",
    "google/gemini-2.5-flash"
]

# Modelos via Replicate
REPLICATE_MODELS = [
    # LLaVA v1.6 34B
    "yorickvp/llava-v1.6-vicuna-13b:0603dec596080fa084e26f0ae6d605fc5788ed2b1a0358cd25010619487eae63" 
    # "yorickvp/llava-v1.6-34b"
]

IMAGE_PATH = "data/ERD.png"
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
    "}\n\n"
    "INSTRUÇÃO CRÍTICA: A sua resposta DEVE ser APENAS um objeto JSON válido e nada mais. O PRIMEIRO caractere da sua resposta deve ser '{' e o ÚLTIMO caractere deve ser '}'. Certifique-se de fechar TODAS as chaves do objeto principal no final. É ESTRITAMENTE PROIBIDO usar formatação markdown (como ```json), apresentar raciocínio passo a passo (Chain of Thought), adicionar texto explicativo ou incluir comentários (como // ou /*) dentro do JSON."
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
    "}\n\n"
    "INSTRUÇÃO CRÍTICA: A sua resposta DEVE ser APENAS um objeto JSON válido e nada mais. O PRIMEIRO caractere da sua resposta deve ser '{' e o ÚLTIMO caractere deve ser '}'. É ESTRITAMENTE PROIBIDO usar formatação markdown (como ```json) ou adicionar texto explicativo."
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
                "content": "Você é um assistente especialista em banco de dados relacionais e transformação de diagramas ER para modelo lógico. Você NÃO PODE explicar seu raciocínio. Sua única saída deve ser um objeto JSON."
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
        max_tokens=4000
    )
    
    return response.choices[0].message.content

def infer_replicate(model_name, prompt_text, image_path):
    
    if not os.getenv("REPLICATE_API_TOKEN"):
        raise ValueError("Variável REPLICATE_API_TOKEN não encontrada.")
    
    input_data = {
        "image": open(image_path, "rb"),
        "prompt": prompt_text,
        "temperature": 0, 
        "max_tokens": 4000
    }
    
    output = replicate.run(model_name, input=input_data)
    # Replicate retorna um gerador de strings (stream), então juntamos tudo.
    return "".join(output)

# =====================
# PIPELINE PRINCIPAL
# =====================

def clean_json_output(content):
    import re
    # Primeiro tenta extrair blocos markdown
    match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1)
    
    # Fallback: Extrai o que está entre as chaves principais
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1:
        content = content[start:end+1]
        
    # Remove comentários (// ou /* */) injetados pelo modelo, pois invalidam o JSON nativo do Python
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
    return content

def save_result(model_name, prompt_name, content):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    safe_model_name = model_name.split("/")[-1].replace(":", "_")
    filename = f"{safe_model_name}_{prompt_name}.json"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Higienização forte antes de salvar no disco
    clean_content = clean_json_output(content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean_content)
        
    print(f"[OK] Resultado salvo: {filepath}")

def main():
    parser = argparse.ArgumentParser(description="Benchmark ER Extraction")
    parser.add_argument("--dry-run", action="store_true", help="Executa o pipeline simulando as chamadas de API")
    parser.add_argument("--skip-openrouter", action="store_true", help="Pula a execução dos modelos do OpenRouter")
    parser.add_argument("--skip-replicate", action="store_true", help="Pula a execução dos modelos do Replicate")
    parser.add_argument("--model", type=str, help="Executa apenas o modelo que contenha este texto (ex: 'qwen', 'llama')")
    args = parser.parse_args()

    if not os.path.exists(IMAGE_PATH):
        print(f"[ERRO] Imagem {IMAGE_PATH} não encontrada.")
        return

    dry_run_msg = " (DRY RUN ATIVADO)" if args.dry_run else ""
    print(f"=== Iniciando Benchmark de Extração ER ({IMAGE_PATH}){dry_run_msg} ===")
    
    image_b64 = carregar_imagem_base64(IMAGE_PATH)
    
    # 1. Executando Modelos via OpenRouter
    if not args.skip_openrouter:
        for model in OPENROUTER_MODELS:
            if args.model and args.model.lower() not in model.lower():
                continue
            for prompt_name, prompt_text in PROMPTS.items():
                print(f"\n-> Processando [OpenRouter] Modelo: {model} | Prompt: {prompt_name}")
                try:
                    if args.dry_run:
                        print("   [DRY RUN] Simulando inferência (API não chamada).")
                        resultado = '{\n  "Entities": {\n    "DRY_RUN_MOCK": {\n      "attributes": ["mock_attr"],\n      "pk": ["mock_attr"]\n    }\n  }\n}'
                    else:
                        resultado = infer_openrouter(model, prompt_text, image_b64)
                    
                    save_result(model, prompt_name, resultado)
                    
                    if not args.dry_run:
                        time.sleep(2) # Pausa pequena entre requests apenas se não for dry run
                except Exception as e:
                    print(f"[ERRO] Falha no OpenRouter ({model}): {e}")
    else:
        print("\n[INFO] Pulando execução via OpenRouter (--skip-openrouter).")

    # 2. Executando Modelos via Replicate
    if not args.skip_replicate:
        for model in REPLICATE_MODELS:
            if args.model and args.model.lower() not in model.lower():
                continue
            for prompt_name, prompt_text in PROMPTS.items():
                print(f"\n-> Processando [Replicate] Modelo: {model} | Prompt: {prompt_name}")
                try:
                    if args.dry_run:
                        print("   [DRY RUN] Simulando inferência (API não chamada).")
                        resultado = '{\n  "Entities": {\n    "DRY_RUN_MOCK": {\n      "attributes": ["mock_attr"],\n      "pk": ["mock_attr"]\n    }\n  }\n}'
                    else:
                        resultado = infer_replicate(model, prompt_text, IMAGE_PATH)
                    
                    save_result(model, prompt_name, resultado)
                    
                    if not args.dry_run:
                        time.sleep(2)
                except Exception as e:
                    print(f"[ERRO] Falha no Replicate ({model}): {e}")
    else:
        print("\n[INFO] Pulando execução via Replicate (--skip-replicate).")
                
    print("\n=== Benchmark Concluído! ===")

if __name__ == "__main__":
    main()
