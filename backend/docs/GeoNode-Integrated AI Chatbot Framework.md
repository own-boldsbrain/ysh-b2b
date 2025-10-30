

# **A Techno-Economic Proposal for a Solar as a Service (SaaS) Business Model in Brazil: Leveraging oemof-solph for Optimal Design and Operation across Consumer Segments**

## **Executive Summary**

This report presents a comprehensive business proposal for the establishment of a "Solar as a Service" (SaaS) enterprise in Brazil. The proposal is predicated on a sophisticated, technology-driven approach that leverages the country's progressive regulatory framework for Distributed Generation (GD) and targets distinct consumer segments with tailored energy solutions. The core of the proposed strategy is the deployment of the oemof-solph energy system modeling framework as a central analytical engine to achieve superior techno-economic optimization, thereby creating a sustainable competitive advantage.  
Brazil's energy market presents a compelling opportunity, characterized by high retail electricity tariffs, a vast and underserved consumer base of over 80 million units, and a supportive legal structure under Law 14.300. This environment has fostered the emergence of SaaS models, but the market is rapidly evolving beyond simple equipment leasing towards integrated, data-driven energy platforms.  
The proposed business model is a multi-modal architecture designed to capture maximum market share by aligning specific service offerings with the primary GD modalities defined by the National Electric Energy Agency (ANEEL):

1. **Corporate Remote Solar (CRS):** A B2B offering based on the Autoconsumo Remoto modality, targeting multi-site commercial and industrial clients with zero-CAPEX solutions and guaranteed savings.  
2. **Community Solar Subscription (CSS):** A mass-market B2C and SME offering leveraging Geração Compartilhada to provide access to solar energy for customers without the physical space or capital for their own installations.  
3. **Condominium Energy Solutions (CES):** A niche, high-value service for residential and commercial condominiums under the EMUC framework.

The strategic differentiator for this venture will be the systematic application of oemof-solph across the entire business lifecycle. This powerful optimization tool will be used for: optimal sizing and siting of generation assets to maximize return on investment; data-driven design of customer contracts and pricing to maximize savings and adoption; portfolio-level management of energy credits to maximize revenue; and forward-looking assessment of emerging technologies like Battery Energy Storage Systems (BESS).  
This report provides a detailed analysis of the market landscape, the regulatory mechanics, consumer energy profiles, and the proposed business architecture. It culminates in a strategic implementation roadmap, positioning the venture to become a leading energy-tech platform in one of the world's most promising solar markets.

## **Section 1: The Brazilian Solar as a Service Landscape: A Market Primed for Disruption**

### **1.1 Market Drivers and Economic Viability**

The Brazilian market for Solar as a Service (SaaS) is underpinned by a confluence of powerful and enduring economic drivers. The most significant factor is the notable and consistent decline in the prices of photovoltaic (PV) generation systems, which has fundamentally improved the investment calculus for SaaS models, making them increasingly attractive and financially viable.1 This reduction in capital expenditure is juxtaposed with the reality of high and often volatile retail electricity tariffs faced by Brazilian consumers.2 This price differential creates a substantial value proposition for any service that can offer consumers a cheaper, more predictable alternative to purchasing power directly from the local utility.  
The addressable market is vast and largely untapped. Brazil has over 80 million electricity consumer units, the majority of whom can be characterized as passive "pagadores de conta" (bill payers) rather than engaged energy customers.3 This passivity represents a significant opportunity for a disruptive, customer-centric business model that simplifies access to renewable energy and delivers tangible savings without requiring upfront investment. Furthermore, the Brazilian government has signaled a clear and sustained interest in transforming the country's energy matrix towards greater sustainability. This commitment is most clearly demonstrated through the establishment of a robust legal framework for Distributed Generation (GD), which provides the necessary policy stability and legal security for long-term investments in the sector.4

### **1.2 Analysis of Incumbent Business Models**

The prevailing SaaS models in Brazil have largely adapted successful international precedents, primarily focusing on subscription and leasing structures that eliminate the primary barrier to adoption: high upfront capital costs.  
The **Subscription/Leasing Model** is the dominant approach. Companies like Solar21 were pioneers in this space, explicitly bringing the successful US leasing model to the Brazilian market.5 This involves the company owning and operating the solar assets while the customer pays a monthly fee for the energy produced, which is lower than their equivalent utility bill. GreenYellow offers a similar structure, providing a monthly subscription plan in exchange for the consumption of 100% clean energy.6 Lemon Energia effectively brands this as "placa solar as a service," where customers conceptually "rent" a specific number of solar panels located in a remote solar farm, corresponding to their energy needs, without any required works or installation on their property.3  
However, a more profound trend is the evolution towards a **Technology-Platform Model**. Leading companies are positioning themselves not merely as energy providers but as technology firms. Solar21 is a prime example, having developed a suite of integrated platforms and mobile applications for end customers, franchisees, and field technicians. These tools leverage artificial intelligence (AI) and data analytics for advanced system monitoring, providing customers with insights into their environmental impact and financial savings. The platform can even detect the level of dirt on solar panels and recommend the optimal time for cleaning by cross-referencing meteorological data with performance metrics.5 This tech-first approach is critical for delivering a superior customer experience, ensuring high system performance, and achieving the operational efficiency required for scaling. The success of this model is not just in deploying hardware, but in mastering the complex software challenge of matching variable generation with diverse consumer loads and navigating the intricate energy credit system.

### **1.3 Competitive Landscape and Strategic Positioning**

The Brazilian SaaS market, while nascent, is dynamic and attracting significant attention. Key players identified in the market include Solar21, GreenYellow, Lemon Energia, Sunne, and Origo Energia, each competing to establish a foothold.3 The market is experiencing what participants describe as "exponencial" growth, a sentiment validated by substantial venture capital investment.3 Lemon Energia's recent R$60 million funding round, earmarked for technology development, design, and geographic expansion from 6 to over 10 states, is a clear indicator of the sector's perceived potential.3  
The competitive battleground is shifting. While early success may have been driven by asset deployment, long-term market leadership will be determined by sophistication in data analytics, customer management, and portfolio optimization. Companies are already investing in systems to "prever e fazer esse balanceamento" (predict and balance) the intricate relationship between generation and consumption.3  
The proposed venture will therefore differentiate itself on the basis of demonstrably superior techno-economic optimization. While a competitive subscription offering and a seamless digital customer experience are table stakes, the core competitive advantage will stem from the rigorous application of the oemof-solph modeling framework. This will enable more precise customer pricing, higher asset return on investment (ROI), more reliable savings guarantees, and a more efficient allocation of capital and energy credits across the entire portfolio. This analytical rigor will position the venture as the most technologically advanced and financially sound partner for consumers and investors alike.

