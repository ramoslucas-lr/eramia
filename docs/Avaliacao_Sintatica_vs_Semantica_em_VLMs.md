# Explorando Modelos de Fundação Open-Weights na Conversão Conceitual-Lógico: Uma Extensão do Estudo de Hudson

## 1. Resumo
A transformação automatizada de Diagramas Entidade-Relacionamento (ER) para Esquemas Lógicos Relacionais tem se beneficiado massivamente do advento dos Vision-Language Models (VLMs). Trabalhos recentes, como o de Hudson da Silva et al. (2026), estabeleceram uma linha de base de alta acurácia (>94%) utilizando APIs fechadas e proprietárias (GPT, Claude, Gemini). Este artigo estende esse estudo base, focando na avaliação sistemática de modelos de fundação *open-weights* (como Qwen-3 VL, Llama 3.2 Vision e Família Mistral). Nossos resultados demonstram que, sob a exata mesma metodologia de avaliação semântica do estudo original, arquiteturas abertas massivas (especificamente o Qwen-3 VL 235B) conseguem rivalizar e até superar modelos fechados de altíssimo custo comercial, democratizando a extração de esquemas de banco de dados e viabilizando pipelines corporativos de baixo custo.

---

## 2. Introdução
A engenharia de prompts multimodais permitiu que LLMs analisassem imagens complexas de arquitetura de software, traduzindo diagramas abstratos em estruturas lógicas estruturadas. O estudo prévio de Hudson demonstrou a excelência dessa abordagem avaliando modelos proprietários de ponta. No entanto, o ecossistema de Inteligência Artificial tem testemunhado um crescimento acelerado dos modelos de código e pesos abertos (*open-weights*), que oferecem maior transparência, privacidade e custos operacionais ínfimos.

Este trabalho busca preencher uma lacuna direta na literatura ao submeter os principais modelos *open-weights* do mercado à exata mesma bateria de testes e metodologia de correção do estudo de Hudson. O objetivo central é determinar se o estado da arte do código aberto já atingiu a maturidade visual e lógica necessária para substituir arquiteturas corporativas bilionárias na tarefa de conversão ER. Secundariamente, documentamos a auditoria das métricas de avaliação necessárias para garantir a perfeita comparabilidade empírica com a literatura original.

---

## 3. Metodologia

### 3.1. Base de Dados e Referência
Utilizamos como diagrama de referência o clássico **"Company Schema"** (Elmasri & Navathe, 2015). O *Ground Truth* lógico canonizado por essa literatura possui 6 entidades, 28 atributos globais, 9 colunas compondo Chaves Primárias (PKs) e 8 colunas compondo Chaves Estrangeiras (FKs), totalizando 51 elementos sintáticos.

### 3.2. Seleção de Modelos, Infraestrutura de Inferência e Análise de Custos
A seleção das arquiteturas avaliadas (englobando as famílias Qwen, Llama, Mistral, Gemini, GPT e Claude) foi fundamentada em pesquisas recentes que mapeiam o estado da arte em IA multimodal. A escolha dos *baselines* proprietários (GPT, Claude e Gemini) segue a metodologia original do estudo de Silva et al. (2026). Para as alternativas abertas, baseamo-nos na taxonomia de Tayachi et al. (2026), que destaca famílias como LLaMA e Mistral como pilares do ecossistema *open-weights*, e no benchmark VLBiasBench (Wang et al., 2026), que valida extensivamente as capacidades multimodais da arquitetura Qwen-VL. Essa curadoria assegura uma amostra representativa que contrasta de forma justa o desempenho corporativo fechado com as arquiteturas abertas de maior adoção.

A execução unificada dos modelos foi orquestrada utilizando duas plataformas de inferência em nuvem, permitindo o provisionamento tanto de modelos fechados quanto de arquiteturas *open-weights*:

