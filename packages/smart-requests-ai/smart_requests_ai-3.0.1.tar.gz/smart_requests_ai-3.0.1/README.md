# Smart Requests AI (Integrated with AI)

**Smart Requests AI** is a simple, yet elegant, HTTP library, now enhanced with built-in AI capabilities. 

### A Note on Evolution & Innovation

We want to express our deepest gratitude to **Kenneth Reitz** and the entire Requests community for building and maintaining this incredible library for over a decade. It has truly been the "HTTP for Humans" backbone of Python.

As we look toward the future, we believe that integrating AI is no longer a luxury, but a necessity to manage the next wave of innovation. This version, maintained by **zinzied**, introduces native AI power to the classic Requests interface, ensuring that our tools evolve as fast as the technology they power. It is time to manage the innovation of tomorrow, today.

```python
>>> import smart_requests as requests
>>> # Initialize AI features
>>> requests.ai.configure(key='YOUR_GEMINI_API_KEY')
>>>
>>> r = requests.get('https://httpbin.org/get')
>>> # Use AI to extract structured data
>>> data = r.ai.extract("Extract any meaningful metadata from this page")
>>>
>>> # Analyze error responses
>>> r_err = requests.get('https://httpbin.org/status/404')
>>> print(r_err.ai.analyze())
```

Requests allows you to send HTTP/1.1 requests extremely easily. There’s no need to manually add query strings to your URLs, or to form-encode your `PUT` & `POST` data — but nowadays, just use the `json` method!

## AI-Powered Features

Smart Requests includes a native `ai` proxy on both `Response` and `Session` objects:

- **`Response.ai.extract(prompt, schema=None)`**: Extract structured information from response body using AI.
- **`Response.ai.analyze()`**: Get a human-readable analysis of the response, including fix suggestions for errors.
- **`Session.ai.humanize()`**: Automatically adjust session headers to mimic a real browser behavior using AI-generated profiles.

## Installing Smart Requests AI

Smart Requests AI is available on PyPI:

```console
$ python -m pip install smart-requests-ai
```

## Supported Features & Best–Practices

Smart Requests is ready for the demands of building robust and reliable HTTP–speaking applications, for the needs of today.

- **Integrated Google Gemini AI support**
- Keep-Alive & Connection Pooling
- International Domains and URLs
- Sessions with Cookie Persistence
- Browser-style TLS/SSL Verification
- Basic & Digest Authentication
- Familiar `dict`–like Cookies
- Automatic Content Decompression and Decoding
- Multi-part File Uploads
- SOCKS Proxy Support
- Connection Timeouts
- Streaming Downloads
- Automatic honoring of `.netrc`
- Chunked HTTP Requests

---

[![Kenneth Reitz](https://raw.githubusercontent.com/psf/requests/main/ext/kr.png)](https://kennethreitz.org) [![Python Software Foundation](https://raw.githubusercontent.com/psf/requests/main/ext/psf.png)](https://www.python.org/psf)