## **Section 2: The Regulatory Framework as a Business Enabler**

### **2.1 Dissection of Law 14.300 and the System of Compensation for Electrical Energy (SCEE)**

The viability of any SaaS business in Brazil is inextricably linked to the country's forward-thinking regulatory framework for Distributed Generation (GD). This framework allows consumers to transition from passive bill-payers to active participants in the energy system, generating their own power and receiving tangible financial benefits for contributing to the grid.4  
The cornerstone of this framework is Law 14.300, known as the *Marco Legal da Geração Distribuída* (Legal Framework for Distributed Generation). Enacted in 2022, this law consolidated and codified previous regulations, providing crucial legal security and clear, long-term guidelines for the sector's development.4 It governs the installation, connection, and compensation mechanisms for small-scale power generation projects.  
Central to the entire system is the *Sistema de Compensação de Energia Elétrica* (SCEE), or System of Compensation for Electrical Energy. The SCEE is the mechanism that allows a consumer's generation system to interact with the utility grid. When a system produces more energy than is being consumed at that moment, the surplus is injected into the local distribution network. The SCEE measures this surplus and converts it into energy credits, denominated in kilowatt-hours ($kWh$). These credits can then be used to offset consumption from the grid at other times, such as at night or on cloudy days. Crucially, these credits have a validity of 60 months, allowing for the banking of energy across different seasons.4 The SCEE effectively allows the grid to function as a virtual battery for the consumer, a feature that is fundamental to the economic viability of asset-light SaaS models that do not require physical, on-site energy storage.  
Within this framework, projects are categorized by size. **Microgeração** (Microgeneration) refers to systems with an installed capacity up to 75 $kW$, while **Minigeração** (Minigeneration) includes systems with a capacity above 75 $kW$ and up to 3 $MW$ for solar (or 5 $MW$ for other sources).4 These definitions are important as they determine the technical and procedural requirements for connecting a project to the grid.

### **2.2 Operational Mechanics of Key Distributed Generation Modalities**

Law 14.300 and the underlying ANEEL regulations define several distinct modalities for participating in the SCEE. Understanding the specific rules of each modality is essential, as they directly enable different business models and target different customer segments.

#### **2.2.1 Autoconsumo Remoto (Remote Self-Consumption)**

* **Definition:** This modality allows a single legal entity (identified by a single CPF for an individual or a single CNPJ for a business, including its branches) to generate electricity in one location and use the energy credits to offset consumption at one or more different locations.12 The critical constraint is that all properties—both the generation site and the consumption sites—must be located within the service area of the same electricity distribution company.15  
* **Target Clientele:** Autoconsumo Remoto is perfectly designed for B2B applications. It is the ideal solution for businesses with multiple sites, such as national retail chains, banking networks, pharmacy franchises, telecommunications companies with numerous towers and offices, and industrial groups with separate production facilities and administrative headquarters.13 It allows them to consolidate their energy procurement by building a single, optimally located solar farm to serve their entire portfolio of properties within a given region.

#### **2.2.2 Geração Compartilhada (Shared Generation)**

* **Definition:** Geração Compartilhada is a collective model that enables multiple, unrelated consumers—be they individuals or companies—to benefit from a single, shared micro or minigeneration facility.17 To participate, consumers must formally unite through a specific legal structure, such as a consortium, a cooperative, a civil association, or a voluntary civil condominium.11 As with other modalities, all participants and the generation plant must be within the same distributor's concession area.21  
* **Operational Model:** In practice, this modality is the foundation of the "community solar" or "solar subscription" model. A SaaS provider develops a solar farm and establishes a legal entity (e.g., a consortium) that customers can join. The energy produced by the farm is converted into credits, which are then allocated to the subscribers based on the size of their subscription or share. These credits appear directly on their individual utility bills, providing a discount without any on-site installation.8  
* **Target Clientele:** This is the key to democratizing access to solar energy. It is designed for the vast market of consumers who cannot host their own systems, including residential renters, apartment dwellers, and small businesses operating from leased premises.13 It removes the barriers of property ownership, available space, and upfront capital.

#### **2.2.3 Empreendimento com Múltiplas Unidades Consumidoras (EMUC) / Geração em Condomínio**

* **Definition:** The EMUC modality, also known as condominium generation, is a specialized framework for properties that contain multiple independent consumer units, such as residential or commercial condominiums.22 A single generation system is installed within the common areas of the property (e.g., on rooftops or in parking lots).23  
* **Operational Model:** The energy generated can be used to power the condominium's common areas (e.g., elevators, hallway lighting, pools), directly reducing the shared condo fees. Alternatively, any surplus energy can be distributed as credits to the individual residential or commercial units within the condominium, offsetting their private electricity bills.23  
* **Target Clientele:** This is a niche but high-value market. The primary targets are real estate developers of new projects, who can incorporate solar as a key selling feature, and the administrative bodies of existing condominiums (homeowner associations) seeking to reduce operational costs and enhance property value.

The distinct nature of these modalities necessitates a multi-pronged business strategy. A single, monolithic offering would fail to capture the full potential of the market. The following table provides a strategic comparison to guide the development of a tailored product portfolio.

| Modality | ANEEL Definition | Key Requirement (Ownership/Legal Structure) | Geographic Constraint | Target Consumer Segment | Corresponding SaaS Business Model |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Autoconsumo Remoto** | Generation and consumption at different sites under the same legal ownership. | All units must have the same CPF or CNPJ (including branches). | All units must be within the same distributor's concession area. | Multi-site corporations (retail chains, banks, industry). | Corporate Remote Solar (CRS) |
| **Geração Compartilhada** | Multiple consumers united to share the benefits of a single generation plant. | Consumers must join a consortium, cooperative, or association. | All participants must be within the same distributor's concession area. | Residential (especially renters/apartments), Small & Medium Enterprises (SMEs). | Community Solar Subscription (CSS) |
| **EMUC** | Generation within a condominium to serve common areas and/or individual units. | The system is installed in a common area of a multi-unit property. | The entire property is located within a single distributor's area. | Residential & commercial condominiums, real estate developers. | Condominium Energy Solutions (CES) |
| **Autoconsumo Local** | Generation and consumption occur at the same physical address. | Single consumer unit. | N/A | Homeowners, single-site businesses with available space. | (Baseline for traditional solar installation) |

