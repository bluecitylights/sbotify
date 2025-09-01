# sbotify

# Run Client with stdio

Add server.py to .env:

```bash
MCP_SERVER_URL=mcp-server/server.py
```

```bash
uv run mcp-client/client.py
```

# Run with remote server:
[build-and-deploy-mcp-server-to-cloud-run](https://cloud.google.com/blog/topics/developers-practitioners/build-and-deploy-a-remote-mcp-server-to-google-cloud-run-in-under-10-minutes)

Make sure that you or any team members trying to access the remote MCP server have the roles/run.invoker IAM role bound to their IAM principal (Google Cloud account).

```bash
#Make tunnel to the Cloud Run
gcloud run services proxy sbotify-mcp-server --region=europe-west4
```

All traffic to http://127.0.0.1:8080 will now be authenticated and forwarded to our remote MCP server.