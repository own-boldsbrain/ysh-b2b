

# **Análise Funcional da Biblioteca pvlib-python: Um Guia Estruturado por Jobs-to-be-Done, Entradas e Saídas**

## **Secção 1: Componentes Fundamentais para a Simulação Fotovoltaica**

A base de qualquer simulação fotovoltaica robusta assenta numa representação precisa e modular da realidade física. A arquitetura da biblioteca pvlib-python reflete este princípio através de uma separação clara de conceitos: o contexto geográfico ("onde"), o equipamento físico ("o quê") e a sua orientação ("como"). Esta secção disseca as classes fundamentais que servem como os blocos de construção para todos os modelos subsequentes, demonstrando como a sua conceção deliberada permite uma modelagem flexível, reutilizável e escalável.

### **1.1 Definição do Contexto Geográfico: pvlib.location.Location**

A classe pvlib.location.Location serve como o pilar geográfico para qualquer simulação. A sua função transcende a de um mero contentor de dados; é um objeto ativo que encapsula o contexto espacial e temporal, tornando-se a fonte única de verdade para todos os cálculos dependentes da localização.

#### **Jobs to be Done (JTBDs)**

O propósito fundamental que um utilizador "contrata" a classe Location para realizar é duplo. Primariamente, quando se modela um sistema fotovoltaico, é imperativo **definir o contexto geográfico e climático exato da sua instalação para que todos os cálculos subsequentes (como a posição do sol e os efeitos atmosféricos) sejam precisos e relevantes para aquele local**. Secundariamente, o utilizador procura **um objeto centralizado que lide com todas as conversões de fuso horário e cálculos astronómicos, eliminando a necessidade de gerir estes parâmetros separadamente em cada etapa da simulação**. A classe Location responde a esta necessidade ao associar os dados geográficos aos métodos que os utilizam, uma decisão de design que simplifica a API e aumenta a robustez do código.1  
Esta abordagem de encapsulamento é um princípio de design fundamental na pvlib-python. Em vez de exigir que o utilizador passe repetidamente parâmetros como latitude e longitude para múltiplas funções, a biblioteca promove a passagem de um único objeto Location. Isto não só reduz a verbosidade do código e a probabilidade de erro humano, mas também reflete o fluxo de trabalho lógico de um engenheiro: o primeiro passo em qualquer projeto fotovoltaico é, invariavelmente, definir a sua localização. A estrutura da biblioteca, especialmente da classe ModelChain, impõe esta lógica, exigindo um objeto Location na sua inicialização, reconhecendo que sem o "onde", a simulação não pode começar.3

#### **User Inputs (Entradas do Usuário)**

A instanciação de um objeto Location requer um conjunto mínimo de informações geográficas, com parâmetros adicionais para aumentar a precisão:

* latitude (float, obrigatório): A latitude do local em graus decimais. Valores positivos indicam o hemisfério Norte.5  
* longitude (float, obrigatório): A longitude do local em graus decimais. Valores positivos indicam o leste do meridiano de Greenwich.5  
* tz (str, int, float, ou datetime.tzinfo, opcional, default='UTC'): O fuso horário do local. É fortemente recomendado o uso de uma string da base de dados IANA (ex: 'America/Sao\_Paulo', 'Europe/Lisbon') para garantir o tratamento correto do horário de verão.5  
* altitude (float, opcional): A altitude acima do nível do mar em metros. Se este parâmetro não for fornecido, a biblioteca tentará obter um valor aproximado a partir de um serviço de busca online, embora a especificação manual seja preferível para maior precisão.5  
* name (str, opcional): Uma string descritiva para identificar a localização, útil em projetos com múltiplos locais.5

#### **System Outputs (Saídas do Sistema)**

A saída direta da instanciação é um objeto pvlib.location.Location. No entanto, o verdadeiro valor deste objeto reside nas saídas dos seus métodos, que utilizam os atributos internos para realizar cálculos complexos e retornar estruturas de dados prontas para análise, tipicamente DataFrames da biblioteca pandas:

* get\_solarposition(): Retorna um DataFrame indexado por tempo com colunas detalhando a posição solar, como apparent\_zenith, zenith, azimuth, e elevation.6  
* get\_airmass(): Retorna um DataFrame com as séries temporais de massa de ar relativa e absoluta.7  
* get\_clearsky(): Calcula e retorna um DataFrame com as estimativas de irradiância de céu claro (GHI, DNI, DHI) para o local.5  
* get\_sun\_rise\_set\_transit(): Retorna os horários de nascer do sol, pôr do sol e trânsito solar para as datas fornecidas.5

### **1.2 Abstração do Sistema Físico: pvlib.pvsystem.PVSystem**

A classe pvlib.pvsystem.PVSystem é a representação digital do hardware fotovoltaico. Ela foi concebida para descrever a coleção e as interações dos componentes do sistema, como módulos e inversores, de uma forma abstrata e independente da sua localização física.8

#### **Jobs to be Done (JTBDs)**

O principal "trabalho" da classe PVSystem é permitir ao utilizador **criar um 'gémeo digital' do seu hardware fotovoltaico, especificando todos os componentes e as suas interconexões (módulos por string, strings por inversor), para que possa simular o seu comportamento sob diferentes condições operacionais**. Um JTBD secundário, mas igualmente importante, é **definir as características do sistema uma única vez e depois testar o seu desempenho em diferentes locais ou com diferentes dados meteorológicos, sem ter de redefinir o hardware a cada vez**.  
Esta separação de preocupações entre o hardware (PVSystem) e a geografia (Location) é uma decisão arquitetónica poderosa. Permite que um engenheiro avalie o mesmo design de sistema em múltiplos locais (por exemplo, em São Paulo e em Salvador) simplesmente combinando o mesmo objeto PVSystem com diferentes objetos Location dentro de uma ModelChain. Esta modularidade facilita análises comparativas e otimizações de design de forma eficiente e escalável.

#### **User Inputs (Entradas do Usuário)**

A construção de um objeto PVSystem envolve a especificação detalhada dos seus componentes:

* arrays (list de objetos Array, opcional): A forma recomendada e mais flexível de definir os arranjos de módulos do sistema. Se este parâmetro for usado, outros parâmetros relacionados com os módulos, como surface\_tilt, são ignorados.8  
* Parâmetros de Módulo (usados se arrays não for fornecido): surface\_tilt (inclinação), surface\_azimuth (azimute), module\_parameters (dicionário com especificações do módulo), modules\_per\_string (módulos em série), strings\_per\_inverter (strings em paralelo).8  
* inverter\_parameters (dict ou pandas.Series): Um dicionário ou Série contendo os parâmetros para o modelo do inversor (ex: eficiência, limites de potência).8  
* losses\_parameters (dict ou pandas.Series): Parâmetros para modelos de perdas diversas, como perdas óhmicas ou por sujidade.8  
* racking\_model (str, opcional): Especifica o tipo de estrutura de montagem (ex: 'open\_rack'), que influencia os modelos de cálculo de temperatura da célula.8

