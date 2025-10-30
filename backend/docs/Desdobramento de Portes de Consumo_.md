

# **Desdobramento Granular de Tiers de Consumo de Energia e Porte de Projetos no Setor Elétrico Brasileiro**

## **1\. Introdução**

A segmentação de consumidores e projetos de energia é uma ferramenta de crescente importância para o planejamento estratégico, o desenvolvimento de novos negócios e a formulação de políticas regulatórias no dinâmico setor elétrico brasileiro. Classificações de consumo excessivamente amplas podem ocultar nuances significativas entre perfis de usuários, limitando a eficácia de análises e a customização de soluções energéticas. Em um cenário marcado pela expansão de tecnologias como a Geração Distribuída (GD), a abertura gradual do mercado livre de energia e a intensificação de programas de eficiência energética, a necessidade de uma granularidade maior na categorização de consumidores e projetos torna-se premente.  
Este relatório atende à solicitação de um desdobramento dos tiers de consumo de energia de referência – Pequeno Porte (PP) a Extra Extra Grande (XGG), medidos em quilowatt-hora por mês (kWh/mês) – em um sistema de classificação mais detalhado. O objetivo central é propor um conjunto de tiers granulares que não apenas refine as faixas de consumo, mas também estabeleça uma correlação explícita com o porte de projetos, tipicamente expresso em termos de potência (kW ou MW). Tal correlação visa tornar a classificação mais aplicável ao dimensionamento, à análise de viabilidade e ao desenvolvimento de diversos tipos de empreendimentos energéticos, desde sistemas fotovoltaicos residenciais até plantas de minigeração para grandes consumidores industriais. A demanda por essa granularidade reflete uma maturidade crescente do mercado, onde a oferta de soluções energéticas customizadas exige uma compreensão mais fina e precisa dos múltiplos perfis de consumo existentes. Este documento busca, portanto, fornecer uma ferramenta analítica robusta e prática para os diversos agentes que atuam no setor elétrico nacional.

## **2\. Panorama Atual das Classificações de Consumo e Projetos no Setor Elétrico Brasileiro**

Antes de propor um novo sistema de tiers, é fundamental contextualizar as classificações de consumo e porte de projetos já existentes e consolidadas no setor elétrico brasileiro. Estas classificações, estabelecidas tanto por práticas de mercado quanto por regulamentações da Agência Nacional de Energia Elétrica (ANEEL), formam a base sobre a qual o desdobramento granular será construído.

### **2.1. Tiers de Consumo de Energia de Referência (Fornecidos pelo Usuário)**

A solicitação para este estudo parte de um conjunto de sete tiers de consumo de energia, que servem como ponto de partida para o desdobramento. Estes tiers são apresentados na Tabela 1\.  
**Tabela 1: Tiers de Consumo de Energia de Referência (Base para Desdobramento)**

| Sigla do Tier | Faixa de Consumo (kWh/mês) | Exemplo Original Fornecido |
| :---- | :---- | :---- |
| PP | Até 300 | Residencial básico |
| P | 301 a 700 | Residencial médio/alto |
| M | 701 a 2.000 | Residencial alto padrão, pequeno comércio |
| G | 2.001 a 10.000 | Comércio médio, pequena indústria |
| GG | 10.001 a 50.000 | Comércio grande, indústria média |
| XG | 50.001 a 200.000 | Indústria grande |
| XGG | 200.001 a 500.000 (limite Mini GD) | Indústria muito grande, limite da Mini GD |

Esta tabela estabelece claramente o ponto de partida, conforme fornecido na consulta, garantindo alinhamento e servindo como referência visual imediata para as subdivisões que serão propostas posteriormente. A menção ao "limite da Mini GD" no tier XGG é particularmente relevante e será analisada em detalhe à luz das definições regulatórias.

### **2.2. Classificações Regulatórias de Unidades Consumidoras (ANEEL)**

A ANEEL, através de suas resoluções normativas, estabelece os critérios oficiais para a classificação das unidades consumidoras de energia elétrica no Brasil. A Resolução Normativa (REN) ANEEL nº 1.000/2021 é o principal instrumento que consolida essas definições, sucedendo normativos anteriores como a REN 414/2010 e a REN 456/2000.1  
As unidades consumidoras são primordialmente divididas em dois grandes grupos:

* **Grupo A:** Composto por unidades consumidoras que recebem energia em tensão igual ou superior a 2,3 quilovolts (kV), ou que são atendidas a partir de sistema subterrâneo de distribuição em tensão inferior a 2,3 kV mas optam por esta modalidade. A característica principal deste grupo é a **tarifação binômia**, onde a fatura inclui componentes de demanda de potência (contratada e/ou medida, em kW) e de consumo de energia (em kWh).1 O Grupo A é subdividido nos seguintes subgrupos, de acordo com o nível de tensão de conexão:  
  * **Subgrupo A1:** Tensão $\\ge 230 \\text{ kV}$  
  * **Subgrupo A2:** Tensão entre $88 \\text{ kV}$ e $138 \\text{ kV}$  
  * **Subgrupo A3:** Tensão de $69 \\text{ kV}$  
  * **Subgrupo A3a:** Tensão entre $30 \\text{ kV}$ e $44 \\text{ kV}$  
  * **Subgrupo A4:** Tensão entre $2,3 \\text{ kV}$ e $25 \\text{ kV}$  
  * **Subgrupo AS:** Tensão $\< 2,3 \\text{ kV}$ (conexão subterrânea)  
* **Grupo B:** Abrange as unidades consumidoras com fornecimento em tensão inferior a 2,3 kV. Este grupo é caracterizado pela **tarifação monômia**, onde a fatura é baseada predominantemente no consumo de energia (em kWh).1 O Grupo B é subdividido em:  
  * **Subgrupo B1:** Residencial (incluindo a subclasse Residencial Baixa Renda com benefícios tarifários específicos)  
  * **Subgrupo B2:** Rural  
  * **Subgrupo B3:** Demais classes (onde se enquadram muitos consumidores comerciais e industriais de pequeno porte)  
  * **Subgrupo B4:** Iluminação Pública

