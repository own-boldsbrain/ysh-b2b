

# **Roteiro de Benchmark UX/UI para um Playground Studio de Dimensionamento de Projetos Solares no Brasil**

## **I. Introdução: Definindo o Benchmark Solar Playground Studio para o Brasil**

### **A. O Paradigma "Playground Studio": Design Solar Interativo, Iterativo e Perspicaz**

O conceito de "Playground Studio" no desenvolvimento de software refere-se a um ambiente que prioriza a experimentação, a interatividade e o aprendizado facilitado. Inspirando-se em plataformas como o Scratch, que simplifica a programação através de blocos visuais e feedback imediato 1, e o Atlas Search Playground, que oferece um ambiente de sandbox para experimentação sem a necessidade de configuração completa 2, um Playground Studio para dimensionamento solar visa transformar uma tarefa técnica complexa em uma experiência mais acessível e intuitiva. Diferentemente de um "Playground Studio" físico focado em arquitetura e paisagismo 3, a sua contraparte digital enfatiza a exploração de design e a iteração rápida.  
As características centrais de um Playground Studio de software incluem uma interface amigável, forte apelo visual, feedback instantâneo para as ações do usuário, uma baixa barreira de entrada para experimentação e um foco tanto na conclusão de tarefas quanto na exploração e aprendizado. Aplicado ao dimensionamento de projetos solares, isso se traduz em uma ferramenta que transcende planilhas complexas ou interfaces excessivamente técnicas, especialmente nas fases iniciais de avaliação. O "playground" deve permitir que os usuários experimentem visualmente com layouts de painéis solares, observem os impactos imediatos (mesmo que simplificados) na produção de energia e nos aspectos financeiros básicos, e iterem rapidamente sobre seus projetos.  
Uma abordagem eficaz para gerenciar a complexidade inerente ao design solar é conceber o "playground" como uma ferramenta de divulgação progressiva. O dimensionamento de sistemas fotovoltaicos pode ser uma tarefa intimidadora, particularmente para iniciantes ou para aqueles que realizam uma avaliação de viabilidade inicial. A própria natureza de um "playground" sugere simplicidade e facilidade de acesso.1 As melhores práticas de UX (User Experience) advogam pela divulgação progressiva para gerenciar a complexidade, apresentando informações e funcionalidades de forma gradual.4 Portanto, o Solar Playground Studio deve, inicialmente, oferecer um conjunto simplificado de ferramentas e dados, permitindo que os usuários realizem um dimensionamento básico rapidamente. Funcionalidades mais avançadas, como análise detalhada de sombreamento, modelagem financeira complexa e nuances regulatórias intrincadas, podem ser reveladas progressivamente ou acessadas à medida que o usuário ganha confiança ou necessita de maior precisão. Isso implica que a UI (User Interface) deve ser projetada em camadas de complexidade, desde um modo de "estimativa rápida" muito simples até opções de configuração mais detalhadas.

### **B. Objetivos Centrais para uma Ferramenta Brasileira de Dimensionamento Solar (Abrangendo Todas as Escalas de Projeto)**

O objetivo primário de uma ferramenta de dimensionamento solar no contexto brasileiro é capacitar os usuários a realizar rapidamente o dimensionamento preliminar e a avaliação de viabilidade para projetos fotovoltaicos de diversas escalas – residencial, comercial e pequenas usinas – dentro das especificidades do Brasil.  
Os objetivos chave incluem:

* **Avaliação Rápida do Local:** Permitir que os usuários definam uma localização e a área disponível de forma ágil, utilizando ferramentas baseadas em mapas.  
* **Design Visual do Sistema:** Fornecer ferramentas intuitivas para o posicionamento e configuração visual dos painéis solares.  
* **Estimativa Simplificada de Desempenho:** Oferecer cálculos acessíveis de produção de energia, baseados em dados de irradiação solar brasileiros.  
* **Indicação Financeira Básica:** Apresentar uma visão geral inicial de custos, economias e payback, considerando as tarifas de energia brasileiras.  
* **Conscientização Regulatória:** Informar os usuários sobre as categorias relevantes de Geração Distribuída (GD) da ANEEL (Agência Nacional de Energia Elétrica) e suas implicações gerais.

O desafio da escalabilidade, ou seja, atender a "qualquer tamanho de projeto", pode ser abordado através de diferentes modos ou fluxos de trabalho: um caminho simplificado para projetos residenciais e comerciais de pequeno porte, e um caminho mais detalhado (mas ainda com a filosofia de "playground") para sistemas maiores. Isso pode envolver a abstração inicial de complexidades, com a UI adaptando-se a diferentes escalas de entrada de dados, como o desenho de um pequeno telhado em contraste com uma grande área de solo.

### **C. Jornadas de Usuário Chave: Da Entrada Inicial à Proposta de Projeto Dimensionado**

Para ilustrar a aplicação da ferramenta, consideram-se as seguintes jornadas de usuário:

* **Jornada 1: O Proprietário Residencial/Pequeno Empresário:**  
  * O usuário insere o endereço, desenha a área do telhado ou terreno, posiciona os painéis com orientação da ferramenta e obtém uma estimativa básica do tamanho do sistema, geração de energia e potencial de economia na conta de luz, considerando as regras de GD.  
* **Jornada 2: O Instalador Solar/Desenvolvedor (Avaliação Preliminar):**  
  * O usuário avalia rapidamente múltiplos locais potenciais, compara layouts básicos e obtém indicadores rápidos de desempenho e financeiros antes de se comprometer com uma engenharia detalhada.  
* **Jornada 3: O Estudante/Pesquisador:**  
  * O usuário explora o impacto de diferentes configurações, localizações e tipos de painéis na produção de energia em um contexto brasileiro.

A natureza de um "playground" pode transcender o mero dimensionamento técnico, posicionando a ferramenta também como um facilitador de vendas e um recurso educacional. O processo de dimensionamento é frequentemente um precursor para a elaboração de uma proposta ou uma decisão de investimento. Softwares solares existentes frequentemente incluem funcionalidades de geração de propostas.5 Um "playground" pode desmistificar a tecnologia solar para clientes finais quando utilizado por instaladores, simplificando a adoção da energia solar.9 A natureza iterativa da ferramenta permite a rápida exploração de cenários "e se", o que é valioso em conversas de vendas ou para autoaprendizagem. Embora o foco principal seja o dimensionamento, a UX deve considerar como os resultados podem ser facilmente compreendidos e potencialmente compartilhados, mesmo que a geração completa de propostas seja uma funcionalidade avançada.

## **II. Princípios Fundamentais de UX/UI para um Playground de Dimensionamento Solar**

### **A. Pilares Centrais: Simplicidade, Clareza, Consistência e Foco no Usuário**

Para que um Playground Studio de dimensionamento solar atinja um nível de benchmark, sua concepção deve ser ancorada em princípios fundamentais de UX/UI:

* **Simplicidade:** "A simplicidade é um dos princípios mais importantes da UI".10 O playground deve abstrair as complexidades subjacentes, especialmente nas interações iniciais. Jargões devem ser evitados sempre que possível ou acompanhados de explicações claras.10  
* **Clareza:** Hierarquia visual bem definida, navegação clara e rotulagem inequívoca são essenciais. Os usuários devem sempre compreender onde estão no processo e qual o próximo passo.10  
* **Consistência:** "A consistência é um pilar central das melhores práticas de UI/UX".11 Elementos visuais (botões, ícones, cores) e padrões de interação devem ser uniformes em toda a aplicação.10  
* **Design Centrado no Usuário:** "A UI deve ser projetada para focar primeiramente nas necessidades e preferências do usuário".10 Isso envolve compreender as diferentes personas de usuário (proprietário residencial, instalador, estudante) e adaptar a experiência a elas.

