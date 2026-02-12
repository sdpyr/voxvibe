# voxvibe

SentioTrace için uygulama çekirdeği + dependency-free HTTP API prototipi.

## Ne var?

- Seans oluşturma (consent zorunlu)
- Transkript parçası ekleme
- Duygu zaman çizelgesi noktası ekleme
- Timestamp'e bağlı branch not ekleme
- API endpoint'leri ile oturum akışını uçtan uca çalıştırma
- Basit web arayüzü (`/`) ile manuel MVP demo

## API'yi çalıştırma

```bash
python -m app.api
```

Varsayılan adres: `http://127.0.0.1:8000`

Tarayıcıdan aç: `http://127.0.0.1:8000/`

### Endpoint'ler

- `GET /health`
- `POST /sessions`
- `POST /sessions/{session_id}/transcript`
- `POST /sessions/{session_id}/emotion`
- `POST /sessions/{session_id}/notes`
- `GET /sessions/{session_id}`

## Demo (otomatik akış)

```bash
python -m app.demo_flow
```

Bu komut lokal bir API başlatır, örnek bir seans akışını işler ve JSON çıktıyı gösterir.

## Test

```bash
python -m unittest discover -s tests -p 'test_*.py' -v
```

## Doküman

- Ürün stratejisi ve yol haritası: [docs/sentiotrace-plan.md](docs/sentiotrace-plan.md)
