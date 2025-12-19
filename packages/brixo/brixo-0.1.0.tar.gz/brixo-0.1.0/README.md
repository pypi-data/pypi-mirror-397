## 🚀 Getting Started

The easiest way to get traces flowing is to add the SDK to your app.

Install:

```bash
pip install brixo
```

Instrument your code:

```python
from brixo import Brixo, interaction, begin_context, update_context

def process_response(response)
    # do some job with the response
    update_context(output=response.result)

@interaction("Agent Run")
def main():
    prompt = "What’s the weather where I am?"

    begin_context(
        customer={"id": "1"},
        user={"email": "user@example.com"},
        session_id="session-123",
        metadata={"env": "demo"},
        input=prompt,
    )


    # call your agent / chain here and attach the output
    response = agent.invoke(prompt={"messages": [{ "role": "user", "content": prompt }]})

    process_response(response)

if __name__ == "__main__":
    Brixo.init(app_name="example-app")
    main()
```

Set `BRIXO_API_KEY` to avoid hardcoding secrets.

For full examples, see `examples/`.

## Development
### Running tests
```bash
uv run pytest
```
### Docker
```bash
docker compose run --rm package-dev bash
```

### Login to Codex using ChatGPT account inside the container
1. Open a bash inside the container
```shell
docker compose run --rm package-dev bash
```
2. Start the login process
```shell
codex login
```
3. Copy the login URL and paste in the browser, login with your account and copy the callback URL that starts with `http://localhost:1455/auth/callback...`
4. Find the name of the running docker container and with the callback URL, run the following command
```shell
docker exec -it brixo-package-dev-run-RUN_SUFFIX curl "http://localhost:1455/auth/callback..."
```
5. Check the login status with:
```shell
codex login status
```
