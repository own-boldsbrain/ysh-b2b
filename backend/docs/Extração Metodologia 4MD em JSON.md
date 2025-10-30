

# **Metodologia e Lógica do Modelo 4MD para o Plano Decenal de Expansão de Energia 2032**

## **I. O Modelo 4MD: Estrutura Conceitual e Arquitetura**

Esta seção estabelece o contexto, os fundamentos teóricos e a estrutura geral do Modelo de Mercado da Micro e Minigeração Distribuída (4MD). Detalha-se o papel do modelo no âmbito do Plano Decenal de Expansão de Energia (PDE), sua fundamentação na Teoria da Difusão de Inovações e seu escopo abrangendo tecnologias, segmentos de consumidores e recortes geográficos.

### **1.1. Introdução à EPE e ao Arcabouço do PDE**

A Empresa de Pesquisa Energética (EPE) é o órgão do governo brasileiro responsável pelos estudos que subsidiam o planejamento do setor energético nacional.1 Um dos seus principais produtos é o Plano Decenal de Expansão de Energia (PDE), um documento informativo que apresenta as perspectivas de expansão futura do setor sob a ótica do Governo, com um horizonte de dez anos.3 O PDE 2032, especificamente, indica as projeções e necessidades do setor até o ano de 2032\.3  
Nesse contexto, o modelo 4MD surge como uma ferramenta analítica crucial, fornecendo as projeções de difusão da Micro e Minigeração Distribuída (MMGD) e de outros Recursos Energéticos Distribuídos (REDs) que são integradas ao planejamento energético global. A metodologia e as premissas do modelo são formalizadas em Notas Técnicas oficiais que acompanham cada ciclo do PDE, garantindo a transparência e a replicabilidade dos estudos.3

### **1.2. A Fundação Teórica: Um Modelo Híbrido Socioeconômico**

O 4MD se fundamenta em uma abordagem que integra a racionalidade econômica com padrões sociológicos de adoção tecnológica.6 A base teórica do modelo é a "Teoria da Difusão de Inovações" de Everett Rogers, que postula que a adoção de uma nova tecnologia por uma sociedade segue um padrão previsível ao longo do tempo, descrito por uma curva em formato de "S".6  
Matematicamente, essa teoria é implementada através do Modelo de Difusão de Bass. Este modelo segmenta os adotantes em duas categorias: os "inovadores", que são influenciados por fatores externos e propaganda (representados pelo parâmetro '$p$'), e os "imitadores", que são influenciados pela pressão social e pelo "boca a boca" de adotantes existentes (representados pelo parâmetro '$q$').6 A atratividade econômica, calculada por meio de uma análise detalhada de *payback*, é o principal vetor que molda a velocidade e o teto de saturação dessa curva de difusão.  
A decisão de combinar um modelo sociológico (Bass) com uma análise econômica tradicional (fluxo de caixa) é uma escolha metodológica deliberada e sofisticada. Um modelo puramente econômico assumiria que, assim que o retorno financeiro de um sistema fotovoltaico se tornasse atrativo, a adoção ocorreria de forma massiva e instantânea entre todos os consumidores para os quais o investimento é viável. A realidade, no entanto, demonstra que a adoção é influenciada por fatores como a conscientização, o efeito de pares ("meu vizinho instalou"), a confiança nos fornecedores e a percepção de risco. O parâmetro '$q$' (imitação) do Modelo de Bass captura matematicamente esse efeito de prova social. Ao utilizar a atratividade econômica para definir o tamanho do mercado potencial e modular a velocidade da curva de Bass, o modelo 4MD gera uma previsão mais robusta, que explica não apenas *se* um consumidor irá adotar a tecnologia, mas também *quando*, com base em uma combinação de incentivo financeiro e momentum social.

### **1.3. Escopo e Granularidade do Modelo**

O escopo do modelo abrange a projeção da adoção de Micro e Minigeração Distribuída (MMGD) e, de forma opcional, de Baterias Atrás do Medidor (*Behind-the-Meter Batteries* \- BADM).6  
Uma das características mais importantes do 4MD é sua alta resolução. As projeções são geradas com um elevado nível de detalhe, sendo segmentadas por:

* **Classe de Consumo:** Residencial, Comercial, Industrial, Rural, entre outras.6  
* **Fonte de Geração:** Com foco principal na fonte fotovoltaica, dada sua predominância no mercado.6  
* **Recorte Geográfico:** As projeções são individualizadas para cada concessionária de distribuição de energia elétrica do país.6

