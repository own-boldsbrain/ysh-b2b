

# **Relatório Técnico: Arquitetura e Implementação de Visualização Geoespacial 3D com Next.js e FastAPI**

## **Parte I: Fundamentos da Visualização Geoespacial 3D para a Web**

A renderização de ambientes 3D complexos e geo-referenciados em navegadores web representa um dos desafios mais significativos na computação gráfica moderna. A demanda por "gêmeos digitais" de cidades, visualizações de dados de infraestrutura e experiências imersivas de exploração de mapas impulsionou o desenvolvimento de tecnologias capazes de lidar com conjuntos de dados de escala massiva. Esta seção estabelece os conceitos fundamentais que sustentam a arquitetura de uma aplicação de ponta, dissecando o problema central, o padrão da indústria que o resolve e o ecossistema de software selecionado para a implementação.

### **1.1 O Desafio de Dados 3D Massivos na Web**

A visualização de dados geoespaciais 3D, como modelos de cidades gerados por fotogrametria, nuvens de pontos LiDAR de alta densidade ou modelos BIM (Building Information Modeling) detalhados, apresenta um obstáculo fundamental para aplicações web. Carregar um modelo 3D monolítico que representa uma cidade inteira, por exemplo, é inviável. Tais conjuntos de dados podem facilmente atingir dezenas ou centenas de gigabytes, excedendo em ordens de magnitude a capacidade de memória RAM de um dispositivo cliente típico, a largura de banda da rede e o poder de processamento da GPU para renderização em tempo real. Uma tentativa de carregar tal ativo resultaria em tempos de carregamento proibitivos e, muito provavelmente, na falha do navegador.  
A solução para este problema reside em abandonar a abordagem monolítica em favor de uma estratégia baseada em *streaming* e **Nível de Detalhe (Level of Detail \- LOD)**. Este paradigma é análogo ao funcionamento de serviços de mapas 2D como o Google Maps, que não carrega o mapa do mundo inteiro de uma só vez, mas sim os "ladrilhos" (tiles) relevantes para a área de visualização atual do usuário.1  
No contexto 3D, este princípio é estendido. A cena tridimensional completa é subdividida em uma hierarquia de blocos, ou *tiles*. A aplicação cliente, em vez de solicitar todo o conjunto de dados, carrega dinamicamente apenas os tiles que estão dentro do campo de visão da câmera. Além disso, a lógica de LOD é aplicada: tiles que estão mais próximos do observador são carregados com um alto nível de detalhe geométrico e de textura, enquanto tiles mais distantes são renderizados com versões simplificadas e de menor resolução. Tiles que estão muito distantes ou fora do campo de visão não são carregados, economizando recursos preciosos. Esta abordagem de carregamento progressivo e seletivo é a única maneira viável de proporcionar uma experiência de exploração fluida e interativa sobre conjuntos de dados geoespaciais massivos.1

### **1.2 Anatomia do Padrão OGC 3D Tiles: O Padrão da Indústria**

Para que a estratégia de streaming e LOD funcione de forma consistente em diferentes plataformas e ferramentas, é necessário um padrão aberto e bem definido. O padrão **OGC 3D Tiles**, mantido pelo Open Geospatial Consortium (OGC), emergiu como o padrão de fato da indústria para o streaming e renderização de conteúdo geoespacial 3D massivo e heterogêneo.2 Desenvolvido originalmente pela Cesium, ele foi adotado como um padrão comunitário do OGC em 2019, garantindo interoperabilidade e evitando a dependência de fornecedores específicos.1 O padrão é projetado para lidar com diversos tipos de dados, incluindo fotogrametria, edifícios 3D, dados BIM/CAD, feições instanciadas e nuvens de pontos.3  
A estrutura de um conjunto de dados 3D Tiles é definida por dois componentes principais: um arquivo de manifesto chamado tileset.json e um conjunto de arquivos de tile contendo os dados geométricos e de aparência.

#### **O Papel Central do tileset.json**

O arquivo tileset.json é o ponto de entrada e o "mapa" de todo o conjunto de dados. É um arquivo JSON que contém metadados e, crucialmente, uma estrutura de árvore que descreve a organização espacial e a hierarquia de LOD dos tiles.1 Quando uma aplicação cliente deseja renderizar um tileset, a primeira ação que ela executa é requisitar e analisar este arquivo. O tileset.json informa ao cliente onde os tiles estão localizados, qual a sua extensão espacial e como eles se relacionam entre si em termos de detalhe.

#### **Estrutura da Árvore de Tiles**

A árvore dentro do tileset.json é composta por objetos de tile, cada um com propriedades que guiam o processo de renderização:

* **Bounding Volumes (Volumes de Delimitação):** Cada tile possui um "volume de delimitação" (como uma caixa, box, ou esfera, sphere) que define sua extensão espacial no sistema de coordenadas do mundo. O motor de renderização utiliza esses volumes para realizar testes de visibilidade eficientes. Se o volume de um tile não intercepta o frustum (o volume de visualização em forma de pirâmide) da câmera, o tile e todos os seus descendentes podem ser descartados com segurança, um processo conhecido como *frustum culling*.1  
* **Refinamento Hierárquico (refine property):** A propriedade refine em um tile pai dita como seus filhos devem ser renderizados quando o nível de detalhe precisa aumentar. Os dois modos principais são REPLACE, onde os tiles filhos, mais detalhados, substituem completamente a renderização do pai, e ADD, onde os tiles filhos são renderizados em adição ao pai. Esta propriedade é fundamental para garantir transições suaves entre os diferentes níveis de detalhe.

#### **Formatos de Tile**

Os arquivos de tile individuais, referenciados pelo tileset.json, contêm a carga útil renderizável. A especificação evoluiu, mas historicamente definiu formatos específicos para tipos de dados comuns:

