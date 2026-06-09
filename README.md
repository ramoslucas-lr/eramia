# ER-to-Logical Schema VLM Benchmark

Este repositório contém o código, os dados e a documentação para a avaliação em larga escala de Vision-Language Models (VLMs) na tarefa de conversão de Diagramas Entidade-Relacionamento (ER) para Esquemas Lógicos Relacionais estruturados em JSON.

Este trabalho é uma extensão sistemática da literatura de base (Silva et al., 2026), expandindo a análise multimodal para englobar as mais recentes arquiteturas de fundação *open-weights* (Qwen, Llama, Mistral) e contrastando-as rigorosamente com *baselines* proprietários corporativos (GPT, Claude, Gemini).

## 📄 Artigo Científico e Resultados
A análise acadêmica aprofundada, contemplando a "Saturação de Contexto", tabelas de custos em nuvem e a divergência entre a validação sintática e semântica, está documentada no nosso artigo oficial:
* [Avaliação Sintática vs Semântica em VLMs](docs/Avaliacao_Sintatica_vs_Semantica_em_VLMs.md)

## 📁 Estrutura do Repositório

* `benchmark_er.py`: Script principal de inferência unificada. Orquestra as chamadas para as APIs do **OpenRouter** e **Replicate**.
* `evaluator.py`: Avaliador **Sintático**. Ferramenta de auditoria rigorosa que exige correspondência literal de *strings* via Jaccard Index.
* `evaluator_hudson.py`: Avaliador **Semântico**. Emula a correção humana do estudo de base, aplicando tolerância via *Regex* para variações lógicas de nomenclatura.
* `data/`: Contém os artefatos de entrada, como a imagem de referência `Company Schema` (Elmasri & Navathe, 2015).
* `docs/`: Documentação e artigos científicos formatados em Markdown.
* `notebooks/`: Cadernos de experimentação iterativa e arquivos legados.
* `results/`: Diretório gerado automaticamente contendo os schemas JSON extraídos das respostas dos modelos.

## 🚀 Como Executar

### 1. Pré-requisitos
Você precisará de Python 3.8+ e das dependências listadas no projeto. As inferências são executadas na nuvem, portanto, é obrigatório possuir as respectivas chaves de API:

Configure suas chaves como variáveis de ambiente:
```bash
export OPENROUTER_API_KEY="sua-chave-openrouter-aqui"
export REPLICATE_API_TOKEN="sua-chave-replicate-aqui"
```

### 2. Disparando o Benchmark
Para inicializar a bateria de inferência visual com todos os modelos (2 *prompts* por modelo) contra o diagrama de referência:
```bash
python3 benchmark_er.py
```
*Isso consumirá tokens das suas contas nas plataformas e populacional a pasta `results/` com arquivos `.json` para cada tentativa.*

### 3. Calculando as Métricas
Com os JSONs gerados, você pode avaliar a exatidão estrutural das respostas sob duas metodologias independentes:

**Avaliação Sintática de Máquina (Rigorosa)**:
```bash
python3 evaluator.py
```

**Avaliação Semântica (Tolerante - Método original)**:
```bash
python3 evaluator_hudson.py
```
