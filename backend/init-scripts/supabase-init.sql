-- Enable extensions
CREATE EXTENSION
IF NOT EXISTS vector;
CREATE EXTENSION
IF NOT EXISTS pg_trgm;
CREATE EXTENSION
IF NOT EXISTS btree_gin;

-- Create schemas
CREATE SCHEMA
IF NOT EXISTS ysh_catalog;
CREATE SCHEMA
IF NOT EXISTS ysh_pricing;
CREATE SCHEMA
IF NOT EXISTS ysh_workflows;
CREATE SCHEMA
IF NOT EXISTS ysh_agents;

-- ==================== DISTRIBUTORS ====================
CREATE TABLE
IF NOT EXISTS ysh_catalog.distributors
(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid
(),
  name TEXT NOT NULL UNIQUE,
  url TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'active',
  credentials JSONB NOT NULL,
  config JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW
(),
  updated_at TIMESTAMPTZ DEFAULT NOW
()
);

INSERT INTO ysh_catalog.distributors
      (name, url, credentials, config)
VALUES
      ('fortlev', 'https://fortlevsolar.app/',
            '{"email": "fernando.teixeira@yello.cash", "password": "@Botapragirar2025"}',
            '{"extraction_interval": "24h", "priority": 1}'),
      ('neosolar', 'https://portalb2b.neosolar.com.br/',
            '{"email": "product@boldsbrain.ai", "password": "Rookie@010100"}',
            '{"extraction_interval": "24h", "priority": 1}'),
      ('solfacil', 'https://sso.solfacil.com.br/',
            '{"email": "fernando.teixeira@yello.cash", "password": "Rookie@010100"}',
            '{"extraction_interval": "24h", "priority": 2}'),
      ('fotus', 'https://app.fotus.com.br/',
            '{"email": "fernando@yellosolarhub.com", "password": "Rookie@010100"}',
            '{"extraction_interval": "24h", "priority": 2}'),
      ('odex', 'https://plataforma.odex.com.br/',
            '{"email": "fernando@yellosolarhub.com", "password": "Rookie@010100"}',
            '{"extraction_interval": "24h", "priority": 3}'),
      ('edeltec', 'https://edeltecsolar.com.br/',
            '{"email": "fernando@yellosolarhub.com", "password": "010100@Rookie"}',
            '{"extraction_interval": "24h", "priority": 3}'),
      ('dynamis', 'https://app.dynamisimportadora.com.br/',
            '{"email": "fernando@yellosolarhub.com", "password": "Rookie@010100"}',
            '{"extraction_interval": "24h", "priority": 3}')
ON CONFLICT
(name) DO NOTHING;

-- ==================== PRODUCTS ====================
CREATE TABLE
IF NOT EXISTS ysh_catalog.products
(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid
(),
  distributor_id UUID REFERENCES ysh_catalog.distributors
(id),
  distributor_sku TEXT NOT NULL,
  ysh_sku TEXT UNIQUE,
  
  -- Basic Info
  name TEXT NOT NULL,
  brand TEXT,
  category TEXT,
  subcategory TEXT,
  
  -- Pricing
  price_brl NUMERIC
(10,2),
  currency TEXT DEFAULT 'BRL',
  price_valid_until TIMESTAMPTZ,
  
  -- Technical Specs
  specifications JSONB DEFAULT '{}',
  
  -- Media
  images TEXT[],
  datasheet_url TEXT,
  
  -- Inventory
  stock_quantity INTEGER,
  stock_status TEXT,
  
  -- Search & Vectors
  search_vector tsvector,
  embedding vector
(1536),
  
  -- Metadata
  raw_data JSONB,
  quality_score NUMERIC
(3,2) DEFAULT 0.0,
  enrichment_status TEXT DEFAULT 'pending',
  
  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW
(),
  updated_at TIMESTAMPTZ DEFAULT NOW
(),
  last_extracted_at TIMESTAMPTZ,
  
  UNIQUE
(distributor_id, distributor_sku)
);

-- Indexes for products
CREATE INDEX
IF NOT EXISTS idx_products_distributor ON ysh_catalog.products
(distributor_id);
CREATE INDEX
IF NOT EXISTS idx_products_ysh_sku ON ysh_catalog.products
(ysh_sku);
CREATE INDEX
IF NOT EXISTS idx_products_category ON ysh_catalog.products
(category, subcategory);
CREATE INDEX
IF NOT EXISTS idx_products_brand ON ysh_catalog.products
(brand);
CREATE INDEX
IF NOT EXISTS idx_products_search ON ysh_catalog.products USING gin
(search_vector);
CREATE INDEX
IF NOT EXISTS idx_products_embedding ON ysh_catalog.products USING ivfflat
(embedding vector_cosine_ops)
WITH
(lists = 100);
CREATE INDEX
IF NOT EXISTS idx_products_enrichment ON ysh_catalog.products
(enrichment_status);

-- ==================== PRICE HISTORY ====================
CREATE TABLE
IF NOT EXISTS ysh_pricing.price_history
(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid
(),
  product_id UUID REFERENCES ysh_catalog.products
(id) ON
DELETE CASCADE,
  price_brl NUMERIC(10,2)
NOT NULL,
  currency TEXT DEFAULT 'BRL',
  recorded_at TIMESTAMPTZ DEFAULT NOW
(),
  source TEXT NOT NULL
);