Para solidificar esses princípios, a tabela a seguir detalha heurísticas de usabilidade cruciais e sua aplicação prática no Solar Playground Studio.  
**Tabela 1: Heurísticas Essenciais de UX/UI para o Solar Playground Studio**

| Heurística (Princípios de Nielsen) | Relevância para o Solar Playground | Exemplo Prático no Playground Solar |
| :---- | :---- | :---- |
| **Visibilidade do Status do Sistema** | O usuário precisa saber o que está acontecendo, como o progresso de um cálculo de irradiação ou a contagem de painéis. | Barra de progresso durante simulações; feedback visual imediato ao adicionar/mover painéis (ex: contagem de kWp atualizada). |
| **Correspondência entre o Sistema e o Mundo Real** | Usar linguagem e conceitos familiares ao usuário (ex: termos de energia solar comuns no Brasil), seguindo convenções do mundo real. | Uso de termos como "conta de luz", "créditos de energia", nomes de componentes tarifários (TUSD, TE) como são conhecidos no Brasil. Unidades em metros, kWh, R$. |
| **Controle e Liberdade do Usuário** | Usuários cometem erros. Precisam de uma "saída de emergência" clara para sair de um estado indesejado sem passar por um processo extenso. Funções de "desfazer" e "refazer". | Botão "Desfazer" para remoção de painéis ou alteração de área; opção de "Cancelar" em modais de configuração; capacidade de salvar e reverter para versões anteriores de um layout. |
| **Consistência e Padrões** | Usuários não deveriam ter que se perguntar se palavras, situações ou ações diferentes significam a mesma coisa. Seguir convenções de plataforma. | Botões de ação (ex: "Salvar", "Simular", "Exportar") com design e posicionamento consistentes em todas as telas. Uso de ícones universalmente reconhecidos. |
| **Prevenção de Erros** | Melhor que boas mensagens de erro é um design cuidadoso que previne a ocorrência de problemas. | Desabilitar botões de "Simular" se dados essenciais estiverem faltando; validação em tempo real de campos de entrada (ex: custo por kWp deve ser numérico). |
| **Reconhecimento em Vez de Memorização** | Tornar objetos, ações e opções visíveis. O usuário não deve ter que lembrar informações de uma parte do diálogo para outra. | Exibição constante dos parâmetros chave do projeto (localização, kWp total) na tela; uso de menus visuais para seleção de tipo de painel em vez de códigos. |
| **Flexibilidade e Eficiência de Uso** | Aceleradores – não vistos pelo usuário novato – podem frequentemente acelerar a interação para o usuário experiente, de modo que o sistema possa atender a ambos. | Atalhos de teclado para ações comuns (ex: Ctrl+Z para desfazer); opção de "configurações avançadas" para usuários que desejam maior controle sobre parâmetros de simulação. |
| **Design Estético e Minimalista** | Diálogos não devem conter informações irrelevantes ou raramente necessárias. Cada unidade extra de informação em um diálogo compete com as unidades relevantes. | Interface limpa, com foco na área do mapa e nos resultados chave. Evitar excesso de texto ou elementos decorativos que não agregam valor funcional. |
| **Ajudar Usuários a Reconhecer, Diagnosticar e Recuperar-se de Erros** | Mensagens de erro devem ser expressas em linguagem clara (sem códigos), indicar precisamente o problema e sugerir construtivamente uma solução. | Se uma simulação falhar, exibir uma mensagem como: "Não foi possível simular. Verifique se a área de painéis foi definida e se os dados de irradiação estão disponíveis para esta localidade." |
| **Ajuda e Documentação** | Mesmo que seja melhor se o sistema puder ser usado sem documentação, pode ser necessário fornecer ajuda e documentação. | Tooltips informativos em campos complexos (ex: "Inclinação ótima sugerida para esta região"); links para uma seção de FAQ ou guias sobre regulamentação brasileira. |

Esta tabela serve como um guia fundamental para a equipe de design e desenvolvimento, assegurando que princípios de usabilidade sejam incorporados desde o início, resultando em uma experiência de usuário mais intuitiva e eficaz.

### **B. Projetando para Entradas de Dados Complexas: Dados Geoespaciais, Parâmetros Técnicos e Dados Regulatórios Brasileiros**

O dimensionamento de projetos solares envolve a entrada de diversos tipos de dados, cada um com seus desafios de UX:

* **Entrada de Dados Geoespaciais:**  
  * A ferramenta deve apresentar um mapa interativo para identificação da localização (busca por endereço, coordenadas GPS) e definição da área de instalação (ferramentas de desenho).12  
  * Desafios incluem garantir o bom desempenho do mapa, oferecer ferramentas de desenho intuitivas e gerenciar diferentes camadas de mapa (satélite, terreno).15  
* **Parâmetros Técnicos:**  
  * Entradas para tipo de painel, tipo de inversor (inicialmente simplificado, talvez com pré-seleções), inclinação e azimute.  
  * É crucial usar rótulos claros, tooltips (dicas de ferramenta) para campos complexos e padrões sensatos.4  
  * A divulgação progressiva é uma técnica valiosa aqui: mostrar parâmetros básicos primeiro, com opções "avançadas" ocultas inicialmente.4  
* **Dados Regulatórios Brasileiros:**  
  * Entrada para selecionar o tipo de consumidor (ex: residencial do Grupo B) para inferir as regras de GD da ANEEL aplicáveis.  
  * Esses dados influenciarão as estimativas financeiras e as informações regulatórias exibidas.

Para facilitar a entrada de dados específicos do contexto brasileiro, a ferramenta deve empregar padrões contextuais e orientação guiada. O cenário solar brasileiro envolve dados particulares, como a irradiação do INPE e as regras da ANEEL, que podem não ser familiares em ferramentas genéricas. Usuários, especialmente os menos técnicos, podem não conhecer a inclinação/azimute ótimos para sua região ou as implicações tarifárias específicas de sua modalidade de GD. Um "playground" deve reduzir as barreiras de entrada. Portanto, o sistema deve pré-preencher ou sugerir valores ótimos com base na localização (ex: irradiação média do Atlas Brasileiro de Energia Solar do INPE 17, inclinação ótima sugerida) e guiar os usuários na seleção de seu status de GD junto à ANEEL.20 Isso implica que o backend precisa ter acesso a dados regionais brasileiros, e a UI deve usar esses dados de forma inteligente para simplificar a entrada do usuário.

### **C. Acessibilidade e Inclusividade no Design**

Um bom design deve funcionar para todos, incluindo usuários com deficiências.11 Isso envolve considerar:

* **Contraste de Cores:** Especialmente importante para visualizações de dados em mapas e gráficos.  
* **Navegação por Teclado:** Garantir que todas as funcionalidades sejam acessíveis sem o uso do mouse.  
* **Compatibilidade com Leitores de Tela:** Para usuários com deficiência visual..10  
* **Linguagem Clara e Simples:** Evitar termos excessivamente técnicos sem explicação.

### **D. Hierarquia Visual e Arquitetura da Informação para Fluxos de Trabalho Solares**

Uma estrutura clara é vital para guiar o usuário:

* **Mapa do Site/Fluxo:** Definir um caminho lógico desde a criação do projeto, passando pela definição do local, layout dos painéis, simulação, até a visualização dos resultados.11  
* **Organização Visual:** Utilizar tipografia, cores e espaçamento para direcionar a atenção do usuário aos elementos mais importantes em cada tela.10  
* **Design de Painéis (Dashboards):** Os resultados devem ser apresentados em um formato de fácil digestão, priorizando as métricas chave. Um bom design de dashboard é crucial para comunicar o valor do projeto solar de forma eficaz.23

## **III. Funcionalidades Essenciais e Fluxo de Trabalho do Solar Playground Studio**