A resolução temporal primária dos cálculos é anual, sendo posteriormente desagregada para uma base mensal para a obtenção de resultados finais, como a geração de energia.6

## **II. Avaliação da Viabilidade Econômica: O Motor de Cálculo do Payback**

Esta seção disseca a análise de fluxo de caixa utilizada para determinar a atratividade econômica dos sistemas de MMGD e BADM, que constitui o motor econômico que impulsiona toda a previsão do modelo.

### **2.1. Estrutura do Fluxo de Caixa**

Para cada consumidor representativo, em cada segmento e área de concessão, e para cada ano do horizonte de projeção, o modelo realiza uma análise de fluxo de caixa descontado.6 O principal resultado dessa análise é o tempo de retorno do investimento (*payback* simples), que serve como um indicador chave para a definição do mercado potencial.6 Outras métricas financeiras, como a Taxa Interna de Retorno (TIR), também são calculadas.8

### **2.2. Componentes de Receitas e Custos**

A análise financeira é estruturada com base nos seguintes componentes:

* **Receitas:** Derivadas primariamente da economia na fatura de energia elétrica, que se divide em:  
  * **Autoconsumo:** Energia gerada e consumida instantaneamente na unidade consumidora, evitando a compra da energia da rede e, consequentemente, o pagamento da tarifa cheia (componentes TE e TUSD).  
  * **Injeção na Rede:** Energia excedente injetada na rede da distribuidora, que gera créditos a serem utilizados para abater o consumo em meses futuros. A valoração desses créditos está sujeita às regras regulatórias de compensação vigentes.6  
* **Custos (Despesas):**  
  * **CAPEX (*Capital Expenditure*):** Custo de investimento inicial do sistema (expresso em R$/kWp), incluindo módulos, inversores, estruturas e instalação. O modelo incorpora uma curva de projeção de redução de custos para este parâmetro ao longo do tempo.6  
  * **OPEX (*Operational Expenditure*):** Custos anuais de operação e manutenção, geralmente calculados como um percentual do CAPEX.6  
  * **Substituição do Inversor:** Despesa de capital significativa que ocorre em um momento intermediário da vida útil do projeto (e.g., no 15º ano).8  
  * **Custos de Reforço da Rede:** Potenciais custos para adequação da rede de distribuição local, quando aplicável.6

### **2.3. Parâmetros de Entrada Técnicos e Econômicos**

A precisão do cálculo de *payback* depende de um conjunto detalhado de premissas. A tabela abaixo consolida os principais parâmetros de entrada do modelo. A alta sensibilidade dos resultados a essas variáveis torna a transparência desses dados fundamental para a análise de cenários e a auditoria do modelo.  
**Tabela 1: Principais Parâmetros de Entrada para o Cálculo de Payback**

| Nome do Parâmetro | Descrição | Unidade | Fonte/Tipo de Dado | Fonte |
| :---- | :---- | :---- | :---- | :---- |
| Potência Típica | Tamanho médio do sistema fotovoltaico para um dado segmento. | kWp | Dado histórico/Premissa | 6 |
| Irradiação Global | Nível de irradiação solar na localidade da distribuidora. | kWh/m²/dia | Dado meteorológico | 6 |
| Performance Ratio (PR) | Fator de eficiência global do sistema, considerando perdas. | % | Premissa técnica | 6 |
| Degradação Anual | Perda anual de produtividade dos painéis fotovoltaicos. | %/ano | Premissa técnica | 6 |
| Evolução Tarifária | Projeção do reajuste anual das tarifas de energia elétrica. | %/ano | Projeção EPE | 6 |
| Fator de Autoconsumo | Percentual da energia gerada que é consumida instantaneamente. | % | Premissa/Dado histórico | 6 |
| Vida Útil | Tempo de vida operacional assumido para o sistema. | anos | Premissa técnica | 6 |
| CAPEX | Custo de capital inicial do sistema. | R$/kWp | Premissa de mercado | 6 |
| OPEX | Custo de operação e manutenção. | % do CAPEX/ano | Premissa de mercado | 6 |
| Ano de Troca do Inversor | Ano em que ocorre a substituição do inversor. | ano | Premissa técnica | 8 |

