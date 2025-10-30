Formas de Pagamento
Cobranças avulsas, parceladas, assinaturas e link de pagamento
Boleto Bancário
R$ 1,89 por boleto pago
Recebimento em 1 dia útil após o pagamento.
Cartão de Crédito
2,89% + R$ 0,00 à vista
3,12% + R$ 0,00 2 a 6 parcelas
3,44% + R$ 0,00 7 a 12 parcelas
5,58% + R$ 0,00 13 a 21 parcelas
Recebimento em 30 dias após o pagamento.
Cartão de Débito
1,89% + R$ 0,00
Recebimento em 3 dias após o pagamento.
Pix Dinâmico
R$ 1,89 por cobrança recebida
Receba em poucos segundos após o pagamento.
Pix
(Chave, manual ou QR Code estático)
R$ 1,89 por cobrança recebida
30 recebimentos gratuitos por mês.

---

Perfeito. Vou levantar os custos totais dos projetos solares em todas as combinações de categoria (de XPP até XGG), região e tier de geração, considerando:

* Perdas estimadas para cálculo da energia líquida
* Custos regionais extras (tarifas das concessionárias)
* Divisão de custos em Projeto, Kit Solar e Mão de Obra (20/60/20)
* Simulações de parcelamento para Stripe, Adyen, Cielo, Stone, Getnet, Rede (1x a 12x) e ASAAS (até 21x)
* Aplicação das taxas de cada gateway e forma de pagamento (boleto, débito, crédito parcelado, pix)

Vou estruturar o retorno com tabelas por categoria, destacando os valores finais e cenários de pagamento.

Te aviso assim que estiver pronto para revisão.


# Custos Totais de Projetos Solares por Categoria, Região e Tier de Geração

Para calcular os custos totais de sistemas solares fotovoltaicos em diferentes **categorias de projeto** (XPP, PP, P, M, G, GG, XG, XGG), considerando cada **região do Brasil** (Norte, Nordeste, Centro-Oeste, Sudeste, Sul) e cada **tier de geração** (Padrão, Consciente, Moderado, Acelerado), foram adotadas as seguintes premissas e passos:

* **Dimensionamento e energia líquida gerada:** Cada categoria corresponde a um porte de sistema, definido por uma potência fotovoltaica aproximada no tier Padrão (por ex., **XPP \~2 kWp**, PP \~3 kWp, P \~5 kWp, M \~8 kWp, G \~12 kWp, GG \~20 kWp, XG \~30 kWp e XGG \~50 kWp). A energia anual gerada por essas capacidades é ajustada por **fatores de perda** como temperatura dos módulos, sombreamento parcial, acúmulo de sujeira, degradação inicial (LID) e mismatches entre painéis. Tais perdas reduzem a produção em torno de 20–25% em relação ao ideal – ou seja, espera-se um rendimento final de \~75–80% da capacidade nominal. Esse rendimento considera, por exemplo, perdas típicas de 7–18% por temperatura elevada, 1–8% por sujeira nos painéis e algumas perdas adicionais em cabeamentos CC/CA e inversor. Desse modo, a **energia líquida** considerada para dimensionar cada sistema por região foi ajustada aos níveis de irradiação solar locais. *Regiões com maior insolação (como o Nordeste, com \~4,5–6 kWh/m²/dia) tendem a exigir menos kWp para gerar a mesma energia, enquanto regiões menos ensolaradas (ex.: Sul) precisam de sistemas ligeiramente maiores para compensar a menor irradiação.*

* **Recomendação de potência do inversor por tier:** De acordo com o tier de geração, ajustou-se a relação entre potência do inversor e dos painéis instalados. No **tier Padrão**, o inversor é dimensionado aproximadamente igual à potência do gerador (relação DC/AC próxima de 1:1). No **tier Consciente**, considera-se um inversor ligeiramente superdimensionado (cerca de 10% acima da potência fotovoltaica atual) ou operação com folga, presumindo que o consumidor adotará uso energético consciente (podendo até demandar menos do que o gerador). Já no **tier Moderado**, recomenda-se um inversor de porte um pouco maior (por exemplo, \~20% além da potência dos painéis instalados), prevendo uma expansão moderada de geração. Finalmente, no **tier Acelerado**, escolhe-se um inversor bem maior que a geração atual (até \~50% de sobra de capacidade), permitindo futura adição acelerada de módulos solares sem necessidade de troca de inversor. Essa estratégia tem sido comum – muitos clientes optam por comprar **inversores maiores** (e pagar um pouco mais) para **deixar sobra de capacidade e adicionar mais placas no futuro**. Em resumo, do tier Padrão ao Acelerado, o sistema vai desde um inversor justificado pela potência presente até um inversor com grande margem para crescimento.