## **Section 3: Characterization of Target Consumer Segments and Energy Profiles**

A successful SaaS strategy requires a deep understanding of the distinct energy consumption patterns of each target market segment. This allows for the precise tailoring of products, pricing, and value propositions. In Brazil, consumers are broadly categorized by ANEEL into groups, with the primary targets for SaaS falling under Group B (low-voltage supply).

### **3.1 The Residential Segment (ANEEL Class B1)**

* **Consumption Magnitude:** The residential sector is a cornerstone of the national energy market, accounting for approximately 27% of total electricity consumption, second only to the industrial sector.25 The segment exhibits a consistent and growing demand for electricity, driven by increasing appliance penetration and quality of life improvements.26  
* **Consumption Profile:** A typical residential load curve is characterized by two distinct peaks: a smaller one in the morning as households prepare for the day, and a much larger, more sustained peak in the evening (roughly 6 PM to 10 PM) when residents return home, turn on lights, prepare meals, and use entertainment devices. The midday period is typically a trough in consumption. Key drivers of residential consumption include refrigeration, which constitutes a significant and relatively constant baseload, and air conditioning, which can dramatically increase consumption during periods of high heat.25 There are also significant regional variations in consumption, with households in the warmer northern states of Brazil generally exhibiting higher average monthly consumption than those in other regions.27  
* **Tariff Interaction:** This segment is highly sensitive to retail tariff fluctuations. The availability of the "Tarifa Branca" (White Tariff), a Time-of-Use (ToU) rate structure, is a critical factor.28 This tariff establishes higher prices during peak ("ponta") and intermediate ("intermediário") hours, which often coincide with the evening residential consumption peak. This creates a powerful financial incentive for residential customers to adopt solutions like solar SaaS, which generates energy credits during the low-cost "fora de ponta" (off-peak) daytime hours that can then be used to offset consumption during the expensive evening peak.

### **3.2 The Commercial Segment (ANEEL Class B3)**

* **Consumption Magnitude:** The commercial sector is a dynamic and rapidly growing component of Brazil's energy demand, with a projected annual growth rate of 6%.26 In 2024, the sector's total consumption reached 104.1 TWh.29  
* **Consumption Profile:** The typical consumption profile for commercial establishments is diurnal, meaning it is heavily concentrated during standard business hours (e.g., 9 AM to 6 PM). This load shape has an exceptionally high correlation with the generation profile of a solar PV system, making the commercial segment an ideal and highly profitable target for SaaS offerings. High-potential sub-sectors include services (offices, hotels), retail (supermarkets, shopping centers), and food service (restaurants), where the primary energy loads are from lighting, HVAC systems, and commercial refrigeration.30  
* **Self-Generation Adoption:** Market penetration of self-generation in this segment remains remarkably low. Currently, only 7% of commercial establishments generate any of their own power. However, of this small group of early adopters, an overwhelming 81.8% have chosen solar PV as their technology of choice.30 This data reveals two crucial points: a high degree of acceptance and trust in solar technology, and a massive, untapped market of the remaining 93% of businesses that represents a prime opportunity for growth.

### **3.3 The Industrial Segment (ANEEL Class B3)**

* **Consumption Magnitude:** The industrial sector is the largest single consumer of energy in Brazil, accounting for roughly 32% of the country's total final energy consumption (including all fuels).33 In terms of electricity alone, its consumption is immense, totaling 15,498 GWh in January 2024\.35  
* **Consumption Profile:** Industrial load profiles are highly heterogeneous and depend entirely on the specific sub-sector and production process. Some electro-intensive industries, such as Metallurgy (which alone accounts for 26.5% of industrial electricity consumption) and Chemicals (10.3%), often operate 24/7, resulting in a high, flat, and constant baseload.35 Other sectors, like Automotive manufacturing, Textiles, or Food and Beverage processing, may have more variable loads tied to specific production shifts, which could be single, double, or triple shifts.  
* **Targeting Strategy:** The SaaS model is most compelling for industrial clients whose operations include significant daytime electricity consumption that can be directly offset by solar generation. While solar alone cannot cover a 24/7 baseload, it can substantially reduce energy costs for a large portion of the day, particularly for single or double-shift operations. The Autoconsumo Remoto modality is especially well-suited to this segment, allowing a company to build a large, efficient solar farm in a rural area to power its urban manufacturing plant.

A critical challenge in serving these markets effectively is the general lack of publicly available, granular, hourly load curve data for specific consumer sub-classes in Brazil.30 While aggregate monthly consumption data is published by entities like the Empresa de Pesquisa Energética (EPE) 36, the typical hourly profiles needed for precise techno-economic modeling are not readily accessible. This information gap, however, should not be viewed as a barrier but as a key strategic opportunity. The profitability of a SaaS business model hinges on the ability to accurately predict a customer's consumption profile to correctly size their subscription and reliably guarantee savings. An inaccurate prediction leads to either oversizing the subscription, resulting in customer dissatisfaction and churn, or undersizing it, leaving potential revenue unrealized.  
Therefore, the ability to develop a sophisticated internal modeling capability becomes a powerful competitive moat. By using initial customer data (e.g., business type, square footage, major electrical equipment) to generate accurate, synthetic load profiles and then refining these profiles with real-time monitoring data post-acquisition, a company can build a core intellectual property. This is where a flexible framework like oemof-solph becomes indispensable. It allows for the modeling of customer savings under a range of simulated load profiles, enabling robust sensitivity analysis that informs contract design, risk assessment, and pricing strategy. This capability allows for the creation of more competitive, reliable, and profitable contracts than those offered by competitors who rely on simplistic, spreadsheet-based calculations.

## **Section 4: A Multi-Modal SaaS Business Model Architecture**

To effectively address the diverse consumer segments and leverage the distinct regulatory modalities available in Brazil, a multi-modal business architecture is proposed. This approach avoids a one-size-fits-all strategy, instead offering a portfolio of tailored services, each designed to achieve optimal product-market fit.