## **III. Dinâmica de Adoção de Mercado: A Formulação da Curva de Difusão de Bass**

Esta seção detalha a modelagem matemática da adoção tecnológica, explicando como os resultados econômicos da seção anterior são traduzidos em uma previsão de difusão ao longo do tempo.

### **3.1. A Equação do Modelo de Bass**

O modelo de Bass descreve como o número de novos adotantes em um determinado período é uma função do número de adotantes existentes. A equação fundamental captura a influência combinada de inovadores e imitadores. Os parâmetros '$p$' (coeficiente de inovação) e '$q$' (coeficiente de imitação) são os pilares do modelo, representando, respectivamente, a propensão à adoção por influências externas (mídia, publicidade) e internas (interação social, "boca a boca").6

### **3.2. Calibração dos Parâmetros para a MMGD**

Para a MMGD, o modelo adota um processo de calibração rigoroso e baseado em dados. Utilizando o histórico de adoções para cada um dos 270 segmentos (pares de distribuidora e classe de consumo), o modelo ajusta uma curva de Bass para determinar os valores ótimos dos parâmetros '$p$' e '$q$'.6 O método estatístico empregado é a regressão não linear pelo Método dos Mínimos Quadrados.6  
Durante o processo de calibração, são aplicadas restrições aos parâmetros para garantir a estabilidade do modelo e refletir observações empíricas de outras difusões tecnológicas: '$0 \\le p \\le 0.01$' e '$0 \\le q \\le 1$'.6 Essas restrições permitem capturar diferentes velocidades de difusão para cada mercado específico.

### **3.3. O Desafio de Projetar a Adoção de Baterias (BADM)**

O módulo de projeção para baterias (BADM) enfrenta uma limitação fundamental: a ausência de uma base de dados histórica robusta sobre a adoção dessa tecnologia no Brasil, o que impede uma calibração estatística confiável dos parâmetros '$p$' e '$q$'.6  
Para contornar essa limitação, o modelo oferece duas abordagens alternativas, baseadas em premissas do usuário 6:

1. **Curva da MMGD com Deslocamento Temporal:** Assume-se que as baterias seguirão a mesma trajetória de adoção da fonte fotovoltaica, porém com um atraso de tempo (defasagem) especificado pelo usuário.  
2. **Curva com Parâmetros Definidos pelo Usuário:** Permite que o usuário insira diretamente os valores que julga adequados para os parâmetros '$p$' e '$q$' da curva de difusão das baterias.

A inclusão explícita de um módulo opcional e não calibrado para baterias é uma decisão de design estratégica. A EPE reconhece que o armazenamento de energia é a próxima fronteira dos recursos distribuídos, mas o mercado ainda é muito incipiente para a abordagem rigorosa usada na MMGD. Ignorar as baterias tornaria o PDE rapidamente obsoleto, enquanto criar um modelo complexo, mas não validado, seria metodologicamente questionável. A solução adotada — um módulo opcional com parâmetros definidos pelo usuário — é um compromisso pragmático. Ele permite que planejadores e pesquisadores explorem cenários (e.g., "E se as baterias seguirem a trajetória da fonte solar, mas com 5 anos de atraso?"), sem que a EPE endosse oficialmente uma previsão não comprovada. Esse design torna o modelo 4MD preparado para o futuro. Assim que dados históricos suficientes sobre a adoção de baterias estiverem disponíveis, o módulo existente poderá ser "ativado" para usar o mesmo método de calibração por regressão aplicado à MMGD. A estrutura já está pronta, aguardando os dados.

## **IV. Definição do Mercado Endereçável: Lógica de Potencial e Segmentação**

Esta seção detalha a metodologia para quantificar o mercado potencial total, que atua como o teto de saturação ('$M$') para a curva de difusão de Bass. A taxa de adoção ('$F(t)$') é multiplicada por esse potencial de mercado para determinar o número de adotantes.

### **4.1. Dimensionamento Inicial do Mercado**

O processo inicia-se com o número total de unidades consumidoras (UCs) por distribuidora e segmento, com base em dados oficiais.8 Em seguida, são aplicados filtros para refinar esse universo. A função epe4md\_mercado\_potencial do pacote R permite, por exemplo, filtrar os consumidores residenciais e comerciais por faixa de renda, o que serve como um *proxy* para a capacidade econômica de realizar o investimento inicial.8