Além dos grupos e subgrupos, a ANEEL também define **classes** de consumo (Residencial, Industrial, Comercial, Rural, Poder Público, Serviço Público, Consumo Próprio) que detalham a finalidade da utilização da energia elétrica.3  
A distinção entre Grupo A e Grupo B é crucial para a correlação entre consumo (kWh) e potência (kW). Para os consumidores do Grupo A, a demanda de potência é um parâmetro contratual e diretamente medido, facilitando o dimensionamento de projetos. Para os consumidores do Grupo B, a demanda de potência não é explicitamente faturada e precisa ser estimada a partir do histórico de consumo e do perfil de uso da energia, o que introduz um grau de incerteza maior na sua determinação para fins de projeto. Consequentemente, os novos tiers propostos neste relatório levarão em consideração se o consumidor típico de cada faixa se enquadraria no Grupo A ou B, pois isso influencia diretamente a precisão da estimativa de potência e o tipo de projeto energético mais adequado.

### **2.3. Definições e Limites de Potência para Microgeração e Minigeração Distribuída (MMGD)**

A Geração Distribuída, especialmente a Microgeração e Minigeração Distribuída (MMGD), tem ganhado destaque no Brasil, impulsionada por incentivos regulatórios e pela redução de custos de tecnologias como a solar fotovoltaica. As definições e os limites de potência para MMGD são estabelecidos pela ANEEL e são fundamentais para o dimensionamento de projetos de geração junto à carga.  
Conforme a REN ANEEL nº 1.000/2021 e suas atualizações, notadamente a REN nº 1.059/2023 4, a MMGD é classificada da seguinte forma:

* **Microgeração Distribuída (MicroGD):** Central geradora de energia elétrica, com potência instalada em corrente alternada **menor ou igual a 75 kW**, conectada na rede de distribuição por meio de instalações de unidades consumidoras e que utilize fontes renováveis ou cogeração qualificada.4  
* **Minigeração Distribuída (MiniGD):** Central geradora com potência instalada em corrente alternada **superior a 75 kW e menor ou igual a**:  
  * **5 MW** para fontes despacháveis (exceto fotovoltaica).  
  * **3 MW** para demais fontes não classificadas como despacháveis e para usinas fotovoltaicas classificadas como despacháveis.  
  * Existem regras específicas para unidades consumidoras conectadas ou com solicitação de acesso protocolada até 7 de janeiro de 2023, que podem manter o limite de 5 MW para fontes renováveis.4

A Tabela 2 sumariza estas definições.  
**Tabela 2: Definições Regulatórias de Microgeração e Minigeração Distribuída (ANEEL)**

| Categoria | Limite de Potência Instalada (kW/MW) | Fontes Elegíveis | Resolução ANEEL de Referência (Principal) |
| :---- | :---- | :---- | :---- |
| MicroGD | $\\le 75 \\text{ kW}$ | Renováveis, Cogeração Qualificada | REN nº 1.000/2021, REN nº 1.059/2023 |
| MiniGD | $\> 75 \\text{ kW}$ e $(\\le 3 \\text{ MW}$ para solar e não despacháveis; ou $\\le 5 \\text{ MW}$ para despacháveis, com especificidades para conexões anteriores a Jan/2023) | Renováveis, Cogeração Qualificada | REN nº 1.000/2021, REN nº 1.059/2023 |

A interpretação do "limite da Mini GD" mencionado no tier XGG (200.001 a 500.000 kWh/mês) fornecido pelo usuário requer atenção. Uma unidade consumidora com consumo mensal de 500.000 kWh, operando continuamente (720 horas/mês), teria uma demanda média de aproximadamente $500.000 \\text{ kWh} / 720 \\text{ h} \\approx 694 \\text{ kW}$. Se considerarmos um fator de carga de 0.7 (típico para algumas indústrias com operação intensiva), a demanda máxima seria de aproximadamente $694 \\text{ kW} / 0.7 \\approx 991 \\text{ kW}$ (ou 0,99 MW). Este valor de potência está confortavelmente dentro dos limites de potência da MiniGD (que vai até 3 MW ou 5 MW).  
No entanto, o termo "limite da Mini GD" pode também se referir à *energia gerada* por um projeto de MiniGD. Um sistema de MiniGD solar fotovoltaico com 3 MW de potência instalada (limite para esta fonte), operando com um fator de capacidade (FC) de 23% (uma média razoável para boas regiões de irradiação no Brasil), geraria aproximadamente $3.000 \\text{ kW} \\times 0,23 \\times 720 \\text{ horas/mês} \= 496.800 \\text{ kWh/mês}$. Este valor é notavelmente próximo do limite superior do tier XGG (500.000 kWh/mês). Portanto, é plausível que a menção ao "limite da Mini GD" no tier XGG se refira mais à capacidade de geração/consumo de um projeto de MiniGD solar de porte considerável, próximo ao teto regulatório de potência para essa fonte, do que a uma conversão direta do limite máximo de potência da MiniGD (5 MW) em consumo energético. Este relatório adotará essa interpretação, esclarecendo que os tiers superiores (G, GG, XG, XGG) representam faixas de consumo de grandes unidades consumidoras que são candidatas a projetos de MiniGD ou autoprodução, ou faixas de energia gerada/consumida por projetos de MiniGD de porte relevante.

## **3\. Metodologia para o Desdobramento de Tiers e Correlação com Porte de Projeto**

A criação de tiers de consumo mais granulares e sua correlação com o porte de projetos exige uma metodologia clara, especialmente na conversão entre energia (kWh/mês) e potência (kW/MW), e na definição dos novos limites de cada sub-tier.

### **3.1. Relação entre Consumo de Energia (kWh/mês) e Demanda de Potência (kW/MW)**

