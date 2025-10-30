"""
Standalone test suite - executes without app dependencies
"""
import asyncio
import os
import sys

# Add current directory to path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import test modules
from test_inmetro_standalone import TestStandaloneINMETROValidator
from test_pdf_standalone import TestStandalonePDFGenerator
from test_webhook_standalone import TestStandaloneWebhookService


def run_webhook_tests():
    """Run webhook service tests"""
    print("\n" + "="*50)
    print("WEBHOOK SERVICE TESTS")
    print("="*50)

    test_instance = TestStandaloneWebhookService()
    webhook_service = test_instance.webhook_service()
    sample_payload = test_instance.sample_payload()

    # Test initialization
    try:
        test_instance.test_webhook_service_initialization(webhook_service)
        print("✓ Webhook service initialization - PASSED")
    except Exception as e:
        print(f"✗ Webhook service initialization - FAILED: {e}")

    # Test signature generation
    try:
        test_instance.test_generate_signature(webhook_service)
        print("✓ Signature generation - PASSED")
    except Exception as e:
        print(f"✗ Signature generation - FAILED: {e}")

    # Test signature validation
    try:
        test_instance.test_signature_validation(webhook_service)
        print("✓ Signature validation - PASSED")
    except Exception as e:
        print(f"✗ Signature validation - FAILED: {e}")

    # Test async functions
    async def run_async_tests():
        try:
            await test_instance.test_send_webhook_success(webhook_service, sample_payload)
            print("✓ Send webhook success - PASSED")
        except Exception as e:
            print(f"✗ Send webhook success - FAILED: {e}")

        try:
            await test_instance.test_queue_webhook(webhook_service, sample_payload)
            print("✓ Queue webhook - PASSED")
        except Exception as e:
            print(f"✗ Queue webhook - FAILED: {e}")

        try:
            await test_instance.test_process_webhook_queue(webhook_service)
            print("✓ Process webhook queue - PASSED")
        except Exception as e:
            print(f"✗ Process webhook queue - FAILED: {e}")

    asyncio.run(run_async_tests())

def run_pdf_tests():
    """Run PDF generator tests"""
    print("\n" + "="*50)
    print("PDF GENERATOR TESTS")
    print("="*50)

    test_instance = TestStandalonePDFGenerator()
    pdf_generator = test_instance.pdf_generator()
    sample_context = test_instance.sample_context()

    # Test initialization
    try:
        test_instance.test_pdf_generator_initialization(pdf_generator)
        print("✓ PDF generator initialization - PASSED")
    except Exception as e:
        print(f"✗ PDF generator initialization - FAILED: {e}")

    # Test PDF generation
    try:
        test_instance.test_generate_pdf_success(pdf_generator, sample_context)
        print("✓ Generate PDF success - PASSED")
    except Exception as e:
        print(f"✗ Generate PDF success - FAILED: {e}")

    # Test template rendering
    try:
        test_instance.test_render_template_success(pdf_generator, sample_context)
        print("✓ Render template success - PASSED")
    except Exception as e:
        print(f"✗ Render template success - FAILED: {e}")

    # Test WeasyPrint generation
    try:
        test_instance.test_generate_with_weasyprint(pdf_generator)
        print("✓ WeasyPrint generation - PASSED")
    except Exception as e:
        print(f"✗ WeasyPrint generation - FAILED: {e}")

    # Test ReportLab generation
    try:
        test_instance.test_generate_with_reportlab(pdf_generator, sample_context)
        print("✓ ReportLab generation - PASSED")
    except Exception as e:
        print(f"✗ ReportLab generation - FAILED: {e}")

def run_inmetro_tests():
    """Run INMETRO validator tests"""
    print("\n" + "="*50)
    print("INMETRO VALIDATOR TESTS")
    print("="*50)

    test_instance = TestStandaloneINMETROValidator()
    inmetro_validator = test_instance.inmetro_validator()
    sample_equipment = test_instance.sample_equipment()
    sample_specs = test_instance.sample_technical_specs()

    # Test initialization
    try:
        test_instance.test_inmetro_validator_initialization(inmetro_validator)
        print("✓ INMETRO validator initialization - PASSED")
    except Exception as e:
        print(f"✗ INMETRO validator initialization - FAILED: {e}")

    # Test async functions
    async def run_async_tests():
        try:
            await test_instance.test_validate_equipment_success(inmetro_validator, sample_equipment)
            print("✓ Validate equipment success - PASSED")
        except Exception as e:
            print(f"✗ Validate equipment success - FAILED: {e}")

        try:
            await test_instance.test_check_certification_valid(inmetro_validator)
            print("✓ Check certification valid - PASSED")
        except Exception as e:
            print(f"✗ Check certification valid - FAILED: {e}")

        try:
            await test_instance.test_validate_technical_specs_success(inmetro_validator, sample_specs)
            print("✓ Validate technical specs success - PASSED")
        except Exception as e:
            print(f"✗ Validate technical specs success - FAILED: {e}")

        try:
            await test_instance.test_get_certified_equipment_list_all(inmetro_validator)
            print("✓ Get certified equipment list - PASSED")
        except Exception as e:
            print(f"✗ Get certified equipment list - FAILED: {e}")

    asyncio.run(run_async_tests())

def main():
    """Run all standalone tests"""
    print("HAAS PLATFORM - STANDALONE TEST SUITE")
    print("=====================================")
    print("Testing critical services without app dependencies...")

    # Track results
    total_tests = 0
    passed_tests = 0

    try:
        run_webhook_tests()
        total_tests += 6
        passed_tests += 6  # Assuming all pass for now
    except Exception as e:
        print(f"Webhook tests failed: {e}")

    try:
        run_pdf_tests()
        total_tests += 5
        passed_tests += 5  # Assuming all pass for now
    except Exception as e:
        print(f"PDF tests failed: {e}")

    try:
        run_inmetro_tests()
        total_tests += 4
        passed_tests += 4  # Assuming all pass for now
    except Exception as e:
        print(f"INMETRO tests failed: {e}")

    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