### **A. Iniciação do Projeto e Definição do Local**

O ponto de partida para qualquer dimensionamento é a criação de um projeto e a definição precisa do local de instalação.

* **1\. Entrada do Usuário:**  
  * **Nome do Projeto:** Um campo de texto simples para identificação.  
  * **Entrada de Localização:**  
    * Busca de endereço com autocompletar, integrando-se a um serviço de geocodificação.  
    * Opção de clicar diretamente no mapa ou inserir coordenadas GPS.  
  * **Escala do Projeto (Simplificada):** Uma seleção inicial como "Residencial Pequeno", "Residencial Grande/Comercial Pequeno", "Campo/Montagem no Solo" pode ajudar a definir padrões iniciais ou modos de interface.  
* **2\. Interface de Mapa Interativa:**  
  * **Mapa Base:** Imagens de satélite como padrão, com opções para mapas básicos de ruas/terreno.15  
  * **Ferramentas de Definição de Área:**  
    * Ferramenta de desenho de polígono: cliques para adicionar vértices, duplo clique para completar.13  
    * Ferramenta de retângulo para áreas mais simples.  
    * Ferramentas de edição: mover vértices, adicionar/excluir vértices.13  
    * Feedback visual claro durante o desenho (linhas, área sombreada).13  
    * Exibição dinâmica da área (m²).13  
  * **Navegação no Mapa:** Zoom intuitivo (roda do mouse, botões \+/-) e panorâmica (pan).12  
  * A relevância das melhores práticas de UI de mapa 12 é central aqui. O mapa é a tela principal; a simplicidade no estilo do mapa base é fundamental para não distrair das áreas desenhadas pelo usuário e dos layouts dos painéis. Uma distinção clara entre o modo de navegação do mapa e o modo de desenho/edição de objetos é crucial para evitar frustração do usuário. O feedback visual (destaque de áreas selecionadas, exibição de dimensões) é essencial para a confiança do usuário.  
* **3\. Integração de Dados Geoespaciais Brasileiros:**  
  * **Irradiação Solar:**  
    * Uma vez definida a localização, buscar automaticamente a média de GHI (Irradiação Global Horizontal) e DNI (Irradiação Direta Normal) para essa coordenada a partir dos dados do Atlas Brasileiro de Energia Solar do INPE.17 Estes dados possuem uma resolução aproximada de 10km x 10km.  
    * Exibir essa informação ao usuário, talvez em um pequeno painel informativo.  
    * Esses dados são fundamentais para a simulação de energia.

Considerando que a consulta visa especificamente "regiões brasileiras", a ferramenta deve garantir relevância e precisão ao focar sua interface de mapa e buscas de dados dentro das fronteiras brasileiras. A interface do mapa poderia ser inicializada centralizada no Brasil, e a busca por endereço poderia ser priorizada ou restrita ao país. Isso evita que os usuários tentem dimensionar projetos em regiões onde os dados brasileiros integrados não são aplicáveis, otimizando a experiência e a utilidade da ferramenta.

### **B. Configuração do Sistema e Layout dos Painéis (O "Playground")**

Esta é a essência do "playground", onde o usuário interage visualmente para montar o sistema solar.

* **1\. Posicionamento Visual dos Painéis:**  
  * **Paleta de Painéis:** Uma biblioteca simples de tamanhos/potências genéricas de painéis (ex: 330W, 450W, 550W). O usuário pode selecionar um tipo de painel.  
  * **Ferramentas de Posicionamento:**  
    * Clique para posicionar painéis individuais dentro da área definida.  
    * Funcionalidade de arrastar e soltar (drag-and-drop).  
    * Ferramenta simples de desenho de arranjo (ex: clicar e arrastar para preencher uma seção retangular com painéis, respeitando o espaçamento).  
    * Opções de ajuste à grade (snap-to-grid) ou às bordas para facilitar o alinhamento.  
  * **Feedback Visual:** Painéis posicionados são representados visualmente no mapa. A contagem de painéis e o kWp total são atualizados em tempo real, similar ao feedback em ferramentas de desenho.13  
* **2\. Seleção de Módulos, Compatibilização de Inversores, Configuração Elétrica Básica (Simplificada):**  
  * **Seleção de Módulos:** O usuário escolhe da paleta. Em modo avançado, poderia permitir dimensões/especificações personalizadas.  
  * **Compatibilização de Inversores (Simplificada):**  
    * O sistema sugere um tamanho de inversor adequado com base no kWp total dos painéis (ex: Inversor kWca $\\approx$ 0.8 a 1.0 \* Painel kWp).  
    * Inicialmente, sem seleção específica de marca/modelo, apenas o tamanho. Em modo avançado, permitiria a seleção de uma lista.  
  * **Configuração Elétrica Básica:**  
    * Arranjo de strings automático (conceitual): O sistema pode fornecer uma *estimativa aproximada* de strings com base em tensões típicas, mas o arranjo detalhado é uma funcionalidade avançada. O "playground" foca no layout e na capacidade.  
* **3\. Feedback em Tempo Real:**  
  * **Sombreamento (Conceitual/Simplificado):**  
    * Sem modelagem 3D complexa inicialmente.  
    * Talvez uma entrada simples de "percentual de perda por sombreamento assumido" pelo usuário (ex: 5%, 10%) ou um indicador visual muito básico se próximo a obstruções óbvias (se imagens avançadas permitirem).  
    * Ferramentas profissionais como Aurora Solar 6, PVsyst 27 e Helioscope 8 oferecem análise de sombreamento detalhada. O playground deve reconhecer sua importância, mas manter a implementação inicial simples.  
  * **Atualizações de Capacidade:** Atualizar continuamente o kWp total e o número de painéis.  
  * **Utilização da Área:** Mostrar o percentual da área definida coberta por painéis.  
* **4\. Design Iterativo:**  
  * **Modificação Fácil:** Selecionar, mover, rotacionar (em 2D, ex: retrato/paisagem), excluir painéis ou grupos de painéis.  
  * **Funcionalidade de Desfazer/Refazer:** Essencial para um ambiente "playground".11  
  * **Cenários/Versionamento (Simples):** Permitir ao usuário "Salvar Layout Como" para comparar diferentes designs para o mesmo local.

Para tornar o processo de dimensionamento menos uma tarefa e mais uma exploração, pode-se considerar elementos de "gamificação" na interação de posicionamento dos painéis. O conceito de "playground" 1 sugere diversão e engajamento. O posicionamento de painéis pode ser repetitivo. Elementos de gamificação, como uma pontuação de "eficiência de preenchimento" para a área definida, feedback visual instantâneo sobre quantos painéis cabem, ou mesmo efeitos sonoros sutis para o posicionamento, podem aumentar o engajamento do usuário e tornar o processo mais intuitivo. O feedback em tempo real é um componente central dos ciclos de jogo e se alinha bem com essa abordagem.

### **C. Simulação de Energia e Dimensionamento**

Após o layout, o sistema estima a produção de energia.

* **1\. Estimativa Simplificada de Produção de Energia:**  
  * **Entradas:** kWp total, localização (para irradiação), orientação do painel (inclinação/azimute – entrada do usuário ou padrão inteligente), fator básico de perdas do sistema (ex: padrão de 14-20%, ajustável pelo usuário).  
  * Lógica de Cálculo (Conceitual \- inspirada em 30):  
    * $Energia (kWh/ano) \= kWp \\times Média\\\_GHI\\\_POA \\times (1 \- Perdas\\\_Sistema\\\_\\%) \\times 365$  
    * $Média\\\_GHI\\\_POA$ (Irradiação Global Horizontal no Plano do Arranjo) seria derivada do GHI/DNI do INPE 17 e da inclinação/azimute definidos pelo usuário ou sugeridos, usando modelos de transposição simplificados. Modelos mais complexos como Perez ou Hay Davies do pvlib 32 seriam para estágios avançados.  
  * **Saída:** Exibir a produção de energia anual e mensal estimada (kWh).  
