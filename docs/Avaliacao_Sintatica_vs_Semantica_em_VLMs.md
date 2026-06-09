# Do Conceitual ao Lógico: Um Benchmark de Vision-Language Models Open-Weights na Conversão de Diagramas ER

## 1. Resumo
A transformação automatizada de Diagramas Entidade-Relacionamento (ER) para Esquemas Lógicos Relacionais tem se beneficiado do advento dos Modelos de Visão e Linguagem (VLMs). Trabalhos recentes, como o de Silva et al. (2026), estabeleceram uma linha de base de acurácia (>94%) utilizando APIs proprietárias (GPT, Claude, Gemini). Este artigo estende esse estudo, focando na avaliação sistemática de modelos de fundação de pesos abertos (*open-weights*, como Qwen-3 VL, Llama 3.2 Vision e Família Mistral). Os resultados demonstram que, sob a mesma metodologia de avaliação semântica do estudo original, arquiteturas abertas (especificamente o Qwen-3 VL 235B) alcançam desempenho equivalente ou superior a modelos fechados, viabilizando a extração automatizada de esquemas com menor custo.

---

## 2. Introdução
A engenharia de prompts multimodais permitiu que LLMs analisassem imagens de arquitetura de software, traduzindo diagramas em estruturas lógicas. O estudo prévio de Silva et al. demonstrou a viabilidade dessa abordagem avaliando modelos proprietários. No entanto, tem-se observado o avanço de modelos de pesos abertos (*open-weights*), que oferecem maior transparência, privacidade e menores custos operacionais.

Este trabalho busca preencher uma lacuna na literatura ao submeter os principais modelos *open-weights* à mesma bateria de testes e metodologia de correção do estudo de Silva et al. O objetivo central é determinar se o estado da arte do código aberto atingiu a maturidade necessária para substituir modelos proprietários na tarefa de conversão ER. Secundariamente, documenta-se a auditoria das métricas de avaliação para garantir a comparabilidade empírica com a literatura original.

---

## 3. Metodologia

### 3.1. Base de Dados e Referência
Utilizou-se como diagrama de referência o clássico **"Company Schema"** (Elmasri & Navathe, 2015). O gabarito lógico (*padrão-ouro*) canonizado por essa literatura possui 6 entidades, 28 atributos globais, 9 colunas compondo Chaves Primárias (PKs) e 8 colunas compondo Chaves Estrangeiras (FKs), totalizando 51 elementos sintáticos.

### 3.2. Seleção de Modelos, Infraestrutura de Inferência e Análise de Custos
A seleção das arquiteturas avaliadas (englobando as famílias Qwen, Llama, Mistral, Gemini, GPT e Claude) foi fundamentada em pesquisas recentes que mapeiam o estado da arte em IA multimodal. A escolha dos modelos de referência proprietários (GPT, Claude e Gemini) segue a metodologia original do estudo de Silva et al. (2026). Para as alternativas abertas, adotou-se a taxonomia de Tayachi et al. (2026), que destaca famílias como LLaMA e Mistral como pilares do ecossistema de pesos abertos, e no benchmark VLBiasBench (Wang et al., 2026), que valida extensivamente as capacidades multimodais da arquitetura Qwen-VL. Essa curadoria assegura uma amostra representativa que contrasta de forma justa o desempenho corporativo fechado com as arquiteturas abertas de maior adoção.

A execução unificada dos modelos foi orquestrada utilizando duas plataformas de inferência em nuvem, permitindo o provisionamento tanto de modelos fechados quanto de arquiteturas *open-weights*:

* **OpenRouter:** Utilizada como ponto de acesso unificado para os modelos de fronteira proprietários (GPT-4o, GPT-5.5, Claude Opus 4.1/4.8, Gemini Flash) e para modelos de pesos abertos otimizados (Qwen-3 VL 235B, Llama 3.2 11B, Família Mistral). O modelo de precificação é baseado no consumo de unidades de processamento (*tokens*) de entrada e saída.
* **Replicate:** Utilizada para o provisionamento isolado e sob demanda do modelo de referência acadêmico (LLaVA v1.6 Vicuna 13B). O modelo de precificação difere, sendo baseado no tempo de alocação de hardware de inferência (tarifado por milissegundos de uso de GPUs de alta performance, como Nvidia A100/H100).

