# Shared Types

```python
from numeral_tax.types import RefundResponse
```

# Tax

Types:

```python
from numeral_tax.types import Metadata, TaxPingResponse
```

Methods:

- <code title="get /tax/ping">client.tax.<a href="./src/numeral_tax/resources/tax/tax.py">ping</a>() -> <a href="./src/numeral_tax/types/tax_ping_response.py">TaxPingResponse</a></code>

## Calculations

Types:

```python
from numeral_tax.types.tax import CalculationResponse
```

Methods:

- <code title="post /tax/calculations">client.tax.calculations.<a href="./src/numeral_tax/resources/tax/calculations.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/calculation_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/tax/calculation_response.py">CalculationResponse</a></code>

## Transactions

Types:

```python
from numeral_tax.types.tax import DeleteTransactionResponse, TransactionResponse
```

Methods:

- <code title="post /tax/transactions">client.tax.transactions.<a href="./src/numeral_tax/resources/tax/transactions/transactions.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/transaction_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/tax/transaction_response.py">TransactionResponse</a></code>
- <code title="get /tax/transactions/{transaction_id}">client.tax.transactions.<a href="./src/numeral_tax/resources/tax/transactions/transactions.py">retrieve</a>(transaction_id) -> <a href="./src/numeral_tax/types/tax/transaction_response.py">TransactionResponse</a></code>
- <code title="delete /tax/transactions/{transaction_id}">client.tax.transactions.<a href="./src/numeral_tax/resources/tax/transactions/transactions.py">delete</a>(transaction_id) -> <a href="./src/numeral_tax/types/tax/delete_transaction_response.py">DeleteTransactionResponse</a></code>

### Refunds

Types:

```python
from numeral_tax.types.tax.transactions import RefundListResponse
```

Methods:

- <code title="get /tax/transactions/{transaction_id}/refunds">client.tax.transactions.refunds.<a href="./src/numeral_tax/resources/tax/transactions/refunds.py">list</a>(transaction_id) -> <a href="./src/numeral_tax/types/tax/transactions/refund_list_response.py">RefundListResponse</a></code>

## Refunds

Methods:

- <code title="post /tax/refunds">client.tax.refunds.<a href="./src/numeral_tax/resources/tax/refunds.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/refund_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/shared/refund_response.py">RefundResponse</a></code>

## RefundReversals

Methods:

- <code title="post /tax/refund_reversals">client.tax.refund_reversals.<a href="./src/numeral_tax/resources/tax/refund_reversals.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/refund_reversal_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/shared/refund_response.py">RefundResponse</a></code>

## Products

Types:

```python
from numeral_tax.types.tax import DeleteProductResponse, ProductResponse, ProductListResponse
```

Methods:

- <code title="post /tax/products">client.tax.products.<a href="./src/numeral_tax/resources/tax/products.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/product_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/tax/product_response.py">ProductResponse</a></code>
- <code title="get /tax/products/{reference_product_id}">client.tax.products.<a href="./src/numeral_tax/resources/tax/products.py">retrieve</a>(reference_product_id) -> <a href="./src/numeral_tax/types/tax/product_response.py">ProductResponse</a></code>
- <code title="get /tax/products">client.tax.products.<a href="./src/numeral_tax/resources/tax/products.py">list</a>(\*\*<a href="src/numeral_tax/types/tax/product_list_params.py">params</a>) -> <a href="./src/numeral_tax/types/tax/product_list_response.py">ProductListResponse</a></code>
- <code title="delete /tax/products/{reference_product_id}">client.tax.products.<a href="./src/numeral_tax/resources/tax/products.py">delete</a>(reference_product_id) -> <a href="./src/numeral_tax/types/tax/delete_product_response.py">DeleteProductResponse</a></code>

## Customers

Types:

```python
from numeral_tax.types.tax import CustomerResponse, CustomerDeleteResponse
```

Methods:

- <code title="post /tax/customers">client.tax.customers.<a href="./src/numeral_tax/resources/tax/customers.py">create</a>(\*\*<a href="src/numeral_tax/types/tax/customer_create_params.py">params</a>) -> <a href="./src/numeral_tax/types/tax/customer_response.py">CustomerResponse</a></code>
- <code title="get /tax/customers/{customer_id}">client.tax.customers.<a href="./src/numeral_tax/resources/tax/customers.py">retrieve</a>(customer_id) -> <a href="./src/numeral_tax/types/tax/customer_response.py">CustomerResponse</a></code>
- <code title="delete /tax/customers/{customer_id}">client.tax.customers.<a href="./src/numeral_tax/resources/tax/customers.py">delete</a>(customer_id) -> <a href="./src/numeral_tax/types/tax/customer_delete_response.py">CustomerDeleteResponse</a></code>