#### **System Outputs (Saídas do Sistema)**

A classe PVSystem atua como um orquestrador, utilizando os seus atributos para chamar funções de modelagem de nível inferior e produzir saídas de desempenho. A saída primária é o próprio objeto PVSystem instanciado. Os seus métodos, quando invocados (geralmente pela ModelChain), produzem séries temporais de dados de desempenho:

* pvwatts\_dc(), sapm(), singlediode(): Retornam a potência de corrente contínua (DC) em Watts.8  
* get\_ac(): Calcula a potência de corrente alternada (AC) em Watts, após as perdas de conversão do inversor.8  
* get\_cell\_temperature(): Estima a temperatura operacional das células fotovoltaicas em graus Celsius.8  
* get\_irradiance(): Calcula a irradiância no plano do arranjo (POA) em W/m².8  
* get\_iam(): Calcula o modificador de ângulo de incidência (IAM), um fator de perda devido à reflexão da luz em ângulos não perpendiculares.8

É importante notar que o PVSystem funciona como uma camada de abstração. Por exemplo, o seu método get\_irradiance não implementa a física da transposição diretamente; em vez disso, ele chama a função pvlib.irradiance.get\_total\_irradiance, passando os seus próprios atributos (como surface\_tilt) como argumentos.8 Esta arquitetura em camadas torna a biblioteca mais manutenível e extensível.

### **1.3 Modelagem de Agregados de Módulos: pvlib.pvsystem.Array**

A classe pvlib.pvsystem.Array representa um subconjunto fundamental de um PVSystem: uma coleção de módulos fotovoltaicos que partilham as mesmas características elétricas e a mesma orientação.10 Um PVSystem é, na sua essência, um contentor para um ou mais objetos Array.

#### **Jobs to be Done (JTBDs)**

O JTBD primário de um Array é **modelar um subconjunto homogéneo de um sistema fotovoltaico, onde todos os painéis são idênticos e estão virados para a mesma direção, para poder calcular a sua produção de energia de forma unificada**. A sua existência permite um JTBD secundário crucial: **construir sistemas complexos com múltiplas orientações (por exemplo, um telhado com águas a leste e a oeste), combinando diferentes Arrays num PVSystem maior**.  
Esta capacidade de composição é a chave para modelar sistemas do mundo real, que raramente são perfeitamente uniformes. Um sistema comercial pode ter uma secção no telhado plano e outra na fachada, cada uma com orientações e, portanto, perfis de produção, distintos. A pvlib aborda esta complexidade permitindo a criação de dois objetos Array separados, cada um com a sua própria orientação, que são depois agregados num único PVSystem. Esta abordagem oferece uma flexibilidade quase ilimitada para definir geometrias de sistema heterogéneas, uma capacidade essencial para a modelagem precisa.11

#### **User Inputs (Entradas do Usuário)**

A definição de um Array requer a especificação da sua orientação e das suas características elétricas e térmicas:

* mount (objeto FixedMount ou SingleAxisTrackerMount): Um objeto que define a estratégia de orientação do arranjo (fixa ou com seguimento solar).10  
* module\_parameters (dict ou pandas.Series): Parâmetros que descrevem o comportamento elétrico do módulo, necessários para modelos como o CEC ou SAPM.10  
* temperature\_model\_parameters (dict ou pandas.Series): Parâmetros para o modelo de temperatura da célula.12  
* modules\_per\_string (int, default=1): O número de módulos conectados em série para formar uma string.10  
* strings (int, default=1): O número de strings idênticas conectadas em paralelo.10

#### **System Outputs (Saídas do Sistema)**

A saída é um objeto Array instanciado. Este objeto possui métodos análogos aos do PVSystem (como get\_irradiance, get\_cell\_temperature), mas os seus cálculos são específicos para as características daquele Array particular.10 Quando um PVSystem com múltiplos Arrays é simulado através da ModelChain, os resultados para cada Array são tipicamente retornados como uma tupla de DataFrames ou Séries.3

### **1.4 Especificação de Estruturas de Montagem: pvlib.pvsystem.FixedMount**

A classe pvlib.pvsystem.FixedMount é um componente simples mas fundamental que representa uma estrutura de montagem com uma orientação estática.11 O seu propósito é encapsular os parâmetros de orientação de um arranjo fixo.

#### **Jobs to be Done (JTBDs)**

O seu JTBD é singular e direto: **especificar a inclinação e a orientação fixas dos painéis solares para que a biblioteca possa calcular corretamente o ângulo em que os raios solares os atingem**.  
A forma como esta classe interage com a classe Array é um exemplo elegante do padrão de design de software "Strategy". O Array precisa de conhecer a sua orientação, mas não quer ser responsável pela lógica de como essa orientação é determinada (se é fixa ou se muda com o tempo). Ao delegar esta responsabilidade a um objeto mount (a "estratégia"), o Array torna-se agnóstico em relação ao tipo de montagem. Ele simplesmente chama o método get\_orientation do objeto mount que lhe foi fornecido.14 Isto torna o sistema altamente extensível: um utilizador pode criar uma nova classe para um tipo de tracker de dois eixos, implementar um método get\_orientation, e passá-la para um Array sem modificar qualquer código existente na biblioteca.

#### **User Inputs (Entradas do Usuário)**

As entradas definem a orientação fixa da estrutura:

* surface\_tilt (float, default=0): O ângulo de inclinação da superfície em graus, onde 0 é horizontal e 90 é vertical.11  
* surface\_azimuth (float, default=180): O azimute da superfície em graus, seguindo a convenção de 0 para Norte, 90 para Leste, 180 para Sul e 270 para Oeste.11  
* racking\_model (str, opcional): Usado por modelos de temperatura para contabilizar a ventilação traseira do módulo.11  
* module\_height (float, opcional): A altura do módulo acima do solo, usada por alguns modelos de temperatura avançados.11

#### **System Outputs (Saídas do Sistema)**

A saída é um objeto FixedMount instanciado. O seu método get\_orientation retorna consistentemente os valores de surface\_tilt e surface\_azimuth com os quais foi inicializado, independentemente de outras entradas como a posição solar.14 Estes valores são então usados pelo Array e pelo PVSystem para os cálculos de irradiância.