### **4.1 Offering 1: Corporate Remote Solar (CRS)**

* **Description:** CRS is a premier B2B service designed for multi-site commercial and industrial clients. Under this model, the company will finance, develop, own, and operate utility-scale solar farms (classified as Minigeração). The energy credits generated by these assets will be sold to a corporate client through a long-term subscription or power purchase agreement. The credits will be applied across the client's portfolio of facilities, simplifying their energy management into a single, predictable monthly payment.  
* **Regulatory Modality:** This offering is built exclusively on the Autoconsumo Remoto (Remote Self-Consumption) modality.14  
* **Value Proposition:** The primary value propositions for the client are the complete elimination of upfront capital expenditure (CAPEX), guaranteed and immediate savings on their consolidated electricity bill, long-term budget certainty that hedges against utility tariff volatility, and a powerful tool for achieving corporate sustainability and ESG (Environmental, Social, and Governance) targets.  
* **Target Market:** The ideal customers for CRS are national retail chains, banking networks with numerous branches, telecommunications companies, fast-food franchises, and industrial groups that meet the essential regulatory criteria of operating multiple sites under a single CNPJ within the same distributor's concession area.

### **4.2 Offering 2: Community Solar Subscription (CSS)**

* **Description:** CSS is a mass-market offering targeting residential consumers and Small and Medium Enterprises (SMEs). This model allows customers to subscribe to a "share" of a locally-sited solar farm. They receive monthly credits on their existing utility bill proportional to their subscription size, which are guaranteed to provide a discount relative to the standard utility tariff. The entire process, from sign-up to billing, is managed through a simple, user-friendly digital platform.  
* **Regulatory Modality:** This service leverages the Geração Compartilhada (Shared Generation) modality. The company will establish and manage the required legal structure, most likely a consortium or a special-purpose cooperative, which customers will join to receive their energy credits.11  
* **Value Proposition:** The core value is democratized access to the financial benefits of solar energy. Customers can start saving with zero upfront cost, no installation on their property, and no long-term commitment tied to their physical address, making it perfect for renters and apartment dwellers.3 The offering is designed for simplicity: sign up online and see the savings on the next utility bill.  
* **Target Market:** The primary target is the vast residential market (ANEEL Class B1) and small commercial establishments (Class B3) located within the concession area of a single electricity distributor where a solar farm is sited.

### **4.3 Offering 3: Condominium Energy Solutions (CES)**

* **Description:** CES is a specialized, turnkey energy solution for new and existing multi-unit properties. The company will manage the entire project lifecycle: initial energy audits, system design, financing, installation, and long-term operation and maintenance of a solar PV system located on the condominium's common property, such as rooftops, carports, or available land.  
* **Regulatory Modality:** This offering is specifically designed to operate under the Empreendimento com Múltiplas Unidades Consumidoras (EMUC) framework.22  
* **Value Proposition:** The benefits are multi-faceted. It directly reduces the condominium's common area electricity costs, which are a major component of monthly fees. It can provide energy credits to individual residents, lowering their personal utility bills. Furthermore, it significantly increases the property's market value and serves as a tangible green amenity for environmentally conscious residents.  
* **Target Market:** The primary sales channels for this service are real estate developers for new constructions and property management companies or homeowner associations (HOAs) for existing condominiums.

This portfolio of services is strategically designed to ensure that each product is precisely aligned with a specific regulatory pathway and a defined market segment. The following table provides a clear visual map of this integrated business strategy.

| Service Offering | Target Consumer(s) | ANEEL Regulatory Modality | Core Value Proposition | Key Sales Channel |
| :---- | :---- | :---- | :---- | :---- |
| **Corporate Remote Solar (CRS)** | Large multi-site commercial & industrial corporations | Autoconsumo Remoto | Zero CAPEX, consolidated savings, budget certainty, ESG goals | Direct B2B sales force, corporate partnerships |
| **Community Solar Subscription (CSS)** | Residential consumers (especially renters), SMEs | Geração Compartilhada | No installation, no upfront cost, immediate savings, flexibility | Digital marketing, online sign-up platform, community partnerships |
| **Condominium Energy Solutions (CES)** | Real estate developers, property managers, HOAs | EMUC | Reduced condo fees, increased property value, green amenity | Partnerships with developers & property management firms |

## **Section 5: Strategic Optimization Using oemof-solph**

### **5.1 The Central Role of oemof-solph as the Analytical Engine**

The strategic linchpin of the proposed business model is the integration of oemof-solph as the core analytical engine. oemof-solph is a powerful, open-source, and highly flexible framework for modeling and optimizing multi-node energy systems. Its key advantage lies in its modular structure, which allows for the creation of custom components and the definition of complex constraints and objective functions. This adaptability makes it perfectly suited for accurately representing the unique rules of Brazil's Distributed Generation framework and the specific economic drivers of the SaaS market.  
This tool will not be used as a one-off engineering utility for initial design. Instead, it will be embedded as a continuous, dynamic engine powering four critical, interconnected business processes: strategic asset planning, customer sales and pricing, operational portfolio management, and long-term technology strategy. This systematic application of advanced optimization will be the primary source of the company's competitive advantage.

### **5.2 Application 1: Optimal Asset Sizing and Siting (Strategic Planning)**

* **Model Setup:** A techno-economic model of potential generation assets will be constructed. In oemof-solph, solar PV plants will be represented as Source components with the nonconvex=True attribute to enable investment decisions (i.e., whether to build a plant and at what capacity). These sources will be connected to a Bus representing the electrical grid. The model will be parameterized with location-specific inputs, including Typical Meteorological Year (TMY) solar irradiance data, land acquisition or lease costs, grid connection fees, and regional construction costs.  
* Objective Function: The model will be solved to maximize the Net Present Value (NPV) of the entire generation asset portfolio over a 25-year operational lifetime. An alternative objective could be to minimize the Levelized Cost of Energy (LCOE) for each potential project. The optimization problem can be formulated as:

  $$\\max(\\text{NPV}) \= \\sum\_{t=0}^{T} \\frac{\\text{Revenues}\_t \- \\text{Costs}\_t}{(1+r)^t} \- \\text{CAPEX}$$

  where t is the time period, T is the project lifetime, and r is the discount rate.  