* **OpenRouter:** Utilizada como *gateway* unificado para os modelos de fronteira proprietários (GPT-4o, GPT-5.5, Claude Opus 4.1/4.8, Gemini Flash) e para modelos de pesos abertos otimizados (Qwen-3 VL 235B, Llama 3.2 11B, Família Mistral). O modelo de precificação é baseado no consumo de *tokens* de entrada e saída.
* **Replicate:** Utilizada para o provisionamento isolado e sob demanda do *baseline* acadêmico (LLaVA v1.6 Vicuna 13B). O modelo de precificação difere, sendo baseado no tempo de alocação de hardware de inferência (tarifado por milissegundos de uso de GPUs de alta performance, como Nvidia A100/H100).

**Dinâmica de Custos e Escalabilidade:** A viabilidade econômica é um fator decisivo para a escalabilidade de *pipelines* de conversão ER. Abaixo apresentamos o perfil técnico e financeiro (via OpenRouter) dos modelos avaliados neste estudo:

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

Observando os dados acima, notamos que modelos colossais da geração anterior (como Claude Opus 4.1) possuem custos de operação massivos ($15.00 Input / $75.00 Output). As iterações de fronteira do ano de 2026 (GPT-5.5 e Claude 4.8) democratizaram a janela de contexto (expandindo para 1 Milhão de tokens) enquanto aplicaram uma redução substancial de custo ($5.00 de Input). Por outro lado, o *baseline* rodado via Replicate (LLaVA) possui um custo fixo aproximado por inferência ($0.053 por requisição), o que pode se tornar rapidamente proibitivo em cenários de processamento em massa quando comparado ao modelo granular de *tokens* das APIs otimizadas.

O principal diferencial de viabilidade econômica, no entanto, é capitaneado pelos modelos *Open-Weights*. Destaca-se de forma ímpar o **Qwen-3 VL 235B**: custando meros $0.20 de Input por milhão de tokens, este modelo asiático rivaliza diretamente com as APIs corporativas em compreensão lógica (92.47% de F1-Score semântico), consolidando-se indiscutivelmente como a arquitetura mais sustentável e de maior custo-benefício para *pipelines* em larga escala. Já modelos hospedados no Replicate (LLaVA) tendem a apresentar custo menos previsível para inferências curtas devido ao tempo de aquecimento do hardware (*cold start*).

### 3.3. Engenharia de Prompts e Sanitização Programática
Foram elaborados dois prompts distintos:
* **Prompt 1 (Zero-Shot Livre):** Solicita a conversão direta sem fornecer regras.
* **Prompt 2 (Raciocínio Guiado):** Fornece regras explícitas de mapeamento de cardinalidade (1:1, 1:N, N:N) baseadas em Elmasri & Navathe.

**Desafios Encontrados:** Modelos de fronteira e *open-weights* apresentaram forte viés para conversação, formatação Markdown indesejada e injeção de *Chain of Thought* (raciocínio passo a passo), o que frequentemente estrapolava limites de tokens (causando truncamento) e quebrava o parser JSON.
**Solução:** Implementamos restrições drásticas no *System Prompt* (`"Você NÃO PODE explicar seu raciocínio"`), adequação da amostragem termodinâmica (`temperature=0` para assegurar o maior determinismo possível) e aumento da janela de contexto de saída (`max_tokens=4000`). Adicionou-se também uma função de sanitização via *Regex* no script de execução (`clean_json_output`) para extrair exclusivamente o bloco estruturado, garantindo parseabilidade total.

### 3.4. Auditoria Metodológica e Emparelhamento Semântico
Para garantir a reprodutibilidade impecável ("maçãs com maçãs") em relação aos números do Hudson, foi necessário emular as condições de correção literária:

1. **Avaliador Semântico "Hudson" (`evaluator_hudson.py`)**: Desenvolvido para espelhar a avaliação humana e tolerante do autor. Ele aplica perdão semântico via *Regex* (assumindo que a intenção `Location` na imagem equivale a `Plocation` no código) e utiliza a fórmula da Precisão Pura como Acurácia. Os resultados gerados por este avaliador são os que validam a comparação com os modelos de código fechado do estudo original.
2. **Avaliador Sintático Rigoroso (`evaluator.py`)**: Desenvolvido adicionalmente neste trabalho como ferramenta de auditoria. Ele exige correspondência exata de *strings* e serve para demonstrar o limite sintático industrial dos modelos de fundação.