## **Secção 2: Modelagem Ambiental e Geometria Solar**

Após a definição do sistema físico e da sua localização, a próxima etapa lógica na simulação fotovoltaica é modelar a fonte de energia — o sol — e a sua interação com a atmosfera terrestre. A pvlib-python fornece módulos dedicados para estes cálculos fundamentais, que servem como a base para a quantificação da energia solar disponível.

### **2.1 Determinação da Posição Solar: pvlib.solarposition**

O módulo pvlib.solarposition é dedicado ao cálculo preciso da posição do sol no céu para qualquer instante e localização na Terra. Esta informação geométrica é um pré-requisito indispensável para praticamente todos os outros cálculos numa simulação fotovoltaica.

#### **Jobs to be Done (JTBDs)**

O JTBD primário deste módulo é inequívoco: **para cada instante no tempo, preciso de saber exatamente onde o sol está no céu (os seus ângulos de zénite e azimute) a partir da minha localização, pois esta é a informação geométrica fundamental para todos os cálculos de irradiância**. Sem conhecer a posição do sol, é impossível determinar o ângulo de incidência dos raios solares nos painéis, um fator que domina a quantidade de energia capturada.

#### **User Inputs (Entradas do Usuário)**

As funções neste módulo, principalmente get\_solarposition, requerem informações de tempo e espaço:

* times (pandas.DatetimeIndex): Um índice de datas e horas, que deve ser localizado num fuso horário específico, para o qual a posição solar será calculada.6  
* latitude (float): A latitude do observador em graus decimais.  
* longitude (float): A longitude do observador em graus decimais.  
* altitude (float, opcional): A altitude em metros, usada para correções atmosféricas.  
* pressure (float, opcional): A pressão atmosférica local em Pascal. Se não for fornecida, pode ser estimada a partir da altitude.6  
* temperature (float, opcional): A temperatura do ar em graus Celsius, usada para correção da refração atmosférica.6

Na prática, os parâmetros de localização, altitude, pressão e temperatura são frequentemente passados de forma conveniente através de um único objeto Location, que chama get\_solarposition como um dos seus métodos.6

#### **System Outputs (Saídas do Sistema)**

A saída principal é um pandas.DataFrame cujas linhas correspondem aos times de entrada e cujas colunas contêm várias métricas da posição solar, incluindo 15:

* apparent\_zenith: O ângulo zenital aparente (corrigido para a refração atmosférica) em graus.  
* zenith: O ângulo zenital verdadeiro (geométrico) em graus.  
* apparent\_elevation: A elevação aparente (90 \- apparent\_zenith).  
* elevation: A elevação verdadeira.  
* azimuth: O ângulo azimutal em graus (N=0, E=90, S=180, W=270).  
* equation\_of\_time: A equação do tempo em minutos.

A biblioteca oferece múltiplos algoritmos subjacentes para estes cálculos, como spa\_python (baseado no algoritmo SPA da NREL) e ephemeris.16 Esta escolha permite que utilizadores avançados façam um trade-off entre a precisão computacional e a velocidade de execução. O algoritmo SPA é um padrão da indústria, conhecido pela sua alta precisão, sendo adequado para análises de "grau bancário". Outros métodos podem ser mais rápidos, o que pode ser vantajoso para simulações em larga escala ou aplicações em tempo real onde a velocidade é mais crítica do que a máxima precisão.

### **2.2 Quantificação dos Efeitos Atmosféricos: pvlib.airmass\_atmospheric**

O módulo pvlib.airmass\_atmospheric (referido em algumas versões como pvlib.atmosphere) lida com o cálculo da massa de ar e outras propriedades atmosféricas que atenuam e modificam a luz solar na sua passagem para a superfície.

#### **Jobs to be Done (JTBDs)**

O JTBD primário deste módulo é **quantificar a 'espessura' da atmosfera que a luz solar atravessa para chegar ao meu sistema, porque isso afeta a intensidade e o espectro da luz, o que é um dado crucial para modelos de irradiância e perdas espectrais**. A massa de ar é uma medida adimensional do caminho ótico através da atmosfera. Uma massa de ar de 1 corresponde ao caminho quando o sol está diretamente no zénite; valores maiores ocorrem quando o sol está mais próximo do horizonte.

#### **User Inputs (Entradas do Usuário)**

As funções para cálculo da massa de ar requerem o ângulo zenital do sol e, para maior precisão, informações sobre a pressão atmosférica local:

* zenith (numeric): O ângulo zenital do sol em graus. É importante notar que alguns modelos requerem o zénite aparente (corrigido pela refração), enquanto outros usam o zénite verdadeiro.17  
* pressure (numeric, opcional): A pressão atmosférica local em Pascal. Usada na função get\_absolute\_airmass para corrigir o valor da massa de ar para a altitude do local.18  
* model (str, opcional): Uma string que especifica o modelo empírico a ser usado para o cálculo. Exemplos incluem 'kastenyoung1989' (o padrão), 'simple' (uma simples função secante), e outros.17

O módulo também inclui funções utilitárias como pres2alt e alt2pres para converter entre pressão e altitude.18

#### **System Outputs (Saídas do Sistema)**

As funções retornam valores numéricos que representam a massa de ar:

* get\_relative\_airmass(): Retorna a massa de ar relativa, que é a massa de ar calculada ao nível do mar (pressão padrão).17  
* get\_absolute\_airmass(): Retorna a massa de ar absoluta, que é a massa de ar relativa corrigida pela pressão local. A fórmula é $AM\_{absolute} \= AM\_{relative} \\times \\frac{P}{P\_0}$, onde $P$ é a pressão local e $P\_0$ é a pressão padrão ao nível do mar (101325 Pa).18

A massa de ar raramente é um resultado final de interesse para o utilizador. Em vez disso, a sua importância reside no seu papel como uma variável intermediária crítica. Por exemplo, modelos de desempenho avançados como o SAPM (Sandia Array Performance Model) usam a massa de ar absoluta para calcular as perdas por descasamento espectral (a mudança na eficiência do módulo devido a variações no espectro da luz solar).8 Portanto, este módulo fornece uma peça fundamental que alimenta outros modelos mais complexos a jusante na cadeia de simulação, demonstrando a natureza interligada e sequencial da modelagem fotovoltaica.

## **Secção 3: Processamento e Transformação da Irradiância Solar**

