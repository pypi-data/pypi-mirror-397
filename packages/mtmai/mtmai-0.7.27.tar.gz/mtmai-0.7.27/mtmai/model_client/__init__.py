from smolagents import LiteLLMRouterModel

# from mtmai.model_client.adk_litellm import MtAdkRouterLiteLlm
from mtmai.model_client.litellm_router import get_model_list
import os
import litellm
from google.adk.models.lite_llm import LiteLlm


def get_default_litellm_model(model_name="gemini-2.0-flash"):
    # gemini-2.5-flash
    # client = MtAdkRouterLiteLlm(
    #     model=model_name,
    # )
    # return client

    # 新版使用 litellm proxy server 进行中转
    os.environ["LITELLM_PROXY_API_KEY"] = "sk-AfBNj8MMkJRDU8qZV-Nz2A"
    # os.environ["LITELLM_PROXY_API_KEY"] = "sk-feihuo321"

    os.environ["LITELLM_PROXY_API_BASE"] = "http://localhost:4000"
    # Enable the use_litellm_proxy flag
    litellm.use_litellm_proxy = True
    model = LiteLlm(model=model_name)
    return model


def get_default_smolagents_model():
    # router = get_litellm_router()
    return LiteLLMRouterModel(
        model_id="gemini-2.0-flash-exp",
        model_list=get_model_list(),
        client_kwargs={
            # "routing_strategy": router.routing_strategy,
            "num_retries": 10,
            "retry_after": 30,
            # "cooldown_time": router.cooldown_time,
            # "allowed_fails_policy": router.allowed_fails_policy,
            # "retry_policy": router.retry_policy,
            # "fallbacks": router.fallbacks,
            # "cache_responses": router.cache_responses,
            # "debug_level": router.debug_level,
        },
    )
