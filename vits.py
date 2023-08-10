vits_config = {
    "device": "cpu",  # cpu or cuda,cuda需要NVIDIA显卡
    "ns": 0.1,  # noise_scale(控制感情变化程度),范围[0.1-1.0],调大了声音容易怪，除非模型好
    "nsw": 0.5,  # noise_scale_w(控制音素发音长度)，范围[0.1-1.0]
    "ls": 1.2,  # 语速调节，范围[0.1-2.0],越大越快
    "text_length": 300,  # 最大文本长度
    "lang": "zh",  # 语言，zh|ja|mix,mix时将中文用[ZH]包裹，日文用[JA]包裹
    "speak_id": 0,  # 朗读人id
}