### **4.2. Potencial de Mercado Dinâmico**

O modelo não assume um mercado estático. Ele incorpora uma taxa de crescimento para o mercado potencial, especialmente para consumidores de alta tensão (Grupo A), para contabilizar a expansão econômica e a conexão de novos consumidores ao longo do horizonte de projeção.8 Além disso, o próprio cálculo do *payback* atua como um filtro dinâmico: consumidores para os quais o retorno do investimento é considerado pouco atrativo em um determinado ano podem ser excluídos do mercado potencial imediato, mas podem vir a integrá-lo em anos futuros, à medida que o CAPEX dos sistemas diminui e as tarifas de energia aumentam.  
A decisão de gerar 270 curvas de adoção únicas (uma para cada par distribuidora-segmento) é a maior força e, ao mesmo tempo, a maior vulnerabilidade do modelo. Essa granularidade permite uma análise de políticas regionais extremamente nuançada, mas cria uma dependência massiva da qualidade e da precisão dos dados locais. Um modelo de nível nacional único mascararia diferenças regionais críticas em tarifas, irradiação solar, níveis de renda e regulações locais. Ao desagregar, o modelo pode prever que a adoção sature em uma região com tarifas altas e muito sol, enquanto ainda é incipiente em outra. Contudo, cada um dos 270 segmentos exige seu próprio conjunto de dados históricos para calibração e suas próprias premissas futuras (como a evolução tarifária). Um erro nos dados de uma única grande distribuidora poderia distorcer significativamente a projeção nacional. Isso revela por que a decisão da EPE de tornar o modelo de código aberto através do pacote epe4md 1 é tão estratégica: é um convite implícito para que concessionárias, pesquisadores e outros agentes validem e contribuam para a melhoria dos dados granulares dos quais a precisão do modelo depende fundamentalmente.

## **V. Síntese da Projeção: De Adotantes ao Impacto Sistêmico**

Esta seção explica como os componentes anteriores são integrados para produzir os resultados finais da projeção, seguindo a cadeia funcional descrita na documentação do pacote epe4md em R.

### **5.1. Projeção de Adotantes**

O número anual de novos adotantes é calculado multiplicando-se a taxa de adoção da curva de Bass ('$F(t)$') pelo mercado potencial final ('$M$') para cada segmento.6 Esta etapa é executada pela função epe4md\_proj\_adotantes. O modelo também realiza uma desagregação desses adotantes por fonte de energia.8

### **5.2. Projeção da Capacidade Instalada**

O número de novos adotantes de cada ano é multiplicado pela potência média histórica do sistema (Potência Típica) para aquela fonte, segmento e distribuidora, a fim de estimar a nova capacidade instalada anualmente.8 Essa tarefa é realizada pela função epe4md\_proj\_potencia.

### **5.3. Desagregação Mensal e Geração**

As projeções anuais de adotantes e capacidade são desagregadas em valores mensais por meio da função epe4md\_proj\_mensal.8 A capacidade instalada mensal é, então, utilizada para estimar a geração mensal de energia, aplicando-se perfis de irradiação solar locais e os fatores de performance do sistema.8 Esta é a etapa final do cálculo, executada pela função epe4md\_proj\_geracao.

### **5.4. Projeções de Investimento**

Uma função auxiliar, epe4md\_investimentos, calcula o montante total de investimento anual. Isso é feito multiplicando-se as adições anuais de capacidade (em kW) pelo CAPEX projetado (em R$/kW) para aquele ano específico.8

## **VI. O Manual de Regras Regulatórias e Cenários**

Esta seção crucial codifica a flexibilidade do modelo para lidar com diferentes ambientes políticos e regulatórios, detalhando os parâmetros configuráveis pelo usuário que permitem ao 4MD funcionar como uma "caixa de areia" para simulação de políticas.

### **6.1. Modelagem do Mecanismo de Compensação**

A rentabilidade da geração distribuída é extremamente sensível às regras que governam a compensação da energia injetada na rede. A tabela abaixo detalha as alavancas regulatórias que podem ser ajustadas no modelo, permitindo uma comparação quantitativa direta de diferentes propostas de políticas.  
**Tabela 2: Parâmetros e Lógica de Cenários Regulatórios**