A energia elétrica consumida (E, em kWh) é o produto da potência elétrica (P, em kW) pelo tempo de utilização (t, em horas): $E \= P \\times t$. Para converter um consumo mensal de energia em uma estimativa de potência, é necessário considerar o perfil de uso dessa energia ao longo do mês.  
Um conceito fundamental nesta conversão é o **Fator de Carga (FC)**. O FC é a razão entre a energia efetivamente consumida em um período e a energia que seria consumida se a demanda máxima fosse mantida constante durante todo esse período.2 Matematicamente:  
$FC \= \\text{Energia Consumida (kWh)} / (\\text{Potência de Demanda Máxima (kW)} \\times \\text{Período (h)})$  
O FC varia consideravelmente entre diferentes tipos de consumidores (residenciais, comerciais, industriais) e até mesmo para um mesmo consumidor dependendo do dia da semana, da estação do ano ou de processos produtivos específicos. Um FC baixo (e.g., 0,2-0,3) indica que a demanda máxima ocorre por poucas horas, enquanto um FC alto (e.g., 0,7-0,9) sugere uma utilização mais constante da potência próxima à máxima.  
A partir do consumo mensal, pode-se calcular a **Potência Média (Pméd)**:  
$P\_{méd} \\text{ (kW)} \= \\text{Consumo Mensal (kWh)} / \\text{Horas no Mês}$  
Considerando um mês com 720 horas (30 dias x 24 horas/dia), esta é uma estimativa da potência que, se mantida constante, resultaria no consumo mensal observado.  
No entanto, para o dimensionamento de projetos e para a caracterização de consumidores do Grupo A (que pagam por demanda), a **Potência de Demanda Máxima (Pmáx)** é o parâmetro mais relevante. Ela pode ser estimada a partir do consumo mensal e de um FC típico para o perfil de consumidor:  
Pmaˊx​ (kW)=Consumo Mensal (kWh)/(FC×Horas no Meˆs)  
Ou, de forma equivalente:  
Pmaˊx​ (kW)=Pmeˊd​ (kW)/FC  
A "Carga Instalada", que é a soma das potências nominais dos equipamentos 2, é outro parâmetro relevante, mas menos direto para estimar a demanda faturável ou a potência de projeto, pois nem todos os equipamentos operam simultaneamente ou em sua potência nominal.  
A escolha do Fator de Carga é, portanto, o elemento mais crítico e que introduz a maior variabilidade na conversão de kWh para kW para os novos tiers, especialmente para consumidores do Grupo B, onde a demanda não é um parâmetro contratual. Para consumidores do Grupo A, a demanda contratada já existe, mas para fins de uma classificação geral baseada em consumo, a utilização de um FC típico ainda é útil para estimar a potência de referência. Este relatório será transparente quanto às premissas de FC utilizadas para cada perfil de consumidor e, sempre que possível, apresentará faixas de potência (mínima e máxima) para cada tier de consumo, refletindo diferentes FCs típicos. Informações de estudos da Empresa de Pesquisa Energética (EPE) sobre perfis de carga setoriais 6 e sobre consumidores que adotam MMGD 9 serão consideradas para embasar as premissas de FC.

### **3.2. Abordagem para Subdivisão dos Tiers Existentes**

Os tiers de consumo de referência, especialmente os de maior porte (G, GG, XG, XGG), abrangem faixas muito amplas, o que justifica sua subdivisão para uma análise mais refinada. A criação dos novos sub-tiers seguirá os seguintes critérios:

1. **Progressão Lógica:** Manter uma progressão nos limites de consumo que seja intuitiva e, sempre que possível, siga uma lógica aritmética ou geométrica aproximada, evitando saltos desproporcionais.  
2. **Relevância Prática e Regulatória:** Alinhar os novos limites com portes típicos de equipamentos disponíveis no mercado (ex: capacidades de inversores solares, transformadores), com limites regulatórios importantes (como o de 75 kW que separa MicroGD de MiniGD 4), e com perfis de consumo de subsegmentos de mercado identificáveis (ex: diferenciar um pequeno comércio de um supermercado, ou uma pequena indústria de uma de médio porte).  
3. **Equilíbrio entre Granularidade e Praticidade:** O objetivo é oferecer maior detalhe, mas sem criar um número excessivo de tiers que torne a classificação complexa e de difícil utilização. Tipicamente, cada tier original será desdobrado em 2 a 4 sub-tiers.

A subdivisão não será arbitrária; cada ponto de corte buscará refletir um ponto de inflexão significativo no mercado ou na regulação. Por exemplo, o limite de 75 kW para MicroGD, que corresponde a uma geração/consumo mensal na ordem de 10.000 a 13.500 kWh/mês (dependendo do FC da fonte e do perfil de uso), é um balizador natural. Consumidores com consumo nessa faixa são candidatos a projetos de MicroGD próximos ao limite máximo da categoria, justificando um sub-tier específico. Da mesma forma, faixas de consumo que tipicamente habilitam um consumidor a migrar para o mercado livre de energia ou que correspondem a portes comuns de projetos de eficiência energética também serão consideradas.

## **4\. Proposta de Tiers Granulares para Consumo e Porte de Projetos de Energia**

Com base na metodologia descrita, esta seção apresenta a proposta de desdobramento dos tiers de consumo de energia. A Tabela 3 detalha os novos sub-tiers, suas faixas de consumo, a estimativa da potência média e da potência de demanda máxima equivalentes (com as respectivas premissas de Fator de Carga), o perfil típico de consumidor ou projeto associado, e exemplos de aplicação em projetos energéticos.  
As estimativas de Potência de Demanda Máxima são cruciais para o dimensionamento de projetos e foram calculadas utilizando faixas de Fatores de Carga (FC) consideradas representativas para os perfis de consumidores predominantes em cada tier. A Potência Média é calculada como Consumo Mensal (kWh) / 720 horas. A Potência de Demanda Máxima é calculada como Potência Média / FC.  
**Premissas de Fator de Carga (FC) Utilizadas para Estimativa da Potência de Demanda Máxima:**

* **Tiers PP e P (predominantemente Residenciais e Pequeno Comércio de baixo consumo):** FC entre 0,20 e 0,35. Um FC médio de 0,275 é usado para referência.  
* **Tiers M (Residencial de alto padrão, Comércio e Serviços de pequeno a médio porte):** FC entre 0,25 e 0,45. Um FC médio de 0,35 é usado para referência.  
* **Tiers G (Comércio de médio porte, Pequenas Indústrias, Serviços maiores):** FC entre 0,30 e 0,55. Um FC médio de 0,425 é usado para referência.  
* **Tiers GG (Comércio de grande porte, Indústrias de médio porte):** FC entre 0,40 e 0,70. Um FC médio de 0,55 é usado para referência.  
* **Tiers XG e XGG (Indústrias de grande e muito grande porte, Data Centers, grandes Shoppings):** FC entre 0,50 e 0,85. Um FC médio de 0,675 é usado para referência.