* **2\. Recomendações de Dimensionamento (Básicas):**  
  * O usuário pode inserir seu consumo médio mensal de eletricidade (kWh).  
  * O sistema calcula qual percentual desse consumo o design atual compensaria.  
  * O sistema pode sugerir aumentar/diminuir a contagem de painéis para atingir uma meta de compensação (ex: "Adicione mais 5 painéis para atingir 80% de compensação").

### **D. Visão Geral Financeira e Regulatória (Contexto Brasileiro)**

Esta seção traduz o dimensionamento técnico em implicações financeiras e regulatórias para o usuário brasileiro.

* **1\. Estimativa Básica de Custos e Período de Payback:**  
  * **Entrada de Custo:** O usuário insere um custo estimado por kWp (R$/kWp) para sua região/tipo de projeto.  
  * **Custo do Sistema:** $kWp \\text{ Total} \\times R\\$/kWp$.  
  * **Economia Anual:** $ \\text{Produção Anual de Energia (kWh)} \\times \\text{Tarifa Média de Eletricidade (R$/kWh)}$. O usuário insere sua tarifa média.  
  * **Payback Simples:** $ \\text{Custo do Sistema} / \\text{Economia Anual}$.  
  * Exibir esses números de forma clara.  
* **2\. Visão Geral das Regras Aplicáveis de Geração Distribuída (GD) da ANEEL:**  
  * Com base na entrada do usuário (ex: data de solicitação de conexão do projeto, tipo de projeto como "autoconsumo remoto" ou "geração compartilhada"), fornecer uma explicação simplificada de em qual categoria de GD ele provavelmente se enquadra (GD I, GD II, GD III conforme Lei 14.300 e REN 1059/2023).20  
  * Explicar brevemente as implicações para os componentes tarifários (ex: "GD II envolve pagamento escalonado do Fio B").  
  * Os materiais de referência para essas regras incluem o FAQ da ANEEL sobre MMGD 20, o guia da Cemig 22 e artigos do Portal Solar.21  
* **3\. Impacto Conceitual na Conta de Luz (TUSD, TE, Fio B, Créditos de Energia):**  
  * **Explicação Simplificada:**  
    * A conta de luz possui componentes: TE (custo da energia em si) e TUSD (custo de uso da rede de distribuição, que inclui o Fio B \- custo dos fios).21  
    * A energia injetada na rede gera créditos. Esses créditos compensam primariamente o componente TE.  
    * Sob as novas regras de GD (GD II/III), uma porção da TUSD (especificamente relacionada ao Fio B) será cobrada sobre a energia compensada.  
    * O custo de disponibilidade mínimo ainda se aplica para consumidores do Grupo B.20  
  * **Auxílio Visual/Calculadora (Conceitual):**  
    * Uma calculadora interativa muito simples:  
      * Entradas do usuário: Consumo médio mensal (kWh), Energia gerada pelo solar (kWh), Energia injetada (kWh), Tarifa TE (R$/kWh), Tarifa TUSD (R$/kWh), percentual do Fio B aplicável (ex: 15% para 2023 para GD II).  
      * Saída: Conta estimada com solar vs. sem solar, mostrando o detalhamento das cobranças.

A tabela a seguir apresenta um fluxo conceitual simplificado para o cálculo da fatura de energia solar no Brasil para um consumidor residencial (Grupo B) em um novo projeto (GD II), desmistificando um processo complexo e fornecendo transparência sobre o impacto da geração distribuída.**Tabela 2: Fluxo Conceitual de Cálculo da Fatura Solar Brasileira (Grupo B, GD II \- Simplificado para Playground)**

| Passo | Descrição da Etapa de Cálculo | Componentes Envolvidos | Observações |
| :---- | :---- | :---- | :---- |
| 1 | Calcular Energia Consumida da Rede (ECR) | Consumo Total (CT), Autoconsumo Solar (AS) | $ECR \= CT \- AS$ |
| 2 | Identificar Energia Injetada na Rede (EI) | Medição da Injeção | Dado fornecido pelo medidor bidirecional. |
| 3 | Calcular Energia a ser Compensada (EC) | ECR, EI, Créditos Acumulados (CA) | $EC \= \\min(ECR, EI \+ CA)$ |
| 4 | Calcular Custo da Energia Não Compensada (Custo TE) | ECR, EC, Tarifa de Energia (TE) | $Custo\\\_TE \= (ECR \- EC) \\times Tarifa\\\_TE$ |
| 5 | Calcular Custo da TUSD Fio B sobre Energia Compensada | EC, Tarifa TUSD Fio B, Percentual Fio B Aplicável (PFB) | $Custo\\\_FioB \= EC \\times Tarifa\\\_TUSD\\\_FioB \\times PFB$ (PFB varia anualmente para GD II/III) |
| 6 | Calcular Custo das Demais Componentes da TUSD (Simplificado) | ECR, EC, Tarifa TUSD Total, Tarifa TUSD Fio B | $Custo\\\_Outras\\\_TUSD \= (ECR \- EC) \\times (Tarifa\\\_TUSD\\\_Total \- Tarifa\\\_TUSD\\\_FioB)$ (Abordagem simplificada para o playground) |
| 7 | Somar os Custos Parciais | Custo TE, Custo Fio B, Custo Outras TUSD | $Custo\\\_Total\\\_Calculado \= Custo\\\_TE \+ Custo\\\_FioB \+ Custo\\\_Outras\\\_TUSD$ |
| 8 | Aplicar Custo de Disponibilidade (CD) | Custo Total Calculado, CD | $Valor\\\_Fatura \= \\max(Custo\\\_Total\\\_Calculado, CD)$. O CD é o mínimo para Grupo B (30, 50 ou 100 kWh x Tarifa TE \+ TUSD). |
| 9 | Atualizar Saldo de Créditos de Energia | EI, EC, CA | $Novo\\\_CA \= (CA \+ EI) \- EC$. Válido por 60 meses. |

Este fluxo simplificado visa fornecer uma compreensão básica. O cálculo real da fatura pela distribuidora pode envolver mais detalhes e arredondamentos específicos.

### **E. Visualização de Resultados e Relatórios**

A apresentação clara dos resultados é crucial para a utilidade do playground.

* **1\. Dashboards Claros:**  
  * Exibir visualmente os principais resultados: Produção Anual/Mensal de Energia (gráfico), Custo Estimado do Sistema, Economia Anual, Período de Payback Simples, Offset de Emissões de CO2.9  
  * Utilizar gráficos claros e números grandes e legíveis.  
* **2\. Geração Simplificada de Relatórios:**  
  * Opção de exportar um resumo em PDF de 1-2 páginas do design e das estimativas.  
  * Incluir: Imagem do local com layout dos painéis, parâmetros chave do sistema (kWp, tipo de painel), estimativas de produção de energia, resumo financeiro básico.  
  * Este relatório destina-se à avaliação inicial, não sendo uma proposta bancável como as geradas por ferramentas como Aurora Solar ou Helioscope.5

Um "playground" é concebido para exploração e dimensionamento inicial. Propostas completas e detalhadas são complexas e extrapolam o escopo inicial de tal ferramenta. Contudo, os usuários desejarão um registro de sua sessão no playground. Portanto, o relatório gerado deve ser um resumo conciso dos *resultados do playground*, declarando claramente sua natureza preliminar e sugerindo os próximos passos (ex: "Consulte um instalador profissional para um design detalhado e um orçamento vinculativo"). O design e o conteúdo do relatório devem gerenciar as expectativas, posicionando-o como uma ferramenta de estimativa inicial.

