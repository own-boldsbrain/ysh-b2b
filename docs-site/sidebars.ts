import type { SidebarsConfig } from "@docusaurus/plugin-content-docs";

/**
 * Estrutura da documentação YSH B2B Platform
 * 
 * Versão mínima inicial - apenas documentos criados
 * Será expandida conforme novos docs forem adicionados
 */
const sidebars: SidebarsConfig = {
  docsSidebar: [
    {
      type: "category",
      label: "📘 Introdução",
      collapsed: false,
      items: [
        "intro/overview",
        "intro/architecture-overview",
        "intro/documentation-index",
      ],
    },
  ],
};

export default sidebars;