É importante ressaltar que estas são faixas gerais. O FC real de uma unidade consumidora específica pode variar significativamente.  
**Tabela 3: Proposta de Tiers Granulares de Consumo de Energia e Porte de Projeto Equivalente**

| Novo Tier ID | Tier Original | Faixa de Consumo (kWh/mês) | Potência Média Estimada (kW) (Consumo/720h) | Faixa de Potência de Demanda Máxima Estimada (kW) (Baseada no FC) | Perfil Típico de Consumidor/Projeto | Exemplos de Aplicação em Projetos |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| PP1 | PP | Até 150 | Até 0,21 | 0,6 – 1,0 | Residencial básico (baixo consumo), kitnet, pequena sala comercial (pouco uso) | Eficiência energética (iluminação LED, eletrodomésticos eficientes), conscientização sobre uso. |
| PP2 | PP | 151 a 300 | 0,21 a 0,42 | 1,0 – 2,1 | Residencial básico/padrão, pequeno escritório individual | Idem PP1, pequenos sistemas fotovoltaicos (1-2 kWp) para abatimento parcial da conta. |
| P1 | P | 301 a 500 | 0,42 a 0,69 | 1,7 – 3,5 | Residencial padrão/médio, pequeno comércio (loja de bairro, salão de beleza pequeno) | MicroGD Fotovoltaica (2-4 kWp), aquecimento solar de água, gestão de horários de uso. |
| P2 | P | 501 a 700 | 0,69 a 0,97 | 2,8 – 4,9 | Residencial médio/alto, comércio de bairro (padaria pequena, mini mercado) | MicroGD Fotovoltaica (4-6 kWp), análise de viabilidade para tarifa branca (se disponível). |
| M1 | M | 701 a 1.200 | 0,97 a 1,67 | 3,0 – 6,7 | Residencial alto padrão, comércio (restaurante pequeno, loja de conveniência, escritório pequeno) | MicroGD Fotovoltaica (5-10 kWp), automação para eficiência energética, substituição de equipamentos antigos. |
| M2 | M | 1.201 a 2.000 | 1,67 a 2,78 | 5,1 – 11,1 | Residencial muito alto padrão (com piscina, ar condicionado central), comércio (clínica pequena, academia pequena) | MicroGD Fotovoltaica (10-15 kWp), gestão de demanda (se Grupo A), análise para mercado livre (se elegível por demanda). |
| G1 | G | 2.001 a 5.000 | 2,78 a 6,94 | 6,5 – 23,1 | Comércio (supermercado pequeno, restaurante médio, escritórios médios), pequena indústria (oficina, marcenaria) | MicroGD Fotovoltaica (15-40 kWp), projetos de eficiência em HVAC e refrigeração, possível enquadramento no Grupo A (baixa demanda). |
| G2 | G | 5.001 a 10.000 | 6,94 a 13,89 | 16,3 – 46,3 | Comércio (loja de departamento pequena, hotel pequeno), indústria leve, condomínios residenciais/comerciais | MicroGD Fotovoltaica (até 75 kWp), início da faixa de MiniGD (\>75kWp se FC baixo e consumo no teto do tier), análise de migração para o Mercado Livre (consumidores do Grupo A). |
| GG1 | GG | 10.001 a 25.000 | 13,89 a 34,72 | 25,3 – 86,8 | Comércio (supermercado médio, shopping pequeno), indústria de porte médio (alimentos, têxtil), hospitais pequenos | MiniGD Fotovoltaica (75-200 kWp), projetos de cogeração de pequeno porte, otimização de contrato de demanda (Grupo A). |
| GG2 | GG | 25.001 a 50.000 | 34,72 a 69,44 | 63,1 – 173,6 | Comércio (centro de distribuição pequeno, hotel médio), indústria de porte médio (metalúrgica, plásticos) | MiniGD Fotovoltaica (200-400 kWp), autoprodução de energia, contratos de energia no Mercado Livre. |
| XG1 | XG | 50.001 a 100.000 | 69,44 a 138,89 | 106,8 – 347,2 | Indústria de grande porte, comércio (shopping center médio, grandes redes varejistas), data centers pequenos | MiniGD (400 kWp \- 1 MWp), soluções de armazenamento de energia, gestão energética avançada. |
| XG2 | XG | 100.001 a 200.000 | 138,89 a 277,78 | 213,7 – 694,4 | Indústria de grande porte (química, automobilística leve), grandes edifícios comerciais, hospitais grandes | MiniGD (1 MWp \- 2 MWp), projetos de eficiência energética em processos industriais, autoprodução remota. |
| XGG1 | XGG | 200.001 a 350.000 | 277,78 a 486,11 | 347,2 – 1.215,3 | Indústria de muito grande porte (siderurgia leve, cimento), data centers médios, grandes complexos comerciais | MiniGD (até 3 MWp para solar, ou maior para outras fontes), contratos de longo prazo no ACL, possibilidade de consumidor especial. |
| XGG2 | XGG | 350.001 a 500.000 | 486,11 a 694,44 | 607,6 – 1.736,1 | Indústria de muito grande porte (papel e celulose, mineração leve), grandes data centers | MiniGD próximo ao limite superior para solar (3 MWp) ou projetos maiores com outras fontes (até 5 MWp), autoprodução em larga escala. Interpretação do "limite da Mini GD" como geração/consumo de um projeto de MiniGD solar de grande porte. |
| XGG+1 | Acima de XGG | 500.001 a 1.000.000 | 694,44 a 1.388,89 | 868,1 – 3.472,2 | Grandes complexos industriais, indústrias eletrointensivas | Projetos de MiniGD de grande porte (até 5 MW), autoprodução, contratos de energia complexos no ACL. |
| XGG+2 | Acima de XGG | Acima de 1.000.000 | Acima de 1.388,89 | Acima de 1.736,1 (FC 0.8) / Acima de 2.777,8 (FC 0.5) | Indústrias eletrointensivas de grande porte (alumínio, siderurgia pesada) | Soluções energéticas de alta complexidade, grandes projetos de autoprodução, participação ativa no mercado de energia. |

