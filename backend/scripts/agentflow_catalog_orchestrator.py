#!/usr/bin/env python3
"""
AgentFlow-inspired Multi-Agent Orchestrator for YSH Store Catalog
Inspired by: https://github.com/lupantech/AgentFlow

Architecture:
- 🧭 Planner Agent: Coordinates workflow and decides next actions
- 👁️ Vision Agent: Analyzes images with Llama 3.2 Vision
- 📝 Enrichment Agent: Normalizes and enriches with Gemma 3
- ✅ Validator Agent: Validates data quality with GPT-OSS
- 🔍 Search Agent: Incremental browser search for missing data
- 💾 Memory: Shared context across agents

Usage:
    python scripts/agentflow_catalog_orchestrator.py --category INVERTERS --max 5
    python scripts/agentflow_catalog_orchestrator.py --all --background
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

try:
    import ollama
except ImportError:
    print("❌ Erro: módulo 'ollama' não instalado")
    print("Execute: pip install ollama")
    sys.exit(1)

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from ollama_model_selector import pick_image_model, pick_text_model
except ImportError:
    def pick_image_model():
        return 'llama3.2-vision:11b'
    def pick_text_model():
        return 'gemma3:4b'


# ============================================================================
# AGENT STATE & MEMORY
# ============================================================================

class AgentAction(Enum):
    """Possible agent actions"""
    ANALYZE_IMAGE = "analyze_image"
    ENRICH_DATA = "enrich_data"
    VALIDATE_QUALITY = "validate_quality"
    SEARCH_WEB = "search_web"
    FINALIZE = "finalize"
    ERROR = "error"


@dataclass
class ProductMemory:
    """Shared memory for product processing"""
    sku: str
    image_path: Optional[str] = None
    category: str = ""
    
    # Agent outputs
    vision_data: Dict[str, Any] = field(default_factory=dict)
    enriched_data: Dict[str, Any] = field(default_factory=dict)
    validation_result: Dict[str, Any] = field(default_factory=dict)
    search_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Workflow state
    completed_actions: List[AgentAction] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    
    # PVLib reference data
    pvlib_data: Optional[Dict[str, Any]] = None
    
    def mark_complete(self, action: AgentAction):
        """Mark action as completed"""
        if action not in self.completed_actions:
            self.completed_actions.append(action)
    
    def has_errors(self) -> bool:
        """Check if any errors occurred"""
        return len(self.errors) > 0
    
    def add_error(self, error: str):
        """Add error to memory"""
        self.errors.append(error)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'sku': self.sku,
            'image_path': self.image_path,
            'category': self.category,
            'vision_data': self.vision_data,
            'enriched_data': self.enriched_data,
            'validation_result': self.validation_result,
            'search_results': self.search_results,
            'completed_actions': [a.value for a in self.completed_actions],
            'errors': self.errors,
            'pvlib_data': self.pvlib_data
        }


# ============================================================================
# PLANNER AGENT - Orchestrates workflow
# ============================================================================

class PlannerAgent:
    """
    Planner Agent: Decides next action based on current state
    Similar to AgentFlow's Planner module
    """
    
    def __init__(self, model: str = "gemma3:4b"):
        self.model = model
        self.name = "🧭 Planner"
    
    def plan_next_action(self, memory: ProductMemory) -> AgentAction:
        """Decide next action based on current state"""
        
        # Priority order
        if AgentAction.ANALYZE_IMAGE not in memory.completed_actions:
            if memory.image_path:
                return AgentAction.ANALYZE_IMAGE
            else:
                return AgentAction.ENRICH_DATA  # Skip if no image
        
        if AgentAction.ENRICH_DATA not in memory.completed_actions:
            return AgentAction.ENRICH_DATA
        
        if AgentAction.VALIDATE_QUALITY not in memory.completed_actions:
            return AgentAction.VALIDATE_QUALITY
        
        # Optional: Search for missing data
        if self._needs_search(memory):
            if AgentAction.SEARCH_WEB not in memory.completed_actions:
                return AgentAction.SEARCH_WEB
        
        return AgentAction.FINALIZE
    
    def _needs_search(self, memory: ProductMemory) -> bool:
        """Determine if web search is needed"""
        # Check if critical data is missing
        enriched = memory.enriched_data
        
        if not enriched:
            return False
        
        # Check for missing manufacturer website
        if not enriched.get('manufacturer_website'):
            return True
        
        # Check for missing datasheet
        if not enriched.get('datasheet_url'):
            return True
        
        return False


# ============================================================================
# VISION AGENT - Analyzes images
# ============================================================================

class VisionAgent:
    """
    Vision Agent: Extracts metadata from product images
    Uses Llama 3.2 Vision for multimodal analysis
    """
    
    def __init__(self, model: str = "llama3.2-vision:11b"):
        self.model = model
        self.name = "👁️ Vision"
    
    def analyze(self, memory: ProductMemory) -> Dict[str, Any]:
        """Analyze product image"""
        
        if not memory.image_path:
            return {'error': 'No image path provided'}
        
        prompt = f"""Você é um especialista em produtos fotovoltaicos.