| Nome do Parâmetro | Definição | Valores Permitidos | Impacto no Fluxo de Caixa | Fonte |
| :---- | :---- | :---- | :---- | :---- |
| alternativas | Define o nível de compensação da energia injetada. Os valores determinam quais componentes tarifários (e.g., TUSD Fio B, Encargos) deixam de ser compensados e devem ser pagos pelo prossumidor. | 0 a 5 | Afeta diretamente a "receita" do projeto ao reduzir o valor do crédito de energia. | 8 |
| p\_transicao | Fator de transição (0 a 1\) que permite uma implementação gradual de uma nova regra (alternativa), definindo qual percentual do novo encargo será aplicado. | 0 a 1 (0% a 100%) | Permite modelar a introdução faseada de novas regras, suavizando o impacto no *payback*. | 8 |
| binomia | Booleano (TRUE/FALSE) que simula a introdução de uma tarifa binômia para consumidores de baixa tensão. | TRUE / FALSE | Se TRUE, componentes da TUSD tornam-se um encargo fixo, não podendo mais ser abatidos por créditos de energia, o que impacta negativamente a economia gerada. | 8 |
| demanda\_g | Booleano (TRUE/FALSE) específico para consumidores do Grupo A (alta tensão), que define se a cobrança pelo uso da rede é baseada na demanda contratada (TUSDg) ou no consumo. | TRUE / FALSE | Altera a base de cálculo da economia na fatura para grandes consumidores, impactando seu potencial de economia. | 8 |

A existência desses parâmetros regulatórios detalhados e explícitos transforma o 4MD de um simples instrumento de previsão em uma ferramenta dinâmica de análise de cenários e simulação de políticas. Em vez de produzir uma única projeção "mais provável", o modelo permite que qualquer usuário formule questões sofisticadas, como: "Qual seria o impacto na adoção de GD nos próximos 10 anos se mudarmos da alternativa 1 para a 3, com uma transição de três anos usando o p\_transicao?". O 4MD pode fornecer uma resposta quantitativa, projetando a alteração resultante na capacidade instalada, no investimento e na geração de energia. Essa capacidade o torna uma ferramenta indispensável para reguladores e formuladores de políticas realizarem análises *ex-ante* de mudanças regulatórias, testando-as em um ambiente virtual antes de implementá-las no mundo real.

## **VII. Blueprint de Implementação: Estruturas de Dados e Fluxo Funcional**

Esta seção final conecta o modelo conceitual à sua implementação prática no pacote epe4md da linguagem R, servindo como um guia para a estrutura lógica do modelo.

### **7.1. Estrutura de Entrada de Dados**

O principal método de entrada de dados do modelo é através de um conjunto de planilhas no formato .xlsx, localizadas no diretório inst/dados\_premissas do pacote.7 Para facilitar a personalização, o pacote inclui a função epe4md\_copia\_premissas, que permite ao usuário criar uma cópia local e editável desses arquivos de premissas. Isso possibilita a execução de simulações customizadas sem alterar os dados originais do pacote.8

### **7.2. Mapeamento do Fluxo de Trabalho Funcional**

A metodologia pode ser executada de duas maneiras dentro do pacote R, mapeando diretamente os passos conceituais às funções de software:

* **Execução em Passo Único:** A função epe4md\_calcula atua como um invólucro (*wrapper*) que executa toda a cadeia de análise com um único comando, simplificando o uso para a obtenção de resultados diretos.8  
* **Execução Passo a Passo:** Permite um controle mais granular e a inspeção de resultados intermediários, seguindo a cadeia de funções 8:  
  1. Dimensionamento do Mercado: epe4md\_mercado\_potencial (Seção IV)  
  2. Geração de Casos para *Payback*: epe4md\_casos\_payback (Seção II)  
  3. Cálculo do *Payback*: epe4md\_payback (Seção II)  
  4. Calibração da Curva S: epe4md\_calibra\_curva\_s (Seção III)  
  5. Projeção de Adotantes: epe4md\_proj\_adotantes (Seção V.1)  
  6. Projeção de Potência: epe4md\_proj\_potencia (Seção V.2)  
  7. Desagregação Mensal: epe4md\_proj\_mensal (Seção V.3)  
  8. Projeção da Geração: epe4md\_proj\_geracao (Seção V.3)

### **7.3. Estrutura de Saída**

