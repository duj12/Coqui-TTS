import torch
from TTS.api import TTS
import os
from tqdm import tqdm
from multiprocessing import Process

max_ref_audio_per_speaker = 300  # 一个参考说话人最多使用300条音频，最多也生成300条音频
min_ref_audio_filesize = 100 * 1024  # 参考音频最小文件大小。 100Kb~对应16k音频大约时长是3s.
def main(args, spk2utts, gpu_id, start_idx, chunk_num):
    device = f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu"
    # Init TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)

    speakers = list(spk2utts.keys())
    total_speakers = len(speakers)
    text_file = args.text_file
    output_dir = args.output_dir

    with open(text_file, "rb") as f:
        for i, line in enumerate(tqdm(f)):
            if not i in range(start_idx, start_idx+chunk_num):
                continue
            try:
                text = line.decode('utf-8').strip()
                speaker_idx = i % total_speakers
                speaker_name = speakers[speaker_idx]
                ref_audios = spk2utts[speaker_name]
                total_ref_audio = len(ref_audios)
                ref_audio_idx = i//total_speakers % total_ref_audio
                ref_audio = ref_audios[ref_audio_idx]

                speaker_path = os.path.join(output_dir, speaker_name)
                if not os.path.exists(speaker_path):
                    os.makedirs(speaker_path, exist_ok=True)
                utt_name = f"{i+1:08d}"
                out_path = f"{speaker_path}/{utt_name}"
                if os.path.exists(f"{out_path}.wav"):
                    print(f"audio {out_path}.wav exists, continue.")
                    continue

                tts.tts_to_file(text=text, speaker_wav=ref_audio, split_sentences=False,
                                language=args.language, file_path=f"{out_path}.wav")
                with open(f"{out_path}.txt", 'w', encoding='utf-8') as fout:
                    fout.write(f"{text}\n")
            except Exception as e:
                print(e)
                continue


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-s', '--speaker_file', type=str, required=True, help='spk2utt of reference audios')
    p.add_argument('-r', '--ref_audio', type=str, required=True, help='wav.scp of reference audios')
    p.add_argument('-t', '--text_file', type=str, required=True, help='the absolute path of test file that is going to inference')
    p.add_argument('-l', '--language', type=str, required=True, help='the language of text.')
    p.add_argument('-o', '--output_dir', type=str, required=True, default=None, help='path to save the generated audios.')
    p.add_argument('-g', '--gpu_ids', type=str, required=False, default='0')
    p.add_argument('-n', '--num_thread', type=str, required=False, default='1')
    args = p.parse_args()

    gpus = args.gpu_ids
    os.environ['CUDA_VISIBLE_DEVICES'] = gpus
    gpu_list = gpus.split(',')
    gpu_num = len(gpu_list)
    thread_per_gpu = int(args.num_thread)  # 4GB GPU memory per thread, bottleneck is CPU usage!!!
    thread_num = gpu_num * thread_per_gpu  # threads

    total_len = 3600000  # len(wavs)
    print(f"Total wavs: {total_len}, Thread nums: {thread_num}")

    speaker_file = args.speaker_file  # spk2utt 每个说话人对应的音频id
    ref_audio = args.ref_audio   # wav.scp  每条音频对应的路径
    text_file = args.text_file   # 文本
    output_dir = args.output_dir

    # 得到每个说话人对应的参考音频路径
    utt2path = {}
    with open(ref_audio, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip().split(maxsplit=1)
            if len(line) != 2:
                print(f"{line} format error, you should supply kaldi format wav.scp.")
                continue
            utt = line[0]
            path = line[1]
            if not os.path.exists(path):
                print(f"wav path: {path} not exist.")
                continue
            if os.path.getsize(path) < min_ref_audio_filesize:
                # print(f"wav path: {path} not bigger than {min_ref_audio_filesize} byte.")
                continue
            utt2path[utt] = path

    spk2utts = {}
    with open(speaker_file, 'r', encoding='utf-8') as fin:
        for line in fin:
            line = line.strip().split()
            if len(line) <= 1:
                continue
            spk = line[0]
            utts = line[1:]
            if spk not in spk2utts:
                spk2utts[spk] = []
            for idx, utt in enumerate(utts):
                if idx >= max_ref_audio_per_speaker:
                    break
                if utt not in utt2path:
                    continue
                spk2utts[spk].append(utt2path[utt])

    spk2utts = {spk:spk2utts[spk] for spk in spk2utts if len(spk2utts[spk]) > 0}
    total_speakers = len(spk2utts)
    print(f"Total speakers: {total_speakers}")

    if total_len >= thread_num:
        chunk_size = int(total_len / thread_num)
        remain_wavs = total_len - chunk_size * thread_num
    else:
        chunk_size = 1
        remain_wavs = 0

    process_list = []
    chunk_begin = 0
    for i in range(thread_num):
        print(f"process part {i}...")
        gpu_id = i % gpu_num
        now_chunk_size = chunk_size
        if remain_wavs > 0:
            now_chunk_size = chunk_size + 1
            remain_wavs = remain_wavs - 1
        # main(args, gpu_id, chunk_begin, now_chunk_size)
        # process i handle wavs at chunk_begin and size of now_chunk_size
        p = Process(target=main, args=(args, spk2utts,
                                       gpu_id, chunk_begin, now_chunk_size))
        chunk_begin = chunk_begin + now_chunk_size
        p.start()
        process_list.append(p)

    for i in process_list:
        p.join()