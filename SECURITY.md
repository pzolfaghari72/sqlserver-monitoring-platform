# Security

- Development credentials in `.env` are for local use only.
- Never commit production secrets.
- SQL Server credentials are environment/secret-manager inputs and are not stored in `config.monitoring_target`.
- Replace the development API secret and database passwords before deployment.
- Use least-privilege SQL Server login permissions in production instead of `sa`.
- Keep `.env` outside Git; only `.env.example` is intended for publication.
- The frontend API key is injected at container startup and must not be hard-coded in tracked frontend files.
- Rotate any credentials that have been shared in chat, terminals, screenshots, or prior local files before publishing.
