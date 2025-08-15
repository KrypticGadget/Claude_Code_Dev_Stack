# Claude Code Browser Integration

This integration provides a bridge between the Claude Code Browser (AGPL-3.0) and the Dev Stack v3.0 system using an adapter pattern to maintain license compliance.

## Architecture Overview

```
Dev Stack v3.0 (AGPL-3.0)
├── integrations/browser/
│   ├── adapter.py          # Main adapter interface
│   ├── server_wrapper.py   # Extended server functionality
│   ├── api_endpoints.py    # Dev Stack specific endpoints
│   ├── streaming.py        # WebRTC/noVNC streaming
│   └── attribution.py     # AGPL compliance & attribution
│
└── clones/claude-code-browser/ (AGPL-3.0 Original)
    ├── LICENSE             # Original AGPL-3.0 license
    ├── main.go            # Original implementation
    ├── server.go          # Original server code
    └── ...                # Other original files
```

## License Compliance

- **Claude Code Browser**: AGPL-3.0 by @zainhoda
- **Integration Layer**: AGPL-3.0 (maintains compatibility)
- **Attribution**: All original code remains attributed to @zainhoda
- **Modifications**: All extensions clearly marked and documented

## Integration Pattern

The adapter pattern ensures:
1. Original AGPL code remains unchanged
2. Extensions are clearly separated
3. Full attribution is maintained
4. Source availability requirements are met

## Dev Stack Features Added

- `/api/devstack/agents` - Agent management API
- `/api/devstack/tasks` - Task monitoring API
- `/api/devstack/hooks` - Hook system integration
- `/api/devstack/audio` - Audio event streaming
- WebRTC/noVNC streaming capability
- PWA integration with monitoring components

## Usage

The integration runs as an extended server that wraps the original Claude Code Browser functionality while adding Dev Stack specific features.

## Attribution

Original Claude Code Browser by @zainhoda (https://github.com/zainhoda/claude-code-browser)
Licensed under AGPL-3.0