A irradiância solar é a variável de entrada mais crítica para qualquer modelo de desempenho fotovoltaico. Esta secção explora o conjunto de ferramentas que a pvlib-python oferece para processar e transformar dados de irradiância. O fluxo de trabalho típico envolve dois passos principais: primeiro, a decomposição da irradiância global nos seus componentes direto e difuso, se necessário; e segundo, a transposição desses componentes do plano horizontal para o plano inclinado dos módulos. A biblioteca também fornece modelos avançados para tecnologias emergentes, como os módulos bifaciais.

#### **Tabela 3.1: Resumo dos Modelos de Irradiância**

| Módulo/Função | Modelo Principal | Job to be Done (JTBD) Primário | Entradas Chave | Saída Principal |
| :---- | :---- | :---- | :---- | :---- |
| irradiance.decomposition | ERBS, DISC, etc. | Estimar componentes DNI e DHI a partir de GHI, quando DNI/DHI não são medidos. | GHI, Posição Solar | DNI, DHI |
| irradiance.transposition | Perez, Hay-Davies, etc. | Calcular a irradiância total numa superfície inclinada (POA) a partir de componentes horizontais. | GHI, DNI, DHI, Geometria do Painel | Irradiância POA (Global, Direta, Difusa) |
| bifacial | pvfactors, infinite\_sheds | Calcular a irradiância nas faces frontal e traseira de módulos bifaciais para estimar o ganho bifacial. | Geometria do Sistema, Albedo, GHI, DNI, DHI | POA Frontal, POA Traseira |

Esta tabela serve como um guia rápido para navegar na funcionalidade de irradiância da biblioteca. Ela organiza os modelos não pela sua localização na API, mas pelo seu propósito fundamental, ajudando o utilizador a selecionar a ferramenta correta para o seu problema específico, seja ele preencher dados em falta (decomposição), projetar a luz numa superfície (transposição) ou modelar hardware avançado (bifacial).

### **3.1 Decomposição da Irradiância Global: pvlib.irradiance.decomposition**

Em muitas situações práticas, os dados meteorológicos disponíveis contêm apenas a Irradiância Horizontal Global (GHI), que é a soma de toda a radiação solar que atinge uma superfície horizontal. No entanto, para modelar com precisão um sistema inclinado, é essencial separar a GHI nos seus dois componentes principais: a Irradiância Normal Direta (DNI), que vem diretamente do disco solar, e a Irradiância Difusa Horizontal (DHI), que é espalhada pela atmosfera. O módulo de decomposição aborda este desafio.

#### **Jobs to be Done (JTBDs)**

O JTBD primário deste módulo é: **"Tenho dados de irradiância global (GHI), mas os meus modelos de transposição precisam dos componentes direto (DNI) e difuso (DHI) separadamente. Preciso de uma forma fiável de estimar estes componentes a partir dos dados que possuo."** A existência deste módulo é uma resposta direta a uma limitação prática comum dos dados do mundo real. Medir GHI é relativamente simples (requer um piranómetro), mas medir DNI é complexo (requer um pirheliómetro num tracker solar), tornando os dados de GHI muito mais abundantes. Este módulo preenche essa lacuna de dados, expandindo drasticamente a aplicabilidade da pvlib a uma gama mais ampla de fontes de dados meteorológicos.19

#### **User Inputs (Entradas do Usuário)**

Os modelos de decomposição, como erbs ou disc, normalmente requerem:

* ghi (numeric): A série temporal de Irradiância Horizontal Global em W/m².19  
* solar\_zenith (numeric): O ângulo zenital solar correspondente em graus.19  
* datetime\_or\_doy (pandas.DatetimeIndex ou int): O tempo ou dia do ano, necessário para que alguns modelos calculem a irradiância extraterrestre, que é usada como referência para a claridade do céu.19

#### **System Outputs (Saídas do Sistema)**

A saída é tipicamente um pandas.DataFrame ou um dicionário contendo as séries temporais estimadas para:

* dni: Irradiância Normal Direta em W/m².  
* dhi: Irradiância Difusa Horizontal em W/m².

Estes valores podem então ser usados como entrada para os modelos de transposição.19

### **3.2 Transposição da Irradiância para o Plano do Módulo (POA): pvlib.irradiance.transposition**

Uma vez que os componentes de irradiância (DNI, GHI, DHI) estão disponíveis para o plano horizontal, o próximo passo é calcular a quantidade de radiação que realmente incide na superfície inclinada dos módulos fotovoltaicos. Este processo é chamado de transposição.

#### **Jobs to be Done (JTBDs)**

O JTBD fundamental deste módulo é: **"Sei quanta luz solar está a atingir o solo horizontalmente, mas os meus painéis estão inclinados. Preciso de calcular a quantidade exata de luz (irradiância) que incide diretamente na superfície dos meus painéis, considerando a luz direta do sol, a luz difusa do céu e a luz refletida do solo."** Este passo representa o ponto de convergência crucial onde a geometria (posição do sol, orientação do painel) e a meteorologia (componentes da irradiância) se encontram para determinar a energia solar disponível para o sistema.  
A função principal, get\_total\_irradiance, calcula a irradiância total no plano do arranjo (POA) como a soma de três componentes: $I\_{POA, global} \= I\_{POA, beam} \+ I\_{POA, sky diffuse} \+ I\_{POA, ground diffuse}$.20

#### **User Inputs (Entradas do Usuário)**

A transposição requer um conjunto abrangente de entradas que descrevem a geometria e as condições de irradiância:

* surface\_tilt (numeric): A inclinação do painel em graus.20  
* surface\_azimuth (numeric): O azimute do painel em graus.20  
* solar\_zenith (numeric): O ângulo zenital solar em graus.20  
* solar\_azimuth (numeric): O ângulo azimutal solar em graus.20  
* dni (numeric): Irradiância Normal Direta em W/m².20  
* ghi (numeric): Irradiância Horizontal Global em W/m².20  
* dhi (numeric): Irradiância Difusa Horizontal em W/m².20  
* albedo (numeric, opcional): A refletividade da superfície do solo (um valor adimensional, e.g., 0.2 para relva, 0.8 para neve fresca).20  
* model (str, opcional): O nome do modelo a ser usado para calcular o componente difuso do céu no plano inclinado. As opções incluem 'isotropic', 'haydavies', 'reindl', 'perez', entre outros.20

#### **System Outputs (Saídas do Sistema)**

A função retorna uma estrutura de dados (tipicamente um OrderedDict ou pandas.DataFrame) que detalha os componentes da irradiância no plano do arranjo 20:

* poa\_global: A irradiância global total na superfície do módulo.  
* poa\_direct: O componente de feixe (direto) na superfície do módulo.  
* poa\_diffuse: A soma dos componentes difusos do céu e do solo.  
* poa\_sky\_diffuse: O componente difuso proveniente da cúpula celeste.  
* poa\_ground\_diffuse: O componente difuso refletido pelo solo.

