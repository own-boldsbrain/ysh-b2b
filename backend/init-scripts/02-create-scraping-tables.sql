-- YSH Solar B2B - Database Schema
-- Tables para sistema de captura de imagens

-- Table: manufacturers
CREATE TABLE IF NOT EXISTS manufacturers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    base_url VARCHAR(500) NOT NULL,
    priority INT DEFAULT 50,
    active BOOLEAN DEFAULT true,
    last_scraped TIMESTAMP,
    last_status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_manufacturers_active ON manufacturers(active);
CREATE INDEX idx_manufacturers_priority ON manufacturers(priority DESC);

-- Table: products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    manufacturer_id INT NOT NULL REFERENCES manufacturers(id) ON DELETE CASCADE,
    model VARCHAR(255) NOT NULL,
    title VARCHAR(500),
    specs_json JSONB,
    image_url VARCHAR(1000),
    facebook_uploaded BOOLEAN DEFAULT false,
    facebook_uploaded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(manufacturer_id, model)
);

CREATE INDEX idx_products_manufacturer ON products(manufacturer_id);
CREATE INDEX idx_products_facebook ON products(facebook_uploaded);
CREATE INDEX idx_products_specs ON products USING GIN(specs_json);

-- Table: product_images
CREATE TABLE IF NOT EXISTS product_images (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    local_path VARCHAR(500),
    quality_score INT DEFAULT 0,
    width INT,
    height INT,
    file_size BIGINT,
    image_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_product_images_product ON product_images(product_id);
CREATE INDEX idx_product_images_score ON product_images(quality_score DESC);
CREATE INDEX idx_product_images_hash ON product_images(image_hash);

-- Table: enriched_products (processados pelo Pathway)
CREATE TABLE IF NOT EXISTS enriched_products (
    id SERIAL PRIMARY KEY,
    product_id INT NOT NULL REFERENCES products(id) ON DELETE CASCADE UNIQUE,
    sku VARCHAR(100) NOT NULL UNIQUE,
    category VARCHAR(100),
    normalized_specs JSONB,
    confidence_score FLOAT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_enriched_sku ON enriched_products(sku);
CREATE INDEX idx_enriched_category ON enriched_products(category);

-- Table: scraping_logs
CREATE TABLE IF NOT EXISTS scraping_logs (
    id SERIAL PRIMARY KEY,
    manufacturer_id INT NOT NULL REFERENCES manufacturers(id) ON DELETE CASCADE,
    status VARCHAR(50) NOT NULL,
    products_found INT DEFAULT 0,
    images_downloaded INT DEFAULT 0,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scraping_logs_manufacturer ON scraping_logs(manufacturer_id);
CREATE INDEX idx_scraping_logs_timestamp ON scraping_logs(timestamp DESC);

-- Seed: Principais fabricantes brasileiros
INSERT INTO manufacturers (name, base_url, priority, active) VALUES
('Jinko Solar', 'https://www.jinkosolar.com/en/site/products', 100, true),
('Canadian Solar', 'https://www.canadiansolar.com/products/', 100, true),
('Fronius', 'https://www.fronius.com/en/solar-energy/products', 90, true),
('Growatt', 'https://www.growatt.com/products', 90, true),
('Deye', 'https://www.deyeinverter.com/products/', 85, true),
('BYD', 'https://www.bydbatterybox.com/products/', 85, true),
('Trina Solar', 'https://www.trinasolar.com/en-glb/product', 80, true),
('SolarEdge', 'https://www.solaredge.com/products/', 80, true),
('Huawei', 'https://solar.huawei.com/en/products', 75, true),
('Aldo Solar', 'https://www.aldosolar.com/produtos/', 70, true)
ON CONFLICT (name) DO NOTHING;

-- View: Dashboard de scraping
CREATE OR REPLACE VIEW v_scraping_dashboard AS
SELECT 
    m.name as manufacturer,
    m.last_scraped,
    m.last_status,
    COUNT(DISTINCT p.id) as total_products,
    COUNT(DISTINCT pi.id) as total_images,
    SUM(CASE WHEN p.facebook_uploaded THEN 1 ELSE 0 END) as uploaded_to_facebook,
    AVG(pi.quality_score) as avg_image_quality
FROM manufacturers m
LEFT JOIN products p ON m.id = p.manufacturer_id
LEFT JOIN product_images pi ON p.id = pi.product_id
WHERE m.active = true
GROUP BY m.id, m.name, m.last_scraped, m.last_status
ORDER BY m.priority DESC, m.last_scraped ASC NULLS FIRST;

-- Function: Update timestamp on update
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers
CREATE TRIGGER manufacturers_updated_at
    BEFORE UPDATE ON manufacturers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER products_updated_at
    BEFORE UPDATE ON products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();

COMMENT ON TABLE manufacturers IS 'Fabricantes de equipamentos solares para scraping';
COMMENT ON TABLE products IS 'Produtos coletados dos sites dos fabricantes';
COMMENT ON TABLE product_images IS 'Imagens de produtos com scoring de qualidade';
COMMENT ON TABLE enriched_products IS 'Produtos enriquecidos com SKU normalizado';
COMMENT ON TABLE scraping_logs IS 'Histórico de execuções de scraping';