**Dinâmica de Custos e Escalabilidade:** A viabilidade econômica é um fator decisivo para a escalabilidade de fluxos de automação na conversão ER. Abaixo é apresentado o perfil técnico e financeiro dos modelos avaliados neste estudo:

| Modelo | Lançamento | Janela de Contexto | Custo Input (por 1M tokens) | Custo Output (por 1M tokens) |
|:---|:---:|:---:|:---:|:---:|
| **Qwen-3 VL 235B** | Set/2025 | 262K | $0.20 | $0.88 |
| **Llama 3.2 11B Vision** | Set/2024 | 131K | $0.345 | $0.345 |
| **Ministral 14B** | Dez/2025 | 262K | $0.20 | $0.20 |
| **Mistral Large** | Dez/2025 | 262K | $0.50 | $1.50 |
| **Gemini 2.5 Flash** | Jun/2025 | 1M | $0.30 | $2.50 |
| **Gemini 3.5 Flash** | Mai/2026 | 1M | $1.50 | $9.00 |
| **GPT-4o** | Mai/2024 | 128K | $2.50 | $10.00 |
| **GPT-5.5** | Abr/2026 | 1M | $5.00 | $30.00 |
| **Claude Opus 4.1** | Ago/2025 | 200K | $15.00 | $75.00 |
| **Claude Opus 4.8** | Mai/2026 | 1M | $5.00 | $25.00 |
| **LLaVA v1.6 13B** | Fev/2024 | N/A | $0.053/run | - |

Observando os dados acima, nota-se que modelos da geração anterior (como Claude Opus 4.1) possuem elevados custos de operação ($15.00 Entrada / $75.00 Saída). As iterações do ano de 2026 (GPT-5.5 e Claude 4.8) expandiram a janela de contexto para 1 milhão de *tokens* com redução de custo ($5.00 de Entrada). Por outro lado, o modelo de referência rodado via Replicate (LLaVA) possui um custo fixo aproximado por inferência ($0.053 por requisição), o que pode inviabilizar o processamento em larga escala quando comparado ao modelo granular das APIs otimizadas.


### 3.3. Engenharia de Prompts
Para garantir a equivalência dos testes, adotaram-se os dois comandos de instrução (*prompts*) utilizados no estudo original de Silva et al. (2026):
* **Prompt 1 (Sem Exemplos Prévios):** Solicita a conversão direta sem fornecer regras ou gabaritos.
* **Prompt 2 (Raciocínio Guiado):** Fornece regras explícitas de mapeamento de cardinalidade (1:1, 1:N, N:N) baseadas em Elmasri & Navathe.

**Desafios Encontrados:** Modelos de fronteira e de pesos abertos apresentaram viés conversacional, gerando formatação Markdown e raciocínio intermediário, o que frequentemente causava truncamento e falhas no analisador JSON.
**Solução:** Foram implementadas restrições na instrução de comportamento do sistema (`"Você NÃO PODE explicar seu raciocínio"`), adequação da amostragem (`temperature=0` para assegurar determinismo) e aumento da janela de saída (`max_tokens=4000`). Adicionou-se também uma função de extração via expressões regulares (`clean_json_output`) para isolar o bloco estruturado.

### 3.4. Auditoria Metodológica e Emparelhamento Semântico
Para garantir a reprodutibilidade em relação aos números de Silva et al., foi necessário emular as condições de correção literária:

1. **Avaliador Semântico Original (`evaluator_semantic.py`)**: Desenvolvido para espelhar a avaliação do autor original. Ele aplica perdão semântico via *Regex* (assumindo que `Location` na imagem equivale a `Plocation` no código) e utiliza a fórmula da Precisão Pura. Os resultados gerados por este avaliador validam a comparação com os modelos do estudo original.
2. **Avaliador Sintático Rigoroso (`evaluator_syntactic.py`)**: Desenvolvido neste trabalho como ferramenta de auditoria. Ele exige correspondência exata de *strings* e demonstra o limite sintático dos modelos.