A variedade de modelos de céu difuso disponíveis (perez, haydavies, etc.) reflete o facto de que a distribuição da luz difusa no céu (anisotropia) é complexa e varia com as condições atmosféricas. Não existe um único "melhor" modelo para todas as situações. Ao fornecer uma gama de opções validadas, a pvlib permite que os modeladores realizem análises de sensibilidade para quantificar a incerteza nos seus resultados, uma prática essencial em avaliações de produção de energia para fins de financiamento de projetos.

### **3.3 Cálculos Especializados de Irradiância (incluindo Bifacial): pvlib.irradiance (geral) e pvlib.bifacial**

Para além dos modelos padrão, a pvlib-python inclui funcionalidades para cenários mais complexos, destacando-se o seu suporte para a modelagem de sistemas bifaciais.

#### **Jobs to be Done (JTBDs)**

O JTBD para o módulo bifacial é: **"Estou a usar módulos bifaciais e preciso de estimar a energia adicional gerada pela parte de trás dos painéis, calculando a irradiância que eles recebem do solo e do céu."** A modelagem bifacial é significativamente mais complexa do que a monofacial, pois requer o cálculo detalhado dos "fatores de visão" — a fração do campo de visão de um ponto na parte de trás do módulo que é ocupada pelo solo iluminado pelo sol e pelo céu, tendo em conta o sombreamento das estruturas vizinhas. A integração de modelos sofisticados como o pvfactors e o infinite\_sheds demonstra o compromisso da pvlib em manter-se na vanguarda da tecnologia fotovoltaica.22

#### **User Inputs (Entradas do Usuário) (Bifacial)**

Os modelos bifaciais requerem os inputs padrão de irradiância e geometria, mais parâmetros detalhados sobre a configuração do sistema:

* gcr (float): A Relação de Cobertura do Solo (Ground Coverage Ratio), definida como a largura dos módulos a dividir pela distância entre os eixos das fileiras.22  
* height (numeric): A altura dos módulos acima do solo.22  
* pitch (numeric): A distância entre os eixos das fileiras de módulos.22  
* albedo (numeric): A refletividade do solo, um parâmetro de importância crítica para a produção da face traseira.22  
* bifaciality (float): A razão entre a eficiência da face traseira e a da face frontal do módulo.22

#### **System Outputs (Saídas do Sistema) (Bifacial)**

As funções de modelagem bifacial retornam os componentes de irradiância para ambas as faces do módulo 22:

* poa\_front: A irradiância incidente na superfície frontal em W/m².  
* poa\_back: A irradiância incidente na superfície traseira em W/m².  
* poa\_front\_absorbed, poa\_back\_absorbed: A irradiância absorvida por cada face, já contabilizando as perdas por ângulo de incidência (IAM).

## **Secção 4: Simulação Abrangente do Desempenho do Sistema**

Com a irradiância no plano dos módulos devidamente calculada, a pvlib-python oferece ferramentas para simular a cascata de conversão de energia, desde os fótons até à eletricidade AC injetada na rede. Esta secção explora a classe ModelChain, o motor de orquestração de alto nível da biblioteca, bem como os módulos que permitem a contabilização de perdas do mundo real e de componentes auxiliares do sistema.

### **4.1 A Classe ModelChain: Um Motor de Simulação de Ponta a Ponta**

A classe pvlib.modelchain.ModelChain é uma das funcionalidades mais poderosas da biblioteca, fornecendo uma interface unificada e de alto nível que automatiza a sequência de cálculos necessários para uma simulação de desempenho completa.3

#### **Jobs to be Done (JTBDs)**

O JTBD primário da ModelChain é: **"Quero simular a produção de energia AC do meu sistema fotovoltaico ao longo do tempo, a partir de dados meteorológicos, sem ter de chamar manualmente cada função de cálculo (posição solar, irradiância, temperatura da célula, potência DC, potência AC) numa sequência correta."** Ao encapsular o fluxo de trabalho padrão, a ModelChain reduz drasticamente a complexidade e a probabilidade de erro, tornando a modelagem fotovoltaica acessível a um público mais vasto.  
Um JTBD secundário é: **"Quero um local único para armazenar todos os resultados da minha simulação, tanto os finais (potência AC) como os intermediários (temperatura da célula, POA), para que possa facilmente analisá-los e depurar o meu modelo."**  
O fluxo de trabalho típico envolve três passos simples: 1\) criar uma instância da ModelChain fornecendo um PVSystem e uma Location; 2\) executar um dos seus métodos run\_model com dados meteorológicos; 3\) analisar os resultados, que são convenientemente armazenados no atributo results da instância.3 A ModelChain codifica a sequência lógica de dependências: a posição solar é calculada primeiro, seguida pela irradiância, depois a temperatura da célula, a potência DC e, finalmente, a potência AC. Esta encapsulação de um "fluxo de trabalho padrão" não só simplifica o uso, mas também promove a reprodutibilidade e a comparabilidade entre diferentes simulações.

#### **User Inputs (Entradas do Usuário)**

A ModelChain é configurada na sua inicialização e executada com dados meteorológicos:

* system (objeto PVSystem): O objeto que descreve o hardware do sistema a ser modelado.23  
* location (objeto Location): O objeto que define o contexto geográfico.23  
* weather (pandas.DataFrame): Fornecido ao método run\_model, este DataFrame deve conter séries temporais de dados meteorológicos, como GHI, DNI, DHI, temperatura do ar e velocidade do vento.4  
* **Seleção de Modelos** (str, opcional): Na inicialização, o utilizador pode especificar explicitamente quais modelos usar para cada etapa da cadeia, por exemplo, transposition\_model='perez', dc\_model='cec', temperature\_model='sapm'.23 Se não forem especificados, a ModelChain tentará inferir os modelos apropriados com base nos parâmetros disponíveis nos objetos PVSystem e Location.4

#### **System Outputs (Saídas do Sistema)**

Após a execução de um método run\_model, o atributo results da instância da ModelChain é preenchido com um objeto ModelChainResult. Este objeto é um contentor que armazena todas as séries temporais calculadas durante a simulação, incluindo 15:

* ac: A potência AC final em Watts.  
* dc: A potência DC em Watts.  
* cell\_temperature: A temperatura da célula em graus Celsius.  
* effective\_irradiance: A irradiância efetiva que contribui para a geração de corrente.  
* total\_irrad: Um DataFrame com os componentes da irradiância POA.  
* aoi: O ângulo de incidência em graus.  
* airmass: Um DataFrame com a massa de ar relativa e absoluta.  
* solar\_position: Um DataFrame com a posição solar.