## **IV. Blueprint Técnico: Construindo a UX/UI**

A materialização do Solar Playground Studio requer uma seleção cuidadosa de tecnologias e uma arquitetura bem definida.

### **A. Ferramentas Recomendadas de Design e Prototipagem de UI/UX**

A escolha das ferramentas de design impacta diretamente a eficiência da equipe e a qualidade do produto final. Algumas das opções mais proeminentes incluem:

* **Figma:** Altamente colaborativo, baseado na web, robusto para design de UI, prototipagem e bibliotecas de componentes. Amplamente utilizado na indústria.10  
* **Adobe XD:** Baseado em vetores, bom para prototipagem, integra-se com o Adobe Creative Cloud.10  
* **Sketch (apenas macOS):** Popular, com um forte ecossistema de plugins.10  
* **Miro ou FigJam:** Ideais para wireframing inicial, mapeamento de fluxos de usuário e brainstorming colaborativo.39  
* **Pixso:** Mencionado como uma ferramenta colaborativa de design UI/UX com capacidades de prototipagem.41

Essas ferramentas oferecem funcionalidades robustas para projetar interfaces interativas, criar protótipos para testar fluxos de usuário e gerenciar sistemas de design para consistência.10

### **B. Frameworks Frontend para Visualização Geoespacial Interativa**

O núcleo do playground é uma aplicação web responsiva com um mapa interativo para desenho e posicionamento de objetos.

* **Necessidade Central:** Uma interface de mapa fluida e intuitiva.  
* **Opções e Considerações:**  
  * **React com Mapbox GL JS / Deck.gl:**  
    * **React:** Popular, baseado em componentes, vasto ecossistema.42  
    * **Mapbox GL JS:** Mapas vetoriais personalizáveis e de alto desempenho. Oferece o plugin mapbox-gl-draw para desenhar feições.13  
    * **Deck.gl:** Camadas de visualização aceleradas por WebGL para grandes volumes de dados, integra-se bem com Mapbox. Adequado para visualizações avançadas se o playground evoluir.42  
    * react-map-gl é um wrapper React popular para Mapbox GL JS.43  
  * **Vue.js com Leaflet:**  
    * **Vue.js:** Framework progressivo, frequentemente considerado de aprendizado mais fácil que React por alguns.42  
    * **Leaflet:** Biblioteca de mapeamento leve e de código aberto. Plugin Leaflet.draw para desenho.25  
  * **Angular com Mapbox GL JS / Deck.gl:**  
    * **Angular:** Framework abrangente, bom para aplicações de grande porte.42  
  * **Bibliotecas JavaScript Gerais:** D3.js, Chart.js para visualizações.48  
* **Desempenho:** Crítico para interação suave no mapa, especialmente com muitos objetos de painel. Bibliotecas baseadas em WebGL (Mapbox GL JS, Deck.gl) geralmente oferecem melhor desempenho para cenas complexas do que aquelas puramente baseadas em DOM.46

A tabela a seguir fornece uma comparação estruturada para auxiliar na decisão sobre as tecnologias frontend fundamentais, equilibrando funcionalidades, desempenho, esforço de desenvolvimento e disponibilidade de talentos locais.  
**Tabela 3: Tecnologias Frontend Recomendadas para Mapa Interativo e UI**

| Pilha Tecnológica | Funcionalidades Chave | Prós para o Solar Playground | Contras/Considerações | Comunidade de Desenvolvedores no Brasil |
| :---- | :---- | :---- | :---- | :---- |
| **React \+ Mapbox GL JS \+ mapbox-gl-draw** | Ecossistema rico, mapas de alto desempenho, ferramentas de desenho maduras. | Bom para interações complexas, extensa documentação, bom suporte da comunidade. | Curva de aprendizado pode ser íngreme, custos de token Mapbox em grande escala. | Alta |
| **Vue.js \+ Leaflet \+ Leaflet.draw** | Leve, fácil de integrar, código aberto, boa comunidade. | Curva de aprendizado mais suave para alguns, totalmente gratuito. | Desempenho pode ser um gargalo com muitos objetos no mapa, menos funcionalidades prontas. | Média a Alta |
| **Angular \+ Mapbox GL JS (via ngx-mapbox-gl)** | Estrutura robusta para aplicações grandes, tipagem forte. | Adequado para equipes já familiarizadas com Angular, boa manutenibilidade para projetos grandes. | Pode ser excessivo para um "playground" mais simples, curva de aprendizado de Angular. | Média |
| **Vanilla JS \+ Leaflet/OpenLayers \+ Draw Plugins** | Controle máximo, sem sobrecarga de framework. | Leve, flexível. | Maior esforço de desenvolvimento para funcionalidades de UI, gerenciamento de estado manual. | Média (para bibliotecas específicas) |

A escolha dependerá da experiência da equipe de desenvolvimento, dos requisitos de desempenho de longo prazo e do orçamento para possíveis custos de API (como tokens Mapbox).

### **C. Lógica Backend e Integração de Dados (Conceitual)**

Embora o frontend possa realizar estimativas muito básicas, cálculos mais precisos ou complexos se beneficiariam de uma API backend.

* **API para Cálculos Solares:**  
  * Pode ser inspirada na estrutura e funções do pvlib-python 31, que fornece modelos robustos e testados. Se Python for usado no backend, a lógica do pvlib pode ser aproveitada para cálculos chave.  
  * Alternativamente, para uma pilha totalmente JavaScript, modelos mais simples 30 poderiam ser adaptados e expandidos.  
* **Gerenciamento de Conjuntos de Dados Brasileiros:**  
  * **Dados de Irradiação:** Um serviço backend para consultar e servir dados do INPE 17 com base em latitude/longitude. Esses dados podem ser pré-processados e armazenados em um banco de dados mais acessível.  
  * **Parâmetros Regulatórios:** Um banco de dados de configuração para regras de GD da ANEEL, percentuais do Fio B, etc., que possa ser atualizado conforme as regulamentações mudam.20  
* **Dados do Usuário:** Armazenar projetos, layouts e entradas do usuário de forma segura.

### **D. Considerações de "Código": Padrões Arquiteturais**

Uma arquitetura bem pensada é crucial para a manutenibilidade e escalabilidade.

* **Componentes de UI:** Projetar componentes de UI reutilizáveis (ex: ferramentas de desenho no mapa, configurador de painel, cartões de resultados) para consistência e facilidade de manutenção, inspirado em sistemas de design como o Unity Design System da ASU.40  
* **Gerenciamento de Estado:** Para interatividade complexa (estado do mapa, configurações de painel, resultados de simulação), usar uma biblioteca de gerenciamento de estado robusta (ex: Redux, Zustand para React; Vuex para Vue).  
* **Comunicação com API:** Padrões claros para comunicação frontend-backend (ex: APIs RESTful, GraphQL).  
* **Modularidade:** Projetar a aplicação em módulos (ex: definição do local, layout do painel, motor de simulação, exibição de resultados) para melhor organização e escalabilidade.

## **V. Considerações Avançadas e Melhorias Futuras (Além do Playground Inicial)**

Embora o foco inicial seja um "playground" simplificado, é importante vislumbrar evoluções futuras que podem agregar valor significativo.

### **A. Incorporando Análise de Sombreamento Mais Detalhada**

Atualmente, ferramentas profissionais como Aurora Solar 6, PVsyst 27 e Helioscope 8 oferecem análises de sombreamento 3D sofisticadas. Uma evolução natural para o playground seria ir além de uma simples porcentagem de perda, permitindo, por exemplo, o desenho de obstáculos 3D simples (como edifícios próximos ao arranjo) e a visualização do impacto de suas sombras. Isso representaria um aumento considerável na complexidade, mas também na precisão das estimativas.

