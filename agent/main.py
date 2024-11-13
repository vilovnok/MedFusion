from agent.src import MedFusionLLM


hf_token='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'
model="microsoft/Phi-3-mini-4k-instruct"

text='New advancements in minimally invasive surgery allow doctors to perform complex procedures with fewer incisions, reducing patient recovery time and minimizing risks associated with traditional open surgery.'


if __name__ == "__main__":
    agent = MedFusionLLM(hf_token=hf_token, model=model)
    output = agent.invoke(text)
    print(output)