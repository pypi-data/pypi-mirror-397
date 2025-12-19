# Finanfut Billing Python SDK

Client oficial sincrònic per consumir la **Finanfut Billing External API (`/external/v1`)** amb models compatibles amb **Pydantic v2**, ara preparat per treballar amb **Business Units**.

## Instal·lació

- Pydantic 2.x: `pip install finanfut-billing-sdk>=2.0`
- Pydantic 1.x: `pip install finanfut-billing-sdk<2.0`
- Des del repositori local: `pip install -e backend/sdk`

Dependències principals:

- `pydantic>=2.0,<3.0`
- `requests>=2.31`

## Configuració bàsica i Business Units

```python
from finanfut_billing_sdk import FinanfutBillingClient

client = FinanfutBillingClient(
    base_url="https://billing.finanfut.com",
    api_key="sk_live_xxx",
    business_unit_id="bu_default",  # opcional: aplicada a serveis/factures per defecte
)
```

### Com funciona `business_unit_id`

- **Global al client:** passa `business_unit_id` al constructor i s'aplicarà automàticament a les operacions compatibles.
- **Per operació:** pots sobreescriure-la en cada mètode (`business_unit_id="bu_alt"`).
- **Endpoints sense BU:** liquidacions, tax rates o partner payment methods són d'abast de companyia i ignoren la BU (l'SDK emet un avís si n'hi ha una definida).
- **Validació:** crear serveis/productes i factures requereix `business_unit_id`. L'SDK llança `FinanfutBillingValidationError` si no n'hi ha cap disponible.

## Exemples d'ús

### Crear producte/servei amb BU
```python
from decimal import Decimal
from finanfut_billing_sdk.models import ExternalServiceUpsertRequest

payload = ExternalServiceUpsertRequest(
    external_reference="service_abc",
    type="service",
    name="Monthly subscription",
    description="Access to premium content",
    price=Decimal("29.90"),
    vat_rate_code="vat_21",
)
service = client.upsert_service(payload)  # usa la BU global
```

### Crear factura amb BU (sobre-escrivint la BU global)
```python
from finanfut_billing_sdk.models import ExternalInvoiceCreateRequest, ExternalInvoiceLine

invoice = client.create_invoice(
    ExternalInvoiceCreateRequest(
        client_external_reference="client_123",
        currency="EUR",
        lines=[
            ExternalInvoiceLine(
                service_external_reference="service_abc",
                description="Premium plan",
                qty=1,
                price=29.90,
                vat_rate_code="vat_21",
            ),
        ],
    ),
    business_unit_id="bu_sales",  # prioritat respecte la BU global
)
```

### Operacions sense BU (àmbit de companyia)
```python
# Les liquidacions continuen essent globals a la companyia.
settlement = client.settlements.create_settlement(...)
# Si el client té BU per defecte, l'SDK avisarà que no s'aplica a aquest endpoint.
```

### Enviar factura i registrar pagament
```python
from finanfut_billing_sdk.models import ExternalInvoiceEmailRequest, ExternalPaymentCreateRequest

email = client.send_invoice_email(
    invoice.invoice_id,
    ExternalInvoiceEmailRequest(subject="La teva factura", body="Adjunt trobaràs el PDF"),
)

payment = client.register_payment(
    invoice.invoice_id,
    ExternalPaymentCreateRequest(amount=29.90, method="stripe"),
)
```

## Errors

```python
from finanfut_billing_sdk.errors import (
    FinanfutBillingAuthError,
    FinanfutBillingServiceError,
    FinanfutBillingValidationError,
)

try:
    client.list_tax_rates()
except FinanfutBillingAuthError:
    print("API key incorrecta o sense permisos")
except FinanfutBillingValidationError as e:
    print("Error de validació:", e.payload)
except FinanfutBillingServiceError as e:
    print(f"Error de servei ({e.request_id}): {e.error}")
```

Els errors del backend inclouen sempre `error`, `message` i `request_id`.

## Publicació a PyPI

El paquet està preparat per publicar-se a PyPI quan es creen tags `v*` al repositori. El workflow `publish-sdk.yml` valida la versió (`__version__`) i fa l'upload amb Twine.