* **Business Value:** This application forms the foundation of the company's capital allocation strategy. It moves beyond simple financial projections to identify the most profitable locations to build solar farms and determine the optimal installed capacity ($MWp$) for each site, considering all technical and economic constraints. This ensures that every dollar of investment capital is deployed for maximum financial return.

### **5.3 Application 2: Customer-Centric Contract Design (Sales & Pricing)**

* **Model Setup:** A detailed model of a potential customer's energy system will be created. The customer's electricity demand will be represented by a Sink component with a time-series load profile. Their connection to the grid will be modeled as both a Source (for buying electricity) and a Sink (for exporting surplus). The complex structure of Brazil's "Tarifa Branca" 28 will be implemented as time-varying, non-uniform costs for grid electricity, with high prices in the "ponta" and "intermediário" periods. The SaaS offering will be modeled as an external inflow of energy credits at a fixed subscription price.  
* **Objective Function:** For a given customer load profile, the model will solve for the optimal subscription size (e.g., the $kW$-equivalent share of a solar farm) that minimizes the customer's total annual electricity bill, which is the sum of their residual grid energy costs and their SaaS subscription fee.  
* **Business Value:** This application is a powerful sales and risk management tool. It allows the sales team to generate instant, data-driven, and optimized proposals for prospective customers, clearly demonstrating the maximum possible savings they can achieve. This provides a significant competitive advantage over competitors who may use simplistic or rule-of-thumb calculations, enabling the company to offer more aggressive yet financially sound savings guarantees.

### **5.4 Application 3: Portfolio-Level Energy Credit Management (Operations)**

* **Model Setup:** This represents the most sophisticated application of oemof-solph and will function as the operational brain of the company. It will be a multi-node model where each company-owned solar farm is a Source node and each subscribed customer is a Sink node. The model will be governed by a complex set of constraints that precisely mirror the rules of the SCEE, including the 60-month validity period for energy credits 4 and the specific allocation rules for Geração Compartilhada and Autoconsumo Remoto.  
* **Objective Function:** The model's objective will be to maximize the total revenue (or net margin) of the entire asset and customer portfolio on a monthly basis. It will achieve this by determining the optimal allocation of every generated $MWh$ of energy credits from all solar farms to all customers, ensuring that all contractual savings guarantees are met while minimizing expired or sub-optimally used credits.  
* **Business Value:** This operational optimization engine ensures that every unit of energy generated is utilized to its maximum financial potential. It prevents the loss of value from expiring credits and intelligently routes credits to customers where they can offset the highest-cost grid electricity, thereby maximizing system-wide profitability across a large, diverse, and growing customer base.

### **5.5 Application 4: Techno-Economic Assessment of Hybrid Systems (Future Strategy)**

* **Model Setup:** The existing asset and customer models will be augmented with a Storage component to represent a Battery Energy Storage System (BESS). This component will have parameters for charging/discharging efficiency, capacity, power, and degradation.  
* **Objective Function:** The model will be used to evaluate the economic case for co-locating BESS with the company's solar farms. The objective will be to determine if the additional revenue generated by the battery outweighs its capital and operational costs. The model will assess multiple value streams, such as energy arbitrage (storing low-cost solar energy generated midday and discharging it to generate more valuable credits during the high-cost "ponta" tariff period) and the potential for providing ancillary services to the grid.  
* **Business Value:** This application provides a rigorous, data-driven roadmap for future technology investments. It allows the company to stay ahead of the market by precisely identifying the economic tipping point at which BESS becomes a profitable and value-accretive addition to its service offerings, ensuring that future capital is deployed intelligently.

The following matrix summarizes how these oemof-solph applications translate directly into business value across the organization.

| Business Function | Key Business Question | oemof-solph Application | Model Objective | Key Outputs & Business Value |
| :---- | :---- | :---- | :---- | :---- |
| **Strategic Planning** | Where should we build our solar farms and how large should they be? | Asset Sizing & Siting | Maximize Portfolio NPV / Minimize LCOE | Optimal geographic locations and MW capacity for new assets. Maximizes ROI on capital investments. |
| **Sales & Marketing** | What is the optimal subscription size and price for a new customer? | Customer Contract Design | Minimize Customer's Annual Electricity Bill | Tailored subscription size and guaranteed savings report. Increases sales conversion and customer satisfaction. |
| **Operations** | How do we allocate our generated energy credits across all customers each month? | Portfolio Credit Management | Maximize Total Portfolio Revenue/Margin | Monthly credit allocation plan for the entire customer base. Maximizes profitability and prevents value loss. |
| **R\&D / Future Strategy** | When and where should we start deploying batteries with our solar farms? | Hybrid System Assessment | Maximize NPV of a Solar+Storage Project | Financial viability analysis (IRR, Payback) for BESS. Provides a data-driven technology roadmap. |

## **Section 6: Financial Projections and Risk Analysis**

### **6.1 Unit Economics and Financial Modeling**

A detailed financial model will be developed for a representative project under each of the three service offerings (CRS, CSS, CES) to establish their standalone economic viability.

* **Inputs:** The models will be populated with conservative, market-validated assumptions.  
  * **Capital Expenditures (CAPEX):** Per-watt costs for Tier-1 PV modules, inverters, mounting structures, and balance-of-system components, along with costs for installation, grid connection, and project development.  
  * **Operational Expenditures (OPEX):** Annual costs for operations and maintenance (O\&M), insurance, land lease payments, asset management, and administrative overhead.  
  * **Revenue:** Projections based on the subscription price per kWh offered to customers, designed to be at a competitive discount to the relevant utility tariff.  
  * **Customer Acquisition Cost (CAC):** Modeled per customer for the CSS offering and as a percentage of contract value for the CRS and CES offerings.  
* **Key Metrics:** The financial performance of each project type will be evaluated using standard investment metrics:  
  * **Levelized Cost of Energy (LCOE):** The break-even price of energy generation over the project's lifetime.  
  * **Project Internal Rate of Return (IRR):** The discount rate at which the project's NPV becomes zero.  
  * **Equity IRR:** The return specifically to equity investors after accounting for debt financing.  
  * **Payback Period:** The time required for the project's cash flows to recoup the initial investment.  
  * **Net Present Value (NPV):** The total discounted value of all future cash flows.

### **6.2 Key Assumptions and Sensitivity Analysis**