Analise esta imagem de produto da categoria {memory.category} e extraia:

{{
  "manufacturer": "marca/logo visível",
  "model": "código/modelo exato",
  "product_type": "inverter/panel/battery/stringbox/structure",
  "subtype": "gridtie/hybrid/offgrid/mono/poly/bifacial",
  "specifications": {{
    "power_w": 0,
    "power_kw": 0.0,
    "voltage": "...",
    "current_a": 0,
    "phase": "mono/tri/N/A",
    "efficiency_percent": 0.0,
    "mppt_count": 0
  }},
  "visible_text": "todo texto legível",
  "certifications": ["INMETRO", "IEC", "CE"],
  "image_quality_score": 0-10,
  "confidence_score": 0-10
}}

Retorne APENAS JSON, sem markdown."""

        try:
            start = time.time()
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [memory.image_path]
                }],
                options={'temperature': 0.1, 'num_predict': 1200}
            )
            elapsed = time.time() - start
            
            result_text = response['message']['content']
            
            # Parse JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            metadata = json.loads(result_text.strip())
            metadata['_processing_time'] = elapsed
            metadata['_agent'] = self.name
            
            return metadata
            
        except Exception as e:
            return {
                'error': str(e),
                '_agent': self.name
            }


# ============================================================================
# ENRICHMENT AGENT - Normalizes and enriches data
# ============================================================================

class EnrichmentAgent:
    """
    Enrichment Agent: Normalizes data and adds business logic
    Uses Gemma 3 for text processing and PVLib for technical validation
    """
    
    def __init__(self, model: str = "gemma3:4b"):
        self.model = model
        self.name = "📝 Enrichment"
        self.pvlib_data = self._load_pvlib_data()
    
    def _load_pvlib_data(self) -> Dict[str, Any]:
        """Load PVLib reference data"""
        try:
            base_path = Path.cwd()
            
            # Load normalized PVLib data
            inverters_path = (
                base_path / "data" / "catalog" / "data" / "catalog" / 
                "normalized_pvlib" / "normalized_inverters_sandia_clean.json"
            )
            panels_path = (
                base_path / "data" / "catalog" / "data" / "catalog" / 
                "normalized_pvlib" / "normalized_panels_cec_clean.json"
            )
            
            data = {}
            
            if inverters_path.exists():
                with open(inverters_path) as f:
                    data['inverters'] = json.load(f)
            
            if panels_path.exists():
                with open(panels_path) as f:
                    data['panels'] = json.load(f)
            
            return data
            
        except Exception as e:
            print(f"⚠️  Não foi possível carregar PVLib data: {e}")
            return {}
    
    def enrich(self, memory: ProductMemory) -> Dict[str, Any]:
        """Enrich product data"""
        
        vision_data = memory.vision_data
        
        if not vision_data or 'error' in vision_data:
            # Fallback: use SKU for basic enrichment
            return self._enrich_from_sku(memory)
        
        # Match with PVLib data if available
        pvlib_match = self._match_pvlib(vision_data, memory.category)
        if pvlib_match:
            memory.pvlib_data = pvlib_match
        
        # Build enrichment prompt
        prompt = f"""Você é um especialista em normalização de dados fotovoltaicos.

DADOS EXTRAÍDOS DA IMAGEM:
{json.dumps(vision_data, ensure_ascii=False, indent=2)}

SKU: {memory.sku}
CATEGORIA: {memory.category}

{"DADOS PVLIB ENCONTRADOS:" if pvlib_match else ""}
{json.dumps(pvlib_match, ensure_ascii=False, indent=2) if pvlib_match else ""}

Tarefas:
1. Normalize fabricante (ex: DEYE, SAJ, GROWATT, CANADIAN SOLAR)
2. Padronize modelo/SKU no formato: FABRICANTE-TIPO-MODELO
3. Valide e complete especificações técnicas
4. Gere descrição comercial curta (max 160 chars)
5. Gere título SEO (max 60 chars)
6. Crie tags/keywords (10 termos)
7. Calcule compatibilidades se for inversor ou painel

