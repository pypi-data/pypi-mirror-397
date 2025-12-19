## Introduction

Phantomwright is a library that bridging playwright-core patch + extending playwright API for stealth injection & user simulation, we aim to:
 + Wrap & Re-export API from patchright, provide basic stealth ability
 + Provide the ability to extend playwright, thus you can use API to:
    + Enable stealth injection script
    + Do user simulation
+ Ability to add breakpoint into playwright-core and playwright-python
+ (TODO) More extending API support for recaptcha resolver, proxy management etc.

### Initialization & Unit Test

```shell
    uv venv
    .venv\Scripts\activate
    uv sync --extra dev
    uv run phantomwright_driver install-deps
    uv run phantomwright_driver install
    uv run pytest
```

### Clear VENV Installation

```shell
    uv venv --clear
```

### Debug Playwright Core

Phantomwright provide the ability to not only debug playwright-python, but also attach to node process that run playwright-core.

You need to first open `Chrome` and goto `chrome://inspect`, then `Open dedicated DevTools for Node`

In `Connection` tab, add connection to `localhost:9229`  

Then you just need to choose debug session `Core Repro: Select Case`, then pick (or write your own) one minimal repro case.

Node process will stopped at the first place and you can debug playwright-core.

This is to provide the ability to debug and send PR to patchright to fix critical issue.



### Bugs & Missing Features

| Minimal Repro | Description | Fixed |
|---------------|-------------|-------|
| [case_perplexity_init.py](core-minimal-repro/case_perplexity_init.py) | CSP Fix patch doesn't support `unsafe-inline` | ✅ |
| [case_locator_or.py](core-minimal-repro/case_locator_or.py) | Frames patch format issue during DOM sorting | ✅ |
| [case_dispatch_event.py](core-minimal-repro/case_dispatch_event.py) | `dispatch_event` only supports evaluates on isolated context, need to support main world dispatch | ❌ |
| [case_expose_binding.py](core-minimal-repro/case_expose_binding.py) | On isolated context, `Page.evaluate` fails to evaluate JS Handle; `JSHandle.evaluate` only supports isolated context, need to support JSHandle evaluate from main world | ❌ |
| [case_custom_select_engine.py](core-minimal-repro/case_custom_select_engine.py) | Custom Selector Engines not atomic in phantomwright | ❌ |

### Won't Fix

#### Console domain Disabled

`Runtime.enable` removing disabled `Runtime.consoleAPICalled` event, thus following test APIs are disabled:

- ❌ **WebError disabled**
  ```python
  page.context.on("weberror", lambda web_error: print(f"uncaught exception: {web_error.error}"))
  page.context.expect_event("weberror")
  ```

- ❌ **PageError disabled**
  ```python
  page.on("pageerror", lambda exc: print(f"uncaught exception: {exc}"))
  page.expect_event("pageerror")
  page.page_errors()
  ```

- ❌ **ConsoleMessage disabled**
  ```python
  page.on("console", lambda msg: print(msg.text))
  page.expect_console_message()
  page.console_messages()
  page.context.wait_for_event("console")
  page.expect_popup()
  ```

#### WebSocketRoute Disabled

CDP does not provide any endpoint to manipulate Web Socket. To support WebSocketRoute API, patchright would need to inject init scripts into MainWorld which is detectable, thus this feature doesn't get supported.

- ❌ **WebSocketRoute**
  ```python
  await page.route_web_socket("/ws", handler)
  ```

#### add_init_script Timing Issue

`add_init_script` can't directly call binding exposed by `expose_function`/`expose_binding`, because in patchright, init script is injected into html document, which will execute earlier than API exposed.

- ❌ Won't work:
  ```python
  args = []
  await context.expose_function("woof", lambda arg: args.append(arg))
  await context.add_init_script("woof('context')")
  await context.new_page()
  assert args == ["context"]
  ```

- ✅ Works:
  ```python
  args = []
  await context.expose_function("woof", lambda arg: args.append(arg))
  page = await context.new_page()
  await page.evaluate("woof('context')")
  assert args == ["context"]
  ```

#### add_init_script can't affect about:blank, Data-URIs and file://

Because patchright init scripts use Routing, and `about:blank`, Data-URIs, `file://` won't trigger playwright routing.

- ❌ **Data-URIs**
  ```python
  await page.add_init_script("window.injected = 123")
  await page.goto("data:text/html,<script>window.result = window.injected</script>")
  ```

- ❌ **about:blank**
  ```python
  await page.add_init_script("window.injected = 123")
  await page.goto("about:blank")
  ```

- ❌ **file://**
  ```python
  await page.add_init_script("window.injected = 123")
  await page.goto("file://app/test.html")
  ```

### add_init_script only take effect on main world, not isolated world

- 
  ``` python
    await page.add_init_script("window.injected = 123")

    # on browser top context
    window.injected # 123

    # on browser utility context
    window.injected # void
  ```

#### args=["--disable-popup-blocking"] Removed

This can be re-enabled if we need popup.

### Thanks

+ [patchright](https://pypi.org/project/patchright/)
+ [playwright-stealth](https://pypi.org/project/playwright-stealth/)