The robustness of the financial projections depends on the validity of the underlying assumptions. All key assumptions will be explicitly stated and justified, including the projected annual escalation rate of utility electricity prices, the annual degradation rate of PV panel performance, expected customer churn rates, and the cost of debt and equity capital.  
A critical component of the financial analysis will be a comprehensive sensitivity analysis. The outputs from the oemof-solph models will be used to quantify the impact of changes in key variables on project profitability. This will include assessing the financial impact of:

* Lower-than-expected solar irradiance in a given year.  
* Adverse changes to the structure of utility tariffs (e.g., a reduction in the price differential between peak and off-peak periods).  
* Potential future changes to the regulatory framework for the SCEE.  
* Variations in construction costs or interest rates.

This analysis will identify the most critical drivers of financial performance and inform the development of robust risk mitigation strategies.

### **6.3 Risk Matrix**

A structured approach to identifying, assessing, and mitigating risks is essential for long-term success.

* **Regulatory Risk:**  
  * **Risk:** Potential for future adverse changes to Law 14.300 or the rules of the SCEE that could reduce the value of energy credits.  
  * **Mitigation:** Proactive engagement with industry associations and policymakers to advocate for stable, long-term regulations. Structuring long-term customer contracts with clauses that allow for adjustments in the event of significant regulatory shifts.  
* **Market Risk:**  
  * **Risk:** Increased competition driving down subscription prices and compressing margins. A significant drop in conventional utility tariffs could also erode the service's value proposition.  
  * **Mitigation:** Securing customers on long-term fixed-price contracts to lock in revenue streams. Building a strong brand based on superior customer service and reliability. Continuously driving down operational costs through the efficiency gains identified by the oemof-solph portfolio management engine.  
* **Operational Risk:**  
  * **Risk:** Underperformance of solar assets due to equipment failure, faster-than-expected degradation, or soiling. Potential for grid curtailment in areas with high solar penetration.  
  * **Mitigation:** Sourcing equipment exclusively from Tier-1 manufacturers with strong warranties. Implementing a proactive O\&M strategy, potentially incorporating AI-powered predictive maintenance similar to that used by competitors.5 Diversifying the geographic footprint of assets to mitigate localized grid issues.  
* **Financial Risk:**  
  * **Risk:** Fluctuations in interest rates increasing the cost of capital for new projects. Difficulty in securing sufficient project financing to support growth targets.  
  * **Mitigation:** Developing relationships with a diversified pool of capital providers, including commercial banks, development banks, and infrastructure funds. Employing interest rate hedging strategies where appropriate. Building a strong track record of operational excellence to improve creditworthiness.

## **Section 7: Strategic Recommendations and Implementation Roadmap**

### **7.1 Phased Market Entry Strategy**

A disciplined, phased approach to market entry is recommended to manage risk, optimize capital deployment, and build a scalable operational foundation.

* **Phase 1 (Years 1-2): Initial Market Penetration & B2B Focus:**  
  * The initial focus will be on the Autoconsumo Remoto (CRS) market within a single, high-potential state, such as São Paulo or Minas Gerais, which have large commercial and industrial bases and favorable regulatory environments.  
  * This B2B-first strategy allows the company to secure larger, long-term contracts with creditworthy counterparties, generating a stable initial revenue base and establishing a strong operational track record with a more concentrated geographic footprint.  
* **Phase 2 (Years 2-4): Mass-Market Launch & Geographic Expansion:**  
  * Leveraging the operational infrastructure and brand recognition established in Phase 1, the company will launch its Geração Compartilhada (CSS) offering in the initial target state. This will open up the vast residential and SME markets.  
  * Concurrently, the successful CRS model will be expanded into adjacent states, following the expansion playbook of competitors like Lemon Energia.3 This phase focuses on scaling both the B2B and B2C/SME business lines.  
* **Phase 3 (Year 5+): National Scale & Technology Leadership:**  
  * The goal in this phase is to achieve a national footprint with both the CRS and CSS offerings, establishing the company as a leading player in the Brazilian SaaS market.  
  * Pilot projects for the niche EMUC (CES) model will be initiated in major metropolitan areas.  
  * Based on the continuous analysis from the oemof-solph engine, the company will begin the strategic integration of Battery Energy Storage Systems (BESS) into its new projects where economically viable, solidifying its position as a technology leader.

### **7.2 Technology Stack and Operational Plan**

* **Core Analytical Engine:** oemof-solph will be the central pillar of the technology stack, used for all techno-economic modeling and optimization as detailed in Section 5\.  
* **Customer Platform:** A proprietary or licensed customer-facing digital platform will be developed. This will include a public website for marketing and lead generation, and a secure customer portal and mobile application for online sign-ups, automated billing, and real-time performance monitoring. This mirrors the tech-forward, customer-centric approach of leading competitors.5  
* **Operational Structure:** A lean internal team of experts will be assembled to manage project development, finance, data science, and customer relations. The capital-intensive and specialized functions of construction (EPC) and field-level operations and maintenance (O\&M) will be outsourced to a network of vetted, high-quality local partners in each region of operation.

### **7.3 Long-Term Vision and Scalability**

The long-term vision is to transcend the role of a simple energy provider and become Brazil's leading energy-technology platform. The company will use its core competencies in data science and optimization to provide the cheapest, cleanest, and most reliable power to all consumer segments, from individual households to the largest industrial corporations.  
Scalability is inherent in the platform-based business model. Growth will be achieved through:

* **Standardization:** Developing standardized legal contracts and operational processes to streamline customer onboarding and asset management.  
* **Automation:** Automating key processes such as customer billing, credit allocation, and performance reporting to maintain a low operational cost base.  
* **Optimization Engine:** Using the oemof-solph portfolio management tool to efficiently manage an increasingly large and complex portfolio of generation assets and diverse customers without a linear increase in administrative overhead.  
* **Channel Partnerships:** Exploring indirect sales channels, such as the franchise model successfully employed by Solar21, to accelerate geographic expansion and customer acquisition.5

By executing this strategy, the venture is positioned not only to capture a significant share of the burgeoning Brazilian Solar as a Service market but also to define the next generation of technology-driven, customer-centric energy providers.

#### **Referências citadas**