Retorne JSON:
{{
  "normalized_sku": "...",
  "manufacturer": "...",
  "manufacturer_normalized": "...",
  "model": "...",
  "category": "...",
  "subcategory": "...",
  "specifications": {{...}},
  "seo_title": "...",
  "short_description": "...",
  "tags": [...],
  "compatibility": {{...}},
  "pvlib_validated": true/false,
  "data_completeness_percent": 0-100,
  "confidence_score": 0-10
}}

Apenas JSON, sem markdown."""

        try:
            start = time.time()
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={'temperature': 0.2, 'num_predict': 1500}
            )
            elapsed = time.time() - start
            
            result_text = response['message']['content']
            
            # Parse JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            enriched = json.loads(result_text.strip())
            enriched['_processing_time'] = elapsed
            enriched['_agent'] = self.name
            enriched['_pvlib_match'] = bool(pvlib_match)
            
            return enriched
            
        except Exception as e:
            return {
                'error': str(e),
                '_agent': self.name
            }
    
    def _enrich_from_sku(self, memory: ProductMemory) -> Dict[str, Any]:
        """Fallback enrichment using only SKU"""
        return {
            'normalized_sku': memory.sku,
            'category': memory.category,
            'data_completeness_percent': 20,
            'confidence_score': 3,
            '_agent': self.name,
            '_fallback': True
        }
    
    def _match_pvlib(
        self, 
        vision_data: Dict[str, Any], 
        category: str
    ) -> Optional[Dict[str, Any]]:
        """Match product with PVLib database"""
        
        if not self.pvlib_data:
            return None
        
        manufacturer = vision_data.get('manufacturer', '').upper()
        model = vision_data.get('model', '').upper()
        
        if not manufacturer or not model:
            return None
        
        # Search in appropriate database
        db_key = 'inverters' if 'INVERTER' in category.upper() else 'panels'
        
        if db_key not in self.pvlib_data:
            return None
        
        products = self.pvlib_data[db_key]
        
        # Simple fuzzy matching
        for product in products[:100]:  # Limit search
            prod_mfg = product.get('Manufacturer', '').upper()
            prod_model = product.get('Model', '').upper()
            
            if manufacturer in prod_mfg or prod_mfg in manufacturer:
                if model in prod_model or prod_model in model:
                    return product
        
        return None


# ============================================================================
# VALIDATOR AGENT - Quality assurance
# ============================================================================

class ValidatorAgent:
    """
    Validator Agent: Validates data quality and completeness
    Uses GPT-OSS for comprehensive validation
    """
    
    def __init__(self, model: str = "gpt-oss:20b"):
        self.model = model
        self.name = "✅ Validator"
    
    def validate(self, memory: ProductMemory) -> Dict[str, Any]:
        """Validate product data quality"""
        
        enriched = memory.enriched_data
        
        if not enriched or 'error' in enriched:
            return {
                'validation_status': 'failed',
                'issues': ['No enriched data available'],
                '_agent': self.name
            }
        
        prompt = f"""Você é um validador de qualidade de dados para e-commerce B2B.

DADOS DO PRODUTO:
{json.dumps(enriched, ensure_ascii=False, indent=2)}

Valide:
1. Completude dos dados (0-100%)
2. Consistência entre campos
3. Qualidade das descrições
4. Presença de dados críticos (fabricante, modelo, specs)
5. Conformidade com padrões da indústria

Retorne JSON:
{{
  "validation_status": "approved/needs_review/rejected",
  "overall_score": 0-10,
  "completeness_percent": 0-100,
  "issues": ["lista de problemas encontrados"],
  "warnings": ["avisos não críticos"],
  "recommendations": ["sugestões de melhoria"],
  "ready_for_catalog": true/false,
  "critical_missing": ["dados críticos faltantes"]
}}