A subdivisão proposta busca um equilíbrio entre detalhamento e usabilidade. A granularidade aumenta nos tiers de consumo mais elevados (G, GG, XG, XGG), onde a diversidade de perfis de consumidores e a complexidade dos projetos energéticos são maiores. Os tiers menores (PP, P) também foram subdivididos para melhor refletir diferentes níveis dentro do consumo residencial e de microcomércios. Foram adicionados tiers "XGG+" para contemplar consumidores com consumo superior ao limite de 500.000 kWh/mês originalmente proposto, que são relevantes no cenário industrial brasileiro.  
A correlação com a potência equivalente, mesmo que estimada, é fundamental para a aplicabilidade da classificação a "tamanhos de projetos", como solicitado. A caracterização do perfil típico de consumidor e os exemplos de aplicação visam enriquecer a compreensão de cada novo tier.

## **5\. Caracterização Detalhada dos Novos Tiers Propostos**

A Tabela 3 introduziu os novos tiers granulares. Esta seção aprofunda a caracterização de cada um, explorando os perfis de consumidores, implicações regulatórias e a adequação para diferentes tipos de projetos energéticos, com base em informações de estudos setoriais e regulamentações.  
**Tiers PP1 e PP2 (Até 300 kWh/mês):**

* **Perfil Típico:** Predominantemente consumidores residenciais do Subgrupo B1, desde unidades de baixíssimo consumo (PP1) até residências com um padrão básico de eletrodomésticos (PP2).1 Pequenas salas comerciais ou escritórios individuais com uso esporádico também podem se enquadrar. O Atlas da Eficiência Energética da EPE indica que o consumo residencial médio varia regionalmente, mas esses tiers representam a base da pirâmide de consumo.8  
* **Implicações Regulatórias:** Geralmente atendidos em baixa tensão (Grupo B), com tarifa monômia. Consumidores no PP1 podem ser elegíveis à Tarifa Social de Energia Elétrica, dependendo de critérios socioeconômicos.  
* **Aplicações em Projetos:** O foco é em eficiência energética (lâmpadas LED, geladeiras eficientes) e conscientização sobre o uso racional da energia. Para o PP2, microgeração fotovoltaica de pequena capacidade (1 a 2 kWp) pode começar a ser considerada para abatimento parcial da fatura, especialmente em regiões com alta irradiação solar e tarifas elevadas.

**Tiers P1 e P2 (301 a 700 kWh/mês):**

* **Perfil Típico:** Consumidores residenciais de padrão médio a alto (P1 e P2), com maior quantidade de eletrodomésticos e possível uso de ar condicionado. Pequenos comércios de bairro (lojas, salões de beleza, padarias artesanais) também se situam aqui.1 O estudo da ABRACEEL sobre o potencial de migração para o mercado livre inclui pequenos negócios nestas faixas de consumo como potenciais beneficiários no futuro.11  
* **Implicações Regulatórias:** Continuam majoritariamente no Grupo B (Subgrupo B1 ou B3). A tarifa branca pode ser uma opção a ser avaliada para consumidores com flexibilidade de horário de consumo.  
* **Aplicações em Projetos:** Microgeração fotovoltaica (2 a 6 kWp) torna-se mais atrativa. Projetos de aquecimento solar de água podem reduzir significativamente o consumo elétrico. A gestão de horários de uso de equipamentos de maior potência (chuveiros, máquinas de lavar) ganha relevância.

**Tiers M1 e M2 (701 a 2.000 kWh/mês):**

* **Perfil Típico:** Residenciais de alto padrão, com uso intensivo de climatização, piscinas aquecidas, ou múltiplos moradores (M1, M2). No setor comercial, abrange restaurantes e escritórios de pequeno porte, clínicas, academias de bairro e lojas de conveniência.6 A pesquisa PPH Comercial 2023 do MME/ENBPar detalha hábitos de consumo para diversos segmentos comerciais que se encaixam aqui.13  
* **Implicações Regulatórias:** Predominantemente Grupo B. Alguns consumidores no limite superior do M2, especialmente se tiverem uma demanda mais concentrada, poderiam, em tese, ter uma demanda que justificaria uma análise para o Grupo A, mas isso é menos comum para esta faixa de *consumo*.  
* **Aplicações em Projetos:** Microgeração fotovoltaica (5 a 15 kWp) é comum. Automação residencial/comercial para otimizar o consumo de iluminação e HVAC. Para consumidores comerciais, a substituição de equipamentos antigos por modelos mais eficientes (freezers, fornos) pode gerar economias expressivas.

**Tiers G1 e G2 (2.001 a 10.000 kWh/mês):**

* **Perfil Típico:** Supermercados pequenos e médios, restaurantes maiores, escritórios de médio porte, clínicas com equipamentos de imagem, pequenas indústrias (confecções, oficinas mecânicas, marcenarias, pequenas gráficas), e condomínios residenciais ou comerciais.6 O consumo industrial aqui ainda é de pequena escala.  
* **Implicações Regulatórias:** Transição entre Grupo B e Grupo A. Consumidores no G1 podem ainda estar no Grupo B (B3), mas muitos no G2, especialmente indústrias ou comércios com máquinas de maior potência, já estarão no Grupo A (Subgrupo A4), com tarifação binômia. A elegibilidade para o Mercado Livre de Energia (ACL) para consumidores do Grupo A com demanda inferior a 500 kW já é uma realidade, tornando esta faixa interessante para comercializadoras.  
* **Aplicações em Projetos:** Microgeração fotovoltaica de maior porte (15 a 75 kWp, limite da MicroGD). Para consumidores no G2, projetos de MiniGD (acima de 75 kWp) podem ser considerados se o consumo estiver no teto do tier e o fator de carga permitir. Projetos de eficiência energética em sistemas de refrigeração comercial, motores industriais e iluminação de grandes áreas. Análise de migração para o ACL é altamente recomendada para os consumidores do Grupo A.

**Tiers GG1 e GG2 (10.001 a 50.000 kWh/mês):**