1. Uso Sustentável da Infraestrutura de Energia nas Cidades e Transição Energética, acessado em outubro 18, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-519/topico-626/Euroclima\_ResumoExecutivo2024\_v04%20(2).pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-519/topico-626/Euroclima_ResumoExecutivo2024_v04%20\(2\).pdf)  
2. Guia completo sobre autoconsumo remoto \- HCC Energia Solar, acessado em outubro 18, 2025, [https://hccenergiasolar.com.br/guia-autoconsumo-remoto/](https://hccenergiasolar.com.br/guia-autoconsumo-remoto/)  
3. Essa empresa quer surfar “momento fintech” no setor de energia \- StartSe, acessado em outubro 18, 2025, [https://www.startse.com/artigos/lemon-capta-rdollar-60-mi-para-surfar-momento-fintech-no-setor-de-energia/](https://www.startse.com/artigos/lemon-capta-rdollar-60-mi-para-surfar-momento-fintech-no-setor-de-energia/)  
4. O que é geração distribuída e como ela funciona no Brasil \- Descarbonize Soluções, acessado em outubro 18, 2025, [https://descarbonizesolucoes.com.br/blog/geracao-distribuida-de-energia](https://descarbonizesolucoes.com.br/blog/geracao-distribuida-de-energia)  
5. Solar21 aposta em tecnologia e Inteligência Artificial para franqueados \- pv magazine Brasil, acessado em outubro 18, 2025, [https://www.pv-magazine-brasil.com/2024/11/19/solar21-aposta-em-tecnologia-e-inteligencia-artificial-para-franqueados/](https://www.pv-magazine-brasil.com/2024/11/19/solar21-aposta-em-tecnologia-e-inteligencia-artificial-para-franqueados/)  
6. Energy as a Service: conheça o modelo de negócio\! \- GreenYellow, acessado em outubro 18, 2025, [https://greenyellow.com.br/energy-as-a-service-2/](https://greenyellow.com.br/energy-as-a-service-2/)  
7. Cinco gigantes do mercado solar brasileiro em 2025 \- Ei Energia, acessado em outubro 18, 2025, [https://eienergia.com.br/cinco-gigantes-do-mercado-solar-brasileiro-em-2025/](https://eienergia.com.br/cinco-gigantes-do-mercado-solar-brasileiro-em-2025/)  
8. O que é energia solar compartilhada? Entenda como funciona\!, acessado em outubro 18, 2025, [https://origoenergia.com.br/blog/energia/energia-solar-compartilhada/](https://origoenergia.com.br/blog/energia/energia-solar-compartilhada/)  
9. Geração Distribuída de Energia (GD): Saiba Tudo\! \- Portal Solar, acessado em outubro 18, 2025, [https://www.portalsolar.com.br/geracao-distribuida-de-energia.html](https://www.portalsolar.com.br/geracao-distribuida-de-energia.html)  
10. Geração distribuída: conheça seus benefícios e desafios \- Idec, acessado em outubro 18, 2025, [https://idec.org.br/dicas-e-direitos/geracao-distribuida](https://idec.org.br/dicas-e-direitos/geracao-distribuida)  
11. Geração compartilhada: o que é e quais as suas exigências? \- Ourolux, acessado em outubro 18, 2025, [https://ourolux.com.br/blog/post/geracao-compartilhada/](https://ourolux.com.br/blog/post/geracao-compartilhada/)  
12. Micro e Minigeração Distribuída — Agência Nacional de Energia Elétrica \- Portal Gov.br, acessado em outubro 18, 2025, [https://www.gov.br/aneel/pt-br/assuntos/geracao-distribuida](https://www.gov.br/aneel/pt-br/assuntos/geracao-distribuida)  
13. Geração distribuída: como escolher a melhor modalidade?, acessado em outubro 18, 2025, [https://canalsolar.com.br/geracao-distribuida-escolher-melhor-modalidade-para-projeto/](https://canalsolar.com.br/geracao-distribuida-escolher-melhor-modalidade-para-projeto/)  
14. L14300 \- Planalto, acessado em outubro 18, 2025, [https://www.planalto.gov.br/ccivil\_03/\_ato2019-2022/2022/lei/l14300.htm](https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2022/lei/l14300.htm)  
15. Autoconsumo Remoto: o que é, suas vantagens e como utilizar, acessado em outubro 18, 2025, [https://descarbonizesolucoes.com.br/blog/autoconsumo-remoto](https://descarbonizesolucoes.com.br/blog/autoconsumo-remoto)  
16. Micro e mini geração distribuída \- EDP, acessado em outubro 18, 2025, [https://www.edp.com.br/micro-e-mini-geracao/](https://www.edp.com.br/micro-e-mini-geracao/)  
17. Conheça as Modalidades de Geração Distribuída e Escolha a Melhor para o Seu Projeto de Energia \- Edeltec Solar, acessado em outubro 18, 2025, [https://edeltecsolar.com.br/blog/institucional/modalidades-de-gd](https://edeltecsolar.com.br/blog/institucional/modalidades-de-gd)  
18. Geração compartilhada: veja como funciona e por que investir, acessado em outubro 18, 2025, [https://www.aldo.com.br/blog/geracao-compartilhada](https://www.aldo.com.br/blog/geracao-compartilhada)  
19. Micro e Minigeração Distribuída — Agência Nacional de Energia ..., acessado em outubro 18, 2025, [https://www.gov.br/aneel/pt-br/acesso-a-informacao/perguntas-frequentes/micro-e-minigeracao-distribuida](https://www.gov.br/aneel/pt-br/acesso-a-informacao/perguntas-frequentes/micro-e-minigeracao-distribuida)  
20. Geração distribuída compartilhada facilita o acesso à energia solar, acessado em outubro 18, 2025, [https://solucoes.edp.com.br/blog/geracao-compartilhada-energia-solar/](https://solucoes.edp.com.br/blog/geracao-compartilhada-energia-solar/)  
21. Como funciona a geração compartilhada de energia e quais são seus benefícios? \- WEG, acessado em outubro 18, 2025, [https://www.weg.net/solar/blog/como-funciona-a-geracao-compartilhada-de-energia-e-quais-sao-seus-beneficios/](https://www.weg.net/solar/blog/como-funciona-a-geracao-compartilhada-de-energia-e-quais-sao-seus-beneficios/)  
22. Modalidades de Geração Distribuída: Entenda os Tipos \- Grupo Quanta, acessado em outubro 18, 2025, [https://grupoquanta.com.br/geracao-distribuida-modalidades-quanta/](https://grupoquanta.com.br/geracao-distribuida-modalidades-quanta/)  
23. Entenda as diferenças entre GD compartilhada, remota ..., acessado em outubro 18, 2025, [https://www.portalsolar.com.br/entenda-as-diferencas-entre-gd-compartilhada-remota-condominial-e-junto-a-carga](https://www.portalsolar.com.br/entenda-as-diferencas-entre-gd-compartilhada-remota-condominial-e-junto-a-carga)  
24. Geração distribuída de energia: tire suas dúvidas sobre o assunto, acessado em outubro 18, 2025, [https://hccenergiasolar.com.br/geracao-distribuida-de-energia/](https://hccenergiasolar.com.br/geracao-distribuida-de-energia/)  
25. Dados sobre o consumo de energia elétrica no Brasil: confira panorama, acessado em outubro 18, 2025, [https://www.mercadolivredeenergia.com.br/noticias/dados-sobre-o-consumo-de-energia-eletrica-no-brasil-confira-panorama/](https://www.mercadolivredeenergia.com.br/noticias/dados-sobre-o-consumo-de-energia-eletrica-no-brasil-confira-panorama/)  
26. Consumo energético \- teleco.com.br, acessado em outubro 18, 2025, [https://www.teleco.com.br/tutoriais/tutorialdatacenter1/pagina\_5.asp](https://www.teleco.com.br/tutoriais/tutorialdatacenter1/pagina_5.asp)  
27. Estimativa da evolução do uso final de energia elétrica no setor residencial do Brasil por região geográfica \- SciELO, acessado em outubro 18, 2025, [https://www.scielo.br/j/ac/a/MC5DNWHS46jH6hCKKtCzFCc/](https://www.scielo.br/j/ac/a/MC5DNWHS46jH6hCKKtCzFCc/)  
28. Tarifa Branca — Agência Nacional de Energia Elétrica \- Portal Gov.br, acessado em outubro 18, 2025, [https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-branca](https://www.gov.br/aneel/pt-br/assuntos/tarifas/tarifa-branca)  
29. Anuário Estatístico de Energia Elétrica 2025, acessado em outubro 18, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-160/topico-168/anuario-factsheet.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-160/topico-168/anuario-factsheet.pdf)  
30. Pesquisa revela hábitos de consumo de energia por comércio e ..., acessado em outubro 18, 2025, [https://enbpar.gov.br/pesquisa-revela-habitos-de-consumo-de-energia-por-comercio-e-servicos/](https://enbpar.gov.br/pesquisa-revela-habitos-de-consumo-de-energia-por-comercio-e-servicos/)  
31. Consumo de energia no Brasil cresce 4,9% em fevereiro e supera os 77 mil MW médios pela primeira vez, calcula CCEE, acessado em outubro 18, 2025, [https://www.ccee.org.br/en/web/guest/-/consumo-de-energia-no-brasil-cresce-4-9-em-fevereiro-e-supera-os-77-mil-mw-medios-pela-primeira-vez-calcula-ccee](https://www.ccee.org.br/en/web/guest/-/consumo-de-energia-no-brasil-cresce-4-9-em-fevereiro-e-supera-os-77-mil-mw-medios-pela-primeira-vez-calcula-ccee)  
32. MME e ENBPar divulgam resultados do perfil de consumo de energia elétrica na classe comercial e de serviços \- Portal Gov.br, acessado em outubro 18, 2025, [https://www.gov.br/mme/pt-br/assuntos/noticias/mme-e-enbpar-divulgam-resultados-do-perfil-de-consumo-de-energia-eletrica-na-classe-comercial-e-de-servicos](https://www.gov.br/mme/pt-br/assuntos/noticias/mme-e-enbpar-divulgam-resultados-do-perfil-de-consumo-de-energia-eletrica-na-classe-comercial-e-de-servicos)  
33. Transporte e indústria representaram 64,8% do consumo de energia do país em 2023, acessado em outubro 18, 2025, [https://www.gov.br/mme/pt-br/assuntos/noticias/transporte-e-industria-representaram-64-8-do-consumo-de-energia-do-pais-em-2023](https://www.gov.br/mme/pt-br/assuntos/noticias/transporte-e-industria-representaram-64-8-do-consumo-de-energia-do-pais-em-2023)  
34. Entenda os desafios do consumo energético nas indústrias\!, acessado em outubro 18, 2025, [https://solucoes.edp.com.br/blog/consumo-energetico-nas-industrias/](https://solucoes.edp.com.br/blog/consumo-energetico-nas-industrias/)  
35. Resenha Mensal do Mercado de Energia Elétrica \- Fevereiro 2024, acessado em outubro 18, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-153/topico-697/Resenha%20Mensal%20-%20Fevereiro%202024%20(base%20Janeiro)\_v2.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-153/topico-697/Resenha%20Mensal%20-%20Fevereiro%202024%20\(base%20Janeiro\)_v2.pdf)  
36. Consumo Mensal de Energia Elétrica por Classe (regiões e ..., acessado em outubro 18, 2025, [https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/consumo-de-energia-eletrica](https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/consumo-de-energia-eletrica)  
37. Resposta da Demanda: Conceitos, aspectos regulatórios e planejamento Energético, acessado em outubro 18, 2025, [https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-389/NT\_EPE\_DEE-NT-022\_2019-r0.pdf](https://www.epe.gov.br/sites-pt/publicacoes-dados-abertos/publicacoes/PublicacoesArquivos/publicacao-389/NT_EPE_DEE-NT-022_2019-r0.pdf)  
38. Contribuição da Abraceel à Consulta Pública 137/2022 do MME Abertura do Mercado aos Consumidores de Baixa Tensão \- Ministério de Minas e Energia, acessado em outubro 18, 2025, [https://antigo.mme.gov.br/c/document\_library/get\_file?uuid=987f4be0-c68b-0ba5-c1c9-23423db3a373\&groupId=36090](https://antigo.mme.gov.br/c/document_library/get_file?uuid=987f4be0-c68b-0ba5-c1c9-23423db3a373&groupId=36090)  
39. Tarifa Branca: como economizar na gestão energética | EDP, acessado em outubro 18, 2025, [https://solucoes.edp.com.br/blog/tarifa-branca/](https://solucoes.edp.com.br/blog/tarifa-branca/)