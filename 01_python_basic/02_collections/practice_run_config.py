config = {
    "model": "example-model",
    "temperature": 0.2,
    "max_tokens": 500,
}

config["timeout"] = 30
config["max_tokens"] = 800
print("retry_count :", config.get("retry_count", 0))  # 없는 키를 조회하면 기본값을 반환한다.
print("model :", config["model"])
print("temperature :", config["temperature"])
print("max_tokens :", config["max_tokens"])
print("timeout :", config["timeout"])