* **Perfil Típico:** Supermercados de porte médio a grande, pequenos shopping centers, hotéis, hospitais de pequeno e médio porte. Indústrias de porte médio em setores como alimentos e bebidas, têxtil, plástico, metalurgia leve.6 A EPE, em seus estudos sobre MMGD, identifica consumidores comerciais e industriais de média tensão (Grupo A) como adotantes de geração distribuída.9  
* **Implicações Regulatórias:** Quase que exclusivamente consumidores do Grupo A (Subgrupo A4 ou A3a), com demanda contratada significativa. Plenamente elegíveis para o Mercado Livre de Energia.  
* **Aplicações em Projetos:** Projetos de MiniGD fotovoltaica (75 kWp a 400 kWp) para autoconsumo local ou remoto. Pequenos projetos de cogeração a biomassa ou gás natural. Otimização da demanda contratada e correção do fator de potência são cruciais. Contratos de compra de energia no ACL são a norma.

**Tiers XG1 e XG2 (50.001 a 200.000 kWh/mês):**

* **Perfil Típico:** Indústrias de grande porte (química, automobilística leve, autopeças, cerâmica). Grandes redes varejistas, shopping centers de porte médio a grande, edifícios comerciais de múltiplos andares, hospitais de referência, e data centers de pequeno a médio porte.6 O consumo industrial aqui já é considerável, com processos produtivos que demandam muita energia.  
* **Implicações Regulatórias:** Consumidores do Grupo A (Subgrupos A4, A3a, A3), com alta demanda contratada. Atuam ativamente no Mercado Livre de Energia.  
* **Aplicações em Projetos:** Projetos de MiniGD de porte significativo (400 kWp a 2 MWp). Soluções de armazenamento de energia (baterias) para *peak shaving* ou otimização do uso da energia de GD podem ser viáveis.10 Gestão energética avançada com sistemas de monitoramento e controle. Autoprodução remota através de consórcios ou SPEs.

**Tiers XGG1 e XGG2 (200.001 a 500.000 kWh/mês):**

* **Perfil Típico:** Indústrias de muito grande porte (siderurgia leve, cimento, papel e celulose de menor escala, grandes complexos alimentícios). Data centers de porte considerável e grandes complexos comerciais ou de serviços.6 Como discutido, o limite superior (500.000 kWh/mês) aproxima-se da geração mensal de um projeto de MiniGD solar de 3 MWp com bom fator de capacidade.  
* **Implicações Regulatórias:** Consumidores do Grupo A (Subgrupos A3a, A3, A2), classificados como grandes consumidores de energia. Podem ser consumidores especiais ou livres, com alta sofisticação na gestão de seus contratos de energia.  
* **Aplicações em Projetos:** Projetos de MiniGD próximos ao limite regulatório de potência (3 MWp para solar, ou até 5 MWp para outras fontes como biomassa). Autoprodução em larga escala, possivelmente em outras localidades (autoconsumo remoto). Contratos de energia de longo prazo e estruturados no ACL.

**Tiers XGG+1 e XGG+2 (Acima de 500.000 kWh/mês):**

* **Perfil Típico:** Grandes complexos industriais e indústrias eletrointensivas (alumínio primário, cloro-soda, siderurgia pesada, grandes plantas de papel e celulose, mineração).6 Estes consumidores possuem um peso significativo no consumo industrial total do país.  
* **Implicações Regulatórias:** Consumidores do Grupo A (Subgrupos A2, A1), com demandas que podem ultrapassar dezenas ou centenas de MW. São os maiores players no Mercado Livre de Energia.  
* **Aplicações em Projetos:** Projetos de MiniGD no limite máximo de 5 MW ou múltiplos projetos. Grandes projetos de autoprodução, muitas vezes com usinas dedicadas. Participação ativa no mercado de energia, com estratégias sofisticadas de hedging e gestão de risco. Soluções de eficiência energética de alta complexidade e customização para processos industriais específicos.

A tentativa de quantificar a participação de cada classe (Residencial, Comercial, Industrial) dentro de cada novo tier é um desafio considerável devido à disponibilidade de dados públicos. Anuários Estatísticos da EPE apresentam o número total de consumidores por classe e o consumo total por classe 14, mas a distribuição do *número de unidades consumidoras por faixas de consumo específicas* dentro de cada classe não é trivialmente acessível. Caso os workbooks detalhados da EPE 15 ou futuras pesquisas como a PPH Comercial 13 venham a disponibilizar essa granularidade, seria possível construir uma Tabela 4 com a distribuição estimada de UCs, o que enriqueceria enormemente a análise de mercado para cada tier. Sem esses dados consolidados, a caracterização acima se baseia na predominância esperada e em exemplos setoriais.  
Esta caracterização detalhada, ao cruzar os tiers de consumo/potência com perfis setoriais e tecnologias energéticas, permite identificar "clusters" de oportunidades. Por exemplo, um determinado sub-tier do Grupo M pode concentrar um grande número de pequenos comércios com telhados adequados para MicroGD, enquanto um sub-tier do Grupo GG pode ser dominado por indústrias com alta demanda no horário de ponta, tornando-as candidatas ideais para projetos de GD com armazenamento ou gestão ativa da demanda.

## **6\. Implicações e Aplicações Práticas dos Tiers Granulares**

