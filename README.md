
<div align="center">
    <h3 align="center">embedbase-qdrant</h3>
    <p align="center">
        <p align="center">
            <a href="https://github.com/different-ai/embedbase">Embedbase</a> + <a href="https://qdrant.tech">Qdrant</a>
            Advanced and high-performant vector similarity search technology in your AI applications 
        </p>
    </p>
    <br>
    ⚠️ Status: Alpha release ⚠️
    <br>
    <br>
    <a href="https://discord.gg/pMNeuGrDky"><img alt="Discord" src="https://img.shields.io/discord/ 1066022656845025310?color=black&style=for-the-badge"></a>
    <a href="https://badge.fury.io/py/embedbase-qdrant"><img alt="PyPI" src="https://img.shields.io/pypi/v/embedbase-qdrant?color=black&style=for-the-badge"></a>
    <br>
    <div align="center">
        <p align="center">
            If you have any feedback or issues, please let us know by opening an issue or contacting us on <a href="https://discord.gg/pMNeuGrDky">discord</a>.
        </p>
        <p align="center">
            Please refer to the <a href="https://docs.embedbase.xyz">documentation</a>
        </p>
    </div>

</div>


## Getting started

To install the Embedbase Qdrant library, run the following command:

```bash
pip install embedbase-qdrant
```

## Quick tour

Let's try Embedbase + Qdrant with an OpenAI `embedder`:

```bash
pip install openai uvicorn
```

```python
import os
import uvicorn
from embedbase import get_app
from embedbase.embedding.openai import Openai
from embedbase_qdrant import Qdrant

# here we use openai to create embeddings and qdrant to store the data
app = get_app().use_embedder(Openai(os.environ["OPENAI_API_KEY"])).use_db(Qdrant()).run()

if __name__ == "__main__":
    uvicorn.run(app)
```

Start a local Qdrant:

```bash
docker-compose up -d
```

Run Embedbase:

```bash
python3 main.py
```

![pika-1683309528643-1x](https://user-images.githubusercontent.com/25003283/236533294-3cd481ac-6437-47b6-ae58-d5a9a6e0e4bf.png)

Check out other [examples](./examples/main.py) and [documentation](https://docs.embedbase.xyz) for more details.

