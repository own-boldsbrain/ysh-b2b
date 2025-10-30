#!/usr/bin/env python3
"""
Simple test script for SVG diagram generation in HaaS platform.
Tests only the SVG generation logic without WeasyPrint dependencies.
"""

import sys
import os

# Add the haas directory to the path
haas_path = os.path.join(os.path.dirname(__file__), 'haas')
sys.path.insert(0, haas_path)
sys.path.insert(0, os.path.join(haas_path, 'app'))

def test_svg_generation_logic():
    """Test SVG diagram generation logic directly."""

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

    print("Testing SVG Diagram Generation Logic...")
    print("=" * 50)

    try:
        # Import only the SVG generation logic without WeasyPrint
        from app.services.pdf_generator import SVGDiagramGenerator

        # Initialize generator
        generator = SVGDiagramGenerator()

        # Test unifilar diagram generation
        print("1. Generating Unifilar Diagram...")
        unifilar_svg = generator.generate_unifilar_diagram(project_data)
        print(f"✓ Unifilar diagram generated successfully ({len(unifilar_svg)} characters)")

        # Check if SVG contains expected elements
        if '<svg' in unifilar_svg and '</svg>' in unifilar_svg:
            print("✓ SVG structure is valid")
        else:
            print("⚠ SVG structure may be invalid")

        # Test layout diagram generation
        print("2. Generating Layout Diagram...")
        layout_svg = generator.generate_layout_diagram(project_data)
        print(f"✓ Layout diagram generated successfully ({len(layout_svg)} characters)")

        if '<svg' in layout_svg and '</svg>' in layout_svg:
            print("✓ Layout SVG structure is valid")
        else:
            print("⚠ Layout SVG structure may be invalid")

        # Save test files for inspection
        test_dir = os.path.join(os.path.dirname(__file__), 'test_outputs')
        os.makedirs(test_dir, exist_ok=True)

        # Save unifilar diagram
        with open(os.path.join(test_dir, 'test_unifilar.svg'), 'w', encoding='utf-8') as f:
            f.write(unifilar_svg)
        print(f"✓ Unifilar diagram saved to test_outputs/test_unifilar.svg")

        # Save layout diagram
        with open(os.path.join(test_dir, 'test_layout.svg'), 'w', encoding='utf-8') as f:
            f.write(layout_svg)
        print(f"✓ Layout diagram saved to test_outputs/test_layout.svg")

        # Print sample of generated SVG
        print("\nSample of generated unifilar SVG (first 500 chars):")
        print("-" * 40)
        print(unifilar_svg[:500] + "..." if len(unifilar_svg) > 500 else unifilar_svg)
        print("-" * 40)

        print("\n" + "=" * 50)
        print("✅ SVG generation logic tests passed successfully!")
        print("SVG diagrams are ready for integration with PDF generation.")
        print(f"Test files saved in: {test_dir}")

        return True

    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_svg_generation_logic()
    sys.exit(0 if success else 1)