Apenas JSON."""

        try:
            start = time.time()
            response = ollama.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={'temperature': 0.1, 'num_predict': 1000}
            )
            elapsed = time.time() - start
            
            result_text = response['message']['content']
            
            # Parse JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            validation = json.loads(result_text.strip())
            validation['_processing_time'] = elapsed
            validation['_agent'] = self.name
            
            return validation
            
        except Exception as e:
            return {
                'error': str(e),
                '_agent': self.name
            }


# ============================================================================
# SEARCH AGENT - Incremental web search (stub)
# ============================================================================

class SearchAgent:
    """
    Search Agent: Intelligent multi-layer fallback search

    Architecture:
    1. RAG (TF-IDF local KB) - Primary, fastest
    2. SearxNG (FOSS multi-engine) - Secondary
    3. Ollama (LLM inference) - Tertiary, slowest
    """

    def __init__(self, kb_dir: str = "../output/knowledge_bases"):
        self.name = "🔍 Search"
        self._orchestrator = None
        self._kb_dir = kb_dir

    def _get_orchestrator(self):
        """Lazy load orchestrator to avoid circular imports."""
        if self._orchestrator is None:
            try:
                from intelligent_fallback_orchestrator import (
                    IntelligentFallbackOrchestrator,
                )

                self._orchestrator = IntelligentFallbackOrchestrator(
                    kb_dir=self._kb_dir,
                    circuit_threshold=5,
                    enable_adaptive=True,
                )
            except ImportError as e:
                print(f"⚠️  Fallback orchestrator não disponível: {e}")
                return None
        return self._orchestrator

    def search(self, memory: ProductMemory) -> List[Dict[str, Any]]:
        """Search for missing product data using intelligent fallback."""

        manufacturer = memory.enriched_data.get('manufacturer', '')
        model = memory.enriched_data.get('model', '')
        base_domain = memory.enriched_data.get("website", "")

        if not manufacturer or not model:
            return [
                {
                    "status": "skipped",
                    "reason": "Missing manufacturer or model",
                    "_agent": self.name,
                }
            ]

        orchestrator = self._get_orchestrator()
        if not orchestrator:
            return [
                {
                    "status": "fallback_unavailable",
                    "reason": "Orchestrator not initialized",
                    "_agent": self.name,
                }
            ]

        # Build search queries
        queries = [
            model,
            f"{manufacturer} {model}",
            f"{model} datasheet",
        ]

        # Infer base domain if not provided
        if not base_domain:
            base_domain = self._infer_domain(manufacturer)

        try:
            result = orchestrator.search(
                manufacturer=manufacturer.upper(),
                product_name=model,
                base_domain=base_domain,
                queries=queries,
                product_context=memory.enriched_data.get("description", ""),
            )

            if result:
                return [
                    {
                        "url": result.url,
                        "score": result.score,
                        "layer": result.layer.value,
                        "metadata": result.metadata,
                        "status": "success",
                        "_agent": self.name,
                    }
                ]
            else:
                return [
                    {
                        "status": "not_found",
                        "queries_attempted": queries,
                        "_agent": self.name,
                    }
                ]

        except Exception as e:
            return [{"status": "error", "error": str(e), "_agent": self.name}]

    def _infer_domain(self, manufacturer: str) -> str:
        """Infer manufacturer website domain."""
        domain_map = {
            "JINKO": "https://jinkosolar.com",
            "DEYE": "https://www.deyeinverter.com",
            "GROWATT": "https://www.growatt.com",
            "CANADIAN": "https://www.canadiansolar.com",
            "FRONIUS": "https://www.fronius.com",
            "HUAWEI": "https://solar.huawei.com",
            "SUNGROW": "https://www.sungrowpower.com",
        }
        return domain_map.get(
            manufacturer.upper(), f"https://{manufacturer.lower()}.com"
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Get search metrics from orchestrator."""
        orchestrator = self._get_orchestrator()
        if orchestrator:
            return orchestrator.get_metrics()
        return {}


# ============================================================================
# ORCHESTRATOR - Coordinates all agents
# ============================================================================