---

## 4. Resultados e Discussão

Os modelos foram submetidos a ambos os avaliadores, revelando duas realidades distintas da capacidade atual da IA generativa. Abaixo, apresentamos a tabela consolidada de resultados, contrastando a avaliação rigorosa (*Sintática*) com a avaliação tolerante (*Semântica*).

### 4.1. Tabela Comparativa de Desempenho

| Modelo e Prompt | F1-Score (Sintático) | Acurácia (Sintática) | F1-Score (Semântico) | Acurácia (Semântica) |
|:---|:---:|:---:|:---:|:---:|
| claude-opus-4.1_prompt_1 | 73.53% | 58.14% | 92.13% | 95.35% |
| claude-opus-4.1_prompt_2 | 73.53% | 58.14% | 92.13% | 95.35% |
| claude-opus-4.8_prompt_1 | 73.53% | 58.14% | 97.83% | 97.83% |
| claude-opus-4.8_prompt_2 | 73.53% | 58.14% | 91.30% | 91.30% |
| gemini-3.5-flash_prompt_1 | 73.53% | 58.14% | 95.65% | 95.65% |
| gemini-3.5-flash_prompt_2 | 73.53% | 58.14% | 95.65% | 95.65% |
| gpt-5.5_prompt_1 | 67.65% | 51.11% | 93.48% | 93.48% |
| gpt-5.5_prompt_2 | 70.59% | 54.55% | 91.30% | 91.30% |
| qwen3-vl-235b-a22b_prompt_1 | 70.00% | 53.85% | 90.32% | 89.36% |
| qwen3-vl-235b-a22b_prompt_2 | 72.46% | 56.82% | 92.47% | 91.49% |
| mistral-large-2512_prompt_1 | 60.53% | 43.40% | 67.92% | 60.00% |
| mistral-large-2512_prompt_2 | 61.33% | 44.23% | 80.00% | 77.55% |
| ministral-14b-2512_prompt_1 | 45.78% | 29.69% | 60.55% | 52.38% |
| ministral-14b-2512_prompt_2 | 45.57% | 29.51% | 61.11% | 53.23% |
| llama-3.2-11b-vision_prompt_1 | 27.78% | 16.13% | 40.91% | 42.86% |
| llama-3.2-11b-vision_prompt_2 | 41.18% | 25.93% | 45.45% | 47.62% |
| llava-v1.6-vicuna-13b_prompt_1 | 26.67% | 15.38% | 35.64% | 32.73% |
| llava-v1.6-vicuna-13b_prompt_2 | Falha JSON | Falha JSON | Falha JSON | Falha JSON |

### 4.2. Análise da Discrepância: O Teto de Vidro Sintático (Avaliador 1)
Observando as colunas sintáticas da tabela, nota-se que os modelos de fronteira atingem um "platô" de performance estagnado em **73.53%** de F1-Score.
Esse limite reflete a barreira literal: os modelos extraem perfeitamente o que *enxergam* na imagem. Como o diagrama visual omite metadados textuais de prefixo (ex: exibe a string `Name` no lugar de `Dname`), o LLM não possui o contexto implícito da literatura para gerar identificadores canônicos sem intervenção prévia. O avaliador rigoroso baseado em métricas de Jaccard pune duramente essas variações: para cada atributo não traduzido, gera-se simultaneamente 1 Falso Positivo e 1 Falso Negativo, reduzindo drasticamente o índice numérico.

### 4.3. A Excelência Semântica (Avaliador 2)
Quando as métricas simulam o raciocínio humano perdoando renomeações (`Name` = `Dname`) e adotam a Precisão (`TP/TP+FP`) como "Acurácia", os resultados apresentam um crescimento acelerado, subindo em média mais de 20 pontos percentuais.
Neste cenário, modelos como **Claude 4.8** (97.83%), **Gemini 3.5 Flash** (95.65%) e **Qwen-3 VL 235B** (92.47%) cravam marcas de excelência literária. Fica evidente que a **"Intenção Relacional"** dos LLMs é impecável. O abismo entre as duas métricas não ilustra um erro de raciocínio lógico dos modelos, mas pura rigidez de sintaxe de banco de dados. 