O principal resultado do modelo é um *data frame* (ou *tibble*) que contém as projeções mensais para o número de adotantes, a capacidade instalada (acumulada e nova) e a geração de energia. Esses dados são segmentados por distribuidora, classe de consumo e fonte.8 O pacote também inclui funções auxiliares de visualização (e.g., epe4md\_graf\_pot\_acum) para facilitar a interpretação dos resultados.8

## **Conclusão**

A metodologia do modelo 4MD, utilizada como subsídio para o PDE 2032, representa uma abordagem sofisticada e robusta para a projeção da difusão de recursos energéticos distribuídos no Brasil. Suas principais forças residem na combinação de uma base teórica socioeconômica, que captura as complexidades do comportamento do consumidor, com uma alta granularidade de análise, permitindo projeções regionalizadas e segmentadas.  
A estrutura do modelo como uma ferramenta de simulação de políticas, com parâmetros regulatórios explícitos e configuráveis, confere-lhe um valor estratégico para a análise de cenários e o planejamento regulatório. A decisão de desenvolvê-lo como um pacote de software de código aberto (epe4md) promove a transparência, a colaboração e o aprimoramento contínuo da ferramenta pela comunidade de especialistas.  
Embora o modelo apresente limitações reconhecidas, como a natureza ainda incipiente do módulo de projeção de baterias, sua arquitetura é extensível e preparada para incorporar novos dados e tecnologias à medida que estas amadurecem. Em suma, o 4MD não é apenas um modelo de previsão, mas uma plataforma analítica dinâmica, essencial para guiar o Brasil na transição energética e no planejamento de um sistema elétrico cada vez mais descentralizado e complexo.

#### **Referências citadas**

1. Empresa de Pesquisa Energética \- GitHub, acessado em setembro 24, 2025, [https://github.com/EPE-GOV-BR](https://github.com/EPE-GOV-BR)  
2. Authors and Citation • epe4md, acessado em setembro 24, 2025, [https://epe-gov-br.github.io/epe4md/authors.html](https://epe-gov-br.github.io/epe4md/authors.html)  
3. Plano Decenal de Expansão de Energia, acessado em setembro 24, 2025, [https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/plano-decenal-de-expansao-de-energia-pde](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/plano-decenal-de-expansao-de-energia-pde)  
4. EPE divulga nova versão da Nota Técnica \- Dados de entrada para modelos elétricos e energéticos: metodologias e premissas, acessado em setembro 24, 2025, [https://www.epe.gov.br/pt/imprensa/noticias/epe-divulga-nova-versao-da-nota-tecnica-dados-de-entrada-para-modelos-eletricos-e-energeticos-metodologias-e-premissas](https://www.epe.gov.br/pt/imprensa/noticias/epe-divulga-nova-versao-da-nota-tecnica-dados-de-entrada-para-modelos-eletricos-e-energeticos-metodologias-e-premissas)  
5. Nota Técnica \- Dados de entrada para modelos elétricos e ..., acessado em setembro 24, 2025, [https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/nota-tecnica-dados-de-entrada-para-modelos-eletricos-e-energeticos-metodologias-e-premissas-nova-versao](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/nota-tecnica-dados-de-entrada-para-modelos-eletricos-e-energeticos-metodologias-e-premissas-nova-versao)  
6. NOTA TÉCNICA EPE-DEA-SEE-009-2025 \- Modelo de Mercado da ..., acessado em setembro 24, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-889/NT-EPE-DEA-SEE-009-2025.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-889/NT-EPE-DEA-SEE-009-2025.pdf)  
7. EPE-GOV-BR/epe4md: O pacote epe4md permite fazer ... \- GitHub, acessado em setembro 24, 2025, [https://github.com/EPE-GOV-BR/epe4md](https://github.com/EPE-GOV-BR/epe4md)  
8. EPE's 4MD model to forecast the adoption of Distributed Generation ..., acessado em setembro 24, 2025, [https://epe-gov-br.github.io/epe4md/](https://epe-gov-br.github.io/epe4md/)  
9. epe4md: EPE's 4MD Model to Forecast the Adoption of Distributed Generation \- CRAN \- R Project, acessado em setembro 24, 2025, [https://cran.r-project.org/package=epe4md](https://cran.r-project.org/package=epe4md)  
10. epe4md \- README, acessado em setembro 24, 2025, [https://cran.r-project.org/web/packages/epe4md/readme/README.html](https://cran.r-project.org/web/packages/epe4md/readme/README.html)