class CatalogOrchestrator:
    """
    Main orchestrator that coordinates all agents
    Inspired by AgentFlow's multi-agent architecture
    """
    
    def __init__(
        self,
        vision_model: str = "llama3.2-vision:11b",
        text_model: str = "gemma3:4b",
        validator_model: str = "gpt-oss:20b",
        verbose: bool = True
    ):
        self.planner = PlannerAgent(model=text_model)
        self.vision = VisionAgent(model=vision_model)
        self.enrichment = EnrichmentAgent(model=text_model)
        self.validator = ValidatorAgent(model=validator_model)
        self.search = SearchAgent()
        self.verbose = verbose
    
    def process_product(
        self, 
        sku: str,
        image_path: Optional[str],
        category: str
    ) -> ProductMemory:
        """Process single product through agent workflow"""
        
        # Initialize memory
        memory = ProductMemory(
            sku=sku,
            image_path=image_path,
            category=category
        )
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Processing: {sku}")
            print(f"Category: {category}")
            print(f"{'='*60}\n")
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # Planner decides next action
            next_action = self.planner.plan_next_action(memory)
            
            if next_action == AgentAction.FINALIZE:
                break
            
            if self.verbose:
                print(f"[{iteration}] {next_action.value}...", end=" ")
            
            start = time.time()
            
            # Execute action
            if next_action == AgentAction.ANALYZE_IMAGE:
                memory.vision_data = self.vision.analyze(memory)
                memory.mark_complete(AgentAction.ANALYZE_IMAGE)
            
            elif next_action == AgentAction.ENRICH_DATA:
                memory.enriched_data = self.enrichment.enrich(memory)
                memory.mark_complete(AgentAction.ENRICH_DATA)
            
            elif next_action == AgentAction.VALIDATE_QUALITY:
                memory.validation_result = self.validator.validate(memory)
                memory.mark_complete(AgentAction.VALIDATE_QUALITY)
            
            elif next_action == AgentAction.SEARCH_WEB:
                memory.search_results = self.search.search(memory)
                memory.mark_complete(AgentAction.SEARCH_WEB)
            
            elapsed = time.time() - start
            
            if self.verbose:
                print(f"({elapsed:.1f}s) ✓")
        
        return memory
    
    def process_batch(
        self,
        products: List[Dict[str, Any]],
        output_dir: Path
    ) -> List[ProductMemory]:
        """Process batch of products"""
        
        results = []
        total = len(products)
        
        print(f"\n{'='*60}")
        print(f"🚀 AgentFlow Catalog Orchestrator")
        print(f"{'='*60}")
        print(f"Products to process: {total}")
        print(f"Output directory: {output_dir}\n")
        
        for i, product in enumerate(products, 1):
            print(f"\n[{i}/{total}] {product['sku']}")
            
            memory = self.process_product(
                sku=product['sku'],
                image_path=product.get('image_path'),
                category=product.get('category', 'UNKNOWN')
            )
            
            results.append(memory)
            
            # Save individual result
            output_file = output_dir / f"{product['sku']}_agentflow.json"
            output_file.write_text(
                json.dumps(memory.to_dict(), ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        
        # Save summary
        self._save_summary(results, output_dir)
        
        return results
    
    def _save_summary(self, results: List[ProductMemory], output_dir: Path):
        """Save processing summary"""
        
        summary = {
            'processed_at': datetime.now().isoformat(),
            'total_products': len(results),
            'successful': sum(1 for r in results if not r.has_errors()),
            'with_errors': sum(1 for r in results if r.has_errors()),
            'results': [r.to_dict() for r in results]
        }
        
        summary_file = output_dir / "agentflow_summary.json"
        summary_file.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        print(f"\n{'='*60}")
        print(f"SUMMARY")
        print(f"{'='*60}")
        print(f"✅ Successful: {summary['successful']}/{summary['total_products']}")
        print(f"❌ With errors: {summary['with_errors']}/{summary['total_products']}")
        print(f"\n💾 Summary saved: {summary_file}")


# ============================================================================
# MAIN
# ============================================================================

def find_images_in_category(category: str, max_count: int = None) -> List[Dict]:
    """Find images in specified category"""
    
    base_path = Path.cwd()
    images_path = (
        base_path / "static" / "images-catálogo_distribuidores" / 
        "images_odex_source" / category
    )
    
    if not images_path.exists():
        return []
    
    images = list(images_path.glob("*.jpg")) + list(images_path.glob("*.jpeg"))
    
    products = []
    for img in images[:max_count] if max_count else images:
        # Extract SKU from filename
        sku = img.stem.split('_')[1] if '_' in img.stem else img.stem
        
        products.append({
            'sku': sku,
            'image_path': str(img),
            'category': category
        })
    
    return products


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='AgentFlow-inspired Multi-Agent Catalog Orchestrator'
    )
    parser.add_argument(
        '--category',
        choices=['INVERTERS', 'PANELS', 'STRINGBOXES', 'STRUCTURES'],
        required=True,
        help='Product category to process'
    )
    parser.add_argument(
        '--max',
        type=int,
        help='Maximum number of products'
    )
    parser.add_argument(
        '--output',
        default='output/agentflow-results',
        help='Output directory'
    )
    parser.add_argument(
        '--background',
        action='store_true',
        help='Run in background mode (less verbose)'
    )
    
    args = parser.parse_args()
    
    # Setup output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Find products
    products = find_images_in_category(args.category, args.max)
    
    if not products:
        print(f"❌ No products found in category: {args.category}")
        sys.exit(1)
    
    # Initialize orchestrator
    orchestrator = CatalogOrchestrator(
        vision_model=pick_image_model(),
        text_model=pick_text_model(),
        validator_model="gpt-oss:20b",
        verbose=not args.background
    )
    
    # Process batch
    results = orchestrator.process_batch(products, output_dir)
    
    print(f"\n✅ Processing complete!")
    print(f"📁 Results: {output_dir}/")


if __name__ == '__main__':
    main()