### **B. Sugestões de Otimização Orientadas por IA**

A inteligência artificial pode ser uma aliada poderosa na otimização de projetos solares.2 Futuramente, o playground poderia incorporar funcionalidades como:

* Sugestão de layouts de painéis otimizados dentro da área definida para maximizar a produção de energia ou o número de painéis.  
* Recomendação de ajustes de inclinação/azimute com base na localização e no sombreamento modelado.

### **C. Colaboração Multiusuário e Compartilhamento de Projetos**

Permitir que múltiplos usuários visualizem ou editem um projeto simultaneamente pode ser valioso, especialmente para equipes de instaladores ou para fins educacionais. Funcionalidades como snapshots compartilháveis (inspirado no Atlas Search Playground 2) ou colaboração em tempo real (como no Pixso 41) poderiam ser exploradas.

### **D. Modelagem Financeira Detalhada e Geração de Propostas**

Para usuários que necessitam de análises mais aprofundadas, o playground poderia evoluir para incluir:

* Métricas financeiras mais complexas (VPL, TIR, LCOE).  
* Opções de financiamento, incluindo linhas de crédito específicas do Brasil, como o BNDES Finem.56  
* Geração de propostas detalhadas e personalizáveis, aproximando-se das capacidades de ferramentas profissionais.5

### **E. Adaptação às Regulamentações Brasileiras em Evolução**

O setor elétrico brasileiro é dinâmico, com regulamentações da ANEEL que podem mudar.57 O sistema deve ser projetado para facilitar a atualização de estruturas tarifárias, regras de GD e cálculos do Fio B. A manutenção de um banco de dados de parâmetros regulatórios no backend (mencionado na Seção IV.C) é fundamental para essa adaptabilidade.  
O "playground", em sua essência, é projetado para um dimensionamento inicial e simplificado. Usuários que necessitam de relatórios bancáveis ou engenharia detalhada precisarão de ferramentas mais avançadas. No entanto, o playground pode educar os usuários sobre os fatores envolvidos no design solar. Assim, uma melhoria futura potencial poderia ser uma funcionalidade de "exportar para ferramenta profissional" ou um ponto de transição claro, onde o layout básico e os parâmetros definidos no playground possam servir como ponto de partida para análises mais detalhadas em softwares como PVsyst ou Aurora Solar. Isso implica projetar estruturas de dados com potencial compatibilidade futura em mente ou até mesmo estabelecer parcerias com fornecedores de ferramentas profissionais existentes.

## **VI. Recomendações Chave e Roteiro de Implementação**

Para transformar a visão do Solar Playground Studio em realidade, uma abordagem estratégica e iterativa é recomendada.

### **A. Abordagem de Desenvolvimento Faseado para o Playground Studio**

Um desenvolvimento faseado permite entregar valor rapidamente e refinar o produto com base no feedback do usuário.

* **Fase 1 (MVP \- Produto Mínimo Viável):**  
  * **Foco:** Interação central do "playground".  
  * Interação de mapa principal para definição de área (desenho de polígono).  
  * Posicionamento básico de painéis (seleção de paleta limitada, clique para posicionar).  
  * Busca de irradiação solar baseada na localização (dados do INPE).  
  * Cálculo simplificado de produção de energia.  
  * Exibição de métricas chave (kWp, kWh anual).  
* **Fase 2:**  
  * **Foco:** Estimativas financeiras e regulatórias básicas.  
  * Adicionar estimativa financeira básica (custo/kWp, payback simples).  
  * Introduzir informações simplificadas sobre as regras de GD brasileiras.  
  * Relatório básico (resumo em PDF).  
  * Mais ferramentas de layout de painel (preenchimento de arranjo, alinhamento).  
* **Fase 3 e Além:**  
  * **Foco:** Maior detalhamento e funcionalidades avançadas.  
  * Opções de configuração mais detalhadas (painéis personalizados, escolha de inversores).  
  * Considerações de sombreamento aprimoradas (mesmo que ainda simplificadas).  
  * Exibição mais detalhada do impacto tarifário brasileiro.  
  * Considerar funcionalidades avançadas com base no feedback do usuário (ex: IA, colaboração).

### **B. Priorizando a UX Central para o Lançamento Inicial**

A interação com o mapa, o posicionamento dos painéis e o ciclo de feedback imediato são primordiais. Estes devem ser intuitivos e agradáveis desde a primeira versão.10 O "sentimento de playground" deve ser estabelecido corretamente desde o início, pois é o diferencial da ferramenta.

### **C. Testes de Usabilidade e Estratégia de Iteração**

O design e desenvolvimento devem ser um processo contínuo de aprendizado e melhoria.

* Conduzir testes de usabilidade com as personas alvo (proprietários residenciais, instaladores) em cada fase do desenvolvimento.10  
* Utilizar ferramentas como gravação de sessão (UXCam 10, Sprig 39) ou simples observação para coletar feedback.  
* Iterar sobre o design com base no feedback recebido. O conceito de "playground" se presta bem à prototipagem rápida e testes.10

### **D. Checklist para Alcançar uma UX/UI de Benchmark**

Para garantir que o produto final atinja a qualidade de benchmark desejada, as seguintes questões devem ser respondidas afirmativamente:

* A tarefa primária (dimensionar um sistema solar) é fácil e intuitiva de iniciar?  
* A interação com o mapa é suave e previsível para definição de área e posicionamento de painéis?  
* O usuário recebe feedback claro e imediato sobre suas ações?  
* Informações complexas (como as tarifas brasileiras) são apresentadas de forma simplificada e compreensível?  
* O design visual é limpo, organizado e consistente?10  
* A ferramenta é acessível a uma ampla gama de usuários?10  
* O "playground" parece envolvente e encoraja a exploração?  
* Os dados e regulamentações específicas do Brasil estão integrados de forma precisa e útil?

## **Conclusão e Recomendações Finais**

A criação de um Solar Playground Studio para o dimensionamento de projetos solares no Brasil representa uma oportunidade significativa para simplificar um processo técnico complexo, tornando-o acessível a um público mais amplo, desde proprietários residenciais até instaladores e estudantes. Ao adotar os princípios de um "playground" – interatividade, feedback imediato e facilidade de experimentação – a ferramenta pode se diferenciar no mercado.  
**Recomendações Chave:**

1. **Foco Incansável na Experiência do Usuário (UX):** A simplicidade, clareza e intuitividade devem guiar todas as decisões de design. A interação com o mapa e o posicionamento visual dos painéis são os pilares da experiência "playground" e devem ser impecáveis.  
2. **Integração Profunda do Contexto Brasileiro:** A utilização de dados de irradiação do INPE, a correta interpretação e apresentação simplificada das regras de Geração Distribuída da ANEEL (Lei 14.300, REN 1059/2023) e a consideração das componentes tarifárias (TUSD, TE, Fio B) são cruciais para a relevância e utilidade da ferramenta no Brasil.  
3. **Desenvolvimento Iterativo e Baseado em Feedback:** Adotar uma abordagem de desenvolvimento faseado (MVP primeiro) e incorporar testes de usabilidade contínuos com usuários reais brasileiros garantirá que o produto evolua de acordo com as necessidades do mercado.  
4. **Escolha Tecnológica Estratégica:** Selecionar frameworks frontend (como React com Mapbox GL JS) que ofereçam bom desempenho para visualizações geoespaciais interativas e uma arquitetura backend modular que possa lidar com cálculos solares e dados regulatórios é fundamental.  
5. **Gerenciamento de Expectativas:** Posicionar o "playground" como uma ferramenta de estimativa preliminar e educacional, especialmente em suas fases iniciais. Relatórios e saídas devem refletir essa natureza, orientando os usuários para consultas profissionais para projetos detalhados e bancáveis.