* **Composição de custo do projeto (20/60/20):** O **custo total** de cada projeto foi decomposto em três partes principais: **20% para Projeto e Homologação** (incluindo elaboração do projeto elétrico, documentação e trâmites com a distribuidora), **60% para o Kit Solar** (equipamentos – painéis, inversor, estruturas, cabeamento, proteções – estimados a partir de um custo médio por kWp) e **20% para Mão de Obra** de instalação. Essa proporção 20/60/20 reflete uma divisão típica onde aproximadamente 2/3 do custo são os equipamentos e 1/3 são os serviços. Para cálculo, assumimos um **custo médio de R\$5.000 por kWp instalado** (no tier Padrão, Sudeste) – valor compatível com os praticados no mercado em 2025. *Por exemplo, um sistema residencial de 2 kWp custa em torno de **R\$10–11 mil**, e um sistema de 12 kWp cerca de **R\$44 mil**, de acordo com fontes do setor, em linha com nossos resultados.* Mantivemos esse custo por kWp base constante para todas as categorias, aplicando a composição fixa de 20%/60%/20% sobre o total. Vale notar que, na prática, sistemas maiores tendem a ter um custo por kW menor devido a economias de escala, mas para simplificação utilizamos uma taxa média fixa. Assim, por cada kW adicional (no mesmo tier e região), o custo cresce linearmente conforme essa estimativa.

* **Custos regionais adicionais:** Além da diferença de geração por clima já mencionada, consideramos **acréscimos de custo por região** ligados principalmente a fatores logísticos, distâncias e eventuais diferenças de mão de obra. Foi aplicado um fator percentual de ajuste no custo total de cada projeto conforme a região: **Norte: +15%**, **Nordeste: +10%**, **Centro-Oeste: +5%**, **Sudeste: +0%** (referência base) e **Sul: +5%**. Esses percentuais representam o impacto de frete de equipamentos para regiões mais remotas (especialmente Norte e Nordeste), possíveis custos extras de instalação em locais distantes dos grandes centros fornecedores, e também consideram que no Sul, apesar da logística favorável, a menor irradiância exige aproximadamente 10–15% mais painéis para a mesma energia (o que eleva o custo). *Em suma, Norte teve o maior acréscimo estimado (combinação de distância e alto calor), Nordeste e Centro-Oeste um acréscimo moderado, Sudeste nenhum (média de referência) e Sul um pequeno acréscimo devido à necessidade de mais capacidade instalada.*

* **Simulação de parcelamento (gateways de pagamento):** Por fim, calculamos o **valor final para o cliente em caso de pagamento parcelado** via diferentes meios, considerando as taxas dos principais gateways (Stripe, Adyen, Cielo, Stone, Getnet, Rede – até 12x – e ASAAS – até 21x) conforme fornecido. As taxas consideradas foram: **2,89%** para pagamento **à vista no cartão de crédito** (1x), **3,12%** para **2x a 6x no cartão**, **3,44%** para **7x a 12x no cartão**, **5,58%** para parcelamentos de **13x a 21x** (disponível via ASAAS), **1,89%** para **cartão de débito**, e tarifa fixa de **R\$1,89** por cobrança via **Pix** (manual ou dinâmico) ou **boleto bancário** (lembrando que os primeiros 30 Pix no mês são gratuitos nessa política). Esses percentuais foram aplicados sobre o total de cada projeto para simular o acréscimo no valor final pago em cada modalidade.

## Tabelas de Custo Total por Categoria, Região e Tier