* **Formatos Legado (Especificação 1.0):**  
  * **Batched 3D Model (.b3dm):** Usado para agrupar múltiplos modelos 3D (como edifícios) em um único tile. Cada modelo pode ter suas próprias texturas e metadados, mas são renderizados em uma única chamada de desenho (draw call) para otimização de desempenho.1  
  * **Point Cloud (.pnts):** Formato para nuvens de pontos, contendo posições, cores e outras informações por ponto.1  
  * **Instanced 3D Model (.i3dm):** Eficiente para renderizar um grande número de instâncias do mesmo modelo (como árvores, postes de luz) em diferentes posições, escalas e rotações.1  
* **A Transição para glTF:** A versão 1.1 da especificação 3D Tiles modernizou o padrão ao adotar o **glTF 2.0** como o formato de conteúdo primário. O glTF é um padrão aberto do Khronos Group para a transmissão eficiente de modelos e cenas 3D, frequentemente chamado de "o JPEG do 3D". Ao se basear no glTF, o 3D Tiles se alinha com o ecossistema mais amplo de ferramentas e motores 3D, simplificando os pipelines de criação de conteúdo e aproveitando as otimizações do formato.4

### **1.3 O Ecossistema de Renderização: Nosso Stack Tecnológico**

Para construir a aplicação cliente que irá consumir e renderizar os 3D Tiles, é necessário um conjunto de bibliotecas que trabalhem em harmonia. A arquitetura proposta utiliza um stack moderno e poderoso, centrado no ecossistema React.

* **Three.js:** Na base de tudo está o **Three.js**, uma biblioteca JavaScript que abstrai a complexidade da API WebGL de baixo nível. Ela fornece as ferramentas essenciais para criar e manipular cenas 3D, incluindo câmeras, geometrias, materiais, luzes e sombras. É a biblioteca de gráficos 3D mais popular e bem documentada para a web, servindo como o motor de renderização fundamental para o nosso projeto.7  
* **React Three Fiber (R3F):** Para integrar o Three.js de forma idiomática com o React e o Next.js, utilizamos o **React Three Fiber (R3F)**. R3F não é um wrapper ou uma versão alternativa do Three.js; é um **renderizador React** para o Three.js. Isso significa que ele permite que os desenvolvedores construam uma cena 3D de forma declarativa, usando componentes JSX, como \<mesh geometry={...} material={...} /\> em vez de código imperativo como scene.add(new THREE.Mesh(...)). Esta abordagem se integra perfeitamente ao modelo de componentes e gerenciamento de estado do React. R3F não introduz sobrecarga de desempenho, pois os componentes simplesmente declaram objetos Three.js que são gerenciados fora do loop de reconciliação do React, e ele se mantém automaticamente atualizado com as novas versões do Three.js.7  
* **@takram/three-geospatial:** Esta é a biblioteca especializada que inspirou a consulta do usuário. Trata-se de um monorepo que contém um conjunto de pacotes modulares projetados para aprimorar a renderização geoespacial com Three.js e R3F.11 A sua natureza modular permite que se utilize apenas as partes necessárias do projeto. Os pacotes mais relevantes para esta implementação são:  
  * **@takram/three-geospatial:** O pacote principal (core) que fornece as funções fundamentais para renderizar dados GIS. Espera-se que este pacote contenha um componente TilesRenderer ou similar, responsável por consumir o tileset.json e orquestrar o carregamento e a renderização dos tiles de forma eficiente.11  
  * **@takram/three-atmosphere e @takram/three-clouds:** Estes pacotes são cruciais para alcançar a alta fidelidade visual vista no exemplo de referência. Eles fornecem implementações de efeitos atmosféricos realistas (como a dispersão da luz do sol, conhecida como Precomputed Atmospheric Scattering) e nuvens volumétricas geo-referenciadas, que transformam uma cena 3D básica em um ambiente imersivo e crível.11

A combinação dessas tecnologias forma um stack coeso e poderoso. O Three.js lida com a renderização de baixo nível, o R3F fornece uma ponte declarativa e eficiente para o mundo React, e o @takram/three-geospatial oferece as abstrações de alto nível necessárias para lidar com a complexidade específica dos dados 3D Tiles e dos efeitos visuais avançados.

| Camada | Tecnologia Principal | Papel no Projeto | Fontes Relevantes |
| :---- | :---- | :---- | :---- |
| Frontend (Framework) | Next.js | Fornece a estrutura da aplicação web, renderização no lado do servidor (SSR) e roteamento. | 14 |
| Frontend (Renderização 3D) | React Three Fiber (R3F) | Permite a criação declarativa de cenas 3D dentro do ecossistema React. | 7 |
| Frontend (Lógica Geoespacial) | @takram/three-geospatial | Orquestra o carregamento e renderização de 3D Tiles e efeitos visuais avançados. | 11 |
| Backend (Framework API) | FastAPI | Expõe endpoints HTTP para servir os dados dos 3D Tiles de forma rápida e eficiente. | 16 |
| Backend (Processamento de Dados) | py3dtiles / py3dtilers | Converte dados geoespaciais brutos (e.g., nuvens de pontos, modelos 3D) para o formato OGC 3D Tiles. | 18 |
| Padrão de Dados | OGC 3D Tiles | Define o formato para streaming eficiente de dados 3D massivos, servindo como o "contrato" entre backend e frontend. | 2 |

## **Parte II: Implementação do Backend: Servindo 3D Tiles com FastAPI**

O backend tem uma responsabilidade crucial, porém direta: disponibilizar os dados do tileset 3D para o cliente de forma eficiente e confiável. A escolha do FastAPI, um framework web Python moderno de alta performance, é ideal para esta tarefa devido à sua velocidade e simplicidade.16 Esta seção detalha a arquitetura do serviço, o processo de preparação dos dados e a implementação da API.