---

## 4. Resultados e Discussão

Os modelos foram submetidos a ambos os avaliadores, revelando duas realidades distintas da capacidade atual da IA generativa. Abaixo, é apresentada a tabela consolidada de resultados, contrastando a avaliação rigorosa (*Sintática*) com a avaliação tolerante (*Semântica*).

### 4.1. Tabela Comparativa de Desempenho

| Modelo e Prompt | F1-Score (Sintático) | Acurácia (Sintática) | F1-Score (Semântico) | Acurácia (Semântica) |
|:---|:---:|:---:|:---:|:---:|
| claude-opus-4.1_prompt_1 | 92.54% | 86.11% | 92.13% | 95.35% |
| claude-opus-4.1_prompt_2 | 86.57% | 76.32% | 92.13% | 95.35% |
| claude-opus-4.8_prompt_1 | 97.06% | 94.29% | 97.83% | 97.83% |
| claude-opus-4.8_prompt_2 | 70.59% | 54.55% | 91.30% | 91.30% |
| gemini-2.5-flash_prompt_1 | 69.70% | 53.49% | 75.00% | 78.57% |
| gemini-2.5-flash_prompt_2 | 67.65% | 51.11% | 93.48% | 93.48% |
| gemini-3.5-flash_prompt_1 | 73.53% | 58.14% | 95.65% | 95.65% |
| gemini-3.5-flash_prompt_2 | 73.53% | 58.14% | 95.65% | 95.65% |
| gpt-4o_prompt_1 | 85.25% | 74.29% | 76.32% | 96.67% |
| gpt-4o_prompt_2 | 86.96% | 76.92% | 80.46% | 85.37% |
| gpt-5.5_prompt_1 | 67.65% | 51.11% | 93.48% | 93.48% |
| gpt-5.5_prompt_2 | 67.65% | 51.11% | 93.48% | 93.48% |
| llama-3.2-11b-vision_prompt_1 | 42.86% | 27.27% | 40.91% | 42.86% |
| llama-3.2-11b-vision_prompt_2 | 32.35% | 19.30% | 45.45% | 47.62% |
| llava-v1.6-vicuna-13b_prompt_1 | 26.67% | 15.38% | 35.64% | 32.73% |
| llava-v1.6-vicuna-13b_prompt_2 | 15.58% | 8.45% | 35.42% | 34.00% |
| ministral-14b-2512_prompt_1 | 48.10% | 31.67% | 60.55% | 52.38% |
| ministral-14b-2512_prompt_2 | 48.72% | 32.20% | 61.11% | 53.23% |
| mistral-large-2512_prompt_1 | 58.23% | 41.07% | 67.92% | 60.00% |
| mistral-large-2512_prompt_2 | 64.79% | 47.92% | 80.00% | 77.55% |
| qwen3-vl-235b-a22b_prompt_1 | 69.57% | 53.33% | 90.32% | 89.36% |
| qwen3-vl-235b-a22b_prompt_2 | 69.57% | 53.33% | 92.47% | 91.49% |

### 4.2. Análise Sintática
Observando as colunas sintáticas da tabela, nota-se que grande parte dos modelos (como as famílias Gemini, GPT e Qwen) estagnam na faixa de **70% a 73%** de F1-Score. A exceção a essa barreira é a família Claude 4, que mapeou prefixos literais com eficácia superior a 92% sob o Prompt 1.

Esse limite estrutural reflete a barreira literal: as arquiteturas extraem o que identificam na imagem. Como o diagrama visual omite metadados textuais (ex: exibe a string `Name` no lugar de `Dname`), o modelo não possui o contexto implícito para gerar identificadores canônicos sem intervenção. O avaliador rigoroso baseado em Jaccard penaliza essas variações: para cada atributo não traduzido, gera-se simultaneamente 1 Falso Positivo e 1 Falso Negativo, reduzindo o índice numérico.

