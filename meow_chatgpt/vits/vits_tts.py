# coding=utf-8
import os
import traceback
import logging
from configparser import ConfigParser
import wave
load_model = True

def save_vits_wav(text, uuid):
    if load_model:
        import numpy as np
        from scipy.io.wavfile import write
        vits = Vits()
        status, voice = vits.get_vits_voice_tuple(text)
        if not status:
            logging.error("vits音频文件生成失败 请检查配置文件参数")
            return False
        try:
            if not os.path.exists(os.path.join(os.getcwd(), 'static')):
                os.mkdir(os.path.join(os.getcwd(), 'static'))
            scaled = np.int16(voice[1] / np.max(np.abs(voice[1])) * 32767)
            file_path = os.path.join(os.getcwd(), 'static', 'out.wav')
            data = np.vstack([scaled, scaled])  # 组合左右声道
            data = data.T  # 转置（这里参考了双声道音频读取得到的格式）

            # 打开目标文件，wb表示以二进制写方式打开，只能写文件，如果文件不存在，创建该文件；如果文件已存在，则覆盖写
            wf = wave.open(file_path, 'wb')
            wf.setnchannels(2)  # 设置声道数
            wf.setsampwidth(2)  # 设置采样宽度
            wf.setframerate(22050)  # 设置采样率
            wf.writeframes(data.tobytes())  # 将data转换为二进制数据写入文件
            wf.close()  # 关闭已打开的文件

            # write(file_path, 44100, scaled)
            logging.info("成功生成WAV文件".format(uuid))
            return True
        except Exception:
            traceback.print_exc()
            return False
    return False


def get_text(text, hps):
    import meow_chatgpt.vits.commons as commons
    from torch import LongTensor
    from meow_chatgpt.vits.text import text_to_sequence
    text_norm, clean_text = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm, clean_text


def change_lang(language):
    if language == 0:
        return 0.6, 0.668, 1.2
    else:
        return 0.6, 0.668, 1.1


class Vits:
    def __init__(self):
        self.config = ConfigParser()
        self.config.read("./config.ini", encoding="UTF-8")
        vits_config = self.config['vits']

        model_folder = vits_config['model_folder']
        self.model_path = os.path.join(os.getcwd(), model_folder, vits_config['model_name'])
        self.config_path = os.path.join(os.getcwd(), model_folder, vits_config['config_name'])
        if not os.path.exists(os.path.join(os.getcwd(), model_folder)):
                logging.error("没有找到配置文件夹[{}]".format(model_folder))
                logging.info("创建文件夹[{}] 请将模型文件和配置文件放入其中".format(model_folder))
                os.mkdir(os.path.join(os.getcwd(), model_folder))
                exit(0)
        if not os.path.exists(self.model_path) or not os.path.exists(self.config_path):
            logging.error("{}文件夹中没有模型[{}]或配置文件[{}]".format(model_folder, self.model_path, self.config_path))
            exit(1)

        self.speakers = None
        self.model = None
        self.optimizer = None
        self.learning_rate = None
        self.epochs = None
        self.hps_ms = None
        self.net_g_ms = None
        self.device = None
        self.device_text = vits_config['device']
        self.ns = float(vits_config['ns'])
        self.nsw = float(vits_config['nsw'])
        self.ls = float(vits_config['ls'])
        self.lang = vits_config['lang']
        self.speak_id = int(vits_config['speak_id'])

    def vits(self, text, language, speaker_id, noise_scale, noise_scale_w, length_scale):
        from torch import no_grad, LongTensor
        text = text.replace('\n', ' ').replace('\r', '').replace(" ", "")
        if language == 'zh':
            text = f"[ZH]{text}[ZH]"
        elif language == 'ja':
            text = f"[JA]{text}[JA]"
        elif language == 'mix':
            text = f"{text}"
        else:
            logging.error('vits 错误的语言 请检查配置文件')
            return False, None
        stn_tst, clean_text = get_text(text, self.hps_ms)
        with no_grad():
            x_tst = stn_tst.unsqueeze(0).to(self.device)
            x_tst_lengths = LongTensor([stn_tst.size(0)]).to(self.device)
            speaker_id = LongTensor([speaker_id]).to(self.device)
            audio = \
                self.net_g_ms.infer(x_tst, x_tst_lengths, sid=speaker_id, noise_scale=noise_scale,
                                    noise_scale_w=noise_scale_w,
                                    length_scale=length_scale)[0][0, 0].data.cpu().float().numpy()

        return True, (22050, audio)

    def search_speaker(self, search_value):
        for s in self.speakers:
            if search_value == s:
                return s
        for s in self.speakers:
            if search_value in s:
                return s

    def get_vits_voice_tuple(self, text_to_voice):
        from meow_chatgpt.vits.models import SynthesizerTrn
        import meow_chatgpt.vits.utils as utils
        import torch
        self.device = torch.device(self.device_text)
        self.hps_ms = utils.get_hparams_from_file(self.config_path)
        self.net_g_ms = SynthesizerTrn(
            len(self.hps_ms.symbols),
            self.hps_ms.data.filter_length // 2 + 1,
            self.hps_ms.train.segment_size // self.hps_ms.data.hop_length,
            n_speakers=self.hps_ms.data.n_speakers,
            **self.hps_ms.model)
        _ = self.net_g_ms.eval().to(self.device)
        self.speakers = self.hps_ms.speakers
        self.model, self.optimizer, self.learning_rate, self.epochs = utils.load_checkpoint(self.model_path, self.net_g_ms,
                                                                                            None)
        return self.vits(text_to_voice, self.lang, self.speak_id, self.ns, self.nsw, self.ls)
