import asyncio

import agentspeak.ext_stdlib
import agentspeak.runtime
from a2a_acl.a2a_utils.card_holder import download_card

actions = agentspeak.Actions(agentspeak.ext_stdlib.actions)


@actions.add("jump", 0)
def _jump(a: agentspeak.runtime.Agent, t, i):
    print("[" + a.name + "] I jump")
    yield


@actions.add_procedure(".print_float", (float,))
def _print_float(a):
    print(str(a))


@actions.add_function(".str_concat", (str, str))
def _str_concat(s1: str, s2: str) -> str:
    return s1 + s2


@actions.add_function(".starts_with", (str, str))
def starts_with(a: str, b: str):
    return a.startswith(b)

@actions.add_function(".is_alive", (str,))
def is_alive(url:str) -> bool:
    try:
        asyncio.run(download_card(url))
        return True
    except Exception:
        return False