A ModelChain também oferece flexibilidade através de múltiplos pontos de entrada. Para além do run\_model (que começa com dados de irradiância horizontal), existem os métodos run\_model\_from\_poa e run\_model\_from\_effective\_irradiance.23 Estes permitem que utilizadores com dados de partida diferentes (por exemplo, irradiância já medida no plano inclinado) entrem na cadeia de simulação no ponto apropriado, saltando os passos iniciais e evitando as suas incertezas associadas.

### **4.2 Modelagem de Efeitos e Perdas no Desempenho: effects\_on\_pv\_system\_output**

Uma simulação idealizada, que considera apenas a física básica, irá invariavelmente superestimar a produção de energia de um sistema real. A pvlib-python fornece uma suíte de modelos para quantificar o impacto de vários efeitos do mundo real que degradam o desempenho.

#### **Jobs to be Done (JTBDs)**

O JTBD coletivo destes módulos é: **"A minha simulação idealizada está a superestimar a produção. Preciso de contabilizar os efeitos do mundo real que reduzem o desempenho do meu sistema, como a acumulação de sujidade e neve nos painéis, o sombreamento de objetos próximos e as variações no espectro da luz solar."** A inclusão destes modelos de perdas é o que eleva a pvlib de uma ferramenta académica para uma ferramenta capaz de realizar "energy yield assessments" (EYAs) de "grau bancário", que são essenciais para a avaliação de risco e financiamento de projetos fotovoltaicos.  
A biblioteca organiza estes modelos em submódulos temáticos 25:

* **Soiling (Sujidade):** Modelos como soiling.hsu e soiling.kimber para estimar as perdas de produção devido à acumulação de poeira e outros detritos na superfície dos módulos.  
* **Snow (Neve):** Modelos como snow.coverage\_nrel para estimar a fração do arranjo coberta por neve e snow.dc\_loss\_nrel para calcular a perda de potência DC resultante.  
* **Shading (Sombreamento):** Funções para calcular o impacto do sombreamento, incluindo o sombreamento difuso e o sombreamento direto de objetos distantes (horizonte).  
* **Spectrum (Espectro):** Modelos como spectral\_factor\_firstsolar para calcular o modificador espectral, que ajusta a irradiância de banda larga para ter em conta como as variações no espectro da luz solar (influenciadas pela massa de ar, vapor de água, etc.) afetam a eficiência de diferentes tecnologias de células.

#### **User Inputs (Entradas do Usuário)**

As entradas variam muito entre os modelos. Por exemplo:

* Modelos de sujidade podem requerer taxas de acumulação de sujidade e dados de precipitação (chuva que limpa os painéis).  
* Modelos de neve requerem dados de queda de neve e temperatura.  
* Modelos espectrais requerem dados atmosféricos como massa de ar absoluta e água precipitável.

#### **System Outputs (Saídas do Sistema)**

As saídas são tipicamente:

* Fatores de perda adimensionais (valores entre 0 e 1\) que podem ser multiplicados pela potência ou irradiância.  
* Valores de potência DC ou irradiância já ajustados para as perdas.

### **4.3 Modelagem de Componentes Auxiliares: pvlib.transformer**

Para completar a simulação do sistema, a pvlib-python inclui modelos para componentes do "Balanço do Sistema" (BOS), como os transformadores.

#### **Jobs to be Done (JTBDs)**

O JTBD do módulo transformer é: **"A potência AC do meu inversor não é a potência final entregue à rede; há perdas no transformador de média/alta tensão. Preciso de modelar estas perdas para obter uma estimativa precisa da energia líquida exportada."** Embora estas perdas sejam relativamente pequenas (tipicamente 1-2%), em centrais de grande escala, elas representam uma quantidade significativa de energia e receita ao longo da vida útil do projeto. A sua inclusão permite uma simulação mais completa "do fóton ao medidor".

#### **User Inputs (Entradas do Usuário)**

A função simple\_efficiency requer os seguintes parâmetros do transformador 27:

* input\_power (numeric): A potência AC que entra no transformador, vinda do inversor (em Watts).  
* no\_load\_loss (numeric): As perdas fixas do transformador (perdas no núcleo), expressas como uma fração da sua potência nominal.  
* load\_loss (numeric): As perdas variáveis (perdas no cobre), que dependem do quadrado da carga, também expressas como uma fração da potência nominal.  
* transformer\_rating (numeric): A potência nominal do transformador em Volt-Ampères (VA).

#### **System Outputs (Saídas do Sistema)**

A função retorna um único valor 28:

* output\_power (numeric): A potência AC na saída do transformador (em Watts), após a dedução das perdas. O modelo também funciona de forma bidirecional, calculando o consumo do transformador a partir da rede durante a noite ou quando a central não está a produzir.28

## **Secção 5: Utilitários de Manipulação e Escalonamento de Dados**

Uma parte significativa do esforço em qualquer projeto de modelagem é a aquisição, limpeza e preparação dos dados de entrada. A pvlib-python reconhece este desafio e fornece um poderoso conjunto de ferramentas para simplificar estas tarefas, bem como funções para manipulações de dados mais avançadas, como o escalonamento espacial e temporal.

### **5.1 Operações de Entrada/Saída de Dados: pvlib.iotools**

O módulo pvlib.iotools é uma coleção de funções concebidas para facilitar a importação de dados meteorológicos de ficheiros locais e de fontes de dados online.

#### **Jobs to be Done (JTBDs)**

O JTBD primário do iotools é: **"Preciso de obter dados meteorológicos e de irradiância para a minha localização de simulação, e quero que eles estejam num formato limpo e padronizado que a pvlib possa usar diretamente, sem que eu tenha de escrever código personalizado para descarregar e formatar os dados de cada fonte diferente."** Este módulo atua como um redutor de atrito, abstraindo a complexidade de interagir com diferentes formatos de ficheiro e APIs web.  
Sem o iotools, um utilizador teria de navegar pela documentação de cada API, escrever código para pedidos HTTP, gerir autenticação, analisar respostas em formatos variados (JSON, CSV, etc.), e, crucialmente, renomear e reformatar os dados para corresponder às convenções da pvlib. Ao automatizar este processo, o iotools não só poupa um tempo considerável, mas também promove boas práticas, incentivando o uso de fontes de dados de alta qualidade e garantindo a consistência dos dados de entrada.

#### **User Inputs (Entradas do Usuário)**

As entradas variam dependendo da fonte de dados, mas geralmente incluem:

* latitude, longitude (float): As coordenadas geográficas para fontes de dados baseadas em localização.29  
* start, end (objetos datetime): O período de tempo para o qual os dados são solicitados.31  
* filename (str): O caminho para um ficheiro local para funções de leitura como read\_epw ou read\_tmy3.33  
* Credenciais (str, opcional): Chaves de API, nomes de utilizador ou senhas para aceder a serviços de dados comerciais ou protegidos, como SolarAnywhere ou BSRN.31

#### **System Outputs (Saídas do Sistema)**

A maioria das funções do iotools retorna uma tupla (data, metadata):

* data (pandas.DataFrame): Uma tabela de dados indexada por tempo, com colunas contendo as variáveis meteorológicas. A opção map\_variables=True (geralmente o padrão) renomeia automaticamente as colunas para os nomes padrão da pvlib (ex: 'temp\_air', 'wind\_speed', 'ghi').29  
* metadata (dict): Um dicionário contendo informações contextuais sobre os dados, como as coordenadas exatas da estação, elevação, fonte dos dados e os parâmetros de entrada usados na consulta.29

### **5.2 Escalonamento Espacial e Temporal de Dados: pvlib.scaling**

O módulo pvlib.scaling oferece funções para manipulações de dados mais avançadas, abordando problemas em diferentes escalas físicas.

#### **Jobs to be Done (JTBDs)**

Este módulo serve a dois JTBDs distintos, ilustrando a amplitude de aplicações da pvlib:

1. **pvsystem.scale\_voltage\_current\_power**: **"Calculei as curvas I-V para um único módulo, mas o meu sistema tem N módulos em série e M strings em paralelo. Preciso de uma forma simples de escalar a tensão, a corrente e a potência para representar o sistema completo."** Esta é uma operação fundamental na engenharia de sistemas, traduzindo o desempenho de um componente para o nível do sistema. A tensão de uma string é a soma das tensões dos módulos, enquanto a corrente do sistema é a soma das correntes das strings.  
2. **scaling.wvm**: **"Estou a estudar o impacto de uma grande central solar na estabilidade da rede elétrica. A produção de uma grande central é mais suave do que a de um único ponto porque as nuvens não cobrem toda a central ao mesmo tempo. Preciso de um modelo para simular este efeito de suavização espacial na minha série temporal de irradiância de um único ponto."** Este é um problema avançado, relevante para a investigação de integração de renováveis na rede.

A coexistência destas duas funções no âmbito do "escalonamento" demonstra que a pvlib foi concebida para servir tanto o engenheiro de projeto, focado na física de circuitos DC, como o investigador académico ou engenheiro de redes, focado na física atmosférica e na estatística de séries temporais em larga escala.

#### **User Inputs (Entradas do Usuário)**

* **pvsystem.scale\_voltage\_current\_power**:  
  * data (pandas.DataFrame): Um DataFrame contendo os resultados da simulação de um único módulo (ex: 'v\_mp', 'i\_mp', 'p\_mp').34  
  * voltage (numeric): O fator de escala para a tensão (geralmente o número de módulos por string).34  
  * current (numeric): O fator de escala para a corrente (geralmente o número de strings em paralelo).34  
* **scaling.wvm (Wavelet Variability Model)**:  
  * clearsky\_index (série temporal): A série temporal do índice de céu claro (GHI / GHI\_clearsky) a ser suavizada.35  
  * positions (array): As coordenadas (x, y) em metros dos subsistemas ou pontos dentro da central.35  
  * cloud\_speed (numeric): A velocidade média das nuvens em m/s.35

#### **System Outputs (Saídas do Sistema)**

* **pvsystem.scale\_voltage\_current\_power**: Retorna uma cópia do DataFrame de entrada com as colunas de tensão, corrente e potência multiplicadas pelos fatores de escala fornecidos.34  
* **scaling.wvm**: Retorna a série temporal do clearsky\_index suavizada, que pode então ser multiplicada pela irradiância de céu claro para obter uma série temporal de GHI que reflete a agregação espacial da central.35

## **Conclusões**

A análise detalhada da documentação da pvlib-python através da estrutura de Jobs-to-be-Done (JTBDs), Entradas e Saídas revela uma biblioteca de software que é simultaneamente poderosa, flexível e bem concebida. Várias conclusões de alto nível podem ser extraídas:

1. **Arquitetura Baseada em Princípios Sólidos:** A pvlib-python não é apenas uma coleção de funções, mas um ecossistema de modelagem coerente. A separação fundamental de preocupações entre o contexto geográfico (Location), o hardware (PVSystem) e a orientação (Mount) permite uma modularidade excecional. Esta arquitetura espelha o processo de pensamento de um engenheiro, facilitando fluxos de trabalho intuitivos e permitindo análises comparativas complexas com um esforço mínimo de reconfiguração.  
2. **Da Teoria à Prática de Engenharia:** A biblioteca abrange toda a cadeia de modelagem, desde os primeiros princípios da geometria solar e física atmosférica até às realidades práticas da engenharia. A inclusão de módulos para decomposição de irradiância, iotools para aquisição de dados e modelos para perdas do mundo real (sujidade, neve, espectro) demonstra um foco claro em resolver os problemas práticos que os engenheiros e analistas enfrentam diariamente. Isto eleva a pvlib-python de uma ferramenta puramente académica para uma suíte de software capaz de produzir avaliações de produção de energia de "grau bancário".  
3. **Orquestração de Alto Nível com Flexibilidade:** A classe ModelChain é a peça central que democratiza a modelagem fotovoltaica. Ao encapsular a sequência complexa de cálculos num único método run\_model, ela baixa a barreira de entrada para novos utilizadores e garante a consistência e reprodutibilidade. Ao mesmo tempo, a sua capacidade de inferir modelos, aceitar modelos definidos pelo utilizador e fornecer múltiplos pontos de entrada (run\_model\_from\_poa) oferece a flexibilidade necessária para utilizadores avançados e investigadores.  
4. **Evolução Contínua e Relevância para a Indústria:** A incorporação de modelos para tecnologias de ponta, como módulos bifaciais, e para problemas de investigação avançados, como a variabilidade de grandes centrais (scaling.wvm), indica que a pvlib-python é um projeto vivo e em evolução. O seu desenvolvimento orientado pela comunidade garante que a biblioteca se mantém relevante e continua a incorporar os mais recentes avanços científicos e tecnológicos da indústria fotovoltaica.

