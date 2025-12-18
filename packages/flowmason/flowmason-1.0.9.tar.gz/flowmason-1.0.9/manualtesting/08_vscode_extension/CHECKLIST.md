# VSCode Extension Checklist

## 8.1 Extension Installation

- [ ] Install from .vsix file succeeds
- [ ] Extension activates on .pipeline.json file
- [ ] Extension settings accessible in VSCode settings
- [ ] Studio URL configuration works
- [ ] API key configuration works (if needed)

---

## 8.2 File Support

### Syntax
- [ ] Syntax highlighting for .pipeline.json
- [ ] JSON validation for pipeline schema
- [ ] Error squiggles for invalid config

### IntelliSense
- [ ] IntelliSense for component types
- [ ] IntelliSense for field names
- [ ] Hover documentation shows

---

## 8.3 Debugging

### Launch
- [ ] Launch configuration works (launch.json)
- [ ] Start debugging pipeline

### Breakpoints
- [ ] Set breakpoint on stage
- [ ] Breakpoint hit pauses execution

### Debug Session
- [ ] Variables panel shows context
- [ ] Watch expressions work
- [ ] Step over (next stage)
- [ ] Step into (subpipeline)
- [ ] Continue execution
- [ ] Stop debugging

### Output
- [ ] Debug console output shows

---

## 8.4 Commands

- [ ] "FlowMason: Run Pipeline" command
- [ ] "FlowMason: Open in Studio" command
- [ ] "FlowMason: Validate Pipeline" command
- [ ] "FlowMason: Show Output" command
- [ ] Command palette integration (Cmd/Ctrl+Shift+P)

---

## Summary

| Area | Tests | Passed |
|------|-------|--------|
| Installation | 5 | ___ |
| File Support | 6 | ___ |
| Debugging | 11 | ___ |
| Commands | 5 | ___ |
| **Total** | **27** | ___ |
