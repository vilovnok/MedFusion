from agent.src import MedFusionLLM

hf_token='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'
model="microsoft/Phi-3-mini-4k-instruct"
text='Migraine sufferers often experience a combination of intense headaches, nausea, and light sensitivity. New treatments targeting specific neurotransmitters show promise in reducing the frequency of migraine attacks.'

if __name__ == "__main__":
    agent = MedFusionLLM(hf_token=hf_token, model=model)
    output = agent.invoke(text)
    print(output)
