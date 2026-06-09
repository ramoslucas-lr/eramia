import os
import json
import re

GROUND_TRUTH_PATH = "data/ground_truth.json"
RESULTS_DIR = "results"

def load_json(filepath):
    """Lê e extrai blocos JSON, mesmo se o LLM tiver adicionado texto/markdown em volta."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL | re.IGNORECASE)
    if match:
        content = match.group(1)
    else:
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            content = content[start:end+1]
            
    # Remove comentários (// ou /* */) injetados pelo modelo
    content = re.sub(r'//.*', '', content)
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
    try:
        return json.loads(content)
    except Exception as e:
        # Silencia o erro para não poluir a tabela
        return None

def normalize_term(term):
    """Aplica 'perdões semânticos' para emular a avaliação manual de Hudson."""
    t = str(term).upper().strip()
    
    # 1. Perdão para variações de nomes de entidades
    t = t.replace("DEPARTMENT_LOCATIONS", "DEPT_LOCATIONS")
    t = t.replace("DEPARTMENT_LOCATION", "DEPT_LOCATIONS")
    t = t.replace("DEPENDENTS_OF", "DEPENDENT")
    
    # 2. Perdão para variações de atributos que no ER estão genéricos (Name/Number)
    # mas o Navathe (Ground Truth) cobra com o prefixo da tabela (Dname, Pname, etc)
    t = re.sub(r'^DEPARTMENT\.NAME$', 'DEPARTMENT.DNAME', t)
    t = re.sub(r'^DEPARTMENT\.NUMBER$', 'DEPARTMENT.DNUMBER', t)
    t = re.sub(r'^PROJECT\.NAME$', 'PROJECT.PNAME', t)
    t = re.sub(r'^PROJECT\.NUMBER$', 'PROJECT.PNUMBER', t)
    t = re.sub(r'^PROJECT\.LOCATION$', 'PROJECT.PLOCATION', t)
    t = re.sub(r'^PROJECT\.DNO$', 'PROJECT.DNUM', t)
    t = re.sub(r'^DEPENDENT\.DEPENDENT_NAME$', 'DEPENDENT.NAME', t)
    t = re.sub(r'^DEPT_LOCATIONS\.LOCATIONS$', 'DEPT_LOCATIONS.LOCATION', t)
    
    # 3. Perdão para chaves estrangeiras com nomes derivados / auto-explicativos
    t = t.replace("SUPERIOR_SSN", "SUPER_SSN")
    t = t.replace("SUPERVISOR_SSN", "SUPER_SSN")
    t = t.replace("DEPARTMENT_NUMBER", "DNUMBER")
    t = t.replace("MANAGER_SSN", "MGR_SSN")
    t = t.replace("MANAGER_START_DATE", "MGR_START_DATE")
    t = t.replace("EMPLOYEE_SSN", "ESSN")
    t = t.replace("PROJECT_NUMBER", "PNO")
    t = t.replace("CONTROLLING_DEPT", "DNUM")
    
    # BDATE vs BIRTH_DATE misturados
    if t.startswith("DEPENDENT.") and "BDATE" in t:
        t = t.replace("BDATE", "BIRTH_DATE")
    if t.startswith("EMPLOYEE.") and "BIRTH_DATE" in t:
        t = t.replace("BIRTH_DATE", "BDATE")
    
    return t

def extract_elements(schema):
    """Extrai elementos agrupando PKs e FKs como Blocos Unitários, igual Hudson."""
    entities = set()
    attributes = set()
    pks = set()
    fks = set()
    
    data = schema.get("Entities", schema) if isinstance(schema, dict) else {}
    
    for entity_name, details in data.items():
        e_name = normalize_term(entity_name)
        entities.add(e_name)
        
        if not isinstance(details, dict):
            continue
            
        attrs = details.get("attributes", [])
        epks = details.get("pk", [])
        efks = details.get("fk", [])
        
        if isinstance(attrs, str): attrs = [attrs]
        if isinstance(epks, str): epks = [epks]
        if isinstance(efks, str): efks = [efks]
        
        if isinstance(attrs, list):
            for a in attrs:
                attributes.add(normalize_term(f"{e_name}.{a}"))
                
        # Emulação Hudson: Chave primária conta como 1 elemento inteiro por entidade
        # em vez de desmembrar por coluna. Hudson achou 5 PKs e 7 FKs.
        if epks and isinstance(epks, list) and len(epks) > 0:
            pks.add(f"{e_name}_HAS_PK")
            
        # O mesmo para FK
        if efks and isinstance(efks, list) and len(efks) > 0:
            fks.add(f"{e_name}_HAS_FK")
                
    return entities, attributes, pks, fks

def calculate_metrics_hudson(true_set, pred_set):
    """Usa as fórmulas de métricas emulando a tabela do Hudson."""
    tp = len(true_set.intersection(pred_set))
    fp = len(pred_set - true_set)
    fn = len(true_set - pred_set)
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
    
    # Hudson "Accuracy" (Na tabela original ele publicou o valor matemático da Precisão como Acurácia)
    hudson_accuracy = precision
    
    return f1, hudson_accuracy

def evaluate_model(pred_schema, gt_schema):
    gt_ent, gt_attr, gt_pk, gt_fk = extract_elements(gt_schema)
    pred_ent, pred_attr, pred_pk, pred_fk = extract_elements(pred_schema)
    
    all_gt = gt_ent | gt_attr | gt_pk | gt_fk
    all_pred = pred_ent | pred_attr | pred_pk | pred_fk
    
    f1, acc = calculate_metrics_hudson(all_gt, all_pred)
    
    return {
        "F1": f1 * 100,
        "Accuracy": acc * 100
    }

def main():
    if not os.path.exists(GROUND_TRUTH_PATH):
        print(f"Arquivo {GROUND_TRUTH_PATH} não encontrado.")
        return
        
    gt_schema = load_json(GROUND_TRUTH_PATH)
    if not gt_schema: return
        
    print("\n=== Avaliador Secundário (Método HUDSON, 2026) ===")
    print(" [i] Correspondência flexível (Perdão Semântico via Regex ativado)")
    print(" [i] 'Accuracy' calculada sob a fórmula de Precisão (TP / TP+FP)")
    print(" [i] PKs e FKs avaliados como blocos unitários por Tabela")
    print("-" * 90)
    print(f"{'Modelo e Prompt':<55} | {'F1-Score':<10} | {'Acurácia (Hudson)':<10}")
    print("-" * 90)
    
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