A adoção de um sistema de tiers de consumo e porte de projeto mais granular, como o proposto, transcende a mera classificação acadêmica, oferecendo implicações e aplicações práticas significativas para diversos agentes do setor elétrico brasileiro.  
Segmentação de Mercado e Estratégias Comerciais:  
Empresas como comercializadoras de energia, Empresas de Serviços de Conservação de Energia (ESCOs), desenvolvedores de projetos de GD e fornecedores de equipamentos podem utilizar os tiers granulares para refinar suas estratégias de marketing e vendas. Ao compreender melhor as faixas de consumo e as potências equivalentes de diferentes subsegmentos, é possível direcionar ofertas de produtos e serviços de forma mais assertiva. Por exemplo, uma campanha de marketing para sistemas fotovoltaicos pode ser customizada para os tiers P2 e M1 (foco residencial e pequeno comercial com telhado), enquanto soluções de gestão de demanda e contratos no mercado livre podem ser direcionadas aos tiers G2, GG e superiores. Esta granularidade permite identificar nichos de mercado que poderiam estar subatendidos pelas abordagens mais genéricas.  
Desenvolvimento de Produtos e Serviços Customizados:  
Os tiers propostos podem orientar o desenvolvimento de soluções energéticas mais adequadas às necessidades específicas de cada perfil de consumo e porte. Pacotes de MicroGD podem ser dimensionados para atender ao consumo típico dos tiers P e M, enquanto soluções de MiniGD podem ser escalonadas para os tiers G, GG e XG. Contratos de fornecimento de energia no Mercado Livre podem ser estruturados com cláusulas e preços mais aderentes aos padrões de consumo e demanda dos tiers GG e XG, por exemplo. Ofertas de eficiência energética podem ser focadas em equipamentos ou processos críticos para determinados tiers (ex: refrigeração para tiers comerciais G1/GG1, motores para tiers industriais GG/XG).  
Análise de Viabilidade de Projetos Energéticos:  
A classificação auxilia na pré-avaliação da atratividade técnica e econômica de diversos projetos. Um desenvolvedor de projetos de GD pode rapidamente identificar os tiers de consumidores que possuem um consumo compatível com a geração de sistemas de Micro ou Minigeração. A estimativa de potência equivalente associada a cada tier facilita o dimensionamento preliminar de sistemas e a análise de payback. Para consumidores, entender em qual tier se enquadram pode ser o primeiro passo para avaliar a viabilidade de instalar um sistema de GD, implementar medidas de eficiência mais robustas ou considerar a migração para o Mercado Livre de Energia, como destacado por estudos da ABRACEEL que mostram o potencial de economia para diversos perfis do Grupo B.11  
Planejamento da Expansão e Operação da Rede pelas Distribuidoras:  
Embora não seja o foco principal desta análise, as distribuidoras de energia podem, em tese, utilizar uma segmentação mais granular para aprimorar suas previsões de demanda em áreas específicas e planejar investimentos na rede de distribuição de forma mais otimizada. A identificação de concentrações de consumidores em tiers com alto potencial de adoção de GD, por exemplo, pode sinalizar a necessidade de reforços na rede local.  
Formulação de Políticas Energéticas e Programas de Incentivo:  
Órgãos governamentais e agências reguladoras podem se beneficiar dos tiers granulares para desenhar políticas públicas e programas de incentivo mais eficazes e direcionados. Por exemplo, subsídios para a aquisição de sistemas de MicroGD poderiam ser focados em consumidores dos tiers P1 a M2. Metas de eficiência energética poderiam ser estabelecidas de forma diferenciada para os diversos tiers industriais (GG, XG, XGG), considerando suas particularidades de consumo e potencial de economia. A Pesquisa de Posse e Hábitos de Uso de Equipamentos Elétricos na Classe Comercial (PPH Comercial), mencionada pelo MME 13, já visa subsidiar o planejamento e as ações de eficiência, e uma classificação granular de consumo pode potencializar o uso desses dados.  
A utilização de tiers mais detalhados pode, portanto, contribuir para um mercado de energia mais eficiente, competitivo e alinhado com as necessidades específicas de uma base de consumidores cada vez mais diversificada e consciente de suas opções energéticas.

## **7\. Conclusões e Recomendações**

Este relatório apresentou uma proposta de desdobramento dos tiers de consumo de energia elétrica em um sistema mais granular, correlacionando o consumo mensal (kWh/mês) com estimativas de potência de projeto (kW/MW). A metodologia buscou alinhar os novos sub-tiers com marcos regulatórios, portes típicos de equipamentos e perfis de consumo setoriais, visando aumentar a aplicabilidade prática da classificação no setor elétrico brasileiro.  
**Principais Conclusões:**

1. **Necessidade de Granularidade:** As classificações de consumo amplas existentes limitam a análise detalhada e o desenvolvimento de soluções energéticas customizadas. O desdobramento proposto oferece um nível de detalhe que pode beneficiar diversos agentes do setor.  
2. **Correlação Consumo-Potência:** A conversão de consumo (energia) para potência (demanda) é fundamental para a aplicação em "tamanhos de projetos". O Fator de Carga é o elemento chave nessa conversão, e suas variações entre perfis de consumidores foram consideradas na estimativa das faixas de potência para cada novo tier.  
3. **Alinhamento com o Setor:** Os novos tiers foram desenhados para refletir pontos de inflexão relevantes, como os limites da Micro e Minigeração Distribuída 4, e para caracterizar perfis de consumidores residenciais, comerciais e industriais com base em dados e estudos setoriais.6  
4. **Aplicabilidade Prática:** A classificação granular tem implicações diretas para segmentação de mercado, desenvolvimento de produtos, análise de viabilidade de projetos (GD, eficiência, migração ao ACL) e formulação de políticas energéticas.

**Recomendações:**

* **Para Empresas do Setor Elétrico (Comercializadoras, ESCOs, Desenvolvedores, Fornecedores):**  
  * Utilizar os tiers granulares propostos como ferramenta para refinar a segmentação de clientes e direcionar estratégias de marketing e vendas.  
  * Desenvolver portfólios de produtos e serviços energéticos (GD, eficiência, consultoria em ACL) customizados para as características e necessidades dos diferentes sub-tiers.  
  * Incorporar a classificação na análise preliminar de viabilidade de projetos, otimizando a alocação de recursos.  
* **Para Formuladores de Políticas e Órgãos Reguladores:**  
  * Considerar a utilização de tiers de consumo mais granulares no desenho de programas de incentivo à Geração Distribuída e à eficiência energética, permitindo um direcionamento mais eficaz dos recursos.  
  * Utilizar a segmentação para monitorar a evolução do mercado e o impacto de novas regulações sobre diferentes perfis de consumidores.  
* **Para Consumidores de Energia Elétrica:**  
  * Identificar seu enquadramento nos novos tiers para obter uma melhor compreensão de seu perfil de consumo e potência.  
  * Utilizar essa autoavaliação como ponto de partida para explorar soluções energéticas mais vantajosas, como a instalação de sistemas de GD, a implementação de medidas de eficiência ou a análise de migração para o Mercado Livre de Energia (quando aplicável).

**Sugestões para Futuras Análises e Coleta de Dados:**