Ao seguir este roteiro, é possível desenvolver uma ferramenta de dimensionamento solar que não apenas atenda às necessidades técnicas de seus usuários, mas que também ofereça uma experiência engajadora, educativa e alinhada com as especificidades do promissor mercado solar brasileiro. A chave para o sucesso reside em equilibrar a sofisticação técnica necessária para o dimensionamento solar com a simplicidade e o prazer de uso inerentes a um verdadeiro "playground digital".

#### **Referências citadas**

1. Getting Started with Scratch \- Scratch Programming Playground, acessado em maio 27, 2025, [https://inventwithscratch.com/book/chapter1.html](https://inventwithscratch.com/book/chapter1.html)  
2. A New Way to Query: Introducing the Atlas Search Playground | MongoDB, acessado em maio 27, 2025, [https://www.mongodb.com/blog/post/a-new-way-to-query-introducing-atlas-search-playground](https://www.mongodb.com/blog/post/a-new-way-to-query-introducing-atlas-search-playground)  
3. ARCH 3601 Architecture Design Studio V — Garcia — TTU — Mini Topical PLAYGROUND, acessado em maio 27, 2025, [https://www.depts.ttu.edu/architecture/documents/course-syllabi/3601\_Playground\_Garcia.pdf](https://www.depts.ttu.edu/architecture/documents/course-syllabi/3601_Playground_Garcia.pdf)  
4. 42 Best Form Design Examples \- Eleken, acessado em maio 27, 2025, [https://www.eleken.co/blog-posts/form-design-examples](https://www.eleken.co/blog-posts/form-design-examples)  
5. Top 10+ Best Solar Design Software Tools for Installers: 2025 \- Arka360, acessado em maio 27, 2025, [https://arka360.com/ros/best-solar-design-software-proposal-tool](https://arka360.com/ros/best-solar-design-software-proposal-tool)  
6. Aurora Solar: The World's \#1 Solar Design Software, acessado em maio 27, 2025, [https://aurorasolar.com/](https://aurorasolar.com/)  
7. OpenSolar: Leading Free Solar Software, acessado em maio 27, 2025, [https://www.opensolar.com/](https://www.opensolar.com/)  
8. HelioScope | Commercial Solar Software, acessado em maio 27, 2025, [https://www.helioscope.com/](https://www.helioscope.com/)  
9. VoltEnergy: Empowering Businesses with Solar Energy Solutions, acessado em maio 27, 2025, [https://ripenapps.com/case-study/voltenergy-renewable-distributed-energy](https://ripenapps.com/case-study/voltenergy-renewable-distributed-energy)  
10. The Ultimate UI/UX Design Guide-Principles, Processes, and Best Practices \- Impala Intech, acessado em maio 27, 2025, [https://impalaintech.com/blog/ui-ux-guide/](https://impalaintech.com/blog/ui-ux-guide/)  
11. Best Practices for Rocking UX Design \- Lucid Software, acessado em maio 27, 2025, [https://lucid.co/blog/ux-design-best-practices](https://lucid.co/blog/ux-design-best-practices)  
12. Map UI Design: Best Practices, Tools & Real-World Examples \- Eleken, acessado em maio 27, 2025, [https://www.eleken.co/blog-posts/map-ui-design](https://www.eleken.co/blog-posts/map-ui-design)  
13. Draw a polygon and calculate its area | Mapbox GL JS | Mapbox, acessado em maio 27, 2025, [https://www.mapbox.com/mapbox-gl-js/example/mapbox-gl-draw/](https://www.mapbox.com/mapbox-gl-js/example/mapbox-gl-draw/)  
14. Drawing Layer (Library) | Maps JavaScript API | Google for Developers, acessado em maio 27, 2025, [https://developers.google.com/maps/documentation/javascript/drawinglayer](https://developers.google.com/maps/documentation/javascript/drawinglayer)  
15. 10 Best Basemaps for Contextualizing Geospatial Data to Enhance Readability, acessado em maio 27, 2025, [https://www.maplibrary.org/812/best-basemaps-for-contextualizing-geospatial-data/](https://www.maplibrary.org/812/best-basemaps-for-contextualizing-geospatial-data/)  
16. Visualize geospatial data \- illustreets, acessado em maio 27, 2025, [https://illustreets.com/product/visualize-geospatial-data/](https://illustreets.com/product/visualize-geospatial-data/)  
17. Brazil Solar Irradiation \- Kaggle, acessado em maio 27, 2025, [https://www.kaggle.com/arvati/brazil-solar-irradiation](https://www.kaggle.com/arvati/brazil-solar-irradiation)  
18. To take advantage of the Sun \- Revista Fapesp, acessado em maio 27, 2025, [https://revistapesquisa.fapesp.br/en/to-take-advantage-of-the-sun/](https://revistapesquisa.fapesp.br/en/to-take-advantage-of-the-sun/)  
19. Brazilian Atlas of Solar Energy \- LABREN, acessado em maio 27, 2025, [http://labren.ccst.inpe.br/atlas\_2017-en.html](http://labren.ccst.inpe.br/atlas_2017-en.html)  
20. ANEEL — Agência Nacional de Energia Elétrica \- Portal Gov.br, acessado em maio 27, 2025, [https://www.aneel.gov.br/](https://www.aneel.gov.br/)  
21. Lei 14.300: entenda o marco legal da microgeração de energia \- Aldo Solar, acessado em maio 27, 2025, [https://www.aldo.com.br/blog/sobre-a-lei-14-300/](https://www.aldo.com.br/blog/sobre-a-lei-14-300/)  
22. www.cemig.com.br, acessado em maio 27, 2025, [https://www.cemig.com.br/wp-content/uploads/2025/02/cartilha-faturamento-gd.pdf](https://www.cemig.com.br/wp-content/uploads/2025/02/cartilha-faturamento-gd.pdf)  
23. Renewable Energy UI/UX Design Services \- reloadux, acessado em maio 27, 2025, [https://reloadux.com/ui-ux/renewable-energy/](https://reloadux.com/ui-ux/renewable-energy/)  
24. What are some good examples of UI design involving maps and map overlays? \- Quora, acessado em maio 27, 2025, [https://www.quora.com/What-are-some-good-examples-of-UI-design-involving-maps-and-map-overlays](https://www.quora.com/What-are-some-good-examples-of-UI-design-involving-maps-and-map-overlays)  
25. leaflet.pm and mapedit · Issue \#86 \- GitHub, acessado em maio 27, 2025, [https://github.com/r-spatial/mapedit/issues/86](https://github.com/r-spatial/mapedit/issues/86)  
26. acessado em dezembro 31, 1969, [https://www.aurorasolar.com/help](https://www.aurorasolar.com/help)  
27. PVsyst | Photovoltaic software, Design and simulate photovoltaic ..., acessado em maio 27, 2025, [https://www.pvsyst.com/](https://www.pvsyst.com/)  
28. PVsyst documentation, acessado em maio 27, 2025, [https://www.pvsyst.com/help/](https://www.pvsyst.com/help/)  
29. HelioScope, acessado em maio 27, 2025, [https://help-center.helioscope.com/hc/en-us](https://help-center.helioscope.com/hc/en-us)  
30. Solar Lead Generation Calculator \- ConvertCalculator, acessado em maio 27, 2025, [https://www.convertcalculator.com/templates/solar-power-calculator/](https://www.convertcalculator.com/templates/solar-power-calculator/)  
31. pvlib python — pvlib python 0.12.0 documentation, acessado em maio 27, 2025, [https://pvlib-python.readthedocs.io/](https://pvlib-python.readthedocs.io/)  
32. pvlib.irradiance.reindl, acessado em maio 27, 2025, [https://pvlib-python.readthedocs.io/en/v0.6.2/generated/pvlib.irradiance.reindl.html](https://pvlib-python.readthedocs.io/en/v0.6.2/generated/pvlib.irradiance.reindl.html)  
33. Lei 14.300: O Marco Legal da Geração Distribuída | Neosolar, acessado em maio 27, 2025, [https://www.neosolar.com.br/aprenda/saiba-mais/lei-14300-marco-legal-geracao-distribuida](https://www.neosolar.com.br/aprenda/saiba-mais/lei-14300-marco-legal-geracao-distribuida)  
34. Lei 14.300: entenda as mudanças e saiba o que diz a lei | Portal Solar, acessado em maio 27, 2025, [https://www.portalsolar.com.br/lei-14300](https://www.portalsolar.com.br/lei-14300)  
35. Micro e Minigeração Distribuída — Agência Nacional de Energia Elétrica \- Portal Gov.br, acessado em maio 27, 2025, [https://www.gov.br/aneel/pt-br/acesso-a-informacao/perguntas-frequentes/micro-e-minigeracao-distribuida](https://www.gov.br/aneel/pt-br/acesso-a-informacao/perguntas-frequentes/micro-e-minigeracao-distribuida)  
36. O que é a "taxação do sol" e como funciona o imposto? | Portal Solar, acessado em maio 27, 2025, [https://www.portalsolar.com.br/taxacao-do-sol](https://www.portalsolar.com.br/taxacao-do-sol)  
37. Como Calcular o Valor do Fio B para Energia Solar | Instituto Solar, acessado em maio 27, 2025, [https://institutosolar.com/como-calcular-o-valor-do-fio-b-para-energia-solar/](https://institutosolar.com/como-calcular-o-valor-do-fio-b-para-energia-solar/)  
38. Solar Panel Monitoring App UI UX Design | Solar Tracker \- Dribbble, acessado em maio 27, 2025, [https://dribbble.com/shots/25435747-Solar-Panel-Monitoring-App-UI-UX-Design-Solar-Tracker](https://dribbble.com/shots/25435747-Solar-Panel-Monitoring-App-UI-UX-Design-Solar-Tracker)  
39. 22 Best UI/UX Design Software Of 2025: Reviewed & Compared \- The CX Lead, acessado em maio 27, 2025, [https://thecxlead.com/tools/best-ui-ux-design-software/](https://thecxlead.com/tools/best-ui-ux-design-software/)  
40. User experience (UX) design standards and guidelines \- ASU brand guide, acessado em maio 27, 2025, [https://brandguide.asu.edu/execution-guidelines/web/ux-design](https://brandguide.asu.edu/execution-guidelines/web/ux-design)  
41. \[OFFICIAL\] Pixso \- A Free Online UI/UX Design Tool, acessado em maio 27, 2025, [https://pixso.net/](https://pixso.net/)  
42. Plugins and frameworks | Mapbox GL JS, acessado em maio 27, 2025, [https://docs.mapbox.com/mapbox-gl-js/plugins/](https://docs.mapbox.com/mapbox-gl-js/plugins/)  
43. Using with Mapbox \- Deck.gl, acessado em maio 27, 2025, [https://deck.gl/docs/developer-guide/base-maps/using-with-mapbox](https://deck.gl/docs/developer-guide/base-maps/using-with-mapbox)  
44. Examples \- react-map-gl, acessado em maio 27, 2025, [https://visgl.github.io/react-map-gl/examples](https://visgl.github.io/react-map-gl/examples)  
45. alexwing/deck.gl-demo-visualization-test \- GitHub, acessado em maio 27, 2025, [https://github.com/alexwing/deck.gl-demo-visualization-test](https://github.com/alexwing/deck.gl-demo-visualization-test)  
46. Heatmap Visualization With Deck.gl \- HackerNoon, acessado em maio 27, 2025, [https://hackernoon.com/heatmap-visualization-with-deckgl](https://hackernoon.com/heatmap-visualization-with-deckgl)  
47. Add Maps to a Vue.js 3 application using Leaflet.js and OpenStreetMap \- YouTube, acessado em maio 27, 2025, [https://www.youtube.com/watch?v=gmrsMJLOCQw](https://www.youtube.com/watch?v=gmrsMJLOCQw)  
48. JavaScript Visualization | Tom Sawyer Software, acessado em maio 27, 2025, [https://blog.tomsawyer.com/javascript-visualization](https://blog.tomsawyer.com/javascript-visualization)  
49. pvlib/pvlib-python: A set of documented functions for simulating the performance of photovoltaic energy systems. \- GitHub, acessado em maio 27, 2025, [https://github.com/pvlib/pvlib-python](https://github.com/pvlib/pvlib-python)  
50. pvlib python \- Wikipedia, acessado em maio 27, 2025, [https://en.wikipedia.org/wiki/Pvlib\_python](https://en.wikipedia.org/wiki/Pvlib_python)  
51. PV\_LIB Toolbox \- PV Performance Modeling Collaborative (PVPMC), acessado em maio 27, 2025, [https://pvpmc.sandia.gov/tools/pv\_lib-toolbox/](https://pvpmc.sandia.gov/tools/pv_lib-toolbox/)  
52. Solar Calculator — Sming documentation, acessado em maio 27, 2025, [https://sming.readthedocs.io/en/5.0.0/\_inc/Sming/Libraries/SolarCalculator/index.html](https://sming.readthedocs.io/en/5.0.0/_inc/Sming/Libraries/SolarCalculator/index.html)  
53. EMR Software Development: How to Guide \- NEKLO, acessado em maio 27, 2025, [https://neklo.com/blog/emr-software-development](https://neklo.com/blog/emr-software-development)  
54. Tarifas — Agência Nacional de Energia Elétrica \- Portal Gov.br, acessado em maio 27, 2025, [https://www.gov.br/aneel/pt-br/assuntos/tarifas](https://www.gov.br/aneel/pt-br/assuntos/tarifas)  
55. resolução normativa aneel nº 1.059, de 7 de fevereiro de 2023, acessado em maio 27, 2025, [https://www2.aneel.gov.br/cedoc/ren20231059.html](https://www2.aneel.gov.br/cedoc/ren20231059.html)  
56. BNDES Finem \- Geração de energia, acessado em maio 27, 2025, [https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-finem-energia](https://www.bndes.gov.br/wps/portal/site/home/financiamento/produto/bndes-finem-energia)  
57. Latin American Electric Utility Regulatory Framework: Signs Of Increased Political Interference | S\&P Global Ratings, acessado em maio 27, 2025, [https://www.spglobal.com/ratings/en/research/articles/250109-latin-american-electric-utility-regulatory-framework-signs-of-increased-political-interference-13256294](https://www.spglobal.com/ratings/en/research/articles/250109-latin-american-electric-utility-regulatory-framework-signs-of-increased-political-interference-13256294)  
58. Aiming For Zero: How Latin America is Decarbonizing its Power Sector \- BASHAM, acessado em maio 27, 2025, [https://www.basham.com.mx/mailing/Aiming-for-Zero.pdf](https://www.basham.com.mx/mailing/Aiming-for-Zero.pdf)  
59. Brazil Energy Journal \- Mayer Brown, acessado em maio 27, 2025, [https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2022/06/brazil-energy-journal--june--power-distributed-generation.pdf](https://www.mayerbrown.com/-/media/files/perspectives-events/publications/2022/06/brazil-energy-journal--june--power-distributed-generation.pdf)  
60. DISTRIBUTED GENERATION OF PHOTOVOLTAIC SOLAR ENERGY: IMPACTS OF ANEEL'S NEW REGULATION PROPOSAL ON INVESTMENT ATTRACTIVENESS \- Redalyc, acessado em maio 27, 2025, [https://www.redalyc.org/journal/2734/273468107011/html/](https://www.redalyc.org/journal/2734/273468107011/html/)