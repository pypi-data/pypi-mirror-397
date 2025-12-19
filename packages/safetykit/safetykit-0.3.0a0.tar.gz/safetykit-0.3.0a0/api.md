# Decisions

Types:

```python
from safetykit.types import DecisionCreateResponse, DecisionGetResponse
```

Methods:

- <code title="post /v1/decisions">client.decisions.<a href="./src/safetykit/resources/decisions.py">create</a>(\*\*<a href="src/safetykit/types/decision_create_params.py">params</a>) -> <a href="./src/safetykit/types/decision_create_response.py">DecisionCreateResponse</a></code>
- <code title="get /v1/decisions/{decision_id}">client.decisions.<a href="./src/safetykit/resources/decisions.py">get</a>(decision_id) -> <a href="./src/safetykit/types/decision_get_response.py">DecisionGetResponse</a></code>

# Batches

Types:

```python
from safetykit.types import BatchCreateResponse, BatchGetResponse
```

Methods:

- <code title="post /v1/batches">client.batches.<a href="./src/safetykit/resources/batches.py">create</a>(\*\*<a href="src/safetykit/types/batch_create_params.py">params</a>) -> <a href="./src/safetykit/types/batch_create_response.py">BatchCreateResponse</a></code>
- <code title="get /v1/batches/{batch_id}">client.batches.<a href="./src/safetykit/resources/batches.py">get</a>(batch_id) -> <a href="./src/safetykit/types/batch_get_response.py">BatchGetResponse</a></code>

# Data

Types:

```python
from safetykit.types import DataAddResponse, DataGetStatusResponse
```

Methods:

- <code title="post /v1/data/{namespace}">client.data.<a href="./src/safetykit/resources/data.py">add</a>(namespace, \*\*<a href="src/safetykit/types/data_add_params.py">params</a>) -> <a href="./src/safetykit/types/data_add_response.py">DataAddResponse</a></code>
- <code title="get /v1/data/status/{requestId}">client.data.<a href="./src/safetykit/resources/data.py">get_status</a>(request_id) -> <a href="./src/safetykit/types/data_get_status_response.py">DataGetStatusResponse</a></code>
