# Test Instructions

## Django test runner
```bash
python manage.py test
```

## Pytest (recommended)
```bash
DJANGO_SETTINGS_MODULE=stockpredictor.settings pytest tests_ui.py tests_integration.py -v
```

## Targeted runs
```bash
DJANGO_SETTINGS_MODULE=stockpredictor.settings pytest tests_ui.py::ProcurementUITests::test_quick_order_creation -v
python manage.py test tests_integration.OrderCreationWorkflowTests
```