1. **Aprimoramento de Dados Públicos:** Existe uma necessidade premente de maior disponibilidade de dados públicos sobre a distribuição quantitativa de unidades consumidoras por faixas de consumo específicas (kWh/mês) e por classe (residencial, comercial, industrial, rural) em nível nacional e regional. A disponibilização desses dados por órgãos como ANEEL e EPE (possivelmente através dos workbooks do Anuário Estatístico de Energia Elétrica 15) enriqueceria significativamente a caracterização e a aplicação dos tiers.  
2. **Validação de Fatores de Carga:** Realizar pesquisas e estudos de campo para validar e refinar os Fatores de Carga típicos utilizados na conversão consumo-potência para os diferentes perfis de consumidores e sub-tiers.  
3. **Análises Regionais e Geoespaciais:** Cruzar a classificação por tiers com dados geográficos e socioeconômicos para identificar particularidades regionais e oportunidades localizadas de desenvolvimento de projetos energéticos.  
4. **Atualização Dinâmica:** O setor elétrico é altamente dinâmico. Novas tecnologias, alterações regulatórias (como a expansão contínua da elegibilidade ao ACL) e mudanças nos padrões de consumo (ex: eletrificação da frota veicular) exigirão revisões e atualizações periódicas desta classificação para que ela mantenha sua relevância e precisão.

Em suma, a proposta de tiers granulares apresentada neste relatório visa oferecer uma contribuição analítica para um melhor entendimento da diversidade de consumidores e projetos no setor elétrico brasileiro, fomentando o desenvolvimento de soluções mais eficientes e customizadas.

#### **Referências citadas**

1. Resolução Normativa Aneel Nº 1.000, de 7 de Dezembro de 2021 \- Agência Nacional de Energia Elétrica, acessado em maio 11, 2025, [https://www2.aneel.gov.br/cedoc/ren20211000.html](https://www2.aneel.gov.br/cedoc/ren20211000.html)  
2. www.mpmg.mp.br, acessado em maio 11, 2025, [https://www.mpmg.mp.br/data/files/97/95/BE/8F/E944A7109CEB34A7760849A8/Perguntas%20e%20Respostas\_Energia%20El\_trica\_Condi\_\_es%20gerais\_%20conforme%20Resolu\_\_o%20Normativa%20Aneel%20n\_%20414\_%20de%2009%20de%20setembro%20de%202010\_Procon-MG\_15%20de.pdf](https://www.mpmg.mp.br/data/files/97/95/BE/8F/E944A7109CEB34A7760849A8/Perguntas%20e%20Respostas_Energia%20El_trica_Condi__es%20gerais_%20conforme%20Resolu__o%20Normativa%20Aneel%20n_%20414_%20de%2009%20de%20setembro%20de%202010_Procon-MG_15%20de.pdf)  
3. www2.aneel.gov.br, acessado em maio 11, 2025, [https://www2.aneel.gov.br/cedoc/res2000456.pdf](https://www2.aneel.gov.br/cedoc/res2000456.pdf)  
4. resolução normativa aneel nº 1.059, de 7 de fevereiro de 2023, acessado em maio 11, 2025, [https://www2.aneel.gov.br/cedoc/ren20231059.html](https://www2.aneel.gov.br/cedoc/ren20231059.html)  
5. Mini e microgeração distribuída – conecte-se a nossa rede\! \- Cemig, acessado em maio 11, 2025, [https://www.cemig.com.br/mini-e-microgeracao-distribuida/](https://www.cemig.com.br/mini-e-microgeracao-distribuida/)  
6. Anuário Estatístico de Energia Elétrica 2023, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-160/topico-168/anuario-factsheet.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-160/topico-168/anuario-factsheet.pdf)  
7. www.epe.gov.br, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-423/topico-481/02%20Demandada%20de%20Energia.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-423/topico-481/02%20Demandada%20de%20Energia.pdf)  
8. www.epe.gov.br, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-857/Atlas%20da%20Efici%C3%AAncia%20Energ%C3%A9tica%20Brasil%202024.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-857/Atlas%20da%20Efici%C3%AAncia%20Energ%C3%A9tica%20Brasil%202024.pdf)  
9. www.epe.gov.br, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-423/topico-488/NT\_Metodologia\_4MD\_PDE\_2029.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-423/topico-488/NT_Metodologia_4MD_PDE_2029.pdf)  
10. www.epe.gov.br, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-804/topico-709/Caderno\_MMGD\_Baterias\_PDE2034\_(20240702).pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-804/topico-709/Caderno_MMGD_Baterias_PDE2034_\(20240702\).pdf)  
11. Além do Grupo A: quem são e quanto poupariam os consumidores ..., acessado em maio 11, 2025, [https://abraceel.com.br/destaques/2024/03/alem-do-grupo-a-quem-sao-e-quanto-poupariam-os-consumidores-ainda-sem-acesso-ao-mercado-livre-de-energia/](https://abraceel.com.br/destaques/2024/03/alem-do-grupo-a-quem-sao-e-quanto-poupariam-os-consumidores-ainda-sem-acesso-ao-mercado-livre-de-energia/)  
12. www.epe.gov.br, acessado em maio 11, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-314/topico-406/TR\_META\_Servi%C3%A7os\_24out\_2013.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-314/topico-406/TR_META_Servi%C3%A7os_24out_2013.pdf)  
13. MME e ENBPar divulgam resultados do perfil de consumo de ..., acessado em maio 11, 2025, [https://www.gov.br/mme/pt-br/assuntos/noticias/mme-e-enbpar-divulgam-resultados-do-perfil-de-consumo-de-energia-eletrica-na-classe-comercial-e-de-servicos](https://www.gov.br/mme/pt-br/assuntos/noticias/mme-e-enbpar-divulgam-resultados-do-perfil-de-consumo-de-energia-eletrica-na-classe-comercial-e-de-servicos)  
14. static.poder360.com.br, acessado em maio 11, 2025, [https://static.poder360.com.br/2025/03/anuario-empresa-de-pesquisa-energetica-2024.pdf](https://static.poder360.com.br/2025/03/anuario-empresa-de-pesquisa-energetica-2024.pdf)  
15. Anuário Estatístico de Energia Elétrica \- Empresa de Pesquisa ..., acessado em maio 11, 2025, [https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/anuario-estatistico-de-energia-eletrica](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/anuario-estatistico-de-energia-eletrica)