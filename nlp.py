from langchain_openai.llms import AzureOpenAI
from langchain_openai import AzureChatOpenAI
from langchain.schema import AIMessage, SystemMessage, HumanMessage
from config import DefaultConfig

CONFIG = DefaultConfig()

llm_instruct = AzureOpenAI(
    openai_api_type="azure",
    azure_endpoint=CONFIG.OPENAI_API_BASE,
    openai_api_version="2023-05-15",
    deployment_name='gpt-35-turbo-instruct',
    openai_api_key=CONFIG.OPENAI_API_KEY,
)

llm_base = AzureChatOpenAI(
    openai_api_type="azure",
    azure_endpoint=CONFIG.OPENAI_API_BASE,
    openai_api_version="2023-05-15",
    deployment_name=CONFIG.DEPLOYMENT_NAME,
    openai_api_key=CONFIG.OPENAI_API_KEY,
    temperature=0.0,
)


translate_prompt = """Please translate this sentence to English:{question}"""

classify_prompt = """This sentence related to fan or light or both of fan and light? {question}
The output must be "light", "fan", "light and fan" or "none of them"
EXAMPLE:
INPUT: turn on the light
OUTPUT: light
INPUT: turn off the fan
OUTPUT: fan
INPUT: turn off the fan and turn on the light
OUTPUT: flight and fan
INPUT: turn on the television
OUTPUT: none of them
"""

fan_prompt = """This sentence related to turn on or turn off fan? {question}
The output must be "on" or "off"
EXAMPLE:
INPUT: turn on the fan
OUTPUT: on
INPUT: turn off the fan
OUTPUT: off
INPUT: turn off the light and turn on the fan
OUTPUT: on
INPUT: turn on the light and turn off the fan
OUTPUT: off
"""

light_prompt = """This sentence related to turn on or turn off light? {question}
The output must be "on" or "off"
EXAMPLE:
INPUT: turn on the light
OUTPUT: on
INPUT: turn off the light
OUTPUT: off
INPUT: turn off the light and turn on the fan
OUTPUT: off
"""


def chatbot(query):
    translated_query = llm_instruct.predict(
        translate_prompt.format(question=query)
    )

    classify_query = llm_instruct.predict(
        classify_prompt.format(question=translated_query),
    )

    translated_query = translated_query.replace("\n", "")

    result = [{"fan": "none"}, {"light": "none"}]

    if "fan" in classify_query:
        fan_query = llm_base.predict(
            fan_prompt.format(question=translated_query),
        )
        if "off" in fan_query:
            result[0]['fan'] = "off"
        if "on" in fan_query:
            result[0]['fan'] = "on"

    if "light" in classify_query:
        light_query = llm_base.predict(
            light_prompt.format(question=translated_query),
        )

        if "off" in light_query:
            result[1]['light'] = "off"
        if "on" in light_query:
            result[1]['light'] = "on"

    return result

print(chatbot("open the light"))