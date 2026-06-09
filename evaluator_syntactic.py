import os
import json
import re

GROUND_TRUTH_PATH = "data/ground_truth.json"
RESULTS_DIR = "results"

def load_json(filepath):
    """Lê e extrai blocos JSON, mesmo se o LLM tiver adicionado texto/markdown em volta."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extrai o json se estiver em blocos markdown ```json ... ```
    match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1)
    else:
        # Busca a primeira e última chaves caso seja apenas texto solto
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
            
    try:
        return json.loads(content)
    except Exception as e:
        print(f"[ERRO] Falha ao parsear JSON em {filepath}: {e}")
        return None

def extract_elements(schema):
    """Plana a estrutura JSON em conjuntos (sets) matemáticos para avaliação rigorosa."""
    entities = set()
    attributes = set()
    pks = set()
    fks = set()
    
    data = schema.get("Entities", schema) if isinstance(schema, dict) else {}
    
    for entity_name, details in data.items():
        e_name = str(entity_name).upper().strip()
        entities.add(e_name)
        
        if not isinstance(details, dict):
            continue
            
        attrs = details.get("attributes", [])
        epks = details.get("pk", [])
        efks = details.get("fk", [])
        
        # Converte para lista caso o LLM retorne uma string solta (ex: "pk": "Ssn")
        if isinstance(attrs, str): attrs = [attrs]
        if isinstance(epks, str): epks = [epks]
        if isinstance(efks, str): efks = [efks]
        
        if isinstance(attrs, list):
            for a in attrs:
                attributes.add(f"{e_name}.{str(a).upper().strip()}")
                
        if isinstance(epks, list):
            for a in epks:
                pks.add(f"{e_name}.{str(a).upper().strip()}")
                
        if isinstance(efks, list):
            for a in efks:
                fks.add(f"{e_name}.{str(a).upper().strip()}")
                
    return entities, attributes, pks, fks

def calculate_metrics(true_set, pred_set):
    """Calcula True Positives, False Positives e False Negatives para gerar as métricas."""
    tp = len(true_set.intersection(pred_set))
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    accuracy = tp / (tp + fp + fn) if (tp + fp + fn) > 0 else 0.0 # Intersection Over Union (Jaccard)
    
    return f1, accuracy

def evaluate_model(pred_schema, gt_schema):
    gt_ent, gt_attr, gt_pk, gt_fk = extract_elements(gt_schema)
    pred_ent, pred_attr, pred_pk, pred_fk = extract_elements(pred_schema)
    
    # Unifica todos os construtos (Entidades, Attrs, PKs, FKs) para as métricas Globais
    all_gt = gt_ent | gt_attr | gt_pk | gt_fk
    all_pred = pred_ent | pred_attr | pred_pk | pred_fk
    
    f1, acc = calculate_metrics(all_gt, all_pred)
    
    # Pode-se calcular as precisões individuais caso se queira fazer o breakdown do erro
    ent_f1, ent_acc = calculate_metrics(gt_ent, pred_ent)
    
    return {
        "F1": f1 * 100,
        "Accuracy": acc * 100,
        "Entities_Acc": ent_acc * 100
    }

def main():
    if not os.path.exists(GROUND_TRUTH_PATH):
        print(f"Arquivo {GROUND_TRUTH_PATH} não encontrado.")
        return
        
    gt_schema = load_json(GROUND_TRUTH_PATH)
    if not gt_schema:
        return
        
    if not os.path.exists(RESULTS_DIR):
        print(f"Diretório {RESULTS_DIR} não encontrado. Execute o benchmark_er.py primeiro.")
        return
        
    print("\n=== Resultados da Avaliação Comparativa ===")
    print(f"{'Modelo e Prompt':<55} | {'F1-Score':<10} | {'Acurácia':<10}")
    print("-" * 83)
    
    for filename in sorted(os.listdir(RESULTS_DIR)):
        if filename.endswith(".json"):
            filepath = os.path.join(RESULTS_DIR, filename)
            pred_schema = load_json(filepath)
            
            if pred_schema:
                metrics = evaluate_model(pred_schema, gt_schema)
                name = filename.replace(".json", "")
                print(f"{name:<55} | {metrics['F1']:<8.2f}% | {metrics['Accuracy']:<8.2f}%")

if __name__ == "__main__":
    main()