### 4.3. Análise Semântica
Quando as métricas simulam o raciocínio humano perdoando renomeações (`Name` = `Dname`) e adotam a Precisão (`TP/TP+FP`) como "Acurácia", os resultados apresentam um aumento significativo, subindo em média mais de 20 pontos percentuais.
Neste cenário, modelos como **Claude 4.8** (97.83%), **Gemini 3.5 Flash** (95.65%) e **Qwen-3 VL 235B** (92.47%) alcançam altas taxas de acurácia. Nota-se que a intenção relacional dos modelos é mantida. A diferença entre as métricas reflete a rigidez da sintaxe, não um déficit lógico. 

O *Qwen-3 VL 235B* obteve destaque entre os modelos de pesos abertos, atingindo inclusive o patamar dos proprietários.

### 4.4. Efeito de Saturação de Contexto sob Instrução Explícita
Observou-se uma resposta assimétrica das arquiteturas à Engenharia de Prompts. A introdução do "Prompt 2", que carrega instruções explícitas de mapeamento relacional (regras de cardinalidade 1:N e N:M baseadas na literatura), produziu impactos divergentes conforme a escala do modelo.

Para modelos medianos, como o Mistral-Large, a instrução explícita foi necessária, elevando seu desempenho (salto de 67.92% para 80.00% em F1-Score semântico). No entanto, ao se aplicar a mesma instrução a modelos de fronteira (como Claude 4.8 e Qwen-3 VL), observou-se degradação de desempenho (o Claude 4.8 regrediu de 97.83% para 91.30%).

Este fenômeno, conhecido como Saturação de Contexto, indica que impor regras a modelos de grande escala pode criar atrito cognitivo. Como essas arquiteturas já possuem o conhecimento relacional codificado em seus pesos, a injeção de instruções dilui a atenção da rede, prejudicando a abstração sob o cenário livre de exemplos prévios (Prompt 1).

---

## 5. Conclusão
Este estudo amplia a discussão da literatura anterior, evidenciando que a exclusividade dos modelos proprietários na extração de esquemas lógicos foi superada. Através do emparelhamento metodológico com o estudo de Silva et al., verificou-se que modelos *open-weights* superaram as limitações no seguimento de instruções em JSON.

Em termos de viabilidade econômica, destaca-se o **Qwen-3 VL 235B**: com custo de $0.20 por milhão de *tokens* de entrada, este modelo alcançou um F1-Score semântico (92.47%) comparável ao de APIs proprietárias (como Claude 4.8 e Gemini 3.5 Flash). Estes resultados o posicionam como uma alternativa de alto custo-benefício para processamento lógico em larga escala, especialmente ao contrastá-lo com modelos hospedados sob demanda (como o LLaVA), cujos custos tornam-se imprevisíveis devido ao tempo de inicialização do hardware.

A avaliação dupla aqui conduzida revelou uma métrica importante para a área: os LLMs atuais compreendem os diagramas, mas a maioria apresenta limitações na exatidão sintática (platô na faixa dos 70%). Para implementações reais de banco de dados, o uso de LLMs de pesos abertos é financeiramente e tecnicamente viável, desde que acoplado a mecanismos de validação sintática e glossários estruturados para suprir variações literais.

---

## 6. Referências

1. SILVA, Hudson Afonso Batista da, et al. *From Conceptual to Logical Schema: An LLM-based Approach*. [s.l.: s.n.], 2026.
2. ELMASRI, Ramez; NAVATHE, Shamkant B. *Fundamentals of Database Systems*. 7ª ed. Pearson, 2015. (Diagrama canônico "Company Schema").
3. TAYACHI, Chaima, et al. *Exploring Open-Weight Foundation Models: A Systematic Review From Transformers to Multimodal AI*. IEEE, 2026.
4. WANG, Sibo, et al. *VLBiasBench: A Comprehensive Benchmark for Evaluating Bias in Large Vision-Language Model*. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2026.