### **2.1 Arquitetura do Serviço de Tiles**

A abordagem mais robusta e performática para servir 3D Tiles não envolve a geração dinâmica de tiles a cada requisição. A conversão de dados geoespaciais brutos para o formato 3D Tiles é uma operação computacionalmente intensiva, inadequada para ser executada em tempo real em um servidor web. Em vez disso, a arquitetura adotada separa o processamento de dados do serviço da API. Os dados são pré-processados uma única vez em um conjunto de arquivos estáticos, e o FastAPI atua como um servidor de arquivos altamente otimizado para entregar esses ativos pré-gerados.  
A estrutura de diretórios para o projeto FastAPI reflete essa separação de responsabilidades:

/backend

|-- /app  
| |-- \_\_init\_\_.py  
| |-- main.py           \# Lógica principal da API, endpoints e configuração  
|-- /static\_tiles         \# Diretório raiz para armazenar os tilesets gerados  
| |-- /my\_dataset       \# Exemplo de um tileset  
| | |-- tileset.json  
| | |-- 0  
| | | |-- 0  
| | | | |-- 0.pnts  
| | |--... (outros arquivos de tile)  
|-- requirements.txt      \# Dependências do projeto Python

As dependências essenciais para este backend são:

* fastapi: O próprio framework web.21  
* uvicorn\[standard\]: O servidor ASGI (Asynchronous Server Gateway Interface) que irá executar a aplicação FastAPI.17  
* py3dtiles: A biblioteca Python que será usada na etapa de pré-processamento para converter os dados brutos para o formato 3D Tiles.18

### **2.2 Pré-processamento de Dados Geoespaciais com py3dtiles**

Antes que a API possa servir qualquer dado, os dados geoespaciais brutos (como arquivos .las, .laz, .xyz para nuvens de pontos, ou formatos geométricos como .obj ou CityGML) devem ser convertidos para a estrutura de 3D Tiles.18 A biblioteca py3dtiles fornece uma poderosa ferramenta de linha de comando (CLI) para realizar essa tarefa.

#### **Guia Prático de Conversão**

1. **Obtenção de Dados Brutos:** O primeiro passo é ter um conjunto de dados para converter. Existem muitas fontes de dados abertos, como portais governamentais que disponibilizam dados LiDAR de regiões ou projetos como o OpenStreetMap que podem ser usados para gerar modelos de edifícios.  
2. **Instalação do py3dtiles:** A biblioteca pode ser instalada via pip, conforme especificado no requirements.txt: pip install py3dtiles.  
3. **Execução da Conversão:** O comando convert da CLI do py3dtiles é usado para iniciar o processo. Por exemplo, para converter um arquivo de nuvem de pontos chamado pointcloud.las e salvar o resultado no diretório static\_tiles/my\_dataset, o comando seria:  
   Bash  
   py3dtiles convert path/to/your/pointcloud.las \--out backend/static\_tiles/my\_dataset

   Este comando analisará o arquivo de entrada, o dividirá em uma estrutura de árvore otimizada com diferentes níveis de detalhe e gerará o tileset.json correspondente, juntamente com os arquivos de tile binários (neste caso, .pnts) dentro do diretório de saída especificado.18 É fundamental garantir que o Sistema de Referência de Coordenadas (CRS) dos dados de entrada seja conhecido para que a visualização seja georreferenciada corretamente.

### **2.3 Desenvolvimento da API de Tiles com FastAPI**

Com os arquivos do tileset já gerados e organizados, a implementação da API com FastAPI é notavelmente simples. O objetivo é criar endpoints que possam servir tanto o arquivo tileset.json quanto os arquivos de tile individuais.  
O arquivo app/main.py conterá toda a lógica necessária:

Python

from fastapi import FastAPI  
from fastapi.staticfiles import StaticFiles  
from fastapi.responses import FileResponse  
from fastapi.middleware.cors import CORSMiddleware  
import os

\# Cria a instância da aplicação FastAPI  
app \= FastAPI()

\# \--- Configuração de CORS \---  
\# Permite que o frontend (ex: http://localhost:3000) faça requisições  
origins \= \[  
    "http://localhost:3000",  
\]

app.add\_middleware(  
    CORSMiddleware,  
    allow\_origins=origins,  
    allow\_credentials=True,  
    allow\_methods=\["\*"\],  
    allow\_headers=\["\*"\],  
)

\# \--- Definição dos Endpoints \---

\# Diretório base onde os tilesets estáticos estão armazenados  
STATIC\_TILES\_DIR \= os.path.join(os.path.dirname(\_\_file\_\_), "..", "static\_tiles")

\# 1\. Endpoint para servir o arquivo tileset.json  
@app.get("/tileset/{dataset\_name}/tileset.json")  
async def get\_tileset(dataset\_name: str):  
    """  
    Serve o arquivo tileset.json principal para um determinado dataset.  
    """  
    tileset\_path \= os.path.join(STATIC\_TILES\_DIR, dataset\_name, "tileset.json")  
    if os.path.exists(tileset\_path):  
        return FileResponse(tileset\_path)  
    return {"error": "Tileset not found"}, 404

\# 2\. Monta um diretório estático para servir todos os outros arquivos de tile  
\# As requisições para /tiles/{dataset\_name}/... serão mapeadas para  
\# /static\_tiles/{dataset\_name}/...  
app.mount("/tiles", StaticFiles(directory=STATIC\_TILES\_DIR), name="tiles")

\# Endpoint raiz para verificação de saúde  
@app.get("/")  
async def root():  
    return {"message": "FastAPI 3D Tiles server is running."}

Neste código, duas estratégias são usadas:

1. Um endpoint dinâmico /tileset/{dataset\_name}/tileset.json é criado para servir especificamente o arquivo manifesto. Isso oferece controle e clareza sobre o ponto de entrada de cada tileset.  
2. A funcionalidade StaticFiles, herdada do Starlette, é usada para servir de forma eficiente todos os outros arquivos. Ao "montar" o diretório static\_tiles na rota /tiles, o FastAPI automaticamente lida com a busca e o serviço de qualquer arquivo solicitado dentro dessa estrutura de diretórios (e.g., uma requisição para /tiles/my\_dataset/0/0/0.pnts servirá o arquivo correspondente do sistema de arquivos). Esta é a abordagem mais performática, pois aproveita otimizações internas para o serviço de arquivos estáticos.

### **2.4 Configuração de CORS (Cross-Origin Resource Sharing)**

Durante o desenvolvimento, o frontend Next.js será executado em uma porta (geralmente 3000), enquanto o backend FastAPI será executado em outra (geralmente 8000). Do ponto de vista do navegador, http://localhost:3000 e http://localhost:8000 são "origens" diferentes. Por padrão, a política de mesma origem (Same-Origin Policy) dos navegadores bloqueia requisições de script de uma origem para outra como medida de segurança.  
Para permitir que o frontend se comunique com o backend, é essencial configurar o **CORS** no servidor FastAPI. O CORSMiddleware do FastAPI simplifica este processo. Ao adicionar o middleware à aplicação, especificamos uma lista de origins permitidas. No código de exemplo acima, a origem http://localhost:3000 é explicitamente autorizada a fazer requisições para a API.23 As opções allow\_credentials=True, allow\_methods=\["\*"\] e allow\_headers=\["\*"\] fornecem uma configuração permissiva para o ambiente de desenvolvimento, permitindo todos os métodos e cabeçalhos HTTP, bem como o envio de cookies ou tokens de autorização.25

| Rota | Método HTTP | Descrição | Exemplo de Resposta |
| :---- | :---- | :---- | :---- |
| /tileset/{dataset\_name}/tileset.json | GET | Retorna o arquivo tileset.json principal para um dataset específico. | Content-Type: application/json, corpo do arquivo tileset.json. |
| /tiles/{dataset\_name}/{path:path} | GET | Serve estaticamente qualquer arquivo de tile (e.g., 0/0/0.pnts) de dentro do diretório do dataset. | Content-Type: application/octet-stream, corpo do arquivo binário do tile. |

## **Parte III: Implementação do Frontend: Renderização da Cena com Next.js e R3F**

O frontend é onde a visualização ganha vida. Ele é responsável por buscar os dados do backend, renderizar a cena 3D e permitir a interação do usuário. A utilização do Next.js como framework base oferece benefícios como uma estrutura de projeto robusta e um ecossistema rico, mas também introduz um desafio específico relacionado à sua natureza de renderização no lado do servidor (SSR).

### **3.1 Estruturando a Aplicação Next.js**

O primeiro passo é inicializar um novo projeto Next.js e instalar as dependências necessárias para a renderização 3D.

1. **Setup Inicial:** Um novo projeto pode ser criado com o comando npx create-next-app@latest frontend.15  
2. **Instalação de Dependências:** As bibliotecas principais para o nosso stack de renderização são instaladas via npm ou yarn:  
   Bash  
   npm install three @types/three @react-three/fiber @react-three/drei @takram/three-geospatial

   * three: O motor de renderização WebGL.7  
   * @react-three/fiber: O renderizador React para Three.js.9  
   * @react-three/drei: Uma biblioteca de helpers e abstrações úteis para R3F, que simplifica tarefas comuns como adicionar controles de câmera ou loaders.7  
   * @takram/three-geospatial: A biblioteca especializada para renderização de 3D Tiles e efeitos atmosféricos.11  
3. **Organização de Componentes:** Uma estrutura de diretórios lógica ajuda a manter o código organizado. Os componentes relacionados à cena 3D são frequentemente isolados em seu próprio diretório para separá-los da lógica de UI padrão.  
   /frontend

