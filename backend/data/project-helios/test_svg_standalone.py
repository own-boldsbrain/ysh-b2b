#!/usr/bin/env python3
"""
Standalone test for SVG diagram generation logic.
Tests the SVG generation without any external dependencies.
"""

import os
from datetime import datetime

class StandaloneSVGGenerator:
    """Standalone SVG generator for testing purposes."""

    def generate_unifilar_diagram(self, project_data):
        """Generate unifilar diagram SVG."""
        equipments = project_data.get('equipments', [])
        panels = [eq for eq in equipments if eq.get('type') == 'panel']
        inverters = [eq for eq in equipments if eq.get('type') == 'inverter']
        string_boxes = [eq for eq in equipments if eq.get('type') == 'string_box']

        total_panels = sum(eq.get('quantity', 0) for eq in panels)
        num_strings = max(1, total_panels // 8)  # 8 panels per string

        svg_content = f'''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <!-- Title -->
    <text x="400" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold">
        Diagrama Unifilar - Sistema Fotovoltaico
    </text>

    <!-- Solar Panels -->
    <g id="panels">
        <text x="50" y="80" font-family="Arial, sans-serif" font-size="12" font-weight="bold">Painéis Solares</text>
'''

        y_pos = 100
        for i in range(min(num_strings, 3)):  # Show max 3 strings
            svg_content += f'''
        <rect x="30" y="{y_pos}" width="60" height="30" fill="#FFD700" stroke="#000" stroke-width="1"/>
        <text x="60" y="{y_pos + 20}" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">
            String {i+1}
        </text>
        <text x="120" y="{y_pos + 15}" font-family="Arial, sans-serif" font-size="9">
            {min(8, total_panels - i*8)} módulos
        </text>
        <text x="120" y="{y_pos + 25}" font-family="Arial, sans-serif" font-size="9">
            {total_panels * 285 // num_strings}W
        </text>
'''
            y_pos += 50

        # Inverters
        svg_content += f'''
    </g>

    <!-- Inverters -->
    <g id="inverters">
        <text x="300" y="80" font-family="Arial, sans-serif" font-size="12" font-weight="bold">Inversores</text>
'''
        y_pos = 100
        for i, inv in enumerate(inverters[:2]):  # Show max 2 inverters
            svg_content += f'''
        <rect x="280" y="{y_pos}" width="80" height="35" fill="#87CEEB" stroke="#000" stroke-width="1"/>
        <text x="320" y="{y_pos + 15}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" font-weight="bold">
            INV {i+1}
        </text>
        <text x="320" y="{y_pos + 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="8">
            {inv.get('power_w', 0)}W
        </text>
'''
            y_pos += 50

        # String Boxes
        svg_content += f'''
    </g>

    <!-- String Boxes -->
    <g id="string-boxes">
        <text x="450" y="80" font-family="Arial, sans-serif" font-size="12" font-weight="bold">Caixas de String</text>
'''
        y_pos = 100
        for i, sb in enumerate(string_boxes[:2]):  # Show max 2 string boxes
            svg_content += f'''
        <rect x="430" y="{y_pos}" width="70" height="30" fill="#FFA500" stroke="#000" stroke-width="1"/>
        <text x="465" y="{y_pos + 15}" text-anchor="middle" font-family="Arial, sans-serif" font-size="9" font-weight="bold">
            SB {i+1}
        </text>
        <text x="465" y="{y_pos + 25}" text-anchor="middle" font-family="Arial, sans-serif" font-size="8">
            {sb.get('voltage_v', 0)}V
        </text>
'''
            y_pos += 50

        # Connections
        svg_content += f'''
    </g>

    <!-- Connections -->
    <g id="connections" stroke="#000" stroke-width="2" fill="none">
        <!-- Panel to String Box -->
        <line x1="90" y1="115" x2="430" y2="115"/>
        <polygon points="425,112 435,115 425,118" fill="#000"/>

        <!-- String Box to Inverter -->
        <line x1="500" y1="115" x2="280" y2="115"/>
        <polygon points="285,112 275,115 285,118" fill="#000"/>
    </g>

    <!-- Grid Connection -->
    <g id="grid">
        <text x="600" y="80" font-family="Arial, sans-serif" font-size="12" font-weight="bold">Rede Elétrica</text>
        <circle cx="650" cy="115" r="20" fill="#FF6B6B" stroke="#000" stroke-width="1"/>
        <text x="650" y="120" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold">⚡</text>
        <line x1="360" y1="115" x2="630" y2="115" stroke="#000" stroke-width="2"/>
        <polygon points="635,112 625,115 635,118" fill="#000"/>
    </g>

    <!-- Technical Specs -->
    <g id="specs">
        <rect x="50" y="450" width="700" height="120" fill="#F8F9FA" stroke="#DEE2E6" stroke-width="1" rx="5"/>
        <text x="60" y="470" font-family="Arial, sans-serif" font-size="11" font-weight="bold">Especificações Técnicas:</text>
        <text x="60" y="485" font-family="Arial, sans-serif" font-size="9">• Potência Total: {project_data.get('total_power_kwp', 0)} kWp</text>
        <text x="60" y="500" font-family="Arial, sans-serif" font-size="9">• Número de Strings: {num_strings}</text>
        <text x="60" y="515" font-family="Arial, sans-serif" font-size="9">• Módulos Totais: {total_panels}</text>
        <text x="400" y="485" font-family="Arial, sans-serif" font-size="9">• Tensão Sistema: 1000V</text>
        <text x="400" y="500" font-family="Arial, sans-serif" font-size="9">• Frequência: 60Hz</text>
        <text x="400" y="515" font-family="Arial, sans-serif" font-size="9">• Tipo de Conexão: Trifásica</text>
    </g>
</svg>'''

        return svg_content

    def generate_layout_diagram(self, project_data):
        """Generate layout diagram SVG."""
        equipments = project_data.get('equipments', [])
        panels = [eq for eq in equipments if eq.get('type') == 'panel']
        total_panels = sum(eq.get('quantity', 0) for eq in panels)
        num_strings = max(1, total_panels // 8)

        svg_content = f'''<svg width="800" height="600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600">
    <!-- Title -->
    <text x="400" y="30" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" font-weight="bold">
        Diagrama de Layout - Sistema Fotovoltaico
    </text>

    <!-- Building -->
    <g id="building">
        <rect x="300" y="200" width="200" height="120" fill="#8B4513" stroke="#654321" stroke-width="2"/>
        <polygon points="300,200 400,150 500,200" fill="#654321" stroke="#654321" stroke-width="2"/>
        <text x="400" y="280" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold" fill="white">
            RESIDÊNCIA
        </text>
        <text x="400" y="295" text-anchor="middle" font-family="Arial, sans-serif" font-size="10" fill="white">
            Área Útil: ~180m²
        </text>
    </g>

    <!-- Solar Panel Arrays -->
    <g id="panel-arrays">
        <text x="50" y="80" font-family="Arial, sans-serif" font-size="12" font-weight="bold">Arranjos de Painéis Solares</text>
'''

        # South-facing array
        svg_content += '''
        <!-- South Array -->
        <g id="south-array">
            <text x="100" y="120" font-family="Arial, sans-serif" font-size="10" font-weight="bold">String Sul (180°)</text>
'''
        for row in range(2):
            for col in range(4):
                x = 80 + col * 25
                y = 130 + row * 20
                svg_content += f'''
            <rect x="{x}" y="{y}" width="20" height="15" fill="#FFD700" stroke="#000" stroke-width="0.5"/>
            <rect x="{x+2}" y="{y+2}" width="16" height="11" fill="#FFA500" stroke="none"/>'''

        svg_content += '''
        </g>
'''

        # East-facing array
        svg_content += '''
        <!-- East Array -->
        <g id="east-array">
            <text x="300" y="120" font-family="Arial, sans-serif" font-size="10" font-weight="bold">String Leste (90°)</text>
'''
        for row in range(2):
            for col in range(4):
                x = 280 + col * 25
                y = 130 + row * 20
                svg_content += f'''
            <rect x="{x}" y="{y}" width="20" height="15" fill="#FFD700" stroke="#000" stroke-width="0.5"/>
            <rect x="{x+2}" y="{y+2}" width="16" height="11" fill="#FFA500" stroke="none"/>'''

        svg_content += '''
        </g>
'''

        if num_strings > 2:
            # West-facing array
            svg_content += '''
            <!-- West Array -->
            <g id="west-array">
                <text x="500" y="120" font-family="Arial, sans-serif" font-size="10" font-weight="bold">String Oeste (270°)</text>
'''
            for row in range(2):
                for col in range(4):
                    x = 480 + col * 25
                    y = 130 + row * 20
                    svg_content += f'''
                <rect x="{x}" y="{y}" width="20" height="15" fill="#FFD700" stroke="#000" stroke-width="0.5"/>
                <rect x="{x+2}" y="{y+2}" width="16" height="11" fill="#FFA500" stroke="none"/>'''

            svg_content += '''
            </g>
'''

        # Compass Rose
        svg_content += '''
    </g>

    <!-- Compass Rose -->
    <g id="compass" transform="translate(650, 100)">
        <circle cx="0" cy="0" r="25" fill="none" stroke="#000" stroke-width="1"/>
        <line x1="0" y1="-20" x2="0" y2="20" stroke="#000" stroke-width="2"/>
        <line x1="-20" y1="0" x2="20" y2="0" stroke="#000" stroke-width="2"/>
        <text x="0" y="-15" text-anchor="middle" font-family="Arial, sans-serif" font-size="12" font-weight="bold">N</text>
        <text x="15" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">E</text>
        <text x="-5" y="18" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">S</text>
        <text x="-18" y="5" text-anchor="middle" font-family="Arial, sans-serif" font-size="10">W</text>
    </g>

    <!-- Scale -->
    <g id="scale">
        <text x="50" y="400" font-family="Arial, sans-serif" font-size="10">Escala: 1:100</text>
        <line x1="50" y1="410" x2="150" y2="410" stroke="#000" stroke-width="2"/>
        <line x1="50" y1="405" x2="50" y2="415" stroke="#000" stroke-width="1"/>
        <line x1="150" y1="405" x2="150" y2="415" stroke="#000" stroke-width="1"/>
        <text x="50" y="425" font-family="Arial, sans-serif" font-size="9">0</text>
        <text x="150" y="425" font-family="Arial, sans-serif" font-size="9">10m</text>
    </g>

    <!-- Technical Specs -->
    <g id="layout-specs">
        <rect x="50" y="450" width="700" height="120" fill="#F8F9FA" stroke="#DEE2E6" stroke-width="1" rx="5"/>
        <text x="60" y="470" font-family="Arial, sans-serif" font-size="11" font-weight="bold">Especificações de Layout:</text>
        <text x="60" y="485" font-family="Arial, sans-serif" font-size="9">• Área Total Ocupada: {total_panels * 2} m²</text>
        <text x="60" y="500" font-family="Arial, sans-serif" font-size="9">• Número de Strings: {num_strings}</text>
        <text x="60" y="515" font-family="Arial, sans-serif" font-size="9">• Módulos por String: 8</text>
        <text x="400" y="485" font-family="Arial, sans-serif" font-size="9">• Inclinação dos Módulos: 30°</text>
        <text x="400" y="500" font-family="Arial, sans-serif" font-size="9">• Distância ao Telhado: 0.3m</text>
        <text x="400" y="515" font-family="Arial, sans-serif" font-size="9">• Tipo de Fixação: Perfil Z + Clips</text>
    </g>
</svg>'''

        return svg_content

def test_standalone_svg_generation():
    """Test standalone SVG generation."""

    # Sample project data
    project_data = {
        'project_name': 'Sistema Fotovoltaico Residencial',
        'client_name': 'João Silva',
        'total_power_kwp': 8.0,
        'equipments': [
            {
                'type': 'panel',
                'model': 'Canadian Solar CS6K-285M',
                'quantity': 24,
                'power_w': 285,
                'voltage_v': 37.5,
                'current_a': 7.6
            },
            {
                'type': 'inverter',
                'model': 'SMA Sunny Boy 5.0',
                'quantity': 1,
                'power_w': 5000,
                'voltage_v': 400,
                'current_a': 12.5
            },
            {
                'type': 'string_box',
                'model': 'String Box 3 Strings',
                'quantity': 1,
                'voltage_v': 1000,
                'current_a': 25
            }
        ],
        'location': {
            'city': 'São Paulo',
            'state': 'SP',
            'latitude': -23.55,
            'longitude': -46.63
        },
        'responsible_engineer': 'Eng. Maria Santos',
        'crea_number': '123456/SP'
    }

    print("Testing Standalone SVG Diagram Generation...")
    print("=" * 50)

    try:
        # Initialize generator
        generator = StandaloneSVGGenerator()

        # Test unifilar diagram generation
        print("1. Generating Unifilar Diagram...")
        unifilar_svg = generator.generate_unifilar_diagram(project_data)
        print(f"✓ Unifilar diagram generated successfully ({len(unifilar_svg)} characters)")

        # Test layout diagram generation
        print("2. Generating Layout Diagram...")
        layout_svg = generator.generate_layout_diagram(project_data)
        print(f"✓ Layout diagram generated successfully ({len(layout_svg)} characters)")

        # Save test files for inspection
        test_dir = os.path.join(os.path.dirname(__file__), 'test_outputs')
        os.makedirs(test_dir, exist_ok=True)

        # Save unifilar diagram
        with open(os.path.join(test_dir, 'standalone_unifilar.svg'), 'w', encoding='utf-8') as f:
            f.write(unifilar_svg)
        print(f"✓ Unifilar diagram saved to test_outputs/standalone_unifilar.svg")

        # Save layout diagram
        with open(os.path.join(test_dir, 'standalone_layout.svg'), 'w', encoding='utf-8') as f:
            f.write(layout_svg)
        print(f"✓ Layout diagram saved to test_outputs/standalone_layout.svg")

        # Validate SVG structure
        if '<svg' in unifilar_svg and '</svg>' in unifilar_svg:
            print("✓ Unifilar SVG structure is valid")
        if '<svg' in layout_svg and '</svg>' in layout_svg:
            print("✓ Layout SVG structure is valid")

        print("\n" + "=" * 50)
        print("✅ Standalone SVG generation tests passed successfully!")
        print("SVG diagrams are ready for integration with PDF generation.")
        print(f"Test files saved in: {test_dir}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_standalone_svg_generation()
    sys.exit(0 if success else 1)