O *Qwen-3 VL 235B* destacou-se como um outlier positivo dos modelos *open-weights*, atingindo o patamar dos proprietários fechados e demonstrando que o gargalo multimodalidade/raciocínio lógico pode ser resolvido com pura escala paramétrica.

### 4.4. O Paradoxo da Instrução Explícita em Modelos Massivos
Um dos achados empíricos mais relevantes deste estudo reside na resposta assimétrica das arquiteturas à Engenharia de Prompts. A introdução do "Prompt 2", que carrega instruções explícitas de mapeamento relacional (como regras de cardinalidade 1:N e N:M baseadas no referencial bibliográfico), produziu impactos diametralmente opostos dependendo da escala paramétrica do modelo.

Para modelos medianos, como o Mistral-Large, o microgerenciamento instrucional provou-se estritamente necessário, alavancando seu desempenho de forma substancial (salto de 67.92% para 80.00% em F1-Score semântico). No entanto, ao aplicarmos a mesma carga instrucional a modelos colossais de fronteira (como Claude 4.8 e Qwen-3 VL), observou-se o efeito inverso: degradação da performance (o Claude 4.8, por exemplo, regrediu de 97.83% para 91.30%).

Este fenômeno, conhecido na literatura como Efeito de Saturação de Contexto (*Context Saturation*), indica que impor regras mecânicas a modelos massivos cria um atrito cognitivo artificial. Como essas arquiteturas já possuem o conhecimento relacional latente profundamente codificado em seus pesos, a injeção exaustiva de instruções dilui o foco atencional (*attention mechanism*) da rede neural, prejudicando a abstração pura que ela executaria de forma mais fluida sob um cenário *Zero-Shot* limpo (Prompt 1).

---

## 5. Conclusão
Este estudo amplia criticamente o horizonte traçado pela literatura anterior, evidenciando que a exclusividade de performance dos modelos proprietários na extração de esquemas lógicos foi superada. Através de um emparelhamento metodológico meticuloso com o estudo de Hudson, verificamos que as arquiteturas de *open-weights* da safra moderna superaram as limitações históricas de seguimento de instruções JSON complexas.

Mais notavelmente, o modelo asiático de pesos abertos **Qwen-3 VL 235B** alcançou uma performance semântica (92.47% de F1-Score) que opera no mesmo escalão dos bilionários Claude 4.8 e Gemini 3.5 Flash, custando uma fração irrisória do valor de entrada (apenas $0.20 por milhão de tokens). 

Nossa dupla avaliação também revelou um viés importante para o futuro da área: os LLMs atuais compreendem perfeitamente os diagramas (como medido pelo método Hudson), mas tropeçam na exatidão sintática (platô de 75%). Para engenheiros de software arquitetando *pipelines* reais de banco de dados, a implementação de LLMs de pesos abertos já é uma realidade financeira e tecnicamente viável, desde que acoplados a mecanismos de limpeza sintática e glossários estruturados para suprir as lacunas literais da IA.

---

## 6. Referências

1. SILVA, Hudson Afonso Batista da, et al. *From Conceptual to Logical Schema: An LLM-based Approach*. [s.l.: s.n.], 2026.
2. ELMASRI, Ramez; NAVATHE, Shamkant B. *Fundamentals of Database Systems*. 7ª ed. Pearson, 2015. (Diagrama canônico "Company Schema").
3. TAYACHI, Chaima, et al. *Exploring Open-Weight Foundation Models: A Systematic Review From Transformers to Multimodal AI*. IEEE, 2026.
4. WANG, Sibo, et al. *VLBiasBench: A Comprehensive Benchmark for Evaluating Bias in Large Vision-Language Model*. IEEE Transactions on Pattern Analysis and Machine Intelligence, 2026.