|-- /components  
| |-- /canvas  
| | |-- Scene.jsx \# Componente que contém a cena 3D e o Canvas R3F  
| | |-- Loader.jsx \# Componente de fallback para React.Suspense  
|-- /pages  
| |-- \_app.js  
| |-- index.js \# Página principal que irá renderizar a cena  
|-- /styles  
\`\`\`

### **3.2 Lidando com as Restrições do SSR: O next/dynamic**

Este é o desafio técnico mais crítico ao integrar bibliotecas WebGL com Next.js. O Next.js, por padrão, pré-renderiza as páginas no servidor para melhorar o desempenho de carregamento inicial e o SEO. Este processo de renderização no lado do servidor (SSR) ocorre em um ambiente Node.js.  
O conflito fundamental surge porque bibliotecas como Three.js e, por extensão, React Three Fiber, dependem intrinsecamente de APIs que só existem no navegador, como window, document, e o WebGLRenderingContext.26 Quando o Next.js tenta importar e executar o código de um componente 3D no servidor, ele não encontra essas APIs, resultando em um erro de compilação, tipicamente ReferenceError: window is not defined.  
A solução canônica para este problema no ecossistema Next.js é a **importação dinâmica com a desativação do SSR**. A função next/dynamic permite importar um componente React de forma assíncrona (lazy loading). Mais importante, ela aceita um objeto de opções onde se pode definir ssr: false. Isso instrui o Next.js a pular a renderização deste componente específico no servidor e a carregá-lo e renderizá-lo apenas no lado do cliente, ou seja, no navegador do usuário, onde as APIs WebGL estão disponíveis.28  
A implementação na página principal (pages/index.js) ficaria assim:

JavaScript

// Em pages/index.js  
import dynamic from 'next/dynamic';  
import Head from 'next/head';

// Importa dinamicamente o componente da cena 3D, desativando o SSR.  
// Um componente de 'loading' é fornecido como fallback enquanto o componente principal carrega.  
const Scene \= dynamic(  
  () \=\> import('@/components/canvas/Scene'),  
  { ssr: false, loading: () \=\> \<p\>Carregando Visualizador 3D...\</p\> }  
);

export default function HomePage() {  
  return (  
    \<\>  
      \<Head\>  
        \<title\>Visualizador Geoespacial 3D\</title\>  
      \</Head\>  
      \<main style={{ height: '100vh', width: '100%', margin: 0, padding: 0, background: '\#000' }}\>  
        \<Scene /\>  
      \</main\>  
    \</\>  
  );  
}

Esta abordagem não é apenas uma otimização; é um requisito funcional para garantir a compatibilidade entre o ambiente de servidor do Next.js e o ambiente de cliente das bibliotecas de renderização 3D.

### **3.3 Construção do Visualizador 3D Básico**

O componente \<Scene /\> é o coração da nossa visualização. Ele utilizará os componentes do React Three Fiber para configurar o ambiente 3D.

JavaScript

// Em components/canvas/Scene.jsx  
'use client'; // Diretiva para Next.js App Router, embora com \`next/dynamic\` no Pages Router, o efeito seja similar.

import { Canvas } from '@react-three/fiber';  
import { OrbitControls, PerspectiveCamera } from '@react-three/drei';

export default function Scene() {  
  return (  
    \<Canvas\>  
      {/\* Iluminação básica para a cena \*/}  
      \<ambientLight intensity={0.5} /\>  
      \<directionalLight position={} intensity={1} /\>

      {/\* Câmera e Controles \*/}  
      \<PerspectiveCamera makeDefault position={} fov={75} /\>  
      \<OrbitControls /\>

      {/\* Os componentes do tileset e efeitos serão adicionados aqui \*/}  
    \</Canvas\>  
  );  
}

* **\<Canvas\>:** Este componente do R3F cria uma cena Three.js, um renderizador WebGL e um loop de renderização que atualiza a cena a cada frame, tudo de forma automática.15  
* **Câmera e Controles:** Uma \<PerspectiveCamera\> é adicionada e definida como a câmera padrão com makeDefault. Os OrbitControls da biblioteca @react-three/drei são incluídos para permitir que o usuário navegue na cena (rotacionar, dar zoom, mover) usando o mouse.15  
* **Iluminação:** Uma \<ambientLight\> fornece iluminação global básica, enquanto uma \<directionalLight\> simula uma fonte de luz distante como o sol, criando sombras e realces.30

### **3.4 Integração do Renderizador de 3D Tiles**

Com a cena básica configurada, o próximo passo é integrar o componente que irá buscar e renderizar os 3D Tiles do nosso backend FastAPI. Assumindo que a biblioteca @takram/three-geospatial exporta um componente TilesRenderer, a lógica de integração ocorreria dentro do \<Scene /\>.  
Primeiro, é necessário criar um componente que receba a URL do tileset.json e a passe para o renderizador da Takram.

JavaScript

// Dentro de components/canvas/Scene.jsx, um novo componente  
import { TilesRenderer } from '@takram/three-geospatial'; // Importação hipotética

function MyTileset() {  
  // A URL aponta para o nosso backend FastAPI  
  const tilesetUrl \= 'http://localhost:8000/tileset/my\_dataset/tileset.json';  
    
  return \<TilesRenderer url={tilesetUrl} /\>;  
}

// E então, dentro do componente Scene:  
export default function Scene() {  
  return (  
    \<Canvas\>  
      {/\*... Iluminação, Câmera e Controles... \*/}  
        
      {/\* Adiciona o renderizador de tiles à cena \*/}  
      \<React.Suspense fallback={null}\>  
        \<MyTileset /\>  
      \</React.Suspense\>  
    \</Canvas\>  
  );  
}

O componente TilesRenderer da biblioteca @takram/three-geospatial seria responsável por toda a lógica complexa:

1. Fazer a requisição HTTP para a tilesetUrl.  
2. Analisar o tileset.json para construir a árvore de tiles em memória.  
3. Monitorar a posição e o frustum da câmera a cada frame.  
4. Determinar quais tiles precisam ser carregados ou descarregados com base na visibilidade e na distância.  
5. Fazer as requisições para os arquivos de tile binários (e.g., .pnts) a partir das URLs relativas encontradas no tileset.json, que apontarão para o endpoint /tiles/... do nosso backend.  
6. Analisar os dados binários dos tiles e criar os objetos THREE.Mesh ou THREE.Points correspondentes para renderizá-los na cena.

O uso de \<React.Suspense\> é comum em R3F para lidar com o carregamento assíncrono de ativos, mostrando um fallback (neste caso, null) enquanto os dados do tileset estão sendo buscados e processados.

### **3.5 Aprimoramento da Fidelidade Visual (Estilo Takram)**

Para replicar a qualidade visual do exemplo de referência, os pacotes de efeitos atmosféricos da Takram são integrados à cena.

JavaScript

// Em components/canvas/Scene.jsx  
import { Atmosphere } from '@takram/three-atmosphere'; // Importação hipotética  
import { Clouds } from '@takram/three-clouds';       // Importação hipotética

//...

export default function Scene() {  
  return (  
    \<Canvas\>  
      {/\*... Iluminação, Câmera e Controles... \*/}  
        
      {/\* Adiciona os efeitos visuais \*/}  
      \<Atmosphere /\>  
      \<Clouds /\>

      \<React.Suspense fallback={null}\>  
        \<MyTileset /\>  
      \</React.Suspense\>  
    \</Canvas\>  
  );  
}

* **\<Atmosphere /\>:** Este componente renderizaria um domo de céu realista, simulando a dispersão da luz solar através das partículas da atmosfera. Isso cria gradientes de cor realistas no horizonte e muda a cor do céu com base na posição do sol (que pode ser controlada por uma luz direcional).11  
* **\<Clouds /\>:** Este componente adicionaria uma camada de nuvens volumétricas e geo-referenciadas, que podem lançar sombras sobre o terreno e adicionar uma sensação de profundidade e escala à cena, um elemento chave na estética do exemplo da Takram.11

## **Parte IV: Blueprint do Projeto e Integração Completa**

Unindo as partes de backend e frontend, esta seção final apresenta uma visão holística da arquitetura da aplicação, detalhando o fluxo de dados completo e fornecendo diretrizes para a organização do código e a implantação em um ambiente de produção.

### **4.1 O Fluxo de Dados de Ponta a Ponta**

A interação entre o cliente e o servidor segue um ciclo de requisição e resposta bem definido, orquestrado pela lógica de streaming do padrão 3D Tiles. O fluxo completo pode ser descrito nos seguintes passos:

1. **Carregamento Inicial:** O usuário acessa a URL da aplicação. O Next.js serve o HTML inicial da página. Como o componente da cena 3D foi importado dinamicamente com ssr: false, ele não faz parte deste payload inicial.  
2. **Montagem no Cliente:** No navegador, o JavaScript da página é executado. O componente \<Scene /\> é carregado e montado, criando o \<Canvas\> do R3F.  
3. **Requisição do Manifesto:** O componente TilesRenderer (da biblioteca @takram/three-geospatial), ao ser montado, dispara uma requisição HTTP GET para o backend FastAPI, solicitando o arquivo manifesto: GET http://localhost:8000/tileset/my\_dataset/tileset.json.  
4. **Resposta do Backend:** O endpoint do FastAPI recebe a requisição, localiza o arquivo tileset.json correspondente no diretório static\_tiles e o retorna com o Content-Type: application/json.  
5. **Análise e Carregamento de Tiles:** O TilesRenderer no frontend recebe e analisa o tileset.json, construindo a hierarquia do tileset em memória. Com base na posição inicial da câmera, ele atravessa a árvore e identifica os tiles que estão visíveis e mais próximos. Para cada um desses tiles, ele dispara novas requisições GET para o backend, como GET http://localhost:8000/tiles/my\_dataset/0/0/0.pnts.  
6. **Serviço de Tiles Estáticos:** O servidor FastAPI, através da sua montagem StaticFiles, intercepta essas requisições. Ele as mapeia para os arquivos correspondentes no sistema de arquivos (e.g., backend/static\_tiles/my\_dataset/0/0/0.pnts) e os serve eficientemente, geralmente com Content-Type: application/octet-stream.  
7. **Renderização e Loop de Interação:** À medida que os dados binários dos tiles chegam ao frontend, o TilesRenderer os decodifica, cria os objetos Three.js apropriados (geometrias, materiais) e os adiciona à cena para serem renderizados.  
8. **Navegação do Usuário:** Quando o usuário navega na cena (movendo a câmera), o loop se repete. O TilesRenderer continuamente reavalia quais tiles estão visíveis, fazendo requisições para novos tiles que entram no campo de visão e liberando da memória os tiles que se tornam irrelevantes. Este ciclo contínuo de avaliação, requisição e renderização é o que permite a exploração fluida de conjuntos de dados massivos.

### **4.2 Estrutura de Repositório e Considerações de Implantação**

A organização do código e a estratégia de implantação são cruciais para a manutenibilidade e escalabilidade do projeto.

#### **Organização do Código**

Existem duas abordagens principais para gerenciar os códigos do frontend e do backend:

* **Repositórios Separados:** Manter o código do frontend Next.js e do backend FastAPI em dois repositórios Git distintos. Esta é uma abordagem simples e desacoplada, onde cada parte pode ter seu próprio ciclo de vida de desenvolvimento e implantação.  
* **Monorepo:** Manter ambos os projetos dentro de um único repositório Git, utilizando ferramentas como **Nx** (como visto no próprio repositório @takram/three-geospatial 11), Turborepo ou Lerna. Um monorepo pode facilitar o compartilhamento de código (e.g., tipos de dados TypeScript entre frontend e backend) e simplificar a gestão de dependências e os scripts de build. A escolha depende da preferência da equipe e da complexidade do projeto.

#### **Variáveis de Ambiente**

É uma má prática codificar URLs de API e outras configurações diretamente no código. Em vez disso, devem ser usadas variáveis de ambiente.

* **Next.js:** Crie um arquivo .env.local na raiz do projeto frontend com uma variável como NEXT\_PUBLIC\_API\_URL=http://localhost:8000. O código do frontend pode então acessar esta variável através de process.env.NEXT\_PUBLIC\_API\_URL.  
* **FastAPI:** A configuração pode ser gerenciada através de variáveis de ambiente do sistema ou um arquivo .env lido por uma biblioteca como python-dotenv.

#### **Passos para Implantação**

* **Backend (FastAPI):**  
  1. **Containerização:** A melhor prática é empacotar a aplicação FastAPI e suas dependências em uma imagem **Docker**. O Dockerfile deve copiar o código da aplicação e o diretório static\_tiles para dentro da imagem.  
  2. **Hospedagem:** A imagem Docker pode ser implantada em uma variedade de serviços de contêineres, como Google Cloud Run, AWS Fargate, ou Fly.io. Esses serviços gerenciam a escalabilidade e a execução do contêiner.  
  3. **Armazenamento de Tiles:** Para tilesets muito grandes, pode ser mais eficiente não incluir os arquivos de tile na imagem Docker, mas sim montá-los a partir de um serviço de armazenamento de objetos, como Amazon S3 ou Google Cloud Storage. A aplicação FastAPI precisaria ser adaptada para servir os arquivos a partir desse bucket de armazenamento.  
* **Frontend (Next.js):**  
  1. **Plataformas Otimizadas:** Serviços como **Vercel** (dos criadores do Next.js) e **Netlify** são altamente otimizados para a implantação de aplicações Next.js. Eles se integram diretamente com repositórios Git e automatizam o processo de build e implantação.  
  2. **Configuração:** Durante o processo de implantação, a variável de ambiente NEXT\_PUBLIC\_API\_URL deve ser configurada para apontar para a URL pública do backend FastAPI implantado. A configuração de CORS no backend também deve ser atualizada para incluir a URL de produção do frontend.

## **Conclusão e Próximos Passos**

Este relatório delineou uma arquitetura completa e robusta para a criação de uma aplicação de visualização de dados geoespaciais 3D de alto desempenho, utilizando um stack tecnológico moderno com Next.js e FastAPI. As decisões arquitetônicas chave foram fundamentadas na necessidade de lidar com conjuntos de dados massivos de forma eficiente. A adoção do padrão **OGC 3D Tiles** estabeleceu o contrato de dados fundamental entre o cliente e o servidor. A estratégia de **pré-processamento de dados** com py3dtiles e o serviço de arquivos estáticos com FastAPI garantem um backend rápido e escalável. No frontend, o uso de **importação dinâmica** (next/dynamic) com ssr: false resolveu o conflito de compatibilidade entre o Next.js e as bibliotecas de renderização WebGL, permitindo uma integração suave com o ecossistema React Three Fiber.  
Com esta base sólida, a aplicação pode ser estendida de várias maneiras para adicionar funcionalidades mais ricas e interativas.

### **Sugestões para Expansão**

* **Interatividade com Raycasting:** Implementar a funcionalidade de *raycasting* do Three.js, utilizando o hook useFrame do R3F. Isso permite detectar quando o cursor do mouse do usuário está sobre um objeto na cena (como um edifício ou um ponto em uma nuvem de pontos). Ao ocorrer uma interseção, informações detalhadas sobre aquele objeto, possivelmente contidas nos metadados do tile (batch table), podem ser exibidas em um painel de UI, criando uma experiência de exploração de dados mais rica.  
* **Estilização Dinâmica de Dados:** Explorar a especificação **3D Tile Styles**, um pequeno "linguagem" declarativa, semelhante a CSS, que pode ser aplicada a um tileset. Isso permite que o cliente estilize dinamicamente as feições com base em suas propriedades de metadados. Por exemplo, edifícios poderiam ser coloridos com base em sua altura ou ano de construção, ou pontos em uma nuvem poderiam ser filtrados com base em sua classificação, tudo no lado do cliente e sem a necessidade de modificar os dados originais.  
* **Integração de Outras Fontes de Dados:** O ecossistema Three.js é vasto. Bibliotecas como three-geo 31 ou geo-three 32 podem ser integradas para renderizar outros tipos de dados geoespaciais, como modelos de terreno 3D texturizados a partir de dados de **Digital Elevation Model (DEM)**. Isso permitiria combinar os dados de 3D Tiles (como edifícios) com uma representação realista do terreno subjacente, criando uma visualização ainda mais completa e contextualmente rica.

#### **Referências citadas**

1. 3D Tiles Explained: OGC, Open Standards, Cesium & Open 3D Data \- Swyvl, acessado em setembro 21, 2025, [https://www.swyvl.io/blog/3d-tiles-explained](https://www.swyvl.io/blog/3d-tiles-explained)  
2. developers.arcgis.com, acessado em setembro 21, 2025, [https://developers.arcgis.com/unreal-engine/layers/data-layers/3d-tiles/\#:\~:text=3D%20Tiles%20is%20an%20Open,3tz).](https://developers.arcgis.com/unreal-engine/layers/data-layers/3d-tiles/#:~:text=3D%20Tiles%20is%20an%20Open,3tz\).)  
3. 3D Tiles Standard | OGC Publications, acessado em setembro 21, 2025, [https://www.ogc.org/standards/3dtiles/](https://www.ogc.org/standards/3dtiles/)  
4. 3D Tiles Specification, acessado em setembro 21, 2025, [https://docs.ogc.org/cs/22-025r4/22-025r4.html](https://docs.ogc.org/cs/22-025r4/22-025r4.html)  
5. 3D Tiles – Cesium, acessado em setembro 21, 2025, [https://cesium.com/why-cesium/3d-tiles/](https://cesium.com/why-cesium/3d-tiles/)  
6. 3D Tiles layers | ArcGIS Maps SDK for Unreal Engine \- Esri Developer, acessado em setembro 21, 2025, [https://developers.arcgis.com/unreal-engine/layers/data-layers/3d-tiles/](https://developers.arcgis.com/unreal-engine/layers/data-layers/3d-tiles/)  
7. React Three Fiber: Introduction, acessado em setembro 21, 2025, [https://r3f.docs.pmnd.rs/](https://r3f.docs.pmnd.rs/)  
8. React Three Fiber and NextJS Starter Template \- Ryosuke, acessado em setembro 21, 2025, [https://whoisryosuke.com/blog/2022/react-three-fiber-and-nextjs-starter-template](https://whoisryosuke.com/blog/2022/react-three-fiber-and-nextjs-starter-template)  
9. pmndrs/react-three-fiber: A React renderer for Three.js \- GitHub, acessado em setembro 21, 2025, [https://github.com/pmndrs/react-three-fiber](https://github.com/pmndrs/react-three-fiber)  
10. What are React and React Three Fiber \- Three.js Journey, acessado em setembro 21, 2025, [https://threejs-journey.com/lessons/what-are-react-and-react-three-fiber](https://threejs-journey.com/lessons/what-are-react-and-react-three-fiber)  
11. takram-design-engineering/three-geospatial: Geospatial ... \- GitHub, acessado em setembro 21, 2025, [https://github.com/takram-design-engineering/three-geospatial](https://github.com/takram-design-engineering/three-geospatial)  
12. @takram/three-geospatial \- npm, acessado em setembro 21, 2025, [https://www.npmjs.com/package/@takram/three-geospatial](https://www.npmjs.com/package/@takram/three-geospatial)  
13. Geospatial Rendering in Three.js \+ Google Map Tiles : r/threejs \- Reddit, acessado em setembro 21, 2025, [https://www.reddit.com/r/threejs/comments/1j5kje4/geospatial\_rendering\_in\_threejs\_google\_map\_tiles/](https://www.reddit.com/r/threejs/comments/1j5kje4/geospatial_rendering_in_threejs_google_map_tiles/)  
14. How to integrate R3F into React (Next.js 15 & React 19)? : r/threejs \- Reddit, acessado em setembro 21, 2025, [https://www.reddit.com/r/threejs/comments/1jhh42d/how\_to\_integrate\_r3f\_into\_react\_nextjs\_15\_react\_19/](https://www.reddit.com/r/threejs/comments/1jhh42d/how_to_integrate_r3f_into_react_nextjs_15_react_19/)  
15. How to use ThreeJS in React & NextJS \- DEV Community, acessado em setembro 21, 2025, [https://dev.to/hnicolus/how-to-use-threejs-in-react-nextjs-4120](https://dev.to/hnicolus/how-to-use-threejs-in-react-nextjs-4120)  
16. First Steps \- FastAPI, acessado em setembro 21, 2025, [https://fastapi.tiangolo.com/tutorial/first-steps/](https://fastapi.tiangolo.com/tutorial/first-steps/)  
17. Using FastAPI to Build Python Web APIs \- Real Python, acessado em setembro 21, 2025, [https://realpython.com/fastapi-python-web-apis/](https://realpython.com/fastapi-python-web-apis/)  
18. py3dtiles, acessado em setembro 21, 2025, [https://py3dtiles.org/](https://py3dtiles.org/)  
19. VCityTeam/py3dtilers: Tilers accepting various input formats (OBJ, 3DCity databases, GeoJson, IFC) and producing 3DTiles tilesets. \- GitHub, acessado em setembro 21, 2025, [https://github.com/VCityTeam/py3dtilers](https://github.com/VCityTeam/py3dtilers)  
20. FastAPI Tutorial \- Tutorials Point, acessado em setembro 21, 2025, [https://www.tutorialspoint.com/fastapi/index.htm](https://www.tutorialspoint.com/fastapi/index.htm)  
21. Tutorial \- User Guide \- FastAPI, acessado em setembro 21, 2025, [https://fastapi.tiangolo.com/tutorial/](https://fastapi.tiangolo.com/tutorial/)  
22. py3dtiles \- PyPI, acessado em setembro 21, 2025, [https://pypi.org/project/py3dtiles/](https://pypi.org/project/py3dtiles/)  
23. Next.js with \--experimental-https, FastAPI calls coming back with "Redirect is not allowed for a preflight request" \- Stack Overflow, acessado em setembro 21, 2025, [https://stackoverflow.com/questions/78561739/next-js-with-experimental-https-fastapi-calls-coming-back-with-redirect-is-n](https://stackoverflow.com/questions/78561739/next-js-with-experimental-https-fastapi-calls-coming-back-with-redirect-is-n)  
24. CORS (Cross-Origin Resource Sharing) \- FastAPI, acessado em setembro 21, 2025, [https://fastapi.tiangolo.com/tutorial/cors/](https://fastapi.tiangolo.com/tutorial/cors/)  
25. CORS issue after FastAPI server deployment \- Questions / Help \- Fly.io Community, acessado em setembro 21, 2025, [https://community.fly.io/t/cors-issue-after-fastapi-server-deployment/19693](https://community.fly.io/t/cors-issue-after-fastapi-server-deployment/19693)  
26. Dynamically import class with no SSR in Next.js | David Angulo \- Software Engineer, acessado em setembro 21, 2025, [https://www.davidangulo.xyz/posts/dynamically-import-class-with-no-ssr-in-next-js/](https://www.davidangulo.xyz/posts/dynamically-import-class-with-no-ssr-in-next-js/)  
27. Using Non-SSR Friendly Components with Next.js \- Bits and Pieces, acessado em setembro 21, 2025, [https://blog.bitsrc.io/using-non-ssr-friendly-components-with-next-js-916f38e8992c](https://blog.bitsrc.io/using-non-ssr-friendly-components-with-next-js-916f38e8992c)  
28. Guides: Lazy Loading | Next.js, acessado em setembro 21, 2025, [https://nextjs.org/docs/pages/guides/lazy-loading](https://nextjs.org/docs/pages/guides/lazy-loading)  
29. Better way of making a component non SSR? : r/nextjs \- Reddit, acessado em setembro 21, 2025, [https://www.reddit.com/r/nextjs/comments/1hsl0k7/better\_way\_of\_making\_a\_component\_non\_ssr/](https://www.reddit.com/r/nextjs/comments/1hsl0k7/better_way_of_making_a_component_non_ssr/)  
30. Introduction \- React Three Fiber, acessado em setembro 21, 2025, [https://r3f.docs.pmnd.rs/getting-started/introduction](https://r3f.docs.pmnd.rs/getting-started/introduction)  
31. w3reality/three-geo: 3D geographic visualization library \- GitHub, acessado em setembro 21, 2025, [https://github.com/w3reality/three-geo](https://github.com/w3reality/three-geo)  
32. tentone/geo-three: Tile based geographic world map visualization library for threejs \- GitHub, acessado em setembro 21, 2025, [https://github.com/tentone/geo-three](https://github.com/tentone/geo-three)