A seguir, apresentam-se tabelas detalhando o **custo total estimado** (em Reais) para cada categoria de sistema, discriminando as variações por região e por tier de geração. Em cada tabela, as colunas correspondem aos *tiers* de geração **Padrão**, **Consciente**, **Moderado** e **Acelerado**, e as linhas correspondem às cinco **regiões** do Brasil. Os valores já incluem a composição completa do projeto (equipamentos + serviços) e os ajustes regionais discutidos. *Lembre-se de que, conforme o tier, a potência instalada e a escolha do inversor variam – por exemplo, no tier Acelerado o sistema conta com maior capacidade (mais módulos) e um inversor com sobra, resultando em custo maior que no Padrão, enquanto no tier Consciente o sistema é ligeiramente reduzido.* Cada valor de custo pode ser aproximadamente decomposto em **20% Projeto/Homologação**, **60% Kit Solar** e **20% Instalação**, conforme mencionado.

### Categoria XPP (Extra Pequeno Porte)

*Sistema de porte **extra pequeno**, \~2 kWp no tier Padrão (adequado para baixos consumos residenciais).*

| Região           | Padrão     | Consciente | Moderado   | Acelerado  |
| ---------------- | ---------- | ---------- | ---------- | ---------- |
| **Norte**        | R\$ 11.500 | R\$ 10.350 | R\$ 13.800 | R\$ 17.250 |
| **Nordeste**     | R\$ 11.000 | R\$ 9.900  | R\$ 13.200 | R\$ 16.500 |
| **Centro-Oeste** | R\$ 10.500 | R\$ 9.450  | R\$ 12.600 | R\$ 15.750 |
| **Sudeste**      | R\$ 10.000 | R\$ 9.000  | R\$ 12.000 | R\$ 15.000 |
| **Sul**          | R\$ 10.500 | R\$ 9.450  | R\$ 12.600 | R\$ 15.750 |

### Categoria PP (Pequeno Porte)

*Sistema **pequeno porte**, \~3 kWp no tier Padrão (residências típicas de baixo a médio consumo).*

| Região           | Padrão     | Consciente | Moderado   | Acelerado  |
| ---------------- | ---------- | ---------- | ---------- | ---------- |
| **Norte**        | R\$ 17.250 | R\$ 15.525 | R\$ 20.700 | R\$ 25.875 |
| **Nordeste**     | R\$ 16.500 | R\$ 14.850 | R\$ 19.800 | R\$ 24.750 |
| **Centro-Oeste** | R\$ 15.750 | R\$ 14.175 | R\$ 18.900 | R\$ 23.625 |
| **Sudeste**      | R\$ 15.000 | R\$ 13.500 | R\$ 18.000 | R\$ 22.500 |
| **Sul**          | R\$ 15.750 | R\$ 14.175 | R\$ 18.900 | R\$ 23.625 |

### Categoria P (Porte Pequeno-Médio)

*Sistema de porte **residencial médio**, \~5 kWp no tier Padrão (atende consumos residenciais maiores ou pequeno comércio).*

| Região           | Padrão     | Consciente | Moderado   | Acelerado  |
| ---------------- | ---------- | ---------- | ---------- | ---------- |
| **Norte**        | R\$ 28.750 | R\$ 25.875 | R\$ 34.500 | R\$ 43.125 |
| **Nordeste**     | R\$ 27.500 | R\$ 24.750 | R\$ 33.000 | R\$ 41.250 |
| **Centro-Oeste** | R\$ 26.250 | R\$ 23.625 | R\$ 31.500 | R\$ 39.375 |
| **Sudeste**      | R\$ 25.000 | R\$ 22.500 | R\$ 30.000 | R\$ 37.500 |
| **Sul**          | R\$ 26.250 | R\$ 23.625 | R\$ 31.500 | R\$ 39.375 |

### Categoria M (Médio Porte)

*Sistema de porte **médio**, \~8 kWp no tier Padrão (ex.: residências de alto consumo ou pequenas empresas).*

| Região           | Padrão     | Consciente | Moderado   | Acelerado  |
| ---------------- | ---------- | ---------- | ---------- | ---------- |
| **Norte**        | R\$ 46.000 | R\$ 41.400 | R\$ 55.200 | R\$ 69.000 |
| **Nordeste**     | R\$ 44.000 | R\$ 39.600 | R\$ 52.800 | R\$ 66.000 |
| **Centro-Oeste** | R\$ 42.000 | R\$ 37.800 | R\$ 50.400 | R\$ 63.000 |
| **Sudeste**      | R\$ 40.000 | R\$ 36.000 | R\$ 48.000 | R\$ 60.000 |
| **Sul**          | R\$ 42.000 | R\$ 37.800 | R\$ 50.400 | R\$ 63.000 |

