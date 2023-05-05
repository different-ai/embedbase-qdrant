# embedbase-qdrant

<div align="center">

[Embedbase](https://github.com/different-ai/embedbase) + [Qdrant](https://qdrant.tech) - Advanced and high-performant vector similarity search technology in your AI applications 
    <br>
    <br>
    ⚠️ Status: Alpha release ⚠️
    <br>
    <br>
    <a href="https://discord.gg/pMNeuGrDky"><img alt="Discord" src="https://img.shields.io/discord/ 1066022656845025310?color=black&style=for-the-badge"></a>
    <a href="https://badge.fury.io/py/embedbase-qdrant"><img alt="PyPI" src="https://img.shields.io/pypi/v/embedbase-qdrant?color=black&style=for-the-badge"></a>


</div>

If you have any feedback or issues, please let us know by opening an issue or contacting us on [discord](https://discord.gg/pMNeuGrDky).

Please refer to the [documentation](https://docs.embedbase.xyz/sdk).

## Getting started

To install the Embedbase Qdrant library, run the following command:

```bash
pip install embedbase-qdrant
```

## Usage

```python
import os
import uvicorn
from embedbase import get_app
from embedbase.embedding.openai import Openai
from sentence_transformers import SentenceTransformer
from embedbase_qdrant import Qdrant

app = get_app().use_embedder(Openai(
    os.environ["OPENAI_API_KEY"],
)).use_db(Qdrant()).run()

if __name__ == "__main__":
    uvicorn.run(app, reload=True)
```

Check out other [examples](./examples/main.py) and [documentation](https://docs.embedbase.xyz/sdk) for more details.

