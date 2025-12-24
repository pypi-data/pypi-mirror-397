
import httpx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
)

from a2a.utils import new_agent_text_message

from a2a.server.events import EventQueue


from a2a_acl.agent.acl_agent import ACLAgentExecutor
from a2a_acl.agent.server_utils import run_server
from a2a_acl.protocol.message_codec import extract_text
from a2a_acl.protocol.acl_message import ACLMessage, Illocution
from a2a_acl.a2a_utils.card_holder import download_card
from a2a_acl.interface.interface import ACLAgentCard, SkillDeclaration
from a2a_acl.protocol.send_acl_message import spawn_send_acl_message
from a2a_acl.utils.url import build_url

from a2a_agentspeak.content_codecs.common import python_agentspeak_codec_id, atom_codec_id

my_skill = SkillDeclaration(
    Illocution.TELL, "agent_ready", 0, "Receive a signal."
)
my_card = ACLAgentCard(
    "Client Agent", "A client agent", [my_skill], [python_agentspeak_codec_id, atom_codec_id]
)


class ClientAgentExecutor(ACLAgentExecutor):
    async def execute_tell(
        self,
        m: ACLMessage,
        output_event_queue: EventQueue,
    ) -> None:
        print("Incoming message: " + str(m))
        await output_event_queue.enqueue_event(
            new_agent_text_message("Ack: tell received.")
        )


host = "127.0.0.1"
my_port = 9998
other_agent_url = "http://127.0.0.1:9999"
my_url = build_url(host=host, port=my_port)


async def main() -> None:

    # 1) start an a2a server
    run_server(ClientAgentExecutor(my_card, my_url), host, my_port)

    # 2) query the other a2a agent
    async with httpx.AsyncClient() as httpx_client:

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None
        try:
            final_agent_card_to_use = await download_card(other_agent_url)

        except Exception as e:
            print("Client failed to fetch the public agent card. Cannot continue.")
            exit(-1)


        # First message (achieve)
        spawn_send_acl_message(final_agent_card_to_use,
            "achieve", "ping", my_url, python_agentspeak_codec_id
        )

        # Another message (ask)
        spawn_send_acl_message(final_agent_card_to_use,
            "ask", "secret", my_url, python_agentspeak_codec_id
        )

        # Another message (tell)
        spawn_send_acl_message(final_agent_card_to_use,
            "tell", "ready", my_url, python_agentspeak_codec_id
        )

        # Another message (achieve)
        spawn_send_acl_message(final_agent_card_to_use,
            "achieve", "ping", my_url, python_agentspeak_codec_id
        )

        # Another message (ask)
        spawn_send_acl_message(final_agent_card_to_use,
            "ask", "secret", my_url, python_agentspeak_codec_id
        )



if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