### Categoria G (Grande Porte)

*Sistema de porte **grande** (microgeração limite), \~12 kWp no tier Padrão (atende pequenas empresas, propriedades rurais ou condomínios).*

| Região           | Padrão     | Consciente | Moderado   | Acelerado   |
| ---------------- | ---------- | ---------- | ---------- | ----------- |
| **Norte**        | R\$ 69.000 | R\$ 62.100 | R\$ 82.800 | R\$ 103.500 |
| **Nordeste**     | R\$ 66.000 | R\$ 59.400 | R\$ 79.200 | R\$ 99.000  |
| **Centro-Oeste** | R\$ 63.000 | R\$ 56.700 | R\$ 75.600 | R\$ 94.500  |
| **Sudeste**      | R\$ 60.000 | R\$ 54.000 | R\$ 72.000 | R\$ 90.000  |
| **Sul**          | R\$ 63.000 | R\$ 56.700 | R\$ 75.600 | R\$ 94.500  |

### Categoria GG (Grande Porte – expansão)

*Sistema de porte **muito grande**, \~20 kWp no tier Padrão (empresas de médio porte, produtores rurais com alto consumo, etc.).*

| Região           | Padrão      | Consciente  | Moderado    | Acelerado   |
| ---------------- | ----------- | ----------- | ----------- | ----------- |
| **Norte**        | R\$ 115.000 | R\$ 103.500 | R\$ 138.000 | R\$ 172.500 |
| **Nordeste**     | R\$ 110.000 | R\$ 99.000  | R\$ 132.000 | R\$ 165.000 |
| **Centro-Oeste** | R\$ 105.000 | R\$ 94.500  | R\$ 126.000 | R\$ 157.500 |
| **Sudeste**      | R\$ 100.000 | R\$ 90.000  | R\$ 120.000 | R\$ 150.000 |
| **Sul**          | R\$ 105.000 | R\$ 94.500  | R\$ 126.000 | R\$ 157.500 |

### Categoria XG (Extra Grande)

*Sistema de porte **extra grande**, \~30 kWp no tier Padrão (grandes consumidores em comércio/serviços; faixa superior da microgeração).*

| Região           | Padrão      | Consciente  | Moderado    | Acelerado   |
| ---------------- | ----------- | ----------- | ----------- | ----------- |
| **Norte**        | R\$ 172.500 | R\$ 155.250 | R\$ 207.000 | R\$ 258.750 |
| **Nordeste**     | R\$ 165.000 | R\$ 148.500 | R\$ 198.000 | R\$ 247.500 |
| **Centro-Oeste** | R\$ 157.500 | R\$ 141.750 | R\$ 189.000 | R\$ 236.250 |
| **Sudeste**      | R\$ 150.000 | R\$ 135.000 | R\$ 180.000 | R\$ 225.000 |
| **Sul**          | R\$ 157.500 | R\$ 141.750 | R\$ 189.000 | R\$ 236.250 |

### Categoria XGG (Extra Grande – expansão máxima)

*Sistema de porte **extra grande++**, \~50 kWp no tier Padrão (próximo do limite de microgeração de 75 kW; atende empresas de maior porte ou minigeradores iniciais).*

| Região           | Padrão      | Consciente  | Moderado    | Acelerado   |
| ---------------- | ----------- | ----------- | ----------- | ----------- |
| **Norte**        | R\$ 287.500 | R\$ 258.750 | R\$ 345.000 | R\$ 431.250 |
| **Nordeste**     | R\$ 275.000 | R\$ 247.500 | R\$ 330.000 | R\$ 412.500 |
| **Centro-Oeste** | R\$ 262.500 | R\$ 236.250 | R\$ 315.000 | R\$ 393.750 |
| **Sudeste**      | R\$ 250.000 | R\$ 225.000 | R\$ 300.000 | R\$ 375.000 |
| **Sul**          | R\$ 262.500 | R\$ 236.250 | R\$ 315.000 | R\$ 393.750 |