CREATE INDEX
IF NOT EXISTS idx_price_history_product ON ysh_pricing.price_history
(product_id, recorded_at DESC);

-- ==================== WORKFLOWS ====================
CREATE TABLE
IF NOT EXISTS ysh_workflows.executions
(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid
(),
  workflow_id TEXT NOT NULL,
  workflow_type TEXT NOT NULL,
  status TEXT NOT NULL,
  input JSONB,
  output JSONB,
  error JSONB,
  started_at TIMESTAMPTZ DEFAULT NOW
(),
  completed_at TIMESTAMPTZ,
  duration_ms INTEGER
);

CREATE INDEX
IF NOT EXISTS idx_workflow_executions_type ON ysh_workflows.executions
(workflow_type, status);
CREATE INDEX
IF NOT EXISTS idx_workflow_executions_started ON ysh_workflows.executions
(started_at DESC);

-- ==================== AGENTS ====================
CREATE TABLE
IF NOT EXISTS ysh_agents.activity_log
(
  id UUID PRIMARY KEY DEFAULT gen_random_uuid
(),
  agent_type TEXT NOT NULL,
  action TEXT NOT NULL,
  input JSONB,
  output JSONB,
  error JSONB,
  duration_ms INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW
()
);

CREATE INDEX
IF NOT EXISTS idx_agent_log_type ON ysh_agents.activity_log
(agent_type, created_at DESC);

-- ==================== FUNCTIONS ====================

-- Update search vector on product insert/update
CREATE OR REPLACE FUNCTION update_product_search_vector
()
RETURNS TRIGGER AS $$
BEGIN
  NEW.search_vector := 
    setweight
(to_tsvector
('portuguese', COALESCE
(NEW.name, '')), 'A') ||
    setweight
(to_tsvector
('portuguese', COALESCE
(NEW.brand, '')), 'B') ||
    setweight
(to_tsvector
('portuguese', COALESCE
(NEW.category, '')), 'C') ||
    setweight
(to_tsvector
('portuguese', COALESCE
(NEW.subcategory, '')), 'D');
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_product_search_vector
  BEFORE
INSERT OR
UPDATE ON ysh_catalog.products
  FOR EACH ROW
EXECUTE FUNCTION update_product_search_vector
();

-- Track price changes
CREATE OR REPLACE FUNCTION track_price_changes
()
RETURNS TRIGGER AS $$
BEGIN
      IF (TG_OP = 'UPDATE' AND OLD.price_brl IS DISTINCT FROM NEW.price_brl) THEN
      INSERT INTO ysh_pricing.price_history
            (product_id, price_brl, currency, source)
      VALUES
            (NEW.id, NEW.price_brl, NEW.currency, 'catalog_update');
END
IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_track_price_changes
  AFTER
INSERT OR
UPDATE ON ysh_catalog.products
  FOR EACH ROW
EXECUTE FUNCTION track_price_changes
();

-- Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at
()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW
();
RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_update_products_timestamp
  BEFORE
UPDATE ON ysh_catalog.products
  FOR EACH ROW
EXECUTE FUNCTION update_updated_at
();

-- ==================== VIEWS ====================

-- Products needing enrichment
CREATE OR REPLACE VIEW ysh_catalog.products_need_enrichment AS
SELECT
      p.id,
      p.distributor_sku,
      p.name,
      p.brand,
      p.price_brl,
      p.quality_score,
      d.name as distributor_name
FROM ysh_catalog.products p
      JOIN ysh_catalog.distributors d ON p.distributor_id = d.id
WHERE p.enrichment_status = 'pending'
      OR p.quality_score < 0.7
      OR p.price_brl IS NULL
ORDER BY p.created_at ASC;

-- Price statistics by distributor
CREATE OR REPLACE VIEW ysh_pricing.distributor_stats AS
SELECT
      d.name as distributor_name,
      COUNT(p.id) as total_products,
      COUNT(p.price_brl) as products_with_price,
      AVG(p.price_brl) as avg_price,
      MIN(p.price_brl) as min_price,
      MAX(p.price_brl) as max_price
FROM ysh_catalog.distributors d
      LEFT JOIN ysh_catalog.products p ON d.id = p.distributor_id
GROUP BY d.id, d.name;

-- Recent workflow executions
CREATE OR REPLACE VIEW ysh_workflows.recent_executions AS
SELECT
      workflow_type,
      status,
      COUNT(*) as count,
      AVG(duration_ms) as avg_duration_ms,
      MAX(started_at) as last_run
FROM ysh_workflows.executions
WHERE started_at > NOW() - INTERVAL
'24 hours'
GROUP BY workflow_type, status;

-- Grant permissions
GRANT USAGE ON SCHEMA ysh_catalog TO postgres;
GRANT USAGE ON SCHEMA ysh_pricing TO postgres;
GRANT USAGE ON SCHEMA ysh_workflows TO postgres;
GRANT USAGE ON SCHEMA ysh_agents TO postgres;

GRANT ALL ON ALL TABLES IN SCHEMA ysh_catalog TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA ysh_pricing TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA ysh_workflows TO postgres;
GRANT ALL ON ALL TABLES IN SCHEMA ysh_agents TO postgres;

GRANT ALL ON ALL SEQUENCES IN SCHEMA ysh_catalog TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ysh_pricing TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ysh_workflows TO postgres;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ysh_agents TO postgres;