Em suma, a pvlib-python estabelece-se como uma ferramenta indispensável para qualquer profissional ou investigador no campo da energia solar. A sua arquitetura robusta, cobertura abrangente da cadeia de modelagem e foco na usabilidade prática tornam-na uma plataforma de referência para a simulação do desempenho de sistemas fotovoltaicos.

#### **Referências citadas**

1. pvlib.location.Location — pvlib-python 0.4.3+0.ge77dfee.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.4.3/generated/pvlib.location.Location.html](https://pvlib-python.readthedocs.io/en/v0.4.3/generated/pvlib.location.Location.html)  
2. pvlib.location — pvlib-python 0.2.1 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.2.1/\_modules/pvlib/location.html](https://pvlib-python.readthedocs.io/en/v0.2.1/_modules/pvlib/location.html)  
3. ModelChain — pvlib python 0.11.2 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.11.2/user\_guide/modelchain.html](https://pvlib-python.readthedocs.io/en/v0.11.2/user_guide/modelchain.html)  
4. ModelChain — pvlib-python 0.5.1+0.g72a7144.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.5.1/modelchain.html](https://pvlib-python.readthedocs.io/en/v0.5.1/modelchain.html)  
5. pvlib.location.Location — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.location.Location.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.location.Location.html)  
6. Location. get\_solarposition \- pvlib python \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.location.Location.get\_solarposition.html](https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.location.Location.get_solarposition.html)  
7. pvlib.location.Location.get\_airmass — pvlib python 0.10.3 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.10.3/reference/generated/pvlib.location.Location.get\_airmass.html](https://pvlib-python.readthedocs.io/en/v0.10.3/reference/generated/pvlib.location.Location.get_airmass.html)  
8. PVSystem \- pvlib python \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.PVSystem.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.PVSystem.html)  
9. pvlib.pvsystem.PVSystem — pvlib python 0.9.0+0.g518cc35.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.PVSystem.html](https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.PVSystem.html)  
10. pvlib.pvsystem.Array — pvlib python 0.13.1.dev16+g39867da0c ..., acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.Array.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.Array.html)  
11. pvlib.pvsystem.FixedMount — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.FixedMount.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.FixedMount.html)  
12. pvlib.pvsystem.Array — pvlib python 0.9.0+0.g518cc35.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.Array.html](https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.Array.html)  
13. pvlib.pvsystem.FixedMount — pvlib python 0.9.0+0.g518cc35.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.FixedMount.html](https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.FixedMount.html)  
14. pvlib.pvsystem.FixedMount.get\_orientation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.FixedMount.get\_orientation.html](https://pvlib-python.readthedocs.io/en/v0.9.0/generated/pvlib.pvsystem.FixedMount.get_orientation.html)  
15. pvlib.modelchain.ModelChainResult — pvlib python 0.13.0 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.modelchain.ModelChainResult.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.modelchain.ModelChainResult.html)  
16. Solar Position — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/solarposition.html](https://pvlib-python.readthedocs.io/en/stable/reference/solarposition.html)  
17. pvlib.atmosphere.get\_relative\_airmass, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.atmosphere.get\_relative\_airmass.html](https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.atmosphere.get_relative_airmass.html)  
18. pvlib.atmosphere — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/\_modules/pvlib/atmosphere.html](https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/atmosphere.html)  
19. DNI estimation models — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/irradiance/decomposition.html](https://pvlib-python.readthedocs.io/en/stable/reference/irradiance/decomposition.html)  
20. pvlib.irradiance.get\_total\_irradiance — pvlib python 0.11.2 ..., acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.11.2/reference/generated/pvlib.irradiance.get\_total\_irradiance.html](https://pvlib-python.readthedocs.io/en/v0.11.2/reference/generated/pvlib.irradiance.get_total_irradiance.html)  
21. pvlib.irradiance.perez — pvlib python 0.13.1.dev20+g2aa17b4f0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.irradiance.perez.html](https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.irradiance.perez.html)  
22. Bifacial — pvlib python 0.13.0 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/bifacial.html](https://pvlib-python.readthedocs.io/en/stable/reference/bifacial.html)  
23. pvlib.modelchain. \- pvlib python \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.modelchain.ModelChain.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.modelchain.ModelChain.html)  
24. pvlib.modelchain.ModelChain — pvlib-python 0.6.3+0.gf38fe07.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.modelchain.ModelChain.html](https://pvlib-python.readthedocs.io/en/v0.6.3/generated/pvlib.modelchain.ModelChain.html)  
25. Effects on PV System Output — pvlib python 0.13.1.dev16+ ..., acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/effects\_on\_pv\_system\_output/index.html](https://pvlib-python.readthedocs.io/en/latest/reference/effects_on_pv_system_output/index.html)  
26. API reference — pvlib python 0.9.0+0.g518cc35.dirty documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/v0.9.0/api.html](https://pvlib-python.readthedocs.io/en/v0.9.0/api.html)  
27. pvlib.transformer — pvlib python 0.13.0 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/\_modules/pvlib/transformer.html](https://pvlib-python.readthedocs.io/en/stable/_modules/pvlib/transformer.html)  
28. pvlib.transformer.simple\_efficiency — pvlib python 0.13.1.dev20+ ..., acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.transformer.simple\_efficiency.html](https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.transformer.simple_efficiency.html)  
29. pvlib.iotools.get\_pvgis\_hourly — pvlib python 0.13.1.dev18+gc5cd60e2e documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get\_pvgis\_hourly.html](https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get_pvgis_hourly.html)  
30. pvlib.iotools.get\_pvgis\_tmy — pvlib python 0.13.0 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.get\_pvgis\_tmy.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.get_pvgis_tmy.html)  
31. pvlib.iotools.get\_solaranywhere — pvlib python 0.13.0 documentation \- Read the Docs, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.get\_solaranywhere.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.get_solaranywhere.html)  
32. pvlib.iotools.get\_bsrn — pvlib python 0.13.1.dev16+g39867da0c documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get\_bsrn.html](https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.iotools.get_bsrn.html)  
33. pvlib.iotools.read\_epw — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.read\_epw.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.iotools.read_epw.html)  
34. pvlib.pvsystem.scale\_voltage\_current\_power — pvlib python 0.13.0 documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.scale\_voltage\_current\_power.html](https://pvlib-python.readthedocs.io/en/stable/reference/generated/pvlib.pvsystem.scale_voltage_current_power.html)  
35. pvlib.scaling.wvm — pvlib python 0.13.1.dev16+g39867da0c documentation, acessado em setembro 22, 2025, [https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.scaling.wvm.html](https://pvlib-python.readthedocs.io/en/latest/reference/generated/pvlib.scaling.wvm.html)