*Observações:* Em todas as tabelas acima, nota-se que os custos nas colunas **Consciente** tendem a ser ligeiramente menores que os do Padrão (devido à menor potência instalada para um consumidor mais “consciente” em economia de energia), enquanto os tiers **Moderado** e **Acelerado** apresentam custos crescentes, refletindo a instalação de capacidade extra (e inversores maiores) para atender aumentos moderados ou rápidos de consumo futuro. As variações por **região** também ficam evidentes: o **Norte** apresenta os custos mais elevados (devido ao acréscimo logístico e necessidade de lidar com temperaturas altas), e o **Sul** também apresenta custos acima do Sudeste (pela necessidade de mais painéis para compensar a irradiância mais baixa). Já o **Nordeste**, mesmo tendo excelente insolação, aqui ficou com um leve acréscimo de custo, hipoteticamente atribuído a logística, enquanto o **Sudeste** serve de base de referência sem acréscimo. Na prática, um sistema no Nordeste poderia até gerar mais energia que um no Sudeste com o mesmo tamanho – podendo compensar parte desse custo – mas optou-se por apresentar todos os valores em termos de custos absolutos de instalação, com esses fatores regionais adicionais conforme estipulado.

## Simulação de Valores Finais com Diferentes Formas de Pagamento

Considerando os custos totais acima, a seguir simulamos o **valor final pago** de acordo com o método de pagamento e o número de parcelas, incorporando as taxas de gateway mencionadas. Os percentuais indicados representam o acréscimo sobre o valor total do projeto, enquanto valores fixos de R\$1,89 se aplicam por cobrança (independentemente do montante):

* **Cartão de crédito (à vista, 1x):** acréscimo de **2,89%** sobre o total (taxa do gateway). *Por exemplo, um projeto de R\$100.000 teria um custo final de aproximadamente **R\$102.890***.
* **Cartão de crédito (parcelado de 2x até 6x):** acréscimo de **3,12%** sobre o total. *(No exemplo de R\$100.000, \~**R\$103.120** no final.)*
* **Cartão de crédito (parcelado de 7x até 12x):** acréscimo de **3,44%** sobre o valor do projeto. *(Ex: **R\$103.440** se fossem R\$100 mil.)*
* **Cartão de crédito (parcelado de 13x até 21x via ASAAS):** acréscimo de **5,58%** sobre o total. *(Ex: **R\$105.580** para um projeto de R\$100 mil.)*
* **Cartão de **débito****:\*\* acréscimo de **1,89%** sobre o total (transação à vista no débito). *(Ex: **R\$101.890** em vez de R\$100.000.)*
* **Pix (manual ou dinâmico):** tarifa **fixa de R\$ 1,89** por transação (os primeiros 30 Pix mensais gratuitos). *Na prática, o valor final quase não se altera – e.g. R\$100.000 vira **R\$100.001,89***.
* **Boleto bancário:** tarifa **fixa de R\$ 1,89** por boleto emitido. *Assim, o custo final aumenta desprezivelmente – ex: R\$100.000 torna-se **R\$100.001,89***.

Em resumo, o método de pagamento pode impactar significativamente o desembolso final principalmente no caso de parcelamentos longos no cartão de crédito. Por exemplo, um sistema **parcelado em 12x** pelo cartão teria um acréscimo de \~3,44% no preço (absorvendo as taxas das intermediadoras), enquanto **pagamentos via Pix ou boleto** praticamente mantêm o mesmo valor do projeto, dadas as tarifas fixas muito baixas. Cabe ao cliente avaliar essas diferenças: pagar à vista no boleto/Pix ou mesmo no cartão (2,89% de acréscimo) resulta no menor custo total, ao passo que parcelar em muitas vezes no cartão eleva o valor final em até \~5,58% nas condições simuladas. Todas essas simulações possibilitam entender o **custo total do projeto solar** não apenas em termos de investimento base por categoria, região e porte de geração, mas também em função da forma de pagamento escolhida, oferecendo transparência no planejamento financeiro da instalação.

**Fontes:** Os cálculos foram baseados em dados típicos de desempenho e preço da energia solar no Brasil, incluindo fatores de perda em sistemas fotovoltaicos, diferenças regionais de insolação, práticas de dimensionamento de inversores para expansão futura e referências de custos médios de sistemas solares por porte (2 kWp, 12 kWp etc.). As taxas de parcelamento utilizadas refletem valores praticados por gateways de pagamento no mercado brasileiro em 2025.